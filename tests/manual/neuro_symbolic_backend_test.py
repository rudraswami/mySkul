#!/usr/bin/env python3
"""
Neuro-Symbolic AI Tutor Backend Testing
Tests the POST /api/ai/neuro-symbolic endpoint with comprehensive validation
"""

import requests
import json
import time
import sys
import os
from datetime import datetime, timezone, timedelta
import uuid
import jwt

# Add backend to path
sys.path.insert(0, '/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio


class NeuroSymbolicTester:
    def __init__(self):
        # Backend URL from environment
        self.base_url = "https://dhruv-neuro-ai.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.jwt_token = None
        self.user_id = None
        self.test_results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def log(self, message, level="INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbols = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "TEST": "🧪"
        }
        symbol = symbols.get(level, "ℹ️")
        print(f"[{timestamp}] {symbol} {message}")
    
    async def create_test_user(self):
        """Create a test user with ACHIEVER subscription"""
        from core.config import settings
        
        client = AsyncIOMotorClient(settings.MONGO_URL)
        db = client[settings.DB_NAME]
        
        # Test user data
        self.user_id = str(uuid.uuid4())
        email = f"neuro_test_{self.user_id[:8]}@example.com"
        
        # Create user with full access
        user_doc = {
            "user_id": self.user_id,
            "email": email,
            "full_name": "Neuro-Symbolic Test User",
            "google_id": f"test_google_id_{self.user_id}",
            "profile_picture": "https://example.com/avatar.jpg",
            "subscription_tier": "ACHIEVER",
            "subscription_status": "active",
            "subscription_start_date": datetime.now(timezone.utc).isoformat(),
            "subscription_end_date": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_login": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "preferences": {},
            "usage_stats": {
                "ai_mentor": {"used": 0, "limit": 999999},
                "mock_tests": {"used": 0, "limit": 999999},
                "auto_notes": {"used": 0, "limit": 999999}
            }
        }
        
        await db.users.insert_one(user_doc)
        self.log(f"Created test user: {email}", "SUCCESS")
        self.log(f"User ID: {self.user_id}", "INFO")
        
        # Generate JWT token
        payload = {
            "user_id": self.user_id,
            "email": email,
            "exp": datetime.now(timezone.utc) + timedelta(hours=2)
        }
        
        self.jwt_token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
        self.session.headers.update({
            'Authorization': f'Bearer {self.jwt_token}'
        })
        
        client.close()
        return self.user_id, self.jwt_token
    
    def test_endpoint(self, test_name, payload, expected_status=200):
        """Test the neuro-symbolic endpoint"""
        self.test_results['total_tests'] += 1
        
        url = f"{self.base_url}/ai/neuro-symbolic"
        
        try:
            start_time = time.time()
            response = self.session.post(url, json=payload, timeout=30)
            elapsed_time = time.time() - start_time
            
            self.log(f"Response status: {response.status_code}", "INFO")
            
            if response.status_code == expected_status:
                try:
                    data = response.json()
                    self.test_results['passed'] += 1
                    return True, data, elapsed_time
                except Exception as json_err:
                    self.test_results['failed'] += 1
                    self.log(f"JSON parse error: {str(json_err)}", "ERROR")
                    return False, {"error": f"Invalid JSON response: {str(json_err)}", "text": response.text[:200]}, elapsed_time
            else:
                self.test_results['failed'] += 1
                try:
                    error_data = response.json()
                except:
                    error_data = {"error": response.text[:500], "status_code": response.status_code}
                self.log(f"Status code mismatch: expected {expected_status}, got {response.status_code}", "ERROR")
                return False, error_data, elapsed_time
                
        except Exception as e:
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {str(e)}")
            self.log(f"Exception during request: {str(e)}", "ERROR")
            return False, {"error": str(e)}, 0
    
    def validate_response_structure(self, response_data, test_name):
        """Validate the 8-section response structure"""
        validation_results = {
            'has_success': False,
            'has_message_id': False,
            'has_response': False,
            'has_emotion_detected': False,
            'has_generation_time': False,
            'all_8_sections': False,
            'visual_schema_valid': False,
            'professor_verification_valid': False,
            'mini_practice_valid': False
        }
        
        # Check top-level fields
        if response_data.get('success') == True:
            validation_results['has_success'] = True
        
        if response_data.get('message_id'):
            validation_results['has_message_id'] = True
        
        if 'emotion_detected' in response_data:
            validation_results['has_emotion_detected'] = True
        
        if 'generation_time' in response_data:
            validation_results['has_generation_time'] = True
        
        # Check response object
        response_obj = response_data.get('response', {})
        if response_obj:
            validation_results['has_response'] = True
            
            # Check all 8 sections
            required_sections = [
                'practical_explanation',
                'indian_example',
                'metaphor',
                'visual_schema',
                'professor_verification',
                'mini_practice',
                'encouragement',
                'ask'
            ]
            
            all_present = all(section in response_obj for section in required_sections)
            validation_results['all_8_sections'] = all_present
            
            # Validate visual_schema
            visual_schema = response_obj.get('visual_schema', {})
            if visual_schema:
                has_diagram_type = 'diagram_type' in visual_schema
                has_nodes = isinstance(visual_schema.get('nodes'), list) and len(visual_schema.get('nodes', [])) > 0
                has_edges = isinstance(visual_schema.get('edges'), list)
                has_caption = 'caption' in visual_schema
                
                valid_diagram_types = ['flow', 'equation_map', 'mind_map', 'timeline', 'comparison', 'cycle', 'hierarchy']
                diagram_type_valid = visual_schema.get('diagram_type') in valid_diagram_types
                
                # Check node structure
                nodes_valid = True
                if has_nodes:
                    for node in visual_schema.get('nodes', []):
                        if not all(key in node for key in ['id', 'label', 'type']):
                            nodes_valid = False
                            break
                
                validation_results['visual_schema_valid'] = (
                    has_diagram_type and has_nodes and has_edges and 
                    has_caption and diagram_type_valid and nodes_valid
                )
            
            # Validate professor_verification
            prof_verify = response_obj.get('professor_verification', {})
            if prof_verify:
                has_steps = isinstance(prof_verify.get('steps'), list) and len(prof_verify.get('steps', [])) > 0
                has_source = 'source' in prof_verify
                has_confidence = 'confidence' in prof_verify
                confidence_valid = False
                if has_confidence:
                    conf = prof_verify.get('confidence')
                    confidence_valid = isinstance(conf, (int, float)) and 0.0 <= conf <= 1.0
                
                validation_results['professor_verification_valid'] = (
                    has_steps and has_source and confidence_valid
                )
            
            # Validate mini_practice
            mini_practice = response_obj.get('mini_practice', {})
            if mini_practice:
                has_question = 'question' in mini_practice and mini_practice.get('question')
                has_hint = 'hint' in mini_practice
                has_question_type = 'question_type' in mini_practice
                
                valid_question_types = ['mcq', 'fill_blank', 'short_answer']
                question_type_valid = mini_practice.get('question_type') in valid_question_types
                
                # If MCQ, check options
                options_valid = True
                if mini_practice.get('question_type') == 'mcq':
                    options = mini_practice.get('options', [])
                    options_valid = isinstance(options, list) and 2 <= len(options) <= 4
                
                validation_results['mini_practice_valid'] = (
                    has_question and has_hint and has_question_type and 
                    question_type_valid and options_valid
                )
        
        return validation_results
    
    def run_basic_functionality_tests(self):
        """Test basic functionality with different subjects and emotions"""
        self.log("=" * 80)
        self.log("BASIC FUNCTIONALITY TESTS (3 scenarios)", "TEST")
        self.log("=" * 80)
        
        test_scenarios = [
            {
                "name": "Mathematics - Neutral Emotion",
                "payload": {
                    "message": "Explain quadratic equations",
                    "subject": "Mathematics",
                    "session_id": f"test-math-{uuid.uuid4()}",
                    "exam_mode": "JEE"
                },
                "expected_emotion": "neutral"
            },
            {
                "name": "Physics - Curious Emotion",
                "payload": {
                    "message": "Why does the moon orbit Earth? I want to know more about gravitational forces",
                    "subject": "Physics",
                    "session_id": f"test-physics-{uuid.uuid4()}",
                    "exam_mode": "JEE"
                },
                "expected_emotion": "curious"
            },
            {
                "name": "Biology - Confused Emotion",
                "payload": {
                    "message": "I don't understand how photosynthesis works. It's very confusing",
                    "subject": "Biology",
                    "session_id": f"test-biology-{uuid.uuid4()}",
                    "exam_mode": "NEET"
                },
                "expected_emotion": "confused"
            }
        ]
        
        results = []
        
        for scenario in test_scenarios:
            self.log(f"\n{'='*60}")
            self.log(f"Test: {scenario['name']}", "TEST")
            self.log(f"{'='*60}")
            
            success, response_data, elapsed_time = self.test_endpoint(
                scenario['name'],
                scenario['payload']
            )
            
            if success:
                self.log(f"✅ Request successful (200 OK)", "SUCCESS")
                self.log(f"⏱️  Generation time: {elapsed_time:.2f}s", "INFO")
                
                # Validate structure
                validation = self.validate_response_structure(response_data, scenario['name'])
                
                # Log validation results
                self.log(f"\n📊 Response Structure Validation:", "INFO")
                self.log(f"   • Success field: {'✅' if validation['has_success'] else '❌'}")
                self.log(f"   • Message ID: {'✅' if validation['has_message_id'] else '❌'}")
                self.log(f"   • Response object: {'✅' if validation['has_response'] else '❌'}")
                self.log(f"   • Emotion detected: {'✅' if validation['has_emotion_detected'] else '❌'}")
                self.log(f"   • Generation time: {'✅' if validation['has_generation_time'] else '❌'}")
                self.log(f"   • All 8 sections present: {'✅' if validation['all_8_sections'] else '❌'}")
                self.log(f"   • Visual schema valid: {'✅' if validation['visual_schema_valid'] else '❌'}")
                self.log(f"   • Professor verification valid: {'✅' if validation['professor_verification_valid'] else '❌'}")
                self.log(f"   • Mini practice valid: {'✅' if validation['mini_practice_valid'] else '❌'}")
                
                # Check emotion detection
                detected_emotion = response_data.get('emotion_detected', 'unknown')
                self.log(f"\n🎭 Emotion Detection:", "INFO")
                self.log(f"   • Detected: {detected_emotion}")
                self.log(f"   • Expected: {scenario['expected_emotion']}")
                
                # Show sample sections
                response_obj = response_data.get('response', {})
                
                self.log(f"\n📝 Sample Content:", "INFO")
                
                # Practical explanation
                practical = response_obj.get('practical_explanation', '')
                if practical:
                    lines = practical.split('\n')
                    self.log(f"   • Practical Explanation ({len(lines)} lines):")
                    for line in lines[:2]:  # Show first 2 lines
                        self.log(f"     {line[:80]}...")
                
                # Indian example
                indian_ex = response_obj.get('indian_example', '')
                if indian_ex:
                    self.log(f"   • Indian Example: {indian_ex[:100]}...")
                
                # Visual schema
                visual = response_obj.get('visual_schema', {})
                if visual:
                    self.log(f"   • Visual Schema:")
                    self.log(f"     - Type: {visual.get('diagram_type')}")
                    self.log(f"     - Nodes: {len(visual.get('nodes', []))}")
                    self.log(f"     - Edges: {len(visual.get('edges', []))}")
                    self.log(f"     - Caption: {visual.get('caption', '')[:60]}...")
                
                # Professor verification
                prof = response_obj.get('professor_verification', {})
                if prof:
                    self.log(f"   • Professor Verification:")
                    self.log(f"     - Steps: {len(prof.get('steps', []))}")
                    self.log(f"     - Source: {prof.get('source', '')}")
                    self.log(f"     - Confidence: {prof.get('confidence', 0):.2f}")
                
                # Mini practice
                practice = response_obj.get('mini_practice', {})
                if practice:
                    self.log(f"   • Mini Practice:")
                    self.log(f"     - Type: {practice.get('question_type')}")
                    self.log(f"     - Question: {practice.get('question', '')[:80]}...")
                    if practice.get('options'):
                        self.log(f"     - Options: {len(practice.get('options', []))}")
                
                results.append({
                    'scenario': scenario['name'],
                    'success': True,
                    'validation': validation,
                    'elapsed_time': elapsed_time,
                    'emotion_detected': detected_emotion
                })
            else:
                self.log(f"❌ Request failed", "ERROR")
                self.log(f"Error: {json.dumps(response_data, indent=2)}", "ERROR")
                results.append({
                    'scenario': scenario['name'],
                    'success': False,
                    'error': response_data
                })
        
        return results
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        self.log("=" * 80)
        self.log("NEURO-SYMBOLIC AI TUTOR ENDPOINT TESTING", "TEST")
        self.log("=" * 80)
        self.log(f"Backend URL: {self.base_url}")
        self.log(f"Endpoint: POST /api/ai/neuro-symbolic")
        self.log("=" * 80)
        
        # Create test user
        self.log("\n🔧 Setting up test user...", "INFO")
        try:
            asyncio.run(self.create_test_user())
        except Exception as e:
            self.log(f"Failed to create test user: {str(e)}", "ERROR")
            return
        
        # Run basic functionality tests
        basic_results = self.run_basic_functionality_tests()
        
        # Summary
        self.log("\n" + "=" * 80)
        self.log("TEST SUMMARY", "TEST")
        self.log("=" * 80)
        
        self.log(f"\n📊 Overall Statistics:")
        self.log(f"   • Total tests: {self.test_results['total_tests']}")
        self.log(f"   • Passed: {self.test_results['passed']} ✅")
        self.log(f"   • Failed: {self.test_results['failed']} ❌")
        self.log(f"   • Success rate: {(self.test_results['passed'] / self.test_results['total_tests'] * 100):.1f}%")
        
        # Detailed results
        self.log(f"\n📋 Test Results by Scenario:")
        for result in basic_results:
            if result.get('success'):
                validation = result.get('validation', {})
                all_valid = all([
                    validation.get('has_success'),
                    validation.get('has_message_id'),
                    validation.get('all_8_sections'),
                    validation.get('visual_schema_valid'),
                    validation.get('professor_verification_valid'),
                    validation.get('mini_practice_valid')
                ])
                status = "✅ PASS" if all_valid else "⚠️  PARTIAL"
                self.log(f"   {status} - {result['scenario']}")
                self.log(f"      Time: {result['elapsed_time']:.2f}s, Emotion: {result['emotion_detected']}")
            else:
                self.log(f"   ❌ FAIL - {result['scenario']}")
        
        # Errors
        if self.test_results['errors']:
            self.log(f"\n⚠️  Errors encountered:")
            for error in self.test_results['errors']:
                self.log(f"   • {error}")
        
        # Success criteria
        self.log(f"\n✅ Success Criteria Check:")
        success_rate = (self.test_results['passed'] / self.test_results['total_tests'] * 100)
        self.log(f"   • All requests return 200 OK: {'✅' if self.test_results['failed'] == 0 else '❌'}")
        self.log(f"   • All 8 sections present: {'✅' if all(r.get('validation', {}).get('all_8_sections') for r in basic_results if r.get('success')) else '❌'}")
        self.log(f"   • Emotion detection works: {'✅' if all(r.get('emotion_detected') for r in basic_results if r.get('success')) else '❌'}")
        self.log(f"   • Visual schema valid: {'✅' if all(r.get('validation', {}).get('visual_schema_valid') for r in basic_results if r.get('success')) else '❌'}")
        self.log(f"   • No 500 errors: {'✅' if self.test_results['failed'] == 0 else '❌'}")
        
        self.log("\n" + "=" * 80)
        self.log("TESTING COMPLETE", "SUCCESS")
        self.log("=" * 80)


if __name__ == "__main__":
    tester = NeuroSymbolicTester()
    tester.run_comprehensive_tests()
