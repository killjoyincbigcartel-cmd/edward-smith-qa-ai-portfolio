# Mini Tasks

A small Flask API built from scratch to practice the application factory pattern, blueprints, environment-based configuration, SQLAlchemy, and Flask-Migrate.

## Structure

    mini_tasks/
    ├── mini_tasks/
    │   ├── __init__.py
    │   ├── config.py
    │   ├── extensions.py
    │   ├── models.py
    │   └── tasks/
    │       ├── __init__.py
    │       └── routes.py
    ├── .env.example
    ├── .gitignore
    ├── requirements.txt
    └── wsgi.py

## Set up locally

Run these commands from this folder:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env

Edit .env and set a local secret. The example file contains placeholders only. The .env file is ignored by Git.

## Create the database schema with migrations

Run these from the project root after activating the virtual environment and creating .env:

    flask --app 'mini_tasks:create_app' db init
    flask --app 'mini_tasks:create_app' db migrate -m "create tasks table"
    flask --app 'mini_tasks:create_app' db upgrade

Only run db init once; keep the generated migrations/ directory in version control. The schema is created through db upgrade, not by calling db.create_all().

## Start and test

    flask --app 'mini_tasks:create_app' run

In another terminal:

    curl -i http://127.0.0.1:5000/health
    curl -i http://127.0.0.1:5000/tasks
    curl -i -X POST http://127.0.0.1:5000/tasks -H 'Content-Type: application/json' -d '{"title":"First task"}'
    curl -i http://127.0.0.1:5000/tasks

## Verification results

The setup, migration workflow, and API checks have been verified.

| Check | Expected result | Result |
|---|---|---|
| Application starts with the factory | App loads using `mini_tasks:create_app` | Verified |
| Health endpoint | `GET /health` returns HTTP 200 | Verified |
| Initial task list | `GET /tasks` returns an empty JSON list when no tasks exist | Verified |
| Create task | Valid `POST /tasks` returns HTTP 201 with the created task | Verified |
| List after creation | `GET /tasks` includes the created task | Verified |
| Database migrations | `db init`, `db migrate`, and `db upgrade` workflow completes | Verified |
| Environment configuration | Settings are read from environment variables / `.env` | Verified |
| Secret handling | Local `.env` is ignored by Git; `.env.example` uses placeholders | Verified |

## Configuration

- `FLASK_CONFIG` selects development, testing, or production.
- `SECRET_KEY` and `DATABASE_URL` come from environment variables.
- Testing config uses an in-memory SQLite database.
- `SQLALCHEMY_TRACK_MODIFICATIONS` is disabled.
