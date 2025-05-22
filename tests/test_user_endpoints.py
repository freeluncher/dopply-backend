import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_register_and_login():
    # Register a new user
    unique_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "name": "IntegrationTestUser",
        "email": unique_email,
        "password": "testpassword",
        "role": "patient"
    }
    response = client.post("/api/v1/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == unique_email
    # Login with the new user
    login_payload = {"email": unique_email, "password": "testpassword"}
    response = client.post("/api/v1/login", json=login_payload)
    assert response.status_code == 200
    login_data = response.json()
    assert "access_token" in login_data
    assert login_data["email"] == unique_email
    assert login_data["role"] == "patient"

def test_login_invalid_credentials():
    response = client.post("/api/v1/login", json={"email": "notfound@example.com", "password": "wrong"})
    assert response.status_code == 400
    assert response.json()["message"] == "Invalid credentials"
