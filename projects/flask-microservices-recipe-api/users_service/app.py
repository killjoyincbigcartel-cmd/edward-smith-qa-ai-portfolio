import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()
db = SQLAlchemy()
migrate = Migrate()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "USERS_DATABASE_URL", "sqlite:///users.db"
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
        return jsonify(service="users", status="ok"), 200

    @app.post("/api/auth/register")
    def register():
        data = request.get_json(silent=True) or {}
        username = data.get("username")
        password = data.get("password")
        if not isinstance(username, str) or not username.strip() or not isinstance(password, str) or not password:
            return jsonify(error="username and password are required"), 400
        username = username.strip()
        if User.query.filter_by(username=username).first():
            return jsonify(error="Username already exists"), 409
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return jsonify(id=user.id, username=user.username), 201

    @app.post("/api/auth/login")
    def login():
        data = request.get_json(silent=True) or {}
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return jsonify(error="username and password are required"), 400
        user = User.query.filter_by(username=username.strip()).first() if isinstance(username, str) else None
        if not user or not isinstance(password, str) or not check_password_hash(user.password_hash, password):
            return jsonify(error="Invalid username or password"), 401
        secret = app.config.get("JWT_SECRET")
        if not secret:
            app.logger.error("JWT_SECRET is missing")
            return jsonify(error="Authentication is not configured"), 500
        now = datetime.now(timezone.utc)
        token = jwt.encode(
            {"user_id": user.id, "iat": now, "exp": now + timedelta(hours=1)},
            secret,
            algorithm="HS256",
        )
        return jsonify(access_token=token, token_type="Bearer", expires_in=3600), 200

    return app


app = create_app()

if __name__ == "__main__":
    if not app.config.get("JWT_SECRET"):
        raise RuntimeError("JWT_SECRET is required. Set it in the environment or .env file.")
    app.run(host="127.0.0.1", port=5001, debug=False)
