from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut, LoginRequest, UserRegister
from app.models.medical import User, Patient, Doctor
from app.db.session import SessionLocal
from app.core.security import verify_password, get_password_hash, create_access_token
from datetime import timedelta
from app.models.medical import Record
from app.schemas.record import RecordOut
from app.services.record_service import get_all_records, get_all_records_for_user
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.security import verify_jwt_token
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
    # Cek validasi dokter jika role doctor
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

@router.post("/register", response_model=UserOut, status_code=201)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    try:
        return register_user_universal(db, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/records", response_model=list[RecordOut])
def get_records(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    records = get_all_records_for_user(db, current_user)
    return records
