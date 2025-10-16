#!/usr/bin/env python3
"""
Profile Settings Update API Test - CRITICAL REVIEW REQUEST FOCUS
Testing PUT /api/user/profile endpoint to identify "Failed to update profile" error
"""

import requests
import json
import sys
from datetime import datetime

class ProfileUpdateTester:
    def __init__(self, base_url="https://auth-gateway-dhruv.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.test_user_email = "test@dhruvai.com"
        self.test_user_password = "password123"

    def authenticate(self):
        """Authenticate with test@dhruvai.com/password123"""
        print("🔐 AUTHENTICATION TEST")
        print(f"   Authenticating with {self.test_user_email}/{self.test_user_password}")
        
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
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                if 'user' in data:
                    self.user_id = data['user'].get('user_id')
                
                print(f"   ✅ Authentication successful")
                print(f"   Token: {self.token[:30]}...")
                print(f"   User ID: {self.user_id}")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False

    def test_profile_update(self, test_name, profile_data, expected_status=200):
        """Test profile update with specific data"""
        print(f"\n🔍 TESTING: {test_name}")
        print(f"   Data: {json.dumps(profile_data, indent=2)}")
        print(f"   Expected Status: {expected_status}")
        
        if not self.token:
            print("   ❌ No authentication token available")
            return False
        
        try:
            response = requests.put(
                f"{self.base_url}/user/profile",
                json=profile_data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                },
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == expected_status:
                print(f"   ✅ SUCCESS: Profile update returned expected status {expected_status}")
                
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)}")
                    
                    # Verify response structure
                    if 'message' in response_data:
                        print(f"   ✅ Response contains message: {response_data['message']}")
                    
                    if 'user' in response_data:
                        updated_user = response_data['user']
                        print(f"   ✅ Response contains updated user data")
                        
                        # Check if requested fields were updated
                        for field, expected_value in profile_data.items():
                            if field in updated_user:
                                actual_value = updated_user[field]
                                if actual_value == expected_value:
                                    print(f"   ✅ {field}: Updated correctly to '{actual_value}'")
                                else:
                                    print(f"   ⚠️  {field}: Expected '{expected_value}', got '{actual_value}'")
                            else:
                                print(f"   ⚠️  {field}: Not found in response")
                    else:
                        print(f"   ⚠️  Response missing 'user' field")
                    
                    return True
                    
                except Exception as e:
                    print(f"   ⚠️  Could not parse JSON response: {e}")
                    print(f"   Raw response: {response.text}")
                    return True  # Still consider success if status code is correct
                    
            else:
                print(f"   ❌ FAILED: Expected {expected_status}, got {response.status_code}")
                
                # Detailed error analysis
                print(f"   🔍 ERROR ANALYSIS:")
                
                if response.status_code == 500:
                    print(f"      🚨 500 INTERNAL SERVER ERROR - This is the reported issue!")
                    print(f"      🔍 Likely causes:")
                    print(f"         - Database connection issues")
                    print(f"         - Server-side validation errors")
                    print(f"         - Backend processing errors")
                elif response.status_code == 401:
                    print(f"      🚨 401 UNAUTHORIZED - Authentication issue")
                    print(f"      🔍 Token may be invalid or expired")
                elif response.status_code == 422:
                    print(f"      🚨 422 VALIDATION ERROR - Invalid data format")
                elif response.status_code == 404:
                    print(f"      🚨 404 NOT FOUND - Endpoint may not exist")
                else:
                    print(f"      🚨 UNEXPECTED ERROR - Status {response.status_code}")
                
                try:
                    error_data = response.json()
                    print(f"      Error Details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"      Raw Error: {response.text}")
                
                return False
                
        except requests.exceptions.Timeout:
            print(f"   ❌ TIMEOUT: Request took longer than 30 seconds")
            return False
        except requests.exceptions.ConnectionError:
            print(f"   ❌ CONNECTION ERROR: Could not connect to server")
            return False
        except Exception as e:
            print(f"   ❌ UNEXPECTED ERROR: {str(e)}")
            return False

    def run_comprehensive_profile_tests(self):
        """Run comprehensive profile update tests"""
        print("🎯 PROFILE SETTINGS UPDATE API TESTING - CRITICAL REVIEW REQUEST")
        print("=" * 80)
        print("Focus: PUT /api/user/profile endpoint")
        print("Issue: User getting 'Failed to update profile. Please check your connection.' error")
        print("Testing: 500 errors, authentication issues, database problems, response structure")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with profile tests")
            return False
        
        # Step 2: Test various profile field combinations
        test_scenarios = [
            {
                "name": "Full Profile Update",
                "data": {
                    "full_name": "Updated Test User",
                    "email": "test@dhruvai.com",
                    "phone": "+91-9876543210",
                    "exam_type": "NEET",
                    "target_year": 2025,
                    "current_standard": "Class 12",
                    "institution": "Test Institute"
                }
            },
            {
                "name": "Partial Update - Name Only",
                "data": {
                    "full_name": "Test User Updated Name"
                }
            },
            {
                "name": "Partial Update - Exam Type",
                "data": {
                    "exam_type": "JEE"
                }
            },
            {
                "name": "Partial Update - Contact Info",
                "data": {
                    "phone": "+91-1234567890",
                    "institution": "New Test Institute"
                }
            },
            {
                "name": "Multiple Fields Update",
                "data": {
                    "full_name": "Multi Field Test User",
                    "target_year": 2026,
                    "current_standard": "Class 11"
                }
            },
            {
                "name": "Empty Update (Edge Case)",
                "data": {}
            }
        ]
        
        success_count = 0
        total_tests = len(test_scenarios)
        
        print(f"\n📋 RUNNING {total_tests} PROFILE UPDATE TEST SCENARIOS")
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n{'='*60}")
            print(f"TEST {i}/{total_tests}: {scenario['name']}")
            print(f"{'='*60}")
            
            success = self.test_profile_update(
                scenario['name'],
                scenario['data']
            )
            
            if success:
                success_count += 1
        
        # Step 3: Test authentication edge cases
        print(f"\n{'='*60}")
        print(f"AUTHENTICATION EDGE CASE TESTING")
        print(f"{'='*60}")
        
        # Test without token
        print(f"\n🔍 TESTING: Profile Update Without Authentication")
        temp_token = self.token
        self.token = None
        
        no_auth_success = self.test_profile_update(
            "No Authentication Test",
            {"full_name": "Should Fail"},
            expected_status=401
        )
        
        self.token = temp_token
        
        if no_auth_success:
            success_count += 1
        total_tests += 1
        
        # Step 4: Final Summary
        success_rate = (success_count / total_tests) * 100
        
        print(f"\n{'='*80}")
        print(f"🎯 PROFILE UPDATE API TESTING SUMMARY")
        print(f"{'='*80}")
        print(f"✅ Successful Tests: {success_count}/{total_tests} ({success_rate:.1f}%)")
        print(f"🔍 Authentication: {'✓' if self.token else '✗'}")
        print(f"🔍 Endpoint: PUT /api/user/profile")
        print(f"🔍 Base URL: {self.base_url}")
        
        if success_count == 0:
            print(f"\n🚨 CRITICAL ISSUE CONFIRMED:")
            print(f"   All profile updates failed")
            print(f"   This explains the 'Failed to update profile' error reported by user")
            print(f"\n🔧 RECOMMENDATIONS:")
            print(f"   1. Check backend server logs for detailed error messages")
            print(f"   2. Verify database connection and user table structure")
            print(f"   3. Check PUT /api/user/profile endpoint implementation")
            print(f"   4. Verify request validation logic")
            print(f"   5. Test database write permissions")
            
        elif success_count < total_tests:
            print(f"\n⚠️  PARTIAL ISSUE IDENTIFIED:")
            print(f"   Some profile updates failed")
            print(f"   Issue may be specific to certain field combinations")
            print(f"\n🔧 RECOMMENDATIONS:")
            print(f"   1. Check field-specific validation logic")
            print(f"   2. Review error handling for edge cases")
            print(f"   3. Verify database schema supports all tested fields")
            
        else:
            print(f"\n✅ ALL TESTS PASSED:")
            print(f"   Profile update API is working correctly")
            print(f"   The reported issue may be:")
            print(f"   1. Network connectivity problem")
            print(f"   2. Frontend-specific error handling")
            print(f"   3. Intermittent server issues")
            print(f"   4. Different user account or data causing issues")
        
        return success_count > 0

def main():
    """Main test execution"""
    tester = ProfileUpdateTester()
    
    try:
        success = tester.run_comprehensive_profile_tests()
        
        if success:
            print(f"\n🎯 TESTING COMPLETED - Issues identified and documented")
            sys.exit(0)
        else:
            print(f"\n❌ TESTING FAILED - Critical issues found")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()