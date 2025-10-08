#!/usr/bin/env python3
"""
Phase C, D, E Backend API Testing Script
Focus: Advanced Guardrails, Enhanced Action Buttons, Analytics Integration APIs
"""

import requests
import json
import time
import uuid
from datetime import datetime

class PhaseCDETester:
    def __init__(self, base_url="https://paywall-unity.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.session_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_email = "test@dhruvai.com"
        self.test_user_password = "password123"

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        if self.token and 'Authorization' not in test_headers:
            test_headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:300]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def authenticate(self):
        """Authenticate with test credentials"""
        print("🔐 AUTHENTICATION SETUP")
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            if 'user' in response:
                self.user_id = response['user'].get('user_id')
            print(f"   ✅ Authentication successful")
            print(f"   Token: {self.token[:20]}...")
            return True
        else:
            print("   ❌ Authentication failed")
            return False

    def test_phase_c_guardrails_apis(self):
        """Test Phase C: Advanced Guardrails APIs"""
        print("\n🎯 PHASE C: ADVANCED GUARDRAILS APIs")
        
        success_count = 0
        total_tests = 0
        
        # Test 1: Math Validation API
        print("\n   Testing POST /api/guardrails/validate-math...")
        math_expressions = [
            {"expression": "x^2 + 5x + 6 = 0", "units": None},
            {"expression": "F = ma", "units": "N = kg⋅m/s²"},
            {"expression": "v = u + at", "units": "m/s"},
            {"expression": "E = mc²", "units": "J = kg⋅m²/s²"}
        ]
        
        for i, test_case in enumerate(math_expressions):
            total_tests += 1
            print(f"   Testing math expression {i+1}/4: {test_case['expression']}")
            
            success, response = self.run_test(
                f"Math Validation - {test_case['expression'][:20]}",
                "POST",
                "guardrails/validate-math",
                200,
                data=test_case
            )
            
            if success:
                print(f"   ✅ Math validation successful")
                print(f"   Is valid: {response.get('is_valid', False)}")
                print(f"   Confidence: {response.get('confidence_score', 0):.2f}")
                success_count += 1
            else:
                print(f"   ❌ Math validation failed")
            
            time.sleep(1)
        
        # Test 2: Citations API
        print("\n   Testing GET /api/guardrails/citations/{subject}/{topic}...")
        citation_tests = [
            {"subject": "Mathematics", "topic": "Quadratic Equations"},
            {"subject": "Physics", "topic": "Newton's Laws"},
            {"subject": "Chemistry", "topic": "Periodic Table"}
        ]
        
        for test_case in citation_tests:
            total_tests += 1
            print(f"   Testing citations for {test_case['subject']}/{test_case['topic']}")
            
            success, response = self.run_test(
                f"Citations - {test_case['subject']}/{test_case['topic']}",
                "GET",
                f"guardrails/citations/{test_case['subject']}/{test_case['topic']}",
                200
            )
            
            if success:
                citations = response.get('citations', []) if isinstance(response, dict) else response
                print(f"   ✅ Citations retrieved: {len(citations)} sources")
                if citations and len(citations) > 0:
                    sample_citation = citations[0] if isinstance(citations[0], dict) else {}
                    print(f"   Sample source: {sample_citation.get('source_title', 'N/A')}")
                    print(f"   Source type: {sample_citation.get('source_type', 'N/A')}")
                success_count += 1
            else:
                print(f"   ❌ Citations retrieval failed")
            
            time.sleep(1)
        
        # Test 3: Disagreement Alerts API (requires session_id)
        print("\n   Testing GET /api/guardrails/disagreements/{session_id}...")
        test_session_id = str(uuid.uuid4())
        total_tests += 1
        
        success, response = self.run_test(
            "Disagreement Alerts",
            "GET",
            f"guardrails/disagreements/{test_session_id}",
            200
        )
        
        if success:
            if isinstance(response, dict):
                alerts = response.get('disagreement_alerts', [])
            elif isinstance(response, list):
                alerts = response
            else:
                alerts = []
            print(f"   ✅ Disagreement alerts retrieved: {len(alerts)} alerts")
            success_count += 1
        else:
            print(f"   ❌ Disagreement alerts failed")
        
        # Test 4: Fact Verification API
        print("\n   Testing POST /api/guardrails/fact-verification...")
        fact_data = {
            "statement": "The speed of light in vacuum is approximately 3 × 10^8 m/s",
            "subject": "Physics",
            "context": "Basic physics constants"
        }
        total_tests += 1
        
        success, response = self.run_test(
            "Fact Verification",
            "POST",
            "guardrails/fact-verification",
            200,
            data=fact_data
        )
        
        if success:
            print(f"   ✅ Fact verification successful")
            if isinstance(response, dict):
                print(f"   Verification result: {response.get('is_verified', False)}")
                print(f"   Confidence: {response.get('confidence_score', 0):.2f}")
            success_count += 1
        else:
            print(f"   ❌ Fact verification failed")
        
        print(f"\n   Phase C Summary: {success_count}/{total_tests} tests passed ({success_count/total_tests*100:.1f}%)")
        return success_count >= total_tests * 0.8

    def test_phase_d_action_buttons_apis(self):
        """Test Phase D: Enhanced Action Buttons APIs"""
        print("\n🎯 PHASE D: ENHANCED ACTION BUTTONS APIs")
        
        success_count = 0
        total_tests = 0
        
        # Test 1: Practice More API
        print("\n   Testing POST /api/actions/practice-more...")
        practice_data = {
            "original_question": "Solve x² - 5x + 6 = 0",
            "subject": "Mathematics",
            "topic": "Quadratic Equations",
            "difficulty_level": "similar",
            "education_standard": "JEE"
        }
        total_tests += 1
        
        success, response = self.run_test(
            "Practice More",
            "POST",
            "actions/practice-more",
            200,
            data=practice_data
        )
        
        if success:
            session_id = response.get('session_id')
            problems = response.get('generated_problems', [])
            print(f"   ✅ Practice session created: {session_id}")
            print(f"   Generated problems: {len(problems)}")
            success_count += 1
        else:
            print(f"   ❌ Practice problems generation failed")
        
        # Test 2: Add to Notes API
        print("\n   Testing POST /api/actions/add-to-notes...")
        note_data = {
            "title": "Quadratic Formula Derivation",
            "content": "The quadratic formula x = (-b ± √(b²-4ac))/2a is derived from completing the square method.",
            "subject": "Mathematics",
            "topic": "Quadratic Equations"
        }
        total_tests += 1
        
        success, response = self.run_test(
            "Add to Notes",
            "POST",
            "actions/add-to-notes",
            200,
            data=note_data
        )
        
        if success:
            note_id = response.get('note_id')
            print(f"   ✅ Note saved: {note_id}")
            print(f"   Title: {response.get('title', 'N/A')}")
            success_count += 1
        else:
            print(f"   ❌ Add to notes failed")
        
        # Test 3: Create Flashcards API
        print("\n   Testing POST /api/actions/create-flashcards...")
        flashcard_data = {
            "title": "Quadratic Equations Flashcards",
            "content": "Key concepts: discriminant, roots, vertex form, standard form",
            "subject": "Mathematics",
            "topic": "Quadratic Equations"
        }
        total_tests += 1
        
        success, response = self.run_test(
            "Create Flashcards",
            "POST",
            "actions/create-flashcards",
            200,
            data=flashcard_data
        )
        
        if success:
            deck_id = response.get('deck_id')
            cards = response.get('cards', [])
            print(f"   ✅ Flashcard deck created: {deck_id}")
            print(f"   Cards generated: {len(cards)}")
            success_count += 1
        else:
            print(f"   ❌ Create flashcards failed")
        
        # Test 4: Schedule Revision API
        print("\n   Testing POST /api/actions/schedule-revision...")
        revision_data = {
            "content_id": str(uuid.uuid4()),
            "content_type": "note",
            "title": "Quadratic Equations Review",
            "difficulty_level": 0.7
        }
        total_tests += 1
        
        success, response = self.run_test(
            "Schedule Revision",
            "POST",
            "actions/schedule-revision",
            200,
            data=revision_data
        )
        
        if success:
            schedule_id = response.get('schedule_id')
            print(f"   ✅ Revision scheduled: {schedule_id}")
            print(f"   Scheduled for: {response.get('scheduled_for', 'N/A')[:10]}")
            success_count += 1
        else:
            print(f"   ❌ Schedule revision failed")
        
        # Test 5: Get Notes API
        print("\n   Testing GET /api/actions/notes...")
        total_tests += 1
        
        success, response = self.run_test(
            "Get Notes",
            "GET",
            "actions/notes",
            200
        )
        
        if success:
            if isinstance(response, dict):
                notes = response.get('notes', [])
            elif isinstance(response, list):
                notes = response
            else:
                notes = []
            print(f"   ✅ Notes retrieved: {len(notes)} notes")
            success_count += 1
        else:
            print(f"   ❌ Get notes failed")
        
        # Test 6: Get Flashcard Decks API
        print("\n   Testing GET /api/actions/flashcard-decks...")
        total_tests += 1
        
        success, response = self.run_test(
            "Get Flashcard Decks",
            "GET",
            "actions/flashcard-decks",
            200
        )
        
        if success:
            if isinstance(response, dict):
                decks = response.get('decks', [])
            elif isinstance(response, list):
                decks = response
            else:
                decks = []
            print(f"   ✅ Flashcard decks retrieved: {len(decks)} decks")
            success_count += 1
        else:
            print(f"   ❌ Get flashcard decks failed")
        
        # Test 7: Get Revision Schedule API
        print("\n   Testing GET /api/actions/revision-schedule...")
        total_tests += 1
        
        success, response = self.run_test(
            "Get Revision Schedule",
            "GET",
            "actions/revision-schedule",
            200
        )
        
        if success:
            if isinstance(response, dict):
                schedule = response.get('schedule', [])
            elif isinstance(response, list):
                schedule = response
            else:
                schedule = []
            print(f"   ✅ Revision schedule retrieved: {len(schedule)} items")
            success_count += 1
        else:
            print(f"   ❌ Get revision schedule failed")
        
        print(f"\n   Phase D Summary: {success_count}/{total_tests} tests passed ({success_count/total_tests*100:.1f}%)")
        return success_count >= total_tests * 0.8

    def test_phase_e_analytics_apis(self):
        """Test Phase E: Analytics Integration APIs"""
        print("\n🎯 PHASE E: ANALYTICS INTEGRATION APIs")
        
        success_count = 0
        total_tests = 0
        
        # Test 1: Performance Stats API
        print("\n   Testing GET /api/analytics/performance-stats...")
        total_tests += 1
        
        success, response = self.run_test(
            "Performance Stats",
            "GET",
            "analytics/performance-stats",
            200
        )
        
        if success:
            stats = response.get('performance_stats', {})
            print(f"   ✅ Performance stats retrieved")
            print(f"   Total interactions: {stats.get('total_interactions', 0)}")
            print(f"   Average score: {stats.get('average_score', 0):.1f}")
            print(f"   Study streak: {stats.get('study_streak', 0)}")
            success_count += 1
        else:
            print(f"   ❌ Performance stats failed")
        
        # Test 2: Learning Analytics API
        print("\n   Testing GET /api/analytics/learning-analytics...")
        total_tests += 1
        
        success, response = self.run_test(
            "Learning Analytics",
            "GET",
            "analytics/learning-analytics?days_back=7",
            200
        )
        
        if success:
            analytics = response.get('learning_analytics', {})
            print(f"   ✅ Learning analytics retrieved")
            print(f"   Analytics ID: {analytics.get('analytics_id', 'N/A')}")
            print(f"   Total study time: {analytics.get('total_study_time', 0):.1f} hours")
            print(f"   Performance trend: {analytics.get('performance_trend', 'N/A')}")
            success_count += 1
        else:
            print(f"   ❌ Learning analytics failed")
        
        # Test 3: Wellness History API
        print("\n   Testing GET /api/analytics/wellness-history...")
        total_tests += 1
        
        success, response = self.run_test(
            "Wellness History",
            "GET",
            "analytics/wellness-history?days_back=30",
            200
        )
        
        if success:
            history = response.get('wellness_history', []) if isinstance(response, dict) else response
            print(f"   ✅ Wellness history retrieved: {len(history)} entries")
            success_count += 1
        else:
            print(f"   ❌ Wellness history failed")
        
        # Test 4: Wellness Check API
        print("\n   Testing POST /api/analytics/wellness-check...")
        wellness_data = {
            "stress_level": 6,
            "motivation_level": 7,
            "confidence_level": 5,
            "study_satisfaction": 8,
            "session_id": str(uuid.uuid4())
        }
        total_tests += 1
        
        success, response = self.run_test(
            "Wellness Check",
            "POST",
            "analytics/wellness-check",
            200,
            data=wellness_data
        )
        
        if success:
            check_id = response.get('check_id')
            print(f"   ✅ Wellness check completed: {check_id}")
            print(f"   Break recommended: {response.get('break_recommendation', False)}")
            print(f"   Motivational content: {'Yes' if response.get('motivational_content_suggested') else 'No'}")
            success_count += 1
        else:
            print(f"   ❌ Wellness check failed")
        
        print(f"\n   Phase E Summary: {success_count}/{total_tests} tests passed ({success_count/total_tests*100:.1f}%)")
        return success_count >= total_tests * 0.8

    def test_enhanced_dual_response_api(self):
        """Test Enhanced Dual Response API - Critical priority"""
        print("\n🎯 ENHANCED DUAL RESPONSE API (Critical Priority)")
        
        success_count = 0
        total_tests = 0
        
        # Test different types of questions
        test_scenarios = [
            {
                "name": "Mathematical Problem",
                "message": "Solve the quadratic equation x² - 5x + 6 = 0 step by step",
                "subject": "Mathematics"
            },
            {
                "name": "Physics Concept",
                "message": "Explain Newton's second law of motion with examples",
                "subject": "Physics"
            },
            {
                "name": "Motivational Query",
                "message": "I'm feeling stressed about my JEE preparation. Can you help me stay motivated?",
                "subject": "General"
            }
        ]
        
        for i, scenario in enumerate(test_scenarios):
            total_tests += 1
            print(f"\n   Testing scenario {i+1}/3: {scenario['name']}")
            print(f"   Question: '{scenario['message'][:50]}...'")
            print("   This may take 15-20 seconds for dual AI processing...")
            
            test_data = {
                "message": scenario['message'],
                "subject": scenario['subject'],
                "session_id": str(uuid.uuid4())
            }
            
            success, response = self.run_test(
                f"Enhanced Dual Response - {scenario['name']}",
                "POST",
                "ai/dual-response",
                200,
                data=test_data
            )
            
            if success:
                print(f"   ✅ Enhanced dual response received")
                
                # Check dual AI structure
                if 'dual_response' in response:
                    dual_response = response['dual_response']
                    primary_persona = dual_response.get('primary_persona', 'N/A')
                    secondary_persona = dual_response.get('secondary_persona', 'N/A')
                    scenario_type = dual_response.get('scenario_type', 'N/A')
                    confidence = dual_response.get('confidence', 0)
                    
                    print(f"   Primary persona: {primary_persona}")
                    print(f"   Secondary persona: {secondary_persona}")
                    print(f"   Scenario type: {scenario_type}")
                    print(f"   Confidence: {confidence:.2f}")
                    
                    # Validate response quality
                    primary_response = dual_response.get('primary_response', '')
                    secondary_response = dual_response.get('secondary_response', '')
                    
                    if len(primary_response) > 100 and len(secondary_response) > 100:
                        print(f"   ✅ Response quality validated")
                        success_count += 1
                    else:
                        print(f"   ⚠️  Response quality insufficient")
                elif 'response' in response:
                    # Single response format
                    print(f"   ✅ Single AI response received")
                    print(f"   Response length: {len(response.get('response', ''))}")
                    success_count += 1
                else:
                    print(f"   ⚠️  Unexpected response structure")
            else:
                print(f"   ❌ Enhanced dual response failed")
            
            time.sleep(5)  # Delay between AI calls
        
        print(f"\n   Enhanced Dual Response Summary: {success_count}/{total_tests} tests passed ({success_count/total_tests*100:.1f}%)")
        return success_count >= total_tests * 0.8

    def run_comprehensive_tests(self):
        """Run comprehensive Phase C, D, E testing"""
        print("🚀 Starting Dhruv AI Platform Phase C, D, E Backend Testing...")
        print(f"   Base URL: {self.base_url}")
        print(f"   Test User: {self.test_user_email}")
        print("   FOCUS: Phase C, D, E API fixes and pre-release polish")
        print("=" * 80)
        
        # Authentication first
        if not self.authenticate():
            print("❌ Authentication failed. Stopping tests.")
            return {"error": "Authentication failed"}
        
        # Run all phase tests
        phase_c_success = self.test_phase_c_guardrails_apis()
        phase_d_success = self.test_phase_d_action_buttons_apis()
        phase_e_success = self.test_phase_e_analytics_apis()
        dual_response_success = self.test_enhanced_dual_response_api()
        
        # Final summary
        print("\n" + "=" * 80)
        print("🏁 PHASE C, D, E TESTING COMPLETED")
        print(f"   Total Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Detailed results by phase
        print(f"\n📊 DETAILED RESULTS BY PHASE:")
        print(f"   Phase C (Guardrails): {'✅ PASS' if phase_c_success else '❌ FAIL'}")
        print(f"   Phase D (Action Buttons): {'✅ PASS' if phase_d_success else '❌ FAIL'}")
        print(f"   Phase E (Analytics): {'✅ PASS' if phase_e_success else '❌ FAIL'}")
        print(f"   Enhanced Dual Response: {'✅ PASS' if dual_response_success else '❌ FAIL'}")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED! Phase C, D, E APIs ready for production.")
        elif self.tests_passed >= self.tests_run * 0.9:
            print("✅ EXCELLENT! 90%+ tests passed. Minor issues to address.")
        elif self.tests_passed >= self.tests_run * 0.8:
            print("👍 GOOD! 80%+ tests passed. Some issues need attention.")
        else:
            print("⚠️  NEEDS ATTENTION! Less than 80% tests passed.")
        
        print("=" * 80)
        
        return {
            "phase_c": phase_c_success,
            "phase_d": phase_d_success, 
            "phase_e": phase_e_success,
            "dual_response": dual_response_success,
            "overall_success_rate": self.tests_passed / self.tests_run if self.tests_run > 0 else 0
        }

if __name__ == "__main__":
    tester = PhaseCDETester()
    results = tester.run_comprehensive_tests()
    print(f"\n🎯 FINAL RESULTS: {results}")