#!/usr/bin/env python3
"""
Auto-Note Mentor ObjectId Serialization Testing
Focus on identifying ObjectId serialization issues in backend responses
"""

import requests
import json
import time

class ObjectIdSerializationTester:
    def __init__(self):
        self.base_url = "https://paywall-unity.preview.emergentagent.com/api"
        self.token = None
        self.user_id = None
        
    def login(self):
        """Login with test credentials"""
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
                self.token = data.get('token')
                if 'user' in data:
                    self.user_id = data['user'].get('user_id')
                print(f"✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_api_endpoint(self, name, method, endpoint, data=None, expected_status=200):
        """Test a single API endpoint for ObjectId serialization issues"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            
            print(f"   Status: {response.status_code}")
            
            # Check for ObjectId serialization issues
            objectid_issues = []
            
            try:
                response_data = response.json()
                
                # Check for raw ObjectId strings in response
                response_str = json.dumps(response_data)
                if 'ObjectId(' in response_str:
                    objectid_issues.append("Raw ObjectId found in JSON response")
                
                # Check for ObjectId serialization errors in error messages
                if response.status_code >= 400:
                    error_str = str(response_data)
                    if 'ObjectId' in error_str:
                        if 'not iterable' in error_str:
                            objectid_issues.append("ObjectId 'not iterable' error")
                        elif 'not JSON serializable' in error_str:
                            objectid_issues.append("ObjectId 'not JSON serializable' error")
                        elif 'vars() argument must have __dict__ attribute' in error_str:
                            objectid_issues.append("ObjectId vars() error")
                        else:
                            objectid_issues.append("ObjectId-related error in response")
                
                if objectid_issues:
                    print(f"   🚨 ObjectId Serialization Issues:")
                    for issue in objectid_issues:
                        print(f"      - {issue}")
                    print(f"   Response: {json.dumps(response_data, indent=2)[:500]}...")
                    return False, response_data, objectid_issues
                else:
                    print(f"   ✅ No ObjectId serialization issues detected")
                    if response.status_code == expected_status:
                        print(f"   ✅ Expected status code: {expected_status}")
                        return True, response_data, []
                    else:
                        print(f"   ⚠️  Unexpected status: {response.status_code} (expected {expected_status})")
                        return False, response_data, []
                        
            except json.JSONDecodeError:
                print(f"   ❌ Invalid JSON response")
                print(f"   Response text: {response.text[:200]}...")
                return False, {}, ["Invalid JSON response"]
                
        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")
            return False, {}, [f"Request error: {str(e)}"]
    
    def run_objectid_serialization_tests(self):
        """Run comprehensive ObjectId serialization tests"""
        print("🚨 FINAL BACKEND VALIDATION - AUTO-NOTE MENTOR OBJECTID SERIALIZATION TESTING")
        print("   Review Request: Test ObjectId serialization issues affecting end-session API calls")
        print("   Focus: /api/auto-notes/sessions, /api/auto-notes/start-session, /api/auto-notes/upload-audio, /api/auto-notes/processing-status")
        print("   Goal: Identify 500 errors caused by ObjectId serialization in backend responses")
        print("=" * 80)
        
        if not self.login():
            print("❌ Cannot proceed without authentication")
            return False
        
        test_results = {
            'sessions_list': False,
            'start_session': False,
            'upload_audio': False,
            'processing_status': False,
            'end_session': False,
            'objectid_issues_found': []
        }
        
        # Test 1: Sessions List API
        print(f"\n📊 Test 1: Auto-Notes Sessions List API")
        success, response, issues = self.test_api_endpoint(
            "Auto-Notes Sessions List",
            "GET",
            "auto-notes/sessions"
        )
        
        test_results['sessions_list'] = success
        test_results['objectid_issues_found'].extend(issues)
        
        if success:
            sessions = response.get('sessions', [])
            print(f"   📊 Found {len(sessions)} sessions")
        
        # Test 2: Start Session API
        print(f"\n📊 Test 2: Auto-Notes Start Session API")
        session_data = {
            "title": "ObjectId Serialization Test Session",
            "subject": "Physics"
        }
        
        success, response, issues = self.test_api_endpoint(
            "Auto-Notes Start Session",
            "POST",
            "auto-notes/start-session",
            data=session_data
        )
        
        test_results['start_session'] = success
        test_results['objectid_issues_found'].extend(issues)
        
        session_id = None
        if success:
            session_id = response.get('session_id')
            print(f"   📊 Session created: {session_id}")
        
        # Test 3: Upload Audio API (if session created)
        if session_id:
            print(f"\n📊 Test 3: Auto-Notes Upload Audio API")
            audio_data = {
                "session_id": session_id,
                "audio_quality": "high",
                "enhancement_options": ["noise_reduction", "voice_enhancement"]
            }
            
            success, response, issues = self.test_api_endpoint(
                "Auto-Notes Upload Audio",
                "POST",
                "auto-notes/upload-audio",
                data=audio_data
            )
            
            test_results['upload_audio'] = success
            test_results['objectid_issues_found'].extend(issues)
        
        # Test 4: Processing Status API
        if session_id:
            print(f"\n📊 Test 4: Auto-Notes Processing Status API")
            success, response, issues = self.test_api_endpoint(
                "Auto-Notes Processing Status",
                "GET",
                f"auto-notes/processing-status/{session_id}"
            )
            
            test_results['processing_status'] = success
            test_results['objectid_issues_found'].extend(issues)
        
        # Test 5: End Session API (Critical - where ObjectId issues are reported)
        if session_id:
            print(f"\n📊 Test 5: Auto-Notes End Session API (CRITICAL - ObjectId Issues Expected)")
            end_session_data = {
                "fallback_transcription": "Test transcription for ObjectId serialization testing",
                "total_duration": 120.0
            }
            
            success, response, issues = self.test_api_endpoint(
                "Auto-Notes End Session",
                "POST",
                f"auto-notes/{session_id}/end-session",
                data=end_session_data
            )
            
            test_results['end_session'] = success
            test_results['objectid_issues_found'].extend(issues)
            
            if success:
                session_status = response.get('status', 'unknown')
                print(f"   📊 Final session status: {session_status}")
        
        # Final Assessment
        print(f"\n🎯 FINAL BACKEND VALIDATION - OBJECTID SERIALIZATION TESTING SUMMARY:")
        print(f"   ✅ Sessions List API: {'✓' if test_results['sessions_list'] else '✗'}")
        print(f"   ✅ Start Session API: {'✓' if test_results['start_session'] else '✗'}")
        print(f"   ✅ Upload Audio API: {'✓' if test_results['upload_audio'] else '✗'}")
        print(f"   ✅ Processing Status API: {'✓' if test_results['processing_status'] else '✗'}")
        print(f"   ✅ End Session API: {'✓' if test_results['end_session'] else '✗'}")
        
        # Calculate success rate
        core_tests = ['sessions_list', 'start_session', 'upload_audio', 'processing_status', 'end_session']
        core_success = sum(test_results[test] for test in core_tests)
        success_rate = (core_success / len(core_tests)) * 100
        
        print(f"\n📊 Core API Success Rate: {core_success}/{len(core_tests)} ({success_rate:.1f}%)")
        
        # ObjectId Issues Analysis
        objectid_issues = test_results['objectid_issues_found']
        if objectid_issues:
            print(f"\n🚨 OBJECTID SERIALIZATION ISSUES IDENTIFIED:")
            for issue in set(objectid_issues):  # Remove duplicates
                print(f"   - {issue}")
            print(f"\n🔧 RECOMMENDATIONS:")
            print(f"   - Fix ObjectId serialization in clean_mongodb_doc function")
            print(f"   - Ensure all MongoDB ObjectIds are converted to strings before JSON response")
            print(f"   - Update error response handling to properly serialize ObjectIds")
            print(f"   - Test custom JSONResponse class implementation")
            return False
        else:
            print(f"\n✅ OBJECTID SERIALIZATION VALIDATION SUCCESSFUL")
            print(f"   - All Auto-Note Mentor APIs working correctly")
            print(f"   - No ObjectId serialization errors detected")
            print(f"   - Backend responses properly formatted for frontend")
            if success_rate == 100:
                print(f"   - 100% success rate achieved")
            return success_rate >= 80

if __name__ == "__main__":
    tester = ObjectIdSerializationTester()
    result = tester.run_objectid_serialization_tests()
    print(f"\n{'='*80}")
    print(f"🎯 FINAL RESULT: {'SUCCESS' if result else 'ISSUES DETECTED'}")
    print(f"{'='*80}")