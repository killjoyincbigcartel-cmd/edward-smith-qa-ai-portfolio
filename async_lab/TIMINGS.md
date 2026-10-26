# Async Lab Timings

## Synchronous baseline

| Number of Calls | Total Time |
|---:|---:|
| 1 (eggs) | 2.104 seconds |
| 3 (eggs, milk, rice) | 6.287 seconds |
| 5 (eggs, milk, rice, beans, bread) | 10.461 seconds |

These are the baseline values currently recorded for the lab. Re-run `sync_baseline.py` against the local nutrition API if you need to verify them on your machine.

## Async comparison (three calls: eggs, milk, rice)

Run this from the repository root while the nutrition API is running:

```bash
python async_lab/async_http.py
```

The script prints the elapsed time for both approaches, the HTTP status for each response, and the result order.

| Approach | Total Time |
|---|---:|
| Sync baseline (3 calls) | 6.287 seconds |
| Async sequential (3 calls) | 6.290 seconds |
| Async concurrent (`asyncio.gather`, 3 calls) | 2.110 seconds |


## Why async fits this endpoint

This endpoint is I/O-bound and makes three independent HTTP calls, so async lets the requests overlap and reduces the total waiting time for one incoming request. The synchronous baseline waits for each call to finish before starting the next, which is why its total time is close to the sum of the individual waits. Threads could also overlap blocking I/O, but for this async HTTP workload, `httpx.AsyncClient` with `asyncio.gather()` is a straightforward fit without adding thread-management complexity. Async does not make each individual request faster or automatically increase the server's overall request capacity.

## What to look for

The sequential async version still awaits each request before starting the next one, so it usually doesn't reduce the total waiting time. The concurrent version starts all three requests before awaiting their combined results, so independent network waits can overlap.

The concurrent result list should stay in the original input order (`eggs`, `milk`, `rice`), even if the requests finish in a different order. All three responses should succeed with HTTP 200.
