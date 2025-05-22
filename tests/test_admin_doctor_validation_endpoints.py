import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def get_admin_token():
    email = f"admin_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "name": "AdminUser",
        "email": email,
        "password": "testpassword",
        "role": "admin"
    }
    client.post("/api/v1/register", json=payload)
    login_resp = client.post("/api/v1/login", json={"email": email, "password": "testpassword"})
    return login_resp.json()["access_token"]

def test_count_doctor_validation_requests_unauthorized():
    response = client.get("/api/v1/admin/doctor/validation-requests/count")
    assert response.status_code in (401, 403)

def test_count_doctor_validation_requests_authorized():
    token = get_admin_token()
    response = client.get("/api/v1/admin/doctor/validation-requests/count", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "pending_validation" in response.json()

def test_list_doctor_validation_requests_authorized():
    token = get_admin_token()
    response = client.get("/api/v1/admin/doctor/validation-requests", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
