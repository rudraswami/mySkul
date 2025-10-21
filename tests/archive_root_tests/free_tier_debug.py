#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class FreeTierDebugger:
    def __init__(self, base_url="https://dhruv-ai-platform.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.test_user_email = "test@dhruvai.com"
        self.test_user_password = "password123"

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
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)

            print(f"   Status Code: {response.status_code}")
            
            # Store last response status for subscription error checking
            self.last_response_status = response.status_code
            
            success = response.status_code == expected_status
            if success:
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:500]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    # Store error details for subscription error analysis
                    self.last_error_data = error_data
                except:
                    print(f"   Error: {response.text}")
                    self.last_error_data = {"error": response.text}
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.last_response_status = 0
            self.last_error_data = {"error": str(e)}
            return False, {}

    def authenticate(self):
        """Authenticate with test user credentials"""
        print(f"\n🔐 Authenticating with {self.test_user_email}...")
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        success, response = self.run_test(
            "User Authentication",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            if 'user' in response:
                self.user_id = response['user'].get('user_id')
            print(f"   ✅ Authentication successful - Token: {self.token[:20]}...")
            return True
        else:
            print("   ❌ Authentication failed")
            return False

    def debug_free_tier_mock_test_access(self):
        """DEBUG FREE TIER MOCK TEST ACCESS ISSUE - REVIEW REQUEST FOCUS"""
        print("\n🚨 DEBUGGING FREE TIER MOCK TEST ACCESS ISSUE")
        print("   Issue: User gets 'Free Tier Limit' popup despite showing 0/2 usage with 2 tests remaining")
        print(f"   User: {self.test_user_email}/{self.test_user_password}")
        print("   Focus: check_feature_access function and get_current_usage logic for mock_tests_monthly")
        
        if not self.authenticate():
            return False
        
        # Step 1: Check Subscription Data
        print("\n📋 STEP 1: Check Subscription Data")
        
        # GET /api/subscription/current
        print("   Testing GET /api/subscription/current...")
        success_current, current_response = self.run_test(
            "Subscription Current Status",
            "GET",
            "subscription/current",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success_current:
            plan = current_response.get('plan', 'unknown')
            status = current_response.get('status', 'unknown')
            period_end = current_response.get('period_end', 'unknown')
            print(f"   ✅ Subscription: plan={plan}, status={status}")
            print(f"   ✅ Period end: {period_end}")
            
            if plan != 'free' or status != 'active':
                print(f"   🚨 ISSUE FOUND: Expected free/active, got {plan}/{status}")
        else:
            print("   ❌ Failed to get subscription current status")
            return False
        
        # GET /api/subscription/usage
        print("\n   Testing GET /api/subscription/usage...")
        success_usage, usage_response = self.run_test(
            "Subscription Usage Status",
            "GET",
            "subscription/usage",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success_usage:
            usage_details = usage_response.get('usage_details', {})
            mock_tests_usage = usage_details.get('mock_tests_monthly', {})
            
            used = mock_tests_usage.get('used', 0)
            limit = mock_tests_usage.get('limit', 0)
            remaining = mock_tests_usage.get('remaining', 0)
            
            print(f"   ✅ Mock Tests Usage: {used}/{limit} used, {remaining} remaining")
            
            if used == 0 and limit == 2 and remaining == 2:
                print("   ✅ Usage shows 0/2 as expected")
            else:
                print(f"   🚨 USAGE ISSUE: Expected 0/2 with 2 remaining, got {used}/{limit} with {remaining} remaining")
        else:
            print("   ❌ Failed to get subscription usage status")
            return False
        
        # Step 2: Debug Mock Test Generation
        print("\n📋 STEP 2: Debug Mock Test Generation")
        print("   Testing POST /api/mock-tests/generate with minimal data...")
        
        minimal_test_data = {
            "exam_type": "JEE",
            "subjects": ["Mathematics"],
            "num_questions": 5,
            "difficulty_level": 3
        }
        
        print(f"   Request data: {minimal_test_data}")
        
        success_generate, generate_response = self.run_test(
            "Mock Test Generation - Free Tier Debug",
            "POST",
            "mock-tests/generate",
            200,  # Expecting success, not 402
            data=minimal_test_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success_generate:
            print("   ✅ Mock test generation succeeded")
            test_id = generate_response.get('test_id', 'N/A')
            print(f"   ✅ Generated test ID: {test_id}")
            
            # Check if usage updated
            print("\n   Checking usage after generation...")
            success_usage_after, usage_after_response = self.run_test(
                "Usage After Generation",
                "GET",
                "subscription/usage",
                200,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success_usage_after:
                usage_details_after = usage_after_response.get('usage_details', {})
                mock_tests_usage_after = usage_details_after.get('mock_tests_monthly', {})
                
                used_after = mock_tests_usage_after.get('used', 0)
                remaining_after = mock_tests_usage_after.get('remaining', 0)
                
                print(f"   Usage after generation: {used_after}/2 used, {remaining_after} remaining")
                
                if used_after == 1 and remaining_after == 1:
                    print("   ✅ Usage tracking working correctly")
                else:
                    print(f"   🚨 USAGE TRACKING ISSUE: Expected 1/2 used, got {used_after}/2")
            
            return True
        else:
            # Analyze the specific error
            error_status = getattr(self, 'last_response_status', 0)
            error_data = getattr(self, 'last_error_data', {})
            
            print(f"   ❌ Mock test generation FAILED")
            print(f"   🔍 ERROR ANALYSIS:")
            print(f"      Status Code: {error_status}")
            print(f"      Error Data: {error_data}")
            
            if error_status == 402:
                print(f"      🚨 402 PAYMENT REQUIRED - This is the 'Free Tier Limit' issue!")
                print(f"      🔍 Root cause: Backend validation incorrectly blocking free tier user")
                print(f"      🔍 Check: check_feature_access function logic")
                print(f"      🔍 Check: subscription validation in mock test generation")
            elif error_status == 500:
                print(f"      🚨 500 INTERNAL SERVER ERROR - Backend processing issue")
                print(f"      🔍 Check: Database connection, datetime comparison issues")
            elif error_status == 422:
                print(f"      🚨 422 VALIDATION ERROR - Request parameter issues")
                print(f"      🔍 Check: API parameter validation logic")
            
            return False

    def check_backend_logs(self):
        """Check backend logs for subscription validation errors"""
        print("\n📋 STEP 3: Backend Log Analysis")
        print("   Checking server logs for subscription validation errors...")
        
        # This would require access to server logs
        # For now, we'll simulate by checking if we can identify patterns
        print("   🔍 Looking for error messages related to 'subscription_expired' or access checking")
        print("   🔍 Focus on check_feature_access function and get_current_usage logic")
        
        # We can't directly access logs, but we can infer from API responses
        if hasattr(self, 'last_error_data'):
            error_data = self.last_error_data
            if 'subscription' in str(error_data).lower():
                print(f"   🚨 SUBSCRIPTION ERROR DETECTED: {error_data}")
            if 'expired' in str(error_data).lower():
                print(f"   🚨 EXPIRATION ERROR DETECTED: {error_data}")
            if 'limit' in str(error_data).lower():
                print(f"   🚨 LIMIT ERROR DETECTED: {error_data}")

    def run_comprehensive_debug(self):
        """Run comprehensive debug of free tier mock test access issue"""
        print("🚀 Starting Free Tier Mock Test Access Debug...")
        print("================================================================================")
        
        try:
            success = self.debug_free_tier_mock_test_access()
            self.check_backend_logs()
            
            print("\n================================================================================")
            print("🎯 FREE TIER DEBUG SUMMARY:")
            
            if success:
                print("   ✅ Free tier mock test access is working correctly")
                print("   ✅ No 'Free Tier Limit' popup issue detected")
            else:
                print("   ❌ Free tier mock test access issue CONFIRMED")
                print("   🚨 User will see 'Free Tier Limit' popup despite having remaining tests")
                print("   🔧 RECOMMENDATION: Check backend subscription validation logic")
                print("   🔧 FOCUS: check_feature_access function and get_current_usage logic")
            
            return success
            
        except Exception as e:
            print(f"❌ Debug failed with error: {str(e)}")
            return False

if __name__ == "__main__":
    debugger = FreeTierDebugger()
    success = debugger.run_comprehensive_debug()
    sys.exit(0 if success else 1)