import requests
import json
import time
import uuid
from datetime import datetime

class Phase1StabilityTester:
    def __init__(self):
        # Use the correct backend URL from frontend/.env
        self.base_url = "https://auth-gateway-dhruv.preview.emergentagent.com/api"
        self.token = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def run_test(self, test_name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        # Merge headers
        test_headers = self.session.headers.copy()
        if headers:
            test_headers.update(headers)
        
        try:
            if method == "GET":
                response = self.session.get(url, headers=test_headers, timeout=30)
            elif method == "POST":
                response = self.session.post(url, json=data, headers=test_headers, timeout=30)
            elif method == "PUT":
                response = self.session.put(url, json=data, headers=test_headers, timeout=30)
            elif method == "DELETE":
                response = self.session.delete(url, headers=test_headers, timeout=30)
            
            # Handle expected status as list or single value
            if isinstance(expected_status, list):
                status_match = response.status_code in expected_status
            else:
                status_match = response.status_code == expected_status
            
            if status_match:
                try:
                    response_data = response.json()
                    return True, response_data, response.status_code
                except:
                    return True, {}, response.status_code
            else:
                print(f"   ❌ {test_name}: Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"      Error: {error_data}")
                    return False, error_data, response.status_code
                except:
                    print(f"      Error: {response.text}")
                    return False, {"error": response.text}, response.status_code
                    
        except Exception as e:
            print(f"   ❌ {test_name}: Exception - {str(e)}")
            return False, {"error": str(e)}, 0
    
    def authenticate(self):
        """Authenticate with test user"""
        login_data = {
            "email": "test@dhruvai.com",
            "password": "password123"
        }
        
        success, response, _ = self.run_test(
            "Authentication Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and response.get('token'):
            self.token = response.get('token')
            self.session.headers.update({'Authorization': f'Bearer {self.token}'})
            print(f"   ✅ Authentication successful")
            return True
        else:
            print(f"   ❌ Authentication failed")
            return False

    def test_phase1_stability_implementation(self):
        """Test Phase 1 Stability Implementation"""
        print("\n🔧 PHASE 1 STABILITY IMPLEMENTATION TESTING")
        print("=" * 80)
        print("   OBJECTIVE: Test Subscription Service Migration, Feature Access, CSRF, Health Check")
        print("   BACKEND URL:", self.base_url)
        print("   AUTH: test@dhruvai.com / password123")
        
        test_results = {
            'authentication': False,
            'health_check': False,
            'csrf_token_endpoint': False,
            'subscription_info_endpoint': False,
            'subscription_current_endpoint': False,
            'subscription_usage_endpoint': False,
            'subscription_plans_endpoint': False,
            'feature_access_ai_mentor': False,
            'feature_access_mock_tests': False,
            'feature_access_auto_notes': False,
            'feature_access_denied_402': False,
            'backward_compatibility': False
        }
        
        # AUTHENTICATION
        print("\n1️⃣ AUTHENTICATION SETUP")
        auth_success = self.authenticate()
        if not auth_success:
            print("   ❌ Authentication failed - cannot proceed with subscription tests")
            return False
        
        test_results['authentication'] = True
        
        # BACKEND HEALTH CHECK
        print("\n2️⃣ BACKEND HEALTH CHECK")
        test_results['health_check'] = self.test_health_endpoint()
        
        # CSRF TOKEN ENDPOINT
        print("\n3️⃣ CSRF TOKEN ENDPOINT")
        test_results['csrf_token_endpoint'] = self.test_csrf_token_endpoint()
        
        # SUBSCRIPTION SERVICE MIGRATION TESTING
        print("\n4️⃣ SUBSCRIPTION SERVICE MIGRATION TESTING")
        subscription_results = self.test_subscription_endpoints()
        test_results.update(subscription_results)
        
        # FEATURE ACCESS TESTING
        print("\n5️⃣ FEATURE ACCESS TESTING")
        feature_access_results = self.test_feature_access_endpoints()
        test_results.update(feature_access_results)
        
        return self._print_phase1_test_results(test_results)
    
    def test_health_endpoint(self):
        """Test /api/health endpoint"""
        print("   Testing /api/health endpoint")
        
        success, response, status_code = self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )
        
        if success and status_code == 200:
            print(f"   ✅ Health check successful")
            print(f"      Status: {response.get('status')}")
            print(f"      Service: {response.get('service')}")
            print(f"      Version: {response.get('version')}")
            return True
        else:
            print(f"   ❌ Health check failed - Status: {status_code}")
            return False
    
    def test_csrf_token_endpoint(self):
        """Test /api/auth/csrf-token endpoint"""
        print("   Testing /api/auth/csrf-token endpoint")
        
        success, response, status_code = self.run_test(
            "CSRF Token",
            "GET",
            "auth/csrf-token",
            200
        )
        
        if success and status_code == 200:
            csrf_token = response.get('csrf_token')
            if csrf_token and len(csrf_token) > 10:
                print(f"   ✅ CSRF token generated successfully")
                print(f"      Token length: {len(csrf_token)} characters")
                return True
            else:
                print(f"   ❌ CSRF token invalid or missing")
                print(f"      Response: {response}")
                return False
        else:
            print(f"   ❌ CSRF token endpoint failed - Status: {status_code}")
            print(f"      Response: {response}")
            return False
    
    def test_subscription_endpoints(self):
        """Test subscription service migration endpoints"""
        print("   Testing subscription service migration endpoints")
        
        results = {
            'subscription_info_endpoint': False,
            'subscription_current_endpoint': False,
            'subscription_usage_endpoint': False,
            'subscription_plans_endpoint': False,
            'backward_compatibility': False
        }
        
        # Test /api/subscription/info
        print("   📝 Testing: GET /api/subscription/info")
        success, response, status_code = self.run_test(
            "Subscription Info",
            "GET",
            "subscription/info",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success and status_code == 200:
            results['subscription_info_endpoint'] = True
            print(f"   ✅ Subscription info endpoint working")
            
            # Check response structure
            print(f"      Response keys: {list(response.keys())}")
            if 'subscription' in response and 'usage_summary' in response:
                results['backward_compatibility'] = True
                print(f"      ✅ Response structure includes subscription and usage_summary")
            else:
                print(f"      ⚠️ Response structure may not be backward compatible")
                print(f"      Expected: subscription, usage_summary")
                print(f"      Actual: {list(response.keys())}")
        else:
            print(f"   ❌ Subscription info failed - Status: {status_code}")
        
        # Test /api/subscription/current
        print("   📝 Testing: GET /api/subscription/current")
        success, response, status_code = self.run_test(
            "Subscription Current",
            "GET",
            "subscription/current",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success and status_code == 200:
            results['subscription_current_endpoint'] = True
            print(f"   ✅ Subscription current endpoint working")
            print(f"      Plan: {response.get('plan', 'N/A')}")
        else:
            print(f"   ❌ Subscription current failed - Status: {status_code}")
        
        # Test /api/subscription/usage
        print("   📝 Testing: GET /api/subscription/usage")
        success, response, status_code = self.run_test(
            "Subscription Usage",
            "GET",
            "subscription/usage",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success and status_code == 200:
            results['subscription_usage_endpoint'] = True
            print(f"   ✅ Subscription usage endpoint working")
            print(f"      Usage data keys: {list(response.keys())}")
        else:
            print(f"   ❌ Subscription usage failed - Status: {status_code}")
        
        # Test /api/subscription/plans
        print("   📝 Testing: GET /api/subscription/plans")
        success, response, status_code = self.run_test(
            "Subscription Plans",
            "GET",
            "subscription/plans",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success and status_code == 200:
            results['subscription_plans_endpoint'] = True
            print(f"   ✅ Subscription plans endpoint working")
            if isinstance(response, list) and len(response) > 0:
                print(f"      Available plans: {len(response)}")
            elif 'plans' in response:
                print(f"      Plans in response: {len(response.get('plans', []))}")
        else:
            print(f"   ❌ Subscription plans failed - Status: {status_code}")
        
        return results
    
    def test_feature_access_endpoints(self):
        """Test feature access check endpoints"""
        print("   Testing feature access check endpoints")
        
        results = {
            'feature_access_ai_mentor': False,
            'feature_access_mock_tests': False,
            'feature_access_auto_notes': False,
            'feature_access_denied_402': False
        }
        
        # Test AI Mentor access
        print("   📝 Testing: POST /api/subscription/check-access (ai_mentor)")
        success, response, status_code = self.run_test(
            "Feature Access - AI Mentor",
            "POST",
            "subscription/check-access",
            [200, 402],
            data={"feature_name": "ai_mentor"},
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success and status_code == 200:
            results['feature_access_ai_mentor'] = True
            print(f"   ✅ AI Mentor access granted - Status: {status_code}")
            print(f"      Access: {response.get('access', 'N/A')}")
        elif success and status_code == 402:
            print(f"   ⚠️ AI Mentor access denied - Status: {status_code} (Payment Required)")
            results['feature_access_denied_402'] = True
        else:
            print(f"   ❌ AI Mentor access check failed - Status: {status_code}")
        
        # Test Mock Tests access
        print("   📝 Testing: POST /api/subscription/check-access (mock_tests)")
        success, response, status_code = self.run_test(
            "Feature Access - Mock Tests",
            "POST",
            "subscription/check-access",
            [200, 402],
            data={"feature_name": "mock_tests"},
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success and status_code == 200:
            results['feature_access_mock_tests'] = True
            print(f"   ✅ Mock Tests access granted - Status: {status_code}")
            print(f"      Access: {response.get('access', 'N/A')}")
        elif success and status_code == 402:
            print(f"   ⚠️ Mock Tests access denied - Status: {status_code} (Payment Required)")
            if not results['feature_access_denied_402']:
                results['feature_access_denied_402'] = True
        else:
            print(f"   ❌ Mock Tests access check failed - Status: {status_code}")
        
        # Test Auto Notes access
        print("   📝 Testing: POST /api/subscription/check-access (auto_notes)")
        success, response, status_code = self.run_test(
            "Feature Access - Auto Notes",
            "POST",
            "subscription/check-access",
            [200, 402],
            data={"feature_name": "auto_notes"},
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success and status_code == 200:
            results['feature_access_auto_notes'] = True
            print(f"   ✅ Auto Notes access granted - Status: {status_code}")
            print(f"      Access: {response.get('access', 'N/A')}")
        elif success and status_code == 402:
            print(f"   ⚠️ Auto Notes access denied - Status: {status_code} (Payment Required)")
            if not results['feature_access_denied_402']:
                results['feature_access_denied_402'] = True
        else:
            print(f"   ❌ Auto Notes access check failed - Status: {status_code}")
        
        return results
    
    def _print_phase1_test_results(self, test_results):
        """Print comprehensive test results for Phase 1 Stability Implementation"""
        print("\n" + "=" * 80)
        print("🔧 PHASE 1 STABILITY IMPLEMENTATION - FINAL RESULTS")
        print("=" * 80)
        
        success_count = sum(test_results.values())
        total_tests = len(test_results)
        success_rate = (success_count / total_tests) * 100
        
        print(f"\n📊 TEST RESULTS SUMMARY:")
        
        # Authentication & Health
        print(f"\n   AUTHENTICATION & HEALTH:")
        auth_health_tests = ['authentication', 'health_check', 'csrf_token_endpoint']
        for test_name in auth_health_tests:
            status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
            display_name = test_name.replace('_', ' ').title()
            print(f"      {display_name}: {status}")
        
        # Subscription Service Migration
        subscription_tests = ['subscription_info_endpoint', 'subscription_current_endpoint', 
                            'subscription_usage_endpoint', 'subscription_plans_endpoint', 'backward_compatibility']
        subscription_success = sum(test_results.get(test, False) for test in subscription_tests)
        print(f"\n   SUBSCRIPTION SERVICE MIGRATION ({subscription_success}/{len(subscription_tests)}):")
        for test_name in subscription_tests:
            status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
            display_name = test_name.replace('subscription_', '').replace('_', ' ').title()
            print(f"      {display_name}: {status}")
        
        # Feature Access Testing
        feature_tests = ['feature_access_ai_mentor', 'feature_access_mock_tests', 
                        'feature_access_auto_notes', 'feature_access_denied_402']
        feature_success = sum(test_results.get(test, False) for test in feature_tests)
        print(f"\n   FEATURE ACCESS TESTING ({feature_success}/{len(feature_tests)}):")
        for test_name in feature_tests:
            status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
            display_name = test_name.replace('feature_access_', '').replace('_', ' ').title()
            print(f"      {display_name}: {status}")
        
        print(f"\n📈 OVERALL SUCCESS RATE: {success_count}/{total_tests} ({success_rate:.1f}%)")
        
        # Success Criteria Summary
        print(f"\n🎯 SUCCESS CRITERIA SUMMARY:")
        criteria_mapping = {
            'Backend health check working': test_results.get('health_check', False),
            'CSRF token endpoint functional': test_results.get('csrf_token_endpoint', False),
            'All subscription endpoints working': all(test_results.get(test, False) for test in subscription_tests[:-1]),
            'Feature access checks functional': any(test_results.get(test, False) for test in feature_tests[:-1]),
            'Proper 402 responses for denied access': test_results.get('feature_access_denied_402', False),
            'Backward compatibility maintained': test_results.get('backward_compatibility', False)
        }
        
        for criterion, passed in criteria_mapping.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {criterion}")
        
        # Determine overall status
        if success_rate >= 90:
            print("\n✅ PHASE 1 STABILITY IMPLEMENTATION: EXCELLENT SUCCESS")
            print("   All subscription service migration and feature access working correctly")
        elif success_rate >= 80:
            print("\n⚠️ PHASE 1 STABILITY IMPLEMENTATION: GOOD SUCCESS")
            print("   Core functionality working, minor issues need attention")
        elif success_rate >= 70:
            print("\n⚠️ PHASE 1 STABILITY IMPLEMENTATION: PARTIAL SUCCESS")
            print("   Basic functionality working, some features need fixes")
        else:
            print("\n❌ PHASE 1 STABILITY IMPLEMENTATION: NEEDS WORK")
            print("   Critical issues prevent proper functionality")
        
        return success_rate >= 80  # 80% success rate for overall pass

if __name__ == "__main__":
    tester = Phase1StabilityTester()
    success = tester.test_phase1_stability_implementation()
    
    if success:
        print("\n🎉 Phase 1 Stability Implementation testing completed successfully!")
    else:
        print("\n⚠️ Phase 1 Stability Implementation testing completed with issues.")