from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.medical import User
from app.core.dependencies import get_current_user

router = APIRouter(tags=["Authentication"])

@router.get("/token/verify")
def verify_token(current_user: User = Depends(get_current_user)):
    """Verify JWT token and return user information"""
    print(f"[DEBUG] token/verify - User found: ID={current_user.id}, role={current_user.role}")
    
    response = {
        "user_id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    }
    
    # If user is a doctor, include is_valid from users table
    if response["role"] == "doctor":
        response["is_valid"] = current_user.is_verified if current_user.is_verified is not None else False
        response["doctor_id"] = current_user.id
        print(f"[DEBUG] token/verify - Doctor data: is_valid={current_user.is_verified}, doctor_id={current_user.id}")
    
    print(f"[DEBUG] token/verify - Final response: {response}")
    return response