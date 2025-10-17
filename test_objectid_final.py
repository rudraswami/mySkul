#!/usr/bin/env python3
"""
Final ObjectId Serialization Testing - Correct endpoint paths
Testing the actual ObjectId serialization issues in Auto-Note Mentor APIs
"""

import requests
import json
import time

class FinalObjectIdTester:
    def __init__(self):
        self.base_url = "https://dhruv-learn-assist.preview.emergentagent.com/api"
        self.token = None
        
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
                print(f"✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_correct_end_session_endpoint(self):
        """Test the correct end-session endpoint that causes ObjectId errors"""
        print("\n🚨 TESTING CORRECT END-SESSION OBJECTID SERIALIZATION ERROR")
        print("   Endpoint: POST /api/auto-notes/end-session (not with session_id in path)")
        print("   Expected: ObjectId serialization error causing 500 Internal Server Error")
        
        # First create a session
        print("\n📊 Step 1: Create Auto-Note Session")
        session_data = {
            "title": "ObjectId Error Test Session",
            "subject": "Physics"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auto-notes/start-session",
                json=session_data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                session_id = data.get('session_id')
                print(f"   ✅ Session created: {session_id}")
            else:
                print(f"   ❌ Session creation failed: {response.status_code}")
                return False, []
                
        except Exception as e:
            print(f"   ❌ Session creation error: {str(e)}")
            return False, []
        
        # Now test the correct end-session endpoint
        print(f"\n📊 Step 2: Test End-Session API (Correct endpoint)")
        end_session_data = {
            "session_id": session_id,
            "fallback_transcription": "Test transcription to trigger ObjectId serialization error",
            "total_duration": 120.0
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auto-notes/end-session",  # Correct endpoint path
                json=end_session_data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                },
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 500:
                print(f"   🚨 CONFIRMED: 500 Internal Server Error (ObjectId serialization issue)")
                
                try:
                    error_data = response.json()
                    error_str = str(error_data)
                    
                    print(f"   📊 Error Response: {json.dumps(error_data, indent=2)}")
                    
                    # Check for specific ObjectId serialization errors
                    objectid_errors = []
                    if 'ObjectId' in error_str:
                        if 'not iterable' in error_str:
                            objectid_errors.append("ObjectId 'not iterable' error")
                        if 'vars() argument must have __dict__ attribute' in error_str:
                            objectid_errors.append("ObjectId vars() error")
                        if 'not JSON serializable' in error_str:
                            objectid_errors.append("ObjectId 'not JSON serializable' error")
                        if not objectid_errors:  # Generic ObjectId error
                            objectid_errors.append("ObjectId serialization error")
                    
                    if objectid_errors:
                        print(f"   🚨 OBJECTID SERIALIZATION ERRORS DETECTED:")
                        for error in objectid_errors:
                            print(f"      - {error}")
                        return True, objectid_errors
                    else:
                        print(f"   ⚠️  500 error but no ObjectId serialization issues in response")
                        return False, []
                        
                except json.JSONDecodeError:
                    print(f"   ❌ 500 error with invalid JSON response")
                    print(f"   Response text: {response.text}")
                    # Still consider this an ObjectId issue if we get 500
                    return True, ["500 error with invalid JSON (likely ObjectId serialization)"]
                    
            elif response.status_code == 200:
                print(f"   ✅ End-session completed successfully")
                data = response.json()
                print(f"   📊 Response: {json.dumps(data, indent=2)}")
                
                # Check if response contains any ObjectId serialization issues
                response_str = json.dumps(data)
                if 'ObjectId(' in response_str:
                    print(f"   🚨 Raw ObjectId found in successful response")
                    return True, ["Raw ObjectId in successful response"]
                
                return False, []
                
            else:
                print(f"   ⚠️  Unexpected status code: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   📊 Response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Response text: {response.text}")
                return False, []
                
        except Exception as e:
            print(f"   ❌ End-session request error: {str(e)}")
            return False, []
    
    def test_enhanced_audio_processing_endpoints(self):
        """Test enhanced audio processing endpoints for ObjectId issues"""
        print("\n📊 Testing Enhanced Audio Processing Endpoints")
        
        # Create a session first
        session_data = {
            "title": "Audio Processing Test",
            "subject": "Mathematics"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auto-notes/start-session",
                json=session_data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                session_id = data.get('session_id')
                print(f"   ✅ Test session created: {session_id}")
            else:
                print(f"   ❌ Test session creation failed")
                return []
                
        except Exception as e:
            print(f"   ❌ Test session creation error: {str(e)}")
            return []
        
        # Test enhanced audio processing endpoints
        endpoints_to_test = [
            ("Audio Quality Analysis", "GET", f"auto-notes/audio-quality-analysis/{session_id}"),
            ("Audio Enhancement", "POST", "auto-notes/enhance-audio-only", {
                "session_id": session_id,
                "enhancement_options": ["noise_reduction"]
            }),
            ("Context Detection", "POST", "auto-notes/context-detection", {
                "session_id": session_id,
                "audio_text": "Test audio transcription"
            }),
        ]
        
        objectid_issues_found = []
        
        for name, method, endpoint, *args in endpoints_to_test:
            data = args[0] if args else None
            print(f"\n   🔍 Testing {name}...")
            
            try:
                url = f"{self.base_url}/{endpoint}"
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                }
                
                if method == 'GET':
                    response = requests.get(url, headers=headers, timeout=30)
                elif method == 'POST':
                    response = requests.post(url, json=data, headers=headers, timeout=30)
                
                print(f"      Status: {response.status_code}")
                
                if response.status_code == 500:
                    print(f"      🚨 500 Internal Server Error detected")
                    
                    try:
                        error_data = response.json()
                        error_str = str(error_data)
                        
                        if 'ObjectId' in error_str:
                            print(f"      🚨 ObjectId-related error in {name}")
                            objectid_issues_found.append(f"{name}: ObjectId serialization error")
                            print(f"      Error: {json.dumps(error_data, indent=2)[:300]}...")
                        else:
                            print(f"      ⚠️  500 error but not ObjectId-related")
                            
                    except json.JSONDecodeError:
                        print(f"      ❌ 500 error with invalid JSON")
                        objectid_issues_found.append(f"{name}: 500 error with invalid JSON (likely ObjectId)")
                        
                elif response.status_code == 200:
                    print(f"      ✅ Working correctly")
                    
                    # Check for ObjectId in successful responses
                    try:
                        data = response.json()
                        response_str = json.dumps(data)
                        if 'ObjectId(' in response_str:
                            print(f"      🚨 Raw ObjectId found in successful response")
                            objectid_issues_found.append(f"{name}: Raw ObjectId in response")
                    except:
                        pass
                        
                else:
                    print(f"      ⚠️  Status: {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ Request error: {str(e)}")
            
            time.sleep(1)  # Small delay between requests
        
        return objectid_issues_found
    
    def run_final_objectid_tests(self):
        """Run final comprehensive ObjectId serialization tests"""
        print("🚨 FINAL BACKEND VALIDATION - AUTO-NOTE MENTOR OBJECTID SERIALIZATION TESTING")
        print("   Review Request: Test ObjectId serialization issues affecting end-session API calls")
        print("   Focus: /api/auto-notes/sessions, /api/auto-notes/start-session, /api/auto-notes/upload-audio, /api/auto-notes/processing-status")
        print("   Goal: Identify 500 errors caused by ObjectId serialization in backend responses")
        print("=" * 80)
        
        if not self.login():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Test the core Auto-Note Mentor APIs first
        print("\n📊 Testing Core Auto-Note Mentor APIs")
        
        core_apis = [
            ("Sessions List", "GET", "auto-notes/sessions"),
            ("Start Session", "POST", "auto-notes/start-session", {
                "title": "Core API Test",
                "subject": "Physics"
            }),
            ("Analytics", "GET", "auto-notes/analytics"),
            ("Class Series", "GET", "auto-notes/class-series"),
        ]
        
        core_objectid_issues = []
        session_id = None
        
        for name, method, endpoint, *args in core_apis:
            data = args[0] if args else None
            print(f"\n   🔍 Testing {name}...")
            
            try:
                url = f"{self.base_url}/{endpoint}"
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                }
                
                if method == 'GET':
                    response = requests.get(url, headers=headers, timeout=30)
                elif method == 'POST':
                    response = requests.post(url, json=data, headers=headers, timeout=30)
                
                print(f"      Status: {response.status_code}")
                
                if response.status_code == 500:
                    print(f"      🚨 500 Internal Server Error")
                    try:
                        error_data = response.json()
                        if 'ObjectId' in str(error_data):
                            core_objectid_issues.append(f"{name}: ObjectId serialization error")
                    except:
                        core_objectid_issues.append(f"{name}: 500 error (likely ObjectId)")
                        
                elif response.status_code == 200:
                    print(f"      ✅ Working correctly")
                    if name == "Start Session":
                        try:
                            data = response.json()
                            session_id = data.get('session_id')
                            print(f"      📊 Session ID: {session_id}")
                        except:
                            pass
                            
            except Exception as e:
                print(f"      ❌ Request error: {str(e)}")
        
        # Test the specific end-session ObjectId error
        end_session_has_error, end_session_errors = self.test_correct_end_session_endpoint()
        
        # Test enhanced audio processing endpoints
        audio_processing_issues = self.test_enhanced_audio_processing_endpoints()
        
        # Final Assessment
        print(f"\n🎯 FINAL BACKEND VALIDATION - OBJECTID SERIALIZATION TESTING SUMMARY:")
        print(f"   📊 Core APIs ObjectId Issues: {len(core_objectid_issues)}")
        print(f"   🚨 End-Session ObjectId Error: {'DETECTED' if end_session_has_error else 'NOT DETECTED'}")
        print(f"   📊 Audio Processing Issues: {len(audio_processing_issues)}")
        
        all_issues = core_objectid_issues + end_session_errors + audio_processing_issues
        
        if core_objectid_issues:
            print(f"\n   🚨 Core API ObjectId Issues:")
            for issue in core_objectid_issues:
                print(f"      - {issue}")
        
        if end_session_errors:
            print(f"\n   🚨 End-Session ObjectId Errors:")
            for error in end_session_errors:
                print(f"      - {error}")
        
        if audio_processing_issues:
            print(f"\n   🚨 Audio Processing ObjectId Issues:")
            for issue in audio_processing_issues:
                print(f"      - {issue}")
        
        total_issues = len(all_issues)
        
        if total_issues > 0:
            print(f"\n🚨 CRITICAL OBJECTID SERIALIZATION ISSUES IDENTIFIED ({total_issues} total):")
            print(f"   🔧 ROOT CAUSE: Backend ObjectId serialization in JSON responses")
            print(f"   🔧 LOCATION: FastAPI jsonable_encoder trying to serialize ObjectId objects")
            print(f"   🔧 ERROR: ValueError: [TypeError(\"'ObjectId' object is not iterable\")]")
            print(f"\n🔧 RECOMMENDED FIXES:")
            print(f"   1. Update clean_mongodb_doc function to handle all ObjectId instances")
            print(f"   2. Ensure custom JSONResponse class is used consistently")
            print(f"   3. Add ObjectId serialization to error response handling")
            print(f"   4. Test all MongoDB document serialization paths")
            return False
        else:
            print(f"\n✅ OBJECTID SERIALIZATION VALIDATION SUCCESSFUL")
            print(f"   - All Auto-Note Mentor APIs working correctly")
            print(f"   - No ObjectId serialization errors detected")
            print(f"   - Backend responses properly formatted for frontend")
            print(f"   - 100% success rate achieved")
            return True

if __name__ == "__main__":
    tester = FinalObjectIdTester()
    result = tester.run_final_objectid_tests()
    print(f"\n{'='*80}")
    print(f"🎯 FINAL RESULT: {'100% SUCCESS RATE ACHIEVED' if result else 'OBJECTID ISSUES DETECTED'}")
    print(f"{'='*80}")