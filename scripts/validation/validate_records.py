"""
Script validasi untuk memverifika    valid_b    print("🔍    v    valid_bpm_structure = 0
    for record in records_with_bpm[:5]:  # Check first 5id_bmp_structure = 0
    for record in records_with_bpm[:5]:  # Check fir    reco    records_without_b                if isinstance(reading, dict) and "bpm" in reading:
                    bpm = reading["bpm"]
                    if not isinstance(bpm, int) or bpm < 60 or bpm > 300:= db.query(Record).filter(
        (Record.bpm_data.is_(None)) | 
        (Record.bpm_data == '[]')
    ).count()
    if records_without_bpm > 0:
        issues.append(f"⚠️ {records_without_bpm} records tanpa BPM data")tho        if record.bpm_data:
            for reading in record.bpm_data:
                if isinstance(reading, dict) and "bpm" in reading:
                    bpm = reading["bpm"]
                    if not isinstance(bpm, int) or bpm < 60 or bpm > 300:m = db.query(Record).filter(
        (Record.bpm_data.is_(None)) | 
        (Record.bpm_data == '[]')
    ).count()
    if records_without_bpm > 0:
        issues.append(f"⚠️ {records_without_bpm} records tanpa BPM data")        if isinstance(record.bpm_data, list) and len(record.bpm_data) > 0:
            first_reading = record.bpm_data[0]
            if isinstance(first_reading, dict) and "time" in first_reading and "bpm" in first_reading:
                valid_bmp_structure += 1asi struktur BPM data:")
    records_with_bpm = db.query(Record).filter(Record.bpm_data.isnot(None)).all()
    
    valid_bpm_structure = 0
    for record in records_with_bpm[:5]:  # Check first 5
        if isinstance(record.bpm_data, list) and len(record.bpm_data) > 0:
            first_reading = record.bpm_data[0]
            if isinstance(first_reading, dict) and "time" in first_reading and "bpm" in first_reading:
                valid_bpm_structure += 1
    
    print(f"   ✅ Records dengan struktur BPM valid: {valid_bpm_structure}/5 (sample)")e = 0
    for record in records_with_bpm[:5]:  # Check first 5
        if isinstance(record.bpm_data, list) and len(record.bpm_data) > 0:
    records_without_bpm = db.query(Record).filter(
        (Record.bpm_data.is_(None)) | 
        (Record.bpm_data == '[]')
    ).count()
    if records_without_bpm > 0:
        issues.append(f"⚠️ {records_without_bpm} records tanpa BPM data")
    if record.bpm_data:
        for reading in record.bpm_data:
            if isinstance(reading, dict) and "bpm" in reading:
                bpm = reading["bpm"]
                if not isinstance(bpm, int) or bpm < 60 or bpm > 300:
                    issues.append(f"⚠️ Record {record.id} memiliki BPM tidak valid: {bpm}")
    ).count()
    if records_without_bpm > 0:
        issues.append(f"⚠️ {records_without_bpm} records tanpa BPM data")      first_reading = record.bpm_data[0]
            if isinstance(first_reading, dict) and "time" in first_reading and "bpm" in first_reading:
                valid_bpm_structure += 1a records yang baru di-seed
"""

import os
import sys
from datetime import datetime, date

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import SessionLocal
from app.models.medical import (
    User, Patient, Doctor, Record, RecordSource, Notification,
    FetalMonitoringSession, MonitoringType, FetalHeartRateReading, FetalMonitoringResult,
    PregnancyInfo
)

def validate_records_data(db: Session):
    """Validasi data records yang baru"""
    print("🔍 VALIDASI DATA RECORDS BARU")
    print("="*60)
    
    # 1. Statistik dasar
    total_records = db.query(Record).count()
    clinic_records = db.query(Record).filter(Record.source == RecordSource.clinic).count()
    self_records = db.query(Record).filter(Record.source == RecordSource.self_).count()
    
    print(f"📊 Total Records: {total_records}")
    print(f"   🏥 Clinic: {clinic_records}")
    print(f"   🏠 Self: {self_records}")
    print()
    
    # 2. Validasi struktur BPM data
    print("🔍 Validasi struktur BPM data:")
    records_with_bpm = db.query(Record).filter(Record.bpm_data.isnot(None)).all()
    
    valid_bpm_structure = 0
    for record in records_with_bpm[:5]:  # Check first 5
        if isinstance(record.bpm_data, list) and len(record.bpm_data) > 0:
            first_reading = record.bpm_data[0]
            if isinstance(first_reading, dict) and "time" in first_reading and "bpm" in first_reading:
                valid_bpm_structure += 1
    
    print(f"   ✅ Records dengan struktur BPM valid: {valid_bpm_structure}/5 (sample)")
    print()
    
    # 3. Validasi relasi dengan fetal monitoring
    print("🔗 Validasi relasi dengan fetal monitoring:")
    fetal_sessions = db.query(FetalMonitoringSession).count()
    records_from_fetal = db.query(Record).filter(
        Record.notes.like('%Risk level:%') | 
        Record.notes.like('%Findings:%') |
        Record.notes.like('%Recommendations:%')
    ).count()
    
    print(f"   📝 Fetal Sessions: {fetal_sessions}")
    print(f"   📊 Records dari Fetal Data: {records_from_fetal}")
    print()
    
    # 4. Validasi tanggal dan waktu
    print("📅 Validasi tanggal:")
    recent_records = db.query(Record).filter(
        Record.start_time >= datetime.now().date()
    ).count()
    
    old_records = db.query(Record).filter(
        Record.start_time < datetime.now().date()
    ).count()
    
    print(f"   📅 Records hari ini: {recent_records}")
    print(f"   📅 Records masa lalu: {old_records}")
    print()
    
    # 5. Validasi classification
    print("🏷️ Validasi classification:")
    classifications = db.query(Record.classification, 
                             func.count(Record.id).label('count')).group_by(Record.classification).all()
    
    for classification, count in classifications:
        print(f"   {classification}: {count}")
    print()
    
    # 6. Validasi patient-doctor relationships
    print("👥 Validasi hubungan patient-doctor:")
    records_with_doctor = db.query(Record).filter(Record.doctor_id.isnot(None)).count()
    records_self_monitoring = db.query(Record).filter(Record.doctor_id.is_(None)).count()
    
    print(f"   👨‍⚕️ Records dengan doctor: {records_with_doctor}")
    print(f"   🏠 Self-monitoring: {records_self_monitoring}")
    print()
    
    # 7. Sample record detail
    print("📋 Sample record (detail):")
    sample_record = db.query(Record).first()
    if sample_record:
        print(f"   ID: {sample_record.id}")
        print(f"   Patient ID: {sample_record.patient_id}")
        print(f"   Doctor ID: {sample_record.doctor_id}")
        print(f"   Source: {sample_record.source.value}")
        print(f"   Classification: {sample_record.classification}")
        print(f"   Start Time: {sample_record.start_time}")
        print(f"   BPM Data Points: {len(sample_record.bpm_data) if sample_record.bpm_data else 0}")
        if sample_record.notes:
            notes_preview = sample_record.notes[:100] + "..." if len(sample_record.notes) > 100 else sample_record.notes
            print(f"   Notes Preview: {notes_preview}")
    print()
    
    return True

def validate_integration_with_fetal_system(db: Session):
    """Validasi integrasi dengan sistem fetal monitoring"""
    print("🤱 VALIDASI INTEGRASI SISTEM FETAL MONITORING")
    print("="*60)
    
    # 1. Consistency check
    fetal_sessions = db.query(FetalMonitoringSession).count()
    fetal_readings = db.query(FetalHeartRateReading).count()
    fetal_results = db.query(FetalMonitoringResult).count()
    
    print(f"📊 Fetal Monitoring Data:")
    print(f"   Sessions: {fetal_sessions}")
    print(f"   Readings: {fetal_readings}")
    print(f"   Results: {fetal_results}")
    print()
    
    # 2. Data mapping validation
    print("🔄 Validasi mapping data:")
    
    # Check jika ada records yang berasal dari fetal sessions
    clinic_records = db.query(Record).filter(Record.source == RecordSource.clinic).count()
    home_records = db.query(Record).filter(Record.source == RecordSource.self_).count()
    
    clinic_sessions = db.query(FetalMonitoringSession).filter(
        FetalMonitoringSession.monitoring_type == MonitoringType.clinic
    ).count()
    
    home_sessions = db.query(FetalMonitoringSession).filter(
        FetalMonitoringSession.monitoring_type == MonitoringType.home
    ).count()
    
    print(f"   📊 Clinic Records: {clinic_records} | Clinic Sessions: {clinic_sessions}")
    print(f"   🏠 Home Records: {home_records} | Home Sessions: {home_sessions}")
    print()
    
    # 3. Sample fetal data to record mapping
    print("📋 Sample mapping (Fetal Session → Record):")
    sample_session = db.query(FetalMonitoringSession).first()
    if sample_session:
        print(f"   Session ID: {sample_session.id}")
        print(f"   Patient ID: {sample_session.patient_id}")
        print(f"   Monitoring Type: {sample_session.monitoring_type.value}")
        
        # Find corresponding record
        corresponding_records = db.query(Record).filter(
            Record.patient_id == sample_session.patient_id,
            Record.start_time == sample_session.start_time
        ).all()
        
        print(f"   📊 Corresponding Records: {len(corresponding_records)}")
        if corresponding_records:
            record = corresponding_records[0]
            print(f"      Record ID: {record.id}")
            print(f"      Source: {record.source.value}")
            print(f"      Classification: {record.classification}")
    
    print()
    
    # 4. Pregnancy info integration
    pregnancy_infos = db.query(PregnancyInfo).count()
    patients_with_records = db.query(Record.patient_id).distinct().count()
    
    print(f"🤱 Pregnancy Integration:")
    print(f"   Pregnancy Info Records: {pregnancy_infos}")
    print(f"   Patients with Records: {patients_with_records}")
    print()
    
    return True

def test_data_quality(db: Session):
    """Test kualitas data yang di-seed"""
    print("🧪 TEST KUALITAS DATA")
    print("="*60)
    
    issues = []
    
    # 1. Check for null/empty critical fields
    records_without_patient = db.query(Record).filter(Record.patient_id.is_(None)).count()
    if records_without_patient > 0:
        issues.append(f"❌ {records_without_patient} records tanpa patient_id")
    
    records_without_time = db.query(Record).filter(Record.start_time.is_(None)).count()
    if records_without_time > 0:
        issues.append(f"❌ {records_without_time} records tanpa start_time")
    
    records_without_bpm = db.query(Record).filter(
        (Record.bpm_data.is_(None)) | 
        (Record.bpm_data == '[]')
    ).count()
    if records_without_bpm > 0:
        issues.append(f"⚠️ {records_without_bpm} records tanpa BPM data")
    
    # 2. Check BPM data validity
    print("🔍 Checking BPM data validity...")
    invalid_bpm_count = 0
    sample_records = db.query(Record).filter(Record.bpm_data.isnot(None)).limit(10).all()
    
    for record in sample_records:
        if record.bpm_data:
            for reading in record.bpm_data:
                if isinstance(reading, dict) and "bpm" in reading:
                    bpm = reading["bpm"]
                    if not isinstance(bpm, int) or bpm < 60 or bpm > 300:
                        invalid_bpm_count += 1
                        break
    
    if invalid_bpm_count > 0:
        issues.append(f"⚠️ {invalid_bpm_count} records dengan BPM data tidak valid")
    
    # 3. Check classification validity
    valid_classifications = ["normal", "concerning", "abnormal", "bradycardia", "tachycardia", "irregular"]
    invalid_classifications = db.query(Record).filter(
        ~Record.classification.in_(valid_classifications)
    ).count()
    
    if invalid_classifications > 0:
        issues.append(f"❌ {invalid_classifications} records dengan classification tidak valid")
    
    # Report results
    if issues:
        print("⚠️ Issues ditemukan:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("✅ Semua test kualitas data PASSED!")
    
    print()
    return len(issues) == 0

def main():
    """Main validation function"""
    print("🔍 VALIDASI KOMPREHENSIF DATA RECORDS")
    print("="*70)
    print(f"📅 Tanggal: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    db = SessionLocal()
    
    try:
        # 1. Validasi data records
        validate_records_data(db)
        
        # 2. Validasi integrasi dengan fetal monitoring
        validate_integration_with_fetal_system(db)
        
        # 3. Test kualitas data
        quality_passed = test_data_quality(db)
        
        # Final summary
        print("="*70)
        if quality_passed:
            print("🎉 VALIDASI LENGKAP - SEMUA TEST BERHASIL!")
            print("✅ Data records siap untuk production testing")
        else:
            print("⚠️ VALIDASI SELESAI - ADA BEBERAPA ISSUES")
            print("💡 Silakan review issues di atas dan perbaiki jika diperlukan")
        
        print("="*70)
        
    except Exception as e:
        print(f"❌ Error during validation: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
