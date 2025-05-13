from sqlalchemy.orm import Session
from app.models.medical import Record
from app.models.medical import Patient
from typing import List

def get_all_records(db: Session) -> List[Record]:
    return db.query(Record).all()

def get_all_records_for_user(db: Session, user) -> list[Record]:
    if user.role.value == "doctor":
        # Tampilkan records yang doctor_id = user.id
        return db.query(Record).filter(Record.doctor_id == user.id).all()
    elif user.role.value == "patient":
        # Tampilkan records yang patient_id = patient.id (dari tabel patients)
        patient = db.query(Patient).filter(Patient.patient_id == user.id).first()
        if patient:
            return db.query(Record).filter(Record.patient_id == patient.id).all()
        else:
            return []
    else:
        return []
