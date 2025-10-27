#!/usr/bin/env python3

import requests
import json
import time

class FreshUserSubscriptionTester:
    def __init__(self):
        self.base_url = "https://eduai-platform-28.preview.emergentagent.com/api"
        self.token = None
        self.user_id = None
        self.fresh_email = f"subscription_test_{int(time.time())}@dhruvai.com"
        
    def create_fresh_user(self):
        """Create a fresh user for testing FREE plan limits"""
        print("🔐 CREATING FRESH FREE USER FOR TESTING")
        
        registration_data = {
            "full_name": "Subscription Test User",
            "email": self.fresh_email,
            "password": "password123",
            "exam_type": "JEE",
            "grade": "Class 12",
            "target_year": 2026
        }
        
        print(f"   Creating user: {self.fresh_email}")
        
        response = requests.post(f"{self.base_url}/auth/register", json=registration_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('token')
            user_data = data.get('user', {})
            self.user_id = user_data.get('user_id')
            print(f"   ✅ Fresh user created successfully: {user_data.get('email')}")
            print(f"   ✅ Token obtained: {self.token[:20]}...")
            return True
        else:
            print(f"   ❌ User creation failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
    
    def test_subscription_info(self):
        """Test GET /api/subscription/info endpoint"""
        print("\n2️⃣ SUBSCRIPTION INFO ENDPOINT VALIDATION")
        print("   Testing GET /api/subscription/info endpoint")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(f"{self.base_url}/subscription/info", headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Subscription info endpoint working")
            
            subscription_tier = data.get('subscription_tier')
            plan_info = data.get('plan_info', {})
            features = plan_info.get('features', {})
            display_name = plan_info.get('display_name')
            
            print(f"   📊 Subscription Info Response:")
            print(f"      subscription_tier: {subscription_tier}")
            print(f"      display_name: {display_name}")
            print(f"      ai_sessions_monthly: {features.get('ai_sessions_monthly')}")
            print(f"      mock_tests_weekly: {features.get('mock_tests_weekly')}")
            print(f"      auto_note_uploads_daily: {features.get('auto_note_uploads_daily')}")
            
            # Validate expected values for Free plan
            expected_values = {
                'subscription_tier': 'FREE',
                'ai_sessions_monthly': 10,
                'mock_tests_weekly': 1,
                'auto_note_uploads_daily': 1,
                'display_name': '🆓 Free - Try Before You Commit'
            }
            
            validation_results = []
            for key, expected_value in expected_values.items():
                if key == 'subscription_tier':
                    actual_value = subscription_tier
                elif key == 'display_name':
                    actual_value = display_name
                else:
                    actual_value = features.get(key)
                
                if actual_value == expected_value:
                    print(f"   ✅ {key}: {actual_value} (matches expected)")
                    validation_results.append(True)
                else:
                    print(f"   ❌ {key}: {actual_value} (expected {expected_value})")
                    validation_results.append(False)
            
            return all(validation_results)
        else:
            print(f"   ❌ Subscription info endpoint failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
    
    def test_feature_access_check(self, feature_name):
        """Test feature access check"""
        print(f"   📊 Testing feature access: {feature_name}")
        
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        data = {"feature_name": feature_name}
        
        response = requests.post(f"{self.base_url}/subscription/check-access", 
                               json=data, headers=headers, timeout=30)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code in [200, 402]:
            response_data = response.json()
            has_access = response_data.get('has_access')
            used = response_data.get('used', 0)
            limit = response_data.get('limit', 0)
            remaining = response_data.get('remaining', 0)
            upgrade_needed = response_data.get('upgrade_needed', False)
            
            print(f"   📊 Response: has_access={has_access}, used={used}, limit={limit}, remaining={remaining}, upgrade_needed={upgrade_needed}")
            
            if response.status_code == 402:
                upsell_info = response_data.get('upsell_info', {})
                print(f"   📊 Upsell info present: {bool(upsell_info)}")
                if upsell_info:
                    print(f"      mentor_message: {bool(upsell_info.get('mentor_message'))}")
                    print(f"      professor_message: {bool(upsell_info.get('professor_message'))}")
                    print(f"      target_plan: {upsell_info.get('target_plan')}")
                    print(f"      growth_stats: {bool(upsell_info.get('growth_stats'))}")
            
            return True, response_data, response.status_code
        else:
            print(f"   ❌ Feature access check failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False, {}, response.status_code
    
    def test_track_usage(self, feature_name):
        """Test usage tracking"""
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        data = {"feature_name": feature_name}
        
        response = requests.post(f"{self.base_url}/subscription/track-usage", 
                               json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return True
        else:
            print(f"   ❌ Usage tracking failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
    
    def test_ai_sessions_monthly_limit(self):
        """Test AI Sessions Monthly Limit (Free: 10 sessions)"""
        print("\n3️⃣ SCENARIO 1: FREE PLAN - AI SESSIONS MONTHLY LIMIT")
        print("   Testing AI Sessions Monthly Limit enforcement")
        
        feature_name = "ai_sessions_monthly"
        
        # Step 1: Check initial access
        print("   📊 Step 1: Check initial access to ai_sessions_monthly")
        success, response, status_code = self.test_feature_access_check(feature_name)
        
        if not success:
            print("   ❌ Initial access check failed")
            return False
        
        limit = response.get('limit', 0)
        used = response.get('used', 0)
        has_access = response.get('has_access')
        remaining = response.get('remaining', 0)
        
        print(f"   📊 Initial Status: has_access={has_access}, used={used}, limit={limit}, remaining={remaining}")
        
        if limit != 10:
            print(f"   ❌ Expected limit=10, got limit={limit}")
            return False
        
        if not has_access:
            print("   ❌ Expected initial access to be True")
            return False
        
        if remaining != 10:
            print(f"   ❌ Expected remaining=10, got remaining={remaining}")
            return False
        
        # Step 2: Track usage multiple times to reach limit
        print("   📊 Step 2: Track usage to reach limit (10 times)")
        
        # Track usage up to the limit
        for i in range(1, 11):  # Track 10 times
            success = self.test_track_usage(feature_name)
            if not success:
                print(f"   ❌ Usage tracking failed at attempt {i}")
                return False
            print(f"   ✅ Usage tracked: {i}/10")
        
        # Step 3: Check access after reaching limit
        print("   📊 Step 3: Check access after reaching limit")
        success, response, status_code = self.test_feature_access_check(feature_name)
        
        if success:
            has_access = response.get('has_access')
            used = response.get('used', 0)
            remaining = response.get('remaining', 0)
            upgrade_needed = response.get('upgrade_needed', False)
            
            print(f"   📊 After Limit Status: status={status_code}, has_access={has_access}, used={used}, remaining={remaining}, upgrade_needed={upgrade_needed}")
            
            # Validate expected behavior
            if status_code == 402 and not has_access and upgrade_needed:
                print("   ✅ AI Sessions monthly limit correctly enforced with 402 status")
                
                # Check upsell info
                upsell_info = response.get('upsell_info', {})
                if upsell_info:
                    target_plan = upsell_info.get('target_plan')
                    if target_plan == 'STARTER':
                        print("   ✅ Upsell info correctly targets STARTER plan for FREE users")
                        return True
                    else:
                        print(f"   ❌ Expected target_plan=STARTER, got {target_plan}")
                        return False
                else:
                    print("   ❌ Missing upsell_info in 402 response")
                    return False
            elif status_code == 200 and not has_access and upgrade_needed:
                print("   ⚠️ Limit enforced but status code is 200 instead of 402")
                return False
            else:
                print("   ❌ Limit enforcement not working correctly")
                return False
        else:
            print("   ❌ Access check after limit failed")
            return False
    
    def test_mock_tests_weekly_limit(self):
        """Test Mock Tests Weekly Limit (Free: 1 test/week)"""
        print("\n4️⃣ SCENARIO 2: FREE PLAN - MOCK TESTS WEEKLY LIMIT")
        print("   Testing Mock Tests Weekly Limit enforcement")
        
        feature_name = "mock_tests_weekly"
        
        # Step 1: Check initial access
        print("   📊 Step 1: Check access to mock_tests_weekly")
        success, response, status_code = self.test_feature_access_check(feature_name)
        
        if not success:
            print("   ❌ Initial access check failed")
            return False
        
        limit = response.get('limit', 0)
        used = response.get('used', 0)
        has_access = response.get('has_access')
        remaining = response.get('remaining', 0)
        
        print(f"   📊 Initial Status: has_access={has_access}, used={used}, limit={limit}, remaining={remaining}")
        
        if limit != 1:
            print(f"   ❌ Expected limit=1, got limit={limit}")
            return False
        
        # Step 2: Track usage once if we have access
        if has_access and remaining > 0:
            print("   📊 Step 2: Track usage once")
            success = self.test_track_usage(feature_name)
            if not success:
                print("   ❌ Usage tracking failed")
                return False
        
        # Step 3: Check access again (should return 402)
        print("   📊 Step 3: Check access after usage (should return 402)")
        success, response, status_code = self.test_feature_access_check(feature_name)
        
        if success:
            has_access = response.get('has_access')
            upgrade_needed = response.get('upgrade_needed', False)
            
            print(f"   📊 After Usage Status: status={status_code}, has_access={has_access}, upgrade_needed={upgrade_needed}")
            
            if status_code == 402 and not has_access and upgrade_needed:
                print("   ✅ Mock Tests weekly limit correctly enforced with 402 status")
                return True
            else:
                print("   ❌ Mock Tests limit enforcement not working correctly")
                return False
        else:
            print("   ❌ Access check after usage failed")
            return False
    
    def test_auto_note_uploads_daily_limit(self):
        """Test Auto-Note Uploads Daily Limit (Free: 1 upload/day)"""
        print("\n5️⃣ SCENARIO 3: FREE PLAN - AUTO-NOTE UPLOADS DAILY LIMIT")
        print("   Testing Auto-Note Uploads Daily Limit enforcement")
        
        feature_name = "auto_note_uploads_daily"
        
        # Step 1: Check initial access
        print("   📊 Step 1: Check access to auto_note_uploads_daily")
        success, response, status_code = self.test_feature_access_check(feature_name)
        
        if not success:
            print("   ❌ Initial access check failed")
            return False
        
        limit = response.get('limit', 0)
        used = response.get('used', 0)
        has_access = response.get('has_access')
        remaining = response.get('remaining', 0)
        
        print(f"   📊 Initial Status: has_access={has_access}, used={used}, limit={limit}, remaining={remaining}")
        
        if limit != 1:
            print(f"   ❌ Expected limit=1, got limit={limit}")
            return False
        
        # Step 2: Track usage once if we have access
        if has_access and remaining > 0:
            print("   📊 Step 2: Track usage once")
            success = self.test_track_usage(feature_name)
            if not success:
                print("   ❌ Usage tracking failed")
                return False
        
        # Step 3: Check access again (should return 402)
        print("   📊 Step 3: Check access after usage (should return 402)")
        success, response, status_code = self.test_feature_access_check(feature_name)
        
        if success:
            has_access = response.get('has_access')
            upgrade_needed = response.get('upgrade_needed', False)
            
            print(f"   📊 After Usage Status: status={status_code}, has_access={has_access}, upgrade_needed={upgrade_needed}")
            
            if status_code == 402 and not has_access and upgrade_needed:
                print("   ✅ Auto-Note Uploads daily limit correctly enforced with 402 status")
                return True
            else:
                print("   ❌ Auto-Note Uploads limit enforcement not working correctly")
                return False
        else:
            print("   ❌ Access check after usage failed")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive subscription system test with fresh FREE user"""
        print("💳 SUBSCRIPTION SYSTEM BACKEND TESTING - COMPREHENSIVE VALIDATION")
        print("=" * 80)
        print("   CONTEXT: Testing with FRESH FREE USER to validate planConfig_ai_tutor.json limits")
        print("   TESTING SCOPE: Feature name consistency, Limit enforcement, 402 status codes, Upsell info, Usage tracking")
        print("   EXPECTED RESULTS:")
        print("     - Scenario 1: 10 AI sessions allowed, 11th blocked with 402")
        print("     - Scenario 2: 1 test allowed, 2nd blocked with 402")
        print("     - Scenario 3: 1 upload allowed, 2nd blocked with 402")
        print("     - Scenario 4: Complete upsell_info in all 402 responses")
        print("     - Scenario 5: Correct Free plan configuration returned")
        
        test_results = {
            'fresh_user_creation': False,
            'subscription_info': False,
            'ai_sessions_monthly_limit': False,
            'mock_tests_weekly_limit': False,
            'auto_note_uploads_daily_limit': False
        }
        
        # Create fresh user
        print("\n1️⃣ FRESH USER CREATION")
        test_results['fresh_user_creation'] = self.create_fresh_user()
        
        if not test_results['fresh_user_creation']:
            print("❌ Fresh user creation failed - cannot proceed with tests")
            return
        
        # Subscription Info Endpoint
        test_results['subscription_info'] = self.test_subscription_info()
        
        # SCENARIO 1: Free Plan - AI Sessions Monthly Limit
        test_results['ai_sessions_monthly_limit'] = self.test_ai_sessions_monthly_limit()
        
        # SCENARIO 2: Free Plan - Mock Tests Weekly Limit  
        test_results['mock_tests_weekly_limit'] = self.test_mock_tests_weekly_limit()
        
        # SCENARIO 3: Free Plan - Auto-Note Uploads Daily Limit
        test_results['auto_note_uploads_daily_limit'] = self.test_auto_note_uploads_daily_limit()
        
        # Final Assessment
        success_count = sum(test_results.values())
        total_tests = len(test_results)
        success_rate = (success_count / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print(f"📊 SUBSCRIPTION SYSTEM COMPREHENSIVE VALIDATION RESULTS")
        print(f"=" * 80)
        print(f"SUCCESS RATE: {success_count}/{total_tests} ({success_rate:.1f}%)")
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        # Expected Results Validation
        print(f"\n🎯 EXPECTED RESULTS VALIDATION:")
        print(f"   ✅ Scenario 1 (10 sessions → 402): {'✅' if test_results['ai_sessions_monthly_limit'] else '❌'}")
        print(f"   ✅ Scenario 2 (1 test → 402): {'✅' if test_results['mock_tests_weekly_limit'] else '❌'}")
        print(f"   ✅ Scenario 3 (1 upload → 402): {'✅' if test_results['auto_note_uploads_daily_limit'] else '❌'}")
        print(f"   ✅ Scenario 5 (Free plan config): {'✅' if test_results['subscription_info'] else '❌'}")
        
        return success_count >= 4  # At least 4/5 tests must pass

if __name__ == "__main__":
    tester = FreshUserSubscriptionTester()
    tester.run_comprehensive_test()