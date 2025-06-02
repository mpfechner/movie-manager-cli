import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "movies.db")
DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URL, echo=True)


# Create tables if they don't exist
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
    """))

    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster_url TEXT,
            note TEXT,
            user_id INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id),
            UNIQUE(title, user_id)
        );
    """))

    connection.commit()


def add_user(name: str) -> None:
    """Add a new user to the users table."""
    with engine.connect() as connection:
        try:
            connection.execute(text(
                "INSERT INTO users (name) VALUES (:name)"
            ), {"name": name})
            connection.commit()
            print(f"✅ User '{name}' added successfully.")
        except Exception as e:
            print(f"⚠️ Error adding user '{name}': {e}")


def list_users() -> list[tuple[int, str]]:
    """Return a list of all users as (id, name) tuples."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT id, name FROM users"))
        users = result.fetchall()
        return users


def get_user_id(name: str) -> int | None:
    """Return the user ID for a given username, or None if not found."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT id FROM users WHERE name = :name"),
            {"name": name}
        ).fetchone()

        if result:
            return result[0]
        return None


def add_movie(title: str, year: int, rating: float, poster_url: str, user_id: int) -> None:
    """Add a new movie to the database for a specific user."""
    with engine.connect() as connection:
        try:
            connection.execute(text("""
                INSERT INTO movies (title, year, rating, poster_url, user_id)
                VALUES (:title, :year, :rating, :poster_url, :user_id)
            """), {
                "title": title,
                "year": year,
                "rating": rating,
                "poster_url": poster_url,
                "user_id": user_id
            })
            connection.commit()
            print(f"🎉 Movie '{title}' added for user ID {user_id}.")
        except Exception as e:
            print(f"⚠️ Error adding movie '{title}': {e}")


def list_movies(user_id: int) -> dict[str, dict[str, str | int | float]]:
    """Return a dictionary of movies for the given user."""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT title, year, rating, poster_url
            FROM movies
            WHERE user_id = :user_id
        """), {"user_id": user_id})

        rows = result.fetchall()

    return {
        row.title: {
            "year": row.year,
            "rating": row.rating,
            "poster_url": row.poster_url
        }
        for row in rows
    }


def delete_movie(title: str, user_id: int) -> None:
    """Delete a movie for a specific user."""
    with engine.connect() as connection:
        result = connection.execute(text("""
            DELETE FROM movies
            WHERE title = :title AND user_id = :user_id
        """), {"title": title, "user_id": user_id})
        connection.commit()

        if result.rowcount:
            print(f"🗑️ Movie '{title}' deleted for user ID {user_id}.")
        else:
            print(f"⚠️ Movie '{title}' not found for user ID {user_id}.")


def update_note(title: str, note: str, user_id: int) -> None:
    """Update or add a note to a movie for a specific user."""
    with engine.connect() as connection:
        result = connection.execute(text("""
            UPDATE movies
            SET note = :note
            WHERE title = :title AND user_id = :user_id
        """), {"note": note, "title": title, "user_id": user_id})
        connection.commit()

        if result.rowcount:
            print(f"📝 Note added to '{title}' for user ID {user_id}.")
        else:
            print(f"⚠️ Movie '{title}' not found for user ID {user_id}.")


def update_movie(title: str, year: int, rating: float, poster_url: str, user_id: int) -> bool:
    """Update an existing movie for a specific user. Returns True if update was successful."""
    try:
        with engine.begin() as connection:
            result = connection.execute(
                text("""
                    UPDATE movies
                    SET year = :year, rating = :rating, poster_url = :poster_url
                    WHERE title = :title AND user_id = :user_id
                """),
                {
                    "year": year,
                    "rating": rating,
                    "poster_url": poster_url,
                    "title": title,
                    "user_id": user_id
                }
            )
            return result.rowcount > 0
    except SQLAlchemyError as e:
        print(f"❌ Database error during update: {e}")
        return False


def get_user_movies(user_id: int) -> list:
    """Return all movies for a specific user."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT * FROM movies WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        return result.fetchall()


def get_movies_sorted_by_rating(user_id: int) -> list:
    """Return all movies sorted by rating (descending) for the given user."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT * FROM movies WHERE user_id = :user_id ORDER BY rating DESC"),
            {"user_id": user_id}
        )
        return result.fetchall()


def get_movies_sorted_by_year(user_id: int) -> list:
    """Return all movies sorted by year (ascending) for the given user."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT * FROM movies WHERE user_id = :user_id ORDER BY year ASC"),
            {"user_id": user_id}
        )
        return result.fetchall()


def filter_movies_by_rating(user_id: int, min_rating: float) -> list:
    """Return all movies for a user with rating >= min_rating."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT * FROM movies WHERE user_id = :user_id AND rating >= :min_rating"),
            {"user_id": user_id, "min_rating": min_rating}
        )
        return result.fetchall()



if __name__ == "__main__":
    uid = get_user_id("Sara")
    if uid:
        update_note("Inception", "My favorite Nolan film!", uid)

