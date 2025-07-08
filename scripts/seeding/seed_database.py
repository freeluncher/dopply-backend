"""
Database seeding script for Dopply Backend
Cleans all tables and populates with test data
All users use password: gandhi12345
"""

import os
import sys
from datetime import datetime, date, timedelta
from typing import List, Dict
import uuid
import random
import random

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

def clean_database(db: Session):
    """Clean all tables while preserving schema"""
    print("🧹 Cleaning database...")
    
    # Create tables first if they don't exist
    print("📋 Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    # Delete in correct order to respect foreign key constraints
    # Use try-except to handle missing tables gracefully
    try:
        db.query(Notification).delete()
    except:
        pass
    
    try:
        db.query(FetalHeartRateReading).delete()
    except:
        pass
    
    try:
        db.query(FetalMonitoringResult).delete()
    except:
        pass
    
    try:
        db.query(FetalMonitoringSession).delete()
    except:
        pass
    
    try:
        db.query(PregnancyInfo).delete()
    except:
        pass
    
    try:
        db.query(DoctorPatientAssociation).delete()
    except:
        pass
    
    try:
        db.query(Record).delete()
    except:
        pass
    
    try:
        db.query(Doctor).delete()
    except:
        pass
    
    try:
        db.query(Patient).delete()
    except:
        pass
    
    try:
        db.query(User).delete()
    except:
        pass
    
    db.commit()
    print("✅ Database cleaned successfully")

def create_users(db: Session) -> Dict[str, User]:
    """Create users with all roles"""
    print("👥 Creating users...")
    
    # Standard password for all users
    password_hash = get_password_hash("gandhi12345")
    
    users_data = [
        # Admin users
        {"name": "System Admin", "email": "admin@dopply.com", "role": UserRole.admin},
        {"name": "Dr. Admin", "email": "admin.doctor@dopply.com", "role": UserRole.admin},
        
        # Doctor users
        {"name": "Dr. Sarah Johnson", "email": "sarah.johnson@hospital.com", "role": UserRole.doctor},
        {"name": "Dr. Michael Chen", "email": "michael.chen@clinic.com", "role": UserRole.doctor},
        {"name": "Dr. Emma Williams", "email": "emma.williams@medical.com", "role": UserRole.doctor},
        {"name": "Dr. David Rodriguez", "email": "david.rodriguez@health.com", "role": UserRole.doctor},
        {"name": "Dr. Lisa Anderson", "email": "lisa.anderson@obgyn.com", "role": UserRole.doctor},
        
        # Patient users
        {"name": "Alice Thompson", "email": "alice.thompson@gmail.com", "role": UserRole.patient},
        {"name": "Maria Garcia", "email": "maria.garcia@outlook.com", "role": UserRole.patient},
        {"name": "Jennifer Lee", "email": "jennifer.lee@yahoo.com", "role": UserRole.patient},
        {"name": "Jessica Brown", "email": "jessica.brown@gmail.com", "role": UserRole.patient},
        {"name": "Amanda Davis", "email": "amanda.davis@hotmail.com", "role": UserRole.patient},
        {"name": "Rachel Wilson", "email": "rachel.wilson@gmail.com", "role": UserRole.patient},
        {"name": "Sarah Martinez", "email": "sarah.martinez@outlook.com", "role": UserRole.patient},
        {"name": "Emily Jones", "email": "emily.jones@gmail.com", "role": UserRole.patient},
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
        db.flush()  # Get the ID without committing
        users[user_data["email"]] = user
    
    db.commit()
    print(f"✅ Created {len(users)} users")
    return users

def create_doctors(db: Session, users: Dict[str, User]) -> List[Doctor]:
    """Create doctor profiles"""
    print("👨‍⚕️ Creating doctor profiles...")
    
    doctor_emails = [
        "sarah.johnson@hospital.com", 
        "michael.chen@clinic.com", 
        "emma.williams@medical.com",
        "david.rodriguez@health.com",
        "lisa.anderson@obgyn.com"
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
    print(f"✅ Created {len(doctors)} doctor profiles")
    return doctors

def create_patients(db: Session, users: Dict[str, User]) -> List[Patient]:
    """Create patient profiles"""
    print("🤰 Creating patient profiles...")
    
    patient_data = [
        {
            "email": "alice.thompson@gmail.com",
            "birth_date": date(1992, 3, 15),
            "address": "123 Main St, Downtown, City",
            "age": 32,
            "gender": "Female",
            "phone": "+1-555-0101",
            "medical_note": "First pregnancy, no complications reported"
        },
        {
            "email": "maria.garcia@outlook.com",
            "birth_date": date(1988, 7, 22),
            "address": "456 Oak Ave, Suburb, City",
            "age": 35,
            "gender": "Female", 
            "phone": "+1-555-0102",
            "medical_note": "Second pregnancy, previous normal delivery"
        },
        {
            "email": "jennifer.lee@yahoo.com",
            "birth_date": date(1995, 11, 8),
            "address": "789 Pine Rd, Northside, City",
            "age": 28,
            "gender": "Female",
            "phone": "+1-555-0103",
            "medical_note": "High-risk pregnancy due to gestational diabetes"
        },
        {
            "email": "jessica.brown@gmail.com",
            "birth_date": date(1990, 5, 30),
            "address": "321 Elm St, Eastside, City",
            "age": 33,
            "gender": "Female",
            "phone": "+1-555-0104",
            "medical_note": "Third pregnancy, history of preterm labor"
        },
        {
            "email": "amanda.davis@hotmail.com",
            "birth_date": date(1993, 9, 12),
            "address": "654 Maple Dr, Westside, City",
            "age": 30,
            "gender": "Female",
            "phone": "+1-555-0105",
            "medical_note": "First pregnancy, twins expected"
        },
        {
            "email": "rachel.wilson@gmail.com",
            "birth_date": date(1991, 1, 25),
            "address": "987 Cedar Ln, Southside, City",
            "age": 32,
            "gender": "Female",
            "phone": "+1-555-0106",
            "medical_note": "Second pregnancy, previous C-section"
        },
        {
            "email": "sarah.martinez@outlook.com",
            "birth_date": date(1994, 4, 18),
            "address": "147 Birch St, Central, City",
            "age": 29,
            "gender": "Female",
            "phone": "+1-555-0107",
            "medical_note": "First pregnancy, regular monitoring"
        },
        {
            "email": "emily.jones@gmail.com",
            "birth_date": date(1989, 12, 3),
            "address": "258 Spruce Ave, Heights, City",
            "age": 34,
            "gender": "Female",
            "phone": "+1-555-0108",
            "medical_note": "Fourth pregnancy, experienced mother"
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
    print(f"✅ Created {len(patients)} patient profiles")
    return patients

def create_doctor_patient_associations(db: Session, users: Dict[str, User], patients: List[Patient]):
    """Create doctor-patient associations"""
    print("🔗 Creating doctor-patient associations...")
    
    doctor_emails = [
        "sarah.johnson@hospital.com", 
        "michael.chen@clinic.com", 
        "emma.williams@medical.com",
        "david.rodriguez@health.com",
        "lisa.anderson@obgyn.com"
    ]
    
    associations = []
    for i, patient in enumerate(patients):
        # Assign patients to doctors in rotation
        doctor_email = doctor_emails[i % len(doctor_emails)]
        
        if doctor_email in users:
            association = DoctorPatientAssociation(
                doctor_id=users[doctor_email].id,
                patient_id=patient.id,
                assigned_at=get_local_naive_now(),
                status="active",
                note=f"Assigned for prenatal care and monitoring"
            )
            db.add(association)
            associations.append(association)
    
    db.commit()
    print(f"✅ Created {len(associations)} doctor-patient associations")

def create_pregnancy_info(db: Session, patients: List[Patient]):
    """Create pregnancy information for patients"""
    print("🤱 Creating pregnancy information...")
    
    pregnancy_data = [
        {
            "gestational_age": 28,
            "last_menstrual_period": date.today() - timedelta(weeks=28),
            "expected_due_date": date.today() + timedelta(weeks=12),
            "is_high_risk": False,
            "complications": []
        },
        {
            "gestational_age": 32,
            "last_menstrual_period": date.today() - timedelta(weeks=32),
            "expected_due_date": date.today() + timedelta(weeks=8),
            "is_high_risk": False,
            "complications": ["Previous C-section"]
        },
        {
            "gestational_age": 24,
            "last_menstrual_period": date.today() - timedelta(weeks=24),
            "expected_due_date": date.today() + timedelta(weeks=16),
            "is_high_risk": True,
            "complications": ["Gestational diabetes", "Advanced maternal age"]
        },
        {
            "gestational_age": 36,
            "last_menstrual_period": date.today() - timedelta(weeks=36),
            "expected_due_date": date.today() + timedelta(weeks=4),
            "is_high_risk": True,
            "complications": ["History of preterm labor"]
        },
        {
            "gestational_age": 30,
            "last_menstrual_period": date.today() - timedelta(weeks=30),
            "expected_due_date": date.today() + timedelta(weeks=10),
            "is_high_risk": True,
            "complications": ["Twin pregnancy"]
        },
        {
            "gestational_age": 26,
            "last_menstrual_period": date.today() - timedelta(weeks=26),
            "expected_due_date": date.today() + timedelta(weeks=14),
            "is_high_risk": False,
            "complications": ["Previous C-section"]
        },
        {
            "gestational_age": 22,
            "last_menstrual_period": date.today() - timedelta(weeks=22),
            "expected_due_date": date.today() + timedelta(weeks=18),
            "is_high_risk": False,
            "complications": []
        },
        {
            "gestational_age": 34,
            "last_menstrual_period": date.today() - timedelta(weeks=34),
            "expected_due_date": date.today() + timedelta(weeks=6),
            "is_high_risk": False,
            "complications": ["Experienced mother"]
        },
    ]
    
    pregnancy_infos = []
    for i, patient in enumerate(patients):
        if i < len(pregnancy_data):
            data = pregnancy_data[i]
            pregnancy_info = PregnancyInfo(
                patient_id=patient.id,
                gestational_age=data["gestational_age"],
                last_menstrual_period=data["last_menstrual_period"],
                expected_due_date=data["expected_due_date"],
                is_high_risk=data["is_high_risk"],
                complications=data["complications"],
                created_at=get_local_naive_now(),
                updated_at=get_local_naive_now()
            )
            db.add(pregnancy_info)
            pregnancy_infos.append(pregnancy_info)
    
    db.commit()
    print(f"✅ Created {len(pregnancy_infos)} pregnancy information records")

def create_fetal_monitoring_sessions(db: Session, patients: List[Patient], users: Dict[str, User]):
    """Create fetal monitoring sessions with heart rate readings and results"""
    print("📊 Creating fetal monitoring sessions...")
    
    doctor_emails = [
        "sarah.johnson@hospital.com", 
        "michael.chen@clinic.com", 
        "emma.williams@medical.com",
        "david.rodriguez@health.com",
        "lisa.anderson@obgyn.com"
    ]
    
    sessions = []
    
    for i, patient in enumerate(patients):
        # Create 3-5 sessions per patient
        num_sessions = 3 + (i % 3)  # 3-5 sessions
        
        for session_num in range(num_sessions):
            session_id = str(uuid.uuid4())
            
            # Alternate between clinic and home monitoring
            monitoring_type = MonitoringType.clinic if session_num % 2 == 0 else MonitoringType.home
            
            # Get doctor for clinic sessions
            doctor_id = None
            if monitoring_type == MonitoringType.clinic:
                doctor_email = doctor_emails[i % len(doctor_emails)]
                doctor_id = users[doctor_email].id
            
            # Create session
            start_time = get_local_naive_now() - timedelta(days=session_num * 7 + i)
            end_time = start_time + timedelta(minutes=30)
            
            session = FetalMonitoringSession(
                id=session_id,
                patient_id=patient.id,
                doctor_id=doctor_id,
                monitoring_type=monitoring_type,
                gestational_age=24 + session_num * 2,  # Progressive gestational age
                start_time=start_time,
                end_time=end_time,
                notes="Patient reports normal fetal movements" if monitoring_type == MonitoringType.home else None,
                doctor_notes="Routine monitoring session" if monitoring_type == MonitoringType.clinic else None,
                shared_with_doctor=monitoring_type == MonitoringType.home and session_num > 0,
                created_at=start_time,
                updated_at=start_time
            )
            db.add(session)
            db.flush()
            sessions.append(session)
            
            # Create heart rate readings for this session
            create_heart_rate_readings(db, session)
            
            # Create monitoring result for this session
            create_monitoring_result(db, session)
    
    db.commit()
    print(f"✅ Created {len(sessions)} fetal monitoring sessions")

def create_heart_rate_readings(db: Session, session: FetalMonitoringSession):
    """Create heart rate readings for a session"""
    
    # Generate 30 minutes of readings (every 30 seconds = 60 readings)
    num_readings = 60
    base_bpm = 140  # Normal fetal heart rate baseline
    
    readings = []
    for i in range(num_readings):
        timestamp = session.start_time + timedelta(seconds=i * 30)
        
        # Simulate realistic fetal heart rate variability
        if session.gestational_age < 28:
            # Earlier gestational age - more variability
            bpm = base_bpm + ((i % 10) - 5) * 3 + (i % 20 - 10)
        else:
            # Later gestational age - more stable
            bpm = base_bpm + ((i % 8) - 4) * 2 + (i % 15 - 7)
        
        # Ensure BPM stays in reasonable range
        bpm = max(110, min(180, bpm))
        
        # Determine classification
        if bpm < 120:
            classification = FetalClassification.bradycardia
        elif bpm > 160:
            classification = FetalClassification.tachycardia
        elif abs(bpm - base_bpm) > 20:
            classification = FetalClassification.irregular
        else:
            classification = FetalClassification.normal
        
        reading = FetalHeartRateReading(
            session_id=session.id,
            timestamp=timestamp,
            bpm=bpm,
            signal_quality=0.85 + (i % 10) * 0.01,  # Good signal quality
            classification=classification,
            created_at=timestamp
        )
        db.add(reading)
        readings.append(reading)

def create_monitoring_result(db: Session, session: FetalMonitoringSession):
    """Create monitoring result for a session"""
    
    # Calculate average BPM (simulate based on session)
    if session.gestational_age < 28:
        avg_bpm = 142.5
        baseline_variability = 12.8
    else:
        avg_bpm = 138.2
        baseline_variability = 8.4
    
    # Determine overall classification and risk
    if session.gestational_age < 24 or session.monitoring_type == MonitoringType.home:
        if avg_bpm < 120 or avg_bpm > 160:
            overall_classification = OverallClassification.abnormal
            risk_level = RiskLevel.high
            findings = ["Abnormal heart rate detected", "Immediate medical attention recommended"]
            recommendations = ["Contact healthcare provider immediately", "Schedule urgent consultation"]
        elif baseline_variability > 15:
            overall_classification = OverallClassification.concerning
            risk_level = RiskLevel.medium
            findings = ["Increased heart rate variability", "Monitor closely"]
            recommendations = ["Continue regular monitoring", "Schedule follow-up in 1 week"]
        else:
            overall_classification = OverallClassification.normal
            risk_level = RiskLevel.low
            findings = ["Normal fetal heart rate pattern", "Good baseline variability"]
            recommendations = ["Continue routine monitoring", "Maintain healthy lifestyle"]
    else:
        overall_classification = OverallClassification.normal
        risk_level = RiskLevel.low
        findings = ["Normal fetal heart rate pattern", "Stable baseline", "Appropriate variability"]
        recommendations = ["Continue routine prenatal care", "Next visit as scheduled"]
    
    result = FetalMonitoringResult(
        session_id=session.id,
        overall_classification=overall_classification,
        average_bpm=avg_bpm,
        baseline_variability=baseline_variability,
        findings=findings,
        recommendations=recommendations,
        risk_level=risk_level,
        created_at=session.created_at
    )
    db.add(result)

def create_patient_status_history(db: Session, patients: List[Patient]):
    """Create patient status history"""
    print("📈 Creating patient status history...")
    
    status_changes = []
    for patient in patients:
        # Create a progression of status changes for each patient
        statuses = [
            ('pending', 'Registration submitted'),
            ('active', 'Profile approved by doctor'),
            ('active', 'Monitoring started'),
        ]
        
        # Some patients might have additional status changes
        if patient.id % 3 == 0:
            statuses.append(('inactive', 'Temporary monitoring pause'))
            statuses.append(('active', 'Monitoring resumed'))
        
        for i, (status, reason) in enumerate(statuses):
            from app.models.patient_status_history import PatientStatusHistory
            
            previous_status = 'pending' if i == 0 else statuses[i-1][0]
            
            status_history = PatientStatusHistory(
                patient_id=patient.id,
                previous_status=previous_status,
                new_status=status,
                changed_by=1,  # System admin
                change_reason=reason,
                created_at=get_local_naive_now() - timedelta(days=30-i*7)
            )
            db.add(status_history)
            status_changes.append(status_history)
    
    db.commit()
    print(f"✅ Created {len(status_changes)} status history records")

def create_additional_notifications(db: Session, patients: List[Patient], users: Dict[str, User]):
    """Create additional notifications for various scenarios"""
    print("🔔 Creating additional notifications...")
    
    notification_scenarios = [
        {
            'title': 'Appointment Reminder',
            'message': 'You have an upcoming appointment tomorrow at 2:00 PM',
            'type': 'appointment_reminder'
        },
        {
            'title': 'Test Results Available',
            'message': 'Your latest monitoring results are now available for review',
            'type': 'test_result'
        },
        {
            'title': 'Medication Reminder',
            'message': 'Please remember to take your prenatal vitamins',
            'type': 'medication_reminder'
        },
        {
            'title': 'System Alert',
            'message': 'New monitoring features have been added to your dashboard',
            'type': 'system_alert'
        },
        {
            'title': 'Doctor Message',
            'message': 'Dr. Johnson has left you a message regarding your recent visit',
            'type': 'doctor_message'
        }
    ]
    
    notifications = []
    
    # Create notifications for patients
    for i, patient in enumerate(patients):
        scenario = notification_scenarios[i % len(notification_scenarios)]
        
        notification = Notification(
            user_id=patient.user_id,
            title=scenario['title'],
            message=scenario['message'],
            type=scenario['type'],
            is_read=i % 3 == 0,  # Some notifications are read
            created_at=get_local_naive_now() - timedelta(days=random.randint(1, 7))
        )
        db.add(notification)
        notifications.append(notification)
    
    # Create notifications for doctors
    doctor_emails = [
        "sarah.johnson@hospital.com", 
        "michael.chen@clinic.com", 
        "emma.williams@medical.com"
    ]
    
    doctor_scenarios = [
        {
            'title': 'Patient Alert',
            'message': 'Patient monitoring data requires your attention',
            'type': 'patient_alert'
        },
        {
            'title': 'System Update',
            'message': 'New monitoring protocols have been implemented',
            'type': 'system_update'
        },
        {
            'title': 'Schedule Reminder',
            'message': 'You have 3 patient consultations scheduled for tomorrow',
            'type': 'schedule_reminder'
        }
    ]
    
    for email in doctor_emails:
        if email in users:
            scenario = doctor_scenarios[len(notifications) % len(doctor_scenarios)]
            
            notification = Notification(
                user_id=users[email].id,
                title=scenario['title'],
                message=scenario['message'],
                type=scenario['type'],
                is_read=False,
                created_at=get_local_naive_now() - timedelta(hours=random.randint(1, 24))
            )
            db.add(notification)
            notifications.append(notification)
    
    db.commit()
    print(f"✅ Created {len(notifications)} additional notifications")

def create_medical_records(db: Session, patients: List[Patient], users: Dict[str, User]):
    """Create comprehensive medical records"""
    print("📋 Creating medical records...")
    
    doctor_emails = [
        "sarah.johnson@hospital.com", 
        "michael.chen@clinic.com", 
        "emma.williams@medical.com",
        "david.rodriguez@health.com",
        "lisa.anderson@obgyn.com"
    ]
    
    records = []
    for i, patient in enumerate(patients):
        # Create 2-4 records per patient
        num_records = 2 + (i % 3)
        
        for record_num in range(num_records):
            doctor_email = doctor_emails[i % len(doctor_emails)]
            
            if doctor_email in users:
                record = Record(
                    patient_id=patient.id,
                    doctor_id=users[doctor_email].id,
                    heart_rate=random.randint(60, 100),
                    temperature=round(random.uniform(36.1, 37.2), 1),
                    blood_pressure_systolic=random.randint(110, 140),
                    blood_pressure_diastolic=random.randint(70, 90),
                    notes=f"Regular checkup #{record_num + 1} - Patient shows normal vital signs",
                    created_at=get_local_naive_now() - timedelta(days=record_num * 14 + i)
                )
                db.add(record)
                records.append(record)
    
    db.commit()
    print(f"✅ Created {len(records)} medical records")

def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")
    print("Password for all users: gandhi12345")
    print("-" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Step 1: Clean database
        clean_database(db)
        
        # Step 2: Create users
        users = create_users(db)
        
        # Step 3: Create doctors
        doctors = create_doctors(db, users)
        
        # Step 4: Create patients
        patients = create_patients(db, users)
        
        # Step 5: Create doctor-patient associations
        create_doctor_patient_associations(db, users, patients)
        
        # Step 6: Create pregnancy information
        create_pregnancy_info(db, patients)
        
        # Step 7: Create fetal monitoring sessions (with heart rate readings and results)
        create_fetal_monitoring_sessions(db, patients, users)
        
        # Step 8: Create patient status history records
        create_patient_status_history(db, patients)
        
        # Step 9: Create medical records
        create_medical_records(db, patients, users)
        
        # Step 10: Create comprehensive notifications
        create_additional_notifications(db, patients, users)
        
        print("-" * 50)
        print("🎉 Database seeding completed successfully!")
        print(f"👥 Created {len(users)} users")
        print(f"👨‍⚕️ Created {len(doctors)} doctors")
        print(f"🤰 Created {len(patients)} patients")
        print("🔐 All users password: gandhi1245")
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
