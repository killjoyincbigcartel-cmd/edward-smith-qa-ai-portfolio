from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app import JWT_ALGORITHM, Recipe, User, create_app, db, hash_password

TEST_SECRET = "test-secret-that-is-long-enough"


@pytest.fixture()
def client():
    test_app = create_app(
        "testing",
        config_overrides={"JWT_SECRET": TEST_SECRET},
    )

    with test_app.app_context():
        db.create_all()

        owner = User(
            username="owner",
            password_hash=hash_password("OwnerPass123!"),
            role="user",
        )
        stranger = User(
            username="stranger",
            password_hash=hash_password("StrangerPass123!"),
            role="user",
        )
        admin = User(
            username="admin",
            password_hash=hash_password("AdminPass123!"),
            role="admin",
        )

        db.session.add_all([owner, stranger, admin])
        db.session.commit()

        recipe = Recipe(
            title="Original Recipe",
            is_public=False,
            owner_id=owner.id,
        )
        db.session.add(recipe)
        db.session.commit()

        ids = (owner.id, stranger.id, admin.id, recipe.id)

    yield test_app.test_client(), test_app, *ids

    with test_app.app_context():
        db.session.remove()
        db.drop_all()


def auth_header(user_id, username, role, expired=False):
    expiration = datetime.now(timezone.utc) + timedelta(
        minutes=-1 if expired else 10
    )

    token = jwt.encode(
        {
            "user_id": user_id,
            "username": username,
            "role": role,
            "exp": expiration,
        },
        TEST_SECRET,
        algorithm=JWT_ALGORITHM,
    )

    return {"Authorization": f"Bearer {token}"}


def test_factory_creates_independent_app_instances():
    app_dev = create_app("development", config_overrides={"JWT_SECRET": TEST_SECRET})
    app_test = create_app("testing", config_overrides={"JWT_SECRET": TEST_SECRET})

    assert app_dev is not app_test
    assert app_dev.config["DEBUG"] is True
    assert app_test.config["DEBUG"] is False
    assert app_test.config["TESTING"] is True


def test_missing_token_is_401(client):
    test_client, _test_app, _owner_id, _stranger_id, _admin_id, recipe_id = client
    response = test_client.delete(f"/recipes/{recipe_id}")
    assert response.status_code == 401


def test_expired_token_is_401(client):
    test_client, _test_app, owner_id, _stranger_id, _admin_id, recipe_id = client
    response = test_client.delete(
        f"/recipes/{recipe_id}",
        headers=auth_header(owner_id, "owner", "user", expired=True),
    )
    assert response.status_code == 401


def test_owner_can_update(client):
    test_client, test_app, owner_id, _stranger_id, _admin_id, recipe_id = client
    response = test_client.patch(
        f"/recipes/{recipe_id}",
        headers=auth_header(owner_id, "owner", "user"),
        json={"title": "Owner Updated"},
    )

    assert response.status_code == 200

    with test_app.app_context():
        recipe = db.session.get(Recipe, recipe_id)
        assert recipe.title == "Owner Updated"


def test_non_owner_gets_403_and_database_stays_unchanged(client):
    test_client, test_app, _owner_id, stranger_id, _admin_id, recipe_id = client

    response = test_client.patch(
        f"/recipes/{recipe_id}",
        headers=auth_header(stranger_id, "stranger", "user"),
        json={"title": "Unauthorized Change"},
    )

    assert response.status_code == 403

    with test_app.app_context():
        recipe = db.session.get(Recipe, recipe_id)
        assert recipe.title == "Original Recipe"


def test_admin_can_delete_other_users_recipe(client):
    test_client, test_app, _owner_id, _stranger_id, admin_id, recipe_id = client

    response = test_client.delete(
        f"/recipes/{recipe_id}",
        headers=auth_header(admin_id, "admin", "admin"),
    )

    assert response.status_code == 200

    with test_app.app_context():
        assert db.session.get(Recipe, recipe_id) is None


def test_health_contract(client):
    test_client = client[0]
    response = test_client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_register_and_login_contract(client):
    test_client = client[0]

    register_response = test_client.post(
        "/register",
        json={"username": "new-account", "password": "NewAccountPass123!"},
    )
    assert register_response.status_code == 201
    assert register_response.get_json() == {
        "message": "User created",
        "username": "new-account",
        "role": "user",
    }

    login_response = test_client.post(
        "/login",
        json={"username": "new-account", "password": "NewAccountPass123!"},
    )
    login_data = login_response.get_json()

    assert login_response.status_code == 200
    assert login_data["message"] == "Login successful"
    assert login_data["username"] == "new-account"
    assert login_data["role"] == "user"
    assert isinstance(login_data["token"], str) and login_data["token"]
    assert "password" not in login_data
    assert "password_hash" not in login_data


def test_public_recipe_can_be_read_without_token(client):
    test_client, test_app, _owner_id, _stranger_id, _admin_id, recipe_id = client

    with test_app.app_context():
        recipe = db.session.get(Recipe, recipe_id)
        recipe.is_public = True
        db.session.commit()

    response = test_client.get(f"/recipes/{recipe_id}")

    assert response.status_code == 200
    assert response.get_json() == {
        "id": recipe_id,
        "title": "Original Recipe",
        "is_public": True,
        "owner_id": client[2],
    }
