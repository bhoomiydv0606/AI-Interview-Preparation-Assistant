from functools import wraps

from flask import abort, flash, g, jsonify, redirect, request, session, url_for

from app.models import get_user_by_id


def current_user():
    if not hasattr(g, "current_user"):
        g.current_user = get_user_by_id(session.get("user_id"))
    return g.current_user


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if current_user() is None:
            flash("Please log in to use the interview assistant.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped_view


def api_login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if current_user() is None:
            return jsonify({"error": "Authentication required."}), 401
        return view(*args, **kwargs)

    return wrapped_view
