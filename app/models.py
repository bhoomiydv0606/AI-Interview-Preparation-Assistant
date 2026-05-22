import json

from app.db import execute_query, using_postgres


def create_user(name, email, password_hash):
    if using_postgres():
        row = execute_query(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
            RETURNING id
            """,
            (name, email, password_hash),
            one=True,
            commit=True,
        )
        return row["id"]

    cursor = execute_query(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, password_hash),
        commit=True,
    )
    return cursor.lastrowid


def get_user_by_email(email):
    return execute_query(
        "SELECT * FROM users WHERE email = ?",
        (email,),
        one=True,
    )


def get_user_by_id(user_id):
    if not user_id:
        return None
    return execute_query(
        "SELECT id, name, email, created_at FROM users WHERE id = ?",
        (user_id,),
        one=True,
    )


def save_attempt(user_id, result):
    execute_query(
        """
        INSERT INTO attempts (
            user_id, category, difficulty, question, answer, score, grade,
            feedback_summary, strengths, improvements, criteria
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            result["category"],
            result["difficulty"],
            result["question"],
            result["answer"],
            result["score"],
            result["grade"],
            result["summary"],
            json.dumps(result["strengths"]),
            json.dumps(result["improvements"]),
            json.dumps(result["criteria"]),
        ),
        commit=True,
    )


def get_recent_attempts(user_id, limit=8):
    rows = execute_query(
        """
        SELECT *
        FROM attempts
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (user_id, limit),
        all_rows=True,
    )
    return [_attempt_from_row(row) for row in rows]


def get_user_stats(user_id):
    row = execute_query(
        """
        SELECT
            COUNT(*) AS total_attempts,
            COALESCE(ROUND(AVG(score), 0), 0) AS average_score,
            COALESCE(MAX(score), 0) AS best_score
        FROM attempts
        WHERE user_id = ?
        """,
        (user_id,),
        one=True,
    )

    category_rows = execute_query(
        """
        SELECT category, COUNT(*) AS attempts, ROUND(AVG(score), 0) AS average_score
        FROM attempts
        WHERE user_id = ?
        GROUP BY category
        ORDER BY attempts DESC, category ASC
        """,
        (user_id,),
        all_rows=True,
    )

    return {
        "total_attempts": int(row["total_attempts"]),
        "average_score": int(row["average_score"]),
        "best_score": int(row["best_score"]),
        "categories": [
            {
                "category": category_row["category"],
                "attempts": int(category_row["attempts"]),
                "average_score": int(category_row["average_score"]),
            }
            for category_row in category_rows
        ],
    }


def _attempt_from_row(row):
    attempt = dict(row)
    if not isinstance(attempt["created_at"], str):
        attempt["created_at"] = attempt["created_at"].isoformat(timespec="seconds")
    attempt["strengths"] = json.loads(attempt["strengths"])
    attempt["improvements"] = json.loads(attempt["improvements"])
    attempt["criteria"] = json.loads(attempt["criteria"])
    return attempt
