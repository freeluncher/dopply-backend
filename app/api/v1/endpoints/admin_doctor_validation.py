from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.medical import Doctor, User
from app.core.security import verify_jwt_token

router = APIRouter()
security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = verify_jwt_token(token)
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user or user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.get("/doctor/validation-requests/count")
def count_doctor_validation_requests(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    count = db.query(Doctor).filter(Doctor.is_valid == False).count()
    return {"pending_validation": count}

@router.get("/doctor/validation-requests")
def list_doctor_validation_requests(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    doctors = db.query(Doctor).filter(Doctor.is_valid == False).all()
    result = []
    for doctor in doctors:
        user = db.query(User).filter(User.id == doctor.user_id).first()
        result.append({
            "doctor_id": doctor.id,
            "user_id": doctor.user_id,
            "name": user.name if user else None,
            "email": user.email if user else None
        })
    return result

@router.post("/doctor/validate/{doctor_id}")
def validate_doctor(doctor_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctor.is_valid = True
    db.commit()
    return {"message": "Doctor validated successfully"}

@router.get("/token/verify")
def verify_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    payload = verify_jwt_token(token)
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token or user not found")
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.value
    }
