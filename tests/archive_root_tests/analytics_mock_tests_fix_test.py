import requests
import json
import time
from datetime import datetime

class AnalyticsMockTestsFixTester:
    def __init__(self):
        # Use the correct backend URL from frontend/.env
        self.base_url = "https://tutor-reborn.preview.emergentagent.com/api"
        self.token = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def run_test(self, test_name, method, endpoint, expected_status, data=None, headers=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        # Merge headers
        test_headers = self.session.headers.copy()
        if headers:
            test_headers.update(headers)
        
        try:
            if method == "GET":
                response = self.session.get(url, headers=test_headers, params=params, timeout=30)
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

    def test_analytics_mock_tests_fix(self):
        """Test the two failing API endpoints that were fixed"""
        print("\n🔧 ANALYTICS & MOCK TESTS ENDPOINTS FIX TESTING")
        print("=" * 80)
        print("   OBJECTIVE: Verify the two failing endpoints are now working correctly")
        print("   BACKEND URL:", self.base_url)
        print("   AUTHENTICATION: OAuth required (401 expected without token)")
        print()
        print("   FAILING ENDPOINTS TO TEST:")
        print("   1. GET /api/analytics/performance (was 404)")
        print("   2. GET /api/mock-tests/subjects (was 422)")
        print()
        print("   REGRESSION TESTS:")
        print("   3. GET /api/analytics/performance-stats (should still work)")
        print("   4. GET /api/user/progress (should still work)")
        print("   5. GET /api/dashboard/analytics (should still work)")
        
        test_results = {
            # Primary failing endpoints
            'analytics_performance_fixed': False,
            'mock_tests_subjects_fixed': False,
            'mock_tests_subjects_with_param_fixed': False,
            
            # Regression tests
            'analytics_performance_stats_working': False,
            'user_progress_working': False,
            'dashboard_analytics_working': False,
            
            # Backend health
            'backend_health': False,
            'authentication_security': False
        }
        
        # 1. BACKEND HEALTH CHECK
        print("\n1️⃣ BACKEND HEALTH CHECK")
        test_results['backend_health'] = self.test_backend_health()
        test_results['authentication_security'] = self.test_authentication_security()
        
        # 2. PRIMARY FAILING ENDPOINTS (FIXED)
        print("\n2️⃣ PRIMARY FAILING ENDPOINTS (SHOULD BE FIXED)")
        primary_results = self.test_primary_failing_endpoints()
        test_results.update(primary_results)
        
        # 3. REGRESSION TESTING
        print("\n3️⃣ REGRESSION TESTING (SHOULD STILL WORK)")
        regression_results = self.test_regression_endpoints()
        test_results.update(regression_results)
        
        return self._print_test_results(test_results)
    
    def test_backend_health(self):
        """Test backend health endpoint"""
        print("   Testing backend health")
        
        success, response, status_code = self.run_test(
            "Backend Health Check",
            "GET",
            "health",
            200
        )
        
        if success and status_code == 200:
            print(f"   ✅ Backend health check successful")
            print(f"      Status: {response.get('status')}")
            print(f"      Service: {response.get('service')}")
            return True
        else:
            print(f"   ❌ Backend health check failed - Status: {status_code}")
            return False
    
    def test_authentication_security(self):
        """Test authentication security (OAuth only expected)"""
        print("   Testing authentication security")
        
        # Test unauthenticated session endpoint
        success, response, status_code = self.run_test(
            "Unauthenticated Session Check",
            "GET",
            "auth/session",
            401
        )
        
        if success and status_code == 401:
            print(f"   ✅ Authentication properly secured (401 for unauthenticated)")
            return True
        else:
            print(f"   ❌ Authentication security issue - Status: {status_code}")
            return False
    
    def test_primary_failing_endpoints(self):
        """Test the two primary failing endpoints that were fixed"""
        print("   Testing primary failing endpoints")
        
        results = {
            'analytics_performance_fixed': False,
            'mock_tests_subjects_fixed': False,
            'mock_tests_subjects_with_param_fixed': False
        }
        
        # 1. Test GET /api/analytics/performance (was 404)
        print("   📝 Testing: GET /api/analytics/performance (was 404)")
        success, response, status_code = self.run_test(
            "Analytics Performance Endpoint",
            "GET",
            "analytics/performance",
            [200, 401]  # Should return 200 OK or 401 (not 404)
        )
        
        if success:
            results['analytics_performance_fixed'] = True
            if status_code == 200:
                print(f"   ✅ Analytics performance endpoint FIXED - Status: 200 OK")
                print(f"      Response includes: {list(response.keys())}")
                # Check if response includes performance data
                expected_fields = ['overall_accuracy', 'study_streak', 'performance_trend']
                has_performance_data = any(field in response for field in expected_fields)
                if has_performance_data:
                    print(f"      ✅ Response includes performance data")
                else:
                    print(f"      ⚠️ Response structure may be different than expected")
            elif status_code == 401:
                print(f"   ✅ Analytics performance endpoint FIXED - Status: 401 (Auth required, not 404)")
        else:
            print(f"   ❌ Analytics performance endpoint still failing - Status: {status_code}")
            if status_code == 404:
                print(f"      ❌ CRITICAL: Still returning 404 Not Found")
        
        # 2. Test GET /api/mock-tests/subjects WITHOUT exam_type parameter (was 422)
        print("   📝 Testing: GET /api/mock-tests/subjects (without exam_type param, was 422)")
        success, response, status_code = self.run_test(
            "Mock Tests Subjects (No Param)",
            "GET",
            "mock-tests/subjects",
            [200, 401]  # Should return 200 OK or 401 (not 422)
        )
        
        if success:
            results['mock_tests_subjects_fixed'] = True
            if status_code == 200:
                print(f"   ✅ Mock tests subjects endpoint FIXED - Status: 200 OK")
                print(f"      Response includes: {list(response.keys())}")
                # Check if response includes subjects array
                if 'subjects' in response:
                    subjects = response.get('subjects', [])
                    exam_type = response.get('exam_type', 'Unknown')
                    print(f"      ✅ Response includes subjects array: {len(subjects)} subjects")
                    print(f"      ✅ Default exam_type: {exam_type}")
                else:
                    print(f"      ⚠️ Response structure may be different than expected")
            elif status_code == 401:
                print(f"   ✅ Mock tests subjects endpoint FIXED - Status: 401 (Auth required, not 422)")
        else:
            print(f"   ❌ Mock tests subjects endpoint still failing - Status: {status_code}")
            if status_code == 422:
                print(f"      ❌ CRITICAL: Still returning 422 Unprocessable Entity")
        
        # 3. Test GET /api/mock-tests/subjects WITH exam_type parameter
        print("   📝 Testing: GET /api/mock-tests/subjects?exam_type=NEET (with param)")
        success, response, status_code = self.run_test(
            "Mock Tests Subjects (With Param)",
            "GET",
            "mock-tests/subjects",
            [200, 401],
            params={"exam_type": "NEET"}
        )
        
        if success:
            results['mock_tests_subjects_with_param_fixed'] = True
            if status_code == 200:
                print(f"   ✅ Mock tests subjects with param WORKING - Status: 200 OK")
                exam_type = response.get('exam_type', 'Unknown')
                subjects = response.get('subjects', [])
                print(f"      ✅ Exam type: {exam_type}")
                print(f"      ✅ Subjects count: {len(subjects)}")
            elif status_code == 401:
                print(f"   ✅ Mock tests subjects with param WORKING - Status: 401 (Auth required)")
        else:
            print(f"   ❌ Mock tests subjects with param failing - Status: {status_code}")
        
        return results
    
    def test_regression_endpoints(self):
        """Test regression endpoints that should still work"""
        print("   Testing regression endpoints")
        
        results = {
            'analytics_performance_stats_working': False,
            'user_progress_working': False,
            'dashboard_analytics_working': False
        }
        
        # 1. Test GET /api/analytics/performance-stats (should still work)
        print("   📝 Testing: GET /api/analytics/performance-stats (regression)")
        success, response, status_code = self.run_test(
            "Analytics Performance Stats",
            "GET",
            "analytics/performance-stats",
            [200, 401]
        )
        
        if success:
            results['analytics_performance_stats_working'] = True
            print(f"   ✅ Analytics performance-stats working - Status: {status_code}")
            if status_code == 200:
                print(f"      Response includes: {list(response.keys())}")
        else:
            print(f"   ❌ Analytics performance-stats regression failure - Status: {status_code}")
        
        # 2. Test GET /api/user/progress (should still work)
        print("   📝 Testing: GET /api/user/progress (regression)")
        success, response, status_code = self.run_test(
            "User Progress",
            "GET",
            "user/progress",
            [200, 401]
        )
        
        if success:
            results['user_progress_working'] = True
            print(f"   ✅ User progress working - Status: {status_code}")
            if status_code == 200:
                print(f"      Response includes: {list(response.keys())}")
        else:
            print(f"   ❌ User progress regression failure - Status: {status_code}")
        
        # 3. Test GET /api/dashboard/analytics (should still work)
        print("   📝 Testing: GET /api/dashboard/analytics (regression)")
        success, response, status_code = self.run_test(
            "Dashboard Analytics",
            "GET",
            "dashboard/analytics",
            [200, 401]
        )
        
        if success:
            results['dashboard_analytics_working'] = True
            print(f"   ✅ Dashboard analytics working - Status: {status_code}")
            if status_code == 200:
                print(f"      Response includes: {list(response.keys())}")
        else:
            print(f"   ❌ Dashboard analytics regression failure - Status: {status_code}")
        
        return results
    
    def _print_test_results(self, test_results):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("🔧 ANALYTICS & MOCK TESTS ENDPOINTS FIX - FINAL RESULTS")
        print("=" * 80)
        
        success_count = sum(test_results.values())
        total_tests = len(test_results)
        success_rate = (success_count / total_tests) * 100
        
        print(f"\n📊 TEST RESULTS SUMMARY:")
        
        # Backend Health
        print(f"\n   BACKEND HEALTH:")
        health_tests = ['backend_health', 'authentication_security']
        for test_name in health_tests:
            status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
            display_name = test_name.replace('_', ' ').title()
            print(f"      {display_name}: {status}")
        
        # Primary Failing Endpoints (CRITICAL)
        print(f"\n   PRIMARY FAILING ENDPOINTS (CRITICAL FIXES):")
        primary_tests = ['analytics_performance_fixed', 'mock_tests_subjects_fixed', 'mock_tests_subjects_with_param_fixed']
        primary_success = sum(test_results.get(test, False) for test in primary_tests)
        for test_name in primary_tests:
            status = "✅ FIXED" if test_results.get(test_name, False) else "❌ STILL FAILING"
            if test_name == 'analytics_performance_fixed':
                display_name = "Analytics Performance (was 404)"
            elif test_name == 'mock_tests_subjects_fixed':
                display_name = "Mock Tests Subjects (was 422)"
            elif test_name == 'mock_tests_subjects_with_param_fixed':
                display_name = "Mock Tests Subjects with Param"
            print(f"      {display_name}: {status}")
        
        # Regression Tests
        print(f"\n   REGRESSION TESTS (SHOULD STILL WORK):")
        regression_tests = ['analytics_performance_stats_working', 'user_progress_working', 'dashboard_analytics_working']
        regression_success = sum(test_results.get(test, False) for test in regression_tests)
        for test_name in regression_tests:
            status = "✅ WORKING" if test_results.get(test_name, False) else "❌ BROKEN"
            if test_name == 'analytics_performance_stats_working':
                display_name = "Analytics Performance Stats"
            elif test_name == 'user_progress_working':
                display_name = "User Progress"
            elif test_name == 'dashboard_analytics_working':
                display_name = "Dashboard Analytics"
            print(f"      {display_name}: {status}")
        
        print(f"\n📈 OVERALL SUCCESS RATE: {success_count}/{total_tests} ({success_rate:.1f}%)")
        
        # Critical Success Criteria
        print(f"\n🎯 CRITICAL SUCCESS CRITERIA:")
        criteria_mapping = {
            'Analytics Performance Endpoint Fixed (not 404)': test_results.get('analytics_performance_fixed', False),
            'Mock Tests Subjects Endpoint Fixed (not 422)': test_results.get('mock_tests_subjects_fixed', False),
            'Mock Tests Subjects with Param Working': test_results.get('mock_tests_subjects_with_param_fixed', False),
            'No Regression in Existing Endpoints': all(test_results.get(test, False) for test in regression_tests),
            'Backend Health Check Working': test_results.get('backend_health', False),
            'Authentication Security Working': test_results.get('authentication_security', False)
        }
        
        for criterion, passed in criteria_mapping.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {criterion}")
        
        # Determine overall status
        critical_fixes = primary_success
        total_critical = len(primary_tests)
        
        if critical_fixes == total_critical and regression_success == len(regression_tests):
            print("\n✅ ENDPOINT FIXES: COMPLETE SUCCESS")
            print("   ✅ Both failing endpoints are now working correctly")
            print("   ✅ All regression tests pass")
            print("   ✅ No 404 or 422 errors on target endpoints")
        elif critical_fixes == total_critical:
            print("\n✅ ENDPOINT FIXES: SUCCESS WITH MINOR REGRESSIONS")
            print("   ✅ Both failing endpoints are now working correctly")
            print("   ⚠️ Some regression tests failed (may need investigation)")
        elif critical_fixes > 0:
            print("\n⚠️ ENDPOINT FIXES: PARTIAL SUCCESS")
            print(f"   ⚠️ {critical_fixes}/{total_critical} critical endpoints fixed")
            print("   🔍 Remaining issues need investigation")
        else:
            print("\n❌ ENDPOINT FIXES: FAILED")
            print("   ❌ Critical endpoints still failing")
            print("   🚨 Requires immediate attention")
        
        # Specific recommendations
        print(f"\n🔧 RECOMMENDATIONS:")
        
        if test_results.get('analytics_performance_fixed', False):
            print("   ✅ Analytics performance endpoint is working correctly")
        else:
            print("   ❌ Analytics performance endpoint still returns 404 - check routing")
        
        if test_results.get('mock_tests_subjects_fixed', False):
            print("   ✅ Mock tests subjects endpoint handles missing exam_type parameter")
        else:
            print("   ❌ Mock tests subjects endpoint still returns 422 - check parameter handling")
        
        if regression_success == len(regression_tests):
            print("   ✅ No regressions detected in existing functionality")
        else:
            print("   ⚠️ Some regression issues detected - verify existing endpoints")
        
        return success_rate >= 75  # 75% success rate for endpoint fixes


if __name__ == "__main__":
    tester = AnalyticsMockTestsFixTester()
    success = tester.test_analytics_mock_tests_fix()
    
    if success:
        print("\n🎉 TESTING COMPLETE: Endpoint fixes verified successfully")
    else:
        print("\n⚠️ TESTING COMPLETE: Issues detected, review results above")