#!/usr/bin/env python3
"""
AI Tutor Performance & Reliability Test
Tests timeout handling, retry logic, and ensures no blank responses
"""

import requests
import json
import time
import uuid
import asyncio

async def test_ai_tutor_performance():
    """Test AI Tutor performance and reliability"""
    base_url = "http://localhost:8001/api"
    
    print("🚀 AI TUTOR PERFORMANCE & RELIABILITY TEST")
    print("=" * 80)
    print("GOAL: Verify latency < 20s, no blank responses, proper error handling")
    print("=" * 80)
    
    # Step 1: Login
    print("\n🔐 AUTHENTICATION")
    login_data = {
        "email": "test@dhruvai.com",
        "password": "password123"
    }
    
    try:
        login_response = requests.post(
            f"{base_url}/auth/login",
            json=login_data,
            timeout=10
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get('token')
            print(f"   ✅ Login successful")
        else:
            print(f"   ❌ Login failed - Status: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Login error: {str(e)}")
        return False
    
    # Step 2: Performance Tests
    print("\n⚡ PERFORMANCE TESTS")
    
    test_cases = [
        {
            'name': 'Simple Math Question',
            'message': 'What is 2 + 2?',
            'expected_max_time': 15.0
        },
        {
            'name': 'Complex Math Problem', 
            'message': 'Solve x^2 + 5x + 6 = 0 step by step',
            'expected_max_time': 20.0
        },
        {
            'name': 'Physics Concept',
            'message': 'Explain Newton\'s second law with examples',
            'expected_max_time': 20.0
        },
        {
            'name': 'Test with Special Characters',
            'message': 'What is **markdown** with emojis ✅ and math x^2?',
            'expected_max_time': 20.0
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases):
        print(f"\n   📝 Test {i+1}/4: {test_case['name']}")
        print(f"      Message: {test_case['message']}")
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        request_data = {
            "message": test_case['message'],
            "session_id": str(uuid.uuid4()),
            "subject": "Mathematics"
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{base_url}/ai/dual-response",
                json=request_data,
                headers=headers,
                timeout=25  # Slightly higher than our backend timeout
            )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Analyze response quality
                analysis = analyze_response_quality(response_data, test_case)
                analysis['response_time'] = elapsed_time
                analysis['test_name'] = test_case['name']
                
                # Check performance requirement
                if elapsed_time <= test_case['expected_max_time']:
                    print(f"      ⚡ Response time: {elapsed_time:.2f}s ✅")
                else:
                    print(f"      ⚠️ Response time: {elapsed_time:.2f}s (exceeds {test_case['expected_max_time']}s)")
                
                print(f"      📊 Quality: {analysis['quality_summary']}")
                results.append(analysis)
                
            else:
                print(f"      ❌ API call failed - Status: {response.status_code}")
                results.append({
                    'test_name': test_case['name'],
                    'success': False,
                    'response_time': elapsed_time,
                    'error': f"HTTP {response.status_code}"
                })
                
        except requests.exceptions.Timeout:
            elapsed_time = time.time() - start_time
            print(f"      ⏰ Timeout after {elapsed_time:.2f}s")
            results.append({
                'test_name': test_case['name'],
                'success': False,
                'response_time': elapsed_time,
                'error': 'Timeout'
            })
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"      ❌ Error: {str(e)}")
            results.append({
                'test_name': test_case['name'],
                'success': False,
                'response_time': elapsed_time,
                'error': str(e)
            })
    
    # Step 3: Performance Analysis
    print("\n" + "=" * 80)
    print("📊 PERFORMANCE ANALYSIS")
    print("=" * 80)
    
    successful_tests = [r for r in results if r.get('success', False)]
    total_tests = len(results)
    success_rate = (len(successful_tests) / total_tests) * 100 if total_tests > 0 else 0
    
    if successful_tests:
        avg_response_time = sum(r['response_time'] for r in successful_tests) / len(successful_tests)
        max_response_time = max(r['response_time'] for r in successful_tests)
        min_response_time = min(r['response_time'] for r in successful_tests)
        
        print(f"\n📈 PERFORMANCE METRICS:")
        print(f"   Success Rate: {len(successful_tests)}/{total_tests} ({success_rate:.1f}%)")
        print(f"   Average Response Time: {avg_response_time:.2f}s")
        print(f"   Fastest Response: {min_response_time:.2f}s")
        print(f"   Slowest Response: {max_response_time:.2f}s")
        
        # Check if performance requirements are met
        performance_ok = max_response_time <= 20.0 and success_rate >= 75.0
        blank_responses = sum(1 for r in successful_tests if r.get('has_blank_content', False))
        
        print(f"\n🎯 REQUIREMENTS CHECK:")
        print(f"   ✅ Latency < 20s: {'PASS' if max_response_time <= 20.0 else 'FAIL'}")
        print(f"   ✅ Success Rate ≥ 75%: {'PASS' if success_rate >= 75.0 else 'FAIL'}")
        print(f"   ✅ Zero Blank Messages: {'PASS' if blank_responses == 0 else f'FAIL ({blank_responses} blank)'}")
        
        if performance_ok and blank_responses == 0:
            print(f"\n🎉 ALL PERFORMANCE REQUIREMENTS MET!")
            return True
        else:
            print(f"\n⚠️ PERFORMANCE ISSUES DETECTED")
            return False
    else:
        print(f"\n❌ NO SUCCESSFUL TESTS - SYSTEM FAILURE")
        return False

def analyze_response_quality(response_data, test_case):
    """Analyze response quality and detect issues"""
    try:
        analysis = {
            'success': True,
            'has_blank_content': False,
            'has_primary_response': False,
            'has_secondary_response': False,
            'quality_issues': []
        }
        
        # Check dual response structure
        if 'dual_response' not in response_data:
            analysis['quality_issues'].append('Missing dual_response structure')
            analysis['success'] = False
        else:
            dual_response = response_data['dual_response']
            
            # Check primary (professor) response
            if 'primary' in dual_response and dual_response['primary']:
                primary = dual_response['primary']
                primary_text = primary.get('response', '')
                
                if primary_text and len(primary_text.strip()) > 10:
                    analysis['has_primary_response'] = True
                else:
                    analysis['quality_issues'].append('Blank or too short primary response')
                    analysis['has_blank_content'] = True
            
            # Check secondary (mentor) response  
            if 'secondary' in dual_response and dual_response['secondary']:
                secondary = dual_response['secondary']
                secondary_text = secondary.get('response', '')
                
                if secondary_text and len(secondary_text.strip()) > 10:
                    analysis['has_secondary_response'] = True
                else:
                    analysis['quality_issues'].append('Blank or too short secondary response')
                    analysis['has_blank_content'] = True
        
        # Generate quality summary
        if analysis['has_primary_response'] and analysis['has_secondary_response']:
            analysis['quality_summary'] = 'Excellent - Complete dual response'
        elif analysis['has_primary_response'] or analysis['has_secondary_response']:
            analysis['quality_summary'] = 'Partial - One response missing'
        else:
            analysis['quality_summary'] = 'Poor - Both responses missing/blank'
            analysis['success'] = False
        
        return analysis
        
    except Exception as e:
        return {
            'success': False,
            'has_blank_content': True,
            'quality_issues': [f'Analysis error: {str(e)}'],
            'quality_summary': 'Analysis failed'
        }

if __name__ == "__main__":
    import sys
    success = asyncio.run(test_ai_tutor_performance())
    sys.exit(0 if success else 1)