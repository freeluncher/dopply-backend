#!/usr/bin/env python3
"""
Test script for refresh token functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_refresh_tokens():
    print("🧪 Testing Refresh Token Implementation...")
    print("=" * 60)
    
    # Test 1: Login and get both tokens
    print("\n1️⃣ Testing Login (should return both tokens)")
    login_data = {
        "email": "alice.thompson@gmail.com",
        "password": "gandhi12345"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/login", json=login_data)
        if response.status_code == 200:
            tokens = response.json()
            print(f"✅ Login successful!")
            print(f"   📧 User: {tokens.get('name')} ({tokens.get('email')})")
            print(f"   🎫 Access Token: {tokens.get('access_token')[:50]}...")
            print(f"   🔄 Refresh Token: {tokens.get('refresh_token')[:50]}...")
            print(f"   👤 Role: {tokens.get('role')}")
            
            access_token = tokens.get('access_token')
            refresh_token = tokens.get('refresh_token')
            
            if not refresh_token:
                print("❌ ERROR: No refresh token returned!")
                return False
                
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Login request failed: {e}")
        return False
    
    # Test 2: Use access token for API call
    print("\n2️⃣ Testing Access Token Usage")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/api/v1/records", headers=headers)
        if response.status_code == 200:
            records = response.json()
            print(f"✅ Access token works! Found {len(records)} records")
        else:
            print(f"⚠️ Access token test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Access token test error: {e}")
    
    # Test 3: Use refresh token to get new access token
    print("\n3️⃣ Testing Refresh Token Usage")
    try:
        refresh_data = {"refresh_token": refresh_token}
        response = requests.post(f"{BASE_URL}/api/v1/auth/refresh", json=refresh_data)
        
        if response.status_code == 200:
            new_tokens = response.json()
            print(f"✅ Refresh token works!")
            print(f"   🆕 New Access Token: {new_tokens.get('access_token')[:50]}...")
            print(f"   🔄 Refresh Token: {new_tokens.get('refresh_token')[:50]}...")
            print(f"   🏷️ Token Type: {new_tokens.get('token_type')}")
            
            new_access_token = new_tokens.get('access_token')
            
            # Test 4: Use new access token
            print("\n4️⃣ Testing New Access Token")
            headers = {"Authorization": f"Bearer {new_access_token}"}
            response = requests.get(f"{BASE_URL}/api/v1/records", headers=headers)
            if response.status_code == 200:
                records = response.json()
                print(f"✅ New access token works! Found {len(records)} records")
            else:
                print(f"⚠️ New access token test failed: {response.status_code}")
                
        else:
            print(f"❌ Refresh token failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Refresh token test error: {e}")
        return False
    
    # Test 5: Test invalid refresh token
    print("\n5️⃣ Testing Invalid Refresh Token")
    try:
        invalid_refresh_data = {"refresh_token": "invalid_token_here"}
        response = requests.post(f"{BASE_URL}/api/v1/auth/refresh", json=invalid_refresh_data)
        
        if response.status_code == 401:
            print("✅ Invalid refresh token properly rejected!")
        else:
            print(f"⚠️ Expected 401, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Invalid refresh token test error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Refresh Token Implementation Test Complete!")
    return True

def test_token_structure():
    """Test the structure and content of tokens"""
    print("\n🔍 Testing Token Structure...")
    
    # Import JWT library to decode tokens (for testing only)
    try:
        from jose import jwt
        from app.core.config import settings
        
        # Login to get tokens
        login_data = {
            "email": "alice.thompson@gmail.com", 
            "password": "gandhi12345"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/login", json=login_data)
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens.get('access_token')
            refresh_token = tokens.get('refresh_token')
            
            # Decode access token (without verification for testing)
            access_payload = jwt.decode(access_token, options={"verify_signature": False})
            print(f"📋 Access Token Payload:")
            for key, value in access_payload.items():
                if key == 'exp':
                    exp_time = datetime.fromtimestamp(value)
                    print(f"   {key}: {value} ({exp_time})")
                else:
                    print(f"   {key}: {value}")
            
            # Decode refresh token
            refresh_payload = jwt.decode(refresh_token, options={"verify_signature": False})
            print(f"\n🔄 Refresh Token Payload:")
            for key, value in refresh_payload.items():
                if key == 'exp':
                    exp_time = datetime.fromtimestamp(value)
                    print(f"   {key}: {value} ({exp_time})")
                else:
                    print(f"   {key}: {value}")
                    
    except ImportError:
        print("⚠️ JWT library not available for token structure testing")
    except Exception as e:
        print(f"❌ Token structure test error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Refresh Token Tests...")
    print(f"📡 Testing against: {BASE_URL}")
    print(f"🕐 Time: {datetime.now()}")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code != 200:
            print("❌ Server doesn't appear to be running!")
            print("   Please start the server with: uvicorn app.main:app --reload")
            exit(1)
    except:
        print("❌ Cannot connect to server!")
        print("   Please start the server with: uvicorn app.main:app --reload")
        exit(1)
    
    # Run tests
    success = test_refresh_tokens()
    test_token_structure()
    
    if success:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n❌ Some tests failed!")
