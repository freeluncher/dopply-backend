from sqlalchemy.orm import Session
from app.models.medical import Patient, User, Doctor
from app.schemas.patient import PatientCreate, PatientUpdate
from app.core.security import get_password_hash
from typing import List, Optional

def get_patients(db: Session) -> List[Patient]:
    # Only return patients with a valid linked User (with name and email)
    return db.query(Patient).join(User, Patient.patient_id == User.id).filter(User.name != None, User.email != None).all()

def get_patient(db: Session, patient_id: int) -> Optional[Patient]:
    return db.query(Patient).filter(Patient.patient_id == patient_id).first()

def update_patient(db: Session, patient_id: int, patient_data: PatientUpdate) -> Optional[Patient]:
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
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
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        return False
    user = db.query(User).filter(User.id == patient.patient_id).first()
    db.delete(patient)
    if user:
        db.delete(user)
    db.commit()
    return True

def register_user_universal(db, data):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        # Register baru (dokter/pasien)
        hashed_password = get_password_hash(data.password)
        user = User(
            name=data.name,
            email=data.email,
            password_hash=hashed_password,
            role=data.role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        if data.role == "doctor":
            doctor = Doctor(doctor_id=user.id, is_valid=False)
            db.add(doctor)
            db.commit()
            db.refresh(doctor)
        elif data.role == "patient":
            patient = Patient(
                patient_id=user.id,
                birth_date=data.birth_date,
                address=data.address,
                medical_note=data.medical_note
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)
        return user
    elif user.role == "patient" and (not user.password_hash or user.password_hash == ""):
        # Aktivasi pasien yang sudah didaftarkan dokter
        user.password_hash = get_password_hash(data.password)
        db.commit()
        db.refresh(user)
        patient = db.query(Patient).filter(Patient.patient_id == user.id).first()
        if patient:
            if data.birth_date is not None:
                patient.birth_date = data.birth_date
            if data.address is not None:
                patient.address = data.address
            if data.medical_note is not None:
                patient.medical_note = data.medical_note
            db.commit()
            db.refresh(patient)
        return user
    else:
        raise Exception("Email sudah digunakan")
