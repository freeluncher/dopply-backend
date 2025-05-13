from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut, LoginRequest
from app.models.medical import User
from app.db.session import SessionLocal
from app.core.security import verify_password, get_password_hash, create_access_token
from datetime import timedelta

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def login_user(user: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": db_user.email}, expires_delta=timedelta(minutes=30))
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "role": db_user.role.value
    }

@router.post("/register", response_model=UserOut, status_code=201)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if user.role not in ["patient", "doctor"]:
        raise HTTPException(status_code=400, detail="Role must be 'patient' or 'doctor'")
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    if user.role == "doctor":
        new_user = User(
            name=user.name,
            email=user.email,
            password_hash=hashed_password,
            role="doctor"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        # Di sini Anda bisa menambahkan notifikasi ke admin atau flag is_active=False jika ingin
        # Contoh: new_user.is_active = False (jika ada field is_active)
        # db.commit()
        return {**new_user.__dict__, "message": "Registration as doctor submitted, waiting for admin approval."}
    else:
        new_user = User(
            name=user.name,
            email=user.email,
            password_hash=hashed_password,
            role="patient"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        # Pastikan import Patient di sini untuk menghindari circular import
        from app.models.medical import Patient
        new_patient = Patient(user_id=new_user.id)
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        return new_user
