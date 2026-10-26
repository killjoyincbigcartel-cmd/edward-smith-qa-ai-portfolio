from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app import JWT_ALGORITHM, Rating, Recipe, User, create_app, db, hash_password

TEST_SECRET = "test-secret-that-is-long-enough"


@pytest.fixture()
def rating_client():
    app = create_app("testing", config_overrides={"JWT_SECRET": TEST_SECRET})
    with app.app_context():
        db.create_all()
        owner = User(username="rating-owner", password_hash=hash_password("OwnerPass123!"))
        voter = User(username="rating-voter", password_hash=hash_password("VoterPass123!"))
        db.session.add_all([owner, voter])
        db.session.commit()
        recipe = Recipe(title="Rated Recipe", is_public=True, owner_id=owner.id)
        db.session.add(recipe)
        db.session.commit()
        ids = (owner.id, voter.id, recipe.id)

    yield app.test_client(), app, *ids

    with app.app_context():
        db.session.remove()
        db.drop_all()


def make_auth(user_id, username):
    token = jwt.encode(
        {
            "user_id": user_id,
            "username": username,
            "role": "user",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
        },
        TEST_SECRET,
        algorithm=JWT_ALGORITHM,
    )
    return {"Authorization": f"Bearer {token}"}


def test_rating_post_and_read_average(rating_client):
    client, _app, _owner_id, voter_id, recipe_id = rating_client
    response = client.post(
        f"/api/recipes/{recipe_id}/ratings",
        headers=make_auth(voter_id, "rating-voter"),
        json={"score": 5},
    )
    assert response.status_code == 200
    assert response.get_json()["score"] == 5

    read = client.get(f"/api/recipes/{recipe_id}/ratings")
    assert read.status_code == 200
    assert read.get_json() == {
        "recipe_id": recipe_id,
        "average_rating": 5.0,
        "rating_count": 1,
    }


def test_user_updates_existing_rating_instead_of_duplicating(rating_client):
    client, app, _owner_id, voter_id, recipe_id = rating_client
    headers = make_auth(voter_id, "rating-voter")
    client.post(f"/api/recipes/{recipe_id}/ratings", headers=headers, json={"score": 5})
    response = client.post(
        f"/api/recipes/{recipe_id}/ratings", headers=headers, json={"score": 3}
    )
    assert response.status_code == 200
    assert response.get_json()["score"] == 3
    with app.app_context():
        assert Rating.query.filter_by(user_id=voter_id, recipe_id=recipe_id).count() == 1


@pytest.mark.parametrize("score", [None, "5", 0, 6, True])
def test_invalid_rating_score_returns_400(rating_client, score):
    client, _app, _owner_id, voter_id, recipe_id = rating_client
    response = client.post(
        f"/api/recipes/{recipe_id}/ratings",
        headers=make_auth(voter_id, "rating-voter"),
        json={"score": score},
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "Score must be an integer from 1 to 5"


def test_rating_for_missing_recipe_returns_404(rating_client):
    client, _app, _owner_id, voter_id, _recipe_id = rating_client
    response = client.post(
        "/api/recipes/9999/ratings",
        headers=make_auth(voter_id, "rating-voter"),
        json={"score": 4},
    )
    assert response.status_code == 404


def test_rating_post_requires_authentication(rating_client):
    client, _app, _owner_id, _voter_id, recipe_id = rating_client
    response = client.post(
        f"/api/recipes/{recipe_id}/ratings", json={"score": 4}
    )
    assert response.status_code == 401


def test_read_ratings_for_missing_recipe_returns_404(rating_client):
    client, _app, _owner_id, _voter_id, _recipe_id = rating_client
    response = client.get("/api/recipes/9999/ratings")
    assert response.status_code == 404
