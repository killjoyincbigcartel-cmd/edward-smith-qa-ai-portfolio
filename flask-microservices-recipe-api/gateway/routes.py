"""Gateway routes: pass-through login and aggregated current-user data."""
import asyncio

import httpx
from flask import Blueprint, current_app, jsonify, request

gateway_bp = Blueprint("gateway", __name__)


def _json_or_error(response):
    """Return upstream JSON, or a safe error if the upstream body isn't JSON."""
    try:
        return response.json()
    except ValueError:
        return {"error": "Upstream service returned an invalid JSON response"}


@gateway_bp.post("/login")
async def login():
    """Forward login credentials to the users service; the gateway issues no JWT."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "A JSON request body is required"}), 400

    url = f"{current_app.config['USERS_SERVICE_URL']}/login"
    timeout = current_app.config["UPSTREAM_TIMEOUT"]

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            upstream = await client.post(url, json=payload)
    except httpx.TimeoutException:
        return jsonify({"error": "Users service timed out"}), 504
    except httpx.RequestError:
        return jsonify({"error": "Users service is unavailable"}), 502

    return jsonify(_json_or_error(upstream)), upstream.status_code


async def _get_service_data(client, *, url, headers, timeout, empty_value):
    """Call one upstream service and return data plus a completeness label."""
    try:
        response = await client.get(url, headers=headers, timeout=timeout)
    except httpx.TimeoutException:
        return empty_value, "missing: timeout"
    except httpx.RequestError:
        return empty_value, "missing: upstream failure (502)"

    if not 200 <= response.status_code < 300:
        return empty_value, f"missing: upstream failure ({response.status_code})"

    try:
        return response.json(), "complete"
    except ValueError:
        return empty_value, "missing: invalid upstream JSON"


@gateway_bp.get("/me")
async def get_me():
    """Fetch user and recipe data concurrently and return a partial result if needed."""
    authorization = request.headers.get("Authorization", "")
    if not authorization.lower().startswith("bearer ") or not authorization[7:].strip():
        return jsonify({"error": "Authorization bearer token required"}), 401

    timeout = current_app.config["UPSTREAM_TIMEOUT"]
    users_url = f"{current_app.config['USERS_SERVICE_URL']}/me"
    recipes_url = f"{current_app.config['RECIPES_SERVICE_URL']}/recipes"

    # Forward the end-user token to both services. Keep the internal token private.
    user_headers = {"Authorization": authorization}
    recipe_headers = {"Authorization": authorization}
    internal_token = current_app.config["RECIPES_INTERNAL_TOKEN"]
    if internal_token:
        recipe_headers["X-Internal-Token"] = internal_token

    async with httpx.AsyncClient() as client:
        user_task = _get_service_data(
            client,
            url=users_url,
            headers=user_headers,
            timeout=timeout,
            empty_value=None,
        )
        recipes_task = _get_service_data(
            client,
            url=recipes_url,
            headers=recipe_headers,
            timeout=timeout,
            empty_value=None,
        )
        (user_data, user_status), (recipes_data, recipes_status) = await asyncio.gather(
            user_task, recipes_task
        )

    result = {
        "user": user_data,
        "recipes": recipes_data,
        "completeness": {
            "user": user_status,
            "recipes": recipes_status,
        },
    }

    # A partial result is useful even when one upstream is down. If both fail,
    # signal that the gateway could not produce a usable aggregate.
    if user_data is None and recipes_data is None:
        return jsonify(result), 502

    return jsonify(result), 200
