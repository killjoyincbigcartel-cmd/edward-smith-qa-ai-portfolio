"""Persistence helpers for recipes."""
from sqlalchemy import func

from app.data.models import Recipe
from app.extensions import db


def get_recipe(recipe_id):
    return db.session.get(Recipe, recipe_id)


def create_recipe(title, is_public, owner_id):
    recipe = Recipe(title=title, is_public=is_public, owner_id=owner_id)
    db.session.add(recipe)
    db.session.commit()
    return recipe


def save_recipe(recipe):
    db.session.commit()
    return recipe


def delete_recipe(recipe):
    db.session.delete(recipe)
    db.session.commit()


def count_recipes():
    return db.session.query(func.count(Recipe.id)).scalar() or 0
