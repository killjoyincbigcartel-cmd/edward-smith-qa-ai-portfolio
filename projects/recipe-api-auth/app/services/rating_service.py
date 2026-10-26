"""Business logic for creating, updating, and reading recipe ratings."""
from sqlalchemy import func

from app.data.models import Rating, Recipe
from app.extensions import db


def save_rating(user_id, recipe_id, score):
    if type(score) is not int or not 1 <= score <= 5:
        return {"error": "Score must be an integer from 1 to 5"}, 400

    recipe = db.session.get(Recipe, recipe_id)
    if recipe is None:
        return {"error": "Recipe not found"}, 404

    rating = Rating.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
    if rating is None:
        rating = Rating(user_id=user_id, recipe_id=recipe_id, score=score)
        db.session.add(rating)
    else:
        rating.score = score

    db.session.commit()
    return {
        "message": "Rating saved",
        "recipe_id": recipe_id,
        "score": rating.score,
    }, 200


def get_recipe_ratings(recipe_id):
    if db.session.get(Recipe, recipe_id) is None:
        return {"error": "Recipe not found"}, 404

    average, count = db.session.query(
        func.avg(Rating.score), func.count(Rating.id)
    ).filter(Rating.recipe_id == recipe_id).one()

    return {
        "recipe_id": recipe_id,
        "average_rating": round(average, 2) if average is not None else None,
        "rating_count": count,
    }, 200
