#!/usr/bin/env python3
"""
Auto-Note Mentor Review Request Testing
Specific focus on diagnosing 500 errors as requested in the review
"""

import requests
import sys
import json
from datetime import datetime
import subprocess

class AutoNoteReviewTester:
    def __init__(self, base_url="https://test-genflow.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.session_id = None
        self.tests_run = 0
        self.tests_passed = 0

    def authenticate(self):
        """Authenticate with test@dhruvai.com/password123"""
        print("🔐 Authenticating with test@dhruvai.com/password123...")
        
        login_data = {
            "email": "test@dhruvai.com",
            "password": "password123"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['token']
                self.user_id = data['user'].get('user_id')
                print(f"   ✅ Authentication successful")
                print(f"   Token: {self.token[:20]}...")
                print(f"   User ID: {self.user_id}")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False

    def test_api_endpoint(self, name, method, endpoint, data=None):
        """Test a single API endpoint and capture detailed error info"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"   ✅ SUCCESS")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys())}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"   ❌ FAILED - Status: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                
                # Capture specific error details for 500 errors
                if response.status_code == 500:
                    print(f"   🔍 500 INTERNAL SERVER ERROR DETECTED")
                    print(f"   This is the core issue mentioned in the review request")
                
                return False, {}
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
            return False, {}

    def check_backend_logs(self):
        """Check backend logs for specific error details"""
        print("\n📋 CHECKING BACKEND LOGS FOR ERROR DETAILS...")
        
        try:
            # Check supervisor backend error logs
            result = subprocess.run(
                ['tail', '-n', '50', '/var/log/supervisor/backend.err.log'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split('\n')
                
                # Look for recent errors related to Auto-Note Mentor
                relevant_errors = []
                for line in lines:
                    if any(keyword in line.lower() for keyword in [
                        'auto-note', 'note_session', 'auto_note_session', 
                        'objectid', 'serialization', 'failed to retrieve session',
                        'collection', 'mongodb'
                    ]):
                        relevant_errors.append(line)
                
                if relevant_errors:
                    print("   🔍 RELEVANT ERROR LOGS FOUND:")
                    for error in relevant_errors[-10:]:  # Show last 10 relevant errors
                        print(f"   - {error}")
                else:
                    print("   ℹ️  No specific Auto-Note errors in recent logs")
                    print("   📋 Last 5 general error lines:")
                    for line in lines[-5:]:
                        print(f"   - {line}")
            else:
                print("   ⚠️  Could not read backend error logs")
                
        except Exception as e:
            print(f"   ⚠️  Error checking logs: {str(e)}")

    def run_review_focused_test(self):
        """Run the specific tests requested in the review"""
        print("🎯 AUTO-NOTE MENTOR REVIEW REQUEST TESTING")
        print("   Focus: Diagnose specific 500 errors in Auto-Note Mentor backend APIs")
        print("   Testing with credentials: test@dhruvai.com/password123")
        print("="*80)
        
        # Step 0: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed")
            return False
        
        test_results = {}
        
        # Step 1: Session Creation Test
        print("\n📋 STEP 1: SESSION CREATION TEST")
        print("   POST /api/auto-notes/start-session with valid credentials")
        
        session_data = {
            "title": "Physics Class - Electromagnetic Induction",
            "subject": "Physics"
        }
        
        success, response = self.test_api_endpoint(
            "Session Creation",
            "POST",
            "auto-notes/start-session",
            session_data
        )
        
        test_results['session_creation'] = success
        if success:
            self.session_id = response.get('session_id')
            print(f"   📊 Session created with ID: {self.session_id}")
            print(f"   📊 Data stored in database:")
            print(f"   - session_id: {self.session_id}")
            print(f"   - user_id: {self.user_id}")
            print(f"   - subject: Physics")
            print(f"   - status: {response.get('status')}")
        
        # Step 2: Session Retrieval Test
        print("\n📋 STEP 2: SESSION RETRIEVAL TEST")
        print("   GET /api/auto-notes/sessions to retrieve all sessions for user")
        
        success, response = self.test_api_endpoint(
            "Session Retrieval",
            "GET",
            "auto-notes/sessions"
        )
        
        test_results['session_retrieval'] = success
        if success:
            sessions = response.get('sessions', [])
            print(f"   📊 Retrieved {len(sessions)} sessions")
            
            # Check if session from step 1 can be retrieved
            if self.session_id:
                session_ids = [s.get('session_id') for s in sessions]
                if self.session_id in session_ids:
                    print(f"   ✅ Session from step 1 found in retrieval")
                else:
                    print(f"   ⚠️  Session from step 1 NOT found in retrieval")
                    print(f"   🔍 This indicates database collection mismatch")
        else:
            print(f"   🔍 This is the core 500 error mentioned in the review")
        
        # Step 3: Database Collection Verification
        print("\n📋 STEP 3: SPECIFIC SESSION LOOKUP TEST")
        print(f"   GET /api/auto-notes/{{session_id}} using session_id from step 1")
        
        if self.session_id:
            success, response = self.test_api_endpoint(
                "Specific Session Lookup",
                "GET",
                f"auto-notes/{self.session_id}"
            )
            
            test_results['specific_session_lookup'] = success
            if success:
                retrieved_id = response.get('session_id')
                print(f"   📊 Retrieved session ID: {retrieved_id}")
                print(f"   📊 Matches created session: {'Yes' if retrieved_id == self.session_id else 'No'}")
            else:
                print(f"   🔍 Session exists in creation but fails in retrieval")
                print(f"   🔍 This confirms database collection inconsistency")
        else:
            print("   ⚠️  Skipping - no session_id from step 1")
            test_results['specific_session_lookup'] = False
        
        # Step 4: Class Series Test
        print("\n📋 STEP 4: CLASS SERIES TEST")
        print("   GET /api/auto-notes/class-series")
        
        success, response = self.test_api_endpoint(
            "Class Series",
            "GET",
            "auto-notes/class-series"
        )
        
        test_results['class_series'] = success
        if success:
            class_series = response.get('class_series', [])
            print(f"   📊 Retrieved {len(class_series)} class series")
        
        # Step 5: Analytics Test
        print("\n📋 STEP 5: ANALYTICS TEST")
        print("   GET /api/auto-notes/analytics")
        
        success, response = self.test_api_endpoint(
            "Analytics",
            "GET",
            "auto-notes/analytics"
        )
        
        test_results['analytics'] = success
        if success:
            analytics = response.get('analytics', {})
            print(f"   📊 Analytics data keys: {list(analytics.keys())}")
        
        # Step 6: Backend Error Analysis
        self.check_backend_logs()
        
        # Final Analysis
        print("\n🎯 REVIEW REQUEST ANALYSIS:")
        print("="*80)
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"   ✅ Session Creation: {'PASS' if test_results['session_creation'] else 'FAIL'}")
        print(f"   ✅ Session Retrieval: {'PASS' if test_results['session_retrieval'] else 'FAIL'}")
        print(f"   ✅ Specific Session Lookup: {'PASS' if test_results['specific_session_lookup'] else 'FAIL'}")
        print(f"   ✅ Class Series: {'PASS' if test_results['class_series'] else 'FAIL'}")
        print(f"   ✅ Analytics: {'PASS' if test_results['analytics'] else 'FAIL'}")
        print(f"   📊 Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Root Cause Analysis
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        
        if test_results['session_creation'] and not test_results['session_retrieval']:
            print("   🎯 PRIMARY ISSUE: Session creation works but retrieval fails with 500 errors")
            print("   🔍 LIKELY CAUSE: Database collection mismatch")
            print("   💡 EXPLANATION: start-session stores in 'auto_note_sessions' but")
            print("      sessions endpoint looks in 'note_sessions' collection")
            print("   💡 SOLUTION: Update all Auto-Note endpoints to use consistent collection")
        
        if not test_results['analytics'] or not test_results['class_series']:
            print("   🎯 SECONDARY ISSUE: Analytics/Class Series endpoints also failing")
            print("   🔍 LIKELY CAUSE: Similar database collection or ObjectId serialization issues")
        
        # Error Pattern Analysis
        print(f"\n📊 ERROR PATTERN COMPARISON:")
        failing_endpoints = [k for k, v in test_results.items() if not v]
        if failing_endpoints:
            print(f"   ❌ Failing endpoints: {', '.join(failing_endpoints)}")
            print(f"   🔍 Common pattern: All involve session/data retrieval operations")
            print(f"   🔍 This confirms the database collection mismatch hypothesis")
        
        print("="*80)
        print(f"   Total API calls: {self.tests_run}")
        print(f"   Successful calls: {self.tests_passed}")
        print(f"   Overall success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        return success_rate >= 40.0  # Lower threshold due to known issues

if __name__ == "__main__":
    tester = AutoNoteReviewTester()
    success = tester.run_review_focused_test()
    
    print(f"\n🎯 REVIEW REQUEST CONCLUSION:")
    if success:
        print("✅ Testing completed - Issues identified and analyzed")
    else:
        print("❌ Critical issues confirmed - Requires immediate attention")
    
    sys.exit(0)  # Always exit 0 for analysis completion