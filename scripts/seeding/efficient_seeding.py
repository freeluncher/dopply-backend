#!/usr/bin/env python3
"""
Efficient database seeding script that handles large data in batches
"""

import sys
import os
import uuid
import random
from datetime import datetime, date, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.medical import (
    Base, User, UserRole, Patient, Doctor, Record, RecordSource,
    Notification, NotificationStatus, DoctorPatientAssociation,
    FetalMonitoringSession, MonitoringType, FetalClassification,
    FetalHeartRateReading, FetalMonitoringResult, OverallClassification,
    RiskLevel, PregnancyInfo
)
from app.core.security import get_password_hash
from app.core.time_utils import get_local_naive_now

def seed_basic_data():
    """Seed basic data without the heavy monitoring data"""
    print("🌱 Seeding basic data...")
    
    db = SessionLocal()
    try:
        # Create users
        print("👥 Creating users...")
        password_hash = get_password_hash("gandhi12345")
        
        users_data = [
            {"name": "System Admin", "email": "admin@dopply.com", "role": UserRole.admin},
            {"name": "Dr. Admin", "email": "admin.doctor@dopply.com", "role": UserRole.admin},
            {"name": "Dr. Sarah Johnson", "email": "sarah.johnson@hospital.com", "role": UserRole.doctor},
            {"name": "Dr. Michael Chen", "email": "michael.chen@clinic.com", "role": UserRole.doctor},
            {"name": "Dr. Emma Williams", "email": "emma.williams@medical.com", "role": UserRole.doctor},
            {"name": "Alice Thompson", "email": "alice.thompson@gmail.com", "role": UserRole.patient},
            {"name": "Maria Garcia", "email": "maria.garcia@outlook.com", "role": UserRole.patient},
            {"name": "Jennifer Lee", "email": "jennifer.lee@yahoo.com", "role": UserRole.patient},
        ]
        
        users = {}
        for user_data in users_data:
            user = User(
                name=user_data["name"],
                email=user_data["email"],
                password_hash=password_hash,
                role=user_data["role"],
                photo_url=f"/static/user_photos/{user_data['email'].split('@')[0]}.jpg",
                created_at=get_local_naive_now()
            )
            db.add(user)
            db.flush()
            users[user_data["email"]] = user
        
        db.commit()
        print(f"✅ Created {len(users)} users")
        
        # Create doctors
        print("👨‍⚕️ Creating doctors...")
        doctor_emails = [
            "sarah.johnson@hospital.com", 
            "michael.chen@clinic.com", 
            "emma.williams@medical.com"
        ]
        
        doctors = []
        for email in doctor_emails:
            if email in users:
                doctor = Doctor(
                    doctor_id=users[email].id,
                    is_valid=True
                )
                db.add(doctor)
                doctors.append(doctor)
        
        db.commit()
        print(f"✅ Created {len(doctors)} doctors")
        
        # Create patients
        print("🤰 Creating patients...")
        patient_data = [
            {
                "email": "alice.thompson@gmail.com",
                "birth_date": date(1992, 3, 15),
                "address": "123 Main St, Downtown, City",
                "age": 32,
                "gender": "Female",
                "phone": "+1-555-0101",
                "medical_note": "First pregnancy, no complications"
            },
            {
                "email": "maria.garcia@outlook.com",
                "birth_date": date(1988, 7, 22),
                "address": "456 Oak Ave, Suburb, City", 
                "age": 35,
                "gender": "Female",
                "phone": "+1-555-0102",
                "medical_note": "Second pregnancy, normal delivery"
            },
            {
                "email": "jennifer.lee@yahoo.com",
                "birth_date": date(1995, 11, 8),
                "address": "789 Pine Rd, Northside, City",
                "age": 28,
                "gender": "Female",
                "phone": "+1-555-0103",
                "medical_note": "High-risk pregnancy"
            },
        ]
        
        patients = []
        for data in patient_data:
            if data["email"] in users:
                patient = Patient(
                    user_id=users[data["email"]].id,
                    birth_date=data["birth_date"],
                    address=data["address"],
                    age=data["age"],
                    gender=data["gender"],
                    phone=data["phone"],
                    medical_note=data["medical_note"]
                )
                db.add(patient)
                db.flush()
                patients.append(patient)
        
        db.commit()
        print(f"✅ Created {len(patients)} patients")
        
        # Create doctor-patient associations
        print("🔗 Creating doctor-patient associations...")
        for i, patient in enumerate(patients):
            doctor_email = doctor_emails[i % len(doctor_emails)]
            if doctor_email in users:
                association = DoctorPatientAssociation(
                    doctor_id=users[doctor_email].id,
                    patient_id=patient.id,
                    assigned_at=get_local_naive_now(),
                    status="active",
                    note="Assigned for prenatal care"
                )
                db.add(association)
        
        db.commit()
        print(f"✅ Created {len(patients)} doctor-patient associations")
        
        # Create pregnancy info
        print("🤱 Creating pregnancy information...")
        for i, patient in enumerate(patients):
            pregnancy_info = PregnancyInfo(
                patient_id=patient.id,
                gestational_age=20 + i * 5,
                last_menstrual_period=date.today() - timedelta(weeks=20 + i * 5),
                expected_due_date=date.today() + timedelta(weeks=20 - i * 5),
                is_high_risk=i == 2,  # Only Jennifer is high risk
                complications=["Gestational diabetes"] if i == 2 else [],
                created_at=get_local_naive_now(),
                updated_at=get_local_naive_now()
            )
            db.add(pregnancy_info)
        
        db.commit()
        print(f"✅ Created {len(patients)} pregnancy information records")
        
        return users, doctors, patients
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def seed_monitoring_data():
    """Seed monitoring data in batches"""
    print("📊 Seeding monitoring data...")
    
    db = SessionLocal()
    try:
        # Get existing data
        patients = db.query(Patient).all()
        users = {user.email: user for user in db.query(User).all()}
        
        doctor_emails = [
            "sarah.johnson@hospital.com", 
            "michael.chen@clinic.com", 
            "emma.williams@medical.com"
        ]
        
        # Create monitoring sessions
        print("📊 Creating monitoring sessions...")
        sessions = []
        for i, patient in enumerate(patients):
            doctor_email = doctor_emails[i % len(doctor_emails)]
            
            # Create 2 sessions per patient (smaller number)
            for session_num in range(2):
                session_id = str(uuid.uuid4())
                
                session = FetalMonitoringSession(
                    id=session_id,
                    patient_id=patient.id,
                    doctor_id=users[doctor_email].id if session_num == 0 else None,
                    monitoring_type=MonitoringType.clinic if session_num == 0 else MonitoringType.home,
                    gestational_age=24 + session_num * 4,
                    start_time=get_local_naive_now() - timedelta(days=session_num * 7),
                    end_time=get_local_naive_now() - timedelta(days=session_num * 7) + timedelta(minutes=30),
                    notes="Routine monitoring" if session_num == 0 else "Home monitoring",
                    shared_with_doctor=session_num == 1,
                    created_at=get_local_naive_now() - timedelta(days=session_num * 7),
                    updated_at=get_local_naive_now() - timedelta(days=session_num * 7)
                )
                db.add(session)
                sessions.append(session)
        
        db.commit()
        print(f"✅ Created {len(sessions)} monitoring sessions")
        
        # Create heart rate readings (smaller batches)
        print("💓 Creating heart rate readings...")
        for session in sessions:
            readings = []
            # Only 10 readings per session instead of 60
            for i in range(10):
                timestamp = session.start_time + timedelta(minutes=i * 3)
                bpm = 140 + random.randint(-15, 15)
                bpm = max(110, min(180, bpm))
                
                if bpm < 120:
                    classification = FetalClassification.bradycardia
                elif bpm > 160:
                    classification = FetalClassification.tachycardia
                else:
                    classification = FetalClassification.normal
                
                reading = FetalHeartRateReading(
                    session_id=session.id,
                    timestamp=timestamp,
                    bpm=bpm,
                    signal_quality=0.85 + random.uniform(0, 0.1),
                    classification=classification,
                    created_at=timestamp
                )
                readings.append(reading)
            
            # Add readings in batch
            db.add_all(readings)
            db.commit()  # Commit after each session
        
        print(f"✅ Created heart rate readings for all sessions")
        
        # Create monitoring results
        print("📈 Creating monitoring results...")
        for session in sessions:
            overall_classification = random.choice([OverallClassification.normal, OverallClassification.concerning])
            
            result = FetalMonitoringResult(
                session_id=session.id,
                overall_classification=overall_classification,
                average_bpm=140.0 + random.uniform(-10, 10),
                baseline_variability=10.0 + random.uniform(-3, 5),
                findings=["Normal heart rate pattern"] if overall_classification == OverallClassification.normal else ["Slight irregularities detected"],
                recommendations=["Continue routine monitoring"] if overall_classification == OverallClassification.normal else ["Increased monitoring frequency"],
                risk_level=RiskLevel.low if overall_classification == OverallClassification.normal else RiskLevel.medium,
                created_at=session.created_at
            )
            db.add(result)
        
        db.commit()
        print(f"✅ Created monitoring results for all sessions")
        
    except Exception as e:
        print(f"❌ Error in monitoring data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def seed_additional_data():
    """Seed additional data like records, notifications, status history"""
    print("📋 Seeding additional data...")
    
    db = SessionLocal()
    try:
        patients = db.query(Patient).all()
        users = {user.email: user for user in db.query(User).all()}
        
        # Create records
        print("📋 Creating medical records...")
        for i, patient in enumerate(patients):
            for record_num in range(2):  # 2 records per patient
                record = Record(
                    patient_id=patient.id,
                    heart_rate=random.randint(60, 100),
                    temperature=round(random.uniform(36.1, 37.2), 1),
                    blood_pressure_systolic=random.randint(110, 140),
                    blood_pressure_diastolic=random.randint(70, 90),
                    notes=f"Regular checkup #{record_num + 1}",
                    created_at=get_local_naive_now() - timedelta(days=record_num * 14)
                )
                db.add(record)
        
        db.commit()
        print("✅ Created medical records")
        
        # Create notifications
        print("🔔 Creating notifications...")
        for i, patient in enumerate(patients):
            notification = Notification(
                user_id=patient.user_id,
                title="Appointment Reminder",
                message="You have an upcoming appointment",
                type="appointment_reminder",
                is_read=i % 2 == 0,
                created_at=get_local_naive_now() - timedelta(days=random.randint(1, 7))
            )
            db.add(notification)
        
        db.commit()
        print("✅ Created notifications")
        
        # Create patient status history
        print("📈 Creating patient status history...")
        from app.models.patient_status_history import PatientStatusHistory
        
        for patient in patients:
            status_history = PatientStatusHistory(
                patient_id=patient.id,
                previous_status='pending',
                new_status='active',
                changed_by=1,  # admin user
                change_reason='Initial activation',
                created_at=get_local_naive_now() - timedelta(days=30)
            )
            db.add(status_history)
        
        db.commit()
        print("✅ Created patient status history")
        
    except Exception as e:
        print(f"❌ Error in additional data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main seeding function"""
    print("🌱 Starting efficient database seeding...")
    print("Password for all users: gandhi12345")
    print("-" * 50)
    
    try:
        # Step 1: Seed basic data (users, doctors, patients, etc.)
        users, doctors, patients = seed_basic_data()
        
        # Step 2: Seed monitoring data in batches
        seed_monitoring_data()
        
        # Step 3: Seed additional data
        seed_additional_data()
        
        print("-" * 50)
        print("🎉 Database seeding completed successfully!")
        print("🔐 All users password: gandhi12345")
        print("-" * 50)
        
        # Final verification
        db = SessionLocal()
        try:
            print("📊 Final table counts:")
            tables = [
                ('users', User),
                ('doctors', Doctor), 
                ('patients', Patient),
                ('fetal_monitoring_sessions', FetalMonitoringSession),
                ('fetal_monitoring_results', FetalMonitoringResult),
                ('fetal_heart_rate_readings', FetalHeartRateReading),
                ('records', Record),
                ('notifications', Notification)
            ]
            
            for table_name, model in tables:
                count = db.query(model).count()
                print(f"  {table_name}: {count}")
                
        finally:
            db.close()
        
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        raise

if __name__ == "__main__":
    main()
