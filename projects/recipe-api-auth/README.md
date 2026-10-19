# Recipe API — JWT Auth, Ownership & Admin Authorization

A Flask + SQLite recipe API built as a security-focused project. The code is organized as a Python package so app setup, authentication, models, and recipe routes have separate homes.

## What this project demonstrates

- Password hashing with Werkzeug
- User registration and login
- JWT access tokens with expiration
- Centralized JWT authentication
- Owner-or-admin authorization
- Owner-stamped recipes
- Private vs public recipe visibility
- Correct 401 vs 403 behavior
- Protection against cross-user edit/delete
- Tests for anonymous, owner, non-owner, and admin requests
- Flask application factory and separate WSGI entry point

## Project layout

```text
recipe-api-auth/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── data/models.py
│   ├── auth/
│   │   ├── routes.py
│   │   ├── passwords.py
│   │   ├── tokens.py
│   │   └── guards.py
│   ├── recipes/
│   │   ├── routes.py
│   │   └── policies.py
│   └── web/routes.py
├── tests/
├── wsgi.py
├── requirements.txt
└── .env.example
```

## Auth rules

- No token / invalid token / expired token -> 401 Unauthorized
- Valid token but no permission -> 403 Forbidden
- Recipe owner -> can update/delete their own recipe
- Admin -> can update/delete any recipe
- New registrations always get role="user"
- Client-supplied role is ignored
- `owner_id` always comes from the verified identity

## Run it

Run these commands **from the `projects/recipe-api-auth` directory**, not the outer GitHub repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set `JWT_SECRET` to a long, random secret. Never commit `.env`.

Start the API:

```bash
flask --app wsgi run
```

The WSGI entry point creates the tables for a first run. Importing the `app` package itself does not create tables.

## Check the imports

From the same project directory:

```bash
python -c "import app; print(app.app)"
python -c "from app import app; print(app.name)"
```

## Run the tests

```bash
pytest
```

## Example login

```bash
curl -i -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"MyFakePass123!"}'
```

Copy the token from the response.

## Example protected write

```bash
curl -i -X DELETE http://127.0.0.1:5000/recipes/1 \
  -H "Authorization: Bearer <TOKEN>"
```

Anonymous or invalid token -> 401.

Logged-in non-owner -> 403 and the database stays unchanged.

Owner or admin -> 2xx and the write is applied.

## Admin testing

Registration never allows a client to choose admin. Use the included `make_admin.py` helper to promote a test account directly in the database.

## Structure responsibilities

- `app/__init__.py` creates/configures the Flask app and registers route blueprints.
- `wsgi.py` exposes the app to Flask and WSGI servers and initializes database tables for a normal run.
- `app/auth/` contains account routes, password helpers, JWT logic, and shared guards.
- `app/data/models.py` contains the SQLAlchemy models.
- `app/recipes/` contains recipe endpoints and permission policy helpers.
- `app/web/routes.py` contains the health endpoint.

The public API routes, status codes, and response fields are intended to stay the same during this refactor.
