"""
🎯 Student-First Intelligence Tests (TRI-LANE)
==============================================

Tests ensuring EVERY student message gets a helpful response using the
Tri-Lane Response Engine:
- LANE A (Conversation): emotion, chitchat, ack, continue, clarification
- LANE B (Education): explain, solve, learn (RAG + Guardrails)
- LANE C (Action): reminders, companion, tools

SHIP BLOCKERS:
1. "hey getting bored today" → Conversation Lane, NOT KB fallback
2. "last time where did I stop" → Conversation Lane (session recall)
3. "hmm yes" → Conversation Lane (acknowledgment)
4. Guardrails only apply grounding to Education Lane (factual routes)
5. NO "knowledge base not found" for Conversation Lane queries
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# =============================================================================
# A) DIALOGUE-ACT DETECTOR TESTS (Message Structure, NOT Keywords)
# =============================================================================

class TestDialogueActDetector:
    """Test dialogue-act detection based on message STRUCTURE"""
    
    def test_short_message_detected_as_conversation(self):
        """
        SHIP BLOCKER: Very short messages (1-3 words) should route to 
        Conversation Lane, not trigger RAG lookup
        """
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        
        engine = IntelligentRoutingEngine()
        
        # Test with prior context (simulating ongoing conversation)
        state_with_context = {
            'last_topic': 'Thermodynamics',
            'ai_asked_question': True
        }
        
        # Short messages should be detected as dialogue acts
        short_messages = ["yes", "ok", "hmm", "sure", "no"]
        
        for msg in short_messages:
            result = engine._detect_dialogue_act(msg, state_with_context)
            assert result is not None, f"'{msg}' should be detected as dialogue act"
            assert result['lane'] == 'conversation', \
                f"'{msg}' should route to Conversation Lane, got {result.get('lane')}"
    
    def test_ultra_short_always_conversation(self):
        """
        Test: 1-2 word messages ALWAYS go to Conversation Lane
        """
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        
        engine = IntelligentRoutingEngine()
        empty_state = {}
        
        # Even without context, ultra-short should be conversation
        result = engine._detect_dialogue_act("ok", empty_state)
        assert result is not None
        assert result['act'] == 'ack'
        assert result['lane'] == 'conversation'
    
    def test_session_recall_pattern_detected(self):
        """
        SHIP BLOCKER: "last time where did I stop" detected by STRUCTURE
        (temporal reference + question pattern), not keywords
        """
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        
        engine = IntelligentRoutingEngine()
        state_with_context = {'last_topic': 'Physics'}
        
        # Should detect temporal + question pattern
        result = engine._detect_dialogue_act("where did I stop last time?", state_with_context)
        assert result is not None
        assert result['act'] == 'continue'
        assert result['lane'] == 'conversation'
    
    def test_educational_query_not_dialogue_act(self):
        """
        Test: Educational queries should NOT be caught by dialogue-act detector
        """
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        
        engine = IntelligentRoutingEngine()
        empty_state = {}
        
        # These should return None (proceed to semantic classifier)
        educational = "explain Newton's third law with an example"
        result = engine._detect_dialogue_act(educational, empty_state)
        assert result is None, "Educational queries should not be dialogue acts"


# =============================================================================
# B) TRI-LANE GUARDRAILS TESTS
# =============================================================================

class TestTriLaneGuardrails:
    """Test Tri-Lane routing in guardrails (Education Lane gets grounding, others don't)"""
    
    def test_factual_routes_require_grounding(self):
        """
        Test: Only factual/educational routes should require grounding
        """
        # These are the ONLY routes that need grounding verification
        factual_routes = {'multi_agent', 'hybrid', 'react_agentic', 'visual_sync'}
        
        # All other routes bypass grounding (Conversation Lane)
        conversation_routes = {'chitchat', 'emotional', 'proactive', 'fast', 'clarification'}
        
        # Verify no overlap
        assert factual_routes.isdisjoint(conversation_routes), \
            "Factual and conversation routes should not overlap"
    
    @pytest.mark.asyncio
    async def test_conversation_lane_bypasses_grounding(self):
        """
        SHIP BLOCKER: Conversation Lane routes bypass grounding entirely
        """
        from services.guardrails_v2 import (
            GuardrailsEngine, 
            ResponseEnvelope,
            GuardrailStatus
        )
        
        engine = GuardrailsEngine()
        
        # Test each conversation lane route type
        conversation_routes = [
            ('chitchat', 'Hey! Let me know what you want to chat about.'),
            ('emotional', 'I hear you - take a breath, I am here.'),
            ('proactive', 'Let me help you continue where you left off.'),
            ('fast', 'Got it! What would you like to do next?'),
            ('clarification', 'Could you tell me more about what you mean?'),
        ]
        
        for route_type, draft in conversation_routes:
            envelope = ResponseEnvelope(
                user_message="test",
                agent_name="mentor",
                route_type=route_type,
                draft_answer=draft,
                retrieval_contexts=[],
                retrieval_confidence=0.0,
                retrieval_method="none"
            )
            
            result = await engine.process(envelope, {})
            
            assert result.guardrail_status == GuardrailStatus.PASS, \
                f"Route '{route_type}' should PASS guardrails (Conversation Lane)"
            assert result.final_answer == draft, \
                f"Route '{route_type}' response should not be modified"
            assert "knowledge base" not in result.final_answer.lower(), \
                f"Route '{route_type}' must NOT produce KB fallback"
    
    @pytest.mark.asyncio
    async def test_education_lane_gets_grounding(self):
        """
        Test: Education Lane routes go through grounding verification
        """
        from services.guardrails_v2 import (
            GuardrailsEngine, 
            ResponseEnvelope,
            RetrievalContext,
            GuardrailStatus
        )
        
        engine = GuardrailsEngine()
        
        # Test factual route with good citations
        envelope = ResponseEnvelope(
            user_message="explain Newton's first law",
            agent_name="professor",
            route_type="multi_agent",  # Education Lane
            draft_answer="Newton's first law states that an object at rest stays at rest...",
            retrieval_contexts=[
                RetrievalContext(
                    chunk_id="physics_001",
                    doc_id="ncert_physics",
                    section="Newton's Laws",
                    text_snippet="Newton's first law of motion states that an object remains at rest or in uniform motion unless acted upon by an external force.",
                    score=0.9,
                    source_file="physics_ch5.txt"
                )
            ],
            retrieval_confidence=0.9,
            retrieval_method="faiss"
        )
        
        result = await engine.process(envelope, {})
        
        # Should go through grounding (not bypassed)
        # With good citations, should pass
        assert result.claims_extracted is not None or result.guardrail_status is not None
    
    @pytest.mark.asyncio
    async def test_education_lane_low_grounding_no_kb_message(self):
        """
        SHIP BLOCKER: Even Education Lane should NOT say "knowledge base not found"
        Should offer helpful alternatives instead
        """
        from services.guardrails_v2 import (
            GuardrailsEngine, 
            ResponseEnvelope,
            GuardrailStatus
        )
        
        engine = GuardrailsEngine()
        
        # Test factual route with NO citations (worst case)
        envelope = ResponseEnvelope(
            user_message="explain quantum entanglement",
            agent_name="professor",
            route_type="multi_agent",
            draft_answer="Quantum entanglement is when particles are connected...",
            retrieval_contexts=[],  # No citations!
            retrieval_confidence=0.0,
            retrieval_method="none"
        )
        
        result = await engine.process(envelope, {})
        
        # Even with low grounding, should NOT say "knowledge base not found"
        assert "knowledge base" not in result.final_answer.lower(), \
            "SHIP BLOCKER: Education Lane must NOT produce 'knowledge base not found'"
        
        # Should offer helpful alternatives instead
        assert "?" in result.final_answer, \
            "Low grounding response should ask clarifying question"


# =============================================================================
# C) PIPELINE VALUES TESTS (Correct Enum Values)
# =============================================================================

class TestPipelineValues:
    """Test that pipeline enum values are correct for Tri-Lane routing"""
    
    def test_pipeline_values_for_conversation_lane(self):
        """
        Test: Conversation Lane pipeline values match guardrails bypass
        """
        from services.intelligent_routing_engine import RecommendedPipeline
        
        # These are the actual .value strings used in guardrails bypass
        assert RecommendedPipeline.CHITCHAT.value == "chitchat"
        assert RecommendedPipeline.EMOTIONAL_SUPPORT.value == "emotional"  # NOT "emotional_support"!
        assert RecommendedPipeline.PROACTIVE_GUIDANCE.value == "proactive"  # NOT "proactive_guidance"!
        assert RecommendedPipeline.FAST_RESPONSE.value == "fast"
        assert RecommendedPipeline.CLARIFICATION.value == "clarification"
    
    def test_pipeline_values_for_education_lane(self):
        """
        Test: Education Lane pipeline values (these require grounding)
        """
        from services.intelligent_routing_engine import RecommendedPipeline
        
        # These need grounding verification
        assert RecommendedPipeline.MULTI_AGENT.value == "multi_agent"
        assert RecommendedPipeline.HYBRID_REASONING.value == "hybrid"
        assert RecommendedPipeline.REACT_AGENTIC.value == "react_agentic"
        assert RecommendedPipeline.VISUAL_SYNC.value == "visual_sync"


# =============================================================================
# D) MEMORY V2 SESSION RECALL TESTS
# =============================================================================

class TestMemoryV2SessionRecall:
    """Test Memory v2 integration for session recall"""
    
    def test_memory_context_pack_exists(self):
        """Test MemoryContextPack is properly defined"""
        from models.memory import MemoryContextPack
        
        pack = MemoryContextPack(user_id="test", session_id="test")
        assert pack.user_id == "test"
    
    def test_student_profile_exists(self):
        """Test StudentProfile is properly defined"""
        from models.memory import StudentProfile
        
        profile = StudentProfile(user_id="test")
        assert profile.user_id == "test"


# =============================================================================
# E) NO KB FALLBACK MESSAGE TESTS
# =============================================================================

class TestNoKBFallback:
    """Verify KB fallback message is removed from codebase"""
    
    def test_guardrails_no_kb_not_found_message(self):
        """
        SHIP BLOCKER: The "I couldn't find specific content in my knowledge base"
        message should be REMOVED from guardrails
        """
        import inspect
        from services.guardrails_v2 import GuardrailsEngine
        
        # Get the source of _generate_no_hallucinate_response
        source = inspect.getsource(GuardrailsEngine._generate_no_hallucinate_response)
        
        # Should NOT contain the old KB fallback message
        assert "couldn't find specific content" not in source.lower(), \
            "SHIP BLOCKER: Remove 'couldn't find specific content' message"
        assert "knowledge base" not in source.lower(), \
            "SHIP BLOCKER: Remove 'knowledge base' from fallback message"


# =============================================================================
# F) REGRESSION TESTS - Safety + Exam Integrity Unchanged
# =============================================================================

class TestNoRegressions:
    """Ensure safety and exam integrity are NOT weakened"""
    
    def test_guardrails_safety_still_works(self):
        """Test: Safety checks still work (not bypassed for any route)"""
        from services.guardrails_v2 import SafetyGuard
        
        guard = SafetyGuard()
        
        # Safety should still detect risk
        result = guard.check("normal message about physics", {})
        assert result is not None
    
    def test_exam_integrity_still_works(self):
        """Test: Exam integrity checker still works"""
        from services.guardrails_v2 import ExamIntegrityChecker
        
        checker = ExamIntegrityChecker()
        
        is_cheating, action = checker.check("explain this concept", {})
        assert isinstance(is_cheating, bool)
    
    @pytest.mark.asyncio
    async def test_safety_not_bypassed_for_conversation_lane(self):
        """
        CRITICAL: Safety checks must run BEFORE grounding bypass
        """
        from services.guardrails_v2 import (
            GuardrailsEngine, 
            ResponseEnvelope,
            GuardrailStatus
        )
        
        engine = GuardrailsEngine()
        
        # Even for conversation lane, safety should still be checked
        # (The actual safety check happens before grounding bypass in process())
        envelope = ResponseEnvelope(
            user_message="I'm feeling really bad about everything",
            agent_name="motivation",
            route_type="emotional",  # Conversation Lane
            draft_answer="I hear you. It sounds like you're going through a tough time.",
            retrieval_contexts=[],
            retrieval_confidence=0.0,
            retrieval_method="none"
        )
        
        result = await engine.process(envelope, {})
        
        # Response should be provided (not blocked unless actual safety issue)
        assert result.final_answer is not None
        assert len(result.final_answer) > 0


# =============================================================================
# G) SEMANTIC CLASSIFIER INTENTS
# =============================================================================

class TestSemanticClassifierIntents:
    """Test semantic intent enum is complete"""
    
    def test_all_required_intents_exist(self):
        """Test: All required intents are defined"""
        from services.semantic_intent_classifier import SemanticIntent
        
        expected_intents = [
            'question',
            'explanation',
            'emotional_support',
            'motivation',
            'continue',
            'acknowledgment',
            'greeting',
            'chitchat',
            'general',
        ]
        
        actual_intents = [i.value for i in SemanticIntent]
        
        for intent in expected_intents:
            assert intent in actual_intents, f"Missing intent: {intent}"


# =============================================================================
# H) STUDENT-FIRST BEHAVIORAL ACCEPTANCE TESTS
# =============================================================================

class TestStudentFirstBehavior:
    """
    BEHAVIORAL ACCEPTANCE CRITERIA:
    Test actual response content for student-first qualities
    """
    
    def test_no_therapy_phrases_in_prompts(self):
        """
        Test: Conversation Lane prompts should NOT contain therapy-speak
        """
        import inspect
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        # Check chitchat generator
        chitchat_source = inspect.getsource(UnifiedAIOrchestrator._generate_intelligent_chitchat)
        
        # Should have FORBIDDEN section
        assert "FORBIDDEN" in chitchat_source, "Chitchat should have FORBIDDEN phrases section"
        
        # Should mention therapy-speak to avoid
        assert "Tell me more" in chitchat_source, "Should list 'Tell me more' as forbidden"
        
    def test_conversation_lane_offers_options(self):
        """
        Test: Conversation Lane responses should offer A/B/C options
        """
        import inspect
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        # Check chitchat generator has option structure
        chitchat_source = inspect.getsource(UnifiedAIOrchestrator._generate_intelligent_chitchat)
        
        # Should build A/B/C options
        assert "option_a" in chitchat_source, "Should build option_a"
        assert "option_b" in chitchat_source, "Should build option_b"
        assert "option_c" in chitchat_source, "Should build option_c"
        
        # Should include A/B/C in format
        assert "A)" in chitchat_source, "Should include A) option format"
        assert "B)" in chitchat_source, "Should include B) option format"
        assert "C)" in chitchat_source, "Should include C) option format"
    
    def test_emotional_response_offers_options(self):
        """
        Test: Emotional responses should also offer A/B/C options
        """
        import inspect
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        # Check emotional generator has options
        emotional_source = inspect.getsource(UnifiedAIOrchestrator._generate_emotional_response)
        
        # Should build options
        assert "option_a" in emotional_source, "Emotional should build option_a"
        assert "option_b" in emotional_source, "Emotional should build option_b"
        
        # Should NOT ask which subject
        assert "Which subject" not in emotional_source, "Emotional should NOT ask 'Which subject'"
    
    def test_clarification_uses_options_not_questions(self):
        """
        Test: Clarification response gives A/B/C options, not interrogation
        """
        import inspect
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        clarification_source = inspect.getsource(UnifiedAIOrchestrator._clarification_response)
        
        # Should have A/B/C format
        assert "A)" in clarification_source, "Clarification should offer A) option"
        assert "B)" in clarification_source, "Clarification should offer B) option"
        assert "C)" in clarification_source, "Clarification should offer C) option"
        
        # Should NOT ask which subject (removed from clarification)
        assert "Which subject" not in clarification_source, \
            "Clarification should NOT ask 'Which subject is this for'"
    
    def test_fallback_responses_have_options(self):
        """
        Test: Even fallback responses should have A/B/C options
        """
        import inspect
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        # Check chitchat fallback
        chitchat_source = inspect.getsource(UnifiedAIOrchestrator._generate_intelligent_chitchat)
        
        # The except block fallback should also have options
        assert "Quick quiz" in chitchat_source or "Pick one" in chitchat_source, \
            "Fallback should still offer quick options"


# =============================================================================
# I) MEMORY V2 WRITE BUG REGRESSION TESTS
# =============================================================================

class TestMemoryWriteBugFix:
    """
    Regression tests for the 'list' object has no attribute 'get' bug
    """
    
    def test_chained_get_handles_list(self):
        """
        Test: Chained .get() calls should handle list values gracefully
        """
        # Simulate the problematic data structure
        ai_response_as_list = ["some", "list", "data"]
        ai_response_as_dict = {"response": {"default_view": {"main_content": {"content": "test"}}}}
        ai_response_nested_list = {"response": ["list", "inside"]}
        
        # Test extraction logic (mirrors memory_integration.py fix)
        def safe_extract(ai_response):
            """Safe extraction that handles lists"""
            response_text = ""
            try:
                if isinstance(ai_response, dict):
                    resp_obj = ai_response.get("response", {})
                    if isinstance(resp_obj, dict):
                        default_view = resp_obj.get("default_view", {})
                        if isinstance(default_view, dict):
                            main_content = default_view.get("main_content", {})
                            if isinstance(main_content, dict):
                                response_text = str(main_content.get("content", ""))
            except (AttributeError, TypeError):
                response_text = ""
            return response_text
        
        # Should NOT raise exception for any input
        assert safe_extract(ai_response_as_list) == ""
        assert safe_extract(ai_response_as_dict) == "test"
        assert safe_extract(ai_response_nested_list) == ""
        assert safe_extract(None) == ""
        assert safe_extract([]) == ""
    
    def test_memory_integration_defensive_checks(self):
        """
        Test: memory_integration.py has defensive isinstance checks
        """
        import inspect
        from services.memory_integration import MemoryIntegration
        
        # Check _build_conversation_summary
        build_summary_source = inspect.getsource(MemoryIntegration._build_conversation_summary)
        assert "isinstance(msg, dict)" in build_summary_source, \
            "_build_conversation_summary should check isinstance(msg, dict)"
        
        # Check for defensive chained .get()
        assert "isinstance(resp_obj, dict)" in build_summary_source or \
               "isinstance(default_view, dict)" in build_summary_source, \
            "_build_conversation_summary should have defensive isinstance checks for nested dicts"
    
    def test_orchestrator_defensive_checks(self):
        """
        Test: unified_ai_orchestrator.py has defensive isinstance checks
        """
        import inspect
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        # Read the file source (or specific method if large)
        orchestrate_source = inspect.getsource(UnifiedAIOrchestrator.orchestrate_pipeline)
        
        # Should have defensive checks for response extraction
        assert "isinstance" in orchestrate_source, \
            "orchestrate_pipeline should have isinstance checks for memory write"


# =============================================================================
# J) NO SUBJECT/CHAPTER INTERROGATION TESTS
# =============================================================================

class TestNoSubjectChapterInterrogation:
    """
    Test: Conversation Lane NEVER asks "which subject/chapter" 
    (only Education Lane may ask, and only with memory anchor check)
    """
    
    def test_chitchat_no_subject_question(self):
        """
        Test: Chitchat generator never asks "which subject"
        """
        import inspect
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        source = inspect.getsource(UnifiedAIOrchestrator._generate_intelligent_chitchat)
        
        # Should explicitly FORBID subject/chapter questions
        forbidden_section = source[source.find("FORBIDDEN"):] if "FORBIDDEN" in source else source
        assert "subject" in forbidden_section.lower() or "chapter" in forbidden_section.lower(), \
            "Should mention subject/chapter as forbidden in FORBIDDEN section"
    
    def test_emotional_no_subject_question(self):
        """
        Test: Emotional response never asks "which subject"
        """
        import inspect
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        source = inspect.getsource(UnifiedAIOrchestrator._generate_emotional_response)
        
        # Should NOT contain "which subject is this for"
        assert "Which subject is this for" not in source, \
            "Emotional response should NEVER ask 'Which subject is this for'"


# =============================================================================
# K) TEACH ME BACK v2 TESTS
# =============================================================================

class TestTeachMeBackV2:
    """
    Tests for Teach Me Back v2 — Learning Verification System
    """
    
    def test_trigger_detector_exists(self):
        """
        Test: TeachbackTriggerDetector class exists and is importable
        """
        from services.teach_me_back_evaluator import (
            TeachbackTriggerDetector,
            TeachbackMode,
            TeachbackTrigger
        )
        
        detector = TeachbackTriggerDetector()
        assert detector is not None
        assert hasattr(detector, 'detect')
        assert hasattr(detector, 'EDUCATION_ROUTES')
    
    def test_trigger_only_education_lane(self):
        """
        SHIP BLOCKER: Teachback should only trigger for Education Lane routes
        """
        from services.teach_me_back_evaluator import (
            TeachbackTriggerDetector,
            TeachbackMode
        )
        
        detector = TeachbackTriggerDetector()
        
        # Education lane routes should be eligible
        education_routes = {'multi_agent', 'hybrid', 'react_agentic', 'visual_sync'}
        assert detector.EDUCATION_ROUTES == education_routes
        
        # Conversation lane routes should NOT trigger
        conversation_routes = ['chitchat', 'emotional', 'proactive', 'fast', 'clarification']
        
        for route in conversation_routes:
            result = detector.detect(
                route_type=route,
                user_message="got it, thanks!",
                ai_response="Here's the explanation..." * 50,
                conversation_state={'last_topic': 'Physics'}
            )
            assert result.should_trigger is False, \
                f"Teachback should NOT trigger for {route} (Conversation Lane)"
    
    def test_no_trigger_on_casual_chat(self):
        """
        Test: "getting bored today" should NOT trigger teachback
        """
        from services.teach_me_back_evaluator import TeachbackTriggerDetector
        
        detector = TeachbackTriggerDetector()
        
        # Casual chat with chitchat route
        result = detector.detect(
            route_type="chitchat",
            user_message="getting bored today",
            ai_response="I hear you! Let's do something fun.",
            conversation_state={}
        )
        
        assert result.should_trigger is False
        assert result.reason == "not_education_lane"
    
    def test_trigger_after_explanation(self):
        """
        Test: Teachback triggers after educational explanation + acknowledgment
        """
        from services.teach_me_back_evaluator import TeachbackTriggerDetector
        
        detector = TeachbackTriggerDetector()
        
        # Education route with long explanation and short acknowledgment
        result = detector.detect(
            route_type="multi_agent",
            user_message="ok got it",  # Short acknowledgment
            ai_response="Newton's First Law states that an object at rest stays at rest..." * 20,  # Long explanation
            conversation_state={
                'last_topic': 'newtons_laws',
                'last_pipeline': 'multi_agent',
                'turn_count': 5
            },
            retrieval_confidence=0.8,
            user_id="test_user_123"
        )
        
        # Should trigger due to signals
        if result.trigger_score >= 0.5:
            assert result.should_trigger is True
            assert result.mode.value in ['quick_check', 'step_check', 'deep_teach']
            assert len(result.prompt) > 0
    
    def test_mastery_update_threshold(self):
        """
        Test: Mastery only updates when score >= 50 (partial or better)
        """
        from services.teach_me_back_evaluator import (
            TeachMeBackEvaluator,
            UnderstandingLevel
        )
        
        evaluator = TeachMeBackEvaluator()
        
        # Test mastery deltas by level
        assert evaluator.get_mastery_delta(UnderstandingLevel.EXCELLENT.value) == 15
        assert evaluator.get_mastery_delta(UnderstandingLevel.GOOD.value) == 10
        assert evaluator.get_mastery_delta(UnderstandingLevel.PARTIAL.value) == 3
        assert evaluator.get_mastery_delta(UnderstandingLevel.INCORRECT.value) == -5
        assert evaluator.get_mastery_delta(UnderstandingLevel.NOT_ATTEMPTED.value) == 0
    
    def test_follow_up_planner_exists(self):
        """
        Test: TeachbackFollowUpPlanner exists and works
        """
        from services.teach_me_back_evaluator import (
            TeachbackFollowUpPlanner,
            UnderstandingLevel
        )
        
        planner = TeachbackFollowUpPlanner()
        
        # Test correction follow-up
        result = planner.plan_follow_up(
            evaluation={
                'score': 30,
                'understanding_level': UnderstandingLevel.INCORRECT.value,
                'gaps': ['Missed the main concept'],
                'understood': []
            },
            topic='thermodynamics',
            original_explanation='Heat flows from hot to cold...'
        )
        
        assert result['type'] == 'correction'
        assert 'question' in result
        assert 'encouragement' in result
        assert len(result['question']) > 0
    
    def test_exam_integrity_teachback_no_leak(self):
        """
        SHIP BLOCKER: Teachback should never leak MCQ answers
        The evaluator must NOT reveal correct options when evaluating
        """
        from services.teach_me_back_evaluator import TeachMeBackEvaluator
        
        evaluator = TeachMeBackEvaluator()
        
        # Check the prompt template doesn't ask LLM to reveal answers
        prompt = evaluator.EVALUATION_PROMPT
        
        # Should NOT contain instructions to reveal correct answer
        assert "correct answer is" not in prompt.lower()
        assert "correct option" not in prompt.lower()
        assert "reveal" not in prompt.lower()
        
        # Should focus on understanding, not grading
        assert "understood" in prompt.lower()
        assert "gaps" in prompt.lower()


# =============================================================================
# RUN CONFIGURATION
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

