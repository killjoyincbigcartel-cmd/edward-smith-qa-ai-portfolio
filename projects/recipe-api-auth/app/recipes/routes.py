"""Recipe HTTP endpoints."""
from flask import Blueprint, g, jsonify, request

from app.auth.guards import authenticate_request, require_auth, require_owner_or_admin
from app.data.models import Recipe
from app.extensions import db
from app.recipes.policies import can_read_private_recipe

recipes_bp = Blueprint("recipes", __name__)

def recipe_payload(recipe):
    return {
        "id": recipe.id,
        "title": recipe.title,
        "is_public": recipe.is_public,
        "owner_id": recipe.owner_id,
    }

@recipes_bp.get("/recipes/<int:recipe_id>")
def get_recipe(recipe_id):
    recipe = db.session.get(Recipe, recipe_id)
    if recipe is None:
        return jsonify({"error": "Recipe not found"}), 404

    if not recipe.is_public:
        user, error_response = authenticate_request()
        if error_response:
            return error_response
        if not can_read_private_recipe(recipe, user):
            return jsonify({"error": "Forbidden"}), 403

    return jsonify(recipe_payload(recipe)), 200

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

    recipe = Recipe(
        title=title.strip(),
        is_public=is_public,
        owner_id=g.current_user_id,
    )
    db.session.add(recipe)
    db.session.commit()

    return jsonify({
        "message": "Recipe created",
        "id": recipe.id,
        "title": recipe.title,
        "owner_id": recipe.owner_id,
    }), 201

@recipes_bp.patch("/recipes/<int:recipe_id>")
@require_owner_or_admin
def update_recipe(recipe_id):
    recipe = g.recipe
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
    return jsonify({
        "message": "Recipe updated",
        "id": recipe.id,
        "title": recipe.title,
        "is_public": recipe.is_public,
        "owner_id": recipe.owner_id,
    }), 200

@recipes_bp.delete("/recipes/<int:recipe_id>")
@require_owner_or_admin
def delete_recipe(recipe_id):
    recipe = g.recipe
    recipe_id = recipe.id
    db.session.delete(recipe)
    db.session.commit()
    return jsonify({"message": "Recipe deleted", "id": recipe_id}), 200
