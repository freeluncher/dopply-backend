from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel

from app.db.session import get_db
from app.models.medical import User, Patient
from app.core.dependencies import get_current_user
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.services.file_upload_service import FileUploadService
from app.schemas.user import UserRegister, UserOut
from app.schemas.refresh import LoginResponse
from app.schemas.common import ProfilePhotoResponse, DoctorData

router = APIRouter(tags=["User Management"])

class DoctorProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    specialization: Optional[str] = None

# Upload foto profil pasien
@router.post("/patient/profile/photo", response_model=ProfilePhotoResponse)
async def upload_patient_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload patient profile photo"""
    if current_user.role.value != "patient":
        raise HTTPException(status_code=403, detail="Hanya pasien yang dapat upload foto")
    
    try:
        file_service = FileUploadService()
        photo_url = await file_service.upload_user_photo(file, current_user.id, "patient")
        current_user.photo_url = photo_url
        db.commit()
        
        return ProfilePhotoResponse(
            success=True,
            data={"profilePhotoUrl": f"https://dopply.my.id{photo_url}"},
            message="Foto profil berhasil diupload"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")

# Upload foto profil dokter
@router.post("/doctor/profile/photo", response_model=ProfilePhotoResponse)
async def upload_doctor_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload doctor profile photo"""
    if current_user.role.value != "doctor":
        raise HTTPException(status_code=403, detail="Hanya dokter yang dapat upload foto")
    
    try:
        file_service = FileUploadService()
        photo_url = await file_service.upload_user_photo(file, current_user.id, "doctor")
        current_user.photo_url = photo_url
        db.commit()
        
        return ProfilePhotoResponse(
            success=True,
            data={"profilePhotoUrl": f"https://dopply.my.id{photo_url}"},
            message="Foto profil berhasil diupload"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")

# Update profil dokter
@router.put("/doctor/profile")
async def update_doctor_profile(
    request: DoctorProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update doctor profile"""
    if current_user.role.value != "doctor":
        raise HTTPException(status_code=403, detail="Hanya dokter yang dapat update profil")
    
    if request.name:
        current_user.name = request.name
    if request.email:
        current_user.email = request.email
    if request.specialization:
        current_user.specialization = request.specialization
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "status": "success",
        "message": "Profil dokter berhasil diupdate",
        "doctor": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "specialization": current_user.specialization,
            "photo_url": current_user.photo_url
        }
    }

# Get profil dokter
@router.get("/doctor/profile")
async def get_doctor_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get doctor profile"""
    if current_user.role.value != "doctor":
        raise HTTPException(status_code=403, detail="Hanya dokter yang dapat akses profil")
    
    return {
        "status": "success",
        "doctor": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "specialization": current_user.specialization,
            "photo_url": current_user.photo_url,
            "created_at": current_user.created_at,
            "updated_at": current_user.updated_at
        }
    }

# Register user (keep existing endpoint)
@router.post("/register", status_code=201, response_model=UserOut)
async def register_user(
    user: UserRegister,
    db: Session = Depends(get_db)
):
    """Register new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    password_hash = get_password_hash(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=password_hash,
        role=user.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # If user is patient, create patient record
    if user.role == "patient":
        patient = Patient(
            user_id=new_user.id,
            name=user.name,
            email=user.email
        )
        db.add(patient)
        db.commit()
    
    return UserOut(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        role=new_user.role.value,
        created_at=new_user.created_at
    )

# Logout (frontend only)
@router.post("/auth/logout")
async def logout_user():
    """Logout user (frontend handles token removal)"""
    return {"status": "success", "message": "Logout successful"}

# Get all doctors
@router.get("/user/all-doctors", response_model=List[DoctorData])
async def get_all_doctors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all doctors in the system"""
    doctors = db.query(User).filter(User.role == "doctor").all()
    
    return [
        DoctorData(
            id=doctor.id,
            userId=doctor.id,
            name=doctor.name,
            email=doctor.email,
            specialization=doctor.specialization,
            profilePhotoUrl=f"https://dopply.my.id{doctor.photo_url}" if doctor.photo_url else None,
            createdAt=doctor.created_at.isoformat() if doctor.created_at else None,
            updatedAt=doctor.updated_at.isoformat() if doctor.updated_at else None
        )
        for doctor in doctors
    ]