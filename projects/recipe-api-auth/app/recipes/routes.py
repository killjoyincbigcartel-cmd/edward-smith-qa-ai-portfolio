"""Recipe HTTP endpoints."""
from flask import Blueprint, g, jsonify, request

from app.auth.guards import authenticate_request, require_auth, require_owner_or_admin
from app.data import recipes as recipe_data
from app.recipes.policies import can_read_private_recipe
from app.services import recipe_service

recipes_bp = Blueprint("recipes", __name__)


@recipes_bp.get("/recipes/<int:recipe_id>")
def get_recipe(recipe_id):
    recipe = recipe_data.get_recipe(recipe_id)
    if recipe is None:
        return jsonify({"error": "Recipe not found"}), 404

    if not recipe.is_public:
        user, error_response = authenticate_request()
        if error_response:
            return error_response
        if not can_read_private_recipe(recipe, user):
            return jsonify({"error": "Forbidden"}), 403

    payload, status = recipe_service.get_recipe(recipe_id)
    return jsonify(payload), status


@recipes_bp.post("/recipes")
@require_auth
def create_recipe():
    data = request.get_json(silent=True) or {}
    payload, status = recipe_service.create_recipe(
        data.get("title"),
        data.get("is_public", False),
        g.current_user_id,
    )
    return jsonify(payload), status


@recipes_bp.patch("/recipes/<int:recipe_id>")
@require_owner_or_admin
def update_recipe(recipe_id):
    payload, status = recipe_service.update_recipe(
        g.recipe, request.get_json(silent=True) or {}
    )
    return jsonify(payload), status


@recipes_bp.delete("/recipes/<int:recipe_id>")
@require_owner_or_admin
def delete_recipe(recipe_id):
    payload, status = recipe_service.delete_recipe(g.recipe)
    return jsonify(payload), status


@recipes_bp.get("/api/recipes/count")
def recipe_count():
    """New endpoint: return the number of saved recipes."""
    payload, status = recipe_service.get_recipe_count()
    return jsonify(payload), status
