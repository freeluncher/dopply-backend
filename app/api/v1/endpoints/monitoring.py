from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import json

from app.db.session import get_db
from app.models.medical import User, Patient, Record, Notification, DoctorPatientAssociation, UserRole, NotificationStatus
from app.core.dependencies import get_current_user
from app.services.monitoring_simple import MonitoringService
from app.schemas.fetal_monitoring import (
    MonitoringRequest, MonitoringResponse, 
    ShareMonitoringRequest, ShareMonitoringResponse,
    MonitoringHistoryResponse, AddPatientRequest, AddPatientResponse,
    PatientListResponse, NotificationListResponse,
    DoctorVerificationRequest, DoctorVerificationResponse,
    ClassifyRequest, ClassifyResponse
)
from app.schemas.common import (
    MonitoringResultRequest, MonitoringResultResponse,
    MonitoringHistoryResponse as CommonMonitoringHistoryResponse
)
from app.utils.bpm_calculator import (
    calculate_bpm_statistics, calculate_duration_seconds, 
    is_shared_with_doctor, format_record_for_api
)

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

# ============= CLASSIFICATION & SUBMIT ENDPOINTS =============

@router.post("/classify", response_model=ClassifyResponse)
async def classify_monitoring(request: ClassifyRequest):
    """Klasifikasi BPM tanpa simpan ke database"""
    classification = MonitoringService.classify_bpm(request.bpm_data, request.gestational_age)
    average_bpm = sum(request.bpm_data) / len(request.bpm_data) if request.bpm_data else 0
    return ClassifyResponse(classification=classification, average_bpm=average_bpm)

@router.post("/submit", response_model=MonitoringResponse)
async def submit_monitoring(
    request: MonitoringRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit hasil monitoring (legacy endpoint - uses service layer)"""
    try:
        result = MonitoringService.save_monitoring_record(db, request, current_user.id)
        return MonitoringResponse(**result)
    except Exception as e:
        import logging
        logger = logging.getLogger("monitoring_submit")
        err_msg = str(e)
        if hasattr(e, "args") and e.args:
            err_msg = str(e.args[0])
        logger.error(f"Submit monitoring error: {err_msg}")
        raise HTTPException(status_code=400, detail=err_msg)

@router.post("/results", response_model=MonitoringResultResponse)
async def save_monitoring_result(
    request: MonitoringResultRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save monitoring result (frontend requirements endpoint)"""
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == request.patientId).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Authorization check
    if current_user.role.value == "patient":
        if patient.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role.value not in ["doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Parse timestamp
    try:
        timestamp = datetime.fromisoformat(request.timestamp.replace('Z', '+00:00'))
    except:
        timestamp = datetime.now()
    
    # Create record using service
    classification = MonitoringService.classify_bpm_simple(request.avgBpm)
    
    record = Record(
        patient_id=request.patientId,
        doctor_id=current_user.id if current_user.role.value == "doctor" else None,
        created_by=current_user.id,
        source="frontend",
        start_time=timestamp,
        end_time=timestamp,
        bpm_data=json.dumps(request.dataPoints),
        classification=classification,
        monitoring_duration=request.duration / 60.0,  # Konversi detik ke menit
        gestational_age=None  # Bisa ditambahkan ke request jika diperlukan
    )
    
    db.add(record)
    db.commit()
    db.refresh(record)
    
    # Hitung statistik dari data yang disimpan
    bpm_stats = calculate_bpm_statistics(record.bpm_data)
    duration_sec = calculate_duration_seconds(record.start_time, record.end_time, record.monitoring_duration)
    
    return MonitoringResultResponse(
        success=True,
        data={
            "id": record.id,
            "patientId": record.patient_id,
            "avgBpm": bpm_stats["avg_bpm"],
            "minBpm": bpm_stats["min_bpm"],
            "maxBpm": bpm_stats["max_bpm"],
            "duration": duration_sec,
            "classification": record.classification,
            "sharedWithDoctor": is_shared_with_doctor(record.shared_with),
            "timestamp": timestamp.isoformat(),
            "createdAt": record.start_time.isoformat()
        },
        message="Monitoring result saved successfully"
    )

# ============= HISTORY ENDPOINTS =============

@router.get("/history")
async def get_monitoring_history(
    patient_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monitoring history (unified endpoint for both legacy and new frontend)"""
    import logging
    logger = logging.getLogger("monitoring_history")
    logger.info(f"Accessed /monitoring/history by user_id={current_user.id}, role={current_user.role.value}, patient_id={patient_id}")
    
    try:
        # Use service layer for consistent behavior
        result = MonitoringService.get_monitoring_history(
            db, current_user.id, current_user.role.value, patient_id, skip, limit
        )
        records = result.get("records", [])
        
        # Return format compatible with both frontend expectations
        return {
            "success": True,
            "data": {
                "results": records if isinstance(records, list) else [],
                "pagination": {
                    "total": len(records) if records else 0,
                    "limit": limit,
                    "offset": skip,
                    "hasMore": len(records) == limit if records else False
                }
            },
            "status": 200
        }
    except Exception as e:
        logger.error(f"Error in /monitoring/history: {e}")
        return {
            "success": False, 
            "data": {"results": [], "pagination": {"total": 0, "limit": limit, "offset": skip, "hasMore": False}}, 
            "status": 401, 
            "message": str(e)
        }

@router.get("/doctor-history", response_model=CommonMonitoringHistoryResponse)
async def get_doctor_monitoring_history(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monitoring history for doctor - all assigned patients"""
    if current_user.role.value != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can access this endpoint")
    
    # Get all patients assigned to this doctor
    assigned_patients = db.query(DoctorPatientAssociation).filter(
        DoctorPatientAssociation.doctor_id == current_user.id
    ).all()
    
    patient_ids = [assoc.patient_id for assoc in assigned_patients]
    
    # Get monitoring records for all assigned patients
    query = db.query(Record).filter(Record.patient_id.in_(patient_ids))
    total = query.count()
    records = query.offset(skip).limit(limit).all()
    
    # Format response using utility function
    results = []
    for record in records:
        patient = db.query(Patient).filter(Patient.id == record.patient_id).first()
        formatted_record = format_record_for_api(record, patient.name if patient else "Unknown")
        # Tambahkan doctor info
        formatted_record.update({
            "doctorId": current_user.id,
            "doctorName": current_user.name
        })
        results.append(formatted_record)
    
    return CommonMonitoringHistoryResponse(
        success=True,
        data={
            "results": results,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": skip,
                "hasMore": skip + len(results) < total
            }
        },
        message="Doctor monitoring history retrieved successfully"
    )

# ============= SHARING ENDPOINTS =============

@router.post("/share", response_model=ShareMonitoringResponse)
async def share_monitoring(
    request: ShareMonitoringRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Share monitoring with doctor (unified endpoint)"""
    try:
        # Cari record yang akan dishare
        record = db.query(Record).filter(Record.id == request.record_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Monitoring record not found")
            
        # Authorization check - hanya patient owner atau doctor yang bisa share
        if current_user.role.value == "patient":
            patient = db.query(Patient).filter(Patient.id == record.patient_id).first()
            if not patient or patient.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied")
        elif current_user.role.value not in ["doctor", "admin"]:
            raise HTTPException(status_code=403, detail="Access denied")
            
        # Cari dokter tujuan
        doctor = db.query(User).filter(
            User.id == request.doctor_id, 
            User.role == UserRole.doctor
        ).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
            
        # Update record dengan shared_with
        record.shared_with = request.doctor_id
        db.commit()
        
        # Buat notifikasi
        patient = db.query(Patient).filter(Patient.id == record.patient_id).first()
        notification = Notification(
            from_patient_id=record.patient_id,
            to_doctor_id=request.doctor_id,
            record_id=record.id,
            message=f"Monitoring result shared by {patient.name if patient else 'Patient'}",
            status=NotificationStatus.unread
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        return ShareMonitoringResponse(
            success=True,
            message=f"Monitoring result shared with Dr. {doctor.name}",
            notification_id=notification.id
        )
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger("monitoring_share")
        logger.error(f"Share monitoring error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ============= PATIENT MANAGEMENT ENDPOINTS =============

@router.get("/patients", response_model=PatientListResponse)
async def get_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patient list for doctor"""
    try:
        result = MonitoringService.get_doctor_patients(db, current_user.id, current_user.role.value)
        return PatientListResponse(**result)
    except Exception as e:
        import logging
        logger = logging.getLogger("monitoring_patients")
        logger.error(f"Get patients error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/patients/add", response_model=AddPatientResponse)
async def add_patient(
    request: AddPatientRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add patient to doctor (doctor only)"""
    try:
        result = MonitoringService.add_patient_to_doctor(db, request, current_user.id, current_user.role.value)
        return AddPatientResponse(**result)
    except Exception as e:
        import logging
        logger = logging.getLogger("monitoring_add_patient")
        logger.error(f"Add patient error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ============= NOTIFICATION ENDPOINTS =============

@router.get("/notifications", response_model=NotificationListResponse)
async def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notifications for current user"""
    try:
        result = MonitoringService.get_user_notifications(db, current_user.id)
        return NotificationListResponse(**result)
    except Exception as e:
        import logging
        logger = logging.getLogger("monitoring_notifications")
        logger.error(f"Get notifications error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/notifications/read/{notification_id}")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    try:
        result = MonitoringService.mark_notification_read(db, notification_id, current_user.id)
        return result
    except Exception as e:
        import logging
        logger = logging.getLogger("monitoring_notification_read")
        logger.error(f"Mark notification read error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ============= ADMIN ENDPOINTS =============

@router.post("/admin/verify-doctor", response_model=DoctorVerificationResponse)
async def verify_doctor(
    request: DoctorVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin verify doctor"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        result = MonitoringService.verify_doctor(db, request.doctor_id, current_user.id)
        return DoctorVerificationResponse(**result)
    except Exception as e:
        import logging
        logger = logging.getLogger("monitoring_verify_doctor")
        logger.error(f"Verify doctor error: {e}")
        raise HTTPException(status_code=400, detail=str(e))