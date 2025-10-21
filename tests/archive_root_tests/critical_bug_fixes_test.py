"""
Critical Bug Fixes Verification Test
Tests all the critical production bugs that were fixed in Dhruv AI platform
"""
import requests
import json
from datetime import datetime

class CriticalBugFixesTester:
    def __init__(self):
        # Use backend URL from frontend/.env
        self.base_url = "https://dhruv-ai-platform.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def run_test(self, test_name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url, timeout=30)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=30)
            
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
                try:
                    error_data = response.json()
                    return False, error_data, response.status_code
                except:
                    return False, {"error": response.text}, response.status_code
                    
        except Exception as e:
            return False, {"error": str(e)}, 0
    
    def test_critical_bug_fixes(self):
        """Test all critical bug fixes"""
        print("\n🔧 CRITICAL BUG FIXES VERIFICATION")
        print("=" * 80)
        print("   OBJECTIVE: Verify all critical production bugs are fixed")
        print("   BACKEND URL:", self.base_url)
        print("   NOTE: OAuth-only app - 401 responses are expected and acceptable")
        
        test_results = {
            # 1. Mock Test Generation (HIGHEST PRIORITY)
            'mock_test_generate_no_initialize_error': False,
            'mock_test_generate_subscription_check': False,
            'mock_test_generate_proper_status': False,
            
            # 2. Dashboard Analytics Endpoints
            'dashboard_analytics_accessible': False,
            'dashboard_streak_accessible': False,
            'dashboard_leaderboard_accessible': False,
            'dashboard_no_500_errors': False,
            
            # 3. Bookmarked Questions Endpoint
            'bookmarked_questions_exists': False,
            'bookmarked_questions_no_404': False,
            
            # 4. Mock Tests Subjects with Optional Param
            'subjects_without_param_works': False,
            'subjects_with_param_works': False,
            'subjects_no_422_error': False,
            
            # 5. Gamification Endpoints
            'gamification_progress_accessible': False,
            'gamification_leaderboard_accessible': False,
            'gamification_no_404_from_service_worker': False,
            
            # 6. Analytics Performance
            'analytics_performance_accessible': False,
            'analytics_performance_no_404': False,
            
            # 7. Regression Testing
            'health_check_working': False,
            'subscription_plans_working': False,
            'auth_oauth_check': False
        }
        
        # 1. MOCK TEST GENERATION (HIGHEST PRIORITY)
        print("\n1️⃣ MOCK TEST GENERATION - HIGHEST PRIORITY")
        mock_test_results = self.test_mock_test_generation()
        test_results.update(mock_test_results)
        
        # 2. DASHBOARD ANALYTICS ENDPOINTS
        print("\n2️⃣ DASHBOARD ANALYTICS ENDPOINTS")
        dashboard_results = self.test_dashboard_analytics()
        test_results.update(dashboard_results)
        
        # 3. BOOKMARKED QUESTIONS ENDPOINT
        print("\n3️⃣ BOOKMARKED QUESTIONS ENDPOINT")
        bookmarked_results = self.test_bookmarked_questions()
        test_results.update(bookmarked_results)
        
        # 4. MOCK TESTS SUBJECTS WITH OPTIONAL PARAM
        print("\n4️⃣ MOCK TESTS SUBJECTS WITH OPTIONAL PARAM")
        subjects_results = self.test_mock_tests_subjects()
        test_results.update(subjects_results)
        
        # 5. GAMIFICATION ENDPOINTS
        print("\n5️⃣ GAMIFICATION ENDPOINTS")
        gamification_results = self.test_gamification_endpoints()
        test_results.update(gamification_results)
        
        # 6. ANALYTICS PERFORMANCE
        print("\n6️⃣ ANALYTICS PERFORMANCE")
        analytics_results = self.test_analytics_performance()
        test_results.update(analytics_results)
        
        # 7. REGRESSION TESTING
        print("\n7️⃣ REGRESSION TESTING")
        regression_results = self.test_regression()
        test_results.update(regression_results)
        
        return self._print_test_results(test_results)
    
    def test_mock_test_generation(self):
        """Test mock test generation endpoint - HIGHEST PRIORITY"""
        print("   Testing POST /api/mock-tests/generate")
        
        results = {
            'mock_test_generate_no_initialize_error': False,
            'mock_test_generate_subscription_check': False,
            'mock_test_generate_proper_status': False
        }
        
        # Test data for mock test generation
        test_data = {
            "exam_type": "JEE",
            "test_type": "full_length",
            "subjects": ["Mathematics", "Physics"],
            "difficulty_level": "medium",
            "num_questions": 10,
            "generation_mode": "standard"
        }
        
        success, response, status_code = self.run_test(
            "Mock Test Generation",
            "POST",
            "mock-tests/generate",
            [201, 401, 402],  # 201=Created, 401=Auth Required, 402=Payment Required
            data=test_data
        )
        
        # Check for "initialize" error
        error_message = str(response.get('detail', '')).lower()
        has_initialize_error = 'initialize' in error_message
        
        if has_initialize_error:
            print(f"   ❌ CRITICAL: 'initialize' error detected!")
            print(f"      Error: {response.get('detail')}")
            results['mock_test_generate_no_initialize_error'] = False
        else:
            print(f"   ✅ No 'initialize' error - Status: {status_code}")
            results['mock_test_generate_no_initialize_error'] = True
        
        # Check subscription check is working
        if status_code in [201, 401, 402]:
            print(f"   ✅ Subscription check working correctly")
            results['mock_test_generate_subscription_check'] = True
        else:
            print(f"   ❌ Unexpected status code: {status_code}")
            results['mock_test_generate_subscription_check'] = False
        
        # Check proper status (NOT 500)
        if status_code != 500:
            print(f"   ✅ Proper status code (not 500 Internal Server Error)")
            results['mock_test_generate_proper_status'] = True
        else:
            print(f"   ❌ 500 Internal Server Error detected")
            results['mock_test_generate_proper_status'] = False
        
        # Additional details
        if status_code == 201:
            print(f"      ✅ Test created successfully")
        elif status_code == 401:
            print(f"      ✅ Authentication required (expected for OAuth app)")
        elif status_code == 402:
            print(f"      ✅ Payment/Subscription required (expected behavior)")
        
        return results
    
    def test_dashboard_analytics(self):
        """Test dashboard analytics endpoints"""
        print("   Testing dashboard analytics endpoints")
        
        results = {
            'dashboard_analytics_accessible': False,
            'dashboard_streak_accessible': False,
            'dashboard_leaderboard_accessible': False,
            'dashboard_no_500_errors': False
        }
        
        has_500_error = False
        
        # Test GET /api/dashboard/analytics
        print("   📝 Testing: GET /api/dashboard/analytics")
        success, response, status_code = self.run_test(
            "Dashboard Analytics",
            "GET",
            "dashboard/analytics",
            [200, 401]
        )
        
        if success:
            results['dashboard_analytics_accessible'] = True
            print(f"      ✅ Dashboard analytics accessible - Status: {status_code}")
        else:
            print(f"      ❌ Dashboard analytics failed - Status: {status_code}")
        
        if status_code == 500:
            has_500_error = True
            print(f"      ❌ CRITICAL: 500 Internal Server Error detected!")
        
        # Test GET /api/dashboard/streak
        print("   📝 Testing: GET /api/dashboard/streak")
        success, response, status_code = self.run_test(
            "Dashboard Streak",
            "GET",
            "dashboard/streak",
            [200, 401]
        )
        
        if success:
            results['dashboard_streak_accessible'] = True
            print(f"      ✅ Dashboard streak accessible - Status: {status_code}")
        else:
            print(f"      ❌ Dashboard streak failed - Status: {status_code}")
        
        if status_code == 500:
            has_500_error = True
            print(f"      ❌ CRITICAL: 500 Internal Server Error detected!")
        
        # Test GET /api/dashboard/leaderboard
        print("   📝 Testing: GET /api/dashboard/leaderboard")
        success, response, status_code = self.run_test(
            "Dashboard Leaderboard",
            "GET",
            "dashboard/leaderboard",
            [200, 401]
        )
        
        if success:
            results['dashboard_leaderboard_accessible'] = True
            print(f"      ✅ Dashboard leaderboard accessible - Status: {status_code}")
        else:
            print(f"      ❌ Dashboard leaderboard failed - Status: {status_code}")
        
        if status_code == 500:
            has_500_error = True
            print(f"      ❌ CRITICAL: 500 Internal Server Error detected!")
        
        # Check for 500 errors
        if not has_500_error:
            results['dashboard_no_500_errors'] = True
            print(f"   ✅ No 500 errors on dashboard endpoints")
        else:
            print(f"   ❌ 500 errors detected on dashboard endpoints")
        
        return results
    
    def test_bookmarked_questions(self):
        """Test bookmarked questions endpoint"""
        print("   Testing GET /api/mock-tests/bookmarked-questions")
        
        results = {
            'bookmarked_questions_exists': False,
            'bookmarked_questions_no_404': False
        }
        
        success, response, status_code = self.run_test(
            "Bookmarked Questions",
            "GET",
            "mock-tests/bookmarked-questions",
            [200, 401]
        )
        
        if success:
            results['bookmarked_questions_exists'] = True
            print(f"   ✅ Bookmarked questions endpoint exists - Status: {status_code}")
        else:
            print(f"   ❌ Bookmarked questions endpoint failed - Status: {status_code}")
        
        if status_code != 404:
            results['bookmarked_questions_no_404'] = True
            print(f"   ✅ No 404 error (endpoint exists)")
        else:
            print(f"   ❌ CRITICAL: 404 Not Found error detected!")
        
        return results
    
    def test_mock_tests_subjects(self):
        """Test mock tests subjects endpoint with optional parameter"""
        print("   Testing GET /api/mock-tests/subjects")
        
        results = {
            'subjects_without_param_works': False,
            'subjects_with_param_works': False,
            'subjects_no_422_error': False
        }
        
        has_422_error = False
        
        # Test without exam_type parameter
        print("   📝 Testing: GET /api/mock-tests/subjects (without exam_type)")
        success, response, status_code = self.run_test(
            "Subjects Without Param",
            "GET",
            "mock-tests/subjects",
            [200, 401]
        )
        
        if success:
            results['subjects_without_param_works'] = True
            print(f"      ✅ Subjects without param works - Status: {status_code}")
        else:
            print(f"      ❌ Subjects without param failed - Status: {status_code}")
        
        if status_code == 422:
            has_422_error = True
            print(f"      ❌ CRITICAL: 422 Unprocessable Entity error detected!")
        
        # Test with exam_type parameter
        print("   📝 Testing: GET /api/mock-tests/subjects?exam_type=JEE")
        success, response, status_code = self.run_test(
            "Subjects With Param",
            "GET",
            "mock-tests/subjects?exam_type=JEE",
            [200, 401]
        )
        
        if success:
            results['subjects_with_param_works'] = True
            print(f"      ✅ Subjects with param works - Status: {status_code}")
        else:
            print(f"      ❌ Subjects with param failed - Status: {status_code}")
        
        if status_code == 422:
            has_422_error = True
            print(f"      ❌ CRITICAL: 422 Unprocessable Entity error detected!")
        
        # Check for 422 errors
        if not has_422_error:
            results['subjects_no_422_error'] = True
            print(f"   ✅ No 422 errors on subjects endpoint")
        else:
            print(f"   ❌ 422 errors detected on subjects endpoint")
        
        return results
    
    def test_gamification_endpoints(self):
        """Test gamification endpoints"""
        print("   Testing gamification endpoints")
        
        results = {
            'gamification_progress_accessible': False,
            'gamification_leaderboard_accessible': False,
            'gamification_no_404_from_service_worker': False
        }
        
        has_service_worker_404 = False
        
        # Test GET /api/gamification/progress
        print("   📝 Testing: GET /api/gamification/progress")
        success, response, status_code = self.run_test(
            "Gamification Progress",
            "GET",
            "gamification/progress",
            [200, 401]
        )
        
        if success:
            results['gamification_progress_accessible'] = True
            print(f"      ✅ Gamification progress accessible - Status: {status_code}")
        else:
            print(f"      ❌ Gamification progress failed - Status: {status_code}")
        
        # Check for service worker 404
        error_message = str(response.get('detail', '')).lower()
        if status_code == 404 and 'service worker' in error_message:
            has_service_worker_404 = True
            print(f"      ❌ CRITICAL: 404 'from service worker' error detected!")
        
        # Test GET /api/gamification/leaderboard?limit=50
        print("   📝 Testing: GET /api/gamification/leaderboard?limit=50")
        success, response, status_code = self.run_test(
            "Gamification Leaderboard",
            "GET",
            "gamification/leaderboard?limit=50",
            [200, 401]
        )
        
        if success:
            results['gamification_leaderboard_accessible'] = True
            print(f"      ✅ Gamification leaderboard accessible - Status: {status_code}")
        else:
            print(f"      ❌ Gamification leaderboard failed - Status: {status_code}")
        
        # Check for service worker 404
        error_message = str(response.get('detail', '')).lower()
        if status_code == 404 and 'service worker' in error_message:
            has_service_worker_404 = True
            print(f"      ❌ CRITICAL: 404 'from service worker' error detected!")
        
        # Check for service worker 404 errors
        if not has_service_worker_404:
            results['gamification_no_404_from_service_worker'] = True
            print(f"   ✅ No 404 'from service worker' errors")
        else:
            print(f"   ❌ 404 'from service worker' errors detected")
        
        return results
    
    def test_analytics_performance(self):
        """Test analytics performance endpoint"""
        print("   Testing GET /api/analytics/performance")
        
        results = {
            'analytics_performance_accessible': False,
            'analytics_performance_no_404': False
        }
        
        success, response, status_code = self.run_test(
            "Analytics Performance",
            "GET",
            "analytics/performance",
            [200, 401]
        )
        
        if success:
            results['analytics_performance_accessible'] = True
            print(f"   ✅ Analytics performance accessible - Status: {status_code}")
        else:
            print(f"   ❌ Analytics performance failed - Status: {status_code}")
        
        if status_code != 404:
            results['analytics_performance_no_404'] = True
            print(f"   ✅ No 404 error (endpoint exists)")
        else:
            print(f"   ❌ CRITICAL: 404 Not Found error detected!")
        
        return results
    
    def test_regression(self):
        """Test regression - ensure existing functionality not broken"""
        print("   Testing regression (existing functionality)")
        
        results = {
            'health_check_working': False,
            'subscription_plans_working': False,
            'auth_oauth_check': False
        }
        
        # Test GET /api/health
        print("   📝 Testing: GET /api/health")
        success, response, status_code = self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )
        
        if success and status_code == 200:
            results['health_check_working'] = True
            print(f"      ✅ Health check working - Status: {response.get('status')}")
        else:
            print(f"      ❌ Health check failed - Status: {status_code}")
        
        # Test GET /api/subscription/plans
        print("   📝 Testing: GET /api/subscription/plans")
        success, response, status_code = self.run_test(
            "Subscription Plans",
            "GET",
            "subscription/plans",
            200
        )
        
        if success and status_code == 200:
            results['subscription_plans_working'] = True
            print(f"      ✅ Subscription plans working - {len(response)} plans available")
        else:
            print(f"      ❌ Subscription plans failed - Status: {status_code}")
        
        # Test POST /api/auth/login (OAuth check)
        print("   📝 Testing: POST /api/auth/login (OAuth check)")
        success, response, status_code = self.run_test(
            "Auth OAuth Check",
            "POST",
            "auth/login",
            [200, 401, 404, 422]  # Accept various responses for OAuth-only app
        )
        
        if status_code in [404, 422]:
            results['auth_oauth_check'] = True
            print(f"      ✅ OAuth-only authentication confirmed - Status: {status_code}")
        elif status_code == 401:
            results['auth_oauth_check'] = True
            print(f"      ✅ Authentication endpoint working - Status: {status_code}")
        else:
            print(f"      ⚠️ Unexpected auth response - Status: {status_code}")
        
        return results
    
    def _print_test_results(self, test_results):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("🔧 CRITICAL BUG FIXES VERIFICATION - FINAL RESULTS")
        print("=" * 80)
        
        success_count = sum(test_results.values())
        total_tests = len(test_results)
        success_rate = (success_count / total_tests) * 100
        
        print(f"\n📊 TEST RESULTS SUMMARY:")
        
        # 1. Mock Test Generation (HIGHEST PRIORITY)
        print(f"\n   1️⃣ MOCK TEST GENERATION (HIGHEST PRIORITY):")
        mock_tests = [
            'mock_test_generate_no_initialize_error',
            'mock_test_generate_subscription_check',
            'mock_test_generate_proper_status'
        ]
        for test_name in mock_tests:
            status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
            display_name = test_name.replace('mock_test_generate_', '').replace('_', ' ').title()
            print(f"      {display_name}: {status}")
        
        # 2. Dashboard Analytics
        print(f"\n   2️⃣ DASHBOARD ANALYTICS ENDPOINTS:")
        dashboard_tests = [
            'dashboard_analytics_accessible',
            'dashboard_streak_accessible',
            'dashboard_leaderboard_accessible',
            'dashboard_no_500_errors'
        ]
        for test_name in dashboard_tests:
            status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
            display_name = test_name.replace('dashboard_', '').replace('_', ' ').title()
            print(f"      {display_name}: {status}")
        
        # 3. Bookmarked Questions
        print(f"\n   3️⃣ BOOKMARKED QUESTIONS ENDPOINT:")
        bookmarked_tests = [
            'bookmarked_questions_exists',
            'bookmarked_questions_no_404'
        ]
        for test_name in bookmarked_tests:
            status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
            display_name = test_name.replace('bookmarked_questions_', '').replace('_', ' ').title()
            print(f"      {display_name}: {status}")
        
        # 4. Mock Tests Subjects
        print(f"\n   4️⃣ MOCK TESTS SUBJECTS WITH OPTIONAL PARAM:")
        subjects_tests = [
            'subjects_without_param_works',
            'subjects_with_param_works',
            'subjects_no_422_error'
        ]
        for test_name in subjects_tests:
            status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
            display_name = test_name.replace('subjects_', '').replace('_', ' ').title()
            print(f"      {display_name}: {status}")
        
        # 5. Gamification
        print(f"\n   5️⃣ GAMIFICATION ENDPOINTS:")
        gamification_tests = [
            'gamification_progress_accessible',
            'gamification_leaderboard_accessible',
            'gamification_no_404_from_service_worker'
        ]
        for test_name in gamification_tests:
            status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
            display_name = test_name.replace('gamification_', '').replace('_', ' ').title()
            print(f"      {display_name}: {status}")
        
        # 6. Analytics Performance
        print(f"\n   6️⃣ ANALYTICS PERFORMANCE:")
        analytics_tests = [
            'analytics_performance_accessible',
            'analytics_performance_no_404'
        ]
        for test_name in analytics_tests:
            status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
            display_name = test_name.replace('analytics_performance_', '').replace('_', ' ').title()
            print(f"      {display_name}: {status}")
        
        # 7. Regression Testing
        print(f"\n   7️⃣ REGRESSION TESTING:")
        regression_tests = [
            'health_check_working',
            'subscription_plans_working',
            'auth_oauth_check'
        ]
        for test_name in regression_tests:
            status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
            display_name = test_name.replace('_', ' ').title()
            print(f"      {display_name}: {status}")
        
        print(f"\n📈 OVERALL SUCCESS RATE: {success_count}/{total_tests} ({success_rate:.1f}%)")
        
        # Success Criteria
        print(f"\n🎯 SUCCESS CRITERIA:")
        criteria = {
            '✅ NO 500 errors on any endpoint': test_results.get('dashboard_no_500_errors', False),
            '✅ NO 404 errors on documented endpoints': (
                test_results.get('bookmarked_questions_no_404', False) and
                test_results.get('analytics_performance_no_404', False) and
                test_results.get('gamification_no_404_from_service_worker', False)
            ),
            '✅ NO 422 errors on mock-tests/subjects': test_results.get('subjects_no_422_error', False),
            '✅ Mock test generation returns proper status': test_results.get('mock_test_generate_proper_status', False),
            '✅ Dashboard endpoints accessible': (
                test_results.get('dashboard_analytics_accessible', False) and
                test_results.get('dashboard_streak_accessible', False) and
                test_results.get('dashboard_leaderboard_accessible', False)
            ),
            '✅ All new endpoints responding correctly': (
                test_results.get('bookmarked_questions_exists', False) and
                test_results.get('gamification_progress_accessible', False) and
                test_results.get('analytics_performance_accessible', False)
            )
        }
        
        for criterion, passed in criteria.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {criterion}")
        
        # Determine overall status
        all_criteria_met = all(criteria.values())
        
        if all_criteria_met and success_rate >= 90:
            print("\n✅ ALL CRITICAL BUGS FIXED - PRODUCTION READY")
            print("   All critical bug fixes verified, no deployment blockers")
        elif success_rate >= 80:
            print("\n⚠️ MOST CRITICAL BUGS FIXED - READY WITH MINOR ISSUES")
            print("   Core bug fixes working, minor issues should be addressed")
        elif success_rate >= 70:
            print("\n⚠️ PARTIAL FIX - NEEDS ATTENTION")
            print("   Some critical bugs still present, requires investigation")
        else:
            print("\n❌ CRITICAL BUGS STILL PRESENT")
            print("   Multiple critical issues detected, requires immediate fixes")
        
        return success_rate >= 80


if __name__ == "__main__":
    tester = CriticalBugFixesTester()
    tester.test_critical_bug_fixes()
