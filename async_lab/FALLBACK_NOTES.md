# Async Lab Fallback Notes

Each outbound nutrition request has a 3-second timeout. If a request times out, fails to connect, returns an HTTP error, or returns invalid JSON, that ingredient gets a structured placeholder with `"source": "fallback"` and `"fallback": true`. The placeholder sets `"calories": null` rather than inventing nutrition facts, and includes a note explaining that no estimate is available. Successful requests use `"source": "api"` and `"fallback": false`.

Example fallback item:

```json
{
  "ingredient": "eggs",
  "status": "timeout",
  "source": "fallback",
  "fallback": true,
  "data": {
    "calories": null,
    "note": "Nutrition data is unavailable; no estimate is being provided."
  },
  "error": "The nutrition service took too long to respond."
}
```

The endpoint returns one result for each ingredient even when the dependency is unavailable. This code change has been committed, but the endpoint still needs to be run locally with the nutrition service stopped or slowed down to confirm the failure response end to end.
