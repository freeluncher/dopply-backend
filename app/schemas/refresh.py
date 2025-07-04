from pydantic import BaseModel
from typing import Optional

class RefreshTokenRequest(BaseModel):
    refresh_token: str
    
    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }

class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    # User data
    id: int
    email: str
    role: str
    name: str
    photo_url: Optional[str] = None
    is_valid: Optional[bool] = None
    doctor_id: Optional[int] = None

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
