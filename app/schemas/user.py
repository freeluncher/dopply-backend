from pydantic import BaseModel

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    name: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "name": "string",
                "password": "string"
            }
        }
