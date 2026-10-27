"""Users service: registration, login, JWT issuance, and identity lookup."""
import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv(
            "USERS_DATABASE_URL", "sqlite:///users.db"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET=os.getenv("JWT_SECRET", ""),
        JWT_EXP_MINUTES=int(os.getenv("JWT_EXP_MINUTES", "60")),
        INTERNAL_SERVICE_TOKEN=os.getenv("INTERNAL_SERVICE_TOKEN", ""),
    )
    if test_config:
        app.config.update(test_config)
    if not app.config["JWT_SECRET"]:
        raise RuntimeError("JWT_SECRET is required for the users service.")
    db.init_app(app)

    from .routes import users_bp
    app.register_blueprint(users_bp)

    with app.app_context():
        db.create_all()
    return app


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")


def create_token(user, secret, expiry_minutes):
    expires = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
    return jwt.encode(
        {"user_id": user.id, "username": user.username, "role": user.role, "exp": expires},
        secret,
        algorithm="HS256",
    )


def verify_user_token(token, secret):
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    if not payload.get("user_id") or not payload.get("role"):
        return None
    return payload
