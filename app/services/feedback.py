import re
from collections import Counter


STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how",
    "i", "in", "is", "it", "of", "on", "or", "that", "the", "this", "to",
    "was", "were", "what", "when", "where", "with", "would", "you", "your",
}

STAR_TERMS = {
    "situation", "task", "action", "result", "challenge", "responsible",
    "approach", "outcome", "impact", "learned", "improved",
}

ACTION_TERMS = {
    "built", "created", "designed", "implemented", "led", "managed",
    "resolved", "optimized", "analyzed", "collaborated", "planned",
    "prioritized", "communicated", "delivered", "improved", "reduced",
}

IMPACT_TERMS = {
    "result", "impact", "increased", "decreased", "reduced", "saved",
    "improved", "measured", "metric", "customer", "team", "deadline",
    "quality", "performance", "revenue", "accuracy",
}

CATEGORY_KEYWORDS = {
    "HR / Behavioral": {"experience", "strength", "weakness", "team", "learned", "role"},
    "Technical / Coding": {"code", "api", "database", "algorithm", "system", "debug"},
    "Leadership": {"team", "led", "conflict", "priority", "decision", "motivate"},
    "Situational": {"handle", "manager", "customer", "deadline", "policy", "decision"},
    "Aptitude": {"logic", "calculate", "reason", "answer", "steps", "pattern"},
    "Data Structures": {"array", "stack", "queue", "tree", "graph", "complexity"},
    "System Design": {"scale", "cache", "database", "service", "latency", "availability"},
    "Communication": {"explain", "stakeholder", "clarify", "feedback", "presentation", "listen"},
}


def analyze_answer(question, answer, category, difficulty):
    cleaned_answer = " ".join(answer.strip().split())
    tokens = _tokens(cleaned_answer)
    word_count = len(tokens)
    sentences = [part for part in re.split(r"[.!?]+", cleaned_answer) if part.strip()]

    relevance = _relevance_score(question, tokens, category)
    structure = _structure_score(tokens, cleaned_answer, difficulty)
    specificity = _specificity_score(tokens, cleaned_answer)
    communication = _communication_score(word_count, sentences, difficulty)

    weighted_score = round(
        relevance * 0.30
        + structure * 0.25
        + specificity * 0.25
        + communication * 0.20
    )
    score = max(0, min(100, weighted_score))

    criteria = {
        "relevance": relevance,
        "structure": structure,
        "specificity": specificity,
        "communication": communication,
        "word_count": word_count,
    }

    result = {
        "category": category,
        "difficulty": difficulty,
        "question": question,
        "answer": cleaned_answer,
        "score": score,
        "grade": _grade(score),
        "summary": _summary(score, criteria),
        "strengths": _strengths(criteria),
        "improvements": _improvements(criteria, difficulty),
        "criteria": criteria,
    }
    return result


def _tokens(text):
    return [
        token
        for token in re.findall(r"[a-zA-Z][a-zA-Z0-9']*", text.lower())
        if token not in STOP_WORDS
    ]


def _relevance_score(question, answer_tokens, category):
    question_terms = set(_tokens(question))
    category_terms = CATEGORY_KEYWORDS.get(category, set())
    expected_terms = question_terms | category_terms
    if not answer_tokens:
        return 0

    answer_set = set(answer_tokens)
    overlap = len(answer_set & expected_terms)
    score = min(100, 35 + overlap * 13)
    if overlap == 0:
        score = 25
    return score


def _structure_score(tokens, answer, difficulty):
    token_set = set(tokens)
    star_hits = len(token_set & STAR_TERMS)
    has_sequence = bool(re.search(r"\b(first|then|next|finally|because|therefore)\b", answer.lower()))
    has_example = bool(re.search(r"\b(example|project|internship|college|team|client)\b", answer.lower()))

    score = 20 + star_hits * 13
    if has_sequence:
        score += 15
    if has_example:
        score += 15
    if difficulty == "Hard":
        score -= 5
    return max(0, min(100, score))


def _specificity_score(tokens, answer):
    token_set = set(tokens)
    action_hits = len(token_set & ACTION_TERMS)
    impact_hits = len(token_set & IMPACT_TERMS)
    has_number = bool(re.search(r"\d+|percent|percentage|hours|days|users|marks", answer.lower()))
    has_named_context = bool(re.search(r"\b(project|internship|hackathon|course|company|team)\b", answer.lower()))

    score = 15 + action_hits * 10 + impact_hits * 8
    if has_number:
        score += 20
    if has_named_context:
        score += 15
    return max(0, min(100, score))


def _communication_score(word_count, sentences, difficulty):
    targets = {
        "Easy": (45, 120),
        "Medium": (70, 170),
        "Hard": (90, 230),
    }
    minimum, maximum = targets.get(difficulty, targets["Easy"])

    if word_count == 0:
        return 0
    if word_count < minimum:
        score = int((word_count / minimum) * 65)
    elif word_count <= maximum:
        score = 90
    else:
        extra = min(30, int((word_count - maximum) / 10))
        score = 90 - extra

    repeated = Counter(tokens for tokens in _tokens(" ".join(sentences)))
    repeated_penalty = sum(1 for count in repeated.values() if count >= 5) * 5
    sentence_bonus = 10 if len(sentences) >= 2 else 0
    return max(0, min(100, score + sentence_bonus - repeated_penalty))


def _grade(score):
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def _summary(score, criteria):
    if score >= 85:
        return "Excellent answer. It is relevant, structured, and supported by clear evidence."
    if score >= 70:
        return "Strong answer. Add one sharper result or metric to make it more interview-ready."
    if score >= 55:
        return "Promising answer. Improve the structure and include a specific example or outcome."
    if score >= 40:
        return "Basic answer. It needs clearer context, actions, and results before an interview."
    if criteria["word_count"] < 20:
        return "The answer is too short for useful evaluation. Add a real example using the STAR method."
    return "The answer needs more relevance, structure, and concrete details."


def _strengths(criteria):
    strengths = []
    if criteria["relevance"] >= 65:
        strengths.append("Your answer stays connected to the selected question.")
    if criteria["structure"] >= 65:
        strengths.append("You show a clear situation, action, and result pattern.")
    if criteria["specificity"] >= 65:
        strengths.append("You include concrete actions, context, or measurable impact.")
    if criteria["communication"] >= 70:
        strengths.append("Your response length is suitable for an interview answer.")
    if not strengths:
        strengths.append("You made a start; now add context, action, and outcome.")
    return strengths[:3]


def _improvements(criteria, difficulty):
    improvements = []
    if criteria["relevance"] < 65:
        improvements.append("Use keywords from the question and answer the exact situation asked.")
    if criteria["structure"] < 65:
        improvements.append("Use STAR: Situation, Task, Action, Result.")
    if criteria["specificity"] < 65:
        improvements.append("Add a real project, number, tool, deadline, or measurable result.")
    if criteria["communication"] < 70:
        improvements.append(f"For a {difficulty} question, expand your answer with two or three clear sentences.")
    if not improvements:
        improvements.append("Practice saying this aloud in under two minutes.")
    return improvements[:3]
