import re
import sqlite3

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db
from app.models import create_user, get_user_by_email
from app.security import csrf_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
@csrf_required
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        error = _validate_registration(name, email, password)
        if error:
            flash(error, "danger")
            return render_template("auth/register.html", name=name, email=email)

        try:
            user_id = create_user(name, email, generate_password_hash(password))
        except Exception as error:
            _rollback_database()
            if not _is_duplicate_email_error(error):
                raise
            flash("An account with this email already exists.", "danger")
            return render_template("auth/register.html", name=name, email=email)

        session.clear()
        session["user_id"] = user_id
        flash("Account created. Welcome to your practice dashboard.", "success")
        return redirect(url_for("main.index"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
@csrf_required
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_user_by_email(email)

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", email=email)

        session.clear()
        session["user_id"] = user["id"]
        flash("Logged in successfully.", "success")
        return redirect(request.args.get("next") or url_for("main.index"))

    return render_template("auth/login.html")


@auth_bp.route("/logout", methods=["POST"])
@csrf_required
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


def _validate_registration(name, email, password):
    if len(name) < 2:
        return "Please enter your full name."
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return "Please enter a valid email address."
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    return None


def _is_duplicate_email_error(error):
    if isinstance(error, sqlite3.IntegrityError):
        return True
    message = str(error).lower()
    return "duplicate" in message or "unique" in message


def _rollback_database():
    try:
        get_db().rollback()
    except Exception:
        pass
