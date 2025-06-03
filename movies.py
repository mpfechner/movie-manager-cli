import random
import sys
from typing import Optional
from rapidfuzz import process
from api.omdb_api import fetch_movie_data
from html_generator import generate_html
from storage import movie_storage_sql as storage

current_user_id: Optional[int] = None

def return_to_menu() -> None:
    """Return to the main menu after user input."""
    input("🔙 Press Enter to return to the menu...")
    present_menu()

def choose_user() -> int:
    """Let the user choose an existing profile or create a new one."""
    users = storage.list_users()

    if not users:
        print("No users found. Let's create one!")
        new_name = input("Enter your name: ").strip()
        storage.add_user(new_name)
        return storage.get_user_id(new_name)

    print("\nSelect a user:")
    for idx, user in enumerate(users, start=1):
        print(f"{idx}. {user.name}")
    print(f"{len(users) + 1}. Create new user")

    while True:
        choice = input("Enter your choice: ").strip()
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(users):
                return users[choice - 1].id
            elif choice == len(users) + 1:
                new_name = input("Enter new user name: ").strip()
                storage.add_user(new_name)
                return storage.get_user_id(new_name)
        print("❌ Invalid input, please try again.")

def command_list_movies() -> None:
    """List all movies in the current user's collection."""
    movies = storage.list_movies(current_user_id)
    if not movies:
        print("\033[31mNo movies found in your collection.\033[0m")
        return

    print("\033[32mYour movie collection:\033[0m")
    for title, data in movies.items():
        print(f"- {title} ({data['year']}), Rating: {data['rating']}")

    return_to_menu()

def command_add_movie() -> None:
    """Add a new movie to the user's collection using the OMDb API."""
    title_input = input("🎬 Enter movie title: ").strip()
    movie_data = fetch_movie_data(title_input)

    if not movie_data:
        print("❌ Could not fetch movie data from OMDb API.")
        return

    try:
        storage.add_movie(
            title=movie_data["title"],
            year=movie_data["year"],
            rating=movie_data["rating"],
            poster_url=movie_data["poster_url"],
            user_id=current_user_id
        )
        print(f"✅ Movie '{movie_data['title']}' added successfully.")
    except Exception as e:
        print(f"❌ Error adding movie: {e}")

    return_to_menu()

def command_delete_movie() -> None:
    """Delete a movie from the user's collection using fuzzy matching."""
    movies = storage.list_movies(current_user_id)
    if not movies:
        print("❌ You have no movies to delete.")
        return

    title_input = input("🗑️ Enter the title of the movie to delete: ").strip()
    best_match, score, _ = process.extractOne(title_input, movies.keys())

    if score < 70:
        print("❌ No close match found.")
        return_to_menu()

    confirm = input(f"❓ Did you mean '{best_match}'? (y/n): ").strip().lower()
    if confirm != "y":
        print("❌ Deletion cancelled.")
        return_to_menu()

    storage.delete_movie(best_match, current_user_id)
    return_to_menu()

def command_update_movie() -> None:
    """Update a movie's information (year, rating, or poster URL)."""
    movies = storage.list_movies(current_user_id)
    if not movies:
        print("❌ No movies to update.")
        return_to_menu()

    title_input = input("✏️ Enter the title of the movie to update: ").strip()
    match = process.extractOne(title_input, movies.keys())

    if not match:
        print("❌ No close match found.")
        return_to_menu()

    best_match, score, _ = match
    if score < 70:
        print("❌ No close match found.")
        return_to_menu()

    confirm = input(f"❓ Did you mean '{best_match}'? (y/n): ").strip().lower()
    if confirm != "y":
        print("❌ Update cancelled.")
        return_to_menu()

    current_data = movies[best_match]
    print(f"Current year: {current_data['year']}")
    print(f"Current rating: {current_data['rating']}")
    print(f"Current poster: {current_data['poster_url']}")

    new_year = input("New year (leave empty to keep current): ").strip()
    new_rating = input("New rating (0.0–10.0, leave empty to keep current): ").strip()
    new_poster = input("New poster URL (leave empty to keep current): ").strip()

    year = int(new_year) if new_year else current_data['year']
    rating = float(new_rating) if new_rating else current_data['rating']
    poster_url = new_poster if new_poster else current_data['poster_url']

    success = storage.update_movie(
        title=best_match,
        year=year,
        rating=rating,
        poster_url=poster_url,
        user_id=current_user_id
    )

    if success:
        print("✅ Movie updated successfully.\n")
    else:
        print("❌ Update failed – movie not found or an error occurred.\n")

    return_to_menu()

def command_show_stats() -> None:
    """Display statistics for the user's movie collection."""
    movies = storage.get_user_movies(current_user_id)
    if not movies:
        print("❌ No movies found.")
        return

    total = len(movies)
    average = round(sum(m.rating for m in movies) / total, 2)
    best = max(movies, key=lambda m: m.rating)
    worst = min(movies, key=lambda m: m.rating)

    print("\n📊 Your Movie Stats:")
    print(f"🎬 Total movies: {total}")
    print(f"⭐ Average rating: {average}")
    print(f"🏆 Best movie: {best.title} ({best.rating})")
    print(f"🐌 Worst movie: {worst.title} ({worst.rating})\n")

    return_to_menu()

def command_random_movie() -> None:
    """Display a randomly selected movie from the user's collection."""
    movies = storage.get_user_movies(current_user_id)
    if not movies:
        print("❌ No movies found.")
        return

    movie = random.choice(movies)
    print("\n🎲 Random Movie Suggestion:")
    print(f"🎬 {movie.title}")
    print(f"📅 Year: {movie.year}")
    print(f"⭐ Rating: {movie.rating}")
    print(f"🖼️ Poster: {movie.poster_url}\n")

    return_to_menu()

def command_search_movie() -> None:
    """Search for a movie in the collection using fuzzy matching."""
    movies = storage.get_user_movies(current_user_id)
    if not movies:
        print("❌ No movies found.")
        return_to_menu()

    query = input("🔍 Enter part of a movie title to search: ").strip()
    if not query:
        print("⚠️ Search query cannot be empty.")
        return_to_menu()

    movie_titles = [m.title for m in movies]
    matches = process.extract(query, movie_titles, limit=5, score_cutoff=60)

    if not matches:
        print("❌ No matching titles found.")
        return_to_menu()

    print("\n🔎 Search results:")
    for title, score, _ in matches:
        movie = next((m for m in movies if m.title == title), None)
        if movie:
            print(f"🎬 {movie.title} ({movie.year}) - Rating: {movie.rating}")
            print(f"🖼️ {movie.poster_url}\n")

    return_to_menu()

def command_sort_movies_by_rating() -> None:
    """Display all movies sorted by rating in descending order."""
    movies = storage.get_movies_sorted_by_rating(current_user_id)
    if not movies:
        print("❌ No movies found.")
        return

    print("\n📈 Movies sorted by rating:\n")
    for movie in movies:
        print(f"🎬 {movie.title} - ⭐ {movie.rating} ({movie.year})")
        print(f"🖼️ {movie.poster_url}\n")

    return_to_menu()

def command_sort_movies_by_year() -> None:
    """Display all movies sorted by release year in ascending order."""
    movies = storage.get_movies_sorted_by_year(current_user_id)
    if not movies:
        print("❌ No movies found.")
        return_to_menu()

    print("\n📆 Movies sorted by year:\n")
    for movie in movies:
        print(f"🎬 {movie.title} ({movie.year}) - ⭐ {movie.rating}")
        print(f"🖼️ {movie.poster_url}\n")

    return_to_menu()

def command_filter_movies() -> None:
    """Filter and display movies that meet a minimum rating threshold."""
    try:
        min_rating = float(input("🔍 Enter minimum rating (0.0 - 10.0): ").strip())
    except ValueError:
        print("❌ Invalid rating input.")
        return_to_menu()

    movies = storage.filter_movies_by_rating(current_user_id, min_rating)
    if not movies:
        print("❌ No movies found with that rating or higher.")
        return_to_menu()

    print(f"\n🎯 Movies with rating >= {min_rating}:\n")
    for movie in movies:
        print(f"🎬 {movie.title} ({movie.year}) - ⭐ {movie.rating}")
        print(f"🖼️ {movie.poster_url}\n")

    return_to_menu()

def command_export_to_html() -> None:
    """Export the movie collection to an HTML file."""
    try:
        generate_html(current_user_id)
        print("✅ Export successful. Open 'movies_output.html' to view your movie collection.")
    except Exception as e:
        print(f"❌ Export failed: {e}")

    return_to_menu()

def present_menu() -> None:
    """Display the main menu and handle user selection."""
    print("\033[33mMenu:")
    print("0. Exit")
    print("1. List movies")
    print("2. Add movie")
    print("3. Delete movie")
    print("4. Update movie")
    print("5. Stats")
    print("6. Random movie")
    print("7. Search movie")
    print("8. Movies sorted by rating")
    print("9. Movies sorted by year")
    print("10. Filter movies")
    print("11. Export movies as HTML")
    print("\033[0m")

    try:
        choice = int(input("\033[34mEnter choice (0-11): \033[0m"))
    except ValueError:
        print("❌ Invalid input. Please enter a number.")
        return present_menu()

    options = {
        0: sys.exit,
        1: command_list_movies,
        2: command_add_movie,
        3: command_delete_movie,
        4: command_update_movie,
        5: command_show_stats,
        6: command_random_movie,
        7: command_search_movie,
        8: command_sort_movies_by_rating,
        9: command_sort_movies_by_year,
        10: command_filter_movies,
        11: command_export_to_html
    }

    if choice in options:
        options[choice]()
    else:
        print("\033[31mInput not valid, please try again\033[0m")
        present_menu()

def main() -> None:
    """Initialize the application and launch the main menu."""
    global current_user_id
    print("********** My Movies Database **********")
    current_user_id = choose_user()
    present_menu()

if __name__ == "__main__":
    main()
