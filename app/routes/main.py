from flask import Blueprint, render_template

from app.auth_helpers import current_user, login_required
from app.models import get_recent_attempts, get_user_stats
from app.services.questions import get_categories, get_difficulties, get_questions

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def index():
    categories = get_categories()
    difficulties = get_difficulties()
    selected_category = categories[0]
    selected_difficulty = difficulties[0]
    user = current_user()

    return render_template(
        "index.html",
        categories=categories,
        difficulties=difficulties,
        selected_category=selected_category,
        selected_difficulty=selected_difficulty,
        questions=get_questions(selected_category, selected_difficulty),
        stats=get_user_stats(user["id"]),
    )


@main_bp.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    return render_template(
        "dashboard.html",
        stats=get_user_stats(user["id"]),
        attempts=get_recent_attempts(user["id"], limit=15),
    )


@main_bp.route("/healthz")
def healthz():
    return {"status": "ok"}
