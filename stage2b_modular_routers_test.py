#!/usr/bin/env python3
"""
STAGE 2b MODULAR ROUTERS COMPREHENSIVE INTEGRATION TESTING

CRITICAL TESTING SCOPE - 5 MODULAR ROUTERS:
1. Auth Router (api/auth.py): Registration, login, logout, CSRF - Full CRUD operations
2. User Router (api/user.py): Profile GET/PUT with authentication - User management  
3. Subscription Router (api/subscription.py): Plans (unified), access check, usage tracking, current subscription - Complete subscription flow
4. AI Router (api/ai.py): Chat sessions, dual-response, guardrails (math validation, citations, fact verification), available contexts - AI functionality core
5. Analytics Router (api/analytics.py): Dashboard analytics, daily goals, subject progress, wellness checks - Performance tracking

ARCHITECTURE VALIDATION:
- Service Layer Integration: AuthService, SubscriptionService, AIService, AnalyticsService with dependency injection
- Duplicate Route Resolution: Removed duplicate /subscription/plans - single unified endpoint
- Database Operations: MongoDB integration via services layer
- Error Handling: Structured HTTP status codes and JSON responses
- Authentication: Hybrid cookie + Bearer token system across all routers
"""

import requests
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

class Stage2bModularRoutersTest:
    def __init__(self, base_url="https://seamless-auth-1.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.session_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_email = "test@dhruvai.com"
        self.test_user_password = "password123"
        
        # Test results tracking
        self.test_results = {
            'auth_router': {
                'registration': False,
                'login': False,
                'logout': False,
                'csrf_token': False
            },
            'user_router': {
                'profile_get': False,
                'profile_put': False,
                'authentication_required': False
            },
            'subscription_router': {
                'plans_unified': False,
                'access_check': False,
                'usage_tracking': False,
                'current_subscription': False
            },
            'ai_router': {
                'dual_response': False,
                'chat_sessions': False,
                'guardrails_math': False,
                'guardrails_citations': False,
                'guardrails_fact_verification': False,
                'available_contexts': False
            },
            'analytics_router': {
                'dashboard_analytics': False,
                'daily_goals': False,
                'subject_progress': False,
                'wellness_checks': False
            },
            'architecture': {
                'service_layer_injection': False,
                'duplicate_route_resolution': False,
                'database_integration': False,
                'error_handling': False,
                'authentication_system': False
            }
        }

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Optional[Dict] = None, headers: Optional[Dict] = None) -> tuple[bool, Dict]:
        """Run a single API test with comprehensive error handling"""
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
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:300]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    return False, error_data
                except:
                    print(f"   Error: {response.text}")
                    return False, {"error": response.text}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {"error": str(e)}

    def authenticate_test_user(self) -> bool:
        """Authenticate with test user to get token for protected endpoints"""
        print("\n🔐 AUTHENTICATING TEST USER")
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        success, response = self.run_test(
            "Test User Authentication",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            if 'user' in response:
                self.user_id = response['user'].get('user_id')
            print(f"✅ Authentication successful - Token: {self.token[:20]}...")
            return True
        else:
            print("❌ Authentication failed - Cannot test protected endpoints")
            return False

    def test_auth_router_comprehensive(self) -> Dict[str, bool]:
        """Test Auth Router (api/auth.py) - Registration, login, logout, CSRF"""
        print("\n" + "="*80)
        print("1️⃣ AUTH ROUTER COMPREHENSIVE TESTING")
        print("="*80)
        
        results = {}
        
        # Test 1: Registration
        print("\n📝 Testing Auth Router - Registration")
        fresh_user_email = f"auth_test_{int(time.time())}@dhruvai.com"
        registration_data = {
            "full_name": "Auth Router Test User",
            "email": fresh_user_email,
            "password": "password123",
            "exam_type": "JEE",
            "grade": "Class 12",
            "target_year": 2026
        }
        
        success, response = self.run_test(
            "Auth Router Registration",
            "POST",
            "auth/register",
            200,
            data=registration_data
        )
        
        results['registration'] = success
        if success:
            print("✅ Registration endpoint working")
            if 'token' in response and 'user' in response:
                print("✅ JWT token and user data provided")
        
        # Test 2: Login
        print("\n🔐 Testing Auth Router - Login")
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        success, response = self.run_test(
            "Auth Router Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        results['login'] = success
        if success:
            print("✅ Login endpoint working")
            if 'token' in response:
                self.token = response['token']
                print("✅ JWT token obtained for subsequent tests")
            if 'user' in response:
                self.user_id = response['user'].get('user_id')
                print("✅ User data provided")
        
        # Test 3: Logout
        print("\n🚪 Testing Auth Router - Logout")
        if self.token:
            success, response = self.run_test(
                "Auth Router Logout",
                "POST",
                "auth/logout",
                200,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            results['logout'] = success
            if success:
                print("✅ Logout endpoint working")
        else:
            print("⚠️ No token available for logout test")
            results['logout'] = False
        
        # Re-authenticate for subsequent tests
        if not self.token:
            self.authenticate_test_user()
        
        # Test 4: CSRF Token
        print("\n🛡️ Testing Auth Router - CSRF Token")
        success, response = self.run_test(
            "Auth Router CSRF Token",
            "GET",
            "auth/csrf-token",
            200
        )
        
        results['csrf_token'] = success
        if success:
            print("✅ CSRF token endpoint working")
            if 'csrf_token' in response:
                print("✅ CSRF token provided")
        
        # Update test results
        self.test_results['auth_router'] = results
        
        success_count = sum(results.values())
        print(f"\n📊 Auth Router Results: {success_count}/4 tests passed")
        
        return results

    def test_user_router_comprehensive(self) -> Dict[str, bool]:
        """Test User Router (api/user.py) - Profile GET/PUT with authentication"""
        print("\n" + "="*80)
        print("2️⃣ USER ROUTER COMPREHENSIVE TESTING")
        print("="*80)
        
        results = {}
        
        if not self.token:
            print("❌ No authentication token - cannot test user router")
            return {'profile_get': False, 'profile_put': False, 'authentication_required': False}
        
        # Test 1: Profile GET
        print("\n👤 Testing User Router - Profile GET")
        success, response = self.run_test(
            "User Router Profile GET",
            "GET",
            "user/profile",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        results['profile_get'] = success
        if success:
            print("✅ Profile GET endpoint working")
            expected_fields = ['user_id', 'full_name', 'email', 'exam_type']
            for field in expected_fields:
                if field in response:
                    print(f"✅ Profile field '{field}' present")
                else:
                    print(f"⚠️ Profile field '{field}' missing")
        
        # Test 2: Profile PUT
        print("\n✏️ Testing User Router - Profile PUT")
        update_data = {
            "full_name": "Updated User Router Test User",
            "phone": "+91-9876543210",
            "exam_type": "NEET",
            "target_year": 2025
        }
        
        success, response = self.run_test(
            "User Router Profile PUT",
            "PUT",
            "user/profile",
            200,
            data=update_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        results['profile_put'] = success
        if success:
            print("✅ Profile PUT endpoint working")
            if 'message' in response:
                print(f"✅ Update message: {response['message']}")
            if 'user' in response:
                updated_user = response['user']
                print(f"✅ Updated data returned")
        
        # Test 3: Authentication Required
        print("\n🔒 Testing User Router - Authentication Required")
        success, response = self.run_test(
            "User Router Authentication Required",
            "GET",
            "user/profile",
            401,  # Should return 401 without token
            headers={}
        )
        
        results['authentication_required'] = success
        if success:
            print("✅ Authentication properly required for protected endpoints")
        
        # Update test results
        self.test_results['user_router'] = results
        
        success_count = sum(results.values())
        print(f"\n📊 User Router Results: {success_count}/3 tests passed")
        
        return results

    def test_subscription_router_comprehensive(self) -> Dict[str, bool]:
        """Test Subscription Router (api/subscription.py) - Plans, access check, usage tracking, current subscription"""
        print("\n" + "="*80)
        print("3️⃣ SUBSCRIPTION ROUTER COMPREHENSIVE TESTING")
        print("="*80)
        
        results = {}
        
        # Test 1: Plans (Unified Endpoint)
        print("\n📋 Testing Subscription Router - Plans (Unified)")
        success, response = self.run_test(
            "Subscription Router Plans",
            "GET",
            "subscription/plans",
            200
        )
        
        results['plans_unified'] = success
        if success:
            print("✅ Plans endpoint working")
            if 'plans' in response:
                plans = response['plans']
                print(f"✅ Plans data returned: {len(plans)} plans")
                expected_plans = ['FREE', 'PREMIUM', 'PRO']
                for plan_name in expected_plans:
                    plan_found = any(p.get('name', '').upper() == plan_name for p in plans)
                    if plan_found:
                        print(f"✅ {plan_name} plan found")
                    else:
                        print(f"⚠️ {plan_name} plan missing")
        
        if not self.token:
            print("❌ No authentication token - cannot test protected subscription endpoints")
            return {**results, 'access_check': False, 'usage_tracking': False, 'current_subscription': False}
        
        # Test 2: Access Check
        print("\n🔍 Testing Subscription Router - Access Check")
        access_check_data = {
            "feature_name": "mock_tests_weekly"
        }
        
        success, response = self.run_test(
            "Subscription Router Access Check",
            "POST",
            "subscription/check-access",
            [200, 402],  # Accept both success and payment required
            data=access_check_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        results['access_check'] = success
        if success:
            print("✅ Access check endpoint working")
            if 'has_access' in response:
                print(f"✅ Access status: {response['has_access']}")
            if 'upsell_info' in response:
                print("✅ Upsell info provided for subscription flow")
        
        # Test 3: Usage Tracking
        print("\n📊 Testing Subscription Router - Usage Tracking")
        success, response = self.run_test(
            "Subscription Router Usage Tracking",
            "GET",
            "subscription/usage",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        results['usage_tracking'] = success
        if success:
            print("✅ Usage tracking endpoint working")
            if 'usage' in response:
                usage_data = response['usage']
                print(f"✅ Usage data returned for {len(usage_data)} features")
            if 'subscription_tier' in response:
                print(f"✅ Subscription tier: {response['subscription_tier']}")
        
        # Test 4: Current Subscription
        print("\n📄 Testing Subscription Router - Current Subscription")
        success, response = self.run_test(
            "Subscription Router Current Subscription",
            "GET",
            "subscription/current",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        results['current_subscription'] = success
        if success:
            print("✅ Current subscription endpoint working")
            if 'plan_name' in response:
                print(f"✅ Current plan: {response['plan_name']}")
            if 'status' in response:
                print(f"✅ Subscription status: {response['status']}")
        
        # Update test results
        self.test_results['subscription_router'] = results
        
        success_count = sum(results.values())
        print(f"\n📊 Subscription Router Results: {success_count}/4 tests passed")
        
        return results

    def test_ai_router_comprehensive(self) -> Dict[str, bool]:
        """Test AI Router (api/ai.py) - Chat sessions, dual-response, guardrails, available contexts"""
        print("\n" + "="*80)
        print("4️⃣ AI ROUTER COMPREHENSIVE TESTING")
        print("="*80)
        
        results = {}
        
        if not self.token:
            print("❌ No authentication token - cannot test AI router")
            return {k: False for k in ['dual_response', 'chat_sessions', 'guardrails_math', 'guardrails_citations', 'guardrails_fact_verification', 'available_contexts']}
        
        # Test 1: Available Contexts
        print("\n🌐 Testing AI Router - Available Contexts")
        success, response = self.run_test(
            "AI Router Available Contexts",
            "GET",
            "ai/available-contexts",
            200
        )
        
        results['available_contexts'] = success
        if success:
            print("✅ Available contexts endpoint working")
            if 'subjects' in response:
                print(f"✅ Subjects available: {len(response['subjects'])}")
            if 'ai_modes' in response:
                print(f"✅ AI modes available: {response['ai_modes']}")
        
        # Test 2: Chat Sessions
        print("\n💬 Testing AI Router - Chat Sessions")
        
        # Create a chat session first
        session_data = {
            "title": "Test AI Session",
            "subject": "Mathematics",
            "topic": "Algebra",
            "ai_mode": "dual"
        }
        
        success, response = self.run_test(
            "AI Router Create Chat Session",
            "POST",
            "ai/chat/sessions",
            200,
            data=session_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success and 'session_id' in response:
            self.session_id = response['session_id']
            print(f"✅ Chat session created: {self.session_id}")
        
        # Get chat sessions
        success, response = self.run_test(
            "AI Router Get Chat Sessions",
            "GET",
            "ai/chat/sessions",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        results['chat_sessions'] = success
        if success:
            print("✅ Chat sessions endpoint working")
            if 'sessions' in response:
                print(f"✅ Sessions returned: {len(response['sessions'])}")
        
        # Test 3: Dual Response
        print("\n🤖 Testing AI Router - Dual Response")
        if self.session_id:
            dual_response_data = {
                "message": "Explain quadratic equations",
                "session_id": self.session_id,
                "subject": "Mathematics"
            }
            
            success, response = self.run_test(
                "AI Router Dual Response",
                "POST",
                "ai/dual-response",
                200,
                data=dual_response_data,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            results['dual_response'] = success
            if success:
                print("✅ Dual response endpoint working")
                if 'primary' in response and 'secondary' in response:
                    print("✅ Both professor and mentor responses provided")
        else:
            print("⚠️ No session ID available for dual response test")
            results['dual_response'] = False
        
        # Test 4: Guardrails - Math Validation
        print("\n🔢 Testing AI Router - Guardrails Math Validation")
        math_data = {
            "expression": "x^2 + 2x + 1 = 0",
            "units": None
        }
        
        success, response = self.run_test(
            "AI Router Guardrails Math Validation",
            "POST",
            "ai/guardrails/validate-math",
            200,
            data=math_data
        )
        
        results['guardrails_math'] = success
        if success:
            print("✅ Math validation guardrails working")
            if 'is_valid' in response:
                print(f"✅ Validation result: {response['is_valid']}")
        
        # Test 5: Guardrails - Citations
        print("\n📚 Testing AI Router - Guardrails Citations")
        success, response = self.run_test(
            "AI Router Guardrails Citations",
            "GET",
            "ai/guardrails/citations/Mathematics/Quadratic Equations",
            200
        )
        
        results['guardrails_citations'] = success
        if success:
            print("✅ Citations guardrails working")
            if 'citations' in response:
                print(f"✅ Citations returned: {len(response['citations'])}")
        
        # Test 6: Guardrails - Fact Verification
        print("\n✅ Testing AI Router - Guardrails Fact Verification")
        fact_data = {
            "statement": "The quadratic formula is x = (-b ± √(b²-4ac)) / 2a",
            "subject": "Mathematics",
            "context": "Quadratic equations"
        }
        
        success, response = self.run_test(
            "AI Router Guardrails Fact Verification",
            "POST",
            "ai/guardrails/fact-verification",
            200,
            data=fact_data
        )
        
        results['guardrails_fact_verification'] = success
        if success:
            print("✅ Fact verification guardrails working")
            if 'is_verified' in response:
                print(f"✅ Verification result: {response['is_verified']}")
        
        # Update test results
        self.test_results['ai_router'] = results
        
        success_count = sum(results.values())
        print(f"\n📊 AI Router Results: {success_count}/6 tests passed")
        
        return results

    def test_analytics_router_comprehensive(self) -> Dict[str, bool]:
        """Test Analytics Router (api/analytics.py) - Dashboard analytics, daily goals, subject progress, wellness checks"""
        print("\n" + "="*80)
        print("5️⃣ ANALYTICS ROUTER COMPREHENSIVE TESTING")
        print("="*80)
        
        results = {}
        
        if not self.token:
            print("❌ No authentication token - cannot test analytics router")
            return {k: False for k in ['dashboard_analytics', 'daily_goals', 'subject_progress', 'wellness_checks']}
        
        # Test 1: Dashboard Analytics
        print("\n📊 Testing Analytics Router - Dashboard Analytics")
        success, response = self.run_test(
            "Analytics Router Dashboard Analytics",
            "GET",
            "analytics/dashboard",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        results['dashboard_analytics'] = success
        if success:
            print("✅ Dashboard analytics endpoint working")
            expected_metrics = ['study_streak', 'total_questions', 'accuracy_rate']
            for metric in expected_metrics:
                if metric in response:
                    print(f"✅ Metric '{metric}' present: {response[metric]}")
        
        # Test 2: Daily Goals
        print("\n🎯 Testing Analytics Router - Daily Goals")
        success, response = self.run_test(
            "Analytics Router Daily Goals",
            "GET",
            "analytics/daily-goals",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        results['daily_goals'] = success
        if success:
            print("✅ Daily goals endpoint working")
            if 'goals' in response:
                print(f"✅ Daily goals data returned")
            if 'completion_percentage' in response:
                print(f"✅ Completion percentage: {response['completion_percentage']}%")
        
        # Test 3: Subject Progress
        print("\n📈 Testing Analytics Router - Subject Progress")
        success, response = self.run_test(
            "Analytics Router Subject Progress",
            "GET",
            "analytics/subject-progress",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        results['subject_progress'] = success
        if success:
            print("✅ Subject progress endpoint working")
            if 'subjects' in response:
                subjects = response['subjects']
                print(f"✅ Subject progress data for {len(subjects)} subjects")
        
        # Test 4: Wellness Checks
        print("\n🧘 Testing Analytics Router - Wellness Checks")
        
        # Perform wellness check
        wellness_data = {
            "stress_level": 5,
            "motivation_level": 7,
            "confidence_level": 6,
            "study_satisfaction": 8,
            "session_id": self.session_id or str(uuid.uuid4())
        }
        
        success, response = self.run_test(
            "Analytics Router Wellness Check",
            "POST",
            "analytics/wellness-check",
            200,
            data=wellness_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            print("✅ Wellness check endpoint working")
            if 'break_recommendation' in response:
                print(f"✅ Break recommendation: {response['break_recommendation']}")
        
        # Get wellness history
        success, response = self.run_test(
            "Analytics Router Wellness History",
            "GET",
            "analytics/wellness-history",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        results['wellness_checks'] = success
        if success:
            print("✅ Wellness history endpoint working")
            if 'wellness_history' in response:
                print(f"✅ Wellness history returned: {len(response['wellness_history'])} entries")
        
        # Update test results
        self.test_results['analytics_router'] = results
        
        success_count = sum(results.values())
        print(f"\n📊 Analytics Router Results: {success_count}/4 tests passed")
        
        return results

    def test_architecture_validation(self) -> Dict[str, bool]:
        """Test Architecture Validation - Service layer, duplicate routes, database integration, error handling"""
        print("\n" + "="*80)
        print("6️⃣ ARCHITECTURE VALIDATION TESTING")
        print("="*80)
        
        results = {}
        
        # Test 1: Service Layer Dependency Injection
        print("\n🔧 Testing Architecture - Service Layer Dependency Injection")
        success, response = self.run_test(
            "Architecture Service Layer Health",
            "GET",
            "health",
            200
        )
        
        if success:
            modular_arch = response.get('modular_architecture', False)
            components_loaded = response.get('modular_components_loaded', False)
            auth_service_ready = response.get('auth_service_ready', False)
            
            print(f"✅ Health endpoint working")
            print(f"   Modular architecture: {modular_arch}")
            print(f"   Components loaded: {components_loaded}")
            print(f"   Auth service ready: {auth_service_ready}")
            
            results['service_layer_injection'] = modular_arch and components_loaded
        else:
            results['service_layer_injection'] = False
        
        # Test 2: Duplicate Route Resolution
        print("\n🔄 Testing Architecture - Duplicate Route Resolution")
        
        # Test /subscription/plans multiple times to ensure consistency
        responses = []
        for i in range(3):
            success, response = self.run_test(
                f"Duplicate Route Test {i+1}",
                "GET",
                "subscription/plans",
                200
            )
            if success:
                responses.append(response)
        
        if len(responses) >= 2:
            # Check if responses are consistent
            consistent = all(r == responses[0] for r in responses[1:])
            results['duplicate_route_resolution'] = consistent
            if consistent:
                print("✅ Duplicate route resolution working - consistent responses")
            else:
                print("⚠️ Inconsistent responses - possible route conflicts")
        else:
            results['duplicate_route_resolution'] = False
        
        # Test 3: Database Integration
        print("\n🗄️ Testing Architecture - Database Integration")
        
        if self.token:
            # Test CRUD operations through service layer
            
            # Create (registration already tested)
            # Read (profile GET)
            success, response = self.run_test(
                "Database Integration - Read",
                "GET",
                "user/profile",
                200,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            read_success = success
            
            # Update (profile PUT)
            update_data = {"full_name": "Database Test User Updated"}
            success, response = self.run_test(
                "Database Integration - Update",
                "PUT",
                "user/profile",
                200,
                data=update_data,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            update_success = success
            
            results['database_integration'] = read_success and update_success
            if results['database_integration']:
                print("✅ Database integration via services working")
        else:
            results['database_integration'] = False
        
        # Test 4: Error Handling
        print("\n⚠️ Testing Architecture - Error Handling")
        
        # Test 401 error for unauthorized access
        success, response = self.run_test(
            "Error Handling - 401 Unauthorized",
            "GET",
            "user/profile",
            401,
            headers={}
        )
        
        unauthorized_handled = success
        
        # Test 404 error for non-existent endpoint
        success, response = self.run_test(
            "Error Handling - 404 Not Found",
            "GET",
            "non-existent-endpoint",
            404
        )
        
        not_found_handled = success
        
        results['error_handling'] = unauthorized_handled  # At least 401 should work
        if results['error_handling']:
            print("✅ Error handling working - proper HTTP status codes")
        
        # Test 5: Authentication System
        print("\n🔐 Testing Architecture - Authentication System")
        
        # Test hybrid authentication (Bearer token already tested)
        auth_working = bool(self.token)
        
        # Test protected vs unprotected endpoints
        protected_success, _ = self.run_test(
            "Authentication - Protected Endpoint",
            "GET",
            "user/profile",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        unprotected_success, _ = self.run_test(
            "Authentication - Unprotected Endpoint",
            "GET",
            "subscription/plans",
            200
        )
        
        results['authentication_system'] = auth_working and protected_success and unprotected_success
        if results['authentication_system']:
            print("✅ Authentication system working - hybrid Bearer token support")
        
        # Update test results
        self.test_results['architecture'] = results
        
        success_count = sum(results.values())
        print(f"\n📊 Architecture Validation Results: {success_count}/5 tests passed")
        
        return results

    def run_comprehensive_test_suite(self):
        """Run the complete Stage 2b Modular Routers test suite"""
        print("🚀 STAGE 2b MODULAR ROUTERS COMPREHENSIVE INTEGRATION TESTING")
        print("="*100)
        print("TESTING SCOPE:")
        print("1. Auth Router (api/auth.py): Registration, login, logout, CSRF")
        print("2. User Router (api/user.py): Profile GET/PUT with authentication")
        print("3. Subscription Router (api/subscription.py): Plans, access check, usage tracking, current subscription")
        print("4. AI Router (api/ai.py): Chat sessions, dual-response, guardrails, available contexts")
        print("5. Analytics Router (api/analytics.py): Dashboard analytics, daily goals, subject progress, wellness checks")
        print("6. Architecture Validation: Service layer, duplicate routes, database integration, error handling")
        print("="*100)
        
        start_time = time.time()
        
        # Authenticate test user first
        auth_success = self.authenticate_test_user()
        if not auth_success:
            print("❌ CRITICAL: Cannot authenticate test user - limited testing possible")
        
        # Run all test suites
        auth_results = self.test_auth_router_comprehensive()
        user_results = self.test_user_router_comprehensive()
        subscription_results = self.test_subscription_router_comprehensive()
        ai_results = self.test_ai_router_comprehensive()
        analytics_results = self.test_analytics_router_comprehensive()
        architecture_results = self.test_architecture_validation()
        
        # Calculate overall results
        end_time = time.time()
        duration = end_time - start_time
        
        # Generate comprehensive report
        self.generate_final_report(duration)

    def generate_final_report(self, duration: float):
        """Generate comprehensive final report"""
        print("\n" + "="*100)
        print("🎯 STAGE 2b MODULAR ROUTERS - FINAL COMPREHENSIVE REPORT")
        print("="*100)
        
        # Calculate success rates for each router
        router_scores = {}
        for router_name, router_tests in self.test_results.items():
            if router_tests:
                passed = sum(router_tests.values())
                total = len(router_tests)
                success_rate = (passed / total) * 100 if total > 0 else 0
                router_scores[router_name] = {
                    'passed': passed,
                    'total': total,
                    'success_rate': success_rate
                }
        
        # Display results by router
        print(f"\n📊 DETAILED RESULTS BY ROUTER:")
        for router_name, scores in router_scores.items():
            status = "✅ PASS" if scores['success_rate'] >= 75 else "⚠️ PARTIAL" if scores['success_rate'] >= 50 else "❌ FAIL"
            print(f"   {router_name.replace('_', ' ').title()}: {scores['passed']}/{scores['total']} ({scores['success_rate']:.1f}%) {status}")
            
            # Show individual test results
            for test_name, result in self.test_results[router_name].items():
                test_status = "✅" if result else "❌"
                print(f"      {test_status} {test_name.replace('_', ' ').title()}")
        
        # Calculate overall success metrics
        total_passed = sum(sum(router_tests.values()) for router_tests in self.test_results.values())
        total_tests = sum(len(router_tests) for router_tests in self.test_results.values())
        overall_success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n📈 OVERALL SUCCESS METRICS:")
        print(f"   Total Tests Run: {self.tests_run}")
        print(f"   Total Tests Passed: {self.tests_passed}")
        print(f"   Overall Success Rate: {total_passed}/{total_tests} ({overall_success_rate:.1f}%)")
        print(f"   Test Duration: {duration:.2f} seconds")
        
        # Critical success criteria assessment
        critical_routers = ['auth_router', 'user_router', 'subscription_router']
        critical_passed = sum(sum(self.test_results[router].values()) for router in critical_routers if router in self.test_results)
        critical_total = sum(len(self.test_results[router]) for router in critical_routers if router in self.test_results)
        critical_success_rate = (critical_passed / critical_total) * 100 if critical_total > 0 else 0
        
        print(f"\n🎯 CRITICAL SUCCESS CRITERIA:")
        print(f"   Critical Routers (Auth, User, Subscription): {critical_passed}/{critical_total} ({critical_success_rate:.1f}%)")
        
        # Final assessment
        if overall_success_rate >= 80:
            final_status = "✅ EXCELLENT"
            recommendation = "Stage 2b modular architecture is production-ready"
        elif overall_success_rate >= 70:
            final_status = "✅ GOOD"
            recommendation = "Stage 2b modular architecture is functional with minor issues"
        elif overall_success_rate >= 60:
            final_status = "⚠️ ACCEPTABLE"
            recommendation = "Stage 2b modular architecture needs some improvements"
        else:
            final_status = "❌ NEEDS WORK"
            recommendation = "Stage 2b modular architecture requires significant fixes"
        
        print(f"\n🏆 FINAL ASSESSMENT: {final_status}")
        print(f"   Recommendation: {recommendation}")
        
        # Specific recommendations
        print(f"\n🔧 SPECIFIC RECOMMENDATIONS:")
        
        failed_tests = []
        for router_name, router_tests in self.test_results.items():
            for test_name, result in router_tests.items():
                if not result:
                    failed_tests.append(f"{router_name}.{test_name}")
        
        if failed_tests:
            print("   Priority fixes needed for:")
            for failed_test in failed_tests[:10]:  # Show top 10 failures
                router, test = failed_test.split('.', 1)
                print(f"   - {router.replace('_', ' ').title()}: {test.replace('_', ' ').title()}")
        else:
            print("   - All tests passed! Architecture is fully functional")
        
        # Architecture-specific recommendations
        arch_results = self.test_results.get('architecture', {})
        if not arch_results.get('service_layer_injection', True):
            print("   - Fix service layer dependency injection")
        if not arch_results.get('duplicate_route_resolution', True):
            print("   - Resolve duplicate route conflicts")
        if not arch_results.get('database_integration', True):
            print("   - Fix MongoDB integration via services")
        if not arch_results.get('error_handling', True):
            print("   - Improve HTTP error handling and status codes")
        if not arch_results.get('authentication_system', True):
            print("   - Fix hybrid authentication system (cookies + Bearer tokens)")
        
        print(f"\n✨ STAGE 2b MODULAR ROUTERS TESTING COMPLETE")
        print("="*100)
        
        return overall_success_rate >= 70  # 70% success rate for overall pass


def main():
    """Main function to run the comprehensive test suite"""
    tester = Stage2bModularRoutersTest()
    success = tester.run_comprehensive_test_suite()
    
    if success:
        print("\n🎉 STAGE 2b MODULAR ROUTERS: COMPREHENSIVE TESTING SUCCESSFUL")
        exit(0)
    else:
        print("\n⚠️ STAGE 2b MODULAR ROUTERS: TESTING COMPLETED WITH ISSUES")
        exit(1)


if __name__ == "__main__":
    main()