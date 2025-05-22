import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid
from app.db.session import SessionLocal
from app.models.medical import User
from app.core.security import get_password_hash

client = TestClient(app)

def create_and_login_user(role="admin"):
    email = f"test_{role}_{uuid.uuid4().hex[:8]}@example.com"
    password = "testpassword"
    db = SessionLocal()
    user = User(name=f"Test {role.title()}", email=email, password_hash=get_password_hash(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    login_resp = client.post("/api/v1/login", json={"email": email, "password": password})
    token = login_resp.json()["access_token"]
    return token, email, password, user.id

def test_unified_change_email_success():
    token, old_email, password, _ = create_and_login_user(role="doctor")
    new_email = f"new_{old_email}"
    resp = client.put(
        "/api/v1/account/email",
        json={"newEmail": new_email},
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

def test_unified_change_email_duplicate():
    token1, email1, password1, _ = create_and_login_user(role="doctor")
    _, email2, _, _ = create_and_login_user(role="doctor")
    resp = client.put(
        "/api/v1/account/email",
        json={"newEmail": email2},
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert resp.status_code == 409
    # Accept both error formats (detail or error)
    err = resp.json().get("error") or resp.json().get("detail", {}).get("error")
    assert "already in use" in err

def test_unified_change_password_success():
    token, email, old_password, _ = create_and_login_user(role="admin")
    new_password = "newpass123"
    resp = client.put(
        "/api/v1/account/password",
        json={"oldPassword": old_password, "newPassword": new_password},
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

def test_unified_change_password_wrong_current():
    token, email, old_password, _ = create_and_login_user(role="admin")
    resp = client.put(
        "/api/v1/account/password",
        json={"oldPassword": "wrongpass", "newPassword": "whatever"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 400
    err = resp.json().get("error") or resp.json().get("detail", {}).get("error")
    assert "incorrect" in err

def test_admin_users_crud():
    # Create admin and login
    admin_token, _, _, _ = create_and_login_user(role="admin")
    # Create user
    user_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    resp = client.post(
        "/api/v1/users",
        json={"name": "User1", "email": user_email, "role": "doctor"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    user_id = resp.json()["id"]
    # Get users
    resp = client.get("/api/v1/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert any(u["email"] == user_email for u in resp.json())
    # Update user
    resp = client.put(
        f"/api/v1/users/{user_id}",
        json={"name": "User1 Updated", "email": user_email, "role": "doctor"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    # Delete user
    resp = client.delete(f"/api/v1/users/{user_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert "successfully" in resp.json()["message"]

def test_admin_users_crud_forbidden():
    # Create doctor and login
    doctor_token, _, _, _ = create_and_login_user(role="doctor")
    # Try to create user
    resp = client.post(
        "/api/v1/users",
        json={"name": "User2", "email": f"forbid_{uuid.uuid4().hex[:8]}@example.com", "role": "patient"},
        headers={"Authorization": f"Bearer {doctor_token}"}
    )
    assert resp.status_code == 403
    err = resp.json().get("error") or resp.json().get("detail", {}).get("error")
    assert "Admin access required" in err
    # Try to get users
    resp = client.get("/api/v1/users", headers={"Authorization": f"Bearer {doctor_token}"})
    assert resp.status_code == 403
    err = resp.json().get("error") or resp.json().get("detail", {}).get("error")
    assert "Admin access required" in err
