#!/usr/bin/env python3
"""
Script untuk menambahkan data ke table yang kosong
"""
import os
import sys
import uuid
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.medical import (
    User, Patient, Record, RecordSource, Notification, NotificationStatus,
    FetalMonitoringSession, MonitoringType, FetalClassification,
    FetalHeartRateReading, FetalMonitoringResult, OverallClassification, RiskLevel
)
from app.models.patient_status_history import PatientStatusHistory
from app.core.time_utils import get_local_naive_now

def main():
    print("🌱 Adding data to empty tables...")
    
    db = SessionLocal()
    
    try:
        # Get existing data
        users = {user.email: user for user in db.query(User).all()}
        patients = db.query(Patient).all()
        
        doctors = [
            "sarah.johnson@hospital.com", 
            "michael.chen@clinic.com", 
            "emma.williams@medical.com"
        ]
        
        # 1. Records
        print("📋 Creating records...")
        for i, patient in enumerate(patients[:5]):
            doctor_email = doctors[i % len(doctors)]
            
            bpm_data = [{"time": j*30, "bpm": 135 + (j%10)-5} for j in range(20)]
            
            record = Record(
                patient_id=patient.id,
                doctor_id=users[doctor_email].id,
                source=RecordSource.clinic,
                bpm_data=bpm_data,
                start_time=get_local_naive_now() - timedelta(days=i*2),
                end_time=get_local_naive_now() - timedelta(days=i*2) + timedelta(minutes=10),
                classification="normal",
                notes=f"Record for {patient.user.name}"
            )
            db.add(record)
        
        db.commit()
        print("✅ Records created")
        
        # 2. Patient Status History
        print("📋 Creating status history...")
        for i, patient in enumerate(patients):
            doctor_email = doctors[i % len(doctors)]
            
            history = PatientStatusHistory(
                doctor_id=users[doctor_email].id,
                patient_id=patient.id,
                old_status=None,
                new_status="active",
                notes="Patient assigned to doctor",
                changed_by=users[doctor_email].id,
                changed_at=get_local_naive_now() - timedelta(days=i)
            )
            db.add(history)
        
        db.commit()
        print("✅ Status history created")
        
        # 3. Notifications
        print("🔔 Creating notifications...")
        records = db.query(Record).limit(5).all()
        
        for i, record in enumerate(records):
            doctor_email = doctors[i % len(doctors)]
            
            notification = Notification(
                from_patient_id=record.patient_id,
                to_doctor_id=users[doctor_email].id,
                record_id=record.id,
                status=NotificationStatus.unread
            )
            db.add(notification)
        
        db.commit()
        print("✅ Notifications created")
        
        # 4. Fetal Monitoring Sessions
        print("📊 Creating monitoring sessions...")
        for i, patient in enumerate(patients[:3]):
            session_id = str(uuid.uuid4())
            doctor_email = doctors[i % len(doctors)]
            
            session = FetalMonitoringSession(
                id=session_id,
                patient_id=patient.id,
                doctor_id=users[doctor_email].id,
                monitoring_type=MonitoringType.clinic,
                gestational_age=30,
                start_time=get_local_naive_now() - timedelta(hours=i*24),
                end_time=get_local_naive_now() - timedelta(hours=i*24) + timedelta(minutes=30),
                doctor_notes="Routine monitoring",
                shared_with_doctor=False,
                created_at=get_local_naive_now(),
                updated_at=get_local_naive_now()
            )
            db.add(session)
        
        db.commit()
        print("✅ Monitoring sessions created")
        
        # Get sessions for next steps
        sessions = db.query(FetalMonitoringSession).all()
        
        # 5. Heart Rate Readings
        print("💓 Creating heart rate readings...")
        for session in sessions:
            for minute in range(10):  # 10 readings per session
                reading = FetalHeartRateReading(
                    session_id=session.id,
                    timestamp=session.start_time + timedelta(minutes=minute*3),
                    bpm=140 + (minute % 5) - 2,
                    signal_quality=0.9,
                    classification=FetalClassification.normal,
                    created_at=session.start_time + timedelta(minutes=minute*3)
                )
                db.add(reading)
        
        db.commit()
        print("✅ Heart rate readings created")
        
        # 6. Monitoring Results
        print("📈 Creating monitoring results...")
        for session in sessions:
            result = FetalMonitoringResult(
                session_id=session.id,
                overall_classification=OverallClassification.normal,
                average_bpm=140.0,
                baseline_variability=10.0,
                findings=["Normal heart rate pattern"],
                recommendations=["Continue routine monitoring"],
                risk_level=RiskLevel.low,
                created_at=session.created_at
            )
            db.add(result)
        
        db.commit()
        print("✅ Monitoring results created")
        
        print("\n🎉 All tables seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
