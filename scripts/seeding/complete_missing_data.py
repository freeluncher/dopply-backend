#!/usr/bin/env python3
"""
Complete missing table data script
"""

import sys
import os
import uuid
import random
from datetime import datetime, date, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.medical import (
    User, Patient, Doctor, Record, RecordSource, 
    Notification, NotificationStatus, FetalMonitoringSession, FetalMonitoringResult, FetalHeartRateReading
)
from app.core.time_utils import get_local_naive_now

def add_missing_records():
    """Add records for all patients"""
    print("📋 Adding medical records...")
    
    db = SessionLocal()
    try:
        # Check if records exist
        existing_records = db.query(Record).count()
        if existing_records > 0:
            print(f"✅ Records already exist ({existing_records}), skipping...")
            return
        
        patients = db.query(Patient).all()
        doctors = db.query(Doctor).all()
        
        records_added = 0
        for patient in patients:
            # Get assigned doctor for this patient
            doctor = doctors[patient.id % len(doctors)]
            
            # Create 2-3 records per patient
            for i in range(3):
                # Create simple BPM data
                bpm_data = [
                    {"time": j * 30, "bpm": random.randint(120, 180)} 
                    for j in range(20)  # 10 minutes of data
                ]
                
                record = Record(
                    patient_id=patient.id,
                    doctor_id=doctor.doctor_id,
                    source=random.choice([RecordSource.clinic, RecordSource.self_]),
                    bpm_data=bpm_data,
                    start_time=get_local_naive_now() - timedelta(days=i * 14 + patient.id),
                    end_time=get_local_naive_now() - timedelta(days=i * 14 + patient.id) + timedelta(minutes=10),
                    classification="normal",
                    notes=f"Regular checkup #{i+1} - Normal vital signs"
                )
                db.add(record)
                records_added += 1
        
        db.commit()
        print(f"✅ Added {records_added} medical records")
        
    except Exception as e:
        print(f"❌ Error adding records: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def add_missing_notifications():
    """Add notifications for all users"""
    print("🔔 Adding notifications...")
    
    db = SessionLocal()
    try:
        # Check if notifications exist
        existing_notifications = db.query(Notification).count()
        if existing_notifications > 0:
            print(f"✅ Notifications already exist ({existing_notifications}), skipping...")
            return
        
        users = db.query(User).all()
        patients = db.query(Patient).all()
        doctors = db.query(Doctor).all()
        records = db.query(Record).all()
        
        if not records:
            print("⚠️ No records found. Please add records first.")
            return
        
        notification_types = [
            {
                'title': 'Appointment Reminder',
                'message': 'You have an upcoming appointment tomorrow at 2:00 PM',
                'type': 'appointment_reminder'
            },
            {
                'title': 'Test Results Available',
                'message': 'Your latest test results are now available for review',
                'type': 'test_result'
            },
            {
                'title': 'Medication Reminder',
                'message': 'Please remember to take your prenatal vitamins',
                'type': 'medication_reminder'
            },
            {
                'title': 'System Update',
                'message': 'New features have been added to your dashboard',
                'type': 'system_update'
            }
        ]
        
        notifications_added = 0
        
        # Create notifications for each patient-doctor combination
        for i, patient in enumerate(patients):
            if i < len(records):
                record = records[i]
                # Find a doctor for this patient
                assigned_doctors = db.query(Doctor).filter(
                    Doctor.doctor_id.in_([assoc.doctor_id for assoc in patient.doctor_patient_associations])
                ).first()
                
                if assigned_doctors:
                    notification = Notification(
                        from_patient_id=patient.id,
                        to_doctor_id=assigned_doctors.doctor_id,
                        record_id=record.id,
                        status=NotificationStatus.unread if i % 2 == 0 else NotificationStatus.read
                    )
                    db.add(notification)
                    notifications_added += 1
        
        db.commit()
        print(f"✅ Added {notifications_added} notifications")
        
    except Exception as e:
        print(f"❌ Error adding notifications: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def add_patient_status_history():
    """Add patient status history"""
    print("📈 Adding patient status history...")
    
    db = SessionLocal()
    try:
        # Check if status history exists
        from app.models.patient_status_history import PatientStatusHistory
        existing_history = db.query(PatientStatusHistory).count()
        if existing_history > 0:
            print(f"✅ Patient status history already exists ({existing_history}), skipping...")
            return
        
        patients = db.query(Patient).all()
        doctors = db.query(Doctor).all()
        
        history_added = 0
        for patient in patients:
            # Get assigned doctor for this patient
            doctor = doctors[patient.id % len(doctors)]
            
            # Create status progression for each patient
            statuses = [
                ('pending', 'active', 'Patient registration submitted and approved'),
                ('active', 'active', 'Monitoring started successfully')
            ]
            
            for i, (old_status, new_status, reason) in enumerate(statuses):
                history = PatientStatusHistory(
                    doctor_id=doctor.doctor_id,
                    patient_id=patient.id,
                    old_status=old_status,
                    new_status=new_status,
                    notes=reason,
                    changed_by=1,  # Admin user
                    changed_at=get_local_naive_now() - timedelta(days=30 - i * 15)
                )
                db.add(history)
                history_added += 1
        
        db.commit()
        print(f"✅ Added {history_added} status history records")
        
    except Exception as e:
        print(f"❌ Error adding patient status history: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def check_fetal_monitoring():
    """Check and complete fetal monitoring data"""
    print("📊 Checking fetal monitoring data...")
    
    db = SessionLocal()
    try:
        sessions = db.query(FetalMonitoringSession).count()
        results = db.query(FetalMonitoringResult).count()
        readings = db.query(FetalHeartRateReading).count()
        
        print(f"📊 Fetal Monitoring Sessions: {sessions}")
        print(f"📈 Fetal Monitoring Results: {results}")
        print(f"💓 Heart Rate Readings: {readings}")
        
        if sessions > 0:
            print("✅ Fetal monitoring data already exists")
        else:
            print("⚠️ No fetal monitoring data found, but this is optional for basic setup")
        
    except Exception as e:
        print(f"❌ Error checking fetal monitoring: {e}")
    finally:
        db.close()

def main():
    """Add missing table data"""
    print("🔧 Completing missing table data...")
    print("-" * 50)
    
    try:
        # Add records
        add_missing_records()
        
        # Add notifications
        add_missing_notifications()
        
        # Add patient status history
        add_patient_status_history()
        
        # Check fetal monitoring
        check_fetal_monitoring()
        
        print("-" * 50)
        print("🎉 Missing data completion successful!")
        
        # Final verification
        db = SessionLocal()
        try:
            print("\n📊 Final table counts:")
            tables = [
                ('users', User),
                ('patients', Patient),
                ('records', Record),
                ('notifications', Notification)
            ]
            
            for table_name, model in tables:
                count = db.query(model).count()
                print(f"  {table_name}: {count}")
                
        finally:
            db.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
