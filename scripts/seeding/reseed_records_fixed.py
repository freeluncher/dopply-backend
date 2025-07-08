"""
Script untuk membersihkan tabel records dan seeding ulang dengan data baru
berdasarkan sistem fetal monitoring
"""

import os
import sys
from datetime import datetime, date, timedelta
from typing import List, Dict
import uuid
import random

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.medical import (
    User, Patient, Doctor, Record, RecordSource, Notification,
    FetalMonitoringSession, MonitoringType, FetalClassification,
    FetalHeartRateReading, FetalMonitoringResult, OverallClassification,
    RiskLevel, PregnancyInfo
)
from app.core.time_utils import get_local_naive_now

def clean_records_table(db: Session):
    """Bersihkan hanya tabel records"""
    print("🧹 Membersihkan tabel records...")
    
    try:
        # Hapus notifications yang reference ke records terlebih dahulu
        notifications_count = db.query(Notification).count()
        db.query(Notification).delete()
        print(f"🔔 Menghapus {notifications_count} notifications")
        
        # Hapus semua record lama
        deleted_count = db.query(Record).count()
        db.query(Record).delete()
        db.commit()
        print(f"✅ Berhasil menghapus {deleted_count} records lama")
    except Exception as e:
        print(f"❌ Error saat membersihkan records: {str(e)}")
        db.rollback()
        raise

def create_new_records_from_fetal_sessions(db: Session):
    """Buat records baru berdasarkan data fetal monitoring sessions"""
    print("📊 Membuat records baru dari fetal monitoring sessions...")
    
    # Ambil semua fetal monitoring sessions
    fetal_sessions = db.query(FetalMonitoringSession).all()
    
    new_records = []
    
    for session in fetal_sessions:
        # Ambil heart rate readings untuk session ini
        readings = db.query(FetalHeartRateReading).filter(
            FetalHeartRateReading.session_id == session.id
        ).all()
        
        # Ambil result untuk session ini
        result = db.query(FetalMonitoringResult).filter(
            FetalMonitoringResult.session_id == session.id
        ).first()
        
        # Convert readings ke format BPM data untuk records
        bpm_data = []
        for i, reading in enumerate(readings):
            # Hitung time relatif dari start_time (dalam detik)
            time_offset = int((reading.timestamp - session.start_time).total_seconds())
            bpm_data.append({
                "time": time_offset,
                "bpm": reading.bpm,
                "signal_quality": reading.signal_quality,
                "classification": reading.classification.value
            })
        
        # Tentukan classification untuk record berdasarkan result
        if result:
            if result.overall_classification == OverallClassification.normal:
                record_classification = "normal"
            elif result.overall_classification == OverallClassification.concerning:
                record_classification = "concerning" 
            else:
                record_classification = "abnormal"
        else:
            # Fallback classification berdasarkan readings
            normal_count = sum(1 for r in readings if r.classification == FetalClassification.normal)
            if normal_count / len(readings) > 0.8:
                record_classification = "normal"
            elif normal_count / len(readings) > 0.5:
                record_classification = "concerning"
            else:
                record_classification = "abnormal"
        
        # Tentukan source berdasarkan monitoring type
        if session.monitoring_type == MonitoringType.clinic:
            source = RecordSource.clinic
        else:
            source = RecordSource.self_
        
        # Buat notes yang komprehensif
        notes_parts = []
        if session.notes:
            notes_parts.append(f"Patient notes: {session.notes}")
        if session.doctor_notes:
            notes_parts.append(f"Doctor notes: {session.doctor_notes}")
        if result:
            notes_parts.append(f"Risk level: {result.risk_level.value}")
            if result.findings:
                notes_parts.append(f"Findings: {', '.join(result.findings)}")
            if result.recommendations:
                notes_parts.append(f"Recommendations: {', '.join(result.recommendations)}")
        
        combined_notes = " | ".join(notes_parts) if notes_parts else None
        
        # Buat record baru
        new_record = Record(
            patient_id=session.patient_id,
            doctor_id=session.doctor_id,
            source=source,
            bpm_data=bpm_data,
            start_time=session.start_time,
            end_time=session.end_time,
            classification=record_classification,
            notes=combined_notes,
            shared_with=session.doctor_id if session.shared_with_doctor else None
        )
        
        db.add(new_record)
        new_records.append(new_record)
    
    # Commit semua records baru
    db.commit()
    print(f"✅ Berhasil membuat {len(new_records)} records baru dari fetal sessions")
    
    return new_records

def create_additional_legacy_records(db: Session):
    """Buat beberapa records legacy tambahan untuk variasi data"""
    print("📋 Membuat records legacy tambahan...")
    
    # Ambil semua patients dan doctors
    patients = db.query(Patient).all()
    doctors = db.query(User).filter(User.role == "doctor").all()
    
    additional_records = []
    
    # Buat 10 records legacy tambahan
    for i in range(10):
        patient = random.choice(patients)
        doctor = random.choice(doctors)
        
        # Generate realistic BPM data
        duration_minutes = random.randint(5, 20)
        base_bpm = random.randint(130, 150)
        
        bpm_data = []
        for minute in range(duration_minutes):
            for second in range(0, 60, 15):  # Every 15 seconds
                time_offset = minute * 60 + second
                # Add some variability
                bpm = base_bpm + random.randint(-8, 8)
                bpm = max(110, min(180, bpm))
                
                bpm_data.append({
                    "time": time_offset,
                    "bpm": bpm
                })
        
        # Determine classification
        avg_bpm = sum(point["bpm"] for point in bpm_data) / len(bpm_data)
        if avg_bpm < 120:
            classification = "bradycardia"
        elif avg_bpm > 160:
            classification = "tachycardia"
        else:
            classification = "normal"
        
        # Random source
        source = random.choice([RecordSource.clinic, RecordSource.self_])
        
        # Create record
        start_time = get_local_naive_now() - timedelta(days=random.randint(1, 30))
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        record = Record(
            patient_id=patient.id,
            doctor_id=doctor.id if source == RecordSource.clinic else None,
            source=source,
            bpm_data=bpm_data,
            start_time=start_time,
            end_time=end_time,
            classification=classification,
            notes=f"Legacy monitoring record - {classification} pattern detected"
        )
        
        db.add(record)
        additional_records.append(record)
    
    db.commit()
    print(f"✅ Berhasil membuat {len(additional_records)} records legacy tambahan")
    
    return additional_records

def create_patient_self_monitoring_records(db: Session):
    """Buat records dari patient self-monitoring"""
    print("🏠 Membuat records self-monitoring dari patients...")
    
    patients = db.query(Patient).all()
    self_records = []
    
    # Setiap patient buat 2-3 self monitoring records
    for patient in patients:
        num_records = random.randint(2, 3)
        
        for j in range(num_records):
            # Generate simple BPM data untuk self monitoring
            duration_minutes = random.randint(10, 15)
            base_bpm = random.randint(135, 145)
            
            bpm_data = []
            for minute in range(duration_minutes):
                time_offset = minute * 60
                bpm = base_bpm + random.randint(-5, 5)
                bpm = max(120, min(170, bpm))
                
                bpm_data.append({
                    "time": time_offset,
                    "bpm": bpm
                })
            
            # Most self-monitoring will be normal
            classification = "normal" if random.random() > 0.2 else random.choice(["concerning", "irregular"])
            
            start_time = get_local_naive_now() - timedelta(days=random.randint(1, 14))
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Patient notes
            patient_notes = random.choice([
                "Feeling baby movements normally",
                "Some decreased movements noticed",
                "Active baby movements today",
                "Regular monitoring at home",
                "Following doctor's instructions"
            ])
            
            record = Record(
                patient_id=patient.id,
                doctor_id=None,  # Self monitoring
                source=RecordSource.self_,
                bpm_data=bpm_data,
                start_time=start_time,
                end_time=end_time,
                classification=classification,
                notes=patient_notes
            )
            
            db.add(record)
            self_records.append(record)
    
    db.commit()
    print(f"✅ Berhasil membuat {len(self_records)} records self-monitoring")
    
    return self_records

def update_existing_data_compatibility(db: Session):
    """Update data yang ada untuk kompatibilitas"""
    print("🔄 Memperbarui kompatibilitas data...")
    
    # Update pregnancy info jika diperlukan
    pregnancy_infos = db.query(PregnancyInfo).all()
    for pregnancy_info in pregnancy_infos:
        # Pastikan tanggal masih valid
        if pregnancy_info.expected_due_date and pregnancy_info.expected_due_date < date.today():
            # Update ke tanggal yang masuk akal
            weeks_remaining = 40 - pregnancy_info.gestational_age
            pregnancy_info.expected_due_date = date.today() + timedelta(weeks=max(1, weeks_remaining))
            pregnancy_info.updated_at = get_local_naive_now()
    
    db.commit()
    print("✅ Data compatibility updated")

def print_summary(db: Session):
    """Cetak ringkasan data setelah seeding"""
    print("\n" + "="*60)
    print("📊 RINGKASAN DATA SETELAH SEEDING")
    print("="*60)
    
    # Count records
    total_records = db.query(Record).count()
    clinic_records = db.query(Record).filter(Record.source == RecordSource.clinic).count()
    self_records = db.query(Record).filter(Record.source == RecordSource.self_).count()
    
    # Count by classification
    normal_records = db.query(Record).filter(Record.classification == "normal").count()
    concerning_records = db.query(Record).filter(Record.classification == "concerning").count()
    abnormal_records = db.query(Record).filter(Record.classification.in_(["abnormal", "bradycardia", "tachycardia", "irregular"])).count()
    
    # Count fetal monitoring data
    fetal_sessions = db.query(FetalMonitoringSession).count()
    fetal_readings = db.query(FetalHeartRateReading).count()
    fetal_results = db.query(FetalMonitoringResult).count()
    
    print(f"📋 Total Records: {total_records}")
    print(f"   🏥 Clinic Records: {clinic_records}")
    print(f"   🏠 Self Monitoring: {self_records}")
    print()
    print(f"📊 Classification Breakdown:")
    print(f"   ✅ Normal: {normal_records}")
    print(f"   ⚠️ Concerning: {concerning_records}")
    print(f"   🚨 Abnormal: {abnormal_records}")
    print()
    print(f"🤱 Fetal Monitoring Data:")
    print(f"   📝 Sessions: {fetal_sessions}")
    print(f"   💓 Heart Rate Readings: {fetal_readings}")
    print(f"   📊 Analysis Results: {fetal_results}")
    print("="*60)

def recreate_notifications(db: Session):
    """Buat ulang notifications berdasarkan records baru"""
    print("🔔 Membuat ulang notifications...")
    
    # Ambil beberapa records untuk membuat notifications
    records = db.query(Record).filter(Record.doctor_id.isnot(None)).limit(5).all()
    
    notifications = []
    for record in records:
        # Hanya buat notification jika ada doctor_id
        if record.doctor_id:
            from app.models.medical import NotificationStatus
            notification = Notification(
                from_patient_id=record.patient_id,
                to_doctor_id=record.doctor_id,
                record_id=record.id,
                status=NotificationStatus.unread
            )
            db.add(notification)
            notifications.append(notification)
    
    db.commit()
    print(f"✅ Berhasil membuat {len(notifications)} notifications baru")
    
    return notifications

def main():
    """Main function untuk membersihkan dan seed ulang records"""
    print("🔄 MEMBERSIHKAN DAN SEEDING ULANG TABEL RECORDS")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Step 1: Bersihkan tabel records
        clean_records_table(db)
        
        # Step 2: Buat records baru dari fetal monitoring sessions
        fetal_records = create_new_records_from_fetal_sessions(db)
        
        # Step 3: Buat records legacy tambahan
        legacy_records = create_additional_legacy_records(db)
        
        # Step 4: Buat records self-monitoring
        self_records = create_patient_self_monitoring_records(db)
        
        # Step 5: Buat ulang notifications
        recreate_notifications(db)
        
        # Step 6: Update kompatibilitas data
        update_existing_data_compatibility(db)
        
        # Step 7: Cetak ringkasan
        print_summary(db)
        
        # Step 7: Buat ulang notifications
        recreate_notifications(db)
        
        print("\n🎉 SEEDING RECORDS BERHASIL DISELESAIKAN!")
        print("💡 Records telah diperbarui berdasarkan data fetal monitoring terbaru")
        
    except Exception as e:
        print(f"❌ Error during records seeding: {str(e)}")
        db.rollback()
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
