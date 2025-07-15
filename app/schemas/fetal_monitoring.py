from pydantic import BaseModel, validator, ConfigDict
from typing import List, Optional
from datetime import datetime

# Request untuk monitoring dari frontend Flutter (setelah monitoring selesai)
class MonitoringRequest(BaseModel):
    patient_id: int
    gestational_age: int
    bpm_data: List[int]  # List BPM dari ESP32
    start_time: datetime
    end_time: Optional[datetime] = None
    notes: Optional[str] = None
    doctor_notes: Optional[str] = None
    
    @validator('gestational_age')
    def validate_gestational_age(cls, v):
        if not 20 <= v <= 42:
            raise ValueError('Gestational age must be between 20 and 42 weeks')
        return v
    
    @validator('bpm_data')
    def validate_bpm_data(cls, v):
        if not v:
            raise ValueError('BPM data cannot be empty')
        for bpm in v:
            if not 50 <= bpm <= 200:
                raise ValueError('BPM values must be between 50 and 200')
        return v

# Response untuk monitoring
class MonitoringResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    patient_id: int
    classification: str
    average_bpm: float
    gestational_age: int
    monitoring_duration: float
    message: str

# Request untuk share monitoring ke dokter
class ShareMonitoringRequest(BaseModel):
    record_id: int
    doctor_id: int
    notes: Optional[str] = None

# Response untuk share monitoring
class ShareMonitoringResponse(BaseModel):
    success: bool
    message: str
    notification_id: Optional[int] = None

# Response untuk history monitoring
class MonitoringHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    patient_name: str
    start_time: datetime
    classification: str
    average_bpm: float
    gestational_age: int
    notes: Optional[str] = None
    doctor_notes: Optional[str] = None
    shared_with_doctor: bool

class MonitoringHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    records: List[MonitoringHistoryItem]
    total_count: int

# Request untuk admin verifikasi dokter
class DoctorVerificationRequest(BaseModel):
    doctor_id: int
    is_verified: bool = True

# Response untuk admin verifikasi dokter
class DoctorVerificationResponse(BaseModel):
    success: bool
    message: str
    doctor_name: str

# Request untuk dokter menambah pasien
class AddPatientRequest(BaseModel):
    patient_email: str
    notes: Optional[str] = None

# Response untuk dokter menambah pasien
class AddPatientResponse(BaseModel):
    success: bool
    message: str
    patient_name: Optional[str] = None

# Item untuk list pasien dokter
class PatientListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    email: str
    hpht: Optional[datetime] = None
    gestational_age_weeks: Optional[int] = None
    last_monitoring: Optional[datetime] = None

# Response untuk list pasien dokter
class PatientListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    patients: List[PatientListItem]
    total_count: int

# Item notifikasi
class NotificationItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    from_patient_name: str
    record_id: int
    message: str
    created_at: datetime
    is_read: bool

# Response untuk list notifikasi
class NotificationListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    notifications: List[NotificationItem]
    unread_count: int
