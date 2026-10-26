import os
from functools import wraps

import jwt
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

load_dotenv()
db = SQLAlchemy()
migrate = Migrate()


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    ingredients = db.Column(db.Text, nullable=False, default="")
    instructions = db.Column(db.Text, nullable=False, default="")
    owner_id = db.Column(db.Integer, nullable=False, index=True)


def token_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify(error="Bearer token required"), 401
        token = header.split(" ", 1)[1].strip()
        secret = current_app_secret()
        if not secret:
            return jsonify(error="Authentication is not configured"), 500
        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            user_id = payload.get("user_id")
            if not isinstance(user_id, int):
                raise jwt.InvalidTokenError("user_id missing")
            g.user_id = user_id
        except jwt.ExpiredSignatureError:
            return jsonify(error="Token expired"), 401
        except jwt.InvalidTokenError:
            return jsonify(error="Invalid token"), 401
        return fn(*args, **kwargs)
    return wrapped


def current_app_secret():
    from flask import current_app
    return current_app.config.get("JWT_SECRET", "")


def recipe_json(recipe):
    return {
        "id": recipe.id,
        "title": recipe.title,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "owner_id": recipe.owner_id,
    }


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "RECIPES_DATABASE_URL", "sqlite:///recipes.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET"] = os.getenv("JWT_SECRET", "")
    app.config["TESTING"] = False
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.get("/health")
    def health():
        return jsonify(service="recipes", status="ok"), 200

    @app.get("/api/recipes")
    @token_required
    def list_recipes():
        recipes = Recipe.query.filter_by(owner_id=g.user_id).order_by(Recipe.id.desc()).all()
        return jsonify(recipes=[recipe_json(item) for item in recipes]), 200

    @app.post("/api/recipes")
    @token_required
    def create_recipe():
        data = request.get_json(silent=True) or {}
        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            return jsonify(error="title is required"), 400
        recipe = Recipe(
            title=title.strip(),
            ingredients=data.get("ingredients", ""),
            instructions=data.get("instructions", ""),
            owner_id=g.user_id,
        )
        db.session.add(recipe)
        db.session.commit()
        return jsonify(recipe_json(recipe)), 201

    @app.route("/api/recipes/<int:recipe_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
    @token_required
    def recipe_detail(recipe_id):
        recipe = db.session.get(Recipe, recipe_id)
        if recipe is None:
            return jsonify(error="Recipe not found"), 404
        if recipe.owner_id != g.user_id:
            return jsonify(error="You do not own this recipe"), 403
        if request.method == "GET":
            return jsonify(recipe_json(recipe)), 200
        if request.method == "DELETE":
            db.session.delete(recipe)
            db.session.commit()
            return jsonify(message="Recipe deleted"), 200
        data = request.get_json(silent=True) or {}
        if "title" in data:
            if not isinstance(data["title"], str) or not data["title"].strip():
                return jsonify(error="title cannot be empty"), 400
            recipe.title = data["title"].strip()
        if "ingredients" in data:
            recipe.ingredients = data["ingredients"]
        if "instructions" in data:
            recipe.instructions = data["instructions"]
        # owner_id is deliberately ignored: ownership always comes from the verified token.
        db.session.commit()
        return jsonify(recipe_json(recipe)), 200

    return app


app = create_app()

if __name__ == "__main__":
    if not app.config.get("JWT_SECRET"):
        raise RuntimeError("JWT_SECRET is required. Set it in the environment or .env file.")
    app.run(host="127.0.0.1", port=5002, debug=False)
