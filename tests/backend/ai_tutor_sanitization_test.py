#!/usr/bin/env python3
"""
AI Tutor Phase 1 Text Sanitization Testing
Focused test for the review request requirements
"""

import requests
import json
import uuid
import time

def test_ai_tutor_sanitization():
    """Test AI Tutor text sanitization fixes"""
    base_url = "https://neuro-tutor-dev.preview.emergentagent.com/api"
    
    print("🤖 AI TUTOR PHASE 1 TEXT SANITIZATION TESTING")
    print("=" * 80)
    print("CRITICAL FIX: /api/ai/dual-response endpoint now uses modular_ai_service")
    print("FOCUS: Text sanitization, GPT-5 prompt enforcement, mentor structure")
    print("CREDENTIALS: test@dhruvai.com / password123")
    print("=" * 80)
    
    # Step 1: Login
    print("\n🔐 AUTHENTICATION")
    login_data = {
        "email": "test@dhruvai.com",
        "password": "password123"
    }
    
    try:
        print("   Attempting login...")
        login_response = requests.post(
            f"{base_url}/auth/login",
            json=login_data,
            timeout=30
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get('token')
            print(f"   ✅ Login successful - Token: {token[:20]}...")
        else:
            print(f"   ❌ Login failed - Status: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Login error: {str(e)}")
        return False
    
    # Step 2: Test AI Tutor endpoint with sanitization test messages
    print("\n🧪 TEXT SANITIZATION TESTING")
    
    test_messages = [
        {
            'name': 'Math with LaTeX',
            'message': 'Solve x^2 + 5x + 6 = 0 step by step',
            'expected': 'latex_formatting'
        },
        {
            'name': 'Special Characters Test',
            'message': 'What is **bold** text with emojis ✅❌?',
            'expected': 'sanitization'
        },
        {
            'name': 'Numbered Emojis Test',
            'message': 'Explain physics with 1️⃣ first law, 2️⃣ second law',
            'expected': 'emoji_removal'
        }
    ]
    
    results = []
    
    for test_msg in test_messages:
        print(f"\n   📝 Testing: {test_msg['name']}")
        print(f"      Message: {test_msg['message']}")
        
        request_data = {
            "message": test_msg['message'],
            "session_id": str(uuid.uuid4()),
            "subject": "Mathematics"
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        try:
            print("      Making API call...")
            response = requests.post(
                f"{base_url}/ai/dual-response",
                json=request_data,
                headers=headers,
                timeout=45
            )
            
            if response.status_code == 200:
                print("      ✅ API call successful")
                response_data = response.json()
                
                # Analyze response
                analysis = analyze_response(response_data, test_msg)
                results.append(analysis)
                
                print(f"      📊 Analysis: {analysis['summary']}")
                
            else:
                print(f"      ❌ API call failed - Status: {response.status_code}")
                print(f"      Error: {response.text[:200]}")
                results.append({
                    'test_name': test_msg['name'],
                    'success': False,
                    'summary': f"API call failed with status {response.status_code}"
                })
                
        except Exception as e:
            print(f"      ❌ Request error: {str(e)}")
            results.append({
                'test_name': test_msg['name'],
                'success': False,
                'summary': f"Request error: {str(e)}"
            })
    
    # Step 3: Final Assessment
    print("\n" + "=" * 80)
    print("🎯 FINAL RESULTS")
    print("=" * 80)
    
    successful_tests = sum(1 for r in results if r['success'])
    total_tests = len(results)
    success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"\n📊 SUMMARY:")
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"   {result['test_name']}: {status}")
        print(f"      {result['summary']}")
    
    print(f"\n📈 SUCCESS RATE: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 70:
        print("\n✅ AI TUTOR PHASE 1 TEXT SANITIZATION: SUCCESS")
        print("   Text sanitization fixes are working correctly")
    else:
        print("\n❌ AI TUTOR PHASE 1 TEXT SANITIZATION: NEEDS WORK")
        print("   Critical sanitization issues identified")
    
    return success_rate >= 70

def analyze_response(response_data, test_msg):
    """Analyze API response for sanitization compliance"""
    try:
        if not isinstance(response_data, dict):
            return {
                'test_name': test_msg['name'],
                'success': False,
                'summary': 'Response is not a dictionary'
            }
        
        primary = response_data.get('primary', {})
        secondary = response_data.get('secondary', {})
        
        if not primary or not secondary:
            return {
                'test_name': test_msg['name'],
                'success': False,
                'summary': 'Missing primary or secondary response'
            }
        
        primary_text = primary.get('response', '')
        secondary_text = secondary.get('response', '')
        combined_text = primary_text + secondary_text
        
        # Check for sanitization based on test type
        issues = []
        
        # Check for markdown symbols
        if '**' in combined_text:
            issues.append('Found markdown symbols (**)')
        
        # Check for emojis
        emoji_patterns = ['✅', '❌', '1️⃣', '2️⃣', '💡']
        found_emojis = [emoji for emoji in emoji_patterns if emoji in combined_text]
        if found_emojis:
            issues.append(f'Found emojis: {found_emojis}')
        
        # Check for escaped sequences
        escaped_sequences = ['\\n', '\\t', '\\"', "\\'"]
        found_escaped = [seq for seq in escaped_sequences if seq in combined_text]
        if found_escaped:
            issues.append(f'Found escaped sequences: {found_escaped}')
        
        # Check for raw_text fields
        has_raw_text = bool(primary.get('raw_text') or secondary.get('raw_text'))
        
        # Check LaTeX formatting for math problems
        if 'solve' in test_msg['message'].lower() and 'x^2' in test_msg['message']:
            has_proper_latex = '\\[' in combined_text and '\\]' in combined_text
            if not has_proper_latex:
                issues.append('Missing proper LaTeX formatting (\\[ \\])')
        
        # Check mentor structure
        if 'mentor' in secondary.get('type', '').lower():
            mentor_sections = secondary.get('mentor_sections', {})
            if not mentor_sections or not isinstance(mentor_sections, dict):
                issues.append('Mentor sections missing or invalid')
        
        success = len(issues) == 0
        summary = "All sanitization checks passed" if success else f"Issues: {'; '.join(issues)}"
        
        if has_raw_text:
            summary += " (Raw text fields present)"
        
        return {
            'test_name': test_msg['name'],
            'success': success,
            'summary': summary,
            'issues': issues,
            'has_raw_text': has_raw_text
        }
        
    except Exception as e:
        return {
            'test_name': test_msg['name'],
            'success': False,
            'summary': f'Analysis error: {str(e)}'
        }

if __name__ == "__main__":
    success = test_ai_tutor_sanitization()
    exit(0 if success else 1)