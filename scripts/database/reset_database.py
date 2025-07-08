#!/usr/bin/env python3
"""
Script untuk reset database dan migrasi Alembic
Usage: python reset_database.py
"""

import os
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.base import Base
from app.models import medical, patient_status_history

def reset_database():
    """Reset database dan buat ulang semua table"""
    print("🔄 Starting database reset...")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        # Drop alembic version table first
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
            conn.commit()
            print("✅ Dropped alembic_version table")
        
        # Drop all tables in correct order (reverse dependency)
        print("🗑️  Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped successfully")
        
        # Create all tables
        print("🏗️  Creating all tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
        
        print("\n🎉 Database reset completed!")
        print("\n📝 Next steps:")
        print("1. Run: alembic stamp head")
        print("2. Run: alembic revision --autogenerate -m 'Initial migration'")
        print("3. Run: alembic upgrade head")
        
    except Exception as e:
        print(f"❌ Error during database reset: {e}")
        sys.exit(1)

if __name__ == "__main__":
    reset_database()
