"""Account business logic, separate from HTTP and persistence."""
from app.auth.passwords import hash_password, verify_password
from app.auth.tokens import create_token
from app.data.users import create_user, get_user_by_username


def register_user(username, password):
    if not isinstance(username, str) or not username.strip():
        return {"error": "Username is required"}, 400
    if not isinstance(password, str) or not password:
        return {"error": "Password is required"}, 400

    username = username.strip()
    if get_user_by_username(username):
        return {"error": "Username already exists"}, 409

    user = create_user(username, hash_password(password), role="user")
    return {
        "message": "User created",
        "username": user.username,
        "role": user.role,
    }, 201


def login_user(username, password):
    if not isinstance(username, str) or not username:
        return {"error": "Username and password are required"}, 400
    if not isinstance(password, str) or not password:
        return {"error": "Username and password are required"}, 400

    user = get_user_by_username(username)
    if not user or not verify_password(user.password_hash, password):
        return {"error": "Invalid username or password"}, 401

    return {
        "message": "Login successful",
        "username": user.username,
        "role": user.role,
        "token": create_token(user),
    }, 200
