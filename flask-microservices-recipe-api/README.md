# Flask Microservices Recipe API

This folder contains three independent Flask apps:

- **Gateway** on port 5000: public entry point and response composition.
- **Users service** on port 5001: registration, login, password hashes, and JWT issuance/validation.
- **Recipes service** on port 5002: recipe CRUD, visibility/ownership checks, cache, and internal-only summary endpoint.

The services use separate SQLite databases. The gateway has no database or ORM models.

## Setup

From this folder:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`. Use long, random, different values for `JWT_SECRET` and `INTERNAL_SERVICE_TOKEN`. `RECIPES_INTERNAL_TOKEN` must match `INTERNAL_SERVICE_TOKEN`. Never commit `.env`, real tokens, or database files.

## Start all three services

Open three terminals. In each, change to this folder and activate `.venv`.

Terminal 1:

```bash
flask --app users_service:create_app run --port 5001
```

Terminal 2:

```bash
flask --app recipes_service:create_app run --port 5002
```

Terminal 3:

```bash
flask --app gateway:create_app run --port 5000
```

Stop the old Unit 3 slow service before running the challenge. The commands above start the new users, recipes, and gateway processes.

## Quick smoke check

```bash
curl -i http://localhost:5000/health
curl -i http://localhost:5001/health
curl -i http://localhost:5002/health
curl -i http://localhost:5000/recipes
```

Create a disposable test account through the gateway:

```bash
curl -i -X POST http://localhost:5000/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"challenge-user","password":"replace-this-test-password"}'
```

Log in and save the returned JWT in your shell:

```bash
export USER_JWT="$(curl -s -X POST http://localhost:5000/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"challenge-user","password":"replace-this-test-password"}' | python -c 'import json,sys; print(json.load(sys.stdin)["token"])')"
curl -i http://localhost:5000/me -H "Authorization: Bearer $USER_JWT"
```

## Public routes and service boundaries

The gateway forwards legacy public routes to their owning service, preserving upstream status and response body:

- `/register`, `/login`, and `/me` are owned by the users service. Gateway `GET /me` is the new composed endpoint, combining user details with recipe summary data.
- `/recipes` and `/recipes/<id>` are owned by the recipes service.
- `POST /recipes`, `PATCH /recipes/<id>`, and `DELETE /recipes/<id>` are forwarded to recipes and require a valid user JWT.

The composed `GET /me` calls users `/me` and recipes `/internal/recipes/summary` concurrently. The recipes internal endpoint requires both a valid user JWT and `X-Internal-Token`. The internal token is sent only to recipes and never returned to clients. A single upstream failure produces HTTP 200 with that section set to null and a `completeness` label; if both fail, the gateway returns HTTP 502.

## Internal authentication rejection

Run without a token:

```bash
curl -i http://localhost:5002/internal/health
```

Expected contract: HTTP 403 and `{"error":"Internal access denied"}`.

With a wrong token:

```bash
curl -i http://localhost:5002/internal/health \
  -H 'X-Internal-Token: definitely-not-the-secret'
```

Expected contract is also HTTP 403 with the same error body. Use the configured real internal token only in a local terminal; do not paste it into reports or commit it.

## Cache and invalidation

The public recipes list uses Flask-Caching `SimpleCache` with a 30-second timeout. Successful recipe creation, update, and deletion clear the cache after the database commit. To check invalidation, read `GET /recipes`, update a public test recipe with `PATCH /recipes/<id>`, and read `GET /recipes` again. The final response should contain the updated value.

## Tests

```bash
pytest -q
```

Gateway tests use fake upstream responses and are quick unit tests. They do not replace the live curl checks in the challenge report. Verify actual status codes and response bodies against running services before submitting the evidence.
