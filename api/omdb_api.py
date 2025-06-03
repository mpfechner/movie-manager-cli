import requests
from typing import Optional

OMDB_API_KEY = "YOUR API KEY HERE"
TEST_MODE = False  # Toggle this to True for development fallback


def fetch_movie_data(title: str) -> Optional[dict]:
    """
    Fetch movie data from OMDb API or return fallback data in test mode.

    Args:
        title (str): The title of the movie to search for.

    Returns:
        dict | None: A dictionary with movie details or None if not found or error occurs.
    """
    if TEST_MODE:
        return {
            "title": title,
            "year": 2000,
            "rating": 7.0,
            "poster_url": "https://via.placeholder.com/150",
            "imdb_id": "tt0111161"
        }

    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("Response") != "True":
            return None

        return {
            "title": data.get("Title"),
            "year": int(data.get("Year", 0)),
            "rating": float(data.get("imdbRating", 0.0)),
            "poster_url": data.get("Poster"),
            "imdb_id": data.get("imdbID")
        }

    except (requests.RequestException, ValueError):
        return None


def fetch_imdb_id(title: str) -> Optional[str]:
    """
    Fetch the IMDb ID for a given movie title from the OMDb API.

    Args:
        title (str): The movie title.

    Returns:
        str | None: IMDb ID string or None if not found.
    """
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("imdbID") if data.get("Response") == "True" else None
    except requests.RequestException:
        return None
