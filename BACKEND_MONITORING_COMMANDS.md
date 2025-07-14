# 🔧 PERINTAH BACKEND - HAPUS DAN REBUILD MONITORING
*Detailed Backend Commands for Removal and Rebuild*

## 📋 LANGKAH-LANGKAH BACKEND

### STEP 1: BACKUP DAN PERSIAPAN

```bash
# 1. Backup files yang akan dimodifikasi
cp app/api/v1/endpoints/fetal_monitoring.py app/api/v1/endpoints/fetal_monitoring_backup.py
cp app/services/fetal_monitoring_service.py app/services/fetal_monitoring_service_backup.py
cp app/schemas/fetal_monitoring.py app/schemas/fetal_monitoring_backup.py
cp app/api/v1/endpoints/doctor_dashboard.py app/api/v1/endpoints/doctor_dashboard_backup.py

# 2. Commit current state
git add .
git commit -m "Backup: Before monitoring system rebuild"
```

### STEP 2: CLEAN UP EXISTING CODE

#### A. Hapus Endpoints Lama dari `fetal_monitoring.py`:
```python
# HAPUS SEMUA endpoints ini dari app/api/v1/endpoints/fetal_monitoring.py:

# 1. Remove monitoring session endpoints
@router.post("/sessions", response_model=FetalMonitoringSessionResponse)
@router.get("/sessions", response_model=FetalMonitoringSessionList) 
@router.get("/sessions/{session_id}", response_model=FetalMonitoringSessionResponse)
@router.put("/sessions/{session_id}/share", response_model=ShareSessionResponse)

# 2. Remove pregnancy info endpoints  
@router.post("/pregnancy-info", response_model=PregnancyInfoResponse)
@router.get("/pregnancy-info/{patient_id}", response_model=PregnancyInfoResponse)
@router.put("/pregnancy-info/{patient_id}", response_model=PregnancyInfoResponse)

# 3. Remove old classification endpoint
@router.post("/classify", response_model=FetalClassificationResponse)

# HASIL: File hanya berisi dependency imports dan basic setup
```

#### B. Clean Up Service Methods:
```python
# HAPUS methods ini dari app/services/fetal_monitoring_service.py:

# 1. Remove session management methods
def save_monitoring_session(db, request, user_id: int) -> Dict[str, Any]:
def get_monitoring_sessions(db, patient_id: Optional[int] = None, skip: int = 0, limit: int = 20) -> Dict[str, Any]:
def get_monitoring_session(db, session_id: int, user_id: int, user_role: str) -> Optional[Dict[str, Any]]:
def share_session_with_doctor(db, session_id: int, patient_id: int, doctor_id: int) -> Dict[str, Any]:

# 2. Remove pregnancy info methods
def create_pregnancy_info(db, patient_id: int, pregnancy_data) -> Dict[str, Any]:
def get_pregnancy_info(db, patient_id: int) -> Optional[Dict[str, Any]]:
def update_pregnancy_info(db, patient_id: int, pregnancy_data) -> Optional[Dict[str, Any]]:

# HASIL: Hanya tersisa classification methods (classify_fetal_bpm + helper methods)
```

#### C. Clean Up Schemas:
```python
# HAPUS schemas ini dari app/schemas/fetal_monitoring.py:

# 1. Remove complex session schemas
class FetalMonitoringSessionCreate(BaseModel):
class FetalMonitoringSessionResponse(BaseModel):
class FetalMonitoringSessionList(BaseModel):
class ShareSessionRequest(BaseModel):
class ShareSessionResponse(BaseModel):

# 2. Remove pregnancy info schemas
class PregnancyInfoCreate(BaseModel):
class PregnancyInfoUpdate(BaseModel):
class PregnancyInfoResponse(BaseModel):

# 3. Remove old classification schemas
class FetalClassificationRequest(BaseModel):
class FetalClassificationResponse(BaseModel):

# HASIL: Hanya tersisa basic enums dan helper schemas
```

#### D. Clean Up Doctor Dashboard:
```python
# HAPUS dari app/api/v1/endpoints/doctor_dashboard.py:

@router.get("/patients/{patient_id}/monitoring/history", response_model=PatientMonitoringHistoryResponse)
def get_patient_monitoring_history(...):

# Dan response models terkait:
class MonitoringRecord(BaseModel):
class PatientMonitoringHistoryResponse(BaseModel):
```

### STEP 3: IMPLEMENT NEW SCHEMAS

```python
# REPLACE app/schemas/fetal_monitoring.py dengan:

from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Basic enums (keep existing)
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
    
    @validator('bmp_readings')
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
```

### STEP 4: IMPLEMENT NEW SERVICE METHODS

```python
# ADD to app/services/fetal_monitoring_service.py:

@staticmethod
def process_esp32_monitoring(db, request: ESP32MonitoringRequest, user_id: int, user_role: str) -> Dict[str, Any]:
    """Process ESP32 monitoring data and save to records table"""
    from app.models.medical import Record, Patient
    from app.core.time_utils import get_local_now
    
    # Validate patient exists
    patient = db.query(Patient).filter(Patient.id == request.patient_id).first()
    if not patient:
        raise ValueError("Patient not found")
    
    # Classify BPM data
    classification_result = FetalMonitoringService.classify_fetal_bpm(
        request.bpm_readings, 
        request.gestational_age
    )
    
    # Calculate monitoring duration
    duration = request.monitoring_duration or (len(request.bpm_readings) / 60.0)  # Assume 1 reading per second
    
    # Create record
    record = Record(
        patient_id=request.patient_id,
        start_time=get_local_now(),
        end_time=get_local_now(),
        monitoring_duration=duration,
        heart_rate_data=json.dumps(request.bpm_readings),
        classification=classification_result['overall_classification'],
        notes=request.notes or "",
        doctor_notes="",
        gestational_age=request.gestational_age,
        created_by=user_id
    )
    
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return {
        "record_id": record.id,
        "classification_result": classification_result
    }

@staticmethod
def get_monitoring_history(db, patient_id: Optional[int] = None, doctor_id: Optional[int] = None, 
                          user_role: str = "patient", skip: int = 0, limit: int = 20) -> Dict[str, Any]:
    """Get monitoring history from records table with role-based access"""
    from app.models.medical import Record, Patient, User
    
    query = db.query(Record).join(Patient)
    
    # Role-based filtering
    if user_role == "patient" and patient_id:
        query = query.filter(Record.patient_id == patient_id)
    elif user_role == "doctor" and doctor_id:
        # Doctor can see records of their assigned patients
        from app.models.medical import DoctorPatientAssociation
        assigned_patient_ids = db.query(DoctorPatientAssociation.patient_id).filter(
            DoctorPatientAssociation.doctor_id == doctor_id
        ).subquery()
        query = query.filter(Record.patient_id.in_(assigned_patient_ids))
    
    total_count = query.count()
    records = query.order_by(Record.start_time.desc()).offset(skip).limit(limit).all()
    
    record_list = []
    for record in records:
        patient = db.query(Patient).filter(Patient.id == record.patient_id).first()
        record_list.append({
            "id": record.id,
            "patient_id": record.patient_id,
            "patient_name": patient.name if patient else "Unknown",
            "doctor_id": record.created_by,
            "monitoring_type": "doctor" if user_role == "doctor" else "patient",
            "gestational_age": record.gestational_age,
            "start_time": record.start_time,
            "end_time": record.end_time,
            "monitoring_duration": record.monitoring_duration,
            "classification": record.classification,
            "notes": record.notes,
            "doctor_notes": record.doctor_notes,
            "shared_with_doctor": bool(record.shared_with),
            "created_at": record.start_time
        })
    
    return {
        "records": record_list,
        "total_count": total_count,
        "current_page": (skip // limit) + 1 if limit > 0 else 1,
        "total_pages": (total_count + limit - 1) // limit if limit > 0 else 1
    }

@staticmethod
def share_monitoring_with_doctor(db, record_id: int, doctor_id: int, patient_id: int, notes: Optional[str] = None) -> Dict[str, Any]:
    """Share monitoring record with doctor"""
    from app.models.medical import Record, User, Patient
    from app.core.time_utils import get_local_now
    
    # Validate record ownership
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.patient_id == patient_id
    ).first()
    
    if not record:
        raise ValueError("Record not found or access denied")
    
    # Validate doctor
    doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
    if not doctor:
        raise ValueError("Doctor not found")
    
    # Update record with sharing info
    sharing_note = f"Shared with Dr. {doctor.name} on {get_local_now().strftime('%Y-%m-%d %H:%M')}"
    if notes:
        sharing_note += f" - Patient notes: {notes}"
    
    existing_notes = record.doctor_notes or ""
    record.doctor_notes = f"{existing_notes}\n{sharing_note}".strip()
    record.shared_with = doctor_id
    
    db.commit()
    
    return {
        "message": f"Record shared with Dr. {doctor.name}",
        "doctor_name": doctor.name,
        "shared_at": get_local_now()
    }

@staticmethod
def get_doctor_assigned_patients(db, doctor_id: int) -> List[Dict[str, Any]]:
    """Get patients assigned to doctor for monitoring selection"""
    from app.models.medical import DoctorPatientAssociation, Patient, User
    
    query = db.query(DoctorPatientAssociation).join(Patient).filter(
        DoctorPatientAssociation.doctor_id == doctor_id
    )
    
    assignments = query.all()
    
    patient_list = []
    for assignment in assignments:
        patient = db.query(Patient).filter(Patient.id == assignment.patient_id).first()
        if patient:
            user = db.query(User).filter(User.id == patient.patient_id).first()
            patient_list.append({
                "patient_id": patient.id,
                "patient_name": patient.name,
                "assigned_date": assignment.assigned_at.strftime("%Y-%m-%d"),
                "status": "active",
                "contact_info": user.email if user else "No contact info"
            })
    
    return patient_list
```

### STEP 5: IMPLEMENT NEW ENDPOINTS

```python
# REPLACE app/api/v1/endpoints/fetal_monitoring.py dengan:

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.medical import User
from app.services.fetal_monitoring_service import FetalMonitoringService
from app.schemas.fetal_monitoring import (
    ESP32MonitoringRequest,
    ESP32MonitoringResponse, 
    MonitoringHistoryResponse,
    ShareMonitoringRequest,
    ShareMonitoringResponse,
    AssignedPatientsResponse
)
from app.core.security import verify_jwt_token

router = APIRouter()
security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get the current authenticated user."""
    token = credentials.credentials
    try:
        payload = verify_jwt_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user

# NEW: Process ESP32 monitoring data
@router.post("/monitoring/process", response_model=ESP32MonitoringResponse)
async def process_monitoring_data(
    request: ESP32MonitoringRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process ESP32 monitoring data for both doctor and patient"""
    try:
        result = FetalMonitoringService.process_esp32_monitoring(
            db, request, current_user.id, current_user.role.value
        )
        
        return ESP32MonitoringResponse(
            success=True,
            message="Monitoring data processed successfully",
            record_id=result["record_id"],
            classification_result=result["classification_result"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# NEW: Get monitoring history
@router.get("/monitoring/history", response_model=MonitoringHistoryResponse)
async def get_monitoring_history(
    patient_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monitoring history with role-based access"""
    try:
        # Determine access parameters based on user role
        if current_user.role.value == "patient":
            # Patient can only see their own records
            from app.models.medical import Patient
            patient = db.query(Patient).filter(Patient.patient_id == current_user.id).first()
            if not patient:
                raise HTTPException(status_code=404, detail="Patient profile not found")
            patient_id = patient.id
            doctor_id = None
        elif current_user.role.value == "doctor":
            # Doctor can see records of assigned patients
            doctor_id = current_user.id
            # patient_id filter optional for doctors
        else:
            raise HTTPException(status_code=403, detail="Access denied")
        
        result = FetalMonitoringService.get_monitoring_history(
            db, patient_id, doctor_id, current_user.role.value, skip, limit
        )
        
        return MonitoringHistoryResponse(
            success=True,
            data=result["records"],
            total_count=result["total_count"],
            current_page=result["current_page"],
            total_pages=result["total_pages"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# NEW: Share monitoring with doctor
@router.post("/monitoring/share", response_model=ShareMonitoringResponse)
async def share_monitoring(
    request: ShareMonitoringRequest,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Share monitoring record with doctor (patient only)"""
    if current_user.role.value != "patient":
        raise HTTPException(status_code=403, detail="Only patients can share monitoring records")
    
    try:
        # Get patient ID
        from app.models.medical import Patient
        patient = db.query(Patient).filter(Patient.patient_id == current_user.id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient profile not found")
        
        result = FetalMonitoringService.share_monitoring_with_doctor(
            db, request.record_id, request.doctor_id, patient.id, request.notes
        )
        
        return ShareMonitoringResponse(
            success=True,
            message=result["message"],
            shared_at=result["shared_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# NEW: Get assigned patients for doctor
@router.get("/doctors/{doctor_id}/assigned-patients", response_model=AssignedPatientsResponse)
async def get_assigned_patients(
    doctor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patients assigned to doctor for monitoring selection"""
    if current_user.role.value != "doctor" or current_user.id != doctor_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        patients = FetalMonitoringService.get_doctor_assigned_patients(db, doctor_id)
        
        return AssignedPatientsResponse(
            success=True,
            patients=patients
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### STEP 6: UPDATE DOCTOR DASHBOARD

```python
# ADD to app/api/v1/endpoints/doctor_dashboard.py:

# Import new schemas
from app.schemas.fetal_monitoring import AssignedPatientsResponse

# NEW: Get assigned patients for monitoring
@router.get("/doctors/{doctor_id}/monitoring/patients", response_model=AssignedPatientsResponse, tags=["Doctor Dashboard"])
def get_patients_for_monitoring(
    doctor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get patients assigned to doctor for monitoring selection"""
    
    # Check if current user is the doctor or admin
    if current_user.role.value != "doctor" or current_user.id != doctor_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        from app.services.fetal_monitoring_service import FetalMonitoringService
        patients = FetalMonitoringService.get_doctor_assigned_patients(db, doctor_id)
        
        return AssignedPatientsResponse(
            success=True,
            patients=patients
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### STEP 7: TESTING

```bash
# 1. Test new endpoints
python test_new_monitoring_endpoints.py

# 2. Commit changes
git add .
git commit -m "Feature: Rebuild monitoring system with ESP32 integration using records table only"

# 3. Push to production
git push origin main
```

---

## ✅ VERIFICATION CHECKLIST

### Endpoints to Test:
- [ ] `POST /api/v1/fetal-monitoring/monitoring/process` - Process ESP32 data
- [ ] `GET /api/v1/fetal-monitoring/monitoring/history` - Get monitoring history  
- [ ] `POST /api/v1/fetal-monitoring/monitoring/share` - Share with doctor
- [ ] `GET /api/v1/fetal-monitoring/doctors/{doctor_id}/assigned-patients` - Get assigned patients
- [ ] `GET /api/v1/doctor-dashboard/doctors/{doctor_id}/monitoring/patients` - Doctor patient selection

### Database Verification:
- [ ] Records table stores ESP32 monitoring data correctly
- [ ] Classification results saved properly
- [ ] Sharing mechanism works with doctor_notes field
- [ ] Role-based access working correctly

**RESULT**: Simplified monitoring system using only records table! 🎯
