# Service layer for monitoring endpoints (bpm classification, monitoring record, etc.)
from sqlalchemy.orm import Session
from app.models.medical import Record, Patient
from datetime import datetime
from app.core.time_utils import get_local_naive_now
from typing import List, Optional, Dict, Any
import logging

class MonitoringService:
    @staticmethod
    def process_monitoring_result(db: Session, patient_id: int, bpm_data: List[int], doctor_note: Optional[str] = None, doctor_id: Optional[int] = None) -> Dict[str, Any]:
        logger = logging.getLogger("uvicorn")
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise ValueError("Patient not found")
        if not bpm_data or not isinstance(bpm_data, list):
            raise ValueError("Invalid bpm_data")
        avg_bpm = sum(bpm_data) / len(bpm_data)
        classification = "normal"
        abnormal_type = None
        if avg_bpm < 60:
            classification = "abnormal"
            abnormal_type = "bradikardia"
        elif avg_bpm > 100:
            classification = "abnormal"
            abnormal_type = "takikardia"
        elif max(bpm_data) - min(bpm_data) > 40:
            classification = "abnormal"
            abnormal_type = "atrial fibrilasi"
        # Gunakan zona waktu lokal Indonesia (WIB) 
        start_time = get_local_naive_now()
        end_time = get_local_naive_now()
        logger.info(f"[MONITORING_RECORD] Akan insert record: patient_id={patient_id}, doctor_id={doctor_id}, classification={classification}, start_time={start_time}, end_time={end_time}")
        new_record = Record(
            patient_id=patient_id,
            doctor_id=doctor_id,
            source="clinic",
            bpm_data=bpm_data,
            start_time=start_time,
            end_time=end_time,
            classification=classification,
            notes=doctor_note,
            shared_with=None
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        logger.info(f"[MONITORING_RECORD] Record berhasil di-insert: id={new_record.id}, doctor_id={new_record.doctor_id}")
        return {
            "patient_id": patient_id,
            "bpm_data": bpm_data,
            "classification": classification,
            "abnormal_type": abnormal_type,
            "doctor_note": doctor_note,
            "start_time": start_time,
            "end_time": end_time,
            "record_id": new_record.id
        }

    @staticmethod
    def classify_bpm(bpm_data: List[Dict[str, int]]) -> Dict[str, str]:
        bpm_values = [point["bpm"] for point in bpm_data]
        if not bpm_values:
            raise ValueError("bpm_data required")
        avg_bpm = sum(bpm_values) / len(bpm_values)
        if avg_bpm < 110:
            result = "pathologic"
            classification = "bradikardia"
        elif avg_bpm > 160:
            result = "pathologic"
            classification = "takikardia"
        else:
            result = "normal"
            classification = "normal"
        return {"result": result, "classification": classification}

    @staticmethod
    def save_monitoring_record(db: Session, req: Any) -> Dict[str, Any]:
        logger = logging.getLogger("uvicorn")
        logger.info(f"[MONITORING_RECORD] patient_id={req.patient_id}, doctor_id={req.doctor_id}, start_time={req.start_time}, end_time={req.end_time}, bpm_data={req.bpm_data}, result={req.result}, classification={req.classification}, doctor_note={req.doctor_note}")
        patient = db.query(Patient).filter(Patient.patient_id == req.patient_id).first()
        if not patient:
            logger.warning(f"[MONITORING_RECORD] Patient not found: {req.patient_id}")
            raise ValueError("Patient not found")
        record = Record(
            patient_id=patient.id,
            doctor_id=req.doctor_id,
            source="clinic",
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
