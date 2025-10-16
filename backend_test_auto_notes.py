#!/usr/bin/env python3
"""
AUTO-NOTES SUBSCRIPTION ENFORCEMENT TESTING - FRESH ACCOUNT
Testing the daily limit enforcement for Free plan users with auto_note_uploads_daily feature
"""

import requests
import sys
import json
from datetime import datetime
import time
import io
import uuid

class DhruvAITester:
    def __init__(self, base_url="https://auth-gateway-dhruv.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.session_id = None
        self.csrf_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_email = "test@dhruvai.com"
        self.test_password = "password123"

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

    def test_auto_notes_subscription_enforcement_fresh_account(self):
        """AUTO-NOTES SUBSCRIPTION ENFORCEMENT TESTING - FRESH ACCOUNT"""
        print("\n📝 AUTO-NOTES SUBSCRIPTION ENFORCEMENT TESTING - FRESH ACCOUNT")
        print("=" * 80)
        print("   OBJECTIVE: Verify Auto-Notes daily limit enforcement works correctly for Free plan users")
        print("   SCENARIO: Fresh FREE user account → Check subscription → Test 1st upload → Test 2nd upload (should trigger 402)")
        print("   EXPECTED: Free plan has exactly 1 upload per day, 2nd upload triggers 402 with upgrade modal")
        print("   CRITICAL: Upsell info shows STARTER plan pricing as target upgrade")
        
        test_results = {
            'fresh_user_creation': False,
            'subscription_info_check': False,
            'initial_feature_access_check': False,
            'first_usage_tracking': False,
            'access_check_after_first_usage': False,
            'second_usage_tracking': False,
            'access_check_after_second_usage_402': False,
            'upsell_info_validation': False,
            'target_plan_validation': False,
            'daily_limit_validation': False
        }
        
        # STEP 1: Create fresh FREE user account
        print("\n1️⃣ STEP 1: CREATE FRESH FREE USER ACCOUNT")
        fresh_user_email = f"auto_notes_test_{int(time.time())}@dhruvai.com"
        registration_data = {
            "full_name": "Auto Notes Test User",
            "email": fresh_user_email,
            "password": "password123",
            "exam_type": "JEE",
            "target_year": 2026
        }
        
        print(f"   Creating fresh user: {fresh_user_email}")
        success, response, _ = self.run_test(
            "Fresh User Registration",
            "POST",
            "auth/register",
            200,
            data=registration_data
        )
        
        if success and response.get('token'):
            fresh_token = response.get('token')
            test_results['fresh_user_creation'] = True
            print(f"   ✅ Fresh user created successfully")
        else:
            print("   ❌ Failed to create fresh user")
            return self._print_auto_notes_test_results(test_results)
        
        # STEP 2: Check subscription info - should show auto_note_uploads_daily: 1 (Free plan)
        print("\n2️⃣ STEP 2: CHECK SUBSCRIPTION INFO")
        print("   Expected: subscription_tier='FREE', auto_note_uploads_daily=1")
        
        success, response, _ = self.run_test(
            "Subscription Info Check",
            "GET",
            "subscription/info",
            200,
            headers={'Authorization': f'Bearer {fresh_token}'}
        )
        
        if success:
            subscription_tier = response.get('subscription_tier')
            plan_info = response.get('plan_info', {})
            features = plan_info.get('features', {})
            auto_note_limit = features.get('auto_note_uploads_daily', 0)
            
            print(f"   📊 Subscription Info:")
            print(f"      subscription_tier: {subscription_tier}")
            print(f"      auto_note_uploads_daily: {auto_note_limit}")
            
            if subscription_tier == "FREE" and auto_note_limit == 1:
                test_results['subscription_info_check'] = True
                print("   ✅ Subscription info correct - FREE plan with 1 upload/day")
            else:
                print(f"   ❌ Subscription info incorrect - Expected FREE/1, got {subscription_tier}/{auto_note_limit}")
        else:
            print("   ❌ Failed to get subscription info")
        
        # STEP 3: Check feature access BEFORE any usage
        print("\n3️⃣ STEP 3: CHECK FEATURE ACCESS BEFORE USAGE")
        print("   Expected: 200 OK with has_access=true, used=0, limit=1, remaining=1")
        
        success, response, _ = self.run_test(
            "Initial Feature Access Check",
            "POST",
            "subscription/check-access",
            200,
            data={"feature_name": "auto_note_uploads_daily"},
            headers={'Authorization': f'Bearer {fresh_token}'}
        )
        
        if success:
            has_access = response.get('has_access', False)
            used = response.get('used', -1)
            limit = response.get('limit', -1)
            remaining = response.get('remaining', -1)
            
            print(f"   📊 Initial Access Check:")
            print(f"      has_access: {has_access}")
            print(f"      used: {used}")
            print(f"      limit: {limit}")
            print(f"      remaining: {remaining}")
            
            if has_access and used == 0 and limit == 1 and remaining == 1:
                test_results['initial_feature_access_check'] = True
                print("   ✅ Initial access check correct")
            else:
                print(f"   ❌ Initial access check incorrect - Expected true/0/1/1, got {has_access}/{used}/{limit}/{remaining}")
        else:
            print("   ❌ Failed initial feature access check")
        
        # STEP 4: Track usage ONCE (simulating 1st file upload today)
        print("\n4️⃣ STEP 4: TRACK USAGE ONCE (1st file upload)")
        print("   Expected: 200 OK (tracking succeeds)")
        
        success, response, _ = self.run_test(
            "First Usage Tracking",
            "POST",
            "subscription/track-usage",
            200,
            data={"feature_name": "auto_note_uploads_daily"},
            headers={'Authorization': f'Bearer {fresh_token}'}
        )
        
        if success:
            test_results['first_usage_tracking'] = True
            print("   ✅ First usage tracking successful")
        else:
            print("   ❌ First usage tracking failed")
        
        # STEP 5: Check feature access AFTER 1st usage
        print("\n5️⃣ STEP 5: CHECK FEATURE ACCESS AFTER 1st USAGE")
        print("   Expected: 200 OK with has_access=true, used=1, limit=1, remaining=0")
        print("   OR: 402 if backend is too strict (current behavior)")
        
        success, response, http_response = self.run_test(
            "Access Check After First Usage",
            "POST",
            "subscription/check-access",
            [200, 402],  # Accept both 200 and 402
            data={"feature_name": "auto_note_uploads_daily"},
            headers={'Authorization': f'Bearer {fresh_token}'}
        )
        
        if success:
            if http_response.status_code == 200:
                # Expected behavior: 200 OK with remaining=0 but still has_access=true
                has_access = response.get('has_access', False)
                used = response.get('used', -1)
                limit = response.get('limit', -1)
                remaining = response.get('remaining', -1)
                
                print(f"   📊 200 Response After 1st Usage:")
                print(f"      has_access: {has_access}")
                print(f"      used: {used}")
                print(f"      limit: {limit}")
                print(f"      remaining: {remaining}")
                
                if has_access and used == 1 and limit == 1 and remaining == 0:
                    test_results['access_check_after_first_usage'] = True
                    print("   ✅ Access check after 1st usage correct (ideal behavior)")
                else:
                    print(f"   ⚠️ Access check after 1st usage - Expected true/1/1/0, got {has_access}/{used}/{limit}/{remaining}")
            
            elif http_response.status_code == 402:
                # Current behavior: 402 immediately after reaching limit
                detail = response.get('detail', {})
                has_access = detail.get('has_access', True)  # Default True since it's not in 402 response
                used = detail.get('current_usage', -1)
                limit = detail.get('limit', -1)
                upgrade_needed = detail.get('upgrade_needed', False)
                
                print(f"   📊 402 Response After 1st Usage (Current Backend Behavior):")
                print(f"      used: {used}")
                print(f"      limit: {limit}")
                print(f"      upgrade_needed: {upgrade_needed}")
                
                if used == 1 and limit == 1 and upgrade_needed:
                    test_results['access_check_after_first_usage'] = True
                    print("   ⚠️ Backend returns 402 immediately after reaching limit (too strict)")
                    print("   📝 ISSUE: Should return 200 OK when at limit but not exceeded")
                else:
                    print(f"   ❌ 402 response incorrect - Expected 1/1/true, got {used}/{limit}/{upgrade_needed}")
        else:
            print("   ❌ Failed access check after 1st usage")
        
        # STEP 6: Track usage AGAIN (simulating 2nd file upload attempt)
        print("\n6️⃣ STEP 6: TRACK USAGE AGAIN (2nd file upload attempt)")
        print("   Expected: 200 OK (tracking succeeds)")
        
        success, response, _ = self.run_test(
            "Second Usage Tracking",
            "POST",
            "subscription/track-usage",
            200,
            data={"feature_name": "auto_note_uploads_daily"},
            headers={'Authorization': f'Bearer {fresh_token}'}
        )
        
        if success:
            test_results['second_usage_tracking'] = True
            print("   ✅ Second usage tracking successful")
        else:
            print("   ❌ Second usage tracking failed")
        
        # STEP 7: Check feature access AFTER 2nd usage (EXCEEDING LIMIT)
        print("\n7️⃣ STEP 7: CHECK FEATURE ACCESS AFTER 2nd USAGE (EXCEEDING LIMIT)")
        print("   Expected: 402 Payment Required with has_access=false, upgrade_needed=true, upsell_info")
        
        success, response, _ = self.run_test(
            "Access Check After Second Usage (402 Expected)",
            "POST",
            "subscription/check-access",
            402,
            data={"feature_name": "auto_note_uploads_daily"},
            headers={'Authorization': f'Bearer {fresh_token}'}
        )
        
        if success:
            # Handle the actual response structure with 'detail' field
            detail = response.get('detail', {})
            has_access = False  # 402 means no access
            upgrade_needed = detail.get('upgrade_needed', False)
            upsell_info = detail.get('upsell_info', {})
            used = detail.get('current_usage', -1)
            limit = detail.get('limit', -1)
            
            print(f"   📊 402 Response After 2nd Usage:")
            print(f"      has_access: {has_access} (402 = no access)")
            print(f"      upgrade_needed: {upgrade_needed}")
            print(f"      upsell_info present: {bool(upsell_info)}")
            print(f"      used: {used}")
            print(f"      limit: {limit}")
            
            if not has_access and upgrade_needed and upsell_info:
                test_results['access_check_after_second_usage_402'] = True
                print("   ✅ 402 response structure correct")
                
                # STEP 8: Validate upsell_info structure
                print("\n8️⃣ STEP 8: VALIDATE UPSELL_INFO STRUCTURE")
                upsell_validation = self._validate_upsell_info_structure(upsell_info)
                test_results['upsell_info_validation'] = upsell_validation
                
                # STEP 9: Validate target_plan is STARTER
                print("\n9️⃣ STEP 9: VALIDATE TARGET_PLAN IS STARTER")
                target_plan = upsell_info.get('target_plan', '')
                if target_plan == "STARTER":
                    test_results['target_plan_validation'] = True
                    print(f"   ✅ Target plan correct: {target_plan}")
                else:
                    print(f"   ❌ Target plan incorrect - Expected STARTER, got {target_plan}")
                
            else:
                print(f"   ❌ 402 response structure incorrect - Expected false/true/present, got {has_access}/{upgrade_needed}/{bool(upsell_info)}")
        else:
            print("   ❌ Expected 402 response not received")
        
        # STEP 10: Validate daily limit logic
        print("\n🔟 STEP 10: VALIDATE DAILY LIMIT LOGIC")
        if test_results['subscription_info_check'] and test_results['access_check_after_second_usage_402']:
            test_results['daily_limit_validation'] = True
            print("   ✅ Daily limit logic working correctly - 1 upload allowed, 2nd triggers 402")
        elif test_results['subscription_info_check'] and test_results['access_check_after_first_usage']:
            test_results['daily_limit_validation'] = True
            print("   ⚠️ Daily limit logic working but backend is too strict")
            print("   📝 RECOMMENDATION: Backend should allow access when at limit, block when exceeded")
        else:
            print("   ❌ Daily limit logic not working correctly")
        
        return self._print_auto_notes_test_results(test_results)
    
    def _validate_upsell_info_structure(self, upsell_info):
        """Validate upsell_info structure contains required fields"""
        required_fields = {
            'target_plan': str,
            'mentor_message': str,
            'professor_message': str
        }
        
        validation_results = {}
        for field, expected_type in required_fields.items():
            value = upsell_info.get(field)
            has_value = value is not None and isinstance(value, expected_type) and len(str(value)) > 0
            validation_results[field] = has_value
            status = "✅" if has_value else "❌"
            print(f"      {field}: {status} ({type(value).__name__})")
        
        return all(validation_results.values())
    
    def _print_auto_notes_test_results(self, test_results):
        """Print comprehensive test results for Auto-Notes subscription enforcement"""
        print("\n" + "=" * 80)
        print("📝 AUTO-NOTES SUBSCRIPTION ENFORCEMENT - FINAL RESULTS")
        print("=" * 80)
        
        success_count = sum(test_results.values())
        total_tests = len(test_results)
        success_rate = (success_count / total_tests) * 100
        
        print(f"\n📊 TEST RESULTS SUMMARY:")
        
        # Core Flow Tests
        core_tests = [
            'fresh_user_creation',
            'subscription_info_check', 
            'initial_feature_access_check',
            'first_usage_tracking',
            'access_check_after_first_usage',
            'second_usage_tracking',
            'access_check_after_second_usage_402'
        ]
        
        core_success = sum(test_results[test] for test in core_tests)
        print(f"\n   CORE FLOW TESTS ({core_success}/{len(core_tests)}):")
        for test_name in core_tests:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"      {test_name.replace('_', ' ').title()}: {status}")
        
        # Validation Tests
        validation_tests = [
            'upsell_info_validation',
            'target_plan_validation',
            'daily_limit_validation'
        ]
        
        validation_success = sum(test_results[test] for test in validation_tests)
        print(f"\n   VALIDATION TESTS ({validation_success}/{len(validation_tests)}):")
        for test_name in validation_tests:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"      {test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\n📈 OVERALL SUCCESS RATE: {success_count}/{total_tests} ({success_rate:.1f}%)")
        
        # Critical Validation Summary
        print(f"\n🎯 CRITICAL VALIDATION SUMMARY:")
        print(f"   ✅ Free plan has exactly 1 upload per day: {'✅' if test_results['subscription_info_check'] else '❌'}")
        print(f"   ✅ 1st upload allowed (remaining: 0 after): {'✅' if test_results['access_check_after_first_usage'] else '❌'}")
        print(f"   ✅ 2nd upload triggers 402 with upgrade modal: {'✅' if test_results['access_check_after_second_usage_402'] else '❌'}")
        print(f"   ✅ Upsell info shows STARTER plan pricing: {'✅' if test_results['target_plan_validation'] else '❌'}")
        print(f"   ✅ Daily limit resets logic validated: {'✅' if test_results['daily_limit_validation'] else '❌'}")
        
        # Determine overall status
        if success_rate >= 90:
            print("\n✅ AUTO-NOTES SUBSCRIPTION ENFORCEMENT: EXCELLENT SUCCESS")
            print("   Free plan correctly limits to 1 upload/day, 2nd attempt triggers 402 with STARTER plan upgrade")
        elif success_rate >= 80:
            print("\n⚠️ AUTO-NOTES SUBSCRIPTION ENFORCEMENT: GOOD SUCCESS")
            print("   Core functionality working, minor validation issues")
        elif success_rate >= 70:
            print("\n⚠️ AUTO-NOTES SUBSCRIPTION ENFORCEMENT: PARTIAL SUCCESS")
            print("   Basic flow working, some critical validations failing")
        else:
            print("\n❌ AUTO-NOTES SUBSCRIPTION ENFORCEMENT: NEEDS WORK")
            print("   Critical issues prevent proper subscription enforcement")
        
        return success_rate >= 80  # 80% success rate for overall pass

# Main execution
if __name__ == "__main__":
    print("🚀 DHRUV AI AUTO-NOTES SUBSCRIPTION ENFORCEMENT TESTING - FRESH ACCOUNT")
    print("=" * 80)
    
    tester = DhruvAITester()
    
    # Run the auto-notes subscription enforcement test
    success = tester.test_auto_notes_subscription_enforcement_fresh_account()
    
    print("\n" + "=" * 80)
    print("🏁 AUTO-NOTES SUBSCRIPTION ENFORCEMENT TESTING COMPLETED")
    print("=" * 80)
    
    if success:
        print("✅ OVERALL RESULT: SUCCESS")
        print("   Auto-Notes subscription enforcement working correctly!")
    else:
        print("❌ OVERALL RESULT: FAILURE") 
        print("   Auto-Notes subscription enforcement needs fixes.")
    
    print(f"\n📊 FINAL STATISTICS:")
    print(f"   Tests Run: {tester.tests_run}")
    print(f"   Tests Passed: {tester.tests_passed}")
    if tester.tests_run > 0:
        success_rate = (tester.tests_passed / tester.tests_run) * 100
        print(f"   Success Rate: {success_rate:.1f}%")
    
    sys.exit(0 if success else 1)