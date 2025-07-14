# Standard library imports
from datetime import datetime, date, timedelta
from typing import List, Optional

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, and_, or_, extract
from pydantic import BaseModel

# Local imports
from app.db.session import SessionLocal
from app.models.medical import Doctor, Patient, User, DoctorPatientAssociation, Record
from app.models.patient_status_history import PatientStatusHistory
from app.api.v1.endpoints.user import get_current_user
from app.core.time_utils import get_local_naive_now, get_local_now

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_doctor(current_user: User = Depends(get_current_user)):
    """Require user to be a doctor"""
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    
    if user_role != "doctor":
        raise HTTPException(status_code=403, detail="Doctor access required")
    
    return current_user

def require_doctor_access(current_user: User = Depends(require_doctor)):
    """Require user to be a doctor (for use in endpoints that check doctor_id separately)"""
    return current_user

# --- Pydantic Models ---

class PatientBasicInfo(BaseModel):
    id: int
    name: str
    email: str
    
    class Config:
        from_attributes = True

class MonitoringRecord(BaseModel):
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    classification: Optional[str] = None
    source: str
    bpm_data: List[dict]
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True

class PatientMonitoringHistoryResponse(BaseModel):
    patient: PatientBasicInfo
    records: List[MonitoringRecord]
    total: int
    limit: int
    offset: int
    
    class Config:
        from_attributes = True

class DoctorInfo(BaseModel):
    id: int
    name: str
    email: str
    
    class Config:
        from_attributes = True

class PatientStats(BaseModel):
    total: int
    active: int
    inactive: int

class RecordStats(BaseModel):
    total: int
    this_month: int
    this_week: int

class ClassificationStats(BaseModel):
    normal: int
    abnormal: int
    irregular: int

class DoctorStatisticsResponse(BaseModel):
    doctor: DoctorInfo
    patients: PatientStats
    records: RecordStats
    classifications: ClassificationStats
    last_activity: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UpdatePatientStatusRequest(BaseModel):
    status: str  # "active", "inactive", "discharged"
    notes: Optional[str] = None

class UpdatePatientStatusResponse(BaseModel):
    status: str
    message: str
    patient: dict
    
    class Config:
        from_attributes = True

# --- Endpoints ---

@router.get("/patients/{patient_id}/monitoring/history", response_model=PatientMonitoringHistoryResponse, tags=["Doctor Dashboard"])
def get_patient_monitoring_history(
    patient_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
):
    """Get monitoring history for a specific patient (doctor access only)"""
    
    # Check if doctor has access to this patient
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    if user_role == "doctor":
        association = db.query(DoctorPatientAssociation).filter(
            and_(
                DoctorPatientAssociation.doctor_id == current_user.id,
                DoctorPatientAssociation.patient_id == patient_id
            )
        ).first()
        if not association:
            raise HTTPException(status_code=403, detail="Patient not assigned to you")
    
    # Get patient basic info
    patient = db.query(Patient).join(User).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get total count
    total = db.query(Record).filter(Record.patient_id == patient_id).count()
    
    # Get records with pagination
    records = db.query(Record).filter(
        Record.patient_id == patient_id
    ).order_by(desc(Record.start_time)).offset(offset).limit(limit).all()
    
    records_data = []
    for record in records:
        records_data.append({
            "id": record.id,
            "start_time": record.start_time,
            "end_time": record.end_time,
            "classification": record.classification,
            "source": record.source.value if record.source else None,
            "bpm_data": record.bpm_data or [],
            "notes": record.notes
        })
    
    return {
        "patient": {
            "id": patient.id,
            "name": patient.user.name,
            "email": patient.user.email
        },
        "records": records_data,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@router.get("/doctors/{doctor_id}/statistics", response_model=DoctorStatisticsResponse, tags=["Doctor Dashboard"])
def get_doctor_statistics(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_access)
):
    """Get comprehensive statistics for a doctor"""
    
    # Check access (doctors can only see their own stats, admins can see any doctor's stats)
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    if user_role == "doctor" and current_user.id != doctor_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get doctor info
    doctor_user = db.query(User).filter(User.id == doctor_id).first()
    if not doctor_user:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Get patient statistics
    total_patients = db.query(DoctorPatientAssociation).filter(
        DoctorPatientAssociation.doctor_id == doctor_id
    ).count()
    
    active_patients = db.query(DoctorPatientAssociation).filter(
        and_(
            DoctorPatientAssociation.doctor_id == doctor_id,
            DoctorPatientAssociation.status == "active"
        )
    ).count()
    
    inactive_patients = total_patients - active_patients
    
    # Get records statistics
    patient_ids = db.query(DoctorPatientAssociation.patient_id).filter(
        DoctorPatientAssociation.doctor_id == doctor_id
    ).subquery()
    
    total_records = db.query(Record).filter(Record.patient_id.in_(patient_ids)).count()
    
    # This month records
    current_month = datetime.now().month
    current_year = datetime.now().year
    this_month_records = db.query(Record).filter(
        and_(
            Record.patient_id.in_(patient_ids),
            extract('month', Record.start_time) == current_month,
            extract('year', Record.start_time) == current_year
        )
    ).count()
    
    # This week records  
    week_ago = datetime.now() - timedelta(days=7)
    this_week_records = db.query(Record).filter(
        and_(
            Record.patient_id.in_(patient_ids),
            Record.start_time >= week_ago
        )
    ).count()
    
    # Classification statistics
    normal_count = db.query(Record).filter(
        and_(
            Record.patient_id.in_(patient_ids),
            Record.classification == "normal"
        )
    ).count()
    
    abnormal_count = db.query(Record).filter(
        and_(
            Record.patient_id.in_(patient_ids),
            Record.classification.in_(["abnormal", "bradycardia", "tachycardia"])
        )
    ).count()
    
    irregular_count = db.query(Record).filter(
        and_(
            Record.patient_id.in_(patient_ids),
            Record.classification == "irregular"
        )
    ).count()
    
    # Last activity
    last_record = db.query(Record).filter(
        Record.patient_id.in_(patient_ids)
    ).order_by(desc(Record.start_time)).first()
    
    return {
        "doctor": {
            "id": doctor_user.id,
            "name": doctor_user.name,
            "email": doctor_user.email
        },
        "patients": {
            "total": total_patients,
            "active": active_patients,
            "inactive": inactive_patients
        },
        "records": {
            "total": total_records,
            "this_month": this_month_records,
            "this_week": this_week_records
        },
        "classifications": {
            "normal": normal_count,
            "abnormal": abnormal_count,
            "irregular": irregular_count
        },
        "last_activity": last_record.start_time if last_record else None
    }

@router.patch("/doctors/{doctor_id}/patients/{patient_id}/status", response_model=UpdatePatientStatusResponse, tags=["Doctor Dashboard"])
def update_patient_status(
    doctor_id: int,
    patient_id: int,
    request: UpdatePatientStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_access)
):
    """Update patient status for a doctor-patient relationship"""
    
    # Check access (doctors can only update their own patients, admins can update any)
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    if user_role == "doctor" and current_user.id != doctor_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Find the association
    association = db.query(DoctorPatientAssociation).filter(
        and_(
            DoctorPatientAssociation.doctor_id == doctor_id,
            DoctorPatientAssociation.patient_id == patient_id
        )
    ).first()
    
    if not association:
        raise HTTPException(status_code=404, detail="Doctor-patient association not found")
    
    # Get patient info for response
    patient = db.query(Patient).join(User).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Store old status for history
    old_status = association.status
    
    # Update the association
    association.status = request.status
    association.note = request.notes
    association.updated_at = get_local_naive_now()
    
    # Create status history record
    status_history = PatientStatusHistory(
        doctor_id=doctor_id,
        patient_id=patient_id,
        old_status=old_status,
        new_status=request.status,
        notes=request.notes,
        changed_by=current_user.id,
        changed_at=get_local_naive_now()
    )
    db.add(status_history)
    
    db.commit()
    
    # Build patient info for response
    patient_info = {
        "id": patient.id,
        "name": patient.user.name,
        "email": patient.user.email,
        "age": patient.age,
        "gender": patient.gender,
        "phone": patient.phone,
        "address": patient.address,
        "photo_url": patient.user.photo_url,
        "assignment_date": association.assigned_at,
        "status": association.status or "active",
        "notes": association.note,
        "last_record_date": None,
        "total_records": None,
        "status_updated_at": association.updated_at
    }

    return {
        "status": "success",
        "message": "Patient status updated successfully",
        "patient": patient_info
    }

@router.get("/doctors/{doctor_id}/patients/{patient_id}/status-history", tags=["Doctor Dashboard"])
def get_patient_status_history(
    doctor_id: int,
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_access)
):
    """Get status change history for a patient under a doctor"""
    
    # Authorization: only assigned doctor or admin
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    if user_role == "doctor" and current_user.id != doctor_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    history = db.query(PatientStatusHistory).filter(
        PatientStatusHistory.doctor_id == doctor_id,
        PatientStatusHistory.patient_id == patient_id
    ).order_by(PatientStatusHistory.changed_at.desc()).all()
    
    data = [
        {
            "old_status": h.old_status,
            "new_status": h.new_status,
            "notes": h.notes,
            "changed_by": h.changed_by_user.name if h.changed_by_user else None,
            "changed_at": h.changed_at
        }
        for h in history
    ]
    
    return {"status": "success", "data": data}
