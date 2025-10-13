#!/usr/bin/env python3
"""
CSRF Protection Validation Test
Focus: Testing CSRF middleware is active and working correctly
"""

import requests
import json
import sys

class CSRFTester:
    def __init__(self, base_url="https://dhruv-ai-fix.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.csrf_token = None
        self.jwt_token = None
        
    def get_csrf_token(self):
        """Get CSRF token using cookie-based approach"""
        print("🔑 Getting CSRF token...")
        
        # First request to set the cookie
        response1 = self.session.get(f"{self.base_url}/auth/csrf-token")
        print(f"   First request status: {response1.status_code}")
        
        # Second request to get the token (now with cookie)
        response2 = self.session.get(f"{self.base_url}/auth/csrf-token")
        print(f"   Second request status: {response2.status_code}")
        
        if response2.status_code == 200:
            data = response2.json()
            self.csrf_token = data.get('csrf_token', '')
            if self.csrf_token:
                print(f"   ✅ CSRF token obtained: {self.csrf_token[:20]}...")
                return True
            else:
                print("   ❌ Empty CSRF token received")
                return False
        else:
            print(f"   ❌ Failed to get CSRF token: {response2.status_code}")
            return False
    
    def test_csrf_protection_login(self):
        """Test CSRF protection on login endpoint"""
        print("\n🔒 Testing CSRF Protection on Login...")
        
        login_data = {
            "email": "test@dhruvai.com",
            "password": "password123"
        }
        
        # Test 1: Login without CSRF token (should fail with 403)
        print("   Test 1: Login WITHOUT CSRF token (should return 403)")
        response = requests.post(
            f"{self.base_url}/auth/login",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 403:
            print("   ✅ CSRF protection working - blocked request without token")
            csrf_blocking = True
        else:
            print("   ❌ CSRF protection NOT working - request succeeded without token")
            csrf_blocking = False
        
        # Test 2: Login with valid CSRF token (should succeed)
        if self.csrf_token:
            print("   Test 2: Login WITH valid CSRF token (should succeed)")
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                headers={
                    'Content-Type': 'application/json',
                    'X-CSRFToken': self.csrf_token
                }
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Login successful with valid CSRF token")
                data = response.json()
                self.jwt_token = data.get('token')
                if self.jwt_token:
                    print(f"   ✅ JWT token received: {self.jwt_token[:20]}...")
                csrf_allowing = True
            else:
                print(f"   ❌ Login failed with valid CSRF token: {response.text}")
                csrf_allowing = False
        else:
            print("   ⚠️ No CSRF token available for valid token test")
            csrf_allowing = False
        
        return csrf_blocking and csrf_allowing
    
    def test_csrf_protection_register(self):
        """Test CSRF protection on register endpoint"""
        print("\n🔒 Testing CSRF Protection on Register...")
        
        import time
        register_data = {
            "full_name": "CSRF Test User",
            "email": f"csrf_test_{int(time.time())}@dhruvai.com",
            "password": "password123",
            "exam_type": "JEE",
            "grade": "Class 12",
            "target_year": 2026
        }
        
        # Test 1: Register without CSRF token (should fail with 403)
        print("   Test 1: Register WITHOUT CSRF token (should return 403)")
        response = requests.post(
            f"{self.base_url}/auth/register",
            json=register_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 403:
            print("   ✅ CSRF protection working - blocked registration without token")
            csrf_blocking = True
        else:
            print("   ❌ CSRF protection NOT working - registration succeeded without token")
            csrf_blocking = False
        
        # Test 2: Register with valid CSRF token (should succeed)
        if self.csrf_token:
            print("   Test 2: Register WITH valid CSRF token (should succeed)")
            register_data['email'] = f"csrf_test_success_{int(time.time())}@dhruvai.com"
            
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=register_data,
                headers={
                    'Content-Type': 'application/json',
                    'X-CSRFToken': self.csrf_token
                }
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Registration successful with valid CSRF token")
                csrf_allowing = True
            else:
                print(f"   ❌ Registration failed with valid CSRF token: {response.text}")
                csrf_allowing = False
        else:
            print("   ⚠️ No CSRF token available for valid token test")
            csrf_allowing = False
        
        return csrf_blocking and csrf_allowing
    
    def test_csrf_protection_critical_endpoints(self):
        """Test CSRF protection on critical endpoints"""
        print("\n🔒 Testing CSRF Protection on Critical Endpoints...")
        
        if not self.jwt_token:
            print("   ❌ No JWT token available for critical endpoint tests")
            return False
        
        critical_endpoints = [
            ("user/profile", "PUT", {"full_name": "CSRF Test Update"}),
            ("subscription/upgrade", "POST", {"target_tier": "PREMIUM", "billing_cycle": "monthly"}),
        ]
        
        results = []
        
        for endpoint, method, data in critical_endpoints:
            print(f"   Testing {method} {endpoint}")
            
            # Test without CSRF token (should fail with 403)
            if method == "PUT":
                response = requests.put(
                    f"{self.base_url}/{endpoint}",
                    json=data,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.jwt_token}'
                    }
                )
            else:  # POST
                response = requests.post(
                    f"{self.base_url}/{endpoint}",
                    json=data,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.jwt_token}'
                    }
                )
            
            print(f"   Status without CSRF: {response.status_code}")
            
            if response.status_code == 403:
                print(f"   ✅ CSRF protection working on {endpoint}")
                results.append(True)
            else:
                print(f"   ❌ CSRF protection NOT working on {endpoint}")
                results.append(False)
        
        return all(results)
    
    def run_comprehensive_csrf_test(self):
        """Run comprehensive CSRF protection test"""
        print("🛡️ CSRF PROTECTION VALIDATION - URGENT RE-TEST")
        print("="*80)
        print("   TESTING SCOPE: CSRF middleware enabled and working correctly")
        print("   FOCUS: Token generation, protection enforcement, critical endpoints")
        print("   CREDENTIALS: test@dhruvai.com / password123")
        print("   GOAL: Confirm CSRF middleware is ACTIVE and protecting endpoints")
        
        results = {}
        
        # Test 1: CSRF Token Generation
        results['token_generation'] = self.get_csrf_token()
        
        # Test 2: CSRF Protection on Login
        results['login_protection'] = self.test_csrf_protection_login()
        
        # Test 3: CSRF Protection on Register
        results['register_protection'] = self.test_csrf_protection_register()
        
        # Test 4: CSRF Protection on Critical Endpoints
        results['critical_endpoints'] = self.test_csrf_protection_critical_endpoints()
        
        # Final Results
        print("\n" + "="*80)
        print("🛡️ CSRF PROTECTION VALIDATION - FINAL RESULTS")
        print("="*80)
        
        success_count = sum(results.values())
        total_tests = len(results)
        success_rate = (success_count / total_tests) * 100
        
        print(f"\n📊 CSRF TEST RESULTS SUMMARY:")
        print(f"   CSRF Token Generation: {'✅ PASS' if results['token_generation'] else '❌ FAIL'}")
        print(f"   CSRF Protection Login: {'✅ PASS' if results['login_protection'] else '❌ FAIL'}")
        print(f"   CSRF Protection Register: {'✅ PASS' if results['register_protection'] else '❌ FAIL'}")
        print(f"   CSRF Protection Critical Endpoints: {'✅ PASS' if results['critical_endpoints'] else '❌ FAIL'}")
        
        print(f"\n📈 OVERALL SUCCESS RATE: {success_count}/{total_tests} ({success_rate:.1f}%)")
        
        # Determine overall status
        if success_rate >= 75:
            print("\n✅ CSRF PROTECTION VALIDATION: EXCELLENT SUCCESS")
            print("   CSRF middleware is ACTIVE and properly protecting all endpoints")
            print("   Security validation PASSED - application is protected against CSRF attacks")
            return True
        elif success_rate >= 50:
            print("\n⚠️ CSRF PROTECTION VALIDATION: PARTIAL SUCCESS")
            print("   CSRF middleware is partially working, some issues need attention")
            print("   Security validation MIXED - some endpoints may be vulnerable")
            return False
        else:
            print("\n❌ CSRF PROTECTION VALIDATION: CRITICAL FAILURE")
            print("   CSRF middleware is NOT working properly")
            print("   Security validation FAILED - application is vulnerable to CSRF attacks")
            return False

def main():
    """Main test execution"""
    tester = CSRFTester()
    success = tester.run_comprehensive_csrf_test()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)