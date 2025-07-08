#!/usr/bin/env python3
"""
Check fetal monitoring table data
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def check_fetal_tables():
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check table counts
        result = db.execute(text("""
            SELECT 
                (SELECT COUNT(*) FROM fetal_monitoring_sessions) as sessions,
                (SELECT COUNT(*) FROM fetal_monitoring_results) as results,
                (SELECT COUNT(*) FROM fetal_heart_rate_readings) as readings
        """))
        counts = result.fetchone()
        
        print(f"📊 Fetal Monitoring Sessions: {counts.sessions}")
        print(f"📈 Fetal Monitoring Results: {counts.results}")
        print(f"💓 Heart Rate Readings: {counts.readings}")
        
        # Check for session IDs in results
        if counts.results > 0:
            result = db.execute(text("SELECT session_id FROM fetal_monitoring_results LIMIT 5"))
            session_ids = result.fetchall()
            print("\nResult session IDs:")
            for row in session_ids:
                print(f"  - {row.session_id}")
        
        # Check for session IDs in sessions
        if counts.sessions > 0:
            result = db.execute(text("SELECT session_id FROM fetal_monitoring_sessions LIMIT 5"))
            session_ids = result.fetchall()
            print("\nSession IDs:")
            for row in session_ids:
                print(f"  - {row.session_id}")
        
        # Check for duplicates in results
        if counts.results > 0:
            result = db.execute(text("""
                SELECT session_id, COUNT(*) as count 
                FROM fetal_monitoring_results 
                GROUP BY session_id 
                HAVING COUNT(*) > 1
            """))
            duplicates = result.fetchall()
            if duplicates:
                print(f"\n❌ Found {len(duplicates)} duplicate session IDs in results!")
                for dup in duplicates:
                    print(f"  - {dup.session_id} appears {dup.count} times")
            else:
                print("\n✅ No duplicate session IDs found in results")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_fetal_tables()
