# Recipe API — JWT Auth, Ownership, and Ratings

A Flask + SQLite API using an application factory and separate route, service, and data/model layers.

## Features

- Password hashing, registration, and JWT login
- Shared authentication and owner/admin authorization
- Public and private recipe visibility
- Named application configurations
- Environment-based secrets
- Rate limiting for account endpoints and rating submissions
- Recipe count endpoint
- Recipe ratings with one rating per user per recipe, 1–5 score validation, and average/count reads
- Flask-Migrate/Alembic database migrations

## Setup

Run commands from `projects/recipe-api-auth`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set `JWT_SECRET` to a long, random value. Never commit `.env`; use the placeholder values in `.env.example`.

## Database migrations

Apply the schema before starting the server:

```bash
flask --app wsgi db upgrade
flask --app wsgi db current
```

The migration creates the rating table and its primary key, foreign keys, score check constraint, and unique user/recipe constraint. It also creates the existing user and recipe tables when initializing a fresh database. Existing databases keep their current user and recipe tables.

## Run and test

```bash
flask --app wsgi run
pytest -q
```

Run the tests in your local environment and use the actual output when reporting pass counts.

## Existing API

- `GET /health`
- `POST /register`
- `POST /login`
- `GET /recipes/<recipe_id>`
- `POST /recipes`
- `PATCH /recipes/<recipe_id>`
- `DELETE /recipes/<recipe_id>`
- `GET /api/recipes/count`

The original API does not have a `GET /recipes` collection endpoint.

## Rating API

### Submit or update a rating

```bash
curl -i -X POST http://127.0.0.1:5000/api/recipes/1/ratings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"score":5}'
```

The authenticated user's ID comes from the verified JWT request context. A score must be an integer from 1 to 5. A missing/invalid score returns 400, a nonexistent recipe returns 404, and missing or invalid authentication returns 401. Submitting another score for the same recipe updates the user's existing rating.

### Read rating summary

```bash
curl -i http://127.0.0.1:5000/api/recipes/1/ratings
```

The response includes `recipe_id`, `average_rating`, and `rating_count`. If a recipe has no ratings, the average is `null` and the count is zero.

## Scaling decision

The project uses Flask-Limiter with `get_remote_address`, so the rating write limit is 10 requests per minute per client IP. This reduces repeated submissions and unnecessary writes. The read endpoint uses SQL aggregate functions rather than loading all ratings into Python. Caching is not enabled for the rating summary so changes are reflected immediately; repeated reads still query the database, which can be optimized later if usage grows.

## Architecture

- `app/recipes/routes.py`: HTTP routes and JSON responses.
- `app/services/recipe_service.py`: recipe business logic.
- `app/services/rating_service.py`: rating validation, create/update behavior, and rating summary.
- `app/data/models.py`: SQLAlchemy models and relationships.
- `app/extensions.py`: SQLAlchemy, Flask-Migrate, and Flask-Limiter extensions.
- `app/auth/guards.py`: shared authentication and authorization guards.
- `migrations/`: Alembic migration environment and revision files.
- `tests/`: automated API tests.

## Authorization rules

- Missing, invalid, or expired token on protected writes -> 401.
- Valid token without permission -> 403.
- Owners can update/delete their own recipes; admins can update/delete any recipe.
- Registration always assigns role `user`.
- Recipe ownership and rating ownership are derived from the authenticated identity, not request-body user IDs.
