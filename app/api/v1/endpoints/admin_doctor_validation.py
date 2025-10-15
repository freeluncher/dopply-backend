from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.medical import User
from app.core.dependencies import get_current_user
from app.services.admin_doctor_validation_service import AdminDoctorValidationService

router = APIRouter(tags=["Admin"])

def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current user and verify admin role"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/doctor/validation-requests/count")
def count_doctor_validation_requests(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    return {"pending_validation": AdminDoctorValidationService.count_doctor_validation_requests(db)}

@router.get("/doctor/validation-requests")
def list_doctor_validation_requests(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    return AdminDoctorValidationService.list_doctor_validation_requests(db)

@router.post("/doctor/validate/{doctor_id}")
def validate_doctor(doctor_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    try:
        AdminDoctorValidationService.validate_doctor(db, doctor_id)
        return {"message": "Doctor validated successfully"}
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)
