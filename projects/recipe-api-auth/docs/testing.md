# Recipe API Security Test Matrix

| Scenario | Expected |
|---|---|
| POST /recipes with no token | 401 |
| PATCH /recipes/:id with no token | 401 |
| DELETE /recipes/:id with no token | 401 |
| PATCH with invalid/tampered token | 401 |
| DELETE with expired token | 401 |
| Owner PATCH | 200 |
| Owner DELETE | 200 |
| Non-owner PATCH | 403 and no DB change |
| Non-owner DELETE | 403 and recipe remains |
| Admin PATCH on another user's recipe | 200 |
| Admin DELETE on another user's recipe | 200 |
| Public recipe GET | 200 without login |
| Private recipe GET by owner | 200 |
| Private recipe GET by another user | 403 |

## Example commands

### Anonymous delete

```bash
curl -i -X DELETE http://127.0.0.1:5000/recipes/1
```

Expected: 401.

### Non-owner delete

```bash
curl -i -X DELETE http://127.0.0.1:5000/recipes/1 \
  -H "Authorization: Bearer <NON_OWNER_TOKEN>"
```

Expected: 403 and the recipe remains.

### Owner update

```bash
curl -i -X PATCH http://127.0.0.1:5000/recipes/1 \
  -H "Authorization: Bearer <OWNER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Owner Updated"}'
```

Expected: 200.

### Admin update

```bash
curl -i -X PATCH http://127.0.0.1:5000/recipes/1 \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Admin Updated"}'
```

Expected: 200.
