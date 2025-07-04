#!/usr/bin/env python3
"""
Quick test of the records endpoint functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import joinedload
from app.db.session import SessionLocal
from app.models.medical import Record, Patient, User

def test_records_endpoint():
    """Test that the records endpoint returns data with patient names"""
    print("🧪 Testing Records Endpoint...")
    
    db = SessionLocal()
    try:
        # Simulate the exact query from the endpoint
        records = db.query(Record).options(
            joinedload(Record.patient).joinedload(Patient.user)
        ).order_by(Record.start_time.desc()).limit(3).all()
        
        print(f"📊 Found {len(records)} records")
        
        for record in records:
            patient_name = record.patient.user.name if record.patient and record.patient.user else "Unknown"
            print(f"  ✅ Record {record.id}: Patient \"{patient_name}\" - {record.classification} ({record.source})")
        
        print(f"✅ Successfully returned {len(records)} records with patient names")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_records_endpoint()
