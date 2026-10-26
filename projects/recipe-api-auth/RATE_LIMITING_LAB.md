# Rate-Limiting Lab

This lab demonstrates the per-endpoint limits configured in this project. Run from `projects/recipe-api-auth` after installing `requirements.txt` and configuring `.env`.

## Limits in the app

- `POST /login`: 5 requests per minute per client IP.
- `POST /register`: 3 requests per hour per client IP.
- Recipe read routes: no rate limit is added in this lesson.

## Trigger a 429 on login

Start the app in one terminal:

```bash
flask --app wsgi run
```

In a second terminal, send more than five login requests in the same minute. These deliberately use invalid credentials, so no real password is needed:

```bash
for i in 1 2 3 4 5 6; do
  echo "Request $i"
  curl -sS -i -X POST http://127.0.0.1:5000/login \
    -H "Content-Type: application/json" \
    -d '{"username":"rate-limit-test-user","password":"not-the-password"}'
  echo
done
```

Because the limit is 5 per minute, one of the later requests should receive a response whose status line is `HTTP/1.1 429 TOO MANY REQUESTS` (the capitalization can vary). The first five may return the normal login failure response. The exact result depends on the limiter's current in-memory counter and whether other requests have already used the quota.

You can similarly test registration by sending four or more requests to `POST /register` within one hour. Use test-only usernames and do not repeatedly create real accounts.

## Understand the response

When the server returns `429 Too Many Requests`, it is telling the client that it exceeded the configured request limit and should wait before trying again.

With rate-limit headers enabled, inspect these response headers if they are present:

- `X-RateLimit-Limit`: the maximum number of requests allowed in the current limit window.
- `X-RateLimit-Remaining`: how many requests remain before the limit is reached.
- `Retry-After`: how long the client should wait before retrying, commonly expressed in seconds.

Header names and formatting can vary by Flask-Limiter version/configuration. Use the headers actually shown by your local response as evidence; do not claim a header appeared if it was not present.

## Why these endpoints are limited

- **Login:** slows repeated password guesses and brute-force attempts.
- **Register:** makes automated signup spam more difficult.
- **User impact:** a real person who mistypes credentials or submits forms repeatedly can be temporarily blocked. Limits should be conservative enough to avoid frustrating normal use.
- **Recipe reads:** not limited in this lesson because reads are lower risk than repeated authentication attempts and are a core usability feature. A production service could add broader protections if traffic or abuse patterns justify them.

## Record actual evidence

Paste the output from your own terminal before submitting. Capture the 429 status line and the rate-limit headers that your response actually includes.

- **Request that returned 429:** _paste actual status line_
- **Headers shown:** _paste actual X-RateLimit and/or Retry-After headers_
- **Meaning:** The client exceeded the endpoint's quota and must wait for the limit window to reset.
- **Note:** This document describes expected behavior; it is not a claim that the requests have already been run.
