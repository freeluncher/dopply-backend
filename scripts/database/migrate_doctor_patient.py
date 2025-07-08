import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.db.session import SessionLocal
from app.models.medical import Doctor, Patient, Record, DoctorPatient

def migrate_doctor_patient_relations():
    db = SessionLocal()
    records = db.query(Record).filter(Record.doctor_id != None, Record.patient_id != None).all()
    inserted = set()
    total = 0
    for record in records:
        total += 1
        doctor = db.query(Doctor).filter(Doctor.doctor_id == record.doctor_id).first()
        patient = db.query(Patient).filter(Patient.id == record.patient_id).first()
        if not doctor:
            print(f"[WARNING] Doctor not found for record.id={record.id}, record.doctor_id={record.doctor_id}")
            continue
        if not patient:
            print(f"[WARNING] Patient not found for record.id={record.id}, record.patient_id={record.patient_id}")
            continue
        key = (doctor.doctor_id, patient.patient_id)
        if key not in inserted:
            db.execute(DoctorPatient.insert().values(doctor_id=doctor.doctor_id, patient_id=patient.patient_id))
            print(f"[INFO] Inserted doctor_id={doctor.doctor_id}, patient_id={patient.patient_id}")
            inserted.add(key)
    db.commit()
    db.close()
    print(f"Migrasi selesai. {len(inserted)} relasi doctor-patient berhasil dimasukkan dari {total} record.")

if __name__ == "__main__":
    migrate_doctor_patient_relations()
