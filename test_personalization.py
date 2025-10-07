#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class PersonalizationTester:
    def __init__(self, base_url="https://study-streak-app.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
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

    def test_personalization_profile_get(self):
        """Test GET /api/personalization/profile for student profile retrieval"""
        if not self.token:
            print("❌ No token available for personalization profile test")
            return False
        
        print("   Testing personalization profile retrieval...")
        
        success, response = self.run_test(
            "Get Personalization Profile",
            "GET",
            "personalization/profile",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            print(f"   ✅ Profile retrieved successfully")
            
            # Validate profile structure
            required_fields = ['profile_id', 'user_id', 'preferred_language', 'learning_style', 
                             'difficulty_preference', 'response_length_preference']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"   ⚠️  Missing profile fields: {missing_fields}")
            else:
                print(f"   ✅ Profile structure validated")
                print(f"   Language: {response.get('preferred_language', 'N/A')}")
                print(f"   Learning Style: {response.get('learning_style', 'N/A')}")
                print(f"   Difficulty: {response.get('difficulty_preference', 0):.1f}")
                print(f"   Response Length: {response.get('response_length_preference', 'N/A')}")
                print(f"   Weak Areas: {len(response.get('weak_areas', []))}")
                print(f"   Strong Areas: {len(response.get('strong_areas', []))}")
                print(f"   Total Interactions: {response.get('total_interactions', 0)}")
            
            return True
        
        return False

    def test_personalization_profile_post(self):
        """Test POST /api/personalization/profile for student profile management"""
        if not self.token:
            print("❌ No token available for personalization profile update test")
            return False
        
        print("   Testing personalization profile update...")
        
        # Test different language preferences and settings
        profile_scenarios = [
            {
                "name": "English Analytical Student",
                "preferred_language": "english",
                "learning_style": "analytical",
                "difficulty_preference": 0.7,
                "response_length_preference": "detailed"
            },
            {
                "name": "Hindi Visual Student",
                "preferred_language": "hindi",
                "learning_style": "visual",
                "difficulty_preference": 0.4,
                "response_length_preference": "medium"
            },
            {
                "name": "Hinglish Practical Student",
                "preferred_language": "hinglish",
                "learning_style": "practical",
                "difficulty_preference": 0.6,
                "response_length_preference": "short"
            }
        ]
        
        success_count = 0
        
        for scenario in profile_scenarios:
            print(f"   Testing {scenario['name']} profile update...")
            
            success, response = self.run_test(
                f"Update Profile - {scenario['name']}",
                "POST",
                "personalization/profile",
                200,
                data={
                    "preferred_language": scenario["preferred_language"],
                    "learning_style": scenario["learning_style"],
                    "difficulty_preference": scenario["difficulty_preference"],
                    "response_length_preference": scenario["response_length_preference"]
                },
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success:
                print(f"   ✅ {scenario['name']} profile updated successfully")
                print(f"   Updated Language: {response.get('preferred_language', 'N/A')}")
                print(f"   Updated Style: {response.get('learning_style', 'N/A')}")
                print(f"   Updated Difficulty: {response.get('difficulty_preference', 0):.1f}")
                success_count += 1
            else:
                print(f"   ❌ {scenario['name']} profile update failed")
            
            time.sleep(1)  # Small delay between updates
        
        return success_count >= len(profile_scenarios) * 0.8

    def test_personalization_mastery_tracking(self):
        """Test /api/personalization/mastery for topic mastery tracking"""
        if not self.token:
            print("❌ No token available for mastery tracking test")
            return False
        
        print("   Testing topic mastery tracking...")
        
        # Test mastery tracking for different subjects and topics
        mastery_scenarios = [
            {
                "subject": "Mathematics",
                "topic_name": "Quadratic Equations",
                "chapter": "Algebra",
                "performance": "high"  # 80% correct
            },
            {
                "subject": "Physics", 
                "topic_name": "Newton's Laws",
                "chapter": "Mechanics",
                "performance": "medium"  # 60% correct
            },
            {
                "subject": "Chemistry",
                "topic_name": "Periodic Table",
                "chapter": "Atomic Structure", 
                "performance": "low"  # 40% correct
            }
        ]
        
        success_count = 0
        
        for scenario in mastery_scenarios:
            print(f"   Testing mastery tracking for {scenario['subject']} - {scenario['topic_name']}...")
            
            success, response = self.run_test(
                f"Mastery Tracking - {scenario['subject']} {scenario['topic_name']}",
                "GET",
                f"personalization/mastery?subject={scenario['subject']}&topic_name={scenario['topic_name']}",
                200,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success:
                print(f"   ✅ Mastery data retrieved for {scenario['topic_name']}")
                
                # Check mastery data structure
                if isinstance(response, list) and len(response) > 0:
                    mastery_data = response[0]
                    print(f"   Mastery Level: {mastery_data.get('mastery_level', 0):.2f}")
                    print(f"   Total Attempts: {mastery_data.get('total_attempts', 0)}")
                    print(f"   Correct Attempts: {mastery_data.get('correct_attempts', 0)}")
                    print(f"   Difficulty Level: {mastery_data.get('difficulty_level', 0):.2f}")
                    success_count += 1
                elif isinstance(response, dict):
                    print(f"   Mastery Level: {response.get('mastery_level', 0):.2f}")
                    print(f"   Total Attempts: {response.get('total_attempts', 0)}")
                    success_count += 1
                else:
                    print(f"   ⚠️  No mastery data found (new topic)")
                    success_count += 1  # This is acceptable for new topics
            else:
                print(f"   ❌ Mastery tracking failed for {scenario['topic_name']}")
            
            time.sleep(1)
        
        return success_count >= len(mastery_scenarios) * 0.8

    def test_personalization_error_patterns(self):
        """Test /api/personalization/error-patterns for error pattern analysis"""
        if not self.token:
            print("❌ No token available for error patterns test")
            return False
        
        print("   Testing error pattern analysis...")
        
        # Test error pattern retrieval for different subjects
        subjects_to_test = ["Mathematics", "Physics", "Chemistry"]
        success_count = 0
        
        for subject in subjects_to_test:
            print(f"   Testing error patterns for {subject}...")
            
            success, response = self.run_test(
                f"Error Patterns - {subject}",
                "GET",
                f"personalization/error-patterns?subject={subject}",
                200,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success:
                print(f"   ✅ Error patterns retrieved for {subject}")
                
                if isinstance(response, list):
                    print(f"   Found {len(response)} error patterns")
                    
                    # Show sample error patterns if any exist
                    for i, pattern in enumerate(response[:2]):  # Show first 2
                        print(f"     Pattern {i+1}: {pattern.get('error_type', 'N/A')} - {pattern.get('topic_name', 'N/A')}")
                        print(f"     Frequency: {pattern.get('frequency', 0)}, Resolved: {pattern.get('resolved', False)}")
                else:
                    print(f"   No error patterns found for {subject} (acceptable for new users)")
                
                success_count += 1
            else:
                print(f"   ❌ Error patterns retrieval failed for {subject}")
            
            time.sleep(1)
        
        return success_count >= len(subjects_to_test) * 0.8

    def test_personalization_feedback_recording(self):
        """Test /api/personalization/feedback for user feedback recording"""
        if not self.token:
            print("❌ No token available for feedback recording test")
            return False
        
        print("   Testing user feedback recording...")
        
        # Test different feedback scenarios
        feedback_scenarios = [
            {
                "name": "Helpful Feedback",
                "session_id": f"test_session_{int(time.time())}",
                "subject": "Mathematics",
                "feedback_type": "helpful",
                "topic_name": "Quadratic Equations"
            },
            {
                "name": "Too Easy Feedback",
                "session_id": f"test_session_{int(time.time()) + 1}",
                "subject": "Physics",
                "feedback_type": "too_easy",
                "topic_name": "Newton's Laws"
            },
            {
                "name": "Too Hard Feedback",
                "session_id": f"test_session_{int(time.time()) + 2}",
                "subject": "Chemistry",
                "feedback_type": "too_hard",
                "topic_name": "Chemical Bonding"
            },
            {
                "name": "Confusing Feedback",
                "session_id": f"test_session_{int(time.time()) + 3}",
                "subject": "Mathematics",
                "feedback_type": "confusing",
                "topic_name": "Integration"
            },
            {
                "name": "Perfect Feedback",
                "session_id": f"test_session_{int(time.time()) + 4}",
                "subject": "Physics",
                "feedback_type": "perfect",
                "topic_name": "Electromagnetic Induction"
            }
        ]
        
        success_count = 0
        
        for scenario in feedback_scenarios:
            print(f"   Testing {scenario['name']}...")
            
            success, response = self.run_test(
                f"Feedback Recording - {scenario['name']}",
                "POST",
                "personalization/feedback",
                200,
                data={
                    "session_id": scenario["session_id"],
                    "subject": scenario["subject"],
                    "feedback_type": scenario["feedback_type"],
                    "topic_name": scenario["topic_name"]
                },
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success:
                print(f"   ✅ {scenario['name']} recorded successfully")
                print(f"   Feedback ID: {response.get('feedback_id', 'N/A')}")
                print(f"   Mastery Updated: {response.get('mastery_updated', False)}")
                print(f"   Difficulty Adjusted: {response.get('difficulty_adjusted', False)}")
                success_count += 1
            else:
                print(f"   ❌ {scenario['name']} recording failed")
            
            time.sleep(1)
        
        return success_count >= len(feedback_scenarios) * 0.8

    def test_personalized_dual_ai_responses(self):
        """Test personalized dual AI responses with language preferences"""
        if not self.token:
            print("❌ No token available for personalized AI responses test")
            return False
        
        print("   Testing personalized dual AI responses...")
        
        # First, set different language preferences and test responses
        language_scenarios = [
            {
                "name": "English Response",
                "language": "english",
                "question": "Explain quadratic equations and their applications in JEE",
                "subject": "Mathematics"
            },
            {
                "name": "Hindi Response", 
                "language": "hindi",
                "question": "समझाएं कि न्यूटन के गति के नियम क्या हैं",
                "subject": "Physics"
            },
            {
                "name": "Hinglish Response",
                "language": "hinglish", 
                "question": "Chemical bonding ke types explain karo with examples",
                "subject": "Chemistry"
            }
        ]
        
        success_count = 0
        
        for scenario in language_scenarios:
            print(f"   Testing {scenario['name']} with personalization...")
            
            # First update profile for this language
            profile_update_success, _ = self.run_test(
                f"Update Profile for {scenario['language']}",
                "POST",
                "personalization/profile",
                200,
                data={
                    "preferred_language": scenario["language"],
                    "learning_style": "balanced",
                    "difficulty_preference": 0.5,
                    "response_length_preference": "medium"
                },
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if not profile_update_success:
                print(f"   ⚠️  Profile update failed for {scenario['language']}")
                continue
            
            # Now test personalized dual AI response
            print(f"   Sending personalized question in {scenario['language']}...")
            print("   This may take 10-15 seconds for personalized dual AI analysis...")
            
            success, response = self.run_test(
                f"Personalized Dual AI - {scenario['name']}",
                "POST",
                "ai/dual-response",
                200,
                data={
                    "message": scenario["question"],
                    "subject": scenario["subject"],
                    "session_id": f"test_session_{int(time.time())}"
                },
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success and 'dual_response' in response:
                dual_resp = response['dual_response']
                print(f"   ✅ Personalized {scenario['name']} received")
                print(f"   Primary Persona: {dual_resp.get('primary_persona', 'N/A')}")
                print(f"   Secondary Persona: {dual_resp.get('secondary_persona', 'N/A')}")
                print(f"   Language Adaptation: {scenario['language']}")
                print(f"   Primary Response Length: {len(dual_resp.get('primary_response', ''))}")
                print(f"   Secondary Response Length: {len(dual_resp.get('secondary_response', ''))}")
                
                # Check if response shows personalization
                primary_response = dual_resp.get('primary_response', '')
                secondary_response = dual_resp.get('secondary_response', '')
                
                # Look for language-specific indicators
                if scenario['language'] == 'hindi':
                    has_hindi_elements = any(char in primary_response + secondary_response 
                                           for char in 'अआइईउऊएऐओऔकखगघचछजझटठडढणतथदधनपफबभमयरलवशषसह')
                    if has_hindi_elements:
                        print(f"   ✅ Hindi language elements detected in response")
                    else:
                        print(f"   ⚠️  No Hindi elements detected (may be transliterated)")
                elif scenario['language'] == 'hinglish':
                    # Look for mixed language patterns
                    has_mixed_elements = ('ke' in primary_response.lower() or 'hai' in primary_response.lower() or 
                                        'karo' in primary_response.lower() or 'aur' in primary_response.lower())
                    if has_mixed_elements:
                        print(f"   ✅ Hinglish language patterns detected")
                    else:
                        print(f"   ⚠️  Limited Hinglish patterns detected")
                
                success_count += 1
            else:
                print(f"   ❌ Personalized {scenario['name']} failed")
            
            time.sleep(5)  # Delay between AI calls
        
        return success_count >= len(language_scenarios) * 0.8

    def run_personalization_tests(self):
        """Run Phase B: Enhanced Personalization tests"""
        print("🚀 Starting Phase B: Enhanced Personalization Testing")
        print("=" * 80)
        
        # Authentication first
        print("\n🔐 Authentication Setup:")
        if not self.test_user_login():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Phase B: Enhanced Personalization Tests
        print("\n📋 PHASE B: ENHANCED PERSONALIZATION TESTS")
        print("-" * 50)
        
        # Personalization API endpoints
        print("\n🎯 Personalization API Endpoints:")
        self.test_personalization_profile_get()
        self.test_personalization_profile_post()
        self.test_personalization_mastery_tracking()
        self.test_personalization_error_patterns()
        self.test_personalization_feedback_recording()
        
        # Enhanced AI personalization
        print("\n🧠 Enhanced AI Personalization:")
        self.test_personalized_dual_ai_responses()
        
        # Final summary
        print("\n" + "=" * 80)
        print("🎯 PHASE B PERSONALIZATION TESTING SUMMARY")
        print("=" * 80)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL PERSONALIZATION TESTS PASSED!")
        elif self.tests_passed / self.tests_run >= 0.8:
            print("✅ MOSTLY SUCCESSFUL! Most personalization features working correctly.")
        else:
            print("⚠️  SOME PERSONALIZATION ISSUES DETECTED. Please review failed tests.")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = PersonalizationTester()
    tester.run_personalization_tests()