import os
from pathlib import Path

import pytest
from flask_migrate import upgrade
from sqlalchemy import inspect, text
from sqlalchemy.engine import make_url

from app import create_app, db
from app.task_model import Task

MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "migrations"


def _reset_schema():
    db.session.remove()
    db.engine.dispose()
    with db.engine.begin() as connection:
        connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))


@pytest.fixture
def pg_app(monkeypatch):
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is not set; skipping PostgreSQL tests")
    if "test" not in (make_url(url).database or ""):
        pytest.fail("TEST_DATABASE_URL must point at a database whose name contains 'test'")

    monkeypatch.setenv("DATABASE_URL", url)
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        _reset_schema()
        upgrade(directory=str(MIGRATIONS_DIR))
        yield app
        _reset_schema()


def test_migrations_create_the_tasks_table(pg_app):
    tables = inspect(db.engine).get_table_names()

    assert "tasks" in tables
    assert "alembic_version" in tables


def test_health_reports_connected_postgres(pg_app):
    response = pg_app.test_client().get("/health")

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"


def test_task_lifecycle_against_postgres(pg_app):
    client = pg_app.test_client()

    # create
    client.post("/tasks/new", data={"title": "Deploy app", "description": "to AWS"})
    task = db.session.query(Task).one()
    assert (task.title, task.status) == ("Deploy app", "pending")

    # change status
    client.post(f"/tasks/{task.id}/status", data={"status": "in_progress"})
    assert db.session.get(Task, task.id).status == "in_progress"

    # edit
    client.post(
        f"/tasks/{task.id}/edit",
        data={"title": "Deploy app v2", "description": "done", "status": "complete"},
    )
    edited = db.session.get(Task, task.id)
    assert (edited.title, edited.status) == ("Deploy app v2", "complete")
    assert edited.updated_at >= edited.created_at

    # delete
    client.post(f"/tasks/{task.id}/delete")
    assert db.session.query(Task).count() == 0


def test_tasks_persist_after_the_app_restarts(pg_app):
    """Mirrors the 'restart the production container' demo scenario."""
    pg_app.test_client().post("/tasks/new", data={"title": "Survive a restart"})
    db.session.remove()

    restarted_app = create_app()  # a brand-new app and database engine
    with restarted_app.app_context():
        titles = [task.title for task in db.session.query(Task).all()]

    assert titles == ["Survive a restart"]