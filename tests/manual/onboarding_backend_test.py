#!/usr/bin/env python3
"""
Onboarding Fix Validation - Backend Testing
Testing email/password registration and login with profile_completed field
"""

import requests
import json
import time
from datetime import datetime
import random
import string

class OnboardingBackendTester:
    def __init__(self):
        self.base_url = "https://dhruv-neuro-ai.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = {}
        self.test_user_email = None
        self.test_user_token = None
        self.test_user_id = None
    
    def log(self, message, level="INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbols = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "FAIL": "❌",
            "WARNING": "⚠️",
            "TEST": "🧪"
        }
        symbol = symbols.get(level, "ℹ️")
        print(f"[{timestamp}] {symbol} {message}")
    
    def generate_test_email(self):
        """Generate unique test email"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"onboarding_test_{random_suffix}@dhruvai.com"
    
    def run_test(self, test_name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        test_headers = self.session.headers.copy()
        if headers:
            test_headers.update(headers)
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(url, headers=test_headers, timeout=15)
            elif method == "POST":
                response = self.session.post(url, json=data, headers=test_headers, timeout=15)
            elif method == "PUT":
                response = self.session.put(url, json=data, headers=test_headers, timeout=15)
            
            elapsed_time = time.time() - start_time
            
            # Handle expected status as list or single value
            if isinstance(expected_status, list):
                status_match = response.status_code in expected_status
            else:
                status_match = response.status_code == expected_status
            
            if status_match:
                try:
                    response_data = response.json()
                    return True, response_data, response.status_code, elapsed_time
                except:
                    return True, {}, response.status_code, elapsed_time
            else:
                try:
                    error_data = response.json()
                    return False, error_data, response.status_code, elapsed_time
                except:
                    return False, {"error": response.text}, response.status_code, elapsed_time
                    
        except Exception as e:
            return False, {"error": str(e)}, 0, 0
    
    # ============= TEST 1: Email/Password Registration with Profile Fields =============
    
    def test_registration_with_profile(self):
        """Test 1: Email/Password Registration with Profile Fields"""
        self.log("=" * 80)
        self.log("TEST 1: Email/Password Registration with Profile Fields", "TEST")
        self.log("=" * 80)
        
        results = {
            'returns_200_or_201': False,
            'returns_jwt_token': False,
            'returns_user_with_profile_completed_true': False,
            'user_saved_in_db_with_profile_completed': False,
            'all_profile_fields_saved': False
        }
        
        # Generate unique test email
        self.test_user_email = self.generate_test_email()
        
        # Test data
        test_data = {
            "full_name": "Onboarding Test User",
            "email": self.test_user_email,
            "password": "TestPassword123!",
            "exam_type": "JEE",
            "grade": "12",
            "target_year": 2026
        }
        
        self.log(f"\n📝 Registering user: {self.test_user_email}")
        self.log(f"   Profile fields: exam_type={test_data['exam_type']}, grade={test_data['grade']}, target_year={test_data['target_year']}")
        
        success, response, status, elapsed = self.run_test(
            "Register User",
            "POST",
            "auth/register",
            [200, 201],
            data=test_data
        )
        
        if success:
            results['returns_200_or_201'] = True
            self.log(f"✅ Registration successful: {status} ({elapsed:.2f}s)", "SUCCESS")
            
            # Check JWT token
            if 'token' in response and response['token']:
                results['returns_jwt_token'] = True
                self.test_user_token = response['token']
                self.log(f"✅ JWT token returned: {response['token'][:30]}...", "SUCCESS")
            else:
                self.log("❌ JWT token NOT returned", "FAIL")
            
            # Check user object with profile_completed
            if 'user' in response:
                user = response['user']
                self.test_user_id = user.get('user_id')
                self.log(f"\n📊 User object returned:")
                self.log(f"   - user_id: {user.get('user_id')}")
                self.log(f"   - full_name: {user.get('full_name')}")
                self.log(f"   - email: {user.get('email')}")
                self.log(f"   - exam_type: {user.get('exam_type')}")
                self.log(f"   - grade: {user.get('grade')}")
                self.log(f"   - target_year: {user.get('target_year')}")
                self.log(f"   - profile_completed: {user.get('profile_completed')}")
                self.log(f"   - subscription_type: {user.get('subscription_type')}")
                
                # Check profile_completed is True
                if user.get('profile_completed') == True:
                    results['returns_user_with_profile_completed_true'] = True
                    self.log("✅ profile_completed = True in response", "SUCCESS")
                else:
                    self.log(f"❌ profile_completed = {user.get('profile_completed')} (expected True)", "FAIL")
                
                # Check all profile fields
                if (user.get('exam_type') == test_data['exam_type'] and
                    user.get('grade') == test_data['grade'] and
                    user.get('target_year') == test_data['target_year']):
                    results['all_profile_fields_saved'] = True
                    self.log("✅ All profile fields present in response", "SUCCESS")
                else:
                    self.log("❌ Some profile fields missing or incorrect", "FAIL")
            else:
                self.log("❌ User object NOT returned", "FAIL")
            
            # Verify in database by logging in again
            self.log("\n🔍 Verifying user in database by logging in...")
            login_success, login_response, login_status, _ = self.run_test(
                "Verify Login",
                "POST",
                "auth/login",
                200,
                data={
                    "email": self.test_user_email,
                    "password": test_data['password']
                }
            )
            
            if login_success and 'user' in login_response:
                db_user = login_response['user']
                if db_user.get('profile_completed') == True:
                    results['user_saved_in_db_with_profile_completed'] = True
                    self.log("✅ User saved in DB with profile_completed = True", "SUCCESS")
                else:
                    self.log(f"❌ User in DB has profile_completed = {db_user.get('profile_completed')}", "FAIL")
        else:
            self.log(f"❌ Registration failed: {status} - {response}", "FAIL")
        
        return results
    
    # ============= TEST 2: Email/Password Login Returns profile_completed =============
    
    def test_login_returns_profile_completed(self):
        """Test 2: Email/Password Login Returns profile_completed"""
        self.log("\n" + "=" * 80)
        self.log("TEST 2: Email/Password Login Returns profile_completed", "TEST")
        self.log("=" * 80)
        
        results = {
            'returns_200': False,
            'returns_jwt_token': False,
            'returns_user_with_profile_completed_true': False,
            'all_profile_fields_present': False
        }
        
        if not self.test_user_email:
            self.log("⚠️ Skipping test - no test user created", "WARNING")
            return results
        
        self.log(f"\n🔐 Logging in with: {self.test_user_email}")
        
        success, response, status, elapsed = self.run_test(
            "Login User",
            "POST",
            "auth/login",
            200,
            data={
                "email": self.test_user_email,
                "password": "TestPassword123!"
            }
        )
        
        if success:
            results['returns_200'] = True
            self.log(f"✅ Login successful: {status} ({elapsed:.2f}s)", "SUCCESS")
            
            # Check JWT token
            if 'token' in response and response['token']:
                results['returns_jwt_token'] = True
                self.log(f"✅ JWT token returned", "SUCCESS")
            else:
                self.log("❌ JWT token NOT returned", "FAIL")
            
            # Check user object
            if 'user' in response:
                user = response['user']
                self.log(f"\n📊 Login response user object:")
                self.log(f"   - user_id: {user.get('user_id')}")
                self.log(f"   - full_name: {user.get('full_name')}")
                self.log(f"   - email: {user.get('email')}")
                self.log(f"   - exam_type: {user.get('exam_type')}")
                self.log(f"   - profile_completed: {user.get('profile_completed')}")
                self.log(f"   - subscription_type: {user.get('subscription_type')}")
                
                # Check profile_completed
                if user.get('profile_completed') == True:
                    results['returns_user_with_profile_completed_true'] = True
                    self.log("✅ profile_completed = True in login response", "SUCCESS")
                else:
                    self.log(f"❌ profile_completed = {user.get('profile_completed')}", "FAIL")
                
                # Check all profile fields present
                if (user.get('exam_type') and 
                    user.get('subscription_type') is not None):
                    results['all_profile_fields_present'] = True
                    self.log("✅ All essential profile fields present", "SUCCESS")
                else:
                    self.log("❌ Some profile fields missing", "FAIL")
            else:
                self.log("❌ User object NOT returned", "FAIL")
        else:
            self.log(f"❌ Login failed: {status} - {response}", "FAIL")
        
        return results
    
    # ============= TEST 3: Verify Existing User Migration =============
    
    def test_existing_user_migration(self):
        """Test 3: Verify Existing User Migration"""
        self.log("\n" + "=" * 80)
        self.log("TEST 3: Verify Existing User Migration", "TEST")
        self.log("=" * 80)
        
        results = {
            'testneuro_user_has_profile_completed': False,
            'test_user_has_profile_completed': False,
            'users_with_profile_completed_count': 0
        }
        
        # Test with known existing users
        test_users = [
            {"email": "testneuro@dhruvai.com", "password": "TestNeuro123!"},
            {"email": "test@dhruvai.com", "password": "password123"}
        ]
        
        self.log("\n🔍 Checking existing users for profile_completed field...")
        
        for test_user in test_users:
            self.log(f"\n   Testing user: {test_user['email']}")
            success, response, status, elapsed = self.run_test(
                f"Login {test_user['email']}",
                "POST",
                "auth/login",
                [200, 401],
                data=test_user
            )
            
            if success and status == 200:
                if 'user' in response:
                    user = response['user']
                    profile_completed = user.get('profile_completed')
                    exam_type = user.get('exam_type')
                    
                    self.log(f"   ✅ User found: profile_completed={profile_completed}, exam_type={exam_type}")
                    
                    if profile_completed == True:
                        results['users_with_profile_completed_count'] += 1
                        if test_user['email'] == "testneuro@dhruvai.com":
                            results['testneuro_user_has_profile_completed'] = True
                        elif test_user['email'] == "test@dhruvai.com":
                            results['test_user_has_profile_completed'] = True
                    else:
                        self.log(f"   ⚠️ User has profile_completed={profile_completed}", "WARNING")
            elif status == 401:
                self.log(f"   ⚠️ User not found or invalid credentials", "WARNING")
            else:
                self.log(f"   ❌ Error checking user: {status}", "FAIL")
        
        self.log(f"\n📊 Total existing users with profile_completed=True: {results['users_with_profile_completed_count']}")
        
        return results
    
    # ============= TEST 4: Profile Complete Endpoint =============
    
    def test_profile_complete_endpoint(self):
        """Test 4: Profile Complete Endpoint (for OAuth users)"""
        self.log("\n" + "=" * 80)
        self.log("TEST 4: Profile Complete Endpoint (for OAuth users)", "TEST")
        self.log("=" * 80)
        
        results = {
            'endpoint_accessible': False,
            'returns_200': False,
            'sets_profile_completed_true': False,
            'returns_updated_user': False
        }
        
        # Note: This endpoint requires OAuth authentication
        # We'll test with JWT token from email/password registration
        
        if not self.test_user_token:
            self.log("⚠️ Skipping test - no JWT token available", "WARNING")
            self.log("   (This endpoint is primarily for OAuth users)")
            return results
        
        self.log("\n📝 Testing profile complete endpoint...")
        self.log("   Note: Using JWT token from email/password registration")
        
        test_data = {
            "exam_type": "NEET",
            "target_year": 2026,
            "grade": "11"
        }
        
        success, response, status, elapsed = self.run_test(
            "Complete Profile",
            "POST",
            "auth/profile/complete",
            [200, 401],
            data=test_data,
            headers={"Authorization": f"Bearer {self.test_user_token}"}
        )
        
        if success:
            results['endpoint_accessible'] = True
            self.log(f"✅ Endpoint accessible: {status}", "SUCCESS")
            
            if status == 200:
                results['returns_200'] = True
                self.log("✅ Returns 200 OK", "SUCCESS")
                
                if 'user' in response:
                    user = response['user']
                    results['returns_updated_user'] = True
                    self.log("✅ Returns updated user object", "SUCCESS")
                    
                    if user.get('profile_completed') == True:
                        results['sets_profile_completed_true'] = True
                        self.log("✅ Sets profile_completed = True", "SUCCESS")
                    else:
                        self.log(f"❌ profile_completed = {user.get('profile_completed')}", "FAIL")
                    
                    self.log(f"\n📊 Updated user:")
                    self.log(f"   - exam_type: {user.get('exam_type')}")
                    self.log(f"   - target_year: {user.get('target_year')}")
                    self.log(f"   - profile_completed: {user.get('profile_completed')}")
            elif status == 401:
                self.log("⚠️ Authentication required (expected for OAuth-only endpoint)", "WARNING")
        else:
            self.log(f"❌ Endpoint failed: {status} - {response}", "FAIL")
        
        return results
    
    # ============= TEST 5: Email Signup Does NOT Go to Profile Setup =============
    
    def test_email_signup_no_profile_setup(self):
        """Test 5: Verify Email Signup Does NOT Go to Profile Setup"""
        self.log("\n" + "=" * 80)
        self.log("TEST 5: Email Signup Does NOT Go to Profile Setup", "TEST")
        self.log("=" * 80)
        
        results = {
            'profile_completed_true_immediately': False,
            'no_profile_setup_needed': False
        }
        
        # Create another test user
        new_email = self.generate_test_email()
        
        test_data = {
            "full_name": "No Profile Setup Test",
            "email": new_email,
            "password": "TestPassword123!",
            "exam_type": "JEE",
            "grade": "11",
            "target_year": 2025
        }
        
        self.log(f"\n📝 Registering new user: {new_email}")
        
        success, response, status, elapsed = self.run_test(
            "Register New User",
            "POST",
            "auth/register",
            [200, 201],
            data=test_data
        )
        
        if success and 'user' in response:
            user = response['user']
            
            # Check profile_completed immediately after registration
            if user.get('profile_completed') == True:
                results['profile_completed_true_immediately'] = True
                results['no_profile_setup_needed'] = True
                self.log("✅ profile_completed = True immediately after registration", "SUCCESS")
                self.log("✅ No profile setup step needed", "SUCCESS")
            else:
                self.log(f"❌ profile_completed = {user.get('profile_completed')} (expected True)", "FAIL")
                self.log("❌ User would be redirected to profile setup", "FAIL")
            
            self.log(f"\n📊 Registration response:")
            self.log(f"   - profile_completed: {user.get('profile_completed')}")
            self.log(f"   - exam_type: {user.get('exam_type')}")
            self.log(f"   - grade: {user.get('grade')}")
            self.log(f"   - target_year: {user.get('target_year')}")
        else:
            self.log(f"❌ Registration failed: {status}", "FAIL")
        
        return results
    
    # ============= TEST 6: Check Login Response Structure =============
    
    def test_login_response_structure(self):
        """Test 6: Check Login Response Structure"""
        self.log("\n" + "=" * 80)
        self.log("TEST 6: Check Login Response Structure", "TEST")
        self.log("=" * 80)
        
        results = {
            'has_profile_completed_field': False,
            'has_subscription_type_field': False,
            'has_exam_type_field': False,
            'has_all_essential_fields': False
        }
        
        if not self.test_user_email:
            self.log("⚠️ Skipping test - no test user available", "WARNING")
            return results
        
        self.log(f"\n🔐 Logging in to check response structure: {self.test_user_email}")
        
        success, response, status, elapsed = self.run_test(
            "Login for Structure Check",
            "POST",
            "auth/login",
            200,
            data={
                "email": self.test_user_email,
                "password": "TestPassword123!"
            }
        )
        
        if success and 'user' in response:
            user = response['user']
            
            self.log("\n📊 Login response structure:")
            
            # Check profile_completed field
            if 'profile_completed' in user:
                results['has_profile_completed_field'] = True
                self.log(f"   ✅ profile_completed: {user['profile_completed']} (boolean)", "SUCCESS")
            else:
                self.log("   ❌ profile_completed: MISSING", "FAIL")
            
            # Check subscription_type field
            if 'subscription_type' in user:
                results['has_subscription_type_field'] = True
                self.log(f"   ✅ subscription_type: {user['subscription_type']}", "SUCCESS")
            else:
                self.log("   ❌ subscription_type: MISSING", "FAIL")
            
            # Check exam_type field
            if 'exam_type' in user:
                results['has_exam_type_field'] = True
                self.log(f"   ✅ exam_type: {user['exam_type']}", "SUCCESS")
            else:
                self.log("   ❌ exam_type: MISSING", "FAIL")
            
            # Check all essential fields
            essential_fields = ['user_id', 'full_name', 'email', 'profile_completed', 
                              'subscription_type', 'exam_type']
            missing_fields = [f for f in essential_fields if f not in user]
            
            if not missing_fields:
                results['has_all_essential_fields'] = True
                self.log("\n   ✅ All essential fields present", "SUCCESS")
            else:
                self.log(f"\n   ❌ Missing fields: {missing_fields}", "FAIL")
            
            # Print all fields
            self.log("\n   📋 All fields in response:")
            for key, value in user.items():
                self.log(f"      - {key}: {value}")
        else:
            self.log(f"❌ Login failed: {status}", "FAIL")
        
        return results
    
    # ============= MAIN TEST RUNNER =============
    
    def run_all_tests(self):
        """Run all onboarding backend tests"""
        self.log("\n" + "=" * 80)
        self.log("🚀 ONBOARDING FIX VALIDATION - BACKEND TESTING")
        self.log("=" * 80)
        self.log(f"Backend URL: {self.base_url}")
        self.log(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_results = {}
        
        # Run all test suites
        all_results['test_1_registration'] = self.test_registration_with_profile()
        all_results['test_2_login'] = self.test_login_returns_profile_completed()
        all_results['test_3_migration'] = self.test_existing_user_migration()
        all_results['test_4_profile_complete'] = self.test_profile_complete_endpoint()
        all_results['test_5_no_profile_setup'] = self.test_email_signup_no_profile_setup()
        all_results['test_6_response_structure'] = self.test_login_response_structure()
        
        # Print final summary
        self.print_final_summary(all_results)
        
        return all_results
    
    def print_final_summary(self, all_results):
        """Print final test summary"""
        self.log("\n" + "=" * 80)
        self.log("📊 FINAL TEST SUMMARY - ONBOARDING FIX VALIDATION")
        self.log("=" * 80)
        
        total_tests = 0
        passed_tests = 0
        
        test_names = {
            'test_1_registration': 'Test 1: Email/Password Registration with Profile Fields',
            'test_2_login': 'Test 2: Email/Password Login Returns profile_completed',
            'test_3_migration': 'Test 3: Verify Existing User Migration',
            'test_4_profile_complete': 'Test 4: Profile Complete Endpoint',
            'test_5_no_profile_setup': 'Test 5: Email Signup Does NOT Go to Profile Setup',
            'test_6_response_structure': 'Test 6: Check Login Response Structure'
        }
        
        for test_key, results in all_results.items():
            test_name = test_names.get(test_key, test_key)
            category_total = len(results)
            category_passed = sum(1 for v in results.values() if v == True)
            total_tests += category_total
            passed_tests += category_passed
            
            self.log(f"\n{test_name}:")
            self.log(f"   Passed: {category_passed}/{category_total}")
            
            for check_name, passed in results.items():
                status = "✅" if passed else "❌"
                self.log(f"   {status} {check_name.replace('_', ' ').title()}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.log("\n" + "=" * 80)
        self.log(f"OVERALL RESULTS: {passed_tests}/{total_tests} checks passed ({success_rate:.1f}%)")
        self.log("=" * 80)
        
        if success_rate >= 90:
            self.log("✅ EXCELLENT: Onboarding fix is working correctly!", "SUCCESS")
        elif success_rate >= 75:
            self.log("⚠️ GOOD: Onboarding mostly working, minor issues to address", "WARNING")
        elif success_rate >= 60:
            self.log("⚠️ PARTIAL: Onboarding has some issues that need attention", "WARNING")
        else:
            self.log("❌ CRITICAL: Onboarding has major issues that must be fixed", "FAIL")
        
        self.log(f"\nTest End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Success criteria check
        self.log("\n" + "=" * 80)
        self.log("🎯 SUCCESS CRITERIA CHECK")
        self.log("=" * 80)
        
        criteria = [
            ("New email signups have profile_completed: true", 
             all_results['test_1_registration'].get('returns_user_with_profile_completed_true', False)),
            ("Login responses include profile_completed", 
             all_results['test_2_login'].get('returns_user_with_profile_completed_true', False)),
            ("Email signup does NOT require profile setup", 
             all_results['test_5_no_profile_setup'].get('no_profile_setup_needed', False)),
            ("Login response has all essential fields", 
             all_results['test_6_response_structure'].get('has_all_essential_fields', False))
        ]
        
        all_criteria_met = True
        for criterion, met in criteria:
            status = "✅" if met else "❌"
            self.log(f"{status} {criterion}")
            if not met:
                all_criteria_met = False
        
        if all_criteria_met:
            self.log("\n✅ ALL SUCCESS CRITERIA MET!", "SUCCESS")
        else:
            self.log("\n❌ SOME SUCCESS CRITERIA NOT MET", "FAIL")


if __name__ == "__main__":
    tester = OnboardingBackendTester()
    results = tester.run_all_tests()
