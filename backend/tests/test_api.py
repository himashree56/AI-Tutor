import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AI Tutor Backend"
    assert data["status"] == "running"


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_chat_without_query(client):
    response = client.post("/chat/", json={"query": "", "session_id": "test123"})
    assert response.status_code == 400


def test_get_history(client):
    response = client.get("/chat/history/test_session")
    assert response.status_code == 200
    data = response.json()
    assert "messages" in data


def test_clear_history(client):
    response = client.delete("/chat/history/test_session")
    assert response.status_code == 200


def test_quiz_without_topic_or_context(client):
    response = client.post("/generate-quiz/", json={})
    assert response.status_code == 400


def test_ingest_stats(client):
    response = client.get("/ingest/stats")
    assert response.status_code == 200


def test_ingest_reset(client):
    response = client.delete("/ingest/reset")
    assert response.status_code == 200
