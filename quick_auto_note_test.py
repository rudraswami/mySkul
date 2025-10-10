#!/usr/bin/env python3
"""
Quick test to verify Auto-Note endpoint issues
"""

import requests
import json

# Test credentials
base_url = "https://ai-education-app.preview.emergentagent.com/api"
test_email = "test@dhruvai.com"
test_password = "password123"

def authenticate():
    """Get auth token"""
    login_data = {"email": test_email, "password": test_password}
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()['token']
    return None

def test_auto_note_endpoints():
    """Test Auto-Note endpoints with correct parameters"""
    token = authenticate()
    if not token:
        print("❌ Authentication failed")
        return
    
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. Start session
    print("1. Testing start session...")
    session_data = {"title": "Test Physics Class", "subject": "Physics"}
    response = requests.post(f"{base_url}/auto-notes/start-session", json=session_data, headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        session_id = response.json()['session_id']
        print(f"   ✅ Session created: {session_id}")
        
        # 2. Process audio
        print("2. Testing process audio...")
        audio_data = {
            "session_id": session_id,
            "transcription": "Test transcription about physics concepts",
            "timestamp": 0.0,
            "sequence_number": 1,
            "confidence": 0.95
        }
        response = requests.post(f"{base_url}/auto-notes/process-audio", json=audio_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Audio processed")
        
        # 3. Test end session - try different approaches
        print("3. Testing end session...")
        
        # Try as JSON body
        print("   3a. Trying with JSON body...")
        end_data = {"session_id": session_id}
        response = requests.post(f"{base_url}/auto-notes/end-session", json=end_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
        
        # Try as query parameter
        print("   3b. Trying with query parameter...")
        response = requests.post(f"{base_url}/auto-notes/end-session?session_id={session_id}", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
        
        # 4. Test list sessions
        print("4. Testing list sessions...")
        response = requests.get(f"{base_url}/auto-notes/sessions", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
        else:
            print("   ✅ Sessions listed")
    
    else:
        print(f"   ❌ Failed to start session: {response.text}")

if __name__ == "__main__":
    test_auto_note_endpoints()