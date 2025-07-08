#!/usr/bin/env python3
"""
Script untuk reset dan rebuild semua migrasi database dengan struktur yang terorganisir
Usage: python reset_migrations.py
"""

import os
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def reset_migrations():
    """Reset dan rebuild semua migrasi database"""
    print("🔄 Starting complete migration reset...")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        # Step 1: Drop alembic version table
        print("1️⃣  Cleaning Alembic version table...")
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
            conn.commit()
            print("✅ Alembic version table dropped")
        
        # Step 2: Check current database structure
        print("\n2️⃣  Current database structure:")
        with engine.connect() as conn:
            result = conn.execute(text('SHOW TABLES'))
            tables = [row[0] for row in result.fetchall()]
            for table in tables:
                print(f"   📋 {table}")
        
        print(f"\n   Total tables: {len(tables)}")
        
        # Step 3: Mark current state as our initial migration
        print("\n3️⃣  Setting up migration tracking...")
        print("   This will mark the current database state as migration: 004_fetal_monitoring")
        
        confirm = input("\n   Continue with migration setup? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ Migration reset cancelled")
            return
        
        # Step 4: Run alembic commands
        print("\n4️⃣  Setting up Alembic...")
        os.system("alembic stamp 004_fetal_monitoring")
        print("✅ Database marked as migrated to 004_fetal_monitoring")
        
        # Step 5: Verify migration state
        print("\n5️⃣  Verifying migration state...")
        os.system("alembic current")
        os.system("alembic history --verbose")
        
        print("\n🎉 Migration reset completed successfully!")
        print("\n📝 Migration structure:")
        print("   001_initial_schema       - Core tables (users, patients, doctors, doctor_patient)")
        print("   002_records_notifications - Records and notifications")  
        print("   003_patient_status_history - Patient status audit trail")
        print("   004_fetal_monitoring     - Fetal monitoring system")
        
        print("\n🔧 Next steps for future migrations:")
        print("   1. For new features: alembic revision --autogenerate -m 'Description'")
        print("   2. To apply: alembic upgrade head")
        print("   3. To rollback: alembic downgrade [revision_id]")
        
    except Exception as e:
        print(f"❌ Error during migration reset: {e}")
        sys.exit(1)

def show_migration_status():
    """Show current migration status"""
    print("📊 Current Migration Status:")
    print("=" * 50)
    try:
        os.system("alembic current")
        print("\n📜 Migration History:")
        os.system("alembic history")
    except Exception as e:
        print(f"❌ Error checking migration status: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        show_migration_status()
    else:
        reset_migrations()
