import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid
from app.db.session import SessionLocal
from app.models.medical import Patient, User
from datetime import date

client = TestClient(app)

def create_and_login_patient():
    email = f"accpat_{uuid.uuid4().hex[:8]}@example.com"
    password = "testpassword"
    reg_resp = client.post("/api/v1/register", json={
        "name": "AccountPatient",
        "email": email,
        "password": password,
        "role": "patient"
    })
    user_id = reg_resp.json()["id"]
    db = SessionLocal()
    if not db.query(Patient).filter(Patient.patient_id == user_id).first():
        db.add(Patient(patient_id=user_id, birth_date=date(2000,1,1), address="Test Address", medical_note="Test note"))
        db.commit()
    db.close()
    login_resp = client.post("/api/v1/login", json={"email": email, "password": password})
    token = login_resp.json()["access_token"]
    return token, email, password, user_id

def test_change_patient_email_success():
    token, old_email, password, user_id = create_and_login_patient()
    new_email = f"new_{old_email}"
    resp = client.patch(
        "/api/v1/patient/account/email",
        json={"new_email": new_email, "current_password": password},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert "success" in resp.json()["message"]
    # Login with new email should work
    login_resp = client.post("/api/v1/login", json={"email": new_email, "password": password})
    assert login_resp.status_code == 200
    # Login with old email should fail
    login_resp = client.post("/api/v1/login", json={"email": old_email, "password": password})
    assert login_resp.status_code == 400

def test_change_patient_email_wrong_password():
    token, old_email, password, user_id = create_and_login_patient()
    new_email = f"fail_{old_email}"
    resp = client.patch(
        "/api/v1/patient/account/email",
        json={"new_email": new_email, "current_password": "wrongpass"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 400
    assert "incorrect" in resp.json()["message"]

def test_change_patient_email_duplicate():
    # Create two patients
    token1, email1, password1, _ = create_and_login_patient()
    _, email2, password2, _ = create_and_login_patient()
    # Try to change email1 to email2
    resp = client.patch(
        "/api/v1/patient/account/email",
        json={"new_email": email2, "current_password": password1},
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert resp.status_code == 400
    assert "already in use" in resp.json()["message"]

def test_change_patient_password_success():
    token, email, old_password, _ = create_and_login_patient()
    new_password = "newpass123"
    resp = client.patch(
        "/api/v1/patient/account/password",
        json={"current_password": old_password, "new_password": new_password},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert "success" in resp.json()["message"]
    # Login with new password should work
    login_resp = client.post("/api/v1/login", json={"email": email, "password": new_password})
    assert login_resp.status_code == 200
    # Login with old password should fail
    login_resp = client.post("/api/v1/login", json={"email": email, "password": old_password})
    assert login_resp.status_code == 400

def test_change_patient_password_wrong_current():
    token, email, old_password, _ = create_and_login_patient()
    resp = client.patch(
        "/api/v1/patient/account/password",
        json={"current_password": "wrongpass", "new_password": "whatever"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 400
    assert "incorrect" in resp.json()["message"]
