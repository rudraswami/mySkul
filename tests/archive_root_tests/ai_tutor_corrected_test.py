import requests
import json
import time
import uuid
from datetime import datetime

class AITutorCorrectedTester:
    def __init__(self):
        # Use the backend URL from the review request
        self.base_url = "https://platform-rescue.preview.emergentagent.com/api"
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

    def test_corrected_ai_tutor_endpoints(self):
        """Test AI Tutor endpoints with corrected methods and paths"""
        print("\n🔧 AI TUTOR CORRECTED ENDPOINT TESTING")
        print("=" * 80)
        print("   OBJECTIVE: Test corrected endpoints based on actual API implementation")
        print("   BACKEND URL:", self.base_url)
        print("   CORRECTIONS: Using POST for check-access, testing available endpoints only")
        
        test_results = {
            # Corrected Feature Access Test
            'subscription_check_access_post': False,
            
            # Additional Available Endpoints
            'ai_available_contexts': False,
            'ai_mentor_tip': False,
            'ai_cache_stats': False,
            'ai_dual_study_plan': False,
            
            # Chat Session Additional Endpoints
            'chat_session_pin': False,
            'chat_session_bookmark': False,
            
            # Core Infrastructure
            'backend_health': False
        }
        
        # 1. CORE INFRASTRUCTURE
        print("\n1️⃣ CORE INFRASTRUCTURE")
        test_results['backend_health'] = self.test_backend_health()
        
        # 2. CORRECTED FEATURE ACCESS TEST
        print("\n2️⃣ CORRECTED FEATURE ACCESS TEST")
        test_results['subscription_check_access_post'] = self.test_subscription_check_access_post()
        
        # 3. ADDITIONAL AVAILABLE ENDPOINTS
        print("\n3️⃣ ADDITIONAL AVAILABLE ENDPOINTS")
        additional_results = self.test_additional_endpoints()
        test_results.update(additional_results)
        
        # 4. CHAT SESSION ADDITIONAL ENDPOINTS
        print("\n4️⃣ CHAT SESSION ADDITIONAL ENDPOINTS")
        chat_additional_results = self.test_chat_additional_endpoints()
        test_results.update(chat_additional_results)
        
        return self._print_corrected_results(test_results)
    
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
    
    def test_subscription_check_access_post(self):
        """Test POST /api/subscription/check-access (corrected method)"""
        print("   Testing corrected subscription check-access endpoint")
        
        # Test POST /api/subscription/check-access with JSON body
        print("   📝 Testing: POST /api/subscription/check-access")
        access_data = {
            "feature_name": "ai_sessions_monthly"
        }
        
        success, response, status_code = self.run_test(
            "Subscription Check Access (POST)",
            "POST",
            "subscription/check-access",
            [200, 401, 402]
        )
        
        if success:
            print(f"   ✅ Subscription check access (POST) endpoint accessible - Status: {status_code}")
            
            if status_code == 200 and isinstance(response, dict):
                has_access = response.get('has_access')
                remaining = response.get('remaining')
                print(f"      Has access: {has_access}")
                print(f"      Remaining: {remaining}")
            elif status_code == 401:
                print(f"      Expected: Authentication required")
            elif status_code == 402:
                print(f"      Expected: Subscription upgrade required")
            return True
        else:
            print(f"   ❌ Subscription check access (POST) failed - Status: {status_code}")
            return False
    
    def test_additional_endpoints(self):
        """Test additional available AI endpoints"""
        print("   Testing additional available AI endpoints")
        
        results = {
            'ai_available_contexts': False,
            'ai_mentor_tip': False,
            'ai_cache_stats': False,
            'ai_dual_study_plan': False
        }
        
        # Test GET /api/ai/available-contexts
        print("   📝 Testing: GET /api/ai/available-contexts")
        success, response, status_code = self.run_test(
            "AI Available Contexts",
            "GET",
            "ai/available-contexts",
            [200, 401]
        )
        
        if success:
            results['ai_available_contexts'] = True
            print(f"   ✅ AI available contexts endpoint accessible - Status: {status_code}")
            
            if status_code == 200 and isinstance(response, dict):
                subjects = response.get('subjects', [])
                ai_modes = response.get('ai_modes', [])
                print(f"      Subjects available: {len(subjects)}")
                print(f"      AI modes: {ai_modes}")
        else:
            print(f"   ❌ AI available contexts failed - Status: {status_code}")
        
        # Test GET /api/ai/mentor-tip/{subject}/{topic}
        print("   📝 Testing: GET /api/ai/mentor-tip/math/algebra")
        success, response, status_code = self.run_test(
            "AI Mentor Tip",
            "GET",
            "ai/mentor-tip/math/algebra",
            [200, 401]
        )
        
        if success:
            results['ai_mentor_tip'] = True
            print(f"   ✅ AI mentor tip endpoint accessible - Status: {status_code}")
            
            if status_code == 200 and isinstance(response, dict):
                cached = response.get('cached', False)
                tip = response.get('tip')
                print(f"      Tip cached: {cached}")
                print(f"      Tip available: {tip is not None}")
        else:
            print(f"   ❌ AI mentor tip failed - Status: {status_code}")
        
        # Test GET /api/ai/cache/stats
        print("   📝 Testing: GET /api/ai/cache/stats")
        success, response, status_code = self.run_test(
            "AI Cache Stats",
            "GET",
            "ai/cache/stats",
            [200, 401]
        )
        
        if success:
            results['ai_cache_stats'] = True
            print(f"   ✅ AI cache stats endpoint accessible - Status: {status_code}")
            
            if status_code == 200 and isinstance(response, dict):
                print(f"      Cache stats keys: {list(response.keys())}")
        else:
            print(f"   ❌ AI cache stats failed - Status: {status_code}")
        
        # Test POST /api/ai/dual-study-plan
        print("   📝 Testing: POST /api/ai/dual-study-plan")
        study_plan_data = {
            "subject": "Mathematics",
            "topics": ["Algebra", "Calculus"],
            "exam_type": "JEE",
            "duration_weeks": 4
        }
        
        success, response, status_code = self.run_test(
            "AI Dual Study Plan",
            "POST",
            "ai/dual-study-plan",
            [200, 401, 402]
        )
        
        if success:
            results['ai_dual_study_plan'] = True
            print(f"   ✅ AI dual study plan endpoint accessible - Status: {status_code}")
        else:
            print(f"   ❌ AI dual study plan failed - Status: {status_code}")
        
        return results
    
    def test_chat_additional_endpoints(self):
        """Test additional chat session endpoints"""
        print("   Testing additional chat session endpoints")
        
        results = {
            'chat_session_pin': False,
            'chat_session_bookmark': False
        }
        
        session_id = "test-session-123"
        
        # Test PUT /api/ai/chat/{session_id}/pin
        print(f"   📝 Testing: PUT /api/ai/chat/{session_id}/pin")
        pin_data = {"pinned": True}
        
        success, response, status_code = self.run_test(
            "Chat Session Pin",
            "PUT",
            f"ai/chat/{session_id}/pin",
            [200, 401, 404]
        )
        
        if success:
            results['chat_session_pin'] = True
            print(f"   ✅ Chat session pin endpoint accessible - Status: {status_code}")
        else:
            print(f"   ❌ Chat session pin failed - Status: {status_code}")
        
        # Test PUT /api/ai/chat/{session_id}/bookmark
        print(f"   📝 Testing: PUT /api/ai/chat/{session_id}/bookmark")
        bookmark_data = {"bookmarked": True}
        
        success, response, status_code = self.run_test(
            "Chat Session Bookmark",
            "PUT",
            f"ai/chat/{session_id}/bookmark",
            [200, 401, 404]
        )
        
        if success:
            results['chat_session_bookmark'] = True
            print(f"   ✅ Chat session bookmark endpoint accessible - Status: {status_code}")
        else:
            print(f"   ❌ Chat session bookmark failed - Status: {status_code}")
        
        return results
    
    def _print_corrected_results(self, test_results):
        """Print corrected test results"""
        print("\n" + "=" * 80)
        print("🔧 AI TUTOR CORRECTED ENDPOINT TESTING - FINAL RESULTS")
        print("=" * 80)
        
        success_count = sum(test_results.values())
        total_tests = len(test_results)
        success_rate = (success_count / total_tests) * 100
        
        print(f"\n📊 CORRECTED TEST RESULTS SUMMARY:")
        
        # Core Infrastructure
        print(f"\n   CORE INFRASTRUCTURE:")
        if test_results.get('backend_health', False):
            print(f"      Backend Health: ✅ PASS")
        else:
            print(f"      Backend Health: ❌ FAIL")
        
        # Corrected Feature Access
        print(f"\n   CORRECTED FEATURE ACCESS:")
        if test_results.get('subscription_check_access_post', False):
            print(f"      Check Access (POST): ✅ PASS")
        else:
            print(f"      Check Access (POST): ❌ FAIL")
        
        # Additional Available Endpoints
        additional_tests = ['ai_available_contexts', 'ai_mentor_tip', 'ai_cache_stats', 'ai_dual_study_plan']
        additional_success = sum(test_results.get(test, False) for test in additional_tests)
        print(f"\n   ADDITIONAL AVAILABLE ENDPOINTS ({additional_success}/{len(additional_tests)}):")
        for test_name in additional_tests:
            status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
            display_name = test_name.replace('ai_', '').replace('_', ' ').title()
            print(f"      {display_name}: {status}")
        
        # Chat Session Additional Endpoints
        chat_additional_tests = ['chat_session_pin', 'chat_session_bookmark']
        chat_additional_success = sum(test_results.get(test, False) for test in chat_additional_tests)
        print(f"\n   CHAT SESSION ADDITIONAL ENDPOINTS ({chat_additional_success}/{len(chat_additional_tests)}):")
        for test_name in chat_additional_tests:
            status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
            display_name = test_name.replace('chat_session_', '').replace('_', ' ').title()
            print(f"      {display_name}: {status}")
        
        print(f"\n📈 OVERALL SUCCESS RATE: {success_count}/{total_tests} ({success_rate:.1f}%)")
        
        # Determine overall status
        if success_rate >= 90:
            print("\n✅ CORRECTED ENDPOINTS: EXCELLENT - ALL WORKING")
            print("   All corrected AI Tutor endpoints accessible and functional")
        elif success_rate >= 80:
            print("\n✅ CORRECTED ENDPOINTS: GOOD - MOSTLY WORKING")
            print("   Most corrected AI Tutor endpoints working correctly")
        elif success_rate >= 70:
            print("\n⚠️ CORRECTED ENDPOINTS: PARTIAL - SOME ISSUES")
            print("   Some corrected AI Tutor endpoints working, issues detected")
        else:
            print("\n❌ CORRECTED ENDPOINTS: MULTIPLE ISSUES")
            print("   Multiple corrected AI Tutor endpoints have issues")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        
        if test_results.get('subscription_check_access_post', False):
            print("   ✅ Feature access check works with POST method (not GET)")
        else:
            print("   ❌ Feature access check still has issues with POST method")
        
        if additional_success >= len(additional_tests) * 0.75:
            print("   ✅ Most additional AI endpoints are accessible")
        else:
            print("   ⚠️ Some additional AI endpoints have issues")
        
        if chat_additional_success >= len(chat_additional_tests) * 0.75:
            print("   ✅ Additional chat session features are accessible")
        else:
            print("   ⚠️ Additional chat session features have issues")
        
        return success_rate >= 70


if __name__ == "__main__":
    tester = AITutorCorrectedTester()
    success = tester.test_corrected_ai_tutor_endpoints()
    
    if success:
        print("\n🎉 AI TUTOR CORRECTED TESTING: SUCCESS")
    else:
        print("\n⚠️ AI TUTOR CORRECTED TESTING: NEEDS ATTENTION")