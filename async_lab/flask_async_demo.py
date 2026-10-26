"""Demo Flask app for concurrent outbound HTTP calls with fallbacks.

Run the nutrition API on port 5001 first, then run this app on port 5002.
"""
import asyncio
import os
import time
from urllib.parse import quote

import httpx
from flask import Flask, jsonify, request

app = Flask(__name__)
DOWNSTREAM_URL = os.getenv("NUTRITION_API_URL", "http://127.0.0.1:5001")
INGREDIENTS = ["eggs", "milk", "rice"]
REQUEST_TIMEOUT_SECONDS = 3.0


def fallback_result(ingredient, status, message):
    """Return a predictable, clearly labeled placeholder when a call fails."""
    return {
        "ingredient": ingredient,
        "status": status,
        "source": "fallback",
        "fallback": True,
        "data": {
            "calories": None,
            "note": "Nutrition data is unavailable; no estimate is being provided.",
        },
        "error": message,
    }


async def fetch_nutrition(client, ingredient):
    url = f"{DOWNSTREAM_URL}/nutrition/{quote(ingredient, safe='')}"
    try:
        response = await client.get(url)
        response.raise_for_status()
        return {
            "ingredient": ingredient,
            "status": response.status_code,
            "source": "api",
            "fallback": False,
            "data": response.json(),
        }
    except httpx.TimeoutException:
        return fallback_result(
            ingredient, "timeout", "The nutrition service took too long to respond."
        )
    except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as exc:
        return fallback_result(ingredient, "error", str(exc))


@app.get("/recipes/async-demo")
async def async_demo():
    """Call the downstream API concurrently and return a result for each ingredient."""
    started = time.perf_counter()

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        tasks = [
            asyncio.create_task(fetch_nutrition(client, ingredient))
            for ingredient in INGREDIENTS
        ]
        # Optional switch for demonstrating how blocking work delays async progress.
        # Let the requests begin before blocking this event-loop thread.
        # Example: /recipes/async-demo?blocking=1
        if request.args.get("blocking") == "1":
            await asyncio.sleep(0.1)
            time.sleep(1.0)  # Simulates a blocking database call; not for production.

        results = await asyncio.gather(*tasks)

    return jsonify({
        "results": results,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "all_succeeded": all(item.get("status") == 200 for item in results),
        "blocking_demo_enabled": request.args.get("blocking") == "1",
    })


if __name__ == "__main__":
    # Keep this demo server separate from the downstream API on port 5001.
    app.run(host="127.0.0.1", port=5002, threaded=True, debug=True)
