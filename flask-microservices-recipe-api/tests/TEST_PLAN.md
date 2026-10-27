# Gateway test plan

Start users (5001), recipes (5002), and gateway (5000) in separate terminals.

1. POST valid credentials to `http://localhost:5000/login`; confirm the users service's status and JSON response pass through.
2. Call `GET /me` without an Authorization header; expect HTTP 401.
3. Call `GET /me` with a valid user JWT while both services are healthy; expect both sections and both completeness labels to be complete.
4. Stop the recipes service and call `GET /me`; expect the user section to remain available and recipes completeness to indicate an upstream failure.
5. Stop the users service and keep recipes healthy; expect the recipes section to remain available and user completeness to indicate an upstream failure.
6. Stop both services; expect HTTP 502 with both sections marked missing.
7. Confirm the internal token is not present in the response body or logs and is not forwarded to the users service.

Example request:

```bash
curl -i http://localhost:5000/me -H 'Authorization: Bearer YOUR_USER_JWT'
```
