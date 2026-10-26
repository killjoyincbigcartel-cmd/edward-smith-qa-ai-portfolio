"""Registration and login HTTP endpoints."""
from flask import Blueprint, jsonify, request

from app.extensions import limiter
from app.services.auth_service import login_user, register_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
@limiter.limit("3 per hour")
def register():
    data = request.get_json(silent=True) or {}
    payload, status = register_user(data.get("username"), data.get("password"))
    return jsonify(payload), status


@auth_bp.post("/login")
@limiter.limit("5 per minute")
def login():
    data = request.get_json(silent=True) or {}
    payload, status = login_user(data.get("username"), data.get("password"))
    return jsonify(payload), status
