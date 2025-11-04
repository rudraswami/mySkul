#!/usr/bin/env python3
"""
402 Payment Required Response Fix Test
Testing the specific fix for Issue 2 - subscription modal not appearing after hitting mock test limits
"""

import requests
import sys
import json
import time
import os
from datetime import datetime

class Test402PaymentRequiredFix:
    def __init__(self):
        # Get backend URL from environment
        backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'https://dhruv-tutor-app.preview.emergentagent.com')
        self.base_url = f"{backend_url}/api"
        self.token = None
        self.last_response_status = None
        self.last_error_data = None
        
        print(f"Backend URL: {self.base_url}")
    
    def run_test(self, test_name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30)
            else:
                print(f"   ❌ Unsupported method: {method}")
                return False, {}
            
            self.last_response_status = response.status_code
            
            # Try to parse JSON response
            try:
                response_data = response.json()
                self.last_error_data = response_data
            except:
                response_data = {"raw_response": response.text}
                self.last_error_data = response_data
            
            # Check if status code matches expected
            if isinstance(expected_status, list):
                status_match = response.status_code in expected_status
            else:
                status_match = response.status_code == expected_status
            
            if status_match:
                print(f"   ✅ {test_name} - Status: {response.status_code}")
                return True, response_data
            else:
                print(f"   ❌ {test_name} - Expected: {expected_status}, Got: {response.status_code}")
                print(f"   Error: {response_data}")
                return False, response_data
                
        except Exception as e:
            print(f"   ❌ {test_name} - Exception: {str(e)}")
            self.last_response_status = 0
            self.last_error_data = {"exception": str(e)}
            return False, {}
    
    def test_402_payment_required_response_fix(self):
        """CRITICAL VALIDATION - Issue 2 Fix: Test 402 Payment Required response using test endpoint"""
        print("\n🚨 CRITICAL VALIDATION - ISSUE 2 FIX: 402 PAYMENT REQUIRED RESPONSE TESTING")
        print("   Testing the 402 Payment Required response fix using test endpoint")
        print("   Focus: Use test endpoint to artificially set usage above limit and verify 402 responses")
        
        # Step 1: Login as test@dhruvai.com/password123 (free tier user with limit=2)
        print("\n📊 Step 1: Login as Free Tier User")
        login_data = {
            "email": "test@dhruvai.com",
            "password": "password123"
        }
        
        success, response = self.run_test(
            "Login Free Tier User",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if not success or 'token' not in response:
            print("❌ Failed to login as test@dhruvai.com")
            return False
        
        self.token = response['token']
        user_data = response.get('user', {})
        print(f"   ✅ Logged in successfully")
        print(f"   User: {user_data.get('email', 'unknown')}")
        print(f"   Plan: {user_data.get('subscription_type', 'unknown')}")
        
        # Step 2: Check initial subscription status
        print("\n📊 Step 2: Check Initial Subscription Status")
        success, response = self.run_test(
            "Initial Subscription Status",
            "GET",
            "subscription/current",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            plan = response.get('plan', 'unknown')
            status = response.get('status', 'unknown')
            print(f"   ✅ Current plan: {plan}, status: {status}")
        
        # Step 3: Check initial usage for mock_tests_weekly
        print("\n📊 Step 3: Check Initial Usage for mock_tests_weekly")
        success, response = self.run_test(
            "Initial Usage Check",
            "GET",
            "subscription/usage",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            usage_data = response
            mock_tests_usage = usage_data.get('mock_tests_weekly', {})
            current_usage = mock_tests_usage.get('used', 0)
            limit = mock_tests_usage.get('limit', 2)
            print(f"   ✅ Initial mock_tests_weekly usage: {current_usage}/{limit}")
        
        # Step 4: Use test endpoint to set usage above limit
        print("\n🔧 Step 4: Use Test Endpoint to Set Usage Above Limit")
        print("   Setting mock_tests_weekly usage to 3 (above limit of 2)")
        
        test_set_usage_data = {
            "feature_name": "mock_tests_weekly",
            "usage_count": 3
        }
        
        # Try with query parameters instead of JSON body
        success, response = self.run_test(
            "Set Usage Above Limit",
            "POST",
            "subscription/test-set-usage?feature_name=mock_tests_weekly&usage_count=3",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if not success:
            print("❌ Failed to set usage above limit using test endpoint")
            print("   This test endpoint may not exist or may be disabled")
            return False
        
        print(f"   ✅ Usage set to 3/2 using test endpoint")
        
        # Step 5: Test check-access endpoint - should return 402
        print("\n🚨 Step 5: Test check-access Endpoint - Expected 402 Payment Required")
        
        check_access_data = {
            "feature_name": "mock_tests_weekly"
        }
        
        success, response = self.run_test(
            "Check Access - Should Return 402",
            "POST",
            "subscription/check-access",
            402,  # EXPECTING 402 Payment Required
            data=check_access_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        check_access_402_working = False
        if success:
            # Verify response structure
            has_access = response.get('has_access', True)
            upgrade_needed = response.get('upgrade_needed', False)
            upsell_info = response.get('upsell_info', {})
            
            print(f"   ✅ check-access correctly returns 402 Payment Required")
            print(f"   📊 Response Details:")
            print(f"      has_access: {has_access}")
            print(f"      upgrade_needed: {upgrade_needed}")
            print(f"      upsell_info present: {bool(upsell_info)}")
            
            # Verify upsell_info structure
            if upsell_info:
                mentor_message = upsell_info.get('mentor_message', '')
                professor_message = upsell_info.get('professor_message', '')
                target_plan = upsell_info.get('target_plan', {})
                
                print(f"      mentor_message: {'✓' if mentor_message else '✗'}")
                print(f"      professor_message: {'✓' if professor_message else '✗'}")
                print(f"      target_plan: {'✓' if target_plan else '✗'}")
                
                if mentor_message and professor_message and target_plan:
                    print(f"   ✅ Complete upsell_info structure present")
                    check_access_402_working = True
                else:
                    print(f"   ❌ Incomplete upsell_info structure")
            else:
                print(f"   ❌ Missing upsell_info in 402 response")
        else:
            status_code = self.last_response_status
            error_data = self.last_error_data
            
            print(f"   ❌ check-access failed to return 402")
            print(f"   Status Code: {status_code}")
            print(f"   Error Data: {error_data}")
            
            if status_code == 200:
                print(f"   🚨 CRITICAL: Still returns 200 OK instead of 402 (fix not working)")
            elif status_code == 500:
                print(f"   🚨 CRITICAL: 500 Internal Server Error (ObjectId serialization issue)")
        
        # Step 6: Test mock test generation - should also return 402
        print("\n🚨 Step 6: Test Mock Test Generation - Expected 402 Payment Required")
        
        mock_test_data = {
            "exam_type": "JEE",
            "subjects": ["Mathematics"],
            "difficulty_level": 3,
            "num_questions": 5
        }
        
        success, response = self.run_test(
            "Mock Test Generation - Should Return 402",
            "POST",
            "mock-tests/generate",
            402,  # EXPECTING 402 Payment Required
            data=mock_test_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        mock_generation_402_working = False
        if success:
            print(f"   ✅ Mock test generation correctly returns 402 Payment Required")
            
            # Check error response structure
            message = response.get('message', '')
            action = response.get('action', '')
            current_plan = response.get('current_plan', '')
            upgrade_url = response.get('upgrade_url', '')
            
            print(f"   📊 Error Response Structure:")
            print(f"      message: {'✓' if message else '✗'}")
            print(f"      action: {'✓' if action == 'upgrade' else '✗'}")
            print(f"      current_plan: {'✓' if current_plan else '✗'}")
            print(f"      upgrade_url: {'✓' if upgrade_url else '✗'}")
            
            if message and action == 'upgrade' and current_plan and upgrade_url:
                print(f"   ✅ Proper error structure for subscription modal")
                mock_generation_402_working = True
            else:
                print(f"   ❌ Incomplete error structure")
        else:
            status_code = self.last_response_status
            print(f"   ❌ Mock test generation failed to return 402 (Status: {status_code})")
            
            if status_code == 500:
                print(f"   🚨 CRITICAL: 500 Internal Server Error (ObjectId serialization issue)")
        
        # Step 7: Verify no ObjectId serialization errors
        print("\n🔍 Step 7: Verify No ObjectId Serialization Errors")
        
        # Check if any responses contained ObjectId serialization errors
        objectid_errors_found = False
        if hasattr(self, 'last_error_data'):
            error_str = str(self.last_error_data)
            if 'ObjectId' in error_str and ('not iterable' in error_str or 'not JSON serializable' in error_str):
                objectid_errors_found = True
                print(f"   🚨 ObjectId serialization errors detected: {error_str}")
        
        if not objectid_errors_found:
            print(f"   ✅ No ObjectId serialization errors detected")
        
        # Final Assessment
        print(f"\n🎯 CRITICAL VALIDATION - ISSUE 2 FIX TESTING SUMMARY:")
        print(f"   ✅ Free Tier User Login: ✓")
        print(f"   ✅ Test Endpoint Usage Set: ✓")
        print(f"   ✅ check-access Returns 402: {'✓' if check_access_402_working else '✗'}")
        print(f"   ✅ Mock Generation Returns 402: {'✓' if mock_generation_402_working else '✗'}")
        print(f"   ✅ No ObjectId Errors: {'✓' if not objectid_errors_found else '✗'}")
        
        # Critical issues identification
        critical_issues = []
        if not check_access_402_working:
            critical_issues.append("check-access endpoint not returning proper 402 status codes")
        if not mock_generation_402_working:
            critical_issues.append("Mock test generation not returning proper 402 responses")
        if objectid_errors_found:
            critical_issues.append("ObjectId serialization errors in error responses")
        
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED:")
            for issue in critical_issues:
                print(f"   - {issue}")
            print(f"\n🔧 RECOMMENDATIONS:")
            print(f"   - Fix check-access to return HTTP 402 when current_usage >= limit")
            print(f"   - Ensure proper upsell_info structure in 402 responses")
            print(f"   - Fix ObjectId serialization in error responses")
            return False
        else:
            print(f"\n✅ ISSUE 2 FIX VALIDATION SUCCESSFUL")
            print(f"   - check-access returns proper 402 status codes")
            print(f"   - Mock test generation handles limits with 402 responses")
            print(f"   - No ObjectId serialization errors")
            print(f"   - Subscription modals should now trigger correctly")
            return True

if __name__ == "__main__":
    tester = Test402PaymentRequiredFix()
    
    # Run the specific 402 Payment Required response fix test
    print("🚀 Starting 402 Payment Required Response Fix Testing")
    print("="*80)
    
    success = tester.test_402_payment_required_response_fix()
    
    if success:
        print("\n🎉 402 Payment Required fix validation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ 402 Payment Required fix validation failed. Check the output above for details.")
        sys.exit(1)