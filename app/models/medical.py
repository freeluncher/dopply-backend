from sqlalchemy import Column, Integer, String, Enum, Date, Text, ForeignKey, DateTime, JSON, Boolean, Table, Float, Float
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
    
    patients = relationship("Patient", back_populates="user")
    records_as_doctor = relationship("Record", back_populates="doctor", foreign_keys='Record.doctor_id')
    records_shared = relationship("Record", back_populates="shared_with_user", foreign_keys='Record.shared_with')
    # Relationship for when this user is a doctor in doctor_patient associations
    assigned_patients = relationship("Patient", secondary="doctor_patient", viewonly=True,
                                   primaryjoin="User.id == DoctorPatientAssociation.doctor_id",
                                   secondaryjoin="DoctorPatientAssociation.patient_id == Patient.id")

class DoctorPatientAssociation(Base):
    __tablename__ = "doctor_patient"
    doctor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), primary_key=True)
    assigned_at = Column(DateTime, nullable=False, default=get_local_naive_now)
    updated_at = Column(DateTime, nullable=True, default=get_local_naive_now, onupdate=get_local_naive_now)
    status = Column(String(50), nullable=True, default="active")
    note = Column(Text, nullable=True)

    # Relationships
    doctor = relationship("User", foreign_keys=[doctor_id])
    patient = relationship("Patient", back_populates="doctor_patient_associations")

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    birth_date = Column(Date, nullable=True)
    address = Column(String(255), nullable=True)
    medical_note = Column(Text, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)
    phone = Column(String(20), nullable=True)
    
    user = relationship("User", back_populates="patients")
    records = relationship("Record", back_populates="patient")
    doctor_patient_associations = relationship("DoctorPatientAssociation", back_populates="patient")
    # Many-to-many relationship with doctors through the association table
    assigned_doctors = relationship("User", secondary="doctor_patient", viewonly=True, 
                                   primaryjoin="Patient.id == DoctorPatientAssociation.patient_id",
                                   secondaryjoin="DoctorPatientAssociation.doctor_id == User.id")

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
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    is_valid = Column(Boolean, default=False, nullable=False)
    
    # User relationship
    user = relationship("User")
    
    # Many-to-many relationship with patients through the association table
    assigned_patients = relationship("Patient", secondary="doctor_patient", viewonly=True,
                                   primaryjoin="Doctor.doctor_id == DoctorPatientAssociation.doctor_id",
                                   secondaryjoin="DoctorPatientAssociation.patient_id == Patient.id")

# Enum untuk fetal monitoring - tetap digunakan untuk klasifikasi
class MonitoringType(enum.Enum):
    clinic = "clinic"
    home = "home"

class FetalClassification(enum.Enum):
    normal = "normal"
    bradycardia = "bradycardia"
    tachycardia = "tachycardia"
    irregular = "irregular"

class RiskLevel(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class OverallClassification(enum.Enum):
    normal = "normal"
    concerning = "concerning"
    abnormal = "abnormal"

# Pregnancy info tetap diperlukan untuk gestational age
class PregnancyInfo(Base):
    __tablename__ = "pregnancy_info"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    gestational_age = Column(Integer, nullable=False)  # weeks
    last_menstrual_period = Column(Date, nullable=True)
    expected_due_date = Column(Date, nullable=True)
    is_high_risk = Column(Boolean, default=False, nullable=False)
    complications = Column(JSON, nullable=True)  # Array of strings
    created_at = Column(DateTime, nullable=False, default=get_local_naive_now)
    updated_at = Column(DateTime, nullable=False, default=get_local_naive_now, onupdate=get_local_naive_now)
    
    # Relationships
    patient = relationship("Patient")
