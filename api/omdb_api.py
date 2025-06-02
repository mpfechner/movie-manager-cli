import requests

OMDB_API_KEY = "f821c8bd"  # dein API Key


def fetch_movie_data(title: str) -> dict | None:
    """Fetch movie data from OMDb API by title."""
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
    response = requests.get(url)

    if response.status_code != 200:
        print("❌ API request failed.")
        return None

    data = response.json()
    if data.get("Response") == "False":
        print(f"❌ Movie not found: {data.get('Error')}")
        return None

    return {
        "title": data.get("Title"),
        "year": int(data.get("Year", 0)),
        "rating": float(data.get("imdbRating", 0.0)),
        "poster_url": data.get("Poster")
    }
