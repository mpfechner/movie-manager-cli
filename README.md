### Features

This application is a command-line based movie management tool that supports the following features:

* 👤 Multiple user profiles
* ➕ Add movies with data from the OMDb API
* 🗒️ Update existing movie details
* 🗑️ Delete movies
* 📃 List all movies for a user
* 🔍 Search and filter movies
* 🎲 Pick a random movie
* 📊 Show statistics
* 📂 Export movies as an HTML file (styled)

---

### File Structure

* `movies.py`: Main CLI application
* `storage.py`: Database interaction logic
* `api/omdb_api.py`: OMDb API handler (with fallback mode)
* `.env`: Environment file containing OMDb API key and test mode flag
* `static/index_template.html`: HTML export template
* `static/style.css`: CSS styling for exported HTML

---

### Setup Instructions

1. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root with the following content:

   ```
   OMDB_API_KEY=your_key_here
   TEST_MODE=False
   ```

   > ⚠️ **Note:** For Codio submission, a `.env` file is already included. In a real-world project, this file should be excluded from version control using `.gitignore` to protect sensitive data.

3. Run the main program:

   ```bash
   python movies.py
   ```

---

### Notes on API Usage

This project uses the free OMDb API to fetch movie data (title, year, rating, poster).

Due to frequent unreliability and rate limiting of the free API tier, the app includes a fallback mode for development and testing. When enabled, it provides dummy movie data to ensure the app remains usable even without API access.

Set `TEST_MODE=True` in the `.env` file to activate the fallback mode.

---

### Sample Database

To make testing easier for reviewers and instructors, this project includes a pre-filled SQLite database: `movies.db`.

You can use it right away without adding movies manually. All core features (listing, searching, updating, exporting, etc.) can be tested immediately.

If you prefer to start with an empty database, simply delete the `movies.db` file.

---

### Known Issues

* Poster URLs may occasionally return broken images due to API inconsistencies
* Rate limiting may cause failed API lookups — fallback mode is recommended in such cases
* No full validation of user inputs for rating and year beyond basic checks

---

### License

MIT License

---

### Author

Michael Fechner
