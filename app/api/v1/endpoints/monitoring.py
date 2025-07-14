# Standard library imports
from datetime import datetime
from typing import List, Optional

# Third-party imports
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Local imports
from app.db.session import SessionLocal
from app.models.medical import Record, Patient, User, Doctor, DoctorPatientAssociation
from app.services.monitoring_service import MonitoringService
from app.core.security import verify_jwt_token
from app.core.time_utils import get_local_naive_now

router = APIRouter()
security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic Models ---
class MonitoringRequest(BaseModel):
    patient_id: int
    bpm_data: List[int]
    doctor_note: Optional[str] = None
    doctor_id: Optional[int] = None

class MonitoringResponse(BaseModel):
    patient_id: int
    bpm_data: List[int]
    classification: str
    abnormal_type: Optional[str] = None
    doctor_note: Optional[str] = None
    start_time: datetime
    end_time: datetime
    record_id: int

class BPMDataPoint(BaseModel):
    time: int
    bpm: int

class ClassifyBPMRequest(BaseModel):
    bpm_data: List[BPMDataPoint]

class ClassifyBPMResponse(BaseModel):
    result: str
    classification: str

class MonitoringRecordBPMData(BaseModel):
    time: int
    bpm: int

class MonitoringRecordRequest(BaseModel):
    patient_id: int
    doctor_id: int
    start_time: datetime
    end_time: datetime
    bpm_data: List[MonitoringRecordBPMData]
    result: str
    classification: str
    doctor_note: Optional[str] = None

class PatientMonitoringBPMData(BaseModel):
    time: int
    bpm: int

class PatientMonitoringRequest(BaseModel):
    patient_id: int
    bpm_data: List[PatientMonitoringBPMData]
    classification: Optional[str] = None
    monitoring_result: Optional[str] = None

class DoctorAssignmentInfo(BaseModel):
    doctor_id: Optional[int] = None
    doctor_name: Optional[str] = None
    doctor_email: Optional[str] = None
    assignment_date: Optional[datetime] = None
    assignment_status: Optional[str] = None
    assignment_notes: Optional[str] = None

    class Config:
        from_attributes = True

class PatientMonitoringHistoryItem(BaseModel):
    id: int
    created_at: datetime
    monitoring_result: Optional[str] = None
    classification: Optional[str] = None
    bpm_data: List[dict]
    source: Optional[str] = None
    doctor_assignment: Optional[DoctorAssignmentInfo] = None

    class Config:
        from_attributes = True

class ShareMonitoringRequest(BaseModel):
    monitoring_id: int
    doctor_id: int

class ShareMonitoringResponse(BaseModel):
    success: bool
    message: str

class DoctorListItem(BaseModel):
    id: int
    name: str
    email: str
    is_valid: Optional[bool] = None
    email: str
    is_valid: Optional[bool] = None

    class Config:
        orm_mode = True

# --- Dependency for current patient ---
def get_current_patient(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get the current user and ensure they are a patient."""
    token = credentials.credentials
    try:
        payload = verify_jwt_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user or (hasattr(user.role, 'value') and user.role.value != "patient") and (str(user.role) != "patient"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Patient access required")
    return user

# --- Dependency for current doctor or patient ---
def get_current_doctor_or_patient(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get the current user and ensure they are a doctor or patient."""
    token = credentials.credentials
    try:
        payload = verify_jwt_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user or (hasattr(user.role, 'value') and user.role.value not in ["doctor", "patient"]) and (str(user.role) not in ["doctor", "patient"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor or patient access required")
    return user

# --- Endpoints ---
from fastapi import Request

@router.post("/monitoring", response_model=MonitoringResponse, status_code=status.HTTP_201_CREATED, tags=["Medical Records"])
async def send_monitoring_result(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_doctor_or_patient)):
    """Process and store monitoring result from doctor."""
    import logging
    logger = logging.getLogger("uvicorn")
    raw_body = await request.json()
    logger.info(f"[MONITORING_ENDPOINT] RAW BODY: {raw_body}")
    # parse ke Pydantic model
    req = MonitoringRequest(**raw_body)
    # Fallback: ambil doctor_id dari raw_body jika tidak ada di model
    doctor_id = getattr(req, "doctor_id", raw_body.get("doctor_id", None))
    logger.info(f"[MONITORING_ENDPOINT] Payload diterima: {req.dict()}")
    logger.info(f"[MONITORING_ENDPOINT] doctor_id type: {type(doctor_id)}, value: {doctor_id}")
    try:
        result = MonitoringService.process_monitoring_result(
            db,
            patient_id=req.patient_id,
            bpm_data=req.bpm_data,
            doctor_note=req.doctor_note,
            doctor_id=doctor_id
        )
        return MonitoringResponse(**result)
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

@router.post("/classify_bpm", response_model=ClassifyBPMResponse, tags=["Medical Records"])
def classify_bpm(req: ClassifyBPMRequest, user: User = Depends(get_current_doctor_or_patient)):
    """Classify BPM data points."""
    try:
        bpm_data = [point.dict() for point in req.bpm_data]
        result = MonitoringService.classify_bpm(bpm_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/monitoring_record", status_code=status.HTTP_201_CREATED, tags=["Medical Records"])
def save_monitoring_record(req: MonitoringRecordRequest, db: Session = Depends(get_db), user: User = Depends(get_current_doctor_or_patient)):
    """Save a monitoring record from doctor."""
    try:
        result = MonitoringService.save_monitoring_record(db, req)
        return result
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

@router.post("/patient/monitoring", status_code=status.HTTP_201_CREATED, tags=["Medical Records"])
def save_patient_monitoring_result(req: PatientMonitoringRequest, db: Session = Depends(get_db), user: User = Depends(get_current_doctor_or_patient)):
    """Save monitoring result submitted by patient."""
    # Validasi: pasien hanya boleh simpan hasil untuk dirinya sendiri
    patient = db.query(Patient).filter(Patient.user_id == user.id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found or not authorized")
    if req.patient_id != patient.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only save monitoring for yourself.")
    # Gunakan zona waktu lokal Indonesia (WIB)
    start_time = get_local_naive_now()
    record = Record(
        patient_id=patient.id,
        doctor_id=None,  # No doctor, self-monitoring
        source="self",  # Use the correct enum value for DB
        bpm_data=[{"time": d.time, "bpm": d.bpm} for d in req.bpm_data],
        start_time=start_time,
        end_time=None,
        classification=req.classification,
        notes=req.monitoring_result
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"message": "Monitoring result saved", "record_id": record.id}

@router.get("/patient/monitoring/history", response_model=List[PatientMonitoringHistoryItem], tags=["Medical Records"])
def get_patient_monitoring_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_doctor_or_patient)):
    """Get all monitoring records for the logged-in patient with doctor assignment information."""
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    
    # Get records with doctor information
    records = db.query(Record).filter(Record.patient_id == patient.id).order_by(Record.id.desc()).all()
    result = []
    
    for r in records:
        # Initialize doctor assignment info
        doctor_assignment = None
        
        # If record has a doctor, get assignment info
        if r.doctor_id:
            # Get doctor user info
            doctor_user = db.query(User).filter(User.id == r.doctor_id).first()
            
            # Get doctor-patient association info
            association = db.query(DoctorPatientAssociation).filter(
                DoctorPatientAssociation.doctor_id == r.doctor_id,
                DoctorPatientAssociation.patient_id == patient.id
            ).first()
            
            if doctor_user:
                doctor_assignment = DoctorAssignmentInfo(
                    doctor_id=doctor_user.id,
                    doctor_name=doctor_user.name,
                    doctor_email=doctor_user.email,
                    assignment_date=association.assigned_at if association else None,
                    assignment_status=association.status if association else None,
                    assignment_notes=association.note if association else None
                )
        
        # Build the history item
        result.append(PatientMonitoringHistoryItem(
            id=r.id,
            created_at=getattr(r, "created_at", getattr(r, "start_time", None)),
            monitoring_result=getattr(r, "notes", None),
            classification=getattr(r, "classification", None),
            bpm_data=getattr(r, "bpm_data", []),
            source=r.source.value if hasattr(r.source, 'value') else str(r.source),
            doctor_assignment=doctor_assignment
        ))
    
    return result

@router.post("/patient/share_monitoring", response_model=ShareMonitoringResponse, tags=["Medical Records"])
def share_monitoring_to_doctor(
    req: ShareMonitoringRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_patient)
):
    # Ambil patient yang sesuai dengan user login
    patient = db.query(Patient).filter(Patient.user_id == user.id).first()
    if not patient:
        return ShareMonitoringResponse(success=False, message="Patient not found or not authorized.")
    # Validasi monitoring_id milik pasien
    record = db.query(Record).filter(Record.id == req.monitoring_id, Record.patient_id == patient.id).first()
    if not record:
        return ShareMonitoringResponse(success=False, message="Monitoring_id tidak valid atau bukan milik Anda.")
    # Validasi doctor_id
    doctor = db.query(User).filter(User.id == req.doctor_id, User.role == "doctor").first()
    if not doctor:
        return ShareMonitoringResponse(success=False, message="Dokter tidak ditemukan.")
    # Update kolom doctor_id pada record yang dibagikan
    record.doctor_id = req.doctor_id
    # (Opsional) juga bisa tetap simpan relasi sharing jika ada field khusus
    record.shared_with = req.doctor_id
    db.commit()
    # (Opsional) Kirim notifikasi ke dokter di sini
    return ShareMonitoringResponse(success=True, message="Hasil monitoring berhasil dibagikan ke dokter.")

@router.get("/doctor/list", response_model=List[DoctorListItem], tags=["User Management"])
def get_doctor_list(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_patient)
):
    """Get list of available doctors for patient to share monitoring results."""
    doctors = db.query(User).filter(User.role == "doctor").all()
    result = []
    for doctor in doctors:
        doctor_profile = db.query(Doctor).filter(Doctor.doctor_id == doctor.id).first()
        is_valid = doctor_profile.is_valid if doctor_profile else None
        result.append(DoctorListItem(
            id=doctor.id,
            name=doctor.name,
            email=doctor.email,
            is_valid=is_valid
        ))
    return result
