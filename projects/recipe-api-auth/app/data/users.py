"""Persistence helpers for user accounts."""
from app.data.models import User
from app.extensions import db


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def create_user(username, password_hash, role="user"):
    user = User(username=username, password_hash=password_hash, role=role)
    db.session.add(user)
    db.session.commit()
    return user
