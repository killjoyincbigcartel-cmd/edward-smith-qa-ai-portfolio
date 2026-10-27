# Microservices Integration Challenge Report

**Branch:** `feature/microservices-gateway`  
**Project:** `flask-microservices-recipe-api`  
**Status:** Implementation review completed; live integration evidence is not yet captured.

## What is currently present

- Flask gateway factory and routes.
- `POST /login` forwards to the users service.
- `GET /me` concurrently requests `/me` from users and `/recipes` from recipes using `asyncio.gather()`.
- Timeout and partial-response handling in the gateway.
- Mock-based gateway tests and setup documentation.

## Important gaps found during review

1. The new project folder currently contains the gateway but does not contain runnable users-service or recipes-service implementations.
2. The original public API contract in `projects/recipe-api-auth/REFACTOR_PLAN.md` has 38 scenarios across `/health`, `/register`, `/login`, and recipe read/create/update/delete endpoints. The current gateway only exposes `/login` and `/me`, so it does not yet preserve the full public contract.
3. The original monolith uses a 30-second `GET /recipes` cache and clears the cache after successful create/update/delete operations. That behavior has not yet been verified in a separate recipes service.
4. No live three-process run has been performed in this environment. The HTTP responses below must be recorded from actual execution; they are not inferred from mocked tests.

## Runtime evidence log

Do not mark a row as passed until the command has been run against the local services and the output has been saved.

| Check | Evidence to capture | Status |
|---|---|---|
| Gateway health / reachability on port 5000 | `curl -i http://localhost:5000/health` | BLOCKED: gateway currently has no `/health` route |
| Users service reachability on port 5001 | `curl -i http://localhost:5001/health` | BLOCKED: users service implementation not present in this folder |
| Recipes service reachability on port 5002 | `curl -i http://localhost:5002/health` | BLOCKED: recipes service implementation not present in this folder |
| Invalid internal token rejected | Save exact request, status, and JSON body | NOT RUN |
| Successful gateway composition | `curl -i http://localhost:5000/me -H 'Authorization: Bearer <TOKEN>'` | NOT RUN against live services |
| Graceful degradation with recipes stopped | Same `/me` request with recipes service stopped | NOT RUN against live services |
| Original 38 acceptance scenarios through gateway | Save status and key response fields for every scenario | BLOCKED: public routes are not all proxied yet |
| Cache read and invalidation | Repeat `GET /recipes`, update a recipe, read again | NOT RUN against a split recipes service |
| No secrets tracked | `git status --short` and `git ls-files '* .env'` review | Requires local checkout review |

## Run evidence collection after completing the service split

Start each service in its own terminal. Confirm the old Unit 3 slow service is stopped. Use a disposable local database and test account; do not paste real passwords or tokens into this report.

### Basic reachability

```bash
curl -i http://localhost:5000/health
curl -i http://localhost:5001/health
curl -i http://localhost:5002/health
```

### Login and composed response

Adapt the credential fields to the users service contract:

```bash
curl -i -X POST http://localhost:5000/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"challenge-user","password":"REPLACE_WITH_TEST_PASSWORD"}'
```

Copy the returned token into a local shell variable, not into Git-tracked files:

```bash
export USER_JWT='REPLACE_WITH_TEST_JWT'
curl -i http://localhost:5000/me -H "Authorization: Bearer $USER_JWT"
```

Save the complete status line and JSON response for both the healthy case and the case where the recipes process is stopped.

### Internal-auth rejection

Use the actual internal-only endpoint implemented by the recipes service and send a deliberately missing or invalid internal token. Record the actual response. The expected contract must be enforced by the recipes service itself; a gateway forwarding header is not proof that the service rejects invalid tokens.

### Cache invalidation

```bash
curl -i http://localhost:5000/recipes
curl -i http://localhost:5000/recipes
# Update a test recipe using the supported authenticated PATCH endpoint.
curl -i -X PATCH http://localhost:5000/recipes/REPLACE_WITH_TEST_ID \
  -H "Authorization: Bearer $USER_JWT" \
  -H 'Content-Type: application/json' \
  -d '{"title":"Cache invalidation check"}'
curl -i http://localhost:5000/recipes
```

The final read should show the updated title. Record the actual bodies/status codes; do not infer a cache hit from response time alone.

## Public-contract comparison

Use all 38 numbered scenarios in `projects/recipe-api-auth/REFACTOR_PLAN.md`. For each one, record the gateway request, actual status, relevant JSON fields, and compare it with the monolith baseline. Mark a case **unchanged** only when the status and relevant response contract match. Document intentional changes separately.

**Current unchanged count:** Not measured.  
**Total baseline scenarios:** 38.  
**Reason:** Live gateway acceptance requests have not yet been executed, and most baseline routes are not exposed by the gateway yet.

## Git hygiene

Before the final challenge commit, run:

```bash
git status --short
git ls-files | grep -E '(^|/)\.env$|\.env\.'
```

Confirm that only `.env.example` is tracked and that real credentials, JWTs, internal tokens, and local databases are excluded. After the missing services and routes are implemented and the evidence is captured, update this report with actual outputs and commit it with the implementation.
