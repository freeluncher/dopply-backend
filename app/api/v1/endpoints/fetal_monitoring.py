# NEW ESP32 Fetal Monitoring Endpoints - SIMPLIFIED
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
    AssignedPatientsResponse,
    FetalBPMClassificationRequest,
    FetalBPMClassificationResponse
)
from app.core.security import verify_jwt_token

router = APIRouter(prefix="/fetal-monitoring", tags=["Fetal Monitoring"])
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
        
        result = FetalMonitoringService.get_monitoring_history_new(
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
        
        result = FetalMonitoringService.share_monitoring_with_doctor_new(
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

# KEEP: BPM Classification endpoint for backward compatibility
@router.post("/classify-bpm", response_model=FetalBPMClassificationResponse)
async def classify_fetal_bpm(
    request: FetalBPMClassificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Classify fetal BPM data (backward compatibility)"""
    try:
        result = FetalMonitoringService.classify_fetal_bpm(
            request.bpm_readings,
            request.gestational_age
        )
        
        return FetalBPMClassificationResponse(
            success=True,
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
