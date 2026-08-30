# Movies REST API Test Plan

## Objective

Validate the Movies API's CRUD behavior, review relationships, input validation, HTTP responses, persistence, and SQL-safety controls.

## Scope

- `GET /movies`
- `GET /movies/<id>`
- `GET /movies/<id>/reviews`
- `POST /movies`
- `PATCH /movies/<id>`
- `DELETE /movies/<id>`
- SQLite persistence across application restarts
- Duplicate-title, missing-field, malformed-input, and not-found behavior

## API acceptance matrix

| ID | Request | Expected result |
| --- | --- | --- |
| API-001 | `GET /movies` | `200` with a JSON collection |
| API-002 | `GET /movies/1` for an existing record | `200` with the requested movie |
| API-003 | `GET /movies/999999` | `404` with a useful error response |
| API-004 | `GET /movies/1/reviews` | `200` with reviews joined to the movie |
| API-005 | Valid `POST /movies` | `201`, created record, and a `Location` header when implemented |
| API-006 | Duplicate movie title | `409`; existing data remains unchanged |
| API-007 | Missing required field | `400`; response explains the validation failure |
| API-008 | Valid `PATCH /movies/<id>` | `200` or the documented success response with updated data |
| API-009 | `PATCH` for an unknown ID | `404` |
| API-010 | `DELETE /movies/<id>` for an existing record | `204` or the documented success response |
| API-011 | `DELETE` for an unknown ID | `404` |
| API-012 | Query value containing SQL metacharacters | No unintended rows are returned or changed; parameterized behavior is preserved |
| API-013 | Restart the application after a write | Previously committed data remains available |

## Example requests

```bash
curl -i http://localhost:5000/movies

curl -i http://localhost:5000/movies/1/reviews

curl -i -X POST http://localhost:5000/movies \
  -H 'Content-Type: application/json' \
  -d '{"title":"Example Movie","director":"Example Director","year":2026}'

curl -i -X PATCH http://localhost:5000/movies/1 \
  -H 'Content-Type: application/json' \
  -d '{"year":2027}'

curl -i -X DELETE http://localhost:5000/movies/1
```

## Test data and evidence

For a real execution report, I would record the database seed, request body, response body, status code, headers, timestamp, and whether the result matched the requirement. Sensitive tokens or private data should never be committed.

