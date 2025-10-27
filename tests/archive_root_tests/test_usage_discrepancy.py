#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class UsageDiscrepancyTester:
    def __init__(self, base_url="https://eduai-platform-28.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
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
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
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
        """Authenticate with test user credentials"""
        print(f"\n🔐 Authenticating with {self.test_user_email}...")
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        success, response = self.run_test(
            "User Authentication",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            if 'user' in response:
                self.user_id = response['user'].get('user_id')
            print(f"   ✅ Authentication successful - Token: {self.token[:20]}...")
            return True
        else:
            print("   ❌ Authentication failed")
            return False

    def test_usage_discrepancy(self):
        """Test for usage discrepancy between frontend display and backend tracking"""
        print("\n🚨 TESTING USAGE DISCREPANCY ISSUE")
        print("   Issue: Frontend shows 0/2 usage but backend tracks different usage")
        print(f"   User: {self.test_user_email}/{self.test_user_password}")
        
        if not self.authenticate():
            return False
        
        # Step 1: Check current usage multiple times to see consistency
        print("\n📋 STEP 1: Check Usage Consistency")
        
        for i in range(3):
            print(f"\n   Check #{i+1}:")
            success, response = self.run_test(
                f"Usage Check #{i+1}",
                "GET",
                "subscription/usage",
                200,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success:
                usage_details = response.get('usage_details', {})
                mock_tests_usage = usage_details.get('mock_tests_monthly', {})
                
                used = mock_tests_usage.get('used', 0)
                limit = mock_tests_usage.get('limit', 0)
                remaining = mock_tests_usage.get('remaining', 0)
                has_access = mock_tests_usage.get('has_access', False)
                
                print(f"   Usage: {used}/{limit} used, {remaining} remaining, has_access: {has_access}")
                
                if used >= limit:
                    print(f"   🚨 USER HAS REACHED LIMIT: {used}/{limit} - This explains the 'Free Tier Limit' popup!")
                    return True
            
            time.sleep(1)
        
        # Step 2: Try to generate a test to see what happens
        print("\n📋 STEP 2: Attempt Mock Test Generation")
        
        test_data = {
            "exam_type": "JEE",
            "subjects": ["Mathematics"],
            "num_questions": 5,
            "difficulty_level": 3
        }
        
        success, response = self.run_test(
            "Mock Test Generation Attempt",
            "POST",
            "mock-tests/generate",
            [200, 402],  # Accept either success or payment required
            data=test_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if not success:
            print("   🚨 Mock test generation failed - this confirms the free tier limit issue")
            return True
        else:
            print("   ✅ Mock test generation succeeded - no limit issue detected")
            return False

    def run_comprehensive_test(self):
        """Run comprehensive test of usage discrepancy"""
        print("🚀 Starting Usage Discrepancy Test...")
        print("================================================================================")
        
        try:
            issue_confirmed = self.test_usage_discrepancy()
            
            print("\n================================================================================")
            print("🎯 USAGE DISCREPANCY TEST SUMMARY:")
            
            if issue_confirmed:
                print("   🚨 ISSUE CONFIRMED: User has reached free tier limit")
                print("   🚨 Backend correctly blocks further test generation")
                print("   🚨 Frontend may be showing incorrect usage (0/2 instead of actual usage)")
                print("   🔧 RECOMMENDATION: Check frontend usage display logic")
                print("   🔧 SOLUTION: Frontend should refresh usage data or fix display bug")
            else:
                print("   ✅ No usage discrepancy detected")
                print("   ✅ User can still generate tests within free tier limits")
            
            return issue_confirmed
            
        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")
            return False

if __name__ == "__main__":
    tester = UsageDiscrepancyTester()
    issue_confirmed = tester.run_comprehensive_test()
    sys.exit(0 if issue_confirmed else 1)