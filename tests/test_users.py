#!/usr/bin/env python3
import sys
sys.path.append('.')
from app.db.session import SessionLocal
from app.models.medical import User, Doctor

# Test database query
db = SessionLocal()
try:
    users = db.query(User).all()
    print('All users in database:')
    for user in users:
        print(f'  ID: {user.id}, Name: {user.name}, Email: {user.email}, Role: {user.role.value}')
    
    print('\nDoctor users:')
    doctors = db.query(User).filter(User.role.in_(['doctor'])).all()
    for doctor in doctors:
        print(f'  ID: {doctor.id}, Name: {doctor.name}, Email: {doctor.email}')
        # Check doctor table
        doctor_record = db.query(Doctor).filter(Doctor.doctor_id == doctor.id).first()
        if doctor_record:
            print(f'    Doctor record: is_valid={doctor_record.is_valid}')
        else:
            print(f'    No doctor record found')
    
finally:
    db.close()
