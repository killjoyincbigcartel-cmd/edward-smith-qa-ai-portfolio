"""Shared request authentication and recipe permission guards."""
from functools import wraps

from flask import g, jsonify, request

from app.data.models import Recipe, User
from app.extensions import db
from app.auth.tokens import decode_token


def get_bearer_token():
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None, (jsonify({"error": "Unauthorized"}), 401)

    token = auth_header.split(" ", 1)[1].strip()
    if not token:
        return None, (jsonify({"error": "Unauthorized"}), 401)

    return token, None


def authenticate_request():
    token, error_response = get_bearer_token()
    if error_response:
        return None, error_response

    payload = decode_token(token)
    if not payload:
        return None, (jsonify({"error": "Unauthorized"}), 401)

    user_id = payload.get("user_id")
    role = payload.get("role")
    if not user_id or not role:
        return None, (jsonify({"error": "Unauthorized"}), 401)

    user = db.session.get(User, user_id)
    if user is None:
        return None, (jsonify({"error": "Unauthorized"}), 401)

    # Use the role currently stored on the account, not client-provided data.
    g.current_user = user
    g.current_user_id = user.id
    g.current_role = user.role
    return user, None


def require_auth(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        _user, error_response = authenticate_request()
        if error_response:
            return error_response
        return route_function(*args, **kwargs)

    return wrapper


def require_owner_or_admin(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        _user, error_response = authenticate_request()
        if error_response:
            return error_response

        recipe = db.session.get(Recipe, kwargs.get("recipe_id"))
        if recipe is None:
            return jsonify({"error": "Recipe not found"}), 404

        if recipe.owner_id != g.current_user_id and g.current_role != "admin":
            return jsonify({"error": "Forbidden"}), 403

        g.recipe = recipe
        return route_function(*args, **kwargs)

    return wrapper
