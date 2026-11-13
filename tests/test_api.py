"""Automated API regression tests, triggered on every pull request."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test_tickets.db"))
    with TestClient(app) as api:
        yield api


def test_health(client):
    result = client.get("/health")
    assert result.status_code == 200
    assert result.json()["status"] == "ok"


def test_create_and_retrieve_ticket(client):
    result = client.post(
        "/tickets", json={"text": "I was charged twice for my membership, urgent"}
    )
    assert result.status_code == 201
    ticket = result.json()
    assert ticket["category"] in {"billing", "login", "technical"}
    assert ticket["priority"] == "high"
    assert isinstance(ticket["confidence"], float)

    stored = client.get(f"/tickets/{ticket['ticket_id']}")
    assert stored.status_code == 200
    assert stored.json()["id"] == ticket["ticket_id"]
    assert client.get("/metrics").json()["tickets_total"] == 1


def test_input_validation(client):
    assert client.post("/tickets", json={"text": "short"}).status_code == 422


def test_missing_ticket(client):
    assert client.get("/tickets/99999").status_code == 404
