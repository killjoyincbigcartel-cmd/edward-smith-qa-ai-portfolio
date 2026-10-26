# Endpoints That Should Never Be Cached

These routes must bypass response caching because they involve credentials, user-specific authorization, or immediate account changes.

- `POST /login` — validates current credentials and returns a user-specific JWT. Never cache authentication results or tokens.
- `POST /register` — creates an account and must reflect current username availability immediately.
- `POST /recipes` — writes new recipe data; cache invalidation happens after the database commit.
- `PATCH /recipes/<recipe_id>` — changes recipe data and must invalidate the cached list after the commit.
- `DELETE /recipes/<recipe_id>` — removes recipe data and must invalidate the cached list after the commit.
- `GET /recipes/<recipe_id>` — can return private recipe details after authorization, so a shared cache could expose one user's data to another.

Only the public list endpoint `GET /recipes` is cached in this project. It returns public recipes only and uses a 30-second timeout. Recipe write handlers clear the cache after a successful database commit.
