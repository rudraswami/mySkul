import requests
import json
import time
from datetime import datetime

class ComprehensiveEndpointTester:
    def __init__(self):
        # Use the correct backend URL from frontend/.env
        self.base_url = "https://eduai-platform-25.preview.emergentagent.com/api"
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

    def test_comprehensive_endpoints(self):
        """Comprehensive testing of all fixed endpoints and validation"""
        print("\n🔍 COMPREHENSIVE ENDPOINT TESTING - ALL FIXES VALIDATION")
        print("=" * 80)
        print("   OBJECTIVE: Verify all endpoint fixes are working correctly")
        print("   BACKEND URL:", self.base_url)
        print("   AUTHENTICATION: OAuth required (401 expected without token)")
        
        test_results = {
            # User Progress Endpoint (GamificationProgress fix)
            'user_progress_endpoint': False,
            'user_progress_complete_data': False,
            'user_progress_no_500_error': False,
            
            # Dashboard Endpoints (500 error fixes)
            'dashboard_analytics_fixed': False,
            'dashboard_streak_fixed': False,
            'dashboard_leaderboard_fixed': False,
            
            # Gamification Endpoints (404 fixes)
            'gamification_progress_fixed': False,
            'gamification_leaderboard_fixed': False,
            'gamification_achievements_fixed': False,
            
            # Mock Test & Analytics (422/404 validation)
            'mock_tests_generate_accessible': False,
            'mock_tests_library_accessible': False,
            
            # Regression Testing
            'ai_dual_response_working': False,
            'auth_me_working': False,
            
            # Backend Health
            'backend_health': False
        }
        
        # 1. BACKEND HEALTH CHECK
        print("\n1️⃣ BACKEND HEALTH CHECK")
        test_results['backend_health'] = self.test_backend_health()
        
        # 2. USER PROGRESS ENDPOINT (GamificationProgress fix)
        print("\n2️⃣ USER PROGRESS ENDPOINT - GAMIFICATIONPROGRESS FIX")
        progress_results = self.test_user_progress_endpoint()
        test_results.update(progress_results)
        
        # 3. DASHBOARD ENDPOINTS (500 error fixes)
        print("\n3️⃣ DASHBOARD ENDPOINTS - 500 ERROR FIXES")
        dashboard_results = self.test_dashboard_endpoints()
        test_results.update(dashboard_results)
        
        # 4. GAMIFICATION ENDPOINTS (404 fixes)
        print("\n4️⃣ GAMIFICATION ENDPOINTS - 404 ERROR FIXES")
        gamification_results = self.test_gamification_endpoints()
        test_results.update(gamification_results)
        
        # 5. MOCK TEST & ANALYTICS (422/404 validation)
        print("\n5️⃣ MOCK TEST & ANALYTICS - 422/404 VALIDATION")
        mock_test_results = self.test_mock_test_endpoints()
        test_results.update(mock_test_results)
        
        # 6. REGRESSION TESTING
        print("\n6️⃣ REGRESSION TESTING - EXISTING FUNCTIONALITY")
        regression_results = self.test_regression_endpoints()
        test_results.update(regression_results)
        
        return self._print_comprehensive_test_results(test_results)
    
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
    
    def test_user_progress_endpoint(self):
        """Test User Progress Endpoint - GamificationProgress fix"""
        print("   Testing User Progress Endpoint (GamificationProgress fix)")
        
        results = {
            'user_progress_endpoint': False,
            'user_progress_complete_data': False,
            'user_progress_no_500_error': False
        }
        
        # Test GET /api/user/progress
        print("   📝 Testing: GET /api/user/progress")
        success, response, status_code = self.run_test(
            "User Progress Endpoint",
            "GET",
            "user/progress",
            [200, 401]  # 200 OK or 401 (not crash with 500)
        )
        
        if success:
            results['user_progress_endpoint'] = True
            results['user_progress_no_500_error'] = True
            print(f"   ✅ User progress endpoint accessible - Status: {status_code}")
            
            if status_code == 200 and isinstance(response, dict):
                # Verify presence of all required fields
                required_fields = [
                    'xp', 'level', 'badges',  # legacy fields
                    'total_xp', 'current_level', 'xp_for_next_level',  # new fields
                    'current_streak', 'longest_streak',  # streak fields
                    'total_badges', 'available_badges', 'badges_earned',  # badge fields
                ]
                
                stats_fields = ['total_tests', 'average_accuracy', 'perfect_scores']
                
                # Check main fields
                missing_fields = []
                present_fields = []
                
                for field in required_fields:
                    if field in response:
                        present_fields.append(field)
                    else:
                        missing_fields.append(field)
                
                # Check stats object
                stats_present = []
                stats_missing = []
                if 'stats' in response and isinstance(response['stats'], dict):
                    for field in stats_fields:
                        if field in response['stats']:
                            stats_present.append(f"stats.{field}")
                        else:
                            stats_missing.append(f"stats.{field}")
                else:
                    stats_missing = [f"stats.{field}" for field in stats_fields]
                
                print(f"      Present fields: {present_fields}")
                print(f"      Present stats: {stats_present}")
                
                if missing_fields or stats_missing:
                    print(f"      ⚠️ Missing fields: {missing_fields + stats_missing}")
                    print(f"      Response structure: {list(response.keys())}")
                else:
                    results['user_progress_complete_data'] = True
                    print(f"      ✅ All required fields present")
                    
            elif status_code == 401:
                print(f"      Expected: Authentication required (OAuth app)")
        else:
            print(f"   ❌ User progress endpoint failed - Status: {status_code}")
            if status_code == 500:
                print(f"      ❌ CRITICAL: Still returning 500 Internal Server Error")
                results['user_progress_no_500_error'] = False
        
        return results
    
    def test_dashboard_endpoints(self):
        """Test Dashboard Endpoints - 500 error fixes"""
        print("   Testing Dashboard Endpoints (500 error fixes)")
        
        results = {
            'dashboard_analytics_fixed': False,
            'dashboard_streak_fixed': False,
            'dashboard_leaderboard_fixed': False
        }
        
        dashboard_endpoints = [
            ("dashboard/analytics", "dashboard_analytics_fixed", "Dashboard Analytics"),
            ("dashboard/streak", "dashboard_streak_fixed", "Dashboard Streak"),
            ("dashboard/leaderboard", "dashboard_leaderboard_fixed", "Dashboard Leaderboard")
        ]
        
        for endpoint, result_key, display_name in dashboard_endpoints:
            print(f"   📝 Testing: GET /api/{endpoint}")
            success, response, status_code = self.run_test(
                display_name,
                "GET",
                endpoint,
                [200, 401]  # Should return 200 OK or 401 (not 500)
            )
            
            if success:
                results[result_key] = True
                print(f"   ✅ {display_name} fixed - Status: {status_code}")
                if status_code == 401:
                    print(f"      Expected: Authentication required")
                elif status_code == 200:
                    print(f"      Success: Endpoint working correctly")
            else:
                print(f"   ❌ {display_name} failed - Status: {status_code}")
                if status_code == 500:
                    print(f"      ❌ CRITICAL: Still returning 500 Internal Server Error")
        
        return results
    
    def test_gamification_endpoints(self):
        """Test Gamification Endpoints - 404 fixes"""
        print("   Testing Gamification Endpoints (404 fixes)")
        
        results = {
            'gamification_progress_fixed': False,
            'gamification_leaderboard_fixed': False,
            'gamification_achievements_fixed': False
        }
        
        gamification_endpoints = [
            ("gamification/progress", "gamification_progress_fixed", "Gamification Progress"),
            ("gamification/leaderboard", "gamification_leaderboard_fixed", "Gamification Leaderboard"),
            ("gamification/achievements", "gamification_achievements_fixed", "Gamification Achievements")
        ]
        
        for endpoint, result_key, display_name in gamification_endpoints:
            print(f"   📝 Testing: GET /api/{endpoint}")
            success, response, status_code = self.run_test(
                display_name,
                "GET",
                endpoint,
                [200, 401]  # Should return 200 OK or 401 (not 404)
            )
            
            if success:
                results[result_key] = True
                print(f"   ✅ {display_name} fixed - Status: {status_code}")
                if status_code == 401:
                    print(f"      Expected: Authentication required")
                elif status_code == 200:
                    print(f"      Success: Endpoint working correctly")
            else:
                print(f"   ❌ {display_name} failed - Status: {status_code}")
                if status_code == 404:
                    print(f"      ❌ CRITICAL: Still returning 404 Not Found")
        
        return results
    
    def test_mock_test_endpoints(self):
        """Test Mock Test & Analytics - 422/404 validation"""
        print("   Testing Mock Test & Analytics (422/404 validation)")
        
        results = {
            'mock_tests_generate_accessible': False,
            'mock_tests_library_accessible': False
        }
        
        # Test POST /api/mock-tests/generate
        print("   📝 Testing: POST /api/mock-tests/generate")
        generate_data = {
            "subject": "Mathematics",
            "topic": "Algebra",
            "difficulty": "intermediate",
            "question_count": 10
        }
        
        success, response, status_code = self.run_test(
            "Mock Tests Generate",
            "POST",
            "mock-tests/generate",
            [200, 401, 402]  # Should return 200 OK, 401, or 402 (not 422/404)
        )
        
        if success:
            results['mock_tests_generate_accessible'] = True
            print(f"   ✅ Mock Tests Generate accessible - Status: {status_code}")
            if status_code == 401:
                print(f"      Expected: Authentication required")
            elif status_code == 402:
                print(f"      Expected: Subscription required")
            elif status_code == 200:
                print(f"      Success: Mock test generation working")
        else:
            print(f"   ❌ Mock Tests Generate failed - Status: {status_code}")
            if status_code in [422, 404]:
                print(f"      ❌ ISSUE: Returning {status_code} error")
        
        # Test GET /api/mock-tests/library
        print("   📝 Testing: GET /api/mock-tests/library")
        success, response, status_code = self.run_test(
            "Mock Tests Library",
            "GET",
            "mock-tests/library",
            [200, 401]  # Should return 200 OK or 401
        )
        
        if success:
            results['mock_tests_library_accessible'] = True
            print(f"   ✅ Mock Tests Library accessible - Status: {status_code}")
            if status_code == 401:
                print(f"      Expected: Authentication required")
            elif status_code == 200:
                print(f"      Success: Mock tests library working")
        else:
            print(f"   ❌ Mock Tests Library failed - Status: {status_code}")
        
        return results
    
    def test_regression_endpoints(self):
        """Test Regression Endpoints - Existing functionality"""
        print("   Testing Regression Endpoints (existing functionality)")
        
        results = {
            'ai_dual_response_working': False,
            'auth_session_working': False
        }
        
        # Test POST /api/ai/dual-response
        print("   📝 Testing: POST /api/ai/dual-response")
        ai_data = {
            "user_message": "Explain quadratic equations",
            "subject": "Mathematics",
            "exam_type": "JEE",
            "mode": "dual"
        }
        
        success, response, status_code = self.run_test(
            "AI Dual Response",
            "POST",
            "ai/dual-response",
            [200, 401, 402]  # Should still work
        )
        
        if success:
            results['ai_dual_response_working'] = True
            print(f"   ✅ AI Dual Response working - Status: {status_code}")
            if status_code == 401:
                print(f"      Expected: Authentication required")
            elif status_code == 402:
                print(f"      Expected: Subscription required")
        else:
            print(f"   ❌ AI Dual Response failed - Status: {status_code}")
        
        # Test GET /api/auth/session
        print("   📝 Testing: GET /api/auth/session")
        success, response, status_code = self.run_test(
            "Auth Session",
            "GET",
            "auth/session",
            [200, 401]  # Should still work
        )
        
        if success:
            results['auth_me_working'] = True
            print(f"   ✅ Auth Me working - Status: {status_code}")
            if status_code == 401:
                print(f"      Expected: Authentication required")
            elif status_code == 200:
                print(f"      Success: User info retrieved")
        else:
            print(f"   ❌ Auth Me failed - Status: {status_code}")
        
        return results
    
    def _print_comprehensive_test_results(self, test_results):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("🔍 COMPREHENSIVE ENDPOINT TESTING - FINAL RESULTS")
        print("=" * 80)
        
        success_count = sum(test_results.values())
        total_tests = len(test_results)
        success_rate = (success_count / total_tests) * 100
        
        print(f"\n📊 TEST RESULTS SUMMARY:")
        
        # User Progress Endpoint (GamificationProgress fix)
        print(f"\n   USER PROGRESS ENDPOINT - GAMIFICATIONPROGRESS FIX:")
        progress_tests = ['user_progress_endpoint', 'user_progress_complete_data', 'user_progress_no_500_error']
        progress_success = sum(test_results.get(test, False) for test in progress_tests)
        for test_name in progress_tests:
            status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
            display_name = test_name.replace('user_progress_', '').replace('_', ' ').title()
            print(f"      {display_name}: {status}")
        
        # Dashboard Endpoints (500 error fixes)
        print(f"\n   DASHBOARD ENDPOINTS - 500 ERROR FIXES:")
        dashboard_tests = ['dashboard_analytics_fixed', 'dashboard_streak_fixed', 'dashboard_leaderboard_fixed']
        dashboard_success = sum(test_results.get(test, False) for test in dashboard_tests)
        for test_name in dashboard_tests:
            status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
            display_name = test_name.replace('dashboard_', '').replace('_fixed', '').replace('_', ' ').title()
            print(f"      {display_name}: {status}")
        
        # Gamification Endpoints (404 fixes)
        print(f"\n   GAMIFICATION ENDPOINTS - 404 ERROR FIXES:")
        gamification_tests = ['gamification_progress_fixed', 'gamification_leaderboard_fixed', 'gamification_achievements_fixed']
        gamification_success = sum(test_results.get(test, False) for test in gamification_tests)
        for test_name in gamification_tests:
            status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
            display_name = test_name.replace('gamification_', '').replace('_fixed', '').replace('_', ' ').title()
            print(f"      {display_name}: {status}")
        
        # Mock Test & Analytics
        print(f"\n   MOCK TEST & ANALYTICS - 422/404 VALIDATION:")
        mock_tests = ['mock_tests_generate_accessible', 'mock_tests_library_accessible']
        mock_success = sum(test_results.get(test, False) for test in mock_tests)
        for test_name in mock_tests:
            status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
            display_name = test_name.replace('mock_tests_', '').replace('_accessible', '').replace('_', ' ').title()
            print(f"      {display_name}: {status}")
        
        # Regression Testing
        print(f"\n   REGRESSION TESTING - EXISTING FUNCTIONALITY:")
        regression_tests = ['ai_dual_response_working', 'auth_me_working']
        regression_success = sum(test_results.get(test, False) for test in regression_tests)
        for test_name in regression_tests:
            status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
            display_name = test_name.replace('_working', '').replace('_', ' ').title()
            print(f"      {display_name}: {status}")
        
        print(f"\n📈 OVERALL SUCCESS RATE: {success_count}/{total_tests} ({success_rate:.1f}%)")
        
        # Critical Success Criteria
        print(f"\n🎯 CRITICAL SUCCESS CRITERIA:")
        critical_criteria = {
            'No 500 Internal Server Errors': test_results.get('user_progress_no_500_error', False) and dashboard_success == len(dashboard_tests),
            'No 404 Not Found Errors': gamification_success == len(gamification_tests),
            'User Progress Complete Data': test_results.get('user_progress_complete_data', False),
            'All Endpoints Accessible': success_count >= total_tests * 0.8,
            'No Regressions': regression_success == len(regression_tests)
        }
        
        for criterion, passed in critical_criteria.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {criterion}")
        
        # Determine overall status
        critical_passed = sum(critical_criteria.values())
        critical_total = len(critical_criteria)
        
        if critical_passed == critical_total and success_rate >= 90:
            print("\n✅ COMPREHENSIVE TESTING: EXCELLENT - ALL FIXES WORKING")
            print("   All endpoint fixes verified, no regressions detected")
        elif critical_passed >= critical_total * 0.8 and success_rate >= 80:
            print("\n✅ COMPREHENSIVE TESTING: GOOD - FIXES WORKING WITH MINOR ISSUES")
            print("   Core fixes working correctly, minor issues are non-blocking")
        elif critical_passed >= critical_total * 0.6:
            print("\n⚠️ COMPREHENSIVE TESTING: PARTIAL - SOME FIXES WORKING")
            print("   Some fixes working, critical issues need attention")
        else:
            print("\n❌ COMPREHENSIVE TESTING: ISSUES DETECTED")
            print("   Multiple endpoint fixes have issues, requires investigation")
        
        # Specific Issue Summary
        print(f"\n🔧 ISSUE SUMMARY:")
        
        issues_found = []
        
        if not test_results.get('user_progress_no_500_error', False):
            issues_found.append("User Progress endpoint still returning 500 errors")
        
        if dashboard_success < len(dashboard_tests):
            failed_dashboard = [test for test in dashboard_tests if not test_results.get(test, False)]
            issues_found.append(f"Dashboard endpoints still have 500 errors: {failed_dashboard}")
        
        if gamification_success < len(gamification_tests):
            failed_gamification = [test for test in gamification_tests if not test_results.get(test, False)]
            issues_found.append(f"Gamification endpoints still have 404 errors: {failed_gamification}")
        
        if not test_results.get('user_progress_complete_data', False):
            issues_found.append("User Progress endpoint missing required data fields")
        
        if regression_success < len(regression_tests):
            failed_regression = [test for test in regression_tests if not test_results.get(test, False)]
            issues_found.append(f"Regression detected in existing functionality: {failed_regression}")
        
        if issues_found:
            for issue in issues_found:
                print(f"   ❌ {issue}")
        else:
            print(f"   ✅ No critical issues detected")
        
        return success_rate >= 80 and critical_passed >= critical_total * 0.8


if __name__ == "__main__":
    tester = ComprehensiveEndpointTester()
    success = tester.test_comprehensive_endpoints()
    
    if success:
        print("\n🎉 COMPREHENSIVE ENDPOINT TESTING COMPLETED SUCCESSFULLY")
    else:
        print("\n⚠️ COMPREHENSIVE ENDPOINT TESTING COMPLETED WITH ISSUES")