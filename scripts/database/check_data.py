#!/usr/bin/env python3
"""
Script untuk cek data dalam database
"""

from app.core.config import settings
from sqlalchemy import create_engine, text

def check_data():
    print("🔍 Checking database data...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            # Get all tables
            result = conn.execute(text('SHOW TABLES'))
            tables = [row[0] for row in result.fetchall()]
            
            # Check data in each table
            total_records = 0
            for table in sorted(tables):
                if table != 'alembic_version':  # Skip alembic table
                    try:
                        count_result = conn.execute(text(f'SELECT COUNT(*) FROM {table}'))
                        count = count_result.fetchone()[0]
                        total_records += count
                        
                        if count > 0:
                            print(f"  ✓ {table}: {count} records")
                        else:
                            print(f"  ⚪ {table}: empty")
                            
                    except Exception as e:
                        print(f"  ❌ {table}: error - {e}")
            
            print(f"\n📊 Total records across all tables: {total_records}")
            
            if total_records == 0:
                print("❌ Database tables exist but contain no data!")
            else:
                print("✅ Database has data")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_data()
