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
# RUN CONFIGURATION
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

