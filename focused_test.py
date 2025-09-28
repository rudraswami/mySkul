#!/usr/bin/env python3
"""
Focused Backend API Testing for Review Request
Tests specific endpoints mentioned in the review request:
1. Mock Test Generation API
2. Auto-Note Mentor APIs (7 endpoints)
3. Stress Management API
4. Dual-Layer AI APIs
"""

import requests
import json
import time
import sys

class FocusedTester:
    def __init__(self, base_url="https://smartlearn-hub-4.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.note_session_id = None
        self.test_user_email = "test@dhruvai.com"
        self.tests_run = 0
        self.tests_passed = 0

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
        """Login to get authentication token"""
        print("🔐 Authenticating...")
        
        login_data = {
            "email": self.test_user_email,
            "password": "password123"
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
            print(f"   ✅ Authenticated: {self.token[:20]}...")
            return True
        return False

    def test_mock_test_generation_api(self):
        """Test Mock Test Generation API with various subjects"""
        print("\n" + "="*50)
        print("🎯 TESTING MOCK TEST GENERATION API")
        print("="*50)
        
        if not self.token:
            print("❌ No authentication token")
            return False
        
        # Test different subjects as specified in review request
        test_subjects = [
            {"exam_type": "JEE", "subject": "Mathematics", "difficulty": 3, "num_questions": 5},
            {"exam_type": "JEE", "subject": "Physics", "difficulty": 4, "num_questions": 5},
            {"exam_type": "JEE", "subject": "Chemistry", "difficulty": 2, "num_questions": 5}
        ]
        
        success_count = 0
        
        for i, params in enumerate(test_subjects):
            print(f"\n📚 Testing {params['subject']} mock test generation...")
            
            success, response = self.run_test(
                f"Mock Test Generation - {params['subject']}",
                "POST",
                "mock-tests/generate",
                200,
                data=params
            )
            
            if success and 'test_id' in response:
                print(f"   ✅ Generated test ID: {response['test_id']}")
                print(f"   Questions: {len(response.get('questions', []))}")
                print(f"   Total marks: {response.get('total_marks', 0)}")
                success_count += 1
            else:
                print(f"   ❌ Failed to generate {params['subject']} test")
            
            time.sleep(2)  # Delay between AI calls
        
        print(f"\n📊 Mock Test Generation Results: {success_count}/{len(test_subjects)} passed")
        return success_count == len(test_subjects)

    def test_auto_note_mentor_apis(self):
        """Test all 7 Auto-Note Mentor API endpoints"""
        print("\n" + "="*50)
        print("📝 TESTING AUTO-NOTE MENTOR APIs")
        print("="*50)
        
        if not self.token:
            print("❌ No authentication token")
            return False
        
        results = {}
        
        # 1. Start recording session
        print("\n1️⃣ Testing /api/auto-notes/start-session")
        session_data = {
            "title": "Physics Class - Electromagnetic Induction",
            "subject": "Physics"
        }
        
        success, response = self.run_test(
            "Auto-Note Start Session",
            "POST",
            "auto-notes/start-session",
            200,
            data=session_data
        )
        
        if success and 'session_id' in response:
            self.note_session_id = response['session_id']
            results['start_session'] = True
            print(f"   ✅ Session started: {self.note_session_id}")
        else:
            results['start_session'] = False
            print("   ❌ Failed to start session")
            return False  # Can't continue without session
        
        # 2. Process transcription
        print("\n2️⃣ Testing /api/auto-notes/process-audio")
        audio_data = {
            "session_id": self.note_session_id,
            "transcription": "Today we will learn about electromagnetic induction and Faraday's law",
            "timestamp": 0.0,
            "sequence_number": 1,
            "confidence": 0.95
        }
        
        success, response = self.run_test(
            "Auto-Note Process Audio",
            "POST",
            "auto-notes/process-audio",
            200,
            data=audio_data
        )
        
        results['process_audio'] = success
        if success:
            print(f"   ✅ Audio processed, concepts detected: {len(response.get('concepts_detected', []))}")
        
        # 3. End session and generate notes
        print("\n3️⃣ Testing /api/auto-notes/end-session")
        success, response = self.run_test(
            "Auto-Note End Session",
            "POST",
            f"auto-notes/end-session?session_id={self.note_session_id}",
            200
        )
        
        results['end_session'] = success
        if success:
            print(f"   ✅ Session completed, status: {response.get('status', 'N/A')}")
            print(f"   Key concepts: {len(response.get('structured_notes', {}).get('key_concepts', []))}")
        
        # 4. Get session details
        print("\n4️⃣ Testing /api/auto-notes/session/{id}")
        success, response = self.run_test(
            "Get Auto-Note Session",
            "GET",
            f"auto-notes/{self.note_session_id}",
            200
        )
        
        results['get_session'] = success
        if success:
            print(f"   ✅ Session retrieved: {response.get('title', 'N/A')}")
        
        # 5. List all sessions
        print("\n5️⃣ Testing /api/auto-notes/sessions")
        success, response = self.run_test(
            "List Auto-Note Sessions",
            "GET",
            "auto-notes/sessions",
            200
        )
        
        results['list_sessions'] = success
        if success:
            print(f"   ✅ Sessions listed: {response.get('total_sessions', 0)} total")
        
        # 6. Explain note point
        print("\n6️⃣ Testing /api/auto-notes/explain-point")
        explain_data = {
            "session_id": self.note_session_id,
            "point_reference": "concept_1",
            "additional_context": "Need more details about electromagnetic induction"
        }
        
        success, response = self.run_test(
            "Explain Note Point",
            "POST",
            "auto-notes/explain-point",
            200,
            data=explain_data
        )
        
        results['explain_point'] = success
        if success:
            print(f"   ✅ Point explained with dual AI analysis")
        
        # 7. Generate flashcards
        print("\n7️⃣ Testing /api/auto-notes/generate-flashcards")
        flashcard_data = {
            "session_id": self.note_session_id,
            "specific_concepts": ["electromagnetic induction", "Faraday's law"]
        }
        
        success, response = self.run_test(
            "Generate Flashcards",
            "POST",
            "auto-notes/generate-flashcards",
            200,
            data=flashcard_data
        )
        
        results['generate_flashcards'] = success
        if success:
            print(f"   ✅ Flashcards generated: {response.get('flashcards_generated', 0)}")
        
        # Summary
        passed = sum(results.values())
        total = len(results)
        print(f"\n📊 Auto-Note Mentor API Results: {passed}/{total} endpoints passed")
        
        for endpoint, result in results.items():
            status = "✅" if result else "❌"
            print(f"   {status} {endpoint}")
        
        return passed == total

    def test_stress_management_api(self):
        """Test Stress Management API with Pydantic request models"""
        print("\n" + "="*50)
        print("🧘 TESTING STRESS MANAGEMENT API")
        print("="*50)
        
        if not self.token:
            print("❌ No authentication token")
            return False
        
        # Test stress assessment with proper Pydantic model
        assessment_data = {
            "stress_level": 7,
            "anxiety_level": 6,
            "sleep_quality": 4,
            "study_motivation": 5,
            "physical_symptoms": ["headache", "fatigue"],
            "emotional_state": "overwhelmed"
        }
        
        success, response = self.run_test(
            "Stress Assessment",
            "POST",
            "wellness/stress-assessment",
            200,
            data=assessment_data
        )
        
        if success:
            print(f"   ✅ Stress assessment completed")
            print(f"   Wellness score: {response.get('wellness_score', 0):.1f}/10")
            print(f"   Recommendations: {len(response.get('recommendations', []))}")
            return True
        else:
            print(f"   ❌ Stress assessment failed")
            return False

    def test_dual_layer_ai_apis(self):
        """Test Dual-Layer AI APIs for verification"""
        print("\n" + "="*50)
        print("🤖 TESTING DUAL-LAYER AI APIs")
        print("="*50)
        
        if not self.token:
            print("❌ No authentication token")
            return False
        
        # Test data
        test_message = {
            "message": "Solve x² + 5x + 6 = 0 step by step",
            "subject": "Mathematics"
        }
        
        results = {}
        
        # 1. Test dual-response
        print("\n1️⃣ Testing /api/ai/dual-response")
        success, response = self.run_test(
            "Dual AI Response",
            "POST",
            "ai/dual-response",
            200,
            data=test_message
        )
        
        results['dual_response'] = success
        if success:
            dual_resp = response.get('dual_response', {})
            print(f"   ✅ Dual response received")
            print(f"   Primary persona: {dual_resp.get('primary', {}).get('persona', 'N/A')}")
            print(f"   Secondary persona: {dual_resp.get('secondary', {}).get('persona', 'N/A')}")
        
        # 2. Test mentor-only
        print("\n2️⃣ Testing /api/ai/mentor-only")
        success, response = self.run_test(
            "Mentor Only Response",
            "POST",
            "ai/mentor-only",
            200,
            data=test_message
        )
        
        results['mentor_only'] = success
        if success:
            print(f"   ✅ Mentor response received")
            print(f"   Persona: {response.get('persona', 'N/A')}")
        
        # 3. Test professor-only
        print("\n3️⃣ Testing /api/ai/professor-only")
        success, response = self.run_test(
            "Professor Only Response",
            "POST",
            "ai/professor-only",
            200,
            data=test_message
        )
        
        results['professor_only'] = success
        if success:
            print(f"   ✅ Professor response received")
            print(f"   Persona: {response.get('persona', 'N/A')}")
        
        # Summary
        passed = sum(results.values())
        total = len(results)
        print(f"\n📊 Dual-Layer AI Results: {passed}/{total} endpoints passed")
        
        for endpoint, result in results.items():
            status = "✅" if result else "❌"
            print(f"   {status} {endpoint}")
        
        return passed == total

def main():
    print("🚀 FOCUSED BACKEND API TESTING - REVIEW REQUEST")
    print("Testing specific endpoints mentioned in review request")
    print("="*60)
    
    tester = FocusedTester()
    
    # Authenticate first
    if not tester.authenticate():
        print("❌ Authentication failed - cannot proceed with tests")
        return 1
    
    # Run focused tests
    test_results = {}
    
    print("\n🎯 Running focused tests for review request...")
    
    # 1. Mock Test Generation API
    test_results['mock_test_generation'] = tester.test_mock_test_generation_api()
    
    # 2. Auto-Note Mentor APIs (7 endpoints)
    test_results['auto_note_mentor'] = tester.test_auto_note_mentor_apis()
    
    # 3. Stress Management API
    test_results['stress_management'] = tester.test_stress_management_api()
    
    # 4. Dual-Layer AI APIs
    test_results['dual_layer_ai'] = tester.test_dual_layer_ai_apis()
    
    # Final Results
    print("\n" + "="*60)
    print("📊 FOCUSED TEST RESULTS SUMMARY")
    print("="*60)
    
    passed_categories = sum(test_results.values())
    total_categories = len(test_results)
    
    print(f"API Categories Tested: {total_categories}")
    print(f"Categories Passed: {passed_categories}")
    print(f"Individual Tests Run: {tester.tests_run}")
    print(f"Individual Tests Passed: {tester.tests_passed}")
    print(f"Overall Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    print(f"\n📋 CATEGORY RESULTS:")
    for category, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status} {category.replace('_', ' ').title()}")
    
    if passed_categories == total_categories:
        print(f"\n🎉 ALL REVIEW REQUEST TESTS PASSED!")
        print(f"✅ Mock Test Generation API working correctly")
        print(f"✅ All 7 Auto-Note Mentor APIs functional")
        print(f"✅ Stress Management API accepts Pydantic models")
        print(f"✅ Dual-Layer AI APIs verified working")
    else:
        print(f"\n⚠️  SOME TESTS FAILED - REVIEW NEEDED")
        failed_categories = [cat for cat, result in test_results.items() if not result]
        print(f"Failed categories: {', '.join(failed_categories)}")
    
    return 0 if passed_categories == total_categories else 1

if __name__ == "__main__":
    sys.exit(main())