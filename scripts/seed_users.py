#!/usr/bin/env python3
"""
Seed script untuk menambahkan user dokter dan pasien ke database.
Usage: python scripts/seed_users.py
"""

import sys
import os
from pathlib import Path

# Add the app directory to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.medical import User, UserRole, Patient
from app.core.security import get_password_hash
from app.core.time_utils import get_local_naive_now
from datetime import date

def create_seed_users():
    """Create seed users for testing"""
    db: Session = SessionLocal()
    
    try:
        # Check if users already exist
        existing_doctor = db.query(User).filter(User.email == "dokter@gmail.com").first()
        existing_patient = db.query(User).filter(User.email == "pasien@gmail.com").first()
        
        if existing_doctor:
            print("❌ User dokter@gmail.com sudah ada di database")
        else:
            # Create doctor user
            doctor_user = User(
                name="Dr. Dokter Test",
                email="dokter@gmail.com",
                password_hash=get_password_hash("password123"),
                role=UserRole.doctor,
                specialization="Obstetri & Ginekologi",
                is_verified=True,  # Doctor sudah terverifikasi
                created_at=get_local_naive_now()
            )
            db.add(doctor_user)
            print("✅ Created doctor user: dokter@gmail.com")
        
        if existing_patient:
            print("❌ User pasien@gmail.com sudah ada di database")
        else:
            # Create patient user
            patient_user = User(
                name="Pasien Test",
                email="pasien@gmail.com",
                password_hash=get_password_hash("password123"),
                role=UserRole.patient,
                created_at=get_local_naive_now()
            )
            db.add(patient_user)
            print("✅ Created patient user: pasien@gmail.com")
        
        # Commit the users first
        db.commit()
        
        # Create patient record for the patient user (if not exists)
        if not existing_patient:
            # Get the patient user we just created
            patient_user_db = db.query(User).filter(User.email == "pasien@gmail.com").first()
            
            # Check if patient record already exists
            existing_patient_record = db.query(Patient).filter(Patient.user_id == patient_user_db.id).first()
            
            if not existing_patient_record:
                from datetime import timedelta
                hpht = date.today() - timedelta(weeks=20)
                patient_record = Patient(
                    user_id=patient_user_db.id,
                    name="Pasien Test",
                    email="pasien@gmail.com",
                    hpht=hpht,  # HPHT = hari ini - 20 minggu
                    birth_date=date(1995, 5, 15),
                    address="Jakarta, Indonesia",
                    medical_note="Patient test untuk development"
                )
                db.add(patient_record)
                print("✅ Created patient record for pasien@gmail.com")
            else:
                print("❌ Patient record untuk pasien@gmail.com sudah ada")
        
        # Create admin user if not exists
        existing_admin = db.query(User).filter(User.email == "admin@gmail.com").first()
        if not existing_admin:
            admin_user = User(
                name="Admin Test",
                email="admin@gmail.com",
                password_hash=get_password_hash("password123"),
                role=UserRole.admin,
                created_at=get_local_naive_now()
            )
            db.add(admin_user)
            print("✅ Created admin user: admin@gmail.com")
        else:
            print("❌ User admin@gmail.com sudah ada di database")
        
        db.commit()
        print("\n🎉 Seeding completed successfully!")
        print("\n📋 Login credentials:")
        print("👨‍⚕️ Doctor: dokter@gmail.com / password123")
        print("👤 Patient: pasien@gmail.com / password123") 
        print("👨‍💼 Admin: admin@gmail.com / password123")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def check_existing_users():
    """Check existing users in database"""
    db: Session = SessionLocal()
    
    try:
        users = db.query(User).all()
        
        if not users:
            print("📭 No users found in database")
            return
        
        print("\n👥 Existing users in database:")
        print("-" * 50)
        for user in users:
            status = "✅ Verified" if user.role == UserRole.doctor and user.is_verified else ""
            if user.role == UserRole.doctor and not user.is_verified:
                status = "❌ Not verified"
            print(f"📧 {user.email:<25} | 👤 {user.role.value:<10} | {user.name} {status}")
        
    except Exception as e:
        print(f"❌ Error checking users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Starting user seeding...")
    
    # Check existing users first
    check_existing_users()
    
    # Create seed users
    create_seed_users()
    
    # Check again after seeding
    print("\n" + "="*60)
    check_existing_users()
