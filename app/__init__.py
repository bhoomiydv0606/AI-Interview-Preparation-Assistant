from pathlib import Path

from flask import Flask, jsonify, render_template, request

from app.auth_helpers import current_user
from app.config import Config
from app.db import close_db, init_db
from app.security import get_csrf_token


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    app.teardown_appcontext(close_db)

    from app.routes.api import api_bp
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.services.keep_alive import start_keep_alive

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.context_processor
    def inject_globals():
        return {
            "current_user": current_user(),
            "csrf_token": get_csrf_token,
        }

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=()",
        )
        return response

    @app.errorhandler(400)
    def bad_request(error):
        return _handle_error(400, "Bad request", str(error))

    @app.errorhandler(401)
    def unauthorized(error):
        return _handle_error(401, "Please log in to continue.", str(error))

    @app.errorhandler(404)
    def not_found(error):
        return _handle_error(404, "Page not found", str(error))

    @app.errorhandler(413)
    def request_too_large(error):
        return _handle_error(413, "The submitted content is too large.", str(error))

    @app.errorhandler(500)
    def server_error(error):
        return _handle_error(500, "Something went wrong", str(error))

    def _handle_error(status_code, message, detail):
        if request.path.startswith("/api/"):
            return jsonify({"error": message, "detail": detail}), status_code
        return render_template(
            "errors/error.html",
            status_code=status_code,
            message=message,
        ), status_code

    with app.app_context():
        init_db()

    start_keep_alive(app)

    return app


_wsgi_app = None


def app(environ, start_response):
    """Compatibility entry point for hosts still running `gunicorn app:app`."""
    global _wsgi_app
    if _wsgi_app is None:
        _wsgi_app = create_app()
    return _wsgi_app(environ, start_response)
