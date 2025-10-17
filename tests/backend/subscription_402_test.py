#!/usr/bin/env python3
"""
Test subscription check-access endpoint 402 responses with a free tier user
"""

import requests
import json
import sys
import time
import uuid

class Subscription402Tester:
    def __init__(self, base_url="https://dhruvai-upgrade.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        # Create a unique email for fresh free tier user
        self.test_user_email = f"free_tier_test_{int(time.time())}@dhruvai.com"
        self.test_user_password = "password123"

    def create_free_tier_user(self):
        """Create a new free tier user for testing"""
        print(f"🆕 STEP 1: Create new free tier user: {self.test_user_email}")
        
        registration_data = {
            "full_name": "Free Tier Test User",
            "email": self.test_user_email,
            "password": self.test_user_password,
            "exam_type": "JEE",
            "grade": "Class 12",
            "target_year": 2026
        }
        
        url = f"{self.base_url}/auth/register"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, json=registration_data, headers=headers, timeout=30)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                if 'token' in response_data:
                    self.token = response_data['token']
                    if 'user' in response_data:
                        self.user_id = response_data['user'].get('user_id')
                    print(f"   ✅ Free tier user created successfully")
                    print(f"   Token: {self.token[:20]}...")
                    return True
                else:
                    print(f"   ❌ No token in response: {response_data}")
                    return False
            else:
                print(f"   ❌ Registration failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Registration error: {str(e)}")
            return False

    def verify_free_tier_status(self):
        """Verify the user is on free tier"""
        print(f"\n🔍 STEP 2: Verify free tier status")
        
        url = f"{self.base_url}/subscription/info"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                plan = data.get('subscription_tier', 'unknown')
                print(f"   📋 Plan: {plan}")
                
                if plan.upper() == 'FREE':
                    print(f"   ✅ User is on FREE tier - perfect for 402 testing")
                    
                    # Show the limits
                    plan_info = data.get('plan_info', {})
                    features = plan_info.get('features', {})
                    ai_limit = features.get('ai_tutor_daily', 'unknown')
                    print(f"   📊 AI Tutor Daily Limit: {ai_limit}")
                    return True
                else:
                    print(f"   ❌ User is on {plan} tier, not FREE")
                    return False
            else:
                print(f"   ❌ Failed to get subscription info: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return False

    def exhaust_ai_tutor_quota(self):
        """Exhaust the AI tutor quota to trigger 402 responses"""
        print(f"\n⚡ STEP 3: Exhaust AI tutor quota (10 messages for free tier)")
        
        # Free tier has 10 AI tutor messages per day
        for i in range(11):  # Try 11 to exceed the limit
            print(f"   Sending AI message {i+1}/11...")
            
            url = f"{self.base_url}/ai/dual-response"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.token}'
            }
            
            message_data = {
                "message": f"Test message {i+1}: What is 2+2?",
                "subject": "Mathematics",
                "session_id": str(uuid.uuid4())
            }
            
            try:
                response = requests.post(url, json=message_data, headers=headers, timeout=30)
                print(f"      Status: {response.status_code}")
                
                if response.status_code == 402:
                    print(f"   🎯 Got 402 Payment Required on message {i+1}")
                    print(f"   ✅ Successfully exhausted quota!")
                    return True
                elif response.status_code == 200:
                    print(f"      ✅ Message {i+1} successful")
                else:
                    print(f"      ⚠️  Unexpected status {response.status_code}: {response.text[:100]}")
                
                time.sleep(1)  # Small delay between requests
                
            except Exception as e:
                print(f"      ❌ Error on message {i+1}: {str(e)}")
        
        print(f"   ⚠️  Did not hit 402 limit after 11 messages")
        return False

    def test_check_access_402(self):
        """Test check-access endpoint expecting 402 response"""
        print(f"\n🎯 STEP 4: Test check-access endpoint expecting 402 response")
        
        feature_name = "ai_tutor_daily"
        url = f"{self.base_url}/subscription/check-access?feature_name={feature_name}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        
        try:
            response = requests.post(url, headers=headers, timeout=30)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 402:
                response_data = response.json()
                print(f"   🎯 ✅ Check-access correctly returns 402 Payment Required!")
                print(f"   📊 402 Response Structure:")
                print(json.dumps(response_data, indent=4))
                
                # Verify upsell_info structure
                upsell_info = response_data.get('upsell_info', {})
                if upsell_info:
                    print(f"\n   ✅ upsell_info present in 402 response")
                    print(f"      mentor_message: {upsell_info.get('mentor_message', 'N/A')[:100]}...")
                    print(f"      professor_message: {upsell_info.get('professor_message', 'N/A')[:100]}...")
                    print(f"      target_plan: {upsell_info.get('target_plan', 'N/A')}")
                    print(f"      current_plan: {upsell_info.get('current_plan', 'N/A')}")
                    print(f"      upgrade_url: {upsell_info.get('upgrade_url', 'N/A')}")
                    return True
                else:
                    print(f"   ❌ upsell_info missing from 402 response")
                    return False
                    
            elif response.status_code == 200:
                response_data = response.json()
                print(f"   ⚠️  Check-access returned 200 OK instead of 402")
                print(f"   📊 Response:")
                print(json.dumps(response_data, indent=4))
                
                has_access = response_data.get('has_access', True)
                if has_access:
                    print(f"   ℹ️  User still has access - quota not exhausted yet")
                else:
                    print(f"   ❌ ISSUE: has_access=false but status is 200, should be 402")
                return False
                
            else:
                print(f"   ❌ Unexpected status code: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=4)}")
                except:
                    print(f"   Error text: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return False

    def run_402_test(self):
        """Run the complete 402 test scenario"""
        print("🚀 SUBSCRIPTION CHECK-ACCESS 402 TESTING")
        print("=" * 60)
        print("TESTING STRATEGY:")
        print("1. Create new free tier user (10 AI messages/day limit)")
        print("2. Verify free tier status and limits")
        print("3. Exhaust AI tutor quota by sending 11 messages")
        print("4. Test check-access endpoint expecting 402 response")
        print("=" * 60)
        
        # Step 1: Create free tier user
        if not self.create_free_tier_user():
            print("\n❌ CRITICAL: Failed to create free tier user")
            return False
        
        # Step 2: Verify free tier status
        if not self.verify_free_tier_status():
            print("\n❌ CRITICAL: User is not on free tier")
            return False
        
        # Step 3: Exhaust quota
        quota_exhausted = self.exhaust_ai_tutor_quota()
        
        # Step 4: Test check-access endpoint
        success = self.test_check_access_402()
        
        return success

def main():
    """Main function"""
    tester = Subscription402Tester()
    
    print("🎯 SUBSCRIPTION CHECK-ACCESS 402 RESPONSE TESTING")
    print("Focus: Test with fresh free tier user to trigger 402 responses")
    print("This will confirm if check-access endpoint returns proper 402 with upsell_info")
    print()
    
    success = tester.run_402_test()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    if success:
        print("✅ SUCCESS: Check-access endpoint correctly returns 402 with upsell_info")
        print("   - 402 Payment Required status code confirmed")
        print("   - upsell_info structure is present and valid")
        print("   - Subscription flow is working correctly")
        print("   - Issue is NOT in check-access endpoint")
    else:
        print("❌ FAILURE: Issues found with check-access 402 responses")
        print("   - Check-access endpoint may not return proper 402 responses")
        print("   - This could explain dual-response endpoint issues")
        print("   - Further investigation needed")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)