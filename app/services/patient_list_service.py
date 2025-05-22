# Service layer for listing patients by doctor (with search)
from sqlalchemy.orm import Session
from app.models.medical import Record, Patient, User
from typing import Optional, List

class PatientListService:
    @staticmethod
    def get_patients_by_doctor(db: Session, doctor_id: int, search: Optional[str] = None) -> list:
        patient_ids = db.query(Record.patient_id).filter(Record.doctor_id == doctor_id).distinct().all()
        patient_ids = [pid[0] for pid in patient_ids]
        if not patient_ids:
            return []
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
