from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.medical import User, Patient
from app.db.session import get_db
from app.core.security import verify_jwt_token
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/patient", tags=["Patient"])
security = HTTPBearer()

class PatientUpdateRequest(BaseModel):
    user_id: int
    name: Optional[str] = None
    email: Optional[str] = None
    hpht: Optional[datetime] = None
    birth_date: Optional[datetime] = None
    address: Optional[str] = None
    medical_note: Optional[str] = None

@router.put("/{id}", summary="Update biodata pasien")
def update_patient_biodata(
    id: int,
    req: PatientUpdateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    # Verifikasi JWT dan role
    payload = verify_jwt_token(credentials.credentials)
    if payload.get("role") != "patient":
        raise HTTPException(status_code=403, detail="Hanya pasien yang dapat mengupdate biodata")
    if payload.get("id") != req.user_id:
        raise HTTPException(status_code=403, detail="Tidak boleh mengupdate data pasien lain")
    # Ambil user dan patient
    user = db.query(User).filter(User.id == req.user_id).first()
    patient = db.query(Patient).filter(Patient.id == id, Patient.user_id == req.user_id).first()
    if not user or not patient:
        raise HTTPException(status_code=404, detail="Data pasien tidak ditemukan")
    # Update data
    if req.name:
        user.name = req.name
        patient.name = req.name
    if req.email:
        user.email = req.email
        patient.email = req.email
    if req.hpht:
        patient.hpht = req.hpht
    if req.birth_date:
        patient.birth_date = req.birth_date
    if req.address:
        patient.address = req.address
    if req.medical_note:
        patient.medical_note = req.medical_note
    db.commit()
    db.refresh(patient)
    db.refresh(user)
    return {
        "status": "success",
        "patient": {
            "id": patient.id,
            "user_id": patient.user_id,
            "name": patient.name,
            "email": patient.email,
            "hpht": patient.hpht,
            "birth_date": patient.birth_date,
            "address": patient.address,
            "medical_note": patient.medical_note
        }
    }
