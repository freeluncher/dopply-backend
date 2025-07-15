from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.medical import User
from app.core.security import verify_jwt_token
from app.services.admin_doctor_validation_service import AdminDoctorValidationService

router = APIRouter(tags=["Admin"])
security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = verify_jwt_token(token)
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user or user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

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
