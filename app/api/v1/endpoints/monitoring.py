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
    bpm_values = [point.bpm for point in req.bpm_data]
    if not bpm_values:
        raise HTTPException(status_code=400, detail="bpm_data required")
    avg_bpm = sum(bpm_values) / len(bpm_values)
    if avg_bpm < 60:
        result = "pathologic"
        classification = "bradikardia"
    elif avg_bpm > 100:
        result = "pathologic"
        classification = "takikardia"
    else:
        result = "normal"
        classification = "normal"
    # Bisa tambahkan logika lain (suspect, dst) sesuai kebutuhan
    return {"result": result, "classification": classification}

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
    import logging
    logger = logging.getLogger("uvicorn")
    logger.info(f"[MONITORING_RECORD] patient_id={req.patient_id}, doctor_id={req.doctor_id}, start_time={req.start_time}, end_time={req.end_time}, bpm_data={req.bpm_data}, result={req.result}, classification={req.classification}, doctor_note={req.doctor_note}")
    # Perbaiki: cari berdasarkan patient_id (FK ke users.id)
    patient = db.query(Patient).filter(Patient.patient_id == req.patient_id).first()
    if not patient:
        logger.warning(f"[MONITORING_RECORD] Patient not found: {req.patient_id}")
        raise HTTPException(status_code=404, detail="Patient not found")
    record = Record(
        patient_id=patient.id,  # Simpan PK patients.id ke records.patient_id
        doctor_id=req.doctor_id,
        source="clinic",  # atau sesuai kebutuhan
        bpm_data=[{"time": d.time, "bpm": d.bpm} for d in req.bpm_data],
        start_time=req.start_time,
        end_time=req.end_time,
        classification=req.classification,
        notes=req.doctor_note,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info(f"[MONITORING_RECORD] Record saved: id={record.id}")
    return {"status": "success", "record_id": record.id}
