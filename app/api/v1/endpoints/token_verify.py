from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.medical import User, Doctor
from app.core.security import verify_jwt_token

router = APIRouter()
security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/token/verify", tags=["Authentication"])
def verify_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = verify_jwt_token(token)
        print(f"[DEBUG] token/verify - JWT payload: {payload}")
    except Exception as e:
        print(f"[DEBUG] token/verify - JWT verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        print(f"[DEBUG] token/verify - User not found for email: {payload['sub']}")
        raise HTTPException(status_code=401, detail="Invalid token or user not found")
    
    print(f"[DEBUG] token/verify - User found: ID={user.id}, role={user.role}")
    
    response = {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role)
    }
    
    # If user is a doctor, include is_valid from doctors table
    if response["role"] == "doctor":
        doctor = db.query(Doctor).filter(Doctor.doctor_id == user.id).first()
        if doctor:
            response["is_valid"] = doctor.is_valid
            response["doctor_id"] = doctor.doctor_id
            print(f"[DEBUG] token/verify - Doctor data: is_valid={doctor.is_valid}, doctor_id={doctor.doctor_id}")
        else:
            response["is_valid"] = False
            print(f"[DEBUG] token/verify - No doctor record found for user {user.id}")
    
    print(f"[DEBUG] token/verify - Final response: {response}")
    return response