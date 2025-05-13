from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.medical import Doctor, User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/doctor/validation-requests/count")
def count_doctor_validation_requests(db: Session = Depends(get_db)):
    count = db.query(Doctor).filter(Doctor.is_valid == False).count()
    return {"pending_validation": count}

@router.get("/doctor/validation-requests")
def list_doctor_validation_requests(db: Session = Depends(get_db)):
    doctors = db.query(Doctor).filter(Doctor.is_valid == False).all()
    result = []
    for doctor in doctors:
        user = db.query(User).filter(User.id == doctor.user_id).first()
        result.append({
            "doctor_id": doctor.id,
            "user_id": doctor.user_id,
            "name": user.name if user else None,
            "email": user.email if user else None
        })
    return result

@router.post("/doctor/validate/{doctor_id}")
def validate_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctor.is_valid = True
    db.commit()
    return {"message": "Doctor validated successfully"}
