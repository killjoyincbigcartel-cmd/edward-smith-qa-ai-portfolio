import os
from flask import Flask

from .config import config_by_name
from .extensions import db, migrate
from .tasks import tasks_bp


def create_app(config_class=None):
    """Create and configure a Mini Tasks application."""
    app = Flask(__name__, instance_relative_config=True)

    if config_class is None:
        config_name = os.getenv("FLASK_CONFIG", "development").lower()
        config_class = config_by_name.get(config_name, config_by_name["development"])

    app.config.from_object(config_class)
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so Flask-Migrate can detect them.
    from . import models  # noqa: F401

    app.register_blueprint(tasks_bp, url_prefix="/tasks")

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "mini-tasks"}, 200

    return app
