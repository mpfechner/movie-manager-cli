### Notes on API Usage

This project uses the free OMDb API to fetch movie data (title, year, rating, poster).

Due to frequent unreliability and rate limiting of the free API tier, the app includes a fallback mode for development and testing. When enabled, it provides dummy movie data to ensure the app remains usable even without API access.

Set `TEST_MODE = True` in `omdb_api.py` to activate the fallback mode.
