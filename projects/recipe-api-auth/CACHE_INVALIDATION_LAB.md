# Cache Invalidation Lab

This lab checks that the cached public recipe list updates immediately after a successful write. Do not paste real passwords or tokens into screenshots or commit them to the repository.

## 1. Start the API and log in

```bash
flask --app app run
```

In another terminal, log in with an existing test account and copy the token from the response:

```bash
curl -s -X POST http://localhost:5000/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"YOUR_TEST_USERNAME","password":"YOUR_TEST_PASSWORD"}'
```

Set the token in your shell:

```bash
export TOKEN='PASTE_TEST_TOKEN_HERE'
```

## 2. Warm the cache

```bash
curl -i http://localhost:5000/recipes
```

Save the response. This is the public recipe list before the write.

## 3. Create a public recipe

```bash
curl -i -X POST http://localhost:5000/recipes \
  -H 'Authorization: Bearer '"$TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"title":"Cache invalidation smoke test","is_public":true}'
```

Save the response and note the new recipe ID.

## 4. Request the list again

```bash
curl -i http://localhost:5000/recipes
```

The final response should include `Cache invalidation smoke test`. The route clears the cache only after the write commits, so the next request should return fresh data.

## 5. Record evidence

Paste your actual terminal output below after running the commands. Do not use estimated timings or example output as if it were measured.

- **Warm GET response:** _paste actual output_
- **POST response:** _paste actual output_
- **GET after write:** _paste actual output_
- **What changed in the database:** The POST created one public recipe, if the request returned 201.
- **What the final GET should show:** The new public recipe appears in the list.

## 6. Reproducing the original stale-data failure

The fixed code clears the cache after successful writes, so it should not produce stale data. To demonstrate the original failure for a lesson, temporarily disable the `cache.clear()` line in each write handler, restart the app, warm `GET /recipes`, create or edit a public recipe, and request `GET /recipes` again within 30 seconds. The list can then show the cached old state. Restore the invalidation lines immediately afterward and repeat the test to verify the fix. Do not commit the temporary broken version.
