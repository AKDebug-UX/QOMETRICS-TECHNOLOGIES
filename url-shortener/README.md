# Snip.ly – URL Shortener (Qometrics Technologies)

A clean, production-ready URL shortener built with Python & Flask.

## Features
- 🔗 Shorten any valid HTTP/HTTPS URL
- ⚡ 6-character random short codes (collision-safe)
- 📊 Click tracking per link
- 📈 Stats dashboard (all links + per-link details)
- 🎨 Beautiful dark glassmorphism UI
- 🚀 Deploy-ready for Render & Railway

## Project Structure

```
url-shortener/
├── app.py              # Flask app, routes, DB logic
├── requirements.txt    # Dependencies
├── Procfile            # For Render / Railway deploy
├── templates/
│   ├── index.html      # Homepage – shorten form
│   ├── stats.html      # All-links stats dashboard
│   ├── url_stats.html  # Per-link stats detail
│   └── error.html      # 404 / 500 error page
└── urls.db             # SQLite DB (auto-created on first run)
```

## Running Locally

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
python app.py
```

Visit `http://localhost:5000` in your browser.

## Routes

| Route | Method | Description |
|---|---|---|
| `/` | GET, POST | Homepage + shorten form |
| `/<short_code>` | GET | Redirect to original URL (increments click count) |
| `/stats` | GET | All links dashboard |
| `/stats/<short_code>` | GET | Per-link detail page |

## Deploying to Render

1. Push this folder to a GitHub repository.
2. Go to [render.com](https://render.com) → **New Web Service**.
3. Connect your GitHub repo.
4. Set:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Environment**: Python 3
5. Click **Deploy** – your app will be live at `https://<name>.onrender.com`.

> **Note on SQLite on Render:** Render's free tier has an ephemeral filesystem, so `urls.db` will reset on deploys. For persistence, swap SQLite for **PostgreSQL** (free tier available on Render) using `psycopg2` + `DATABASE_URL`.

## Deploying to Railway

1. Push this folder to GitHub.
2. Go to [railway.app](https://railway.app) → **New Project → Deploy from GitHub**.
3. Select your repo – Railway auto-detects the `Procfile`.
4. Add a **PostgreSQL** plugin for persistent storage (optional).
5. Your app deploys automatically.
