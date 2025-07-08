import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.config import settings
from sqlalchemy import create_engine, text

print("🔍 Detailed Database Check:")
print("=" * 50)

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    
    # Check all tables with data
    tables = ['users', 'patients', 'doctors', 'doctor_patient', 'pregnancy_info', 'records', 'notifications']
    
    for table in tables:
        try:
            result = conn.execute(text(f'SELECT COUNT(*) FROM {table}'))
            count = result.fetchone()[0]
            status = "✅" if count > 0 else "⚪"
            print(f"{status} {table}: {count} records")
        except Exception as e:
            print(f"❌ {table}: error - {e}")

print("\n👥 Sample Users:")
with engine.connect() as conn:
    result = conn.execute(text('SELECT name, email, role FROM users ORDER BY role, name'))
    current_role = None
    for row in result:
        if row[2] != current_role:
            current_role = row[2]
            print(f"\n{current_role.upper()}:")
        print(f"  - {row[0]} ({row[1]})")

print("\n🔗 Doctor-Patient Assignments:")
with engine.connect() as conn:
    result = conn.execute(text('''
        SELECT u1.name as doctor_name, u2.name as patient_name, dp.status
        FROM doctor_patient dp
        JOIN users u1 ON dp.doctor_id = u1.id  
        JOIN patients p ON dp.patient_id = p.id
        JOIN users u2 ON p.user_id = u2.id
        ORDER BY u1.name
    '''))
    for row in result:
        print(f"  👩‍⚕️ {row[0]} → 🤰 {row[1]} ({row[2]})")

print(f"\n🎉 Database berhasil dipopulasi dengan data sample!")
print(f"🔑 Password untuk semua user: gandhi12345")
