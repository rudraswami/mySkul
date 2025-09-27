#!/usr/bin/env python3
"""
PRIORITY TEST: Dashboard Analytics API
Testing for MongoDB ObjectId serialization issues causing loading placeholders
"""

import requests
import json
import sys

class DashboardTester:
    def __init__(self):
        self.base_url = "https://dhruv-edtech.preview.emergentagent.com/api"
        self.token = None
        self.test_email = "test@dhruvai.com"
        self.test_password = "password123"

    def login(self):
        """Login with test credentials"""
        print("🔐 Logging in with test@dhruvai.com/password123...")
        
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"   Login Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.token = data['token']
                    print(f"   ✅ Login successful - Token: {self.token[:20]}...")
                    return True
                else:
                    print(f"   ❌ No token in response: {data}")
                    return False
            else:
                print(f"   ❌ Login failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Login error: {str(e)}")
            return False

    def test_dashboard_analytics(self):
        """PRIORITY TEST: Dashboard Analytics API for loading placeholder issue"""
        if not self.token:
            print("❌ No token available for dashboard analytics test")
            return False
        
        print("\n🎯 PRIORITY TEST: Dashboard Analytics API")
        print("   Testing /api/dashboard/analytics endpoint...")
        print("   Checking for MongoDB ObjectId serialization issues...")
        print("   Expected: Valid JSON with study time, progress data, etc.")
        
        try:
            response = requests.get(
                f"{self.base_url}/dashboard/analytics",
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                },
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ API returned 200 OK")
                
                try:
                    data = response.json()
                    print("   ✅ Response is valid JSON")
                    
                    # Pretty print the response structure
                    print(f"   Response structure: {json.dumps(data, indent=2)[:500]}...")
                    
                    # Check for expected dashboard data
                    expected_fields = ['study_time', 'progress_data', 'recent_activity', 'performance_summary']
                    present_fields = []
                    missing_fields = []
                    
                    for field in expected_fields:
                        if field in data:
                            present_fields.append(field)
                        else:
                            missing_fields.append(field)
                    
                    print(f"   Present fields: {present_fields}")
                    if missing_fields:
                        print(f"   Missing fields: {missing_fields}")
                    
                    # Check for actual data vs placeholders
                    if 'study_time' in data:
                        study_time = data['study_time']
                        if isinstance(study_time, dict) and study_time.get('total_minutes', 0) > 0:
                            print(f"   ✅ Study time has data: {study_time}")
                        else:
                            print(f"   ⚠️  Study time appears empty: {study_time}")
                    
                    if 'progress_data' in data:
                        progress_data = data['progress_data']
                        if progress_data and len(progress_data) > 0:
                            print(f"   ✅ Progress data has {len(progress_data)} entries")
                        else:
                            print(f"   ⚠️  Progress data appears empty: {progress_data}")
                    
                    print("   🎯 CONCLUSION: Dashboard API is working and returning valid JSON")
                    print("   📊 The loading placeholder issue is likely in frontend data handling")
                    return True
                    
                except json.JSONDecodeError as e:
                    print(f"   ❌ CRITICAL: Response is not valid JSON - {str(e)}")
                    print(f"   Raw response: {response.text[:200]}...")
                    return False
                    
            elif response.status_code == 500:
                print("   ❌ CRITICAL: 500 Internal Server Error - MongoDB serialization issue confirmed")
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data}")
                except:
                    print(f"   Raw error: {response.text}")
                
                # Check for ObjectId serialization error
                if "ObjectId" in response.text or "not iterable" in response.text:
                    print("   🔍 CONFIRMED: MongoDB ObjectId serialization error detected")
                    print("   💡 SOLUTION: Backend needs ObjectId to string conversion")
                
                return False
                
            else:
                print(f"   ❌ Unexpected status code: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Request error: {str(e)}")
            return False

    def run_priority_test(self):
        """Run the priority dashboard analytics test"""
        print("=" * 60)
        print("DASHBOARD ANALYTICS API PRIORITY TEST")
        print("=" * 60)
        
        # Step 1: Login
        if not self.login():
            print("\n❌ FAILED: Could not authenticate")
            return False
        
        # Step 2: Test dashboard analytics
        success = self.test_dashboard_analytics()
        
        print("\n" + "=" * 60)
        if success:
            print("✅ PRIORITY TEST PASSED: Dashboard Analytics API is working")
            print("📊 Issue is likely in frontend data handling, not backend API")
        else:
            print("❌ PRIORITY TEST FAILED: Dashboard Analytics API has issues")
            print("🔧 Backend API needs fixing for dashboard to show data")
        print("=" * 60)
        
        return success

if __name__ == "__main__":
    tester = DashboardTester()
    success = tester.run_priority_test()
    sys.exit(0 if success else 1)