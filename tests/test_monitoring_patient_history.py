import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid
from app.db.session import SessionLocal
from app.models.medical import Patient, User, Record
from datetime import date, datetime

client = TestClient(app)

def test_get_patient_monitoring_history():
    # Buat user pasien via endpoint
    email = f"historypat_{uuid.uuid4().hex[:8]}@example.com"
    reg_resp = client.post("/api/v1/register", json={
        "name": "HistoryPatient",
        "email": email,
        "password": "testpassword",
        "role": "patient"
    })
    user_id = reg_resp.json()["id"]
    db = SessionLocal()
    # Pastikan Patient record ada
    patient = db.query(Patient).filter(Patient.patient_id == user_id).first()
    if not patient:
        patient = Patient(patient_id=user_id, birth_date=date(2000,1,1), address="Test Address", medical_note="Test note")
        db.add(patient)
        db.commit()
        db.refresh(patient)
    # Tambah record monitoring
    record = Record(
        patient_id=patient.id,
        doctor_id=None,
        source="self",
        bpm_data=[{"time": 0, "bpm": 120}, {"time": 1, "bpm": 122}],
        classification="Tidak terdeteksi kelainan",
        notes="Normal",
        start_time=datetime(2025, 5, 22, 20, 0, 0)
    )
    db.add(record)
    db.commit()
    db.close()
    # Login
    login_resp = client.post("/api/v1/login", json={"email": email, "password": "testpassword"})
    token = login_resp.json()["access_token"]
    # Hit endpoint
    resp = client.get("/api/v1/patient/monitoring/history", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(item["monitoring_result"] == "Normal" for item in data)
    assert any(item["classification"] == "Tidak terdeteksi kelainan" for item in data)
    assert any(isinstance(item["bpm_data"], list) for item in data)
