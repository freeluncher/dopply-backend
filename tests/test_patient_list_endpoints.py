import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def get_doctor_token():
    email = f"doctor_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "name": "DoctorList",
        "email": email,
        "password": "testpassword",
        "role": "doctor"
    }
    client.post("/api/v1/register", json=payload)
    login_resp = client.post("/api/v1/login", json={"email": email, "password": "testpassword"})
    return login_resp.json()["access_token"], email

def test_get_patients_by_doctor_unauthorized():
    response = client.get("/api/v1/patients/by-doctor")
    assert response.status_code in (401, 403)

def test_get_patients_by_doctor_authorized():
    token, _ = get_doctor_token()
    response = client.get("/api/v1/patients/by-doctor", headers={"Authorization": f"Bearer {token}"})
    # Should return 200 and a list (may be empty if no patients assigned)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
