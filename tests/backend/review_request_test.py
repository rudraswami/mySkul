#!/usr/bin/env python3
"""
Review Request Focused Testing
Testing recent fixes to MockTests component and subscription system
"""

import requests
import sys
import json
from datetime import datetime
import time

class ReviewRequestTester:
    def __init__(self, base_url="https://razorpay-live.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        if self.token and 'Authorization' not in test_headers:
            test_headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
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
            
            success = response.status_code == expected_status or (isinstance(expected_status, list) and response.status_code in expected_status)
            if success:
                self.tests_passed += 1
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

    def test_subscription_modal_fixes(self):
        """Test subscription modal and checkFeatureAccess 402 responses"""
        print("\n🚨 CRITICAL: SUBSCRIPTION MODAL FIXES TESTING")
        print("   Issue: checkFeatureAccess should return 402 status codes when limits exceeded")
        print("   Focus: Backend API responses for subscription limits")
        
        if not self.token:
            print("❌ No token available, attempting login...")
            if not self.test_user_login():
                print("❌ Failed to login, cannot proceed with testing")
                return False
        
        # Create fresh free tier user to test limits
        fresh_user_email = f"subscription_test_{int(time.time())}@dhruvai.com"
        registration_data = {
            "full_name": "Subscription Test User",
            "email": fresh_user_email,
            "password": "password123",
            "exam_type": "JEE",
            "grade": "Class 12",
            "target_year": 2026
        }
        
        print(f"\n📝 Step 1: Creating Fresh User for Testing")
        print(f"   Email: {fresh_user_email}")
        
        success, response = self.run_test(
            "Create Fresh User for Subscription Testing",
            "POST",
            "auth/register",
            200,
            data=registration_data
        )
        
        if not success or 'token' not in response:
            print("❌ Failed to create fresh user")
            return False
        
        fresh_token = response['token']
        print(f"   ✅ Fresh user created")
        
        # Test initial checkFeatureAccess (should have access)
        print(f"\n📊 Step 2: Test Initial checkFeatureAccess")
        check_access_data = {
            "feature_name": "mock_tests_weekly"
        }
        
        success, response = self.run_test(
            "Check Access - Initial State",
            "POST",
            "subscription/check-access",
            [200, 402],
            data=check_access_data,
            headers={'Authorization': f'Bearer {fresh_token}'}
        )
        
        if success:
            has_access = response.get('has_access', False)
            current_usage = response.get('current_usage', 0)
            limit = response.get('limit', 0)
            status_code = getattr(self, 'last_response_status', 0)
            
            print(f"   📊 Initial Access Check:")
            print(f"      Status Code: {status_code}")
            print(f"      has_access: {has_access}")
            print(f"      current_usage: {current_usage}")
            print(f"      limit: {limit}")
            
            if has_access and status_code == 200:
                print(f"   ✅ Fresh user has initial access as expected")
            else:
                print(f"   ⚠️  Unexpected initial access state")
        
        # Generate mock tests to exhaust quota
        print(f"\n🎯 Step 3: Exhaust Mock Test Quota")
        mock_test_data = {
            "exam_type": "JEE",
            "subjects": ["Mathematics"],
            "difficulty_level": 3,
            "num_questions": 5
        }
        
        tests_generated = 0
        max_attempts = 3
        
        for i in range(max_attempts):
            print(f"   Generating test {i+1}/{max_attempts}...")
            
            success, response = self.run_test(
                f"Mock Test Generation - Attempt {i+1}",
                "POST",
                "mock-tests/generate",
                [200, 402, 429],
                data=mock_test_data,
                headers={'Authorization': f'Bearer {fresh_token}'}
            )
            
            status_code = getattr(self, 'last_response_status', 0)
            
            if status_code == 200:
                tests_generated += 1
                test_id = response.get('test_id', 'unknown')
                print(f"      ✅ Test {i+1} generated successfully (ID: {test_id})")
            elif status_code in [402, 429]:
                print(f"      🎯 Quota exhausted at test {i+1} (Status: {status_code})")
                break
            else:
                print(f"      ❌ Test {i+1} failed with status {status_code}")
            
            time.sleep(2)
        
        print(f"   📊 Generated {tests_generated} tests before hitting limit")
        
        # Test checkFeatureAccess after quota exhaustion
        print(f"\n🚨 Step 4: Test checkFeatureAccess After Quota Exhaustion")
        print("   Expected: HTTP 402 Payment Required with upsell_info")
        
        success, response = self.run_test(
            "Check Access - After Quota Exhaustion",
            "POST",
            "subscription/check-access",
            402,  # Expecting 402 Payment Required
            data=check_access_data,
            headers={'Authorization': f'Bearer {fresh_token}'}
        )
        
        check_access_402_working = False
        if success:
            has_access = response.get('has_access', True)
            upgrade_needed = response.get('upgrade_needed', False)
            upsell_info = response.get('upsell_info', {})
            
            print(f"   ✅ checkFeatureAccess correctly returns 402")
            print(f"   📊 Response Details:")
            print(f"      has_access: {has_access}")
            print(f"      upgrade_needed: {upgrade_needed}")
            print(f"      upsell_info present: {bool(upsell_info)}")
            
            if upsell_info:
                mentor_message = upsell_info.get('mentor_message', '')
                professor_message = upsell_info.get('professor_message', '')
                target_plan = upsell_info.get('target_plan', {})
                
                print(f"      mentor_message: {'Present' if mentor_message else 'Missing'}")
                print(f"      professor_message: {'Present' if professor_message else 'Missing'}")
                print(f"      target_plan: {target_plan.get('name', 'Missing')}")
                
                if mentor_message and professor_message and target_plan:
                    print(f"   ✅ Complete upsell_info structure present")
                    check_access_402_working = True
                else:
                    print(f"   ⚠️  Incomplete upsell_info structure")
            else:
                print(f"   ❌ Missing upsell_info in 402 response")
        else:
            status_code = getattr(self, 'last_response_status', 0)
            error_data = getattr(self, 'last_error_data', {})
            
            print(f"   ❌ checkFeatureAccess failed to return 402")
            print(f"   Status Code: {status_code}")
            print(f"   Error Data: {error_data}")
            
            if status_code == 200:
                print(f"   🚨 CRITICAL: Returns 200 OK instead of 402 (this is the reported issue)")
            elif status_code == 500:
                print(f"   🚨 CRITICAL: 500 Internal Server Error (backend issue)")
        
        return check_access_402_working

    def run_focused_tests(self):
        """Run focused tests for the review request"""
        print("🎯 REVIEW REQUEST FOCUSED TESTING")
        print("=" * 60)
        print("Issue 1: Slow generation banner appears instantly (should delay 10s)")
        print("Issue 2: Subscription modal not appearing (402 status codes)")
        print("Focus: Backend API responses for subscription system")
        print("Test credentials: test@dhruvai.com/password123")
        print("=" * 60)
        
        # Run subscription modal tests
        subscription_success = self.test_subscription_modal_fixes()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 REVIEW REQUEST TESTING SUMMARY")
        print("=" * 60)
        
        if subscription_success:
            print("✅ SUBSCRIPTION SYSTEM: All tests passed")
            print("   - checkFeatureAccess returns proper 402 status codes")
            print("   - Mock test generation handles limits correctly")
            print("   - Error responses contain proper upsell_info structure")
        else:
            print("❌ SUBSCRIPTION SYSTEM: Issues detected")
            print("   - checkFeatureAccess may not return proper 402 status codes")
            print("   - Mock test generation error handling needs review")
            print("   - Subscription modal may not trigger correctly")
        
        print(f"\nNote: Slow generation banner testing requires frontend validation")
        print(f"Backend APIs tested focus on subscription error responses")
        
        print(f"\n📊 Test Statistics:")
        print(f"   Total Tests: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%" if self.tests_run > 0 else "   Success Rate: 0%")
        
        return subscription_success

if __name__ == "__main__":
    tester = ReviewRequestTester()
    
    print("🚨 CRITICAL: REVIEW REQUEST FOCUSED TESTING")
    print("Testing recent fixes to MockTests component and subscription system")
    
    success = tester.run_focused_tests()
    
    if success:
        print("\n✅ Review request testing completed successfully!")
        print("Backend subscription system is working correctly")
        sys.exit(0)
    else:
        print("\n❌ Review request testing completed with critical issues")
        print("Backend subscription system needs attention")
        sys.exit(1)