from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.medical import User, Patient
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.config import settings
from app.schemas.common import LoginRequest, LoginResponse, LoginData, PatientUserData, UserData

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse)
async def login_user(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login user with email and password"""
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value, "user_id": user.id}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    # Prepare user data
    user_data = {
        "id": user.id,
        "userId": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.value,
        "profilePhotoUrl": f"https://dopply.my.id{user.photo_url}" if user.photo_url else None
    }
    
    # Add patient-specific data if user is a patient
    if user.role.value == "patient":
        patient = db.query(Patient).filter(Patient.user_id == user.id).first()
        if patient:
            user_data.update({
                "hpht": patient.hpht.isoformat() if patient.hpht else None,
                "birthDate": patient.birth_date.isoformat() if patient.birth_date else None,
                "address": patient.address,
                "medicalNote": patient.medical_note
            })
    
    return LoginResponse(
        success=True,
        data={
            "token": access_token,
            "refreshToken": refresh_token,
            "user": user_data
        },
        message="Login successful"
    )