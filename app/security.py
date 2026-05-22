import secrets
from functools import wraps

from flask import abort, jsonify, request, session


def get_csrf_token():
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def validate_csrf_token():
    expected = session.get("_csrf_token")
    received = request.headers.get("X-CSRFToken") or request.form.get("csrf_token")
    if not expected or not received:
        return False
    return secrets.compare_digest(expected, received)


def csrf_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and not validate_csrf_token():
            if request.path.startswith("/api/"):
                return jsonify({"error": "Invalid or missing CSRF token."}), 400
            abort(400, "Invalid or missing CSRF token.")
        return view(*args, **kwargs)

    return wrapped_view
