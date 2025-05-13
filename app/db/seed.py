from app.db.session import SessionLocal
from app.models.medical import User, UserRole, Patient, Record, RecordSource, Notification, NotificationStatus
from datetime import datetime, date

def seed():
    db = SessionLocal()
    # Users
    admin = User(name="Admin", email="admin@example.com", password_hash="adminpass", role=UserRole.admin)
    doctor = User(name="Dr. John", email="doctor@example.com", password_hash="doctorpass", role=UserRole.doctor)
    patient_user = User(name="Jane Patient", email="patient@example.com", password_hash="patientpass", role=UserRole.patient)
    db.add_all([admin, doctor, patient_user])
    db.commit()
    db.refresh(admin)
    db.refresh(doctor)
    db.refresh(patient_user)

    # Patient
    patient = Patient(patient_id=patient_user.id, birth_date=date(1990, 1, 1), address="123 Main St", medical_note="No allergies.")
    db.add(patient)
    db.commit()
    db.refresh(patient)

    # Record
    record = Record(
        patient_id=patient.id,
        doctor_id=doctor.id,
        source=RecordSource.clinic,
        bpm_data={"bpm": 72},
        start_time=datetime(2024, 5, 1, 9, 0),
        end_time=datetime(2024, 5, 1, 9, 30),
        classification="normal",
        notes="Routine checkup.",
        shared_with=doctor.id
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # Notification
    notif = Notification(
        from_patient_id=patient.id,
        to_doctor_id=doctor.id,
        record_id=record.id,
        status=NotificationStatus.unread
    )
    db.add(notif)
    db.commit()
    db.close()

if __name__ == "__main__":
    seed()
