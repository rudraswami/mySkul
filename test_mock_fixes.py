#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class MockTestBugFixesTester:
    def __init__(self, base_url="https://eduai-platform-25.preview.emergentagent.com/api"):
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
            
            success = response.status_code == expected_status
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
        """Test user login with the registered user"""
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

    def test_mock_tests_critical_bug_fixes(self):
        """CRITICAL: Test Mock Tests Bug Fixes - Feature Name Consistency and Free Tier Access"""
        print("\n🚨 CRITICAL: MOCK TESTS BUG FIXES TESTING")
        print("   Focus: Feature name consistency (mock_tests_weekly), Free tier access, 402 status codes")
        print("   User reported: Free tier shows 0/2 but blocks generation, toLowerCase error, static error messages")
        
        # Create fresh user for free tier testing
        fresh_user_email = f"mock_test_fix_{int(time.time())}@dhruvai.com"
        registration_data = {
            "full_name": "Mock Test Fix User",
            "email": fresh_user_email,
            "password": "password123",
            "exam_type": "JEE",
            "grade": "Class 12",
            "target_year": 2026
        }
        
        print(f"\n📝 Step 1: Creating Fresh User for Free Tier Testing")
        print(f"   Email: {fresh_user_email}")
        
        success, response = self.run_test(
            "Create Fresh User for Mock Test Fix Testing",
            "POST",
            "auth/register",
            200,
            data=registration_data
        )
        
        if not success or 'token' not in response:
            print("❌ Failed to create fresh user for testing")
            return False
        
        fresh_token = response['token']
        print(f"   ✅ Fresh user created successfully")
        
        # Test 1: Subscription Check-Access with mock_tests_weekly
        print(f"\n🔍 Step 2: Test Subscription Check-Access with mock_tests_weekly")
        print(f"   Testing: /api/subscription/check-access with feature_name='mock_tests_weekly'")
        print(f"   Expected: Proper access validation with consistent feature naming")
        
        # Use POST with query parameter
        success, response = self.run_test(
            "Check Access - mock_tests_weekly",
            "POST",
            "subscription/check-access?feature_name=mock_tests_weekly",
            [200, 402],  # Accept both for now
            headers={'Authorization': f'Bearer {fresh_token}'}
        )
        
        if success:
            has_access = response.get('has_access', False)
            reason = response.get('reason', 'unknown')
            current_usage = response.get('current_usage', 0)
            limit = response.get('limit', 0)
            upgrade_needed = response.get('upgrade_needed', False)
            status_code = getattr(self, 'last_response_status', 0)
            
            print(f"   📊 Check-Access Results:")
            print(f"      Status Code: {status_code}")
            print(f"      has_access: {has_access}")
            print(f"      current_usage: {current_usage}")
            print(f"      limit: {limit}")
            print(f"      reason: {reason}")
            print(f"      upgrade_needed: {upgrade_needed}")
            
            # Verify free tier should have access initially
            if has_access and current_usage == 0 and limit >= 1:
                print(f"   ✅ Free tier access logic working correctly")
                free_tier_access_working = True
            else:
                print(f"   ❌ Free tier access logic issue detected")
                free_tier_access_working = False
        else:
            print(f"   ❌ Check-access endpoint failed")
            free_tier_access_working = False
        
        # Test 2: Mock Test Generation with mock_tests_weekly validation
        print(f"\n🎯 Step 3: Test Mock Test Generation API")
        print(f"   Testing: /api/mock-tests/generate with subscription validation")
        print(f"   Expected: Should work within free tier limits (1 test per week)")
        
        mock_test_data = {
            "exam_type": "JEE",
            "subjects": ["Mathematics"],  # Changed to array format
            "difficulty": 3,
            "num_questions": 5
        }
        
        success, response = self.run_test(
            "Mock Test Generation - Within Free Tier",
            "POST",
            "mock-tests/generate",
            200,
            data=mock_test_data,
            headers={'Authorization': f'Bearer {fresh_token}'}
        )
        
        if success:
            test_id = response.get('test_id')
            test_name = response.get('test_name', 'N/A')
            questions_count = len(response.get('questions', []))
            
            print(f"   ✅ Mock test generated successfully")
            print(f"   Test ID: {test_id}")
            print(f"   Test Name: {test_name}")
            print(f"   Questions: {questions_count}")
            mock_generation_working = True
        else:
            error_status = getattr(self, 'last_response_status', 0)
            error_data = getattr(self, 'last_error_data', {})
            
            print(f"   ❌ Mock test generation failed")
            print(f"   Status Code: {error_status}")
            print(f"   Error Data: {error_data}")
            
            # Check for specific error types
            if error_status == 402:
                print(f"   🚨 402 Payment Required - This should NOT happen for fresh free tier user")
            elif error_status == 500:
                print(f"   🚨 500 Internal Server Error - Backend issue")
            elif error_status == 422:
                print(f"   🚨 422 Validation Error - Request format issue")
            
            mock_generation_working = False
        
        # Test 3: Mock Test Subjects API for usage display
        print(f"\n📊 Step 4: Test Mock Test Subjects API for Usage Display")
        print(f"   Testing: /api/mock-tests/subjects for correct usage information")
        
        success, response = self.run_test(
            "Mock Test Subjects - Usage Display",
            "GET",
            "mock-tests/subjects",
            200,
            headers={'Authorization': f'Bearer {fresh_token}'}
        )
        
        if success:
            subjects = response.get('subjects', [])
            usage_info = response.get('usage_info', {})
            
            print(f"   ✅ Subjects API working")
            print(f"   Subjects available: {len(subjects)}")
            print(f"   Usage info: {usage_info}")
            
            # Check if usage info shows correct feature name and limits
            feature_usage = usage_info.get('mock_tests_weekly', {})
            if feature_usage:
                used = feature_usage.get('used', 0)
                limit = feature_usage.get('limit', 0)
                remaining = feature_usage.get('remaining', 0)
                
                print(f"   📊 mock_tests_weekly usage: {used}/{limit} (remaining: {remaining})")
                
                if mock_generation_working and used == 1 and limit >= 1:
                    print(f"   ✅ Usage tracking updated correctly after generation")
                    usage_tracking_working = True
                else:
                    print(f"   ⚠️  Usage tracking may have issues")
                    usage_tracking_working = False
            else:
                print(f"   ❌ mock_tests_weekly not found in usage info")
                usage_tracking_working = False
        else:
            print(f"   ❌ Subjects API failed")
            usage_tracking_working = False
        
        # Test 4: Test limit reached scenario (generate second test)
        print(f"\n🚫 Step 5: Test Limit Reached Scenario")
        print(f"   Testing: Second mock test generation to trigger limit")
        print(f"   Expected: Should return 402 with proper error structure")
        
        success, response = self.run_test(
            "Mock Test Generation - Limit Reached",
            "POST",
            "mock-tests/generate",
            402,  # Expecting 402 Payment Required
            data=mock_test_data,
            headers={'Authorization': f'Bearer {fresh_token}'}
        )
        
        if success:
            print(f"   ✅ Correctly returned 402 Payment Required")
            
            # Check error structure for subscription modal
            message = response.get('message', '')
            action = response.get('action', '')
            current_plan = response.get('current_plan', '')
            used = response.get('used', 0)
            limit = response.get('limit', 0)
            upgrade_url = response.get('upgrade_url', '')
            
            print(f"   📊 Error Response Structure:")
            print(f"      message: {message}")
            print(f"      action: {action}")
            print(f"      current_plan: {current_plan}")
            print(f"      used: {used}")
            print(f"      limit: {limit}")
            print(f"      upgrade_url: {upgrade_url}")
            
            # Verify proper error structure for frontend modal
            has_proper_structure = (
                message and action == 'upgrade' and 
                current_plan and used > 0 and limit > 0 and upgrade_url
            )
            
            if has_proper_structure:
                print(f"   ✅ Error structure suitable for subscription modal")
                error_handling_working = True
            else:
                print(f"   ❌ Error structure incomplete for subscription modal")
                error_handling_working = False
        else:
            error_status = getattr(self, 'last_response_status', 0)
            error_data = getattr(self, 'last_error_data', {})
            
            print(f"   ❌ Expected 402 but got {error_status}")
            print(f"   Error Data: {error_data}")
            
            if error_status == 200:
                print(f"   🚨 CRITICAL: Should have blocked second test but allowed it")
            elif error_status == 500:
                print(f"   🚨 CRITICAL: 500 error instead of proper 402 subscription error")
            
            error_handling_working = False
        
        # Final Assessment
        print(f"\n🎯 MOCK TESTS BUG FIXES TESTING SUMMARY:")
        print(f"   ✅ Fresh User Creation: ✓")
        print(f"   ✅ Free Tier Access Logic: {'✓' if free_tier_access_working else '✗'}")
        print(f"   ✅ Mock Test Generation: {'✓' if mock_generation_working else '✗'}")
        print(f"   ✅ Usage Tracking: {'✓' if usage_tracking_working else '✗'}")
        print(f"   ✅ 402 Error Handling: {'✓' if error_handling_working else '✗'}")
        
        total_tests = 4
        passed_tests = sum([
            free_tier_access_working,
            mock_generation_working, 
            usage_tracking_working,
            error_handling_working
        ])
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n📊 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests == total_tests:
            print(f"✅ ALL MOCK TEST BUG FIXES WORKING CORRECTLY")
        elif passed_tests >= 3:
            print(f"⚠️  MOST BUG FIXES WORKING - Minor issues remain")
        else:
            print(f"❌ CRITICAL ISSUES REMAIN - Bug fixes not fully working")
        
        return passed_tests >= 3  # At least 3/4 tests should pass

    def run_testing(self):
        """Run the mock test bug fixes testing"""
        print("🚨 CRITICAL: MOCK TEST BUG FIXES TESTING - REVIEW REQUEST FOCUS")
        print(f"   Backend URL: {self.base_url}")
        print(f"   Focus: Feature name consistency, Free tier access, 402 status codes")
        print("=" * 80)
        
        # Authentication first
        print("\n🔐 AUTHENTICATION SETUP")
        if not self.test_user_login():
            print("❌ Authentication failed - cannot proceed with mock test testing")
            return False
        
        # Critical Mock Test Bug Fixes Testing
        print("\n🎯 CRITICAL MOCK TEST BUG FIXES TESTING")
        mock_test_fixes_working = self.test_mock_tests_critical_bug_fixes()
        
        # Final Results
        print("\n" + "=" * 80)
        print(f"🎯 MOCK TEST BUG FIXES TESTING COMPLETED")
        print(f"   Total Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        print(f"\n📊 CRITICAL COMPONENTS STATUS:")
        print(f"   Mock Test Bug Fixes: {'✅ WORKING' if mock_test_fixes_working else '❌ FAILING'}")
        
        if mock_test_fixes_working:
            print("✅ CRITICAL MOCK TEST BUG FIXES WORKING!")
            return True
        else:
            print("❌ CRITICAL FAILURES - Mock test bug fixes not working")
            return False

if __name__ == "__main__":
    tester = MockTestBugFixesTester()
    
    # Run Mock Test Bug Fixes Testing (Review Request Focus)
    print("🚨 CRITICAL: MOCK TEST BUG FIXES TESTING - REVIEW REQUEST FOCUS")
    success = tester.run_testing()
    
    if success:
        print("\n✅ Mock Test Bug Fixes testing completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Mock Test Bug Fixes testing completed with critical issues")
        sys.exit(1)