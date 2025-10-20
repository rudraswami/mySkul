#!/usr/bin/env python3
"""
Auto-Note Mentor Routing Fix Test
Tests the fixed FastAPI routing issue where specific endpoints were incorrectly matching general {session_id} endpoint
"""

import requests
import sys
import json
from datetime import datetime
import time

class AutoNoteRoutingTester:
    def __init__(self, base_url="https://edtech-fixes.preview.emergentagent.com/api"):
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

    def test_auto_note_mentor_routing_fix(self):
        """Test the fixed Auto-Note Mentor backend endpoints after FastAPI routing fix"""
        if not self.token:
            print("❌ No token available for Auto-Note Mentor routing fix test")
            return False
        
        print("\n🎯 AUTO-NOTE MENTOR ROUTING FIX VALIDATION")
        print("   Testing fixed FastAPI routing issue where specific endpoints were incorrectly matching general {session_id} endpoint")
        print("   Expected: All endpoints should return 200 OK instead of 500 Internal Server Error")
        print("   Authentication: test@dhruvai.com/password123")
        
        # Track test results for each endpoint
        test_results = {
            'session_creation': False,
            'sessions_list': False,
            'class_series': False,
            'analytics': False,
            'individual_session': False
        }
        
        session_id = None
        
        # Test 1: POST /api/auto-notes/start-session (should work)
        print("\n   Test 1: Session Creation - POST /api/auto-notes/start-session")
        session_data = {
            "title": "Test Physics Class",
            "subject": "Physics"
        }
        
        success, response = self.run_test(
            "Auto-Note Session Creation",
            "POST",
            "auto-notes/start-session",
            200,
            data=session_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success and 'session_id' in response:
            session_id = response['session_id']
            print(f"   ✅ Session created successfully: {session_id}")
            test_results['session_creation'] = True
        else:
            print("   ❌ Session creation failed")
        
        # Test 2: GET /api/auto-notes/sessions (was failing with 500 before routing fix)
        print("\n   Test 2: Sessions List - GET /api/auto-notes/sessions")
        print("   This endpoint was failing with 500 errors due to FastAPI routing conflict")
        
        success, response = self.run_test(
            "Auto-Note Sessions List",
            "GET",
            "auto-notes/sessions",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            sessions = response.get('sessions', [])
            print(f"   ✅ Sessions list retrieved successfully: {len(sessions)} sessions")
            test_results['sessions_list'] = True
        else:
            print("   ❌ Sessions list failed - routing fix may not be working")
        
        # Test 3: GET /api/auto-notes/class-series (was failing with 500 before routing fix)
        print("\n   Test 3: Class Series - GET /api/auto-notes/class-series")
        print("   This endpoint was failing with 500 errors due to FastAPI routing conflict")
        
        success, response = self.run_test(
            "Auto-Note Class Series",
            "GET",
            "auto-notes/class-series",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            class_series = response.get('class_series', [])
            print(f"   ✅ Class series retrieved successfully: {len(class_series)} series")
            test_results['class_series'] = True
        else:
            print("   ❌ Class series failed - routing fix may not be working")
        
        # Test 4: GET /api/auto-notes/analytics (was failing with 500 before routing fix)
        print("\n   Test 4: Analytics - GET /api/auto-notes/analytics")
        print("   This endpoint was failing with 500 errors due to FastAPI routing conflict")
        
        success, response = self.run_test(
            "Auto-Note Analytics",
            "GET",
            "auto-notes/analytics",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            analytics = response.get('analytics', {})
            total_sessions = analytics.get('total_sessions', 0)
            total_hours = analytics.get('total_hours', 0)
            print(f"   ✅ Analytics retrieved successfully: {total_sessions} sessions, {total_hours} hours")
            test_results['analytics'] = True
        else:
            print("   ❌ Analytics failed - routing fix may not be working")
        
        # Test 5: GET /api/auto-notes/{session_id} (should still work)
        if session_id:
            print(f"\n   Test 5: Individual Session - GET /api/auto-notes/{session_id}")
            print("   This endpoint should continue working after routing fix")
            
            success, response = self.run_test(
                "Auto-Note Individual Session",
                "GET",
                f"auto-notes/{session_id}",
                200,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success:
                session_data = response.get('session', {})
                session_title = session_data.get('title', 'Unknown')
                print(f"   ✅ Individual session retrieved successfully: {session_title}")
                test_results['individual_session'] = True
            else:
                print("   ❌ Individual session failed")
        else:
            print("\n   Test 5: Individual Session - SKIPPED (no session_id available)")
        
        # Summary of routing fix validation
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"\n🎯 AUTO-NOTE MENTOR ROUTING FIX SUMMARY:")
        print(f"   ✅ Session Creation: {'PASS' if test_results['session_creation'] else 'FAIL'}")
        print(f"   ✅ Sessions List: {'PASS' if test_results['sessions_list'] else 'FAIL'}")
        print(f"   ✅ Class Series: {'PASS' if test_results['class_series'] else 'FAIL'}")
        print(f"   ✅ Analytics: {'PASS' if test_results['analytics'] else 'FAIL'}")
        print(f"   ✅ Individual Session: {'PASS' if test_results['individual_session'] else 'FAIL'}")
        print(f"   📊 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("   🎉 ROUTING FIX SUCCESSFUL - FastAPI routing issue resolved!")
        else:
            print("   ⚠️  ROUTING FIX INCOMPLETE - Some endpoints still failing")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = AutoNoteRoutingTester()
    
    # Run only the Auto-Note Mentor routing fix test as per review request
    print("🚀 Starting Auto-Note Mentor Routing Fix Testing...")
    print("   Focus: Testing fixed FastAPI routing issue")
    print("="*80)
    
    # Authentication first
    if not tester.test_user_login():
        print("❌ Login failed, cannot proceed with routing fix test")
        sys.exit(1)
    
    # Run the specific routing fix test
    success = tester.test_auto_note_mentor_routing_fix()
    
    # Final summary
    print("\n" + "="*80)
    print("🎯 AUTO-NOTE MENTOR ROUTING FIX TESTING COMPLETE")
    print("="*80)
    print(f"Total tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if success:
        print("🎉 ROUTING FIX VALIDATION SUCCESSFUL!")
    else:
        print("⚠️  ROUTING FIX VALIDATION FAILED - Review needed")
    
    sys.exit(0 if success else 1)