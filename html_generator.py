from storage.movie_storage_sql import get_user_movies
from pathlib import Path

def generate_movie_card(movie) -> str:
    """Return HTML snippet for a single movie card."""
    return f"""
    <div class="movie-card">
        <img src="{movie.poster_url}" alt="Poster of {movie.title}">
        <div class="movie-title">{movie.title}</div>
        <div class="movie-year">{movie.year}</div>
    </div>
    """

def generate_html(user_id: int,
                  template_path: str = "static/index_template.html",
                  output_path: str = "movies_output.html") -> None:
    """Generate a complete HTML page of the user's movie collection."""
    movies = get_user_movies(user_id)
    if not movies:
        print("❌ No movies to export.")
        return

    cards_html = "\n".join(generate_movie_card(m) for m in movies)

    template = Path(template_path).read_text(encoding="utf-8")
    html_output = template.replace("{{MOVIE_CARDS}}", cards_html)

    Path(output_path).write_text(html_output, encoding="utf-8")
    print(f"✅ HTML export completed: {output_path}")
