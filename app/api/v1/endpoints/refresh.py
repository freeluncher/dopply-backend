from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from app.schemas.refresh import RefreshTokenRequest, RefreshTokenResponse, ErrorResponse
from app.db.session import SessionLocal
from app.core.security import verify_refresh_token, create_access_token, create_refresh_token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/refresh", 
            response_model=RefreshTokenResponse, 
            tags=["Authentication"],
            summary="🔄 Refresh Access Token",
            description="Exchange a valid refresh token for a new access token and optionally a new refresh token",
            responses={
                200: {
                    "description": "Successfully refreshed tokens",
                    "content": {
                        "application/json": {
                            "example": {
                                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                                "token_type": "bearer"
                            }
                        }
                    }
                },
                401: {
                    "description": "Invalid or expired refresh token",
                    "content": {
                        "application/json": {
                            "example": {
                                "status": "error",
                                "message": "Refresh token invalid or expired"
                            }
                        }
                    }
                }
            })
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using a valid refresh token.
    
    - **refresh_token**: Valid refresh token obtained from login
    
    Returns new access token and optionally a new refresh token.
    """
    try:
        # Verify refresh token
        payload = verify_refresh_token(request.refresh_token)
        user_email = payload.get("sub")
        
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user from database
        from app.models.medical import User
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Build JWT payload with full user data
        role_value = user.role.value if hasattr(user.role, 'value') else str(user.role)
        jwt_payload = {
            "sub": user.email,
            "id": user.id,
            "email": user.email,
            "role": role_value,
            "name": user.name,
        }
        
        if hasattr(user, "photo_url") and user.photo_url:
            jwt_payload["photo_url"] = user.photo_url
        
        # Add doctor-specific data if applicable
        if role_value == "doctor":
            from app.models.medical import Doctor
            doctor = db.query(Doctor).filter(Doctor.doctor_id == user.id).first()
            if doctor:
                jwt_payload["is_valid"] = doctor.is_valid
                jwt_payload["doctor_id"] = doctor.doctor_id
        
        # Create new access token
        access_token = create_access_token(jwt_payload)
        
        # Optionally create new refresh token (for token rotation security)
        # For now, we'll return the same refresh token
        # In production, you might want to implement token rotation
        
        return RefreshTokenResponse(
            access_token=access_token,
            refresh_token=request.refresh_token,  # Return same refresh token
            token_type="bearer"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalid or expired"
        )
