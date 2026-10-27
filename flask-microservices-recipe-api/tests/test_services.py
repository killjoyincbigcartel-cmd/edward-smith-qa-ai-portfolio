import jwt

from users_service import create_app as create_users_app
from recipes_service import Recipe, create_app as create_recipes_app, db as recipes_db


def test_users_registration_and_login_contract():
    app = create_users_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET": "test-jwt-secret",
        "JWT_EXP_MINUTES": 60,
    })
    client = app.test_client()
    created = client.post("/register", json={"username": "alice", "password": "example-password"})
    assert created.status_code == 201
    assert created.get_json() == {"message": "User created", "username": "alice", "role": "user"}
    duplicate = client.post("/register", json={"username": "alice", "password": "example-password"})
    assert duplicate.status_code == 409
    logged_in = client.post("/login", json={"username": "alice", "password": "example-password"})
    assert logged_in.status_code == 200
    body = logged_in.get_json()
    assert body["username"] == "alice"
    assert body["role"] == "user"
    assert body["token"]
    assert "password" not in body and "password_hash" not in body


def test_recipes_internal_endpoint_rejects_missing_and_wrong_internal_token():
    app = create_recipes_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET": "test-jwt-secret",
        "INTERNAL_SERVICE_TOKEN": "expected-internal-token",
    })
    client = app.test_client()
    missing = client.get("/internal/health")
    wrong = client.get("/internal/health", headers={"X-Internal-Token": "wrong"})
    assert missing.status_code == 403
    assert missing.get_json() == {"error": "Internal access denied"}
    assert wrong.status_code == 403
    assert wrong.get_json() == {"error": "Internal access denied"}


def test_recipes_cache_is_invalidated_after_update():
    secret = "test-jwt-secret"
    app = create_recipes_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET": secret,
        "INTERNAL_SERVICE_TOKEN": "expected-internal-token",
        "CACHE_DEFAULT_TIMEOUT": 30,
    })
    with app.app_context():
        recipes_db.session.add(Recipe(title="Original", is_public=True, owner_id=1))
        recipes_db.session.commit()
        recipe_id = Recipe.query.first().id
    token = jwt.encode({"user_id": 1, "username": "alice", "role": "user"}, secret, algorithm="HS256")
    client = app.test_client()
    first = client.get("/recipes")
    assert first.status_code == 200
    assert first.get_json()[0]["title"] == "Original"
    updated = client.patch(
        f"/recipes/{recipe_id}",
        json={"title": "Updated"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert updated.status_code == 200
    after = client.get("/recipes")
    assert after.status_code == 200
    assert after.get_json()[0]["title"] == "Updated"
