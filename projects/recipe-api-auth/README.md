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
- Flask application factory with named configurations
- Independent app instances for development and testing

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
├── tests/test_auth.py
├── wsgi.py
├── requirements.txt
└── .env.example
```

## Application factory

`app/__init__.py` defines `create_app(config_name, config_overrides=None)`. The `Flask(__name__)` object is created inside this function. Named configurations are in `app/config.py`:

- `development`: `DEBUG=True`
- `testing`: `TESTING=True`, `DEBUG=False`, in-memory SQLite database
- `production`: debug and testing modes are disabled

Each call returns a distinct Flask app instance. The package does not create a module-level app at import time.

For an independence check, run from the project directory:

```bash
python - <<'PY'
from app import create_app

app_dev = create_app("development")
app_test = create_app("testing")

print("same object:", app_dev is app_test)
print("dev DEBUG:", app_dev.config["DEBUG"])
print("test DEBUG:", app_test.config["DEBUG"])
print("test TESTING:", app_test.config["TESTING"])
PY
```

Expected values are `same object: False`, `dev DEBUG: True`, `test DEBUG: False`, and `test TESTING: True`.

## Run it

Run these commands **from the `projects/recipe-api-auth` directory**, not from the outer repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set `JWT_SECRET` to a long, random secret. Never commit `.env`.

Start the development app:

```bash
flask --app wsgi run
```

The entry point `wsgi.py` calls `create_app("development")`, validates the JWT secret, and initializes database tables. Importing the `app` package does not create a Flask app or create tables.

## Import and test checks

From the same project directory:

```bash
python -c 'from app import create_app; print(create_app("development"))'
python -c 'from app import create_app; a=create_app("development"); b=create_app("testing"); print(a is not b, a.config["DEBUG"], b.config["DEBUG"])'
pytest
```

## API smoke check

Register a user:

```bash
curl -i -X POST http://127.0.0.1:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"refactor-check","password":"RefactorPass123!"}'
```

Log in and copy the returned token:

```bash
curl -i -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"refactor-check","password":"RefactorPass123!"}'
```

Create a public recipe with that token:

```bash
curl -i -X POST http://127.0.0.1:5000/recipes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title":"Refactor smoke test","is_public":true}'
```

Then fetch the recipe by the ID returned by the create call:

```bash
curl -i http://127.0.0.1:5000/recipes/RECIPE_ID
```

**Route note:** The current API has `GET /recipes/<recipe_id>` to fetch one recipe. It does not currently have a collection/list endpoint at `GET /recipes`; this refactor preserves the original routes instead of silently adding a new API contract.

## Auth rules

- Missing, invalid, or expired token on protected route -> 401 Unauthorized
- Valid token but no permission -> 403 Forbidden
- Recipe owner -> can update/delete their own recipe
- Admin -> can update/delete any recipe
- New registrations always get role="user"
- Client-supplied role is ignored
- `owner_id` always comes from the verified token identity

## Admin testing

Registration never allows a client to choose admin. Use the included `make_admin.py` helper to promote a test account directly in the database.

## Structure responsibilities

- `app/__init__.py` creates and configures each Flask app instance.
- `wsgi.py` exposes the development app to Flask and WSGI servers and initializes database tables for a normal run.
- `app/auth/` contains account routes, password helpers, JWT logic, and shared guards.
- `app/data/models.py` contains the SQLAlchemy models.
- `app/recipes/` contains recipe endpoints and permission policy helpers.
- `app/web/routes.py` contains the health endpoint.

The public API routes, status codes, and response fields are intended to stay the same during this refactor.
