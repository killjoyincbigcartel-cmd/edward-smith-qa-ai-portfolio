from gateway import create_app
import gateway.routes as routes


class FakeResponse:
    def __init__(self, status_code=200, payload=None, content=None, headers=None):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.content = content if content is not None else b""
        self.headers = headers or {"content-type": "application/json"}

    def json(self):
        return self._payload


class FakeAsyncClient:
    recipes_down = False

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def post(self, url, json=None, **kwargs):
        assert url.endswith("/login")
        return FakeResponse(200, {"token": "test-jwt", "username": json["username"]})

    async def get(self, url, headers=None, timeout=None, **kwargs):
        if url.endswith("/me"):
            assert headers["Authorization"] == "Bearer test-jwt"
            return FakeResponse(200, {"id": 7, "username": "test-user", "role": "user"})
        if url.endswith("/internal/recipes/summary"):
            assert headers["Authorization"] == "Bearer test-jwt"
            assert headers["X-Internal-Token"] == "test-internal-secret"
            if self.recipes_down:
                raise routes.httpx.ConnectError("recipes unavailable")
            return FakeResponse(200, [{"id": 12, "title": "Soup"}])
        raise AssertionError(f"Unexpected URL: {url}")

    async def request(self, method, url, **kwargs):
        assert url.endswith("/recipes")
        return FakeResponse(200, [{"id": 12, "title": "Soup"}], content=b'[{"id":12,"title":"Soup"}]')


def test_gateway_health():
    response = create_app().test_client().get("/health")
    assert response.status_code == 200
    assert response.get_json()["service"] == "gateway"


def test_login_forwards_response(monkeypatch):
    monkeypatch.setattr(routes.httpx, "AsyncClient", FakeAsyncClient)
    response = create_app().test_client().post(
        "/login", json={"username": "test-user", "password": "example-password"}
    )
    assert response.status_code == 200
    assert response.get_json()["token"] == "test-jwt"


def test_me_requires_bearer_token():
    response = create_app().test_client().get("/me")
    assert response.status_code == 401


def test_me_combines_upstream_data_and_keeps_internal_token_private(monkeypatch):
    monkeypatch.setattr(routes.httpx, "AsyncClient", FakeAsyncClient)
    app = create_app({"RECIPES_INTERNAL_TOKEN": "test-internal-secret"})
    response = app.test_client().get("/me", headers={"Authorization": "Bearer test-jwt"})
    body = response.get_json()
    assert response.status_code == 200
    assert body["user"]["id"] == 7
    assert body["recipes"][0]["title"] == "Soup"
    assert body["completeness"] == {"user": "complete", "recipes": "complete"}
    assert "test-internal-secret" not in response.get_data(as_text=True)


def test_me_degrades_when_recipes_service_is_unavailable(monkeypatch):
    monkeypatch.setattr(routes.httpx, "AsyncClient", FakeAsyncClient)
    FakeAsyncClient.recipes_down = True
    try:
        app = create_app({"RECIPES_INTERNAL_TOKEN": "test-internal-secret"})
        response = app.test_client().get("/me", headers={"Authorization": "Bearer test-jwt"})
        body = response.get_json()
        assert response.status_code == 200
        assert body["user"]["username"] == "test-user"
        assert body["recipes"] is None
        assert body["completeness"]["recipes"] == "missing: upstream failure (502)"
    finally:
        FakeAsyncClient.recipes_down = False


def test_legacy_recipe_route_is_proxied(monkeypatch):
    monkeypatch.setattr(routes.httpx, "AsyncClient", FakeAsyncClient)
    response = create_app().test_client().get("/recipes")
    assert response.status_code == 200
    assert response.get_json()[0]["title"] == "Soup"
