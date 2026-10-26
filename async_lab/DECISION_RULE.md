# Decision Rule: Sync, Threads, Async, or Processes

- **Synchronous:** Use it for straightforward work or when there is no real performance problem to solve.
- **Threads:** Use them when several independent blocking I/O tasks need to overlap in code that is otherwise synchronous.
- **Async:** Use it when there are multiple independent, slow I/O calls and they can be awaited concurrently. The lab comparison should show async sequential calls taking roughly the sum of the waits, while `asyncio.gather` can bring the total closer to the slowest call. Async does not help much if each request is still awaited one at a time, and it does not make an individual request faster.
- **Processes:** Consider multiprocessing for CPU-heavy Python work that can be split across CPU cores.

**Check the measurements:** Run `python async_lab/async_http.py` with the local API running and record the actual sequential and concurrent times in [TIMINGS.md](TIMINGS.md). Only claim a speedup if the measured concurrent run is faster and all responses succeed.
