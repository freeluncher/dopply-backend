# Service layer for admin doctor validation endpoints
from sqlalchemy.orm import Session
from app.models.medical import Doctor, User
from typing import List, Dict

class AdminDoctorValidationService:
    @staticmethod
    def count_doctor_validation_requests(db: Session) -> int:
        return db.query(Doctor).filter(Doctor.is_valid == False).count()

    @staticmethod
    def list_doctor_validation_requests(db: Session) -> List[Dict]:
        doctors = db.query(Doctor).filter(Doctor.is_valid == False).all()
        result = []
        for doctor in doctors:
            user = db.query(User).filter(User.id == doctor.doctor_id).first()
            result.append({
                "doctor_id": doctor.id,
                "doctor_id": doctor.doctor_id,
                "name": user.name if user else None,
                "email": user.email if user else None
            })
        return result

    @staticmethod
    def validate_doctor(db: Session, doctor_id: int) -> None:
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            raise ValueError("Doctor not found")
        doctor.is_valid = True
        db.commit()
