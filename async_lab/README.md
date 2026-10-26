# Async Lab: Synchronous Baseline

This project measures how long sequential HTTP requests take before comparing them with an asynchronous version.

## Setup

1. Start the nutrition API at `http://127.0.0.1:5001`.
2. Install the dependency:

```bash
python -m pip install -r async_lab/requirements.txt
```

3. From the repository root, run:

```bash
python async_lab/sync_baseline.py
```

The script makes 1, 3, and 5 sequential requests to the nutrition endpoint and prints the total elapsed time for each group.

See [TIMINGS.md](TIMINGS.md) for the timing results and explanation.
