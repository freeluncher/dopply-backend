#!/usr/bin/env python3
"""
Add sample fetal monitoring data for complete system demonstration
"""

import sys
import os
import uuid
import random
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.medical import (
    Patient, Doctor, User, FetalMonitoringSession, MonitoringType,
    FetalHeartRateReading, FetalClassification, FetalMonitoringResult,
    OverallClassification, RiskLevel
)
from app.core.time_utils import get_local_naive_now

def add_fetal_monitoring_data():
    """Add sample fetal monitoring sessions, readings, and results"""
    print("📊 Adding fetal monitoring data...")
    
    db = SessionLocal()
    try:
        # Check if sessions already exist
        existing_sessions = db.query(FetalMonitoringSession).count()
        if existing_sessions > 0:
            print(f"✅ Fetal monitoring sessions already exist ({existing_sessions}), skipping...")
            return
        
        patients = db.query(Patient).limit(3).all()  # Use first 3 patients
        doctors = db.query(Doctor).all()
        
        sessions_added = 0
        
        for i, patient in enumerate(patients):
            # Get assigned doctor
            doctor = doctors[i % len(doctors)]
            
            # Create 2 sessions per patient (1 clinic, 1 home)
            for session_type in [MonitoringType.clinic, MonitoringType.home]:
                session_id = str(uuid.uuid4())
                
                start_time = get_local_naive_now() - timedelta(days=7 * sessions_added)
                end_time = start_time + timedelta(minutes=30)
                
                session = FetalMonitoringSession(
                    id=session_id,
                    patient_id=patient.id,
                    doctor_id=doctor.doctor_id if session_type == MonitoringType.clinic else None,
                    monitoring_type=session_type,
                    gestational_age=28 + sessions_added * 2,
                    start_time=start_time,
                    end_time=end_time,
                    notes="Routine monitoring session" if session_type == MonitoringType.clinic else "Home monitoring with mobile app",
                    doctor_notes="Normal session" if session_type == MonitoringType.clinic else None,
                    shared_with_doctor=session_type == MonitoringType.home,
                    created_at=start_time,
                    updated_at=start_time
                )
                
                db.add(session)
                db.flush()  # Get session ID
                
                # Add heart rate readings for this session
                add_heart_rate_readings(db, session)
                
                # Add monitoring result for this session
                add_monitoring_result(db, session)
                
                sessions_added += 1
        
        db.commit()
        print(f"✅ Added {sessions_added} monitoring sessions with readings and results")
        
    except Exception as e:
        print(f"❌ Error adding fetal monitoring data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def add_heart_rate_readings(db: Session, session: FetalMonitoringSession):
    """Add heart rate readings for a session"""
    
    # Generate 30 readings (every minute for 30 minutes)
    base_bpm = 140
    readings = []
    
    for i in range(30):
        timestamp = session.start_time + timedelta(minutes=i)
        
        # Simulate realistic heart rate with some variation
        variation = random.randint(-10, 15)
        bpm = base_bpm + variation
        bpm = max(110, min(180, bpm))  # Keep in realistic range
        
        # Determine classification
        if bpm < 120:
            classification = FetalClassification.bradycardia
        elif bpm > 160:
            classification = FetalClassification.tachycardia
        elif abs(variation) > 12:
            classification = FetalClassification.irregular
        else:
            classification = FetalClassification.normal
        
        reading = FetalHeartRateReading(
            session_id=session.id,
            timestamp=timestamp,
            bpm=bpm,
            signal_quality=0.85 + random.uniform(0, 0.15),  # Good signal quality
            classification=classification,
            created_at=timestamp
        )
        readings.append(reading)
    
    db.add_all(readings)

def add_monitoring_result(db: Session, session: FetalMonitoringSession):
    """Add monitoring result for a session"""
    
    # Calculate realistic results based on session
    average_bpm = 140.0 + random.uniform(-5, 5)
    baseline_variability = 10.0 + random.uniform(-3, 5)
    
    # Determine overall classification based on data
    if session.gestational_age < 26:
        # Earlier pregnancy - might be more concerning
        if random.random() < 0.3:  # 30% chance of concerning result
            overall_classification = OverallClassification.concerning
            risk_level = RiskLevel.medium
            findings = ["Reduced baseline variability for gestational age", "Monitor closely"]
            recommendations = ["Increase monitoring frequency", "Follow-up in 3 days"]
        else:
            overall_classification = OverallClassification.normal
            risk_level = RiskLevel.low
            findings = ["Normal heart rate pattern for gestational age"]
            recommendations = ["Continue routine monitoring"]
    else:
        # Later pregnancy - more stable
        if random.random() < 0.1:  # 10% chance of abnormal result
            overall_classification = OverallClassification.abnormal
            risk_level = RiskLevel.high
            findings = ["Prolonged decelerations detected", "Fetal distress indicators"]
            recommendations = ["Immediate medical evaluation", "Consider delivery planning"]
        elif random.random() < 0.2:  # 20% chance of concerning result
            overall_classification = OverallClassification.concerning
            risk_level = RiskLevel.medium
            findings = ["Occasional decelerations", "Slightly reduced variability"]
            recommendations = ["Increased monitoring", "Recheck in 1 week"]
        else:
            overall_classification = OverallClassification.normal
            risk_level = RiskLevel.low
            findings = ["Normal fetal heart rate pattern", "Good baseline variability", "Reactive non-stress test"]
            recommendations = ["Continue routine prenatal care", "Next appointment as scheduled"]
    
    result = FetalMonitoringResult(
        session_id=session.id,
        overall_classification=overall_classification,
        average_bpm=average_bpm,
        baseline_variability=baseline_variability,
        findings=findings,
        recommendations=recommendations,
        risk_level=risk_level,
        created_at=session.created_at
    )
    
    db.add(result)

def main():
    """Add fetal monitoring data"""
    print("🩺 Adding fetal monitoring data for complete system...")
    print("-" * 50)
    
    try:
        add_fetal_monitoring_data()
        
        print("-" * 50)
        print("🎉 Fetal monitoring data added successfully!")
        
        # Final verification
        db = SessionLocal()
        try:
            sessions = db.query(FetalMonitoringSession).count()
            results = db.query(FetalMonitoringResult).count()
            readings = db.query(FetalHeartRateReading).count()
            
            print("\n📊 Fetal monitoring counts:")
            print(f"  Sessions: {sessions}")
            print(f"  Results: {results}")
            print(f"  Heart rate readings: {readings}")
            
        finally:
            db.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
