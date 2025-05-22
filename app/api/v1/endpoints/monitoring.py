from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from app.db.session import SessionLocal
from app.models.medical import Record, Patient, User
from datetime import datetime
from sqlalchemy import desc
from app.services.monitoring_service import MonitoringService

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
    try:
        result = MonitoringService.process_monitoring_result(db, req.patient_id, req.bpm_data, req.doctor_note)
        return MonitoringResponse(**result)
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)

# --- Klasifikasi BPM ---
class BPMDataPoint(BaseModel):
    time: int
    bpm: int

class ClassifyBPMRequest(BaseModel):
    bpm_data: List[BPMDataPoint]

class ClassifyBPMResponse(BaseModel):
    result: str
    classification: str

@router.post("/classify_bpm", response_model=ClassifyBPMResponse)
def classify_bpm(req: ClassifyBPMRequest):
    try:
        bpm_data = [point.dict() for point in req.bpm_data]
        result = MonitoringService.classify_bpm(bpm_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Simpan Riwayat Monitoring ---
class MonitoringRecordBPMData(BaseModel):
    time: int
    bpm: int

class MonitoringRecordRequest(BaseModel):
    patient_id: int
    doctor_id: int
    start_time: datetime
    end_time: datetime
    bpm_data: List[MonitoringRecordBPMData]
    result: str
    classification: str
    doctor_note: Optional[str] = None

@router.post("/monitoring_record", status_code=201)
def save_monitoring_record(req: MonitoringRecordRequest, db: Session = Depends(get_db)):
    try:
        result = MonitoringService.save_monitoring_record(db, req)
        return result
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)
