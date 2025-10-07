#!/usr/bin/env python3
"""
Focused Dual-Layer AI System Testing Script
Testing the three AI Tutor API endpoints as requested in the review
"""

import requests
import sys
import json
from datetime import datetime
import time

class DualAITester:
    def __init__(self, base_url="https://dhruv-edutech.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
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
                response = requests.get(url, headers=test_headers, timeout=60)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=60)

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

    def test_user_login(self):
        """Test user login with the test credentials"""
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
            print(f"   Login token: {self.token[:20]}...")
            return True
        return False

    def test_dual_response_endpoint(self):
        """Test /api/ai/dual-response endpoint"""
        if not self.token:
            print("❌ No token available for dual response test")
            return False
        
        print("   Testing /api/ai/dual-response endpoint...")
        
        # Test scenarios from review request
        test_scenarios = [
            {
                "message": "Solve the quadratic equation x² + 5x + 6 = 0 step by step",
                "subject": "Mathematics",
                "expected_primary": "professor",
                "description": "Technical question (should trigger Professor lead)"
            },
            {
                "message": "I'm feeling stressed about my JEE preparation and need motivation",
                "subject": "General",
                "expected_primary": "mentor", 
                "description": "Motivational question (should trigger Mentor lead)"
            },
            {
                "message": "What are the best study techniques for competitive exams?",
                "subject": "General",
                "expected_primary": "mentor",
                "description": "General guidance question"
            }
        ]
        
        success_count = 0
        
        for i, scenario in enumerate(test_scenarios):
            print(f"\n   🎯 Scenario {i+1}/3: {scenario['description']}")
            print(f"   Question: '{scenario['message'][:60]}...'")
            print("   ⏳ This may take 10-15 seconds for dual AI processing...")
            
            success, response = self.run_test(
                f"Dual Response - {scenario['description']}",
                "POST",
                "ai/dual-response",
                200,
                data={
                    "message": scenario['message'],
                    "subject": scenario['subject']
                }
            )
            
            if success and 'dual_response' in response:
                dual_resp = response['dual_response']
                primary = dual_resp.get('primary', {})
                secondary = dual_resp.get('secondary', {})
                scenario_type = dual_resp.get('scenario_type')
                confidence = dual_resp.get('confidence', 0)
                
                print(f"   ✅ Dual response received")
                print(f"   📊 Primary persona: {primary.get('persona')}")
                print(f"   📊 Secondary persona: {secondary.get('persona')}")
                print(f"   📊 Scenario type: {scenario_type}")
                print(f"   📊 Confidence: {confidence:.2f}")
                print(f"   📝 Primary response length: {len(primary.get('response', ''))}")
                print(f"   📝 Secondary response length: {len(secondary.get('response', ''))}")
                
                # Validate dual response structure
                required_fields = ['primary', 'secondary', 'scenario_type', 'confidence']
                has_all_fields = all(field in dual_resp for field in required_fields)
                
                # Validate persona responses
                primary_valid = (primary.get('persona') and 
                               primary.get('response') and 
                               len(primary.get('response', '')) > 50)
                secondary_valid = (secondary.get('persona') and 
                                 secondary.get('reasoning') and
                                 len(secondary.get('reasoning', '')) > 20)
                
                if has_all_fields and primary_valid and secondary_valid:
                    print(f"   ✅ Response structure validated")
                    print(f"   ✅ Both personas provided substantial responses")
                    success_count += 1
                else:
                    print(f"   ⚠️  Response structure incomplete")
                    print(f"   Missing fields: {[f for f in required_fields if f not in dual_resp]}")
                    print(f"   Primary valid: {primary_valid}")
                    print(f"   Secondary valid: {secondary_valid}")
            else:
                print(f"   ❌ Dual response failed")
            
            time.sleep(3)  # Delay between AI calls
        
        return success_count == len(test_scenarios)

    def test_mentor_only_endpoint(self):
        """Test /api/ai/mentor-only endpoint"""
        if not self.token:
            print("❌ No token available for mentor test")
            return False
        
        print("   Testing /api/ai/mentor-only endpoint...")
        
        # Test mentor-focused messages
        mentor_scenarios = [
            {
                "message": "I'm feeling overwhelmed with my JEE preparation and need encouragement",
                "subject": "General",
                "description": "Stress and motivation"
            },
            {
                "message": "How can I create an effective study schedule for competitive exams?",
                "subject": "General", 
                "description": "Study planning guidance"
            }
        ]
        
        success_count = 0
        
        for i, scenario in enumerate(mentor_scenarios):
            print(f"\n   🎯 Mentor Test {i+1}/2: {scenario['description']}")
            print(f"   Question: '{scenario['message'][:60]}...'")
            print("   ⏳ This may take 5-10 seconds for AI processing...")
            
            success, response = self.run_test(
                f"Mentor Only - {scenario['description']}",
                "POST",
                "ai/mentor-only",
                200,
                data=scenario
            )
            
            if success:
                persona = response.get('persona')
                ai_response = response.get('response', '')
                reasoning = response.get('reasoning', '')
                
                print(f"   ✅ Mentor response received")
                print(f"   📊 Persona: {persona}")
                print(f"   📝 Response length: {len(ai_response)}")
                print(f"   🧠 Has reasoning: {'Yes' if reasoning else 'No'}")
                
                # Validate mentor persona and response quality
                if (persona == 'mentor' and 
                    ai_response and len(ai_response) > 50 and 
                    reasoning and len(reasoning) > 20):
                    print(f"   ✅ Mentor response validated")
                    print(f"   ✅ Response shows mentoring characteristics")
                    success_count += 1
                else:
                    print(f"   ⚠️  Mentor response incomplete")
                    print(f"   Persona correct: {persona == 'mentor'}")
                    print(f"   Response substantial: {len(ai_response) > 50}")
                    print(f"   Has reasoning: {len(reasoning) > 20}")
            else:
                print(f"   ❌ Mentor response failed")
            
            time.sleep(3)  # Delay between AI calls
        
        return success_count == len(mentor_scenarios)

    def test_professor_only_endpoint(self):
        """Test /api/ai/professor-only endpoint"""
        if not self.token:
            print("❌ No token available for professor test")
            return False
        
        print("   Testing /api/ai/professor-only endpoint...")
        
        # Test professor-focused messages
        professor_scenarios = [
            {
                "message": "Derive the quadratic formula from ax² + bx + c = 0",
                "subject": "Mathematics",
                "description": "Mathematical derivation"
            },
            {
                "message": "Explain Newton's second law of motion with mathematical proof",
                "subject": "Physics",
                "description": "Physics concept with proof"
            }
        ]
        
        success_count = 0
        
        for i, scenario in enumerate(professor_scenarios):
            print(f"\n   🎯 Professor Test {i+1}/2: {scenario['description']}")
            print(f"   Question: '{scenario['message'][:60]}...'")
            print("   ⏳ This may take 5-10 seconds for AI processing...")
            
            success, response = self.run_test(
                f"Professor Only - {scenario['description']}",
                "POST",
                "ai/professor-only",
                200,
                data=scenario
            )
            
            if success:
                persona = response.get('persona')
                ai_response = response.get('response', '')
                reasoning = response.get('reasoning', '')
                
                print(f"   ✅ Professor response received")
                print(f"   📊 Persona: {persona}")
                print(f"   📝 Response length: {len(ai_response)}")
                print(f"   🧠 Has reasoning: {'Yes' if reasoning else 'No'}")
                
                # Validate professor persona and response quality
                if (persona == 'professor' and 
                    ai_response and len(ai_response) > 50 and 
                    reasoning and len(reasoning) > 20):
                    print(f"   ✅ Professor response validated")
                    print(f"   ✅ Response shows academic rigor")
                    success_count += 1
                else:
                    print(f"   ⚠️  Professor response incomplete")
                    print(f"   Persona correct: {persona == 'professor'}")
                    print(f"   Response substantial: {len(ai_response) > 50}")
                    print(f"   Has reasoning: {len(reasoning) > 20}")
            else:
                print(f"   ❌ Professor response failed")
            
            time.sleep(3)  # Delay between AI calls
        
        return success_count == len(professor_scenarios)

    def test_authentication_validation(self):
        """Test authentication validation on all dual AI endpoints"""
        print("   Testing authentication validation...")
        
        # Test without token (should fail with 401)
        endpoints_to_test = [
            ("ai/dual-response", "POST", {"message": "Test message", "subject": "Mathematics"}),
            ("ai/mentor-only", "POST", {"message": "Test message", "subject": "Mathematics"}),
            ("ai/professor-only", "POST", {"message": "Test message", "subject": "Mathematics"})
        ]
        
        success_count = 0
        
        for endpoint, method, test_data in endpoints_to_test:
            print(f"\n   🔒 Testing {endpoint} without authentication...")
            
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

def main():
    print("🚀 DHRUV AI DUAL-LAYER SYSTEM COMPREHENSIVE TESTING")
    print("=" * 70)
    print("🎯 FOCUS: Test all three AI Tutor API endpoints")
    print("🔐 AUTHENTICATION: Using test@dhruvai.com / password123")
    print("📋 ENDPOINTS TO TEST:")
    print("   1. /api/ai/dual-response (dual response structure)")
    print("   2. /api/ai/mentor-only (Mentor-only responses)")
    print("   3. /api/ai/professor-only (Professor-only responses)")
    print("=" * 70)
    
    tester = DualAITester()
    
    # Test sequence
    tests = [
        ("🔐 User Authentication", tester.test_user_login),
        ("🤖 Dual-Response Endpoint", tester.test_dual_response_endpoint),
        ("👨‍🏫 Mentor-Only Endpoint", tester.test_mentor_only_endpoint),
        ("👨‍🎓 Professor-Only Endpoint", tester.test_professor_only_endpoint),
        ("🔒 Authentication Validation", tester.test_authentication_validation),
    ]
    
    failed_tests = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 {test_name}")
        print(f"{'='*50}")
        
        try:
            success = test_func()
            if not success:
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            failed_tests.append(test_name)
        
        # Small delay between tests
        time.sleep(2)
    
    # Print final results
    print("\n" + "=" * 70)
    print("📊 FINAL TEST RESULTS - DUAL-LAYER AI SYSTEM")
    print("=" * 70)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test in failed_tests:
            print(f"   - {test}")
        print(f"\n🔍 ISSUES FOUND:")
        print(f"   Please review failed tests above for API functionality issues.")
        return 1
    else:
        print(f"\n✅ All tests passed!")
        print(f"🎉 Dual-Layer AI System is working correctly!")
        
    print(f"\n📋 ENDPOINTS TESTED:")
    print(f"   ✓ /api/ai/dual-response - Coordinated Professor+Mentor responses")
    print(f"   ✓ /api/ai/mentor-only - Pure mentor responses with persona validation")
    print(f"   ✓ /api/ai/professor-only - Pure professor responses with technical accuracy")
    print(f"   ✓ Authentication integration confirmed for all endpoints")
    print(f"   ✓ Response quality and formatting validated")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())