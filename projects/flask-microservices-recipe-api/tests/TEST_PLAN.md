# Smoke and Security Test Results

| ID | Test | Result |
| --- | --- | --- |
| T01 | GET /health on ports 5000, 5001, 5002 | 200 from each service |
| T02 | Register with username/password | 201; response excludes password/hash |
| T03 | Register same username twice | Second request returns 409 |
| T04 | Register with missing fields | 400 |
| T05 | Login with correct password | 200 with expiring JWT |
| T06 | Login with incorrect password | 401 with generic message |
| T07 | GET /api/recipes without Bearer token | 401 |
| T08 | Create recipe with valid token | 201; owner_id matches token user ID |
| T09 | Submit owner_id in create/update body | Body-supplied owner_id is ignored |
| T10 | User B updates/deletes User A's recipe | 403; stored recipe remains unchanged |
