#!/usr/bin/env python3
"""
Email/Password Authentication Flow Testing
Testing registration, login, invalid credentials, and session validation
"""

import requests
import json
import time
from datetime import datetime
import random
import string

class EmailAuthTester:
    def __init__(self):
        self.base_url = "https://neuro-tutor-dev.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = {}
        self.jwt_token = None
        self.test_user_email = None
        self.test_user_password = "test123456"
    
    def log(self, message, level="INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def generate_unique_email(self):
        """Generate unique email for testing"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"teststudent_{random_suffix}@test.com"
    
    def test_user_registration(self):
        """Test 1: User Registration (Email/Password)"""
        self.log("=" * 80)
        self.log("🔐 TEST 1: USER REGISTRATION (EMAIL/PASSWORD)")
        self.log("=" * 80)
        
        # Generate unique email
        self.test_user_email = self.generate_unique_email()
        
        registration_data = {
            "full_name": "Test Student",
            "email": self.test_user_email,
            "password": self.test_user_password,
            "exam_type": "JEE",
            "target_year": 2026,
            "grade": None
        }
        
        self.log(f"\n📧 Registering user: {self.test_user_email}")
        self.log(f"📊 Registration data: {json.dumps({k: v for k, v in registration_data.items() if k != 'password'}, indent=2)}")
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=registration_data,
                timeout=10
            )
            elapsed_time = time.time() - start_time
            
            self.log(f"\n⏱️ Response time: {elapsed_time:.2f}s")
            self.log(f"📊 Status code: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                self.log(f"✅ Registration successful!")
                self.log(f"📊 Response: {json.dumps(response_data, indent=2)}")
                
                # Validate response structure
                checks = {
                    'has_message': 'message' in response_data,
                    'has_token': 'token' in response_data,
                    'has_user': 'user' in response_data,
                    'token_not_empty': response_data.get('token', '') != '',
                    'user_has_user_id': 'user_id' in response_data.get('user', {}),
                    'user_has_full_name': 'full_name' in response_data.get('user', {}),
                    'user_has_email': 'email' in response_data.get('user', {}),
                    'user_has_exam_type': 'exam_type' in response_data.get('user', {}),
                }
                
                self.log("\n🔍 Response Validation:")
                for check_name, check_result in checks.items():
                    status = "✅" if check_result else "❌"
                    self.log(f"   {status} {check_name.replace('_', ' ').title()}")
                
                # Store token for later tests
                if response_data.get('token'):
                    self.jwt_token = response_data['token']
                    self.log(f"\n🔑 JWT Token stored: {self.jwt_token[:30]}...")
                
                all_checks_passed = all(checks.values())
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'response_time': elapsed_time,
                    'all_checks_passed': all_checks_passed,
                    'checks': checks
                }
            
            elif response.status_code == 403:
                self.log(f"❌ CSRF Error (403 Forbidden)")
                self.log(f"📊 Response: {response.text}")
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': 'CSRF protection blocking registration',
                    'response': response.text
                }
            
            elif response.status_code == 500:
                self.log(f"❌ Internal Server Error (500)")
                try:
                    error_data = response.json()
                    self.log(f"📊 Error: {json.dumps(error_data, indent=2)}")
                except:
                    self.log(f"📊 Error: {response.text}")
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': 'Internal server error'
                }
            
            else:
                self.log(f"❌ Unexpected status code: {response.status_code}")
                self.log(f"📊 Response: {response.text}")
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': f'Unexpected status code: {response.status_code}'
                }
        
        except Exception as e:
            self.log(f"❌ Exception during registration: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_user_login(self):
        """Test 2: User Login (Email/Password)"""
        self.log("\n" + "=" * 80)
        self.log("🔐 TEST 2: USER LOGIN (EMAIL/PASSWORD)")
        self.log("=" * 80)
        
        if not self.test_user_email:
            self.log("❌ Cannot test login: No registered user email")
            return {'success': False, 'error': 'No registered user'}
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        self.log(f"\n📧 Logging in user: {self.test_user_email}")
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                timeout=10
            )
            elapsed_time = time.time() - start_time
            
            self.log(f"\n⏱️ Response time: {elapsed_time:.2f}s")
            self.log(f"📊 Status code: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                self.log(f"✅ Login successful!")
                self.log(f"📊 Response: {json.dumps(response_data, indent=2)}")
                
                # Validate response structure
                checks = {
                    'has_message': 'message' in response_data,
                    'has_token': 'token' in response_data,
                    'has_user': 'user' in response_data,
                    'token_not_empty': response_data.get('token', '') != '',
                    'message_correct': response_data.get('message') == 'Login successful',
                }
                
                self.log("\n🔍 Response Validation:")
                for check_name, check_result in checks.items():
                    status = "✅" if check_result else "❌"
                    self.log(f"   {status} {check_name.replace('_', ' ').title()}")
                
                # Update token if different from registration
                if response_data.get('token'):
                    self.jwt_token = response_data['token']
                    self.log(f"\n🔑 JWT Token updated: {self.jwt_token[:30]}...")
                
                all_checks_passed = all(checks.values())
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'response_time': elapsed_time,
                    'all_checks_passed': all_checks_passed,
                    'checks': checks
                }
            
            elif response.status_code == 401:
                self.log(f"❌ Unauthorized (401) - Invalid credentials")
                self.log(f"📊 Response: {response.text}")
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': 'Invalid credentials'
                }
            
            elif response.status_code == 403:
                self.log(f"❌ CSRF Error (403 Forbidden)")
                self.log(f"📊 Response: {response.text}")
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': 'CSRF protection blocking login',
                    'response': response.text
                }
            
            elif response.status_code == 500:
                self.log(f"❌ Internal Server Error (500)")
                try:
                    error_data = response.json()
                    self.log(f"📊 Error: {json.dumps(error_data, indent=2)}")
                except:
                    self.log(f"📊 Error: {response.text}")
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': 'Internal server error',
                    'response': response.text
                }
            
            else:
                self.log(f"❌ Unexpected status code: {response.status_code}")
                self.log(f"📊 Response: {response.text}")
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': f'Unexpected status code: {response.status_code}'
                }
        
        except Exception as e:
            self.log(f"❌ Exception during login: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_invalid_login(self):
        """Test 3: Invalid Login Attempts"""
        self.log("\n" + "=" * 80)
        self.log("🔐 TEST 3: INVALID LOGIN ATTEMPTS")
        self.log("=" * 80)
        
        test_cases = [
            {
                "name": "Nonexistent email",
                "email": "nonexistent@test.com",
                "password": "wrongpassword"
            },
            {
                "name": "Wrong password",
                "email": self.test_user_email if self.test_user_email else "test@test.com",
                "password": "wrongpassword123"
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            self.log(f"\n🧪 Testing: {test_case['name']}")
            self.log(f"📧 Email: {test_case['email']}")
            
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{self.base_url}/auth/login",
                    json={
                        "email": test_case['email'],
                        "password": test_case['password']
                    },
                    timeout=10
                )
                elapsed_time = time.time() - start_time
                
                self.log(f"⏱️ Response time: {elapsed_time:.2f}s")
                self.log(f"📊 Status code: {response.status_code}")
                
                if response.status_code == 401:
                    try:
                        error_data = response.json()
                        detail = error_data.get('detail', '')
                        self.log(f"✅ Correctly returned 401 Unauthorized")
                        self.log(f"📊 Error detail: {detail}")
                        
                        # Check if error message is correct
                        expected_message = "Invalid email or password"
                        message_correct = detail == expected_message
                        
                        if message_correct:
                            self.log(f"✅ Error message correct: '{expected_message}'")
                        else:
                            self.log(f"⚠️ Error message: '{detail}' (expected: '{expected_message}')")
                        
                        results.append({
                            'test_case': test_case['name'],
                            'success': True,
                            'status_code': response.status_code,
                            'message_correct': message_correct
                        })
                    except:
                        self.log(f"✅ Correctly returned 401 Unauthorized")
                        self.log(f"📊 Response: {response.text}")
                        results.append({
                            'test_case': test_case['name'],
                            'success': True,
                            'status_code': response.status_code,
                            'message_correct': False
                        })
                
                elif response.status_code == 500:
                    self.log(f"❌ Internal Server Error (500) - Should return 401")
                    try:
                        error_data = response.json()
                        self.log(f"📊 Error: {json.dumps(error_data, indent=2)}")
                    except:
                        self.log(f"📊 Error: {response.text}")
                    results.append({
                        'test_case': test_case['name'],
                        'success': False,
                        'status_code': response.status_code,
                        'error': 'Internal server error instead of 401'
                    })
                
                else:
                    self.log(f"❌ Unexpected status code: {response.status_code} (expected 401)")
                    self.log(f"📊 Response: {response.text}")
                    results.append({
                        'test_case': test_case['name'],
                        'success': False,
                        'status_code': response.status_code,
                        'error': f'Expected 401, got {response.status_code}'
                    })
            
            except Exception as e:
                self.log(f"❌ Exception: {str(e)}")
                results.append({
                    'test_case': test_case['name'],
                    'success': False,
                    'error': str(e)
                })
        
        all_passed = all(r.get('success', False) for r in results)
        return {
            'success': all_passed,
            'test_cases': results
        }
    
    def test_session_check(self):
        """Test 4: Session Check with Token"""
        self.log("\n" + "=" * 80)
        self.log("🔐 TEST 4: SESSION CHECK WITH TOKEN")
        self.log("=" * 80)
        
        if not self.jwt_token:
            self.log("❌ Cannot test session: No JWT token available")
            return {'success': False, 'error': 'No JWT token'}
        
        self.log(f"\n🔑 Using JWT token: {self.jwt_token[:30]}...")
        
        try:
            start_time = time.time()
            response = self.session.get(
                f"{self.base_url}/auth/session",
                headers={
                    'Authorization': f'Bearer {self.jwt_token}'
                },
                timeout=10
            )
            elapsed_time = time.time() - start_time
            
            self.log(f"\n⏱️ Response time: {elapsed_time:.2f}s")
            self.log(f"📊 Status code: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                self.log(f"✅ Session check successful!")
                self.log(f"📊 Response: {json.dumps(response_data, indent=2)}")
                
                # Validate response has user data
                has_user_data = 'user' in response_data or 'user_id' in response_data or 'email' in response_data
                
                if has_user_data:
                    self.log(f"✅ Session contains user data")
                else:
                    self.log(f"⚠️ Session response structure unexpected")
                
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'response_time': elapsed_time,
                    'has_user_data': has_user_data
                }
            
            elif response.status_code == 401:
                self.log(f"❌ Unauthorized (401) - Token invalid or expired")
                self.log(f"📊 Response: {response.text}")
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': 'Token invalid or expired'
                }
            
            else:
                self.log(f"❌ Unexpected status code: {response.status_code}")
                self.log(f"📊 Response: {response.text}")
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': f'Unexpected status code: {response.status_code}'
                }
        
        except Exception as e:
            self.log(f"❌ Exception during session check: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_all_tests(self):
        """Run all email/password authentication tests"""
        self.log("\n" + "=" * 80)
        self.log("🚀 EMAIL/PASSWORD AUTHENTICATION FLOW TESTING")
        self.log("=" * 80)
        self.log(f"Backend URL: {self.base_url}")
        self.log(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_results = {}
        
        # Test 1: Registration
        all_results['registration'] = self.test_user_registration()
        
        # Test 2: Login (only if registration succeeded)
        if all_results['registration'].get('success'):
            all_results['login'] = self.test_user_login()
        else:
            self.log("\n⚠️ Skipping login test - registration failed")
            all_results['login'] = {'success': False, 'error': 'Registration failed, skipped'}
        
        # Test 3: Invalid login attempts
        all_results['invalid_login'] = self.test_invalid_login()
        
        # Test 4: Session check (only if we have a token)
        if self.jwt_token:
            all_results['session_check'] = self.test_session_check()
        else:
            self.log("\n⚠️ Skipping session check - no JWT token available")
            all_results['session_check'] = {'success': False, 'error': 'No JWT token, skipped'}
        
        # Print final summary
        self.print_final_summary(all_results)
        
        return all_results
    
    def print_final_summary(self, all_results):
        """Print final test summary"""
        self.log("\n" + "=" * 80)
        self.log("📊 FINAL TEST SUMMARY - EMAIL/PASSWORD AUTHENTICATION")
        self.log("=" * 80)
        
        test_names = {
            'registration': '1️⃣ User Registration',
            'login': '2️⃣ User Login',
            'invalid_login': '3️⃣ Invalid Login Attempts',
            'session_check': '4️⃣ Session Check with Token'
        }
        
        passed_tests = 0
        total_tests = len(all_results)
        
        for test_key, test_name in test_names.items():
            result = all_results.get(test_key, {})
            success = result.get('success', False)
            status = "✅" if success else "❌"
            
            self.log(f"\n{status} {test_name}")
            
            if success:
                passed_tests += 1
                if 'status_code' in result:
                    self.log(f"   Status: {result['status_code']}")
                if 'response_time' in result:
                    self.log(f"   Response time: {result['response_time']:.2f}s")
            else:
                if 'error' in result:
                    self.log(f"   Error: {result['error']}")
                if 'status_code' in result:
                    self.log(f"   Status: {result['status_code']}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.log("\n" + "=" * 80)
        self.log(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        self.log("=" * 80)
        
        # Specific findings
        self.log("\n🔍 KEY FINDINGS:")
        
        if all_results.get('registration', {}).get('success'):
            self.log("   ✅ Registration creates user successfully")
            if all_results['registration'].get('all_checks_passed'):
                self.log("   ✅ Registration returns valid JWT token")
        else:
            self.log("   ❌ Registration failed")
            if all_results.get('registration', {}).get('status_code') == 403:
                self.log("   ❌ CSRF errors (403) during registration")
            elif all_results.get('registration', {}).get('status_code') == 500:
                self.log("   ❌ Internal Server Error during registration")
        
        if all_results.get('login', {}).get('success'):
            self.log("   ✅ Login works with registered credentials")
            if all_results['login'].get('all_checks_passed'):
                self.log("   ✅ Login returns valid JWT token")
        else:
            self.log("   ❌ Login failed")
            if all_results.get('login', {}).get('status_code') == 403:
                self.log("   ❌ CSRF errors (403) during login")
            elif all_results.get('login', {}).get('status_code') == 500:
                self.log("   ❌ Internal Server Error during login")
        
        if all_results.get('invalid_login', {}).get('success'):
            self.log("   ✅ Invalid credentials return 401 (not 500)")
        else:
            self.log("   ❌ Invalid credentials handling failed")
        
        if all_results.get('session_check', {}).get('success'):
            self.log("   ✅ JWT token can be used for authenticated endpoints")
        else:
            self.log("   ❌ Session check with JWT token failed")
        
        # CSRF status
        csrf_errors = any(
            r.get('status_code') == 403 
            for r in all_results.values() 
            if isinstance(r, dict)
        )
        
        if not csrf_errors:
            self.log("   ✅ No CSRF errors (403) during auth")
        else:
            self.log("   ❌ CSRF errors detected during authentication")
        
        # Session expired errors
        session_errors = any(
            'Session expired or invalid' in str(r.get('error', ''))
            for r in all_results.values()
            if isinstance(r, dict)
        )
        
        if not session_errors:
            self.log("   ✅ No 'Session expired or invalid' errors")
        else:
            self.log("   ❌ 'Session expired or invalid' errors detected")
        
        self.log(f"\nTest End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Final verdict
        if success_rate == 100:
            self.log("\n✅ EXCELLENT: Email/Password authentication is fully working!")
        elif success_rate >= 75:
            self.log("\n⚠️ GOOD: Email/Password authentication mostly working, minor issues")
        elif success_rate >= 50:
            self.log("\n⚠️ PARTIAL: Email/Password authentication has issues that need attention")
        else:
            self.log("\n❌ CRITICAL: Email/Password authentication has major issues")


if __name__ == "__main__":
    tester = EmailAuthTester()
    results = tester.run_all_tests()
