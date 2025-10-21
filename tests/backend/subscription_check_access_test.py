#!/usr/bin/env python3
"""
Subscription Check-Access Endpoint Testing - REVIEW REQUEST FOCUS
Test the subscription check-access endpoint directly to confirm it returns proper 402 responses.
"""

import requests
import json
import sys
import time

class SubscriptionCheckAccessTester:
    def __init__(self, base_url="https://platform-rescue.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.test_user_email = "test@dhruvai.com"
        self.test_user_password = "password123"

    def login(self):
        """Login with test@dhruvai.com/password123 to get token"""
        print("🔐 STEP 1: Login with test@dhruvai.com/password123")
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        url = f"{self.base_url}/auth/login"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, json=login_data, headers=headers, timeout=30)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                if 'token' in response_data:
                    self.token = response_data['token']
                    if 'user' in response_data:
                        self.user_id = response_data['user'].get('user_id')
                    print(f"   ✅ Login successful")
                    print(f"   Token: {self.token[:20]}...")
                    return True
                else:
                    print(f"   ❌ No token in response: {response_data}")
                    return False
            else:
                print(f"   ❌ Login failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Login error: {str(e)}")
            return False

    def test_check_access_endpoint(self):
        """Test the subscription/check-access endpoint with ai_tutor_daily feature"""
        if not self.token:
            print("❌ No token available for check-access test")
            return False
        
        print("\n🎯 STEP 2: Test subscription/check-access endpoint with ai_tutor_daily feature")
        
        # Use query parameter instead of request body
        feature_name = "ai_tutor_daily"
        url = f"{self.base_url}/subscription/check-access?feature_name={feature_name}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        
        try:
            response = requests.post(url, headers=headers, timeout=30)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"   ✅ Check-access endpoint returned 200 OK")
                print(f"   📊 Response Structure:")
                print(json.dumps(response_data, indent=4))
                
                # Analyze the response structure
                has_access = response_data.get('has_access', None)
                remaining_usage = response_data.get('remaining_usage', None)
                limit = response_data.get('limit', None)
                used = response_data.get('used', None)
                
                print(f"\n   🔍 ACCESS ANALYSIS:")
                print(f"      has_access: {has_access}")
                print(f"      remaining_usage: {remaining_usage}")
                print(f"      limit: {limit}")
                print(f"      used: {used}")
                
                return True, response_data
                
            elif response.status_code == 402:
                response_data = response.json()
                print(f"   🎯 Check-access returned 402 Payment Required - EXPECTED BEHAVIOR")
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
                else:
                    print(f"   ❌ upsell_info missing from 402 response")
                
                return True, response_data
                
            else:
                print(f"   ❌ Unexpected status code: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error response: {json.dumps(error_data, indent=4)}")
                except:
                    print(f"   Error text: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"   ❌ Check-access test error: {str(e)}")
            return False, {}

    def verify_response_structure(self, response_data, status_code):
        """Verify the response structure and status code"""
        print(f"\n🔍 STEP 3: Verify response structure and status code")
        
        if status_code == 200:
            # For 200 responses, verify access control structure
            required_fields = ['has_access', 'remaining_usage', 'limit', 'used']
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if not missing_fields:
                print(f"   ✅ All required fields present for 200 response: {required_fields}")
                
                has_access = response_data.get('has_access')
                if has_access is False:
                    print(f"   🎯 User has no access - this should trigger 402 response")
                    print(f"   ⚠️  Check-access returning 200 with has_access=false instead of 402")
                    return False
                else:
                    print(f"   ✅ User has access - 200 response is correct")
                    return True
            else:
                print(f"   ❌ Missing required fields in 200 response: {missing_fields}")
                return False
                
        elif status_code == 402:
            # For 402 responses, verify subscription error structure
            required_fields = ['message', 'upsell_info']
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if not missing_fields:
                print(f"   ✅ All required fields present for 402 response: {required_fields}")
                
                upsell_info = response_data.get('upsell_info', {})
                upsell_required_fields = ['mentor_message', 'professor_message', 'target_plan']
                upsell_missing_fields = [field for field in upsell_required_fields if field not in upsell_info]
                
                if not upsell_missing_fields:
                    print(f"   ✅ All required upsell_info fields present: {upsell_required_fields}")
                    return True
                else:
                    print(f"   ❌ Missing upsell_info fields: {upsell_missing_fields}")
                    return False
            else:
                print(f"   ❌ Missing required fields in 402 response: {missing_fields}")
                return False
        else:
            print(f"   ❌ Unexpected status code: {status_code}")
            return False

    def run_focused_test(self):
        """Run the focused subscription check-access test as per review request"""
        print("🚀 SUBSCRIPTION CHECK-ACCESS ENDPOINT TESTING")
        print("=" * 60)
        print("TESTING STEPS:")
        print("1. Login with test@dhruvai.com/password123 to get token")
        print("2. Test the subscription/check-access endpoint with ai_tutor_daily feature")
        print("3. Verify the response structure and status code")
        print("4. If user has exhausted quota, confirm it returns proper subscription error response")
        print("=" * 60)
        
        # Step 1: Login
        if not self.login():
            print("\n❌ CRITICAL: Login failed - cannot proceed with testing")
            return False
        
        # Step 2: Test check-access endpoint
        success, response_data = self.test_check_access_endpoint()
        if not success:
            print("\n❌ CRITICAL: Check-access endpoint test failed")
            return False
        
        # Step 3: Verify response structure
        # Determine the actual status code from the last response
        # We need to make another call to get the actual status
        print("\n🔍 STEP 4: Final verification - Testing check-access behavior")
        
        feature_name = "ai_tutor_daily"
        url = f"{self.base_url}/subscription/check-access?feature_name={feature_name}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        
        try:
            response = requests.post(url, headers=headers, timeout=30)
            actual_status = response.status_code
            actual_data = response.json() if response.status_code in [200, 402] else {}
            
            print(f"   Final status code: {actual_status}")
            
            if actual_status == 200:
                has_access = actual_data.get('has_access', True)
                if has_access:
                    print(f"   ✅ RESULT: User has access - check-access working correctly")
                    print(f"   ℹ️  Cannot test 402 scenario as user still has quota")
                else:
                    print(f"   ❌ ISSUE: User has no access but getting 200 instead of 402")
                    print(f"   🔧 RECOMMENDATION: Check-access should return 402 when has_access=false")
                    return False
            elif actual_status == 402:
                print(f"   ✅ RESULT: User quota exhausted - check-access correctly returns 402")
                upsell_info = actual_data.get('upsell_info', {})
                if upsell_info:
                    print(f"   ✅ RESULT: upsell_info present - subscription flow working correctly")
                else:
                    print(f"   ❌ ISSUE: upsell_info missing from 402 response")
                    return False
            else:
                print(f"   ❌ ISSUE: Unexpected status code {actual_status}")
                return False
            
            return self.verify_response_structure(actual_data, actual_status)
            
        except Exception as e:
            print(f"   ❌ Final verification error: {str(e)}")
            return False

def main():
    """Main function to run the subscription check-access test"""
    tester = SubscriptionCheckAccessTester()
    
    print("🎯 SUBSCRIPTION CHECK-ACCESS ENDPOINT DIRECT TESTING")
    print("Focus: Confirm proper 402 responses with upsell_info when limits reached")
    print("This will help isolate if the issue is in check-access or in dual-response endpoint")
    print()
    
    success = tester.run_focused_test()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    if success:
        print("✅ SUCCESS: Subscription check-access endpoint is working correctly")
        print("   - Endpoint responds with proper status codes")
        print("   - Response structure is valid")
        print("   - Subscription flow is functional")
    else:
        print("❌ FAILURE: Issues found with subscription check-access endpoint")
        print("   - This explains why dual-response endpoint has issues")
        print("   - Check-access endpoint needs to be fixed first")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)