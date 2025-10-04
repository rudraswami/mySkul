#!/usr/bin/env python3
"""
Debug the sessions endpoint issue
"""

import requests
import json

def test_sessions_endpoint():
    # Authenticate
    login_url = 'https://dhruv-ai.preview.emergentagent.com/api/auth/login'
    login_data = {'email': 'test@dhruvai.com', 'password': 'password123'}
    response = requests.post(login_url, json=login_data)
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    token = response.json()['token']
    user_id = response.json()['user']['user_id']
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f"Authenticated as user: {user_id}")
    
    # Create a session first
    session_data = {'title': 'Debug Session', 'subject': 'Physics'}
    create_response = requests.post(
        'https://dhruv-ai.preview.emergentagent.com/api/auto-notes/start-session',
        json=session_data,
        headers=headers
    )
    
    if create_response.status_code == 200:
        session_id = create_response.json()['session_id']
        print(f"Created session: {session_id}")
    else:
        print(f"Session creation failed: {create_response.status_code}")
        return
    
    # Test individual session retrieval (this works)
    individual_response = requests.get(
        f'https://dhruv-ai.preview.emergentagent.com/api/auto-notes/{session_id}',
        headers=headers
    )
    
    print(f"Individual session retrieval: {individual_response.status_code}")
    if individual_response.status_code == 200:
        print("Individual session data keys:", list(individual_response.json().keys()))
    
    # Test sessions list (this fails)
    sessions_response = requests.get(
        'https://dhruv-ai.preview.emergentagent.com/api/auto-notes/sessions',
        headers=headers
    )
    
    print(f"Sessions list retrieval: {sessions_response.status_code}")
    print(f"Sessions response: {sessions_response.text}")
    
    # Test analytics endpoint (also fails)
    analytics_response = requests.get(
        'https://dhruv-ai.preview.emergentagent.com/api/auto-notes/analytics',
        headers=headers
    )
    
    print(f"Analytics retrieval: {analytics_response.status_code}")
    print(f"Analytics response: {analytics_response.text}")
    
    # Test class series endpoint (also fails)
    class_series_response = requests.get(
        'https://dhruv-ai.preview.emergentagent.com/api/auto-notes/class-series',
        headers=headers
    )
    
    print(f"Class series retrieval: {class_series_response.status_code}")
    print(f"Class series response: {class_series_response.text}")

if __name__ == "__main__":
    test_sessions_endpoint()