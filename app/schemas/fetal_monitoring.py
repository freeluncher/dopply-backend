# Schemas untuk Fetal Monitoring System
from pydantic import BaseModel, validator
from typing import List, Optional, Union
from datetime import datetime, date
from enum import Enum

# Enums for validation
class MonitoringTypeEnum(str, Enum):
    clinic = "clinic"
    home = "home"

class FetalClassificationEnum(str, Enum):
    normal = "normal"
    bradycardia = "bradycardia"
    tachycardia = "tachycardia"
    irregular = "irregular"

class RiskLevelEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class OverallClassificationEnum(str, Enum):
    normal = "normal"
    concerning = "concerning"
    abnormal = "abnormal"

# Request/Response Schemas
class FetalHeartRateReadingIn(BaseModel):
    timestamp: datetime
    bpm: int
    signal_quality: Optional[float] = None
    classification: FetalClassificationEnum

    @validator('bpm')
    def validate_bpm(cls, v):
        if not 60 <= v <= 300:
            raise ValueError('BPM must be between 60 and 300')
        return v

    @validator('signal_quality')
    def validate_signal_quality(cls, v):
        if v is not None and not 0.0 <= v <= 1.0:
            raise ValueError('Signal quality must be between 0.0 and 1.0')
        return v

class FetalHeartRateReadingOut(FetalHeartRateReadingIn):
    id: int
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class FetalMonitoringResultIn(BaseModel):
    overall_classification: OverallClassificationEnum
    average_bpm: float
    baseline_variability: Optional[float] = None
    findings: List[str] = []
    recommendations: List[str] = []
    risk_level: RiskLevelEnum

class FetalMonitoringResultOut(FetalMonitoringResultIn):
    id: int
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class FetalMonitoringSessionIn(BaseModel):
    id: str
    patient_id: Optional[int] = None
    doctor_id: Optional[int] = None
    monitoring_type: MonitoringTypeEnum
    gestational_age: int
    start_time: datetime
    end_time: Optional[datetime] = None
    readings: List[FetalHeartRateReadingIn] = []
    notes: Optional[str] = None
    doctor_notes: Optional[str] = None
    shared_with_doctor: bool = False
    result: Optional[FetalMonitoringResultIn] = None

    @validator('gestational_age')
    def validate_gestational_age(cls, v):
        if not 1 <= v <= 42:
            raise ValueError('Gestational age must be between 1 and 42 weeks')
        return v

    @validator('id')
    def validate_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Session ID cannot be empty')
        return v

class FetalMonitoringSessionOut(BaseModel):
    id: str
    patient_id: Optional[int]
    doctor_id: Optional[int]
    monitoring_type: MonitoringTypeEnum
    gestational_age: int
    start_time: datetime
    end_time: Optional[datetime]
    notes: Optional[str]
    doctor_notes: Optional[str]
    shared_with_doctor: bool
    created_at: datetime
    updated_at: datetime
    readings: List[FetalHeartRateReadingOut] = []
    result: Optional[FetalMonitoringResultOut] = None

    class Config:
        from_attributes = True

class PregnancyInfoIn(BaseModel):
    gestational_age: int
    last_menstrual_period: Optional[date] = None
    expected_due_date: Optional[date] = None
    is_high_risk: bool = False
    complications: List[str] = []

    @validator('gestational_age')
    def validate_gestational_age(cls, v):
        if not 1 <= v <= 42:
            raise ValueError('Gestational age must be between 1 and 42 weeks')
        return v

class PregnancyInfoOut(PregnancyInfoIn):
    id: int
    patient_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Classification request/response
class FetalBPMClassificationRequest(BaseModel):
    bpm: Optional[int] = None  # For single BPM
    gestational_age: int
    readings: List[FetalHeartRateReadingIn] = []
    monitoring_type: MonitoringTypeEnum = MonitoringTypeEnum.clinic

    @validator('gestational_age')
    def validate_gestational_age(cls, v):
        if not 1 <= v <= 42:
            raise ValueError('Gestational age must be between 1 and 42 weeks')
        return v

    def get_bpm_values(self) -> List[int]:
        """Extract BPM values from readings or single BPM"""
        if self.readings:
            return [reading.bpm for reading in self.readings]
        elif self.bpm is not None:
            return [self.bpm]
        else:
            raise ValueError("Either bpm or readings must be provided")

class FetalBPMClassificationResponse(BaseModel):
    overall_classification: OverallClassificationEnum
    average_bpm: float
    baseline_variability: float
    findings: List[str]
    recommendations: List[str]
    risk_level: RiskLevelEnum

class FetalHeartRateDataPoint(BaseModel):
    timestamp: datetime
    bpm: int
    signal_quality: Optional[float] = None

    @validator('bpm')
    def validate_bpm(cls, v):
        if not 60 <= v <= 300:
            raise ValueError('BPM must be between 60 and 300')
        return v

    @validator('signal_quality')
    def validate_signal_quality(cls, v):
        if v is not None and not 0.0 <= v <= 1.0:
            raise ValueError('Signal quality must be between 0.0 and 1.0')
        return v

class FetalClassificationRequest(BaseModel):
    fhr_data: List[FetalHeartRateDataPoint]
    gestational_age: int
    maternal_age: Optional[int] = None
    duration_minutes: Optional[int] = None

    @validator('gestational_age')
    def validate_gestational_age(cls, v):
        if not 1 <= v <= 42:
            raise ValueError('Gestational age must be between 1 and 42 weeks')
        return v

    @validator('maternal_age')
    def validate_maternal_age(cls, v):
        if v is not None and not 15 <= v <= 50:
            raise ValueError('Maternal age must be between 15 and 50 years')
        return v

    @validator('fhr_data')
    def validate_fhr_data(cls, v):
        if not v or len(v) == 0:
            raise ValueError('FHR data cannot be empty')
        return v

class FetalClassificationResponse(BaseModel):
    overall_classification: OverallClassificationEnum
    average_bpm: float
    baseline_variability: Optional[float] = None
    findings: List[str] = []
    recommendations: List[str] = []
    risk_level: RiskLevelEnum

# Session management schemas
class FetalMonitoringSessionCreate(BaseModel):
    patient_id: int
    monitoring_type: MonitoringTypeEnum
    gestational_age: int
    start_time: datetime
    end_time: Optional[datetime] = None
    readings: List[FetalHeartRateReadingIn] = []
    notes: Optional[str] = None
    doctor_notes: Optional[str] = None
    result: Optional[FetalMonitoringResultIn] = None

    @validator('gestational_age')
    def validate_gestational_age(cls, v):
        if not 1 <= v <= 42:
            raise ValueError('Gestational age must be between 1 and 42 weeks')
        return v

class FetalMonitoringSessionResponse(BaseModel):
    id: str
    patient_id: int
    doctor_id: Optional[int]
    monitoring_type: MonitoringTypeEnum
    gestational_age: int
    start_time: datetime
    end_time: Optional[datetime]
    readings: List[FetalHeartRateReadingOut] = []
    notes: Optional[str]
    doctor_notes: Optional[str]
    shared_with_doctor: bool
    result: Optional[FetalMonitoringResultOut]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FetalMonitoringSessionList(BaseModel):
    sessions: List[FetalMonitoringSessionResponse]
    total_count: int
    skip: int
    limit: int

# Pregnancy info schemas
class PregnancyInfoCreate(BaseModel):
    patient_id: int
    gestational_age: int
    last_menstrual_period: Optional[date] = None
    expected_due_date: Optional[date] = None
    is_high_risk: bool = False
    complications: List[str] = []

    @validator('gestational_age')
    def validate_gestational_age(cls, v):
        if not 1 <= v <= 42:
            raise ValueError('Gestational age must be between 1 and 42 weeks')
        return v

class PregnancyInfoUpdate(BaseModel):
    gestational_age: Optional[int] = None
    last_menstrual_period: Optional[date] = None
    expected_due_date: Optional[date] = None
    is_high_risk: Optional[bool] = None
    complications: Optional[List[str]] = None

    @validator('gestational_age')
    def validate_gestational_age(cls, v):
        if v is not None and not 1 <= v <= 42:
            raise ValueError('Gestational age must be between 1 and 42 weeks')
        return v

class PregnancyInfoResponse(BaseModel):
    id: int
    patient_id: int
    gestational_age: int
    last_menstrual_period: Optional[date]
    expected_due_date: Optional[date]
    is_high_risk: bool
    complications: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Session list request/response
class FetalSessionListRequest(BaseModel):
    patient_id: Optional[int] = None
    doctor_id: Optional[int] = None
    monitoring_type: Optional[MonitoringTypeEnum] = None
    limit: int = 10
    offset: int = 0

    @validator('limit')
    def validate_limit(cls, v):
        if not 1 <= v <= 100:
            raise ValueError('Limit must be between 1 and 100')
        return v

    @validator('offset')
    def validate_offset(cls, v):
        if v < 0:
            raise ValueError('Offset must be non-negative')
        return v

class FetalSessionListResponse(BaseModel):
    sessions: List[FetalMonitoringSessionOut]
    total_count: int
    limit: int
    offset: int

# Share session request
class ShareSessionRequest(BaseModel):
    doctor_id: int
    message: Optional[str] = None

class ShareSessionResponse(BaseModel):
    success: bool
    message: str

# Session save response
class SessionSaveResponse(BaseModel):
    id: str
    message: str
    created_at: datetime
