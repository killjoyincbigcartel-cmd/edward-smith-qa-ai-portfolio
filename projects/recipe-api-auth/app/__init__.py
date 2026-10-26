"""Flask application factory and shared public imports."""
from flask import Flask

from app.auth.passwords import hash_password, verify_password
from app.auth.routes import auth_bp
from app.auth.tokens import create_token
from app.config import CONFIG_BY_NAME, Config
from app.data.db import init_db
from app.data.models import Rating, Recipe, User
from app.extensions import db, limiter, migrate
from app.recipes.routes import recipes_bp
from app.web.routes import web_bp

JWT_ALGORITHM = Config.JWT_ALGORITHM
JWT_SECRET = Config.JWT_SECRET


def create_app(config_name="development", config_overrides=None):
    """Build and return a separately configured Flask app instance."""
    try:
        config_class = CONFIG_BY_NAME[config_name]
    except (KeyError, TypeError):
        supported = ", ".join(sorted(CONFIG_BY_NAME))
        raise ValueError(
            f"Unknown config_name {config_name!r}. Choose one of: {supported}"
        ) from None

    flask_app = Flask(__name__, instance_relative_config=True)
    flask_app.config.from_object(config_class)
    if config_overrides:
        flask_app.config.update(config_overrides)

    if not flask_app.config.get("JWT_SECRET"):
        raise RuntimeError("JWT_SECRET is required. Put it in .env.")

    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    limiter.init_app(flask_app)
    flask_app.register_blueprint(web_bp)
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(recipes_bp)

    # Preserve existing startup behavior while enabling versioned migrations.
    init_db(flask_app)
    return flask_app


__all__ = [
    "JWT_ALGORITHM", "JWT_SECRET", "Rating", "Recipe", "User",
    "create_app", "create_token", "db", "hash_password", "verify_password",
]
