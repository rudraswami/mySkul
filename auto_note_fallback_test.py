#!/usr/bin/env python3
"""
Auto-Note Mentor Fallback Mechanism Test
Testing the fixed recording workflow with fallback transcription as requested in review.
"""

import requests
import json
import time
import sys

class AutoNoteFallbackTester:
    def __init__(self, base_url="https://ai-education-app.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.session_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_email = "test@dhruvai.com"
        self.test_user_password = "password123"

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
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
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)

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
                    self.last_error_data = error_data
                except:
                    print(f"   Error: {response.text}")
                    self.last_error_data = {"error": response.text}
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.last_error_data = {"error": str(e)}
            return False, {}

    def test_authentication(self):
        """Test authentication with test@dhruvai.com / password123"""
        print("   Testing authentication with test@dhruvai.com / password123...")
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        success, response = self.run_test(
            "Authentication",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            if 'user' in response:
                self.user_id = response['user'].get('user_id')
            print(f"   ✅ Authentication successful - Token: {self.token[:20]}...")
            return True
        else:
            print("   ❌ Authentication failed")
            return False

    def test_session_creation(self):
        """Test POST /api/auto-notes/start-session"""
        print("   Testing session creation (POST /api/auto-notes/start-session)...")
        
        session_data = {
            "title": "Physics Class - Newton's Laws",
            "subject": "Physics"
        }
        
        success, response = self.run_test(
            "Session Creation",
            "POST",
            "auto-notes/start-session",
            200,
            data=session_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success and 'session_id' in response:
            self.session_id = response['session_id']
            print(f"   ✅ Session created successfully - ID: {self.session_id}")
            print(f"   Title: {response.get('title', 'N/A')}")
            print(f"   Subject: {response.get('subject', 'N/A')}")
            print(f"   Status: {response.get('status', 'N/A')}")
            return True
        else:
            print("   ❌ Session creation failed")
            return False

    def test_audio_processing(self):
        """Test POST /api/auto-notes/process-audio (simulate 2-3 chunks)"""
        print("   Testing audio processing with 2-3 chunks...")
        
        # Simulate 3 audio chunks as requested in review
        audio_chunks = [
            {
                "session_id": self.session_id,
                "transcription": "Today we will discuss Newton's first law of motion. An object at rest stays at rest.",
                "timestamp": 0.0,
                "sequence_number": 1,
                "confidence": 0.95
            },
            {
                "session_id": self.session_id,
                "transcription": "Newton's second law states that force equals mass times acceleration. F = ma.",
                "timestamp": 30.5,
                "sequence_number": 2,
                "confidence": 0.92
            },
            {
                "session_id": self.session_id,
                "transcription": "The third law says for every action there is an equal and opposite reaction.",
                "timestamp": 65.2,
                "sequence_number": 3,
                "confidence": 0.88
            }
        ]
        
        success_count = 0
        
        for i, chunk in enumerate(audio_chunks):
            print(f"   Processing chunk {i+1}/3: '{chunk['transcription'][:40]}...'")
            
            success, response = self.run_test(
                f"Audio Processing Chunk {i+1}",
                "POST",
                "auto-notes/process-audio",
                200,
                data=chunk,
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if success:
                print(f"   ✅ Chunk {i+1} processed successfully")
                if 'concepts_detected' in response:
                    concepts = response.get('concepts_detected', [])
                    print(f"   Concepts detected: {len(concepts)} - {concepts[:2]}")
                success_count += 1
            else:
                print(f"   ❌ Chunk {i+1} processing failed")
            
            time.sleep(1)  # Small delay between chunks
        
        if success_count >= 2:  # At least 2 out of 3 chunks should succeed
            print(f"   ✅ Audio processing successful: {success_count}/3 chunks processed")
            return True
        else:
            print(f"   ❌ Audio processing failed: only {success_count}/3 chunks processed")
            return False

    def test_session_completion_with_fallback(self):
        """Test POST /api/auto-notes/end-session with fallback transcription - THE KEY TEST"""
        print("   🎯 TESTING FALLBACK MECHANISM - KEY TEST FROM REVIEW REQUEST")
        print("   Testing session completion with fallback transcription...")
        
        # Test the new fallback mechanism as specified in review request
        fallback_data = {
            "fallback_transcription": "This is a physics class about Newton's laws of motion. The first law states that an object at rest stays at rest unless acted upon by an external force. The second law is F=ma, force equals mass times acceleration. The third law states that for every action there is an equal and opposite reaction. These laws form the foundation of classical mechanics.",
            "total_duration": 120.5
        }
        
        print(f"   Using fallback transcription: '{fallback_data['fallback_transcription'][:60]}...'")
        print(f"   Total duration: {fallback_data['total_duration']} seconds")
        print("   This may take 10-15 seconds for AI processing...")
        
        success, response = self.run_test(
            "Session Completion with Fallback",
            "POST",
            f"auto-notes/end-session?session_id={self.session_id}",
            200,
            data=fallback_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            print("   ✅ Session completed successfully with fallback transcription")
            
            # Check for expected response fields as specified in review
            session_status = response.get('status', 'unknown')
            has_structured_notes = 'structured_notes' in response
            has_dual_analysis = 'dual_analysis' in response
            
            print(f"   Session status: {session_status}")
            print(f"   Has structured_notes: {has_structured_notes}")
            print(f"   Has dual_analysis: {has_dual_analysis}")
            
            # Detailed verification of structured_notes
            if has_structured_notes:
                structured_notes = response.get('structured_notes', {})
                key_concepts = structured_notes.get('key_concepts', [])
                important_points = structured_notes.get('important_points', [])
                formulas = structured_notes.get('formulas', [])
                
                print(f"   Structured notes - Key concepts: {len(key_concepts)}")
                print(f"   Structured notes - Important points: {len(important_points)}")
                print(f"   Structured notes - Formulas: {len(formulas)}")
                
                if key_concepts:
                    print(f"   Sample concept: {key_concepts[0][:50]}...")
            
            # Detailed verification of dual_analysis
            if has_dual_analysis:
                dual_analysis = response.get('dual_analysis', {})
                professor_analysis = dual_analysis.get('professor_analysis', '')
                mentor_guidance = dual_analysis.get('mentor_guidance', '')
                
                print(f"   Dual analysis - Professor analysis: {len(professor_analysis)} chars")
                print(f"   Dual analysis - Mentor guidance: {len(mentor_guidance)} chars")
                
                if professor_analysis:
                    print(f"   Professor analysis sample: {str(professor_analysis)[:50]}...")
                if mentor_guidance:
                    print(f"   Mentor guidance sample: {str(mentor_guidance)[:50]}...")
            
            # Final verification as per review requirements
            if session_status == 'completed' and has_structured_notes and has_dual_analysis:
                print("   ✅ ALL EXPECTED RESULTS VERIFIED - FALLBACK MECHANISM WORKING!")
                print("   ✅ Session completed with status 'completed'")
                print("   ✅ Structured notes generated successfully")
                print("   ✅ Dual analysis generated successfully")
                print("   ✅ No more 'No audio data found for this session' errors")
                return True
            else:
                print("   ⚠️  Some expected fields missing from response")
                missing = []
                if session_status != 'completed':
                    missing.append(f"status (got '{session_status}', expected 'completed')")
                if not has_structured_notes:
                    missing.append("structured_notes")
                if not has_dual_analysis:
                    missing.append("dual_analysis")
                print(f"   Missing: {', '.join(missing)}")
                return False
        else:
            print("   ❌ Session completion with fallback failed")
            # Check for specific error messages
            if hasattr(self, 'last_error_data'):
                error_msg = self.last_error_data.get('detail', 'Unknown error')
                if "No audio data found" in error_msg:
                    print("   ❌ CRITICAL: Still getting 'No audio data found' error - fallback mechanism NOT working")
                else:
                    print(f"   Error details: {error_msg}")
            return False

    def test_results_verification(self):
        """Test results verification - check if session has structured_notes and dual_analysis"""
        print("   Testing results verification...")
        
        # Get the completed session to verify results
        success, response = self.run_test(
            "Session Results Verification",
            "GET",
            f"auto-notes/{self.session_id}",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        if success:
            print("   ✅ Session retrieved successfully")
            
            # Verify expected results structure
            session_status = response.get('status', 'unknown')
            structured_notes = response.get('structured_notes', {})
            dual_analysis = response.get('dual_analysis', {})
            transcription = response.get('transcription', '')
            
            print(f"   Session status: {session_status}")
            print(f"   Has transcription: {'Yes' if transcription else 'No'} ({len(transcription)} chars)")
            
            # Final verification
            has_all_expected = (
                session_status == 'completed' and
                bool(structured_notes) and
                bool(dual_analysis) and
                bool(transcription)
            )
            
            if has_all_expected:
                print("   ✅ All expected results verified - session completed successfully")
                return True
            else:
                print("   ⚠️  Some expected results missing")
                return False
        else:
            print("   ❌ Failed to retrieve session for verification")
            return False

    def run_fallback_workflow_test(self):
        """Run the complete fallback workflow test as requested in review"""
        print("🎯 AUTO-NOTE MENTOR FALLBACK MECHANISM TEST")
        print("   Focus: Test the new fallback transcription mechanism")
        print("   Expected: Session completes with structured_notes and dual_analysis")
        print("   Expected: No more 'No audio data found for this session' errors")
        print("="*80)
        
        # Track all test results
        test_results = {
            'authentication': False,
            'session_creation': False,
            'audio_processing': False,
            'session_completion_with_fallback': False,
            'results_verification': False
        }
        
        # 1. Authentication Test
        print("\n📋 STEP 1: Authentication Test")
        test_results['authentication'] = self.test_authentication()
        
        if not test_results['authentication']:
            print("❌ Authentication failed - cannot proceed")
            return False
        
        # 2. Session Creation Test
        print("\n📋 STEP 2: Session Creation Test")
        test_results['session_creation'] = self.test_session_creation()
        
        if not test_results['session_creation']:
            print("❌ Session creation failed - cannot proceed")
            return False
        
        # 3. Audio Processing Test (simulate 2-3 chunks)
        print("\n📋 STEP 3: Audio Processing Test (2-3 chunks)")
        test_results['audio_processing'] = self.test_audio_processing()
        
        # 4. Session Completion with Fallback Test - THE KEY TEST
        print("\n📋 STEP 4: Session Completion with Fallback Test - KEY TEST")
        test_results['session_completion_with_fallback'] = self.test_session_completion_with_fallback()
        
        # 5. Results Verification Test
        print("\n📋 STEP 5: Results Verification Test")
        if test_results['session_completion_with_fallback']:
            test_results['results_verification'] = self.test_results_verification()
        
        # Final summary
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"\n🎯 AUTO-NOTE MENTOR FALLBACK MECHANISM SUMMARY:")
        print(f"   ✅ Authentication: {'PASS' if test_results['authentication'] else 'FAIL'}")
        print(f"   ✅ Session Creation: {'PASS' if test_results['session_creation'] else 'FAIL'}")
        print(f"   ✅ Audio Processing: {'PASS' if test_results['audio_processing'] else 'FAIL'}")
        print(f"   ✅ Session Completion with Fallback: {'PASS' if test_results['session_completion_with_fallback'] else 'FAIL'}")
        print(f"   ✅ Results Verification: {'PASS' if test_results['results_verification'] else 'FAIL'}")
        print(f"   📊 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Key findings
        if test_results['session_completion_with_fallback']:
            print("\n🎉 FALLBACK MECHANISM SUCCESS:")
            print("   ✅ Fallback transcription mechanism is working")
            print("   ✅ Session completes successfully with fallback data")
            print("   ✅ Structured notes generated from fallback transcription")
            print("   ✅ Dual analysis generated successfully")
            print("   ✅ No 'No audio data found' errors")
        else:
            print("\n❌ FALLBACK MECHANISM FAILURE:")
            print("   ❌ Fallback transcription mechanism is NOT working")
            print("   ❌ Session still fails to complete")
            print("   ❌ Users will still get stuck on 'Processing your notes'")
        
        return success_rate >= 80.0  # 80% success threshold

if __name__ == "__main__":
    tester = AutoNoteFallbackTester()
    
    print("🚀 Starting Auto-Note Mentor Fallback Mechanism Testing...")
    print("   Testing the fixed recording workflow with fallback transcription")
    print("   As requested in review: Focus on fallback mechanism")
    
    # Run the fallback workflow test
    success = tester.run_fallback_workflow_test()
    
    # Final summary
    print("\n" + "="*80)
    print("🎯 AUTO-NOTE MENTOR FALLBACK TESTING COMPLETE")
    print("="*80)
    print(f"Total tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    success_rate = (tester.tests_passed/tester.tests_run)*100 if tester.tests_run > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if success:
        print("🎉 FALLBACK MECHANISM TESTING SUCCESSFUL!")
        print("   The fallback transcription mechanism is working correctly")
    else:
        print("⚠️  FALLBACK MECHANISM TESTING FAILED")
        print("   The fallback transcription mechanism needs further fixes")
    
    sys.exit(0 if success else 1)