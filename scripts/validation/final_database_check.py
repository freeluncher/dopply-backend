#!/usr/bin/env python3
"""
Final comprehensive database check - all tables
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.medical import (
    User, Patient, Doctor, Record, Notification, 
    DoctorPatientAssociation, PregnancyInfo,
    FetalMonitoringSession, FetalMonitoringResult, FetalHeartRateReading
)
from app.models.patient_status_history import PatientStatusHistory

def comprehensive_check():
    """Check all tables and their relationships"""
    print("🔍 COMPREHENSIVE DATABASE CHECK")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Basic counts
        tables_info = [
            ("Users", User),
            ("Patients", Patient),
            ("Doctors", Doctor),
            ("Doctor-Patient Associations", DoctorPatientAssociation),
            ("Pregnancy Info", PregnancyInfo),
            ("Medical Records", Record),
            ("Notifications", Notification),
            ("Patient Status History", PatientStatusHistory),
            ("Fetal Monitoring Sessions", FetalMonitoringSession),
            ("Fetal Monitoring Results", FetalMonitoringResult),
            ("Fetal Heart Rate Readings", FetalHeartRateReading),
        ]
        
        print("📊 TABLE COUNTS:")
        total_records = 0
        for table_name, model in tables_info:
            count = db.query(model).count()
            status = "✅" if count > 0 else "⚪"
            print(f"  {status} {table_name}: {count} records")
            total_records += count
        
        print(f"\n📈 TOTAL RECORDS ACROSS ALL TABLES: {total_records}")
        
        # Detailed relationship checks
        print("\n🔗 RELATIONSHIP CHECKS:")
        
        # Users by role
        admin_count = db.query(User).filter(User.role == 'admin').count()
        doctor_count = db.query(User).filter(User.role == 'doctor').count()
        patient_count = db.query(User).filter(User.role == 'patient').count()
        
        print(f"  👑 Admin users: {admin_count}")
        print(f"  👨‍⚕️ Doctor users: {doctor_count}")
        print(f"  🤰 Patient users: {patient_count}")
        
        # Doctor validations
        valid_doctors = db.query(Doctor).filter(Doctor.is_valid == True).count()
        print(f"  ✅ Valid doctors: {valid_doctors}")
        
        # Patient assignments
        active_assignments = db.query(DoctorPatientAssociation).filter(
            DoctorPatientAssociation.status == 'active'
        ).count()
        print(f"  🔗 Active doctor-patient assignments: {active_assignments}")
        
        # High-risk pregnancies
        high_risk_pregnancies = db.query(PregnancyInfo).filter(
            PregnancyInfo.is_high_risk == True
        ).count()
        print(f"  ⚠️ High-risk pregnancies: {high_risk_pregnancies}")
        
        # Records by source
        clinic_records = db.query(Record).filter(Record.source == 'clinic').count()
        self_records = db.query(Record).filter(Record.source == 'self').count()
        print(f"  🏥 Clinic records: {clinic_records}")
        print(f"  📱 Self-monitoring records: {self_records}")
        
        # Notifications by status
        unread_notifications = db.query(Notification).filter(
            Notification.status == 'unread'
        ).count()
        read_notifications = db.query(Notification).filter(
            Notification.status == 'read'
        ).count()
        print(f"  📧 Unread notifications: {unread_notifications}")
        print(f"  ✉️ Read notifications: {read_notifications}")
        
        # Fetal monitoring by type
        clinic_sessions = db.query(FetalMonitoringSession).filter(
            FetalMonitoringSession.monitoring_type == 'clinic'
        ).count()
        home_sessions = db.query(FetalMonitoringSession).filter(
            FetalMonitoringSession.monitoring_type == 'home'
        ).count()
        print(f"  🏥 Clinic monitoring sessions: {clinic_sessions}")
        print(f"  🏠 Home monitoring sessions: {home_sessions}")
        
        # Results by classification
        normal_results = db.query(FetalMonitoringResult).filter(
            FetalMonitoringResult.overall_classification == 'normal'
        ).count()
        concerning_results = db.query(FetalMonitoringResult).filter(
            FetalMonitoringResult.overall_classification == 'concerning'
        ).count()
        abnormal_results = db.query(FetalMonitoringResult).filter(
            FetalMonitoringResult.overall_classification == 'abnormal'
        ).count()
        print(f"  ✅ Normal monitoring results: {normal_results}")
        print(f"  ⚠️ Concerning monitoring results: {concerning_results}")
        print(f"  ❌ Abnormal monitoring results: {abnormal_results}")
        
        print("\n📋 SAMPLE DATA:")
        
        # Sample users
        sample_patients = db.query(User).filter(User.role == 'patient').limit(3).all()
        print("  🤰 Sample patients:")
        for patient in sample_patients:
            print(f"    - {patient.name} ({patient.email})")
        
        sample_doctors = db.query(User).filter(User.role == 'doctor').limit(3).all()
        print("  👨‍⚕️ Sample doctors:")
        for doctor in sample_doctors:
            print(f"    - {doctor.name} ({doctor.email})")
        
        # Sample monitoring sessions
        sample_sessions = db.query(FetalMonitoringSession).limit(3).all()
        print("  📊 Sample monitoring sessions:")
        for session in sample_sessions:
            patient_name = db.query(Patient).filter(Patient.id == session.patient_id).first()
            patient_user = db.query(User).filter(User.id == patient_name.user_id).first() if patient_name else None
            print(f"    - {session.monitoring_type.value} session for {patient_user.name if patient_user else 'Unknown'} (GA: {session.gestational_age} weeks)")
        
        print("\n" + "=" * 60)
        print("🎉 DATABASE SEEDING COMPLETE!")
        print("🔑 All user password: gandhi12345")
        print("📝 The system now has comprehensive test data for:")
        print("   • User management (admins, doctors, patients)")
        print("   • Doctor-patient relationships")
        print("   • Medical records and notifications") 
        print("   • Pregnancy tracking and monitoring")
        print("   • Fetal heart rate monitoring")
        print("   • Patient status history")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during check: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    comprehensive_check()
