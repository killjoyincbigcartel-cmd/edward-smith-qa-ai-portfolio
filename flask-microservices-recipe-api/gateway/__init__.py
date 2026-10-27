"""Flask application factory for the API gateway."""
import os
from dotenv import load_dotenv
from flask import Flask


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__)
    app.config.update(
        USERS_SERVICE_URL=os.getenv("USERS_SERVICE_URL", "http://localhost:5001").rstrip("/"),
        RECIPES_SERVICE_URL=os.getenv("RECIPES_SERVICE_URL", "http://localhost:5002").rstrip("/"),
        RECIPES_INTERNAL_TOKEN=os.getenv("RECIPES_INTERNAL_TOKEN", ""),
        UPSTREAM_TIMEOUT=float(os.getenv("UPSTREAM_TIMEOUT", "1.5")),
    )
    if test_config:
        app.config.update(test_config)
    from .routes import gateway_bp
    app.register_blueprint(gateway_bp)
    return app
