#!/usr/bin/env python3
"""
Neuro-Symbolic AI Tutor & Email/Password Authentication Backend Testing
Comprehensive verification of auth flow and neuro-symbolic AI endpoint
"""

import requests
import json
import time
from datetime import datetime

class NeuroAuthBackendTester:
    def __init__(self):
        self.base_url = "https://neuro-tutor-dev.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.jwt_token = None
        self.user_id = None
        self.test_results = {}
    
    def log(self, message, level="INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_test(self, test_name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        # Merge headers
        test_headers = self.session.headers.copy()
        if headers:
            test_headers.update(headers)
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(url, headers=test_headers, timeout=30)
            elif method == "POST":
                response = self.session.post(url, json=data, headers=test_headers, timeout=30)
            elif method == "PUT":
                response = self.session.put(url, json=data, headers=test_headers, timeout=30)
            elif method == "DELETE":
                response = self.session.delete(url, headers=test_headers, timeout=30)
            
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
    
    # ============= EMAIL/PASSWORD AUTHENTICATION =============
    
    def test_email_password_auth(self):
        """Test email/password authentication flow"""
        self.log("=" * 80)
        self.log("🔐 EMAIL/PASSWORD AUTHENTICATION TESTING")
        self.log("=" * 80)
        
        results = {
            'register_endpoint': False,
            'register_returns_token': False,
            'register_returns_user_id': False,
            'login_endpoint': False,
            'login_returns_token': False,
            'login_returns_user_details': False,
            'logout_endpoint': False
        }
        
        # Test 1: Register New User
        self.log("\n1️⃣ Testing User Registration")
        register_data = {
            "email": "testneuro@dhruvai.com",
            "password": "TestNeuro123!",
            "full_name": "Test Neuro User",
            "exam_type": "JEE"
        }
        
        success, response, status, elapsed = self.run_test(
            "Register User",
            "POST",
            "auth/register",
            [200, 201],
            data=register_data
        )
        
        if success:
            results['register_endpoint'] = True
            self.log(f"   ✅ Registration endpoint working ({status}) - {elapsed:.2f}s")
            
            # Check for JWT token
            if 'token' in response:
                results['register_returns_token'] = True
                self.jwt_token = response['token']
                self.log(f"   ✅ JWT token returned: {self.jwt_token[:30]}...")
            else:
                self.log(f"   ❌ JWT token not returned in response")
            
            # Check for user_id
            if 'user' in response and 'user_id' in response['user']:
                results['register_returns_user_id'] = True
                self.user_id = response['user']['user_id']
                self.log(f"   ✅ User ID returned: {self.user_id}")
            else:
                self.log(f"   ❌ User ID not returned in response")
            
            self.log(f"   📊 Response keys: {list(response.keys())}")
        else:
            if status == 400 and 'already registered' in str(response.get('detail', '')).lower():
                self.log(f"   ⚠️ User already exists (expected if test ran before)")
                results['register_endpoint'] = True
                # Try login instead
                self.log(f"   🔄 Attempting login with existing user...")
                return self.test_login_existing_user(results)
            else:
                self.log(f"   ❌ Registration failed: {status} - {response}")
        
        # Test 2: Login with Registered User
        self.log("\n2️⃣ Testing User Login")
        login_data = {
            "email": "testneuro@dhruvai.com",
            "password": "TestNeuro123!"
        }
        
        success, response, status, elapsed = self.run_test(
            "Login User",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success:
            results['login_endpoint'] = True
            self.log(f"   ✅ Login endpoint working (200 OK) - {elapsed:.2f}s")
            
            # Check for JWT token
            if 'token' in response:
                results['login_returns_token'] = True
                self.jwt_token = response['token']
                self.log(f"   ✅ JWT token returned: {self.jwt_token[:30]}...")
            else:
                self.log(f"   ❌ JWT token not returned in response")
            
            # Check for user details
            if 'user' in response:
                results['login_returns_user_details'] = True
                user = response['user']
                self.user_id = user.get('user_id')
                self.log(f"   ✅ User details returned:")
                self.log(f"      - user_id: {user.get('user_id')}")
                self.log(f"      - full_name: {user.get('full_name')}")
                self.log(f"      - email: {user.get('email')}")
                self.log(f"      - exam_type: {user.get('exam_type')}")
            else:
                self.log(f"   ❌ User details not returned in response")
        else:
            self.log(f"   ❌ Login failed: {status} - {response}")
        
        # Test 3: Logout
        self.log("\n3️⃣ Testing User Logout")
        
        # Add JWT token to headers
        logout_headers = {}
        if self.jwt_token:
            logout_headers['Authorization'] = f'Bearer {self.jwt_token}'
        
        success, response, status, elapsed = self.run_test(
            "Logout User",
            "POST",
            "auth/logout",
            200,
            headers=logout_headers
        )
        
        if success:
            results['logout_endpoint'] = True
            self.log(f"   ✅ Logout endpoint working (200 OK) - {elapsed:.2f}s")
            self.log(f"   📊 Response: {response}")
        else:
            self.log(f"   ❌ Logout failed: {status} - {response}")
        
        return results
    
    def test_login_existing_user(self, results):
        """Helper to login with existing user"""
        login_data = {
            "email": "testneuro@dhruvai.com",
            "password": "TestNeuro123!"
        }
        
        success, response, status, elapsed = self.run_test(
            "Login Existing User",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success:
            results['login_endpoint'] = True
            results['login_returns_token'] = 'token' in response
            results['login_returns_user_details'] = 'user' in response
            
            if 'token' in response:
                self.jwt_token = response['token']
                self.log(f"   ✅ Logged in with existing user, token: {self.jwt_token[:30]}...")
            
            if 'user' in response:
                self.user_id = response['user'].get('user_id')
                self.log(f"   ✅ User ID: {self.user_id}")
        
        return results
    
    # ============= NEURO-SYMBOLIC AI TUTOR =============
    
    def test_neuro_symbolic_endpoint(self):
        """Test neuro-symbolic AI tutor endpoint"""
        self.log("\n" + "=" * 80)
        self.log("🧠 NEURO-SYMBOLIC AI TUTOR TESTING")
        self.log("=" * 80)
        
        results = {
            'endpoint_accessible': False,
            'returns_all_8_sections': False,
            'practical_explanation_present': False,
            'indian_example_present': False,
            'metaphor_present': False,
            'visual_schema_present': False,
            'professor_verification_present': False,
            'mini_practice_present': False,
            'encouragement_present': False,
            'ask_present': False,
            'emotion_detected_present': False,
            'generation_time_present': False,
            'message_id_returned': False,
            'response_format_valid': False
        }
        
        if not self.jwt_token:
            self.log("   ❌ No JWT token available. Cannot test authenticated endpoint.")
            return results
        
        # Test: Generate Neuro-Symbolic Response
        self.log("\n1️⃣ Testing Neuro-Symbolic AI Response Generation")
        
        test_payload = {
            "message": "Explain Pythagoras theorem",
            "subject": "Mathematics",
            "session_id": None,
            "exam_mode": "JEE"
        }
        
        headers = {
            'Authorization': f'Bearer {self.jwt_token}'
        }
        
        self.log(f"   📤 Request payload:")
        self.log(f"      - message: {test_payload['message']}")
        self.log(f"      - subject: {test_payload['subject']}")
        self.log(f"      - exam_mode: {test_payload['exam_mode']}")
        
        success, response, status, elapsed = self.run_test(
            "Neuro-Symbolic Response",
            "POST",
            "ai/neuro-symbolic",
            200,
            data=test_payload,
            headers=headers
        )
        
        if success:
            results['endpoint_accessible'] = True
            self.log(f"   ✅ Neuro-symbolic endpoint accessible (200 OK) - {elapsed:.2f}s")
            
            # Check for message_id
            if 'message_id' in response:
                results['message_id_returned'] = True
                self.log(f"   ✅ Message ID returned: {response['message_id']}")
            else:
                self.log(f"   ❌ Message ID not returned")
            
            # Check for emotion_detected
            if 'emotion_detected' in response:
                results['emotion_detected_present'] = True
                self.log(f"   ✅ Emotion detected: {response['emotion_detected']}")
            else:
                self.log(f"   ❌ Emotion detected field missing")
            
            # Check for generation_time
            if 'generation_time' in response:
                results['generation_time_present'] = True
                self.log(f"   ✅ Generation time: {response['generation_time']:.2f}s")
            else:
                self.log(f"   ❌ Generation time field missing")
            
            # Check response structure
            if 'response' in response:
                results['response_format_valid'] = True
                ai_response = response['response']
                
                self.log(f"\n   📊 Checking 8-section structure:")
                
                # Section 1: Practical Explanation
                if 'practical_explanation' in ai_response:
                    results['practical_explanation_present'] = True
                    self.log(f"   ✅ 1. Practical Explanation: Present")
                    self.log(f"      {ai_response['practical_explanation'][:100]}...")
                else:
                    self.log(f"   ❌ 1. Practical Explanation: MISSING")
                
                # Section 2: Indian Example
                if 'indian_example' in ai_response:
                    results['indian_example_present'] = True
                    self.log(f"   ✅ 2. Indian Example: Present")
                    self.log(f"      {ai_response['indian_example'][:100]}...")
                else:
                    self.log(f"   ❌ 2. Indian Example: MISSING")
                
                # Section 3: Metaphor
                if 'metaphor' in ai_response:
                    results['metaphor_present'] = True
                    self.log(f"   ✅ 3. Metaphor: Present")
                    self.log(f"      {ai_response['metaphor'][:100]}...")
                else:
                    self.log(f"   ❌ 3. Metaphor: MISSING")
                
                # Section 4: Visual Schema
                if 'visual_schema' in ai_response:
                    results['visual_schema_present'] = True
                    self.log(f"   ✅ 4. Visual Schema: Present")
                    if isinstance(ai_response['visual_schema'], dict):
                        self.log(f"      Type: JSON diagram structure")
                    else:
                        self.log(f"      {str(ai_response['visual_schema'])[:100]}...")
                else:
                    self.log(f"   ❌ 4. Visual Schema: MISSING")
                
                # Section 5: Professor Verification
                if 'professor_verification' in ai_response:
                    results['professor_verification_present'] = True
                    self.log(f"   ✅ 5. Professor Verification: Present")
                    prof_ver = ai_response['professor_verification']
                    if isinstance(prof_ver, dict):
                        self.log(f"      - Steps: {'steps' in prof_ver}")
                        self.log(f"      - Source: {'source' in prof_ver}")
                        self.log(f"      - Confidence: {'confidence' in prof_ver}")
                    else:
                        self.log(f"      {str(prof_ver)[:100]}...")
                else:
                    self.log(f"   ❌ 5. Professor Verification: MISSING")
                
                # Section 6: Mini Practice
                if 'mini_practice' in ai_response:
                    results['mini_practice_present'] = True
                    self.log(f"   ✅ 6. Mini Practice: Present")
                    mini_practice = ai_response['mini_practice']
                    if isinstance(mini_practice, dict):
                        self.log(f"      - Question: {'question' in mini_practice}")
                        self.log(f"      - Options: {'options' in mini_practice}")
                    else:
                        self.log(f"      {str(mini_practice)[:100]}...")
                else:
                    self.log(f"   ❌ 6. Mini Practice: MISSING")
                
                # Section 7: Encouragement
                if 'encouragement' in ai_response:
                    results['encouragement_present'] = True
                    self.log(f"   ✅ 7. Encouragement: Present")
                    self.log(f"      {ai_response['encouragement'][:100]}...")
                else:
                    self.log(f"   ❌ 7. Encouragement: MISSING")
                
                # Section 8: Ask (Follow-up)
                if 'ask' in ai_response:
                    results['ask_present'] = True
                    self.log(f"   ✅ 8. Ask (Follow-up): Present")
                    self.log(f"      {ai_response['ask'][:100]}...")
                else:
                    self.log(f"   ❌ 8. Ask (Follow-up): MISSING")
                
                # Check if all 8 sections are present
                all_sections = [
                    results['practical_explanation_present'],
                    results['indian_example_present'],
                    results['metaphor_present'],
                    results['visual_schema_present'],
                    results['professor_verification_present'],
                    results['mini_practice_present'],
                    results['encouragement_present'],
                    results['ask_present']
                ]
                
                if all(all_sections):
                    results['returns_all_8_sections'] = True
                    self.log(f"\n   ✅ ALL 8 SECTIONS PRESENT")
                else:
                    missing_count = all_sections.count(False)
                    self.log(f"\n   ❌ MISSING {missing_count} SECTION(S)")
            else:
                self.log(f"   ❌ Response field missing in API response")
        else:
            self.log(f"   ❌ Neuro-symbolic endpoint failed: {status}")
            self.log(f"   📊 Error response: {response}")
        
        return results
    
    # ============= SESSION MANAGEMENT =============
    
    def test_session_management(self):
        """Test session management endpoints"""
        self.log("\n" + "=" * 80)
        self.log("💬 SESSION MANAGEMENT TESTING")
        self.log("=" * 80)
        
        results = {
            'create_session_endpoint': False,
            'create_session_returns_id': False,
            'get_sessions_endpoint': False,
            'get_sessions_returns_list': False
        }
        
        if not self.jwt_token:
            self.log("   ❌ No JWT token available. Cannot test authenticated endpoints.")
            return results
        
        headers = {
            'Authorization': f'Bearer {self.jwt_token}'
        }
        
        # Test 1: Create New Session
        self.log("\n1️⃣ Testing Create Chat Session")
        
        session_data = {
            "title": "Test Session",
            "subject": "Mathematics",
            "topic": "Pythagoras"
        }
        
        success, response, status, elapsed = self.run_test(
            "Create Session",
            "POST",
            "ai/chat/sessions",
            [200, 201],
            data=session_data,
            headers=headers
        )
        
        session_id = None
        if success:
            results['create_session_endpoint'] = True
            self.log(f"   ✅ Create session endpoint working ({status}) - {elapsed:.2f}s")
            
            if 'session_id' in response:
                results['create_session_returns_id'] = True
                session_id = response['session_id']
                self.log(f"   ✅ Session ID returned: {session_id}")
            else:
                self.log(f"   ❌ Session ID not returned")
            
            self.log(f"   📊 Response keys: {list(response.keys())}")
        else:
            self.log(f"   ❌ Create session failed: {status} - {response}")
        
        # Test 2: Get All Sessions
        self.log("\n2️⃣ Testing Get All Sessions")
        
        success, response, status, elapsed = self.run_test(
            "Get Sessions",
            "GET",
            "ai/chat/sessions",
            200,
            headers=headers
        )
        
        if success:
            results['get_sessions_endpoint'] = True
            self.log(f"   ✅ Get sessions endpoint working (200 OK) - {elapsed:.2f}s")
            
            if 'sessions' in response and isinstance(response['sessions'], list):
                results['get_sessions_returns_list'] = True
                session_count = len(response['sessions'])
                self.log(f"   ✅ Sessions list returned: {session_count} session(s)")
                
                if session_count > 0:
                    sample_session = response['sessions'][0]
                    self.log(f"   📊 Sample session keys: {list(sample_session.keys())}")
            else:
                self.log(f"   ❌ Sessions list not returned or invalid format")
        else:
            self.log(f"   ❌ Get sessions failed: {status} - {response}")
        
        return results
    
    # ============= DEFAULT PROMPTS =============
    
    def test_default_prompts(self):
        """Test default prompts endpoint"""
        self.log("\n" + "=" * 80)
        self.log("📝 DEFAULT PROMPTS TESTING")
        self.log("=" * 80)
        
        results = {
            'mathematics_prompts': False,
            'physics_prompts': False,
            'chemistry_prompts': False,
            'prompts_have_correct_structure': False
        }
        
        subjects = ["Mathematics", "Physics", "Chemistry"]
        
        for subject in subjects:
            self.log(f"\n{subjects.index(subject) + 1}️⃣ Testing {subject} Default Prompts")
            
            success, response, status, elapsed = self.run_test(
                f"{subject} Prompts",
                "GET",
                f"ai/subjects/{subject}/defaultPrompts",
                200
            )
            
            if success:
                subject_key = subject.lower() + '_prompts'
                results[subject_key] = True
                self.log(f"   ✅ {subject} prompts endpoint working (200 OK) - {elapsed:.2f}s")
                
                if 'prompts' in response and isinstance(response['prompts'], list):
                    prompt_count = len(response['prompts'])
                    self.log(f"   ✅ Prompts returned: {prompt_count} prompt(s)")
                    
                    if prompt_count > 0:
                        sample_prompt = response['prompts'][0]
                        if 'text' in sample_prompt and 'type' in sample_prompt:
                            results['prompts_have_correct_structure'] = True
                            self.log(f"   ✅ Prompt structure valid (text, type)")
                            self.log(f"   📊 Sample: {sample_prompt['text'][:60]}...")
                        else:
                            self.log(f"   ⚠️ Prompt structure may be incomplete")
                else:
                    self.log(f"   ❌ Prompts list not returned or invalid format")
            else:
                self.log(f"   ❌ {subject} prompts failed: {status} - {response}")
        
        return results
    
    # ============= BACKEND LOGS CHECK =============
    
    def check_backend_logs(self):
        """Check backend logs for errors"""
        self.log("\n" + "=" * 80)
        self.log("📋 BACKEND LOGS CHECK")
        self.log("=" * 80)
        
        self.log("\n⚠️ Note: Backend logs check requires server access")
        self.log("   Manual verification recommended:")
        self.log("   - Check for 500 errors")
        self.log("   - Check for authentication errors")
        self.log("   - Check for AI generation errors")
        self.log("   - Verify no crashes or exceptions")
        
        return {'manual_check_required': True}
    
    # ============= MAIN TEST RUNNER =============
    
    def run_all_tests(self):
        """Run all neuro-symbolic and auth tests"""
        self.log("\n" + "=" * 80)
        self.log("🚀 NEURO-SYMBOLIC AI TUTOR & EMAIL/PASSWORD AUTH TESTING")
        self.log("=" * 80)
        self.log(f"Backend URL: {self.base_url}")
        self.log(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_results = {}
        
        # Run all test suites
        all_results['email_password_auth'] = self.test_email_password_auth()
        all_results['neuro_symbolic_endpoint'] = self.test_neuro_symbolic_endpoint()
        all_results['session_management'] = self.test_session_management()
        all_results['default_prompts'] = self.test_default_prompts()
        all_results['backend_logs'] = self.check_backend_logs()
        
        # Print final summary
        self.print_final_summary(all_results)
        
        return all_results
    
    def print_final_summary(self, all_results):
        """Print final test summary"""
        self.log("\n" + "=" * 80)
        self.log("📊 FINAL TEST SUMMARY")
        self.log("=" * 80)
        
        total_tests = 0
        passed_tests = 0
        
        for category, results in all_results.items():
            if category == 'backend_logs':
                continue  # Skip manual check
            
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
        
        # Critical success criteria
        self.log("\n🎯 CRITICAL SUCCESS CRITERIA:")
        
        auth_working = all_results['email_password_auth'].get('login_endpoint', False)
        neuro_working = all_results['neuro_symbolic_endpoint'].get('endpoint_accessible', False)
        all_8_sections = all_results['neuro_symbolic_endpoint'].get('returns_all_8_sections', False)
        
        self.log(f"   {'✅' if auth_working else '❌'} Email/password auth working")
        self.log(f"   {'✅' if neuro_working else '❌'} Neuro-symbolic endpoint accessible")
        self.log(f"   {'✅' if all_8_sections else '❌'} All 8 sections present in response")
        
        if success_rate >= 90 and all_8_sections:
            self.log("\n✅ EXCELLENT: All critical features working!")
        elif success_rate >= 75:
            self.log("\n⚠️ GOOD: Most features working, minor issues to address")
        elif success_rate >= 60:
            self.log("\n⚠️ PARTIAL: Some features have issues that need attention")
        else:
            self.log("\n❌ CRITICAL: Major issues that must be fixed")
        
        self.log(f"\nTest End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    tester = NeuroAuthBackendTester()
    results = tester.run_all_tests()
