from app.core.config import settings
from sqlalchemy import create_engine, text

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    # Check users
    result = conn.execute(text('SELECT COUNT(*) FROM users'))
    users_count = result.fetchone()[0]
    print(f"Users: {users_count}")
    
    # Check patients  
    result = conn.execute(text('SELECT COUNT(*) FROM patients'))
    patients_count = result.fetchone()[0]
    print(f"Patients: {patients_count}")
    
    # Check doctors
    result = conn.execute(text('SELECT COUNT(*) FROM doctors'))
    doctors_count = result.fetchone()[0]
    print(f"Doctors: {doctors_count}")
    
    # Check associations
    result = conn.execute(text('SELECT COUNT(*) FROM doctor_patient'))
    assoc_count = result.fetchone()[0]
    print(f"Doctor-Patient associations: {assoc_count}")

print("Sample users:")
with engine.connect() as conn:
    result = conn.execute(text('SELECT name, email, role FROM users LIMIT 5'))
    for row in result:
        print(f"  - {row[0]} ({row[1]}) - {row[2]}")
