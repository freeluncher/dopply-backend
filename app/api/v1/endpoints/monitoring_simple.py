from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.models.medical import User
from app.services.monitoring_simple import MonitoringService
from app.schemas.fetal_monitoring import (
    MonitoringRequest, MonitoringResponse, 
    ShareMonitoringRequest, ShareMonitoringResponse,
    MonitoringHistoryResponse, AddPatientRequest, AddPatientResponse,
    PatientListResponse, NotificationListResponse,
    DoctorVerificationRequest, DoctorVerificationResponse
)
from app.core.security import verify_jwt_token

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get the current authenticated user."""
    try:
        payload = verify_jwt_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# 1. Submit monitoring result (patient/doctor)
@router.post("/submit", response_model=MonitoringResponse)
async def submit_monitoring(
    request: MonitoringRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit hasil monitoring (bisa patient atau doctor)"""
    try:
        result = MonitoringService.save_monitoring_record(db, request, current_user.id)
        return MonitoringResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 2. Get monitoring history (patient/doctor)
@router.get("/history", response_model=MonitoringHistoryResponse)
async def get_monitoring_history(
    patient_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ambil riwayat monitoring berdasarkan role"""
    try:
        result = MonitoringService.get_monitoring_history(
            db, current_user.id, current_user.role.value, patient_id, skip, limit
        )
        return MonitoringHistoryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 3. Share monitoring with doctor (patient only)
@router.post("/share", response_model=ShareMonitoringResponse)
async def share_monitoring(
    request: ShareMonitoringRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pasien membagikan hasil monitoring ke dokter"""
    if current_user.role.value != "patient":
        raise HTTPException(status_code=403, detail="Only patients can share monitoring")
    
    try:
        # Get patient ID
        from app.models.medical import Patient
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient profile not found")
        
        result = MonitoringService.share_monitoring_with_doctor(
            db, request.record_id, request.doctor_id, patient.id, request.notes
        )
        
        return ShareMonitoringResponse(
            success=True,
            message=result["message"],
            notification_id=result.get("notification_id")
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 4. Doctor endpoints
@router.get("/patients", response_model=PatientListResponse)
async def get_doctor_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dokter melihat list pasiennya"""
    if current_user.role.value != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can access this")
    
    try:
        patients = MonitoringService.get_doctor_patients(db, current_user.id)
        return PatientListResponse(
            patients=patients,
            total_count=len(patients)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/patients/add", response_model=AddPatientResponse)
async def add_patient(
    request: AddPatientRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dokter menambahkan pasien berdasarkan email"""
    if current_user.role.value != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can add patients")
    
    try:
        result = MonitoringService.add_patient_to_doctor(
            db, current_user.id, request.patient_email, request.notes
        )
        return AddPatientResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 5. Notifications
@router.get("/notifications", response_model=NotificationListResponse)
async def get_notifications(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dokter melihat notifikasi"""
    if current_user.role.value != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can access notifications")
    
    try:
        result = MonitoringService.get_doctor_notifications(db, current_user.id, skip, limit)
        return NotificationListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/notifications/read/{notification_id}")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Tandai notifikasi sebagai sudah dibaca"""
    if current_user.role.value != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can mark notifications")
    
    try:
        result = MonitoringService.mark_notification_read(db, notification_id, current_user.id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 6. Admin endpoints
@router.post("/admin/verify-doctor", response_model=DoctorVerificationResponse)
async def verify_doctor(
    request: DoctorVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin memverifikasi dokter"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admin can verify doctors")
    
    try:
        result = MonitoringService.verify_doctor(db, current_user.id, request.doctor_id)
        return DoctorVerificationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
