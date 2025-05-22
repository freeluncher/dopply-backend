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
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import status

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

# --- Unified Account Endpoints ---
from sqlalchemy.exc import IntegrityError

@router.put("/account/email")
def change_email_unified(
    req: ChangeEmailUnifiedRequest,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    token = credentials.credentials
    payload = verify_jwt_token(token)
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail={"error": "User not found"})
    if db.query(User).filter(User.email == req.newEmail).first():
        raise HTTPException(status_code=409, detail={"error": "Email already in use"})
    user.email = req.newEmail
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail={"error": "Email already in use"})
    return {"message": "Email updated successfully"}

@router.put("/account/password")
def change_password_unified(
    req: ChangePasswordUnifiedRequest,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    token = credentials.credentials
    payload = verify_jwt_token(token)
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail={"error": "User not found"})
    if not verify_password(req.oldPassword, user.password_hash):
        raise HTTPException(status_code=400, detail={"error": "Current password is incorrect"})
    user.password_hash = get_password_hash(req.newPassword)
    db.commit()
    db.refresh(user)
    return {"message": "Password updated successfully"}

# --- Admin User Management Endpoints ---

def require_admin(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    payload = verify_jwt_token(token)
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user or (hasattr(user.role, 'value') and user.role.value != "admin") and (str(user.role) != "admin"):
        raise HTTPException(status_code=403, detail={"error": "Admin access required"})
    return user

@router.get("/users", response_model=List[UserOut])
def get_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    users = db.query(User).all()
    return [UserOut(id=u.id, name=u.name, email=u.email, role=str(u.role)) for u in users]

@router.post("/users")
def create_user(
    req: UserCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=409, detail={"error": "Email already in use"})
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
        raise HTTPException(status_code=409, detail={"error": "Email already in use"})
    return {"id": user.id, "message": "User created successfully"}

@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    req: UserUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail={"error": "User not found"})
    if db.query(User).filter(User.email == req.email, User.id != user_id).first():
        raise HTTPException(status_code=409, detail={"error": "Email already in use"})
    user.name = req.name
    user.email = req.email
    user.role = req.role
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail={"error": "Email already in use"})
    return {"message": "User updated successfully"}

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail={"error": "User not found"})
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

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

@router.put("/account/email")
async def change_account_email(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user_role)):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid request body"})
    new_email = body.get("newEmail")
    if not new_email:
        return JSONResponse(status_code=400, content={"error": "newEmail is required"})
    if db.query(User).filter(User.email == new_email).first():
        return JSONResponse(status_code=409, content={"error": "Email already in use"})
    user.email = new_email
    db.commit()
    db.refresh(user)
    return {"message": "Email updated successfully"}

@router.put("/account/password")
async def change_account_password(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user_role)):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid request body"})
    old_password = body.get("oldPassword")
    new_password = body.get("newPassword")
    if not old_password or not new_password:
        return JSONResponse(status_code=400, content={"error": "Both oldPassword and newPassword are required"})
    if not verify_password(old_password, user.password_hash):
        return JSONResponse(status_code=400, content={"error": "Old password is incorrect"})
    user.password_hash = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return {"message": "Password updated successfully"}

# --- User Management Endpoints (Admin Only) ---
@router.get("/users")
def get_users(db: Session = Depends(get_db), user: User = Depends(get_current_user_role)):
    if (hasattr(user.role, 'value') and user.role.value != "admin") and (str(user.role) != "admin"):
        return JSONResponse(status_code=403, content={"error": "Admin access required"})
    users = db.query(User).all()
    return [{"id": u.id, "name": u.name, "email": u.email, "role": u.role.value if hasattr(u.role, 'value') else str(u.role)} for u in users]

@router.post("/users")
async def create_user(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user_role)):
    if (hasattr(user.role, 'value') and user.role.value != "admin") and (str(user.role) != "admin"):
        return JSONResponse(status_code=403, content={"error": "Admin access required"})
    body = await request.json()
    name = body.get("name")
    email = body.get("email")
    role = body.get("role")
    if not name or not email or not role:
        return JSONResponse(status_code=400, content={"error": "name, email, and role are required"})
    if db.query(User).filter(User.email == email).first():
        return JSONResponse(status_code=409, content={"error": "Email already in use"})
    from app.core.security import get_password_hash
    user_obj = User(name=name, email=email, password_hash=get_password_hash("default123"), role=role)
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return {"id": user_obj.id, "message": "User created successfully"}

@router.put("/users/{id}")
async def update_user(id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user_role)):
    if (hasattr(user.role, 'value') and user.role.value != "admin") and (str(user.role) != "admin"):
        return JSONResponse(status_code=403, content={"error": "Admin access required"})
    body = await request.json()
    name = body.get("name")
    email = body.get("email")
    role = body.get("role")
    user_obj = db.query(User).filter(User.id == id).first()
    if not user_obj:
        return JSONResponse(status_code=404, content={"error": "User not found"})
    if email and email != user_obj.email and db.query(User).filter(User.email == email).first():
        return JSONResponse(status_code=409, content={"error": "Email already in use"})
    if name:
        user_obj.name = name
    if email:
        user_obj.email = email
    if role:
        user_obj.role = role
    db.commit()
    db.refresh(user_obj)
    return {"message": "User updated successfully"}

@router.delete("/users/{id}")
def delete_user(id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user_role)):
    if (hasattr(user.role, 'value') and user.role.value != "admin") and (str(user.role) != "admin"):
        return JSONResponse(status_code=403, content={"error": "Admin access required"})
    user_obj = db.query(User).filter(User.id == id).first()
    if not user_obj:
        return JSONResponse(status_code=404, content={"error": "User not found"})
    db.delete(user_obj)
    db.commit()
    return {"message": "User deleted successfully"}
