import os
from datetime import datetime, timedelta, timezone

import jwt
import pytest

os.environ["JWT_SECRET"] = "test-secret-that-is-long-enough"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import JWT_ALGORITHM, JWT_SECRET, Recipe, User, app, db, hash_password


@pytest.fixture()
def client():
    app.config.update(TESTING=True)

    with app.app_context():
        db.drop_all()
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

        yield app.test_client(), owner.id, stranger.id, admin.id, recipe.id


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
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

    return {"Authorization": f"Bearer {token}"}


def test_missing_token_is_401(client):
    test_client, _, _, _, recipe_id = client
    response = test_client.delete(f"/recipes/{recipe_id}")
    assert response.status_code == 401


def test_expired_token_is_401(client):
    test_client, owner_id, _, _, recipe_id = client
    response = test_client.delete(
        f"/recipes/{recipe_id}",
        headers=auth_header(owner_id, "owner", "user", expired=True),
    )
    assert response.status_code == 401


def test_owner_can_update(client):
    test_client, owner_id, _, _, recipe_id = client
    response = test_client.patch(
        f"/recipes/{recipe_id}",
        headers=auth_header(owner_id, "owner", "user"),
        json={"title": "Owner Updated"},
    )

    assert response.status_code == 200

    with app.app_context():
        recipe = db.session.get(Recipe, recipe_id)
        assert recipe.title == "Owner Updated"


def test_non_owner_gets_403_and_database_stays_unchanged(client):
    test_client, _, stranger_id, _, recipe_id = client

    response = test_client.patch(
        f"/recipes/{recipe_id}",
        headers=auth_header(stranger_id, "stranger", "user"),
        json={"title": "Unauthorized Change"},
    )

    assert response.status_code == 403

    with app.app_context():
        recipe = db.session.get(Recipe, recipe_id)
        assert recipe.title == "Original Recipe"


def test_admin_can_delete_other_users_recipe(client):
    test_client, _, _, admin_id, recipe_id = client

    response = test_client.delete(
        f"/recipes/{recipe_id}",
        headers=auth_header(admin_id, "admin", "admin"),
    )

    assert response.status_code == 200

    with app.app_context():
        assert db.session.get(Recipe, recipe_id) is None
