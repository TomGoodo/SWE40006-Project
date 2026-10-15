import pytest

from app import create_app, db


def test_health():
    client = create_app().test_client()
    response = client.get("/health")

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert "version" in data
    assert "environment" in data


def test_index():
    client = create_app().test_client()
    assert client.get("/").status_code == 200


def test_db_check(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    client = create_app().test_client()
    first = client.get("/db-check").get_json()
    second = client.get("/db-check").get_json()
    assert first["status"] == "ok"
    assert first["database"] == "sqlite"
    assert second["checks"] == first["checks"] + 1

@pytest.fixture
def client():
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
