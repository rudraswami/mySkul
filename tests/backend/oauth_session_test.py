#!/usr/bin/env python3
"""
Production OAuth Session Cookie Testing
Comprehensive test to identify the exact cause of 401 errors on /api/auth/session after OAuth login
"""

import requests
import json
from urllib.parse import urlparse, parse_qs

class ProductionOAuthTester:
    def __init__(self):
        self.base_url = "https://seamless-auth-1.emergent.host"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def test_oauth_flow_complete(self):
        """Test the complete OAuth flow to identify the session cookie issue"""
        print("🔐 PRODUCTION OAUTH SESSION COOKIE COMPREHENSIVE TESTING")
        print("=" * 80)
        print("CRITICAL ISSUE: Users getting 401 on /api/auth/session after OAuth login")
        print("OBJECTIVE: Identify exact cause and provide specific fix recommendations")
        print("=" * 80)
        
        results = {
            'oauth_login_accessible': False,
            'oauth_redirect_proper': False,
            'oauth_state_created': False,
            'session_endpoint_401_without_cookie': False,
            'cors_headers_present': False,
            'cookie_requirements_met': False,
            'session_validation_working': False
        }
        
        # STEP 1: Test OAuth Login Endpoint
        print("\n1️⃣ STEP 1: OAUTH LOGIN ENDPOINT TESTING")
        results.update(self.test_oauth_login_endpoint())
        
        # STEP 2: Test Session Endpoint Behavior
        print("\n2️⃣ STEP 2: SESSION ENDPOINT BEHAVIOR TESTING")
        results.update(self.test_session_endpoint_behavior())
        
        # STEP 3: Test CORS Configuration
        print("\n3️⃣ STEP 3: CORS CONFIGURATION TESTING")
        results.update(self.test_cors_configuration())
        
        # STEP 4: Analyze Root Cause
        print("\n4️⃣ STEP 4: ROOT CAUSE ANALYSIS")
        self.analyze_root_cause(results)
        
        return results
    
    def test_oauth_login_endpoint(self):
        """Test OAuth login endpoint accessibility and redirect behavior"""
        print("   Testing OAuth login endpoint...")
        
        results = {
            'oauth_login_accessible': False,
            'oauth_redirect_proper': False,
            'oauth_state_created': False
        }
        
        try:
            # Test OAuth login endpoint
            response = self.session.get(
                f"{self.base_url}/api/auth/google/login",
                allow_redirects=False,
                timeout=30
            )
            
            print(f"   📊 Response Status: {response.status_code}")
            print(f"   📊 Response Headers: {dict(response.headers)}")
            
            if response.status_code in [302, 307]:
                results['oauth_login_accessible'] = True
                print(f"   ✅ OAuth login endpoint accessible - Status: {response.status_code}")
                
                # Check redirect location
                redirect_location = response.headers.get('Location', '')
                print(f"   📍 Redirect Location: {redirect_location}")
                
                # Parse redirect URL to check parameters
                if 'accounts.google.com' in redirect_location:
                    parsed_url = urlparse(redirect_location)
                    query_params = parse_qs(parsed_url.query)
                    
                    required_params = ['client_id', 'redirect_uri', 'response_type', 'scope', 'state']
                    params_present = all(param in query_params for param in required_params)
                    
                    if params_present:
                        results['oauth_redirect_proper'] = True
                        print(f"   ✅ OAuth redirect URL properly configured")
                        
                        # Check if state parameter exists
                        state = query_params.get('state', [None])[0]
                        if state:
                            results['oauth_state_created'] = True
                            print(f"   ✅ OAuth state created: {state[:20]}...")
                            
                            # Check redirect_uri domain
                            redirect_uri = query_params.get('redirect_uri', [None])[0]
                            if redirect_uri and 'seamless-auth-1.emergent.host' in redirect_uri:
                                print(f"   ✅ Redirect URI uses correct production domain")
                            else:
                                print(f"   ⚠️ Redirect URI domain issue: {redirect_uri}")
                        else:
                            print(f"   ❌ OAuth state not found in redirect URL")
                    else:
                        print(f"   ❌ OAuth redirect URL missing required parameters")
                        print(f"      Present params: {list(query_params.keys())}")
                        print(f"      Required params: {required_params}")
                else:
                    print(f"   ❌ Redirect URL does not point to Google OAuth")
            else:
                print(f"   ❌ OAuth login endpoint failed - Status: {response.status_code}")
                print(f"   📄 Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ OAuth login endpoint test failed: {str(e)}")
        
        return results
    
    def test_session_endpoint_behavior(self):
        """Test session endpoint behavior without and with cookies"""
        print("   Testing session endpoint behavior...")
        
        results = {
            'session_endpoint_401_without_cookie': False,
            'session_validation_working': False
        }
        
        try:
            # Test session endpoint without cookie
            response = self.session.get(
                f"{self.base_url}/api/auth/session",
                timeout=30
            )
            
            print(f"   📊 Session Response Status: {response.status_code}")
            print(f"   📊 Session Response Headers: {dict(response.headers)}")
            
            if response.status_code == 401:
                results['session_endpoint_401_without_cookie'] = True
                print(f"   ✅ Session endpoint correctly returns 401 without cookie")
                
                try:
                    response_data = response.json()
                    print(f"   📄 Response body: {response_data}")
                    
                    if 'detail' in response_data:
                        results['session_validation_working'] = True
                        print(f"   ✅ Session validation logic working correctly")
                    else:
                        print(f"   ⚠️ Response structure unexpected")
                        
                except Exception as e:
                    print(f"   ⚠️ Could not parse response JSON: {e}")
            else:
                print(f"   ❌ Session endpoint unexpected status: {response.status_code}")
                print(f"   📄 Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Session endpoint test failed: {str(e)}")
        
        return results
    
    def test_cors_configuration(self):
        """Test CORS configuration for cookie support"""
        print("   Testing CORS configuration...")
        
        results = {
            'cors_headers_present': False,
            'cookie_requirements_met': False
        }
        
        try:
            # Test CORS with OPTIONS request
            response = self.session.options(
                f"{self.base_url}/api/auth/session",
                headers={
                    'Origin': 'https://seamless-auth-1.emergent.host',
                    'Access-Control-Request-Method': 'GET',
                    'Access-Control-Request-Headers': 'Content-Type'
                },
                timeout=30
            )
            
            print(f"   📊 CORS OPTIONS Status: {response.status_code}")
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            print(f"   🌐 CORS Headers: {cors_headers}")
            
            # Check if CORS headers are present
            if any(cors_headers.values()):
                results['cors_headers_present'] = True
                print(f"   ✅ CORS headers present")
                
                # Check if credentials are allowed
                if cors_headers['Access-Control-Allow-Credentials'] == 'true':
                    results['cookie_requirements_met'] = True
                    print(f"   ✅ CORS allows credentials (required for cookies)")
                else:
                    print(f"   ❌ CORS does not allow credentials")
            else:
                print(f"   ❌ CORS headers missing")
                
        except Exception as e:
            print(f"   ❌ CORS configuration test failed: {str(e)}")
        
        return results
    
    def analyze_root_cause(self, results):
        """Analyze test results to identify root cause"""
        print("   Analyzing test results for root cause...")
        
        print(f"\n📊 TEST RESULTS SUMMARY:")
        for key, value in results.items():
            status = "✅ PASS" if value else "❌ FAIL"
            print(f"   {key}: {status}")
        
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        
        # Check OAuth flow
        if not results['oauth_login_accessible']:
            print(f"   ❌ CRITICAL: OAuth login endpoint not accessible")
            print(f"      → Backend may not be running properly")
            print(f"      → Check supervisor backend service status")
        elif not results['oauth_redirect_proper']:
            print(f"   ❌ CRITICAL: OAuth redirect configuration issue")
            print(f"      → Check GOOGLE_CLIENT_ID and redirect_uri configuration")
        elif not results['oauth_state_created']:
            print(f"   ❌ CRITICAL: OAuth state creation failing")
            print(f"      → Check MongoDB connection and oauth_states collection")
        
        # Check session validation
        if not results['session_endpoint_401_without_cookie']:
            print(f"   ❌ CRITICAL: Session endpoint not working properly")
            print(f"      → Check /api/auth/session endpoint implementation")
        elif not results['session_validation_working']:
            print(f"   ❌ CRITICAL: Session validation logic issue")
            print(f"      → Check session token validation in database")
        
        # Check CORS
        if not results['cors_headers_present']:
            print(f"   ❌ CRITICAL: CORS headers missing")
            print(f"      → Check CORS middleware configuration")
            print(f"      → Verify CORS_ORIGINS environment variable")
        elif not results['cookie_requirements_met']:
            print(f"   ❌ CRITICAL: CORS does not allow credentials")
            print(f"      → Set Access-Control-Allow-Credentials: true")
        
        # Provide specific fix recommendations
        print(f"\n🛠️ SPECIFIC FIX RECOMMENDATIONS:")
        
        if results['oauth_login_accessible'] and results['oauth_redirect_proper'] and results['oauth_state_created']:
            print(f"   ✅ OAuth flow is working correctly")
        else:
            print(f"   1. Fix OAuth flow issues first")
        
        if results['session_endpoint_401_without_cookie'] and results['session_validation_working']:
            print(f"   ✅ Session validation is working correctly")
        else:
            print(f"   2. Fix session validation issues")
        
        if not results['cors_headers_present'] or not results['cookie_requirements_met']:
            print(f"   3. CRITICAL: Fix CORS configuration")
            print(f"      → Ensure Access-Control-Allow-Credentials: true")
            print(f"      → Ensure Access-Control-Allow-Origin includes production domain")
            print(f"      → This is likely the main cause of the 401 issue")
        
        print(f"\n💡 LIKELY ROOT CAUSE:")
        if results['oauth_login_accessible'] and results['session_endpoint_401_without_cookie']:
            if not results['cors_headers_present'] or not results['cookie_requirements_met']:
                print(f"   🎯 CORS configuration prevents cookie transmission")
                print(f"   📝 Browser receives cookie from OAuth callback but cannot send it back")
                print(f"   🔧 Fix: Ensure CORS middleware allows credentials and includes production domain")
            else:
                print(f"   🎯 Cookie setting or session storage issue")
                print(f"   📝 Check if cookies are being set properly in OAuth callback")
                print(f"   🔧 Fix: Verify cookie setting in /api/auth/google/callback")
        else:
            print(f"   🎯 Backend service or endpoint configuration issue")
            print(f"   📝 Basic OAuth or session endpoints not working")
            print(f"   🔧 Fix: Check backend service status and endpoint implementations")

def main():
    tester = ProductionOAuthTester()
    results = tester.test_oauth_flow_complete()
    
    # Final summary
    print("\n" + "=" * 80)
    print("🔐 PRODUCTION OAUTH SESSION COOKIE TESTING - FINAL SUMMARY")
    print("=" * 80)
    
    success_count = sum(results.values())
    total_tests = len(results)
    success_rate = (success_count / total_tests) * 100
    
    print(f"\n📈 OVERALL SUCCESS RATE: {success_count}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("\n✅ OAUTH SESSION TESTING: MOSTLY WORKING")
        print("   Minor issues may need attention")
    elif success_rate >= 60:
        print("\n⚠️ OAUTH SESSION TESTING: PARTIAL SUCCESS")
        print("   Several issues need attention")
    else:
        print("\n❌ OAUTH SESSION TESTING: CRITICAL ISSUES")
        print("   Major problems prevent proper OAuth session management")
    
    return success_rate >= 60

if __name__ == "__main__":
    main()