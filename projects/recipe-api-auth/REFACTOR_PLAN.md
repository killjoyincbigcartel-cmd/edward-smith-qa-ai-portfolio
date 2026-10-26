# Recipe API Refactor Plan

**Date:** October 18, 2026  
**Baseline implementation on `main` before refactor:** `projects/recipe-api-auth/app.py`  
**Refactor branch:** `refactor/recipe-api-package-structure`; the current implementation on this branch lives in `projects/recipe-api-auth/app/` with `projects/recipe-api-auth/wsgi.py`.  
**Scope:** Records the original API contract, implemented package layout, and verification status for the refactor branch.

## 1. Single-file pain: import check

The original single-file implementation imported Flask and its extensions at module import time, raised an error immediately when `JWT_SECRET` was missing, and called `db.create_all()` at the bottom of `app.py`. That tied importing the module to runtime configuration and database initialization.

**Environment check:** The Python environment available while editing this GitHub branch does not have Flask installed; checking the dependency produced `ModuleNotFoundError: No module named 'flask'`. Because of that, I could not run the original application or verify HTTP responses in this environment. This is a dependency limitation, not proof that the app would fail in a correctly configured local virtual environment.

**Run these import checks locally after installing `requirements.txt`, from `projects/recipe-api-auth`:**

```bash
python -c 'from app import create_app; print(create_app("development"))'
python -c 'from app import create_app; a=create_app("development"); b=create_app("testing"); print(a is not b, a.config["DEBUG"], b.config["DEBUG"])'
```

The package refactor does not create a global Flask object at import time. Each `create_app(config_name)` call constructs/configures its own Flask object and registers blueprints. `wsgi.py` calls `create_app("development")`, checks that `JWT_SECRET` is configured, and initializes the database when starting with `flask --app wsgi run`. These startup and HTTP behaviors still need local runtime verification.

## 2. Responsibilities currently living in `app.py`

**Counting rule:** Count one responsibility for each cohesive concern that could reasonably move into a module. Related endpoints are grouped by feature rather than counting every individual route as its own responsibility.

1. **Application configuration** — load `.env`, read `DATABASE_URL`, read the JWT secret and token expiry setting.
2. **Database and models** — create the Flask/SQLAlchemy objects, define `User` and `Recipe`, and create tables.
3. **Password utilities** — hash passwords and verify login candidates.
4. **Token authentication** — issue JWTs, read bearer headers, decode/verify tokens, and load the authenticated user.
5. **Authorization rules** — check recipe ownership and admin role; enforce private recipe visibility.
6. **Health endpoint** — answer `GET /health`.
7. **Account endpoints** — register users and log users in.
8. **Recipe endpoints** — read, create, update, and delete recipes, including request validation and database writes.

**Responsibilities in app.py: 8**

One thing the refactor should improve: private `GET /recipes/<recipe_id>` currently repeats bearer-token parsing and JWT decoding instead of using the same shared auth guard as protected write routes.

## 3. Target package layout (implemented on the refactor branch)

The goal is to keep the public API contract the same while moving each concern to a clearer home.

```text
recipe-api-auth/
├── app/
│   ├── __init__.py          # create_app(); no global app object
│   ├── config.py            # named config classes
│   ├── extensions.py        # SQLAlchemy extension
│   ├── data/
│   │   ├── __init__.py
│   │   └── models.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── passwords.py
│   │   ├── tokens.py
│   │   └── guards.py
│   ├── recipes/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── policies.py
│   └── web/
│       ├── __init__.py
│       └── routes.py
├── tests/
│   └── test_auth.py
├── wsgi.py
├── make_admin.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── SECURITY_AUDIT.md
```

This layout was first recorded as the plan and then implemented on `refactor/recipe-api-package-structure`. The original single-file implementation remains on `main`. The acceptance list below records the baseline behavior the refactor is intended to preserve.

## 4. Acceptance list — existing public API contract

Each numbered row is one acceptance item/test scenario. A refactor should keep these outcomes stable unless a separate, explicitly agreed API change is made. Recipe ownership in this implementation is stored as `owner_id`.

| # | Method + path | Scenario | Expected result |
|---:|---|---|---|
| 1 | `GET /health` | Health check | `200`, JSON status is `ok` |
| 2 | `POST /register` | Username missing or blank | `400`, validation error |
| 3 | `POST /register` | Password missing or blank | `400`, validation error |
| 4 | `POST /register` | Username already exists | `409`, no second account created |
| 5 | `POST /register` | Valid new account | `201`, returns message, username, and default role `user`; no password/hash returned |
| 6 | `POST /login` | Username missing | `400`, required-fields error |
| 7 | `POST /login` | Password missing | `400`, required-fields error |
| 8 | `POST /login` | Unknown username | `401`, generic invalid-credentials response |
| 9 | `POST /login` | Existing username, wrong password | `401`, same generic response as unknown username |
| 10 | `POST /login` | Valid credentials | `200`, returns username, role, and signed JWT; no password/hash returned |
| 11 | `GET /recipes/<recipe_id>` | Recipe ID does not exist | `404`, recipe not found |
| 12 | `GET /recipes/<recipe_id>` | Existing public recipe, no token | `200`, public recipe data |
| 13 | `GET /recipes/<recipe_id>` | Existing private recipe, no token | `401`, unauthorized |
| 14 | `GET /recipes/<recipe_id>` | Private recipe with invalid or expired token | `401`, unauthorized |
| 15 | `GET /recipes/<recipe_id>` | Private recipe requested by a different ordinary user | `403`, forbidden |
| 16 | `GET /recipes/<recipe_id>` | Private recipe requested by its owner | `200`, private recipe data |
| 17 | `POST /recipes` | No bearer token | `401`, no recipe created |
| 18 | `POST /recipes` | Invalid or expired token | `401`, no recipe created |
| 19 | `POST /recipes` | Missing, blank, or non-string title | `400`, validation error |
| 20 | `POST /recipes` | `is_public` is not a boolean | `400`, validation error |
| 21 | `POST /recipes` | Valid title and valid token | `201`, recipe created with `owner_id` from verified identity |
| 22 | `POST /recipes` | Client includes another `owner_id` in body | `201`, created recipe still belongs to token identity |
| 23 | `PATCH /recipes/<recipe_id>` | No bearer token | `401`, no recipe change |
| 24 | `PATCH /recipes/<recipe_id>` | Invalid or expired token | `401`, no recipe change |
| 25 | `PATCH /recipes/<recipe_id>` | Valid token, recipe ID does not exist | `404`, recipe not found |
| 26 | `PATCH /recipes/<recipe_id>` | Authenticated non-owner, not admin | `403`, recipe stays unchanged |
| 27 | `PATCH /recipes/<recipe_id>` | Owner submits valid update | `200`, requested recipe field changes |
| 28 | `PATCH /recipes/<recipe_id>` | Admin updates another user's recipe | `200`, requested recipe field changes |
| 29 | `PATCH /recipes/<recipe_id>` | Owner submits a blank/non-string title | `400`, invalid title rejected |
| 30 | `PATCH /recipes/<recipe_id>` | Owner submits non-boolean `is_public` | `400`, invalid value rejected |
| 31 | `PATCH /recipes/<recipe_id>` | Client tries to change `owner_id` in body | `200` currently; `owner_id` remains unchanged |
| 32 | `PATCH /recipes/<recipe_id>` | Empty body or only unrecognized fields | `200` currently; recipe remains unchanged (noted as current behavior to preserve during refactor) |
| 33 | `DELETE /recipes/<recipe_id>` | No bearer token | `401`, recipe remains |
| 34 | `DELETE /recipes/<recipe_id>` | Invalid or expired token | `401`, recipe remains |
| 35 | `DELETE /recipes/<recipe_id>` | Valid token, recipe ID does not exist | `404`, recipe not found |
| 36 | `DELETE /recipes/<recipe_id>` | Authenticated non-owner, not admin | `403`, recipe remains in database |
| 37 | `DELETE /recipes/<recipe_id>` | Owner deletes own recipe | `200`, success message and recipe is removed |
| 38 | `DELETE /recipes/<recipe_id>` | Admin deletes another user's recipe | `200`, success message and recipe is removed |

**Acceptance list items: 38**

## 5. Scoreboard

- **Responsibilities in app.py: 8**
- **Acceptance list items: 38**

## 6. Refactor guardrails

- Keep existing method/path pairs and response/status semantics stable.
- Move JWT validation into one shared guard and use it on every protected route, including private recipe reads.
- Make the verified identity available to handlers through Flask `g` (or an equivalent request-scoped object).
- Keep ownership/admin authorization separate from token validation: missing/invalid/expired token is `401`; authenticated but unauthorized mutation is `403`.
- Denied update/delete requests must return before mutation and leave the database unchanged.
- Do not accept `owner_id` or `role` as trusted client input.
- Add an application factory so importing modules does not create tables or depend on the runtime server starting.
- Run the full acceptance suite before considering the refactor complete.


## 7. Implementation verification status

- Package files and `wsgi.py` have been updated on `refactor/recipe-api-package-structure`.
- The old `projects/recipe-api-auth/app.py` file is removed on this branch. `app/__init__.py` exports `create_app`, models, the extension, and helper functions, but does not create a module-level Flask app.
- `create_app("development")` and `create_app("testing")` apply different named configurations. A regression test checks that the returned objects are different and the `DEBUG`/`TESTING` values differ.
- `wsgi.py` exposes the development app by calling `create_app("development")` and initializes tables for normal server startup.
- The README documents running from `projects/recipe-api-auth` with `flask --app wsgi run`.
- Runtime import checks, HTTP requests, and the pytest suite have not been run in this editing environment because Flask and Flask-SQLAlchemy are not installed there. Run them locally after `pip install -r requirements.txt`.
- The baseline has no `GET /recipes` collection endpoint. Its read endpoint is `GET /recipes/<recipe_id>`, and that route is preserved.


## 8. Recipe ratings feature

The ratings feature is implemented on this branch in addition to the 38 baseline acceptance scenarios above.

- `POST /api/recipes/<recipe_id>/ratings`: requires the shared bearer-token auth guard, accepts an integer score from 1 through 5, and creates or updates the authenticated user's rating.
- `GET /api/recipes/<recipe_id>/ratings`: returns the average rating and rating count, using SQL aggregate functions.
- `Rating` in `app/data/models.py`: includes user/recipe foreign keys, relationships, a unique constraint on the user/recipe pair, and a score check constraint.
- `app/services/rating_service.py`: handles validation, recipe existence checks, create/update behavior, and the summary query.
- `app/recipes/routes.py`: exposes both endpoints. The POST endpoint uses the existing `require_auth` guard and a `10 per minute` Flask-Limiter limit keyed by client IP.
- `tests/test_ratings.py`: covers POST/GET behavior, updates without duplicates, invalid scores, missing recipes, and authentication.
- `migrations/versions/20261026_add_rating.py`: creates the rating table and its constraints. On a fresh database it also creates the existing user and recipe tables; on an existing database it leaves those tables intact.

Run `pip install -r requirements.txt`, then `flask --app wsgi db upgrade`, `flask --app wsgi db current`, and `pytest -q` from this directory to verify the migration and runtime behavior. The 38 baseline acceptance items remain the original API contract; the new rating tests are additional coverage, not part of that baseline count.
