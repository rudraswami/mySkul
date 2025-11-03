"""
Backend Testing - Subscription Gating Bug Fix Validation
Test Objective: Verify that new users with 0 usage are NOT blocked by subscription gating
"""
import requests
import json
import time
from datetime import datetime

# Backend URL
BACKEND_URL = "https://neuro-tutor-dev.preview.emergentagent.com/api"

# Test results storage
test_results = []

def log_test(test_name, status, details):
    """Log test result"""
    result = {
        "test": test_name,
        "status": status,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    test_results.append(result)
    
    status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"\n{status_icon} {test_name}: {status}")
    print(f"   Details: {details}")

def create_test_user(email, full_name, password="TestPassword123!"):
    """Create a fresh test user"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "full_name": full_name,
                "email": email,
                "password": password,
                "exam_type": "JEE",
                "grade": "12",
                "target_year": 2026
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "user_id": data.get("user", {}).get("user_id"),
                "token": data.get("token"),
                "email": email
            }
        else:
            return {
                "success": False,
                "error": response.text,
                "status_code": response.status_code
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

def login_user(email, password="TestPassword123!"):
    """Login existing user"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "token": data.get("token"),
                "user": data.get("user")
            }
        else:
            return {
                "success": False,
                "error": response.text,
                "status_code": response.status_code
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

def check_feature_access(token, feature_name, amount=1):
    """Check feature access"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/subscription/check-access",
            json={
                "feature_name": feature_name,
                "amount": amount
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        return {
            "status_code": response.status_code,
            "data": response.json() if response.status_code in [200, 402] else None,
            "text": response.text
        }
    except Exception as e:
        return {"error": str(e)}

def call_neuro_symbolic(token, message="Test question about quadratic equations"):
    """Call neuro-symbolic AI endpoint"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/ai/neuro-symbolic",
            json={
                "message": message,
                "subject": "Mathematics",
                "exam_mode": "JEE"
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        )
        
        return {
            "status_code": response.status_code,
            "data": response.json() if response.status_code == 200 else None,
            "text": response.text
        }
    except Exception as e:
        return {"error": str(e)}

def get_usage_info(token):
    """Get current usage information"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/subscription/usage",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        return {
            "status_code": response.status_code,
            "data": response.json() if response.status_code == 200 else None
        }
    except Exception as e:
        return {"error": str(e)}

# =============================================================================
# TEST 1: Fresh User - First AI Question (Should Work)
# =============================================================================
def test_1_fresh_user_first_question():
    """Test 1: Fresh User - First AI Question (Should Work)"""
    print("\n" + "="*80)
    print("TEST 1: Fresh User - First AI Question (Should Work)")
    print("="*80)
    
    # Step 1: Create fresh user
    timestamp = int(time.time())
    email = f"fresh_gating_test_{timestamp}@dhruvai.com"
    
    print(f"\n📝 Step 1: Creating fresh user: {email}")
    user_result = create_test_user(email, "Fresh Gating Test User")
    
    if not user_result.get("success"):
        log_test("Test 1 - User Creation", "FAIL", f"Failed to create user: {user_result.get('error')}")
        return None
    
    token = user_result["token"]
    user_id = user_result["user_id"]
    print(f"✅ User created: {user_id}")
    
    # Step 2: Check feature access for AI Mentor (should be allowed)
    print(f"\n📝 Step 2: Checking AI Mentor access (should be ALLOWED)")
    access_result = check_feature_access(token, "ai_mentor", 1)
    
    if "error" in access_result:
        log_test("Test 1 - Check Access", "FAIL", f"Error checking access: {access_result['error']}")
        return None
    
    # Validate response
    status_code = access_result["status_code"]
    data = access_result.get("data", {})
    
    print(f"   Status Code: {status_code}")
    print(f"   Response: {json.dumps(data, indent=2)}")
    
    # Check if allowed
    if status_code == 200:
        has_access = data.get("has_access", False)
        used = data.get("used", -1)
        limit = data.get("limit", -1)
        remaining = data.get("remaining", -1)
        
        # When checking with amount=1, remaining = limit - used - 1
        # For fresh user: remaining = 10 - 0 - 1 = 9
        if has_access and used == 0 and limit == 10 and remaining == 9:
            log_test("Test 1 - Check Access", "PASS", f"✅ Fresh user allowed: used={used}, limit={limit}, remaining={remaining}")
        else:
            log_test("Test 1 - Check Access", "FAIL", f"❌ Unexpected values: has_access={has_access}, used={used}, limit={limit}, remaining={remaining}")
            return None
    elif status_code == 402:
        log_test("Test 1 - Check Access", "FAIL", f"❌ Fresh user BLOCKED with 402! This is the bug. Response: {data}")
        return None
    else:
        log_test("Test 1 - Check Access", "FAIL", f"❌ Unexpected status code: {status_code}")
        return None
    
    # Step 3: Call neuro-symbolic endpoint
    print(f"\n📝 Step 3: Calling neuro-symbolic endpoint")
    ai_result = call_neuro_symbolic(token, "Explain quadratic equations")
    
    if "error" in ai_result:
        log_test("Test 1 - AI Call", "FAIL", f"Error calling AI: {ai_result['error']}")
        return None
    
    ai_status = ai_result["status_code"]
    print(f"   Status Code: {ai_status}")
    
    if ai_status == 200:
        log_test("Test 1 - AI Call", "PASS", "✅ AI question processed successfully")
    elif ai_status == 402:
        log_test("Test 1 - AI Call", "FAIL", f"❌ AI call blocked with 402! Response: {ai_result.get('text')}")
        return None
    else:
        log_test("Test 1 - AI Call", "FAIL", f"❌ Unexpected status: {ai_status}, Response: {ai_result.get('text')}")
        return None
    
    return {"token": token, "user_id": user_id, "email": email}

# =============================================================================
# TEST 2: Check Usage After First Question
# =============================================================================
def test_2_usage_after_first_question(user_data):
    """Test 2: Check Usage After First Question"""
    print("\n" + "="*80)
    print("TEST 2: Check Usage After First Question")
    print("="*80)
    
    if not user_data:
        log_test("Test 2", "SKIP", "Skipped due to Test 1 failure")
        return
    
    token = user_data["token"]
    
    print(f"\n📝 Checking feature access after first question")
    access_result = check_feature_access(token, "ai_mentor", 1)
    
    if "error" in access_result:
        log_test("Test 2", "FAIL", f"Error: {access_result['error']}")
        return
    
    status_code = access_result["status_code"]
    data = access_result.get("data", {})
    
    print(f"   Status Code: {status_code}")
    print(f"   Response: {json.dumps(data, indent=2)}")
    
    if status_code == 200:
        used = data.get("used", -1)
        limit = data.get("limit", -1)
        remaining = data.get("remaining", -1)
        has_access = data.get("has_access", False)
        
        # After 1 use, with amount=1 check: remaining = 10 - 1 - 1 = 8
        if used == 1 and limit == 10 and remaining == 8 and has_access:
            log_test("Test 2", "PASS", f"✅ Usage tracked correctly: used={used}, limit={limit}, remaining={remaining}")
        else:
            log_test("Test 2", "FAIL", f"❌ Unexpected values: used={used}, limit={limit}, remaining={remaining}, has_access={has_access}")
    else:
        log_test("Test 2", "FAIL", f"❌ Unexpected status: {status_code}")

# =============================================================================
# TEST 3: Exhaust Free Tier AI Questions
# =============================================================================
def test_3_exhaust_free_tier(user_data):
    """Test 3: Exhaust Free Tier AI Questions"""
    print("\n" + "="*80)
    print("TEST 3: Exhaust Free Tier AI Questions")
    print("="*80)
    
    if not user_data:
        log_test("Test 3", "SKIP", "Skipped due to Test 1 failure")
        return
    
    token = user_data["token"]
    
    # We already used 1, so we need to use 9 more to reach limit
    print(f"\n📝 Simulating 9 more AI questions (questions 2-10)")
    
    for i in range(2, 11):
        print(f"   Question {i}/10...")
        # Check access
        access_result = check_feature_access(token, "ai_mentor", 1)
        if access_result.get("status_code") != 200:
            log_test("Test 3", "FAIL", f"❌ Question {i} blocked unexpectedly")
            return
        
        # Call AI (simulated by just tracking usage)
        # In real scenario, we'd call neuro-symbolic endpoint
        time.sleep(0.2)  # Small delay to avoid rate limiting
    
    print(f"\n📝 Checking access for 11th question (should be BLOCKED)")
    access_result = check_feature_access(token, "ai_mentor", 1)
    
    status_code = access_result["status_code"]
    data = access_result.get("data", {})
    
    print(f"   Status Code: {status_code}")
    print(f"   Response: {json.dumps(data, indent=2)}")
    
    if status_code == 402:
        used = data.get("used", -1)
        limit = data.get("limit", -1)
        remaining = data.get("remaining", -1)
        upgrade_message = data.get("upsell_info", {}).get("upgrade_message")
        
        if used == 10 and limit == 10 and remaining == 0 and upgrade_message:
            log_test("Test 3", "PASS", f"✅ Correctly blocked at limit: used={used}, limit={limit}, upgrade_message present")
        else:
            log_test("Test 3", "FAIL", f"❌ Blocked but unexpected values: used={used}, limit={limit}, remaining={remaining}")
    elif status_code == 200:
        log_test("Test 3", "FAIL", "❌ 11th question NOT blocked! Should return 402")
    else:
        log_test("Test 3", "FAIL", f"❌ Unexpected status: {status_code}")

# =============================================================================
# TEST 4: Fresh User - Mock Tests (Should Work)
# =============================================================================
def test_4_fresh_user_mock_tests():
    """Test 4: Fresh User - Mock Tests (Should Work)"""
    print("\n" + "="*80)
    print("TEST 4: Fresh User - Mock Tests (Should Work)")
    print("="*80)
    
    timestamp = int(time.time())
    email = f"fresh_mock_test_{timestamp}@dhruvai.com"
    
    print(f"\n📝 Creating fresh user: {email}")
    user_result = create_test_user(email, "Fresh Mock Test User")
    
    if not user_result.get("success"):
        log_test("Test 4", "FAIL", f"Failed to create user: {user_result.get('error')}")
        return
    
    token = user_result["token"]
    
    print(f"\n📝 Checking mock_tests access")
    access_result = check_feature_access(token, "mock_tests", 1)
    
    status_code = access_result["status_code"]
    data = access_result.get("data", {})
    
    print(f"   Status Code: {status_code}")
    print(f"   Response: {json.dumps(data, indent=2)}")
    
    if status_code == 200:
        has_access = data.get("has_access", False)
        used = data.get("used", -1)
        limit = data.get("limit", -1)
        remaining = data.get("remaining", -1)
        
        # Fresh user with amount=1: remaining = 2 - 0 - 1 = 1
        if has_access and used == 0 and limit == 2 and remaining == 1:
            log_test("Test 4", "PASS", f"✅ Mock tests access granted: used={used}, limit={limit}, remaining={remaining}")
        else:
            log_test("Test 4", "FAIL", f"❌ Unexpected values: has_access={has_access}, used={used}, limit={limit}, remaining={remaining}")
    else:
        log_test("Test 4", "FAIL", f"❌ Unexpected status: {status_code}")

# =============================================================================
# TEST 5: Fresh User - Auto Notes (Should Work)
# =============================================================================
def test_5_fresh_user_auto_notes():
    """Test 5: Fresh User - Auto Notes (Should Work)"""
    print("\n" + "="*80)
    print("TEST 5: Fresh User - Auto Notes (Should Work)")
    print("="*80)
    
    timestamp = int(time.time())
    email = f"fresh_auto_notes_{timestamp}@dhruvai.com"
    
    print(f"\n📝 Creating fresh user: {email}")
    user_result = create_test_user(email, "Fresh Auto Notes User")
    
    if not user_result.get("success"):
        log_test("Test 5", "FAIL", f"Failed to create user: {user_result.get('error')}")
        return
    
    token = user_result["token"]
    
    print(f"\n📝 Checking auto_notes access")
    access_result = check_feature_access(token, "auto_notes", 1)
    
    status_code = access_result["status_code"]
    data = access_result.get("data", {})
    
    print(f"   Status Code: {status_code}")
    print(f"   Response: {json.dumps(data, indent=2)}")
    
    if status_code == 200:
        has_access = data.get("has_access", False)
        used = data.get("used", -1)
        limit = data.get("limit", -1)
        remaining = data.get("remaining", -1)
        
        # Fresh user with amount=1: remaining = 5 - 0 - 1 = 4
        if has_access and used == 0 and limit == 5 and remaining == 4:
            log_test("Test 5", "PASS", f"✅ Auto notes access granted: used={used}, limit={limit}, remaining={remaining}")
        else:
            log_test("Test 5", "FAIL", f"❌ Unexpected values: has_access={has_access}, used={used}, limit={limit}, remaining={remaining}")
    else:
        log_test("Test 5", "FAIL", f"❌ Unexpected status: {status_code}")

# =============================================================================
# TEST 6: Verify Tier Detection
# =============================================================================
def test_6_tier_detection():
    """Test 6: Verify Tier Detection"""
    print("\n" + "="*80)
    print("TEST 6: Verify Tier Detection")
    print("="*80)
    
    timestamp = int(time.time())
    email = f"tier_detection_{timestamp}@dhruvai.com"
    
    print(f"\n📝 Creating fresh user: {email}")
    user_result = create_test_user(email, "Tier Detection User")
    
    if not user_result.get("success"):
        log_test("Test 6", "FAIL", f"Failed to create user: {user_result.get('error')}")
        return
    
    token = user_result["token"]
    
    print(f"\n📝 Getting subscription info")
    try:
        response = requests.get(
            f"{BACKEND_URL}/subscription/info",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            tier = data.get("subscription_tier")
            
            print(f"   Subscription Tier: {tier}")
            print(f"   Response: {json.dumps(data, indent=2)}")
            
            if tier == "free":
                log_test("Test 6", "PASS", f"✅ Tier correctly detected as 'free'")
            elif tier in ["unknown", None]:
                log_test("Test 6", "FAIL", f"❌ Tier is '{tier}' - should be 'free'")
            else:
                log_test("Test 6", "WARN", f"⚠️ Tier is '{tier}' - expected 'free'")
        else:
            log_test("Test 6", "FAIL", f"❌ Failed to get subscription info: {response.status_code}")
    except Exception as e:
        log_test("Test 6", "FAIL", f"Error: {str(e)}")

# =============================================================================
# TEST 7: Check Current Usage Logic
# =============================================================================
def test_7_current_usage_logic():
    """Test 7: Check Current Usage Logic"""
    print("\n" + "="*80)
    print("TEST 7: Check Current Usage Logic")
    print("="*80)
    
    timestamp = int(time.time())
    email = f"usage_logic_{timestamp}@dhruvai.com"
    
    print(f"\n📝 Creating fresh user: {email}")
    user_result = create_test_user(email, "Usage Logic User")
    
    if not user_result.get("success"):
        log_test("Test 7", "FAIL", f"Failed to create user: {user_result.get('error')}")
        return
    
    token = user_result["token"]
    
    print(f"\n📝 Getting usage info")
    usage_result = get_usage_info(token)
    
    if "error" in usage_result:
        log_test("Test 7", "FAIL", f"Error: {usage_result['error']}")
        return
    
    if usage_result["status_code"] == 200:
        data = usage_result["data"]
        usage = data.get("usage", {})
        
        print(f"   Usage Data: {json.dumps(usage, indent=2)}")
        
        # Check ai_mentor
        ai_mentor = usage.get("ai_mentor", {})
        mock_tests = usage.get("mock_tests", {})
        auto_notes = usage.get("auto_notes", {})
        
        checks = []
        
        # AI Mentor check
        if ai_mentor.get("used") == 0 and ai_mentor.get("limit") == 10 and ai_mentor.get("remaining") == 10:
            checks.append(("ai_mentor", True))
        else:
            checks.append(("ai_mentor", False))
        
        # Mock Tests check
        if mock_tests.get("used") == 0 and mock_tests.get("limit") == 2 and mock_tests.get("remaining") == 2:
            checks.append(("mock_tests", True))
        else:
            checks.append(("mock_tests", False))
        
        # Auto Notes check
        if auto_notes.get("used") == 0 and auto_notes.get("limit") == 5 and auto_notes.get("remaining") == 5:
            checks.append(("auto_notes", True))
        else:
            checks.append(("auto_notes", False))
        
        all_passed = all(check[1] for check in checks)
        
        if all_passed:
            log_test("Test 7", "PASS", "✅ All usage values correct for fresh user")
        else:
            failed = [check[0] for check in checks if not check[1]]
            log_test("Test 7", "FAIL", f"❌ Incorrect usage for: {', '.join(failed)}")
    else:
        log_test("Test 7", "FAIL", f"❌ Failed to get usage: {usage_result['status_code']}")

# =============================================================================
# MAIN TEST EXECUTION
# =============================================================================
def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("SUBSCRIPTION GATING BUG FIX - BACKEND TESTING")
    print("="*80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Start Time: {datetime.now().isoformat()}")
    
    # Run tests
    user_data = test_1_fresh_user_first_question()
    test_2_usage_after_first_question(user_data)
    test_3_exhaust_free_tier(user_data)
    test_4_fresh_user_mock_tests()
    test_5_fresh_user_auto_notes()
    test_6_tier_detection()
    test_7_current_usage_logic()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for r in test_results if r["status"] == "PASS")
    failed = sum(1 for r in test_results if r["status"] == "FAIL")
    warned = sum(1 for r in test_results if r["status"] == "WARN")
    skipped = sum(1 for r in test_results if r["status"] == "SKIP")
    total = len(test_results)
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Warnings: {warned}")
    print(f"⏭️  Skipped: {skipped}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Subscription gating bug is FIXED.")
    else:
        print(f"\n⚠️  {failed} TEST(S) FAILED. Review details above.")
    
    # Detailed results
    print("\n" + "="*80)
    print("DETAILED RESULTS")
    print("="*80)
    for result in test_results:
        status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️" if result["status"] == "WARN" else "⏭️"
        print(f"\n{status_icon} {result['test']}")
        print(f"   Status: {result['status']}")
        print(f"   Details: {result['details']}")

if __name__ == "__main__":
    main()
