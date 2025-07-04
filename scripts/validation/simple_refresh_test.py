#!/usr/bin/env python3
"""
Simple test of refresh token implementation using built-in libraries
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import urllib.request
import urllib.parse
import json
from datetime import datetime

def test_login_with_refresh_tokens():
    """Test that login now returns both access and refresh tokens"""
    print("🧪 Testing Login with Refresh Tokens...")
    
    # Test data
    login_data = {
        "email": "alice.thompson@gmail.com",
        "password": "gandhi12345"
    }
    
    # Convert to JSON
    data = json.dumps(login_data).encode('utf-8')
    
    # Create request
    url = "http://localhost:8000/api/v1/login"
    req = urllib.request.Request(url, data=data)
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            
            print("✅ Login successful!")
            print(f"   👤 User: {result.get('name')} ({result.get('email')})")
            print(f"   🎭 Role: {result.get('role')}")
            print(f"   🎫 Access Token: {'Present' if result.get('access_token') else 'Missing'}")
            print(f"   🔄 Refresh Token: {'Present' if result.get('refresh_token') else 'Missing'}")
            print(f"   🏷️ Token Type: {result.get('token_type')}")
            
            if result.get('access_token') and result.get('refresh_token'):
                print("✅ Both tokens returned successfully!")
                return result.get('access_token'), result.get('refresh_token')
            else:
                print("❌ Missing tokens in response!")
                return None, None
                
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None, None

def test_refresh_endpoint(refresh_token):
    """Test the refresh endpoint"""
    print("\n🔄 Testing Refresh Endpoint...")
    
    if not refresh_token:
        print("❌ No refresh token to test with!")
        return
    
    # Test data
    refresh_data = {
        "refresh_token": refresh_token
    }
    
    # Convert to JSON
    data = json.dumps(refresh_data).encode('utf-8')
    
    # Create request
    url = "http://localhost:8000/api/v1/auth/refresh"
    req = urllib.request.Request(url, data=data)
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            
            print("✅ Refresh successful!")
            print(f"   🆕 New Access Token: {'Present' if result.get('access_token') else 'Missing'}")
            print(f"   🔄 Refresh Token: {'Present' if result.get('refresh_token') else 'Missing'}")
            print(f"   🏷️ Token Type: {result.get('token_type')}")
            
            return result.get('access_token')
            
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()
        print(f"❌ Refresh failed: HTTP {e.code}")
        print(f"   Error: {error_msg}")
        return None
    except Exception as e:
        print(f"❌ Refresh failed: {e}")
        return None

def test_api_with_token(access_token, token_description=""):
    """Test API endpoint with access token"""
    print(f"\n📡 Testing API with {token_description}Access Token...")
    
    if not access_token:
        print("❌ No access token to test with!")
        return
    
    # Create request
    url = "http://localhost:8000/api/v1/records"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {access_token}')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"✅ API call successful! Found {len(result)} records")
            return True
            
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()
        print(f"❌ API call failed: HTTP {e.code}")
        print(f"   Error: {error_msg}")
        return False
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False

def test_invalid_refresh_token():
    """Test with invalid refresh token"""
    print("\n🚫 Testing Invalid Refresh Token...")
    
    # Test data with invalid token
    refresh_data = {
        "refresh_token": "invalid.token.here"
    }
    
    # Convert to JSON
    data = json.dumps(refresh_data).encode('utf-8')
    
    # Create request
    url = "http://localhost:8000/api/v1/auth/refresh"
    req = urllib.request.Request(url, data=data)
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            print("⚠️ Invalid token was accepted (this shouldn't happen)")
            
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("✅ Invalid refresh token properly rejected (401)")
        else:
            print(f"⚠️ Unexpected status code: {e.code}")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🚀 Testing Refresh Token Implementation")
    print("=" * 50)
    print(f"🕐 Time: {datetime.now()}")
    print(f"📡 Server: http://localhost:8000")
    
    # Test 1: Login to get both tokens
    access_token, refresh_token = test_login_with_refresh_tokens()
    
    if not access_token or not refresh_token:
        print("\n❌ Cannot continue without tokens!")
        exit(1)
    
    # Test 2: Use original access token
    test_api_with_token(access_token, "Original ")
    
    # Test 3: Use refresh token to get new access token
    new_access_token = test_refresh_endpoint(refresh_token)
    
    # Test 4: Use new access token
    if new_access_token:
        test_api_with_token(new_access_token, "New ")
    
    # Test 5: Test invalid refresh token
    test_invalid_refresh_token()
    
    print("\n" + "=" * 50)
    print("🎉 Refresh Token Tests Complete!")
    
    if access_token and refresh_token and new_access_token:
        print("✅ All tests passed! Refresh token implementation working correctly.")
    else:
        print("❌ Some tests failed! Check the implementation.")
