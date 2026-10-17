
import pytest

from app import create_app, db
from app.task_model import Task


@pytest.fixture(autouse=True)
def _in_memory_database(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite://")


@pytest.fixture
def app():
    """A fresh app with empty tables, torn down after the test."""
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_task(app):
    """Factory that inserts a task and returns it."""

    def _make_task(title="Write report", description="", status="pending"):
        task = Task(title=title, description=description, status=status)
        db.session.add(task)
        db.session.commit()
        return task

    return _make_task