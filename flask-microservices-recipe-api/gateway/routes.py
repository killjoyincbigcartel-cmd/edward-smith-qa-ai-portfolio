"""Public API gateway: preserve legacy routes and compose cross-service data."""
import asyncio

import httpx
from flask import Blueprint, current_app, jsonify, request, Response

gateway_bp = Blueprint("gateway", __name__)


def _json_or_error(response):
    try:
        return response.json()
    except ValueError:
        return {"error": "Upstream service returned an invalid JSON response"}


@gateway_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "gateway"}), 200


@gateway_bp.post("/login")
async def login():
    """Login is owned by the users service; pass its status and JSON through."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "A JSON request body is required"}), 400
    try:
        async with httpx.AsyncClient(timeout=current_app.config["UPSTREAM_TIMEOUT"]) as client:
            upstream = await client.post(f"{current_app.config['USERS_SERVICE_URL']}/login", json=payload)
    except httpx.TimeoutException:
        return jsonify({"error": "Users service timed out"}), 504
    except httpx.RequestError:
        return jsonify({"error": "Users service is unavailable"}), 502
    return jsonify(_json_or_error(upstream)), upstream.status_code


async def _get_service_data(client, *, url, headers, timeout):
    try:
        response = await client.get(url, headers=headers, timeout=timeout)
    except httpx.TimeoutException:
        return None, "missing: timeout"
    except httpx.RequestError:
        return None, "missing: upstream failure (502)"
    if not 200 <= response.status_code < 300:
        return None, f"missing: upstream failure ({response.status_code})"
    try:
        return response.json(), "complete"
    except ValueError:
        return None, "missing: invalid upstream JSON"


@gateway_bp.get("/me")
async def get_me():
    """Concurrent user + recipe composition with partial results when one fails."""
    authorization = request.headers.get("Authorization", "")
    if not authorization.lower().startswith("bearer ") or not authorization[7:].strip():
        return jsonify({"error": "Unauthorized"}), 401

    timeout = current_app.config["UPSTREAM_TIMEOUT"]
    users_url = f"{current_app.config['USERS_SERVICE_URL']}/me"
    recipes_url = f"{current_app.config['RECIPES_SERVICE_URL']}/internal/recipes/summary"
    user_headers = {"Authorization": authorization}
    recipe_headers = {
        "Authorization": authorization,
        "X-Internal-Token": current_app.config["RECIPES_INTERNAL_TOKEN"],
    }

    async with httpx.AsyncClient() as client:
        (user_data, user_status), (recipes_data, recipes_status) = await asyncio.gather(
            _get_service_data(client, url=users_url, headers=user_headers, timeout=timeout),
            _get_service_data(client, url=recipes_url, headers=recipe_headers, timeout=timeout),
        )

    result = {
        "user": user_data,
        "recipes": recipes_data,
        "completeness": {"user": user_status, "recipes": recipes_status},
    }
    if user_data is None and recipes_data is None:
        return jsonify(result), 502
    return jsonify(result), 200


@gateway_bp.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@gateway_bp.route("/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_public_api(path):
    """Forward legacy public API routes to their owning service without changing payloads."""
    users_paths = {"register", "users/me"}
    # Account/auth routes belong to users. Everything else is owned by recipes.
    service_base = current_app.config["USERS_SERVICE_URL"] if path in users_paths else current_app.config["RECIPES_SERVICE_URL"]
    upstream_url = f"{service_base}/{path}" if path else f"{service_base}/"
    headers = {
        key: value for key, value in request.headers.items()
        if key.lower() not in {"host", "content-length", "connection"}
    }
    try:
        async with httpx.AsyncClient(timeout=current_app.config["UPSTREAM_TIMEOUT"]) as client:
            upstream = await client.request(
                request.method,
                upstream_url,
                params=request.args,
                content=request.get_data(),
                headers=headers,
            )
    except httpx.TimeoutException:
        return jsonify({"error": "Upstream service timed out"}), 504
    except httpx.RequestError:
        return jsonify({"error": "Upstream service is unavailable"}), 502

    response_headers = {}
    for key in ("Content-Type", "Cache-Control", "ETag", "Last-Modified"):
        if key in upstream.headers:
            response_headers[key] = upstream.headers[key]
    return Response(upstream.content, status=upstream.status_code, headers=response_headers)
