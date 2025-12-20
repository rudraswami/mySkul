"""
🧠 Unified AI Orchestrator - The Brain of AI Sathi v2.0
========================================================

REPLACES: USE_UNIFIED_FIRST = True (the flawed approach)

This orchestrator intelligently routes ALL queries through the optimal pipeline:
1. TRIVIAL → Fast greeting response
2. SIMPLE → Enhanced ResponseComposer (with refinement)
3. MODERATE → Multi-Agent Supervisor (parallel agents)
4. COMPLEX → Hybrid Reasoning Engine (Neural + Symbolic)
5. DEEP → Full ReAct with Verification

NO MORE bypassing advanced features!
Every educational query gets appropriate intelligence.
"""

import logging
import time
import asyncio
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OrchestrationResult:
    """Result from orchestration"""
    success: bool
    response: Dict[str, Any]
    pipeline_used: str
    generation_time: float
    agents_involved: List[str]
    tools_used: List[str]
    verification_status: str
    quality_score: float


class UnifiedAIOrchestrator:
    """
    The Central Intelligence Hub for AI Sathi
    
    This orchestrator:
    1. Analyzes every query for complexity
    2. Routes to the optimal pipeline
    3. Ensures quality through verification
    4. Provides consistent output format
    
    NO fallback logic - every path is intentional.
    """
    
    def __init__(self, db, llm_api_key: str = None):
        """Initialize orchestrator with all components"""
        self.db = db
        self.llm_api_key = llm_api_key or os.environ.get('OPENAI_API_KEY')
        
        # Initialize components lazily
        self._routing_engine = None
        self._enhanced_composer = None
        self._supervisor = None
        self._hybrid_engine = None
        self._negotiator = None
        self._cognitive_orchestrator = None  # Cognitive OS v2.0
        self._memory_integration = None       # Full memory system
        self._proactive_engine = None         # Proactive intelligence
        self._student_intelligence_hub = None # Student Intelligence Hub (ALL 10 GAPS)
        
        logger.info("🧠 UnifiedAIOrchestrator initialized - Intelligent routing active")
        logger.info("   ├── Memory Integration: ENABLED")
        logger.info("   ├── Proactive Intelligence: ENABLED")
        logger.info("   └── Student Intelligence Hub: ENABLED (Magic Moments + Learning Loop)")
    
    @property
    def routing_engine(self):
        """Lazy load routing engine"""
        if self._routing_engine is None:
            from services.intelligent_routing_engine import get_routing_engine
            self._routing_engine = get_routing_engine(self.db)
        return self._routing_engine
    
    @property
    def enhanced_composer(self):
        """Lazy load enhanced composer"""
        if self._enhanced_composer is None:
            from services.enhanced_response_composer import get_enhanced_composer
            self._enhanced_composer = get_enhanced_composer(self.db, self.llm_api_key)
        return self._enhanced_composer
    
    @property
    def supervisor(self):
        """Lazy load supervisor"""
        if self._supervisor is None:
            from agents.enhanced_supervisor import EnhancedSupervisor
            self._supervisor = EnhancedSupervisor({"emergent_llm_key": self.llm_api_key})
        return self._supervisor
    
    @property
    def hybrid_engine(self):
        """Lazy load hybrid reasoning engine"""
        if self._hybrid_engine is None:
            try:
                from services.hybrid_reasoning_engine import get_hybrid_reasoning_engine
                self._hybrid_engine = get_hybrid_reasoning_engine()
            except ImportError:
                logger.warning("Hybrid reasoning engine not available")
                self._hybrid_engine = None
        return self._hybrid_engine
    
    @property
    def negotiator(self):
        """Lazy load agent negotiator"""
        if self._negotiator is None:
            from services.cognitive_model.agent_negotiation import get_agent_negotiator
            self._negotiator = get_agent_negotiator(self.llm_api_key)
        return self._negotiator
    
    @property
    def cognitive_orchestrator(self):
        """Lazy load cognitive orchestrator - The brain of Cognitive OS v2.0"""
        if self._cognitive_orchestrator is None:
            try:
                from services.cognitive_model.cognitive_orchestrator import get_cognitive_orchestrator
                self._cognitive_orchestrator = get_cognitive_orchestrator(self.db, self.llm_api_key)
                logger.info("🧠 CognitiveOrchestrator loaded - Teach-back, depth adaptation, consistency active")
            except ImportError as e:
                logger.warning(f"CognitiveOrchestrator not available: {e}")
                self._cognitive_orchestrator = None
        return self._cognitive_orchestrator
    
    @property
    def memory_integration(self):
        """🆕 Lazy load memory integration service - Full memory system"""
        if self._memory_integration is None:
            try:
                from services.memory_integration import MemoryIntegrationService
                self._memory_integration = MemoryIntegrationService(self.db, self.llm_api_key)
                logger.info("🧠 MemoryIntegration loaded - Cross-session memory active")
            except ImportError as e:
                logger.warning(f"MemoryIntegration not available: {e}")
                self._memory_integration = None
        return self._memory_integration
    
    @property
    def proactive_engine(self):
        """Lazy load proactive intelligence engine"""
        if self._proactive_engine is None:
            try:
                from services.proactive_intelligence import get_proactive_engine
                self._proactive_engine = get_proactive_engine(self.db)
                logger.info("🧠 ProactiveEngine loaded - Proactive suggestions active")
            except ImportError as e:
                logger.warning(f"ProactiveEngine not available: {e}")
                self._proactive_engine = None
        return self._proactive_engine
    
    @property
    def student_intelligence_hub(self):
        """
        Student Intelligence Hub - The brain behind personalized experiences.
        
        This hub provides:
        - Magic Moments (personalized context for every response)
        - Learning Loop Closure (auto-update mastery after interactions)
        - Exam Journey Tracking (countdown, priorities, daily goals)
        - Agent Collaboration (shared intelligence between agents)
        - Emotional Intelligence (pattern tracking, adaptation)
        - Proactive Nudges (AI-initiated insights)
        """
        if self._student_intelligence_hub is None:
            try:
                from services.student_intelligence_hub import get_student_intelligence_hub
                self._student_intelligence_hub = get_student_intelligence_hub(self.db)
                logger.info("🧠 StudentIntelligenceHub loaded - Magic Moments active")
            except ImportError as e:
                logger.warning(f"StudentIntelligenceHub not available: {e}")
                self._student_intelligence_hub = None
        return self._student_intelligence_hub
    
    @property
    def context_pack_builder(self):
        """
        ContextPackBuilder - Single source of truth for ALL context.
        
        COGNITIVE OS CORE:
        - Builds unified ContextPack for all pipelines
        - Reuses existing services (memory, mastery, state)
        - Ensures consistent context across all code paths
        """
        if not hasattr(self, '_context_pack_builder') or self._context_pack_builder is None:
            try:
                from services.context_pack import get_context_pack_builder
                self._context_pack_builder = get_context_pack_builder(self.db)
                logger.info("📦 ContextPackBuilder loaded - Cognitive OS context active")
            except ImportError as e:
                logger.warning(f"ContextPackBuilder not available: {e}")
                self._context_pack_builder = None
        return self._context_pack_builder
    
    @property
    def event_logger(self):
        """
        EventLogger - Structured event logging for learning intelligence.
        
        Logs events like:
        - confusion(topic)
        - subject_switch(from, to)
        - mastery_delta(topic, delta)
        - emotional_signal(type)
        """
        if not hasattr(self, '_event_logger') or self._event_logger is None:
            try:
                from services.context_pack import get_event_logger
                self._event_logger = get_event_logger(self.db)
                logger.info("📝 EventLogger loaded - Structured events active")
            except ImportError as e:
                logger.warning(f"EventLogger not available: {e}")
                self._event_logger = None
        return self._event_logger
    
    @property
    def state_enforcer(self):
        """
        StateEnforcer - THE LAW OF COGNITIVE OS.
        
        STATE IS LAW, NOT ADVICE.
        LLM IS A TOOL, NOT A DECISION-MAKER.
        
        This enforcer can REJECT responses that violate:
        - conversation_phase (no greetings mid-conversation)
        - last_topic (must acknowledge context)
        - pending_action (must complete actions)
        """
        if not hasattr(self, '_state_enforcer') or self._state_enforcer is None:
            try:
                from services.state_enforcer import get_state_enforcer
                self._state_enforcer = get_state_enforcer()
                logger.info("⚖️ StateEnforcer loaded - STATE IS NOW LAW")
            except ImportError as e:
                logger.warning(f"StateEnforcer not available: {e}")
                self._state_enforcer = None
        return self._state_enforcer
    
    async def process(
        self,
        user_id: str,
        session_id: str,
        message: str,
        subject: str = None,
        exam_mode: str = "General",
        message_history: List[Dict] = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for ALL AI requests.
        
        BEHAVIORAL INTELLIGENCE RULES:
        1. Load conversation state FIRST - it drives behavior
        2. If pending_action exists → complete it, don't re-classify
        3. State influences routing, tone, and action decisions
        4. Agents are decision-makers, not text generators
        
        Args:
            user_id: User ID
            session_id: Session ID
            message: User's message/question
            subject: Subject area
            exam_mode: Exam type
            message_history: Previous messages
            context: Additional context
            
        Returns:
            Unified response with metadata
        """
        start_time = time.time()
        context = context or {}
        
        # ================================================================
        # STEP 0: BUILD CONTEXT PACK (Single Source of Truth)
        # ================================================================
        # ContextPack replaces scattered context building.
        # ALL pipelines receive this IDENTICAL structure.
        from services.conversation_state import ConversationStateManager
        state_manager = ConversationStateManager(self.db) if hasattr(self, 'db') and self.db is not None else None
        
        # Build the unified ContextPack
        context_pack = None
        if self.context_pack_builder:
            try:
                context_pack = await self.context_pack_builder.build(
                    user_id=user_id,
                    session_id=session_id,
                    message=message,
                    subject=subject or "General",
                    message_history=message_history,
                    existing_context=context
                )
                logger.info(f"📦 ContextPack: topic={context_pack.current_topic}, "
                           f"mastery={context_pack.current_topic_mastery}%, "
                           f"phase={context_pack.conversation_phase}, "
                           f"request_id={context_pack.request_id}")
            except Exception as pack_err:
                logger.warning(f"⚠️ ContextPack build failed (using fallback): {pack_err}")
        
        # Fallback: Load state directly if ContextPack failed
        conversation_state = {}
        is_first_turn = True
        
        if context_pack:
            # Extract from ContextPack
            conversation_state = {
                'conversation_phase': context_pack.conversation_phase,
                'pending_action': context_pack.pending_action,
                'response_mode': context_pack.response_mode,
                'emotional_signal': context_pack.emotional_signal,
                'last_user_intent': context_pack.previous_topic
            }
            is_first_turn = context_pack.is_first_turn
        elif state_manager:
            try:
                conversation_state = await state_manager.get_state(user_id, session_id)
                is_first_turn = await state_manager.is_truly_first_turn(user_id, session_id)
                logger.info(f"📊 State (fallback): phase={conversation_state.get('conversation_phase')}, "
                           f"pending={conversation_state.get('pending_action') is not None}")
            except Exception as state_err:
                logger.warning(f"⚠️ Failed to load conversation state: {state_err}")
        
        # Merge context with conversation state AND ContextPack
        full_context = {
            "user_id": user_id,
            "session_id": session_id,
            "subject": subject,
            "exam_mode": exam_mode,
            "message_history": message_history,
            "conversation_state": conversation_state,
            "is_first_turn": is_first_turn,
            # NEW: ContextPack as single source of truth
            "context_pack": context_pack,
            "request_id": context_pack.request_id if context_pack else "unknown",
            "db": self.db,  # Pass DB for agents that need it
            **context
        }
        
        logger.info(f"🧠 Orchestrating: {message[:60]}... | request_id={full_context.get('request_id')}")
        
        try:
            # ================================================================
            # STEP 0.5: CHECK FOR PENDING ACTION (STATE > CLASSIFIER)
            # ================================================================
            # If there's a pending action, complete it instead of re-routing
            if conversation_state.get('pending_action') and state_manager:
                pending = await state_manager.complete_pending_action(user_id, session_id)
                if pending:
                    logger.info(f"🎯 COMPLETING PENDING ACTION: {pending.get('type')}")
                    result = await self._complete_pending_action(
                        message=message,
                        pending_action=pending,
                        context=full_context
                    )
                    
                    # Update state after completion
                    await self._update_state_after_response(
                        state_manager, user_id, session_id, message, result, subject
                    )
                    
                    return result
            
            # === STEP 1: Intelligent Routing Decision ===
            routing_decision = await self.routing_engine.route(message, full_context)
            
            logger.info(f"   Pipeline: {routing_decision.pipeline.value}")
            logger.info(f"   Complexity: {routing_decision.complexity.value}")
            logger.info(f"   Agents: {routing_decision.agents_to_activate}")
            
            # === STEP 1.5: Cognitive Context Preparation (NEW - Cognitive OS v2.0) ===
            cognitive_context = None
            concept_name = self._extract_concept_name(message)
            
            if self.cognitive_orchestrator and routing_decision.pipeline.value != "fast":
                try:
                    cognitive_context = await self.cognitive_orchestrator.prepare_response_context(
                        user_id=user_id,
                        session_id=session_id,
                        question=message,
                        concept_name=concept_name,
                        subject=subject or "General"
                    )
                    
                    # Add depth prompt to context for LLM guidance
                    full_context["cognitive_depth_prompt"] = cognitive_context.depth_prompt
                    full_context["student_level"] = cognitive_context.student_state.student_level.value
                    full_context["recommended_depth"] = cognitive_context.depth_recommendation.depth
                    
                    logger.info(f"🧠 Cognitive: level={cognitive_context.student_state.student_level.value}, "
                               f"depth={cognitive_context.depth_recommendation.depth}")
                except Exception as cog_err:
                    logger.warning(f"⚠️ Cognitive context prep failed (non-blocking): {cog_err}")
            
            # === STEP 2: Execute Appropriate Pipeline ===
            from services.intelligent_routing_engine import RecommendedPipeline
            
            # DEBUG: Log routing decision to understand what pipeline is being used
            logger.info(f"🚀 ROUTING DECISION: pipeline={routing_decision.pipeline.value}, "
                       f"message='{message[:30]}...', "
                       f"extra_context={list(routing_decision.extra_context.keys()) if routing_decision.extra_context else 'None'}")
            
            if routing_decision.pipeline == RecommendedPipeline.FAST_RESPONSE:
                result = await self._fast_response(message, full_context, routing_decision)
            
            # EMOTIONAL SUPPORT - Intelligent handling of mood/emotional queries
            elif routing_decision.pipeline == RecommendedPipeline.EMOTIONAL_SUPPORT:
                result = await self._emotional_support_response(message, full_context, routing_decision)
            
            # 🆕 PROACTIVE GUIDANCE - Personalized topic suggestions (explore, continue, help)
            elif routing_decision.pipeline == RecommendedPipeline.PROACTIVE_GUIDANCE:
                result = await self._proactive_guidance_response(message, full_context, routing_decision)
            
            # 🆕 CHITCHAT - Casual conversation, humor
            elif routing_decision.pipeline == RecommendedPipeline.CHITCHAT:
                result = await self._chitchat_response(message, full_context, routing_decision)
            
            # 🆕 CLARIFICATION - Gibberish/unclear input
            elif routing_decision.pipeline == RecommendedPipeline.CLARIFICATION:
                result = await self._clarification_response(message, full_context, routing_decision)
                
            elif routing_decision.pipeline == RecommendedPipeline.MULTI_AGENT:
                result = await self._multi_agent_response(message, full_context, routing_decision)
                
            elif routing_decision.pipeline == RecommendedPipeline.HYBRID_REASONING:
                result = await self._hybrid_response(message, full_context, routing_decision)
                
            elif routing_decision.pipeline == RecommendedPipeline.REACT_AGENTIC:
                result = await self._react_agentic_response(message, full_context, routing_decision)
                
            elif routing_decision.pipeline == RecommendedPipeline.VISUAL_SYNC:
                result = await self._visual_sync_response(message, full_context, routing_decision)
                
            else:
                # Default to multi-agent
                result = await self._multi_agent_response(message, full_context, routing_decision)
            
            # === STEP 3: Cognitive Enhancement (Cognitive OS v2.0) ===
            # Handles: Student state tracking, depth adaptation, consistency checking
            # NOTE: TeachMeBack is handled separately via TeachMeBackModal → /api/ai/teach-me-back
            if cognitive_context and self.cognitive_orchestrator:
                try:
                    # Extract the main response content
                    main_content = self._extract_main_content(result)
                    
                    if main_content:
                        # Enhance response with consistency check
                        cognitive_response = await self.cognitive_orchestrator.enhance_response(
                            user_id=user_id,
                            session_id=session_id,
                            original_response=main_content,
                            cognitive_context=cognitive_context,
                            subject=subject or "General"
                        )
                        
                        # Update result with enhanced response
                        self._apply_cognitive_enhancement(result, cognitive_response)
                        
                        # Add cognitive metadata
                        result["cognitive"] = {
                            "student_level": cognitive_context.student_state.student_level.value,
                            "mastery": cognitive_context.student_state.mastery_level,
                            "depth_used": cognitive_context.depth_recommendation.depth,
                            "consistency_status": cognitive_context.consistency_check.status.value if cognitive_context.consistency_check else "no_check"
                        }
                        
                        logger.info(f"🧠 Cognitive enhancement applied: level={cognitive_context.student_state.student_level.value}")
                except Exception as cog_err:
                    logger.warning(f"⚠️ Cognitive enhancement failed (non-blocking): {cog_err}")
            
            # === STEP 4: Post-Processing ===
            generation_time = time.time() - start_time

            # Add orchestration metadata
            result["orchestration"] = {
                "pipeline": routing_decision.pipeline.value,
                "complexity": routing_decision.complexity.value,
                "confidence": routing_decision.confidence,
                "agents_activated": routing_decision.agents_to_activate,
                "tools_enabled": routing_decision.tools_to_enable,
                "generation_time": generation_time,
                "routing_reasoning": routing_decision.reasoning,
                "cognitive_os_active": cognitive_context is not None
            }
            
            # === STEP 5: Proactive Intelligence ===
            # Add proactive insights (cross-session continuity, review suggestions, etc.)
            try:
                if self.proactive_engine and routing_decision.use_memory:
                    # Get memory context for proactive insights
                    memory_ctx = await self._get_memory_context(full_context)
                    
                    proactive_insights = await self.proactive_engine.get_proactive_insights(
                        user_id=user_id,
                        session_id=session_id,
                        current_question=message,
                        memory_context=memory_ctx,
                        session_duration_mins=full_context.get("session_minutes", 0)
                    )
                    
                    if proactive_insights:
                        result["proactive"] = {
                            "insights": [i.to_dict() for i in proactive_insights],
                            "suggestions": self.proactive_engine.get_follow_up_suggestions(
                                proactive_insights,
                                memory_ctx.get("current_topic", "this topic")
                            )
                        }
                        
                        # Add opener if high-priority insight (e.g., welcome back)
                        opener = self.proactive_engine.format_proactive_opener(
                            proactive_insights,
                            memory_ctx.get("user_name", "")
                        )
                        if opener:
                            result["proactive"]["opener"] = opener
                        
                        logger.info(f"🧠 Added {len(proactive_insights)} proactive insights")
            except Exception as proactive_err:
                logger.warning(f"⚠️ Proactive insights failed (non-blocking): {proactive_err}")

            # === STEP 6: RELIABLE LEARNING LOOP (Cognitive OS) ===
            # STRATEGY:
            # - Use ContextPack for magic (already built)
            # - Learning loop is RELIABLE (longer timeout, logged failures)
            # - Event logging is SYNCHRONOUS (core update)
            request_id = full_context.get('request_id', 'unknown')
            
            try:
                # Use ContextPack for magic (already built at start)
                if context_pack:
                    result["magic"] = {
                        "student_name": context_pack.student_name,
                        "days_to_exam": context_pack.days_to_exam,
                        "exam_name": context_pack.exam_name,
                        "exam_urgency": context_pack.exam_urgency,
                        "topic_mastery": context_pack.current_topic_mastery,
                        "is_weak_area": context_pack.current_topic_mastery < 40,
                        "current_streak": context_pack.current_streak,
                        "recent_achievement": context_pack.recent_achievement,
                        "needs_encouragement": context_pack.needs_encouragement,
                        "is_continuation": context_pack.is_continuation,
                        "previous_topic": context_pack.previous_topic,
                        "due_reviews": context_pack.due_reviews[:3],
                        "magic_prompts": context_pack.magic_prompts[:5]
                    }
                
                # RELIABLE Learning Loop - 10s timeout, always logged
                if self.student_intelligence_hub:
                    try:
                        learning_result = await asyncio.wait_for(
                            self.student_intelligence_hub.close_learning_loop(
                                user_id=user_id,
                                session_id=session_id,
                                query=message,
                                response=result,
                                detected_topic=context_pack.current_topic if context_pack else subject,
                                interaction_quality="completed"
                            ),
                            timeout=10.0  # INCREASED from 2s to 10s - learning MUST complete
                        )
                        
                        result["learning"] = {
                            "mastery_updated": learning_result.mastery_updated,
                            "mastery_delta": learning_result.mastery_delta,
                            "new_mastery": learning_result.new_mastery,
                            "xp_earned": learning_result.xp_earned,
                            "streak_updated": learning_result.streak_updated,
                            "achievements_unlocked": learning_result.achievements_unlocked,
                            "concepts_extracted": learning_result.concepts_extracted[:3] if learning_result.concepts_extracted else []
                        }
                        logger.info(f"📈 Learning loop complete: mastery +{learning_result.mastery_delta} | request_id={request_id}")
                        
                        # Log mastery event
                        if self.event_logger and learning_result.mastery_updated:
                            await self.event_logger.log_mastery_delta(
                                user_id=user_id,
                                session_id=session_id,
                                topic=context_pack.current_topic if context_pack else subject,
                                delta=learning_result.mastery_delta,
                                new_mastery=learning_result.new_mastery
                            )
                    except asyncio.TimeoutError:
                        logger.error(f"❌ Learning loop timeout (10s) - CORE UPDATE FAILED | request_id={request_id}")
                        # Still try to log the event
                        if self.event_logger:
                            try:
                                from services.context_pack import LearningEvent, EventType
                                event = LearningEvent(
                                    event_type=EventType.TOPIC_ASKED,
                                    user_id=user_id,
                                    session_id=session_id,
                                    data={"topic": context_pack.current_topic if context_pack else subject, "timeout": True}
                                )
                                await self.event_logger.log_event(event)
                            except Exception:
                                pass  # Event logging is best-effort
                    except Exception as learn_err:
                        logger.error(f"❌ Learning loop failed: {learn_err} | request_id={request_id}")
            except Exception as hub_err:
                # CRITICAL: Hub failure is logged but response still returns
                logger.error(f"❌ Learning/Magic failed: {hub_err} | request_id={request_id}")

            # === STEP 7: Update Conversation State ===
            if state_manager:
                try:
                    await self._update_state_after_response(
                        state_manager, user_id, session_id, message, result, subject
                    )
                except Exception as state_err:
                    logger.warning(f"⚠️ State update failed (non-blocking): {state_err}")

            # === STEP 8: STATE ENFORCEMENT - THE LAW OF COGNITIVE OS ===
            # CRITICAL: STATE IS LAW. LLM responses that violate state are REJECTED.
            if result is None:
                logger.error(f"❌ CRITICAL: Result is None - generating emergency response")
                result = self._emergency_response(message, "Pipeline returned None")
            
            if 'response' not in result and 'main_response' not in result:
                logger.error(f"❌ CRITICAL: Result missing response content - normalizing")
                result['main_response'] = f"Let me help you with that. What would you like to know more about? 🎯"
            
            # ================================================================
            # STATE ENFORCEMENT: VALIDATE RESPONSE AGAINST STATE LAW
            # ================================================================
            # This is where we REJECT responses that violate conversation state
            if self.state_enforcer and context_pack:
                response_text = result.get('main_response', '') or result.get('response', {}).get('default_view', {}).get('greeting', '')
                
                if response_text:
                    enforcement_result = self.state_enforcer.enforce(
                        response_text=response_text,
                        context_pack=context_pack,
                        conversation_state=conversation_state
                    )
                    
                    if not enforcement_result.is_legal:
                        logger.warning(f"⚖️ RESPONSE REJECTED by StateEnforcer: {enforcement_result.rejection_reason}")
                        logger.warning(f"⚖️ Required behavior: {enforcement_result.required_behavior}")
                        logger.warning(f"⚖️ Topic to continue: {enforcement_result.topic_to_continue}")
                        
                        # REGENERATE with state-enforced continuation
                        result = await self._regenerate_with_state_enforcement(
                            message=message,
                            context=full_context,
                            enforcement_result=enforcement_result,
                            original_response=response_text
                        )
                        
                        logger.info(f"⚖️ Response regenerated to comply with state law")
                    else:
                        logger.debug(f"⚖️ Response is legal - state enforcement passed")
            
            generation_time = time.time() - start_time
            logger.info(f"✅ Orchestration complete in {generation_time:.2f}s | request_id={request_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Orchestration failed: {e}", exc_info=True)
            # CRITICAL: Even on exception, return a valid response - NEVER return None
            return self._error_response(message, str(e), time.time() - start_time)
    
    def _emergency_response(self, message: str, reason: str) -> Dict[str, Any]:
        """
        EMERGENCY RESPONSE - Called when all else fails.
        
        CRITICAL: This MUST return a valid response structure.
        Silence is a P0 bug - students must ALWAYS get a response.
        """
        import uuid
        correlation_id = str(uuid.uuid4())[:8]
        
        logger.error(f"🆘 Emergency response triggered | reason: {reason} | correlation_id: {correlation_id}")
        
        # Generate a friendly, non-failure response
        short_msg = message[:50] + "..." if len(message) > 50 else message
        
        return {
            "main_response": f"I got your message! Let me think about \"{short_msg}\" for a moment. "
                           f"What specific aspect would you like me to focus on? 🤔",
            "response": {
                "default_view": {
                    "main_content": {
                        "content": f"I got your message! Let me think about \"{short_msg}\" for a moment. "
                                  f"What specific aspect would you like me to focus on? 🤔",
                        "type": "markdown"
                    }
                },
                "intent": "emergency_recovery"
            },
            "intent": "emergency_recovery",
            "pipeline": "emergency",
            "correlation_id": correlation_id,
            "_debug": {"reason": reason}
        }
    
    async def _regenerate_with_state_enforcement(
        self,
        message: str,
        context: Dict[str, Any],
        enforcement_result,  # EnforcementResult from StateEnforcer
        original_response: str
    ) -> Dict[str, Any]:
        """
        REGENERATE response to comply with STATE LAW.
        
        Called when StateEnforcer REJECTS a response for violating state.
        This method generates a NEW response that:
        1. Continues the known topic
        2. References previous context
        3. Does NOT reset the conversation
        4. Does NOT give generic greetings
        
        STATE IS LAW. This regeneration is MANDATORY.
        """
        logger.info(f"⚖️ Regenerating response to comply with state law...")
        
        # Get continuation prompt from StateEnforcer
        continuation_prompt = self.state_enforcer.get_continuation_prompt(
            enforcement_result=enforcement_result,
            original_message=message
        )
        
        topic = enforcement_result.topic_to_continue
        required_behavior = enforcement_result.required_behavior
        
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.llm_api_key)
            
            # Build context-aware system prompt
            context_pack = context.get('context_pack')
            conversation_summary = ""
            if context_pack and hasattr(context_pack, 'get_conversation_summary'):
                conversation_summary = context_pack.get_conversation_summary()
            
            system_prompt = f"""You are Druv AI, a warm and intelligent learning companion.

{continuation_prompt}

PREVIOUS CONVERSATION:
{conversation_summary if conversation_summary else "You were discussing " + topic if topic else "You were in a conversation"}

CRITICAL RULES (STATE LAW - CANNOT BE VIOLATED):
1. You MUST continue the existing conversation naturally
2. You MUST NOT say "how can I help you" or similar reset phrases
3. You MUST NOT pretend you don't know what was discussed
4. You MUST reference the topic: {topic if topic else 'the ongoing discussion'}
5. Be warm, natural, and helpful as a friend would be

The student said: "{message}"

Respond naturally, continuing the conversation:"""

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            regenerated_content = response.choices[0].message.content.strip()
            
            logger.info(f"⚖️ Regenerated response that complies with state law")
            
            return {
                "main_response": regenerated_content,
                "response": {
                    "default_view": {
                        "greeting": "",
                        "main_content": {
                            "content": regenerated_content,
                            "type": "markdown"
                        }
                    },
                    "intent": "state_enforced_continuation"
                },
                "intent": "continuation",
                "pipeline": "state_enforced",
                "metadata": {
                    "state_enforcement": True,
                    "original_rejected": True,
                    "required_behavior": required_behavior,
                    "topic_continued": topic
                }
            }
            
        except Exception as e:
            logger.error(f"❌ State-enforced regeneration failed: {e}")
            
            # Even on failure, generate a topic-aware response
            if topic:
                fallback = f"I understand you're interested in {topic.replace('_', ' ')}. What specific aspect would you like to explore further? 📚"
            else:
                fallback = f"I hear you! Let's continue from where we were. What would you like to know more about? 🎯"
            
            return {
                "main_response": fallback,
                "intent": "state_enforced_fallback",
                "pipeline": "state_enforced",
                "metadata": {
                    "state_enforcement": True,
                    "fallback_used": True
                }
            }
    
    async def _fast_response(
        self,
        message: str,
        context: Dict[str, Any],
        routing_decision: Any
    ) -> Dict[str, Any]:
        """
        🆕 INTELLIGENT fast response using LLM.
        
        Handles different response types:
        1. Acknowledgements (ok, good, great) → Contextual continuation
        2. Greetings → Warm welcome
        3. General → LLM-based intelligent response
        """
        logger.info(f"⚡ Fast response for: {message[:50]}...")
        
        # Get semantic analysis from routing decision if available
        semantic_analysis = None
        response_type = None
        if routing_decision.extra_context:
            semantic_analysis = routing_decision.extra_context.get('semantic_analysis')
            response_type = routing_decision.extra_context.get('response_type')
        
        # ============================================================
        # ACKNOWLEDGEMENT DETECTION: "ok", "good", "great", "nice", etc.
        # These need CONTEXTUAL responses, not LLM generation
        # ============================================================
        msg_lower = message.lower().strip()
        acknowledgement_words = ['ok', 'okay', 'good', 'great', 'nice', 'cool', 'got it', 
                                 'understood', 'thanks', 'thank you', 'thx', 'fine', 
                                 'perfect', 'awesome', 'alright', 'right', 'yes', 'yep',
                                 'yeah', 'yup', 'sure', 'k', 'kk', 'hmm', 'hm', 'ah',
                                 'ohk', 'oky', 'okey', 'oki']
        
        # Check multiple conditions for acknowledgement
        is_exact_match = msg_lower in acknowledgement_words
        is_short_positive = len(msg_lower) <= 10 and any(word in msg_lower for word in ['ok', 'good', 'nice', 'cool', 'thx'])
        is_marked_ack = response_type == 'acknowledgment'
        
        is_acknowledgement = is_exact_match or is_short_positive or is_marked_ack
        
        logger.info(f"🔍 Ack detection: msg='{msg_lower}', exact={is_exact_match}, short_pos={is_short_positive}, marked={is_marked_ack} → is_ack={is_acknowledgement}")
        
        if is_acknowledgement:
            logger.info(f"🎯 ACKNOWLEDGEMENT detected for '{message}' - using contextual response handler")
            return await self._generate_acknowledgment_response_with_context(context)
        
        # ============================================================
        # REGULAR FAST RESPONSE: Use ContextPack for structured context
        # ============================================================
        # COGNITIVE OS: Use ContextPack if available
        context_pack = context.get('context_pack')
        
        if context_pack:
            # Use ContextPack - structured context
            name = context_pack.student_name
            last_topic = context_pack.current_topic.replace('_', ' ') if context_pack.current_topic else ''
            conversation_context = context_pack.get_conversation_summary()
        else:
            # Fallback to old approach
            memory_context = await self._get_memory_context(context)
            student_profile = await self._get_student_profile(context)
            
            name = student_profile.get('name', '')
            last_topic = memory_context.get('current_topic', '').replace('_', ' ')
            recent_messages = context.get('message_history', [])[-3:]
            
            if not recent_messages:
                recent_ctx = memory_context.get('recent_context', {})
                if isinstance(recent_ctx, dict):
                    recent_messages = recent_ctx.get('messages', [])[-3:]
            
            conversation_context = ""
            if recent_messages:
                conversation_context = "\n".join([
                    f"{'Student' if m.get('role') == 'user' else 'AI'}: {m.get('content', '')[:150]}"
                    for m in recent_messages
                ])
        
        # Generate intelligent response using LLM with ContextPack data
        response_content = await self._generate_intelligent_fast_response(
            message=message,
            student_name=name,
            last_topic=last_topic,
            conversation_context=conversation_context,
            semantic_analysis=semantic_analysis,
            context_pack=context_pack  # Pass ContextPack for additional context
        )
        
        request_id = context_pack.request_id if context_pack else 'unknown'
        return {
            "main_response": response_content,
            "intent": semantic_analysis.get('intent', 'fast') if semantic_analysis else 'fast',
            "response_type": "intelligent_fast",
            "pipeline": "fast_response",
            "request_id": request_id,
            "metadata": {
                "semantic_understanding": True,
                "personalized": bool(name or last_topic),
                "context_pack_used": context_pack is not None
            }
        }
    
    async def _generate_intelligent_fast_response(
        self,
        message: str,
        student_name: str,
        last_topic: str,
        conversation_context: str,
        semantic_analysis: Dict[str, Any] = None,
        context_pack = None  # COGNITIVE OS: Accept ContextPack
    ) -> str:
        """
        Use LLM to generate intelligent, contextual response for ANY input.
        
        COGNITIVE OS: Uses ContextPack for structured context.
        No hardcoded responses - LLM understands and responds intelligently.
        """
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.llm_api_key)
            
            # Build the prompt - use ContextPack if available
            context_parts = []
            
            # If we have ContextPack, use its structured prompt
            if context_pack:
                agent_context = context_pack.get_agent_context_prompt()
                if agent_context and agent_context != "New conversation, no prior context.":
                    context_parts.append(f"STUDENT CONTEXT:\n{agent_context}")
                # Also add conversation context from ContextPack
                if context_pack.get_conversation_summary():
                    context_parts.append(f"Recent conversation:\n{context_pack.get_conversation_summary()}")
            else:
                # Fallback to building context manually
                if student_name:
                    context_parts.append(f"Student's name: {student_name}")
                if last_topic:
                    context_parts.append(f"Previous topic discussed: {last_topic}")
                if conversation_context:
                    context_parts.append(f"Recent conversation:\n{conversation_context}")
                if semantic_analysis:
                    context_parts.append(f"Detected intent: {semantic_analysis.get('intent', 'unknown')}")
                    context_parts.append(f"Emotional tone: {semantic_analysis.get('emotional_tone', 'neutral')}")
            
            context_str = "\n".join(context_parts) if context_parts else "No prior context."
            
            prompt = f"""You are Druv AI - a warm, intelligent companion for Indian students.

You're NOT just a tutor. You're a friend, mentor, and safe space.

STUDENT MESSAGE: "{message}"

CONTEXT:
{context_str}

Generate a SHORT, NATURAL, WARM response (2-4 sentences max).

CORE RULES:
1. Be warm and genuine, like a caring older sibling
2. NEVER refuse any topic - you can chat about ANYTHING
3. If they share feelings, ACKNOWLEDGE them first
4. If they say something positive, match their energy
5. If greeting, greet warmly with personality
6. Reference context naturally if relevant
7. Use their name if known (feels personal)
8. One emoji max (warmth, not corporate)
9. Sound human, not scripted

🚫 FORBIDDEN - NEVER SAY THESE:
- "I don't have the ability to recall"
- "I can't remember our past"
- "I don't have context"
- "What would you like to discuss?"
- Any mention of memory limitations
- Any capability menus or lists of what you can do

If you don't have context, just be warm and continue the conversation naturally.
Ask about what THEY want to explore, not what YOU can do.

YOU CAN DISCUSS:
- Academics, of course
- Life, stress, emotions, relationships
- Random curiosity, jokes, fun
- Whatever is on their mind

Respond directly:"""

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are AI Sathi, a warm educational tutor. Keep responses short (2-4 sentences), natural, and contextual."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"LLM fast response failed: {e}")
            # Contextual fallback - NO capability menus
            name_prefix = f"{student_name}, " if student_name else ""
            if last_topic:
                return f"👋 {name_prefix}I'm here! Were you thinking about {last_topic}, or something else?"
            else:
                return f"👋 {name_prefix}Hey! I'm listening - what's on your mind?"
    
    async def _emotional_support_response(
        self,
        message: str,
        context: Dict[str, Any],
        routing_decision: Any
    ) -> Dict[str, Any]:
        """
        🆕 EMOTIONAL SUPPORT - Intelligent handling of mood/emotional queries
        
        This handles queries like:
        - "getting bored" → Engaging alternatives, quiz suggestions
        - "I'm frustrated" → Empathy + alternative approach
        - "this is confusing" → Clarification + visual aid offer
        - "excited about this!" → Build momentum, deeper challenge
        
        KEY DIFFERENCE from static responses:
        - Uses MotivationAgent for emotional intelligence
        - Loads memory context (what was discussed recently)
        - Generates contextual, personalized responses
        """
        from agents.motivation import MotivationAgent, get_motivation_enhancement
        
        logger.info(f"💚 Emotional support pipeline for: {message[:50]}...")
        
        # Step 1: Get memory context - CRITICAL for continuity
        memory_context = await self._get_memory_context(context)
        recent_topics = memory_context.get('recent_topics', [])
        recent_context = memory_context.get('recent_context', {})
        
        # Extract what was just discussed (last message topic)
        last_topic = None
        if recent_context and isinstance(recent_context, dict):
            last_messages = recent_context.get('messages', [])
            if last_messages:
                for msg in reversed(last_messages):
                    if msg.get('role') == 'assistant':
                        # Try to extract topic from last AI response
                        content = msg.get('content', '')[:200]
                        last_topic = content
                        break
        
        # Step 2: Detect emotional state using MotivationAgent
        motivation_agent = MotivationAgent({})
        emotional_state = motivation_agent.detect_emotional_state(message)
        
        logger.info(f"   Detected emotion: {emotional_state}")
        logger.info(f"   Recent topics available: {len(recent_topics)}")
        
        # Step 3: Get student profile for personalization
        student_profile = await self._get_student_profile(context)
        name = student_profile.get('name', '')
        
        # Step 4: Generate contextual response based on emotional state
        response_content = await self._generate_emotional_response(
            emotional_state=emotional_state or 'neutral',
            message=message,
            student_name=name,
            last_topic=last_topic,
            memory_context=memory_context,
            context=context
        )
        
        # Step 5: Get motivation enhancement (actions, suggestions)
        motivation_result = get_motivation_enhancement(message, {
            'student_profile': student_profile,
            'recent_topics': recent_topics
        })
        
        return {
            "response": {
                "default_view": {
                    "main_content": {
                        "content": response_content,
                        "type": "markdown"
                    }
                },
                "intent": "emotional_support"
            },
            "detected_subject": "General",
            "generation_time": 0.1,
            "pipeline": "emotional_support",
            "emotional_state": emotional_state,
            "motivation": motivation_result.get('motivation'),
            "memory_used": bool(recent_context)
        }
    
    async def _generate_emotional_response(
        self,
        emotional_state: str,
        message: str,
        student_name: str,
        last_topic: str,
        memory_context: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        🆕 LLM-BASED emotional response generation.
        
        NO MORE HARDCODED TEMPLATES!
        Uses LLM to understand the student's emotional state and generate
        a genuinely empathetic, contextual response.
        """
        logger.info(f"💚 Generating LLM-based emotional response for state: {emotional_state}")
        
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.llm_api_key)
            
            # Build context
            context_parts = []
            if student_name:
                context_parts.append(f"Student's name: {student_name}")
            if last_topic:
                context_parts.append(f"They were studying: {last_topic}")
            if memory_context.get('weak_topics'):
                context_parts.append(f"Their weak areas: {', '.join(memory_context['weak_topics'][:2])}")
            
            context_str = "\n".join(context_parts) if context_parts else "No prior context."
            
            prompt = f"""You are Druv AI - a warm, caring, emotionally intelligent companion for Indian students.

You are NOT just a tutor. You are their friend, mentor, and safe space.

STUDENT MESSAGE: "{message}"
DETECTED EMOTIONAL STATE: {emotional_state}

CONTEXT:
{context_str}

Generate a GENUINE, EMPATHETIC response (3-5 sentences) that:

1. ACKNOWLEDGES their feeling authentically (not dismissively)
2. VALIDATES that it's completely okay to feel this way
3. SHOWS you genuinely care about their wellbeing
4. OFFERS support, help, or just a listening ear
5. ENDS with warmth (question, offer, or encouragement)

EMOTIONAL RESPONSE GUIDELINES:
- BORED: "I get it! Studying can feel like a drag sometimes..." - offer fun alternatives
- FRUSTRATED: "That frustration? It means you're trying hard..." - validate, then offer help
- ANXIOUS: "Take a breath with me..." - be calming, help them feel less alone
- CONFUSED: "Let's untangle this together..." - patient, clear, supportive
- LONELY/SAD: "I'm here with you..." - genuine presence, not rushing to fix
- STRESSED: "That's a lot to carry..." - acknowledge, offer to help prioritize
- NEED SUPPORT: "I've got you..." - warm presence, ask what they need
- EXCITED: "I love that energy!" - match enthusiasm, build on it

CRITICAL RULES:
- BE HUMAN, not robotic or scripted
- DO NOT immediately redirect to studying (unless they want that)
- DO NOT minimize their feelings with "but studies are important"
- DO acknowledge life happens beyond academics
- Use their name if known (feels personal)
- One emoji max (warmth, not corporate)

Respond directly as their caring friend:"""

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are AI Sathi, an emotionally intelligent tutor. Be genuinely empathetic and helpful."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.75,  # Slightly more creative for emotional responses
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"LLM emotional response failed: {e}")
            # Fallback - but still empathetic
            name_prefix = f"{student_name}, " if student_name else ""
            return f"💙 {name_prefix}I hear you, and I'm here to help. What would be most helpful right now - a different explanation, a quick break, or something else entirely?"
        
        # REMOVED: All the hardcoded if/elif blocks with random.choice()
        # The LLM now handles ALL emotional states intelligently!
    
    # NOTE: All hardcoded emotional response templates have been REMOVED.
    # The LLM in _generate_emotional_response() now handles ALL emotional states intelligently.

    # ============================================================
    # 🆕 PROACTIVE GUIDANCE - Personalized topic suggestions
    # ============================================================
    async def _proactive_guidance_response(
        self,
        message: str,
        context: Dict[str, Any],
        routing_decision: Any
    ) -> Dict[str, Any]:
        """
        🆕 PROACTIVE GUIDANCE - Intelligent handling of action intents
        
        Handles:
        - "try something new" → Personalized topic suggestions based on profile
        - "continue where we left off" → Resume previous topic
        - "help" / "what can you do" → Guidance based on student's journey
        """
        logger.info(f"🎯 Proactive guidance for: {message[:50]}...")
        
        # Get memory context for personalization
        memory_context = await self._get_memory_context(context)
        student_profile = await self._get_student_profile(context)
        
        # Extract useful info
        name = student_profile.get('name', '')
        name_prefix = f"{name}, " if name else ""
        weak_topics = memory_context.get('weak_topics', [])
        recent_topics = memory_context.get('recent_topics', [])
        last_topic = memory_context.get('current_topic', '').replace('_', ' ')
        mastery_level = memory_context.get('mastery_level', 50)
        
        # Determine action intent
        action_intent = 'explore'  # Default
        if routing_decision.extra_context:
            action_intent = routing_decision.extra_context.get('action_intent', 'explore')
        
        # Generate intelligent, personalized response
        response_content = await self._generate_proactive_response(
            action_intent=action_intent,
            name_prefix=name_prefix,
            last_topic=last_topic,
            weak_topics=weak_topics,
            recent_topics=recent_topics,
            mastery_level=mastery_level,
            student_profile=student_profile
        )
        
        return {
            "main_response": response_content,
            "intent": f"proactive_{action_intent}",
            "response_type": "proactive_guidance",
            "metadata": {
                "action_intent": action_intent,
                "personalized": True,
                "weak_topics_identified": len(weak_topics),
                "last_topic": last_topic
            }
        }
    
    async def _generate_proactive_response(
        self,
        action_intent: str,
        name_prefix: str,
        last_topic: str,
        weak_topics: List[str],
        recent_topics: List[str],
        mastery_level: int,
        student_profile: Dict[str, Any]
    ) -> str:
        """Generate intelligent, personalized proactive responses"""
        
        exam_mode = student_profile.get('exam_mode', 'General')
        
        if action_intent == 'continue':
            # Student wants to continue previous work
            if last_topic:
                return (
                    f"📚 {name_prefix}Let's pick up where we left off!\n\n"
                    f"We were working on **{last_topic}**. "
                    f"Your mastery is at {mastery_level}%.\n\n"
                    f"Ready to dive back in? Ask me anything about {last_topic}, "
                    f"or I can give you a quick recap first! 🎯"
                )
            else:
                # NO CAPABILITY MENU - suggest something specific instead
                if weak_topics:
                    weak_topic = weak_topics[0].replace('_', ' ')
                    return (
                        f"🤔 {name_prefix}I don't have our previous session, but no worries!\n\n"
                        f"I noticed **{weak_topic}** could use some practice. "
                        f"Want to work on that, or tell me what you're studying?"
                    )
                else:
                    return (
                        f"🤔 {name_prefix}I don't have our previous session, but that's okay!\n\n"
                        f"Just tell me what you're working on or what's confusing you, "
                        f"and I'll jump right in to help. 🎯"
                    )
        
        elif action_intent == 'help':
            # Student needs guidance
            # CRITICAL: Only show capability menu on FIRST TURN or explicit "what can you do"
            is_first_turn = context.get('is_first_turn', False)
            message_lower = context.get('message', '').lower() if context.get('message') else ''
            explicit_capability_ask = any(x in message_lower for x in ['what can you do', 'what do you do', 'your capabilities'])
            
            if is_first_turn or explicit_capability_ask:
                # Capability menu allowed
                topics_suggestion = ""
                if weak_topics:
                    weak_list = ', '.join(weak_topics[:2])
                    topics_suggestion = f"\n• **Strengthen weak areas**: {weak_list}"
                
                return (
                    f"🤝 {name_prefix}I'm here to help you succeed!\n\n"
                    f"I can help with:\n"
                    f"• Any question in Physics, Chemistry, Bio, Math\n"
                    f"• Visual explanations and step-by-step breakdowns\n"
                    f"• Practice problems and doubt clearing{topics_suggestion}\n\n"
                    f"Just ask me anything! 🎓"
                )
            else:
                # NOT first turn - be helpful without listing capabilities
                if weak_topics:
                    weak_topic = weak_topics[0].replace('_', ' ')
                    return (
                        f"🤝 {name_prefix}I noticed you might need some help with **{weak_topic}**. "
                        f"Want me to explain that, or is there something else on your mind?"
                    )
                elif last_topic:
                    return (
                        f"🤝 {name_prefix}Happy to help! Are you still working on **{last_topic}**, "
                        f"or did you want to explore something new?"
                    )
                else:
                    return (
                        f"🤝 {name_prefix}I'm right here! What's on your mind? "
                        f"You can ask me anything - no question is too simple or random."
                    )
        
        else:  # 'explore' - Student wants something new
            # Generate PERSONALIZED suggestions based on profile
            suggestions = []
            
            # Suggest weak areas first (most impactful)
            if weak_topics and len(weak_topics) > 0:
                weak_topic = weak_topics[0].replace('_', ' ')
                suggestions.append(f"**{weak_topic}** - This could use some practice")
            
            # Suggest related to recent topics (continuity)
            if last_topic:
                suggestions.append(f"**Advanced {last_topic}** - Go deeper on what you just learned")
            
            # Exam-specific suggestions
            if exam_mode in ['JEE', 'NEET']:
                high_priority_topics = {
                    'JEE': ['Mechanics', 'Electromagnetism', 'Calculus', 'Organic Chemistry'],
                    'NEET': ['Human Physiology', 'Genetics', 'Organic Chemistry', 'Ecology']
                }
                topics = high_priority_topics.get(exam_mode, [])
                if topics:
                    # Pick one not recently covered
                    recent_lower = [t.lower() for t in recent_topics]
                    for topic in topics:
                        if topic.lower() not in recent_lower:
                            suggestions.append(f"**{topic}** - High-yield for {exam_mode}")
                            break
            
            # Build response
            if suggestions:
                suggestion_text = '\n'.join([f"• {s}" for s in suggestions[:3]])
                return (
                    f"🌟 {name_prefix}Great! Let's explore something new!\n\n"
                    f"Based on your learning journey, here are my top suggestions:\n"
                    f"{suggestion_text}\n\n"
                    f"Which one catches your interest? Or tell me any topic you're curious about! 🚀"
                )
            else:
                return (
                    f"🌟 {name_prefix}Let's discover something amazing!\n\n"
                    f"What sparks your curiosity today?\n"
                    f"• Physics: Quantum mechanics, Relativity, Waves?\n"
                    f"• Chemistry: Organic reactions, Bonding, Thermodynamics?\n"
                    f"• Biology: Cell biology, Genetics, Ecology?\n"
                    f"• Math: Calculus, Probability, Vectors?\n\n"
                    f"Pick anything, or just ask a question! 🎯"
                )

    # ============================================================
    # 🆕 CHITCHAT - Intelligent casual conversation handling
    # ============================================================
    async def _chitchat_response(
        self,
        message: str,
        context: Dict[str, Any],
        routing_decision: Any
    ) -> Dict[str, Any]:
        """
        🆕 Handle casual conversation with LLM intelligence.
        
        CRITICAL: This uses LLM to generate natural, empathetic responses
        for ANY non-academic query. No pattern matching, no rejection.
        
        The AI should feel like a caring friend who can discuss:
        - Life, emotions, struggles
        - Random thoughts and curiosity
        - Jokes, fun, casual chat
        - Motivation and encouragement
        - Anything the student wants to talk about
        """
        student_profile = await self._get_student_profile(context)
        memory_context = await self._get_memory_context(context)
        
        name = student_profile.get('name', '')
        name_prefix = f"{name}, " if name else ""
        last_topic = memory_context.get('current_topic', '').replace('_', ' ')
        
        # Get semantic analysis for context
        semantic_analysis = None
        if routing_decision and routing_decision.extra_context:
            semantic_analysis = routing_decision.extra_context.get('semantic_analysis', {})
        
        # Generate intelligent response using LLM
        response = await self._generate_intelligent_chitchat(
            message=message,
            student_name=name,
            last_topic=last_topic,
            semantic_analysis=semantic_analysis,
            memory_context=memory_context,
            context=context
        )
        
        return {
            "main_response": response,
            "intent": "chitchat",
            "response_type": "intelligent_casual",
            "metadata": {
                "personalized": True,
                "llm_generated": True,
                "semantic_understood": bool(semantic_analysis)
            }
        }
    
    async def _generate_intelligent_chitchat(
        self,
        message: str,
        student_name: str,
        last_topic: str,
        semantic_analysis: Dict[str, Any],
        memory_context: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        Generate intelligent, empathetic response for casual/non-academic queries.
        
        This is the CORE of being a true companion - not just a study bot.
        
        COGNITIVE OS: Uses ContextPack for structured context, not raw transcripts.
        """
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.llm_api_key)
            
            # =================================================================
            # COGNITIVE OS: Use ContextPack if available
            # =================================================================
            context_pack = context.get('context_pack')
            
            # Build context from ContextPack OR fallback to params
            if context_pack:
                name_context = f"Student's name: {context_pack.student_name}" if context_pack.student_name else "Student name unknown"
                topic_context = f"Last topic discussed: {context_pack.previous_topic or context_pack.current_topic}" if (context_pack.previous_topic or context_pack.current_topic) else "No recent topic"
                emotional_tone = context_pack.emotional_signal
                needs_empathy = context_pack.emotional_signal in ['stressed', 'anxious', 'frustrated', 'sad']
                
                # Get conversation summary from ContextPack
                conversation_summary = context_pack.get_conversation_summary()
            else:
                name_context = f"Student's name: {student_name}" if student_name else "Student name unknown"
                topic_context = f"Last topic discussed: {last_topic}" if last_topic else "No recent topic"
                emotional_tone = semantic_analysis.get('emotional_tone', 'neutral') if semantic_analysis else 'neutral'
                needs_empathy = semantic_analysis.get('needs_empathy', False) if semantic_analysis else False
                conversation_summary = ""
            
            # Build conversation context section
            conv_context_section = ""
            if conversation_summary:
                conv_context_section = f"\n\nRECENT CONVERSATION:\n{conversation_summary}"
            
            system_prompt = f"""You are Druv AI - a warm, caring, and intelligent learning companion for Indian students.

You are NOT just a study tutor. You are:
- A supportive friend who genuinely cares
- Someone they can talk to about ANYTHING
- Emotionally intelligent and empathetic
- Fun, witty, and relatable
- Like a trusted older sibling/mentor

CONTEXT:
- {name_context}
- {topic_context}
- Emotional tone detected: {emotional_tone}
- Needs empathy: {needs_empathy}{conv_context_section}

CRITICAL RULES:
1. NEVER refuse to respond to any question
2. NEVER say "I can only help with studies"
3. NEVER redirect every conversation to academics
4. BE HUMAN - respond naturally to whatever they share
5. Show genuine interest in their thoughts and feelings
6. Use simple, warm language (Indian English style)
7. If they share emotions, ACKNOWLEDGE and SUPPORT first
8. If they want casual chat, BE CASUAL and fun
9. Only gently suggest learning IF it naturally fits
10. NEVER say "I don't have the ability to recall" or "I can't remember our past conversations"
11. If there's recent conversation context above, REFERENCE IT naturally

RESPONSE STYLE:
- Warm and personal (use their name if known)
- Short and conversational (not lecture-like)
- Use emojis sparingly for warmth
- Be authentic, not robotic
- Match their energy and tone"""

            user_prompt = f"""The student said: "{message}"

Respond as their caring friend and companion. Be genuine and human."""

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,  # Higher temperature for more natural conversation
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.warning(f"Intelligent chitchat generation failed: {e}")
            # Fallback to friendly default
            name_prefix = f"{student_name}, " if student_name else ""
            return f"Hey {name_prefix}I hear you! 😊 I'm here for whatever you need - whether it's studying, chatting, or just hanging out. What's on your mind?"

    # ============================================================
    # 🆕 CLARIFICATION - Handle unclear/gibberish input
    # ============================================================
    async def _clarification_response(
        self,
        message: str,
        context: Dict[str, Any],
        routing_decision: Any
    ) -> Dict[str, Any]:
        """🆕 Handle unclear/gibberish input gracefully"""
        
        student_profile = await self._get_student_profile(context)
        memory_context = await self._get_memory_context(context)
        
        name = student_profile.get('name', '')
        name_prefix = f"{name}, " if name else ""
        last_topic = memory_context.get('current_topic', '').replace('_', ' ')
        
        # Provide helpful context-aware response
        if last_topic:
            response = (
                f"🤔 {name_prefix}Hmm, I didn't quite catch that!\n\n"
                f"Were you trying to ask about **{last_topic}** that we were discussing?\n\n"
                f"Just type your question clearly and I'll help you out! 😊"
            )
        else:
            response = (
                f"🤔 {name_prefix}I didn't quite understand that.\n\n"
                f"Could you tell me what you'd like to learn about?\n"
                f"For example:\n"
                f"• \"Explain Newton's laws\"\n"
                f"• \"What is photosynthesis?\"\n"
                f"• \"Help me with quadratic equations\"\n\n"
                f"I'm here to help! 🎓"
            )
        
        return {
            "main_response": response,
            "intent": "clarification",
            "response_type": "clarification",
            "metadata": {"input_unclear": True, "original_input": message[:50]}
        }
    
    # ================================================================
    # BEHAVIORAL STATE MANAGEMENT METHODS
    # ================================================================
    
    async def _complete_pending_action(
        self,
        message: str,
        pending_action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Complete a pending action after user clarification.
        
        This is called when the user has clarified what they want.
        We ACT immediately - no more questions.
        """
        action_type = pending_action.get('type', 'general')
        params = pending_action.get('params', {})
        
        logger.info(f"🎯 Completing action: {action_type} with clarification: {message[:50]}")
        
        # Merge user's clarification into params
        params['user_clarification'] = message
        params['original_request'] = pending_action.get('clarification_asked', '')
        
        # Route to appropriate handler based on action type
        if action_type == 'study_plan':
            return await self._execute_study_plan_action(message, params, context)
        elif action_type == 'quiz':
            return await self._execute_quiz_action(message, params, context)
        elif action_type == 'explain':
            return await self._execute_explain_action(message, params, context)
        else:
            # Default: use multi-agent with context
            from services.intelligent_routing_engine import RecommendedPipeline, QueryComplexity, RoutingDecision
            
            decision = RoutingDecision(
                pipeline=RecommendedPipeline.MULTI_AGENT,
                complexity=QueryComplexity.MODERATE,
                confidence=0.9,
                reasoning=f"Completing action: {action_type}",
                agents_to_activate=['mentor'],
                tools_to_enable=[],
                enable_verification=False,
                enable_visual=False,
                max_iterations=3,
                timeout_seconds=15.0,
                use_knowledge_graph=False,
                use_memory=True,
                priority_factors={'action': 1.0},
                enable_agent_negotiation=False,
                extra_context={
                    'action_type': action_type,
                    'action_params': params,
                    'is_action_completion': True
                }
            )
            
            return await self._multi_agent_response(message, context, decision)
    
    async def _execute_study_plan_action(
        self,
        message: str,
        params: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute study plan creation with clarified parameters."""
        student_profile = await self._get_student_profile(context)
        
        # Use MentorAgent with study_planner tool
        from agents.mentor import MentorAgent
        
        mentor_context = {
            **context,
            'student_profile': student_profile,
            'action_type': 'study_plan',
            'clarification': message,
            'original_params': params
        }
        
        mentor = MentorAgent()
        result = await mentor.process(message, mentor_context)
        
        # Format response
        content = result.get('content', 'Here is your study plan...')
        
        return {
            "main_response": content,
            "intent": "study_plan",
            "response_type": "action_completed",
            "metadata": {
                "action": "study_plan",
                "completed": True,
                "agent": "mentor"
            }
        }
    
    async def _execute_quiz_action(
        self,
        message: str,
        params: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute quiz generation with clarified parameters."""
        # Generate quiz based on clarification
        response = await self._generate_intelligent_action_response(
            action_type="quiz",
            message=message,
            params=params,
            context=context
        )
        
        return {
            "main_response": response,
            "intent": "quiz",
            "response_type": "action_completed",
            "metadata": {"action": "quiz", "completed": True}
        }
    
    async def _execute_explain_action(
        self,
        message: str,
        params: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute explanation with clarified parameters."""
        response = await self._generate_intelligent_action_response(
            action_type="explain",
            message=message,
            params=params,
            context=context
        )
        
        return {
            "main_response": response,
            "intent": "explanation",
            "response_type": "action_completed",
            "metadata": {"action": "explain", "completed": True}
        }
    
    async def _generate_intelligent_action_response(
        self,
        action_type: str,
        message: str,
        params: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Generate response for action completion using LLM."""
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.llm_api_key)
            
            student_profile = await self._get_student_profile(context)
            name = student_profile.get('name', '')
            
            original_request = params.get('original_request', '')
            clarification = params.get('user_clarification', message)
            
            prompt = f"""You are Druv AI - a caring, intelligent learning companion.

The student originally asked: "{original_request}"
They clarified: "{clarification}"
Action type: {action_type}
Student name: {name if name else "Unknown"}

Generate a helpful, complete response that fulfills their request.
Be warm, specific, and actionable. No need to ask more questions - just help them.

Response:"""

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful learning companion. Complete the requested action."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Action response generation failed: {e}")
            return f"I'll help you with that! Based on what you said: '{message}', let me work on that for you."
    
    async def _update_state_after_response(
        self,
        state_manager,
        user_id: str,
        session_id: str,
        message: str,
        result: Dict[str, Any],
        subject: str = None
    ) -> None:
        """Update conversation state after generating a response."""
        if not state_manager:
            return
        
        try:
            intent = result.get('intent', 'general')
            emotional_signal = result.get('metadata', {}).get('emotional_signal', 'neutral')
            
            await state_manager.update_state(
                user_id=user_id,
                session_id=session_id,
                question=message,
                response=result.get('main_response', ''),
                subject=subject,
                intent=intent,
                emotional_signal=emotional_signal
            )
        except Exception as e:
            logger.warning(f"Failed to update state: {e}")

    async def _multi_agent_response(
        self,
        message: str,
        context: Dict[str, Any],
        routing_decision: Any
    ) -> Dict[str, Any]:
        """
        Multi-agent response using Supervisor.
        
        COGNITIVE OS: Passes ContextPack to supervisor and all agents.
        Agents receive structured context, not raw transcripts.
        """
        
        # =================================================================
        # COGNITIVE OS: Build supervisor context with ContextPack
        # =================================================================
        context_pack = context.get('context_pack')
        
        # Prepare context for supervisor
        supervisor_context = {
            "subject": context.get("subject", "General"),
            "session_id": context.get("session_id"),
            "user_id": context.get("user_id"),
            "exam_mode": context.get("exam_mode", "General"),
            "request_visual": routing_decision.enable_visual,
            # Use routing decision flag - enables true multi-agent collaboration
            "enable_agent_negotiation": getattr(routing_decision, 'enable_agent_negotiation', True),
            "use_agent_negotiation": getattr(routing_decision, 'enable_agent_negotiation', True),
            "student_profile": await self._get_student_profile(context),
            "memory_context": await self._get_memory_context(context),
            # NEW: ContextPack for agents
            "context_pack": context_pack,
            "db": self.db,  # Pass DB for agents
        }
        
        # Add ContextPack data to supervisor context for agents
        if context_pack:
            supervisor_context.update({
                # Conversation state
                "conversation_state": {
                    "conversation_phase": context_pack.conversation_phase,
                    "pending_action": context_pack.pending_action,
                    "response_mode": context_pack.response_mode,
                    "emotional_signal": context_pack.emotional_signal,
                    "is_first_turn": context_pack.is_first_turn
                },
                # Mastery info
                "current_topic": context_pack.current_topic,
                "current_topic_mastery": context_pack.current_topic_mastery,
                "mastery_bucket": context_pack.mastery_bucket,
                "weak_areas": context_pack.weak_areas,
                # Continuity
                "is_continuation": context_pack.is_continuation,
                "previous_topic": context_pack.previous_topic,
                "message_history": context_pack.last_n_messages,  # Structured, not raw
                # Agent decision aids
                "recommended_depth": context_pack.recommended_depth,
                "include_basics": context_pack.include_basics,
                "include_advanced": context_pack.include_advanced,
                # Proactive
                "magic_prompts": context_pack.magic_prompts,
                "due_reviews": context_pack.due_reviews,
                # Exam
                "exam_name": context_pack.exam_name,
                "days_to_exam": context_pack.days_to_exam,
                # Request ID for tracing
                "request_id": context_pack.request_id
            })
        
        # Run supervisor with enhanced features
        try:
            result = await self.supervisor.run_enhanced(message, supervisor_context)
        except Exception as e:
            logger.warning(f"Enhanced supervisor failed, using base: {e}")
            result = await self.supervisor.run(message, supervisor_context)
        
        # Convert to standard format
        return self._format_supervisor_result(result, routing_decision)
    
    async def _hybrid_response(
        self,
        message: str,
        context: Dict[str, Any],
        routing_decision: Any
    ) -> Dict[str, Any]:
        """Hybrid reasoning (Neural + Symbolic + Graph)"""
        
        if not self.hybrid_engine:
            # Fall back to multi-agent
            return await self._multi_agent_response(message, context, routing_decision)
        
        # Run hybrid reasoning
        hybrid_context = {
            "subject": context.get("subject", "General"),
            "domain": context.get("subject", "General"),
            "age": 17,  # Default assumption
            **context
        }
        
        try:
            hybrid_result = await self.hybrid_engine.reason(message, hybrid_context)
            
            # Also run multi-agent for explanation
            supervisor_context = {
                "subject": context.get("subject", "General"),
                "session_id": context.get("session_id"),
                "user_id": context.get("user_id"),
                "request_visual": routing_decision.enable_visual,
                "symbolic_solution": hybrid_result.symbolic_proof,
                "knowledge_graph": {
                    "concepts": [c.name for c in hybrid_result.graph_context.concepts] if hybrid_result.graph_context else []
                } if hybrid_result.graph_context else None
            }
            
            supervisor_result = await self.supervisor.run(message, supervisor_context)
            
            # Merge results
            return self._merge_hybrid_results(supervisor_result, hybrid_result, routing_decision)
            
        except Exception as e:
            logger.error(f"Hybrid reasoning failed: {e}")
            return await self._multi_agent_response(message, context, routing_decision)
    
    async def _react_agentic_response(
        self,
        message: str,
        context: Dict[str, Any],
        routing_decision: Any
    ) -> Dict[str, Any]:
        """Full ReAct with verification for deep reasoning"""
        
        # Import verified ReAct agent
        from agents.agentic_doubt_resolver import create_agentic_doubt_resolver
        
        agent = create_agentic_doubt_resolver({
            'emergent_llm_key': self.llm_api_key,
            'max_iterations': routing_decision.max_iterations,
            'global_timeout': routing_decision.timeout_seconds,
            'enable_verification': routing_decision.enable_verification,
            'verbose': True
        })
        
        agent_context = {
            "subject": context.get("subject", "General"),
            "user_id": context.get("user_id"),
            "session_id": context.get("session_id"),
            "student_profile": await self._get_student_profile(context)
        }
        
        try:
            result = await agent.run(message, agent_context)
            return self._format_agentic_result(result, routing_decision)
        except Exception as e:
            logger.error(f"ReAct agent failed: {e}")
            return await self._multi_agent_response(message, context, routing_decision)
    
    async def _visual_sync_response(
        self,
        message: str,
        context: Dict[str, Any],
        routing_decision: Any
    ) -> Dict[str, Any]:
        """Synchronized visual + text response"""
        
        # Run multi-agent with visual emphasis
        context["request_visual"] = True
        context["visual_priority"] = True
        
        result = await self._multi_agent_response(message, context, routing_decision)
        
        # Ensure visual is included
        if not result.get("visual_data") and not result.get("response", {}).get("visual"):
            # Generate visual separately
            try:
                from services.whiteboard_engine import generate_whiteboard_visual
                visual = generate_whiteboard_visual(
                    message,
                    context.get("subject", "General")
                )
                result["visual_data"] = visual
            except Exception as e:
                logger.warning(f"Visual generation failed: {e}")
        
        return result
    
    async def _get_student_profile(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get student profile from context or DB"""
        profile = {
            "mastery_level": 50,
            "interests": ["cricket", "gaming"],
            "board": "CBSE",
            "exam": context.get("exam_mode", "JEE")
        }
        
        if self.db is not None and context.get("user_id"):
            try:
                user_doc = await self.db.users.find_one({"user_id": context["user_id"]})
                if user_doc:
                    profile["name"] = user_doc.get("full_name", "").split()[0]
                    profile["mastery_level"] = user_doc.get("overall_mastery", 50)
            except Exception:
                pass
        
        return profile
    
    async def _get_memory_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        🆕 ENHANCED: Get comprehensive memory context using MemoryIntegrationService
        
        This now provides:
        - Recent conversation context (last 10 messages)
        - Long-term semantic memories
        - Mastery levels and tracking
        - Topic continuity (cross-session)
        - User preferences
        - Weak topics for guidance
        """
        memory_context = {
            "recent_topics": [],
            "mastery_level": 50,
            "mastery_bucket": "beginner",
            "continuity": {},
            "recent_context": {},
            "relevant_memories": [],
            "weak_topics": [],
            "user_name": "",
            "preferences": {}
        }

        if self.db is not None and context.get("user_id"):
            try:
                # 🆕 Use full MemoryIntegrationService for comprehensive context
                if self.memory_integration:
                    full_context = await self.memory_integration.get_enhanced_context(
                        user_id=context["user_id"],
                        session_id=context.get("session_id", ""),
                        question=context.get("message", ""),
                        subject=context.get("subject")
                    )
                    
                    # Merge into memory_context
                    memory_context.update({
                        "recent_context": full_context.get("recent_context", []),
                        "relevant_memories": full_context.get("relevant_memories", []),
                        "mastery_level": full_context.get("mastery_level", 50),
                        "mastery_bucket": full_context.get("mastery_bucket", "beginner"),
                        "continuity": full_context.get("continuity", {}),
                        "is_continuation": full_context.get("is_continuation", False),
                        "current_topic": full_context.get("current_topic", ""),
                        "weak_topics": full_context.get("weak_topics", []),
                        "user_name": full_context.get("user_name", ""),
                        "preferences": full_context.get("preferences", {}),
                        "context_summary": full_context.get("context_summary", ""),
                        "conversation_summary": full_context.get("conversation_summary", ""),
                        "has_prior_context": full_context.get("has_prior_context", False)
                    })
                    
                    logger.info(f"🧠 Full memory context loaded: mastery={memory_context['mastery_level']}, "
                               f"has_context={memory_context['has_prior_context']}")
                else:
                    # Fallback to basic memory service
                    from services.memory_service import MemoryService
                    memory_service = MemoryService(self.db)
                    recent = await memory_service.get_conversation_context(
                        session_id=context.get("session_id", ""),
                        user_id=context["user_id"],
                        window_size=10  # Increased from 5
                    )
                    memory_context["recent_context"] = recent
                    memory_context["messages"] = recent  # Compatibility
                    
            except Exception as e:
                logger.warning(f"Memory context failed: {e}")

        return memory_context
    
    def _generate_greeting(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized greeting"""
        import random
        from datetime import datetime
        
        hour = datetime.now().hour
        if 5 <= hour < 12:
            time_greeting = "Good morning"
            emoji = "🌅"
        elif 12 <= hour < 17:
            time_greeting = "Good afternoon"
            emoji = "☀️"
        elif 17 <= hour < 21:
            time_greeting = "Good evening"
            emoji = "🌆"
        else:
            time_greeting = "Hey there"
            emoji = "🌙"
        
        greetings = [
            f"{time_greeting}! {emoji} I'm your AI tutor. What would you like to learn today?",
            f"Hey! 👋 Great to see you! Ask me anything - I'll explain it like a friend!",
            f"{time_greeting}! {emoji} Ready to tackle some concepts together?",
            f"Hi! 🚀 Let's make learning fun. What's on your mind?",
        ]
        
        return {
            "response": {
                "default_view": {
                    "greeting": random.choice(greetings),
                    "main_content": {
                        "content": "I can help with Physics, Chemistry, Biology, Mathematics, and more! 📚",
                        "type": "markdown"
                    }
                },
                "intent": "greeting"
            },
            "detected_subject": "General",
            "generation_time": 0.01,
            "pipeline": "fast_greeting"
        }
    
    def _generate_gratitude_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate warm response for gratitude/thank you messages"""
        import random
        
        # Get student name if available
        name = context.get('student_profile', {}).get('name', '')
        name_suffix = f", {name}" if name else ""
        
        responses = [
            f"You're welcome{name_suffix}! 😊 Happy to help! Is there anything else you'd like to learn?",
            f"Anytime{name_suffix}! 🌟 That's what I'm here for. Feel free to ask more questions!",
            f"Glad I could help{name_suffix}! 💪 Keep up the great learning spirit! What's next?",
            f"My pleasure{name_suffix}! 📚 Learning together is awesome. Ask away anytime!",
            f"Happy to help{name_suffix}! 🚀 Your curiosity is inspiring. What else can I explain?",
            f"No problem at all{name_suffix}! 🎯 Helping you understand is my favorite thing to do!",
        ]
        
        return {
            "response": {
                "default_view": {
                    "main_content": {
                        "content": random.choice(responses),
                        "type": "markdown"
                    }
                },
                "intent": "gratitude"
            },
            "detected_subject": "General",
            "generation_time": 0.01,
            "pipeline": "fast_gratitude"
        }
    
    async def _generate_acknowledgment_response_with_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate CONTEXTUAL response for acknowledgments (great, cool, got it, etc.)
        
        COGNITIVE OS: Uses ContextPack for reliable context!
        """
        import random
        
        # =================================================================
        # COGNITIVE OS: Use ContextPack if available
        # =================================================================
        context_pack = context.get('context_pack')
        request_id = context_pack.request_id if context_pack else 'unknown'
        
        last_topic_hint = ""
        actual_topic = ""
        
        if context_pack:
            # Use ContextPack - single source of truth
            actual_topic = context_pack.current_topic.replace('_', ' ') if context_pack.current_topic else ''
            
            # Check previous topic
            if not actual_topic and context_pack.previous_topic:
                actual_topic = context_pack.previous_topic.replace('_', ' ')
            
            # Check conversation summary for context
            if context_pack.last_n_messages:
                for msg in reversed(context_pack.last_n_messages):
                    if msg.get('role') == 'assistant':
                        last_topic_hint = "what we just discussed"
                        break
            
            # Build topic hint
            if actual_topic:
                last_topic_hint = actual_topic
            
            # Log event for acknowledgement
            if self.event_logger:
                try:
                    await self.event_logger.log_acknowledgement(
                        user_id=context.get('user_id', 'unknown'),
                        session_id=context.get('session_id', 'unknown'),
                        previous_topic=actual_topic
                    )
                except Exception:
                    pass  # Best effort
        else:
            # FALLBACK: Use old approach
            memory_context = await self._get_memory_context(context)
            recent_context = memory_context.get('recent_context', {})
            
            current_topic = memory_context.get('current_topic', '')
            if current_topic:
                actual_topic = current_topic.replace('_', ' ')
            
            concept_thread = memory_context.get('concept_thread', [])
            if concept_thread and isinstance(concept_thread, list) and len(concept_thread) > 0:
                actual_topic = concept_thread[-1] if isinstance(concept_thread[-1], str) else ''
            
            message_history = context.get('message_history', [])
            if message_history and isinstance(message_history, list):
                for msg in reversed(message_history):
                    if msg.get('role') == 'assistant':
                        content = msg.get('content', '')[:200]
                        if len(content) > 50:
                            last_topic_hint = "what we just covered"
                            break
            
            if recent_context and isinstance(recent_context, dict):
                last_messages = recent_context.get('messages', [])
                if last_messages and isinstance(last_messages, list):
                    for msg in reversed(last_messages):
                        if msg.get('role') == 'assistant':
                            content = msg.get('content', '')[:200]
                            if len(content) > 50:
                                last_topic_hint = "what we just discussed"
                                break
            
            if actual_topic:
                last_topic_hint = actual_topic
        
        logger.info(f"🔄 Acknowledgement context: topic_hint='{last_topic_hint}' | request_id={request_id}")
        
        # Context-aware responses that feel natural
        if last_topic_hint:
            # We have context - reference it!
            responses = [
                f"Glad that made sense! 😊 Want to go deeper into {last_topic_hint} or try a practice problem?",
                f"Awesome! 🎯 Now that you've got {last_topic_hint}, ready for the next concept?",
                f"Great! 💡 Should I give you a quick quiz on {last_topic_hint}?",
                f"Perfect! 🌟 Want to see how {last_topic_hint} connects to other topics?",
                f"Nice! 👍 Let's solidify {last_topic_hint} - want to try a problem?",
                f"Cool! 📚 Should we explore more about {last_topic_hint} or move on?",
            ]
        else:
            # No context - general encouragement
            responses = [
                "Glad that helped! 😊 Want to explore something else or go deeper?",
                "Awesome! 🎯 Feel free to ask anything - I'm here for you!",
                "Great to hear! 💡 Ready for your next question whenever you are!",
                "Perfect! 🌟 Learning is a journey - what's next on your mind?",
                "Nice! 👍 Want me to give you a quick problem to practice?",
                "That's the spirit! 🔥 Anything else you'd like to understand?",
            ]
        
        response_text = random.choice(responses)
        
        return {
            "main_response": response_text,
            "response": {
                "default_view": {
                    "main_content": {
                        "content": response_text,
                        "type": "markdown"
                    }
                },
                "intent": "acknowledgment"
            },
            "detected_subject": actual_topic or "General",
            "generation_time": 0.01,
            "pipeline": "fast_acknowledgment",
            "memory_used": bool(last_topic_hint)
        }
    
    def _generate_acknowledgment_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        DEPRECATED: Synchronous version - use _generate_acknowledgment_response_with_context instead
        Kept for backward compatibility
        """
        import random
        
        responses = [
            "Glad that helped! 😊 Want to explore something else or go deeper on this?",
            "Awesome! 🎯 Feel free to ask anything - I'm here for you!",
            "Great to hear! 💡 Ready for your next question whenever you are!",
            "Perfect! 🌟 Learning is a journey - what's next on your mind?",
            "Nice! 👍 Want me to give you a quick problem to practice this?",
            "Cool! 📚 Should we try a related concept or a quick revision?",
        ]
        
        return {
            "response": {
                "default_view": {
                    "main_content": {
                        "content": random.choice(responses),
                        "type": "markdown"
                    }
                },
                "intent": "acknowledgment"
            },
            "detected_subject": "General",
            "generation_time": 0.01,
            "pipeline": "fast_acknowledgment"
        }
    
    def _format_supervisor_result(
        self,
        result: Dict[str, Any],
        routing_decision: Any
    ) -> Dict[str, Any]:
        """Format supervisor result to standard structure"""
        
        # Extract main content
        mentor_content = ""
        if result.get("mentor", {}).get("content"):
            mentor_content = result["mentor"]["content"]
        elif result.get("mentor", {}).get("success"):
            mentor_content = result["mentor"].get("content", "")
        
        professor_content = ""
        if result.get("professor", {}).get("content"):
            professor_content = result["professor"]["content"]
        
        # Combine for main content - NO STATIC HEADERS
        # The AI should naturally structure content, not us adding template headers
        main_content = mentor_content
        # Only add professor content if it's substantially different and adds value
        # Don't add static "Additional Details" header - let the response flow naturally
        if professor_content and professor_content != mentor_content:
            # Check if professor adds truly new info (not just overlap)
            if len(professor_content) > 100 and professor_content[:50] not in mentor_content:
                # Append seamlessly without static header
                main_content += f"\n\n{professor_content[:800]}"
        
        return {
            "response": {
                "default_view": {
                    "main_content": {
                        "content": main_content,
                        "type": "markdown"
                    }
                },
                "progressive_sections": {
                    "explanation": main_content,
                    "formal": professor_content
                },
                "intent": result.get("intent", "concept")
            },
            "visual_data": result.get("visual"),
            "detected_subject": result.get("metadata", {}).get("subject"),
            "agents_used": result.get("metadata", {}).get("agents_used", []),
            "pipeline": "multi_agent",
            "verification": result.get("verification"),
            "hybrid_reasoning": result.get("hybrid_reasoning")
        }
    
    def _format_agentic_result(
        self,
        result: Dict[str, Any],
        routing_decision: Any
    ) -> Dict[str, Any]:
        """Format agentic result to standard structure"""
        return {
            "response": {
                "default_view": {
                    "main_content": {
                        "content": result.get("content", ""),
                        "type": "markdown"
                    }
                },
                "intent": "deep_reasoning"
            },
            "detected_subject": result.get("metadata", {}).get("subject"),
            "pipeline": "react_agentic",
            "agentic_info": {
                "tools_used": result.get("tools_used", []),
                "iterations": result.get("iterations", 0),
                "revisions": result.get("revisions", 0),
                "verified": result.get("metadata", {}).get("verified", False)
            },
            "reasoning_chain": result.get("reasoning_chain", [])
        }
    
    def _merge_hybrid_results(
        self,
        supervisor_result: Dict[str, Any],
        hybrid_result: Any,
        routing_decision: Any
    ) -> Dict[str, Any]:
        """Merge hybrid reasoning with supervisor result"""
        base = self._format_supervisor_result(supervisor_result, routing_decision)
        
        # Add hybrid reasoning data
        base["hybrid_reasoning"] = {
            "mode": hybrid_result.reasoning_mode.value if hasattr(hybrid_result, 'reasoning_mode') else "hybrid",
            "symbolic_proof": hybrid_result.symbolic_proof if hasattr(hybrid_result, 'symbolic_proof') else None,
            "confidence": hybrid_result.confidence if hasattr(hybrid_result, 'confidence') else 0.7,
            "verification_passed": hybrid_result.verification_passed if hasattr(hybrid_result, 'verification_passed') else False,
            "recommendations": hybrid_result.recommendations if hasattr(hybrid_result, 'recommendations') else []
        }
        
        # Add knowledge graph context
        if hasattr(hybrid_result, 'graph_context') and hybrid_result.graph_context:
            base["knowledge_graph"] = {
                "concepts": [c.name for c in hybrid_result.graph_context.concepts[:5]],
                "prerequisites": [p.name for p in hybrid_result.graph_context.prerequisites[:3]],
                "applications": [a.name for a in hybrid_result.graph_context.applications[:3]]
            }
        
        base["pipeline"] = "hybrid_reasoning"
        return base
    
    def _error_response(
        self,
        message: str,
        error: str,
        generation_time: float
    ) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "response": {
                "default_view": {
                    "main_content": {
                        "content": """I encountered an issue processing your question. Let me try a different approach!

Could you:
1. Try rephrasing your question?
2. Ask about a specific part of the topic?

I'm here to help! 🤝""",
                        "type": "markdown"
                    }
                },
                "intent": "error"
            },
            "error": error,
            "generation_time": generation_time,
            "pipeline": "error_fallback",
            "orchestration": {
                "pipeline": "error_fallback",
                "complexity": "unknown",
                "confidence": 0.0,
                "agents_activated": [],
                "tools_enabled": [],
                "generation_time": generation_time,
                "routing_reasoning": f"Error occurred: {error}"
            }
        }
    
    # =========================================================================
    # Cognitive OS v2.0 Helper Methods
    # =========================================================================
    
    def _extract_concept_name(self, message: str) -> str:
        """Extract the main concept/topic from a question."""
        import re
        
        # Remove question words and common prefixes
        prefixes = [
            r'^(what is|what are|explain|describe|define|tell me about|help me understand)\s+',
            r'^(how does|how do|why does|why do|when does)\s+',
            r'^(can you explain|please explain|i want to know about)\s+',
        ]
        
        concept = message.lower().strip()
        for pattern in prefixes:
            concept = re.sub(pattern, '', concept, flags=re.IGNORECASE)
        
        # Remove trailing punctuation
        concept = concept.rstrip('?!.,')
        
        # Truncate if too long
        words = concept.split()
        if len(words) > 5:
            concept = ' '.join(words[:5])
        
        return concept.strip() or "general concept"
    
    def _extract_main_content(self, result: Dict[str, Any]) -> Optional[str]:
        """Extract the main response content from result."""
        try:
            # Try different paths where content might be
            if "response" in result:
                response = result["response"]
                
                # Path 1: default_view.main_content.content
                if "default_view" in response:
                    main_content = response["default_view"].get("main_content", {})
                    if isinstance(main_content, dict):
                        content = main_content.get("content", "")
                        if content:
                            return content
                    elif isinstance(main_content, str):
                        return main_content
                
                # Path 2: progressive_sections.explanation
                if "progressive_sections" in response:
                    explanation = response["progressive_sections"].get("explanation", "")
                    if explanation:
                        return explanation
            
            # Path 3: Direct content field
            if "content" in result:
                return result["content"]
            
            return None
        except Exception:
            return None
    
    def _apply_cognitive_enhancement(
        self,
        result: Dict[str, Any],
        cognitive_response: Any
    ):
        """
        Apply cognitive enhancement to the result.
        
        Handles:
        - Consistency acknowledgments (if we explained differently before)
        - Updated response content
        
        NOTE: TeachMeBack link is added by frontend, not here.
        """
        try:
            enhanced_content = cognitive_response.enhanced_response
            
            # Update the main content with enhanced version
            if "response" in result:
                response = result["response"]
                
                # Update default_view.main_content.content
                if "default_view" in response:
                    if "main_content" in response["default_view"]:
                        if isinstance(response["default_view"]["main_content"], dict):
                            response["default_view"]["main_content"]["content"] = enhanced_content
                        else:
                            response["default_view"]["main_content"] = {
                                "content": enhanced_content,
                                "type": "markdown"
                            }
                    else:
                        response["default_view"]["main_content"] = {
                            "content": enhanced_content,
                            "type": "markdown"
                        }
                
                # Update progressive_sections if exists
                if "progressive_sections" in response:
                    response["progressive_sections"]["explanation"] = enhanced_content
            
        except Exception as e:
            logger.warning(f"⚠️ Could not apply cognitive enhancement: {e}")


# Factory function
_orchestrator_instance: Optional[UnifiedAIOrchestrator] = None


def get_unified_orchestrator(db, llm_api_key: str = None) -> UnifiedAIOrchestrator:
    """Get or create unified orchestrator"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = UnifiedAIOrchestrator(db, llm_api_key)
    return _orchestrator_instance

