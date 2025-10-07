#!/usr/bin/env python3

import requests
import json
import time
from datetime import datetime

class Phase4Tester:
    def __init__(self):
        self.base_url = "https://edutech-dhruv.preview.emergentagent.com/api"
        self.token = None
        self.user_id = None
        self.test_ids = []
        self.test_user_email = f"phase4_test_{datetime.now().strftime('%H%M%S')}@test.com"

    def setup_user(self):
        """Register and login a test user"""
        print("🔧 Setting up test user...")
        
        # Register
        registration_data = {
            "full_name": "Phase 4 Test User",
            "email": self.test_user_email,
            "password": "TestPass123!",
            "exam_type": "JEE",
            "grade": "Class 12",
            "target_year": 2026
        }
        
        response = requests.post(f"{self.base_url}/auth/register", json=registration_data)
        if response.status_code == 200:
            data = response.json()
            self.token = data['token']
            self.user_id = data['user']['user_id']
            print(f"✅ User registered and logged in")
            return True
        else:
            print(f"❌ Failed to register user: {response.status_code}")
            return False

    def test_mock_test_generation(self):
        """Test mock test generation"""
        print("\n🧪 Testing Mock Test Generation...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        params = {
            'exam_type': 'JEE',
            'subject': 'Physics',
            'difficulty': 3,
            'num_questions': 5
        }
        
        response = requests.post(f"{self.base_url}/mock-tests/generate", headers=headers, params=params, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            self.test_ids.append(data['test_id'])
            print(f"✅ Mock test generated successfully")
            print(f"   Test ID: {data['test_id']}")
            print(f"   Questions: {len(data.get('questions', []))}")
            print(f"   Total marks: {data.get('total_marks', 0)}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False

    def test_mock_test_submission(self):
        """Test mock test submission"""
        if not self.test_ids:
            print("❌ No test ID available for submission")
            return False
            
        print("\n🧪 Testing Mock Test Submission...")
        
        test_id = self.test_ids[0]
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Get the actual test to get real question IDs
        test_response = requests.get(f"{self.base_url}/mock-tests/{test_id}", headers=headers)
        if test_response.status_code != 200:
            print("❌ Could not fetch test details")
            return False
            
        # For now, use form data approach
        form_data = {
            'time_taken': '1200'
        }
        
        # Add sample answers
        for i in range(5):
            form_data[f'answers[q_{i+1}]'] = 'A'
        
        response = requests.post(f"{self.base_url}/mock-tests/{test_id}/submit", 
                               headers=headers, data=form_data, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Mock test submitted successfully")
            print(f"   Score: {data.get('score', 0)}")
            print(f"   Percentage: {data.get('percentage', 0):.1f}%")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False

    def test_performance_analytics(self):
        """Test performance analytics"""
        print("\n🧪 Testing Performance Analytics...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(f"{self.base_url}/analytics/performance", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Performance analytics retrieved")
            print(f"   Subjects analyzed: {len(data.get('subject_performance', {}))}")
            print(f"   Parent summary available: {'parent_summary' in data}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False

    def test_stress_assessment(self):
        """Test stress assessment"""
        print("\n🧪 Testing Stress Assessment...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        form_data = {
            'stress_level': '7',
            'anxiety_level': '6',
            'sleep_quality': '4',
            'study_motivation': '5',
            'physical_symptoms': 'headache,fatigue',
            'emotional_state': 'overwhelmed'
        }
        
        response = requests.post(f"{self.base_url}/wellness/stress-assessment", 
                               headers=headers, data=form_data, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stress assessment completed")
            print(f"   Wellness score: {data.get('wellness_score', 0):.1f}/10")
            print(f"   Recommendations: {len(data.get('recommendations', []))}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False

    def test_motivational_content(self):
        """Test motivational content"""
        print("\n🧪 Testing Motivational Content...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(f"{self.base_url}/wellness/motivational-content", headers=headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Motivational content retrieved")
            print(f"   Content items: {len(data.get('daily_content', []))}")
            print(f"   Wellness tip: {'wellness_tip' in data}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False

def main():
    print("🚀 Phase 4 Enhanced Features Testing")
    print("=" * 50)
    
    tester = Phase4Tester()
    
    if not tester.setup_user():
        print("❌ Failed to setup test user")
        return 1
    
    tests = [
        ("Mock Test Generation", tester.test_mock_test_generation),
        ("Mock Test Submission", tester.test_mock_test_submission),
        ("Performance Analytics", tester.test_performance_analytics),
        ("Stress Assessment", tester.test_stress_assessment),
        ("Motivational Content", tester.test_motivational_content),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            time.sleep(2)  # Delay between tests
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
    
    print(f"\n" + "=" * 50)
    print(f"📊 PHASE 4 TEST RESULTS")
    print(f"=" * 50)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All Phase 4 features working correctly!")
        return 0
    else:
        print("⚠️  Some Phase 4 features need attention")
        return 1

if __name__ == "__main__":
    exit(main())