# AI Interview Preparation Assistant

A professional Flask web application for placement interview practice. Users can register, log in, answer categorized interview questions, receive AI-style feedback, and track scores in a SQLite database.

## Features

- Flask backend with an app factory structure
- User registration, login, logout, and protected pages
- SQLite database locally and Render Postgres in production
- Question categories with Easy, Medium, and Hard levels
- Local AI-style feedback engine using NLP-inspired scoring
- Score, grade, strengths, improvement tips, and criteria breakdown
- Dashboard with attempt history and category performance
- Responsive HTML, CSS, and JavaScript frontend
- Render-ready `Procfile`, `wsgi.py`, and `render.yaml`
- Optional Render free-tier keep-alive pinger
- Beginner-friendly code with no heavy external AI dependencies

## Tech Stack

- Python
- Flask
- SQLite
- PostgreSQL
- HTML
- CSS
- JavaScript
- Gunicorn for production serving

## Project Structure

```text
AI-Interview-Preparation-Assistant/
|-- app.py
|-- wsgi.py
|-- Procfile
|-- render.yaml
|-- requirements.txt
|-- requirements-dev.txt
|-- .env.example
|-- app/
|   |-- __init__.py
|   |-- auth_helpers.py
|   |-- config.py
|   |-- db.py
|   |-- models.py
|   |-- security.py
|   |-- data/
|   |   |-- questions.json
|   |-- routes/
|   |   |-- api.py
|   |   |-- auth.py
|   |   |-- main.py
|   |-- services/
|   |   |-- feedback.py
|   |   |-- keep_alive.py
|   |   |-- questions.py
|   |-- static/
|   |   |-- css/style.css
|   |   |-- img/favicon.svg
|   |   |-- js/main.js
|   |-- templates/
|       |-- base.html
|       |-- index.html
|       |-- dashboard.html
|       |-- auth/login.html
|       |-- auth/register.html
|       |-- errors/error.html
|-- tests/
|   |-- test_app.py
```

## File Explanation

`app.py`  
Local entry point. It creates the Flask app and lets beginners run `python app.py`.

`wsgi.py`  
Production entry point used by Gunicorn and Render.

`app/__init__.py`  
Creates and configures the Flask app, registers routes, initializes the database, and adds security headers.

`app/config.py`  
Stores environment-based configuration such as `SECRET_KEY`, database path, debug mode, and upload limits.

`app/db.py`  
Manages the database connection and creates the `users` and `attempts` tables. It uses SQLite locally, and switches to Postgres when `DATABASE_URL` is set.

`app/models.py`  
Contains beginner-friendly database functions for creating users, saving attempts, and reading dashboard stats.

`app/security.py`  
Provides CSRF token generation and validation for forms and API requests.

`app/auth_helpers.py`  
Provides `current_user`, page login protection, and API login protection.

`app/routes/auth.py`  
Handles register, login, and logout routes.

`app/routes/main.py`  
Handles the practice page, dashboard page, and health check.

`app/routes/api.py`  
Provides JSON endpoints for loading questions, generating feedback, and fetching stats.

`app/services/questions.py`  
Loads questions from JSON and validates category/difficulty values.

`app/services/feedback.py`  
Local AI-style feedback engine. It scores answers using relevance, STAR structure, specificity, and communication quality.

`app/services/keep_alive.py`  
Optional background pinger for Render free-tier demos. Enable it with environment variables only after deployment.

`app/data/questions.json`  
Question bank grouped by category and difficulty.

`app/templates/base.html`  
Shared layout, navigation, flash messages, metadata, and CSS link.

`app/templates/index.html`  
Main practice screen.

`app/templates/dashboard.html`  
Shows attempt history and performance stats.

`app/templates/auth/login.html`  
Login form.

`app/templates/auth/register.html`  
Registration form.

`app/static/css/style.css`  
Professional responsive UI styling.

`app/static/js/main.js`  
Frontend behavior: category switching, question loading, answer readiness meter, and feedback submission.

`tests/test_app.py`  
Basic tests for authentication, protected pages, APIs, feedback, and database-backed attempts.

## Local Setup

1. Create and activate a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Copy environment variables.

```bash
copy .env.example .env
```

4. Run the app.

```bash
python app.py
```

The app will create the SQLite database automatically inside the `instance/` folder.

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Secret value used to sign sessions and CSRF tokens |
| `FLASK_ENV` | Use `production` on Render |
| `FLASK_DEBUG` | Use `1` for local debug mode only |
| `DATABASE_PATH` | Optional custom SQLite file path for local development |
| `DATABASE_URL` | Render Postgres connection string. If present, the app uses Postgres instead of SQLite |
| `KEEP_ALIVE_ENABLED` | Set to `true` to enable the optional keep-alive pinger |
| `KEEP_ALIVE_URL` | Your deployed Render health URL, for example `https://your-app.onrender.com/healthz` |
| `KEEP_ALIVE_INTERVAL_SECONDS` | Ping interval. Default is `600` seconds |

## Render Deployment

1. Push this project to GitHub.
2. Create a new Render Web Service.
3. Use these settings:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn wsgi:app --workers 1 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT`
4. Add environment variables:
   - `SECRET_KEY`: generate a strong random value
   - `FLASK_ENV`: `production`
5. Create a Render Postgres database and add its **Internal Database URL** as `DATABASE_URL`.

The included `render.yaml` can also be used as a blueprint.

### Render Postgres Setup

Option A: use `render.yaml`

The included Blueprint creates:

- a free Python web service
- a free Render Postgres database
- a `DATABASE_URL` environment variable linked to the database connection string

Option B: set it manually in the Render dashboard

1. Create a new Render Postgres database.
2. Open the database page and copy the **Internal Database URL**.
3. Open your web service settings.
4. Add this environment variable:

```text
DATABASE_URL=postgresql://user:password@host:port/database
```

5. Redeploy the web service.

When `DATABASE_URL` exists, the app automatically stores users and attempts in Postgres.

## Optional Render Keep-Alive

Render free web services can sleep after inactivity. This app includes an optional pinger that calls your own health endpoint while the app is already running.

After your Render app is deployed, add these environment variables:

```text
KEEP_ALIVE_ENABLED=true
KEEP_ALIVE_URL=https://your-app-name.onrender.com/healthz
KEEP_ALIVE_INTERVAL_SECONDS=600
```

Then redeploy the service.

Important notes:

- Replace `your-app-name` with your real Render app URL.
- The pinger cannot wake the app if it is already asleep; the first visitor may still see one cold start.
- Render free services are still not guaranteed to be always-on. For production, use a paid instance.

## Run Tests

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run tests:

```bash
python -m unittest
```

## Notes

The feedback engine is local and deterministic, so it works without an external API key. It is designed for placement projects where reliability, privacy, and easy deployment matter.
