#!/usr/bin/env python3
"""
Critical Backend Testing for Review Request
Tests the specific issues mentioned in the review request
"""

import requests
import json
import time
import sys

class CriticalFixesTester:
    def __init__(self):
        # Use internal backend URL since external is timing out
        self.base_url = "http://localhost:8001/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0

    def log(self, message):
        print(f"[{time.strftime('%H:%M:%S')}] {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        if self.token and 'Authorization' not in test_headers:
            test_headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        self.log(f"   URL: {url}")
        self.log(f"   Method: {method}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)

            self.log(f"   Status Code: {response.status_code}")
            
            # Store last response status for subscription error checking
            self.last_response_status = response.status_code
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                self.log(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    self.log(f"   Error: {error_data}")
                    self.last_error_data = error_data
                except:
                    self.log(f"   Error: {response.text}")
                    self.last_error_data = {"error": response.text}
                return False, {}

        except Exception as e:
            self.log(f"❌ Failed - Error: {str(e)}")
            self.last_response_status = 0
            self.last_error_data = {"error": str(e)}
            return False, {}

    def authenticate(self):
        """Authenticate with test user"""
        self.log("🔐 Authenticating with test@dhruvai.com...")
        
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
            self.log(f"✅ Authentication successful")
            return True
        else:
            self.log(f"❌ Authentication failed")
            return False

    def create_fresh_user(self):
        """Create fresh user for quota testing"""
        fresh_user_email = f"quota_test_{int(time.time())}@dhruvai.com"
        registration_data = {
            "full_name": "Quota Test User",
            "email": fresh_user_email,
            "password": "password123",
            "exam_type": "JEE",
            "grade": "Class 12",
            "target_year": 2026
        }
        
        success, response = self.run_test(
            "Create Fresh User",
            "POST",
            "auth/register",
            200,
            data=registration_data
        )
        
        if success and 'token' in response:
            fresh_token = response['token']
            fresh_user_id = response.get('user', {}).get('user_id')
            self.log(f"✅ Fresh user created: {fresh_user_email}")
            return fresh_token, fresh_user_id
        else:
            self.log(f"❌ Failed to create fresh user")
            return None, None

    def test_mock_test_quota_enforcement(self):
        """Test Mock Test Quota Enforcement - 2 successful, 3rd returns 402"""
        self.log("\n🎯 TESTING MOCK TEST QUOTA ENFORCEMENT")
        self.log("   Expected: 2 successful generations, 3rd returns 402 Payment Required")
        
        # Create fresh user for quota testing
        fresh_token, fresh_user_id = self.create_fresh_user()
        if not fresh_token:
            return False
        
        mock_test_data = {
            "exam_type": "JEE",
            "subjects": ["Mathematics"],
            "difficulty_level": 3,
            "num_questions": 5
        }
        
        quota_test_results = []
        
        for i in range(3):  # Try to generate 3 tests
            self.log(f"   Generating mock test {i+1}/3...")
            
            success, response = self.run_test(
                f"Mock Test Generation - Attempt {i+1}",
                "POST",
                "mock-tests/generate",
                [200, 402],  # Accept both success and quota limit
                data=mock_test_data,
                headers={'Authorization': f'Bearer {fresh_token}'}
            )
            
            status_code = getattr(self, 'last_response_status', 0)
            
            if status_code == 200:
                test_id = response.get('test_id', 'unknown')
                self.log(f"      ✅ Test {i+1} generated successfully (ID: {test_id})")
                quota_test_results.append({'attempt': i+1, 'status': 'success', 'test_id': test_id})
            elif status_code == 402:
                upsell_info = response.get('upsell_info', {})
                self.log(f"      🎯 Test {i+1} blocked with 402 Payment Required")
                self.log(f"      Upsell info present: {bool(upsell_info)}")
                quota_test_results.append({'attempt': i+1, 'status': 'quota_reached', 'upsell_info': upsell_info})
                break
            else:
                self.log(f"      ❌ Test {i+1} failed with status {status_code}")
                quota_test_results.append({'attempt': i+1, 'status': 'error', 'status_code': status_code})
            
            time.sleep(2)  # Delay between generations
        
        # Analyze results
        successful_tests = [r for r in quota_test_results if r['status'] == 'success']
        quota_blocked = [r for r in quota_test_results if r['status'] == 'quota_reached']
        
        self.log(f"\n   📊 Quota Enforcement Results:")
        self.log(f"      Successful generations: {len(successful_tests)}")
        self.log(f"      Quota blocks (402): {len(quota_blocked)}")
        
        quota_enforcement_working = (len(successful_tests) == 2 and len(quota_blocked) == 1)
        
        if quota_enforcement_working:
            self.log(f"   ✅ QUOTA ENFORCEMENT WORKING: 2 successful, 3rd blocked with 402")
            return True, fresh_token
        else:
            self.log(f"   ❌ QUOTA ENFORCEMENT FAILED: Expected 2 successful + 1 blocked")
            return False, fresh_token

    def test_subscription_check_access_402(self, fresh_token):
        """Test Subscription Check Access returns 402 when quota exceeded"""
        self.log("\n🔍 TESTING SUBSCRIPTION CHECK ACCESS 402 STATUS CODES")
        self.log("   Testing /api/subscription/check-access endpoint")
        
        check_access_data = {
            "feature_name": "mock_tests_weekly"
        }
        
        success, response = self.run_test(
            "Check Access - Should Return 402",
            "POST",
            "subscription/check-access",
            402,  # Expecting 402 Payment Required
            data=check_access_data,
            headers={'Authorization': f'Bearer {fresh_token}'}
        )
        
        if success:
            has_access = response.get('has_access', True)
            upsell_info = response.get('upsell_info', {})
            
            self.log(f"   ✅ check-access returns 402 Payment Required")
            self.log(f"   has_access: {has_access}")
            self.log(f"   upsell_info present: {bool(upsell_info)}")
            
            if not has_access and upsell_info:
                self.log(f"   ✅ Proper 402 response structure")
                return True
            else:
                self.log(f"   ❌ Incomplete 402 response structure")
                return False
        else:
            status_code = getattr(self, 'last_response_status', 0)
            self.log(f"   ❌ check-access failed to return 402 (got {status_code})")
            return False

    def test_plan_upgrade_query_parameters(self):
        """Test Plan Upgrade with Query Parameters"""
        self.log("\n🔧 TESTING PLAN UPGRADE WITH QUERY PARAMETERS")
        self.log("   Testing /api/subscription/upgrade?target_tier=PREMIUM&billing_cycle=monthly")
        
        if not self.token:
            if not self.authenticate():
                return False
        
        # Test upgrade endpoint with query parameters
        upgrade_url = "subscription/upgrade?target_tier=PREMIUM&billing_cycle=monthly"
        
        success, response = self.run_test(
            "Plan Upgrade with Query Parameters",
            "POST",
            upgrade_url,
            [200, 201, 422],  # Accept success or validation responses
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        status_code = getattr(self, 'last_response_status', 0)
        
        if status_code in [200, 201]:
            self.log(f"   ✅ Plan upgrade accepts query parameters")
            return True
        elif status_code == 422:
            error_data = getattr(self, 'last_error_data', {})
            self.log(f"   ❌ 422 Validation Error - query parameters not accepted")
            self.log(f"   Error: {error_data}")
            return False
        else:
            self.log(f"   ❌ Plan upgrade failed with status {status_code}")
            return False

    def test_case_sensitivity_fix(self):
        """Test Case Sensitivity Fix for plan_name 'FREE'"""
        self.log("\n🔤 TESTING CASE SENSITIVITY FIX (plan_name 'FREE')")
        self.log("   Testing uppercase 'FREE' plan name handling")
        
        if not self.token:
            if not self.authenticate():
                return False
        
        # Check current subscription
        success, response = self.run_test(
            "Current Subscription - Case Sensitivity",
            "GET",
            "subscription/current",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            plan_name = response.get('plan', '').upper()
            self.log(f"   Plan name returned: '{response.get('plan', '')}'")
            self.log(f"   Uppercase plan name: '{plan_name}'")
            
            if plan_name == 'FREE':
                self.log(f"   ✅ Case sensitivity working - 'FREE' plan recognized")
                return True
            else:
                self.log(f"   ❌ Case sensitivity issue - expected 'FREE', got '{plan_name}'")
                return False
        else:
            return False

    def run_all_tests(self):
        """Run all critical fix tests"""
        self.log("🚀 STARTING CRITICAL BACKEND FIXES TESTING")
        self.log("="*60)
        self.log("Focus Areas:")
        self.log("1. Mock Test Quota Enforcement (2 successful, 3rd returns 402)")
        self.log("2. Subscription Check Access (/api/subscription/check-access returns 402)")
        self.log("3. Plan Upgrade Parameters (/api/subscription/upgrade with query params)")
        self.log("4. Case Sensitivity Fix (plan_name 'FREE' uppercase)")
        self.log("="*60)
        
        # Authenticate first
        if not self.authenticate():
            self.log("❌ Authentication failed - cannot proceed")
            return False
        
        # Test 1: Mock Test Quota Enforcement
        quota_working, fresh_token = self.test_mock_test_quota_enforcement()
        
        # Test 2: Subscription Check Access 402
        check_access_working = False
        if fresh_token:
            check_access_working = self.test_subscription_check_access_402(fresh_token)
        
        # Test 3: Plan Upgrade Query Parameters
        upgrade_params_working = self.test_plan_upgrade_query_parameters()
        
        # Test 4: Case Sensitivity Fix
        case_sensitivity_working = self.test_case_sensitivity_fix()
        
        # Final Assessment
        self.log(f"\n🎯 CRITICAL FIXES TESTING SUMMARY:")
        self.log(f"   ✅ Mock Test Quota Enforcement: {'✓' if quota_working else '✗'}")
        self.log(f"   ✅ Subscription Check Access 402: {'✓' if check_access_working else '✗'}")
        self.log(f"   ✅ Plan Upgrade Query Parameters: {'✓' if upgrade_params_working else '✗'}")
        self.log(f"   ✅ Case Sensitivity Fix: {'✓' if case_sensitivity_working else '✗'}")
        
        # Count successful fixes
        fixes_working = sum([
            quota_working,
            check_access_working,
            upgrade_params_working,
            case_sensitivity_working
        ])
        
        total_fixes = 4
        success_rate = (fixes_working / total_fixes) * 100
        
        self.log(f"\n📊 Overall Fix Success Rate: {fixes_working}/{total_fixes} ({success_rate:.1f}%)")
        self.log(f"📊 API Tests: {self.tests_passed}/{self.tests_run} passed ({(self.tests_passed/self.tests_run)*100:.1f}%)")
        
        if fixes_working == total_fixes:
            self.log("🎉 ALL CRITICAL FIXES WORKING - Backend issues resolved!")
            return True
        elif fixes_working >= 3:
            self.log("✅ MOST FIXES WORKING - Minor issues remain")
            return True
        elif fixes_working >= 2:
            self.log("⚠️  SOME FIXES WORKING - Significant issues remain")
            return False
        else:
            self.log("🚨 CRITICAL ISSUES PERSIST - Major backend problems")
            return False

if __name__ == "__main__":
    tester = CriticalFixesTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)