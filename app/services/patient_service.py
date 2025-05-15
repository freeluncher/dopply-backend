from sqlalchemy.orm import Session
from app.models.medical import Patient, User
from app.schemas.patient import PatientCreate, PatientUpdate
from app.core.security import get_password_hash
from typing import List, Optional

def get_patients(db: Session) -> List[Patient]:
    return db.query(Patient).all()

def get_patient(db: Session, patient_id: int) -> Optional[Patient]:
    return db.query(Patient).filter(Patient.id == patient_id).first()

def create_patient(db: Session, patient_data: PatientCreate) -> Patient:
    hashed_password = get_password_hash(patient_data.password)
    user = User(
        name=patient_data.name,
        email=patient_data.email,
        password_hash=hashed_password,
        role="patient"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    patient = Patient(
        patient_id=user.id,
        birth_date=patient_data.birth_date,
        address=patient_data.address,
        medical_note=patient_data.medical_note
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

def update_patient(db: Session, patient_id: int, patient_data: PatientUpdate) -> Optional[Patient]:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return None
    user = db.query(User).filter(User.id == patient.patient_id).first()
    if patient_data.name:
        user.name = patient_data.name
    if patient_data.email:
        user.email = patient_data.email
    if patient_data.password:
        user.password_hash = get_password_hash(patient_data.password)
    if patient_data.birth_date is not None:
        patient.birth_date = patient_data.birth_date
    if patient_data.address is not None:
        patient.address = patient_data.address
    if patient_data.medical_note is not None:
        patient.medical_note = patient_data.medical_note
    db.commit()
    db.refresh(patient)
    return patient

def delete_patient(db: Session, patient_id: int) -> bool:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return False
    user = db.query(User).filter(User.id == patient.patient_id).first()
    db.delete(patient)
    if user:
        db.delete(user)
    db.commit()
    return True
