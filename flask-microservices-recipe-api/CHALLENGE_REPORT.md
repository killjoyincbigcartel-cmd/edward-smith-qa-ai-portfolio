# Microservices Integration Challenge Report

**Branch:** `feature/microservices-gateway`  
**Project:** `flask-microservices-recipe-api`

This report contains the expected results from the current implementation. Run the commands locally and replace/annotate these expectations with the actual status lines and response bodies before submitting. No live service responses are claimed here.

## Services and responsibilities

| Service | Port | Responsibility |
|---|---:|---|
| Gateway | 5000 | Public entry point, legacy-route forwarding, concurrent `GET /me` composition |
| Users | 5001 | Registration, password hashing, login, JWT issuance and identity lookup |
| Recipes | 5002 | Recipe CRUD, JWT checks, ownership/visibility rules, cache and invalidation |

The gateway has no database. Users and recipes use separate SQLite databases. All three services use the same `JWT_SECRET`; recipes also checks the separate `INTERNAL_SERVICE_TOKEN` supplied by the gateway as `X-Internal-Token` for internal-only routes.

## 1. Basic roles — expected results

Run these with all three services started and the old Unit 3 slow service stopped:

```bash
curl -i http://localhost:5000/health
curl -i http://localhost:5001/health
curl -i http://localhost:5002/health
```

Expected status: **HTTP 200** for each. The response JSON includes `status: "ok"`; the gateway/users/recipes health endpoints identify their respective service. The gateway is the public client entry point. Direct service ports are for local verification and internal operations.

## 2. Internal authentication — expected rejection

Call the internal route through the gateway, not directly to the recipes service:

```bash
curl -i http://localhost:5000/internal/health
curl -i http://localhost:5000/internal/health \
  -H 'X-Internal-Token: definitely-not-the-secret'
```

Expected for both calls:

```http
HTTP/1.1 403 FORBIDDEN
Content-Type: application/json
```

```json
{"error":"Internal access denied"}
```

The gateway forwards the request without inventing or injecting an internal token; the recipes service enforces the boundary. This is an expected result to verify locally, not a captured live response.

## 3. Successful composition — expected result

Register and log in a disposable user:

```bash
curl -i -X POST http://localhost:5000/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"challenge-user","password":"replace-this-test-password"}'

export USER_JWT="$(curl -s -X POST http://localhost:5000/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"challenge-user","password":"replace-this-test-password"}' \
  | python -c 'import json,sys; print(json.load(sys.stdin)["token"])')"

curl -i http://localhost:5000/me -H "Authorization: Bearer $USER_JWT"
```

Expected when both upstream services are healthy: **HTTP 200**. The JSON has populated `user` and `recipes` fields, and:

```json
"completeness": {"user":"complete","recipes":"complete"}
```

The gateway requests user identity and the recipes internal summary concurrently. Save the real response body from the final command as successful-composition evidence.

## 4. Graceful degradation — expected result

Stop only the recipes process on port 5002. Keep gateway and users running, then repeat:

```bash
curl -i http://localhost:5000/me -H "Authorization: Bearer $USER_JWT"
```

Expected: **HTTP 200** because the users service still provides usable data. `user` remains populated; `recipes` is `null`; `completeness.recipes` identifies the upstream failure. This is graceful degradation because a recipe-service outage does not erase the user data. Restart recipes before continuing.

If both upstreams are unavailable, expected result is **HTTP 502** with both data fields null and both completeness labels marked missing.

## 5. Public contract acceptance — all 38 scenarios

The baseline is `projects/recipe-api-auth/REFACTOR_PLAN.md`. Use the same test data and conditions as the monolith baseline. These are expected statuses based on that contract and the split service code; confirm actual response bodies and mark each row unchanged only after comparing them.

| # | Request / scenario | Gateway request | Expected status | Key expected response |
|---:|---|---|---:|---|
| 1 | Health | `GET /health` | 200 | `status: ok`; gateway adds a service label |
| 2 | Register missing username | `POST /register` | 400 | `Username is required` |
| 3 | Register missing password | `POST /register` | 400 | `Password is required` |
| 4 | Duplicate registration | `POST /register` | 409 | `Username already exists` |
| 5 | Valid registration | `POST /register` | 201 | message, username, role=user; no password/hash |
| 6 | Login missing username | `POST /login` | 400 | required-fields error |
| 7 | Login missing password | `POST /login` | 400 | required-fields error |
| 8 | Login unknown username | `POST /login` | 401 | `Invalid username or password` |
| 9 | Login wrong password | `POST /login` | 401 | same generic credentials error |
| 10 | Login valid credentials | `POST /login` | 200 | username, role, signed token; no password/hash |
| 11 | Missing recipe ID | `GET /recipes/999999` | 404 | `Recipe not found` |
| 12 | Public recipe without token | `GET /recipes/<id>` | 200 | recipe fields |
| 13 | Private recipe without token | `GET /recipes/<id>` | 401 | `Unauthorized` |
| 14 | Private recipe invalid/expired token | `GET /recipes/<id>` | 401 | `Unauthorized` |
| 15 | Private recipe by another ordinary user | `GET /recipes/<id>` | 403 | `Forbidden` |
| 16 | Private recipe by owner | `GET /recipes/<id>` | 200 | recipe fields |
| 17 | Create recipe without token | `POST /recipes` | 401 | `Unauthorized`; no creation |
| 18 | Create recipe with invalid token | `POST /recipes` | 401 | `Unauthorized`; no creation |
| 19 | Create missing/blank/non-string title | `POST /recipes` | 400 | `Title is required` |
| 20 | Create with non-boolean is_public | `POST /recipes` | 400 | `is_public must be a boolean` |
| 21 | Valid recipe create | `POST /recipes` | 201 | created ID/title/owner_id |
| 22 | Create with spoofed owner_id | `POST /recipes` | 201 | owner_id comes from signed token |
| 23 | Patch without token | `PATCH /recipes/<id>` | 401 | `Unauthorized`; no change |
| 24 | Patch invalid/expired token | `PATCH /recipes/<id>` | 401 | `Unauthorized`; no change |
| 25 | Patch missing recipe | `PATCH /recipes/<id>` | 404 | `Recipe not found` |
| 26 | Patch by non-owner, non-admin | `PATCH /recipes/<id>` | 403 | `Forbidden`; no change |
| 27 | Owner updates valid field | `PATCH /recipes/<id>` | 200 | updated recipe fields |
| 28 | Admin updates another user's recipe | `PATCH /recipes/<id>` | 200 | updated recipe fields |
| 29 | Patch blank/non-string title | `PATCH /recipes/<id>` | 400 | title validation error |
| 30 | Patch non-boolean is_public | `PATCH /recipes/<id>` | 400 | boolean validation error |
| 31 | Attempt to change owner_id | `PATCH /recipes/<id>` | 200 | owner_id remains unchanged |
| 32 | Empty/unrecognized patch body | `PATCH /recipes/<id>` | 200 | recipe unchanged |
| 33 | Delete without token | `DELETE /recipes/<id>` | 401 | `Unauthorized`; recipe remains |
| 34 | Delete invalid/expired token | `DELETE /recipes/<id>` | 401 | `Unauthorized`; recipe remains |
| 35 | Delete missing recipe | `DELETE /recipes/<id>` | 404 | `Recipe not found` |
| 36 | Delete by non-owner, non-admin | `DELETE /recipes/<id>` | 403 | `Forbidden`; recipe remains |
| 37 | Owner deletes own recipe | `DELETE /recipes/<id>` | 200 | deletion message and ID |
| 38 | Admin deletes another user's recipe | `DELETE /recipes/<id>` | 200 | deletion message and ID |

**Current unchanged count:** not measured.  
**Total scenarios:** 38.  
**Expected result:** The gateway forwards legacy route statuses and response bodies from the owning service, but this still needs to be compared against actual monolith captures. Health adds a service field; treat that as an intentional extra field if the baseline body did not include it. Do not state an unchanged count until all 38 requests have been run and compared.

## 6. Cache and invalidation — expected result

The recipes service uses a 30-second `SimpleCache` for public `GET /recipes`. Successful create, patch, and delete operations clear the cache after committing.

```bash
curl -i http://localhost:5000/recipes
curl -i http://localhost:5000/recipes
curl -i -X PATCH http://localhost:5000/recipes/REPLACE_WITH_TEST_ID \
  -H "Authorization: Bearer $USER_JWT" \
  -H 'Content-Type: application/json' \
  -d '{"title":"Cache invalidation check"}'
curl -i http://localhost:5000/recipes
```

Expected: the final list shows `Cache invalidation check` for the public test recipe. Save the actual response bodies for the before/after comparison. Response speed alone is not reliable proof of a cache hit.

## 7. Git hygiene and commit

```bash
git status --short
git ls-files | grep -E '(^|/)\.env$|\.env\.'
```

Expected: `.env.example` can be tracked; real `.env`, JWT secrets, internal tokens, and local SQLite databases must not be tracked. Once the local run and evidence are complete, commit the finished report and any fixes with:

```bash
git add flask-microservices-recipe-api
git commit -m "chore: complete multi-service integration challenge"
```

## Automated tests

Run:

```bash
pytest -q
```

Gateway tests use fake upstream responses. Service tests cover registration/login, internal-token rejection, and cache invalidation with test databases. These are code-level tests, not a substitute for the live three-process curl evidence above.
