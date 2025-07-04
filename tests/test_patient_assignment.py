#!/usr/bin/env python3
import requests
import json

# Get fresh token
login_response = requests.post("http://localhost:8000/api/v1/login", 
                              json={"email": "doctor@dopply.my.id", "password": "gandhi12345"})
if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"✅ Login successful, got token")
    
    # Test patient assignment
    headers = {"Authorization": f"Bearer {token}"}
    assign_data = {"email": "patient24@dopply.my.id", "status": "active"}
    
    print(f"\n🧪 Testing patient assignment...")
    print(f"POST /api/v1/doctors/12/assign-patient-by-email")
    print(f"Data: {assign_data}")
    
    assign_response = requests.post("http://localhost:8000/api/v1/doctors/12/assign-patient-by-email",
                                   json=assign_data, headers=headers)
    
    print(f"\n📊 Response:")
    print(f"Status: {assign_response.status_code}")
    print(f"Response: {assign_response.text}")
    
    if assign_response.status_code == 200:
        print("✅ SUCCESS: Patient assignment endpoint is now working!")
    else:
        print("❌ FAILED: There's still an issue with the patient assignment")
        
else:
    print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
