from app import create_app


def test_health():
    client = create_app().test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


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
