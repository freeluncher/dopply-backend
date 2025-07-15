from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.schemas.user import UserRegister, UserOut, LoginRequest
from app.schemas.refresh import LoginResponse
from app.models.medical import User, Patient
from app.db.session import SessionLocal
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, verify_jwt_token
from datetime import timedelta

router = APIRouter(tags=["Authentication"])
security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = verify_jwt_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Debug logging
    print(f"[DEBUG] JWT payload: {payload}")
    
    # Robust: support both 'sub' and fallback to 'email' if needed
    user_email = payload.get("sub") or payload.get("email")
    if not user_email:
        raise HTTPException(status_code=401, detail="Token missing user email (sub/email)")
    
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Handle enum vs string role comparison properly
    user_role = user.role.value if hasattr(user.role, 'value') else str(user.role)
    
    # For doctors, add additional fields from JWT payload
    if user_role == "doctor":
        # Add doctor-specific fields from JWT payload
        if "doctor_id" in payload:
            user.doctor_id = payload["doctor_id"]
        if "is_valid" in payload:
            user.is_valid = payload["is_valid"]
    
    print(f"[DEBUG] User from DB: id={user.id}, role={user.role} ({user_role}), doctor_id={getattr(user, 'doctor_id', None)}, is_valid={getattr(user, 'is_valid', None)}")
    
    return user

@router.post("/login",
             summary="Login User",
             description="Authenticate user dan dapatkan JWT access token.")
def login_user(user: LoginRequest, db: Session = Depends(get_db)):
    # Validate user credentials
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    role_value = db_user.role.value if hasattr(db_user.role, 'value') else str(db_user.role)
    
    # Build JWT payload
    jwt_payload = {
        "sub": db_user.email,
        "id": db_user.id,
        "email": db_user.email,
        "role": role_value,
        "name": db_user.name,
    }

    if hasattr(db_user, "photo_url") and db_user.photo_url:
        jwt_payload["photo_url"] = db_user.photo_url

    # Add doctor-specific data
    is_valid = None
    if role_value == "doctor":
        is_valid = db_user.is_verified if db_user.is_verified is not None else False
        jwt_payload["is_valid"] = is_valid
        jwt_payload["doctor_id"] = db_user.id

    # Add gestationalAge for patient
    if role_value == "patient":
        patient = db.query(Patient).filter(Patient.user_id == db_user.id).first()
        if patient and hasattr(patient, "gestational_age"):
            jwt_payload["gestationalAge"] = patient.gestational_age

    # Create both tokens
    access_token = create_access_token(jwt_payload)
    refresh_token = create_refresh_token(jwt_payload)

    # Return response with both tokens
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        **jwt_payload
    }

@router.post("/register", status_code=201,
             summary="Register User", 
             description="Register user baru sebagai patient, doctor atau admin.")
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise Exception("Email sudah digunakan")
        
        # Create new user
        created_user = User(
            email=user.email,
            password=get_password_hash(user.password),
            name=user.name,
            role=user.role
        )
        db.add(created_user)
        db.commit()
        db.refresh(created_user)
        
        # Create related records based on role
        if user.role == "patient":
            patient = Patient(
                user_id=created_user.id,
                name=user.name,  # Denormalized
                email=user.email,  # Denormalized
                birth_date=getattr(user, 'birth_date', None),
                address=getattr(user, 'address', None),
                medical_note=getattr(user, 'medical_note', None)
            )
            db.add(patient)
            
        elif user.role == "doctor":
            # Set doctor-specific fields in User table
            created_user.specialization = getattr(user, 'specialization', None)
            created_user.is_verified = False  # Default not validated
            
        db.commit()
        role_value = created_user.role.value if hasattr(created_user.role, 'value') else str(created_user.role)
        jwt_payload = {
            "sub": created_user.email,  # Always include 'sub' for compatibility
            "id": created_user.id,
            "email": created_user.email,
            "role": role_value,
            "name": created_user.name,
        }
        if hasattr(created_user, "photo_url") and created_user.photo_url:
            jwt_payload["photo_url"] = created_user.photo_url
        if role_value == "doctor":
            jwt_payload["is_valid"] = created_user.is_verified
            jwt_payload["doctor_id"] = created_user.id
        # Optionally add patient info to response, but not to JWT
        patient_info = {}
        if role_value == "patient":
            patient = db.query(Patient).filter(Patient.user_id == created_user.id).first()
            patient_info = {
                "birth_date": getattr(patient, "birth_date", None),
                "address": getattr(patient, "address", None),
                "medical_note": getattr(patient, "medical_note", None),
            }
        access_token = create_access_token(jwt_payload)
        response_content = {
            "access_token": access_token,
            **jwt_payload,
            **patient_info
        }
        return JSONResponse(status_code=201, content=response_content)
    except Exception as e:
        error_message = str(e)
        if "Email sudah digunakan" in error_message:
            raise HTTPException(status_code=400, detail="Email already registered. Please use a different email or activate your account if pre-registered.")
        raise HTTPException(status_code=400, detail=error_message)
