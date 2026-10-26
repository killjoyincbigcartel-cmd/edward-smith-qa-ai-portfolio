# Async Lab: Sync vs. Async HTTP Requests

This project compares sequential HTTP requests with concurrent async requests against the local nutrition API at `http://127.0.0.1:5001`.

## Setup

1. Start the nutrition API at `http://127.0.0.1:5001`.
2. Install the dependency:

```bash
python -m pip install -r async_lab/requirements.txt
```

## Run the scripts

From the repository root:

```bash
python async_lab/sync_baseline.py
python async_lab/async_http.py
```

The async script first awaits three requests one at a time, then runs the same requests together with `asyncio.gather`. It prints elapsed times, response status codes, whether all responses succeeded, and the returned ingredient order.

See [TIMINGS.md](TIMINGS.md) to record and compare your measured results, and [DECISION_RULE.md](DECISION_RULE.md) for the updated rule of thumb.
