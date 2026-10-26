# Recipe API — JWT Auth, Ownership & Admin Authorization

A Flask + SQLite recipe API with a package layout and route/service/data layers.

## What this project demonstrates

- Password hashing, registration, and JWT login
- Shared authentication and owner/admin authorization
- Public and private recipe visibility
- Application factory with named configurations
- Environment-based secrets and local-only `.env`
- Route modules for HTTP translation, services for business rules, and data helpers for persistence
- Rate limiting on login and registration to reduce brute-force attempts and signup spam
- New layered endpoint: `GET /api/recipes/count`

## Project layout

```text
recipe-api-auth/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── auth/
│   │   ├── routes.py
│   │   ├── passwords.py
│   │   ├── tokens.py
│   │   └── guards.py
│   ├── recipes/
│   │   ├── routes.py
│   │   └── policies.py
│   ├── services/
│   │   ├── auth_service.py
│   │   └── recipe_service.py
│   ├── data/
│   │   ├── db.py
│   │   ├── models.py
│   │   ├── users.py
│   │   └── recipes.py
│   └── web/routes.py
├── instance/                 # local SQLite database is created here
├── tests/
├── wsgi.py
├── requirements.txt
└── .env.example
```

## Configuration and startup

Run commands from `projects/recipe-api-auth`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set `JWT_SECRET` to a long, random value. Never commit `.env`; `.gitignore` excludes it. Commit `.env.example` with placeholders only.

The default SQLite URL is `sqlite:///recipes.db`, which Flask-SQLAlchemy resolves under the app's `instance/` directory. Override `DATABASE_URL` for a different database. The testing configuration uses an isolated in-memory SQLite database.

Start the development server:

```bash
flask --app wsgi run
```

`wsgi.py` only creates and exposes the app using `create_app("development")`. Configuration, extension setup, required-secret validation, blueprint registration, and table initialization are handled by the factory and `init_db(app)`.

## Rate limiting

Flask-Limiter is registered through the application factory in `app/__init__.py`. Only the account endpoints have per-route limits:

- `POST /login`: 5 requests per minute per client IP.
- `POST /register`: 3 requests per hour per client IP.

Recipe reads are not rate-limited in this lesson. The limits help slow repeated password guesses and signup spam, but a legitimate user can temporarily hit a limit. When that happens, the server returns `429 Too Many Requests`. With headers enabled, look for `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `Retry-After` to understand the configured quota, remaining requests, and wait time. Header availability and exact formatting can depend on the installed Flask-Limiter version and configuration.

See [RATE_LIMITING_LAB.md](RATE_LIMITING_LAB.md) for the repeat-request exercise and evidence checklist.

## Layer responsibilities

- `app/auth/routes.py`: parses account HTTP requests, applies endpoint limits, and formats JSON responses.
- `app/services/auth_service.py`: registration/login validation and account workflow.
- `app/recipes/routes.py`: parses recipe HTTP requests and formats JSON responses.
- `app/services/recipe_service.py`: recipe validation, update/delete workflow, and count feature.
- `app/data/users.py` and `app/data/recipes.py`: database queries and writes.
- `app/data/db.py`: database table initialization.
- `app/config.py`: named configuration classes and environment-backed settings.

## Existing API contract

The refactor keeps the existing endpoint paths and response contracts:

- `GET /health`
- `POST /register`
- `POST /login`
- `GET /recipes/<recipe_id>`
- `POST /recipes`
- `PATCH /recipes/<recipe_id>`
- `DELETE /recipes/<recipe_id>`

The original API does not have a `GET /recipes` collection endpoint. The new feature is added separately at `GET /api/recipes/count`, returning `{"count": <integer>}`.

## Smoke checks

Register:

```bash
curl -i -X POST http://127.0.0.1:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"smoke-check-user","password":"SmokePass123!"}'
```

Log in:

```bash
curl -i -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"smoke-check-user","password":"SmokePass123!"}'
```

Use the returned token to create a recipe:

```bash
curl -i -X POST http://127.0.0.1:5000/recipes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title":"Smoke check recipe","is_public":true}'
```

Read a specific recipe using the ID returned above:

```bash
curl -i http://127.0.0.1:5000/recipes/RECIPE_ID
```

Check the new count endpoint:

```bash
curl -i http://127.0.0.1:5000/api/recipes/count
```

Run automated tests with `pytest`. Runtime verification should be reported from actual test and HTTP output; expected outcomes should not be represented as captured results.

## Authorization rules

- Missing, invalid, or expired token on protected writes -> 401.
- Valid token without permission -> 403.
- Owners can update/delete their own recipes; admins can update/delete any recipe.
- Registration always assigns role `user`.
- Recipe ownership is assigned from the verified token identity, not client input.
