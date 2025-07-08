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
    print(f"[DEBUG] require_doctor - user role: {current_user.role}")
    
    # Handle enum vs string comparison
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    
    if user_role != "doctor":
        print(f"[DEBUG] Access denied - user role '{user_role}' is not 'doctor'")
        raise HTTPException(status_code=403, detail="Doctor access required")
    
    print(f"[DEBUG] Doctor access granted for user {current_user.id}")
    return current_user

def require_doctor_access(current_user: User = Depends(require_doctor)):
    """Require user to be a doctor (for use in endpoints that check doctor_id separately)"""
    return current_user

# --- Pydantic Models ---

class LastRecordInfo(BaseModel):
    id: int
    start_time: datetime
    classification: Optional[str] = None
    source: str
    
    class Config:
        from_attributes = True

class PatientDetailResponse(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    photo_url: Optional[str] = None
    created_at: datetime
    last_record: Optional[LastRecordInfo] = None
    total_records: int
    assignment_date: datetime
    status: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True

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

class EnhancedPatientInfo(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    address: Optional[str] = None
    photo_url: Optional[str] = None
    assignment_date: datetime
    status: Optional[str] = None
    notes: Optional[str] = None
    last_record_date: Optional[datetime] = None
    total_records: int

    class Config:
        from_attributes = True

class EnhancedDoctorPatientsResponse(BaseModel):
    patients: List[EnhancedPatientInfo]
    total: int
    limit: int
    offset: int
    
    class Config:
        from_attributes = True

# --- Endpoints ---

@router.get("/patients/{patient_id}", response_model=PatientDetailResponse, tags=["Doctor Dashboard"])
def get_patient_details(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
):
    """Get detailed patient information for doctor dashboard"""
    
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
    
    # Get patient with user info
    patient = db.query(Patient).options(joinedload(Patient.user)).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get last record
    last_record = db.query(Record).filter(Record.patient_id == patient_id).order_by(desc(Record.start_time)).first()
    
    # Get total records count
    total_records = db.query(Record).filter(Record.patient_id == patient_id).count()
    
    # Get association info
    association = db.query(DoctorPatientAssociation).filter(
        DoctorPatientAssociation.patient_id == patient_id
    ).first()
    
    # Build response
    response_data = {
        "id": patient.id,
        "name": patient.user.name,
        "email": patient.user.email,
        "age": patient.age,
        "gender": patient.gender,
        "phone": patient.phone,
        "photo_url": patient.user.photo_url,
        "created_at": patient.user.created_at,
        "total_records": total_records,
        "assignment_date": association.assigned_at if association else patient.user.created_at,
        "status": association.status if association else "active",
        "notes": association.note if association else None
    }
    
    if last_record:
        response_data["last_record"] = {
            "id": last_record.id,
            "start_time": last_record.start_time,
            "classification": last_record.classification,
            "source": last_record.source
        }
    
    return response_data

@router.get("/patients/{patient_id}/monitoring/history", response_model=PatientMonitoringHistoryResponse, tags=["Doctor Dashboard"])
def get_patient_monitoring_history(
    patient_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
):
    """Get monitoring history for specific patient"""
    
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
    
    # Get patient info
    patient = db.query(Patient).options(joinedload(Patient.user)).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Build query with filters
    query = db.query(Record).filter(Record.patient_id == patient_id)
    
    if date_from:
        query = query.filter(func.date(Record.start_time) >= date_from)
    if date_to:
        query = query.filter(func.date(Record.start_time) <= date_to)
    
    # Get total count
    total = query.count()
    
    # Get records with pagination
    records = query.order_by(desc(Record.start_time)).offset(offset).limit(limit).all()
    
    return {
        "patient": {
            "id": patient.id,
            "name": patient.user.name,
            "email": patient.user.email
        },
        "records": [
            {
                "id": record.id,
                "start_time": record.start_time,
                "end_time": record.end_time,
                "classification": record.classification,
                "source": record.source,
                "bpm_data": record.bpm_data or [],
                "notes": record.notes
            }
            for record in records
        ],
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
    """Get aggregated statistics for doctor dashboard"""
    
    print(f"[DEBUG] get_doctor_statistics - requested doctor_id: {doctor_id}")
    print(f"[DEBUG] get_doctor_statistics - current_user.id: {current_user.id}")
    print(f"[DEBUG] get_doctor_statistics - current_user.role: {current_user.role}")
    print(f"[DEBUG] get_doctor_statistics - current_user doctor_id: {getattr(current_user, 'doctor_id', None)}")
    
    # Check access (doctors can only see their own stats, admins can see all)
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    
    if user_role == "doctor" and current_user.id != doctor_id:
        print(f"[DEBUG] Access denied - doctor {current_user.id} trying to access stats for doctor {doctor_id}")
        raise HTTPException(status_code=403, detail="Access denied")
    
    print(f"[DEBUG] Access granted for doctor statistics")
    
    # Get doctor info - use enum comparison for role
    from app.models.medical import UserRole
    doctor = db.query(User).filter(and_(User.id == doctor_id, User.role == UserRole.doctor)).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Get patient statistics
    total_patients = db.query(DoctorPatientAssociation).filter(DoctorPatientAssociation.doctor_id == doctor_id).count()
    active_patients = db.query(DoctorPatientAssociation).filter(
        and_(
            DoctorPatientAssociation.doctor_id == doctor_id,
            or_(DoctorPatientAssociation.status == "active", DoctorPatientAssociation.status.is_(None))
        )
    ).count()
    inactive_patients = total_patients - active_patients
    
    # Get patient IDs for this doctor
    patient_ids_subquery = db.query(DoctorPatientAssociation.patient_id).filter(
        DoctorPatientAssociation.doctor_id == doctor_id
    ).subquery()
    
    # Get record statistics
    total_records = db.query(Record).filter(Record.patient_id.in_(patient_ids_subquery)).count()
    
    current_local = get_local_naive_now()
    current_month = current_local.month
    current_year = current_local.year
    records_this_month = db.query(Record).filter(
        and_(
            Record.patient_id.in_(patient_ids_subquery),
            extract('month', Record.start_time) == current_month,
            extract('year', Record.start_time) == current_year
        )
    ).count()
    
    # Get records from last 7 days
    week_ago = current_local - timedelta(days=7)
    records_this_week = db.query(Record).filter(
        and_(
            Record.patient_id.in_(patient_ids_subquery),
            Record.start_time >= week_ago
        )
    ).count()
    
    # Get classification statistics
    classifications = db.query(
        Record.classification,
        func.count(Record.id)
    ).filter(
        Record.patient_id.in_(patient_ids_subquery)
    ).group_by(Record.classification).all()
    
    classification_stats = {"normal": 0, "abnormal": 0, "irregular": 0}
    for classification, count in classifications:
        if classification in classification_stats:
            classification_stats[classification] = count
    
    # Get last activity
    last_record = db.query(Record).filter(
        Record.patient_id.in_(patient_ids_subquery)
    ).order_by(desc(Record.start_time)).first()
    
    return {
        "doctor": {
            "id": doctor.id,
            "name": doctor.name,
            "email": doctor.email
        },
        "patients": {
            "total": total_patients,
            "active": active_patients,
            "inactive": inactive_patients
        },
        "records": {
            "total": total_records,
            "this_month": records_this_month,
            "this_week": records_this_week
        },
        "classifications": classification_stats,
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
    """Update patient status and notes"""
    
    print(f"[DEBUG] update_patient_status - requested doctor_id: {doctor_id}")
    print(f"[DEBUG] update_patient_status - current_user.id: {current_user.id}")
    print(f"[DEBUG] update_patient_status - current_user.role: {current_user.role}")
    
    # Check access (doctors can only update their own patients, admins can update any)
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    
    if user_role == "doctor" and current_user.id != doctor_id:
        print(f"[DEBUG] Access denied - doctor {current_user.id} trying to update patient for doctor {doctor_id}")
        raise HTTPException(status_code=403, detail="Access denied")
    
    print(f"[DEBUG] Access granted for patient status update")
    
    # Validate status
    valid_statuses = ["active", "inactive", "discharged"]
    if request.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    # Get association
    association = db.query(DoctorPatientAssociation).filter(
        and_(
            DoctorPatientAssociation.doctor_id == doctor_id,
            DoctorPatientAssociation.patient_id == patient_id
        )
    ).first()
    
    if not association:
        raise HTTPException(status_code=404, detail="Patient not assigned to doctor")
    
    # Get patient info
    patient = db.query(Patient).options(joinedload(Patient.user)).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Validate allowed status transitions
    old_status = association.status or "active"
    new_status = request.status
    if old_status == "discharged" and new_status != "discharged":
        raise HTTPException(status_code=400, detail="Cannot change status from 'discharged' to another status.")

    # Only log if status is actually changing or notes are updated
    status_changed = old_status != new_status
    notes_changed = (request.notes is not None and request.notes != association.note)

    # Update association
    if status_changed:
        association.status = new_status
        association.updated_at = get_local_naive_now()
        association.status_updated_by = current_user.id
    if request.notes is not None:
        association.note = request.notes
    association.updated_at = get_local_naive_now()

    # Log to patient_status_history if status or notes changed
    if status_changed or notes_changed:
        from app.models.patient_status_history import PatientStatusHistory
        status_history = PatientStatusHistory(
            doctor_id=doctor_id,
            patient_id=patient_id,
            old_status=old_status,
            new_status=new_status,
            notes=request.notes,
            changed_by=current_user.id,
            changed_at=get_local_naive_now()
        )
        db.add(status_history)

    db.commit()
    db.refresh(association)
    db.refresh(patient)

    # Build enhanced patient info for response
    patient_info = {
        "id": patient.id,
        "name": patient.user.name,
        "email": patient.user.email,
        "age": patient.age,
        "gender": patient.gender,
        "phone": patient.phone,
        "birth_date": patient.birth_date.isoformat() if patient.birth_date else None,
        "address": patient.address,
        "photo_url": patient.user.photo_url,
        "assignment_date": association.assigned_at,
        "status": association.status or "active",
        "notes": association.note,
        "last_record_date": None,  # Optionally fetch last record if needed
        "total_records": None,     # Optionally fetch total records if needed
        "status_updated_at": association.updated_at,
        "status_updated_by": association.status_updated_by
    }

    return {
        "status": "success",
        "message": "Patient status updated successfully",
        "patient": patient_info
    }

@router.get("/doctors/{doctor_id}/patients", response_model=EnhancedDoctorPatientsResponse, tags=["Doctor Dashboard"])
def get_enhanced_doctor_patients(
    doctor_id: int,
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_access)
):
    """Get enhanced list of patients assigned to doctor with status, assignment date, and notes"""
    
    print(f"[DEBUG] get_enhanced_doctor_patients - requested doctor_id: {doctor_id}")
    print(f"[DEBUG] get_enhanced_doctor_patients - current_user.id: {current_user.id}")
    print(f"[DEBUG] get_enhanced_doctor_patients - current_user.role: {current_user.role}")
    
    # Check access (doctors can only see their own patients, admins can see any doctor's patients)
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    
    if user_role == "doctor" and current_user.id != doctor_id:
        print(f"[DEBUG] Access denied - doctor {current_user.id} trying to access patients for doctor {doctor_id}")
        raise HTTPException(status_code=403, detail="Access denied")
    
    print(f"[DEBUG] Access granted for doctor patients list")
    
    # Base query with joins
    query = db.query(
        Patient,
        User,
        DoctorPatientAssociation
    ).join(
        User, Patient.user_id == User.id
    ).join(
        DoctorPatientAssociation, Patient.id == DoctorPatientAssociation.patient_id
    ).filter(
        DoctorPatientAssociation.doctor_id == doctor_id
    )
    
    # Apply status filter
    if status:
        query = query.filter(DoctorPatientAssociation.status == status)
    
    # Get total count
    total = query.count()
    
    # Get results with pagination
    results = query.offset(offset).limit(limit).all()
    
    patients = []
    for patient, user, association in results:
        # Get last record date
        last_record = db.query(Record).filter(
            Record.patient_id == patient.id
        ).order_by(desc(Record.start_time)).first()

        # Get total records count
        total_records = db.query(Record).filter(Record.patient_id == patient.id).count()

        patients.append({
            "id": patient.id,
            "name": user.name,
            "email": user.email,
            "age": patient.age,
            "gender": patient.gender,
            "phone": patient.phone,
            "birth_date": patient.birth_date.isoformat() if patient.birth_date else None,
            "address": patient.address,
            "photo_url": user.photo_url,
            "assignment_date": association.assigned_at,
            "status": association.status or "active",
            "notes": association.note,
            "last_record_date": last_record.start_time if last_record else None,
            "total_records": total_records,
            "status_updated_at": association.updated_at,
            "status_updated_by": association.status_updated_by
        })
    
    return {
        "patients": patients,
        "total": total,
        "limit": limit,
        "offset": offset
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
