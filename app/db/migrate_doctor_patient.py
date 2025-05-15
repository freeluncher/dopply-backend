from app.db.session import SessionLocal
from app.models.medical import Doctor, Patient, Record, DoctorPatient

def migrate_doctor_patient_relations():
    db = SessionLocal()
    # Ambil semua record yang punya doctor_id dan patient_id
    records = db.query(Record).filter(Record.doctor_id != None, Record.patient_id != None).all()
    inserted = set()
    for record in records:
        # Ambil doctor_id dari doctors.doctor_id dan patient_id dari patients.patient_id
        doctor = db.query(Doctor).filter(Doctor.doctor_id == record.doctor_id).first()
        patient = db.query(Patient).filter(Patient.id == record.patient_id).first()
        if doctor and patient:
            key = (doctor.doctor_id, patient.patient_id)
            if key not in inserted:
                db.execute(DoctorPatient.insert().values(doctor_id=doctor.doctor_id, patient_id=patient.patient_id))
                inserted.add(key)
    db.commit()
    db.close()
    print(f"Migrasi selesai. {len(inserted)} relasi doctor-patient berhasil dimasukkan.")

if __name__ == "__main__":
    migrate_doctor_patient_relations()
