# Gateway service contract

## Trust boundaries

- Client -> users service: the users service validates login credentials and issues the user JWT.
- Client -> gateway -> users service: the gateway forwards the user's bearer token; the users service validates it on `GET /me`.
- Gateway -> recipes service: the gateway forwards the bearer token for user identity and sends `X-Internal-Token` using `RECIPES_INTERNAL_TOKEN`. The recipes service must validate the JWT and the internal token when its route requires both.

A localhost address is not proof of identity. The internal token must be a high-entropy secret supplied through environment configuration, never committed to Git, and compared safely by the recipes service.

## Aggregated response

`GET /me` returns:

```json
{
  "user": {"id": 1, "email": "you@example.com"},
  "recipes": [],
  "completeness": {
    "user": "complete",
    "recipes": "complete"
  }
}
```

If an upstream times out, its section becomes `null` and its completeness value becomes `missing: timeout`. Connection errors, non-2xx responses, and invalid JSON are labeled as missing rather than silently presented as complete.

## Login

`POST /login` forwards the incoming JSON body to the users service and passes through its JSON response and HTTP status. The gateway does not create a token itself.
