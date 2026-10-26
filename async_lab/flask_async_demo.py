"""Demo Flask app for comparing sequential and concurrent outbound HTTP calls.

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


async def fetch_nutrition(client, ingredient):
    url = f"{DOWNSTREAM_URL}/nutrition/{quote(ingredient, safe='')}"
    response = await client.get(url)
    response.raise_for_status()
    return {
        "ingredient": ingredient,
        "status": response.status_code,
        "body": response.json(),
    }


@app.get("/recipes/async-demo")
async def async_demo():
    """Call the downstream API three times concurrently and return partial results."""
    started = time.perf_counter()
    results = []

    timeout_seconds = 3.0
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
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

        try:
            # wait_for bounds the overall wait. gather preserves input order.
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=timeout_seconds,
            )
        except asyncio.TimeoutError:
            # A whole-operation timeout can cancel unfinished work. Keep any
            # completed task results and label requests that did not finish.
            for ingredient, task in zip(INGREDIENTS, tasks):
                if task.done() and not task.cancelled():
                    try:
                        results.append(task.result())
                    except Exception as exc:
                        results.append({
                            "ingredient": ingredient,
                            "status": "error",
                            "error": str(exc),
                        })
                else:
                    results.append({
                        "ingredient": ingredient,
                        "status": "timeout",
                    })

    normalized = []
    for ingredient, result in zip(INGREDIENTS, results):
        if isinstance(result, Exception):
            normalized.append({
                "ingredient": ingredient,
                "status": "error",
                "error": str(result),
            })
        else:
            normalized.append(result)

    return jsonify({
        "results": normalized,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "all_succeeded": all(item.get("status") == 200 for item in normalized),
        "blocking_demo_enabled": request.args.get("blocking") == "1",
    })


if __name__ == "__main__":
    # Keep this demo server separate from the downstream API on port 5001.
    app.run(host="127.0.0.1", port=5002, threaded=True, debug=True)
