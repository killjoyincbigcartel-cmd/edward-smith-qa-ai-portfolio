"""SQLAlchemy models for user accounts, recipes, and ratings."""
from app.extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    ratings = db.relationship(
        "Rating", back_populates="user", cascade="all, delete-orphan"
    )


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    is_public = db.Column(db.Boolean, nullable=False, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    ratings = db.relationship(
        "Rating", back_populates="recipe", cascade="all, delete-orphan"
    )


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    __table_args__ = (
        db.UniqueConstraint("user_id", "recipe_id", name="uq_rating_user_recipe"),
        db.CheckConstraint("score >= 1 AND score <= 5", name="ck_rating_score_range"),
    )
    user = db.relationship("User", back_populates="ratings")
    recipe = db.relationship("Recipe", back_populates="ratings")
