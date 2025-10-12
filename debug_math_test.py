#!/usr/bin/env python3
"""
Debug test to see the actual response structure from the AI Tutor API
"""

import requests
import json
import sys

def test_ai_endpoint():
    base_url = "https://dhruv-tutor-upgrade.preview.emergentagent.com/api"
    
    # Authenticate first
    login_data = {
        "email": "test@dhruvai.com",
        "password": "password123"
    }
    
    print("🔐 Authenticating...")
    auth_response = requests.post(
        f"{base_url}/auth/login",
        json=login_data,
        headers={'Content-Type': 'application/json'},
        timeout=30
    )
    
    if auth_response.status_code != 200:
        print(f"❌ Authentication failed: {auth_response.status_code}")
        return
    
    token = auth_response.json().get('token')
    print(f"✅ Authenticated, token: {token[:20]}...")
    
    # Test the AI endpoint
    print("\n📝 Testing /api/ai/dual-response endpoint...")
    
    test_data = {
        "message": "Solve x^2 - 5x + 6 = 0 step by step",
        "subject": "Mathematics"
    }
    
    try:
        response = requests.post(
            f"{base_url}/ai/dual-response",
            json=test_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            },
            timeout=60
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"\n📋 FULL RESPONSE STRUCTURE:")
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError:
                print(f"❌ Response is not valid JSON")
                print(f"Raw response: {response.text}")
        else:
            print(f"❌ Request failed")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw error: {response.text}")
                
    except Exception as e:
        print(f"❌ Request exception: {str(e)}")

if __name__ == "__main__":
    test_ai_endpoint()