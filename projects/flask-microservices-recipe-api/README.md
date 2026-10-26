# Flask Microservices Recipe API

A learning project that separates authentication, recipe ownership, and request routing into three Flask services.

## Architecture (the 10-step implementation checklist)

1. **Document service boundaries** in [docs/architecture.md](docs/architecture.md).
2. **Create independent services**: Users (5001), Recipes (5002), and Gateway (5000).
3. **Configure environments** with environment variables and safe example defaults.
4. **Give each data-owning service its own database**; the services do not share ORM models or perform cross-service joins.
5. **Implement registration** with required-field validation, unique usernames, and Werkzeug password hashing.
6. **Implement login and JWTs** with expiry; return a generic error for invalid credentials.
7. **Protect recipe routes** by validating Bearer tokens and deriving the user ID from the verified token.
8. **Enforce ownership** on update/delete; reject cross-user writes with 403.
9. **Route requests through the gateway** without putting business data in the gateway.
10. **Run smoke/security checks** using the commands and checklist below; record actual results after running locally.

## Setup

Use Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Set a unique `JWT_SECRET` in `.env` before use. Never commit real secrets.

## Start services

Run each command in a separate terminal from this project directory:

```bash
python -m users_service.app
python -m recipes_service.app
python -m gateway.app
```

The services bind to ports 5001, 5002, and 5000 respectively. The gateway exposes the client-facing API.

## API examples

Register:
```bash
curl -i -X POST http://127.0.0.1:5000/api/auth/register -H "Content-Type: application/json" -d '{"username":"alice","password":"TestPass123!"}'
```

Login:
```bash
curl -s -X POST http://127.0.0.1:5000/api/auth/login -H "Content-Type: application/json" -d '{"username":"alice","password":"TestPass123!"}'
```

Use the returned token as `TOKEN`:

```bash
TOKEN="paste-token-here"
curl -i http://127.0.0.1:5000/api/recipes -H "Authorization: Bearer $TOKEN"
curl -i -X POST http://127.0.0.1:5000/api/recipes -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"title":"Test Recipe","ingredients":"Flour, water","instructions":"Mix and bake"}'
```

## Database migrations

Each service initializes its own Flask-Migrate extension and has its own SQLAlchemy database URI. From the project root, set the service-specific Flask app and run migrations separately:

```bash
# Users database
export FLASK_APP=users_service.app:app
flask db init --directory users_service/migrations
flask db migrate -m "initial users schema" --directory users_service/migrations
flask db upgrade --directory users_service/migrations

# Recipes database (use a separate terminal or change FLASK_APP)
export FLASK_APP=recipes_service.app:app
flask db init --directory recipes_service/migrations
flask db migrate -m "initial recipes schema" --directory recipes_service/migrations
flask db upgrade --directory recipes_service/migrations
```

Do not share migration directories or database files between services.

## Smoke/security verification

The table below is the **expected test plan**, not a claim that tests ran in this environment. Run the commands locally and replace each status with the observed result.

| Check | Expected result | Actual result |
| --- | --- | --- |
| All three services start | All listen on their assigned ports | Not run here |
| Register a new username | 201 | Not run here |
| Duplicate username | 409 | Not run here |
| Valid login | 200 and token | Not run here |
| Invalid login | 401 | Not run here |
| Recipes request without token | 401 | Not run here |
| Create recipe with token | 201 | Not run here |
| Update/delete own recipe | Success | Not run here |
| Update/delete another user's recipe | 403 | Not run here |
| User and recipe data stored separately | Independent databases | Not run here |

## Important implementation notes

- This is a development starter, not production-hardened software.
- SQLite is for local learning. Configure production-grade database URLs, HTTPS, key rotation, rate limiting, logging, and secret management before deployment.
- The gateway is a simple HTTP reverse proxy. It does not own user or recipe data.
- The service databases are created by their migration workflows; the first migration must be generated and applied for a fresh checkout.
