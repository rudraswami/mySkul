#!/usr/bin/env python3
"""
Focused test for Dashboard Analytics API endpoint
Review Request: Test /api/dashboard/analytics endpoint specifically
"""

import requests
import json
import sys
from datetime import datetime

class DashboardAnalyticsTest:
    def __init__(self):
        self.base_url = "https://neurotutor.preview.emergentagent.com/api"
        self.token = None
        self.test_email = "test@dhruvai.com"
        self.test_password = "password123"
    
    def login(self):
        """Login with test credentials"""
        print("🔐 Logging in with test credentials...")
        print(f"   Email: {self.test_email}")
        print(f"   Password: {self.test_password}")
        
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
                    print(f"   ✅ Login successful")
                    print(f"   Token: {self.token[:20]}...")
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
        """Test the dashboard analytics endpoint specifically"""
        if not self.token:
            print("❌ No authentication token available")
            return False
        
        print("\n🎯 TESTING DASHBOARD ANALYTICS ENDPOINT")
        print("=" * 60)
        print("Focus: /api/dashboard/analytics endpoint")
        print("Expected fields: recent_progress, total_study_time, chat_sessions_count, current_streak, weekly_goals_progress")
        print("Goal: Determine if API returns actual data or placeholder values")
        
        try:
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            print(f"\n📡 Making GET request to: {self.base_url}/dashboard/analytics")
            print(f"   Headers: Authorization: Bearer {self.token[:20]}...")
            
            response = requests.get(
                f"{self.base_url}/dashboard/analytics",
                headers=headers,
                timeout=30
            )
            
            print(f"   Response Status: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("   ✅ API returned 200 OK")
                
                try:
                    data = response.json()
                    print(f"\n📊 FULL RESPONSE DATA:")
                    print(json.dumps(data, indent=2))
                    
                    # Check for required fields from review request
                    required_fields = [
                        'recent_progress',
                        'total_study_time', 
                        'chat_sessions_count',
                        'current_streak',
                        'weekly_goals_progress'
                    ]
                    
                    print(f"\n🔍 FIELD ANALYSIS:")
                    present_fields = []
                    missing_fields = []
                    
                    for field in required_fields:
                        if field in data:
                            present_fields.append(field)
                            value = data[field]
                            value_type = type(value).__name__
                            print(f"   ✅ {field}: {value} (type: {value_type})")
                        else:
                            missing_fields.append(field)
                            print(f"   ❌ {field}: MISSING")
                    
                    print(f"\n📈 DATA QUALITY ASSESSMENT:")
                    
                    # Analyze each field for actual vs placeholder data
                    recent_progress = data.get('recent_progress', [])
                    if isinstance(recent_progress, list):
                        if len(recent_progress) > 0:
                            print(f"   ✅ recent_progress: Contains {len(recent_progress)} entries (ACTUAL DATA)")
                            for i, item in enumerate(recent_progress[:3]):
                                print(f"      Entry {i+1}: {item}")
                        else:
                            print(f"   ⚠️  recent_progress: Empty array (PLACEHOLDER)")
                    else:
                        print(f"   ❌ recent_progress: Wrong type - {type(recent_progress)} (INVALID)")
                    
                    total_study_time = data.get('total_study_time', 0)
                    if isinstance(total_study_time, (int, float)):
                        if total_study_time > 0:
                            print(f"   ✅ total_study_time: {total_study_time} minutes (ACTUAL DATA)")
                        else:
                            print(f"   ⚠️  total_study_time: {total_study_time} (PLACEHOLDER/ZERO)")
                    else:
                        print(f"   ❌ total_study_time: Wrong type - {type(total_study_time)} (INVALID)")
                    
                    chat_sessions_count = data.get('chat_sessions_count', 0)
                    if isinstance(chat_sessions_count, int):
                        if chat_sessions_count > 0:
                            print(f"   ✅ chat_sessions_count: {chat_sessions_count} sessions (ACTUAL DATA)")
                        else:
                            print(f"   ⚠️  chat_sessions_count: {chat_sessions_count} (PLACEHOLDER/ZERO)")
                    else:
                        print(f"   ❌ chat_sessions_count: Wrong type - {type(chat_sessions_count)} (INVALID)")
                    
                    current_streak = data.get('current_streak', 0)
                    if isinstance(current_streak, int):
                        if current_streak >= 0:
                            print(f"   ✅ current_streak: {current_streak} days (VALID)")
                        else:
                            print(f"   ❌ current_streak: {current_streak} (INVALID - negative)")
                    else:
                        print(f"   ❌ current_streak: Wrong type - {type(current_streak)} (INVALID)")
                    
                    weekly_goals_progress = data.get('weekly_goals_progress', 0)
                    if isinstance(weekly_goals_progress, (int, float)):
                        if 0 <= weekly_goals_progress <= 100:
                            print(f"   ✅ weekly_goals_progress: {weekly_goals_progress}% (VALID)")
                        else:
                            print(f"   ⚠️  weekly_goals_progress: {weekly_goals_progress}% (OUT OF RANGE)")
                    else:
                        print(f"   ❌ weekly_goals_progress: Wrong type - {type(weekly_goals_progress)} (INVALID)")
                    
                    # Final conclusion
                    print(f"\n🎯 REVIEW REQUEST CONCLUSION:")
                    print("=" * 40)
                    
                    has_actual_data = (
                        (isinstance(recent_progress, list) and len(recent_progress) > 0) or
                        (isinstance(total_study_time, (int, float)) and total_study_time > 0) or
                        (isinstance(chat_sessions_count, int) and chat_sessions_count > 0)
                    )
                    
                    all_fields_present = len(missing_fields) == 0
                    valid_structure = all_fields_present and isinstance(data, dict)
                    
                    if valid_structure and has_actual_data:
                        print("   ✅ RESULT: API returns ACTUAL DATABASE DATA")
                        print("   ✅ Dashboard should display real user data, not placeholders")
                        print("   ✅ Data loading issue is NOT caused by backend API failure")
                    elif valid_structure and not has_actual_data:
                        print("   ⚠️  RESULT: API returns VALID STRUCTURE but PLACEHOLDER VALUES")
                        print("   ⚠️  Dashboard shows placeholders because user has no activity data")
                        print("   ⚠️  This is expected behavior for new/inactive users")
                    elif not valid_structure:
                        print("   ❌ RESULT: API returns INVALID STRUCTURE")
                        print("   ❌ Dashboard loading issue IS caused by backend API problems")
                        print(f"   ❌ Missing fields: {missing_fields}")
                    else:
                        print("   ❓ RESULT: UNCLEAR - Mixed data quality")
                    
                    return True
                    
                except json.JSONDecodeError as e:
                    print(f"   ❌ Invalid JSON response: {e}")
                    print(f"   Raw response: {response.text}")
                    return False
                    
            else:
                print(f"   ❌ API request failed with status {response.status_code}")
                print(f"   Error response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Request error: {str(e)}")
            return False
    
    def run_test(self):
        """Run the complete test"""
        print("🚀 DASHBOARD ANALYTICS API TEST")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Target URL: {self.base_url}")
        
        # Step 1: Login
        if not self.login():
            print("\n❌ TEST FAILED: Could not authenticate")
            return False
        
        # Step 2: Test dashboard analytics
        if not self.test_dashboard_analytics():
            print("\n❌ TEST FAILED: Dashboard analytics endpoint failed")
            return False
        
        print("\n✅ TEST COMPLETED SUCCESSFULLY")
        return True

if __name__ == "__main__":
    tester = DashboardAnalyticsTest()
    success = tester.run_test()
    sys.exit(0 if success else 1)