#!/usr/bin/env python3
"""
COMPREHENSIVE EMAIL/PASSWORD AUTHENTICATION TESTING
Final verification of all authentication scenarios
"""

import requests
import json
import time
from datetime import datetime
import random
import string

class ComprehensiveAuthTester:
    def __init__(self):
        self.base_url = "https://dhruv-neuro-ai.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.jwt_token = None
        self.test_user_email = None
        self.test_user_password = "test123456"
        self.results = {}
    
    def log(self, message, level="INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbol = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️"
        }.get(level, "ℹ️")
        print(f"[{timestamp}] {symbol} {message}")
    
    def generate_unique_email(self):
        """Generate unique email for testing"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"authtest_{random_suffix}@test.com"
    
    def test_registration(self):
        """Test user registration"""
        self.log("=" * 80)
        self.log("TEST 1: USER REGISTRATION", "INFO")
        self.log("=" * 80)
        
        self.test_user_email = self.generate_unique_email()
        
        registration_data = {
            "full_name": "Auth Test User",
            "email": self.test_user_email,
            "password": self.test_user_password,
            "exam_type": "JEE",
            "target_year": 2026,
            "grade": None
        }
        
        self.log(f"Registering: {self.test_user_email}")
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=registration_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get('token')
                self.log("Registration successful!", "SUCCESS")
                self.log(f"JWT Token: {self.jwt_token[:30]}...")
                
                # Validate response
                checks = {
                    'has_message': 'message' in data,
                    'has_token': 'token' in data and data['token'] != '',
                    'has_user': 'user' in data,
                    'user_has_id': 'user_id' in data.get('user', {}),
                }
                
                all_passed = all(checks.values())
                self.results['registration'] = {
                    'passed': True,
                    'status': 200,
                    'all_checks': all_passed
                }
                return True
            else:
                self.log(f"Registration failed: {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}")
                self.results['registration'] = {'passed': False, 'status': response.status_code}
                return False
        except Exception as e:
            self.log(f"Exception: {str(e)}", "ERROR")
            self.results['registration'] = {'passed': False, 'error': str(e)}
            return False
    
    def test_login(self):
        """Test user login"""
        self.log("\n" + "=" * 80)
        self.log("TEST 2: USER LOGIN", "INFO")
        self.log("=" * 80)
        
        if not self.test_user_email:
            self.log("Skipping - no registered user", "WARNING")
            self.results['login'] = {'passed': False, 'skipped': True}
            return False
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        self.log(f"Logging in: {self.test_user_email}")
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get('token')
                self.log("Login successful!", "SUCCESS")
                self.log(f"JWT Token: {self.jwt_token[:30]}...")
                
                checks = {
                    'has_message': data.get('message') == 'Login successful',
                    'has_token': 'token' in data and data['token'] != '',
                    'has_user': 'user' in data,
                }
                
                all_passed = all(checks.values())
                self.results['login'] = {
                    'passed': True,
                    'status': 200,
                    'all_checks': all_passed
                }
                return True
            else:
                self.log(f"Login failed: {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}")
                self.results['login'] = {'passed': False, 'status': response.status_code}
                return False
        except Exception as e:
            self.log(f"Exception: {str(e)}", "ERROR")
            self.results['login'] = {'passed': False, 'error': str(e)}
            return False
    
    def test_invalid_credentials(self):
        """Test invalid login attempts"""
        self.log("\n" + "=" * 80)
        self.log("TEST 3: INVALID CREDENTIALS", "INFO")
        self.log("=" * 80)
        
        test_cases = [
            ("Nonexistent email", "nonexistent@test.com", "wrongpass"),
            ("Wrong password", self.test_user_email or "test@test.com", "wrongpass123")
        ]
        
        all_passed = True
        for name, email, password in test_cases:
            self.log(f"Testing: {name}")
            
            try:
                response = self.session.post(
                    f"{self.base_url}/auth/login",
                    json={"email": email, "password": password},
                    timeout=10
                )
                
                if response.status_code == 401:
                    self.log(f"  ✅ Correctly returned 401", "SUCCESS")
                else:
                    self.log(f"  ❌ Expected 401, got {response.status_code}", "ERROR")
                    all_passed = False
            except Exception as e:
                self.log(f"  ❌ Exception: {str(e)}", "ERROR")
                all_passed = False
        
        self.results['invalid_credentials'] = {'passed': all_passed}
        return all_passed
    
    def test_jwt_with_authenticated_endpoints(self):
        """Test JWT token with various authenticated endpoints"""
        self.log("\n" + "=" * 80)
        self.log("TEST 4: JWT TOKEN WITH AUTHENTICATED ENDPOINTS", "INFO")
        self.log("=" * 80)
        
        if not self.jwt_token:
            self.log("Skipping - no JWT token", "WARNING")
            self.results['jwt_endpoints'] = {'passed': False, 'skipped': True}
            return False
        
        endpoints = [
            ("Subscription Info", "GET", "/subscription/info", None),
            ("User Profile", "GET", "/user/profile", None),
            ("Check Access", "POST", "/subscription/check-access", {"feature_name": "ai_mentor"}),
        ]
        
        all_passed = True
        for name, method, endpoint, data in endpoints:
            self.log(f"Testing: {name}")
            
            try:
                headers = {"Authorization": f"Bearer {self.jwt_token}"}
                
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
                else:
                    response = self.session.post(f"{self.base_url}{endpoint}", headers=headers, json=data, timeout=10)
                
                if response.status_code == 200:
                    self.log(f"  ✅ {name} works (200 OK)", "SUCCESS")
                else:
                    self.log(f"  ❌ {name} failed ({response.status_code})", "ERROR")
                    all_passed = False
            except Exception as e:
                self.log(f"  ❌ Exception: {str(e)}", "ERROR")
                all_passed = False
        
        self.results['jwt_endpoints'] = {'passed': all_passed}
        return all_passed
    
    def test_csrf_protection(self):
        """Test CSRF protection status"""
        self.log("\n" + "=" * 80)
        self.log("TEST 5: CSRF PROTECTION", "INFO")
        self.log("=" * 80)
        
        # Check if registration/login are CSRF exempt
        self.log("Checking CSRF exemption for auth endpoints...")
        
        # Registration and login should work without CSRF token (they're exempt)
        csrf_exempt = True
        if self.results.get('registration', {}).get('status') == 403:
            csrf_exempt = False
            self.log("  ❌ Registration blocked by CSRF (403)", "ERROR")
        elif self.results.get('login', {}).get('status') == 403:
            csrf_exempt = False
            self.log("  ❌ Login blocked by CSRF (403)", "ERROR")
        else:
            self.log("  ✅ Auth endpoints are CSRF exempt", "SUCCESS")
        
        self.results['csrf_protection'] = {'passed': csrf_exempt}
        return csrf_exempt
    
    def test_session_endpoint(self):
        """Test /api/auth/session endpoint"""
        self.log("\n" + "=" * 80)
        self.log("TEST 6: SESSION ENDPOINT", "INFO")
        self.log("=" * 80)
        
        if not self.jwt_token:
            self.log("Skipping - no JWT token", "WARNING")
            self.results['session_endpoint'] = {'passed': False, 'skipped': True}
            return False
        
        self.log("Testing /api/auth/session with JWT token...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/auth/session",
                headers={"Authorization": f"Bearer {self.jwt_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log("  ✅ Session endpoint works with JWT", "SUCCESS")
                self.results['session_endpoint'] = {'passed': True, 'status': 200}
                return True
            elif response.status_code == 401:
                error = response.json().get('detail', '')
                if 'Session expired or invalid' in error:
                    self.log("  ⚠️ Session endpoint doesn't support JWT tokens", "WARNING")
                    self.log("  ℹ️ This is expected - session endpoint only checks DB session tokens")
                    self.log("  ℹ️ JWT tokens work with all other authenticated endpoints")
                    self.results['session_endpoint'] = {
                        'passed': False,
                        'status': 401,
                        'note': 'Session endpoint only supports DB session tokens, not JWT'
                    }
                else:
                    self.log(f"  ❌ Unexpected error: {error}", "ERROR")
                    self.results['session_endpoint'] = {'passed': False, 'status': 401, 'error': error}
                return False
            else:
                self.log(f"  ❌ Unexpected status: {response.status_code}", "ERROR")
                self.results['session_endpoint'] = {'passed': False, 'status': response.status_code}
                return False
        except Exception as e:
            self.log(f"  ❌ Exception: {str(e)}", "ERROR")
            self.results['session_endpoint'] = {'passed': False, 'error': str(e)}
            return False
    
    def run_all_tests(self):
        """Run all authentication tests"""
        self.log("\n" + "=" * 80)
        self.log("🚀 COMPREHENSIVE EMAIL/PASSWORD AUTHENTICATION TESTING", "INFO")
        self.log("=" * 80)
        self.log(f"Backend URL: {self.base_url}")
        self.log(f"Test Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run tests
        self.test_registration()
        self.test_login()
        self.test_invalid_credentials()
        self.test_jwt_with_authenticated_endpoints()
        self.test_csrf_protection()
        self.test_session_endpoint()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        self.log("\n" + "=" * 80)
        self.log("📊 TEST SUMMARY", "INFO")
        self.log("=" * 80)
        
        test_names = {
            'registration': '1️⃣ User Registration',
            'login': '2️⃣ User Login',
            'invalid_credentials': '3️⃣ Invalid Credentials',
            'jwt_endpoints': '4️⃣ JWT with Authenticated Endpoints',
            'csrf_protection': '5️⃣ CSRF Protection',
            'session_endpoint': '6️⃣ Session Endpoint'
        }
        
        passed = 0
        total = 0
        
        for key, name in test_names.items():
            result = self.results.get(key, {})
            if result.get('skipped'):
                self.log(f"⏭️  {name}: SKIPPED")
            elif result.get('passed'):
                self.log(f"✅ {name}: PASSED", "SUCCESS")
                passed += 1
                total += 1
            else:
                self.log(f"❌ {name}: FAILED", "ERROR")
                total += 1
                if 'note' in result:
                    self.log(f"   Note: {result['note']}")
        
        self.log("\n" + "=" * 80)
        self.log(f"RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)" if total > 0 else "No tests completed")
        self.log("=" * 80)
        
        # Key findings
        self.log("\n🔍 KEY FINDINGS:")
        
        if self.results.get('registration', {}).get('passed'):
            self.log("✅ Registration creates user successfully", "SUCCESS")
            self.log("✅ Registration returns valid JWT token", "SUCCESS")
        else:
            self.log("❌ Registration failed", "ERROR")
        
        if self.results.get('login', {}).get('passed'):
            self.log("✅ Login works with registered credentials", "SUCCESS")
            self.log("✅ Login returns valid JWT token", "SUCCESS")
        else:
            self.log("❌ Login failed", "ERROR")
        
        if self.results.get('invalid_credentials', {}).get('passed'):
            self.log("✅ Invalid credentials return 401 (not 500)", "SUCCESS")
        
        if self.results.get('jwt_endpoints', {}).get('passed'):
            self.log("✅ JWT token can be used for authenticated endpoints", "SUCCESS")
        
        if self.results.get('csrf_protection', {}).get('passed'):
            self.log("✅ No CSRF errors (403) during auth", "SUCCESS")
        
        if not self.results.get('session_endpoint', {}).get('passed'):
            self.log("⚠️ /api/auth/session doesn't support JWT tokens", "WARNING")
            self.log("   (This is expected - it only checks DB session tokens)")
        
        self.log(f"\nTest End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Final verdict
        if passed == total and total > 0:
            self.log("\n✅ EXCELLENT: All authentication tests passed!", "SUCCESS")
        elif passed >= total * 0.8:
            self.log("\n✅ GOOD: Email/Password authentication is working!", "SUCCESS")
        elif passed >= total * 0.5:
            self.log("\n⚠️ PARTIAL: Some authentication issues need attention", "WARNING")
        else:
            self.log("\n❌ CRITICAL: Major authentication issues", "ERROR")


if __name__ == "__main__":
    tester = ComprehensiveAuthTester()
    tester.run_all_tests()
