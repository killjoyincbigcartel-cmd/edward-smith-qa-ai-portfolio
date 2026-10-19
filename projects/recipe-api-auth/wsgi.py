"""WSGI/Flask CLI entry point.

Run `flask --app wsgi run` from this project directory. Importing `app`
alone does not create tables; starting through this entry point retains the
project's original first-run database initialization behavior.
"""
from app import app
from app.extensions import db

with app.app_context():
    db.create_all()
