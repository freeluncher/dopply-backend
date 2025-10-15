"""
BPM Statistics Calculator
Utility functions untuk menghitung statistik BPM dari data yang ada
tanpa perlu mengubah skema database.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime

def calculate_bpm_statistics(bpm_data: Any) -> Dict[str, Any]:
    """
    Menghitung statistik BPM dari data yang tersimpan
    
    Args:
        bpm_data: Data BPM dalam format JSON (list integer) atau string JSON
        
    Returns:
        Dict dengan avg_bpm, min_bpm, max_bpm
    """
    try:
        # Handle berbagai format input
        if isinstance(bpm_data, str):
            bpm_list = json.loads(bpm_data)
        elif isinstance(bpm_data, list):
            bpm_list = bpm_data
        elif bpm_data is None:
            return {"avg_bpm": 0, "min_bpm": 0, "max_bpm": 0}
        else:
            return {"avg_bpm": 0, "min_bpm": 0, "max_bpm": 0}
        
        if not bpm_list or len(bpm_list) == 0:
            return {"avg_bpm": 0, "min_bpm": 0, "max_bpm": 0}
            
        # Convert to integers untuk safety
        bpm_integers = [int(bpm) for bpm in bpm_list if isinstance(bpm, (int, float, str)) and str(bpm).isdigit()]
        
        if not bpm_integers:
            return {"avg_bpm": 0, "min_bpm": 0, "max_bpm": 0}
            
        avg_bpm = round(sum(bpm_integers) / len(bpm_integers))
        min_bpm = min(bpm_integers) 
        max_bpm = max(bpm_integers)
        
        return {
            "avg_bpm": avg_bpm,
            "min_bpm": min_bpm,
            "max_bpm": max_bpm
        }
        
    except Exception as e:
        # Fallback jika parsing gagal
        return {"avg_bpm": 0, "min_bpm": 0, "max_bpm": 0}

def calculate_duration_seconds(start_time: datetime, end_time: Optional[datetime] = None, monitoring_duration: Optional[float] = None) -> int:
    """
    Menghitung durasi monitoring dalam detik
    
    Args:
        start_time: Waktu mulai monitoring
        end_time: Waktu selesai monitoring (optional)
        monitoring_duration: Durasi dalam menit (optional)
        
    Returns:
        Durasi dalam detik
    """
    try:
        if end_time and start_time:
            # Hitung dari selisih waktu
            delta = end_time - start_time
            return int(delta.total_seconds())
        elif monitoring_duration:
            # Konversi dari menit ke detik
            return int(monitoring_duration * 60)
        else:
            return 0
    except Exception:
        return 0

def is_shared_with_doctor(shared_with: Optional[int]) -> bool:
    """
    Cek apakah record sudah dishare dengan dokter
    
    Args:
        shared_with: ID dokter yang dibagikan (dari field shared_with)
        
    Returns:
        True jika sudah dishare, False jika belum
    """
    return shared_with is not None

def format_record_for_api(record, patient_name: str = None) -> Dict[str, Any]:
    """
    Format record database menjadi format API yang konsisten
    
    Args:
        record: Record object dari database
        patient_name: Nama pasien (optional)
        
    Returns:
        Dictionary dengan format API yang diharapkan
    """
    # Hitung statistik BPM
    bpm_stats = calculate_bpm_statistics(record.bpm_data)
    
    # Hitung durasi dalam detik
    duration_sec = calculate_duration_seconds(
        record.start_time, 
        record.end_time, 
        record.monitoring_duration
    )
    
    # Format response
    formatted_record = {
        "id": record.id,
        "patientId": record.patient_id,
        "avgBpm": bpm_stats["avg_bpm"],
        "minBpm": bpm_stats["min_bpm"], 
        "maxBpm": bpm_stats["max_bpm"],
        "duration": duration_sec,
        "classification": record.classification or "unknown",
        "sharedWithDoctor": is_shared_with_doctor(record.shared_with),
        "timestamp": record.start_time.isoformat() if record.start_time else None,
        "createdAt": record.start_time.isoformat() if record.start_time else None,
        "gestationalAge": record.gestational_age,
        "notes": record.notes,
        "doctorNotes": record.doctor_notes
    }
    
    # Tambahkan patient name jika ada
    if patient_name:
        formatted_record["patientName"] = patient_name
        
    # Tambahkan doctor info jika ada
    if record.doctor_id:
        formatted_record["doctorId"] = record.doctor_id
        if hasattr(record, 'doctor') and record.doctor:
            formatted_record["doctorName"] = record.doctor.name
            
    return formatted_record