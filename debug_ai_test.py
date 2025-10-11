#!/usr/bin/env python3
import requests
import time
import uuid
import json

# Test locally 
API_BASE = "http://localhost:8001/api"

def debug_ai_response():
    print("🔍 DEBUG AI Tutor Response Pipeline")
    print("=" * 60)
    
    # Step 1: Login
    login_data = {"email": "test@dhruvai.com", "password": "password123"}
    
    try:
        print("🔐 Step 1: Authentication")
        login_response = requests.post(f"{API_BASE}/auth/login", json=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return False
        
        token = login_response.json().get('token')
        print("✅ Login successful")
        
        # Step 2: Test Health Check
        print("\n🏥 Step 2: API Health Check")
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        try:
            health_response = requests.get(f"{API_BASE}/user/profile", headers=headers, timeout=5)
            print(f"✅ API accessible - Status: {health_response.status_code}")
        except Exception as e:
            print(f"⚠️ API health check failed: {str(e)}")
        
        # Step 3: Test AI Endpoint with Detailed Timing
        print("\n🧠 Step 3: AI Response Test with Detailed Timing")
        
        test_message = "What is 2 + 2?"
        request_data = {
            "message": test_message,
            "session_id": str(uuid.uuid4()),
            "subject": "Mathematics"
        }
        
        print(f"📝 Request: {test_message}")
        print(f"📊 Payload size: {len(json.dumps(request_data))} bytes")
        
        # Track different phases
        start_time = time.time()
        
        try:
            print("⏳ Starting AI request...")
            response = requests.post(
                f"{API_BASE}/ai/dual-response",
                json=request_data,
                headers=headers,
                timeout=45,  # 45 second timeout
                stream=True  # Enable streaming to see if data comes back
            )
            
            request_time = time.time() - start_time
            print(f"📡 Request completed in {request_time:.2f}s")
            
            if response.status_code == 200:
                print("✅ HTTP 200 OK")
                
                # Parse response
                try:
                    data = response.json()
                    total_time = time.time() - start_time
                    print(f"⚡ Total response time: {total_time:.2f}s")
                    
                    # Analyze response structure
                    print(f"\n📊 Response Analysis:")
                    print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    if 'dual_response' in data:
                        dual = data['dual_response']
                        print(f"   Dual response keys: {list(dual.keys())}")
                        
                        if 'primary' in dual:
                            primary = dual['primary']
                            primary_text = primary.get('response', '')
                            print(f"   Primary response length: {len(primary_text)} chars")
                            print(f"   Primary preview: {primary_text[:100]}..." if primary_text else "   Primary: EMPTY!")
                        
                        if 'secondary' in dual:
                            secondary = dual['secondary']
                            secondary_text = secondary.get('response', '')
                            print(f"   Secondary response length: {len(secondary_text)} chars")
                            print(f"   Secondary preview: {secondary_text[:100]}..." if secondary_text else "   Secondary: EMPTY!")
                    
                    # Check for blank responses
                    has_content = False
                    if 'dual_response' in data:
                        primary_resp = data['dual_response'].get('primary', {}).get('response', '')
                        secondary_resp = data['dual_response'].get('secondary', {}).get('response', '')
                        has_content = len(primary_resp) > 20 and len(secondary_resp) > 20
                    
                    result = "✅ SUCCESS" if has_content else "❌ BLANK RESPONSES"
                    print(f"\n🎯 Result: {result}")
                    return has_content
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing failed: {str(e)}")
                    print(f"Raw response: {response.text[:200]}...")
                    return False
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                return False
                
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            print(f"⏰ TIMEOUT after {elapsed:.2f}s")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = debug_ai_response()
    print(f"\n{'🎉 DEBUG COMPLETE - SYSTEM WORKING' if success else '❌ DEBUG COMPLETE - ISSUES FOUND'}")