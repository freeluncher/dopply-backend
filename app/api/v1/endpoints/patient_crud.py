from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.patient import PatientCreate, PatientUpdate, PatientOut
from app.services.patient_service import get_patients, get_patient, update_patient, delete_patient
from app.db.session import SessionLocal
from app.models.medical import Doctor, Patient, User, DoctorPatientAssociation
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.services.doctor_patient_service import DoctorPatientService

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DoctorPatientAssociationIn(BaseModel):
    status: Optional[str] = None
    note: Optional[str] = None

class DoctorPatientAssociationOut(BaseModel):
    doctor_id: int
    patient_id: int
    assigned_at: datetime
    status: Optional[str] = None
    note: Optional[str] = None

    class Config:
        orm_mode = True

class AssignPatientByEmailIn(BaseModel):
    email: str
    status: Optional[str] = None
    note: Optional[str] = None

@router.get("/patients", response_model=List[PatientOut])
def read_patients(db: Session = Depends(get_db)):
    return get_patients(db)

@router.get("/patients/{patient_id}", response_model=PatientOut)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.put("/patients/{patient_id}", response_model=PatientOut)
def update_existing_patient(patient_id: int, patient: PatientUpdate, db: Session = Depends(get_db)):
    updated = update_patient(db, patient_id, patient)
    if not updated:
        raise HTTPException(status_code=404, detail="Patient not found")
    return updated

@router.delete("/patients/{patient_id}", status_code=204)
def delete_existing_patient(patient_id: int, db: Session = Depends(get_db)):
    success = delete_patient(db, patient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")
    return None

@router.post("/doctors/{doctor_id}/assign-patient/{patient_id}", response_model=DoctorPatientAssociationOut)
def assign_patient_to_doctor(
    doctor_id: int,
    patient_id: int,
    data: DoctorPatientAssociationIn = None,
    db: Session = Depends(get_db)
):
    try:
        assoc = DoctorPatientService.assign_patient_to_doctor(
            db, doctor_id, patient_id,
            status=data.status if data else None,
            note=data.note if data else None
        )
        return assoc
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=msg)
        if "already assigned" in msg:
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=400, detail=msg)

@router.post("/doctors/{doctor_id}/assign-patient-by-email", response_model=DoctorPatientAssociationOut)
def assign_patient_to_doctor_by_email(
    doctor_id: int,
    data: AssignPatientByEmailIn,
    db: Session = Depends(get_db)
):
    try:
        assoc = DoctorPatientService.assign_patient_to_doctor_by_email(
            db, doctor_id, data.email, status=data.status, note=data.note
        )
        return assoc
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=msg)
        if "already assigned" in msg:
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=400, detail=msg)

@router.patch("/doctors/{doctor_id}/patients/{patient_id}", response_model=DoctorPatientAssociationOut)
def update_doctor_patient_association(
    doctor_id: int,
    patient_id: int,
    data: DoctorPatientAssociationIn,
    db: Session = Depends(get_db)
):
    try:
        assoc = DoctorPatientService.update_doctor_patient_association(
            db, doctor_id, patient_id, status=data.status, note=data.note
        )
        return assoc
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)

@router.get("/doctors/{doctor_id}/patients", response_model=List[PatientOut])
def list_patients_for_doctor(doctor_id: int, db: Session = Depends(get_db)):
    return DoctorPatientService.list_patients_for_doctor(db, doctor_id)

@router.delete("/doctors/{doctor_id}/unassign-patient/{patient_id}")
def unassign_patient_from_doctor(doctor_id: int, patient_id: int, db: Session = Depends(get_db)):
    try:
        DoctorPatientService.unassign_patient_from_doctor(db, doctor_id, patient_id)
        return {"message": "Patient unassigned from doctor"}
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)
