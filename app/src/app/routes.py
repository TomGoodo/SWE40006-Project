from flask import Blueprint, redirect, render_template, request, url_for

from . import db
from .task_model import Task

task_bp = Blueprint("tasks", __name__)


@task_bp.route("/")
def index():
    return render_template("index.html")


@task_bp.route("/tasks", methods=["POST"])
def create_task():
    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip()

    if not title:
        return redirect(url_for("tasks.index"))

    task = Task(title=title, description=description)
    db.session.add(task)
    db.session.commit()
    return redirect(url_for("tasks.index"))

 "http://127.0.0.1:5000/debug/tasks"
@task_bp.route("/debug/tasks")
def debug_tasks():
    return {"tasks": [t.title for t in Task.query.all()]}