import json
from typing import Dict

filename = "movies.json"


def get_movies() -> Dict[str, Dict[str, int]]:
    """
    Loads and returns the movie database from the JSON file.

    Returns:
        dict: Dictionary of movies, where each key is a movie title,
              and each value is another dict with 'year' and 'rating'.
    """
    try:
        with open(filename, 'r') as file:
            movies_data = json.load(file)
        return movies_data

    except FileNotFoundError:
        print(f"\033[31mError: The file '{filename}' was not found.\033[0m")
        return {}

    except json.JSONDecodeError:
        print("\033[31mError: Failed to decode the JSON file.\033[0m")
        return {}


def save_movies(movies: Dict[str, Dict[str, int]]) -> None:
    """
    Saves the given movies dictionary to the JSON file.

    Args:
        movies (dict): Dictionary of movie data to save.
    """
    try:
        with open(filename, 'w') as file:
            json.dump(movies, file, indent=4)
        print(f"\033[34mMovies successfully saved to {filename}\033[0m")

    except IOError:
        print(f"\033[31mError: Unable to write to the file '{filename}'.\033[0m")


def add_movie(title: str, year: int, rating: int) -> None:
    """
    Adds a movie to the database and saves the changes.

    Args:
        title (str): Movie title.
        year (int): Release year.
        rating (int): Movie rating (0–10).
    """
    movies = get_movies()
    movies[title] = {"year": year, "rating": rating}
    save_movies(movies)


def delete_movie(title: str) -> None:
    """
    Deletes a movie from the database if it exists.

    Args:
        title (str): Title of the movie to delete.
    """
    movies = get_movies()

    if title in movies:
        del movies[title]
        save_movies(movies)
        print(f"\033[32mMovie '{title}' has been deleted.\033[0m")
    else:
        print(f"\033[31mMovie '{title}' not found in the database.\033[0m")


def update_movie(title: str, rating: int) -> None:
    """
    Updates the rating of an existing movie.

    Args:
        title (str): Movie title.
        rating (int): New rating value.
    """
    movies = get_movies()

    if title in movies:
        movies[title]["rating"] = rating
        save_movies(movies)
        print(f"\033[32mMovie '{title}' rating updated to {rating}.\033[0m")
    else:
        print(f"\033[31mMovie '{title}' not found in the database.\033[0m")


def list_movies() -> Dict[str, Dict[str, int]]:
    """
    Alias for get_movies() to match expected function naming in main program.

    Returns:
        dict: Dictionary of movies.
    """
    return get_movies()
