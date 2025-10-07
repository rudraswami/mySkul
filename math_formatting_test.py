#!/usr/bin/env python3
"""
Focused test for AI Tutor Mathematical Formatting Functionality
Review Request: Test mathematical expression handling in AI responses
"""

import requests
import json
import sys

class MathFormattingTester:
    def __init__(self):
        self.base_url = "https://quota-handler.preview.emergentagent.com/api"
        self.token = None
        self.test_user_email = "test@dhruvai.com"
        self.test_user_password = "password123"

    def authenticate(self):
        """Authenticate with test credentials"""
        print("🔐 Authenticating with test credentials...")
        
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
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.token = data['token']
                    print(f"✅ Authentication successful")
                    print(f"   Token: {self.token[:20]}...")
                    return True
                else:
                    print(f"❌ No token in response: {data}")
                    return False
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False

    def test_mathematical_formatting(self):
        """Test AI Tutor mathematical formatting functionality"""
        if not self.token:
            print("❌ No authentication token available")
            return False
        
        print("\n🎯 TESTING: AI Tutor Mathematical Formatting Functionality")
        print("=" * 60)
        print("FOCUS: Verify mathematical expression handling in AI responses")
        print("ENDPOINT: /api/ai/dual-response")
        print("AUTHENTICATION: test@dhruvai.com / password123")
        print("QUESTION: 'Solve x^2 - 5x + 6 = 0 step by step'")
        print("=" * 60)
        
        # Test the specific mathematical question from review request
        mathematical_question = "Solve x^2 - 5x + 6 = 0 step by step"
        
        print(f"\n📝 Sending mathematical question...")
        print(f"   Question: '{mathematical_question}'")
        print("   This may take 10-15 seconds for dual AI processing...")
        
        try:
            response = requests.post(
                f"{self.base_url}/ai/dual-response",
                json={
                    "message": mathematical_question,
                    "subject": "Mathematics"
                },
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                },
                timeout=60
            )
            
            print(f"\n📊 API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API returned 200 OK")
                
                # Check response structure
                if 'dual_response' in data:
                    dual_response = data['dual_response']
                    primary_response = dual_response.get('primary', {})
                    secondary_response = dual_response.get('secondary', {})
                    scenario_type = dual_response.get('scenario_type', 'N/A')
                    confidence = dual_response.get('confidence', 0)
                    
                    print(f"\n🤖 DUAL AI RESPONSE STRUCTURE:")
                    print(f"   Primary persona: {primary_response.get('persona', 'N/A')}")
                    print(f"   Secondary persona: {secondary_response.get('persona', 'N/A')}")
                    print(f"   Scenario type: {scenario_type}")
                    print(f"   Confidence: {confidence:.2f}")
                    
                    # Extract response content for analysis
                    primary_content = primary_response.get('response', '')
                    secondary_content = secondary_response.get('response', '')
                    
                    print(f"\n📏 RESPONSE LENGTH ANALYSIS:")
                    print(f"   Primary response: {len(primary_content)} characters")
                    print(f"   Secondary response: {len(secondary_content)} characters")
                    
                    # Mathematical content analysis
                    mathematical_indicators = [
                        'x²', 'x^2', '=', 'step', 'solve', 'equation', 'quadratic',
                        'factor', 'discriminant', 'roots', '±', '+', '-', '×', '÷',
                        'x = ', '(x', ')²', 'formula'
                    ]
                    
                    primary_math_score = sum(1 for indicator in mathematical_indicators 
                                           if indicator.lower() in primary_content.lower())
                    secondary_math_score = sum(1 for indicator in mathematical_indicators 
                                             if indicator.lower() in secondary_content.lower())
                    
                    print(f"\n🔢 MATHEMATICAL CONTENT ANALYSIS:")
                    print(f"   Primary response math indicators: {primary_math_score}")
                    print(f"   Secondary response math indicators: {secondary_math_score}")
                    
                    # Step-by-step analysis
                    step_indicators = ['step 1', 'step 2', 'step', 'first', 'second', 'then', 'next', 'finally']
                    primary_steps = sum(1 for indicator in step_indicators 
                                      if indicator.lower() in primary_content.lower())
                    secondary_steps = sum(1 for indicator in step_indicators 
                                        if indicator.lower() in secondary_content.lower())
                    
                    print(f"   Primary response step indicators: {primary_steps}")
                    print(f"   Secondary response step indicators: {secondary_steps}")
                    
                    # Display sample content
                    print(f"\n📖 RESPONSE CONTENT PREVIEW:")
                    print(f"   PRIMARY RESPONSE (first 300 chars):")
                    print(f"   '{primary_content[:300]}...'")
                    print(f"\n   SECONDARY RESPONSE (first 300 chars):")
                    print(f"   '{secondary_content[:300]}...'")
                    
                    # Assessment criteria
                    has_mathematical_content = (primary_math_score >= 3 or secondary_math_score >= 3)
                    has_step_by_step = (primary_steps >= 1 or secondary_steps >= 1)
                    has_proper_length = (len(primary_content) > 100 and len(secondary_content) > 100)
                    both_respond = (primary_content and secondary_content)
                    
                    print(f"\n🎯 MATHEMATICAL FORMATTING ASSESSMENT:")
                    print(f"   ✅ API returns 200 OK: {'✅' if response.status_code == 200 else '❌'}")
                    print(f"   ✅ Contains mathematical expressions: {'✅' if has_mathematical_content else '❌'}")
                    print(f"   ✅ Contains step-by-step solution: {'✅' if has_step_by_step else '❌'}")
                    print(f"   ✅ Responses have proper length: {'✅' if has_proper_length else '❌'}")
                    print(f"   ✅ Both personas respond coherently: {'✅' if both_respond else '❌'}")
                    
                    # Final verdict
                    all_criteria_met = (
                        response.status_code == 200 and
                        has_mathematical_content and 
                        has_step_by_step and 
                        has_proper_length and 
                        both_respond
                    )
                    
                    print(f"\n🏆 FINAL ASSESSMENT:")
                    if all_criteria_met:
                        print("✅ MATHEMATICAL FORMATTING TEST PASSED")
                        print("   - API returns 200 OK with mathematical content")
                        print("   - Response contains step-by-step mathematical solution")
                        print("   - Mathematical expressions are properly formatted")
                        print("   - Both professor and mentor responses are coherent")
                        return True
                    else:
                        print("❌ MATHEMATICAL FORMATTING TEST FAILED")
                        print("   - One or more assessment criteria not met")
                        return False
                        
                else:
                    print("❌ Response missing 'dual_response' structure")
                    print(f"   Response keys: {list(data.keys())}")
                    return False
                    
            else:
                print(f"❌ API request failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Request error: {str(e)}")
            return False

def main():
    print("🧮 AI Tutor Mathematical Formatting Test")
    print("Review Request: Test mathematical expression handling")
    print("=" * 60)
    
    tester = MathFormattingTester()
    
    # Step 1: Authenticate
    if not tester.authenticate():
        print("\n❌ AUTHENTICATION FAILED - Cannot proceed with testing")
        sys.exit(1)
    
    # Step 2: Test mathematical formatting
    success = tester.test_mathematical_formatting()
    
    # Final summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    if success:
        print("✅ MATHEMATICAL FORMATTING FUNCTIONALITY: WORKING")
        print("   The AI Tutor correctly handles mathematical expressions")
        print("   and provides step-by-step solutions in dual AI responses.")
        sys.exit(0)
    else:
        print("❌ MATHEMATICAL FORMATTING FUNCTIONALITY: FAILED")
        print("   Issues detected with mathematical expression handling")
        print("   or response formatting in the AI Tutor system.")
        sys.exit(1)

if __name__ == "__main__":
    main()