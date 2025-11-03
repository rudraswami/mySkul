#!/usr/bin/env python3
"""
Test JWT Token with Authenticated Endpoints
"""

import requests
import json

# Use the token from the previous test
jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjYyMjkxZmUtMDQyZS00ZTE3LWIyYjAtNTY3M2IzMTM3OTA4IiwiZW1haWwiOiJ0ZXN0c3R1ZGVudF85NmIxeXl3dUB0ZXN0LmNvbSIsImV4cCI6MTc2Mjc3MzMxM30.MyHXdZfXj32qViDtXQIJO8fotlSnBog3a0tdzVycMO0"

base_url = "https://eduai-platform-28.preview.emergentagent.com/api"

print("Testing JWT Token with Authenticated Endpoints")
print("=" * 80)

# Test 1: Subscription Info
print("\n1️⃣ Testing /api/subscription/info")
response = requests.get(
    f"{base_url}/subscription/info",
    headers={"Authorization": f"Bearer {jwt_token}"},
    timeout=10
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ JWT token works with subscription endpoint!")
    print(f"Response: {json.dumps(response.json(), indent=2)[:200]}...")
else:
    print(f"❌ Failed: {response.text}")

# Test 2: User Profile
print("\n2️⃣ Testing /api/user/profile")
response = requests.get(
    f"{base_url}/user/profile",
    headers={"Authorization": f"Bearer {jwt_token}"},
    timeout=10
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ JWT token works with user profile endpoint!")
    print(f"Response: {json.dumps(response.json(), indent=2)[:200]}...")
else:
    print(f"❌ Failed: {response.text}")

# Test 3: Check Access
print("\n3️⃣ Testing /api/subscription/check-access")
response = requests.post(
    f"{base_url}/subscription/check-access",
    headers={"Authorization": f"Bearer {jwt_token}"},
    json={"feature": "ai_mentor"},
    timeout=10
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ JWT token works with check-access endpoint!")
    print(f"Response: {json.dumps(response.json(), indent=2)[:200]}...")
else:
    print(f"❌ Failed: {response.text}")

print("\n" + "=" * 80)
print("JWT Token Validation Complete")
