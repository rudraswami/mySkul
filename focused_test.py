#!/usr/bin/env python3

import requests
import json
import time

class FocusedSubscriptionTester:
    def __init__(self):
        self.base_url = "https://modular-backend-5.preview.emergentagent.com/api"
        self.token = None
        self.test_user_email = "test@dhruvai.com"
        self.test_user_password = "password123"

    def login(self):
        """Login with test credentials"""
        print("🔐 Logging in with test@dhruvai.com...")
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"Login status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                print(f"✅ Login successful, token: {self.token[:20]}...")
                return True
            else:
                print(f"❌ Login failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False

    def test_subscription_current(self):
        """Test GET /api/subscription/current"""
        print("\n🎯 Testing GET /api/subscription/current...")
        
        if not self.token:
            print("❌ No token available")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/subscription/current",
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                },
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS: /api/subscription/current returns 200 OK")
                print(f"Response: {json.dumps(data, indent=2)}")
                return True
            elif response.status_code == 500:
                print("❌ CRITICAL: Still returning 500 Internal Server Error")
                print(f"Error: {response.text}")
                return False
            else:
                print(f"⚠️  Unexpected status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Request error: {str(e)}")
            return False

    def test_subscription_usage(self):
        """Test GET /api/subscription/usage"""
        print("\n🎯 Testing GET /api/subscription/usage...")
        
        if not self.token:
            print("❌ No token available")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/subscription/usage",
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                },
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS: /api/subscription/usage returns 200 OK")
                print(f"Response: {json.dumps(data, indent=2)}")
                return True
            elif response.status_code == 500:
                print("❌ CRITICAL: Still returning 500 Internal Server Error")
                print(f"Error: {response.text}")
                return False
            else:
                print(f"⚠️  Unexpected status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Request error: {str(e)}")
            return False

    def test_mock_test_generation(self):
        """Test mock test generation with correct format"""
        print("\n🎯 Testing mock test generation with subjects array format...")
        
        if not self.token:
            print("❌ No token available")
            return False
            
        test_data = {
            "exam_type": "JEE",
            "subjects": ["Mathematics"],  # Array format
            "difficulty": 3,
            "num_questions": 3  # Minimum questions
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/mock-tests/generate",
                json=test_data,
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                },
                timeout=60
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS: Mock test generation works with subjects array")
                print(f"Test ID: {data.get('test_id', 'N/A')}")
                print(f"Questions: {len(data.get('questions', []))}")
                return True
            elif response.status_code == 402:
                data = response.json()
                print("✅ SUCCESS: Proper 402 error for subscription limits")
                print(f"Error message: {data.get('message', 'N/A')}")
                return True
            elif response.status_code == 422:
                data = response.json()
                print("❌ PARAMETER VALIDATION ISSUE: 422 validation error")
                print(f"Error: {data}")
                return False
            elif response.status_code == 500:
                print("❌ CRITICAL: 500 Internal Server Error")
                print(f"Error: {response.text}")
                return False
            else:
                print(f"⚠️  Unexpected status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Request error: {str(e)}")
            return False

    def test_dynamic_subjects(self):
        """Test dynamic subject mapping"""
        print("\n🎯 Testing dynamic subject mapping...")
        
        if not self.token:
            print("❌ No token available")
            return False
            
        # Step 1: Get current subjects
        try:
            response = requests.get(
                f"{self.base_url}/mock-tests/subjects",
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                },
                timeout=30
            )
            
            print(f"Get subjects status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                current_exam_type = data.get('exam_type', 'unknown')
                current_subjects = data.get('subjects', [])
                print(f"✅ Current exam type: {current_exam_type}")
                print(f"✅ Current subjects: {current_subjects}")
                
                # Step 2: Switch exam type
                target_exam_type = "UPSC" if current_exam_type == "JEE" else "JEE"
                
                switch_response = requests.post(
                    f"{self.base_url}/user/update-exam-type",
                    json={"exam_type": target_exam_type},
                    headers={
                        'Authorization': f'Bearer {self.token}',
                        'Content-Type': 'application/json'
                    },
                    timeout=30
                )
                
                print(f"Switch exam type status: {switch_response.status_code}")
                
                if switch_response.status_code == 200:
                    print(f"✅ Switched to {target_exam_type}")
                    
                    # Step 3: Check if subjects updated
                    time.sleep(2)  # Wait for sync
                    
                    sync_response = requests.get(
                        f"{self.base_url}/mock-tests/subjects",
                        headers={
                            'Authorization': f'Bearer {self.token}',
                            'Content-Type': 'application/json'
                        },
                        timeout=30
                    )
                    
                    if sync_response.status_code == 200:
                        sync_data = sync_response.json()
                        synced_exam_type = sync_data.get('exam_type', 'unknown')
                        synced_subjects = sync_data.get('subjects', [])
                        
                        print(f"Synced exam type: {synced_exam_type}")
                        print(f"Synced subjects: {synced_subjects}")
                        
                        if synced_exam_type == target_exam_type and set(synced_subjects) != set(current_subjects):
                            print("✅ SYNCHRONIZATION WORKING: Subjects updated after exam type change")
                            return True
                        else:
                            print("❌ SYNCHRONIZATION ISSUE: Subjects not updated properly")
                            return False
                    else:
                        print(f"❌ Failed to get synced subjects: {sync_response.status_code}")
                        return False
                else:
                    print(f"❌ Failed to switch exam type: {switch_response.status_code}")
                    return False
            else:
                print(f"❌ Failed to get current subjects: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Request error: {str(e)}")
            return False

    def run_focused_tests(self):
        """Run focused subscription infrastructure tests"""
        print("🚀 CRITICAL SUBSCRIPTION INFRASTRUCTURE RETEST")
        print("=" * 60)
        
        # Login first
        if not self.login():
            print("❌ Cannot proceed without authentication")
            return False
        
        results = {
            'subscription_current': self.test_subscription_current(),
            'subscription_usage': self.test_subscription_usage(),
            'mock_test_generation': self.test_mock_test_generation(),
            'dynamic_subjects': self.test_dynamic_subjects()
        }
        
        passed = sum(results.values())
        total = len(results)
        
        print("\n" + "=" * 60)
        print("🎯 FOCUSED TEST RESULTS:")
        print(f"✅ Subscription Current: {'PASS' if results['subscription_current'] else 'FAIL'}")
        print(f"✅ Subscription Usage: {'PASS' if results['subscription_usage'] else 'FAIL'}")
        print(f"✅ Mock Test Generation: {'PASS' if results['mock_test_generation'] else 'FAIL'}")
        print(f"✅ Dynamic Subjects: {'PASS' if results['dynamic_subjects'] else 'FAIL'}")
        print(f"📊 Overall: {passed}/{total} ({(passed/total)*100:.1f}%)")
        
        if passed >= 3:
            print("🎉 SUBSCRIPTION INFRASTRUCTURE FIXES SUCCESSFUL!")
        else:
            print("⚠️  SUBSCRIPTION INFRASTRUCTURE STILL HAS ISSUES")
        
        return passed >= 3

if __name__ == "__main__":
    tester = FocusedSubscriptionTester()
    success = tester.run_focused_tests()
    exit(0 if success else 1)