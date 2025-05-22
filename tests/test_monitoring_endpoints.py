import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid
from app.db.session import SessionLocal
from app.models.medical import Patient, User, Doctor, DoctorPatientAssociation
from datetime import date

client = TestClient(app)

def setup_patient_with_doctor():
    db = SessionLocal()
    # Create doctor user
    doctor_email = f"doctor_{uuid.uuid4().hex[:8]}@example.com"
    doctor_user = User(name="DoctorMonitor", email=doctor_email, password_hash="x", role="doctor")
    db.add(doctor_user)
    db.commit()
    db.refresh(doctor_user)
    doctor = Doctor(doctor_id=doctor_user.id, is_valid=True)
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    # Create patient user
    patient_email = f"monitor_{uuid.uuid4().hex[:8]}@example.com"
    patient_user = User(name="MonitorPatient", email=patient_email, password_hash="x", role="patient")
    db.add(patient_user)
    db.commit()
    db.refresh(patient_user)
    patient = Patient(patient_id=patient_user.id, birth_date=date(2000,1,1), address="Test Address", medical_note="Test note")
    db.add(patient)
    db.commit()
    db.refresh(patient)
    # Assign patient to doctor (use doctor.doctor_id, not doctor.id)
    assoc = DoctorPatientAssociation(doctor_id=doctor.doctor_id, patient_id=patient.patient_id)
    db.add(assoc)
    db.commit()
    patient_id = patient.id  # Use Patient.id (PK)
    db.close()
    return patient_id

def test_send_monitoring_result_success():
    patient_id = setup_patient_with_doctor()
    payload = {
        "patient_id": patient_id,
        "bpm_data": [80, 82, 78, 81],
        "doctor_note": "Routine check"
    }
    response = client.post("/api/v1/monitoring", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["patient_id"] == patient_id
    assert "bpm_data" in data
    assert "classification" in data

def test_send_monitoring_result_not_found():
    payload = {
        "patient_id": 999999,
        "bpm_data": [80, 82, 78, 81],
        "doctor_note": "Routine check"
    }
    response = client.post("/api/v1/monitoring", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["message"].lower()
