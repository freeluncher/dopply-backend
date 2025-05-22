import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid
from app.db.session import SessionLocal
from app.models.medical import Patient, User
from datetime import date

client = TestClient(app)

def test_save_patient_monitoring_result():
    # Buat user pasien
    email = f"monitoringpat_{uuid.uuid4().hex[:8]}@example.com"
    user = User(name="PatientMonitor", email=email, password_hash="x", role="patient")
    db = SessionLocal()
    db.add(user)
    db.commit()
    db.refresh(user)
    patient = Patient(patient_id=user.id, birth_date=date(2000,1,1), address="Test Address", medical_note="Test note")
    db.add(patient)
    db.commit()
    db.refresh(patient)
    patient_id = patient.id
    db.close()
    # Kirim monitoring
    payload = {
        "patient_id": patient_id,
        "bpm_data": [
            {"time": 1, "bpm": 80},
            {"time": 2, "bpm": 82}
        ],
        "classification": "normal",
        "monitoring_result": "Feeling good"
    }
    response = client.post("/api/v1/patient/monitoring", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "record_id" in data
    assert data["message"] == "Monitoring result saved"
