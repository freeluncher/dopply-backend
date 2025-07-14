from sqlalchemy.orm import Session
from app.models.medical import Record
from app.models.medical import Patient
from typing import List

def get_all_records(db: Session) -> List[Record]:
    return db.query(Record).all()

def get_all_records_for_user(db: Session, user) -> list[dict]:
    from app.models.medical import User
    if user.role.value == "doctor":
        records = db.query(Record).filter(Record.doctor_id == user.id).all()
    elif user.role.value == "patient":
        patient = db.query(Patient).filter(Patient.user_id == user.id).first()
        if patient:
            records = db.query(Record).filter(Record.patient_id == patient.id).all()
        else:
            records = []
    else:
        records = []
    # Sertakan nama pasien
    result = []
    for r in records:
        patient_name = None
        if r.patient and r.patient.user:
            patient_name = r.patient.user.name
        result.append({
            "id": r.id,
            "patient_id": r.patient_id,
            "doctor_id": r.doctor_id,
            "source": r.source.value if hasattr(r.source, 'value') else r.source,
            "bpm_data": r.bpm_data,
            "start_time": r.start_time,
            "end_time": r.end_time,
            "classification": r.classification,
            "notes": r.notes,
            "shared_with": r.shared_with,
            "patient_name": patient_name
        })
    return result
