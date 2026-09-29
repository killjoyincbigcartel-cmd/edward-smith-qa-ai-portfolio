import os
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///recipe_api.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXP_MINUTES = int(os.getenv("JWT_EXP_MINUTES", "60"))

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET is required. Put it in .env.")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    is_public = db.Column(db.Boolean, nullable=False, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(stored_hash: str, candidate_password: str) -> bool:
    return check_password_hash(stored_hash, candidate_password)


def create_token(user: User) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXP_MINUTES)
    payload = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "exp": expires_at,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_bearer_token():
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None, (jsonify({"error": "Unauthorized"}), 401)

    token = auth_header.split(" ", 1)[1].strip()

    if not token:
        return None, (jsonify({"error": "Unauthorized"}), 401)

    return token, None


def require_auth(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        token, error_response = get_bearer_token()

        if error_response:
            return error_response

        try:
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM],
            )
        except jwt.PyJWTError:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = payload.get("user_id")
        role = payload.get("role")

        if not user_id or not role:
            return jsonify({"error": "Unauthorized"}), 401

        user = db.session.get(User, user_id)

        if user is None:
            return jsonify({"error": "Unauthorized"}), 401

        g.current_user = user
        g.current_user_id = user_id
        g.current_role = role

        return route_function(*args, **kwargs)

    return wrapper


def require_owner_or_admin(route_function):
    @wraps(route_function)
    @require_auth
    def wrapper(*args, **kwargs):
        recipe_id = kwargs.get("recipe_id")
        recipe = db.session.get(Recipe, recipe_id)

        if recipe is None:
            return jsonify({"error": "Recipe not found"}), 404

        if recipe.owner_id != g.current_user_id and g.current_role != "admin":
            return jsonify({"error": "Forbidden"}), 403

        g.recipe = recipe
        return route_function(*args, **kwargs)

    return wrapper


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.post("/register")
def register():
    data = request.get_json(silent=True) or {}

    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not username.strip():
        return jsonify({"error": "Username is required"}), 400

    if not isinstance(password, str) or not password:
        return jsonify({"error": "Password is required"}), 400

    username = username.strip()

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409

    user = User(
        username=username,
        password_hash=hash_password(password),
        role="user",
    )

    db.session.add(user)
    db.session.commit()

    return jsonify(
        {
            "message": "User created",
            "username": user.username,
            "role": user.role,
        }
    ), 201


@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not username:
        return jsonify({"error": "Username and password are required"}), 400

    if not isinstance(password, str) or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not verify_password(user.password_hash, password):
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify(
        {
            "message": "Login successful",
            "username": user.username,
            "role": user.role,
            "token": create_token(user),
        }
    ), 200


@app.get("/recipes/<int:recipe_id>")
def get_recipe(recipe_id):
    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None:
        return jsonify({"error": "Recipe not found"}), 404

    if recipe.is_public:
        return jsonify(
            {
                "id": recipe.id,
                "title": recipe.title,
                "is_public": recipe.is_public,
                "owner_id": recipe.owner_id,
            }
        ), 200

    token, error_response = get_bearer_token()

    if error_response:
        return error_response

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        return jsonify({"error": "Unauthorized"}), 401

    if payload.get("user_id") != recipe.owner_id:
        return jsonify({"error": "Forbidden"}), 403

    return jsonify(
        {
            "id": recipe.id,
            "title": recipe.title,
            "is_public": recipe.is_public,
            "owner_id": recipe.owner_id,
        }
    ), 200


@app.post("/recipes")
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

    return jsonify(
        {
            "message": "Recipe created",
            "id": recipe.id,
            "title": recipe.title,
            "owner_id": recipe.owner_id,
        }
    ), 201


@app.patch("/recipes/<int:recipe_id>")
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

    return jsonify(
        {
            "message": "Recipe updated",
            "id": recipe.id,
            "title": recipe.title,
            "is_public": recipe.is_public,
            "owner_id": recipe.owner_id,
        }
    ), 200


@app.delete("/recipes/<int:recipe_id>")
@require_owner_or_admin
def delete_recipe(recipe_id):
    recipe = g.recipe
    db.session.delete(recipe)
    db.session.commit()

    return jsonify({"message": "Recipe deleted", "id": recipe.id}), 200


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
