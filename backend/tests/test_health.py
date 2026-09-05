from fastapi.testclient import TestClient

from app.main import create_app


def test_health_returns_ok(tmp_path) -> None:
    with TestClient(create_app(tmp_path / "test.sqlite3")) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
