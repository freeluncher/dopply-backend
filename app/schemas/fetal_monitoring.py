# NEW Schemas untuk ESP32 Fetal Monitoring System - SIMPLIFIED
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Basic enums
class MonitoringTypeEnum(str, Enum):
    doctor = "doctor"  # Monitoring oleh dokter
    patient = "patient"  # Monitoring mandiri pasien

class ClassificationEnum(str, Enum):
    normal = "normal"
    bradycardia = "bradycardia" 
    tachycardia = "tachycardia"
    irregular = "irregular"

class RiskLevelEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

# NEW: ESP32 Monitoring Request
class ESP32MonitoringRequest(BaseModel):
    patient_id: int
    gestational_age: int
    bpm_readings: List[int]  # Raw BPM data dari ESP32
    monitoring_duration: Optional[float] = None  # dalam menit
    notes: Optional[str] = None
    
    @validator('gestational_age')
    def validate_gestational_age(cls, v):
        if not 1 <= v <= 42:
            raise ValueError('Gestational age must be between 1 and 42 weeks')
        return v
    
    @validator('bpm_readings')
    def validate_bpm_readings(cls, v):
        if not v:
            raise ValueError('BPM readings cannot be empty')
        for bpm in v:
            if not 0 <= bpm <= 300:
                raise ValueError('BPM values must be between 0 and 300')
        return v

# NEW: Classification Result
class MonitoringClassificationResult(BaseModel):
    classification: ClassificationEnum
    average_bpm: float
    risk_level: RiskLevelEnum  
    recommendations: List[str]
    variability: float
    min_bpm: int
    max_bpm: int
    total_readings: int
    is_irregular: bool
    normal_range: Dict[str, int]

# NEW: ESP32 Monitoring Response
class ESP32MonitoringResponse(BaseModel):
    success: bool
    message: str
    record_id: int
    classification_result: MonitoringClassificationResult

# NEW: Monitoring History
class MonitoringRecord(BaseModel):
    id: int
    patient_id: int
    doctor_id: Optional[int] = None
    monitoring_type: MonitoringTypeEnum
    gestational_age: int
    start_time: datetime
    end_time: Optional[datetime] = None
    monitoring_duration: float
    classification: ClassificationEnum
    average_bpm: float
    notes: str
    doctor_notes: str
    shared_with_doctor: bool = False
    created_at: datetime

class MonitoringHistoryResponse(BaseModel):
    success: bool
    data: List[MonitoringRecord]
    total_count: int
    current_page: int
    total_pages: int

# NEW: Share Monitoring
class ShareMonitoringRequest(BaseModel):
    record_id: int
    doctor_id: int
    notes: Optional[str] = None

class ShareMonitoringResponse(BaseModel):
    success: bool
    message: str
    shared_at: datetime

# NEW: Assigned Patients
class AssignedPatient(BaseModel):
    patient_id: int
    patient_name: str
    assigned_date: str
    status: str
    contact_info: str

class AssignedPatientsResponse(BaseModel):
    success: bool
    patients: List[AssignedPatient]

# KEEP: BPM Classification for backward compatibility
class FetalBPMClassificationRequest(BaseModel):
    bpm_readings: List[int]
    gestational_age: int
    
    @validator('gestational_age')
    def validate_gestational_age(cls, v):
        if not 1 <= v <= 42:
            raise ValueError('Gestational age must be between 1 and 42 weeks')
        return v
    
    @validator('bpm_readings')
    def validate_bpm_readings(cls, v):
        if not v:
            raise ValueError('BPM readings cannot be empty')
        return v

class FetalBPMClassificationResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
