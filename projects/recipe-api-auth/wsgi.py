"""WSGI/Flask CLI entry point.

Run `flask --app wsgi run` from the recipe-api-auth project directory.
The entry point builds the development app and initializes its database.
"""
from app import create_app
from app.extensions import db

app = create_app("development")

if not app.config.get("JWT_SECRET"):
    raise RuntimeError("JWT_SECRET is required. Put it in .env.")

with app.app_context():
    db.create_all()
