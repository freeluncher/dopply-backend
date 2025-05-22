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

def test_create_patient():
    email = f"newpatient_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "name": "New Patient",
        "email": email,
        "password": "testpassword",
        "birth_date": "2000-01-01",
        "address": "Test Address",
        "medical_note": "Test note"
    }
    response = client.post("/api/v1/patients", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]
    assert data["birth_date"] == payload["birth_date"]
    assert data["address"] == payload["address"]
    assert data["medical_note"] == payload["medical_note"]


def test_assign_patient_to_doctor_body():
    # Create doctor
    doctor_email = f"doctor_{uuid.uuid4().hex[:8]}@example.com"
    doctor_payload = {
        "name": "DoctorAssign",
        "email": doctor_email,
        "password": "testpassword",
        "role": "doctor"
    }
    reg_resp = client.post("/api/v1/register", json=doctor_payload)
    doctor_id = reg_resp.json()["id"]
    # Create patient
    patient_email = f"assignbody_{uuid.uuid4().hex[:8]}@example.com"
    patient_payload = {
        "name": "AssignBodyPatient",
        "email": patient_email,
        "password": "testpassword",
        "birth_date": "2000-01-01",
        "address": "Test Address",
        "medical_note": "Test note"
    }
    patient_resp = client.post("/api/v1/patients", json=patient_payload)
    patient_id = patient_resp.json()["id"]
    # Assign via body
    assign_payload = {"patient_id": patient_id, "status": "active", "note": "Test assign"}
    assign_resp = client.post(f"/api/v1/doctors/{doctor_id}/assign-patient", json=assign_payload)
    assert assign_resp.status_code == 200
    data = assign_resp.json()
    assert data["doctor_id"] == doctor_id
    assert data["patient_id"] == patient_id
    assert data["status"] == "active"
    assert data["note"] == "Test assign"
