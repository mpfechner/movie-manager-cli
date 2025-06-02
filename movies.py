import statistics  # For statistics functions
import random  # For random movie selection
import sys
from fuzzywuzzy import process  # For fuzzy matching in movie search
import movie_storage


def list_movies() -> None:
    """ Function to list all movies with their ratings """
    movies = movie_storage.get_movies()  # Load movies from the storage file
    print(f"\033[34m{len(movies)} movies in total\033[0m")
    for title, data in movies.items():
        print(f"\033[34m{title}: Rating: {data['rating']} Year: {data['year']}\033[0m")
    print()
    input("\033[34mPress enter to continue\033[0m")
    present_menu()


def add_movie() -> None:
    """ Function to add a new movie with a rating """
    while True:
        new_movie = input("\033[34mPlease enter name of movie: \33[0m").strip()
        if new_movie:
            break
        print("\033[31mMovie title cannot be empty! Please enter a valid title.\033[0m")

    while True:
        try:
            new_year = int(input("\033[34mPlease enter the release year: \33[0m"))
            break
        except ValueError:
            print("\033[31mPlease enter a valid year (numeric).")

    while True:
        try:
            new_rating = float(input("\033[34mPlease enter rating (0-10): \33[0m"))
            if 0 <= new_rating <= 10:
                break
            print(f"\033[31mRating {new_rating} is invalid. Please enter rating between 0 and 10\033[0m")
        except ValueError:
            print("\033[31mPlease enter a valid numeric rating.\033[0m")

    movie_storage.add_movie(new_movie, new_year, round(new_rating, 2))
    print(f"\033[34mMovie {new_movie} successfully added\033[0m")
    print()
    input("\033[34mPress enter to continue\033[0m")
    present_menu()


def delete_movie() -> None:
    """ Function to delete a movie by its name """
    delete_movie_name = input("\033[34mEnter movie name to delete: \33[0m").strip()

    if not delete_movie_name:
        print("\033[31mMovie name cannot be empty.\033[0m")
        input("\033[34mPress enter to continue\033[0m")
        present_menu()
        return

    movie_storage.delete_movie(delete_movie_name)
    print()
    input("\033[34mPress enter to continue\033[0m")
    present_menu()


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
        1: list_movies,
        2: add_movie,
        3: delete_movie,
        4: update_movie,
        5: show_stats,
        6: random_movie,
        7: search_movie,
        8: sort_movies_by_rating,
        9: sort_movies_by_year,
        10: filter_movies
    }

    # Call the function corresponding to the user's choice
    if choice in options:
        options[choice]()
    else:
        print("\033[31mInput not valid, please try again\033[0m")
        present_menu()


def main():
    """ Hauptfunktion, um die Filmdatenbank zu starten """
    print("********** My Movies Database **********")
    present_menu()


if __name__ == "__main__":
    main()