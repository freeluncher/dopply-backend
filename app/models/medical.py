from sqlalchemy import Column, Integer, String, Enum, Date, Text, ForeignKey, DateTime, JSON, Boolean, Table
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum
from datetime import datetime

class UserRole(enum.Enum):
    admin = "admin"
    doctor = "doctor"
    patient = "patient"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    patients = relationship("Patient", back_populates="user")
    records_as_doctor = relationship("Record", back_populates="doctor", foreign_keys='Record.doctor_id')
    records_shared = relationship("Record", back_populates="shared_with_user", foreign_keys='Record.shared_with')

class DoctorPatientAssociation(Base):
    __tablename__ = "doctor_patient"
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id", ondelete="CASCADE"), primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id", ondelete="CASCADE"), primary_key=True)
    assigned_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String(50), nullable=True)  # contoh: 'active', 'finished', dsb
    note = Column(Text, nullable=True)  # catatan khusus dokter terhadap pasien

    doctor = relationship("Doctor", back_populates="doctor_patient_associations")
    patient = relationship("Patient", back_populates="doctor_patient_associations")

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # ubah dari user_id ke patient_id
    birth_date = Column(Date, nullable=True)
    address = Column(String(255), nullable=True)
    medical_note = Column(Text, nullable=True)
    user = relationship("User", back_populates="patients")
    records = relationship("Record", back_populates="patient")
    doctor_patient_associations = relationship("DoctorPatientAssociation", back_populates="patient")
    doctors = relationship("Doctor", secondary="doctor_patient", back_populates="patients", viewonly=True)

class RecordSource(enum.Enum):
    clinic = "clinic"
    self_ = "self"  # Tetap gunakan self_ di Python, tapi di DB akan tersimpan sebagai 'self'

class Record(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    source = Column(Enum(RecordSource, values_callable=lambda x: [e.value for e in x]), nullable=False)
    bpm_data = Column(JSON, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    classification = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    shared_with = Column(Integer, ForeignKey("users.id"), nullable=True)
    patient = relationship("Patient", back_populates="records")
    doctor = relationship("User", back_populates="records_as_doctor", foreign_keys=[doctor_id])
    shared_with_user = relationship("User", back_populates="records_shared", foreign_keys=[shared_with])
    notifications = relationship("Notification", back_populates="record")

class NotificationStatus(enum.Enum):
    unread = "unread"
    read = "read"

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    from_patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    to_doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    record_id = Column(Integer, ForeignKey("records.id"), nullable=False)
    status = Column(Enum(NotificationStatus), nullable=False)
    record = relationship("Record", back_populates="notifications")
    from_patient = relationship("Patient")
    to_doctor = relationship("User")

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)  # ubah dari user_id ke doctor_id
    is_valid = Column(Boolean, default=False, nullable=False)
    user = relationship("User")
    doctor_patient_associations = relationship("DoctorPatientAssociation", back_populates="doctor")
    patients = relationship("Patient", secondary="doctor_patient", back_populates="doctors", viewonly=True)
