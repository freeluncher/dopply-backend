from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class PatientStatusHistory(Base):
    __tablename__ = "patient_status_history"
    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime, nullable=False, default=datetime.now)

    doctor = relationship("User", foreign_keys=[doctor_id])
    patient = relationship("Patient", foreign_keys=[patient_id])
    changed_by_user = relationship("User", foreign_keys=[changed_by])
