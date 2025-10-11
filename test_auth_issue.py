#!/usr/bin/env python3

import requests
import json

def test_auth_issue():
    """Test if the issue is with authentication"""
    
    print("🔍 TESTING AUTHENTICATION ISSUE")
    print("="*50)
    
    base_url = "https://modular-backend-5.preview.emergentagent.com/api"
    
    # Step 1: Login and get token
    print("1. Getting authentication token...")
    login_data = {
        "email": "test@dhruvai.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=30)
        print(f"   Login status: {response.status_code}")
        
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data['token']
            user_id = auth_data['user'].get('user_id')
            print(f"   ✅ Token obtained: {token[:20]}...")
            print(f"   User ID: {user_id}")
        else:
            print(f"   ❌ Login failed: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return
    
    # Step 2: Test each failing endpoint with detailed error analysis
    endpoints_to_test = [
        ("auto-notes/sessions", "Sessions"),
        ("auto-notes/analytics", "Analytics"), 
        ("auto-notes/class-series", "Class Series")
    ]
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    for endpoint, name in endpoints_to_test:
        print(f"\n2. Testing {name} endpoint...")
        print(f"   URL: {base_url}/{endpoint}")
        print(f"   Headers: Authorization: Bearer {token[:20]}...")
        
        try:
            response = requests.get(f"{base_url}/{endpoint}", headers=headers, timeout=30)
            print(f"   Status: {response.status_code}")
            print(f"   Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Success: {name} returned data")
                    print(f"   Response keys: {list(data.keys())}")
                    if 'sessions' in data:
                        print(f"   Sessions count: {len(data['sessions'])}")
                    elif 'total_sessions' in data:
                        print(f"   Total sessions: {data['total_sessions']}")
                    elif 'series' in data:
                        print(f"   Series count: {len(data['series'])}")
                except Exception as e:
                    print(f"   ⚠️  Response parsing error: {e}")
                    print(f"   Raw response: {response.text[:200]}...")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data}")
                except:
                    print(f"   Raw error: {response.text}")
                
                # Check if it's an authentication issue
                if response.status_code == 401:
                    print(f"   🔍 Authentication issue detected")
                elif response.status_code == 500:
                    print(f"   🔍 Server error - checking if it's ObjectId serialization")
                    
        except Exception as e:
            print(f"   ❌ Request error: {e}")
    
    # Step 3: Test a working endpoint for comparison
    print(f"\n3. Testing a working endpoint for comparison...")
    try:
        response = requests.get(f"{base_url}/user/profile", headers=headers, timeout=30)
        print(f"   Profile endpoint status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Profile endpoint works - authentication is OK")
        else:
            print(f"   ❌ Profile endpoint also fails - authentication issue")
    except Exception as e:
        print(f"   ❌ Profile test error: {e}")

if __name__ == "__main__":
    test_auth_issue()