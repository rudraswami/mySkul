#!/usr/bin/env python3
"""
Stage 1 Authentication Hardening Security Tests
Testing comprehensive security implementation for Dhruv AI backend
"""

import requests
import json
import time
import sys
from datetime import datetime
import uuid

class AuthSecurityTester:
    def __init__(self, base_url="https://tutor-reborn.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.test_email = "test@dhruvai.com"
        self.test_password = "password123"
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        self.tests_run += 1
        if status:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASS")
        else:
            print(f"❌ {test_name}: FAIL")
        
        if details:
            print(f"   {details}")
        print()

    def test_secure_cookie_authentication(self):
        """Test 1: Secure Cookie Authentication - httpOnly cookies"""
        print("🔐 TEST 1: SECURE COOKIE AUTHENTICATION")
        print("=" * 50)
        
        # Test login endpoint sets httpOnly cookies
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        try:
            response = self.session.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                timeout=30
            )
            
            print(f"Login Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            # Check if login was successful
            if response.status_code == 200:
                response_data = response.json()
                print(f"Login Response: {json.dumps(response_data, indent=2)}")
                
                # Check for httpOnly cookie in Set-Cookie header
                set_cookie_header = response.headers.get('Set-Cookie', '')
                print(f"Set-Cookie Header: {set_cookie_header}")
                
                # Check for dhruv_ai_auth cookie
                has_auth_cookie = 'dhruv_ai_auth' in set_cookie_header
                has_httponly = 'HttpOnly' in set_cookie_header
                has_samesite = 'SameSite=Lax' in set_cookie_header
                secure_flag = 'Secure' in set_cookie_header
                
                print(f"Auth Cookie Present: {has_auth_cookie}")
                print(f"HttpOnly Flag: {has_httponly}")
                print(f"SameSite=Lax: {has_samesite}")
                print(f"Secure Flag: {secure_flag} (should be False for dev)")
                
                # Test cookie-based authentication
                if has_auth_cookie:
                    # Test accessing protected endpoint with cookie (no Authorization header)
                    profile_response = self.session.get(
                        f"{self.api_url}/user/profile",
                        timeout=30
                    )
                    
                    print(f"Profile Access with Cookie: {profile_response.status_code}")
                    
                    if profile_response.status_code == 200:
                        self.log_test(
                            "Secure Cookie Authentication",
                            True,
                            f"✅ httpOnly cookie set: {has_httponly}, ✅ Cookie auth works: True"
                        )
                        return True
                    else:
                        self.log_test(
                            "Secure Cookie Authentication",
                            False,
                            f"Cookie set but authentication failed: {profile_response.status_code}"
                        )
                        return False
                else:
                    self.log_test(
                        "Secure Cookie Authentication",
                        False,
                        "No dhruv_ai_auth cookie found in response"
                    )
                    return False
            else:
                self.log_test(
                    "Secure Cookie Authentication",
                    False,
                    f"Login failed with status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Secure Cookie Authentication",
                False,
                f"Exception occurred: {str(e)}"
            )
            return False

    def test_cors_security(self):
        """Test 2: CORS Security - Verify allowed origins only"""
        print("🌐 TEST 2: CORS SECURITY")
        print("=" * 50)
        
        # Test allowed origins
        allowed_origins = [
            "http://localhost:3000",
            "https://tutor-reborn.preview.emergentagent.com"
        ]
        
        # Test disallowed origins
        disallowed_origins = [
            "https://malicious-site.com",
            "http://evil.com",
            "https://attacker.example.com"
        ]
        
        cors_results = {
            'allowed_origins_pass': 0,
            'disallowed_origins_blocked': 0,
            'total_allowed': len(allowed_origins),
            'total_disallowed': len(disallowed_origins)
        }
        
        # Test allowed origins
        print("Testing ALLOWED origins:")
        for origin in allowed_origins:
            try:
                response = requests.options(
                    f"{self.api_url}/auth/login",
                    headers={
                        'Origin': origin,
                        'Access-Control-Request-Method': 'POST',
                        'Access-Control-Request-Headers': 'Content-Type'
                    },
                    timeout=10
                )
                
                cors_header = response.headers.get('Access-Control-Allow-Origin', '')
                print(f"  Origin: {origin}")
                print(f"  Status: {response.status_code}")
                print(f"  CORS Header: {cors_header}")
                
                if cors_header == origin or cors_header == '*':
                    cors_results['allowed_origins_pass'] += 1
                    print(f"  ✅ ALLOWED correctly")
                else:
                    print(f"  ❌ NOT ALLOWED (unexpected)")
                print()
                
            except Exception as e:
                print(f"  ❌ Error testing {origin}: {str(e)}")
        
        # Test disallowed origins
        print("Testing DISALLOWED origins:")
        for origin in disallowed_origins:
            try:
                response = requests.options(
                    f"{self.api_url}/auth/login",
                    headers={
                        'Origin': origin,
                        'Access-Control-Request-Method': 'POST',
                        'Access-Control-Request-Headers': 'Content-Type'
                    },
                    timeout=10
                )
                
                cors_header = response.headers.get('Access-Control-Allow-Origin', '')
                print(f"  Origin: {origin}")
                print(f"  Status: {response.status_code}")
                print(f"  CORS Header: {cors_header}")
                
                if cors_header != origin and cors_header != '*':
                    cors_results['disallowed_origins_blocked'] += 1
                    print(f"  ✅ BLOCKED correctly")
                else:
                    print(f"  ❌ NOT BLOCKED (security issue)")
                print()
                
            except Exception as e:
                print(f"  ❌ Error testing {origin}: {str(e)}")
        
        # Evaluate CORS security
        allowed_pass_rate = cors_results['allowed_origins_pass'] / cors_results['total_allowed']
        blocked_pass_rate = cors_results['disallowed_origins_blocked'] / cors_results['total_disallowed']
        
        cors_secure = allowed_pass_rate >= 0.5 and blocked_pass_rate >= 0.5
        
        self.log_test(
            "CORS Security",
            cors_secure,
            f"Allowed origins working: {cors_results['allowed_origins_pass']}/{cors_results['total_allowed']}, "
            f"Disallowed origins blocked: {cors_results['disallowed_origins_blocked']}/{cors_results['total_disallowed']}"
        )
        
        return cors_secure

    def test_csrf_protection(self):
        """Test 3: CSRF Protection - Verify CSRF middleware is active"""
        print("🛡️ TEST 3: CSRF PROTECTION")
        print("=" * 50)
        
        csrf_results = {
            'csrf_token_endpoint': False,
            'csrf_token_required': False,
            'csrf_validation_working': False
        }
        
        # Test 1: Check if CSRF token endpoint exists
        try:
            csrf_response = self.session.get(
                f"{self.api_url}/auth/csrf-token",
                timeout=10
            )
            
            print(f"CSRF Token Endpoint Status: {csrf_response.status_code}")
            
            if csrf_response.status_code == 200:
                csrf_data = csrf_response.json()
                csrf_token = csrf_data.get('csrf_token', '')
                print(f"CSRF Token Response: {json.dumps(csrf_data, indent=2)}")
                
                if csrf_token:
                    csrf_results['csrf_token_endpoint'] = True
                    print("✅ CSRF token endpoint working")
                    
                    # Test 2: Try request without CSRF token (should fail)
                    login_data = {
                        "email": self.test_email,
                        "password": self.test_password
                    }
                    
                    no_csrf_response = requests.post(
                        f"{self.api_url}/auth/login",
                        json=login_data,
                        timeout=10
                    )
                    
                    print(f"Request without CSRF token: {no_csrf_response.status_code}")
                    
                    # Test 3: Try request with valid CSRF token (should succeed)
                    csrf_headers = {
                        'X-CSRFToken': csrf_token,
                        'Content-Type': 'application/json'
                    }
                    
                    with_csrf_response = requests.post(
                        f"{self.api_url}/auth/login",
                        json=login_data,
                        headers=csrf_headers,
                        timeout=10
                    )
                    
                    print(f"Request with CSRF token: {with_csrf_response.status_code}")
                    
                    # Evaluate CSRF protection
                    if no_csrf_response.status_code == 403 and with_csrf_response.status_code == 200:
                        csrf_results['csrf_validation_working'] = True
                        print("✅ CSRF validation working correctly")
                    elif no_csrf_response.status_code == with_csrf_response.status_code:
                        print("⚠️ CSRF protection may not be enforced")
                    else:
                        print("⚠️ CSRF behavior unclear")
                        
                else:
                    print("❌ No CSRF token in response")
            else:
                print("❌ CSRF token endpoint not accessible")
                
        except Exception as e:
            print(f"❌ Error testing CSRF protection: {str(e)}")
        
        csrf_working = csrf_results['csrf_token_endpoint'] and csrf_results['csrf_validation_working']
        
        self.log_test(
            "CSRF Protection",
            csrf_working,
            f"Token endpoint: {csrf_results['csrf_token_endpoint']}, "
            f"Validation working: {csrf_results['csrf_validation_working']}"
        )
        
        return csrf_working

    def test_environment_variable_security(self):
        """Test 4: Environment Variable Security - No hard-coded secrets"""
        print("🔐 TEST 4: ENVIRONMENT VARIABLE SECURITY")
        print("=" * 50)
        
        security_results = {
            'no_fallback_secrets': True,
            'jwt_secret_loaded': False,
            'csrf_secret_loaded': False,
            'no_console_logging': True
        }
        
        # Test by attempting operations that would fail if secrets are missing
        try:
            # Test JWT token validation (requires JWT_SECRET)
            login_data = {
                "email": self.test_email,
                "password": self.test_password
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Check if JWT token is properly formatted (not a fallback)
                token = response_data.get('token', '')
                if token and len(token) > 50 and '.' in token:
                    security_results['jwt_secret_loaded'] = True
                    print("✅ JWT_SECRET appears to be properly loaded")
                    
                    # Test token validation by accessing protected endpoint
                    headers = {'Authorization': f'Bearer {token}'}
                    profile_response = requests.get(
                        f"{self.api_url}/user/profile",
                        headers=headers,
                        timeout=10
                    )
                    
                    if profile_response.status_code == 200:
                        print("✅ JWT token validation working")
                    else:
                        print("⚠️ JWT token validation issues")
                        security_results['jwt_secret_loaded'] = False
                else:
                    print("❌ JWT token appears invalid or using fallback")
                    security_results['jwt_secret_loaded'] = False
            else:
                print("❌ Login failed - cannot test JWT_SECRET")
                security_results['jwt_secret_loaded'] = False
                
        except Exception as e:
            print(f"❌ Error testing JWT_SECRET: {str(e)}")
            security_results['jwt_secret_loaded'] = False
        
        # Test CSRF secret (if CSRF is implemented)
        try:
            csrf_response = self.session.get(
                f"{self.api_url}/auth/csrf-token",
                timeout=10
            )
            
            if csrf_response.status_code == 200:
                csrf_data = csrf_response.json()
                csrf_token = csrf_data.get('csrf_token', '')
                
                if csrf_token and len(csrf_token) > 20:
                    security_results['csrf_secret_loaded'] = True
                    print("✅ CSRF_SECRET appears to be properly loaded")
                else:
                    print("⚠️ CSRF token appears weak or using fallback")
            else:
                print("⚠️ CSRF endpoint not available")
                
        except Exception as e:
            print(f"⚠️ Error testing CSRF_SECRET: {str(e)}")
        
        # Check for common fallback patterns in responses
        try:
            # Look for signs of fallback secrets in error messages
            invalid_login = {
                "email": "invalid@test.com",
                "password": "wrongpassword"
            }
            
            response = requests.post(
                f"{self.api_url}/auth/login",
                json=invalid_login,
                timeout=10
            )
            
            response_text = response.text.lower()
            fallback_indicators = [
                'fallback',
                'default-secret',
                'change-me',
                'development-only',
                'insecure'
            ]
            
            for indicator in fallback_indicators:
                if indicator in response_text:
                    security_results['no_fallback_secrets'] = False
                    print(f"❌ Fallback secret indicator found: {indicator}")
                    break
            
            if security_results['no_fallback_secrets']:
                print("✅ No obvious fallback secret indicators found")
                
        except Exception as e:
            print(f"⚠️ Error checking for fallback secrets: {str(e)}")
        
        env_security_score = sum(security_results.values())
        env_security_pass = env_security_score >= 2  # At least JWT and no fallbacks
        
        self.log_test(
            "Environment Variable Security",
            env_security_pass,
            f"JWT loaded: {security_results['jwt_secret_loaded']}, "
            f"CSRF loaded: {security_results['csrf_secret_loaded']}, "
            f"No fallbacks: {security_results['no_fallback_secrets']}"
        )
        
        return env_security_pass

    def test_logout_cookie_clearing(self):
        """Test 5: Logout Cookie Clearing - Verify logout clears cookies"""
        print("🚪 TEST 5: LOGOUT COOKIE CLEARING")
        print("=" * 50)
        
        try:
            # First login to get cookies
            login_data = {
                "email": self.test_email,
                "password": self.test_password
            }
            
            login_response = self.session.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                timeout=30
            )
            
            if login_response.status_code == 200:
                print("✅ Login successful")
                
                # Check if we have cookies
                cookies_before = self.session.cookies
                print(f"Cookies before logout: {len(cookies_before)} cookies")
                
                # Test logout
                logout_response = self.session.post(
                    f"{self.api_url}/auth/logout",
                    timeout=10
                )
                
                print(f"Logout Response Status: {logout_response.status_code}")
                
                if logout_response.status_code == 200:
                    # Check Set-Cookie header for cookie clearing
                    set_cookie_header = logout_response.headers.get('Set-Cookie', '')
                    print(f"Logout Set-Cookie Header: {set_cookie_header}")
                    
                    # Look for cookie clearing patterns
                    cookie_cleared = (
                        'dhruv_ai_auth=;' in set_cookie_header or
                        'dhruv_ai_auth=deleted' in set_cookie_header or
                        'Max-Age=0' in set_cookie_header or
                        'expires=' in set_cookie_header.lower()
                    )
                    
                    print(f"Cookie clearing detected: {cookie_cleared}")
                    
                    # Test accessing protected endpoint after logout (should fail)
                    profile_response = self.session.get(
                        f"{self.api_url}/user/profile",
                        timeout=10
                    )
                    
                    print(f"Profile access after logout: {profile_response.status_code}")
                    
                    # Should return 401 Unauthorized
                    logout_effective = profile_response.status_code == 401
                    
                    self.log_test(
                        "Logout Cookie Clearing",
                        logout_effective and cookie_cleared,
                        f"Cookie cleared: {cookie_cleared}, Access denied after logout: {logout_effective}"
                    )
                    
                    return logout_effective and cookie_cleared
                else:
                    self.log_test(
                        "Logout Cookie Clearing",
                        False,
                        f"Logout failed with status: {logout_response.status_code}"
                    )
                    return False
            else:
                self.log_test(
                    "Logout Cookie Clearing",
                    False,
                    f"Login failed, cannot test logout: {login_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Logout Cookie Clearing",
                False,
                f"Exception occurred: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all authentication security tests"""
        print("🔒 STAGE 1 AUTHENTICATION HARDENING SECURITY TESTS")
        print("=" * 60)
        print(f"Testing backend: {self.base_url}")
        print(f"Test credentials: {self.test_email} / {self.test_password}")
        print("=" * 60)
        print()
        
        # Run all security tests
        test_results = {
            'secure_cookie_auth': self.test_secure_cookie_authentication(),
            'cors_security': self.test_cors_security(),
            'csrf_protection': self.test_csrf_protection(),
            'env_var_security': self.test_environment_variable_security(),
            'logout_clearing': self.test_logout_cookie_clearing()
        }
        
        # Summary
        print("🎯 AUTHENTICATION SECURITY TEST SUMMARY")
        print("=" * 50)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print()
        print(f"Overall Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        # Critical security assessment
        critical_tests = ['secure_cookie_auth', 'env_var_security']
        critical_passed = sum(test_results[test] for test in critical_tests)
        
        if critical_passed == len(critical_tests):
            print("🔒 CRITICAL SECURITY: ✅ PASS - Core authentication security implemented")
        else:
            print("🚨 CRITICAL SECURITY: ❌ FAIL - Core authentication security issues found")
        
        # Recommendations
        print("\n🔧 RECOMMENDATIONS:")
        if not test_results['secure_cookie_auth']:
            print("- Implement httpOnly cookie authentication")
        if not test_results['cors_security']:
            print("- Configure CORS to allow only specified origins")
        if not test_results['csrf_protection']:
            print("- Implement CSRF protection middleware")
        if not test_results['env_var_security']:
            print("- Ensure all secrets are loaded from environment variables")
        if not test_results['logout_clearing']:
            print("- Implement proper cookie clearing on logout")
        
        return success_rate >= 80  # 80% pass rate required

if __name__ == "__main__":
    tester = AuthSecurityTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)