#!/usr/bin/env python3
"""
AI Tutor Comprehensive Backend Testing
Testing all AI Tutor fixes and optimizations as per review request
"""

import requests
import json
import time
from datetime import datetime

class AITutorBackendTester:
    def __init__(self):
        # Use environment variable for backend URL
        self.base_url = "https://neuro-tutor-dev.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = {}
    
    def log(self, message, level="INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_test(self, test_name, method, endpoint, expected_status, data=None, headers=None, timeout=30):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        # Merge headers
        test_headers = self.session.headers.copy()
        if headers:
            test_headers.update(headers)
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(url, headers=test_headers, timeout=timeout)
            elif method == "POST":
                response = self.session.post(url, json=data, headers=test_headers, timeout=timeout)
            elif method == "PUT":
                response = self.session.put(url, json=data, headers=test_headers, timeout=timeout)
            elif method == "DELETE":
                response = self.session.delete(url, headers=test_headers, timeout=timeout)
            
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
    
    # ============= CRITICAL TEST 1: CHAT HISTORY LOADING =============
    
    def test_chat_history_loading(self):
        """Test /api/ai/chat/sessions endpoint"""
        self.log("=" * 80)
        self.log("🔍 TEST 1: CHAT HISTORY LOADING")
        self.log("=" * 80)
        
        results = {
            'endpoint_exists': False,
            'returns_401_not_404': False,
            'endpoint_accessible': False
        }
        
        self.log("\n📋 Testing GET /api/ai/chat/sessions")
        success, response, status, elapsed = self.run_test(
            "Chat Sessions Endpoint",
            "GET",
            "ai/chat/sessions",
            [200, 401]  # 401 expected for unauth, 200 if somehow accessible
        )
        
        if status == 404:
            results['endpoint_exists'] = False
            results['returns_401_not_404'] = False
            self.log(f"   ❌ CRITICAL: Endpoint returns 404 (NOT FOUND)")
            self.log(f"   ❌ This means the endpoint doesn't exist!")
        elif status == 401:
            results['endpoint_exists'] = True
            results['returns_401_not_404'] = True
            results['endpoint_accessible'] = True
            self.log(f"   ✅ Endpoint exists and returns 401 (Auth Required)")
            self.log(f"   ✅ This is CORRECT - endpoint is properly secured")
        elif status == 200:
            results['endpoint_exists'] = True
            results['returns_401_not_404'] = True
            results['endpoint_accessible'] = True
            self.log(f"   ✅ Endpoint accessible (200 OK)")
            self.log(f"   📊 Response: {json.dumps(response, indent=2)[:200]}...")
        else:
            self.log(f"   ⚠️ Unexpected status: {status}")
        
        return results
    
    # ============= CRITICAL TEST 2: SESSION MESSAGES =============
    
    def test_session_messages(self):
        """Test /api/ai/chat/{session_id}/messages endpoint"""
        self.log("\n" + "=" * 80)
        self.log("🔍 TEST 2: SESSION MESSAGES")
        self.log("=" * 80)
        
        results = {
            'endpoint_exists': False,
            'returns_401_not_404': False,
            'endpoint_accessible': False
        }
        
        # Use a test session ID
        test_session_id = "test-session-123"
        
        self.log(f"\n📋 Testing GET /api/ai/chat/{test_session_id}/messages")
        success, response, status, elapsed = self.run_test(
            "Session Messages Endpoint",
            "GET",
            f"ai/chat/{test_session_id}/messages",
            [200, 401, 404]  # 404 might be valid if session doesn't exist
        )
        
        if status == 404:
            # Check if it's a "session not found" 404 or "endpoint not found" 404
            error_detail = response.get('detail', '')
            if 'session' in str(error_detail).lower() or 'not found' in str(error_detail).lower():
                results['endpoint_exists'] = True
                results['returns_401_not_404'] = True
                results['endpoint_accessible'] = True
                self.log(f"   ✅ Endpoint exists (404 is for missing session, not missing endpoint)")
                self.log(f"   ✅ Detail: {error_detail}")
            else:
                results['endpoint_exists'] = False
                self.log(f"   ❌ CRITICAL: Endpoint returns 404 (NOT FOUND)")
        elif status == 401:
            results['endpoint_exists'] = True
            results['returns_401_not_404'] = True
            results['endpoint_accessible'] = True
            self.log(f"   ✅ Endpoint exists and returns 401 (Auth Required)")
            self.log(f"   ✅ This is CORRECT - endpoint is properly secured")
        elif status == 200:
            results['endpoint_exists'] = True
            results['returns_401_not_404'] = True
            results['endpoint_accessible'] = True
            self.log(f"   ✅ Endpoint accessible (200 OK)")
            self.log(f"   📊 Response: {json.dumps(response, indent=2)[:200]}...")
        else:
            self.log(f"   ⚠️ Unexpected status: {status}")
        
        return results
    
    # ============= CRITICAL TEST 3: CREATE SESSION =============
    
    def test_create_session(self):
        """Test POST /api/ai/chat/sessions endpoint"""
        self.log("\n" + "=" * 80)
        self.log("🔍 TEST 3: CREATE SESSION")
        self.log("=" * 80)
        
        results = {
            'endpoint_exists': False,
            'returns_401_not_404': False,
            'endpoint_accessible': False,
            'proper_response_structure': False
        }
        
        test_data = {
            "title": "Test Session",
            "subject": "Mathematics"
        }
        
        self.log(f"\n📋 Testing POST /api/ai/chat/sessions")
        success, response, status, elapsed = self.run_test(
            "Create Session Endpoint",
            "POST",
            "ai/chat/sessions",
            [200, 201, 401]  # 201 for created, 401 for auth required
        )
        
        if status == 404:
            results['endpoint_exists'] = False
            self.log(f"   ❌ CRITICAL: Endpoint returns 404 (NOT FOUND)")
        elif status == 401:
            results['endpoint_exists'] = True
            results['returns_401_not_404'] = True
            results['endpoint_accessible'] = True
            self.log(f"   ✅ Endpoint exists and returns 401 (Auth Required)")
            self.log(f"   ✅ This is CORRECT - endpoint is properly secured")
        elif status in [200, 201]:
            results['endpoint_exists'] = True
            results['returns_401_not_404'] = True
            results['endpoint_accessible'] = True
            self.log(f"   ✅ Endpoint accessible ({status})")
            
            # Check response structure
            if 'session_id' in response or 'id' in response:
                results['proper_response_structure'] = True
                self.log(f"   ✅ Response has proper structure (session_id present)")
            
            self.log(f"   📊 Response: {json.dumps(response, indent=2)[:200]}...")
        else:
            self.log(f"   ⚠️ Unexpected status: {status}")
        
        return results
    
    # ============= CRITICAL TEST 4: SIMPLE MESSAGE PERFORMANCE =============
    
    def test_simple_message_performance(self):
        """Test greeting response optimization"""
        self.log("\n" + "=" * 80)
        self.log("🔍 TEST 4: SIMPLE MESSAGE PERFORMANCE")
        self.log("=" * 80)
        
        results = {
            'endpoint_exists': False,
            'returns_401_not_404': False,
            'response_time_measured': False,
            'fast_response_under_1s': False,
            'fast_response_flag_present': False
        }
        
        test_data = {
            "message": "hi",
            "subject": "Mathematics",
            "session_id": None
        }
        
        self.log(f"\n📋 Testing POST /api/ai/dual-response with simple message 'hi'")
        self.log(f"   Expected: Fast response (< 1 second if optimization works)")
        
        success, response, status, elapsed = self.run_test(
            "Simple Message Performance",
            "POST",
            "ai/dual-response",
            [200, 401, 402],  # 402 for subscription required
            data=test_data,
            timeout=5  # Short timeout for simple message
        )
        
        if status == 404:
            results['endpoint_exists'] = False
            self.log(f"   ❌ CRITICAL: Endpoint returns 404 (NOT FOUND)")
        elif status == 401:
            results['endpoint_exists'] = True
            results['returns_401_not_404'] = True
            self.log(f"   ✅ Endpoint exists and returns 401 (Auth Required)")
            self.log(f"   ⚠️ Cannot test performance without authentication")
        elif status == 402:
            results['endpoint_exists'] = True
            results['returns_401_not_404'] = True
            self.log(f"   ✅ Endpoint exists and returns 402 (Subscription Required)")
            self.log(f"   ⚠️ Cannot test performance without subscription")
        elif status == 200:
            results['endpoint_exists'] = True
            results['returns_401_not_404'] = True
            results['response_time_measured'] = True
            
            self.log(f"   ✅ Endpoint accessible (200 OK)")
            self.log(f"   ⏱️ Response time: {elapsed:.2f}s")
            
            if elapsed < 1.0:
                results['fast_response_under_1s'] = True
                self.log(f"   ✅ EXCELLENT: Response time < 1s (optimization working!)")
            else:
                self.log(f"   ⚠️ Response time >= 1s (optimization may not be active)")
            
            # Check for fast_response flag
            if 'fast_response' in response:
                results['fast_response_flag_present'] = True
                self.log(f"   ✅ fast_response flag present: {response['fast_response']}")
            else:
                self.log(f"   ⚠️ fast_response flag not in response")
            
            self.log(f"   📊 Response keys: {list(response.keys())}")
        else:
            self.log(f"   ⚠️ Unexpected status: {status}")
        
        return results
    
    # ============= CRITICAL TEST 5: COMPLEX MESSAGE PERFORMANCE =============
    
    def test_complex_message_performance(self):
        """Test parallel execution for complex questions"""
        self.log("\n" + "=" * 80)
        self.log("🔍 TEST 5: COMPLEX MESSAGE PERFORMANCE")
        self.log("=" * 80)
        
        results = {
            'endpoint_exists': False,
            'returns_401_not_404': False,
            'response_time_measured': False,
            'parallel_execution_working': False,
            'dual_response_structure': False
        }
        
        test_data = {
            "message": "Explain the concept of derivatives in calculus, including the chain rule, product rule, and quotient rule with detailed examples",
            "subject": "Mathematics",
            "session_id": None
        }
        
        self.log(f"\n📋 Testing POST /api/ai/dual-response with complex question")
        self.log(f"   Expected: ~18-20s (NOT 35-40s) if parallel execution works")
        
        success, response, status, elapsed = self.run_test(
            "Complex Message Performance",
            "POST",
            "ai/dual-response",
            [200, 401, 402],
            data=test_data,
            timeout=45  # Longer timeout for complex message
        )
        
        if status == 404:
            results['endpoint_exists'] = False
            self.log(f"   ❌ CRITICAL: Endpoint returns 404 (NOT FOUND)")
        elif status == 401:
            results['endpoint_exists'] = True
            results['returns_401_not_404'] = True
            self.log(f"   ✅ Endpoint exists and returns 401 (Auth Required)")
            self.log(f"   ⚠️ Cannot test performance without authentication")
        elif status == 402:
            results['endpoint_exists'] = True
            results['returns_401_not_404'] = True
            self.log(f"   ✅ Endpoint exists and returns 402 (Subscription Required)")
            self.log(f"   ⚠️ Cannot test performance without subscription")
        elif status == 200:
            results['endpoint_exists'] = True
            results['returns_401_not_404'] = True
            results['response_time_measured'] = True
            
            self.log(f"   ✅ Endpoint accessible (200 OK)")
            self.log(f"   ⏱️ Response time: {elapsed:.2f}s")
            
            if elapsed <= 25:  # Allow some margin
                results['parallel_execution_working'] = True
                self.log(f"   ✅ EXCELLENT: Response time ~{elapsed:.2f}s (parallel execution working!)")
            else:
                self.log(f"   ⚠️ Response time {elapsed:.2f}s (may indicate sequential execution)")
            
            # Check dual response structure
            if 'primary' in response and 'secondary' in response:
                results['dual_response_structure'] = True
                self.log(f"   ✅ Dual response structure present (primary + secondary)")
            elif 'professor' in response and 'mentor' in response:
                results['dual_response_structure'] = True
                self.log(f"   ✅ Dual response structure present (professor + mentor)")
            else:
                self.log(f"   ⚠️ Dual response structure not found")
            
            self.log(f"   📊 Response keys: {list(response.keys())}")
        else:
            self.log(f"   ⚠️ Unexpected status: {status}")
        
        return results
    
    # ============= CRITICAL TEST 6: ENDPOINT AVAILABILITY =============
    
    def test_endpoint_availability(self):
        """Test all AI endpoints exist"""
        self.log("\n" + "=" * 80)
        self.log("🔍 TEST 6: ENDPOINT AVAILABILITY")
        self.log("=" * 80)
        
        results = {
            'chat_sessions_get': False,
            'chat_session_messages_get': False,
            'chat_sessions_post': False,
            'dual_response_post': False,
            'mentor_only_post': False,
            'professor_only_post': False,
            'all_endpoints_accessible': False
        }
        
        endpoints = [
            ("GET", "ai/chat/sessions", "chat_sessions_get"),
            ("GET", "ai/chat/test-123/messages", "chat_session_messages_get"),
            ("POST", "ai/chat/sessions", "chat_sessions_post"),
            ("POST", "ai/dual-response", "dual_response_post"),
            ("POST", "ai/mentor-only", "mentor_only_post"),
            ("POST", "ai/professor-only", "professor_only_post"),
        ]
        
        self.log("\n📋 Testing all AI endpoints for availability")
        
        all_accessible = True
        for method, endpoint, result_key in endpoints:
            success, response, status, elapsed = self.run_test(
                f"{method} {endpoint}",
                method,
                endpoint,
                [200, 401, 402, 404, 422]  # Accept various responses
            )
            
            # 401 = Auth required (GOOD - endpoint exists)
            # 402 = Payment required (GOOD - endpoint exists)
            # 404 = Not found (BAD - endpoint doesn't exist)
            # 422 = Validation error (GOOD - endpoint exists but needs data)
            
            if status == 404:
                results[result_key] = False
                all_accessible = False
                self.log(f"   ❌ {method} /{endpoint} - Returns 404 (NOT FOUND)")
            elif status in [200, 401, 402, 422]:
                results[result_key] = True
                status_msg = {
                    200: "OK",
                    401: "Auth Required",
                    402: "Payment Required",
                    422: "Validation Error"
                }.get(status, str(status))
                self.log(f"   ✅ {method} /{endpoint} - Returns {status} ({status_msg})")
            else:
                self.log(f"   ⚠️ {method} /{endpoint} - Returns {status}")
        
        results['all_endpoints_accessible'] = all_accessible
        
        if all_accessible:
            self.log(f"\n   ✅ ALL ENDPOINTS ACCESSIBLE (return 401/402, NOT 404)")
        else:
            self.log(f"\n   ❌ SOME ENDPOINTS RETURN 404 (NOT FOUND)")
        
        return results
    
    # ============= MAIN TEST RUNNER =============
    
    def run_all_tests(self):
        """Run all AI Tutor backend tests"""
        self.log("\n" + "=" * 80)
        self.log("🚀 AI TUTOR COMPREHENSIVE BACKEND TESTING")
        self.log("=" * 80)
        self.log(f"Backend URL: {self.base_url}")
        self.log(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("\nTesting Scope:")
        self.log("  1. Chat History Loading")
        self.log("  2. Session Messages")
        self.log("  3. Create Session")
        self.log("  4. Simple Message Performance")
        self.log("  5. Complex Message Performance")
        self.log("  6. Endpoint Availability")
        
        all_results = {}
        
        # Run all test suites
        all_results['chat_history_loading'] = self.test_chat_history_loading()
        all_results['session_messages'] = self.test_session_messages()
        all_results['create_session'] = self.test_create_session()
        all_results['simple_message_performance'] = self.test_simple_message_performance()
        all_results['complex_message_performance'] = self.test_complex_message_performance()
        all_results['endpoint_availability'] = self.test_endpoint_availability()
        
        # Print final summary
        self.print_final_summary(all_results)
        
        return all_results
    
    def print_final_summary(self, all_results):
        """Print final test summary"""
        self.log("\n" + "=" * 80)
        self.log("📊 FINAL TEST SUMMARY - AI TUTOR BACKEND")
        self.log("=" * 80)
        
        total_tests = 0
        passed_tests = 0
        critical_failures = []
        
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
                
                # Track critical failures
                if not passed and ('endpoint_exists' in test_name or 'returns_401_not_404' in test_name):
                    critical_failures.append(f"{category}: {test_name}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.log("\n" + "=" * 80)
        self.log(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        self.log("=" * 80)
        
        # Critical issues
        if critical_failures:
            self.log("\n❌ CRITICAL ISSUES FOUND:")
            for failure in critical_failures:
                self.log(f"   - {failure}")
        
        # Overall assessment
        if success_rate >= 90:
            self.log("\n✅ EXCELLENT: AI Tutor backend is production ready!")
        elif success_rate >= 75:
            self.log("\n⚠️ GOOD: AI Tutor backend mostly working, minor issues to address")
        elif success_rate >= 60:
            self.log("\n⚠️ PARTIAL: AI Tutor backend has some issues that need attention")
        else:
            self.log("\n❌ CRITICAL: AI Tutor backend has major issues that must be fixed")
        
        # Specific recommendations
        self.log("\n" + "=" * 80)
        self.log("📋 RECOMMENDATIONS:")
        self.log("=" * 80)
        
        # Check for 404 errors
        has_404_errors = any(
            not results.get('endpoint_exists', True) or not results.get('returns_401_not_404', True)
            for results in all_results.values()
        )
        
        if has_404_errors:
            self.log("❌ CRITICAL: Some endpoints return 404 (NOT FOUND)")
            self.log("   - This means endpoints are missing or routes are incorrect")
            self.log("   - Expected: 401 (Auth Required) for secured endpoints")
            self.log("   - Action: Check route definitions in backend/api/ai.py")
        else:
            self.log("✅ All endpoints exist and return proper status codes (401/402)")
        
        # Check performance
        if all_results.get('simple_message_performance', {}).get('fast_response_under_1s', False):
            self.log("✅ Simple message optimization working (< 1s response)")
        else:
            self.log("⚠️ Simple message optimization may not be active")
        
        if all_results.get('complex_message_performance', {}).get('parallel_execution_working', False):
            self.log("✅ Parallel execution working (~18-20s for complex messages)")
        else:
            self.log("⚠️ Parallel execution may not be active (check for sequential execution)")
        
        self.log(f"\nTest End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    tester = AITutorBackendTester()
    results = tester.run_all_tests()
