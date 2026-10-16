import pytest

from app import db
from app.task_model import STATUS_LABELS, Task


def test_new_task_gets_defaults(make_task):
    task = make_task("Defaults")

    assert task.id is not None
    assert task.status == "pending"
    assert task.created_at is not None
    assert task.updated_at is not None


def test_description_is_optional(app):
    task = Task(title="No description")
    db.session.add(task)
    db.session.commit()

    assert db.session.get(Task, task.id).description is None


def test_updated_at_moves_forward_when_task_changes(make_task):
    task = make_task("Change me")
    first_updated = task.updated_at

    task.title = "Changed"
    db.session.commit()

    assert task.updated_at >= first_updated


@pytest.mark.parametrize(("status", "label"), STATUS_LABELS.items())
def test_status_label_for_known_statuses(status, label):
    assert Task(title="x", status=status).status_label == label


def test_status_label_falls_back_to_raw_value():
    assert Task(title="x", status="mystery").status_label == "mystery"


def test_repr_includes_title_and_status(make_task):
    task = make_task("Visible", status="complete")

    text = repr(task)

    assert "Visible" in text
    assert "complete" in text