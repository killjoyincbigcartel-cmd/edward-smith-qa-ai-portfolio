"""Recipe business logic, separate from HTTP and persistence."""
from app.data import recipes as recipe_data


def recipe_payload(recipe):
    return {
        "id": recipe.id,
        "title": recipe.title,
        "is_public": recipe.is_public,
        "owner_id": recipe.owner_id,
    }


def get_recipe(recipe_id):
    recipe = recipe_data.get_recipe(recipe_id)
    if recipe is None:
        return {"error": "Recipe not found"}, 404
    return recipe_payload(recipe), 200


def create_recipe(title, is_public, owner_id):
    if not isinstance(title, str) or not title.strip():
        return {"error": "Title is required"}, 400
    if not isinstance(is_public, bool):
        return {"error": "is_public must be a boolean"}, 400

    recipe = recipe_data.create_recipe(title.strip(), is_public, owner_id)
    return {
        "message": "Recipe created",
        "id": recipe.id,
        "title": recipe.title,
        "owner_id": recipe.owner_id,
    }, 201


def update_recipe(recipe, data):
    title = data.get("title")
    is_public = data.get("is_public")

    if title is not None:
        if not isinstance(title, str) or not title.strip():
            return {"error": "Title must be a non-empty string"}, 400
    if is_public is not None and not isinstance(is_public, bool):
        return {"error": "is_public must be a boolean"}, 400

    if title is not None:
        recipe.title = title.strip()
    if is_public is not None:
        recipe.is_public = is_public

    recipe_data.save_recipe(recipe)
    return {
        "message": "Recipe updated",
        "id": recipe.id,
        "title": recipe.title,
        "is_public": recipe.is_public,
        "owner_id": recipe.owner_id,
    }, 200


def delete_recipe(recipe):
    recipe_id = recipe.id
    recipe_data.delete_recipe(recipe)
    return {"message": "Recipe deleted", "id": recipe_id}, 200


def get_recipe_count():
    return {"count": recipe_data.count_recipes()}, 200
