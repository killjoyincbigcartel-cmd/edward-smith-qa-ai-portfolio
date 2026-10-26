# Architecture and Data Ownership

## Users Service
- Owns account and authentication records.
- Stores unique usernames and password hashes, never plaintext passwords.
- Handles registration and login and issues expiring JWTs.
- Listens on port 5001 and uses its own database.

## Recipes Service
- Owns recipe records and their `owner_id`.
- Listens on port 5002 and uses its own database.
- Verifies JWT signatures and expiry locally.
- Derives the acting user's ID from the verified token, never from request JSON.
- Checks ownership before update/delete and returns 403 when a recipe belongs to another user.

## API Gateway
- Listens on port 5000.
- Forwards `/api/auth/*` to Users and `/api/recipes*` to Recipes.
- Passes through request bodies, authorization headers, status codes, and responses.
- Stores no business data and does not query either service's database.

## Data ownership rule
Each service is the sole owner of its database and schema. The Recipes service does not import the Users service's ORM model, connect to the Users database, or perform cross-service joins. The shared JWT signing secret is configuration, not a shared data store. For a larger production system, consider asymmetric signing so the recipe service can verify tokens without being able to issue them.
