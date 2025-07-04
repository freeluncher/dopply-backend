from pydantic import BaseModel, validator, EmailStr
from typing import Optional
from datetime import date

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str
    role: str = "patient"  # hanya boleh 'patient' atau 'doctor' saat register

    @validator('role')
    def validate_role(cls, v):
        if v not in ('patient', 'doctor'):
            raise ValueError('Role must be either "patient" or "doctor"')
        return v

class UserOut(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    email: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "user@email.com",
                "password": "string"
            }
        }

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str  # 'patient' atau 'doctor'
    birth_date: Optional[date] = None
    address: Optional[str] = None
    medical_note: Optional[str] = None

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: Optional[bool] = None
    photo_url: Optional[str] = None

    class Config:
        orm_mode = True
