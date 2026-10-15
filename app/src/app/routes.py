from flask import Blueprint, redirect, render_template, request, url_for

from . import db
from .task_model import Task

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
            return render_template("new_task.html", error="A task needs a title."), 400

        db.session.add(Task(title=title, description=description))
        db.session.commit()
        return redirect(url_for("tasks.index"))

    return render_template("new_task.html", error=None)