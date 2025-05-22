from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from app.schemas.patient import PatientCreate, PatientUpdate, PatientOut
from app.services.patient_service import get_patients, get_patient, update_patient, delete_patient, register_user_universal
from app.db.session import SessionLocal
from app.models.medical import Doctor, Patient, User, DoctorPatientAssociation
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.services.doctor_patient_service import DoctorPatientService
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_jwt_token, verify_password, get_password_hash

router = APIRouter()

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_patient_id(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    payload = verify_jwt_token(token)
    # sub is email, not user_id
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user or (hasattr(user.role, 'value') and user.role.value != "patient") and (str(user.role) != "patient"):
        raise HTTPException(status_code=403, detail="Patient access required")
    return user.id

class DoctorPatientAssociationIn(BaseModel):
    status: Optional[str] = None
    note: Optional[str] = None

class DoctorPatientAssociationOut(BaseModel):
    doctor_id: int
    patient_id: int
    assigned_at: datetime
    status: Optional[str] = None
    note: Optional[str] = None

    class Config:
        orm_mode = True

class AssignPatientByEmailIn(BaseModel):
    email: str
    status: Optional[str] = None
    note: Optional[str] = None

class ChangeEmailRequest(BaseModel):
    new_email: str
    current_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.get("/patients", response_model=List[PatientOut])
def read_patients(db: Session = Depends(get_db)):
    patients = db.query(Patient).join(User, Patient.patient_id == User.id).filter(User.name != None, User.email != None).all()
    result = []
    for p in patients:
        result.append(PatientOut(
            id=p.patient_id,
            patient_id=p.patient_id,
            name=p.user.name if p.user else None,
            email=p.user.email if p.user else None,
            birth_date=p.birth_date,
            address=p.address,
            medical_note=p.medical_note,
        ))
    return result

@router.get("/patients/{patient_id}", response_model=PatientOut)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.put("/patients/{patient_id}", response_model=PatientOut)
def update_existing_patient(patient_id: int, patient: PatientUpdate, db: Session = Depends(get_db)):
    updated = update_patient(db, patient_id, patient)
    if not updated:
        raise HTTPException(status_code=404, detail="Patient not found")
    return updated

@router.delete("/patients/{patient_id}", status_code=204)
def delete_existing_patient(patient_id: int, db: Session = Depends(get_db)):
    success = delete_patient(db, patient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")
    return None

@router.post("/doctors/{doctor_id}/assign-patient/{patient_id}", response_model=DoctorPatientAssociationOut)
def assign_patient_to_doctor(
    doctor_id: int,
    patient_id: int,
    data: DoctorPatientAssociationIn = None,
    db: Session = Depends(get_db)
):
    try:
        assoc = DoctorPatientService.assign_patient_to_doctor(
            db, doctor_id, patient_id,
            status=data.status if data else None,
            note=data.note if data else None
        )
        return assoc
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=msg)
        if "already assigned" in msg:
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=400, detail=msg)

@router.post("/doctors/{doctor_id}/assign-patient-by-email", response_model=DoctorPatientAssociationOut)
def assign_patient_to_doctor_by_email(
    doctor_id: int,
    data: AssignPatientByEmailIn,
    db: Session = Depends(get_db)
):
    try:
        assoc = DoctorPatientService.assign_patient_to_doctor_by_email(
            db, doctor_id, data.email, status=data.status, note=data.note
        )
        return assoc
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=msg)
        if "already assigned" in msg:
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=400, detail=msg)

@router.patch("/doctors/{doctor_id}/patients/{patient_id}", response_model=DoctorPatientAssociationOut)
def update_doctor_patient_association(
    doctor_id: int,
    patient_id: int,
    data: DoctorPatientAssociationIn,
    db: Session = Depends(get_db)
):
    try:
        assoc = DoctorPatientService.update_doctor_patient_association(
            db, doctor_id, patient_id, status=data.status, note=data.note
        )
        return assoc
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)

@router.get("/doctors/{doctor_id}/patients", response_model=List[PatientOut])
def list_patients_for_doctor(doctor_id: int, db: Session = Depends(get_db)):
    return DoctorPatientService.list_patients_for_doctor(db, doctor_id)

@router.delete("/doctors/{doctor_id}/unassign-patient/{patient_id}")
def unassign_patient_from_doctor(doctor_id: int, patient_id: int, db: Session = Depends(get_db)):
    try:
        DoctorPatientService.unassign_patient_from_doctor(db, doctor_id, patient_id)
        return {"message": "Patient unassigned from doctor"}
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)

@router.post("/patients", response_model=PatientOut, status_code=201)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    # Daftar user baru dengan role patient
    from app.models.medical import UserRole
    class PatientCreateWithRole(PatientCreate):
        role: str = "patient"
    # Gabungkan data dengan role
    data = PatientCreateWithRole(**patient.dict(), role="patient")
    created_user = register_user_universal(db, data)
    patient_obj = db.query(Patient).filter(Patient.patient_id == created_user.id).first()
    return PatientOut(
        id=created_user.id,
        name=created_user.name,
        email=created_user.email,
        birth_date=getattr(patient_obj, "birth_date", None),
        address=getattr(patient_obj, "address", None),
        medical_note=getattr(patient_obj, "medical_note", None)
    )

class AssignPatientIn(BaseModel):
    patient_id: int
    status: Optional[str] = None
    note: Optional[str] = None

@router.post("/doctors/{doctor_id}/assign-patient", response_model=DoctorPatientAssociationOut)
def assign_patient_to_doctor_body(
    doctor_id: int,
    data: AssignPatientIn,
    db: Session = Depends(get_db)
):
    try:
        assoc = DoctorPatientService.assign_patient_to_doctor(
            db, doctor_id, data.patient_id,
            status=data.status,
            note=data.note
        )
        return assoc
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=msg)
        if "already assigned" in msg:
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=400, detail=msg)

# --- Account Management Endpoints for All Roles ---

class ChangeEmailOnlyRequest(BaseModel):
    email: str

class ChangePasswordOnlyRequest(BaseModel):
    old_password: str
    new_password: str

def get_current_user_role(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    payload = verify_jwt_token(token)
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.patch("/patient/account/email")
def patient_change_email(
    req: ChangeEmailOnlyRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_role)
):
    if (hasattr(user.role, 'value') and user.role.value != "patient") and (str(user.role) != "patient"):
        raise HTTPException(status_code=403, detail="Patient access required")
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=409, detail="Email already in use")
    user.email = req.email
    db.commit()
    db.refresh(user)
    return {"message": "Email updated successfully"}

@router.patch("/patient/account/password")
def patient_change_password(
    req: ChangePasswordOnlyRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_role)
):
    if (hasattr(user.role, 'value') and user.role.value != "patient") and (str(user.role) != "patient"):
        raise HTTPException(status_code=403, detail="Patient access required")
    if not verify_password(req.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.password_hash = get_password_hash(req.new_password)
    db.commit()
    db.refresh(user)
    return {"message": "Password updated successfully"}

@router.patch("/doctor/account/email")
def doctor_change_email(
    req: ChangeEmailOnlyRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_role)
):
    if (hasattr(user.role, 'value') and user.role.value != "doctor") and (str(user.role) != "doctor"):
        raise HTTPException(status_code=403, detail="Doctor access required")
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=409, detail="Email already in use")
    user.email = req.email
    db.commit()
    db.refresh(user)
    return {"message": "Email updated successfully"}

@router.patch("/doctor/account/password")
def doctor_change_password(
    req: ChangePasswordOnlyRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_role)
):
    if (hasattr(user.role, 'value') and user.role.value != "doctor") and (str(user.role) != "doctor"):
        raise HTTPException(status_code=403, detail="Doctor access required")
    if not verify_password(req.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.password_hash = get_password_hash(req.new_password)
    db.commit()
    db.refresh(user)
    return {"message": "Password updated successfully"}

@router.patch("/admin/account/email")
def admin_change_email(
    req: ChangeEmailOnlyRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_role)
):
    if (hasattr(user.role, 'value') and user.role.value != "admin") and (str(user.role) != "admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=409, detail="Email already in use")
    user.email = req.email
    db.commit()
    db.refresh(user)
    return {"message": "Email updated successfully"}

@router.patch("/admin/account/password")
def admin_change_password(
    req: ChangePasswordOnlyRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_role)
):
    if (hasattr(user.role, 'value') and user.role.value != "admin") and (str(user.role) != "admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    if not verify_password(req.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.password_hash = get_password_hash(req.new_password)
    db.commit()
    db.refresh(user)
    return {"message": "Password updated successfully"}
