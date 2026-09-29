"""Promote a test account directly in the database."""

import sys

from app import User, app, db

username = sys.argv[1] if len(sys.argv) > 1 else None

if not username:
    raise SystemExit("Usage: python make_admin.py <username>")

with app.app_context():
    user = User.query.filter_by(username=username).first()

    if user is None:
        raise SystemExit(f"User not found: {username}")

    user.role = "admin"
    db.session.commit()

    print(f"{username} is now an admin.")
