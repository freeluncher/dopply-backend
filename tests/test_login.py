import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.medical import User
from app.core.security import get_password_hash

client = TestClient(app)

def setup_module(module):
    # Setup test database and create a test user
    db = SessionLocal()
    # Delete dependent patients row(s) first
    from app.models.medical import Patient
    user_obj = db.query(User).filter(User.email == "testuser@example.com").first()
    if user_obj:
        db.query(Patient).filter(Patient.patient_id == user_obj.id).delete()
        db.commit()
        db.delete(user_obj)
        db.commit()
    hashed_password = get_password_hash("testpassword")
    test_user = User(
        name="testuser",
        email="testuser@example.com",
        password_hash=hashed_password,
        role="patient"
    )
    db.add(test_user)
    db.commit()
    db.close()

def teardown_module(module):
    # Cleanup test database
    db = SessionLocal()
    from app.models.medical import Patient
    user_obj = db.query(User).filter(User.email == "testuser@example.com").first()
    if user_obj:
        db.query(Patient).filter(Patient.patient_id == user_obj.id).delete()
        db.commit()
        db.delete(user_obj)
        db.commit()
    db.close()

def test_login_success():
    response = client.post(
        "/api/v1/login",
        json={"email": "testuser@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_email():
    response = client.post(
        "/api/v1/login",
        json={"email": "invaliduser@example.com", "password": "testpassword"}
    )
    assert response.status_code == 400
    assert response.json()["message"] == "Invalid credentials"

def test_login_invalid_password():
    response = client.post(
        "/api/v1/login",
        json={"email": "testuser@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert response.json()["message"] == "Invalid credentials"
