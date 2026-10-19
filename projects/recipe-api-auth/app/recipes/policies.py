"""Recipe visibility and mutation permission rules."""
from app.data.models import Recipe, User

def can_read_private_recipe(recipe: Recipe, user: User) -> bool:
    return recipe.owner_id == user.id

def can_manage_recipe(recipe: Recipe, user: User) -> bool:
    return recipe.owner_id == user.id or user.role == "admin"
