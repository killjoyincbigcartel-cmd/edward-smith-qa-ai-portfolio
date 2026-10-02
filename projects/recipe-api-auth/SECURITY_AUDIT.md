# Recipe API Security Audit

**Date:** October 2, 2026  
**Project:** Recipe API — JWT Auth, Ownership & Admin Authorization  
**Scope:** Single-service Flask API security review

## Audit summary

This audit checks the main security controls covered in the course: password storage, JWT authentication, ownership checks, role-based authorization, centralized protection, and regression against earlier access-control problems.

**Important:** The code-level findings below are based on a review of the current project files. Runtime request/response and database evidence should be captured by running the API and tests locally. No local runtime output is being represented here as if it was already observed.

---

## 1. Password storage

| Protection | Evidence | Status |
| :--- | :--- | :--- |
| Passwords hashed | `hash_password()` uses Werkzeug `generate_password_hash()` | PASS |
| Password verification | `verify_password()` uses `check_password_hash()` | PASS |
| Plaintext passwords stored | User model stores `password_hash`, not a plaintext password | PASS |

### Example code

```python
def hash_password(password: str) -> str:
    return generate_password_hash(password)

def verify_password(stored_hash: str, candidate_password: str) -> bool:
    return check_password_hash(stored_hash, candidate_password)
```

---

## 2. Authentication: anonymous and invalid-token writes

Protected write routes use the shared `require_auth` guard.

| Protection | Request | Expected | Runtime evidence |
| :--- | :--- | :--- | :--- |
| No anonymous writes | `POST /recipes` without token | 401 + no DB change | Run locally |
| No invalid-token writes | `POST /recipes` with fake token | 401 + no DB change | Run locally |
| No expired-token writes | Protected route with expired JWT | 401 + no DB change | Run locally |

### Expected commands

```bash
curl -i -X POST http://127.0.0.1:5000/recipes \
  -H "Content-Type: application/json" \
  -d '{"title":"Unauthenticated Test"}'
```

Expected: **401 Unauthorized** and no recipe created.

```bash
curl -i -X POST http://127.0.0.1:5000/recipes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid.token.here" \
  -d '{"title":"Bad Token Test"}'
```

Expected: **401 Unauthorized** and no recipe created.

---

## 3. Ownership checks

Recipe mutations use the authenticated identity from the verified JWT.

| Protection | Request | Expected | Runtime evidence |
| :--- | :--- | :--- | :--- |
| Owner can update own recipe | `PATCH /recipes/:id` as owner | 200 | Run locally |
| Cross-user update blocked | `PATCH /recipes/:id` as another user | 403 + no DB change | Run locally |
| Cross-user delete blocked | `DELETE /recipes/:id` as another user | 403 + no DB change | Run locally |
| Owner can delete own recipe | `DELETE /recipes/:id` as owner | 200 + row removed | Run locally |

The important authorization rule is:

```python
is_owner = recipe.owner_id == g.current_user_id
is_admin = g.current_role == "admin"

if not is_owner and not is_admin:
    return jsonify({"error": "Forbidden"}), 403
```

The route does **not** take ownership from the request body.

---

## 4. Admin authorization

New registrations always create normal users:

```python
user = User(
    username=username,
    password_hash=hash_password(password),
    role="user",
)
```

The client cannot promote itself to admin through registration.

| Protection | Request | Expected | Runtime evidence |
| :--- | :--- | :--- | :--- |
| Normal user blocked from another user's recipe | PATCH/DELETE | 403 | Run locally |
| Admin can update another user's recipe | PATCH | 200 | Run locally |
| Admin can delete another user's recipe | DELETE | 200 | Run locally |

Admin test accounts are promoted directly in the database with `make_admin.py`, not through client input.

---

## 5. Centralized middleware / decorators

The project uses reusable guards so protected write routes do not each implement their own JWT parsing.

### `require_auth`

Responsible for:

- Reading `Authorization: Bearer <token>`
- Verifying the JWT signature
- Rejecting missing, malformed, invalid, and expired tokens with 401
- Making `current_user_id` and `current_role` available through Flask `g`

### `require_owner_or_admin`

Responsible for:

- Loading the target recipe
- Checking recipe ownership
- Allowing the owner or an admin
- Returning 403 when a verified normal user is not the owner

Protected write routes use these guards:

```python
@app.post("/recipes")
@require_auth
def create_recipe():
    ...

@app.patch("/recipes/<int:recipe_id>")
@require_owner_or_admin
def update_recipe(recipe_id):
    ...

@app.delete("/recipes/<int:recipe_id>")
@require_owner_or_admin
def delete_recipe(recipe_id):
    ...
```

---

## 6. Previous exploit regression tests

| Previous problem | Protected behavior now | Status |
| :--- | :--- | :--- |
| Anonymous recipe creation | 401 and no DB change | Run locally |
| Invalid/tampered JWT | 401 | Run locally |
| Expired JWT | 401 | Run locally |
| Cross-user recipe update | 403 and no DB change | Run locally |
| Cross-user recipe delete | 403 and recipe remains | Run locally |
| Owner mutation | 2xx and DB changes | Run locally |
| Admin mutation | 2xx and DB changes | Run locally |

The included test suite already covers representative authentication and authorization cases, including missing token, expired token, owner update, non-owner 403 with unchanged data, and admin deletion.

---

## 7. Security notes

- `.env` is ignored by Git.
- `.env.example` contains only a placeholder secret.
- The real JWT signing secret must stay in `.env` or another secret store.
- JWT payloads are readable, so passwords and other secrets do not belong in the token.
- A valid JWT is not enough for recipe mutation; ownership or admin authorization is checked before the database change.
- Denied authorization attempts return before mutation, so the recipe should remain unchanged.

---

## 8. Final conclusion

From the code review, the main single-service protections covered by this course are in place:

- Passwords are hashed instead of stored as plaintext.
- JWT authentication is centralized for protected write routes.
- Missing, invalid, and expired tokens are treated as 401.
- Valid but unauthorized users are treated as 403.
- Owners can modify their own recipes.
- Admins can moderate recipes outside their ownership.
- Client input cannot choose `owner_id` or promote itself to admin.

### Final runtime step

Run the API, execute the curl commands and pytest suite, and replace the **"Run locally"** entries above with the actual observed status codes and database results.
