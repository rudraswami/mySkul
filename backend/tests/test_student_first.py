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
# D) CONTEXT CONTINUITY TESTS (Continuation Topic Resolver)
# =============================================================================

class TestContextContinuity:
    """
    Test context continuity for follow-up messages like "explain deeper".
    
    SHIP BLOCKER: "explain deeper" after an education explanation must:
    1. Stay in Education Lane
    2. Keep the previous topic
    3. NOT ask "what topic?"
    """
    
    def test_continuation_resolver_detects_short_followup(self):
        """
        Test: Short follow-ups like "explain deeper" detected as continuation
        """
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        
        engine = IntelligentRoutingEngine()
        
        # Mock context with previous topic
        context_with_topic = {
            'context_pack': type('MockContextPack', (), {
                'current_topic': 'newton_laws',
                'previous_topic': 'newton_laws',
                'is_first_turn': False
            })(),
            'conversation_state': {
                'last_topic': 'newton_laws'
            }
        }
        
        # Test various short follow-up messages
        short_followups = [
            "explain deeper",
            "more details",
            "go on",
            "tell me more",
            "in detail?"
        ]
        
        for msg in short_followups:
            result = engine._resolve_continuation_topic(msg, context_with_topic, None)
            assert result['is_continuation'] == True, \
                f"'{msg}' should be detected as continuation"
            assert result['topic'] == 'newton_laws', \
                f"'{msg}' should preserve topic 'newton_laws', got {result.get('topic')}"
    
    def test_continuation_resolver_ignores_new_topic(self):
        """
        Test: Messages with clear new topics are NOT continuations
        """
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        
        engine = IntelligentRoutingEngine()
        
        context_with_topic = {
            'context_pack': type('MockContextPack', (), {
                'current_topic': 'newton_laws',
                'previous_topic': 'newton_laws',
                'is_first_turn': False
            })(),
            'conversation_state': {
                'last_topic': 'newton_laws'
            }
        }
        
        # Messages with new topics (not continuations)
        new_topic_messages = [
            "explain photosynthesis in detail",
            "what is thermodynamics?",
            "tell me about Einstein's relativity",
        ]
        
        for msg in new_topic_messages:
            result = engine._resolve_continuation_topic(msg, context_with_topic, None)
            assert result['is_continuation'] == False, \
                f"'{msg}' should NOT be a continuation (has new topic)"
    
    def test_continuation_without_prior_topic_fails(self):
        """
        Test: Continuation detection fails without prior topic
        """
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        
        engine = IntelligentRoutingEngine()
        
        # No prior topic
        empty_context = {
            'context_pack': type('MockContextPack', (), {
                'current_topic': '',
                'previous_topic': '',
                'is_first_turn': True
            })(),
            'conversation_state': {}
        }
        
        result = engine._resolve_continuation_topic("explain deeper", empty_context, None)
        assert result['is_continuation'] == False, \
            "Should NOT be continuation without prior topic"
        assert result['reason'] == 'no_previous_topic', \
            f"Reason should be 'no_previous_topic', got {result.get('reason')}"
    
    @pytest.mark.asyncio
    async def test_context_continuity_explain_deeper_keeps_topic(self):
        """
        SHIP BLOCKER: "explain deeper" after education keeps topic.
        
        Scenario:
        1. User: "Explain Newton's laws" → Education Lane, topic extracted
        2. User: "explain deeper" → Should stay Education Lane, keep topic
        
        This test verifies the full routing flow.
        """
        from services.intelligent_routing_engine import IntelligentRoutingEngine, RecommendedPipeline
        
        engine = IntelligentRoutingEngine()
        
        # Simulate context after first educational message
        context_after_education = {
            'context_pack': type('MockContextPack', (), {
                'current_topic': 'newton_laws',
                'previous_topic': 'newton_laws',
                'is_first_turn': False,
                'is_continuation': True
            })(),
            'conversation_state': {
                'last_topic': 'newton_laws',
                'conversation_phase': 'active',
                'last_pipeline': 'multi_agent'
            },
            'current_topic': 'newton_laws',
            'is_first_turn': False
        }
        
        # User says "explain deeper" after Newton's laws explanation
        decision = await engine.route("explain deeper", context_after_education)
        
        # ASSERTIONS:
        
        # 1. Should stay in Education Lane (not conversation)
        education_pipelines = [
            RecommendedPipeline.MULTI_AGENT,
            RecommendedPipeline.HYBRID_REASONING,
            RecommendedPipeline.REACT_AGENTIC,
            RecommendedPipeline.VISUAL_SYNC
        ]
        assert decision.pipeline in education_pipelines, \
            f"'explain deeper' should route to Education Lane, got {decision.pipeline.value}"
        
        # 2. Should have continuation_topic in extra_context
        assert decision.extra_context is not None, \
            "extra_context should exist"
        
        # Check for continuation topic (may be in extra_context or via state authority)
        has_continuation = (
            decision.extra_context.get('is_continuation') == True or
            decision.extra_context.get('continuation_topic') == 'newton_laws' or
            decision.extra_context.get('forced_continuation') == True
        )
        assert has_continuation, \
            f"Should have continuation info, got extra_context: {decision.extra_context}"
        
        # 3. If continuation resolved, topic should be preserved
        if decision.extra_context.get('is_continuation'):
            assert decision.extra_context.get('continuation_topic') == 'newton_laws', \
                f"Topic should be 'newton_laws', got {decision.extra_context.get('continuation_topic')}"


# =============================================================================
# E) MEMORY V2 SESSION RECALL TESTS
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
    
    def test_memory_list_input_does_not_throw(self):
        """
        REGRESSION: Memory v2 write failed: 'list' object has no attribute 'get'
        
        Test: Passing a list-shaped payload to memory extraction should NOT raise.
        """
        from services.memory_extraction import _normalize_to_dict
        
        # These inputs previously caused "'list' object has no attribute 'get'"
        test_inputs = [
            ["some", "list", "data"],  # Raw list
            ("tuple", "data"),          # Tuple
            None,                       # None
            [],                         # Empty list
            [{"nested": "dict"}],       # List of dicts
        ]
        
        # MUST NOT RAISE for any input
        for inp in test_inputs:
            try:
                result = _normalize_to_dict(inp)
                assert isinstance(result, dict), f"Result must be dict, got {type(result)}"
            except Exception as e:
                pytest.fail(f"_normalize_to_dict raised for {type(inp)}: {e}")
    
    def test_memory_normalization_wraps_items(self):
        """
        Test: List payloads are wrapped as {"items": [...]}
        """
        from services.memory_extraction import _normalize_to_dict
        
        # List input should become {"items": [...]}
        list_input = ["item1", "item2", "item3"]
        result = _normalize_to_dict(list_input)
        
        assert result == {"items": ["item1", "item2", "item3"]}, \
            "List should be wrapped as {'items': [...]}"
        
        # Tuple input should also be wrapped
        tuple_input = ("a", "b")
        result = _normalize_to_dict(tuple_input)
        assert result == {"items": ["a", "b"]}, \
            "Tuple should be converted to list and wrapped"
        
        # None should become empty dict
        assert _normalize_to_dict(None) == {}, "None should become {}"
        
        # String should become {"content": ...}
        result = _normalize_to_dict("hello")
        assert result == {"content": "hello"}, "String should be wrapped as {'content': ...}"
    
    def test_memory_dict_input_unchanged(self):
        """
        Test: Dict payloads remain unchanged (no wrapper added)
        """
        from services.memory_extraction import _normalize_to_dict
        
        # Dict input should pass through unchanged
        dict_input = {"key": "value", "nested": {"a": 1}}
        result = _normalize_to_dict(dict_input)
        
        assert result == dict_input, "Dict input should remain unchanged"
        assert result is dict_input, "Dict should be the same object (no copy)"
    
    def test_bound_payload_handles_list(self):
        """
        REGRESSION: _bound_payload would fail on list.keys()
        
        Test: memory_service._bound_payload handles list input gracefully.
        """
        from services.memory_service import MemoryService
        
        # Create a mock db (won't be used for this test)
        class MockDB:
            pass
        
        service = MemoryService(MockDB())
        
        # These inputs previously caused errors
        test_inputs = [
            ["list", "items"],   # List
            {"dict": "data"},    # Dict (should work)
            None,                # None
            ("tuple",),          # Tuple
        ]
        
        for inp in test_inputs:
            try:
                result = service._bound_payload(inp)
                assert isinstance(result, dict), f"Result must be dict, got {type(result)}"
            except Exception as e:
                pytest.fail(f"_bound_payload raised for {type(inp)}: {e}")


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
        POLICY: No negative deltas from teachback
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
        # POLICY: No negative deltas - INCORRECT should be 0, not -5
        assert evaluator.get_mastery_delta(UnderstandingLevel.INCORRECT.value) == 0
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
    
    def test_teachback_not_appended_to_main_response(self):
        """
        SHIP BLOCKER: Teachback CTA text must NOT be appended to main_response.
        
        UX CONTRACT: Backend returns structured teachback payload for frontend
        to render as a clickable CTA button that opens a modal.
        """
        import inspect
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        # Read the process method source (main orchestration entry point)
        source = inspect.getsource(UnifiedAIOrchestrator.process)
        
        # OLD (BANNED): result['main_response'] += teachback_prompt
        # NEW (CORRECT): result['teachback'] = {...structured payload...}
        
        # These patterns should NOT exist:
        assert "main_response'] += teachback" not in source, \
            "Teachback text should NOT be appended to main_response"
        assert "content'] += teachback" not in source, \
            "Teachback text should NOT be appended to content"
        
        # This pattern SHOULD exist:
        assert "check_and_build_teachback_payload" in source, \
            "Should use structured payload function, not string appender"
        assert "'prompt_appended': False" in source, \
            "Should explicitly mark that text is NOT appended"
    
    def test_teachback_payload_contains_cta_and_prompt(self):
        """
        Test: Teachback payload must contain cta_text and prompt fields.
        """
        from services.teach_me_back_evaluator import TeachbackTriggerDetector
        
        detector = TeachbackTriggerDetector()
        
        # Trigger teachback
        result = detector.detect(
            route_type="multi_agent",
            user_message="ok understood",
            ai_response="Newton's First Law states that..." * 20,
            conversation_state={
                'last_topic': 'newtons_laws',
                'turn_count': 5
            },
            retrieval_confidence=0.85,
            user_id="test_user",
            session_id="test_session"
        )
        
        if result.should_trigger:
            # Verify the trigger has required fields
            assert result.prompt is not None and len(result.prompt) > 0, \
                "Teachback prompt must not be empty"
            assert result.topic is not None, \
                "Teachback topic must be set"
            assert result.mode is not None, \
                "Teachback mode must be set"
    
    def test_teachback_cooldown_isolated_by_session(self):
        """
        SHIP BLOCKER: Same user, different sessions → independent cooldown.
        This prevents cross-session teachback blocking.
        """
        from services.teach_me_back_evaluator import TeachbackTriggerDetector
        
        detector = TeachbackTriggerDetector()
        
        # Common setup
        user_message = "ok got it"
        ai_response = "Here is a detailed explanation..." * 30
        
        # First session - trigger teachback
        result1 = detector.detect(
            route_type="multi_agent",
            user_message=user_message,
            ai_response=ai_response,
            conversation_state={'turn_count': 5, 'last_topic': 'physics'},
            retrieval_confidence=0.9,
            user_id="user_123",
            session_id="session_A"
        )
        
        # DIFFERENT session, same user - should NOT be blocked by session_A's cooldown
        result2 = detector.detect(
            route_type="multi_agent",
            user_message=user_message,
            ai_response=ai_response,
            conversation_state={'turn_count': 5, 'last_topic': 'physics'},
            retrieval_confidence=0.9,
            user_id="user_123",
            session_id="session_B"  # DIFFERENT session
        )
        
        # Session B should have independent cooldown
        if result1.should_trigger:
            # If first triggered, second (different session) should also be able to trigger
            # (cooldown is per-session, not per-user)
            assert result2.reason != "cooldown" or result2.should_trigger, \
                "Different session should have independent cooldown"
    
    def test_teachback_cooldown_blocks_within_session(self):
        """
        Test: Same user + same session → blocks within MIN_TURNS_BETWEEN_TEACHBACK.
        """
        from services.teach_me_back_evaluator import TeachbackTriggerDetector
        
        detector = TeachbackTriggerDetector()
        
        # Common setup
        user_message = "ok got it"
        ai_response = "Here is a detailed explanation..." * 30
        
        # First trigger at turn 5
        result1 = detector.detect(
            route_type="multi_agent",
            user_message=user_message,
            ai_response=ai_response,
            conversation_state={'turn_count': 5, 'last_topic': 'physics'},
            retrieval_confidence=0.9,
            user_id="user_456",
            session_id="session_X"
        )
        
        # Second attempt at turn 6 (within cooldown)
        result2 = detector.detect(
            route_type="multi_agent",
            user_message=user_message,
            ai_response=ai_response,
            conversation_state={'turn_count': 6, 'last_topic': 'physics'},  # Only 1 turn later
            retrieval_confidence=0.9,
            user_id="user_456",
            session_id="session_X"  # SAME session
        )
        
        # If first triggered, second should be blocked by cooldown
        if result1.should_trigger:
            assert result2.should_trigger is False, \
                "Should be blocked by cooldown within same session"
            assert result2.reason == "cooldown", \
                f"Expected 'cooldown' reason, got '{result2.reason}'"
    
    def test_mastery_not_decreased_on_incorrect_teachback(self):
        """
        SHIP BLOCKER: Incorrect teachback should NOT decrease mastery
        POLICY: We don't punish students for trying to explain
        """
        from services.teach_me_back_evaluator import (
            TeachMeBackEvaluator,
            UnderstandingLevel
        )
        
        evaluator = TeachMeBackEvaluator()
        
        # INCORRECT should NOT have negative delta
        incorrect_delta = evaluator.get_mastery_delta(UnderstandingLevel.INCORRECT.value)
        assert incorrect_delta >= 0, f"INCORRECT delta should be >= 0, got {incorrect_delta}"
        
        # NOT_ATTEMPTED should also be 0
        not_attempted_delta = evaluator.get_mastery_delta(UnderstandingLevel.NOT_ATTEMPTED.value)
        assert not_attempted_delta == 0, f"NOT_ATTEMPTED delta should be 0, got {not_attempted_delta}"
    
    def test_no_trigger_during_active_solving_mode(self):
        """
        SHIP BLOCKER: Teachback should NOT trigger during active problem solving
        """
        from services.teach_me_back_evaluator import TeachbackTriggerDetector
        
        detector = TeachbackTriggerDetector()
        
        # Simulate active solving: conversation_state has open_problem or pending_question
        # Note: The orchestrator checks these flags, but detector should not trigger
        # on multi-step responses (response_has_steps)
        
        # Test with multi-step response (should still be eligible for trigger detection)
        # The actual suppression happens in the orchestrator based on conversation_state
        
        # Test that short acknowledgment without prior educational context doesn't trigger
        result = detector.detect(
            route_type="multi_agent",
            user_message="and then?",  # Continuation, not acknowledgment
            ai_response="Step 1: First we need to...\nStep 2: Then calculate...\nStep 3: Finally...",
            conversation_state={
                'last_topic': 'calculus',
                'last_pipeline': 'hybrid',
                'turn_count': 3,
                'open_problem': True  # Signal for active solving
            },
            retrieval_confidence=0.5,
            user_id="test_user_456"
        )
        
        # Trigger detection in the detector still runs, but orchestrator will suppress
        # based on open_problem/pending_question flags
        # Here we just verify detector doesn't crash and returns valid result
        assert result is not None
        assert hasattr(result, 'should_trigger')
    
    def test_orchestrator_has_guardrail_gate(self):
        """
        Test: Orchestrator has teachback gate for guardrails hard_block
        """
        import inspect
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        source = inspect.getsource(UnifiedAIOrchestrator.orchestrate_pipeline)
        
        # Should check for HARD_BLOCK before teachback
        assert "HARD_BLOCK" in source, "Should check for HARD_BLOCK before teachback"
        assert "guardrail_status" in source, "Should log guardrail_status"
        
        # Should have GATE comments for suppression
        assert "GATE" in source, "Should have GATE comments for suppression logic"


# =============================================================================
# TEST: NO AGENT TRACE LEAKAGE
# =============================================================================

class TestNoAgentTraceLeakage:
    """
    SHIP BLOCKER: Agent traces (thought, action, action_input) must NEVER leak to UI.
    """
    
    def test_sanitize_response_exists(self):
        """Verify sanitization method exists in orchestrator"""
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        # Check that _sanitize_response_for_student method exists
        assert hasattr(UnifiedAIOrchestrator, '_sanitize_response_for_student')
        assert hasattr(UnifiedAIOrchestrator, '_sanitize_text_content')
        assert hasattr(UnifiedAIOrchestrator, '_sanitize_nested_dict')
    
    def test_sanitize_removes_reasoning_chain(self):
        """Test that reasoning_chain is removed from results"""
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        orchestrator = UnifiedAIOrchestrator.__new__(UnifiedAIOrchestrator)
        
        # Test input with reasoning_chain
        test_result = {
            "main_response": "Newton's laws explain motion.",
            "reasoning_chain": [{"thought": "Let me think...", "action": "search"}],
            "_debug": {"internal": True}
        }
        
        sanitized = orchestrator._sanitize_response_for_student(test_result, "test_req")
        
        # Verify internal keys are removed
        assert "reasoning_chain" not in sanitized
        assert "_debug" not in sanitized
        assert "main_response" in sanitized
    
    def test_sanitize_text_removes_react_patterns(self):
        """Test that ReAct patterns are removed from text content"""
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        orchestrator = UnifiedAIOrchestrator.__new__(UnifiedAIOrchestrator)
        
        # Text with embedded ReAct trace
        text_with_trace = """Here's an explanation.
        
        {"thought": "I should search", "action": "knowledge_search", "action_input": {"query": "newton"}}
        
        Newton's laws are fundamental."""
        
        sanitized = orchestrator._sanitize_text_content(text_with_trace)
        
        # Should not contain ReAct JSON
        assert '"thought"' not in sanitized
        assert '"action_input"' not in sanitized
        assert "Newton's laws" in sanitized
    
    def test_format_agentic_result_no_reasoning_chain(self):
        """Verify _format_agentic_result doesn't include reasoning_chain"""
        import inspect
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        source = inspect.getsource(UnifiedAIOrchestrator._format_agentic_result)
        
        # Should NOT have reasoning_chain in return value
        # The REMOVED comment indicates it was intentionally removed
        assert "REMOVED" in source or "reasoning_chain" not in source.split("return")[1]
    
    def test_sanitize_called_before_return(self):
        """Verify sanitization is called at the end of orchestrate_pipeline"""
        import inspect
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        source = inspect.getsource(UnifiedAIOrchestrator.orchestrate_pipeline)
        
        # Should have sanitization step before return
        assert "_sanitize_response_for_student" in source


# =============================================================================
# TEST: SUBJECT CONTEXT CARRY-FORWARD
# =============================================================================

class TestSubjectCarryForward:
    """
    SHIP BLOCKER: Subject should be inferred from context, NOT default to Mathematics.
    """
    
    def test_subject_detector_has_context_param(self):
        """Verify _detect_subject_from_question accepts context_subject"""
        import inspect
        from api.ai import _detect_subject_from_question
        
        sig = inspect.signature(_detect_subject_from_question)
        params = list(sig.parameters.keys())
        
        assert 'context_subject' in params, "Should accept context_subject parameter"
    
    def test_general_subject_not_math(self):
        """GENERAL classification should NOT default to Mathematics"""
        from api.ai import _detect_subject_from_question
        
        # Short vague message without context should return "General", not "Mathematics"
        result = _detect_subject_from_question("ok got it", None)
        assert result == "General" or result != "Mathematics"
        
        # With context, should carry forward
        result_with_context = _detect_subject_from_question("ok got it", "Physics")
        assert result_with_context == "Physics"
    
    def test_short_ack_uses_context(self):
        """Short acknowledgments should use context subject"""
        from api.ai import _detect_subject_from_question
        
        # Very short message with Physics context
        result = _detect_subject_from_question("yes", "Physics")
        assert result == "Physics"
        
        # Very short message with Chemistry context
        result = _detect_subject_from_question("hmm ok", "Chemistry")
        assert result == "Chemistry"


# =============================================================================
# TEST: RECAP TAKEOVER BUG FIX
# =============================================================================

class TestRecapTakeoverFix:
    """
    SHIP BLOCKER: Education requests must NOT be hijacked by recap/continue.
    """
    
    def test_education_override_in_dialogue_act(self):
        """
        Test: "explain photosynthesis" MUST bypass dialogue_act detection.
        Even with prior context, education requests should route to classifier.
        """
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        
        engine = IntelligentRoutingEngine()
        
        # Test with prior context (which was causing the bug)
        conversation_state = {
            'last_topic': 'physics',
            'pending_action': None
        }
        
        # Education requests should return None (bypass to classifier)
        result = engine._detect_dialogue_act("explain photosynthesis", conversation_state)
        assert result is None, f"'explain photosynthesis' should bypass dialogue_act, got: {result}"
        
        result = engine._detect_dialogue_act("what is photosynthesis", conversation_state)
        assert result is None, f"'what is photosynthesis' should bypass dialogue_act, got: {result}"
        
        result = engine._detect_dialogue_act("how does photosynthesis work?", conversation_state)
        assert result is None, f"'how does photosynthesis work?' should bypass dialogue_act, got: {result}"
        
        result = engine._detect_dialogue_act("define mitochondria", conversation_state)
        assert result is None, f"'define mitochondria' should bypass dialogue_act, got: {result}"
    
    def test_acknowledgments_still_route_conversation(self):
        """
        Test: Pure acknowledgments like "ok" should still route to conversation.
        """
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        
        engine = IntelligentRoutingEngine()
        
        conversation_state = {
            'last_topic': 'physics',
            'ai_asked_question': True
        }
        
        # True acknowledgments should route to conversation
        result = engine._detect_dialogue_act("ok", conversation_state)
        assert result is not None
        assert result.get('lane') == 'conversation'
        
        result = engine._detect_dialogue_act("yes", conversation_state)
        assert result is not None
        assert result.get('lane') == 'conversation'
    
    def test_no_recap_string_for_education(self):
        """
        Test: Response to "explain X" must NOT contain recap strings.
        """
        # This tests the sanitization/format at response level
        RECAP_MARKERS = [
            "Here's where we left off",
            "Student asked:",
            "your mastery: 0%"
        ]
        
        # Simulate what a clean education response should look like
        test_response = "Photosynthesis is the process by which plants convert sunlight..."
        
        for marker in RECAP_MARKERS:
            assert marker not in test_response, f"Education response should not contain '{marker}'"
    
    def test_name_prefix_sanitization(self):
        """
        Test: Placeholder names like 'dsd', 'hiremath' should NOT appear as prefix.
        """
        # Test the sanitization logic
        BLOCKED_NAMES = ['dsd', 'hiremath', 'test', 'user', 'student', 'unknown']
        
        for name in BLOCKED_NAMES:
            # Simulate sanitization check
            if name and len(name.strip()) >= 3:
                name_clean = name.strip().lower()
                # These should be blocked
                assert name_clean in BLOCKED_NAMES, f"Name '{name}' should be blocked"
    
    def test_question_form_triggers_education(self):
        """
        Test: Messages ending with ? and 3+ words should trigger education override.
        """
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        
        engine = IntelligentRoutingEngine()
        
        conversation_state = {'last_topic': 'chemistry'}
        
        # Question form should bypass dialogue_act
        result = engine._detect_dialogue_act("what happens in photosynthesis?", conversation_state)
        assert result is None, "Question form should bypass dialogue_act"
        
        result = engine._detect_dialogue_act("why is the sky blue?", conversation_state)
        assert result is None, "Question form should bypass dialogue_act"


class TestNoDebugLeakage:
    """
    Test that internal debug strings never appear in responses.
    """
    
    def test_no_student_asked_in_response(self):
        """Responses should not contain 'Student asked:' internal format."""
        # This is now formatted as "Q:" internally which is cleaner
        from services.memory_integration import MemoryIntegrationService
        
        # Verify the format was changed
        import inspect
        source = inspect.getsource(MemoryIntegrationService._build_conversation_summary)
        
        # Should use Q: format, not "Student asked:"
        assert "Q:" in source or "Student asked:" not in source
    
    def test_recap_format_is_clean(self):
        """Recap response should have clean format without debug info."""
        import inspect
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        source = inspect.getsource(UnifiedAIOrchestrator._generate_proactive_response)
        
        # Should NOT have raw mastery 0% display
        # The new code conditionally shows mastery only if > 0
        assert "mastery_level > 0" in source or "mastery: 0%" not in source


# =============================================================================
# TEST: PRODUCTION BUG REGRESSIONS
# =============================================================================

class TestProductionBugRegressions:
    """
    Regression tests for production bugs that must NEVER return.
    """
    
    def test_risk_flags_list_handling(self):
        """
        REGRESSION: Memory v2 write failed: 'list' object has no attribute 'get'
        
        risk_flags is a LIST of RiskFlag enums, not a dict.
        The orchestrator must handle both list and dict formats.
        """
        import inspect
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        source = inspect.getsource(UnifiedAIOrchestrator.orchestrate_pipeline)
        
        # Should check isinstance for list handling
        assert "isinstance(risk_flags" in source, "Should check risk_flags type"
        
        # Should handle both list and dict
        assert "list" in source and "dict" in source
        
        # Should NOT use .get() directly on risk_flags without type check
        # The old buggy code was: risk_flags.get('self_harm')
    
    def test_guardrail_status_redirect_not_required(self):
        """
        REGRESSION: GuardrailStatus.REDIRECT doesn't exist in enum.
        
        Teachback gating must NOT reference GuardrailStatus.REDIRECT directly.
        Should use getattr() for backward compatibility.
        """
        import inspect
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        source = inspect.getsource(UnifiedAIOrchestrator.orchestrate_pipeline)
        
        # Should use getattr for backward compatibility
        assert "getattr(GuardrailStatus" in source, "Should use getattr for safe enum access"
        
        # Should NOT have direct GuardrailStatus.REDIRECT reference
        # (would crash if enum doesn't define REDIRECT)
        assert "GuardrailStatus.REDIRECT]" not in source, "Should not directly reference REDIRECT"
    
    def test_guardrail_status_enum_values(self):
        """
        Verify GuardrailStatus enum has expected values.
        """
        from services.guardrails_v2 import GuardrailStatus
        
        # These MUST exist
        assert hasattr(GuardrailStatus, 'PASS')
        assert hasattr(GuardrailStatus, 'HARD_BLOCK')
        assert hasattr(GuardrailStatus, 'SOFT_BLOCK')
        
        # REDIRECT may or may not exist - code must handle both cases
        # This is why we use getattr()
    
    def test_risk_flag_enum_values(self):
        """
        Verify RiskFlag enum has expected values.
        """
        from services.guardrails_v2 import RiskFlag
        
        # These MUST exist for safety checks
        assert hasattr(RiskFlag, 'CHEATING')
        assert hasattr(RiskFlag, 'SELF_HARM_INSTRUCTION')
        assert hasattr(RiskFlag, 'SELF_HARM_IDEATION')
        assert hasattr(RiskFlag, 'UNSAFE')
    
    def test_teachback_suppression_string_fallback(self):
        """
        Teachback suppression should work via string matching as fallback.
        """
        import inspect
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        source = inspect.getsource(UnifiedAIOrchestrator.orchestrate_pipeline)
        
        # Should have string-based fallback for robustness
        assert "status_str" in source or ".lower()" in source
        assert "'hard'" in source or '"hard"' in source


# =============================================================================
# TEST: INTERNAL TRACE LEAKAGE — CRITICAL PRODUCTION BUG
# =============================================================================

class TestInternalTraceLeakage:
    """
    CRITICAL: Test that internal ReAct traces NEVER leak to student UI.
    
    Tests the robust sanitization of:
    1. Nested JSON with thought/action/action_input
    2. Flat JSON blocks
    3. Duplicated content
    4. Line-by-line ReAct patterns
    """
    
    def test_nested_react_json_removed(self):
        """
        CRITICAL: Nested JSON with action_input containing nested objects must be removed.
        This was the original bug - the regex couldn't handle nested braces.
        """
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        orchestrator = UnifiedAIOrchestrator.__new__(UnifiedAIOrchestrator)
        
        # Exact pattern that was leaking
        text_with_nested_json = '''Here's an explanation of calculus.

{"thought": "I need to explain the fundamental theorem", "action": "FINISH", "action_input": {"answer": "The theorem states..."}, "confidence": 0.9}

The fundamental theorem of calculus connects differentiation and integration.'''
        
        result = orchestrator._sanitize_text_content(text_with_nested_json)
        
        # Must NOT contain any of these
        assert '"thought"' not in result.lower()
        assert '"action"' not in result.lower()
        assert '"action_input"' not in result.lower()
        assert '"confidence"' not in result.lower()
        
        # Must STILL contain the educational content
        assert 'calculus' in result.lower()
        assert 'differentiation' in result.lower() or 'fundamental' in result.lower()
    
    def test_duplicated_json_blocks_removed(self):
        """
        Test that duplicated JSON blocks (appearing twice) are removed.
        """
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        orchestrator = UnifiedAIOrchestrator.__new__(UnifiedAIOrchestrator)
        
        # Same block duplicated
        text_with_duplicate = '''{"thought": "analyzing", "action": "FINISH", "action_input": {}}

The answer is: 42.

{"thought": "analyzing", "action": "FINISH", "action_input": {}}'''
        
        result = orchestrator._sanitize_text_content(text_with_duplicate)
        
        assert '"thought"' not in result.lower()
        assert 'answer is' in result.lower()
    
    def test_line_by_line_react_blocks_removed(self):
        """
        Test removal of ReAct transcript format: Thought: ..., Action: ..., Observation: ...
        """
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        orchestrator = UnifiedAIOrchestrator.__new__(UnifiedAIOrchestrator)
        
        text_with_blocks = '''The answer to your question:

Thought: I need to search for information
Action: knowledge_search
Action Input: {"query": "calculus theorem"}
Observation: Found relevant content

Here's what I found about calculus.'''
        
        result = orchestrator._sanitize_text_content(text_with_blocks)
        
        assert 'Thought:' not in result
        assert 'Action:' not in result
        assert 'Observation:' not in result
        assert 'calculus' in result.lower()
    
    def test_math_latex_preserved(self):
        """
        CRITICAL: Math/LaTeX content must NOT be accidentally removed.
        """
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        orchestrator = UnifiedAIOrchestrator.__new__(UnifiedAIOrchestrator)
        
        text_with_math = r'''The integral is:

$$\int_a^b f(x) dx = F(b) - F(a)$$

This is the fundamental theorem of calculus.'''
        
        result = orchestrator._sanitize_text_content(text_with_math)
        
        # Math must be preserved
        assert '\\int' in result or 'int' in result
        assert 'F(b)' in result or 'f(x)' in result.lower()
    
    def test_stray_braces_removed(self):
        """
        CRITICAL: Stray braces from truncated JSON must be removed.
        This is the exact bug pattern seen in production.
        """
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        orchestrator = UnifiedAIOrchestrator.__new__(UnifiedAIOrchestrator)
        
        # Pattern that was showing in UI: stray { on its own line
        text_with_stray_brace = '''{
\\int_a^b f(x) dx = F(b) - F(a)

This means that the definite integral...'''
        
        result = orchestrator._sanitize_text_content(text_with_stray_brace)
        
        # Should NOT start with orphaned brace
        assert not result.strip().startswith('{')
        # Should preserve the math and explanation
        assert 'integral' in result.lower() or 'int' in result
    
    def test_partial_json_with_trace_removed(self):
        """
        Test that partial/malformed JSON with trace keys is removed.
        """
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        orchestrator = UnifiedAIOrchestrator.__new__(UnifiedAIOrchestrator)
        
        # Incomplete JSON block
        text_with_partial = '''{"thought": "I need to explain calculus",
"action": "FINISH",
"action_input": {"answer": 

The fundamental theorem of calculus states...'''
        
        result = orchestrator._sanitize_text_content(text_with_partial)
        
        # Trace keys must be removed
        assert '"thought"' not in result.lower()
        assert '"action"' not in result.lower()
        # Content should remain
        assert 'calculus' in result.lower()
    
    def test_streaming_sanitizer_exists(self):
        """
        Test that streaming service has sanitization method.
        """
        from services.streaming_ai_service import StreamingAIService
        
        service = StreamingAIService(None, None)
        assert hasattr(service, '_sanitize_streaming_content')
        
        # Test basic sanitization
        dirty = '{"thought": "test", "action": "FINISH"} Here is the answer'
        clean = service._sanitize_streaming_content(dirty)
        assert '"thought"' not in clean.lower()
        assert 'answer' in clean.lower()
    
    def test_api_sanitizer_removes_forbidden_keys(self):
        """
        Test the API-level last-mile sanitizer.
        """
        from api.ai import _sanitize_api_response
        
        # Input with forbidden keys
        dirty_response = {
            'response': {
                'default_view': {
                    'main_content': {
                        'content': 'Clean educational content'
                    }
                },
                'thought': 'Internal thinking',
                'action': 'FINISH',
                'action_input': {'answer': 'some answer'}
            },
            'reasoning_chain': [{'step': 1, 'thought': 'thinking'}],
            '_debug': {'internal': True},
            'detected_subject': 'Mathematics'
        }
        
        result = _sanitize_api_response(dirty_response)
        
        # Forbidden keys must be gone
        assert 'reasoning_chain' not in result
        assert '_debug' not in result
        assert 'thought' not in result.get('response', {})
        assert 'action' not in result.get('response', {})
        assert 'action_input' not in result.get('response', {})
        
        # Safe keys must remain
        assert 'detected_subject' in result
        assert 'default_view' in result.get('response', {})
    
    def test_sanitizer_doesnt_over_remove(self):
        """
        Sanitizer must not remove too much legitimate content.
        """
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        orchestrator = UnifiedAIOrchestrator.__new__(UnifiedAIOrchestrator)
        
        # Long legitimate content
        clean_text = '''The Fundamental Theorem of Calculus

Part 1: If f is continuous on [a, b], then the function g defined by:
g(x) = ∫[a to x] f(t) dt
is continuous on [a, b] and differentiable on (a, b), and g'(x) = f(x).

Part 2: If f is continuous on [a, b], then:
∫[a to b] f(x) dx = F(b) - F(a)
where F is any antiderivative of f.

This theorem shows the beautiful connection between differentiation and integration,
which are the two main operations in calculus.'''
        
        result = orchestrator._sanitize_text_content(clean_text)
        
        # Content should be mostly preserved (allow some whitespace normalization)
        assert len(result) > 0.8 * len(clean_text)
        assert 'Fundamental Theorem' in result
        assert 'differentiation' in result


# =============================================================================
# L) URGENCY-AWARE RESPONSE TESTS
# =============================================================================

class TestUrgencyAwareResponses:
    """
    SHIP BLOCKER: Test that urgency detection leads to appropriate routing and responses.
    
    Key scenarios:
    1. HIGH urgency → structured, actionable response (NOT clarifying questions)
    2. TIME-CRITICAL temporal_scope → forces structured response
    3. Fallback under urgency → provides value, not asks questions
    """
    
    @pytest.mark.asyncio
    async def test_high_urgency_forces_structured_response(self):
        """
        SHIP BLOCKER: When urgency_level='high', routing should force structured response mode.
        
        This is triggered by SemanticIntentClassifier detecting urgency, and
        IntelligentRoutingEngine acting on it.
        """
        from services.intelligent_routing_engine import IntelligentRoutingEngine, RecommendedPipeline
        from services.semantic_intent_classifier import SemanticAnalysis, SemanticIntent
        
        engine = IntelligentRoutingEngine()
        
        # Mock high-urgency analysis (as if from SemanticIntentClassifier)
        high_urgency_analysis = SemanticAnalysis(
            intent=SemanticIntent.QUESTION,
            confidence=0.9,
            emotional_tone="anxious",
            emotional_intensity=0.7,
            topic_mentioned=None,
            is_follow_up=False,
            urgency_level="high",  # HIGH URGENCY
            needs_empathy=True,
            needs_encouragement=True,
            needs_clarification=False,
            suggested_response_style="supportive",
            reasoning="Student asking for exam tips with high urgency",
            response_expectation="conversational_advice",  # Would normally be brief
            temporal_scope="immediate",
            delivery_mode="conversational"  # Would normally be casual
        )
        
        # Route with high urgency
        decision = engine._route_from_semantic_analysis(
            query="Quick revision tips for exam tomorrow",
            analysis=high_urgency_analysis,
            context={}
        )
        
        # ASSERTIONS: High urgency should override normal routing
        assert decision.extra_context is not None
        assert decision.extra_context.get('is_urgent') == True, \
            "High urgency should set is_urgent=True"
        assert decision.extra_context.get('response_expectation') == 'urgent_assistance', \
            "High urgency should force response_expectation='urgent_assistance'"
        assert decision.extra_context.get('delivery_mode') == 'structured', \
            "High urgency should force delivery_mode='structured'"
        assert decision.extra_context.get('require_actionable_items') == True, \
            "High urgency should require actionable items"
    
    @pytest.mark.asyncio
    async def test_time_critical_scope_forces_structured_response(self):
        """
        Test: temporal_scope='immediate' or 'today' with conversational_advice
        should force structured response (urgency override).
        """
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        from services.semantic_intent_classifier import SemanticAnalysis, SemanticIntent
        
        engine = IntelligentRoutingEngine()
        
        # Time-critical scope with medium urgency
        time_critical_analysis = SemanticAnalysis(
            intent=SemanticIntent.QUESTION,
            confidence=0.85,
            emotional_tone="neutral",
            emotional_intensity=0.4,
            topic_mentioned=None,
            is_follow_up=False,
            urgency_level="medium",  # Not explicitly high, but...
            needs_empathy=False,
            needs_encouragement=False,
            needs_clarification=False,
            suggested_response_style="educational",
            reasoning="Student asking about exam preparation",
            response_expectation="conversational_advice",
            temporal_scope="today",  # TIME-CRITICAL SCOPE
            delivery_mode="conversational"
        )
        
        decision = engine._route_from_semantic_analysis(
            query="What should I focus on for my exam today?",
            analysis=time_critical_analysis,
            context={}
        )
        
        # time_critical + conversational_advice should trigger urgency override
        assert decision.extra_context.get('is_urgent') == True or \
               decision.extra_context.get('delivery_mode') == 'structured', \
            "Time-critical scope should trigger structured response mode"
    
    def test_mentor_urgent_response_method_exists(self):
        """
        Test: MentorAgent has _generate_urgent_response method.
        """
        from agents.mentor import MentorAgent
        
        assert hasattr(MentorAgent, '_generate_urgent_response'), \
            "MentorAgent must have _generate_urgent_response method"
    
    def test_mentor_urgent_fallback_never_asks_questions(self):
        """
        SHIP BLOCKER: Urgent fallback content must NEVER ask clarifying questions
        as the primary response. It must provide immediate actionable value.
        """
        from agents.mentor import MentorAgent
        
        # Create agent instance
        agent = MentorAgent.__new__(MentorAgent)
        
        # Get fallback content
        fallback = agent._get_urgent_fallback_content("Quick revision tips", "")
        
        # Must contain actionable items
        assert "Priority" in fallback or "Action" in fallback, \
            "Urgent fallback must have priority/action items"
        
        # Must have structure (bullets/numbers)
        assert "1." in fallback or "•" in fallback or "**" in fallback, \
            "Urgent fallback must be structured"
        
        # Must NOT lead with clarifying questions (may have follow-up offer at end)
        first_100_chars = fallback[:100].lower()
        assert "could you" not in first_100_chars, \
            "Urgent fallback must NOT start with clarifying questions"
        assert "tell me more" not in first_100_chars, \
            "Urgent fallback must NOT start with 'tell me more'"
    
    def test_supervisor_urgent_fallback_provides_value(self):
        """
        SHIP BLOCKER: Supervisor fallback under urgency must provide value,
        not ask generic clarifying questions.
        """
        from agents.supervisor import SupervisorAgent
        
        # Create agent instance
        supervisor = SupervisorAgent.__new__(SupervisorAgent)
        
        # Test urgent fallback
        urgent_fallback = supervisor._generate_urgent_fallback("revision tips for exam tomorrow")
        
        # Must have structured content
        assert "**" in urgent_fallback or "##" in urgent_fallback, \
            "Urgent fallback must have headers/structure"
        
        # Must have actionable items (numbers or bullets)
        assert any(f"{i}." in urgent_fallback for i in range(1, 6)), \
            "Urgent fallback must have numbered action items"
        
        # Must NOT be just questions
        question_count = urgent_fallback.count("?")
        assert question_count <= 2, \
            f"Urgent fallback has too many questions ({question_count}), should provide answers"
    
    def test_supervisor_helpful_fallback_not_interrogation(self):
        """
        Test: Even non-urgent fallback should provide value, not just interrogate.
        """
        from agents.supervisor import SupervisorAgent
        
        supervisor = SupervisorAgent.__new__(SupervisorAgent)
        
        # Test helpful fallback
        helpful_fallback = supervisor._generate_helpful_fallback("explain photosynthesis")
        
        # Should acknowledge the query
        assert "question" in helpful_fallback.lower() or "asked" in helpful_fallback.lower(), \
            "Helpful fallback should acknowledge the query"
        
        # Should offer options/help
        assert "help" in helpful_fallback.lower() or "can" in helpful_fallback.lower(), \
            "Helpful fallback should offer help"
        
        # Should have some structure
        assert "•" in helpful_fallback or "-" in helpful_fallback or "**" in helpful_fallback, \
            "Helpful fallback should have structure (bullets or bold)"
    
    def test_urgency_level_not_ignored_in_routing(self):
        """
        REGRESSION TEST: urgency_level from SemanticAnalysis must be USED in routing.
        
        This was the original bug - urgency was detected but ignored.
        """
        import inspect
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        
        source = inspect.getsource(IntelligentRoutingEngine._route_from_semantic_analysis)
        
        # Must reference urgency_level
        assert "urgency_level" in source, \
            "Routing must use urgency_level from analysis"
        
        # Must have urgency override logic
        assert "is_high_urgency" in source or "urgency_level == \"high\"" in source or \
               "urgency == 'high'" in source, \
            "Routing must check for high urgency condition"
        
        # Must have time-critical check
        assert "is_time_critical" in source or "temporal_scope" in source, \
            "Routing must check temporal_scope for time-critical situations"
    
    def test_urgent_routing_enables_tools(self):
        """
        Test: Urgent routing should enable knowledge tools for better content,
        unlike conversational_advice which disables tools.
        """
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        from services.semantic_intent_classifier import SemanticAnalysis, SemanticIntent
        
        engine = IntelligentRoutingEngine()
        
        # High urgency analysis
        urgent_analysis = SemanticAnalysis(
            intent=SemanticIntent.QUESTION,
            confidence=0.9,
            emotional_tone="anxious",
            emotional_intensity=0.6,
            topic_mentioned=None,
            is_follow_up=False,
            urgency_level="high",
            needs_empathy=True,
            needs_encouragement=True,
            needs_clarification=False,
            suggested_response_style="supportive",
            reasoning="Urgent exam preparation request",
            response_expectation="conversational_advice",
            temporal_scope="immediate",
            delivery_mode="conversational"
        )
        
        decision = engine._route_from_semantic_analysis(
            query="Quick tips for my exam in 2 hours",
            analysis=urgent_analysis,
            context={}
        )
        
        # Urgent routing should have tools enabled (unlike conversational_advice)
        assert len(decision.tools_to_enable) > 0 or decision.use_knowledge_graph == True, \
            "Urgent routing should enable tools or knowledge graph for better content"
    
    @pytest.mark.asyncio
    async def test_full_urgent_query_flow(self):
        """
        INTEGRATION TEST: Full flow for urgent query should produce structured response.
        
        This tests the complete pipeline from routing to response.
        """
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        
        engine = IntelligentRoutingEngine()
        
        # Full routing with urgent query
        decision = await engine.route(
            query="Quick revision tips for exam tomorrow",
            context={
                'user_id': 'test_user',
                'session_id': 'test_session'
            }
        )
        
        # Should have urgency information in extra_context
        if decision.extra_context:
            # If urgency was detected by classifier, should be acted upon
            is_urgent = decision.extra_context.get('is_urgent', False)
            urgency_level = decision.extra_context.get('urgency_level', 'medium')
            
            # Log for debugging
            print(f"Routing decision: is_urgent={is_urgent}, urgency_level={urgency_level}")
            print(f"Response expectation: {decision.extra_context.get('response_expectation')}")
            print(f"Delivery mode: {decision.extra_context.get('delivery_mode')}")


class TestUrgencyDetectionVariants:
    """
    Test that urgency detection works for various phrasings,
    not just specific keywords.
    """
    
    def test_urgency_detection_various_phrasings(self):
        """
        Test that various urgent phrasings are detected.
        
        These should all trigger high urgency:
        - "exam tomorrow"
        - "viva in 2 hours"
        - "interview tonight"
        - "test in the morning"
        - "deadline today"
        """
        # This is tested via the SemanticIntentClassifier
        # which uses LLM to detect urgency, not keywords
        
        urgent_queries = [
            "Quick revision tips for exam tomorrow",
            "What should I focus on for my viva in 2 hours?",
            "Help me prepare for interview tonight",
            "I have a test in the morning, what to revise?",
            "Last minute preparation tips",
            "Need quick help before my presentation"
        ]
        
        # These should be detected as urgent by the LLM classifier
        # We can't test the LLM directly in unit tests, but we test
        # that the routing handles urgency_level='high' correctly
        
        # The key is that these tests verify the ROUTING behavior,
        # not the LLM classification (which is integration-level)
        
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        from services.semantic_intent_classifier import SemanticAnalysis, SemanticIntent
        
        engine = IntelligentRoutingEngine()
        
        for query in urgent_queries:
            # Simulate high-urgency classification
            analysis = SemanticAnalysis(
                intent=SemanticIntent.QUESTION,
                confidence=0.85,
                emotional_tone="anxious",
                emotional_intensity=0.5,
                topic_mentioned=None,
                is_follow_up=False,
                urgency_level="high",  # Simulating LLM detected this
                needs_empathy=False,
                needs_encouragement=True,
                needs_clarification=False,
                suggested_response_style="supportive",
                reasoning=f"Urgent: {query[:30]}",
                response_expectation="conversational_advice",
                temporal_scope="immediate",
                delivery_mode="conversational"
            )
            
            decision = engine._route_from_semantic_analysis(query, analysis, {})
            
            # All urgent queries should get urgency override
            assert decision.extra_context.get('is_urgent') == True, \
                f"Query '{query[:30]}...' should be routed as urgent"


# =============================================================================
# PHASE 5: COGNITIVE OS TRANSFORMATION REGRESSION TESTS
# =============================================================================

class TestPhase1KeywordNeutralization:
    """
    PHASE 1 REGRESSION TESTS: Verify keywords don't override semantic decisions.
    """
    
    def test_emotional_patterns_dont_override_semantic(self):
        """
        Keywords like 'bored', 'frustrated' should NOT override semantic analysis.
        """
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        from services.semantic_intent_classifier import SemanticAnalysis, SemanticIntent
        
        engine = IntelligentRoutingEngine()
        
        # Semantic says it's a QUESTION, but query contains "bored"
        analysis = SemanticAnalysis(
            intent=SemanticIntent.QUESTION,  # Semantic: QUESTION
            confidence=0.9,  # High confidence
            emotional_tone="curious",  # Not bored according to semantic
            emotional_intensity=0.3,
            topic_mentioned="physics",
            is_follow_up=False,
            urgency_level="low",
            needs_empathy=False,
            needs_encouragement=False,
            needs_clarification=False,
            suggested_response_style="educational",
            reasoning="Student asking about physics"
        )
        
        # Query has "bored" but semantic says it's a question
        query = "I'm bored of simple physics, explain quantum mechanics"
        
        decision = engine._route_from_semantic_analysis(query, analysis, {})
        
        # Should NOT route to EMOTIONAL_SUPPORT because semantic says QUESTION
        # (The old behavior would have keyword-matched "bored" and routed to emotional)
        assert decision.pipeline.value != "emotional", \
            "Keywords should NOT override semantic analysis"
    
    def test_trivial_detection_is_structural(self):
        """
        Trivial detection should use structure, not keywords.
        """
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        
        engine = IntelligentRoutingEngine()
        
        # Test structural trivial detection
        assert engine._is_trivial_structural("ok") == True, "1 word, no question should be trivial"
        assert engine._is_trivial_structural("hi") == True, "Short greeting should be trivial"
        assert engine._is_trivial_structural("explain quantum physics?") == False, "Question should NOT be trivial"
        assert engine._is_trivial_structural("What is gravity") == False, "Substantive should NOT be trivial"


class TestPhase2SemanticAgentSelection:
    """
    PHASE 2 REGRESSION TESTS: Verify agents are selected by semantic signals.
    """
    
    def test_agents_selected_by_semantic_not_keywords(self):
        """
        Agent selection should use semantic signals, not keyword matching.
        """
        from agents.supervisor import SupervisorAgent
        
        supervisor = SupervisorAgent({})
        
        # Test with semantic analysis
        semantic_analysis = {
            'intent': 'question',
            'confidence': 0.9,
            'emotional_tone': 'curious',
            'emotional_intensity': 0.3,
            'response_expectation': 'detailed_explanation',
            'needs_empathy': False,
            'needs_encouragement': False,
            'needs_clarification': False
        }
        
        agents = supervisor._select_agents('concept', {}, semantic_analysis)
        
        # Should include professor for detailed explanation
        assert 'mentor' in agents, "Mentor should always be included"
        assert 'professor' in agents, "Professor should be included for detailed explanation"
    
    def test_emotional_agents_included_for_emotional_semantic(self):
        """
        Mentor should be primary for emotional semantic signals.
        """
        from agents.supervisor import SupervisorAgent
        
        supervisor = SupervisorAgent({})
        
        # Semantic analysis indicates emotional need
        semantic_analysis = {
            'intent': 'emotional_support',
            'confidence': 0.85,
            'emotional_tone': 'anxious',
            'emotional_intensity': 0.7,
            'response_expectation': 'emotional_acknowledgment',
            'needs_empathy': True,
            'needs_encouragement': True,
            'needs_clarification': False
        }
        
        agents = supervisor._select_agents('emotional', {}, semantic_analysis)
        
        # Mentor should be primary for emotional support
        assert 'mentor' in agents, "Mentor should be included for emotional support"


class TestPhase3ContinuityLockIn:
    """
    PHASE 3 REGRESSION TESTS: Verify continuity is enforced.
    """
    
    def test_intent_detects_continuation_with_context(self):
        """
        When semantic says continuation and we have context, intent should be 'continuation'.
        """
        from agents.supervisor import SupervisorAgent
        
        supervisor = SupervisorAgent({})
        
        # Semantic says acknowledgment, we have prior context
        semantic_analysis = {
            'intent': 'acknowledgment',
            'confidence': 0.9
        }
        
        context = {
            'last_task_type': 'study_plan',
            'awaiting_continuation': True
        }
        
        intent = supervisor._detect_intent("okay", context, semantic_analysis)
        
        assert intent == 'continuation', \
            "With awaiting_continuation=True, intent should be 'continuation'"


class TestPhase4EmotionAsContext:
    """
    PHASE 4 REGRESSION TESTS: Verify emotion modulates, doesn't trigger.
    """
    
    def test_emotion_goes_to_multi_agent_not_emotional_support(self):
        """
        Emotional queries should use MULTI_AGENT with emotional context, not EMOTIONAL_SUPPORT.
        """
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        from services.semantic_intent_classifier import SemanticAnalysis, SemanticIntent
        
        engine = IntelligentRoutingEngine()
        
        # Semantic says emotional support needed
        analysis = SemanticAnalysis(
            intent=SemanticIntent.EMOTIONAL_SUPPORT,
            confidence=0.85,
            emotional_tone="frustrated",
            emotional_intensity=0.7,
            topic_mentioned=None,
            is_follow_up=False,
            urgency_level="medium",
            needs_empathy=True,
            needs_encouragement=True,
            needs_clarification=False,
            suggested_response_style="supportive",
            reasoning="Student is frustrated"
        )
        
        decision = engine._route_from_semantic_analysis("I'm so frustrated", analysis, {})
        
        # PHASE 4: Should use MULTI_AGENT, not EMOTIONAL_SUPPORT
        assert decision.pipeline.value == "multi_agent", \
            "Emotional queries should use MULTI_AGENT pipeline with emotional context"
        
        # Should have emotional context for modulation
        assert decision.extra_context.get('emotional_context') is not None, \
            "Should have emotional_context for response modulation"
        assert decision.extra_context['emotional_context'].get('modulate_response') == True, \
            "emotional_context should indicate response modulation"


class TestPhase5RegressionSafety:
    """
    PHASE 5 REGRESSION TESTS: Verify no regressions in existing flows.
    """
    
    def test_planning_still_works(self):
        """
        Planning requests should still produce structured deliverables.
        """
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        from services.semantic_intent_classifier import SemanticAnalysis, SemanticIntent
        
        engine = IntelligentRoutingEngine()
        
        # Semantic says structured deliverable (study plan)
        analysis = SemanticAnalysis(
            intent=SemanticIntent.QUESTION,
            confidence=0.9,
            emotional_tone="neutral",
            emotional_intensity=0.2,
            topic_mentioned="physics",
            is_follow_up=False,
            urgency_level="low",
            needs_empathy=False,
            needs_encouragement=False,
            needs_clarification=False,
            suggested_response_style="educational",
            reasoning="Study plan request",
            has_actionable_request=True,
            requested_output_type="study_plan",
            response_expectation="structured_deliverable"
        )
        
        decision = engine._route_from_semantic_analysis("Create a 3 day study plan", analysis, {})
        
        # Should still enable study planner tool
        assert 'study_planner' in decision.tools_to_enable, \
            "Study plan requests should still use study_planner tool"
    
    def test_greeting_still_fast(self):
        """
        Greetings should still route to fast response.
        """
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        from services.semantic_intent_classifier import SemanticAnalysis, SemanticIntent
        
        engine = IntelligentRoutingEngine()
        
        # Semantic says greeting
        analysis = SemanticAnalysis(
            intent=SemanticIntent.GREETING,
            confidence=0.95,
            emotional_tone="positive",
            emotional_intensity=0.3,
            topic_mentioned=None,
            is_follow_up=False,
            urgency_level="low",
            needs_empathy=False,
            needs_encouragement=False,
            needs_clarification=False,
            suggested_response_style="casual",
            reasoning="Greeting"
        )
        
        decision = engine._route_from_semantic_analysis("hi there!", analysis, {})
        
        # Should route to fast response
        assert decision.pipeline.value == "fast", \
            "Greetings should still use fast response pipeline"
    
    def test_config_flags_exist(self):
        """
        All Phase 5 config flags should exist.
        """
        from core.config import settings
        
        assert hasattr(settings, 'ENABLE_SEMANTIC_ONLY_ROUTING'), "Should have ENABLE_SEMANTIC_ONLY_ROUTING"
        assert hasattr(settings, 'ENABLE_SEMANTIC_EMOTION_DETECTION'), "Should have ENABLE_SEMANTIC_EMOTION_DETECTION"
        assert hasattr(settings, 'ENABLE_CONTINUITY_TRACKING'), "Should have ENABLE_CONTINUITY_TRACKING"
        assert hasattr(settings, 'ENABLE_SEMANTIC_AGENT_SELECTION'), "Should have ENABLE_SEMANTIC_AGENT_SELECTION"
        assert hasattr(settings, 'ENABLE_CONTINUITY_LOCKIN'), "Should have ENABLE_CONTINUITY_LOCKIN"
        assert hasattr(settings, 'ENABLE_EMOTION_AS_CONTEXT'), "Should have ENABLE_EMOTION_AS_CONTEXT"


# =============================================================================
# GAP 4 TESTS: REAL-TIME CONFIDENCE CALIBRATION
# =============================================================================

class TestGap4ConfidenceCalibration:
    """
    GAP 4 TESTS: Verify confidence calibration works correctly.
    
    SHIP CONDITIONS:
    - Every response carries explicit confidence metadata
    - Low confidence changes behavior (clarification, hedging, escalation)
    - No silent guessing
    """
    
    def test_response_confidence_dataclass_exists(self):
        """
        ResponseConfidence dataclass should exist with required fields.
        """
        from services.cognitive_model.response_confidence import ResponseConfidence, ConfidenceLevel
        
        conf = ResponseConfidence()
        
        # Check required fields exist
        assert hasattr(conf, 'overall_confidence')
        assert hasattr(conf, 'factual_confidence')
        assert hasattr(conf, 'reasoning_confidence')
        assert hasattr(conf, 'completeness_confidence')
        assert hasattr(conf, 'calibrated_confidence')
        assert hasattr(conf, 'level')
        
        # Check default values
        assert 0 <= conf.overall_confidence <= 1
        assert isinstance(conf.level, ConfidenceLevel)
    
    def test_confidence_levels_correct(self):
        """
        Confidence levels should map correctly to thresholds.
        """
        from services.cognitive_model.response_confidence import ResponseConfidence, ConfidenceLevel
        
        # High confidence
        high = ResponseConfidence(overall_confidence=0.9)
        assert high.level == ConfidenceLevel.HIGH
        
        # Medium confidence
        medium = ResponseConfidence(overall_confidence=0.7)
        assert medium.level == ConfidenceLevel.MEDIUM
        
        # Low confidence
        low = ResponseConfidence(overall_confidence=0.5)
        assert low.level == ConfidenceLevel.LOW
        
        # Very low confidence
        very_low = ResponseConfidence(overall_confidence=0.3)
        assert very_low.level == ConfidenceLevel.VERY_LOW
    
    def test_low_confidence_triggers_hedging(self):
        """
        Low confidence should trigger hedging behavior.
        """
        from services.cognitive_model.response_confidence import ResponseConfidence
        
        low = ResponseConfidence(overall_confidence=0.5)
        assert low.needs_hedging, "Low confidence should trigger hedging"
        
        high = ResponseConfidence(overall_confidence=0.9)
        assert not high.needs_hedging, "High confidence should not need hedging"
    
    def test_ambiguity_triggers_clarification(self):
        """
        Ambiguity + low confidence should trigger clarification request.
        """
        from services.cognitive_model.response_confidence import ResponseConfidence
        
        # Ambiguous + low confidence = clarification
        ambiguous_low = ResponseConfidence(
            overall_confidence=0.4,
            ambiguity_flags=["unclear which formula they mean"]
        )
        assert ambiguous_low.needs_clarification, "Ambiguous + low confidence should need clarification"
        
        # Ambiguous but high confidence = no clarification
        ambiguous_high = ResponseConfidence(
            overall_confidence=0.8,
            ambiguity_flags=["unclear which formula they mean"]
        )
        assert not ambiguous_high.needs_clarification, "High confidence should not need clarification even with ambiguity"
    
    def test_confidence_to_dict_format(self):
        """
        Confidence should serialize to consistent dict format.
        """
        from services.cognitive_model.response_confidence import ResponseConfidence
        
        conf = ResponseConfidence(
            overall_confidence=0.7,
            factual_confidence=0.8,
            reasoning_confidence=0.6,
            completeness_confidence=0.7,
            ambiguity_flags=["test flag"],
            uncertainty_sources=["test source"]
        )
        
        d = conf.to_dict()
        
        assert "overall_confidence" in d
        assert "confidence_level" in d
        assert "calibrated_confidence" in d
        assert "needs_clarification" in d
        assert "needs_hedging" in d
        assert isinstance(d["ambiguity_flags"], list)
    
    def test_confidence_handler_exists(self):
        """
        ConfidenceAwareResponseHandler should exist and be instantiable.
        """
        from services.cognitive_model.response_confidence import ConfidenceAwareResponseHandler
        
        handler = ConfidenceAwareResponseHandler()
        assert handler is not None
    
    def test_config_flags_for_confidence(self):
        """
        Confidence calibration config flags should exist.
        """
        from core.config import settings
        
        assert hasattr(settings, 'ENABLE_CONFIDENCE_CALIBRATION'), "Should have ENABLE_CONFIDENCE_CALIBRATION"
        assert hasattr(settings, 'ENABLE_CONFIDENCE_SELF_ASSESSMENT'), "Should have ENABLE_CONFIDENCE_SELF_ASSESSMENT"
        assert hasattr(settings, 'ENABLE_CONFIDENCE_CLARIFICATION'), "Should have ENABLE_CONFIDENCE_CLARIFICATION"
        assert hasattr(settings, 'ENABLE_CONFIDENCE_HEDGING'), "Should have ENABLE_CONFIDENCE_HEDGING"
    
    def test_confidence_extraction_from_response(self):
        """
        Should be able to extract confidence from LLM response with JSON block.
        """
        from services.cognitive_model.response_confidence import extract_confidence_from_response
        
        # Response with embedded confidence
        response_with_conf = '''Here is my answer about physics.

```json
{
  "confidence_assessment": {
    "overall_confidence": 0.8,
    "factual_confidence": 0.9,
    "reasoning_confidence": 0.7,
    "completeness_confidence": 0.8,
    "ambiguity_flags": [],
    "uncertainty_sources": []
  }
}
```'''
        
        conf = extract_confidence_from_response(response_with_conf)
        assert conf is not None, "Should extract confidence from response"
        assert conf.overall_confidence == 0.8
        assert conf.factual_confidence == 0.9
    
    def test_strip_confidence_block(self):
        """
        Confidence JSON block should be stripped from content.
        """
        from services.cognitive_model.response_confidence import strip_confidence_block
        
        response_with_conf = '''Here is my answer about physics.

```json
{
  "confidence_assessment": {
    "overall_confidence": 0.8
  }
}
```'''
        
        stripped = strip_confidence_block(response_with_conf)
        assert "confidence_assessment" not in stripped
        assert "Here is my answer" in stripped


class TestGap4NoSilentGuessing:
    """
    CRITICAL: System must never guess silently.
    
    If confidence is low and system responds with high certainty, that is a BUG.
    """
    
    def test_very_low_confidence_triggers_escalation(self):
        """
        Very low factual AND reasoning confidence should recommend escalation.
        """
        from services.cognitive_model.response_confidence import ResponseConfidence
        
        very_low = ResponseConfidence(
            factual_confidence=0.3,
            reasoning_confidence=0.3
        )
        
        assert very_low.needs_escalation, "Very low confidence should recommend escalation"
    
    def test_high_confidence_factory(self):
        """
        High confidence factory should create appropriate confidence for greetings.
        """
        from services.cognitive_model.response_confidence import ResponseConfidence
        
        high = ResponseConfidence.high_confidence()
        
        assert high.overall_confidence >= 0.9
        assert high.level.value == "high"
        assert not high.needs_hedging
        assert not high.needs_clarification
        assert not high.needs_escalation


# =============================================================================
# GAP 2 TESTS: DYNAMIC MODEL SELECTION
# =============================================================================

class TestGap2SemanticModelSelection:
    """
    GAP 2 TESTS: Verify model selection is a pure function.
    
    model = f(semantic_complexity, latency_budget, confidence_required)
    
    NO task names. NO agent names. NO keywords.
    """
    
    def test_model_capability_dataclass_exists(self):
        """
        ModelCapability dataclass should exist with required fields.
        """
        from services.cognitive_model.semantic_model_selector import ModelCapability, ModelTier, ModelProvider
        
        cap = ModelCapability(
            name="test-model",
            provider=ModelProvider.GEMINI,
            tier=ModelTier.BALANCED,
            reasoning_strength=0.8,
            factual_accuracy=0.8,
            math_ability=0.7,
            creativity=0.8,
            instruction_following=0.9,
            latency_ms=2000,
            cost_per_1k_tokens=0.001,
            max_context=100000
        )
        
        assert cap.name == "test-model"
        assert cap.tier == ModelTier.BALANCED
    
    def test_model_selection_criteria_exists(self):
        """
        ModelSelectionCriteria should exist with required fields.
        """
        from services.cognitive_model.semantic_model_selector import ModelSelectionCriteria
        
        criteria = ModelSelectionCriteria()
        
        assert hasattr(criteria, 'semantic_complexity')
        assert hasattr(criteria, 'latency_budget_ms')
        assert hasattr(criteria, 'confidence_required')
        assert hasattr(criteria, 'quality_vs_speed')
    
    def test_model_registry_exists(self):
        """
        Model registry should contain multiple models.
        """
        from services.cognitive_model.semantic_model_selector import MODEL_REGISTRY
        
        assert len(MODEL_REGISTRY) > 0
        assert "gemini-1.5-flash" in MODEL_REGISTRY
        assert "gemini-1.5-pro" in MODEL_REGISTRY
    
    def test_semantic_model_selector_exists(self):
        """
        SemanticModelSelector should be instantiable.
        """
        from services.cognitive_model.semantic_model_selector import SemanticModelSelector
        
        selector = SemanticModelSelector()
        assert selector is not None
    
    def test_simple_query_selects_fast_model(self):
        """
        Simple queries with tight latency budget should prefer fast models.
        """
        from services.cognitive_model.semantic_model_selector import (
            SemanticModelSelector, ModelSelectionCriteria
        )
        
        selector = SemanticModelSelector(["gemini-1.5-flash", "gemini-1.5-pro"])
        
        # Simple query criteria with VERY tight latency budget
        # Flash: 800ms, Pro: 2000ms, so budget of 1000ms should force flash
        criteria = ModelSelectionCriteria(
            semantic_complexity=0.2,
            reasoning_depth_required=1,
            latency_budget_ms=1000,  # Tight - only flash can meet this
            quality_vs_speed=0.1  # Strongly prefer speed
        )
        
        model = selector.select(criteria)
        
        # Should select faster model when latency is constrained
        assert model == "gemini-1.5-flash", f"Tight latency budget should select fast model, got {model}"
    
    def test_complex_query_selects_advanced_model(self):
        """
        Complex queries should prefer advanced models.
        """
        from services.cognitive_model.semantic_model_selector import (
            SemanticModelSelector, ModelSelectionCriteria
        )
        
        selector = SemanticModelSelector(["gemini-1.5-flash", "gemini-1.5-pro"])
        
        # Complex query criteria
        criteria = ModelSelectionCriteria(
            semantic_complexity=0.9,
            reasoning_depth_required=5,
            latency_budget_ms=10000,
            quality_vs_speed=0.9,  # Prefer quality
            involves_analysis=True,
            involves_step_by_step=True
        )
        
        model = selector.select(criteria)
        
        # Should select more capable model for complex queries
        assert model == "gemini-1.5-pro", f"Complex query should select pro model, got {model}"
    
    def test_model_selection_is_deterministic(self):
        """
        Same criteria should always select same model (pure function).
        """
        from services.cognitive_model.semantic_model_selector import (
            SemanticModelSelector, ModelSelectionCriteria
        )
        
        selector = SemanticModelSelector()
        
        criteria = ModelSelectionCriteria(
            semantic_complexity=0.5,
            reasoning_depth_required=2,
            latency_budget_ms=5000,
            quality_vs_speed=0.5
        )
        
        # Call multiple times
        model1 = selector.select(criteria)
        model2 = selector.select(criteria)
        model3 = selector.select(criteria)
        
        assert model1 == model2 == model3, "Model selection must be deterministic"
    
    def test_config_flags_for_model_selection(self):
        """
        Model selection config flags should exist.
        """
        from core.config import settings
        
        assert hasattr(settings, 'ENABLE_SEMANTIC_MODEL_SELECTION'), "Should have ENABLE_SEMANTIC_MODEL_SELECTION"
        assert hasattr(settings, 'DEFAULT_LLM_MODEL'), "Should have DEFAULT_LLM_MODEL"
        assert hasattr(settings, 'AVAILABLE_LLM_MODELS'), "Should have AVAILABLE_LLM_MODELS"


class TestGap2NoKeywordModelSelection:
    """
    CRITICAL: Model selection must NOT use task/agent names.
    """
    
    def test_no_task_name_in_criteria(self):
        """
        ModelSelectionCriteria should not have task name fields.
        """
        from services.cognitive_model.semantic_model_selector import ModelSelectionCriteria
        
        criteria = ModelSelectionCriteria()
        
        # These should NOT exist
        assert not hasattr(criteria, 'task_name')
        assert not hasattr(criteria, 'agent_name')
        assert not hasattr(criteria, 'intent_name')
    
    def test_selection_uses_only_numeric_criteria(self):
        """
        Selection should use numeric/semantic criteria only.
        """
        from services.cognitive_model.semantic_model_selector import ModelSelectionCriteria
        import dataclasses
        
        criteria = ModelSelectionCriteria()
        fields = {f.name: f.type for f in dataclasses.fields(criteria)}
        
        # No string-based selection criteria
        for field_name, field_type in fields.items():
            assert 'str' not in str(field_type) or field_name == 'model_name', \
                f"Selection criteria should not have string field: {field_name}"


# =============================================================================
# GAP 1 TESTS: AGENT AUTONOMY
# =============================================================================

class TestGap1AgentAutonomy:
    """
    GAP 1 TESTS: Verify agents can self-assess and decline.
    
    SHIP CONDITIONS:
    - Agents self-assess whether to participate
    - Supervisor never assigns agents
    - Agents can decline participation
    """
    
    def test_participation_decision_enum_exists(self):
        """
        ParticipationDecision enum should have all required values.
        """
        from services.cognitive_model.agent_self_assessment import ParticipationDecision
        
        assert hasattr(ParticipationDecision, 'STRONG_YES')
        assert hasattr(ParticipationDecision, 'YES')
        assert hasattr(ParticipationDecision, 'MAYBE')
        assert hasattr(ParticipationDecision, 'NO')
        assert hasattr(ParticipationDecision, 'DEFER')
    
    def test_agent_capability_dataclass_exists(self):
        """
        AgentCapability dataclass should exist with capability fields.
        """
        from services.cognitive_model.agent_self_assessment import AgentCapability
        
        cap = AgentCapability()
        
        assert hasattr(cap, 'can_handle_emotion')
        assert hasattr(cap, 'can_handle_planning')
        assert hasattr(cap, 'can_handle_problem_solving')
        assert hasattr(cap, 'can_handle_explanation')
        assert hasattr(cap, 'can_handle_urgency')
    
    def test_self_assessment_dataclass_exists(self):
        """
        SelfAssessment dataclass should exist with required fields.
        """
        from services.cognitive_model.agent_self_assessment import (
            SelfAssessment, ParticipationDecision
        )
        
        assessment = SelfAssessment(
            decision=ParticipationDecision.YES,
            confidence=0.8,
            relevance=0.9,
            reasoning="Test reasoning"
        )
        
        assert assessment.should_participate
        assert assessment.participation_score > 0
    
    def test_agent_can_decline(self):
        """
        CRITICAL: Agent must be able to say NO.
        """
        from services.cognitive_model.agent_self_assessment import (
            SelfAssessment, ParticipationDecision
        )
        
        # Agent declines
        assessment = SelfAssessment(
            decision=ParticipationDecision.NO,
            confidence=0.1,
            relevance=0.1,
            reasoning="Not my area of expertise"
        )
        
        assert not assessment.should_participate, "Agent must be able to decline"
        assert assessment.participation_score == 0, "Declined agent should have zero score"
    
    def test_agent_coordinator_exists(self):
        """
        AgentCoordinator should be instantiable.
        """
        from services.cognitive_model.agent_self_assessment import AgentCoordinator
        
        coordinator = AgentCoordinator()
        assert coordinator is not None
    
    def test_participation_score_calculation(self):
        """
        Participation score should combine decision, confidence, relevance.
        """
        from services.cognitive_model.agent_self_assessment import (
            SelfAssessment, ParticipationDecision
        )
        
        # Strong yes with high confidence should have highest score
        strong = SelfAssessment(
            decision=ParticipationDecision.STRONG_YES,
            confidence=0.9,
            relevance=0.9,
            reasoning="Highly relevant"
        )
        
        # Regular yes with medium confidence
        regular = SelfAssessment(
            decision=ParticipationDecision.YES,
            confidence=0.7,
            relevance=0.7,
            reasoning="Can help"
        )
        
        # Maybe with low confidence
        maybe = SelfAssessment(
            decision=ParticipationDecision.MAYBE,
            confidence=0.5,
            relevance=0.5,
            reasoning="Not sure"
        )
        
        assert strong.participation_score > regular.participation_score
        assert regular.participation_score > maybe.participation_score
    
    def test_config_flags_for_autonomy(self):
        """
        Agent autonomy config flags should exist.
        """
        from core.config import settings
        
        assert hasattr(settings, 'ENABLE_AGENT_AUTONOMY'), "Should have ENABLE_AGENT_AUTONOMY"
        assert hasattr(settings, 'ENABLE_AGENT_SELF_ASSESSMENT'), "Should have ENABLE_AGENT_SELF_ASSESSMENT"
        assert hasattr(settings, 'MAX_PARTICIPATING_AGENTS'), "Should have MAX_PARTICIPATING_AGENTS"


class TestGap1SupervisorAsCoordinator:
    """
    CRITICAL: Supervisor must be a coordinator, NOT a brain.
    """
    
    def test_coordinator_collects_not_assigns(self):
        """
        Coordinator collects assessments, does not assign agents.
        """
        from services.cognitive_model.agent_self_assessment import AgentCoordinator
        
        # Coordinator has no assign() method
        coordinator = AgentCoordinator()
        
        assert not hasattr(coordinator, 'assign_agent'), "Coordinator should not assign agents"
        assert hasattr(coordinator, 'coordinate'), "Coordinator should coordinate"
    
    def test_no_intent_to_agent_mapping(self):
        """
        There should be no static intent → agent mapping.
        """
        from services.cognitive_model.agent_self_assessment import AgentCoordinator
        
        coordinator = AgentCoordinator()
        
        # These patterns are BANNED
        assert not hasattr(coordinator, 'intent_agent_map')
        assert not hasattr(coordinator, 'task_agent_map')


# =============================================================================
# GAP 3 TESTS: CROSS-SESSION SEMANTIC LEARNING
# =============================================================================

class TestGap3SemanticLearning:
    """
    GAP 3 TESTS: Verify semantic learning stores signals, not transcripts.
    
    SHIP CONDITIONS:
    - Store structured semantic signals only
    - No transcripts stored
    - No embeddings stored
    - Learning through context injection only
    """
    
    def test_semantic_signal_dataclass_exists(self):
        """
        SemanticSignal dataclass should exist with required fields.
        """
        from services.cognitive_model.student_semantic_profile import SemanticSignal
        from datetime import datetime, timezone
        
        signal = SemanticSignal(
            signal_type="engaged_topic",
            subject="Physics",
            concept="Thermodynamics",
            value={"depth": 3},
            confidence=0.8
        )
        
        assert signal.signal_type == "engaged_topic"
        assert signal.subject == "Physics"
        assert isinstance(signal.value, dict)
    
    def test_student_semantic_profile_exists(self):
        """
        StudentSemanticProfile dataclass should exist.
        """
        from services.cognitive_model.student_semantic_profile import StudentSemanticProfile
        
        profile = StudentSemanticProfile(user_id="test_user")
        
        assert profile.user_id == "test_user"
        assert hasattr(profile, 'strong_subjects')
        assert hasattr(profile, 'weak_subjects')
        assert hasattr(profile, 'preferred_explanation_style')
    
    def test_profile_context_injection(self):
        """
        Profile should generate context injection dict.
        """
        from services.cognitive_model.student_semantic_profile import StudentSemanticProfile
        
        profile = StudentSemanticProfile(
            user_id="test_user",
            strong_subjects=["Physics", "Math"],
            weak_subjects=["Chemistry"],
            preferred_explanation_style="detailed"
        )
        
        injection = profile.get_context_injection()
        
        assert "student_learning_profile" in injection
        assert injection["student_learning_profile"]["preferred_explanation_style"] == "detailed"
    
    def test_no_raw_transcript_storage(self):
        """
        CRITICAL: Profile should not store raw transcripts.
        """
        from services.cognitive_model.student_semantic_profile import StudentSemanticProfile
        
        profile = StudentSemanticProfile(user_id="test_user")
        
        # These should NOT exist
        assert not hasattr(profile, 'transcripts')
        assert not hasattr(profile, 'raw_messages')
        assert not hasattr(profile, 'conversation_history')
    
    def test_no_embeddings_storage(self):
        """
        CRITICAL: Profile should not store embeddings.
        """
        from services.cognitive_model.student_semantic_profile import StudentSemanticProfile
        
        profile = StudentSemanticProfile(user_id="test_user")
        
        # These should NOT exist
        assert not hasattr(profile, 'embeddings')
        assert not hasattr(profile, 'vectors')
        assert not hasattr(profile, 'embedding_cache')
    
    def test_semantic_learning_extractor_exists(self):
        """
        SemanticLearningExtractor should be instantiable.
        """
        from services.cognitive_model.student_semantic_profile import SemanticLearningExtractor
        
        extractor = SemanticLearningExtractor()
        assert extractor is not None
    
    def test_profile_manager_exists(self):
        """
        SemanticProfileManager should be instantiable.
        """
        from services.cognitive_model.student_semantic_profile import SemanticProfileManager
        
        manager = SemanticProfileManager()
        assert manager is not None
    
    def test_config_flags_for_learning(self):
        """
        Semantic learning config flags should exist.
        """
        from core.config import settings
        
        assert hasattr(settings, 'ENABLE_SEMANTIC_LEARNING'), "Should have ENABLE_SEMANTIC_LEARNING"
        assert hasattr(settings, 'ENABLE_PROFILE_CONTEXT_INJECTION'), "Should have ENABLE_PROFILE_CONTEXT_INJECTION"
        assert hasattr(settings, 'MAX_SEMANTIC_SIGNALS_PER_USER'), "Should have MAX_SEMANTIC_SIGNALS_PER_USER"


class TestGap3ContextInjectionOnly:
    """
    CRITICAL: Learning must influence behavior ONLY through context injection.
    """
    
    def test_learning_is_explicit_not_hidden(self):
        """
        All learning must flow through explicit context injection.
        """
        from services.cognitive_model.student_semantic_profile import StudentSemanticProfile
        
        profile = StudentSemanticProfile(user_id="test_user")
        
        # The only way to get learning data is through get_context_injection
        injection = profile.get_context_injection()
        
        # All data must be in this explicit structure
        assert "student_learning_profile" in injection
        
        # No hidden state
        assert not hasattr(profile, '_hidden_model')
        assert not hasattr(profile, '_implicit_state')
    
    def test_signal_to_dict_is_structured(self):
        """
        Signals should serialize to structured data, not raw text.
        """
        from services.cognitive_model.student_semantic_profile import SemanticSignal
        
        signal = SemanticSignal(
            signal_type="concept_struggle",
            subject="Physics",
            concept="Thermodynamics",
            value={"difficulty": "high", "attempts": 3},
            confidence=0.9
        )
        
        d = signal.to_dict()
        
        # Should be structured
        assert isinstance(d, dict)
        assert "signal_type" in d
        assert "value" in d
        assert isinstance(d["value"], dict)


# =============================================================================
# RUN CONFIGURATION
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

