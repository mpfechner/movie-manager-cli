import requests

OMDB_API_KEY = "f821c8bd"
TEST_MODE = False  # Toggle this to True for development fallback

def fetch_movie_data(title: str) -> dict | None:
    """Fetch movie data from OMDb API or fallback to mock data."""
    if TEST_MODE:
        print("⚠️ TEST_MODE enabled — using fallback data.")
        return {
            "title": title,
            "year": 2000,
            "rating": 7.0,
            "poster_url": "https://via.placeholder.com/150",
            "imdb_id": "tt0111161"
        }

    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ API error {response.status_code}: {response.text}")
            return None

        data = response.json()
        if data.get("Response") == "False":
            print(f"❌ Movie not found: {data.get('Error')}")
            return None

        return {
                "title": data.get("Title"),
                "year": int(data.get("Year")),
                "rating": float(data.get("imdbRating", 0.0)),
                "poster_url": data.get("Poster"),
                "imdb_id": data.get("imdbID")
            }


    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def fetch_imdb_id(title: str) -> str | None:
    """Fetch the IMDb ID for a movie title."""
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("Response") == "True":
            return data.get("imdbID")
    return None
