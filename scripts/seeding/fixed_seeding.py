#!/usr/bin/env python3
"""
Fixed seeding script that avoids duplicates and ensures referential integrity
"""

import sys
import os
import uuid
import random
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def main():
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🔧 Fixing fetal monitoring data...")
        
        # Get sessions that don't have results yet
        result = db.execute(text("""
            SELECT fms.id 
            FROM fetal_monitoring_sessions fms
            LEFT JOIN fetal_monitoring_results fmr ON fms.id = fmr.session_id
            WHERE fmr.session_id IS NULL
        """))
        sessions_without_results = [row.id for row in result.fetchall()]
        
        print(f"📊 Found {len(sessions_without_results)} sessions without results")
        
        # Create results for sessions that don't have them
        for session_id in sessions_without_results:
            overall_classification = random.choice(['normal', 'concerning', 'abnormal'])
            average_bpm = round(random.uniform(120, 180), 1)
            baseline_variability = round(random.uniform(5, 25), 1)
            
            if overall_classification == 'normal':
                findings = ['["Normal heart rate pattern", "Good baseline variability"]']
                recommendations = ['["Continue routine monitoring", "Regular prenatal care"]']
                risk_level = 'low'
            elif overall_classification == 'concerning':
                findings = ['["Slightly reduced variability", "Occasional decelerations"]']
                recommendations = ['["Increased monitoring frequency", "Follow-up in 1 week"]']
                risk_level = 'medium'
            else:  # abnormal
                findings = ['["Prolonged decelerations", "Reduced baseline variability"]']
                recommendations = ['["Immediate medical attention", "Consider delivery"]']
                risk_level = 'high'
            
            db.execute(text("""
                INSERT INTO fetal_monitoring_results 
                (session_id, overall_classification, average_bpm, baseline_variability, 
                 findings, recommendations, risk_level, created_at)
                VALUES (:session_id, :overall_classification, :average_bpm, :baseline_variability,
                        :findings, :recommendations, :risk_level, :created_at)
            """), {
                'session_id': session_id,
                'overall_classification': overall_classification,
                'average_bpm': average_bpm,
                'baseline_variability': baseline_variability,
                'findings': findings[0],
                'recommendations': recommendations[0],
                'risk_level': risk_level,
                'created_at': datetime.now()
            })
        
        # Check other tables and add data if needed
        
        # Check records table
        result = db.execute(text("SELECT COUNT(*) as count FROM records"))
        records_count = result.fetchone().count
        
        if records_count == 0:
            print("📋 Adding records...")
            # Get some patients for records
            result = db.execute(text("SELECT id FROM patients LIMIT 5"))
            patient_ids = [row.id for row in result.fetchall()]
            
            for patient_id in patient_ids:
                for i in range(2):  # 2 records per patient
                    record_id = str(uuid.uuid4())
                    db.execute(text("""
                        INSERT INTO records 
                        (id, patient_id, heart_rate, temperature, blood_pressure_systolic, 
                         blood_pressure_diastolic, notes, created_at)
                        VALUES (:id, :patient_id, :heart_rate, :temperature, :bp_sys, :bp_dia, :notes, :created_at)
                    """), {
                        'id': record_id,
                        'patient_id': patient_id,
                        'heart_rate': random.randint(60, 100),
                        'temperature': round(random.uniform(36.1, 37.2), 1),
                        'bp_sys': random.randint(110, 140),
                        'bp_dia': random.randint(70, 90),
                        'notes': f'Regular checkup #{i+1}',
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    })
        
        # Check patient_status_history table
        result = db.execute(text("SELECT COUNT(*) as count FROM patient_status_history"))
        status_count = result.fetchone().count
        
        if status_count == 0:
            print("📈 Adding patient status history...")
            result = db.execute(text("SELECT id FROM patients LIMIT 5"))
            patient_ids = [row.id for row in result.fetchall()]
            
            for patient_id in patient_ids:
                statuses = ['active', 'inactive', 'active']  # Some history
                for i, status in enumerate(statuses):
                    db.execute(text("""
                        INSERT INTO patient_status_history 
                        (patient_id, previous_status, new_status, changed_by, change_reason, created_at)
                        VALUES (:patient_id, :prev_status, :new_status, :changed_by, :reason, :created_at)
                    """), {
                        'patient_id': patient_id,
                        'prev_status': 'pending' if i == 0 else statuses[i-1],
                        'new_status': status,
                        'changed_by': 1,  # admin user
                        'reason': f'Status change #{i+1}',
                        'created_at': datetime.now() - timedelta(days=30-i*10)
                    })
        
        # Check notifications table
        result = db.execute(text("SELECT COUNT(*) as count FROM notifications"))
        notifications_count = result.fetchone().count
        
        if notifications_count == 0:
            print("🔔 Adding notifications...")
            result = db.execute(text("SELECT id FROM users WHERE role IN ('doctor', 'patient') LIMIT 8"))
            user_ids = [row.id for row in result.fetchall()]
            
            notification_types = ['appointment_reminder', 'test_result', 'medication_reminder', 'system_alert']
            
            for user_id in user_ids:
                for i in range(2):  # 2 notifications per user
                    notification_id = str(uuid.uuid4())
                    notif_type = random.choice(notification_types)
                    db.execute(text("""
                        INSERT INTO notifications 
                        (id, user_id, type, title, message, is_read, created_at)
                        VALUES (:id, :user_id, :type, :title, :message, :is_read, :created_at)
                    """), {
                        'id': notification_id,
                        'user_id': user_id,
                        'type': notif_type,
                        'title': f'{notif_type.replace("_", " ").title()} #{i+1}',
                        'message': f'This is a {notif_type} notification for user {user_id}',
                        'is_read': random.choice([True, False]),
                        'created_at': datetime.now() - timedelta(days=random.randint(1, 7))
                    })
        
        db.commit()
        print("✅ Fixed seeding completed successfully!")
        
        # Final count check
        print("\n📊 Final table counts:")
        tables = [
            'fetal_monitoring_sessions',
            'fetal_monitoring_results', 
            'fetal_heart_rate_readings',
            'records',
            'patient_status_history',
            'notifications'
        ]
        
        for table in tables:
            result = db.execute(text(f"SELECT COUNT(*) as count FROM {table}"))
            count = result.fetchone().count
            print(f"  {table}: {count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
