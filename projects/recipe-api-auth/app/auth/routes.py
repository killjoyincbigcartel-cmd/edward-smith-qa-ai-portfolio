"""Registration and login HTTP endpoints."""
from flask import Blueprint, jsonify, request

from app.auth.passwords import hash_password, verify_password
from app.auth.tokens import create_token
from app.data.models import User
from app.extensions import db

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not username.strip():
        return jsonify({"error": "Username is required"}), 400

    if not isinstance(password, str) or not password:
        return jsonify({"error": "Password is required"}), 400

    username = username.strip()
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409

    user = User(
        username=username,
        password_hash=hash_password(password),
        role="user",
    )
    db.session.add(user)
    db.session.commit()

    return jsonify(
        {
            "message": "User created",
            "username": user.username,
            "role": user.role,
        }
    ), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not username:
        return jsonify({"error": "Username and password are required"}), 400

    if not isinstance(password, str) or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not verify_password(user.password_hash, password):
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify(
        {
            "message": "Login successful",
            "username": user.username,
            "role": user.role,
            "token": create_token(user),
        }
    ), 200
