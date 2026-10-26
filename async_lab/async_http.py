import asyncio
import time
from urllib.parse import quote

import httpx

BASE_URL = "http://127.0.0.1:5001"
INGREDIENTS = ["eggs", "milk", "rice"]


async def fetch_nutrition(client, ingredient):
    url = f"{BASE_URL}/nutrition/{quote(ingredient, safe='')}"
    response = await client.get(url)
    response.raise_for_status()
    return {
        "ingredient": ingredient,
        "status": response.status_code,
        "body": response.json(),
    }


async def run_sequential(client, ingredients):
    results = []
    for ingredient in ingredients:
        results.append(await fetch_nutrition(client, ingredient))
    return results


async def run_concurrent(client, ingredients):
    return await asyncio.gather(
        *(fetch_nutrition(client, ingredient) for ingredient in ingredients)
    )


def show_results(label, results, elapsed):
    print(f"\n{label}")
    print(f"Total time: {elapsed:.3f} seconds")
    for result in results:
        print(f"{result['ingredient']}: HTTP {result['status']}")
    print("Result order:", [result["ingredient"] for result in results])
    print("All requests succeeded:", all(result["status"] == 200 for result in results))


async def main():
    timeout = httpx.Timeout(120.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        start = time.perf_counter()
        sequential_results = await run_sequential(client, INGREDIENTS)
        sequential_elapsed = time.perf_counter() - start
        show_results("Async sequential (one request awaited at a time)", sequential_results, sequential_elapsed)

        start = time.perf_counter()
        concurrent_results = await run_concurrent(client, INGREDIENTS)
        concurrent_elapsed = time.perf_counter() - start
        show_results("Async concurrent (asyncio.gather)", concurrent_results, concurrent_elapsed)

        expected_order = INGREDIENTS
        actual_order = [result["ingredient"] for result in concurrent_results]
        print("\nConcurrent results preserve input order:", actual_order == expected_order)


if __name__ == "__main__":
    asyncio.run(main())
