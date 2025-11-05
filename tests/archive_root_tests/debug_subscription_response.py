#!/usr/bin/env python3
"""
Debug script to understand the exact subscription response structure
"""

import requests
import json
import time

def debug_subscription_response():
    base_url = "https://dhruv-neuro-ai.preview.emergentagent.com/api"
    
    # Create fresh user
    fresh_user_email = f"debug_user_{int(time.time())}@dhruvai.com"
    registration_data = {
        "full_name": "Debug User",
        "email": fresh_user_email,
        "password": "password123",
        "exam_type": "JEE",
        "target_year": 2026
    }
    
    print("Creating fresh user...")
    response = requests.post(f"{base_url}/auth/register", json=registration_data)
    if response.status_code != 200:
        print(f"Failed to create user: {response.status_code}")
        return
    
    token = response.json().get('token')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    print("\n1. Initial check-access call:")
    response = requests.post(f"{base_url}/subscription/check-access", 
                           json={"feature_name": "auto_note_uploads_daily"}, 
                           headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n2. Track usage once:")
    response = requests.post(f"{base_url}/subscription/track-usage", 
                           json={"feature_name": "auto_note_uploads_daily"}, 
                           headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n3. Check access after first usage:")
    response = requests.post(f"{base_url}/subscription/check-access", 
                           json={"feature_name": "auto_note_uploads_daily"}, 
                           headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n4. Track usage again:")
    response = requests.post(f"{base_url}/subscription/track-usage", 
                           json={"feature_name": "auto_note_uploads_daily"}, 
                           headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n5. Check access after second usage:")
    response = requests.post(f"{base_url}/subscription/check-access", 
                           json={"feature_name": "auto_note_uploads_daily"}, 
                           headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    debug_subscription_response()