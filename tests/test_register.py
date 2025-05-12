import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user_success(monkeypatch):
    # Mock DB and dependencies if needed
    payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    }
    response = client.post("/api/v1/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert "id" in data


def test_register_user_duplicate(monkeypatch):
    payload = {
        "username": "testuserdup",
        "email": "testuserdup@example.com",
        "password": "testpassword"
    }
    # First registration should succeed
    response1 = client.post("/api/v1/register", json=payload)
    assert response1.status_code == 201
    # Second registration with same username should fail
    response2 = client.post("/api/v1/register", json=payload)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Username already registered"
