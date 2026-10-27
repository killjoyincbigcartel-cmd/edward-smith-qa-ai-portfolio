"""HTTP routes for user accounts and token validation."""
import jwt
from flask import Blueprint, current_app, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from . import User, create_token, db

users_bp = Blueprint("users", __name__)


def _bearer():
    header = request.headers.get("Authorization", "")
    if not header.lower().startswith("bearer ") or not header[7:].strip():
        return None
    return header[7:].strip()


@users_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "users"}), 200


@users_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    username, password = data.get("username"), data.get("password")
    if not isinstance(username, str) or not username.strip():
        return jsonify({"error": "Username is required"}), 400
    if not isinstance(password, str) or not password:
        return jsonify({"error": "Password is required"}), 400
    username = username.strip()
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409
    user = User(username=username, password_hash=generate_password_hash(password), role="user")
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created", "username": user.username, "role": user.role}), 201


@users_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username, password = data.get("username"), data.get("password")
    if not isinstance(username, str) or not username:
        return jsonify({"error": "Username and password are required"}), 400
    if not isinstance(password, str) or not password:
        return jsonify({"error": "Username and password are required"}), 400
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid username or password"}), 401
    return jsonify({
        "message": "Login successful",
        "username": user.username,
        "role": user.role,
        "token": create_token(user, current_app.config["JWT_SECRET"], current_app.config["JWT_EXP_MINUTES"]),
    }), 200


@users_bp.get("/me")
def me():
    token = _bearer()
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        payload = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
    except jwt.PyJWTError:
        return jsonify({"error": "Unauthorized"}), 401
    user = db.session.get(User, payload.get("user_id"))
    if user is None:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"id": user.id, "username": user.username, "role": user.role}), 200


@users_bp.get("/internal/health")
def internal_health():
    from hmac import compare_digest
    expected = current_app.config["INTERNAL_SERVICE_TOKEN"]
    supplied = request.headers.get("X-Internal-Token", "")
    if not expected or not compare_digest(supplied, expected):
        return jsonify({"error": "Internal access denied"}), 403
    return jsonify({"message": "Access granted", "service": "users"}), 200
