from pydantic import BaseModel, validator

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
