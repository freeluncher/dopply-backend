from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.medical import Record, Patient, User
from app.core.security import verify_jwt_token
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
    payload = verify_jwt_token(token)
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
    # Ambil semua patient_id dari records yang pernah ditangani dokter ini
    patient_ids = db.query(Record.patient_id).filter(Record.doctor_id == doctor_id).distinct().all()
    patient_ids = [pid[0] for pid in patient_ids]
    if not patient_ids:
        return []
    # Query pasien
    query = db.query(Patient).filter(Patient.id.in_(patient_ids))
    if search:
        query = query.join(User, Patient.patient_id == User.id).filter(User.name.ilike(f"%{search}%"))
    patients = query.all()
    result = []
    for patient in patients:
        user = db.query(User).filter(User.id == patient.patient_id).first()
        result.append({
            "patient_id": patient.id,
            "name": user.name if user else None,
            "email": user.email if user else None,
            "address": patient.address,
            "birth_date": patient.birth_date,
            "medical_note": patient.medical_note
        })
    return result
