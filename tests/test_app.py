import unittest
import uuid
from pathlib import Path

from app import create_app


class InterviewAssistantTestCase(unittest.TestCase):
    def setUp(self):
        self.database_path = Path.cwd() / f".test_interview_{uuid.uuid4().hex}.sqlite3"
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": str(self.database_path),
                "SECRET_KEY": "test-secret",
                "WTF_CSRF_ENABLED": False,
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        if self.database_path.exists():
            self.database_path.unlink()

    def register_and_login(self):
        response = self.client.get("/register")
        csrf = self.extract_csrf(response.get_data(as_text=True))
        self.client.post(
            "/register",
            data={
                "csrf_token": csrf,
                "name": "Test User",
                "email": "test@example.com",
                "password": "password123",
            },
            follow_redirects=True,
        )

    def extract_csrf(self, html):
        marker = 'name="csrf-token" content="'
        start = html.index(marker) + len(marker)
        end = html.index('"', start)
        return html[start:end]

    def test_login_required_for_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_register_creates_account_and_home_loads(self):
        self.register_and_login()
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Practice interviews", response.data)

    def test_questions_api_requires_login(self):
        response = self.client.get("/api/questions")
        self.assertEqual(response.status_code, 401)

    def test_questions_api_returns_questions(self):
        self.register_and_login()
        response = self.client.get("/api/questions?category=HR+%2F+Behavioral&difficulty=Easy")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreater(len(data["questions"]), 0)

    def test_feedback_api_scores_and_saves_attempt(self):
        self.register_and_login()
        home = self.client.get("/")
        csrf = self.extract_csrf(home.get_data(as_text=True))
        response = self.client.post(
            "/api/feedback",
            json={
                "category": "HR / Behavioral",
                "difficulty": "Easy",
                "question": "Tell me about yourself.",
                "answer": (
                    "In my final year project, I built a Flask app with my team. "
                    "My task was to design the backend, so I created the routes, "
                    "tested the database flow, and improved response time by 20 percent. "
                    "The result was a working demo that our faculty accepted."
                ),
            },
            headers={"X-CSRFToken": csrf},
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("feedback", data)
        self.assertGreater(data["feedback"]["score"], 40)
        self.assertEqual(data["stats"]["total_attempts"], 1)

    def test_feedback_rejects_invalid_category(self):
        self.register_and_login()
        home = self.client.get("/")
        csrf = self.extract_csrf(home.get_data(as_text=True))
        response = self.client.post(
            "/api/feedback",
            json={
                "category": "Fake",
                "difficulty": "Easy",
                "question": "Tell me about yourself.",
                "answer": "A valid answer.",
            },
            headers={"X-CSRFToken": csrf},
        )
        self.assertEqual(response.status_code, 400)

    def test_health_check(self):
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")


if __name__ == "__main__":
    unittest.main()
