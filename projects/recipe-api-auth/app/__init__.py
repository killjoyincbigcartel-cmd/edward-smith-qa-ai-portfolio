"""Flask app factory and compatibility exports for the recipe API."""
from flask import Flask

from app.auth.passwords import hash_password, verify_password
from app.auth.routes import auth_bp
from app.auth.tokens import create_token
from app.config import Config
from app.data.models import Recipe, User
from app.extensions import db
from app.recipes.routes import recipes_bp
from app.web.routes import web_bp

# Keep these names available for existing scripts and tests using `from app import ...`.
JWT_ALGORITHM = Config.JWT_ALGORITHM
JWT_SECRET = Config.JWT_SECRET

def create_app(config_overrides=None):
    """Create and configure an app without creating tables at import time."""
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)
    if config_overrides:
        flask_app.config.update(config_overrides)
    db.init_app(flask_app)
    flask_app.register_blueprint(web_bp)
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(recipes_bp)
    return flask_app

app = create_app()

__all__ = [
    "JWT_ALGORITHM", "JWT_SECRET", "Recipe", "User", "app", "create_app",
    "create_token", "db", "hash_password", "verify_password",
]
