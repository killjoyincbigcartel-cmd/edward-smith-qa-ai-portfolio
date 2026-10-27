"""Promote a local test account to admin.

Run from flask-microservices-recipe-api:
    python -m users_service.make_admin challenge-user
Only use this helper with a local development database and disposable test account.
"""
import sys

from . import User, create_app, db


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python -m users_service.make_admin USERNAME")
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username=sys.argv[1]).first()
        if user is None:
            raise SystemExit(f"No user found with username: {sys.argv[1]}")
        user.role = "admin"
        db.session.commit()
        print(f"Promoted {user.username} to admin.")


if __name__ == "__main__":
    main()
