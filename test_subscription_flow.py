#!/usr/bin/env python3
"""Test subscription modal flow for AI Tutor and Auto-Note Generator"""
import requests
import json

BACKEND_URL = "https://dhruvai-upgrade.preview.emergentagent.com"

print("=" * 60)
print("Testing Subscription Modal Flow")
print("=" * 60)

# Test 1: Check AI Tutor access endpoint
print("\n1. Testing /api/subscription/check-ai-tutor-access")
print("-" * 60)

try:
    response = requests.get(
        f"{BACKEND_URL}/api/subscription/check-ai-tutor-access",
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 401:
        print("❌ Authentication required (expected for logged-out user)")
        print("Response:", response.json())
    elif response.status_code == 200:
        data = response.json()
        print("✅ Success! Response structure:")
        print(json.dumps(data, indent=2))
        
        # Validate response structure
        required_fields = ['allowed', 'remaining', 'total', 'current_usage', 'usage_percent', 'current_tier']
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            print(f"\n⚠️  Missing fields: {missing_fields}")
        else:
            print("\n✅ All required fields present")
            
        if not data.get('allowed'):
            print("\n🚫 Limit reached!")
            if 'upgrade_hint' in data:
                print("Upgrade hint present:", 'upgrade_hint' in data)
                print("Upgrade hint structure:", json.dumps(data.get('upgrade_hint'), indent=2))
            else:
                print("❌ upgrade_hint is MISSING!")
    else:
        print(f"❌ Unexpected status: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Check feature access endpoint (used by Auto-Note Generator)
print("\n\n2. Testing /api/subscription/check-access (auto_note_uploads_daily)")
print("-" * 60)

try:
    response = requests.post(
        f"{BACKEND_URL}/api/subscription/check-access",
        json={"feature_name": "auto_note_uploads_daily"},
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 401:
        print("❌ Authentication required (expected for logged-out user)")
        print("Response:", response.json())
    elif response.status_code == 200:
        data = response.json()
        print("✅ Success! Response structure:")
        print(json.dumps(data, indent=2))
        
        # Validate response structure
        required_fields = ['has_access', 'used', 'limit', 'remaining']
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            print(f"\n⚠️  Missing fields: {missing_fields}")
        else:
            print("\n✅ All required fields present")
            
        if not data.get('has_access'):
            print("\n🚫 Limit reached!")
            if 'upsell_info' in data:
                print("Upsell info present:", 'upsell_info' in data)
                print("Upsell info structure:", json.dumps(data.get('upsell_info'), indent=2))
            else:
                print("❌ upsell_info is MISSING!")
    elif response.status_code == 402:
        print("🚫 Payment Required (limit reached)")
        print("Response:", json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Unexpected status: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
