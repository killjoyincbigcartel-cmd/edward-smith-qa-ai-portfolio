# Smoke and Security Test Plan

These are expected outcomes. Mark actual results only after running the services locally.

| ID | Action | Expected |
| --- | --- | --- |
| T01 | GET /health on ports 5000, 5001, 5002 | 200 from each service |
| T02 | Register with username/password | 201; response has no password/hash |
| T03 | Register same username twice | second request 409 |
| T04 | Register with missing fields | 400 |
| T05 | Login with correct password | 200 and expiring JWT |
| T06 | Login with incorrect password | 401 with generic message |
| T07 | GET /api/recipes without Bearer token | 401 |
| T08 | Create recipe with valid token | 201; owner_id equals token user ID |
| T09 | Submit owner_id in create/update body | ignored; owner remains token user |
| T10 | User B updates/deletes User A's recipe | 403; stored recipe unchanged |
| T11 | Request unknown recipe ID | 404 |
| T12 | Stop Recipes service and call through gateway | 502 |
| T13 | Inspect data files/configuration | separate databases; no committed .env |

## Result record

Execution status: **Not run by GitHub integration**. The expected outcomes above are not actual test results. Run the tests on your machine and replace this line with the date, environment, and observed pass/fail details.
