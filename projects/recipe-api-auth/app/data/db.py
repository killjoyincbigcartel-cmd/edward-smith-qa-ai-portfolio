"""Database initialization helpers."""
from app.extensions import db


def init_db(app):
    """Create missing tables using the database configured on this app.

    SQLAlchemy's create_all is safe to call repeatedly: existing tables are
    left in place, and the app's SQLALCHEMY_DATABASE_URI selects the database.
    """
    with app.app_context():
        db.create_all()
