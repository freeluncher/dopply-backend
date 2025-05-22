import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_token_verify_success():
    # Register and login to get a token
    unique_email = f"verify_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "name": "VerifyUser",
        "email": unique_email,
        "password": "testpassword",
        "role": "patient"
    }
    client.post("/api/v1/register", json=payload)
    login_resp = client.post("/api/v1/login", json={"email": unique_email, "password": "testpassword"})
    token = login_resp.json()["access_token"]
    # Verify token
    response = client.get("/api/v1/token/verify", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == unique_email
    assert data["role"] == "patient"

def test_token_verify_invalid():
    response = client.get("/api/v1/token/verify", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code in (400, 401)
    # Accept either JSON error or exception message
    try:
        msg = response.json().get("message", "")
        assert "Invalid token" in msg or "not found" in msg
    except Exception as e:
        assert "Invalid token" in str(e) or "not found" in str(e)
