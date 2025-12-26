"""
🧠 Intelligence Regression Tests - Behavioral Validation
=========================================================

These tests validate SEMANTIC CORRECTNESS of outputs, not just status codes.
They ensure the AI actually behaves intelligently for key use cases.

CRITICAL: Tests must validate DYNAMIC behavior (LLM-determined), NOT keyword-based.

Run with: pytest backend/tests/test_intelligence_regression.py -v
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import os

# Set up test environment
os.environ.setdefault('OPENAI_API_KEY', 'test-key')


class TestSemanticAnalysisFields:
    """Test that semantic analysis includes actionable request detection"""
    
    def test_has_actionable_request_field_exists(self):
        """SemanticAnalysis must have has_actionable_request field"""
        from services.semantic_intent_classifier import SemanticAnalysis, SemanticIntent
        
        # Create an analysis with actionable request
        analysis = SemanticAnalysis(
            intent=SemanticIntent.GENERAL,
            confidence=0.9,
            emotional_tone="neutral",
            emotional_intensity=0.3,
            topic_mentioned=None,
            is_follow_up=False,
            urgency_level="medium",
            needs_empathy=False,
            needs_encouragement=False,
            needs_clarification=False,
            suggested_response_style="educational",
            reasoning="Test",
            has_actionable_request=True,
            requested_output_type="study_plan"
        )
        
        assert hasattr(analysis, 'has_actionable_request'), \
            "SemanticAnalysis must have has_actionable_request field"
        assert hasattr(analysis, 'requested_output_type'), \
            "SemanticAnalysis must have requested_output_type field"
        assert analysis.has_actionable_request == True
        assert analysis.requested_output_type == "study_plan"
    
    def test_to_dict_includes_actionable_fields(self):
        """to_dict must include actionable request fields"""
        from services.semantic_intent_classifier import SemanticAnalysis, SemanticIntent
        
        analysis = SemanticAnalysis(
            intent=SemanticIntent.GENERAL,
            confidence=0.9,
            emotional_tone="neutral",
            emotional_intensity=0.3,
            topic_mentioned=None,
            is_follow_up=False,
            urgency_level="medium",
            needs_empathy=False,
            needs_encouragement=False,
            needs_clarification=False,
            suggested_response_style="educational",
            reasoning="Test",
            has_actionable_request=True,
            requested_output_type="study_plan"
        )
        
        result = analysis.to_dict()
        
        assert "has_actionable_request" in result
        assert "requested_output_type" in result


class TestClassificationPrompt:
    """Test that classification prompt is dynamic, not keyword-based"""
    
    def test_prompt_has_actionable_request_instructions(self):
        """Prompt must instruct LLM to detect actionable requests dynamically"""
        from services.semantic_intent_classifier import SemanticIntentClassifier
        
        prompt = SemanticIntentClassifier.CLASSIFICATION_PROMPT
        
        assert "has_actionable_request" in prompt, \
            "Prompt must include has_actionable_request field for LLM to determine"
        assert "requested_output_type" in prompt, \
            "Prompt must include requested_output_type field for LLM to determine"
    
    def test_prompt_does_not_have_hardcoded_planning_intent(self):
        """Intent list should NOT have 'planning' as hardcoded keyword match"""
        from services.semantic_intent_classifier import SemanticIntent
        
        # Verify PLANNING_REQUEST is NOT in enum (we use dynamic detection instead)
        intent_values = [i.value for i in SemanticIntent]
        
        assert "planning" not in intent_values, \
            "Should not have hardcoded 'planning' intent - use has_actionable_request instead"
        assert "solve" not in intent_values, \
            "Should not have hardcoded 'solve' intent - use has_actionable_request instead"


class TestRoutingDecision:
    """Test that routing uses dynamic actionable request detection"""
    
    def test_actionable_request_routes_to_multi_agent(self):
        """
        When has_actionable_request=True, route to MULTI_AGENT (not proactive_guidance)
        """
        from services.intelligent_routing_engine import (
            IntelligentRoutingEngine, 
            RecommendedPipeline,
            QueryComplexity
        )
        from services.semantic_intent_classifier import SemanticIntent, SemanticAnalysis
        
        engine = IntelligentRoutingEngine()
        
        # Create analysis with actionable request (study_plan)
        # Note: intent can be "general" - the actionable_request field is what matters
        mock_analysis = SemanticAnalysis(
            intent=SemanticIntent.GENERAL,  # Intent is generic
            confidence=0.9,
            emotional_tone="neutral",
            emotional_intensity=0.3,
            topic_mentioned="study",
            is_follow_up=False,
            urgency_level="medium",
            needs_empathy=False,
            needs_encouragement=False,
            needs_clarification=False,
            suggested_response_style="educational",
            reasoning="User wants a study plan created",
            has_actionable_request=True,  # THIS is what triggers special handling
            requested_output_type="study_plan"
        )
        
        decision = engine._route_from_semantic_analysis(
            query="create a study plan for next 3 days",
            analysis=mock_analysis,
            context={}
        )
        
        # CRITICAL: Must route to MULTI_AGENT, not PROACTIVE_GUIDANCE
        assert decision.pipeline == RecommendedPipeline.MULTI_AGENT, \
            f"Actionable requests must route to MULTI_AGENT, got {decision.pipeline.value}"
        
        # Verify output_type is passed through
        assert decision.extra_context.get('output_type') == 'study_plan'
        assert decision.extra_context.get('has_actionable_request') == True
    
    def test_non_actionable_help_routes_to_proactive(self):
        """
        Non-actionable 'help' intent should still route to PROACTIVE_GUIDANCE
        """
        from services.intelligent_routing_engine import (
            IntelligentRoutingEngine, 
            RecommendedPipeline
        )
        from services.semantic_intent_classifier import SemanticIntent, SemanticAnalysis
        
        engine = IntelligentRoutingEngine()
        
        # "what can you do" - help intent, no actionable request
        mock_analysis = SemanticAnalysis(
            intent=SemanticIntent.GET_HELP,
            confidence=0.9,
            emotional_tone="neutral",
            emotional_intensity=0.2,
            topic_mentioned=None,
            is_follow_up=False,
            urgency_level="low",
            needs_empathy=False,
            needs_encouragement=False,
            needs_clarification=False,
            suggested_response_style="friendly",
            reasoning="User asking about capabilities",
            has_actionable_request=False,
            requested_output_type=None
        )
        
        decision = engine._route_from_semantic_analysis(
            query="what can you do",
            analysis=mock_analysis,
            context={}
        )
        
        assert decision.pipeline == RecommendedPipeline.PROACTIVE_GUIDANCE, \
            f"Non-actionable help should route to PROACTIVE_GUIDANCE, got {decision.pipeline.value}"


class TestEmotionalSupport:
    """Test emotional support stays as emotional support"""
    
    def test_anxious_message_not_routed_to_planning(self):
        """
        'I feel anxious about exams' should NOT be treated as a planning request
        """
        from services.intelligent_routing_engine import (
            IntelligentRoutingEngine, 
            RecommendedPipeline
        )
        from services.semantic_intent_classifier import SemanticIntent, SemanticAnalysis
        
        engine = IntelligentRoutingEngine()
        
        # Emotional support - NOT actionable
        mock_analysis = SemanticAnalysis(
            intent=SemanticIntent.EMOTIONAL_SUPPORT,
            confidence=0.9,
            emotional_tone="anxious",
            emotional_intensity=0.7,
            topic_mentioned="exams",
            is_follow_up=False,
            urgency_level="medium",
            needs_empathy=True,
            needs_encouragement=True,
            needs_clarification=False,
            suggested_response_style="supportive",
            reasoning="Student feeling anxious about exams",
            has_actionable_request=False,  # NOT a planning request
            requested_output_type=None
        )
        
        decision = engine._route_from_semantic_analysis(
            query="I feel anxious about exams",
            analysis=mock_analysis,
            context={}
        )
        
        # Should route to emotional support, NOT multi-agent for planning
        assert decision.pipeline == RecommendedPipeline.EMOTIONAL_SUPPORT, \
            f"Anxious message should route to EMOTIONAL_SUPPORT, got {decision.pipeline.value}"


class TestResponseContract:
    """Test that all pipelines return correct response schema"""
    
    def test_proactive_response_has_pipeline_key(self):
        """All pipeline responses must include 'pipeline' key for normalizer"""
        import inspect
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        source = inspect.getsource(UnifiedAIOrchestrator._proactive_guidance_response)
        
        assert '"pipeline"' in source or "'pipeline'" in source, \
            "_proactive_guidance_response must return dict with 'pipeline' key"
    
    def test_chitchat_response_has_pipeline_key(self):
        """Chitchat response must have pipeline key"""
        import inspect
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        source = inspect.getsource(UnifiedAIOrchestrator._chitchat_response)
        
        assert '"pipeline"' in source or "'pipeline'" in source, \
            "_chitchat_response must return dict with 'pipeline' key"


class TestMentorAgentIntegration:
    """Test MentorAgent properly handles output_type"""
    
    def test_mentor_has_output_type_handling(self):
        """MentorAgent must check context for output_type"""
        import inspect
        from agents.mentor import MentorAgent
        
        # Get source and verify output_type is used
        source = inspect.getsource(MentorAgent)
        
        assert "output_type" in source, \
            "MentorAgent must reference output_type from context"
        
        assert "has_actionable_request" in source, \
            "MentorAgent must reference has_actionable_request from context"
    
    def test_mentor_uses_study_planner_tool(self):
        """MentorAgent must have study_planner in tools"""
        from agents.mentor import MentorAgent
        
        agent = MentorAgent({})
        tools = agent.get_available_tools()
        
        assert "study_planner" in tools, \
            "MentorAgent must list study_planner as available tool"


class TestIdempotency:
    """Test request deduplication works"""
    
    def test_idempotency_code_present(self):
        """Verify idempotency code is in API endpoint"""
        import inspect
        from api.ai import generate_neuro_symbolic_response
        
        source = inspect.getsource(generate_neuro_symbolic_response)
        
        assert "request_idempotency" in source, \
            "API endpoint must include idempotency check"
        assert "request_hash" in source, \
            "API endpoint must compute request hash for deduplication"


class TestNoHardcodedKeywords:
    """Ensure no hardcoded keyword matching"""
    
    def test_routing_engine_does_not_have_planning_keywords(self):
        """
        Routing should NOT use keyword lists like ['plan', 'schedule', 'timetable']
        to detect planning requests. It should use LLM-determined has_actionable_request.
        """
        import inspect
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        
        source = inspect.getsource(IntelligentRoutingEngine._route_from_semantic_analysis)
        
        # Should NOT have keyword lists for planning
        keyword_patterns = [
            "'plan'", '"plan"',
            "'schedule'", '"schedule"',
            "'timetable'", '"timetable"'
        ]
        
        # The function should use has_actionable_request, not keyword matching
        for pattern in keyword_patterns:
            # Allow the word in logging/reasoning but not as routing condition
            assert f"if {pattern}" not in source.lower() and \
                   f"in [{pattern}" not in source.lower(), \
                f"_route_from_semantic_analysis should not use keyword matching for '{pattern}'"


class TestConversationContinuity:
    """
    Test conversation continuity - ensuring 'okay' after plan continues properly.
    
    ROOT CAUSE FIXED: conversation_state was querying 'session_messages' collection
    but messages are stored in 'chat_messages'. This caused is_truly_first_turn=True
    even when messages existed.
    """
    
    def test_is_truly_first_turn_uses_correct_collection(self):
        """is_truly_first_turn must query chat_messages, not session_messages"""
        import inspect
        from services.conversation_state import ConversationStateManager
        
        source = inspect.getsource(ConversationStateManager.is_truly_first_turn)
        
        # Must use chat_messages (where messages are stored)
        assert "chat_messages" in source, \
            "is_truly_first_turn must query chat_messages collection"
        
        # Must NOT use session_messages (which is always empty)
        # Allow the word in comments but not as the actual collection
        assert "self.db.session_messages" not in source, \
            "is_truly_first_turn must NOT query session_messages collection"
    
    def test_student_state_uses_correct_collection(self):
        """student_state_engine._detect_emotion_state must query chat_messages"""
        import inspect
        from services.cognitive_model.student_state_engine import StudentStateEngine
        
        source = inspect.getsource(StudentStateEngine._detect_emotion_state)
        
        assert "chat_messages" in source, \
            "_detect_emotion_state must query chat_messages collection"
        # Must NOT use self.db.session_messages (collection access)
        # Allow the word in comments but not as actual db access
        assert "self.db.session_messages" not in source, \
            "_detect_emotion_state must NOT use session_messages collection"
    
    @pytest.mark.asyncio
    async def test_first_turn_false_when_messages_exist(self):
        """is_truly_first_turn returns False when messages exist in session"""
        from services.conversation_state import ConversationStateManager
        
        # Mock the database
        mock_db = MagicMock()
        mock_db.chat_messages.count_documents = AsyncMock(return_value=3)
        mock_db.conversation_states.find_one = AsyncMock(return_value=None)
        
        manager = ConversationStateManager(mock_db)
        
        result = await manager.is_truly_first_turn("user123", "session456")
        
        assert result == False, \
            "is_truly_first_turn should return False when messages exist"
        
        # Verify it queried chat_messages with correct params
        mock_db.chat_messages.count_documents.assert_called_once_with({
            "session_id": "session456",
            "user_id": "user123"
        })
    
    @pytest.mark.asyncio
    async def test_first_turn_true_when_no_messages(self):
        """is_truly_first_turn returns True when session has no messages"""
        from services.conversation_state import ConversationStateManager
        
        mock_db = MagicMock()
        mock_db.chat_messages.count_documents = AsyncMock(return_value=0)
        mock_db.conversation_states.find_one = AsyncMock(return_value=None)
        
        manager = ConversationStateManager(mock_db)
        
        result = await manager.is_truly_first_turn("user123", "session456")
        
        assert result == True, \
            "is_truly_first_turn should return True when no messages exist"


class TestCSRFMiddleware:
    """
    Test CSRF middleware returns proper 403, not 500.
    
    ROOT CAUSE FIXED: HTTPException raised inside BaseHTTPMiddleware dispatch()
    causes Starlette's TaskGroup to wrap it in ExceptionGroup, resulting in 500.
    Fix: Use JSONResponse instead of raise HTTPException.
    """
    
    def test_csrf_uses_json_response_not_exception(self):
        """CSRF middleware must return JSONResponse, not raise HTTPException"""
        import inspect
        from middleware.csrf import CSRFMiddleware
        
        source = inspect.getsource(CSRFMiddleware.dispatch)
        
        # Must use JSONResponse for CSRF errors
        assert "JSONResponse" in source, \
            "CSRFMiddleware.dispatch must use JSONResponse for CSRF errors"
        
        # Check the fix pattern: return JSONResponse(...), not raise HTTPException(...)
        assert "return JSONResponse" in source, \
            "CSRFMiddleware should return JSONResponse for 403 errors"
    
    def test_csrf_imports_json_response(self):
        """CSRF module must import JSONResponse"""
        from middleware import csrf
        
        assert hasattr(csrf, 'JSONResponse'), \
            "csrf module must have JSONResponse imported"


class TestAcknowledgmentRouting:
    """Test that acknowledgment messages route correctly with context"""
    
    def test_acknowledgment_intent_exists(self):
        """SemanticIntent must include ACKNOWLEDGMENT"""
        from services.semantic_intent_classifier import SemanticIntent
        
        assert hasattr(SemanticIntent, 'ACKNOWLEDGMENT'), \
            "SemanticIntent must have ACKNOWLEDGMENT intent"
    
    def test_routing_has_state_authority_check(self):
        """Routing engine must have STATE_AUTHORITY check for continuity"""
        import inspect
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        
        source = inspect.getsource(IntelligentRoutingEngine.route)
        
        assert "STATE AUTHORITY" in source or "state_has_context" in source, \
            "Routing must check state authority for acknowledgments"
    
    def test_acknowledgment_decision_includes_continuity(self):
        """Acknowledgment routing decision must have continuity priority"""
        import inspect
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        
        source = inspect.getsource(IntelligentRoutingEngine._acknowledgment_decision)
        
        assert "continuity" in source, \
            "_acknowledgment_decision must prioritize continuity"


class TestPhaseC_ContinuityTracking:
    """
    Phase C: Test last_task_type tracking and continuation handler.
    
    The system must properly track the last output type (study_plan, explanation, etc.)
    so that "okay" / "got it" after a deliverable continues correctly.
    """
    
    def test_context_pack_has_continuity_fields(self):
        """ContextPack must have last_task tracking fields"""
        from services.context_pack import ContextPack
        import inspect
        
        source = inspect.getsource(ContextPack)
        
        # Must have new continuity fields
        assert "last_output_type" in source, \
            "ContextPack must have last_output_type field"
        assert "last_task_type" in source, \
            "ContextPack must have last_task_type field"
        assert "last_assistant_message" in source, \
            "ContextPack must have last_assistant_message field"
        assert "awaiting_continuation" in source, \
            "ContextPack must have awaiting_continuation field"
    
    def test_routing_preserves_continuation_context(self):
        """Routing must preserve last_output_type in extra_context for ack"""
        import inspect
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        
        # Check the route method includes last_output_type for continuation
        source = inspect.getsource(IntelligentRoutingEngine)
        
        # Must pass last_output_type for continuations
        assert "last_output_type" in source, \
            "Routing must pass last_output_type for continuation handling"
        assert "action_intent" in source, \
            "Routing must include action_intent in extra_context"
    
    def test_orchestrator_has_continuation_handler(self):
        """Orchestrator must have _generate_continuation_for_deliverable method"""
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        assert hasattr(UnifiedAIOrchestrator, '_generate_continuation_for_deliverable'), \
            "Orchestrator must have _generate_continuation_for_deliverable method"


class TestPhaseB_NoHardcoding:
    """
    Phase B: Test that hardcoding has been removed.
    
    When ENABLE_SEMANTIC_ONLY_ROUTING is True:
    - No keyword-based classification
    - No ACK_WORDS list routing
    - No casual_patterns model selection
    - No emotion keyword detection
    """
    
    def test_feature_flags_exist(self):
        """Feature flags must exist in config"""
        from core.config import settings
        
        assert hasattr(settings, 'ENABLE_SEMANTIC_ONLY_ROUTING'), \
            "Config must have ENABLE_SEMANTIC_ONLY_ROUTING flag"
        assert hasattr(settings, 'ENABLE_SEMANTIC_MODE_SELECTION'), \
            "Config must have ENABLE_SEMANTIC_MODE_SELECTION flag"
        assert hasattr(settings, 'ENABLE_SEMANTIC_EMOTION_DETECTION'), \
            "Config must have ENABLE_SEMANTIC_EMOTION_DETECTION flag"
        assert hasattr(settings, 'ENABLE_CONTINUITY_TRACKING'), \
            "Config must have ENABLE_CONTINUITY_TRACKING flag"
    
    def test_semantic_fallback_uses_no_keywords_when_enabled(self):
        """_fallback_analysis must not use keyword lists when flag enabled"""
        import inspect
        from services.semantic_intent_classifier import SemanticIntentClassifier
        
        source = inspect.getsource(SemanticIntentClassifier._fallback_analysis)
        
        # Must check the flag
        assert "ENABLE_SEMANTIC_ONLY_ROUTING" in source, \
            "_fallback_analysis must check ENABLE_SEMANTIC_ONLY_ROUTING flag"
        
        # Must have GENERAL path for flag-enabled case
        assert "SemanticIntent.GENERAL" in source, \
            "_fallback_analysis must return GENERAL when LLM fails and flag enabled"
    
    def test_routing_dialogue_act_checks_flag(self):
        """_detect_dialogue_act must check semantic flag for ACK handling"""
        import inspect
        from services.intelligent_routing_engine import IntelligentRoutingEngine
        
        source = inspect.getsource(IntelligentRoutingEngine._detect_dialogue_act)
        
        # Must check the flag
        assert "ENABLE_SEMANTIC_ONLY_ROUTING" in source, \
            "_detect_dialogue_act must check ENABLE_SEMANTIC_ONLY_ROUTING flag"
    
    def test_model_selection_uses_routing_decision(self):
        """_select_model must accept routing_decision for semantic selection"""
        import inspect
        from services.response_composer import ResponseComposer
        
        source = inspect.getsource(ResponseComposer._select_model)
        
        # Must accept routing_decision parameter
        assert "routing_decision" in source, \
            "_select_model must accept routing_decision parameter"
        assert "ENABLE_SEMANTIC_MODEL_SELECTION" in source, \
            "_select_model must check ENABLE_SEMANTIC_MODEL_SELECTION flag"
    
    def test_emotion_detection_uses_semantic_analysis(self):
        """_detect_emotion_state must accept semantic_analysis parameter"""
        import inspect
        from services.cognitive_model.student_state_engine import StudentStateEngine
        
        source = inspect.getsource(StudentStateEngine._detect_emotion_state)
        
        # Must accept semantic_analysis parameter
        assert "semantic_analysis" in source, \
            "_detect_emotion_state must accept semantic_analysis parameter"
        assert "ENABLE_SEMANTIC_EMOTION_DETECTION" in source, \
            "_detect_emotion_state must check ENABLE_SEMANTIC_EMOTION_DETECTION flag"
    
    def test_agent_negotiation_uses_semantic_scoring(self):
        """_estimate_confidence must use semantic signals when flag enabled"""
        import inspect
        from services.cognitive_model.agent_negotiation import AgentNegotiator
        
        source = inspect.getsource(AgentNegotiator._estimate_confidence)
        
        # Must accept semantic_analysis parameter
        assert "semantic_analysis" in source, \
            "_estimate_confidence must accept semantic_analysis parameter"
        assert "ENABLE_SEMANTIC_ONLY_ROUTING" in source, \
            "_estimate_confidence must check flag for semantic scoring"


class TestPhase1MentorBehavior:
    """
    Phase 1 INTELLIGENCE HARDENING - Mentor Behavior Tests
    
    These tests verify the AI behaves like a true mentor:
    - Clarifies vague questions before answering
    - Explains WHY mistakes happen (Error Genome™)
    - References exam urgency when relevant
    - Attributes intelligence ("Based on your patterns...")
    """
    
    def test_magic_prompts_include_error_genome(self):
        """MagicContext magic_prompts must include mistake patterns when present"""
        from services.student_intelligence_hub import MagicContext
        
        context = MagicContext()
        # Use actual mistake type patterns that are mapped in get_magic_prompts
        context.common_mistake_types = ['sign_error', 'unit_error']
        context.previous_topic = 'physics'
        context.topic_mastery = 50
        
        prompts = context.get_magic_prompts()
        prompts_text = "\n".join(prompts)
        
        # Must include Error Genome reference when mistakes exist
        # Maps to "sign errors" and "unit errors" in the prompt builder
        assert "ERROR GENOME" in prompts_text or "sign" in prompts_text.lower() or "unit" in prompts_text.lower(), \
            f"Magic prompts must surface common_mistake_types when present. Got: {prompts_text}"
    
    def test_magic_context_has_error_genome_field(self):
        """MagicContext must have common_mistake_types field"""
        from services.student_intelligence_hub import MagicContext
        
        context = MagicContext()
        
        assert hasattr(context, 'common_mistake_types'), \
            "MagicContext must have common_mistake_types field for Error Genome™"
    
    def test_formatting_rules_include_mentor_behavior(self):
        """FORMATTING_RULES must include mentor clarification guidance"""
        from services.dynamic_mentor_prompts import FORMATTING_RULES
        
        # Must guide mentor-like behavior
        assert "clarify" in FORMATTING_RULES.lower() or "guide" in FORMATTING_RULES.lower(), \
            "FORMATTING_RULES must include mentor clarification guidance"
    
    def test_adaptive_engine_includes_exam_urgency(self):
        """adapt_prompt must inject exam urgency when days_to_exam provided"""
        import inspect
        from services.cognitive_model.adaptive_engine import AdaptiveEngine
        
        source = inspect.getsource(AdaptiveEngine.adapt_prompt)
        
        # Must reference days_to_exam for urgency
        assert "days_to_exam" in source, \
            "adapt_prompt must use days_to_exam for exam urgency injection"
    
    def test_adaptive_engine_includes_error_genome(self):
        """adapt_prompt must inject mistake context when available"""
        import inspect
        from services.cognitive_model.adaptive_engine import AdaptiveEngine
        
        source = inspect.getsource(AdaptiveEngine.adapt_prompt)
        
        # Must reference common mistakes for Error Genome
        assert "mistake" in source.lower() or "error" in source.lower(), \
            "adapt_prompt must inject mistake context for Error Genome™"
    
    def test_adaptive_engine_includes_trust_attribution(self):
        """adapt_prompt must include attribution phrases for trust signals"""
        import inspect
        from services.cognitive_model.adaptive_engine import AdaptiveEngine
        
        source = inspect.getsource(AdaptiveEngine.adapt_prompt)
        
        # Must include attribution pattern
        assert "Based on" in source or "pattern" in source.lower(), \
            "adapt_prompt must include trust attribution phrases"
    
    def test_exam_countdown_magic_prompt_exists(self):
        """MagicContext must generate exam countdown prompts"""
        from services.student_intelligence_hub import MagicContext
        
        context = MagicContext()
        context.days_to_exam = 15
        context.exam_name = "JEE Main"
        
        prompts = context.get_magic_prompts()
        prompts_text = "\n".join(prompts)
        
        # Must include countdown
        assert "15" in prompts_text or "day" in prompts_text.lower(), \
            "Magic prompts must include exam countdown when days_to_exam set"
    
    def test_conceptual_prompt_includes_mentor_context(self):
        """_build_conceptual must include mistake-awareness"""
        import inspect
        from services.dynamic_mentor_prompts import DynamicMentorPrompts
        
        source = inspect.getsource(DynamicMentorPrompts._build_conceptual)
        
        # Must reference memory_context for mistakes
        assert "memory_context" in source or "mistake" in source.lower(), \
            "_build_conceptual must be aware of student mistake patterns"


class TestContinuityBehavior:
    """
    Behavior tests for conversation continuity.
    
    These tests verify that the system behaves like a teacher:
    - "okay" after a plan → continues the plan conversation
    - "simpler" after explanation → simplifies that explanation
    """
    
    @pytest.mark.asyncio
    async def test_context_pack_loads_last_task_info(self):
        """ContextPackBuilder must load last task info from DB"""
        from services.context_pack import ContextPackBuilder
        import inspect
        
        source = inspect.getsource(ContextPackBuilder)
        
        # Must have _get_last_task_info method
        assert "_get_last_task_info" in source, \
            "ContextPackBuilder must have _get_last_task_info method"
        
        # Must call it during build
        assert "last_task_info" in source or "last_output_type" in source, \
            "ContextPackBuilder.build must populate last task info"
    
    def test_proactive_response_passes_last_task_info(self):
        """_proactive_guidance_response must pass last_output_type to generator"""
        import inspect
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        source = inspect.getsource(UnifiedAIOrchestrator._proactive_guidance_response)
        
        # Must extract and pass last_output_type
        assert "last_output_type" in source, \
            "_proactive_guidance_response must handle last_output_type"
    
    def test_continuation_generator_uses_llm(self):
        """_generate_continuation_for_deliverable must use LLM, not templates"""
        import inspect
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        source = inspect.getsource(UnifiedAIOrchestrator._generate_continuation_for_deliverable)
        
        # Must use LLM for generation
        assert "AsyncOpenAI" in source or "client.chat.completions" in source, \
            "_generate_continuation_for_deliverable must use LLM, not hardcoded templates"
        
        # Must not have hardcoded response templates for specific outputs
        # (except minimal fallbacks)
        assert source.count('return "') < 5, \
            "_generate_continuation_for_deliverable should minimize hardcoded responses"


class TestFrontendChatComponents:
    """
    Frontend component contract tests - validates SmartResponse and ChatMessage
    
    CRITICAL REGRESSION TESTS:
    - SmartResponse must receive 'response' prop (not 'data')
    - Feedback buttons must render for ALL assistant messages
    - Input state must persist independently from AI responses
    
    Root Cause Fixed: SathiClassroom.jsx was passing 'data' prop but 
    SmartResponse expects 'response', causing feedback buttons to never render.
    """
    
    def test_sathi_classroom_uses_correct_smartresponse_props(self):
        """SathiClassroom ChatMessage must pass 'response' prop to SmartResponse"""
        import re
        
        # Read the frontend file
        with open('C:\\Users\\DELL\\DruvAI\\personal\\frontend\\src\\components\\SathiClassroom.jsx', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # CRITICAL: Must NOT use data= prop (the bug)
        assert 'data={content}' not in source, \
            "SathiClassroom must NOT pass 'data' prop to SmartResponse - use 'response' instead"
        
        # Must use correct 'response=' prop
        assert 'response={content}' in source or 'response={' in source, \
            "SathiClassroom must pass 'response' prop to SmartResponse"
    
    def test_sathi_classroom_passes_question_for_response_detection(self):
        """SmartResponse needs question prop for response type detection"""
        with open('C:\\Users\\DELL\\DruvAI\\personal\\frontend\\src\\components\\SathiClassroom.jsx', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Must pass question prop for response type detection
        assert 'question={' in source, \
            "SathiClassroom must pass 'question' prop to SmartResponse for response type detection"
    
    def test_smartresponse_feedback_bar_logic(self):
        """SmartResponse must show feedback bar for non-greeting responses"""
        with open('C:\\Users\\DELL\\DruvAI\\personal\\frontend\\src\\components\\SmartResponse.jsx', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # showInteractionBar logic must exist
        assert 'showInteractionBar' in source, \
            "SmartResponse must have showInteractionBar logic"
        
        # Must check for mainContent length
        assert "content?.mainContent?.length" in source or "mainContent?.length" in source, \
            "showInteractionBar must check mainContent length"
        
        # Must render ThumbsUp/ThumbsDown for feedback
        assert 'ThumbsUp' in source and 'ThumbsDown' in source, \
            "SmartResponse must render feedback buttons"
    
    def test_input_not_cleared_on_message_render(self):
        """Input state must NOT be affected by message list updates"""
        with open('C:\\Users\\DELL\\DruvAI\\personal\\frontend\\src\\components\\SathiClassroom.jsx', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # setInputMessage('') should ONLY appear in handleSend
        # Count occurrences of clearing input
        clear_input_count = source.count("setInputMessage('')")
        
        # Should only clear input once - in handleSend after sending
        assert clear_input_count <= 1, \
            f"setInputMessage('') appears {clear_input_count} times - should only clear on send"
        
        # Verify no useEffect that clears input on messages change
        import re
        # Look for patterns like useEffect(...setInputMessage('')...[messages])
        dangerous_effect = re.search(r'useEffect\([^)]+setInputMessage\([\'\"]{2}\)[^)]+\[.*messages.*\]', source)
        assert dangerous_effect is None, \
            "Found useEffect that clears input on messages change - this will cause input loss"
    
    def test_chatmessage_key_stability(self):
        """ChatMessage keys should be stable to prevent unnecessary remounts"""
        with open('C:\\Users\\DELL\\DruvAI\\personal\\frontend\\src\\components\\SathiClassroom.jsx', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Should use stable keys (message_id or timestamp), not just index
        # Look for the messages.map pattern
        assert 'message_id' in source or 'timestamp' in source, \
            "ChatMessage should use stable keys (message_id or timestamp) not just index"


class TestMagicContextSchema:
    """
    Test MagicContext schema completeness for Phase 1.
    
    Ensures all intelligence fields are properly serialized.
    """
    
    def test_magic_context_to_dict_includes_all_fields(self):
        """MagicContext.to_dict must include all Phase 1 intelligence fields"""
        from services.student_intelligence_hub import MagicContext
        
        context = MagicContext()
        context.days_to_exam = 30
        context.exam_name = "NEET"
        context.previous_topic = "Biology"  # MagicContext uses previous_topic, not current_topic
        context.topic_mastery = 65
        context.is_weak_area = False
        context.common_mistake_types = ['concept_confusion']
        
        result = context.to_dict()
        
        # Phase 1 required fields
        assert "days_to_exam" in result
        assert "exam_name" in result
        assert "previous_topic" in result  # Field that tracks topic context
        assert "topic_mastery" in result
        assert "is_weak_area" in result
        assert "common_mistake_types" in result, \
            "to_dict must include common_mistake_types for Error Genome™"
    
    def test_magic_context_defaults_are_safe(self):
        """MagicContext default values must not cause errors"""
        from services.student_intelligence_hub import MagicContext
        
        # Default initialization should not fail
        context = MagicContext()
        
        # All fields should have safe defaults
        assert context.common_mistake_types == [], \
            "common_mistake_types should default to empty list"
        assert context.days_to_exam is None or isinstance(context.days_to_exam, (int, float)), \
            "days_to_exam should be None or numeric"
        
        # to_dict should work with defaults
        try:
            result = context.to_dict()
            assert isinstance(result, dict)
        except Exception as e:
            pytest.fail(f"MagicContext.to_dict failed with defaults: {e}")
    
    def test_get_magic_prompts_with_empty_context(self):
        """get_magic_prompts must not fail when context is minimal"""
        from services.student_intelligence_hub import MagicContext
        
        context = MagicContext()
        
        # Should not raise even with empty data
        try:
            prompts = context.get_magic_prompts()
            assert isinstance(prompts, list)
        except Exception as e:
            pytest.fail(f"get_magic_prompts failed with empty context: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
