from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.patient import PatientCreate, PatientUpdate, PatientOut
from app.services.patient_service import get_patients, get_patient, update_patient, delete_patient
from app.db.session import SessionLocal
from app.models.medical import Doctor, Patient, User, DoctorPatient
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@router.post("/doctors/{doctor_id}/assign-patient/{patient_id}")
def assign_patient_to_doctor(doctor_id: int, patient_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not doctor or not patient:
        raise HTTPException(status_code=404, detail="Doctor or patient not found")
    exists = db.execute(DoctorPatient.select().where(DoctorPatient.c.doctor_id == doctor_id, DoctorPatient.c.patient_id == patient_id)).first()
    if exists:
        raise HTTPException(status_code=400, detail="Patient already assigned to doctor")
    db.execute(DoctorPatient.insert().values(doctor_id=doctor_id, patient_id=patient_id))
    db.commit()
    return {"message": "Patient assigned to doctor"}

@router.delete("/doctors/{doctor_id}/unassign-patient/{patient_id}")
def unassign_patient_from_doctor(doctor_id: int, patient_id: int, db: Session = Depends(get_db)):
    result = db.execute(DoctorPatient.delete().where(DoctorPatient.c.doctor_id == doctor_id, DoctorPatient.c.patient_id == patient_id))
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Relation not found")
    return {"message": "Patient unassigned from doctor"}
