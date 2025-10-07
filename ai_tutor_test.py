import requests
import sys
import json
from datetime import datetime
import time

class AITutorSubscriptionTester:
    def __init__(self, base_url="https://quota-handler.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        if self.token and 'Authorization' not in test_headers:
            test_headers['Authorization'] = f'Bearer {self.token}'

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    return False, error_data
                except:
                    print(f"   Error: {response.text}")
                    return False, {"error": response.text}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {"error": str(e)}

    def test_user_login(self):
        """Test user login with test@dhruvai.com/password123"""
        login_data = {
            "email": "test@dhruvai.com",
            "password": "password123"
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            if 'user' in response:
                self.user_id = response['user'].get('user_id')
            print(f"   Login token: {self.token[:20]}...")
            return True
        return False

    def test_ai_tutor_subscription_limit_debug(self):
        """Test AI Tutor subscription limit issue - CRITICAL REVIEW REQUEST FOCUS"""
        if not self.token:
            print("❌ No token available for AI Tutor subscription limit test")
            return False
        
        print("\n🎯 AI TUTOR SUBSCRIPTION LIMIT DEBUG - CRITICAL REVIEW REQUEST FOCUS")
        print("   Testing: AI Tutor subscription flow with test@dhruvai.com/password123")
        print("   Issue: User shows '0 left to use' and gets error messages instead of subscription modal")
        print("   Focus: /api/subscription/check-access endpoint for ai_tutor_daily feature")
        print("   Expected: 402 errors with upsell_info when limits reached")
        
        # Step 1: Check current subscription status
        print("\n📋 Step 1: Check Current Subscription Status")
        success, response = self.run_test(
            "Current Subscription Status",
            "GET",
            "subscription/current",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            subscription = response.get('subscription', {})
            plan = subscription.get('plan_name', 'unknown')
            status = subscription.get('status', 'unknown')
            print(f"   ✅ Subscription Status: Plan={plan}, Status={status}")
        else:
            print("   ❌ Failed to get subscription status")
            return False
        
        # Step 2: Check current usage for ai_tutor_daily
        print("\n📋 Step 2: Check Current Usage for AI Tutor Daily")
        success, response = self.run_test(
            "Current Usage Status",
            "GET",
            "subscription/usage",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            usage_details = response.get('usage_details', {})
            ai_tutor_usage = usage_details.get('ai_tutor_daily', {})
            used = ai_tutor_usage.get('used', 0)
            limit = ai_tutor_usage.get('limit', 0)
            remaining = ai_tutor_usage.get('remaining', 0)
            has_access = ai_tutor_usage.get('has_access', True)
            
            print(f"   ✅ AI Tutor Usage: {used}/{limit} used, {remaining} remaining")
            print(f"   ✅ Has Access: {has_access}")
            
            if used >= limit and not has_access:
                print("   🚨 CONFIRMED: User has exhausted AI Tutor quota")
            elif has_access:
                print("   ⚠️  User still has access - may need to exhaust quota first")
        else:
            print("   ❌ Failed to get usage status")
            return False
        
        # Step 3: Test /api/subscription/check-access for ai_tutor_daily
        print("\n📋 Step 3: Test Subscription Check-Access for AI Tutor Daily")
        
        success, response = self.run_test(
            "Check Access - AI Tutor Daily",
            "POST",
            "subscription/check-access?feature_name=ai_tutor_daily",
            200,  # Should return 200 with has_access: false if quota exhausted
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            has_access = response.get('has_access', True)
            reason = response.get('reason', 'unknown')
            current_usage = response.get('current_usage', {})
            upsell_info = response.get('upsell_info', {})
            
            print(f"   ✅ Check Access Response: has_access={has_access}, reason={reason}")
            print(f"   ✅ Current Usage: {current_usage}")
            
            if not has_access and upsell_info:
                print(f"   ✅ EXPECTED BEHAVIOR: has_access=false with upsell_info present")
                print(f"   ✅ Upsell Info: {upsell_info}")
                print("   ✅ This should trigger subscription modal, not error messages")
            elif has_access:
                print("   ⚠️  User still has access - quota not exhausted yet")
            else:
                print("   ❌ ISSUE: has_access=false but no upsell_info provided")
        else:
            print("   ❌ Check access endpoint failed")
            return False
        
        # Step 4: Test AI Tutor message sending when quota exhausted
        print("\n📋 Step 4: Test AI Tutor Message Sending (Should Return 402 if Quota Exhausted)")
        
        # First create a chat session
        session_success, session_response = self.run_test(
            "Create Chat Session",
            "POST",
            "chat/sessions",
            200,
            data={"title": "Test AI Tutor Session", "subject": "Mathematics"},
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if not session_success:
            print("   ❌ Failed to create chat session")
            return False
            
        session_id = session_response.get('session_id')
        print(f"   ✅ Created session: {session_id}")
        
        # Now test AI dual response (the actual AI Tutor endpoint)
        ai_message_data = {
            "session_id": session_id,
            "message": "Explain quadratic equations",
            "subject": "Mathematics"
        }
        
        # This should return 402 if quota is exhausted, or 200 if still has access
        expected_status = 402 if not has_access else 200
        
        success, response = self.run_test(
            "AI Tutor Dual Response - Quota Check",
            "POST",
            "ai/dual-response",
            expected_status,
            data=ai_message_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if expected_status == 402 and success:
            print("   ✅ EXPECTED: AI Tutor correctly returned 402 when quota exhausted")
            
            # Check for proper 402 error structure with upsell_info
            error_message = response.get('message', '')
            upsell_info = response.get('upsell_info', {})
            
            if upsell_info:
                print(f"   ✅ 402 Error includes upsell_info: {upsell_info}")
                print("   ✅ This should trigger subscription modal in frontend")
            else:
                print("   ❌ ISSUE: 402 error missing upsell_info")
                print("   ❌ This explains why user gets generic error instead of subscription modal")
                
        elif expected_status == 200 and success:
            print("   ✅ AI Tutor working normally - user still has quota")
            
        else:
            print(f"   ❌ Unexpected response - Expected {expected_status}, got different result")
            print("   ❌ This could explain the repeated error messages issue")
        
        # Step 5: Summary and Diagnosis
        print("\n🎯 AI TUTOR SUBSCRIPTION LIMIT DIAGNOSIS SUMMARY:")
        
        if not has_access and upsell_info:
            print("   ✅ BACKEND WORKING CORRECTLY:")
            print("     - User has exhausted AI Tutor quota")
            print("     - check-access returns has_access: false")
            print("     - Proper upsell_info provided")
            print("     - Should trigger subscription modal")
            print("   🔍 LIKELY FRONTEND ISSUE: Check if frontend properly handles 402 responses")
            
        elif has_access:
            print("   ⚠️  USER STILL HAS QUOTA:")
            print("     - User has not exhausted AI Tutor daily limit")
            print("     - Backend correctly allows access")
            print("     - Issue may be frontend display showing wrong usage")
            print("   🔍 RECOMMENDATION: Check frontend usage display logic")
            
        else:
            print("   ❌ BACKEND ISSUE IDENTIFIED:")
            print("     - Subscription system not returning proper error structure")
            print("     - Missing upsell_info in 402 responses")
            print("     - This causes generic error messages instead of subscription modal")
            print("   🔧 FIX NEEDED: Ensure 402 responses include complete upsell_info")
        
        return True

if __name__ == "__main__":
    # Run focused AI Tutor subscription limit debug test
    tester = AITutorSubscriptionTester()
    
    # Login first
    if not tester.test_user_login():
        print("❌ Login failed - cannot proceed with subscription limit test")
        sys.exit(1)
    
    # Run the specific test for the review request
    print("🎯 RUNNING FOCUSED AI TUTOR SUBSCRIPTION LIMIT DEBUG TEST")
    tester.test_ai_tutor_subscription_limit_debug()