from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class RecordOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: Optional[int]
    source: str
    bpm_data: Any
    start_time: datetime
    end_time: Optional[datetime]
    classification: Optional[str]
    notes: Optional[str]
    shared_with: Optional[int]
    patient_name: Optional[str]  # Tambahkan field ini

    class Config:
        orm_mode = True
