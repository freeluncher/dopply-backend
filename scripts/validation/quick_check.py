#!/usr/bin/env python3
"""
Script cepat untuk cek status database
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.core.config import settings
from sqlalchemy import create_engine, text

def check_database():
    print("🔍 Checking database status...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text('SHOW TABLES'))
            tables = [row[0] for row in result.fetchall()]
            
            print(f"📊 Total tables: {len(tables)}")
            if tables:
                print("Tables found:")
                for table in sorted(tables):
                    print(f"  ✓ {table}")
            else:
                print("❌ No tables found! Database is empty!")
                
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")

if __name__ == "__main__":
    check_database()
