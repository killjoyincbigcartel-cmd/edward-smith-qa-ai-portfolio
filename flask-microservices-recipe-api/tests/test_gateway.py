import asyncio

from gateway import create_app
import gateway.routes as routes


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}

    def json(self):
        return self._payload


class FakeAsyncClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def post(self, url, json=None, **kwargs):
        assert url.endswith("/login")
        return FakeResponse(200, {"token": "test-jwt", "email": json["email"]})

    async def get(self, url, headers=None, timeout=None, **kwargs):
        if url.endswith("/me"):
            assert headers["Authorization"] == "Bearer test-jwt"
            return FakeResponse(200, {"id": 7, "email": "test@example.com"})
        if url.endswith("/recipes"):
            assert headers["Authorization"] == "Bearer test-jwt"
            assert headers["X-Internal-Token"] == "test-internal-secret"
            return FakeResponse(200, [{"id": 12, "title": "Soup"}])
        raise AssertionError(f"Unexpected URL: {url}")


def test_login_forwards_response(monkeypatch):
    monkeypatch.setattr(routes.httpx, "AsyncClient", FakeAsyncClient)
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/login",
        json={"email": "test@example.com", "password": "example-password"},
    )

    assert response.status_code == 200
    assert response.get_json()["token"] == "test-jwt"


def test_me_requires_bearer_token():
    app = create_app()
    response = app.test_client().get("/me")
    assert response.status_code == 401


def test_me_combines_upstream_data_and_keeps_internal_token_private(monkeypatch):
    monkeypatch.setattr(routes.httpx, "AsyncClient", FakeAsyncClient)
    app = create_app()
    app.config["RECIPES_INTERNAL_TOKEN"] = "test-internal-secret"

    response = app.test_client().get(
        "/me", headers={"Authorization": "Bearer test-jwt"}
    )

    body = response.get_json()
    assert response.status_code == 200
    assert body["user"]["id"] == 7
    assert body["recipes"][0]["title"] == "Soup"
    assert body["completeness"] == {"user": "complete", "recipes": "complete"}
    assert "test-internal-secret" not in response.get_data(as_text=True)
