import statistics  # For statistics functions
import random  # For random movie selection
import sys
from rapidfuzz import process
from storage import movie_storage_sql as storage
from api.omdb_api import fetch_movie_data


current_user_id = None


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
    print(f"{len(users)+1}. Create new user")

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



def command_list_movies():
    """List all movies for the current user using SQL storage."""
    movies = storage.list_movies(current_user_id)
    if not movies:
        print("\033[31mNo movies found in your collection.\033[0m")
        return

    print("\033[32mYour movie collection:\033[0m")
    for title, data in movies.items():
        print(f"- {title} ({data['year']}), Rating: {data['rating']}")


def command_add_movie():
    """Add a movie using the OMDb API."""
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


def command_delete_movie():
    """Delete a movie from the current user's collection using fuzzy search."""
    movies = storage.list_movies(current_user_id)
    if not movies:
        print("❌ You have no movies to delete.")
        return

    title_input = input("🗑️ Enter the title of the movie to delete: ").strip()

    best_match, score, _ = process.extractOne(title_input, movies.keys())
    if score < 70:
        print("❌ No close match found.")
        return

    confirm = input(f"❓ Did you mean '{best_match}'? (y/n): ").strip().lower()
    if confirm != "y":
        print("❌ Deletion cancelled.")
        return

    storage.delete_movie(best_match, current_user_id)



def update_movie() -> None:
    """ Function to update the rating of a movie """
    update_movie_name = input("\033[34mEnter movie name to update: \033[0m").strip()

    movies = movie_storage.get_movies()

    if not update_movie_name:
        print("\033[31mMovie name cannot be empty.\033[0m")
        input("\033[34mPress enter to continue\033[0m")
        present_menu()
        return

    if update_movie_name not in movies:
        print(f"\033[31mMovie {update_movie_name} not in database and could not be updated!\033[0m")
    else:
        updated_rating = float(input("\033[34mPlease enter new movie rating (0-10): \033[0m"))

        while not 0 <= updated_rating <= 10:
            print(f"\033[31mRating {updated_rating} is invalid. Please enter rating between 0 and 10\033[0m")
            updated_rating = float(input("\033[34mPlease enter new movie rating (0-10): \033[0m"))

        movie_storage.update_movie(update_movie_name, round(updated_rating, 2))

    print()
    input("\033[34mPress enter to continue\033[0m")
    present_menu()


def show_stats() -> None:
    """ Function to show statistics like average, median, best and worst movie """
    movies = movie_storage.get_movies()
    if len(movies) > 0:
        try:
            average_rating = round(sum(movie["rating"] for movie in movies.values()) / len(movies), 2)
            median_rating = round(statistics.median(movie["rating"] for movie in movies.values()), 2)
            best_rated_movie = max(movies, key=lambda title: movies[title]["rating"])
            worst_rated_movie = min(movies, key=lambda title: movies[title]["rating"])

            print(f"\033[34mAverage rating: {average_rating}\033[0m")
            print(f"\033[34mMedian rating: {median_rating}\033[0m")
            print(f"\033[34mBest movie: {best_rated_movie}, Rating: {movies[best_rated_movie]['rating']}\033[0m")
            print(f"\033[34mWorst movie: {worst_rated_movie}, Rating: {movies[worst_rated_movie]['rating']}\033[0m")
        except (KeyError, ValueError, TypeError) as error:
            print(f"\033[31mError calculating statistics: {str(error)}\033[0m")
    else:
        print("\033[31mNo more movies in Database\033[0m")

    print("\033[0m")
    input("\033[34mPress enter to continue\033[0m")
    present_menu()


def random_movie() -> None:
    """ Function to select a random movie from the list """
    movies = movie_storage.get_movies()
    if movies:
        random_movie_name = random.choice(list(movies))
        try:
            movie_rating = movies[random_movie_name]["rating"]
            print(f"\033[34mYour movie for tonight: {random_movie_name}, it's rated {movie_rating}\033[0m")
        except (KeyError, ValueError, TypeError) as error:
            print(f"\033[31mError retrieving movie rating: {str(error)}\033[0m")
    else:
        print("\033[31mNo more movies in Database\033[0m")

    print("\033[0m")
    input("\033[34mPress enter to continue\033[0m")
    present_menu()


def filter_movies() -> None:
    """ Function to filter movies based on criteria """
    try:
        min_rating = input("\033[34mEnter minimum rating (leave blank for no filter): \033[0m")
        min_year = input("\033[34mEnter start year (leave blank for no filter): \033[0m")
        max_year = input("\033[34mEnter end year (leave blank for no filter): \033[0m")

        min_rating = float(min_rating) if min_rating else 0
        if min_rating < 0 or min_rating > 10:
            print("\033[31mRating must be between 0 and 10\033[0m")
            return

        min_year = int(min_year) if min_year else 0
        max_year = int(max_year) if max_year else 9999

        if min_year > max_year:
            print("\033[31mStart year cannot be greater than end year.\033[0m")
            return

        movies = movie_storage.get_movies()
        filtered_movies = {title: data for title, data in movies.items() if
            data["rating"] >= min_rating and min_year <= data["year"] <= max_year}

        if filtered_movies:
            for title, data in filtered_movies.items():
                print(f"\033[34m{title} ({data['year']}): Rating: {data['rating']}\033[0m")
        else:
            print("\033[31mNo movies match the filter criteria\033[0m")

    except ValueError as error:
        print(f"\033[31mInvalid input: {error}\033[0m")

    print()
    input("\033[34mPress enter to continue\033[0m")
    present_menu()


def search_movie() -> None:
    """ Function to search for movies by part of the name """
    movies = movie_storage.get_movies()
    needle = input("\033[34mEnter part of movie name: \33[0m").lower().strip()

    if not needle:
        print("\033[31mYou must enter a search term!\033[0m")
        input("\033[34mPress enter to continue\033[0m")
        present_menu()
        return

    matches = process.extract(needle, movies.keys(), limit=None)
    matches = [match for match in matches if match[1] >= 60]

    if matches:
        for match in matches:
            movie_title = match[0]
            movie_data = movies[movie_title]
            print(f"\033[34m{movie_title}: Rating: {movie_data['rating']} Year: {movie_data['year']}\033[0m")
    else:
        print("\033[31mNo close matches found\033[0m")

    print("\033[0m")
    input("\033[34mPress enter to continue\033[0m")
    present_menu()


def sort_movies_by_rating() -> None:
    """ Function to sort movies by rating """
    movies = movie_storage.get_movies()
    sorted_movies = sorted(movies.items(), key=lambda x: x[1]["rating"], reverse=True)

    if sorted_movies:
        print("\033[34mMovies sorted by rating:\033[0m")
        for title, data in sorted_movies:
            print(f"\033[34m{title}: Rating: {data['rating']} Year: {data['year']}\033[0m")
    else:
        print("\033[31mNo movies in the database to sort\033[0m")

    print("\033[0m")
    input("\033[34mPress enter to continue\033[0m")
    present_menu()


def sort_movies_by_year() -> None:
    """ Function to sort movies by year """
    movies = movie_storage.get_movies()
    sorted_movies = sorted(movies.items(), key=lambda x: x[1]["year"])

    if sorted_movies:
        print("\033[34mMovies sorted by year:\033[0m")
        for title, data in sorted_movies:
            print(f"\033[34m{title} ({data['year']}): Rating: {data['rating']}\033[0m")
    else:
        print("\033[31mNo movies in the database to sort\033[0m")

    print("\033[0m")
    input("\033[34mPress enter to continue\033[0m")
    present_menu()


def present_menu() -> None:
    """ Main menu to navigate through the options """
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
    print("\033[0m")

    choice = int(input("\033[34mEnter choice (0-10): \033[0m"))

    # Dictionary to map choices to functions
    options = {
        0: sys.exit,
        1: command_list_movies,
        2: command_add_movie,
        3: command_delete_movie,
        # 4: command_update_movie,
        # 5: command_show_stats,
        # 6: command_random_movie,
        # 7: command_search_movie,
        # 8: command_sort_movies_by_rating,
        # 9: command_sort_movies_by_year,
        # 10: command_filter_movies
    }

    # Call the function corresponding to the user's choice
    if choice in options:
        options[choice]()
    else:
        print("\033[31mInput not valid, please try again\033[0m")
        present_menu()


def main():
    global current_user_id
    print("********** My Movies Database **********")
    current_user_id = choose_user()
    present_menu()
    choose_user()  # ← das hier muss drin sein
    present_menu()



if __name__ == "__main__":
    main()