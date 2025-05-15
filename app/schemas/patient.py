from pydantic import BaseModel
from typing import Optional
from datetime import date

class PatientCreate(BaseModel):
    name: str
    email: str
    password: str
    birth_date: Optional[date] = None
    address: Optional[str] = None
    medical_note: Optional[str] = None

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    birth_date: Optional[date] = None
    address: Optional[str] = None
    medical_note: Optional[str] = None

class PatientOut(BaseModel):
    id: int
    name: str
    email: str
    birth_date: Optional[date]
    address: Optional[str]
    medical_note: Optional[str]

    class Config:
        orm_mode = True
