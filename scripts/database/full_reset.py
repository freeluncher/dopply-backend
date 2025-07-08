#!/usr/bin/env python3
"""
Script untuk melakukan full reset database dan migrasi dengan benar
"""

import os
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def full_database_reset():
    """Reset complete database dan rebuild dari awal"""
    print("🔄 Starting complete database and migration reset...")
    print("⚠️  This will completely drop and recreate the database!")
    
    confirm = input("Are you sure you want to continue? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Operation cancelled")
        return
    
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        # Step 1: Drop all tables
        print("\n1️⃣  Dropping all existing tables...")
        with engine.connect() as conn:
            # Get all tables
            result = conn.execute(text('SHOW TABLES'))
            tables = [row[0] for row in result.fetchall()]
            
            # Disable foreign key checks
            conn.execute(text('SET FOREIGN_KEY_CHECKS = 0'))
            
            # Drop all tables
            for table in tables:
                conn.execute(text(f'DROP TABLE IF EXISTS {table}'))
                print(f"   ✓ Dropped {table}")
            
            # Re-enable foreign key checks
            conn.execute(text('SET FOREIGN_KEY_CHECKS = 1'))
            
            conn.commit()
        
        print("✅ All tables dropped successfully")
        
        # Step 2: Run Alembic migrations from scratch
        print("\n2️⃣  Running Alembic migrations from scratch...")
        
        # Apply all migrations in sequence
        migrations = [
            "001_initial_schema",
            "002_records_notifications", 
            "003_patient_status_history",
            "004_fetal_monitoring"
        ]
        
        for migration in migrations:
            print(f"📦 Applying {migration}...")
            result = os.system(f"alembic upgrade {migration}")
            if result != 0:
                print(f"❌ Failed to apply {migration}")
                return False
            print(f"✅ {migration} applied successfully")
        
        # Step 3: Verify final state
        print("\n3️⃣  Verifying final state...")
        with engine.connect() as conn:
            result = conn.execute(text('SHOW TABLES'))
            final_tables = [row[0] for row in result.fetchall()]
            
            print(f"📊 Final database tables ({len(final_tables)}):")
            for table in sorted(final_tables):
                print(f"  ✓ {table}")
        
        # Check Alembic state
        print("\n📍 Final migration state:")
        os.system("alembic current")
        
        print("\n🎉 Complete database reset successful!")
        print("\n📝 Your database is now clean and properly migrated")
        print("📝 All migrations are properly tracked and in sync")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during reset: {e}")
        return False

if __name__ == "__main__":
    full_database_reset()
