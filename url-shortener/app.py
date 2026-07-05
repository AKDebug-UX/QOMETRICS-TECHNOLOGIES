import os
import secrets
import sqlite3
from datetime import datetime
from flask import Flask, request, redirect, render_template, url_for, abort
from urllib.parse import urlparse

app = Flask(__name__)

# Database setup

DB_PATH = os.path.join(os.path.dirname(__file__), "urls.db")


def get_db():
    """Open a database connection and return it with row_factory set."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS urls (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                long_url    TEXT    NOT NULL,
                short_code  TEXT    NOT NULL UNIQUE,
                created_at  TEXT    NOT NULL,
                click_count INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()


# Core helpers

def generate_short_code(length: int = 6) -> str:
    """Generate a URL-safe random short code."""
    return secrets.token_urlsafe(length)[:length]


def validate_url(url: str) -> bool:
    """Basic URL validation – must have a scheme and a netloc."""
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except ValueError:
        return False


def create_short_url(long_url: str) -> str:
    """
    Look up an existing mapping or create a new one.
    Returns the short_code string.
    """
    with get_db() as conn:
        # Return existing code for the same URL to avoid duplicates
        row = conn.execute(
            "SELECT short_code FROM urls WHERE long_url = ?", (long_url,)
        ).fetchone()
        if row:
            return row["short_code"]

        # Generate a unique code (retry on collision)
        for _ in range(10):
            code = generate_short_code()
            exists = conn.execute(
                "SELECT 1 FROM urls WHERE short_code = ?", (code,)
            ).fetchone()
            if not exists:
                break
        else:
            # Extremely unlikely, but handle it gracefully
            raise RuntimeError("Could not generate a unique short code.")

        conn.execute(
            "INSERT INTO urls (long_url, short_code, created_at, click_count) VALUES (?, ?, ?, 0)",
            (long_url, code, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        return code


# Application routes

@app.route("/", methods=["GET", "POST"])
def index():
    short_url = None
    error = None

    if request.method == "POST":
        long_url = request.form.get("url", "").strip()

        if not long_url:
            error = "Please enter a URL."
        elif not validate_url(long_url):
            error = "Invalid URL. Make sure it starts with http:// or https://"
        else:
            try:
                code = create_short_url(long_url)
                short_url = url_for("redirect_to_url", short_code=code, _external=True)
            except Exception as exc:
                error = f"Something went wrong: {exc}"

    return render_template("index.html", short_url=short_url, error=error)


@app.route("/<short_code>")
def redirect_to_url(short_code: str):
    """Increment click count, then redirect to the original URL."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT long_url FROM urls WHERE short_code = ?", (short_code,)
        ).fetchone()

        if row is None:
            abort(404)

        conn.execute(
            "UPDATE urls SET click_count = click_count + 1 WHERE short_code = ?",
            (short_code,),
        )
        conn.commit()
        return redirect(row["long_url"], code=302)


@app.route("/stats")
def stats():
    """Show a table of all shortened URLs with their click counts."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM urls ORDER BY click_count DESC, id DESC"
        ).fetchall()
    return render_template("stats.html", rows=rows)


@app.route("/stats/<short_code>")
def url_stats(short_code: str):
    """Show stats for a single short URL."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM urls WHERE short_code = ?", (short_code,)
        ).fetchone()
    if row is None:
        abort(404)
    short_url = url_for("redirect_to_url", short_code=short_code, _external=True)
    return render_template("url_stats.html", row=row, short_url=short_url)


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="That short link doesn't exist."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="Internal server error."), 500


# Server startup

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
