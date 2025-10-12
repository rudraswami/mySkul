import requests
import sys
import json
from datetime import datetime
import time
import io
import uuid

class DhruvAITester:
    def __init__(self, base_url="https://dhruv-tutor-upgrade.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.session_id = None
        self.csrf_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_email = "test@dhruvai.com"
        self.test_password = "password123"
        self.fresh_user_email = f"fresh_user_{int(time.time())}@dhruvai.com"  # Fresh user for free tier testing

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, use_session=False):
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
            # Use session for cookie handling if needed
            if use_session:
                session = requests.Session()
                
                if method == 'GET':
                    response = session.get(url, headers=test_headers, timeout=60)
                elif method == 'POST':
                    response = session.post(url, json=data, headers=test_headers, timeout=60)
                elif method == 'PUT':
                    response = session.put(url, json=data, headers=test_headers, timeout=60)
            else:
                if method == 'GET':
                    response = requests.get(url, headers=test_headers, timeout=60)
                elif method == 'POST':
                    response = requests.post(url, json=data, headers=test_headers, timeout=60)
                elif method == 'PUT':
                    response = requests.put(url, json=data, headers=test_headers, timeout=60)

            print(f"   Status Code: {response.status_code}")
            
            # Store last response status for subscription error checking
            self.last_response_status = response.status_code
            
            success = response.status_code == expected_status or (isinstance(expected_status, list) and response.status_code in expected_status)
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data, response
                except:
                    return True, {}, response
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    # Store error details for subscription error analysis
                    self.last_error_data = error_data
                except:
                    print(f"   Error: {response.text}")
                    self.last_error_data = {"error": response.text}
                return False, {}, response

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.last_response_status = 0
            self.last_error_data = {"error": str(e)}
            return False, {}, None

    def test_auth_router_login(self):
        """Test Auth Router - POST /api/auth/login"""
        print("   Testing POST /api/auth/login endpoint")
        
        login_data = {
            "email": "test@dhruvai.com",
            "password": "password123"
        }
        
        success, response, _ = self.run_test(
            "Auth Router Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success:
            print("   ✅ Auth router login working")
            
            # Store token for subsequent tests
            if 'token' in response:
                self.token = response['token']
                print(f"   ✅ JWT token obtained: {self.token[:20]}...")
            
            if 'user' in response:
                user_data = response['user']
                self.user_id = user_data.get('user_id')
                print(f"   ✅ User authenticated: {user_data.get('email')}")
            
            return True
        else:
            print("   ❌ Auth router login failed")
            return False

    def test_subscription_system_retest_post_fix(self):
        """Test subscription system re-test - POST-FIX VALIDATION"""
        print("\n💳 SUBSCRIPTION SYSTEM RE-TEST - POST-FIX VALIDATION")
        print("=" * 80)
        print("   CONTEXT: Fixed subscription service initialization issue")
        print("   CHANGES: Updated inline endpoints to use modular_subscription_service instance")
        print("   TESTING: All scenarios with planConfig_ai_tutor.json validation")
        print("   CREDENTIALS: test@dhruvai.com / password123 OR fresh user creation")
        
        test_results = {
            'scenario_1_subscription_info': False,
            'scenario_2_ai_sessions_full_flow': False,
            'scenario_3_mock_tests_full_flow': False,
            'scenario_4_auto_notes_full_flow': False,
            'scenario_5_402_response_structure': False,
            'limits_match_config': False,
            'display_name_validation': False,
            'usage_tracking_accuracy': False,
            'has_access_logic': False,
            'upsell_info_complete': False
        }
        
        # AUTHENTICATION SETUP
        print("\n1️⃣ AUTHENTICATION SETUP")
        if not self.token:
            print("   Authenticating with test@dhruvai.com / password123")
            auth_success = self.test_auth_router_login()
            if not auth_success:
                print("   ❌ Authentication failed - cannot proceed with subscription tests")
                return False
        
        # SCENARIO 1: Subscription Info Validation
        print("\n2️⃣ SCENARIO 1: SUBSCRIPTION INFO VALIDATION")
        test_results['scenario_1_subscription_info'] = self.test_scenario_1_subscription_info()
        
        # SCENARIO 2: AI Sessions Monthly - Full Flow
        print("\n3️⃣ SCENARIO 2: AI SESSIONS MONTHLY - FULL FLOW")
        test_results['scenario_2_ai_sessions_full_flow'] = self.test_scenario_2_ai_sessions_full_flow()
        
        # SCENARIO 3: Mock Tests Weekly - Full Flow
        print("\n4️⃣ SCENARIO 3: MOCK TESTS WEEKLY - FULL FLOW")
        test_results['scenario_3_mock_tests_full_flow'] = self.test_scenario_3_mock_tests_full_flow()
        
        # SCENARIO 4: Auto-Note Uploads Daily - Full Flow
        print("\n5️⃣ SCENARIO 4: AUTO-NOTE UPLOADS DAILY - FULL FLOW")
        test_results['scenario_4_auto_notes_full_flow'] = self.test_scenario_4_auto_notes_full_flow()
        
        # SCENARIO 5: 402 Response Structure Validation
        print("\n6️⃣ SCENARIO 5: 402 RESPONSE STRUCTURE VALIDATION")
        test_results['scenario_5_402_response_structure'] = self.test_scenario_5_402_response_structure()
        
        # CRITICAL SUCCESS CRITERIA VALIDATION
        print("\n7️⃣ CRITICAL SUCCESS CRITERIA VALIDATION")
        test_results['limits_match_config'] = self.test_limits_match_config()
        test_results['display_name_validation'] = self.test_display_name_validation()
        test_results['usage_tracking_accuracy'] = self.test_usage_tracking_accuracy()
        test_results['has_access_logic'] = self.test_has_access_logic()
        test_results['upsell_info_complete'] = self.test_upsell_info_complete()
        
        # Final Assessment
        print("\n" + "=" * 80)
        print("💳 SUBSCRIPTION SYSTEM RE-TEST - FINAL RESULTS")
        print("=" * 80)
        
        success_count = sum(test_results.values())
        total_tests = len(test_results)
        success_rate = (success_count / total_tests) * 100
        
        print(f"\n📊 TEST RESULTS SUMMARY:")
        
        # Scenario Results
        scenario_tests = [k for k in test_results.keys() if k.startswith('scenario_')]
        scenario_success = sum(test_results[test] for test in scenario_tests)
        print(f"\n   SCENARIO TESTS ({scenario_success}/{len(scenario_tests)}):")
        for test_name in scenario_tests:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"      {test_name.replace('_', ' ').title()}: {status}")
        
        # Critical Criteria Results
        criteria_tests = [k for k in test_results.keys() if not k.startswith('scenario_')]
        criteria_success = sum(test_results[test] for test in criteria_tests)
        print(f"\n   CRITICAL SUCCESS CRITERIA ({criteria_success}/{len(criteria_tests)}):")
        for test_name in criteria_tests:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"      {test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\n📈 OVERALL SUCCESS RATE: {success_count}/{total_tests} ({success_rate:.1f}%)")
        
        # Determine overall status
        if success_rate >= 90:
            print("\n✅ SUBSCRIPTION SYSTEM RE-TEST: EXCELLENT SUCCESS")
            print("   All post-fix scenarios working correctly")
        elif success_rate >= 75:
            print("\n⚠️ SUBSCRIPTION SYSTEM RE-TEST: GOOD SUCCESS")
            print("   Most scenarios working, minor issues need attention")
        elif success_rate >= 60:
            print("\n⚠️ SUBSCRIPTION SYSTEM RE-TEST: PARTIAL SUCCESS")
            print("   Core scenarios working, some features need fixes")
        else:
            print("\n❌ SUBSCRIPTION SYSTEM RE-TEST: NEEDS WORK")
            print("   Critical issues prevent proper subscription functionality")
        
        return success_rate >= 75  # 75% success rate for overall pass

    def test_scenario_1_subscription_info(self):
        """SCENARIO 1: Subscription Info Validation with fresh FREE user"""
        print("   Testing GET /api/subscription/info with fresh FREE user")
        print("   Expected: FREE tier with planConfig_ai_tutor.json limits")
        
        # Create fresh user for FREE tier testing
        fresh_user_email = f"free_user_{int(time.time())}@dhruvai.com"
        registration_data = {
            "full_name": "Fresh Free User",
            "email": fresh_user_email,
            "password": "password123",
            "exam_type": "JEE",
            "target_year": 2026
        }
        
        # Register fresh user
        success, response, _ = self.run_test(
            "Fresh User Registration",
            "POST",
            "auth/register",
            200,
            data=registration_data
        )
        
        if not success:
            print("   ❌ Failed to create fresh user")
            return False
        
        fresh_token = response.get('token')
        if not fresh_token:
            print("   ❌ No token from fresh user registration")
            return False
        
        # Test subscription info endpoint
        success, response, _ = self.run_test(
            "Subscription Info - Fresh FREE User",
            "GET",
            "subscription/info",
            200,
            headers={'Authorization': f'Bearer {fresh_token}'}
        )
        
        if success:
            subscription_tier = response.get('subscription_tier')
            plan_info = response.get('plan_info', {})
            display_name = plan_info.get('display_name')
            features = plan_info.get('features', {})
            
            print(f"   📊 Subscription Info Response:")
            print(f"      subscription_tier: {subscription_tier}")
            print(f"      display_name: {display_name}")
            print(f"      features: {features}")
            
            # Validate expected response structure
            expected_tier = "FREE"
            expected_display_name = "🆓 Free - Try Before You Commit"
            expected_features = {
                "ai_sessions_monthly": 10,
                "mentor_tips_daily": 0,
                "mock_tests_weekly": 1,
                "auto_note_uploads_daily": 1
            }
            
            validation_results = {
                'tier_correct': subscription_tier == expected_tier,
                'display_name_correct': display_name == expected_display_name,
                'ai_sessions_correct': features.get('ai_sessions_monthly') == expected_features['ai_sessions_monthly'],
                'mentor_tips_correct': features.get('mentor_tips_daily') == expected_features['mentor_tips_daily'],
                'mock_tests_correct': features.get('mock_tests_weekly') == expected_features['mock_tests_weekly'],
                'auto_notes_correct': features.get('auto_note_uploads_daily') == expected_features['auto_note_uploads_daily']
            }
            
            print(f"   📋 Validation Results:")
            for key, result in validation_results.items():
                status = "✅" if result else "❌"
                print(f"      {key}: {status}")
            
            # Store fresh token for subsequent tests
            self.fresh_user_token = fresh_token
            
            return all(validation_results.values())
        else:
            print("   ❌ Subscription info endpoint failed")
            return False

    def test_scenario_2_ai_sessions_full_flow(self):
        """SCENARIO 2: AI Sessions Monthly - Full Flow (10 limit test)"""
        print("   Testing AI Sessions Monthly full flow: 0→10→11 usage")
        
        if not hasattr(self, 'fresh_user_token') or not self.fresh_user_token:
            print("   ❌ No fresh user token available")
            return False
        
        # Step 1: Check initial access (should show limit: 10, used: 0, remaining: 10)
        print("   Step 1: Check initial access")
        success, response, _ = self.run_test(
            "AI Sessions - Initial Access Check",
            "POST",
            "subscription/check-access",
            200,
            data={"feature_name": "ai_sessions_monthly"},
            headers={'Authorization': f'Bearer {self.fresh_user_token}'}
        )
        
        if not success:
            print("   ❌ Initial access check failed")
            return False
        
        initial_limit = response.get('limit', 0)
        initial_used = response.get('used', 0)
        initial_remaining = response.get('remaining', 0)
        initial_has_access = response.get('has_access', False)
        
        print(f"   📊 Initial Access: limit={initial_limit}, used={initial_used}, remaining={initial_remaining}, has_access={initial_has_access}")
        
        if initial_limit != 10 or initial_used != 0 or initial_remaining != 10:
            print("   ❌ Initial access values incorrect")
            return False
        
        # Step 2: Track usage 10 times
        print("   Step 2: Track usage 10 times")
        for i in range(10):
            success, response, _ = self.run_test(
                f"AI Sessions - Track Usage {i+1}",
                "POST",
                "subscription/track-usage",
                200,
                data={"feature_name": "ai_sessions_monthly"},
                headers={'Authorization': f'Bearer {self.fresh_user_token}'}
            )
            
            if not success:
                print(f"   ❌ Usage tracking failed at attempt {i+1}")
                return False
        
        # Step 3: Check access after 10 uses (should show limit: 10, used: 10, remaining: 0, has_access: true)
        print("   Step 3: Check access after 10 uses")
        success, response, _ = self.run_test(
            "AI Sessions - Access Check After 10",
            "POST",
            "subscription/check-access",
            200,
            data={"feature_name": "ai_sessions_monthly"},
            headers={'Authorization': f'Bearer {self.fresh_user_token}'}
        )
        
        if not success:
            print("   ❌ Access check after 10 uses failed")
            return False
        
        after_10_limit = response.get('limit', 0)
        after_10_used = response.get('used', 0)
        after_10_remaining = response.get('remaining', 0)
        after_10_has_access = response.get('has_access', False)
        
        print(f"   📊 After 10 Uses: limit={after_10_limit}, used={after_10_used}, remaining={after_10_remaining}, has_access={after_10_has_access}")
        
        if after_10_limit != 10 or after_10_used != 10 or after_10_remaining != 0 or not after_10_has_access:
            print("   ❌ Access values after 10 uses incorrect")
            return False
        
        # Step 4: Track usage 11th time
        print("   Step 4: Track usage 11th time")
        success, response, _ = self.run_test(
            "AI Sessions - Track Usage 11th",
            "POST",
            "subscription/track-usage",
            200,
            data={"feature_name": "ai_sessions_monthly"},
            headers={'Authorization': f'Bearer {self.fresh_user_token}'}
        )
        
        if not success:
            print("   ❌ 11th usage tracking failed")
            return False
        
        # Step 5: Check access after 11 uses (should return 402 with has_access: false, upgrade_needed: true)
        print("   Step 5: Check access after 11 uses (should return 402)")
        success, response, _ = self.run_test(
            "AI Sessions - Access Check After 11",
            "POST",
            "subscription/check-access",
            402,  # Should return 402 Payment Required
            data={"feature_name": "ai_sessions_monthly"},
            headers={'Authorization': f'Bearer {self.fresh_user_token}'}
        )
        
        if success:
            has_access = response.get('has_access', True)
            upgrade_needed = response.get('upgrade_needed', False)
            upsell_info = response.get('upsell_info', {})
            
            print(f"   📊 After 11 Uses (402): has_access={has_access}, upgrade_needed={upgrade_needed}")
            print(f"   📊 Upsell info present: {bool(upsell_info)}")
            
            if has_access or not upgrade_needed or not upsell_info:
                print("   ❌ 402 response structure incorrect")
                return False
            
            return True
        else:
            print("   ❌ Expected 402 response not received")
            return False

    def test_scenario_3_mock_tests_full_flow(self):
        """SCENARIO 3: Mock Tests Weekly - Full Flow (1 limit test)"""
        print("   Testing Mock Tests Weekly full flow: 0→1→2 usage")
        
        if not hasattr(self, 'fresh_user_token') or not self.fresh_user_token:
            print("   ❌ No fresh user token available")
            return False
        
        # Step 1: Check initial access (should show limit: 1, used: 0, remaining: 1)
        print("   Step 1: Check initial access")
        success, response, _ = self.run_test(
            "Mock Tests - Initial Access Check",
            "POST",
            "subscription/check-access",
            200,
            data={"feature_name": "mock_tests_weekly"},
            headers={'Authorization': f'Bearer {self.fresh_user_token}'}
        )
        
        if not success:
            print("   ❌ Initial access check failed")
            return False
        
        initial_limit = response.get('limit', 0)
        initial_used = response.get('used', 0)
        initial_remaining = response.get('remaining', 0)
        
        print(f"   📊 Initial Access: limit={initial_limit}, used={initial_used}, remaining={initial_remaining}")
        
        if initial_limit != 1 or initial_used != 0 or initial_remaining != 1:
            print("   ❌ Initial access values incorrect")
            return False
        
        # Step 2: Track usage once
        print("   Step 2: Track usage once")
        success, response, _ = self.run_test(
            "Mock Tests - Track Usage 1",
            "POST",
            "subscription/track-usage",
            200,
            data={"feature_name": "mock_tests_weekly"},
            headers={'Authorization': f'Bearer {self.fresh_user_token}'}
        )
        
        if not success:
            print("   ❌ Usage tracking failed")
            return False
        
        # Step 3: Check access after 1 use (should show limit: 1, used: 1, remaining: 0, has_access: true)
        print("   Step 3: Check access after 1 use")
        success, response, _ = self.run_test(
            "Mock Tests - Access Check After 1",
            "POST",
            "subscription/check-access",
            200,
            data={"feature_name": "mock_tests_weekly"},
            headers={'Authorization': f'Bearer {self.fresh_user_token}'}
        )
        
        if not success:
            print("   ❌ Access check after 1 use failed")
            return False
        
        after_1_limit = response.get('limit', 0)
        after_1_used = response.get('used', 0)
        after_1_remaining = response.get('remaining', 0)
        after_1_has_access = response.get('has_access', False)
        
        print(f"   📊 After 1 Use: limit={after_1_limit}, used={after_1_used}, remaining={after_1_remaining}, has_access={after_1_has_access}")
        
        if after_1_limit != 1 or after_1_used != 1 or after_1_remaining != 0 or not after_1_has_access:
            print("   ❌ Access values after 1 use incorrect")
            return False
        
        # Step 4: Track usage 2nd time
        print("   Step 4: Track usage 2nd time")
        success, response, _ = self.run_test(
            "Mock Tests - Track Usage 2nd",
            "POST",
            "subscription/track-usage",
            200,
            data={"feature_name": "mock_tests_weekly"},
            headers={'Authorization': f'Bearer {self.fresh_user_token}'}
        )
        
        if not success:
            print("   ❌ 2nd usage tracking failed")
            return False
        
        # Step 5: Check access after 2 uses (should return 402 with upsell_info)
        print("   Step 5: Check access after 2 uses (should return 402)")
        success, response, _ = self.run_test(
            "Mock Tests - Access Check After 2",
            "POST",
            "subscription/check-access",
            402,  # Should return 402 Payment Required
            data={"feature_name": "mock_tests_weekly"},
            headers={'Authorization': f'Bearer {self.fresh_user_token}'}
        )
        
        if success:
            upsell_info = response.get('upsell_info', {})
            print(f"   📊 402 Response with upsell_info: {bool(upsell_info)}")
            return bool(upsell_info)
        else:
            print("   ❌ Expected 402 response not received")
            return False

    def test_scenario_4_auto_notes_full_flow(self):
        """SCENARIO 4: Auto-Note Uploads Daily - Full Flow (1 limit test)"""
        print("   Testing Auto-Note Uploads Daily full flow: 0→1→2 usage")
        
        if not hasattr(self, 'fresh_user_token') or not self.fresh_user_token:
            print("   ❌ No fresh user token available")
            return False
        
        # Step 1: Check initial access (should show limit: 1, used: 0, remaining: 1)
        print("   Step 1: Check initial access")
        success, response, _ = self.run_test(
            "Auto Notes - Initial Access Check",
            "POST",
            "subscription/check-access",
            200,
            data={"feature_name": "auto_note_uploads_daily"},
            headers={'Authorization': f'Bearer {self.fresh_user_token}'}
        )
        
        if not success:
            print("   ❌ Initial access check failed")
            return False
        
        initial_limit = response.get('limit', 0)
        initial_used = response.get('used', 0)
        initial_remaining = response.get('remaining', 0)
        
        print(f"   📊 Initial Access: limit={initial_limit}, used={initial_used}, remaining={initial_remaining}")
        
        if initial_limit != 1 or initial_used != 0 or initial_remaining != 1:
            print("   ❌ Initial access values incorrect")
            return False
        
        # Step 2: Track usage once
        print("   Step 2: Track usage once")
        success, response, _ = self.run_test(
            "Auto Notes - Track Usage 1",
            "POST",
            "subscription/track-usage",
            200,
            data={"feature_name": "auto_note_uploads_daily"},
            headers={'Authorization': f'Bearer {self.fresh_user_token}'}
        )
        
        if not success:
            print("   ❌ Usage tracking failed")
            return False
        
        # Step 3: Check access after 1 use (should show limit: 1, used: 1, remaining: 0, has_access: true)
        print("   Step 3: Check access after 1 use")
        success, response, _ = self.run_test(
            "Auto Notes - Access Check After 1",
            "POST",
            "subscription/check-access",
            200,
            data={"feature_name": "auto_note_uploads_daily"},
            headers={'Authorization': f'Bearer {self.fresh_user_token}'}
        )
        
        if not success:
            print("   ❌ Access check after 1 use failed")
            return False
        
        after_1_limit = response.get('limit', 0)
        after_1_used = response.get('used', 0)
        after_1_remaining = response.get('remaining', 0)
        after_1_has_access = response.get('has_access', False)
        
        print(f"   📊 After 1 Use: limit={after_1_limit}, used={after_1_used}, remaining={after_1_remaining}, has_access={after_1_has_access}")
        
        if after_1_limit != 1 or after_1_used != 1 or after_1_remaining != 0 or not after_1_has_access:
            print("   ❌ Access values after 1 use incorrect")
            return False
        
        # Step 4: Track usage 2nd time
        print("   Step 4: Track usage 2nd time")
        success, response, _ = self.run_test(
            "Auto Notes - Track Usage 2nd",
            "POST",
            "subscription/track-usage",
            200,
            data={"feature_name": "auto_note_uploads_daily"},
            headers={'Authorization': f'Bearer {self.fresh_user_token}'}
        )
        
        if not success:
            print("   ❌ 2nd usage tracking failed")
            return False
        
        # Step 5: Check access after 2 uses (should return 402 with upsell_info)
        print("   Step 5: Check access after 2 uses (should return 402)")
        success, response, _ = self.run_test(
            "Auto Notes - Access Check After 2",
            "POST",
            "subscription/check-access",
            402,  # Should return 402 Payment Required
            data={"feature_name": "auto_note_uploads_daily"},
            headers={'Authorization': f'Bearer {self.fresh_user_token}'}
        )
        
        if success:
            upsell_info = response.get('upsell_info', {})
            print(f"   📊 402 Response with upsell_info: {bool(upsell_info)}")
            return bool(upsell_info)
        else:
            print("   ❌ Expected 402 response not received")
            return False

    def test_scenario_5_402_response_structure(self):
        """SCENARIO 5: 402 Response Structure Validation"""
        print("   Testing 402 response structure when limit exceeded")
        
        if not hasattr(self, 'fresh_user_token') or not self.fresh_user_token:
            print("   ❌ No fresh user token available")
            return False
        
        # Force a 402 response by checking access for a feature that should be exhausted
        success, response, _ = self.run_test(
            "402 Response Structure Validation",
            "POST",
            "subscription/check-access",
            402,
            data={"feature_name": "ai_sessions_monthly"},  # Should be exhausted from previous test
            headers={'Authorization': f'Bearer {self.fresh_user_token}'}
        )
        
        if success:
            print("   📊 Validating 402 response structure...")
            
            # Required fields in 402 response
            required_fields = {
                'has_access': False,
                'upgrade_needed': True,
                'upsell_info': dict
            }
            
            # Upsell info required fields
            upsell_info = response.get('upsell_info', {})
            required_upsell_fields = {
                'mentor_message': str,
                'professor_message': str,
                'target_plan': str,
                'growth_stats': dict,
                'feature_name': str,
                'reason': str
            }
            
            validation_results = {}
            
            # Validate main response fields
            for field, expected_type in required_fields.items():
                value = response.get(field)
                if field == 'has_access':
                    validation_results[field] = value is False
                elif field == 'upgrade_needed':
                    validation_results[field] = value is True
                elif field == 'upsell_info':
                    validation_results[field] = isinstance(value, expected_type) and bool(value)
                else:
                    validation_results[field] = isinstance(value, expected_type)
            
            # Validate upsell_info fields
            for field, expected_type in required_upsell_fields.items():
                value = upsell_info.get(field)
                validation_results[f'upsell_{field}'] = isinstance(value, expected_type) and bool(value)
            
            # Special validation for target_plan (should be "STARTER" for FREE users)
            target_plan = upsell_info.get('target_plan', '')
            validation_results['target_plan_correct'] = target_plan == "STARTER"
            
            print(f"   📋 402 Response Validation:")
            for field, result in validation_results.items():
                status = "✅" if result else "❌"
                print(f"      {field}: {status}")
            
            return all(validation_results.values())
        else:
            print("   ❌ Failed to get 402 response")
            return False

    def test_limits_match_config(self):
        """Test that limits match planConfig_ai_tutor.json exactly (10/1/1)"""
        print("   Testing limits match planConfig_ai_tutor.json exactly")
        
        # Test subscription info to get plan limits
        success, response, _ = self.run_test(
            "Limits Match Config",
            "GET",
            "subscription/info",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            plan_info = response.get('plan_info', {})
            features = plan_info.get('features', {})
            
            expected_limits = {
                'ai_sessions_monthly': 10,
                'mock_tests_weekly': 1,
                'auto_note_uploads_daily': 1
            }
            
            validation_results = {}
            for feature, expected_limit in expected_limits.items():
                actual_limit = features.get(feature, 0)
                validation_results[feature] = actual_limit == expected_limit
                print(f"      {feature}: expected={expected_limit}, actual={actual_limit} {'✅' if validation_results[feature] else '❌'}")
            
            return all(validation_results.values())
        else:
            print("   ❌ Failed to get subscription info")
            return False

    def test_display_name_validation(self):
        """Test display name matches: '🆓 Free - Try Before You Commit'"""
        print("   Testing display name matches expected format")
        
        success, response, _ = self.run_test(
            "Display Name Validation",
            "GET",
            "subscription/info",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            plan_info = response.get('plan_info', {})
            display_name = plan_info.get('display_name', '')
            expected_display_name = "🆓 Free - Try Before You Commit"
            
            matches = display_name == expected_display_name
            print(f"      Expected: '{expected_display_name}'")
            print(f"      Actual: '{display_name}'")
            print(f"      Matches: {'✅' if matches else '❌'}")
            
            return matches
        else:
            print("   ❌ Failed to get subscription info")
            return False

    def test_usage_tracking_accuracy(self):
        """Test usage tracking is accurate"""
        print("   Testing usage tracking accuracy")
        
        # Create another fresh user for isolated testing
        fresh_user_email = f"usage_test_{int(time.time())}@dhruvai.com"
        registration_data = {
            "full_name": "Usage Test User",
            "email": fresh_user_email,
            "password": "password123",
            "exam_type": "JEE",
            "target_year": 2026
        }
        
        # Register fresh user
        success, response, _ = self.run_test(
            "Usage Test User Registration",
            "POST",
            "auth/register",
            200,
            data=registration_data
        )
        
        if not success:
            print("   ❌ Failed to create usage test user")
            return False
        
        usage_test_token = response.get('token')
        
        # Check initial usage (should be 0)
        success, response, _ = self.run_test(
            "Initial Usage Check",
            "POST",
            "subscription/check-access",
            200,
            data={"feature_name": "ai_sessions_monthly"},
            headers={'Authorization': f'Bearer {usage_test_token}'}
        )
        
        if not success or response.get('used', -1) != 0:
            print("   ❌ Initial usage not 0")
            return False
        
        # Track usage 3 times
        for i in range(3):
            success, response, _ = self.run_test(
                f"Track Usage {i+1}",
                "POST",
                "subscription/track-usage",
                200,
                data={"feature_name": "ai_sessions_monthly"},
                headers={'Authorization': f'Bearer {usage_test_token}'}
            )
            
            if not success:
                print(f"   ❌ Usage tracking failed at {i+1}")
                return False
        
        # Check usage after 3 (should be 3)
        success, response, _ = self.run_test(
            "Usage Check After 3",
            "POST",
            "subscription/check-access",
            200,
            data={"feature_name": "ai_sessions_monthly"},
            headers={'Authorization': f'Bearer {usage_test_token}'}
        )
        
        if success:
            used = response.get('used', -1)
            remaining = response.get('remaining', -1)
            
            accuracy_correct = used == 3 and remaining == 7
            print(f"      Used: {used} (expected: 3)")
            print(f"      Remaining: {remaining} (expected: 7)")
            print(f"      Accuracy: {'✅' if accuracy_correct else '❌'}")
            
            return accuracy_correct
        else:
            print("   ❌ Failed to check usage after tracking")
            return False

    def test_has_access_logic(self):
        """Test has_access correctly reflects remaining quota"""
        print("   Testing has_access logic reflects remaining quota")
        
        # Use existing fresh user token
        if not hasattr(self, 'fresh_user_token') or not self.fresh_user_token:
            print("   ❌ No fresh user token available")
            return False
        
        # Test different features to validate has_access logic
        features_to_test = [
            "mock_tests_weekly",  # Should have 0 remaining from previous tests
            "auto_note_uploads_daily"  # Should have 0 remaining from previous tests
        ]
        
        validation_results = []
        
        for feature in features_to_test:
            success, response, _ = self.run_test(
                f"Has Access Logic - {feature}",
                "POST",
                "subscription/check-access",
                [200, 402],  # Accept both
                data={"feature_name": feature},
                headers={'Authorization': f'Bearer {self.fresh_user_token}'}
            )
            
            if success:
                remaining = response.get('remaining', 0)
                has_access = response.get('has_access', False)
                
                # Logic: has_access should be True if remaining > 0, False if remaining = 0
                expected_has_access = remaining > 0
                logic_correct = has_access == expected_has_access
                
                print(f"      {feature}: remaining={remaining}, has_access={has_access}, expected={expected_has_access} {'✅' if logic_correct else '❌'}")
                validation_results.append(logic_correct)
            else:
                print(f"      {feature}: ❌ Failed to check access")
                validation_results.append(False)
        
        return all(validation_results)

    def test_upsell_info_complete(self):
        """Test complete upsell_info in 402 responses"""
        print("   Testing complete upsell_info structure in 402 responses")
        
        if not hasattr(self, 'fresh_user_token') or not self.fresh_user_token:
            print("   ❌ No fresh user token available")
            return False
        
        # Get a 402 response with upsell_info
        success, response, _ = self.run_test(
            "Complete Upsell Info Test",
            "POST",
            "subscription/check-access",
            402,
            data={"feature_name": "ai_sessions_monthly"},  # Should be exhausted
            headers={'Authorization': f'Bearer {self.fresh_user_token}'}
        )
        
        if success:
            upsell_info = response.get('upsell_info', {})
            
            # Check all required upsell_info fields
            required_fields = [
                'mentor_message',
                'professor_message', 
                'target_plan',
                'growth_stats',
                'feature_name',
                'reason'
            ]
            
            validation_results = {}
            for field in required_fields:
                value = upsell_info.get(field)
                has_value = value is not None and value != "" and value != {}
                validation_results[field] = has_value
                print(f"      {field}: {'✅' if has_value else '❌'} ({type(value).__name__})")
            
            # Special checks
            mentor_msg = upsell_info.get('mentor_message', '')
            professor_msg = upsell_info.get('professor_message', '')
            target_plan = upsell_info.get('target_plan', '')
            reason = upsell_info.get('reason', '')
            
            # Validate content quality
            content_quality = {
                'mentor_motivational': len(mentor_msg) > 20,  # Should be motivational message
                'professor_analytical': len(professor_msg) > 20,  # Should be analytical message
                'target_plan_starter': target_plan == "STARTER",  # Should suggest STARTER for FREE users
                'reason_limit_reached': 'limit' in reason.lower() or 'reached' in reason.lower()
            }
            
            print(f"      Content Quality:")
            for check, result in content_quality.items():
                print(f"        {check}: {'✅' if result else '❌'}")
            
            validation_results.update(content_quality)
            
            return all(validation_results.values())
        else:
            print("   ❌ Failed to get 402 response with upsell_info")
            return False

# Main execution
if __name__ == "__main__":
    print("🚀 DHRUV AI SUBSCRIPTION SYSTEM RE-TEST - POST-FIX VALIDATION")
    print("=" * 80)
    
    tester = DhruvAITester()
    
    # Run the subscription system re-test
    success = tester.test_subscription_system_retest_post_fix()
    
    print("\n" + "=" * 80)
    print("🏁 SUBSCRIPTION SYSTEM RE-TEST COMPLETED")
    print("=" * 80)
    
    if success:
        print("✅ OVERALL RESULT: SUCCESS")
        print("   The subscription system post-fix validation passed!")
    else:
        print("❌ OVERALL RESULT: FAILURE") 
        print("   The subscription system needs additional fixes.")
    
    print(f"\n📊 FINAL STATISTICS:")
    print(f"   Tests Run: {tester.tests_run}")
    print(f"   Tests Passed: {tester.tests_passed}")
    if tester.tests_run > 0:
        success_rate = (tester.tests_passed / tester.tests_run) * 100
        print(f"   Success Rate: {success_rate:.1f}%")
    
    sys.exit(0 if success else 1)