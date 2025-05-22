import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid
from app.db.session import SessionLocal
from app.models.medical import Patient, User
from datetime import date

client = TestClient(app)

def get_patient_token_and_id():
    email = f"patient_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "name": "PatientCRUD",
        "email": email,
        "password": "testpassword",
        "role": "patient"
    }
    reg_resp = client.post("/api/v1/register", json=payload)
    user_id = reg_resp.json()["id"]
    # Ensure Patient record exists with all required fields
    db = SessionLocal()
    if not db.query(Patient).filter(Patient.patient_id == user_id).first():
        db.add(Patient(patient_id=user_id, birth_date=date(2000,1,1), address="Test Address", medical_note="Test note"))
        db.commit()
    db.close()
    login_resp = client.post("/api/v1/login", json={"email": email, "password": "testpassword"})
    return login_resp.json()["access_token"], user_id

def test_read_patients():
    # Ensure at least one patient exists with all required fields
    _, _ = get_patient_token_and_id()
    response = client.get("/api/v1/patients")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_patient_not_found():
    response = client.get("/api/v1/patients/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["message"].lower()
