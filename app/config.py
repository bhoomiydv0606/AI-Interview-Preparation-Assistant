import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def _bool_env(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-before-deploy")
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash").strip()
    GEMINI_TIMEOUT_SECONDS = max(5, _int_env("GEMINI_TIMEOUT_SECONDS", 20))
    DATABASE = os.environ.get(
        "DATABASE_PATH",
        str(BASE_DIR / "instance" / "interview_assistant.sqlite3"),
    )
    MAX_CONTENT_LENGTH = 64 * 1024
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
    KEEP_ALIVE_ENABLED = _bool_env("KEEP_ALIVE_ENABLED", False)
    KEEP_ALIVE_URL = os.environ.get("KEEP_ALIVE_URL", "").strip()
    KEEP_ALIVE_INTERVAL_SECONDS = max(300, _int_env("KEEP_ALIVE_INTERVAL_SECONDS", 600))
