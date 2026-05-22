from flask import Blueprint, jsonify, request

from app.auth_helpers import api_login_required, current_user
from app.models import get_recent_attempts, get_user_stats, save_attempt
from app.security import csrf_required
from app.services.feedback import analyze_answer
from app.services.questions import (
    get_categories,
    get_difficulties,
    get_questions,
    is_valid_category,
    is_valid_difficulty,
)

api_bp = Blueprint("api", __name__)


@api_bp.route("/questions")
@api_login_required
def questions():
    category = request.args.get("category", get_categories()[0])
    difficulty = request.args.get("difficulty", get_difficulties()[0])

    if not is_valid_category(category):
        return jsonify({"error": "Invalid category."}), 400
    if not is_valid_difficulty(difficulty):
        return jsonify({"error": "Invalid difficulty."}), 400

    return jsonify({"questions": get_questions(category, difficulty)})


@api_bp.route("/feedback", methods=["POST"])
@api_login_required
@csrf_required
def feedback():
    data = request.get_json(silent=True) or {}
    category = str(data.get("category", "")).strip()
    difficulty = str(data.get("difficulty", "")).strip()
    question = str(data.get("question", "")).strip()
    answer = str(data.get("answer", "")).strip()

    if not is_valid_category(category):
        return jsonify({"error": "Invalid category."}), 400
    if not is_valid_difficulty(difficulty):
        return jsonify({"error": "Invalid difficulty."}), 400
    if not question:
        return jsonify({"error": "Please select a question."}), 400
    if not answer:
        return jsonify({"error": "Please write an answer before requesting feedback."}), 400
    if len(answer) > 4000:
        return jsonify({"error": "Answer is too long. Keep it under 4000 characters."}), 400

    valid_questions = get_questions(category, difficulty)
    if question not in valid_questions:
        return jsonify({"error": "Selected question does not match this category."}), 400

    result = analyze_answer(question, answer, category, difficulty)
    save_attempt(current_user()["id"], result)

    return jsonify(
        {
            "feedback": result,
            "stats": get_user_stats(current_user()["id"]),
            "recent_attempts": get_recent_attempts(current_user()["id"], limit=5),
        }
    )


@api_bp.route("/stats")
@api_login_required
def stats():
    user = current_user()
    return jsonify(
        {
            "stats": get_user_stats(user["id"]),
            "recent_attempts": get_recent_attempts(user["id"], limit=5),
        }
    )
