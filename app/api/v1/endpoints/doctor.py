from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.models.medical import User
from app.core.dependencies import get_current_user
from app.schemas.common import DoctorResponse, DoctorUpdateRequest, ProfilePhotoResponse
from app.services.file_upload_service import FileUploadService

router = APIRouter(prefix="/doctors", tags=["Doctor"])

@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(
    doctor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get doctor by ID"""
    doctor = db.query(User).filter(
        User.id == doctor_id,
        User.role == "doctor"
    ).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return DoctorResponse(
        success=True,
        data={
            "id": doctor.id,
            "userId": doctor.id,
            "name": doctor.name,
            "email": doctor.email,
            "specialization": doctor.specialization,
            "profilePhotoUrl": f"https://dopply.my.id{doctor.photo_url}" if doctor.photo_url else None,
            "createdAt": doctor.created_at.isoformat() if doctor.created_at else None,
            "updatedAt": datetime.now().isoformat()
        },
        message="Doctor data retrieved successfully"
    )

@router.put("/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(
    doctor_id: int,
    request: DoctorUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update doctor data"""
    # Authorization check - only doctor themselves can update their data
    if current_user.role.value != "doctor" or current_user.id != doctor_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    doctor = db.query(User).filter(
        User.id == doctor_id,
        User.role == "doctor"
    ).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Update doctor data
    if request.name:
        doctor.name = request.name
    if request.email:
        doctor.email = request.email
    if request.specialization:
        doctor.specialization = request.specialization
    
    db.commit()
    db.refresh(doctor)
    
    return DoctorResponse(
        success=True,
        data={
            "id": doctor.id,
            "userId": doctor.id,
            "name": doctor.name,
            "email": doctor.email,
            "specialization": doctor.specialization,
            "profilePhotoUrl": f"https://dopply.my.id{doctor.photo_url}" if doctor.photo_url else None,
            "updatedAt": datetime.now().isoformat()
        },
        message="Doctor data updated successfully"
    )

@router.post("/{doctor_id}/profile-photo", response_model=ProfilePhotoResponse)
async def upload_doctor_profile_photo(
    doctor_id: int,
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload doctor profile photo"""
    # Authorization check
    if current_user.role.value != "doctor" or current_user.id != doctor_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    doctor = db.query(User).filter(
        User.id == doctor_id,
        User.role == "doctor"
    ).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
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
        photo_url = await file_service.upload_user_photo(photo, doctor.id, "doctor")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")
    doctor.photo_url = photo_url
    db.commit()
    
    return ProfilePhotoResponse(
        success=True,
        data={
            "profilePhotoUrl": f"https://dopply.my.id{photo_url}"
        },
        message="Profile photo uploaded successfully"
    )