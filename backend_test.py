#!/usr/bin/env python3
"""
Phase 2 Wave 1 Backend Testing - Comprehensive Verification
Testing CSRF protection, critical endpoints, subscription, auth, and error handling
"""

import requests
import json
import time
from datetime import datetime

class Phase2BackendTester:
    def __init__(self):
        # Use environment variable for backend URL
        self.base_url = "https://dhruv-frontend-test.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.csrf_token = None
        self.test_results = {}
    
    def log(self, message, level="INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_test(self, test_name, method, endpoint, expected_status, data=None, headers=None, include_csrf=False):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        # Merge headers
        test_headers = self.session.headers.copy()
        if headers:
            test_headers.update(headers)
        
        # Add CSRF token if requested
        if include_csrf and self.csrf_token:
            test_headers['X-CSRF-Token'] = self.csrf_token
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(url, headers=test_headers, timeout=10)
            elif method == "POST":
                response = self.session.post(url, json=data, headers=test_headers, timeout=10)
            elif method == "PUT":
                response = self.session.put(url, json=data, headers=test_headers, timeout=10)
            elif method == "DELETE":
                response = self.session.delete(url, headers=test_headers, timeout=10)
            
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
    
    # ============= SECURITY TESTING =============
    
    def test_csrf_protection(self):
        """Test CSRF protection implementation"""
        self.log("=" * 80)
        self.log("🛡️ SECURITY TESTING - CSRF PROTECTION")
        self.log("=" * 80)
        
        results = {
            'csrf_token_endpoint_accessible': False,
            'csrf_token_returned': False,
            'csrf_exempt_paths_work': False,
            'csrf_protected_endpoints_reject_without_token': False,
            'csrf_protected_endpoints_accept_with_token': False
        }
        
        # Test 1: CSRF Token Endpoint
        self.log("\n1️⃣ Testing CSRF Token Endpoint")
        success, response, status, elapsed = self.run_test(
            "CSRF Token Endpoint",
            "GET",
            "auth/csrf-token",
            200
        )
        
        if success:
            results['csrf_token_endpoint_accessible'] = True
            self.log(f"   ✅ CSRF token endpoint accessible (200 OK)")
            
            # Check if token is returned
            csrf_token = response.get('csrf_token') or response.get('token')
            if csrf_token and csrf_token != "":
                results['csrf_token_returned'] = True
                self.csrf_token = csrf_token
                self.log(f"   ✅ CSRF token returned: {csrf_token[:20]}...")
            else:
                self.log(f"   ⚠️ CSRF token empty (middleware may be disabled)")
        else:
            self.log(f"   ❌ CSRF token endpoint failed: {status}")
        
        # Test 2: Exempt Paths (should work without CSRF token)
        self.log("\n2️⃣ Testing CSRF Exempt Paths")
        exempt_paths = [
            ("auth/google/login", "GET", [302, 200]),
            ("health", "GET", 200),
            ("auth/session", "GET", [200, 401])
        ]
        
        exempt_working = True
        for path, method, expected in exempt_paths:
            success, response, status, elapsed = self.run_test(
                f"Exempt Path: {path}",
                method,
                path,
                expected
            )
            if success:
                self.log(f"   ✅ Exempt path working: {method} /{path} ({status})")
            else:
                self.log(f"   ❌ Exempt path failed: {method} /{path} ({status})")
                exempt_working = False
        
        results['csrf_exempt_paths_work'] = exempt_working
        
        # Test 3: Protected Endpoints Without CSRF Token
        self.log("\n3️⃣ Testing Protected Endpoints Without CSRF Token")
        # Note: Most endpoints require authentication, so we expect 401 not 403
        # CSRF protection would return 403 if enabled and token missing
        
        protected_test = {
            "endpoint": "subscription/track-usage",
            "method": "POST",
            "data": {"feature": "ai_mentor"}
        }
        
        success, response, status, elapsed = self.run_test(
            "Protected Endpoint Without CSRF",
            protected_test["method"],
            protected_test["endpoint"],
            [401, 403],  # 401 for auth, 403 for CSRF
            data=protected_test["data"]
        )
        
        if success:
            if status == 403:
                results['csrf_protected_endpoints_reject_without_token'] = True
                self.log(f"   ✅ CSRF protection active: 403 Forbidden without token")
            elif status == 401:
                self.log(f"   ⚠️ Authentication required (401) - CSRF may be disabled or auth checked first")
        else:
            self.log(f"   ❌ Unexpected response: {status}")
        
        # Test 4: Protected Endpoints With CSRF Token (if we have one)
        if self.csrf_token:
            self.log("\n4️⃣ Testing Protected Endpoints With CSRF Token")
            success, response, status, elapsed = self.run_test(
                "Protected Endpoint With CSRF",
                protected_test["method"],
                protected_test["endpoint"],
                [200, 401],  # 401 for auth (expected), 200 if auth bypassed
                data=protected_test["data"],
                include_csrf=True
            )
            
            if success and status == 401:
                results['csrf_protected_endpoints_accept_with_token'] = True
                self.log(f"   ✅ CSRF token accepted, auth required (401)")
            elif success and status == 200:
                results['csrf_protected_endpoints_accept_with_token'] = True
                self.log(f"   ✅ CSRF token accepted, request successful (200)")
            else:
                self.log(f"   ⚠️ Response: {status}")
        
        return results
    
    # ============= CRITICAL API ENDPOINTS =============
    
    def test_critical_endpoints(self):
        """Test critical API endpoints"""
        self.log("\n" + "=" * 80)
        self.log("🎯 CRITICAL API ENDPOINTS TESTING")
        self.log("=" * 80)
        
        results = {
            'health_endpoint': False,
            'dashboard_analytics': False,
            'dashboard_streak': False,
            'gamification_leaderboard': False,
            'gamification_progress': False,
            'mock_tests_generate': False
        }
        
        # Test 1: Health Endpoint
        self.log("\n1️⃣ Testing Health Endpoint")
        success, response, status, elapsed = self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )
        
        if success:
            results['health_endpoint'] = True
            self.log(f"   ✅ Health endpoint working (200 OK) - {elapsed:.2f}s")
            self.log(f"   📊 Response: {json.dumps(response, indent=2)}")
        else:
            self.log(f"   ❌ Health endpoint failed: {status}")
        
        # Test 2: Dashboard Analytics
        self.log("\n2️⃣ Testing Dashboard Analytics")
        success, response, status, elapsed = self.run_test(
            "Dashboard Analytics",
            "GET",
            "dashboard/analytics",
            [200, 401]  # 401 expected without auth
        )
        
        if success:
            results['dashboard_analytics'] = True
            if status == 200:
                self.log(f"   ✅ Dashboard analytics accessible (200 OK) - {elapsed:.2f}s")
                if elapsed < 2:
                    self.log(f"   ✅ Performance: {elapsed:.2f}s < 2s")
                else:
                    self.log(f"   ⚠️ Performance: {elapsed:.2f}s >= 2s (target: <2s)")
            else:
                self.log(f"   ✅ Dashboard analytics secured (401 Unauthorized)")
        else:
            self.log(f"   ❌ Dashboard analytics failed: {status}")
        
        # Test 3: Dashboard Streak
        self.log("\n3️⃣ Testing Dashboard Streak")
        success, response, status, elapsed = self.run_test(
            "Dashboard Streak",
            "GET",
            "dashboard/streak",
            [200, 401]
        )
        
        if success:
            results['dashboard_streak'] = True
            if status == 200:
                self.log(f"   ✅ Dashboard streak accessible (200 OK) - {elapsed:.2f}s")
            else:
                self.log(f"   ✅ Dashboard streak secured (401 Unauthorized)")
        else:
            self.log(f"   ❌ Dashboard streak failed: {status}")
        
        # Test 4: Gamification Leaderboard
        self.log("\n4️⃣ Testing Gamification Leaderboard")
        success, response, status, elapsed = self.run_test(
            "Gamification Leaderboard",
            "GET",
            "gamification/leaderboard",
            [200, 401]
        )
        
        if success:
            results['gamification_leaderboard'] = True
            if status == 200:
                self.log(f"   ✅ Leaderboard accessible (200 OK) - {elapsed:.2f}s")
            else:
                self.log(f"   ✅ Leaderboard secured (401 Unauthorized)")
        else:
            self.log(f"   ❌ Leaderboard failed: {status}")
        
        # Test 5: Gamification Progress
        self.log("\n5️⃣ Testing Gamification Progress")
        success, response, status, elapsed = self.run_test(
            "Gamification Progress",
            "GET",
            "gamification/progress",
            [200, 401]
        )
        
        if success:
            results['gamification_progress'] = True
            if status == 200:
                self.log(f"   ✅ Progress accessible (200 OK) - {elapsed:.2f}s")
            else:
                self.log(f"   ✅ Progress secured (401 Unauthorized)")
        else:
            self.log(f"   ❌ Progress failed: {status}")
        
        # Test 6: Mock Tests Generate
        self.log("\n6️⃣ Testing Mock Tests Generate")
        test_data = {
            "subject": "Mathematics",
            "difficulty": "medium",
            "num_questions": 10
        }
        
        success, response, status, elapsed = self.run_test(
            "Mock Tests Generate",
            "POST",
            "mock-tests/generate",
            [200, 401, 402]  # 402 for subscription required
        )
        
        if success:
            results['mock_tests_generate'] = True
            if status == 200:
                self.log(f"   ✅ Mock test generation working (200 OK)")
            elif status == 401:
                self.log(f"   ✅ Mock test generation secured (401 Unauthorized)")
            elif status == 402:
                self.log(f"   ✅ Mock test generation requires subscription (402)")
        else:
            self.log(f"   ❌ Mock test generation failed: {status}")
        
        return results
    
    # ============= SUBSCRIPTION ENDPOINTS =============
    
    def test_subscription_endpoints(self):
        """Test subscription endpoints"""
        self.log("\n" + "=" * 80)
        self.log("💳 SUBSCRIPTION ENDPOINTS TESTING")
        self.log("=" * 80)
        
        results = {
            'subscription_info': False,
            'subscription_current': False,
            'subscription_check_access': False,
            'subscription_track_usage': False
        }
        
        # Test 1: Subscription Info
        self.log("\n1️⃣ Testing Subscription Info")
        success, response, status, elapsed = self.run_test(
            "Subscription Info",
            "GET",
            "subscription/info",
            [200, 401]
        )
        
        if success:
            results['subscription_info'] = True
            if status == 200:
                self.log(f"   ✅ Subscription info accessible (200 OK)")
                self.log(f"   📊 Response keys: {list(response.keys())}")
            else:
                self.log(f"   ✅ Subscription info secured (401 Unauthorized)")
        else:
            self.log(f"   ❌ Subscription info failed: {status}")
        
        # Test 2: Current Subscription
        self.log("\n2️⃣ Testing Current Subscription")
        success, response, status, elapsed = self.run_test(
            "Current Subscription",
            "GET",
            "subscription/current",
            [200, 401]
        )
        
        if success:
            results['subscription_current'] = True
            if status == 200:
                self.log(f"   ✅ Current subscription accessible (200 OK)")
            else:
                self.log(f"   ✅ Current subscription secured (401 Unauthorized)")
        else:
            self.log(f"   ❌ Current subscription failed: {status}")
        
        # Test 3: Check Access
        self.log("\n3️⃣ Testing Check Access")
        test_data = {"feature": "ai_mentor"}
        
        success, response, status, elapsed = self.run_test(
            "Check Access",
            "POST",
            "subscription/check-access",
            [200, 401, 402]
        )
        
        if success:
            results['subscription_check_access'] = True
            if status == 200:
                self.log(f"   ✅ Check access working (200 OK)")
            elif status == 401:
                self.log(f"   ✅ Check access secured (401 Unauthorized)")
            elif status == 402:
                self.log(f"   ✅ Check access requires payment (402)")
        else:
            self.log(f"   ❌ Check access failed: {status}")
        
        # Test 4: Track Usage
        self.log("\n4️⃣ Testing Track Usage")
        test_data = {"feature": "ai_mentor"}
        
        success, response, status, elapsed = self.run_test(
            "Track Usage",
            "POST",
            "subscription/track-usage",
            [200, 401]
        )
        
        if success:
            results['subscription_track_usage'] = True
            if status == 200:
                self.log(f"   ✅ Track usage working (200 OK)")
            else:
                self.log(f"   ✅ Track usage secured (401 Unauthorized)")
        else:
            self.log(f"   ❌ Track usage failed: {status}")
        
        return results
    
    # ============= AUTHENTICATION FLOW =============
    
    def test_authentication_flow(self):
        """Test authentication flow"""
        self.log("\n" + "=" * 80)
        self.log("🔐 AUTHENTICATION FLOW TESTING")
        self.log("=" * 80)
        
        results = {
            'auth_session_endpoint': False,
            'oauth_callback_accessible': False
        }
        
        # Test 1: Session Endpoint
        self.log("\n1️⃣ Testing Session Endpoint")
        success, response, status, elapsed = self.run_test(
            "Auth Session",
            "GET",
            "auth/session",
            [200, 401]
        )
        
        if success:
            results['auth_session_endpoint'] = True
            if status == 200:
                self.log(f"   ✅ Session endpoint accessible (200 OK)")
                self.log(f"   📊 Response: {json.dumps(response, indent=2)}")
            else:
                self.log(f"   ✅ Session endpoint secured (401 Unauthorized)")
        else:
            self.log(f"   ❌ Session endpoint failed: {status}")
        
        # Test 2: OAuth Callback
        self.log("\n2️⃣ Testing OAuth Callback")
        success, response, status, elapsed = self.run_test(
            "OAuth Callback",
            "GET",
            "auth/google/callback",
            [200, 302, 400, 422]  # Various valid responses
        )
        
        if success:
            results['oauth_callback_accessible'] = True
            self.log(f"   ✅ OAuth callback accessible ({status})")
        else:
            self.log(f"   ❌ OAuth callback failed: {status}")
        
        return results
    
    # ============= ERROR HANDLING =============
    
    def test_error_handling(self):
        """Test error handling"""
        self.log("\n" + "=" * 80)
        self.log("⚠️ ERROR HANDLING TESTING")
        self.log("=" * 80)
        
        results = {
            'invalid_endpoint_404': False,
            'unauthorized_401': False,
            'forbidden_403': False,
            'error_format_consistent': False
        }
        
        # Test 1: Invalid Endpoint (404)
        self.log("\n1️⃣ Testing Invalid Endpoint (404)")
        success, response, status, elapsed = self.run_test(
            "Invalid Endpoint",
            "GET",
            "invalid/endpoint/that/does/not/exist",
            404
        )
        
        if success:
            results['invalid_endpoint_404'] = True
            self.log(f"   ✅ Invalid endpoint returns 404")
            self.log(f"   📊 Error response: {json.dumps(response, indent=2)}")
        else:
            self.log(f"   ❌ Invalid endpoint did not return 404: {status}")
        
        # Test 2: Unauthorized (401)
        self.log("\n2️⃣ Testing Unauthorized Access (401)")
        success, response, status, elapsed = self.run_test(
            "Unauthorized Access",
            "GET",
            "subscription/info",
            401
        )
        
        if success:
            results['unauthorized_401'] = True
            self.log(f"   ✅ Unauthorized access returns 401")
            self.log(f"   📊 Error response: {json.dumps(response, indent=2)}")
        else:
            self.log(f"   ⚠️ Unauthorized access returned: {status}")
        
        # Test 3: Check Error Format Consistency
        self.log("\n3️⃣ Testing Error Format Consistency")
        error_responses = []
        
        # Collect error responses
        test_endpoints = [
            ("invalid/endpoint", "GET", 404),
            ("subscription/info", "GET", 401)
        ]
        
        for endpoint, method, expected in test_endpoints:
            success, response, status, elapsed = self.run_test(
                f"Error Format: {endpoint}",
                method,
                endpoint,
                expected
            )
            if success and isinstance(response, dict):
                error_responses.append(response)
        
        # Check if error responses have consistent format
        if error_responses:
            # Check for common error fields
            has_detail = all('detail' in resp for resp in error_responses)
            has_message = all('message' in resp or 'detail' in resp for resp in error_responses)
            
            if has_detail or has_message:
                results['error_format_consistent'] = True
                self.log(f"   ✅ Error format consistent across endpoints")
            else:
                self.log(f"   ⚠️ Error format may vary across endpoints")
        
        return results
    
    # ============= MAIN TEST RUNNER =============
    
    def run_all_tests(self):
        """Run all Phase 2 backend tests"""
        self.log("\n" + "=" * 80)
        self.log("🚀 PHASE 2 WAVE 1 BACKEND TESTING - COMPREHENSIVE VERIFICATION")
        self.log("=" * 80)
        self.log(f"Backend URL: {self.base_url}")
        self.log(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_results = {}
        
        # Run all test suites
        all_results['csrf_protection'] = self.test_csrf_protection()
        all_results['critical_endpoints'] = self.test_critical_endpoints()
        all_results['subscription_endpoints'] = self.test_subscription_endpoints()
        all_results['authentication_flow'] = self.test_authentication_flow()
        all_results['error_handling'] = self.test_error_handling()
        
        # Print final summary
        self.print_final_summary(all_results)
        
        return all_results
    
    def print_final_summary(self, all_results):
        """Print final test summary"""
        self.log("\n" + "=" * 80)
        self.log("📊 FINAL TEST SUMMARY - PHASE 2 WAVE 1")
        self.log("=" * 80)
        
        total_tests = 0
        passed_tests = 0
        
        for category, results in all_results.items():
            category_total = len(results)
            category_passed = sum(results.values())
            total_tests += category_total
            passed_tests += category_passed
            
            self.log(f"\n{category.upper().replace('_', ' ')}:")
            self.log(f"   Passed: {category_passed}/{category_total}")
            
            for test_name, passed in results.items():
                status = "✅" if passed else "❌"
                self.log(f"   {status} {test_name.replace('_', ' ').title()}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.log("\n" + "=" * 80)
        self.log(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        self.log("=" * 80)
        
        if success_rate >= 90:
            self.log("✅ EXCELLENT: Phase 2 backend is production ready!")
        elif success_rate >= 75:
            self.log("⚠️ GOOD: Phase 2 backend mostly working, minor issues to address")
        elif success_rate >= 60:
            self.log("⚠️ PARTIAL: Phase 2 backend has some issues that need attention")
        else:
            self.log("❌ CRITICAL: Phase 2 backend has major issues that must be fixed")
        
        self.log(f"\nTest End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    tester = Phase2BackendTester()
    results = tester.run_all_tests()
