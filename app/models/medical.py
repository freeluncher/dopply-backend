from sqlalchemy import Column, Integer, String, Enum, Date, Text, ForeignKey, DateTime, JSON, Boolean, Float
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum
from datetime import datetime
from app.core.time_utils import get_local_naive_now

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
    photo_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=get_local_naive_now)
    
    # For doctors only
    specialization = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    patients = relationship("Patient", back_populates="user")
    records_as_doctor = relationship("Record", back_populates="doctor", foreign_keys=["doctor_id"])
    notifications = relationship("Notification", back_populates="to_doctor", foreign_keys=["to_doctor_id"])

class DoctorPatientAssociation(Base):
    __tablename__ = "doctor_patient"
    doctor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), primary_key=True)
    assigned_at = Column(DateTime, nullable=False, default=get_local_naive_now)

    doctor = relationship("User", foreign_keys=[doctor_id])
    patient = relationship("Patient", back_populates="doctor_patient_associations", foreign_keys=[patient_id])

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    hpht = Column(Date, nullable=True)  # Hari Pertama Haid Terakhir
    birth_date = Column(Date, nullable=True)
    address = Column(String(255), nullable=True)
    medical_note = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="patients", foreign_keys=[user_id])
    doctor_patient_associations = relationship("DoctorPatientAssociation", back_populates="patient", foreign_keys=["patient_id"])
    records = relationship("Record", back_populates="patient", foreign_keys=["patient_id"])

class Record(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Dokter yang melakukan monitoring
    source = Column(String(50), nullable=False, default="esp32")  # esp32, manual, etc
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    bpm_data = Column(JSON, nullable=True)  # List BPM data dari ESP32
    classification = Column(String(50), nullable=True)  # normal, bradikardia, takikardia
    gestational_age = Column(Integer, nullable=True)  # Usia kehamilan dalam minggu
    notes = Column(Text, nullable=True)  # Catatan pasien
    doctor_notes = Column(Text, nullable=True)  # Catatan dokter
    monitoring_duration = Column(Float, nullable=True)  # Durasi monitoring dalam menit
    shared_with = Column(Integer, ForeignKey("users.id"), nullable=True)  # Dokter yang dibagikan
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # User yang membuat record
    
    # Relationships
    patient = relationship("Patient", back_populates="records", foreign_keys=["patient_id"])
    doctor = relationship("User", back_populates="records_as_doctor", foreign_keys=["doctor_id"])
    notifications = relationship("Notification", back_populates="record", foreign_keys=["record_id"])

class NotificationStatus(enum.Enum):
    unread = "unread"
    read = "read"

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    from_patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    to_doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    record_id = Column(Integer, ForeignKey("records.id"), nullable=False)
    message = Column(Text, nullable=False)  # Pesan notifikasi
    status = Column(Enum(NotificationStatus), nullable=False, default=NotificationStatus.unread)
    created_at = Column(DateTime, nullable=False, default=get_local_naive_now)
    
    # Relationships
    record = relationship("Record", back_populates="notifications", foreign_keys=["record_id"])
    to_doctor = relationship("User", back_populates="notifications", foreign_keys=["to_doctor_id"])
