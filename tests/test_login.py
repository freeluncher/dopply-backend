import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

client = TestClient(app)

def setup_module(module):
    # Setup test database and create a test user
    db = SessionLocal()
    hashed_password = get_password_hash("testpassword")
    test_user = User(
        username="testuser",
        email="testuser@example.com",
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False
    )
    db.add(test_user)
    db.commit()
    db.close()

def teardown_module(module):
    # Cleanup test database
    db = SessionLocal()
    db.query(User).filter(User.username == "testuser").delete()
    db.commit()
    db.close()

def test_login_success():
    response = client.post(
        "/api/v1/login",
        json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_username():
    response = client.post(
        "/api/v1/login",
        json={"username": "invaliduser", "password": "admin123"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"

def test_login_invalid_password():
    response = client.post(
        "/api/v1/login",
        json={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"
