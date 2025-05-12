from sqlalchemy import Column, Integer, String, Enum, Date, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum

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

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    birth_date = Column(Date, nullable=True)
    address = Column(String(255), nullable=True)
    medical_note = Column(Text, nullable=True)
    user = relationship("User", back_populates="patients")
    records = relationship("Record", back_populates="patient")

class RecordSource(enum.Enum):
    clinic = "clinic"
    self_ = "self"

class Record(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    source = Column(Enum(RecordSource), nullable=False)
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
