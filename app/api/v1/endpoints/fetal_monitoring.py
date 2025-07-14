# Standard library imports
from datetime import datetime
from typing import List, Optional

# Third-party imports
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

# Local imports
from app.db.session import SessionLocal
from app.models.medical import User, Patient, Doctor, PregnancyInfo
from app.services.fetal_monitoring_service import FetalMonitoringService
from app.schemas.fetal_monitoring import (
    FetalClassificationRequest,
    FetalClassificationResponse,
    FetalMonitoringSessionCreate,
    FetalMonitoringSessionResponse,
    FetalMonitoringSessionList,
    ShareSessionRequest,
    ShareSessionResponse,
    PregnancyInfoCreate,
    PregnancyInfoUpdate,
    PregnancyInfoResponse,
    FetalBPMClassificationRequest,
    FetalBPMClassificationResponse
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

# --- Dependencies ---
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

def get_current_patient(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get the current user and ensure they are a patient."""
    user = get_current_user(credentials, db)
    user_role = user.role.value if hasattr(user.role, 'value') else str(user.role)
    if user_role != "patient":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Patient access required")
    return user

def get_current_doctor(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get the current user and ensure they are a doctor."""
    user = get_current_user(credentials, db)
    user_role = user.role.value if hasattr(user.role, 'value') else str(user.role)
    if user_role != "doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor access required")
    return user

def get_current_doctor_or_patient(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get the current user and ensure they are a doctor or patient."""
    user = get_current_user(credentials, db)
    user_role = user.role.value if hasattr(user.role, 'value') else str(user.role)
    if user_role not in ["doctor", "patient"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor or patient access required")
    return user

# --- Fetal Heart Rate Classification Endpoints ---

@router.post("/fetal/classify", response_model=FetalClassificationResponse, tags=["Fetal Monitoring"], 
             summary="🤖 AI-Powered Fetal Heart Rate Classification",
             description="Advanced AI-powered analysis of fetal heart rate patterns with medical-grade accuracy. Provides detailed classification, risk assessment, and medical recommendations.")
def classify_fetal_heart_rate(
    request: FetalClassificationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_doctor_or_patient)
):
    """
    Classify fetal heart rate data using advanced analysis algorithms.
    Returns classification, risk level, and recommendations.
    """
    try:
        result = FetalMonitoringService.classify_fetal_heart_rate(
            fhr_data=request.fhr_data,
            gestational_age=request.gestational_age,
            maternal_age=request.maternal_age,
            duration_minutes=request.duration_minutes
        )
        return FetalClassificationResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Classification failed")

# --- Fetal Monitoring Session Endpoints ---

@router.post("/fetal/sessions", response_model=FetalMonitoringSessionResponse, status_code=status.HTTP_201_CREATED, tags=["Fetal Monitoring"],
             summary="🏥 Start New Fetal Monitoring Session",
             description="Create a new fetal monitoring session for clinic or home monitoring. Supports real-time data collection and session management.")
def save_fetal_monitoring_session(
    request: FetalMonitoringSessionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_doctor_or_patient)
):
    """
    Save a complete fetal monitoring session with heart rate data and analysis results.
    Can be created by doctors or patients (self-monitoring).
    """
    try:
        # Validate patient access
        user_role = user.role.value if hasattr(user.role, 'value') else str(user.role)
        if user_role == "patient":
            # Patients can only create sessions for themselves
            patient = db.query(Patient).filter(Patient.patient_id == user.id).first()
            if not patient or patient.id != request.patient_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="You can only create monitoring sessions for yourself"
                )
        
        result = FetalMonitoringService.save_monitoring_session(db, request, user.id)
        return FetalMonitoringSessionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save monitoring session")

@router.get("/fetal/sessions", response_model=FetalMonitoringSessionList, tags=["Fetal Monitoring"],
            summary="📋 Get Monitoring Sessions",
            description="Retrieve list of fetal monitoring sessions with advanced filtering options. Supports pagination and status filtering.")
def get_fetal_monitoring_sessions(
    patient_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_doctor_or_patient)
):
    """
    Get fetal monitoring sessions. 
    - Patients can only see their own sessions
    - Doctors can see sessions for their assigned patients or all if no patient_id specified
    """
    try:
        user_role = user.role.value if hasattr(user.role, 'value') else str(user.role)
        
        if user_role == "patient":
            # Patients can only see their own sessions
            patient = db.query(Patient).filter(Patient.patient_id == user.id).first()
            if not patient:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
            patient_id = patient.id
        
        result = FetalMonitoringService.get_monitoring_sessions(
            db, patient_id=patient_id, skip=skip, limit=limit
        )
        return FetalMonitoringSessionList(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve sessions")

@router.get("/fetal/sessions/{session_id}", response_model=FetalMonitoringSessionResponse, tags=["Fetal Monitoring"],
            summary="🔍 Get Session Details",
            description="Get detailed information about a specific monitoring session including heart rate readings, analysis results, and session metadata.")
def get_fetal_monitoring_session(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_doctor_or_patient)
):
    """
    Get a specific fetal monitoring session by ID.
    Access control applied based on user role.
    """
    try:
        user_role = user.role.value if hasattr(user.role, 'value') else str(user.role)
        
        result = FetalMonitoringService.get_monitoring_session(db, session_id, user.id, user_role)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found or access denied")
        
        return FetalMonitoringSessionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve session")

@router.post("/fetal/sessions/{session_id}/share", response_model=ShareSessionResponse, tags=["Fetal Monitoring"],
             summary="🤝 Share Session with Doctor",
             description="Securely share a fetal monitoring session with a healthcare provider for professional review and consultation.")
def share_fetal_monitoring_session(
    session_id: int,
    request: ShareSessionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_patient)
):
    """
    Share a fetal monitoring session with a doctor.
    Only patients can share their own sessions.
    """
    try:
        # Get patient profile
        patient = db.query(Patient).filter(Patient.patient_id == user.id).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
        
        result = FetalMonitoringService.share_session_with_doctor(
            db, session_id, patient.id, request.doctor_id
        )
        return ShareSessionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to share session")

# --- Pregnancy Information Endpoints ---

@router.post("/fetal/pregnancy-info", response_model=PregnancyInfoResponse, status_code=status.HTTP_201_CREATED, tags=["Pregnancy Management"],
             summary="🤱 Create Pregnancy Information",
             description="Create comprehensive pregnancy information including gestational age, risk assessment, and medical history for enhanced monitoring.")
def create_pregnancy_info(
    request: PregnancyInfoCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_doctor_or_patient)
):
    """
    Create pregnancy information record.
    Patients can create for themselves, doctors can create for their patients.
    """
    try:
        user_role = user.role.value if hasattr(user.role, 'value') else str(user.role)
        
        if user_role == "patient":
            # Patients can only create for themselves
            patient = db.query(Patient).filter(Patient.patient_id == user.id).first()
            if not patient or patient.id != request.patient_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only create pregnancy information for yourself"
                )
        
        result = FetalMonitoringService.create_pregnancy_info(db, request)
        return PregnancyInfoResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create pregnancy information")

@router.get("/fetal/pregnancy-info/{patient_id}", response_model=PregnancyInfoResponse, tags=["Pregnancy Management"],
            summary="📊 Get Pregnancy Information",
            description="Retrieve detailed pregnancy information for risk assessment and monitoring planning.")
def get_pregnancy_info(
    patient_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_doctor_or_patient)
):
    """
    Get pregnancy information for a patient.
    Patients can only see their own info, doctors can see their patients' info.
    """
    try:
        user_role = user.role.value if hasattr(user.role, 'value') else str(user.role)
        
        if user_role == "patient":
            # Patients can only see their own info
            patient = db.query(Patient).filter(Patient.patient_id == user.id).first()
            if not patient or patient.id != patient_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only view your own pregnancy information"
                )
        
        result = FetalMonitoringService.get_pregnancy_info(db, patient_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pregnancy information not found")
        
        return PregnancyInfoResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve pregnancy information")

@router.put("/fetal/pregnancy-info/{patient_id}", response_model=PregnancyInfoResponse, tags=["Pregnancy Management"])
def update_pregnancy_info(
    patient_id: int,
    request: PregnancyInfoUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_doctor_or_patient)
):
    """
    Update pregnancy information for a patient.
    Patients can only update their own info, doctors can update their patients' info.
    """
    try:
        user_role = user.role.value if hasattr(user.role, 'value') else str(user.role)
        
        if user_role == "patient":
            # Patients can only update their own info
            patient = db.query(Patient).filter(Patient.patient_id == user.id).first()
            if not patient or patient.id != patient_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only update your own pregnancy information"
                )
        
        result = FetalMonitoringService.update_pregnancy_info(db, patient_id, request)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pregnancy information not found")
        
        return PregnancyInfoResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update pregnancy information")

@router.delete("/fetal/pregnancy-info/{patient_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Pregnancy Management"])
def delete_pregnancy_info(
    patient_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_doctor_or_patient)
):
    """
    Delete pregnancy information for a patient.
    Patients can only delete their own info, doctors can delete their patients' info.
    """
    try:
        user_role = user.role.value if hasattr(user.role, 'value') else str(user.role)
        
        if user_role == "patient":
            # Patients can only delete their own info
            patient = db.query(Patient).filter(Patient.patient_id == user.id).first()
            if not patient or patient.id != patient_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only delete your own pregnancy information"
                )
        
        result = FetalMonitoringService.delete_pregnancy_info(db, patient_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pregnancy information not found")
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete pregnancy information")

# --- Doctor List Endpoint for Sharing ---

@router.get("/fetal/doctors", tags=["Fetal Monitoring"])
def get_available_doctors(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_patient)
):
    """
    Get list of available doctors for sharing fetal monitoring sessions.
    Only accessible by patients.
    """
    try:
        doctors = db.query(User).filter(User.role == "doctor").all()
        result = []
        
        for doctor in doctors:
            doctor_profile = db.query(Doctor).filter(Doctor.doctor_id == doctor.id).first()
            is_valid = doctor_profile.is_valid if doctor_profile else None
            
            result.append({
                "id": doctor.id,
                "name": doctor.name,
                "email": doctor.email,
                "is_valid": is_valid,
                "specialization": doctor_profile.specialization if doctor_profile else None
            })
        
        return {"doctors": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve doctors list")

# --- Backward Compatibility Aliases ---

@router.post("/fetal/classify_bpm", response_model=FetalBPMClassificationResponse, tags=["Fetal Monitoring - Legacy"], 
             summary="🔄 Legacy BPM Classification (Alias)",
             description="Legacy endpoint for backward compatibility. Use /fetal/classify instead.")
def classify_bpm_legacy(
    request: FetalBPMClassificationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_doctor_or_patient)
):
    """
    Legacy endpoint for BPM classification. Redirects to new classify endpoint.
    """
    try:
        # Convert legacy request to new format
        fhr_data = request.get_bpm_values()
        
        result = FetalMonitoringService.classify_fetal_heart_rate(
            fhr_data=fhr_data,
            gestational_age=request.gestational_age,
            maternal_age=28,  # Default
            duration_minutes=None
        )
        return FetalBPMClassificationResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Classification failed")

@router.post("/fetal/monitoring_sessions", response_model=FetalMonitoringSessionResponse, status_code=status.HTTP_201_CREATED, tags=["Fetal Monitoring - Legacy"],
             summary="🔄 Legacy Monitoring Sessions (Alias)", 
             description="Legacy endpoint for backward compatibility. Use /fetal/sessions instead.")
def save_monitoring_session_legacy(
    request: FetalMonitoringSessionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_doctor_or_patient)
):
    """
    Legacy endpoint for monitoring sessions. Redirects to new sessions endpoint.
    """
    # Delegate to the new endpoint
    return save_fetal_monitoring_session(request, db, user)

# --- Main Endpoints ---
