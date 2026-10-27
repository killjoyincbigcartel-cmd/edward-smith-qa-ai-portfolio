# Flask Microservices Recipe API

This folder contains the API gateway for a split Flask recipe API. The gateway owns no database and defines no ORM models; it forwards requests to the users and recipes services.

## Expected services

- Users service: `http://localhost:5001`
- Recipes service: `http://localhost:5002`
- Gateway: `http://localhost:5000`

The upstream services are expected to expose:

- `POST /login` on the users service, accepting the login JSON and returning a JSON response.
- `GET /me` on the users service, validating the forwarded user JWT and returning the current user's JSON.
- `GET /recipes` on the recipes service, validating the forwarded user JWT and, if required by your internal endpoint policy, the `X-Internal-Token` header.

If your existing services use different paths or response schemas, update the URLs in `gateway/routes.py` to match them.

## Setup

From this folder:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`. Set `RECIPES_INTERNAL_TOKEN` to the same secret value the recipes service expects as `INTERNAL_SERVICE_TOKEN`. Keep the real `.env` out of Git.

## Run three processes

Open three terminals. Activate the same virtual environment in each.

Terminal 1 (from the directory containing your users service):

```bash
flask --app users_service run -p 5001
```

Terminal 2 (from the directory containing your recipes service):

```bash
flask --app recipes_service run -p 5002
```

Terminal 3 (from `flask-microservices-recipe-api/`):

```bash
flask --app gateway run -p 5000
```

The users and recipes commands assume those packages expose a Flask app or app factory compatible with Flask CLI.

## Test through the gateway

Login (adjust the request fields to match your users service):

```bash
curl -i -X POST http://localhost:5000/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"YOUR_PASSWORD"}'
```

Use the returned JWT:

```bash
curl -i http://localhost:5000/me \
  -H 'Authorization: Bearer YOUR_USER_JWT'
```

The `/me` response combines the user and recipes sections. Each section has its own `completeness` label. One upstream timeout or failure does not prevent the gateway from returning the other section. If both upstream calls fail, the gateway returns HTTP 502.

## Design choices

- `/me` uses `asyncio.gather` to fetch both services concurrently.
- Each upstream call has a 1.5-second timeout by default; change `UPSTREAM_TIMEOUT` in `.env` if needed.
- The end-user JWT is forwarded to both services. The internal token is sent only to the recipes service and is never included in the response.
- The gateway does not create JWTs, access databases, or own business data.
