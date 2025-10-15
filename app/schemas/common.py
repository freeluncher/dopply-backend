from pydantic import BaseModel
from typing import Optional, List, Any

# Base response models
class BaseResponse(BaseModel):
    success: bool
    message: str

class BaseDataResponse(BaseResponse):
    data: Any

# Pagination model
class Pagination(BaseModel):
    total: int
    limit: int
    offset: int
    hasMore: bool

# Common user data
class UserData(BaseModel):
    id: int
    userId: int
    name: str
    email: str
    role: str
    profilePhotoUrl: Optional[str] = None

# Auth models
class LoginRequest(BaseModel):
    email: str
    password: str

class PatientUserData(UserData):
    hpht: Optional[str] = None
    birthDate: Optional[str] = None
    address: Optional[str] = None
    medicalNote: Optional[str] = None

class LoginData(BaseModel):
    token: str
    refreshToken: str
    user: UserData

class LoginResponse(BaseDataResponse):
    data: LoginData

# Patient models
class PatientData(BaseModel):
    id: int
    userId: int
    name: str
    email: str
    hpht: Optional[str] = None
    birthDate: Optional[str] = None
    address: Optional[str] = None
    medicalNote: Optional[str] = None
    profilePhotoUrl: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class PatientUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    hpht: Optional[str] = None
    birthDate: Optional[str] = None
    address: Optional[str] = None
    medicalNote: Optional[str] = None

class PatientResponse(BaseDataResponse):
    data: PatientData

# Doctor models
class DoctorData(BaseModel):
    id: int
    userId: int
    name: str
    email: str
    specialization: Optional[str] = None
    profilePhotoUrl: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class DoctorUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    specialization: Optional[str] = None

class DoctorResponse(BaseDataResponse):
    data: DoctorData

# Profile photo models
class ProfilePhotoData(BaseModel):
    profilePhotoUrl: str

class ProfilePhotoResponse(BaseDataResponse):
    data: ProfilePhotoData

# Monitoring models
class MonitoringResultRequest(BaseModel):
    patientId: int
    avgBpm: int
    minBpm: int
    maxBpm: int
    duration: int
    dataPoints: List[int]
    timestamp: str

class MonitoringResultData(BaseModel):
    id: int
    patientId: int
    avgBpm: int
    minBpm: int
    maxBpm: int
    duration: int
    classification: str
    sharedWithDoctor: bool = False
    timestamp: str
    createdAt: str

class MonitoringResultResponse(BaseDataResponse):
    data: MonitoringResultData

class MonitoringHistoryItem(BaseModel):
    id: int
    patientId: int
    patientName: str
    avgBpm: int
    minBpm: int
    maxBpm: int
    duration: int
    classification: str
    sharedWithDoctor: bool
    doctorId: Optional[int] = None
    doctorName: Optional[str] = None
    timestamp: str

class MonitoringHistoryData(BaseModel):
    results: List[MonitoringHistoryItem]
    pagination: Pagination

class MonitoringHistoryResponse(BaseDataResponse):
    data: MonitoringHistoryData

class ShareMonitoringRequest(BaseModel):
    monitoringResultId: int
    doctorId: int

class ShareMonitoringData(BaseModel):
    id: int
    sharedWithDoctor: bool
    doctorId: int
    sharedAt: str

class ShareMonitoringResponse(BaseDataResponse):
    data: ShareMonitoringData