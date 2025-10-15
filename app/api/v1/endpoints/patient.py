
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.models.medical import User, Patient, DoctorPatientAssociation
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.schemas.common import PatientResponse, PatientUpdateRequest, ProfilePhotoResponse
from app.services.file_upload_service import FileUploadService
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/patients", tags=["Patient"])

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patient by ID"""
    # Check authorization - patient can only access their own data, doctor can access assigned patients
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Authorization check
    if current_user.role.value == "patient":
        # Patient can only access their own data
        if patient.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role.value == "doctor":
        # Doctor can access assigned patients
        association = db.query(DoctorPatientAssociation).filter(
            DoctorPatientAssociation.doctor_id == current_user.id,
            DoctorPatientAssociation.patient_id == patient_id
        ).first()
        if not association:
            raise HTTPException(status_code=403, detail="Access denied - patient not assigned")
    
    return PatientResponse(
        success=True,
        data={
            "id": patient.id,
            "userId": patient.user_id,
            "name": patient.name,
            "email": patient.email,
            "hpht": patient.hpht.isoformat() if patient.hpht else None,
            "birthDate": patient.birth_date.isoformat() if patient.birth_date else None,
            "address": patient.address,
            "medicalNote": patient.medical_note,
            "profilePhotoUrl": f"https://dopply.my.id{patient.user.photo_url}" if patient.user and patient.user.photo_url else None,
            "createdAt": patient.user.created_at.isoformat() if patient.user else None,
            "updatedAt": datetime.now().isoformat()
        },
        message="Patient data retrieved successfully"
    )

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    request: PatientUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update patient data"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Authorization check - only patient themselves can update their data
    if current_user.role.value == "patient" and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role.value not in ["patient", "doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update patient data
    if request.name:
        patient.name = request.name
    if request.email:
        patient.email = request.email
        # Also update user email
        patient.user.email = request.email
    if request.hpht:
        from datetime import datetime as dt
        patient.hpht = dt.strptime(request.hpht, "%Y-%m-%d").date()
    if request.birthDate:
        from datetime import datetime as dt
        patient.birth_date = dt.strptime(request.birthDate, "%Y-%m-%d").date()
    if request.address:
        patient.address = request.address
    if request.medicalNote:
        patient.medical_note = request.medicalNote
    
    db.commit()
    db.refresh(patient)
    
    return PatientResponse(
        success=True,
        data={
            "id": patient.id,
            "userId": patient.user_id,
            "name": patient.name,
            "email": patient.email,
            "hpht": patient.hpht.isoformat() if patient.hpht else None,
            "birthDate": patient.birth_date.isoformat() if patient.birth_date else None,
            "address": patient.address,
            "medicalNote": patient.medical_note,
            "profilePhotoUrl": f"https://dopply.my.id{patient.user.photo_url}" if patient.user and patient.user.photo_url else None,
            "updatedAt": datetime.now().isoformat()
        },
        message="Patient data updated successfully"
    )

@router.post("/{patient_id}/profile-photo", response_model=ProfilePhotoResponse)
async def upload_patient_profile_photo(
    patient_id: int,
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload patient profile photo"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Authorization check
    if current_user.role.value == "patient" and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png"]
    if photo.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file format. Only jpg, jpeg, png allowed")
    
    # Check file size (5MB limit)
    if photo.size and photo.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File size exceeds maximum limit of 5MB")
    
    # Use file upload service
    try:
        file_service = FileUploadService()
        photo_url = await file_service.upload_user_photo(photo, patient.user_id, "patient")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")
    patient.user.photo_url = photo_url
    db.commit()
    
    return ProfilePhotoResponse(
        success=True,
        data={
            "profilePhotoUrl": f"https://dopply.my.id{photo_url}"
        },
        message="Profile photo uploaded successfully"
    )

# Legacy endpoint - keep for backward compatibility
@router.get("/legacy/{id}", summary="Get biodata pasien (legacy)")
def get_patient_biodata_legacy(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.value != "patient":
        raise HTTPException(status_code=403, detail="Hanya pasien yang dapat mengakses biodata")
    
    patient = db.query(Patient).filter(Patient.id == id, Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Data pasien tidak ditemukan")
    
    return {
        "status": "success",
        "patient": {
            "id": patient.id,
            "user_id": current_user.id,
            "name": patient.name,
            "email": patient.email,
            "hpht": patient.hpht,
            "birth_date": patient.birth_date,
            "address": patient.address,
            "medical_note": patient.medical_note
        }
    }

@router.put("/legacy/{id}", summary="Update biodata pasien (legacy)")
def update_patient_biodata_legacy(
    id: int,
    req: PatientUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verifikasi role
    if current_user.role.value != "patient":
        raise HTTPException(status_code=403, detail="Hanya pasien yang dapat mengupdate biodata")
    
    # Ambil patient
    patient = db.query(Patient).filter(Patient.id == id, Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Data pasien tidak ditemukan")
    
    # Update data
    if req.name:
        current_user.name = req.name
        patient.name = req.name
    if req.email:
        current_user.email = req.email
        patient.email = req.email
    if req.hpht:
        patient.hpht = req.hpht
    if req.birthDate:
        from datetime import datetime as dt
        patient.birth_date = dt.strptime(req.birthDate, "%Y-%m-%d").date()
    if req.address:
        patient.address = req.address
    if req.medicalNote:
        patient.medical_note = req.medicalNote
    
    db.commit()
    db.refresh(patient)
    db.refresh(current_user)
    
    return {
        "status": "success",
        "patient": {
            "id": patient.id,
            "user_id": patient.user_id,
            "name": patient.name,
            "email": patient.email,
            "hpht": patient.hpht,
            "birth_date": patient.birth_date,
            "address": patient.address,
            "medical_note": patient.medical_note
        }
    }
