# Recipe API — JWT Auth, Ownership & Admin Authorization

A Flask + SQLite recipe API built as a security-focused project.

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

## Auth rules

- No token / invalid token / expired token -> 401 Unauthorized
- Valid token but no permission -> 403 Forbidden
- Recipe owner -> can update/delete their own recipe
- Admin -> can update/delete any recipe
- New registrations always get role="user"
- Client-supplied role is ignored
- owner_id always comes from the verified JWT identity

## Run it

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app app run
```

Use a real random secret in .env. Never commit .env.

## Example login

```bash
curl -s -X POST http://127.0.0.1:5000/login \
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

Registration never allows a client to choose admin. Use the included make_admin.py helper to promote a test account directly in the database.

## Security notes

JWT payloads are readable by anyone holding the token, so passwords and other secrets never belong in the payload. The API trusts user_id and role only after the JWT signature and expiration are verified.

The shared decorators keep authentication and owner/admin checks out of the individual write routes so a route cannot accidentally skip the security checks.
