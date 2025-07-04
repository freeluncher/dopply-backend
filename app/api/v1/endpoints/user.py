from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
import os
import shutil
from datetime import date
from typing import Optional
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import JSONResponse
from app.schemas.user import UserRegister, UserOut, LoginRequest
from app.schemas.refresh import LoginResponse
from app.models.medical import User, Patient, Doctor, Record, DoctorPatientAssociation
from app.db.session import SessionLocal
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, verify_jwt_token
from datetime import timedelta
from app.schemas.record import RecordOut
from app.services.record_service import get_all_records_for_user
from app.services.patient_service import register_user_universal

router = APIRouter()
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

@router.post("/login", tags=["Authentication"],
             summary="🔑 User Login",
             description="Authenticate user credentials and receive JWT access token + refresh token. Access token expires in 30 minutes, refresh token in 7 days.",
             responses={
                 200: {
                     "description": "Successful authentication with tokens",
                     "content": {
                         "application/json": {
                             "examples": {
                                 "patient_login": {
                                     "summary": "Patient Login Response",
                                     "value": {
                                         "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                                         "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                                         "token_type": "bearer",
                                         "id": 1,
                                         "email": "patient@example.com",
                                         "role": "patient",
                                         "name": "John Doe",
                                         "photo_url": "/static/user_photos/user_1.jpg"
                                     }
                                 },
                                 "doctor_login": {
                                     "summary": "Doctor Login Response",
                                     "value": {
                                         "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                                         "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                                         "token_type": "bearer",
                                         "id": 2,
                                         "email": "doctor@example.com",
                                         "role": "doctor",
                                         "name": "Dr. Sarah Johnson",
                                         "photo_url": "/static/user_photos/user_2.jpg",
                                         "is_valid": True,
                                         "doctor_id": 2
                                     }
                                 }
                             }
                         }
                     }
                 },
                 400: {
                     "description": "Invalid credentials",
                     "content": {
                         "application/json": {
                             "example": {
                                 "status": "error",
                                 "code": 400,
                                 "error_code": "bad_request",
                                 "message": "Invalid credentials",
                                 "error_type": "HTTPException"
                             }
                         }
                     }
                 }
             })
def login_user(user: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user with email and password.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns access token (30 min expiry) and refresh token (7 days expiry).
    """
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
    doctor_id = None
    if role_value == "doctor":
        doctor = db.query(Doctor).filter(Doctor.doctor_id == db_user.id).first()
        is_valid = doctor.is_valid if doctor else False
        jwt_payload["is_valid"] = is_valid
        doctor_id = doctor.doctor_id if doctor else db_user.id
        if doctor_id:
            jwt_payload["doctor_id"] = doctor_id
    
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

@router.post("/register", status_code=201, tags=["Authentication"],
             summary="📝 User Registration", 
             description="Register new user account (patient or doctor). Doctors require admin validation before full access.",
             responses={
                 201: {
                     "description": "User successfully registered",
                     "content": {
                         "application/json": {
                             "examples": {
                                 "patient_register": {
                                     "summary": "Patient Registration Response",
                                     "value": {
                                         "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                                         "id": 1,
                                         "email": "newpatient@example.com",
                                         "role": "patient",
                                         "name": "Alice Smith",
                                         "photo_url": None,
                                         "birth_date": "1990-05-15",
                                         "address": "Jakarta",
                                         "medical_note": "No known allergies"
                                     }
                                 },
                                 "doctor_register": {
                                     "summary": "Doctor Registration Response",
                                     "value": {
                                         "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                                         "id": 2,
                                         "email": "newdoctor@example.com",
                                         "role": "doctor",
                                         "name": "Dr. Michael Chen",
                                         "photo_url": None,
                                         "is_valid": False
                                     }
                                 }
                             }
                         }
                     }
                 },
                 400: {
                     "description": "Registration failed - validation error",
                     "content": {
                         "application/json": {
                             "example": {
                                 "status": "error",
                                 "code": 400,
                                 "error_code": "bad_request",
                                 "message": "Email already registered",
                                 "error_type": "HTTPException"
                             }
                         }
                     }
                 }
             })
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    try:
        created_user = register_user_universal(db, user)
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
            doctor = db.query(Doctor).filter(Doctor.doctor_id == created_user.id).first()
            jwt_payload["is_valid"] = getattr(doctor, "is_valid", False)
            if doctor:
                jwt_payload["doctor_id"] = doctor.doctor_id
        # Optionally add patient info to response, but not to JWT
        patient_info = {}
        if role_value == "patient":
            patient = db.query(Patient).filter(Patient.patient_id == created_user.id).first()
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

@router.get("/records", response_model=list[RecordOut], tags=["Medical Records"])
def get_records(
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    doctor_id: Optional[int] = Query(None, description="Filter by doctor ID"),
    date_from: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    classification: Optional[str] = Query(None, description="Filter by classification"),
    source: Optional[str] = Query(None, description="Filter by source"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get medical records with filtering options"""
    
    # Handle enum vs string role comparison
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    
    # Base query - users can only see records they have access to
    if user_role == "patient":
        # Patients can only see their own records
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient:
            return []
        query = db.query(Record).filter(Record.patient_id == patient.id)
    elif user_role == "doctor":
        # Doctors can see records of patients assigned to them
        query = db.query(Record).join(Patient).join(
            DoctorPatientAssociation,
            and_(
                DoctorPatientAssociation.patient_id == Patient.id,
                DoctorPatientAssociation.doctor_id == current_user.id
            )
        )
    elif user_role == "admin":
        # Admins can see all records
        query = db.query(Record)
    else:
        return []
    
    # Apply filters
    if patient_id is not None:
        if user_role == "patient":
            # Patients can only filter by their own patient_id
            patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
            if not patient or patient.id != patient_id:
                return []
        query = query.filter(Record.patient_id == patient_id)
    
    if doctor_id is not None:
        query = query.filter(Record.doctor_id == doctor_id)
    
    if date_from is not None:
        query = query.filter(func.date(Record.start_time) >= date_from)
    
    if date_to is not None:
        query = query.filter(func.date(Record.start_time) <= date_to)
    
    if classification is not None:
        query = query.filter(Record.classification == classification)
    
    if source is not None:
        query = query.filter(Record.source == source)
    
    # Execute query with patient relationship
    records = query.options(joinedload(Record.patient).joinedload(Patient.user)).order_by(Record.start_time.desc()).all()
    
    # Create response with patient names
    record_responses = []
    for record in records:
        record_dict = {
            "id": record.id,
            "patient_id": record.patient_id,
            "doctor_id": record.doctor_id,
            "source": record.source.value if hasattr(record.source, 'value') else record.source,
            "bpm_data": record.bpm_data,
            "start_time": record.start_time,
            "end_time": record.end_time,
            "classification": record.classification,
            "notes": record.notes,
            "shared_with": record.shared_with,
            "patient_name": record.patient.user.name if record.patient and record.patient.user else None
        }
        record_responses.append(record_dict)
    
    return record_responses
STATIC_USER_PHOTO_DIR = "app/static/user_photos"

@router.post("/user/photo", tags=["User Management"], summary="Upload user profile photo")
def upload_user_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only allow image files
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    # Create user-specific filename
    ext = os.path.splitext(file.filename)[1]
    filename = f"user_{current_user.id}{ext}"
    file_path = os.path.join(STATIC_USER_PHOTO_DIR, filename)

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update user photo_url in DB (URL path, not local path)
    photo_url = f"/static/user_photos/{filename}"
    current_user.photo_url = photo_url
    db.commit()
    db.refresh(current_user)

    # Generate JWT baru dengan data lengkap
    from app.core.security import create_access_token
    role_value = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    jwt_payload = {
        "sub": current_user.email,  # Always include 'sub' for compatibility
        "id": current_user.id,
        "email": current_user.email,
        "role": role_value,
        "name": current_user.name,
    }
    if current_user.photo_url:
        jwt_payload["photo_url"] = current_user.photo_url
    # If doctor, add is_valid and doctor_id
    if role_value == "doctor":
        doctor = db.query(Doctor).filter(Doctor.doctor_id == current_user.id).first()
        if doctor:
            jwt_payload["is_valid"] = doctor.is_valid
            jwt_payload["doctor_id"] = doctor.doctor_id
    access_token = create_access_token(jwt_payload)
    return {
        "status": "success",
        "photo_url": photo_url,
        "access_token": access_token
    }
