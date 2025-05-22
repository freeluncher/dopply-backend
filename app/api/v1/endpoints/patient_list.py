from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.medical import Record, Patient, User
from app.core.security import verify_jwt_token
from app.services.patient_list_service import PatientListService
from typing import List, Optional

router = APIRouter()
security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_doctor_id(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = verify_jwt_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user or user.role.value != "doctor":
        raise HTTPException(status_code=403, detail="Doctor access required")
    return user.id

@router.get("/patients/by-doctor", response_model=List[dict])
def get_patients_by_doctor(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    doctor_id: int = Depends(get_current_doctor_id)
):
    return PatientListService.get_patients_by_doctor(db, doctor_id, search)
