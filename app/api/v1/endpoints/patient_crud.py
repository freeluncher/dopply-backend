# Standard library imports
from datetime import datetime
from typing import List, Optional

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, Security, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

# Local imports
from app.db.session import SessionLocal
from app.models.medical import Doctor, Patient, User, DoctorPatientAssociation
from app.schemas.patient import PatientCreate, PatientUpdate, PatientOut
from app.services.patient_service import get_patients, get_patient, update_patient, delete_patient, register_user_universal
from app.services.doctor_patient_service import DoctorPatientService
from app.core.security import verify_jwt_token, verify_password, get_password_hash

router = APIRouter()
security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic Models ---
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
    email: Optional[str] = None
    patient_email: Optional[str] = None
    status: Optional[str] = None
    note: Optional[str] = None

    @property
    def resolved_email(self) -> str:
        # Prefer patient_email if provided, else fallback to email
        if self.patient_email:
            return self.patient_email
        if self.email:
            return self.email
        raise ValueError("Field 'email' or 'patient_email' is required")

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    class Config:
        orm_mode = True

class UserCreateRequest(BaseModel):
    name: str
    email: str
    role: str

class UserUpdateRequest(BaseModel):
    name: str
    email: str
    role: str

class ChangeEmailUnifiedRequest(BaseModel):
    newEmail: str

class ChangePasswordUnifiedRequest(BaseModel):
    oldPassword: str
    newPassword: str

class AssignPatientIn(BaseModel):
    patient_id: int
    status: Optional[str] = None
    note: Optional[str] = None

# --- Dependency for current user and admin ---
def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)) -> User:
    token = credentials.credentials
    payload = verify_jwt_token(token)
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

def require_admin(user: User = Depends(get_current_user)):
    if (hasattr(user.role, 'value') and user.role.value != "admin") and (str(user.role) != "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user

def require_patient(user: User = Depends(get_current_user)):
    if (hasattr(user.role, 'value') and user.role.value != "patient") and (str(user.role) != "patient"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Patient access required")
    return user

def require_admin_or_doctor(user: User = Depends(get_current_user)):
    if (hasattr(user.role, 'value') and user.role.value not in ["admin", "doctor"]) and (str(user.role) not in ["admin", "doctor"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Doctor access required")
    return user

# --- Unified Account Endpoints ---
@router.put("/account/email", tags=["User Management"])
def change_email_unified(
    req: ChangeEmailUnifiedRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if db.query(User).filter(User.email == req.newEmail).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
    user.email = req.newEmail
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
    return {"message": "Email updated successfully"}

@router.put("/account/password", tags=["User Management"])
def change_password_unified(
    req: ChangePasswordUnifiedRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not verify_password(req.oldPassword, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    user.password_hash = get_password_hash(req.newPassword)
    db.commit()
    db.refresh(user)
    return {"message": "Password updated successfully"}

# --- Admin User Management Endpoints ---
@router.get("/users", response_model=List[UserOut], tags=["Admin Functions"])
def get_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    users = db.query(User).all()
    return [UserOut(id=u.id, name=u.name, email=u.email, role=str(u.role)) for u in users]

@router.post("/users", tags=["Admin Functions"])
def create_user(
    req: UserCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
    from app.models.medical import UserRole
    user = User(
        name=req.name,
        email=req.email,
        role=UserRole(req.role) if hasattr(UserRole, req.role) else req.role,
        password_hash=get_password_hash("default123")
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
    return {"id": user.id, "message": "User created successfully"}

@router.put("/users/{user_id}", tags=["Admin Functions"])
def update_user(
    user_id: int,
    req: UserUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if db.query(User).filter(User.email == req.email, User.id != user_id).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
    user.name = req.name
    user.email = req.email
    user.role = req.role
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
    return {"message": "User updated successfully"}

# --- Patient CRUD Endpoints ---
@router.get("/patients", response_model=List[PatientOut], tags=["Patient Management"])
def read_patients(db: Session = Depends(get_db), user: User = Depends(require_admin_or_doctor)):
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

@router.get("/patients/{patient_id}", response_model=PatientOut, tags=["Patient Management"])
def read_patient(patient_id: int, db: Session = Depends(get_db), user: User = Depends(require_admin_or_doctor)):
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return patient

@router.put("/patients/{patient_id}", response_model=PatientOut, tags=["Patient Management"])
def update_existing_patient(patient_id: int, patient: PatientUpdate, db: Session = Depends(get_db), user: User = Depends(require_admin_or_doctor)):
    updated = update_patient(db, patient_id, patient)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return updated

@router.post("/patients", response_model=PatientOut, status_code=status.HTTP_201_CREATED, tags=["Patient Management"])
def create_patient(patient: PatientCreate, db: Session = Depends(get_db), user: User = Depends(require_admin_or_doctor)):
    from app.models.medical import UserRole
    class PatientCreateWithRole(PatientCreate):
        role: str = "patient"
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

# --- Doctor-Patient Association Endpoints ---
@router.post("/doctors/{doctor_id}/assign-patient/{patient_id}", response_model=DoctorPatientAssociationOut, tags=["Patient Management"])
def assign_patient_to_doctor(
    doctor_id: int,
    patient_id: int,
    data: DoctorPatientAssociationIn = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_doctor)  # Restrict to admin/doctor
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        if "already assigned" in msg:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

@router.post("/doctors/{doctor_id}/assign-patient-by-email", response_model=DoctorPatientAssociationOut, tags=["Patient Management"])
def assign_patient_to_doctor_by_email(
    doctor_id: int,
    data: AssignPatientByEmailIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_doctor)  # Restrict to admin/doctor
):
    try:
        assoc = DoctorPatientService.assign_patient_to_doctor_by_email(
            db, doctor_id, data.resolved_email, status=data.status, note=data.note
        )
        return assoc
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        if "already assigned" in msg:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

@router.patch("/doctors/{doctor_id}/patients/{patient_id}", response_model=DoctorPatientAssociationOut, tags=["Patient Management"])
def update_doctor_patient_association(
    doctor_id: int,
    patient_id: int,
    data: DoctorPatientAssociationIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_doctor)  # Restrict to admin/doctor
):
    try:
        assoc = DoctorPatientService.update_doctor_patient_association(
            db, doctor_id, patient_id, status=data.status, note=data.note
        )
        return assoc
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

@router.delete("/doctors/{doctor_id}/unassign-patient/{patient_id}", tags=["Patient Management"])
def unassign_patient_from_doctor(doctor_id: int, patient_id: int, db: Session = Depends(get_db), user: User = Depends(require_admin_or_doctor)):
    try:
        DoctorPatientService.unassign_patient_from_doctor(db, doctor_id, patient_id)
        return {"message": "Patient unassigned from doctor"}
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

# --- Patient Profile Endpoint ---
class PatientProfileResponse(BaseModel):
    user: UserOut
    patient: Optional[PatientOut]

@router.get("/patient/profile", response_model=PatientProfileResponse, tags=["User Management"])
def get_patient_profile(user: User = Depends(require_patient), db: Session = Depends(get_db)):
    """
    Get the profile of the currently logged-in patient, including both user and patient data.
    - Returns user info (id, name, email, role) and patient info (id, patient_id, name, email, birth_date, address, medical_note).
    - Only accessible to users with the 'patient' role.
    - Returns 404 if the patient profile is not found.
    """
    patient = db.query(Patient).filter(Patient.patient_id == user.id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return PatientProfileResponse(
        user=UserOut(id=user.id, name=user.name, email=user.email, role=str(user.role)),
        patient=PatientOut(
            id=patient.id,
            patient_id=patient.patient_id,
            name=user.name,
            email=user.email,
            birth_date=patient.birth_date,
            address=patient.address,
            medical_note=patient.medical_note
        )
    )
