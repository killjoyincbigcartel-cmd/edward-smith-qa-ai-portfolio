from flask import request

from ..extensions import db
from ..models import Task
from . import tasks_bp


@tasks_bp.get("")
def list_tasks():
    tasks = Task.query.order_by(Task.id.asc()).all()
    return [task.to_dict() for task in tasks], 200


@tasks_bp.post("")
def create_task():
    payload = request.get_json(silent=True) or {}
    title = payload.get("title")

    if not isinstance(title, str) or not title.strip():
        return {"error": "title is required"}, 400

    task = Task(title=title.strip())
    db.session.add(task)
    db.session.commit()
    return task.to_dict(), 201
