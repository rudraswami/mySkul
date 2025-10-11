#!/usr/bin/env python3
import requests
import time
import uuid

# Test locally 
API_BASE = "http://localhost:8001/api"

def test_ai_response():
    print("🚀 Quick AI Tutor Local Test")
    print("=" * 50)
    
    # Login
    login_data = {"email": "test@dhruvai.com", "password": "password123"}
    
    try:
        print("🔐 Logging in...")
        login_response = requests.post(f"{API_BASE}/auth/login", json=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        token = login_response.json().get('token')
        print("✅ Login successful")
        
        # Test AI response
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        test_message = "What is 2 + 2?"
        request_data = {
            "message": test_message,
            "session_id": str(uuid.uuid4()),
            "subject": "Mathematics"
        }
        
        print(f"\n📝 Testing message: {test_message}")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE}/ai/dual-response",
            json=request_data,
            headers=headers,
            timeout=40  # Give it 40 seconds
        )
        
        elapsed = time.time() - start_time
        print(f"⏱️ Response time: {elapsed:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for blank responses
            primary_response = data.get('dual_response', {}).get('primary', {}).get('response', '')
            secondary_response = data.get('dual_response', {}).get('secondary', {}).get('response', '')
            
            print(f"✅ HTTP Status: 200 OK")
            print(f"📊 Primary response length: {len(primary_response)} chars")
            print(f"📊 Secondary response length: {len(secondary_response)} chars")
            
            if len(primary_response) > 20 and len(secondary_response) > 20:
                print("🎉 SUCCESS: Both responses have content!")
                print(f"📄 Primary preview: {primary_response[:100]}...")
                print(f"💬 Secondary preview: {secondary_response[:100]}...")
                return True
            else:
                print("❌ FAILURE: Blank or too short responses detected")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time if 'start_time' in locals() else 0
        print(f"⏰ TIMEOUT after {elapsed:.2f}s")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_ai_response()
    print(f"\n{'🎉 TEST PASSED' if success else '❌ TEST FAILED'}")