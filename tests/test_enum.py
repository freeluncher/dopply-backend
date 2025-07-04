#!/usr/bin/env python3
import sys
sys.path.append('.')
from app.models.medical import UserRole

# Test enum comparison
print('Testing enum comparisons:')
print('UserRole.doctor == "doctor":', UserRole.doctor == 'doctor')
print('UserRole.doctor.value == "doctor":', UserRole.doctor.value == 'doctor')
print('str(UserRole.doctor) == "doctor":', str(UserRole.doctor) == 'doctor')
print('str(UserRole.doctor):', str(UserRole.doctor))
print('UserRole.doctor.value:', UserRole.doctor.value)
