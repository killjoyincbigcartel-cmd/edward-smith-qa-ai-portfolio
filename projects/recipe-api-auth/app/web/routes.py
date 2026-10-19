"""Health and service status endpoints."""
from flask import Blueprint, jsonify

web_bp = Blueprint("web", __name__)

@web_bp.get("/health")
def health():
    return jsonify({"status": "ok"}), 200
