import sqlite3
from pathlib import Path

from flask import current_app, g


SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    score INTEGER NOT NULL,
    grade TEXT NOT NULL,
    feedback_summary TEXT NOT NULL,
    strengths TEXT NOT NULL,
    improvements TEXT NOT NULL,
    criteria TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_attempts_user_created
ON attempts (user_id, created_at DESC);
"""

POSTGRES_SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS attempts (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
        category TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        score INTEGER NOT NULL,
        grade TEXT NOT NULL,
        feedback_summary TEXT NOT NULL,
        strengths TEXT NOT NULL,
        improvements TEXT NOT NULL,
        criteria TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_attempts_user_created
    ON attempts (user_id, created_at DESC)
    """,
]


def using_postgres():
    return bool(current_app.config.get("DATABASE_URL"))


def get_db():
    if "db" not in g:
        if using_postgres():
            try:
                import psycopg2
                from psycopg2.extras import RealDictCursor
            except ImportError as error:
                raise RuntimeError(
                    "DATABASE_URL is set, but psycopg2-binary is not installed."
                ) from error

            g.db = psycopg2.connect(
                current_app.config["DATABASE_URL"],
                cursor_factory=RealDictCursor,
            )
        else:
            database_path = Path(current_app.config["DATABASE"])
            database_path.parent.mkdir(parents=True, exist_ok=True)
            connection = sqlite3.connect(database_path)
            connection.row_factory = sqlite3.Row
            g.db = connection
    return g.db


def close_db(error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def execute_query(query, params=(), one=False, all_rows=False, commit=False):
    connection = get_db()

    if using_postgres():
        sql = query.replace("?", "%s")
        cursor = connection.cursor()
        try:
            cursor.execute(sql, params)
            result = None
            if one:
                result = cursor.fetchone()
            elif all_rows:
                result = cursor.fetchall()
            if commit:
                connection.commit()
            return result
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()

    cursor = connection.execute(query, params)
    result = cursor
    if one:
        result = cursor.fetchone()
    elif all_rows:
        result = cursor.fetchall()
    if commit:
        connection.commit()
    return result


def init_db():
    connection = get_db()
    if using_postgres():
        cursor = connection.cursor()
        for statement in POSTGRES_SCHEMA:
            cursor.execute(statement)
        connection.commit()
        cursor.close()
    else:
        connection.executescript(SQLITE_SCHEMA)
        connection.commit()
