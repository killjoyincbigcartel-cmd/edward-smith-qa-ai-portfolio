"""Recipe routes with JWT auth, internal-token checks, and cache invalidation."""
import hmac
from functools import wraps

import jwt
from flask import Blueprint, current_app, g, jsonify, request

from . import Recipe, cache, db

recipes_bp = Blueprint("recipes", __name__)


def _payload_from_request():
    header = request.headers.get("Authorization", "")
    if not header.lower().startswith("bearer ") or not header[7:].strip():
        return None
    try:
        payload = jwt.decode(header[7:].strip(), current_app.config["JWT_SECRET"], algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    if not payload.get("user_id") or not payload.get("role"):
        return None
    return payload


def require_auth(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        payload = _payload_from_request()
        if not payload:
            return jsonify({"error": "Unauthorized"}), 401
        g.user_id = payload["user_id"]
        g.role = payload["role"]
        return fn(*args, **kwargs)
    return wrapped


def require_internal(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        expected = current_app.config["INTERNAL_SERVICE_TOKEN"]
        supplied = request.headers.get("X-Internal-Token", "")
        if not expected or not hmac.compare_digest(supplied, expected):
            return jsonify({"error": "Internal access denied"}), 403
        return fn(*args, **kwargs)
    return wrapped


def _recipe_json(recipe):
    return {"id": recipe.id, "title": recipe.title, "is_public": recipe.is_public, "owner_id": recipe.owner_id}


def _owner_or_admin(recipe):
    if recipe.owner_id != g.user_id and g.role != "admin":
        return jsonify({"error": "Forbidden"}), 403
    return None


@recipes_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "recipes"}), 200


@recipes_bp.get("/internal/health")
@require_internal
def internal_health():
    return jsonify({"message": "Access granted", "service": "recipes"}), 200


@recipes_bp.get("/internal/recipes/summary")
@require_internal
@require_auth
def internal_summary():
    recipes = Recipe.query.filter(
        (Recipe.is_public.is_(True)) | (Recipe.owner_id == g.user_id)
    ).order_by(Recipe.id.asc()).all()
    return jsonify([_recipe_json(recipe) for recipe in recipes]), 200


@recipes_bp.get("/recipes")
@cache.cached(timeout=30, query_string=True)
def list_recipes():
    recipes = Recipe.query.filter_by(is_public=True).order_by(Recipe.id.asc()).all()
    return jsonify([_recipe_json(recipe) for recipe in recipes]), 200


@recipes_bp.get("/recipes/<int:recipe_id>")
def get_recipe(recipe_id):
    recipe = db.session.get(Recipe, recipe_id)
    if recipe is None:
        return jsonify({"error": "Recipe not found"}), 404
    if recipe.is_public:
        return jsonify(_recipe_json(recipe)), 200
    payload = _payload_from_request()
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401
    if payload["user_id"] != recipe.owner_id:
        return jsonify({"error": "Forbidden"}), 403
    return jsonify(_recipe_json(recipe)), 200


@recipes_bp.post("/recipes")
@require_auth
def create_recipe():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    is_public = data.get("is_public", False)
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Title is required"}), 400
    if not isinstance(is_public, bool):
        return jsonify({"error": "is_public must be a boolean"}), 400
    recipe = Recipe(title=title.strip(), is_public=is_public, owner_id=g.user_id)
    db.session.add(recipe)
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Recipe created", "id": recipe.id, "title": recipe.title, "owner_id": recipe.owner_id}), 201


@recipes_bp.patch("/recipes/<int:recipe_id>")
@require_auth
def update_recipe(recipe_id):
    recipe = db.session.get(Recipe, recipe_id)
    if recipe is None:
        return jsonify({"error": "Recipe not found"}), 404
    denied = _owner_or_admin(recipe)
    if denied:
        return denied
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    is_public = data.get("is_public")
    if title is not None:
        if not isinstance(title, str) or not title.strip():
            return jsonify({"error": "Title must be a non-empty string"}), 400
        recipe.title = title.strip()
    if is_public is not None:
        if not isinstance(is_public, bool):
            return jsonify({"error": "is_public must be a boolean"}), 400
        recipe.is_public = is_public
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Recipe updated", **_recipe_json(recipe)}), 200


@recipes_bp.delete("/recipes/<int:recipe_id>")
@require_auth
def delete_recipe(recipe_id):
    recipe = db.session.get(Recipe, recipe_id)
    if recipe is None:
        return jsonify({"error": "Recipe not found"}), 404
    denied = _owner_or_admin(recipe)
    if denied:
        return denied
    recipe_id = recipe.id
    db.session.delete(recipe)
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Recipe deleted", "id": recipe_id}), 200
