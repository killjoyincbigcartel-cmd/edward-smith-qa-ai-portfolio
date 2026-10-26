import time
from urllib.parse import quote

import httpx

BASE_URL = "http://127.0.0.1:5001"


def run_nutrition_calls(ingredients):
    start = time.perf_counter()

    with httpx.Client(timeout=120.0) as client:
        for ingredient in ingredients:
            url = f"{BASE_URL}/nutrition/{quote(ingredient, safe='')}"
            response = client.get(url)
            response.raise_for_status()
            print(f"{ingredient}: {response.status_code}")

    total = time.perf_counter() - start
    print(f"Total time for {len(ingredients)} call(s): {total:.3f} seconds")


if __name__ == "__main__":
    run_nutrition_calls(["eggs"])
    run_nutrition_calls(["eggs", "milk", "rice"])
    run_nutrition_calls(["eggs", "milk", "rice", "beans", "bread"])
