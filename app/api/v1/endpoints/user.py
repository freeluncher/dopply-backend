from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import JSONResponse
from app.schemas.user import UserRegister, UserOut, LoginRequest
from app.models.medical import User, Patient, Doctor, Record
from app.db.session import SessionLocal
from app.core.security import verify_password, get_password_hash, create_access_token, verify_jwt_token
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
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/login")
def login_user(user: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    is_valid = None
    if db_user.role.value == "doctor":
        doctor = db.query(Doctor).filter(Doctor.doctor_id == db_user.id).first()
        is_valid = doctor.is_valid if doctor else False
    access_token = create_access_token(data={"sub": db_user.email}, expires_delta=timedelta(minutes=30))
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "role": db_user.role.value,
        "is_valid": is_valid
    }

@router.post("/register", status_code=201)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    try:
        created_user = register_user_universal(db, user)
        role_value = created_user.role.value if hasattr(created_user.role, 'value') else str(created_user.role)
        if role_value == "doctor":
            doctor = db.query(Doctor).filter(Doctor.doctor_id == created_user.id).first()
            return JSONResponse(status_code=201, content={
                "id": created_user.id,
                "name": created_user.name,
                "email": created_user.email,
                "role": role_value,
                "is_valid": getattr(doctor, "is_valid", False)
            })
        else:
            patient = db.query(Patient).filter(Patient.patient_id == created_user.id).first()
            return JSONResponse(status_code=201, content={
                "id": created_user.id,
                "name": created_user.name,
                "email": created_user.email,
                "role": role_value,
                "birth_date": getattr(patient, "birth_date", None),
                "address": getattr(patient, "address", None),
                "medical_note": getattr(patient, "medical_note", None)
            })
    except Exception as e:
        error_message = str(e)
        if "Email sudah digunakan" in error_message:
            raise HTTPException(status_code=400, detail="Email already registered. Please use a different email or activate your account if pre-registered.")
        raise HTTPException(status_code=400, detail=error_message)

@router.get("/records", response_model=list[RecordOut])
def get_records(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    records = get_all_records_for_user(db, current_user)
    return records
