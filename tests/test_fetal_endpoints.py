"""
Simple test script to verify the fetal monitoring endpoints work
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# Test data
LOGIN_DATA = {
    "email": "alice.thompson@gmail.com",  # Patient user
    "password": "gandhi1245"
}

DOCTOR_LOGIN_DATA = {
    "email": "sarah.johnson@hospital.com",  # Doctor user
    "password": "gandhi1245"
}

def test_login():
    """Test user login"""
    print("🔐 Testing login...")
    
    response = requests.post(f"{BASE_URL}/login", json=LOGIN_DATA)
    if response.status_code == 200:
        token = response.json().get("access_token")
        print("✅ Patient login successful")
        return token
    else:
        print(f"❌ Patient login failed: {response.status_code} - {response.text}")
        return None

def test_doctor_login():
    """Test doctor login"""
    print("🔐 Testing doctor login...")
    
    response = requests.post(f"{BASE_URL}/login", json=DOCTOR_LOGIN_DATA)
    if response.status_code == 200:
        token = response.json().get("access_token")
        print("✅ Doctor login successful")
        return token
    else:
        print(f"❌ Doctor login failed: {response.status_code} - {response.text}")
        return None

def test_fetal_classification(token):
    """Test fetal heart rate classification"""
    print("📊 Testing fetal classification...")
    
    headers = {"Authorization": f"Bearer {token}"}
    classification_data = {
        "fhr_data": [
            {
                "timestamp": "2025-07-03T10:30:00Z",
                "bpm": 140,
                "signal_quality": 0.85
            },
            {
                "timestamp": "2025-07-03T10:30:30Z",
                "bpm": 142,
                "signal_quality": 0.87
            },
            {
                "timestamp": "2025-07-03T10:31:00Z",
                "bpm": 138,
                "signal_quality": 0.83
            }
        ],
        "gestational_age": 32,
        "maternal_age": 28,
        "duration_minutes": 30
    }
    
    response = requests.post(f"{BASE_URL}/fetal/classify", json=classification_data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print("✅ Fetal classification successful")
        print(f"   Classification: {result.get('overall_classification')}")
        print(f"   Risk Level: {result.get('risk_level')}")
        return result
    else:
        print(f"❌ Fetal classification failed: {response.status_code} - {response.text}")
        return None

def test_get_fetal_sessions(token):
    """Test getting fetal monitoring sessions"""
    print("📋 Testing get fetal sessions...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/fetal/sessions", headers=headers)
    if response.status_code == 200:
        result = response.json()
        print("✅ Get fetal sessions successful")
        print(f"   Found {result.get('total_count')} sessions")
        return result
    else:
        print(f"❌ Get fetal sessions failed: {response.status_code} - {response.text}")
        return None

def test_get_pregnancy_info(token, patient_id):
    """Test getting pregnancy information"""
    print("🤱 Testing get pregnancy info...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/fetal/pregnancy-info/{patient_id}", headers=headers)
    if response.status_code == 200:
        result = response.json()
        print("✅ Get pregnancy info successful")
        print(f"   Gestational age: {result.get('gestational_age')} weeks")
        return result
    else:
        print(f"❌ Get pregnancy info failed: {response.status_code} - {response.text}")
        return None

def test_endpoints():
    """Main test function"""
    print("🧪 Starting API endpoint tests...")
    print("-" * 50)
    
    # Test patient login
    patient_token = test_login()
    if not patient_token:
        return
    
    # Test doctor login
    doctor_token = test_doctor_login()
    if not doctor_token:
        return
    
    print("-" * 50)
    
    # Test fetal classification with patient token
    classification_result = test_fetal_classification(patient_token)
    
    # Test getting fetal sessions
    sessions_result = test_get_fetal_sessions(patient_token)
    
    # Test pregnancy info (patient ID 1 should exist from seeding)
    pregnancy_result = test_get_pregnancy_info(patient_token, 1)
    
    print("-" * 50)
    print("🎉 API tests completed!")

if __name__ == "__main__":
    test_endpoints()
