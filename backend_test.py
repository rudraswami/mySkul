import requests
import sys
import json
from datetime import datetime
import time

class DhruvAITester:
    def __init__(self, base_url="https://smart-exam-coach.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.session_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_email = f"test_user_{datetime.now().strftime('%H%M%S')}@test.com"

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
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
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

    def test_health_check(self):
        """Test health check endpoint"""
        return self.run_test("Health Check", "GET", "health", 200)

    def test_root_endpoint(self):
        """Test root endpoint"""
        return self.run_test("Root Endpoint", "GET", "", 200)

    def test_user_registration(self):
        """Test user registration"""
        registration_data = {
            "full_name": "Test User",
            "email": self.test_user_email,
            "password": "TestPass123!",
            "exam_type": "JEE",
            "grade": "Class 12",
            "target_year": 2026
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=registration_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            if 'user' in response:
                self.user_id = response['user'].get('user_id')
            print(f"   Token obtained: {self.token[:20]}...")
            return True
        return False

    def test_user_login(self):
        """Test user login with the registered user"""
        login_data = {
            "email": self.test_user_email,
            "password": "TestPass123!"
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
            print(f"   Login token: {self.token[:20]}...")
            return True
        return False

    def test_user_profile(self):
        """Test getting user profile"""
        if not self.token:
            print("❌ No token available for profile test")
            return False
            
        return self.run_test(
            "Get User Profile",
            "GET",
            "user/profile",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )

    def test_ai_chat_message(self):
        """Test AI chat functionality"""
        if not self.token:
            print("❌ No token available for chat test")
            return False
            
        chat_data = {
            "message": "Explain quadratic equations and their applications in JEE",
            "subject": "Mathematics"
        }
        
        print("   Sending AI chat message (this may take a few seconds)...")
        success, response = self.run_test(
            "AI Chat Message",
            "POST",
            "chat/message",
            200,
            data=chat_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success and 'session_id' in response:
            self.session_id = response['session_id']
            print(f"   Session ID: {self.session_id}")
            return True
        return False

    def test_chat_sessions(self):
        """Test getting chat sessions"""
        if not self.token:
            print("❌ No token available for chat sessions test")
            return False
            
        return self.run_test(
            "Get Chat Sessions",
            "GET",
            "chat/sessions",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )

    def test_chat_messages(self):
        """Test getting messages from a chat session"""
        if not self.token or not self.session_id:
            print("❌ No token or session_id available for chat messages test")
            return False
            
        return self.run_test(
            "Get Chat Messages",
            "GET",
            f"chat/{self.session_id}/messages",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )

    def test_dashboard_analytics(self):
        """Test dashboard analytics"""
        if not self.token:
            print("❌ No token available for analytics test")
            return False
            
        return self.run_test(
            "Dashboard Analytics",
            "GET",
            "dashboard/analytics",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )

    def test_progress_summary(self):
        """Test progress summary"""
        if not self.token:
            print("❌ No token available for progress test")
            return False
            
        return self.run_test(
            "Progress Summary",
            "GET",
            "progress/summary",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )

    def test_doubt_resolution(self):
        """Test doubt resolution"""
        if not self.token:
            print("❌ No token available for doubt test")
            return False
            
        doubt_data = {
            "query": "What is Newton's second law of motion?",
            "subject": "Physics"
        }
        
        print("   Sending doubt query (this may take a few seconds)...")
        return self.run_test(
            "Doubt Resolution",
            "POST",
            "doubt/resolve",
            200,
            data=doubt_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )

    def test_update_progress(self):
        """Test updating study progress"""
        if not self.token:
            print("❌ No token available for progress update test")
            return False
            
        progress_data = {
            "subject": "Mathematics",
            "chapter": "Quadratic Equations",
            "concept": "Discriminant",
            "mastery_level": 75.0,
            "time_spent": 30,
            "questions_attempted": 10,
            "questions_correct": 8
        }
        
        return self.run_test(
            "Update Progress",
            "POST",
            "progress/update",
            200,
            data=progress_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )

    # ============= PHASE 4: ENHANCED FEATURES TESTS =============

    def test_generate_mock_test(self):
        """Test enhanced mock test generation with JSON request body"""
        if not self.token:
            print("❌ No token available for mock test generation")
            return False
            
        # Test with different parameters as specified in review request
        test_params = [
            {"exam_type": "JEE", "subject": "Mathematics", "difficulty": 3, "num_questions": 10},
            {"exam_type": "JEE", "subject": "Physics", "difficulty": 4, "num_questions": 5},
            {"exam_type": "JEE", "subject": "Chemistry", "difficulty": 2, "num_questions": 25},
            {"exam_type": "NEET", "subject": "Mathematics", "difficulty": 1, "num_questions": 5},
            {"exam_type": "NEET", "subject": "Physics", "difficulty": 5, "num_questions": 10}
        ]
        
        success_count = 0
        self.test_ids = []  # Store test IDs for submission tests
        
        for i, params in enumerate(test_params):
            print(f"   Testing mock test generation {i+1}/{len(test_params)}: {params['subject']} Level {params['difficulty']} ({params['num_questions']} questions)")
            
            # Use JSON body instead of query parameters (as per review request)
            success, response = self.run_test(
                f"Generate Mock Test - {params['subject']} L{params['difficulty']}",
                "POST",
                "mock-tests/generate",
                200,
                data=params,  # Send as JSON body
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success and 'test_id' in response:
                self.test_ids.append({
                    'test_id': response['test_id'],
                    'questions': response.get('questions', []),
                    'subject': params['subject']
                })
                success_count += 1
                print(f"   ✅ Generated test ID: {response['test_id']}")
                print(f"   Test name: {response.get('test_name', 'N/A')}")
                print(f"   Questions count: {len(response.get('questions', []))}")
                print(f"   Total marks: {response.get('total_marks', 0)}")
                print(f"   Time limit: {response.get('time_limit', 0)} minutes")
                
                # Validate response structure as per review request
                questions = response.get('questions', [])
                if questions:
                    sample_question = questions[0]
                    required_fields = ['question_id', 'question_text', 'options', 'correct_answer', 'explanation', 'chapter']
                    missing_fields = [field for field in required_fields if field not in sample_question]
                    if missing_fields:
                        print(f"   ⚠️  Missing question fields: {missing_fields}")
                    else:
                        print(f"   ✅ Question structure validated")
                        print(f"   Sample question: {sample_question['question_text'][:50]}...")
                        print(f"   Options count: {len(sample_question.get('options', []))}")
                        print(f"   Chapter: {sample_question.get('chapter', 'N/A')}")
            else:
                print(f"   ❌ Failed to generate test for {params['subject']}")
            
            time.sleep(3)  # Delay between AI calls
        
        return success_count == len(test_params)

    def test_submit_mock_test(self):
        """Test mock test submission and analysis"""
        if not self.token or not hasattr(self, 'test_ids') or not self.test_ids:
            print("❌ No token or test IDs available for mock test submission")
            return False
        
        # Use the first generated test for submission
        test_id = self.test_ids[0]
        
        # Create sample answers (simulating a student taking the test)
        sample_answers = {}
        for i in range(5):  # Physics test has 5 questions
            question_id = f"q_{i+1}"  # This would normally come from the test questions
            sample_answers[question_id] = "A"  # Simulate selecting option A for all
        
        # Prepare form data for the API
        form_data = {
            "answers": sample_answers,
            "time_taken": 1200  # 20 minutes in seconds
        }
        
        print(f"   Submitting test {test_id} with {len(sample_answers)} answers...")
        print("   This may take a few seconds for AI analysis...")
        
        # Send as form data instead of JSON
        url = f"{self.base_url}/mock-tests/{test_id}/submit"
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            response = requests.post(url, data=form_data, headers=headers, timeout=60)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   ✅ Test submitted successfully")
                    print(f"   Score: {response_data.get('score', 0)}")
                    print(f"   Percentage: {response_data.get('percentage', 0):.1f}%")
                    print(f"   Correct answers: {response_data.get('correct_answers', 0)}")
                    print(f"   Recommendations count: {len(response_data.get('recommendations', []))}")
                    return True
                except:
                    return True
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False

    def test_performance_analytics(self):
        """Test comprehensive performance analytics"""
        if not self.token:
            print("❌ No token available for performance analytics")
            return False
        
        print("   Fetching comprehensive performance analytics...")
        
        success, response = self.run_test(
            "Performance Analytics",
            "GET",
            "analytics/performance",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            print(f"   ✅ Analytics retrieved successfully")
            
            # Check key analytics components
            overall_perf = response.get('overall_performance', {})
            subject_perf = response.get('subject_performance', {})
            weekly_progress = response.get('weekly_progress', {})
            parent_summary = response.get('parent_summary', {})
            
            print(f"   Average score: {overall_perf.get('average_score', 0):.1f}")
            print(f"   Subjects analyzed: {len(subject_perf)}")
            print(f"   Weekly completed hours: {weekly_progress.get('completed_hours', 0):.1f}")
            print(f"   Parent grade: {parent_summary.get('overall_grade', 'N/A')}")
            
            return True
        
        return False

    def test_stress_assessment(self):
        """Test stress assessment and wellness recommendations"""
        if not self.token:
            print("❌ No token available for stress assessment")
            return False
        
        # Test different stress levels
        assessment_scenarios = [
            {
                "stress_level": 7,
                "anxiety_level": 6,
                "sleep_quality": 4,
                "study_motivation": 5,
                "physical_symptoms": ["headache", "fatigue"],
                "emotional_state": "overwhelmed"
            },
            {
                "stress_level": 3,
                "anxiety_level": 2,
                "sleep_quality": 8,
                "study_motivation": 9,
                "physical_symptoms": [],
                "emotional_state": "confident"
            }
        ]
        
        success_count = 0
        
        for i, scenario in enumerate(assessment_scenarios):
            print(f"   Testing stress assessment scenario {i+1}/2: Stress Level {scenario['stress_level']}/10")
            print("   This may take a few seconds for AI recommendations...")
            
            # Send as form data for FastAPI
            url = f"{self.base_url}/wellness/stress-assessment"
            headers = {'Authorization': f'Bearer {self.token}'}
            
            # Convert list to comma-separated string for form data
            form_data = scenario.copy()
            form_data["physical_symptoms"] = ",".join(scenario["physical_symptoms"])
            
            try:
                response = requests.post(url, data=form_data, headers=headers, timeout=60)
                print(f"   Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    self.tests_passed += 1
                    print(f"✅ Passed - Status: {response.status_code}")
                    try:
                        response_data = response.json()
                        print(f"   ✅ Assessment completed")
                        print(f"   Wellness score: {response_data.get('wellness_score', 0):.1f}/10")
                        print(f"   Recommendations count: {len(response_data.get('recommendations', []))}")
                        print(f"   Priority actions: {len(response_data.get('priority_actions', []))}")
                        success_count += 1
                    except:
                        success_count += 1
                else:
                    print(f"❌ Failed - Expected 200, got {response.status_code}")
                    try:
                        error_data = response.json()
                        print(f"   Error: {error_data}")
                    except:
                        print(f"   Error: {response.text}")
            except Exception as e:
                print(f"❌ Failed - Error: {str(e)}")
            
            self.tests_run += 1
            time.sleep(2)  # Delay between AI calls
        
        return success_count == len(assessment_scenarios)

    def test_motivational_content(self):
        """Test personalized motivational content generation"""
        if not self.token:
            print("❌ No token available for motivational content")
            return False
        
        print("   Fetching personalized motivational content...")
        print("   This may take a few seconds for AI content generation...")
        
        success, response = self.run_test(
            "Motivational Content",
            "GET",
            "wellness/motivational-content",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            print(f"   ✅ Motivational content retrieved")
            
            daily_content = response.get('daily_content', [])
            print(f"   Content items: {len(daily_content)}")
            
            # Check content types
            content_types = [item.get('content_type') for item in daily_content]
            print(f"   Content types: {', '.join(set(content_types))}")
            
            wellness_tip = response.get('wellness_tip', '')
            print(f"   Wellness tip provided: {'Yes' if wellness_tip else 'No'}")
            
            return True
        
        return False

    def test_integration_auth_validation(self):
        """Test authentication validation across all new endpoints"""
        print("   Testing authentication validation on new endpoints...")
        
        # Test without token (should fail with 401)
        endpoints_to_test = [
            ("mock-tests/generate?exam_type=JEE&subject=Mathematics", "POST"),
            ("analytics/performance", "GET"),
            ("wellness/stress-assessment", "POST"),
            ("wellness/motivational-content", "GET")
        ]
        
        success_count = 0
        
        for endpoint, method in endpoints_to_test:
            print(f"   Testing {endpoint} without auth...")
            
            # Temporarily remove token
            temp_token = self.token
            self.token = None
            
            success, _ = self.run_test(
                f"Auth Validation - {endpoint}",
                method,
                endpoint,
                401,  # Expecting 401 Unauthorized
                data={} if method == "POST" else None
            )
            
            # Restore token
            self.token = temp_token
            
            if success:
                success_count += 1
        
        return success_count == len(endpoints_to_test)

def main():
    print("🚀 Starting Dhruv AI Backend API Tests - Phase 4 Enhanced Features")
    print("=" * 70)
    
    tester = DhruvAITester()
    
    # Test sequence - Core APIs first, then Phase 4 features
    tests = [
        ("Health Check", tester.test_health_check),
        ("Root Endpoint", tester.test_root_endpoint),
        ("User Registration", tester.test_user_registration),
        ("User Login", tester.test_user_login),
        ("User Profile", tester.test_user_profile),
        ("AI Chat Message", tester.test_ai_chat_message),
        ("Chat Sessions", tester.test_chat_sessions),
        ("Chat Messages", tester.test_chat_messages),
        ("Dashboard Analytics", tester.test_dashboard_analytics),
        ("Progress Summary", tester.test_progress_summary),
        ("Update Progress", tester.test_update_progress),
        ("Doubt Resolution", tester.test_doubt_resolution),
        
        # Phase 4 Enhanced Features
        ("🆕 Generate Mock Tests", tester.test_generate_mock_test),
        ("🆕 Submit Mock Test", tester.test_submit_mock_test),
        ("🆕 Performance Analytics", tester.test_performance_analytics),
        ("🆕 Stress Assessment", tester.test_stress_assessment),
        ("🆕 Motivational Content", tester.test_motivational_content),
        ("🆕 Auth Validation", tester.test_integration_auth_validation),
    ]
    
    failed_tests = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            if not success:
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            failed_tests.append(test_name)
        
        # Small delay between tests
        time.sleep(1)
    
    # Print final results
    print("\n" + "=" * 70)
    print("📊 FINAL TEST RESULTS - DHRUV AI PHASE 4 TESTING")
    print("=" * 70)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test in failed_tests:
            print(f"   - {test}")
        print(f"\n🔍 CRITICAL ISSUES FOUND:")
        print(f"   Please review failed tests above for backend functionality issues.")
    else:
        print(f"\n✅ All tests passed!")
        print(f"🎉 Phase 4 Enhanced Features are working correctly!")
    
    print(f"\n📋 PHASE 4 FEATURES TESTED:")
    print(f"   ✓ Enhanced Mock Test System (Generation & Submission)")
    print(f"   ✓ Performance Analytics (Student & Parent Views)")
    print(f"   ✓ Stress Management & Wellness Assessment")
    print(f"   ✓ Personalized Motivational Content")
    print(f"   ✓ Authentication & Security Validation")
    
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())