# Smoke and Security Test Results

The following results reflect the outcomes the user verified for the requested steps.

| ID | Test | Result |
| --- | --- | --- |
| T01 | GET /health on ports 5000, 5001, 5002 | Verified: expected 200 from each service |
| T02 | Register with username/password | Verified: expected 201; response excludes password/hash |
| T03 | Register same username twice | Verified: expected second request returns 409 |
| T04 | Register with missing fields | Verified: expected 400 |
| T05 | Login with correct password | Verified: expected 200 with expiring JWT |
| T06 | Login with incorrect password | Verified: expected 401 with generic message |
| T07 | GET /api/recipes without Bearer token | Verified: expected 401 |
| T08 | Create recipe with valid token | Verified: expected 201; owner_id matches token user ID |
| T09 | Submit owner_id in create/update body | Verified: expected body-supplied owner_id is ignored |
| T10 | User B updates/deletes User A's recipe | Verified: expected 403; stored recipe remains unchanged |

## Verification note

These results are recorded as user-verified. No independent execution logs or automated test report were attached to this repository, so they should not be described as a CI run or as tests independently executed by GitHub.
