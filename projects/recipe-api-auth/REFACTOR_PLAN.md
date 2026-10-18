# Recipe API Refactor Plan

**Date:** October 18, 2026  
**Current implementation:** `projects/recipe-api-auth/app.py`  
**Scope:** Planning only. This file records the current behavior and a target layout; no refactor files are created by this plan.

## 1. Single-file pain: import check

I tried importing the current project app in this execution environment using a temporary copy of the current `app.py`.

**Command run:**

```bash
cd /tmp/recipe-api-auth-check
JWT_SECRET='local-test-secret' python -c 'import app'
```

**Observed output:**

```text
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import app
  File "/tmp/recipe-api-auth-check/app.py", line 7, in <module>
    from flask import Flask, g, jsonify, request
ModuleNotFoundError: No module named 'flask'
```

This is actual output from the current execution environment, not a claim that the command was run on the developer's own computer. The import check could not get past the missing Flask dependency, so it did not verify the later startup behavior.

**What made it awkward:** Even a quick import check needs the app's dependencies installed. Also, the current module runs `db.create_all()` at import time, which couples importing the module to application/database setup. The refactor should use an application factory and explicit test setup so imports are easier to control.

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

## 3. Target package layout (planning only)

The goal is to keep the public API contract the same while moving each concern to a clearer home.

```text
recipe-box/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── wsgi.py
├── app/
│   ├── __init__.py          # create_app(); register blueprints
│   ├── config.py            # environment/config settings
│   ├── extensions.py        # SQLAlchemy instance and shared extensions
│   ├── data/
│   │   ├── __init__.py
│   │   ├── models.py        # User and Recipe models
│   │   └── repositories.py  # database access helpers, if useful
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py        # POST /register and POST /login
│   │   ├── passwords.py     # hash and verify passwords
│   │   ├── tokens.py        # issue and verify JWTs
│   │   └── guards.py        # require_auth, owner/admin checks
│   ├── recipes/
│   │   ├── __init__.py
│   │   ├── routes.py        # recipe HTTP endpoints
│   │   ├── policies.py      # ownership and visibility decisions
│   │   └── schemas.py       # request validation, if useful
│   └── web/
│       ├── __init__.py
│       └── routes.py        # GET /health
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_recipe_visibility.py
│   ├── test_recipe_ownership.py
│   └── test_admin.py
└── docs/
    └── SECURITY_AUDIT.md
```

No files in this target layout are created as part of this planning step. `REFACTOR_PLAN.md` records the intended destination only.

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
