from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.patient import PatientCreate, PatientUpdate, PatientOut
from app.services.patient_service import get_patients, get_patient, update_patient, delete_patient
from app.db.session import SessionLocal
from app.models.medical import Doctor, Patient, User, DoctorPatientAssociation
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

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
    doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not doctor or not patient:
        raise HTTPException(status_code=404, detail="Doctor or patient not found")
    assoc = db.query(DoctorPatientAssociation).filter_by(doctor_id=doctor_id, patient_id=patient_id).first()
    if assoc:
        raise HTTPException(status_code=400, detail="Patient already assigned to doctor")
    assoc = DoctorPatientAssociation(
        doctor_id=doctor_id,
        patient_id=patient_id,
        assigned_at=datetime.utcnow(),
        status=data.status if data else None,
        note=data.note if data else None
    )
    db.add(assoc)
    db.commit()
    db.refresh(assoc)
    return assoc

@router.post("/doctors/{doctor_id}/assign-patient-by-email", response_model=DoctorPatientAssociationOut)
def assign_patient_to_doctor_by_email(
    doctor_id: int,
    data: AssignPatientByEmailIn,
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    patient = db.query(Patient).join(User).filter(User.email == data.email).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient with this email not found")
    assoc = db.query(DoctorPatientAssociation).filter_by(doctor_id=doctor_id, patient_id=patient.patient_id).first()
    if assoc:
        raise HTTPException(status_code=400, detail="Patient already assigned to doctor")
    assoc = DoctorPatientAssociation(
        doctor_id=doctor_id,
        patient_id=patient.patient_id,
        assigned_at=datetime.utcnow(),
        status=data.status,
        note=data.note
    )
    db.add(assoc)
    db.commit()
    db.refresh(assoc)
    return assoc

@router.patch("/doctors/{doctor_id}/patients/{patient_id}", response_model=DoctorPatientAssociationOut)
def update_doctor_patient_association(
    doctor_id: int,
    patient_id: int,
    data: DoctorPatientAssociationIn,
    db: Session = Depends(get_db)
):
    assoc = db.query(DoctorPatientAssociation).filter_by(doctor_id=doctor_id, patient_id=patient_id).first()
    if not assoc:
        raise HTTPException(status_code=404, detail="Relation not found")
    if data.status is not None:
        assoc.status = data.status
    if data.note is not None:
        assoc.note = data.note
    db.commit()
    db.refresh(assoc)
    return assoc

@router.get("/doctors/{doctor_id}/patients", response_model=List[PatientOut])
def list_patients_for_doctor(doctor_id: int, db: Session = Depends(get_db)):
    # Ambil semua relasi doctor-patient yang masih ada
    assocs = db.query(DoctorPatientAssociation).filter_by(doctor_id=doctor_id).all()
    patient_user_ids = [assoc.patient_id for assoc in assocs]
    if not patient_user_ids:
        return []
    # Ambil data pasien dari tabel Patient dan join ke User agar field name/email terisi
    patients = db.query(Patient).join(User, Patient.patient_id == User.id).filter(Patient.patient_id.in_(patient_user_ids)).all()
    return patients

@router.delete("/doctors/{doctor_id}/unassign-patient/{patient_id}")
def unassign_patient_from_doctor(doctor_id: int, patient_id: int, db: Session = Depends(get_db)):
    assoc = db.query(DoctorPatientAssociation).filter_by(doctor_id=doctor_id, patient_id=patient_id).first()
    if not assoc:
        raise HTTPException(status_code=404, detail="Relation not found")
    db.delete(assoc)
    db.commit()
    return {"message": "Patient unassigned from doctor"}
