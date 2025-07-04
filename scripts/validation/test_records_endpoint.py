#!/usr/bin/env python3
"""
Test script to validate the records endpoint fix
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session, joinedload
from app.db.session import SessionLocal
from app.models.medical import Record, Patient, User

def test_records_endpoint_data():
    """Test that we can fetch records with patient names"""
    print("🧪 Testing records endpoint data structure...")
    
    db = SessionLocal()
    try:
        # Simulate the query from the endpoint
        records = db.query(Record).options(
            joinedload(Record.patient).joinedload(Patient.user)
        ).order_by(Record.start_time.desc()).limit(5).all()
        
        print(f"📊 Found {len(records)} records")
        
        if records:
            print("\n📋 Sample record data:")
            for i, record in enumerate(records[:3]):
                patient_name = record.patient.user.name if record.patient and record.patient.user else "Unknown"
                print(f"  {i+1}. Record ID: {record.id}")
                print(f"     Patient ID: {record.patient_id}")
                print(f"     Patient Name: {patient_name}")
                print(f"     Source: {record.source}")
                print(f"     Start Time: {record.start_time}")
                print(f"     Classification: {record.classification}")
                print()
            
            # Test creating the response structure
            print("✅ Creating response structure...")
            record_responses = []
            for record in records:
                record_dict = {
                    "id": record.id,
                    "patient_id": record.patient_id,
                    "doctor_id": record.doctor_id,
                    "source": record.source.value if hasattr(record.source, 'value') else record.source,
                    "bpm_data": record.bpm_data,
                    "start_time": record.start_time,
                    "end_time": record.end_time,
                    "classification": record.classification,
                    "notes": record.notes,
                    "shared_with": record.shared_with,
                    "patient_name": record.patient.user.name if record.patient and record.patient.user else None
                }
                record_responses.append(record_dict)
            
            print(f"✅ Successfully created {len(record_responses)} response objects")
            print(f"✅ All records have patient_name field: {all('patient_name' in r for r in record_responses)}")
            
            # Show a sample response
            if record_responses:
                sample = record_responses[0]
                print(f"\n📝 Sample response structure:")
                for key, value in sample.items():
                    if key == 'bpm_data' and value:
                        print(f"     {key}: [BPM data with {len(value)} entries]")
                    else:
                        print(f"     {key}: {value}")
        else:
            print("⚠️ No records found in database")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_records_endpoint_data()
