# Service layer for doctor-patient association and management
from sqlalchemy.orm import Session
from app.models.medical import Doctor, Patient, User, DoctorPatientAssociation
from datetime import datetime
from typing import Optional, List
from app.core.time_utils import get_local_naive_now

class DoctorPatientService:
    @staticmethod
    def assign_patient_to_doctor(db: Session, doctor_id: int, patient_id: int, status: Optional[str] = None, note: Optional[str] = None) -> DoctorPatientAssociation:
        doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not doctor or not patient:
            raise ValueError("Doctor or patient not found")
        assoc = db.query(DoctorPatientAssociation).filter_by(doctor_id=doctor_id, patient_id=patient_id).first()
        if assoc:
            raise ValueError("Patient already assigned to doctor")
        assoc = DoctorPatientAssociation(
            doctor_id=doctor_id,
            patient_id=patient_id,
            assigned_at=get_local_naive_now(),
            status=status,
            note=note
        )
        db.add(assoc)
        db.commit()
        db.refresh(assoc)
        return assoc

    @staticmethod
    def assign_patient_to_doctor_by_email(db: Session, doctor_id: int, email: str, status: Optional[str] = None, note: Optional[str] = None) -> DoctorPatientAssociation:
        doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
        if not doctor:
            raise ValueError("Doctor not found")
        patient = db.query(Patient).join(User).filter(User.email == email).first()
        if not patient:
            raise ValueError("Patient with this email not found")
        assoc = db.query(DoctorPatientAssociation).filter_by(doctor_id=doctor_id, patient_id=patient.id).first()
        if assoc:
            raise ValueError("Patient already assigned to doctor")
        assoc = DoctorPatientAssociation(
            doctor_id=doctor_id,
            patient_id=patient.id,
            assigned_at=get_local_naive_now(),
            status=status,
            note=note
        )
        db.add(assoc)
        db.commit()
        db.refresh(assoc)
        return assoc

    @staticmethod
    def update_doctor_patient_association(db: Session, doctor_id: int, patient_id: int, status: Optional[str] = None, note: Optional[str] = None) -> DoctorPatientAssociation:
        assoc = db.query(DoctorPatientAssociation).filter_by(doctor_id=doctor_id, patient_id=patient_id).first()
        if not assoc:
            raise ValueError("Relation not found")
        if status is not None:
            assoc.status = status
        if note is not None:
            assoc.note = note
        db.commit()
        db.refresh(assoc)
        return assoc

    @staticmethod
    def list_patients_for_doctor(db: Session, doctor_id: int) -> list:
        assocs = db.query(DoctorPatientAssociation).filter_by(doctor_id=doctor_id).all()
        patient_ids = [assoc.patient_id for assoc in assocs]
        if not patient_ids:
            return []
        patients = db.query(Patient).join(User, Patient.user_id == User.id).filter(Patient.id.in_(patient_ids)).all()
        result = []
        for p in patients:
            result.append({
                "id": p.id,
                "patient_id": p.id,
                "name": p.user.name if p.user else None,
                "email": p.user.email if p.user else None,
                "birth_date": p.birth_date,
                "address": p.address,
                "medical_note": p.medical_note,
            })
        return result

    @staticmethod
    def unassign_patient_from_doctor(db: Session, doctor_id: int, patient_id: int) -> None:
        assoc = db.query(DoctorPatientAssociation).filter_by(doctor_id=doctor_id, patient_id=patient_id).first()
        if not assoc:
            raise ValueError("Relation not found")
        db.delete(assoc)
        db.commit()
