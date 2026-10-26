# Flask Async View Challenge

## What it does

The `flask_async_demo.py` file adds `GET /recipes/async-demo`. The view is declared with `async def`, uses `httpx.AsyncClient`, and requests eggs, milk, and rice concurrently with `asyncio.gather()`. The JSON response includes the results, elapsed time, and whether all requests succeeded.

The view applies a 3-second overall timeout. If the whole operation times out, unfinished requests are labeled `timeout`; request-level failures are labeled `error`.

## Run it

Start the nutrition API on port 5001, then in another terminal run:

```bash
python -m pip install -r async_lab/requirements.txt
python async_lab/flask_async_demo.py
```

Call the endpoint:

```bash
curl -s http://127.0.0.1:5002/recipes/async-demo
```

Compare the blocking-work demonstration:

```bash
curl -s 'http://127.0.0.1:5002/recipes/async-demo?blocking=1'
```

The `blocking=1` option adds a one-second `time.sleep()` to simulate blocking database work. It is only for demonstrating the effect; blocking calls should not be used on an async event-loop path in production.

## Timing comparison

Record the `elapsed_seconds` value returned by each request.

| Test | Expected behavior |
|---|---|
| Existing slow calls made sequentially | Total time is close to the sum of the individual waits |
| Async endpoint | Independent outbound waits overlap, so total time is closer to the slowest call |
| Async endpoint with blocking demo enabled | The blocking operation adds delay and holds up progress on that event-loop thread |

The actual values depend on the local API and machine. Use the values printed by your own run as the final measurements.

## Takeaway

An async Flask view can reduce the waiting time for one request when its independent outbound I/O calls run concurrently. It does not automatically increase the number of simultaneous requests the server can handle. Blocking operations such as `time.sleep()`, synchronous database calls, or CPU-heavy work prevent other coroutines on the same event loop from making progress.
