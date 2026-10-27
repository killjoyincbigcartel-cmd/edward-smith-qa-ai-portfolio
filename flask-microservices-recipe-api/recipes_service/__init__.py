"""Recipes service: recipe data, ownership, and internal service boundary."""
import os
from dotenv import load_dotenv
from flask import Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
cache = Cache()


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv(
            "RECIPES_DATABASE_URL", "sqlite:///recipes.db"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        CACHE_TYPE="SimpleCache",
        CACHE_DEFAULT_TIMEOUT=30,
        JWT_SECRET=os.getenv("JWT_SECRET", ""),
        INTERNAL_SERVICE_TOKEN=os.getenv("INTERNAL_SERVICE_TOKEN", ""),
    )
    if test_config:
        app.config.update(test_config)
    if not app.config["JWT_SECRET"]:
        raise RuntimeError("JWT_SECRET is required for the recipes service.")
    db.init_app(app)
    cache.init_app(app)

    from .routes import recipes_bp
    app.register_blueprint(recipes_bp)

    with app.app_context():
        db.create_all()
    return app


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    is_public = db.Column(db.Boolean, nullable=False, default=False)
    owner_id = db.Column(db.Integer, nullable=False, index=True)
