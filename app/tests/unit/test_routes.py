import pytest
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.task_model import Task


def task_count():
    return db.session.query(Task).count()


# ---------- list page and static pages ----------


def test_index_loads_with_no_tasks(client):
    assert client.get("/").status_code == 200


def test_index_loads_with_tasks(client, make_task):
    make_task("First")
    make_task("Second")
    assert client.get("/").status_code == 200


def test_hello_page(client):
    response = client.get("/hello")
    assert response.status_code == 200
    assert b"TasketCasket" in response.data


# ---------- create ----------


def test_new_task_form_loads(client):
    assert client.get("/tasks/new").status_code == 200


def test_create_task_saves_and_redirects_to_list(client):
    response = client.post(
        "/tasks/new", data={"title": "Buy milk", "description": "Semi-skimmed"}
    )

    assert response.status_code == 302
    assert response.location == "/"
    task = db.session.query(Task).one()
    assert task.title == "Buy milk"
    assert task.description == "Semi-skimmed"
    assert task.status == "pending"


def test_create_task_trims_whitespace(client):
    client.post("/tasks/new", data={"title": "  Padded  ", "description": "  note  "})

    task = db.session.query(Task).one()
    assert task.title == "Padded"
    assert task.description == "note"


@pytest.mark.parametrize("title", ["", "   "])
def test_create_task_rejects_blank_title(client, title):
    response = client.post("/tasks/new", data={"title": title})

    assert response.status_code == 400
    assert task_count() == 0


def test_create_task_rejects_missing_title(client):
    response = client.post("/tasks/new", data={})

    assert response.status_code == 400
    assert task_count() == 0


# ---------- status ----------


@pytest.mark.parametrize("status", ["pending", "in_progress", "complete"])
def test_set_status_updates_task(client, make_task, status):
    task = make_task(status="pending" if status != "pending" else "complete")

    response = client.post(f"/tasks/{task.id}/status", data={"status": status})

    assert response.status_code == 302
    assert response.location == "/"
    assert db.session.get(Task, task.id).status == status


def test_set_status_rejects_invalid_status(client, make_task):
    task = make_task()

    response = client.post(f"/tasks/{task.id}/status", data={"status": "finished"})

    assert response.status_code == 400
    assert db.session.get(Task, task.id).status == "pending"


def test_set_status_rejects_missing_status(client, make_task):
    task = make_task()

    assert client.post(f"/tasks/{task.id}/status", data={}).status_code == 400


def test_set_status_unknown_task_is_404(client):
    response = client.post("/tasks/999/status", data={"status": "complete"})

    assert response.status_code == 404


# ---------- edit ----------


def test_edit_form_loads(client, make_task):
    task = make_task()

    assert client.get(f"/tasks/{task.id}/edit").status_code == 200


def test_edit_task_updates_all_fields(client, make_task):
    task = make_task("Old title", "Old description", "pending")

    response = client.post(
        f"/tasks/{task.id}/edit",
        data={
            "title": "New title",
            "description": "New description",
            "status": "in_progress",
        },
    )

    assert response.status_code == 302
    assert response.location == "/"
    updated = db.session.get(Task, task.id)
    assert updated.title == "New title"
    assert updated.description == "New description"
    assert updated.status == "in_progress"


def test_edit_task_rejects_blank_title(client, make_task):
    task = make_task("Keep me")

    response = client.post(
        f"/tasks/{task.id}/edit", data={"title": "  ", "status": "pending"}
    )

    assert response.status_code == 400
    assert db.session.get(Task, task.id).title == "Keep me"


def test_edit_task_rejects_invalid_status(client, make_task):
    task = make_task()

    response = client.post(
        f"/tasks/{task.id}/edit", data={"title": "Fine", "status": "nonsense"}
    )

    assert response.status_code == 400
    assert db.session.get(Task, task.id).status == "pending"


def test_edit_unknown_task_is_404(client):
    assert client.get("/tasks/999/edit").status_code == 404
    response = client.post("/tasks/999/edit", data={"title": "x", "status": "pending"})
    assert response.status_code == 404


# ---------- delete ----------


def test_delete_task_removes_it(client, make_task):
    task = make_task()

    response = client.post(f"/tasks/{task.id}/delete")

    assert response.status_code == 302
    assert response.location == "/"
    assert db.session.get(Task, task.id) is None


def test_delete_only_removes_the_chosen_task(client, make_task):
    keep = make_task("Keep")
    remove = make_task("Remove")

    client.post(f"/tasks/{remove.id}/delete")

    assert db.session.get(Task, keep.id) is not None
    assert task_count() == 1


def test_delete_unknown_task_is_404(client):
    assert client.post("/tasks/999/delete").status_code == 404


def test_delete_rejects_get_requests(client, make_task):
    task = make_task()

    assert client.get(f"/tasks/{task.id}/delete").status_code == 405
    assert db.session.get(Task, task.id) is not None


# ---------- health endpoint ----------


def test_health_reports_ok_when_database_is_connected(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "database": "connected",
        "version": "dev",
        "environment": "local",
    }


def test_health_reports_configured_version_and_environment(app, client):
    app.config["APP_VERSION"] = "abc1234"
    app.config["APP_ENV"] = "staging"

    data = client.get("/health").get_json()

    assert data["version"] == "abc1234"
    assert data["environment"] == "staging"


def test_health_returns_503_when_database_is_unreachable(client, monkeypatch):
    def broken_execute(*args, **kwargs):
        raise SQLAlchemyError("database down")

    monkeypatch.setattr(db.session, "execute", broken_execute)

    response = client.get("/health")

    assert response.status_code == 503
    data = response.get_json()
    assert data["status"] == "degraded"
    assert data["database"] == "unreachable"