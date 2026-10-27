# Integration test plan

Run from the `flask-microservices-recipe-api` folder after installing requirements and creating a local `.env`.

## 1. Service roles

```bash
curl -i http://localhost:5000/health
curl -i http://localhost:5001/health
curl -i http://localhost:5002/health
```

Expected: all return HTTP 200 JSON with their own `service` field. Stop the old Unit 3 slow service before starting the three new processes.

## 2. Internal boundary

Call the internal route through the gateway without the token. The gateway does not add a token to arbitrary client requests, so the recipes service must reject it:

```bash
curl -i http://localhost:5000/internal/health
curl -i http://localhost:5000/internal/health -H 'X-Internal-Token: wrong-token'
```

Expected: HTTP 403 and `{"error":"Internal access denied"}`.

## 2. Internal boundary

```bash
curl -i http://localhost:5002/internal/health
curl -i http://localhost:5002/internal/health -H 'X-Internal-Token: wrong-token'
```

Expected for both: HTTP 403 and `{"error":"Internal access denied"}`.

## 3. Composition and degradation

After registering a disposable user and logging in through port 5000:

```bash
curl -i http://localhost:5000/me -H "Authorization: Bearer $USER_JWT"
```

Expected with both services healthy: HTTP 200, non-null `user` and `recipes`, and both completeness values `complete`.

Stop recipes service only, then repeat the same request. Expected: HTTP 200, the user section remains populated, recipes is null, and recipes completeness indicates the upstream failure. Restart recipes before continuing.

## 4. Legacy public contract

Use the 38 scenarios in `../../projects/recipe-api-auth/REFACTOR_PLAN.md`. Run each against port 5000, recording status and relevant JSON fields. Compare to the monolith's contract; mark only matching status and fields as unchanged. Public recipe listing and detail endpoints should be reachable without the internal token; internal-only routes must reject it when absent or wrong.

## 5. Cache invalidation

Read `GET /recipes` twice, update a test recipe using the owner's JWT, then read `GET /recipes` again. Expected: the final list reflects the update. Record the actual response bodies. Cache timing alone is not sufficient proof.

## 6. Git hygiene

```bash
git status --short
git ls-files | grep -E '(^|/)\.env$|\.env\.'
```

Expected: `.env.example` may be tracked; real `.env`, secrets, and local SQLite database files must not be tracked.
