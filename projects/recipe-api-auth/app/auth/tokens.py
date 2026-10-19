"""JWT creation and verification."""
from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app

from app.data.models import User


def create_token(user: User) -> str:
    secret = current_app.config.get("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET is required. Put it in .env.")

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=current_app.config["JWT_EXP_MINUTES"]
    )
    payload = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "exp": expires_at,
    }
    return jwt.encode(
        payload,
        secret,
        algorithm=current_app.config["JWT_ALGORITHM"],
    )


def decode_token(token: str):
    secret = current_app.config.get("JWT_SECRET")
    if not secret:
        return None

    try:
        return jwt.decode(
            token,
            secret,
            algorithms=[current_app.config["JWT_ALGORITHM"]],
        )
    except jwt.PyJWTError:
        return None
