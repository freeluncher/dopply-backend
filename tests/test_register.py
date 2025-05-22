import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_register_user_success(monkeypatch):
    # Mock DB and dependencies if needed
    payload = {
        "name": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
        "role": "patient"
    }
    response = client.post("/api/v1/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]
    assert "id" in data
    assert data["role"] == payload["role"]


def test_register_user_duplicate(monkeypatch):
    unique_email = f"testuserdup_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "name": "testuserdup",
        "email": unique_email,
        "password": "testpassword",
        "role": "patient"
    }
    # First registration should succeed
    response1 = client.post("/api/v1/register", json=payload)
    assert response1.status_code == 201
    # Second registration with same email should fail
    response2 = client.post("/api/v1/register", json=payload)
    assert response2.status_code == 400
    assert response2.json()["message"].startswith("Email already registered")
