from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from app.db.session import SessionLocal
from app.models.medical import Record, Patient, User
from datetime import datetime
from sqlalchemy import desc

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class MonitoringRequest(BaseModel):
    patient_id: int
    bpm_data: List[int]
    doctor_note: Optional[str] = None

class MonitoringResponse(BaseModel):
    patient_id: int
    bpm_data: List[int]
    classification: str
    abnormal_type: Optional[str] = None
    doctor_note: Optional[str] = None
    start_time: datetime
    end_time: datetime
    record_id: int

@router.post("/monitoring", response_model=MonitoringResponse)
def send_monitoring_result(
    req: MonitoringRequest,
    db: Session = Depends(get_db)
):
    # 1. Validasi pasien
    patient = db.query(Patient).filter(Patient.id == req.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # 2. Proses klasifikasi detak jantung
    bpm_data = req.bpm_data
    if not bpm_data or not isinstance(bpm_data, list):
        raise HTTPException(status_code=400, detail="Invalid bpm_data")
    avg_bpm = sum(bpm_data) / len(bpm_data)
    classification = "normal"
    abnormal_type = None
    # Contoh logika sederhana, bisa diganti dengan ML/AI
    if avg_bpm < 60:
        classification = "abnormal"
        abnormal_type = "bradikardia"
    elif avg_bpm > 100:
        classification = "abnormal"
        abnormal_type = "takikardia"
    # Deteksi atrial fibrilasi (contoh: variasi bpm sangat tinggi)
    elif max(bpm_data) - min(bpm_data) > 40:
        classification = "abnormal"
        abnormal_type = "atrial fibrilasi"

    # 3. Simpan ke database
    start_time = datetime.utcnow()
    end_time = datetime.utcnow()
    new_record = Record(
        patient_id=req.patient_id,
        doctor_id=None,  # Diisi jika ada autentikasi dokter
        source="clinic",
        bpm_data=bpm_data,
        start_time=start_time,
        end_time=end_time,
        classification=classification,
        notes=req.doctor_note,
        shared_with=None
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return MonitoringResponse(
        patient_id=req.patient_id,
        bpm_data=bpm_data,
        classification=classification,
        abnormal_type=abnormal_type,
        doctor_note=req.doctor_note,
        start_time=start_time,
        end_time=end_time,
        record_id=new_record.id
    )
