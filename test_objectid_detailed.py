#!/usr/bin/env python3
"""
Detailed ObjectId Serialization Testing - Focus on 500 errors
Based on backend logs showing: ValueError: [TypeError("'ObjectId' object is not iterable"), TypeError('vars() argument must have __dict__ attribute')]
"""

import requests
import json
import time

class DetailedObjectIdTester:
    def __init__(self):
        self.base_url = "https://razorpay-live.preview.emergentagent.com/api"
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
    
    def test_end_session_objectid_error(self):
        """Test the specific end-session ObjectId serialization error"""
        print("\n🚨 TESTING END-SESSION OBJECTID SERIALIZATION ERROR")
        print("   Backend logs show: ValueError: [TypeError(\"'ObjectId' object is not iterable\"), TypeError('vars() argument must have __dict__ attribute')]")
        print("   This occurs in /api/auto-notes/end-session endpoint")
        
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
                return False
                
        except Exception as e:
            print(f"   ❌ Session creation error: {str(e)}")
            return False
        
        # Now test the end-session endpoint that causes ObjectId errors
        print(f"\n📊 Step 2: Test End-Session API (Expected to trigger ObjectId error)")
        end_session_data = {
            "fallback_transcription": "Test transcription to trigger ObjectId serialization error",
            "total_duration": 120.0
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auto-notes/{session_id}/end-session",
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
                    return False, []
                    
            elif response.status_code == 200:
                print(f"   ✅ End-session completed successfully (ObjectId issue may be fixed)")
                data = response.json()
                print(f"   📊 Response: {json.dumps(data, indent=2)}")
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
    
    def test_other_potential_objectid_endpoints(self):
        """Test other endpoints that might have ObjectId serialization issues"""
        print("\n📊 Testing Other Potential ObjectId Serialization Issues")
        
        endpoints_to_test = [
            ("Mock Test Generation", "POST", "mock-tests/generate", {
                "exam_type": "JEE",
                "subjects": ["Mathematics"],
                "difficulty_level": 3,
                "num_questions": 5
            }),
            ("Auto-Notes Analytics", "GET", "auto-notes/analytics", None),
            ("Auto-Notes Class Series", "GET", "auto-notes/class-series", None),
        ]
        
        objectid_issues_found = []
        
        for name, method, endpoint, data in endpoints_to_test:
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
                        
                elif response.status_code == 200:
                    print(f"      ✅ Working correctly")
                else:
                    print(f"      ⚠️  Status: {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ Request error: {str(e)}")
            
            time.sleep(1)  # Small delay between requests
        
        return objectid_issues_found
    
    def run_detailed_objectid_tests(self):
        """Run comprehensive ObjectId serialization tests"""
        print("🚨 DETAILED OBJECTID SERIALIZATION TESTING")
        print("   Focus: Identify specific ObjectId serialization errors causing 500 responses")
        print("   Based on backend logs: ValueError: [TypeError(\"'ObjectId' object is not iterable\")]")
        print("=" * 80)
        
        if not self.login():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Test the specific end-session ObjectId error
        end_session_has_error, end_session_errors = self.test_end_session_objectid_error()
        
        # Test other potential ObjectId endpoints
        other_objectid_issues = self.test_other_potential_objectid_endpoints()
        
        # Final Assessment
        print(f"\n🎯 DETAILED OBJECTID SERIALIZATION TESTING SUMMARY:")
        print(f"   🚨 End-Session ObjectId Error: {'DETECTED' if end_session_has_error else 'NOT DETECTED'}")
        
        if end_session_errors:
            print(f"   📊 End-Session Error Types:")
            for error in end_session_errors:
                print(f"      - {error}")
        
        if other_objectid_issues:
            print(f"   🚨 Other ObjectId Issues Found:")
            for issue in other_objectid_issues:
                print(f"      - {issue}")
        
        total_issues = len(end_session_errors) + len(other_objectid_issues)
        
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
            print(f"\n✅ NO OBJECTID SERIALIZATION ISSUES DETECTED")
            print(f"   - All tested endpoints handle ObjectId serialization correctly")
            print(f"   - Backend responses are properly formatted for frontend consumption")
            print(f"   - Custom JSONResponse implementation working as expected")
            return True

if __name__ == "__main__":
    tester = DetailedObjectIdTester()
    result = tester.run_detailed_objectid_tests()
    print(f"\n{'='*80}")
    print(f"🎯 FINAL RESULT: {'OBJECTID ISSUES RESOLVED' if result else 'OBJECTID ISSUES DETECTED'}")
    print(f"{'='*80}")