from flask import Blueprint, redirect, render_template, request, url_for

from . import db
from .task_model import STATUS_LABELS, Task

task_bp = Blueprint("tasks", __name__)


@task_bp.route("/")
def index():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template("index.html", tasks=tasks)


@task_bp.route("/tasks/new", methods=["GET", "POST"])
def new_task():
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()

        if not title:
            return render_template("new_task.html", error="Please enter a task title."), 400

        db.session.add(Task(title=title, description=description))
        db.session.commit()
        return redirect(url_for("tasks.index"))

    return render_template("new_task.html", error=None)


@task_bp.route("/tasks/<int:task_id>/status", methods=["POST"])
def set_status(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        abort(404)

    status = request.form.get("status")
    if status not in STATUS_LABELS:
        abort(400)

    task.status = status
    db.session.commit()
    return redirect(url_for("tasks.index"))

@task_bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        abort(404)

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        status = request.form.get("status")

        if not title or status not in STATUS_LABELS:
            return render_template(
                "edit_task.html", task=task, statuses=STATUS_LABELS,
                error="Please enter a title and choose a valid status.",
            ), 400

        task.title = title
        task.description = (request.form.get("description") or "").strip()
        task.status = status
        db.session.commit()
        return redirect(url_for("tasks.index"))

    return render_template("edit_task.html", task=task, statuses=STATUS_LABELS, error=None)


@task_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        abort(404)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("tasks.index"))