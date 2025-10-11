#!/usr/bin/env python3
"""
Check subscription status and usage for test@dhruvai.com
"""

import requests
import json
import sys

def login():
    """Login with test@dhruvai.com/password123"""
    base_url = "https://tutor-upgrade.preview.emergentagent.com/api"
    login_data = {
        "email": "test@dhruvai.com",
        "password": "password123"
    }
    
    url = f"{base_url}/auth/login"
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, json=login_data, headers=headers, timeout=30)
        if response.status_code == 200:
            response_data = response.json()
            if 'token' in response_data:
                return response_data['token'], base_url
    except Exception as e:
        print(f"Login error: {str(e)}")
    
    return None, None

def check_subscription_info(token, base_url):
    """Check current subscription information"""
    print("🔍 Checking subscription information...")
    
    url = f"{base_url}/subscription/info"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Subscription Info:")
            print(json.dumps(data, indent=4))
            return data
        else:
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"   Error: {str(e)}")
        return None

def check_usage_stats(token, base_url):
    """Check current usage statistics"""
    print("\n🔍 Checking usage statistics...")
    
    url = f"{base_url}/subscription/usage"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Usage Statistics:")
            print(json.dumps(data, indent=4))
            return data
        else:
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"   Error: {str(e)}")
        return None

def check_ai_tutor_access(token, base_url):
    """Check AI tutor access specifically"""
    print("\n🔍 Checking AI tutor access...")
    
    url = f"{base_url}/subscription/check-access?feature_name=ai_tutor_daily"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.post(url, headers=headers, timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 AI Tutor Access:")
            print(json.dumps(data, indent=4))
            return data
        elif response.status_code == 402:
            data = response.json()
            print(f"   🎯 402 Payment Required:")
            print(json.dumps(data, indent=4))
            return data
        else:
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"   Error: {str(e)}")
        return None

def main():
    print("🔍 SUBSCRIPTION STATUS CHECK FOR test@dhruvai.com")
    print("=" * 60)
    
    token, base_url = login()
    if not token:
        print("❌ Login failed")
        return False
    
    print("✅ Login successful")
    
    # Check subscription info
    sub_info = check_subscription_info(token, base_url)
    
    # Check usage stats
    usage_stats = check_usage_stats(token, base_url)
    
    # Check AI tutor access
    ai_access = check_ai_tutor_access(token, base_url)
    
    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    
    if sub_info:
        plan = sub_info.get('subscription_tier', 'unknown')
        print(f"📋 Current Plan: {plan}")
        
        if plan.lower() in ['premium', 'pro']:
            print(f"   ℹ️  User has {plan} plan - unlimited AI tutor access")
            print(f"   ℹ️  Cannot test 402 scenario with this user")
        elif plan.lower() == 'free':
            print(f"   🎯 User has free plan - should have limited access")
            if ai_access and ai_access.get('has_access'):
                print(f"   ⚠️  User still has access - quota not exhausted")
            else:
                print(f"   ✅ User quota exhausted - should get 402 responses")
    
    if usage_stats:
        daily_usage = usage_stats.get('daily_usage', {})
        ai_usage = daily_usage.get('ai_tutor_daily', {})
        if ai_usage:
            used = ai_usage.get('used', 0)
            limit = ai_usage.get('limit', 0)
            print(f"📊 AI Tutor Usage: {used}/{limit}")
            
            if used >= limit and limit > 0:
                print(f"   🎯 User has exhausted quota - perfect for 402 testing")
            else:
                print(f"   ℹ️  User still has quota remaining")
    
    return True

if __name__ == "__main__":
    main()