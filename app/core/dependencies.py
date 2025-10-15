from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.medical import User
from app.core.security import verify_jwt_token

# Global security instance - avoid duplication
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_db)
) -> User:
    """
    Global dependency to get current authenticated user.
    Used across all endpoints to avoid code duplication.
    """
    token = credentials.credentials
    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_email = payload.get("sub")
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

def require_role(allowed_roles: list[str]):
    """
    Decorator factory to check user roles.
    Usage: @require_role(["doctor", "admin"])
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role.value not in allowed_roles:
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
        return current_user
    return role_checker

def require_patient(current_user: User = Depends(get_current_user)):
    """Dependency to ensure user is a patient"""
    if current_user.role.value != "patient":
        raise HTTPException(status_code=403, detail="Patient access required")
    return current_user

def require_doctor(current_user: User = Depends(get_current_user)):
    """Dependency to ensure user is a doctor"""
    if current_user.role.value != "doctor":
        raise HTTPException(status_code=403, detail="Doctor access required")
    return current_user

def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to ensure user is an admin"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user