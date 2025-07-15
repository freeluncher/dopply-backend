# Service layer for admin doctor validation endpoints
from sqlalchemy.orm import Session
from app.models.medical import User, UserRole
from typing import List, Dict

class AdminDoctorValidationService:
    @staticmethod
    def count_doctor_validation_requests(db: Session) -> int:
        return db.query(User).filter(
            User.role == UserRole.doctor,
            User.is_verified == False
        ).count()

    @staticmethod
    def list_doctor_validation_requests(db: Session) -> List[Dict]:
        doctors = db.query(User).filter(
            User.role == UserRole.doctor,
            User.is_verified == False
        ).all()
        result = []
        for doctor in doctors:
            result.append({
                "doctor_id": doctor.id,
                "name": doctor.name,
                "email": doctor.email,
                "specialization": doctor.specialization
            })
        return result

    @staticmethod
    def validate_doctor(db: Session, doctor_id: int) -> None:
        doctor = db.query(User).filter(
            User.id == doctor_id,
            User.role == UserRole.doctor
        ).first()
        if not doctor:
            raise ValueError("Doctor not found")
        doctor.is_verified = True
        db.commit()
