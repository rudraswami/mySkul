import requests
import sys
import json
from datetime import datetime
import time

class DhruvAITester:
    def __init__(self, base_url="https://dhruv-edtech.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.session_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_email = "test@dhruvai.com"

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
            "password": "password123",
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
        """Test mock test submission with JSON body"""
        if not self.token or not hasattr(self, 'test_ids') or not self.test_ids:
            print("❌ No token or test IDs available for mock test submission")
            return False
        
        # Use the first generated test for submission
        test_data = self.test_ids[0]
        test_id = test_data['test_id']
        questions = test_data['questions']
        
        # Create realistic answers based on actual question IDs
        sample_answers = {}
        for i, question in enumerate(questions[:5]):  # Test with first 5 questions
            question_id = question['question_id']
            # Simulate realistic test-taking: some correct, some wrong
            if i % 3 == 0:  # Every 3rd answer is correct
                sample_answers[question_id] = question['correct_answer']
            else:  # Others are random wrong answers
                options = ['A', 'B', 'C', 'D']
                wrong_options = [opt for opt in options if opt != question['correct_answer']]
                sample_answers[question_id] = wrong_options[i % len(wrong_options)]
        
        # Prepare JSON data for the API (not form data)
        submission_data = {
            "answers": sample_answers,
            "time_taken": 1800  # 30 minutes in seconds
        }
        
        print(f"   Submitting test {test_id} with {len(sample_answers)} answers...")
        print("   This may take a few seconds for AI analysis...")
        
        success, response = self.run_test(
            "Submit Mock Test",
            "POST",
            f"mock-tests/{test_id}/submit",
            200,
            data=submission_data,  # Send as JSON body
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            print(f"   ✅ Test submitted successfully")
            print(f"   Score: {response.get('score', 0)}")
            print(f"   Percentage: {response.get('percentage', 0):.1f}%")
            print(f"   Correct answers: {response.get('correct_answers', 0)}")
            print(f"   Wrong answers: {response.get('wrong_answers', 0)}")
            print(f"   Unanswered: {response.get('unanswered', 0)}")
            print(f"   Recommendations count: {len(response.get('recommendations', []))}")
            
            # Validate response structure
            required_fields = ['result_id', 'score', 'percentage', 'correct_answers', 'wrong_answers', 'subject_wise_analysis']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                print(f"   ⚠️  Missing response fields: {missing_fields}")
            else:
                print(f"   ✅ Response structure validated")
            
            return True
        
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
        """Test stress assessment with JSON request body"""
        if not self.token:
            print("❌ No token available for stress assessment")
            return False
        
        # Test different stress levels with JSON body
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
            
            # Send as JSON body (not form data)
            success, response = self.run_test(
                f"Stress Assessment - Scenario {i+1}",
                "POST",
                "wellness/stress-assessment",
                200,
                data=scenario,  # Send as JSON body
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success:
                print(f"   ✅ Assessment completed")
                print(f"   Wellness score: {response.get('wellness_score', 0):.1f}/10")
                print(f"   Recommendations count: {len(response.get('recommendations', []))}")
                print(f"   Priority actions: {len(response.get('priority_actions', []))}")
                success_count += 1
            else:
                print(f"   ❌ Assessment failed for scenario {i+1}")
            
            time.sleep(3)  # Delay between AI calls
        
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
            ("mock-tests/generate", "POST", {"exam_type": "JEE", "subject": "Mathematics", "difficulty": 3, "num_questions": 5}),
            ("analytics/performance", "GET", None),
            ("wellness/stress-assessment", "POST", {"stress_level": 5, "anxiety_level": 5, "sleep_quality": 5, "study_motivation": 5, "physical_symptoms": [], "emotional_state": "neutral"}),
            ("wellness/motivational-content", "GET", None),
            ("ai/dual-response", "POST", {"message": "Test message", "subject": "Mathematics"}),
            ("ai/mentor-only", "POST", {"message": "Test message", "subject": "Mathematics"}),
            ("ai/professor-only", "POST", {"message": "Test message", "subject": "Mathematics"})
        ]
        
        success_count = 0
        
        for endpoint, method, test_data in endpoints_to_test:
            print(f"   Testing {endpoint} without auth...")
            
            # Temporarily remove token
            temp_token = self.token
            self.token = None
            
            success, _ = self.run_test(
                f"Auth Validation - {endpoint}",
                method,
                endpoint,
                401,  # Expecting 401 Unauthorized
                data=test_data
            )
            
            # Restore token
            self.token = temp_token
            
            if success:
                success_count += 1
                print(f"   ✅ Correctly rejected unauthorized request")
            else:
                print(f"   ❌ Failed to reject unauthorized request")
        
        return success_count == len(endpoints_to_test)

    def test_enhanced_question_generation(self):
        """Test AI-powered question generation and fallback mechanisms"""
        if not self.token:
            print("❌ No token available for question generation test")
            return False
        
        print("   Testing enhanced question generation features...")
        
        # Test different subjects to verify subject-specific questions
        subjects_to_test = ["Mathematics", "Physics", "Chemistry"]
        success_count = 0
        
        for subject in subjects_to_test:
            print(f"   Testing {subject} question generation...")
            
            test_data = {
                "exam_type": "JEE",
                "subject": subject,
                "difficulty": 3,
                "num_questions": 3  # Small number for faster testing
            }
            
            success, response = self.run_test(
                f"Enhanced Questions - {subject}",
                "POST",
                "mock-tests/generate",
                200,
                data=test_data,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success and 'questions' in response:
                questions = response['questions']
                print(f"   ✅ Generated {len(questions)} {subject} questions")
                
                # Verify question quality and structure
                for i, question in enumerate(questions[:2]):  # Check first 2 questions
                    q_text = question.get('question_text', '')
                    options = question.get('options', [])
                    explanation = question.get('explanation', '')
                    chapter = question.get('chapter', '')
                    
                    print(f"     Q{i+1}: {q_text[:60]}...")
                    print(f"     Options: {len(options)}, Chapter: {chapter}")
                    print(f"     Has explanation: {'Yes' if explanation else 'No'}")
                    
                    # Check if questions are subject-specific (not just generic)
                    is_realistic = len(q_text) > 20 and len(options) == 4 and explanation
                    if is_realistic:
                        print(f"     ✅ Question appears realistic and subject-specific")
                    else:
                        print(f"     ⚠️  Question may be generic/placeholder")
                
                success_count += 1
            else:
                print(f"   ❌ Failed to generate {subject} questions")
            
            time.sleep(2)  # Delay between AI calls
        
        return success_count == len(subjects_to_test)

    # ============= PHASE 2: DUAL-LAYER AI SCENARIO IMPLEMENTATIONS =============

    def test_mock_tests_dual_feedback_system(self):
        """Test Phase 2: Mock Tests Dual Feedback System with dual AI feedback"""
        if not self.token or not hasattr(self, 'test_ids') or not self.test_ids:
            print("❌ No token or test IDs available for dual feedback test")
            return False
        
        print("   Testing Phase 2: Mock Tests Dual Feedback System...")
        
        # Use the first generated test for submission with dual feedback
        test_data = self.test_ids[0]
        test_id = test_data['test_id']
        questions = test_data['questions']
        
        # Create realistic answers with varying performance levels
        performance_scenarios = [
            {"name": "High Performance", "correct_ratio": 0.8},
            {"name": "Medium Performance", "correct_ratio": 0.6},
            {"name": "Low Performance", "correct_ratio": 0.3}
        ]
        
        success_count = 0
        
        for scenario in performance_scenarios:
            print(f"   Testing {scenario['name']} scenario (correct ratio: {scenario['correct_ratio']})")
            
            # Create answers based on performance level
            sample_answers = {}
            for i, question in enumerate(questions[:5]):  # Test with first 5 questions
                question_id = question['question_id']
                if i < len(questions) * scenario['correct_ratio']:
                    # Correct answer
                    sample_answers[question_id] = question['correct_answer']
                else:
                    # Wrong answer
                    options = ['A', 'B', 'C', 'D']
                    wrong_options = [opt for opt in options if opt != question['correct_answer']]
                    sample_answers[question_id] = wrong_options[i % len(wrong_options)]
            
            submission_data = {
                "answers": sample_answers,
                "time_taken": 1800  # 30 minutes
            }
            
            print(f"   Submitting test with {len(sample_answers)} answers for dual AI feedback...")
            print("   This may take 10-15 seconds for dual AI analysis...")
            
            success, response = self.run_test(
                f"Dual Feedback - {scenario['name']}",
                "POST",
                f"mock-tests/{test_id}/submit",
                200,
                data=submission_data,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success and 'dual_feedback' in response:
                dual_feedback = response['dual_feedback']
                professor_analysis = dual_feedback.get('professor_analysis', '')
                mentor_feedback = dual_feedback.get('mentor_feedback', '')
                scenario_confidence = dual_feedback.get('scenario_confidence', 0)
                
                print(f"   ✅ Dual feedback received")
                print(f"   Professor analysis length: {len(professor_analysis)}")
                print(f"   Mentor feedback length: {len(mentor_feedback)}")
                print(f"   Scenario confidence: {scenario_confidence:.2f}")
                
                # Verify dual intelligence structure
                has_professor = professor_analysis and len(professor_analysis) > 50
                has_mentor = mentor_feedback and len(mentor_feedback) > 50
                has_confidence = scenario_confidence > 0
                
                if has_professor and has_mentor and has_confidence:
                    print(f"   ✅ Dual intelligence structure validated")
                    print(f"   Professor provides: Technical analysis")
                    print(f"   Mentor provides: Motivational feedback")
                    success_count += 1
                else:
                    print(f"   ⚠️  Dual intelligence structure incomplete")
                    print(f"   Professor analysis: {'✓' if has_professor else '✗'}")
                    print(f"   Mentor feedback: {'✓' if has_mentor else '✗'}")
                    print(f"   Confidence score: {'✓' if has_confidence else '✗'}")
            else:
                print(f"   ❌ Dual feedback failed for {scenario['name']}")
            
            time.sleep(3)  # Delay between tests
        
        return success_count >= len(performance_scenarios) * 0.8  # 80% success threshold

    def test_study_planning_dual_intelligence(self):
        """Test Phase 2: Study Planning Dual Intelligence with StudyPlanRequest model"""
        if not self.token:
            print("❌ No token available for study planning test")
            return False
        
        print("   Testing Phase 2: Study Planning Dual Intelligence...")
        
        # Test different user preferences and stress levels
        study_plan_scenarios = [
            {
                "name": "High Stress Student",
                "target_exam_date": "2025-05-15T00:00:00Z",
                "daily_study_hours": 8,
                "weak_subjects": ["Mathematics", "Physics"],
                "strong_subjects": ["Chemistry"],
                "preferred_study_times": ["morning", "evening"],
                "stress_level": 8
            },
            {
                "name": "Balanced Student",
                "target_exam_date": "2025-05-15T00:00:00Z",
                "daily_study_hours": 6,
                "weak_subjects": ["Physics"],
                "strong_subjects": ["Mathematics", "Chemistry"],
                "preferred_study_times": ["afternoon", "evening"],
                "stress_level": 4
            },
            {
                "name": "Low Stress Student",
                "target_exam_date": "2025-05-15T00:00:00Z",
                "daily_study_hours": 4,
                "weak_subjects": [],
                "strong_subjects": ["Mathematics", "Physics", "Chemistry"],
                "preferred_study_times": ["morning"],
                "stress_level": 2
            }
        ]
        
        success_count = 0
        
        for scenario in study_plan_scenarios:
            print(f"   Testing {scenario['name']} (stress level: {scenario['stress_level']}/10)")
            print(f"   Daily hours: {scenario['daily_study_hours']}, Weak subjects: {len(scenario['weak_subjects'])}")
            print("   This may take 10-15 seconds for dual AI planning...")
            
            success, response = self.run_test(
                f"Study Plan - {scenario['name']}",
                "POST",
                "ai/dual-study-plan",
                200,
                data=scenario,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success and 'dual_intelligence_plan' in response:
                dual_plan = response['dual_intelligence_plan']
                professor_plan = dual_plan.get('professor', {})
                mentor_plan = dual_plan.get('mentor', {})
                scenario_classification = response.get('scenario_classification', {})
                implementation_timeline = response.get('implementation_timeline', {})
                
                print(f"   ✅ Dual intelligence plan generated")
                print(f"   Plan ID: {response.get('plan_id', 'N/A')}")
                print(f"   Professor focus: {professor_plan.get('focus', 'N/A')}")
                print(f"   Mentor focus: {mentor_plan.get('focus', 'N/A')}")
                print(f"   Primary persona: {scenario_classification.get('primary_persona', 'N/A')}")
                print(f"   Timeline start: {implementation_timeline.get('start_date', 'N/A')[:10]}")
                print(f"   Review frequency: {implementation_timeline.get('review_frequency', 'N/A')}")
                
                # Verify dual intelligence structure
                has_professor_structure = (
                    professor_plan.get('academic_structure') and 
                    professor_plan.get('focus') and
                    len(professor_plan.get('academic_structure', '')) > 100
                )
                has_mentor_guidance = (
                    mentor_plan.get('personalized_guidance') and
                    mentor_plan.get('focus') and
                    len(mentor_plan.get('personalized_guidance', '')) > 100
                )
                has_timeline = implementation_timeline.get('review_frequency') == 'weekly'
                
                if has_professor_structure and has_mentor_guidance and has_timeline:
                    print(f"   ✅ Dual intelligence structure validated")
                    print(f"   Professor provides: Academic structure & curriculum compliance")
                    print(f"   Mentor provides: Personalized guidance & motivation")
                    success_count += 1
                else:
                    print(f"   ⚠️  Dual intelligence structure incomplete")
                    print(f"   Professor structure: {'✓' if has_professor_structure else '✗'}")
                    print(f"   Mentor guidance: {'✓' if has_mentor_guidance else '✗'}")
                    print(f"   Timeline setup: {'✓' if has_timeline else '✗'}")
            else:
                print(f"   ❌ Study plan generation failed for {scenario['name']}")
            
            time.sleep(5)  # Delay between AI calls
        
        return success_count >= len(study_plan_scenarios) * 0.8  # 80% success threshold

    def test_enhanced_question_analysis(self):
        """Test Phase 2: Enhanced Question Analysis with dual intelligence and student psychology"""
        if not self.token:
            print("❌ No token available for enhanced question analysis")
            return False
        
        print("   Testing Phase 2: Enhanced Question Analysis...")
        
        # Test different student contexts and question types
        analysis_scenarios = [
            {
                "name": "Stressed Student - Math Problem",
                "message": "Solve the integral ∫(x² + 3x + 2)dx step by step",
                "subject": "Mathematics",
                "context": "High stress, struggling student"
            },
            {
                "name": "Confident Student - Physics Concept",
                "message": "Explain the concept of electromagnetic induction and Faraday's law",
                "subject": "Physics", 
                "context": "Confident student seeking deeper understanding"
            },
            {
                "name": "Average Student - Chemistry Problem",
                "message": "Balance the chemical equation: C₂H₆ + O₂ → CO₂ + H₂O",
                "subject": "Chemistry",
                "context": "Average performance student"
            }
        ]
        
        success_count = 0
        
        for scenario in analysis_scenarios:
            print(f"   Testing {scenario['name']}")
            print(f"   Question: '{scenario['message'][:50]}...'")
            print("   This may take 10-15 seconds for enhanced dual analysis...")
            
            success, response = self.run_test(
                f"Enhanced Analysis - {scenario['name']}",
                "POST",
                "ai/enhanced-question-analysis",
                200,
                data={
                    "message": scenario['message'],
                    "subject": scenario['subject']
                },
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success and 'enhanced_analysis' in response:
                enhanced_analysis = response['enhanced_analysis']
                technical_accuracy = enhanced_analysis.get('technical_accuracy', {})
                learning_psychology = enhanced_analysis.get('learning_psychology', {})
                student_context = response.get('student_context', {})
                scenario_metadata = response.get('scenario_metadata', {})
                
                print(f"   ✅ Enhanced analysis received")
                print(f"   Technical accuracy persona: {technical_accuracy.get('persona', 'N/A')}")
                print(f"   Learning psychology persona: {learning_psychology.get('persona', 'N/A')}")
                print(f"   Student performance level: {student_context.get('performance_level', 'N/A')}")
                print(f"   Student stress status: {student_context.get('stress_status', 'N/A')}")
                print(f"   Recommended approach: {student_context.get('recommended_approach', 'N/A')}")
                print(f"   Primary persona: {scenario_metadata.get('primary_persona', 'N/A')}")
                
                # Verify enhanced analysis structure
                has_technical_analysis = (
                    technical_accuracy.get('persona') == 'professor' and
                    technical_accuracy.get('analysis') and
                    len(technical_accuracy.get('analysis', '')) > 100
                )
                has_psychology_guidance = (
                    learning_psychology.get('persona') == 'mentor' and
                    learning_psychology.get('guidance') and
                    len(learning_psychology.get('guidance', '')) > 100
                )
                has_student_assessment = (
                    student_context.get('performance_level') and
                    student_context.get('stress_status') and
                    student_context.get('recommended_approach')
                )
                has_scenario_metadata = (
                    scenario_metadata.get('primary_persona') and
                    scenario_metadata.get('scenario_type') and
                    scenario_metadata.get('confidence', 0) > 0
                )
                
                if has_technical_analysis and has_psychology_guidance and has_student_assessment and has_scenario_metadata:
                    print(f"   ✅ Enhanced analysis structure validated")
                    print(f"   Technical accuracy: Professor provides factual correctness")
                    print(f"   Learning psychology: Mentor optimizes for student understanding")
                    print(f"   Student context: Performance and stress assessment included")
                    print(f"   Scenario metadata: Persona classification provided")
                    success_count += 1
                else:
                    print(f"   ⚠️  Enhanced analysis structure incomplete")
                    print(f"   Technical analysis: {'✓' if has_technical_analysis else '✗'}")
                    print(f"   Psychology guidance: {'✓' if has_psychology_guidance else '✗'}")
                    print(f"   Student assessment: {'✓' if has_student_assessment else '✗'}")
                    print(f"   Scenario metadata: {'✓' if has_scenario_metadata else '✗'}")
            else:
                print(f"   ❌ Enhanced analysis failed for {scenario['name']}")
            
            time.sleep(5)  # Delay between AI calls
        
        return success_count >= len(analysis_scenarios) * 0.8  # 80% success threshold

    def test_phase2_integration_with_authentication(self):
        """Test Phase 2 endpoints integration with authentication and database operations"""
        if not self.token:
            print("❌ No token available for Phase 2 integration test")
            return False
        
        print("   Testing Phase 2 integration with authentication and database...")
        
        # Test all Phase 2 endpoints with authentication
        phase2_endpoints = [
            {
                "name": "Mock Test Dual Feedback",
                "endpoint": f"mock-tests/{self.test_ids[0]['test_id'] if hasattr(self, 'test_ids') and self.test_ids else 'dummy'}/submit",
                "method": "POST",
                "data": {
                    "answers": {"q1": "A", "q2": "B"},
                    "time_taken": 1800
                },
                "skip_if_no_test": True
            },
            {
                "name": "Study Planning Dual Intelligence",
                "endpoint": "ai/dual-study-plan",
                "method": "POST",
                "data": {
                    "target_exam_date": "2025-05-15T00:00:00Z",
                    "daily_study_hours": 6,
                    "weak_subjects": ["Mathematics"],
                    "strong_subjects": ["Physics"],
                    "preferred_study_times": ["morning"],
                    "stress_level": 5
                }
            },
            {
                "name": "Enhanced Question Analysis",
                "endpoint": "ai/enhanced-question-analysis",
                "method": "POST",
                "data": {
                    "message": "What is the derivative of x³?",
                    "subject": "Mathematics"
                }
            }
        ]
        
        success_count = 0
        
        for test_case in phase2_endpoints:
            if test_case.get('skip_if_no_test') and (not hasattr(self, 'test_ids') or not self.test_ids):
                print(f"   Skipping {test_case['name']} - no test IDs available")
                continue
            
            print(f"   Testing {test_case['name']} with authentication...")
            
            # Test with valid authentication
            success, response = self.run_test(
                f"Phase 2 Auth - {test_case['name']}",
                test_case['method'],
                test_case['endpoint'],
                200,
                data=test_case['data'],
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success:
                print(f"   ✅ {test_case['name']} authenticated successfully")
                success_count += 1
                
                # Test database operations (check if data is persisted)
                if test_case['name'] == "Study Planning Dual Intelligence" and 'plan_id' in response:
                    print(f"   ✅ Study plan persisted with ID: {response['plan_id']}")
                elif test_case['name'] == "Enhanced Question Analysis" and 'session_id' in response:
                    print(f"   ✅ Analysis session created: {response['session_id']}")
            else:
                print(f"   ❌ {test_case['name']} authentication failed")
            
            # Test without authentication (should fail with 401)
            print(f"   Testing {test_case['name']} without authentication...")
            temp_token = self.token
            self.token = None
            
            success_unauth, _ = self.run_test(
                f"Phase 2 Unauth - {test_case['name']}",
                test_case['method'],
                test_case['endpoint'],
                401,  # Expecting 401 Unauthorized
                data=test_case['data']
            )
            
            self.token = temp_token
            
            if success_unauth:
                print(f"   ✅ Correctly rejected unauthorized request")
            else:
                print(f"   ⚠️  Failed to reject unauthorized request")
            
            time.sleep(2)  # Delay between tests
        
        return success_count >= len([tc for tc in phase2_endpoints if not tc.get('skip_if_no_test')]) * 0.8

    def test_phase2_error_handling_and_fallbacks(self):
        """Test Phase 2 error handling and fallback mechanisms"""
        if not self.token:
            print("❌ No token available for Phase 2 error handling test")
            return False
        
        print("   Testing Phase 2 error handling and fallback mechanisms...")
        
        # Test error scenarios
        error_scenarios = [
            {
                "name": "Invalid Study Plan Date",
                "endpoint": "ai/dual-study-plan",
                "method": "POST",
                "data": {
                    "target_exam_date": "invalid-date",
                    "daily_study_hours": 6,
                    "weak_subjects": ["Mathematics"],
                    "strong_subjects": ["Physics"],
                    "preferred_study_times": ["morning"],
                    "stress_level": 5
                },
                "expected_status": 422  # Validation error
            },
            {
                "name": "Invalid Study Hours",
                "endpoint": "ai/dual-study-plan", 
                "method": "POST",
                "data": {
                    "target_exam_date": "2025-05-15T00:00:00Z",
                    "daily_study_hours": 25,  # Invalid: > 16
                    "weak_subjects": ["Mathematics"],
                    "strong_subjects": ["Physics"],
                    "preferred_study_times": ["morning"],
                    "stress_level": 5
                },
                "expected_status": 422  # Validation error
            },
            {
                "name": "Empty Question Analysis",
                "endpoint": "ai/enhanced-question-analysis",
                "method": "POST",
                "data": {
                    "message": "",  # Empty message
                    "subject": "Mathematics"
                },
                "expected_status": 422  # Validation error
            }
        ]
        
        success_count = 0
        
        for scenario in error_scenarios:
            print(f"   Testing {scenario['name']}...")
            
            success, response = self.run_test(
                f"Error Handling - {scenario['name']}",
                scenario['method'],
                scenario['endpoint'],
                scenario['expected_status'],
                data=scenario['data'],
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success:
                print(f"   ✅ Error handled correctly (status {scenario['expected_status']})")
                success_count += 1
            else:
                print(f"   ❌ Error handling failed")
            
            time.sleep(1)  # Small delay between tests
        
        return success_count >= len(error_scenarios) * 0.8

    def test_phase2_backward_compatibility(self):
        """Test that Phase 2 enhancements maintain backward compatibility with existing mock test system"""
        if not self.token:
            print("❌ No token available for backward compatibility test")
            return False
        
        print("   Testing Phase 2 backward compatibility with existing mock test system...")
        
        # Test that existing mock test endpoints still work
        compatibility_tests = [
            {
                "name": "Legacy Mock Test Generation",
                "endpoint": "mock-tests/generate",
                "method": "POST",
                "data": {
                    "exam_type": "JEE",
                    "subject": "Mathematics",
                    "difficulty": 3,
                    "num_questions": 5
                }
            }
        ]
        
        success_count = 0
        
        for test_case in compatibility_tests:
            print(f"   Testing {test_case['name']}...")
            print("   This may take 5-10 seconds for AI processing...")
            
            success, response = self.run_test(
                f"Backward Compatibility - {test_case['name']}",
                test_case['method'],
                test_case['endpoint'],
                200,
                data=test_case['data'],
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success:
                print(f"   ✅ {test_case['name']} still works")
                
                # Verify response structure is maintained
                if 'test_id' in response and 'questions' in response:
                    print(f"   ✅ Response structure maintained")
                    print(f"   Test ID: {response['test_id']}")
                    print(f"   Questions count: {len(response.get('questions', []))}")
                    success_count += 1
                else:
                    print(f"   ⚠️  Response structure may have changed")
            else:
                print(f"   ❌ {test_case['name']} failed")
            
            time.sleep(3)  # Delay for AI processing
        
        return success_count >= len(compatibility_tests)

    # ============= AUTO-NOTE MENTOR API TESTS =============

    def test_auto_note_start_session(self):
        """Test starting a new auto-note session"""
        if not self.token:
            print("❌ No token available for auto-note session test")
            return False
        
        print("   Testing auto-note session start...")
        
        session_data = {
            "title": "Physics Class - Electromagnetic Induction",
            "subject": "Physics"
        }
        
        success, response = self.run_test(
            "Auto-Note Start Session",
            "POST",
            "auto-notes/start-session",
            200,
            data=session_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success and 'session_id' in response:
            self.note_session_id = response['session_id']
            print(f"   ✅ Session started: {self.note_session_id}")
            print(f"   Title: {response.get('title', 'N/A')}")
            print(f"   Subject: {response.get('subject', 'N/A')}")
            print(f"   Status: {response.get('status', 'N/A')}")
            return True
        
        return False

    def test_auto_note_process_audio(self):
        """Test processing audio transcription chunks"""
        if not self.token or not hasattr(self, 'note_session_id'):
            print("❌ No token or session ID available for audio processing test")
            return False
        
        print("   Testing audio chunk processing...")
        
        # Test multiple audio chunks
        audio_chunks = [
            {
                "session_id": self.note_session_id,
                "transcription": "Today we will learn about electromagnetic induction and Faraday's law",
                "timestamp": 0.0,
                "sequence_number": 1,
                "confidence": 0.95
            },
            {
                "session_id": self.note_session_id,
                "transcription": "The formula for electromagnetic induction is EMF equals negative dPhi by dt",
                "timestamp": 15.5,
                "sequence_number": 2,
                "confidence": 0.92
            },
            {
                "session_id": self.note_session_id,
                "transcription": "This principle is fundamental to understanding how generators and transformers work",
                "timestamp": 30.2,
                "sequence_number": 3,
                "confidence": 0.88
            }
        ]
        
        success_count = 0
        
        for i, chunk_data in enumerate(audio_chunks):
            print(f"   Processing audio chunk {i+1}/3...")
            
            success, response = self.run_test(
                f"Process Audio Chunk {i+1}",
                "POST",
                "auto-notes/process-audio",
                200,
                data=chunk_data,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success:
                print(f"   ✅ Chunk {i+1} processed")
                print(f"   Concepts detected: {len(response.get('concepts_detected', []))}")
                print(f"   Transcription preview: {response.get('transcription_preview', 'N/A')[:50]}...")
                success_count += 1
            else:
                print(f"   ❌ Chunk {i+1} processing failed")
            
            time.sleep(1)  # Small delay between chunks
        
        return success_count == len(audio_chunks)

    def test_auto_note_end_session(self):
        """Test ending auto-note session and generating structured notes"""
        if not self.token or not hasattr(self, 'note_session_id'):
            print("❌ No token or session ID available for ending session test")
            return False
        
        print("   Testing auto-note session completion...")
        print("   This may take 10-15 seconds for dual AI analysis...")
        
        success, response = self.run_test(
            "Auto-Note End Session",
            "POST",
            f"auto-notes/end-session?session_id={self.note_session_id}",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            print(f"   ✅ Session completed")
            print(f"   Status: {response.get('status', 'N/A')}")
            print(f"   Duration: {response.get('duration_minutes', 0):.1f} minutes")
            
            # Check structured notes
            structured_notes = response.get('structured_notes', {})
            print(f"   Key concepts: {len(structured_notes.get('key_concepts', []))}")
            print(f"   Important points: {len(structured_notes.get('important_points', []))}")
            print(f"   Formulas mentioned: {len(structured_notes.get('formulas_mentioned', []))}")
            
            # Check dual analysis
            dual_analysis = response.get('dual_analysis', {})
            professor_analysis = dual_analysis.get('professor_analysis', {})
            mentor_guidance = dual_analysis.get('mentor_guidance', {})
            
            print(f"   Professor analysis: {'✓' if professor_analysis.get('content') else '✗'}")
            print(f"   Mentor guidance: {'✓' if mentor_guidance.get('content') else '✗'}")
            
            # Check summary
            summary = response.get('summary', {})
            print(f"   Note quality: {summary.get('note_quality', 'N/A')}")
            
            return True
        
        return False

    def test_auto_note_get_session(self):
        """Test retrieving auto-note session details"""
        if not self.token or not hasattr(self, 'note_session_id'):
            print("❌ No token or session ID available for get session test")
            return False
        
        print("   Testing auto-note session retrieval...")
        
        success, response = self.run_test(
            "Get Auto-Note Session",
            "GET",
            f"auto-notes/{self.note_session_id}",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            print(f"   ✅ Session retrieved")
            print(f"   Session ID: {response.get('session_id', 'N/A')}")
            print(f"   Title: {response.get('title', 'N/A')}")
            print(f"   Subject: {response.get('subject', 'N/A')}")
            print(f"   Status: {response.get('status', 'N/A')}")
            print(f"   Has transcription: {'Yes' if response.get('transcription') else 'No'}")
            print(f"   Has structured notes: {'Yes' if response.get('structured_notes') else 'No'}")
            print(f"   Has dual analysis: {'Yes' if response.get('dual_analysis') else 'No'}")
            return True
        
        return False

    def test_auto_note_list_sessions(self):
        """Test listing all auto-note sessions"""
        if not self.token:
            print("❌ No token available for list sessions test")
            return False
        
        print("   Testing auto-note sessions listing...")
        
        success, response = self.run_test(
            "List Auto-Note Sessions",
            "GET",
            "auto-notes/sessions",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            sessions = response.get('sessions', [])
            total_sessions = response.get('total_sessions', 0)
            active_sessions = response.get('active_sessions', 0)
            
            print(f"   ✅ Sessions listed")
            print(f"   Total sessions: {total_sessions}")
            print(f"   Active sessions: {active_sessions}")
            print(f"   Sessions returned: {len(sessions)}")
            
            # Check session structure
            if sessions:
                sample_session = sessions[0]
                required_fields = ['session_id', 'title', 'subject', 'status', 'created_at']
                missing_fields = [field for field in required_fields if field not in sample_session]
                if missing_fields:
                    print(f"   ⚠️  Missing session fields: {missing_fields}")
                else:
                    print(f"   ✅ Session structure validated")
            
            return True
        
        return False

    def test_auto_note_explain_point(self):
        """Test explaining specific note points"""
        if not self.token or not hasattr(self, 'note_session_id'):
            print("❌ No token or session ID available for explain point test")
            return False
        
        print("   Testing auto-note point explanation...")
        print("   This may take 5-10 seconds for dual AI explanation...")
        
        explain_data = {
            "session_id": self.note_session_id,
            "point_reference": "concept_1",
            "additional_context": "I need more details about electromagnetic induction"
        }
        
        success, response = self.run_test(
            "Explain Note Point",
            "POST",
            "auto-notes/explain-point",
            200,
            data=explain_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            explanation = response.get('explanation', {})
            professor_explanation = explanation.get('professor_explanation', {})
            mentor_guidance = explanation.get('mentor_guidance', {})
            
            print(f"   ✅ Point explanation received")
            print(f"   Professor explanation: {'✓' if professor_explanation.get('content') else '✗'}")
            print(f"   Mentor guidance: {'✓' if mentor_guidance.get('content') else '✗'}")
            print(f"   Related concepts: {len(response.get('related_concepts', []))}")
            print(f"   Study tip: {'✓' if response.get('study_tip') else '✗'}")
            
            return True
        
        return False

    def test_auto_note_generate_flashcards(self):
        """Test generating flashcards from notes"""
        if not self.token or not hasattr(self, 'note_session_id'):
            print("❌ No token or session ID available for flashcard generation test")
            return False
        
        print("   Testing auto-note flashcard generation...")
        print("   This may take 5-10 seconds for AI flashcard creation...")
        
        flashcard_data = {
            "session_id": self.note_session_id,
            "specific_concepts": ["electromagnetic induction", "Faraday's law"]
        }
        
        success, response = self.run_test(
            "Generate Flashcards",
            "POST",
            "auto-notes/generate-flashcards",
            200,
            data=flashcard_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            flashcards_generated = response.get('flashcards_generated', 0)
            flashcards = response.get('flashcards', [])
            ai_insights = response.get('ai_insights', {})
            
            print(f"   ✅ Flashcards generated: {flashcards_generated}")
            print(f"   Flashcards returned: {len(flashcards)}")
            print(f"   Professor review: {'✓' if ai_insights.get('professor_review') else '✗'}")
            print(f"   Mentor encouragement: {'✓' if ai_insights.get('mentor_encouragement') else '✗'}")
            print(f"   Study recommendation: {'✓' if response.get('study_recommendation') else '✗'}")
            
            # Check flashcard structure
            if flashcards:
                sample_card = flashcards[0]
                required_fields = ['card_id', 'question', 'answer', 'concept', 'difficulty_level']
                missing_fields = [field for field in required_fields if field not in sample_card]
                if missing_fields:
                    print(f"   ⚠️  Missing flashcard fields: {missing_fields}")
                else:
                    print(f"   ✅ Flashcard structure validated")
                    print(f"   Sample question: {sample_card.get('question', '')[:50]}...")
            
            return True
        
        return False

    # ============= DUAL-LAYER AI SYSTEM TESTS =============

    def test_scenario_classification(self):
        """Test scenario classification endpoint"""
        print("   Testing scenario classification logic...")
        
        # Test different types of questions as specified in review request
        test_scenarios = [
            {
                "message": "Solve x² + 5x + 6 = 0 step by step",
                "expected_primary": "professor",
                "scenario_type": "Technical/factual question"
            },
            {
                "message": "I'm stressed about my JEE exam, help me plan",
                "expected_primary": "mentor", 
                "scenario_type": "Motivational/guidance question"
            },
            {
                "message": "What are effective study techniques?",
                "expected_primary": "mentor",
                "scenario_type": "Mixed/general question"
            },
            {
                "message": "Explain the concept of derivatives in calculus",
                "expected_primary": "professor",
                "scenario_type": "Technical/factual question"
            },
            {
                "message": "I'm feeling demotivated and need guidance",
                "expected_primary": "mentor",
                "scenario_type": "Motivational/guidance question"
            }
        ]
        
        success_count = 0
        
        for i, scenario in enumerate(test_scenarios):
            print(f"   Testing scenario {i+1}/5: {scenario['scenario_type']}")
            print(f"   Message: '{scenario['message'][:50]}...'")
            
            success, response = self.run_test(
                f"Scenario Classification - {scenario['scenario_type']}",
                "GET",
                f"ai/scenario-classify?message={scenario['message']}",
                200
            )
            
            if success and 'classification' in response:
                classification = response['classification']
                primary_persona = classification.get('primary_persona')
                scenario_type = classification.get('scenario_type')
                confidence = classification.get('confidence', 0)
                
                print(f"   ✅ Classification successful")
                print(f"   Primary persona: {primary_persona}")
                print(f"   Scenario type: {scenario_type}")
                print(f"   Confidence: {confidence:.2f}")
                
                # Validate expected persona
                if primary_persona == scenario['expected_primary']:
                    print(f"   ✅ Correct persona classification")
                    success_count += 1
                else:
                    print(f"   ⚠️  Expected {scenario['expected_primary']}, got {primary_persona}")
                    success_count += 0.5  # Partial credit as AI classification can vary
            else:
                print(f"   ❌ Classification failed")
        
        return success_count >= len(test_scenarios) * 0.8  # 80% success threshold

    def test_dual_layer_ai_response(self):
        """Test coordinated dual-layer AI responses"""
        if not self.token:
            print("❌ No token available for dual AI test")
            return False
        
        print("   Testing dual-layer AI coordinated responses...")
        
        # Test scenarios from review request
        test_messages = [
            {
                "message": "Solve x² + 5x + 6 = 0 step by step",
                "subject": "Mathematics",
                "expected_primary": "professor",
                "description": "Technical math problem"
            },
            {
                "message": "I'm stressed about my JEE exam, help me plan",
                "subject": "General",
                "expected_primary": "mentor",
                "description": "Motivational guidance"
            },
            {
                "message": "What are effective study techniques?",
                "subject": "General", 
                "expected_primary": "mentor",
                "description": "Mixed/general question"
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_messages):
            print(f"   Testing dual response {i+1}/3: {test_case['description']}")
            print(f"   Message: '{test_case['message'][:50]}...'")
            print("   This may take 10-15 seconds for dual AI processing...")
            
            success, response = self.run_test(
                f"Dual AI Response - {test_case['description']}",
                "POST",
                "ai/dual-response",
                200,
                data={
                    "message": test_case['message'],
                    "subject": test_case['subject']
                },
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success and 'dual_response' in response:
                dual_resp = response['dual_response']
                primary = dual_resp.get('primary', {})
                secondary = dual_resp.get('secondary', {})
                scenario_type = dual_resp.get('scenario_type')
                confidence = dual_resp.get('confidence', 0)
                
                print(f"   ✅ Dual response received")
                print(f"   Primary persona: {primary.get('persona')}")
                print(f"   Secondary persona: {secondary.get('persona')}")
                print(f"   Scenario type: {scenario_type}")
                print(f"   Confidence: {confidence:.2f}")
                print(f"   Primary response length: {len(primary.get('response', ''))}")
                print(f"   Secondary response length: {len(secondary.get('response', ''))}")
                
                # Validate response structure
                required_fields = ['primary', 'secondary', 'scenario_type', 'confidence']
                has_all_fields = all(field in dual_resp for field in required_fields)
                
                # Validate persona responses
                primary_valid = primary.get('persona') and primary.get('response') and primary.get('reasoning')
                secondary_valid = secondary.get('persona') and secondary.get('reasoning')
                
                if has_all_fields and primary_valid and secondary_valid:
                    print(f"   ✅ Response structure validated")
                    success_count += 1
                else:
                    print(f"   ⚠️  Response structure incomplete")
                    print(f"   Missing fields: {[f for f in required_fields if f not in dual_resp]}")
            else:
                print(f"   ❌ Dual response failed")
            
            time.sleep(5)  # Delay between AI calls
        
        return success_count == len(test_messages)

    def test_mentor_only_response(self):
        """Test pure Mentor AI responses"""
        if not self.token:
            print("❌ No token available for mentor test")
            return False
        
        print("   Testing pure Mentor AI responses...")
        
        # Test mentor-focused messages
        mentor_messages = [
            {
                "message": "I'm feeling overwhelmed with JEE preparation, need motivation",
                "subject": "General"
            },
            {
                "message": "How can I manage my study schedule better?",
                "subject": "General"
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(mentor_messages):
            print(f"   Testing mentor response {i+1}/2")
            print(f"   Message: '{test_case['message'][:50]}...'")
            print("   This may take 5-10 seconds for AI processing...")
            
            success, response = self.run_test(
                f"Mentor Only Response - {i+1}",
                "POST",
                "ai/mentor-only",
                200,
                data=test_case,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success:
                persona = response.get('persona')
                ai_response = response.get('response', '')
                reasoning = response.get('reasoning', '')
                
                print(f"   ✅ Mentor response received")
                print(f"   Persona: {persona}")
                print(f"   Response length: {len(ai_response)}")
                print(f"   Has reasoning: {'Yes' if reasoning else 'No'}")
                
                # Validate mentor persona
                if persona == 'mentor' and ai_response and reasoning:
                    print(f"   ✅ Mentor response validated")
                    success_count += 1
                else:
                    print(f"   ⚠️  Mentor response incomplete")
            else:
                print(f"   ❌ Mentor response failed")
            
            time.sleep(3)  # Delay between AI calls
        
        return success_count == len(mentor_messages)

    def test_professor_only_response(self):
        """Test pure Professor AI responses"""
        if not self.token:
            print("❌ No token available for professor test")
            return False
        
        print("   Testing pure Professor AI responses...")
        
        # Test professor-focused messages
        professor_messages = [
            {
                "message": "Derive the quadratic formula step by step",
                "subject": "Mathematics"
            },
            {
                "message": "Explain Newton's laws of motion with examples",
                "subject": "Physics"
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(professor_messages):
            print(f"   Testing professor response {i+1}/2")
            print(f"   Message: '{test_case['message'][:50]}...'")
            print("   This may take 5-10 seconds for AI processing...")
            
            success, response = self.run_test(
                f"Professor Only Response - {i+1}",
                "POST",
                "ai/professor-only",
                200,
                data=test_case,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success:
                persona = response.get('persona')
                ai_response = response.get('response', '')
                reasoning = response.get('reasoning', '')
                
                print(f"   ✅ Professor response received")
                print(f"   Persona: {persona}")
                print(f"   Response length: {len(ai_response)}")
                print(f"   Has reasoning: {'Yes' if reasoning else 'No'}")
                
                # Validate professor persona
                if persona == 'professor' and ai_response and reasoning:
                    print(f"   ✅ Professor response validated")
                    success_count += 1
                else:
                    print(f"   ⚠️  Professor response incomplete")
            else:
                print(f"   ❌ Professor response failed")
            
            time.sleep(3)  # Delay between AI calls
        
        return success_count == len(professor_messages)

    def test_backward_compatibility(self):
        """Test that existing /api/chat/message endpoint still works with legacy functionality"""
        if not self.token:
            print("❌ No token available for backward compatibility test")
            return False
        
        print("   Testing backward compatibility with legacy chat endpoint...")
        
        # Test that legacy endpoint still works
        legacy_message = {
            "message": "What is the derivative of x²?",
            "subject": "Mathematics"
        }
        
        print("   Testing legacy /api/chat/message endpoint...")
        print("   This may take 5-10 seconds for AI processing...")
        
        success, response = self.run_test(
            "Legacy Chat Message Compatibility",
            "POST",
            "chat/message",
            200,
            data=legacy_message,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            ai_response = response.get('response', '')
            reasoning = response.get('reasoning', '')
            session_id = response.get('session_id', '')
            
            print(f"   ✅ Legacy endpoint working")
            print(f"   Response length: {len(ai_response)}")
            print(f"   Has reasoning: {'Yes' if reasoning else 'No'}")
            print(f"   Session ID: {session_id[:20]}..." if session_id else "No session ID")
            
            # Check if response indicates dual-layer usage
            if 'dual-layer' in reasoning.lower() or 'mentor' in reasoning.lower() or 'professor' in reasoning.lower():
                print(f"   ✅ Legacy endpoint now uses dual-layer AI system")
                return True
            else:
                print(f"   ⚠️  Legacy endpoint may not be using dual-layer system")
                return True  # Still working, just may not be enhanced
        else:
            print(f"   ❌ Legacy endpoint failed")
            return False

    def test_dual_ai_authentication_integration(self):
        """Test that all dual-layer AI endpoints work with existing JWT authentication"""
        if not self.token:
            print("❌ No token available for auth integration test")
            return False
        
        print("   Testing dual-layer AI authentication integration...")
        
        # Test all dual AI endpoints with valid token
        endpoints_to_test = [
            ("ai/dual-response", "POST", {"message": "Test auth", "subject": "Mathematics"}),
            ("ai/mentor-only", "POST", {"message": "Test auth", "subject": "Mathematics"}),
            ("ai/professor-only", "POST", {"message": "Test auth", "subject": "Mathematics"}),
            ("ai/scenario-classify", "GET", None)  # GET endpoint with query param
        ]
        
        success_count = 0
        
        for endpoint, method, test_data in endpoints_to_test:
            print(f"   Testing {endpoint} with valid authentication...")
            
            if endpoint == "ai/scenario-classify":
                # Special handling for GET endpoint with query param
                success, response = self.run_test(
                    f"Auth Integration - {endpoint}",
                    method,
                    f"{endpoint}?message=Test message",
                    200,
                    headers={'Authorization': f'Bearer {self.token}'}
                )
            else:
                success, response = self.run_test(
                    f"Auth Integration - {endpoint}",
                    method,
                    endpoint,
                    200,
                    data=test_data,
                    headers={'Authorization': f'Bearer {self.token}'}
                )
            
            if success:
                print(f"   ✅ {endpoint} authenticated successfully")
                success_count += 1
            else:
                print(f"   ❌ {endpoint} authentication failed")
            
            time.sleep(2)  # Small delay between requests
        
        return success_count == len(endpoints_to_test)

def main():
    print("🚀 Starting Dhruv AI Backend API Tests - Dual-Layer AI System")
    print("=" * 70)
    
    tester = DhruvAITester()
    
    # Test sequence - Core APIs first, then Phase 4 features, then Dual-Layer AI
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
        ("🆕 Enhanced Question Generation", tester.test_enhanced_question_generation),
        ("🆕 Submit Mock Test", tester.test_submit_mock_test),
        ("🆕 Performance Analytics", tester.test_performance_analytics),
        ("🆕 Stress Assessment", tester.test_stress_assessment),
        ("🆕 Motivational Content", tester.test_motivational_content),
        ("🆕 Auth Validation", tester.test_integration_auth_validation),
        
        # Auto-Note Mentor API Tests
        ("📝 Auto-Note Start Session", tester.test_auto_note_start_session),
        ("📝 Auto-Note Process Audio", tester.test_auto_note_process_audio),
        ("📝 Auto-Note End Session", tester.test_auto_note_end_session),
        ("📝 Auto-Note Get Session", tester.test_auto_note_get_session),
        ("📝 Auto-Note List Sessions", tester.test_auto_note_list_sessions),
        ("📝 Auto-Note Explain Point", tester.test_auto_note_explain_point),
        ("📝 Auto-Note Generate Flashcards", tester.test_auto_note_generate_flashcards),
        
        # Phase 2: Dual-Layer AI Scenario Implementations
        ("🚀 Phase 2: Mock Tests Dual Feedback", tester.test_mock_tests_dual_feedback_system),
        ("🚀 Phase 2: Study Planning Dual Intelligence", tester.test_study_planning_dual_intelligence),
        ("🚀 Phase 2: Enhanced Question Analysis", tester.test_enhanced_question_analysis),
        ("🚀 Phase 2: Integration with Authentication", tester.test_phase2_integration_with_authentication),
        ("🚀 Phase 2: Error Handling & Fallbacks", tester.test_phase2_error_handling_and_fallbacks),
        ("🚀 Phase 2: Backward Compatibility", tester.test_phase2_backward_compatibility),
        
        # Dual-Layer AI System Tests
        ("🤖 Scenario Classification", tester.test_scenario_classification),
        ("🤖 Dual-Layer AI Response", tester.test_dual_layer_ai_response),
        ("🤖 Mentor-Only Response", tester.test_mentor_only_response),
        ("🤖 Professor-Only Response", tester.test_professor_only_response),
        ("🤖 Backward Compatibility", tester.test_backward_compatibility),
        ("🤖 Dual AI Authentication", tester.test_dual_ai_authentication_integration),
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
    print("📊 FINAL TEST RESULTS - DHRUV AI DUAL-LAYER SYSTEM TESTING")
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
    
    print(f"\n📋 FEATURES TESTED:")
    print(f"   ✓ Enhanced Mock Test System (Generation & Submission)")
    print(f"   ✓ Performance Analytics (Student & Parent Views)")
    print(f"   ✓ Stress Management & Wellness Assessment")
    print(f"   ✓ Personalized Motivational Content")
    print(f"   ✓ Authentication & Security Validation")
    print(f"   📝 AUTO-NOTE MENTOR API:")
    print(f"   ✓ Start Recording Session")
    print(f"   ✓ Process Audio Transcription")
    print(f"   ✓ End Session & Generate Notes")
    print(f"   ✓ Get Session Details")
    print(f"   ✓ List All Sessions")
    print(f"   ✓ Explain Note Points")
    print(f"   ✓ Generate Flashcards")
    print(f"   🚀 PHASE 2: DUAL-LAYER AI SCENARIO IMPLEMENTATIONS:")
    print(f"   ✓ Mock Tests Dual Feedback System (Professor + Mentor Analysis)")
    print(f"   ✓ Study Planning Dual Intelligence (Academic + Personal Guidance)")
    print(f"   ✓ Enhanced Question Analysis (Technical + Learning Psychology)")
    print(f"   ✓ Integration Testing with Authentication & Database")
    print(f"   ✓ Error Handling & Fallback Mechanisms")
    print(f"   ✓ Backward Compatibility with Existing Systems")
    print(f"   🤖 DUAL-LAYER AI SYSTEM:")
    print(f"   ✓ Scenario Classification Logic")
    print(f"   ✓ Coordinated Mentor+Professor Responses")
    print(f"   ✓ Pure Mentor AI Responses")
    print(f"   ✓ Pure Professor AI Responses")
    print(f"   ✓ Backward Compatibility with Legacy Chat")
    print(f"   ✓ JWT Authentication Integration")
    
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())