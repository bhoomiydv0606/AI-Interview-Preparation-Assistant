import json
from functools import lru_cache
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "questions.json"
DIFFICULTIES = ["Easy", "Medium", "Hard"]


@lru_cache(maxsize=1)
def load_questions():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_categories():
    return list(load_questions().keys())


def get_difficulties():
    return DIFFICULTIES


def get_questions(category=None, difficulty=None):
    data = load_questions()
    safe_category = category if category in data else get_categories()[0]
    category_data = data[safe_category]
    safe_difficulty = difficulty if difficulty in DIFFICULTIES else DIFFICULTIES[0]
    return category_data.get(safe_difficulty, category_data[DIFFICULTIES[0]])


def is_valid_category(category):
    return category in load_questions()


def is_valid_difficulty(difficulty):
    return difficulty in DIFFICULTIES
