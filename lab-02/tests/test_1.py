import pytest
import app as app_module
from app import app

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "COUNTER_FILE", tmp_path / "visits.txt")
    monkeypatch.setattr(app_module, "DATABASE_URL", None)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.data == b"ok\n"

def test_ready_ok(client):
    response = client.get('/ready')
    assert response.status_code == 200
    assert response.get_json()["ready"] is True

def test_ready_broken(client, monkeypatch):
    monkeypatch.setattr(app_module, "DATABASE_URL", "postgresql://broken:5432/db")
    response = client.get('/ready')
    assert response.status_code == 503
    assert response.get_json()["ready"] is False

def test_visits(client):
    first = client.get('/visits')
    second = client.get('/visits')
    assert second.get_json()["visits"] == first.get_json()["visits"]+1
