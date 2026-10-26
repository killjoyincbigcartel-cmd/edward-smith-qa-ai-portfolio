# Smoke and Security Test Plan

This plan records the expected behavior for the Flask microservices recipe API.

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

**User-reported verification:** The user confirmed that they verified the expected results for the requested 10 steps.

**Verification scope:** This entry records the user's confirmation. No independent execution logs or automated test report were available to attach here, so this file does not claim that GitHub or this assistant ran the tests.

**Next step:** If you want a reproducible test record, run the checks against the services and add the execution date, environment, and observed pass/fail results.
