"""
🧠 Intelligent Routing Engine - The Brain of AI Sathi
======================================================

REPLACES: USE_UNIFIED_FIRST = True (the flawed default)

This engine makes INTELLIGENT decisions about which pipeline to use:
- Simple queries → Fast ResponseComposer
- Complex/Educational → Multi-Agent Supervisor
- Deep Reasoning → ReAct with Tools
- Visual → Synchronized Visual+Text Pipeline

NO MORE bypassing multi-agent flow by default!
"""

import logging
import re
from typing import Dict, Any, Tuple, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class QueryComplexity(Enum):
    """Query complexity levels"""
    TRIVIAL = "trivial"           # "hi", "thanks" - instant response
    SIMPLE = "simple"             # Quick factual lookups
    MODERATE = "moderate"         # Standard explanations
    COMPLEX = "complex"           # Multi-step reasoning
    DEEP_REASONING = "deep"       # Proofs, derivations, analysis


class RecommendedPipeline(Enum):
    """Which pipeline should handle this query"""
    FAST_RESPONSE = "fast"               # ResponseComposer only
    EMOTIONAL_SUPPORT = "emotional"      # MotivationAgent + contextual response
    PROACTIVE_GUIDANCE = "proactive"     # 🆕 Personalized topic suggestions (explore, continue, help)
    CHITCHAT = "chitchat"                # 🆕 Casual conversation, humor
    CLARIFICATION = "clarification"      # 🆕 Gibberish/unclear input - ask for clarification
    MULTI_AGENT = "multi_agent"          # Supervisor orchestration
    REACT_AGENTIC = "react_agentic"      # Full ReAct with tools
    HYBRID_REASONING = "hybrid"          # Neural + Symbolic + Graph
    VISUAL_SYNC = "visual_sync"          # Text + Visual synchronized


@dataclass
class RoutingDecision:
    """Complete routing decision with reasoning"""
    pipeline: RecommendedPipeline
    complexity: QueryComplexity
    confidence: float
    reasoning: str
    agents_to_activate: List[str]
    tools_to_enable: List[str]
    enable_verification: bool
    enable_visual: bool
    max_iterations: int
    timeout_seconds: float
    use_knowledge_graph: bool
    use_memory: bool
    priority_factors: Dict[str, float]
    # Enable agent negotiation (cross-verification, consensus building)
    enable_agent_negotiation: bool = False
    # 🆕 Extra context for specific pipelines (e.g., action_intent type)
    extra_context: Dict[str, Any] = None
    # 🆕 GAP 2: Model selection criteria (NOT the model itself)
    # Model is selected at EXECUTION TIME by SemanticModelSelector
    model_selection_criteria: Dict[str, Any] = None


class IntelligentRoutingEngine:
    """
    Makes intelligent routing decisions based on query analysis.
    
    PRINCIPLES:
    1. Default to MULTI-AGENT for educational queries (not single LLM)
    2. Use complexity analysis, not keyword matching
    3. Consider student context (mastery, history)
    4. Adapt dynamically based on confidence
    """
    
    # Complexity indicators with weights
    COMPLEXITY_PATTERNS = {
        # High complexity indicators
        'prove': 0.8,
        'derive': 0.8,
        'derivation': 0.8,
        'proof': 0.8,
        'why does': 0.7,
        'how does': 0.6,
        'explain the mechanism': 0.8,
        'step by step': 0.7,
        'compare and contrast': 0.7,
        'analyze': 0.7,
        'evaluate': 0.7,
        'solve': 0.6,
        'calculate': 0.5,
        
        # Moderate complexity
        'explain': 0.5,
        'what is': 0.4,
        'define': 0.3,
        'describe': 0.4,
        'difference between': 0.6,
        
        # Low complexity
        'who is': 0.2,
        'when did': 0.2,
        'where is': 0.2,
    }
    
    # Subject-based complexity multipliers
    SUBJECT_MULTIPLIERS = {
        'physics': 1.3,
        'mathematics': 1.4,
        'chemistry': 1.2,
        'biology': 1.1,
        'general': 1.0,
    }
    
    # Trivial patterns (instant response) - COMPREHENSIVE list
    # CRITICAL: These must ALWAYS get a response - never go unanswered
    TRIVIAL_PATTERNS = [
        # Greetings
        r'^(hi|hello|hey|namaste|yo|sup|hola)[\s!?.]*$',
        # Thanks
        r'^(thanks?|thank you|thx|ty|tysm|appreciate)[\s!?.]*$',
        # Farewells
        r'^(bye|goodbye|see you|later|cya)[\s!?.]*$',
        # Yes/No
        r'^(ok|okay|k|sure|yes|yeah|yep|yup|no|nope|nah)[\s!?.]*$',
        # Affirmations - CRITICAL: Students naturally say these
        r'^(good|great|nice|cool|awesome|perfect|amazing|excellent|brilliant|fantastic|wonderful|superb|love it)[\s!?.]*$',
        # Understanding confirmations
        r'^(got it|understood|i see|makes sense|clear|i understand|that helps|helpful)[\s!?.]*$',
        # Short reactions
        r'^(wow|whoa|oh|ah|hmm|hm|ooh|aha|aah)[\s!?.]*$',
        # Emojis (text representation)
        r'^[👍👏🙏❤️🔥💯✅😊🎉👌🤝💪]+[\s!?.]*$',
    ]
    
    # 🆕 EMOTIONAL PATTERNS - Detect mood/emotional states that need intelligent handling
    # These are NOT trivial - they need empathetic, context-aware responses
    EMOTIONAL_PATTERNS = {
        'bored': [
            r'(getting |feeling |i\'?m |so |really )?(bored|boring)',
            r'(this is |it\'?s )?(boring|dull|tedious)',
            r'(not |don\'?t feel )?(interested|engaged|motivated)',
            r'(can\'?t |don\'?t want to )?(focus|concentrate|study)',
            r'(tired of|fed up|sick of) (this|studying|learning)',
            r'(want to|wanna) (do something else|change|switch)',
            r'(sleepy|drowsy|tired)',
        ],
        'frustrated': [
            r'(i\'?m |feeling |getting |so )?(frustrated|stuck|confused)',
            r'(this is |it\'?s )?(hard|difficult|impossible|confusing)',
            r'(i |can\'?t |don\'?t )?(understand|get it|figure)',
            r'(hate|stupid|dumb|useless)',
            r'(give up|quit|stop|enough)',
            r'(failing|failed|wrong again)',
            r'(not working|doesn\'?t make sense)',
        ],
        'anxious': [
            r'(i\'?m |feeling )?(worried|anxious|nervous|scared|stressed)',
            r'(exam|test|assessment) (stress|anxiety|pressure|fear)',
            r'(panic|panicking|overwhelmed)',
            r'(too much|can\'?t handle|too hard)',
            r'(what if|afraid|fear)',
        ],
        'excited': [
            r'(this is |it\'?s )?(exciting|interesting|cool|amazing|awesome)',
            r'(love|loving|enjoy|enjoying) (this|it|learning)',
            r'(want to|wanna) (learn more|know more|explore)',
            r'(really |so )?(curious|interested|fascinated)',
        ],
        'confused': [
            r'(i\'?m |feeling |still )?(confused|lost|unsure)',
            r'(don\'?t|doesn\'?t) (get|understand|make sense)',
            r'(what do you mean|explain again|say that again)',
            r'(huh|wait what|come again)',
        ],
        'success': [
            r'(i |finally )?(got it|understand|figured)',
            r'(makes sense|clicked|clear now)',
            r'(aha|eureka|oh i see)',
            r'(that was|this is) (helpful|useful|great)',
        ],
        # 🆕 ACTION INTENTS - Student wants to DO something (explore, start, learn)
        'explore': [
            r'(try|start|show|teach|give) (something|me something) (new|else|different)',
            r'(what|which) (should i|can i|to) (learn|study|do|try)',
            r'(suggest|recommend) (a |some )?(topic|subject|concept)',
            r'(new|different|another) (topic|subject|concept|thing)',
            r'(let\'?s|i want to|wanna) (start|try|learn|explore|do) (something)?',
            r'(what\'?s next|next topic|move on|continue)',
            r'(show me|tell me) (what|something) (interesting|cool|new)',
            r'(i\'?m ready|ready to|prepared) (for|to) (learn|start|go)',
            r'(pick|choose|select) (a |for me|something)',
            r'(anything|everything) (new|else|interesting)',
            r'^(new topic|next|continue|proceed|go ahead)[\s!?.]*$',
        ],
        # 🆕 CONTINUATION INTENTS - Student wants to continue previous work
        'continue': [
            r'(continue|resume|pick up) (where|from)',
            r'(where|what) (were|was|did) (we|i)',
            r'(last|previous) (topic|session|time)',
            r'(back to|return to|go back)',
            r'^(continue|resume|back)[\s!?.]*$',
        ],
        # 🆕 CHITCHAT - Casual conversation, jokes, etc.
        'chitchat': [
            r'^(how are you|what\'?s up|whats up|wassup|sup)[\s!?.]*$',
            r'(tell me|say) (a joke|something funny)',
            r'(who are you|what are you|introduce yourself)',
            r'(your name|what\'?s your name)',
            r'^(lol|haha|hehe|rofl|lmao)[\s!?.]*$',
        ],
        # 🆕 HELP/GUIDANCE - Student needs direction
        'help': [
            r'^(help|help me|i need help)[\s!?.]*$',
            r'(what can you do|how (can|do) you help)',
            r'(i\'?m lost|don\'?t know (what|where))',
            r'(guide me|show me how)',
        ]
    }
    
    # Compile emotional patterns for performance
    _compiled_emotional = None
    
    def __init__(self, db=None):
        """Initialize routing engine"""
        self.db = db
        self._compiled_trivial = [re.compile(p, re.IGNORECASE) for p in self.TRIVIAL_PATTERNS]
        
        # Compile emotional patterns
        self._compiled_emotional = {}
        for emotion, patterns in self.EMOTIONAL_PATTERNS.items():
            self._compiled_emotional[emotion] = [re.compile(p, re.IGNORECASE) for p in patterns]
        
        logger.info("🧠 IntelligentRoutingEngine initialized - Smart routing active")
        logger.info("   ├── Emotional pattern detection ENABLED (bored, frustrated, anxious, etc.)")
    
    async def route(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> RoutingDecision:
        """
        Make intelligent routing decision for a query.
        
        🆕 NOW USES LLM-BASED SEMANTIC CLASSIFICATION!
        No more brittle pattern matching for primary routing.
        
        CRITICAL BEHAVIORAL RULES:
        1. Check conversation state FIRST - state can override classifier
        2. If pending_action exists → complete it, don't re-classify
        3. Clarification detected → increase confidence, act immediately
        4. Intent classifier is ONE signal, not the final decision
        
        Args:
            query: The student's question
            context: Context including subject, user_id, mastery, etc.
            
        Returns:
            RoutingDecision with complete pipeline configuration
        """
        logger.info(f"🧠 Routing query: {query[:60]}...")
        
        # ============================================================
        # STEP 0: DIALOGUE-ACT DETECTION (Message Characteristics + State)
        # ============================================================
        # 🎯 TRI-LANE: Detect dialogue acts based on message structure,
        # NOT keywords. This ensures short/continuation messages route
        # to Conversation Lane, not Education Lane.
        
        conversation_state = context.get('conversation_state', {})
        dialogue_act = self._detect_dialogue_act(query, conversation_state)
        
        if dialogue_act:
            logger.info(f"💬 Dialogue Act Detected: {dialogue_act['act']} → {dialogue_act['lane']}")
            
            if dialogue_act['lane'] == 'conversation':
                # Route to appropriate conversation pipeline
                if dialogue_act['act'] in ['ack', 'continue', 'short_response']:
                    # Acknowledgment or continuation - use proactive guidance
                    # PHASE C FIX: Include last task info for proper continuation
                    last_output_type = context.get('last_output_type', '') or context.get('context_pack', {}).get('last_output_type', '')
                    last_task_type = context.get('last_task_type', '') or context.get('context_pack', {}).get('last_task_type', '')
                    last_assistant_message = context.get('last_assistant_message', '') or context.get('context_pack', {}).get('last_assistant_message', '')
                    awaiting_continuation = context.get('awaiting_continuation', False) or context.get('context_pack', {}).get('awaiting_continuation', False)
                    
                    return RoutingDecision(
                        pipeline=RecommendedPipeline.PROACTIVE_GUIDANCE,
                        complexity=QueryComplexity.SIMPLE,
                        confidence=0.9,
                        reasoning=f"Dialogue act: {dialogue_act['act']} - continuing conversation (last_output={last_output_type})",
                        agents_to_activate=['mentor'],
                        tools_to_enable=[],
                        enable_verification=False,
                        enable_visual=False,
                        max_iterations=2,
                        timeout_seconds=10.0,
                        use_knowledge_graph=False,
                        use_memory=True,
                        priority_factors={'continuity': 1.0},
                        enable_agent_negotiation=False,
                        extra_context={
                            'dialogue_act': dialogue_act['act'],
                            'action_intent': 'continue',  # CRITICAL: Must be 'continue', not 'explore'
                            'is_continuation': True,
                            # PHASE C: Pass last task info for proper continuation
                            'last_output_type': last_output_type,
                            'last_task_type': last_task_type,
                            'last_assistant_message': last_assistant_message[:300] if last_assistant_message else '',
                            'awaiting_continuation': awaiting_continuation
                        }
                    )
                elif dialogue_act['act'] == 'emotional':
                    # Emotional signal - use emotional support
                    return RoutingDecision(
                        pipeline=RecommendedPipeline.EMOTIONAL_SUPPORT,
                        complexity=QueryComplexity.SIMPLE,
                        confidence=0.85,
                        reasoning=f"Dialogue act: emotional signal detected",
                        agents_to_activate=['motivation'],
                        tools_to_enable=[],
                        enable_verification=False,
                        enable_visual=False,
                        max_iterations=2,
                        timeout_seconds=10.0,
                        use_knowledge_graph=False,
                        use_memory=True,
                        priority_factors={'empathy': 1.0},
                        enable_agent_negotiation=False,
                        extra_context={
                            'dialogue_act': 'emotional',
                            'emotional_tone': dialogue_act.get('tone', 'neutral')
                        }
                    )
        
        # ============================================================
        # STEP 1: CHECK CONVERSATION STATE (STATE > CLASSIFIER)
        # ============================================================
        
        # Check if there's a pending action (user clarified)
        if conversation_state.get('pending_action'):
            pending = conversation_state['pending_action']
            logger.info(f"🎯 PENDING ACTION DETECTED: {pending.get('type')} - ACTING IMMEDIATELY")
            
            # Create decision that will complete the pending action
            return RoutingDecision(
                pipeline=RecommendedPipeline.MULTI_AGENT,
                complexity=QueryComplexity.MODERATE,
                confidence=0.95,  # High confidence - user clarified
                reasoning=f"Completing pending action: {pending.get('type')}",
                agents_to_activate=['mentor'],
                tools_to_enable=self._get_tools_for_action(pending.get('type', '')),
                enable_verification=False,
                enable_visual=False,
                max_iterations=3,
                timeout_seconds=15.0,
                use_knowledge_graph=False,
                use_memory=True,
                priority_factors={'action_completion': 1.0},
                enable_agent_negotiation=False,
                extra_context={
                    'pending_action': pending,
                    'is_action_completion': True,
                    'clarification_response': query
                }
            )
        
        # Check if user is clarifying OR switching context (should continue action, not reset)
        # Uses SEMANTIC detection: negation + entity change, NOT hardcoded subject lists
        clarification_result = self._detect_clarification_or_switch(query, conversation_state)
        
        if clarification_result.get('is_clarification') and conversation_state.get('last_user_intent'):
            logger.info(f"🔄 CLARIFICATION/SWITCH DETECTED: {clarification_result.get('reason')} - continuing action")
            
            # Boost confidence and continue with the pending intent
            boosted_confidence = min(1.0, conversation_state.get('intent_confidence', 0.5) + 0.3)
            
            # If user specified a new entity (e.g., "Physics" instead of "Maths"), pass it
            extra_ctx = {
                'is_clarification': True,
                'original_intent': conversation_state.get('last_user_intent'),
                'boosted_confidence': boosted_confidence,
                'clarification_type': clarification_result.get('type'),
                'new_entity': clarification_result.get('new_entity')  # e.g., "Physics"
            }
            
            return RoutingDecision(
                pipeline=RecommendedPipeline.MULTI_AGENT,
                complexity=QueryComplexity.MODERATE,
                confidence=boosted_confidence,
                reasoning=f"User clarified/switched: {clarification_result.get('reason')}",
                agents_to_activate=['mentor'],
                tools_to_enable=self._get_tools_for_action(conversation_state.get('last_user_intent', '')),
                enable_verification=False,
                enable_visual=False,
                max_iterations=3,
                timeout_seconds=15.0,
                use_knowledge_graph=False,
                use_memory=True,
                priority_factors={'clarification': 1.0},
                enable_agent_negotiation=False,
                extra_context=extra_ctx
            )
        
        # ============================================================
        # STEP 1: SEMANTIC CLASSIFICATION (one signal among many)
        # ============================================================
        try:
            from services.semantic_intent_classifier import (
                get_semantic_classifier, 
                SemanticIntent,
                SemanticAnalysis
            )
            
            # Get recent messages for context
            recent_messages = context.get('message_history', [])[-5:]
            current_topic = context.get('current_topic', '')
            
            # Use LLM to understand the input semantically
            classifier = get_semantic_classifier()
            semantic_analysis = await classifier.classify(
                message=query,
                conversation_context=current_topic,
                recent_messages=recent_messages
            )
            
            logger.info(f"🧠 Semantic Analysis: intent={semantic_analysis.intent.value}, "
                       f"tone={semantic_analysis.emotional_tone}, "
                       f"confidence={semantic_analysis.confidence:.2f}")
            
            # ============================================================
            # STATE AUTHORITY: STATE OVERRIDES CLASSIFIER
            # ============================================================
            # If state says we have an active conversation with a topic,
            # and classifier says "general" or "greeting", STATE WINS.
            # The classifier is a SIGNAL, not a DECISION-MAKER.
            
            context_pack = context.get('context_pack')
            phase = conversation_state.get('conversation_phase', 'active')
            last_topic = conversation_state.get('last_topic', '')
            is_first_turn = context.get('is_first_turn', False)
            
            # Get topic from ContextPack if available
            if context_pack:
                if hasattr(context_pack, 'current_topic') and context_pack.current_topic:
                    last_topic = context_pack.current_topic
                elif hasattr(context_pack, 'previous_topic') and context_pack.previous_topic:
                    last_topic = context_pack.previous_topic
                if hasattr(context_pack, 'is_first_turn'):
                    is_first_turn = context_pack.is_first_turn
            
            # STATE AUTHORITY CHECK
            state_has_context = (last_topic or phase == 'active') and not is_first_turn
            classifier_says_generic = semantic_analysis.intent.value in ['general', 'greeting', 'acknowledgment']
            
            if state_has_context and classifier_says_generic:
                logger.warning(f"⚖️ STATE AUTHORITY: Classifier says '{semantic_analysis.intent.value}' "
                             f"but state has context (topic={last_topic}, phase={phase})")
                logger.warning(f"⚖️ STATE WINS: Forcing CONTINUATION routing instead of generic")
                
                # OVERRIDE: Force continuation routing
                return RoutingDecision(
                    pipeline=RecommendedPipeline.MULTI_AGENT,
                    complexity=QueryComplexity.MODERATE,
                    confidence=0.85,  # State-enforced confidence
                    reasoning=f"STATE AUTHORITY: Continuing conversation about {last_topic} despite classifier saying {semantic_analysis.intent.value}",
                    agents_to_activate=['mentor'],
                    tools_to_enable=['knowledge_search'],
                    enable_verification=False,
                    enable_visual=False,
                    max_iterations=3,
                    timeout_seconds=15.0,
                    use_knowledge_graph=False,
                    use_memory=True,
                    priority_factors={'state_authority': 1.0, 'continuation': 0.9},
                    enable_agent_negotiation=False,
                    extra_context={
                        'state_authority_override': True,
                        'classifier_intent': semantic_analysis.intent.value,
                        'forced_continuation': True,
                        'continuation_topic': last_topic,
                        'conversation_phase': phase,
                        'semantic_analysis': {
                            'intent': semantic_analysis.intent.value,
                            'emotional_tone': semantic_analysis.emotional_tone,
                            'confidence': semantic_analysis.confidence
                        }
                    }
                )
            
            # No override needed - use classifier result
            decision = self._route_from_semantic_analysis(query, semantic_analysis, context)
            
            # Enrich decision with conversation state
            if decision.extra_context is None:
                decision.extra_context = {}
            decision.extra_context['conversation_phase'] = phase
            decision.extra_context['emotional_signal'] = conversation_state.get('emotional_signal', 'neutral')
            decision.extra_context['semantic_analysis'] = {
                'intent': semantic_analysis.intent.value,
                'emotional_tone': semantic_analysis.emotional_tone,
                'confidence': semantic_analysis.confidence
            }
            
            logger.info(f"✅ Routing: {decision.pipeline.value} (semantic, confidence: {decision.confidence:.2f})")
            return decision
            
        except Exception as e:
            # Log with stack trace for debugging
            logger.warning(f"⚠️ Semantic classification failed, falling back to pattern matching: {type(e).__name__}: {e}")
            import traceback
            logger.debug(f"Semantic classification traceback: {traceback.format_exc()}")
            # Fall through to pattern matching ONLY if LLM fails
        
        # ============================================================
        # FALLBACK: Pattern matching (LEGACY - only if LLM fails completely)
        # ============================================================
        # PHASE 1 FIX: This path should be rare. Semantic classification
        # is the authoritative intelligence layer. Keywords are only hints.
        logger.warning("⚠️ LEGACY FALLBACK: Using pattern matching (semantic failed)")
        
        # Check for obvious gibberish (structural, not keyword - acceptable)
        if self._is_gibberish(query):
            logger.info(f"❓ Detected unclear/gibberish input (structural)")
            return self._clarification_decision(query, context)
        
        # PHASE 1: Keyword patterns are HINTS only, not decision-makers
        # They guide default routing when no semantic signal exists
        # The response is still shaped by the pipeline, not keywords
        
        # Check for trivial queries (structural: length + punctuation)
        if self._is_trivial_structural(query):
            logger.info("📋 Trivial query detected (structural fallback)")
            return self._trivial_decision(query)
        
        # Default to multi-agent pipeline for any substantive query
        # Let the agents figure out intent - don't force it via keywords
        student_context = await self._get_student_context(context)
        
        # Use conservative complexity (don't let keywords decide depth)
        decision = RoutingDecision(
            pipeline=RecommendedPipeline.MULTI_AGENT,
            complexity=QueryComplexity.MODERATE,  # Conservative default
            confidence=0.6,  # Lower confidence for fallback
            reasoning="LEGACY FALLBACK: Semantic classification unavailable - using default pipeline",
            agents_to_activate=['mentor', 'professor'],  # Let agents negotiate
            tools_to_enable=['knowledge_search'],
            enable_verification=False,
            enable_visual=False,
            max_iterations=3,
            timeout_seconds=15.0,
            use_knowledge_graph=False,
            use_memory=True,
            priority_factors={'fallback': 1.0},
            enable_agent_negotiation=True,  # IMPORTANT: Let agents decide
            # CRITICAL: Pass None explicitly so supervisor knows semantic failed
            extra_context={'semantic_analysis': None, 'fallback_reason': 'semantic_classification_failed'}
        )

        logger.info(f"✅ Routing: {decision.pipeline.value} (LEGACY fallback)")
        return decision
    
    def _get_tools_for_action(self, action_type: str) -> List[str]:
        """
        Get the tools needed for a specific action type.
        
        This maps pending actions to their required tools.
        """
        action_tools = {
            'study_plan': ['study_planner'],
            'quiz': ['quiz_generator'],
            'practice': ['problem_generator'],
            'explain': ['knowledge_search'],
            'calculate': ['calculator'],
            'schedule': ['study_planner'],
            'reminder': ['schedule_reminder'],
        }
        
        return action_tools.get(action_type, [])
    
    def _detect_dialogue_act(
        self,
        query: str,
        conversation_state: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        🎯 TRI-LANE: Lightweight dialogue-act detection based on message STRUCTURE.
        
        NOT keyword-based. Uses:
        1. Message length (word count)
        2. Punctuation patterns
        3. Prior conversation state
        4. Message structure (questions vs statements)
        
        Returns:
            {
                'act': 'ack' | 'continue' | 'emotional' | 'short_response' | None,
                'lane': 'conversation' | 'education' | None,
                'confidence': float,
                'tone': str (for emotional)
            }
            or None if no dialogue act detected (proceed to classifier)
        """
        if not query:
            return None
        
        query_stripped = query.strip()
        query_lower = query_stripped.lower()
        words = query_stripped.split()
        word_count = len(words)
        
        # Structural indicators
        ends_with_question = query_stripped.endswith('?')
        is_single_punctuation = len(query_stripped) <= 2 and not query_stripped.isalnum()
        has_prior_context = bool(conversation_state.get('last_topic') or conversation_state.get('pending_action'))
        last_turn_asked_question = conversation_state.get('ai_asked_question', False)
        
        # ================================================================
        # RULE 0: EDUCATION REQUEST OVERRIDE (HARD PRIORITY)
        # ================================================================
        # If the message looks like an education request, NEVER route to recap.
        # This must run BEFORE short-message rules to prevent "explain X" takeover.
        # 
        # Education indicators (structure-based, NOT keyword-hardcoded):
        # 1. Starts with educational verbs: explain/what/how/why/define/solve/derive/prove
        # 2. Contains question-concept structure
        # 3. Message length >= 2 words with noun concept
        
        EDUCATION_VERBS = {'explain', 'what', 'how', 'why', 'define', 'solve', 'derive', 
                          'prove', 'calculate', 'find', 'describe', 'tell', 'show', 'teach'}
        
        first_word = words[0].lower().rstrip('?!,') if words else ''
        
        # Check if it's an education request
        is_education_request = False
        
        # Pattern 1: Starts with education verb + has content
        if first_word in EDUCATION_VERBS and word_count >= 2:
            is_education_request = True
        
        # Pattern 2: "what is X", "how does X", "why does X" etc.
        if word_count >= 2 and first_word in {'what', 'how', 'why', 'when', 'where', 'which'}:
            is_education_request = True
        
        # Pattern 3: Question form with concept (ends with ? and has content)
        if ends_with_question and word_count >= 3:
            is_education_request = True
        
        # If education request detected, return None to let classifier handle it
        # This OVERRIDES any prior continue/recap state
        if is_education_request:
            logger.debug(f"🎓 Education override: '{query_stripped[:50]}' bypasses dialogue-act → classifier")
            return None  # Let semantic classifier route to education lane
        
        # ================================================================
        # RULE 1: Very short messages (1-3 words) with prior context
        # These are likely acknowledgments or continuations, NOT new queries
        # But ONLY if not an education request (already handled above)
        # ================================================================
        if word_count <= 3 and has_prior_context:
            # Check if it's a response to AI's question
            if last_turn_asked_question:
                return {
                    'act': 'ack',
                    'lane': 'conversation',
                    'confidence': 0.85,
                    'reason': f'Short response ({word_count} words) to AI question'
                }
            else:
                # Short message with context but no question - likely continuation
                return {
                    'act': 'short_response',
                    'lane': 'conversation',
                    'confidence': 0.75,
                    'reason': f'Short message ({word_count} words) with prior context'
                }
        
        # ================================================================
        # RULE 2: Single word or very short (1-2 words) - conversation
        # PHASE B FIX: Use semantic classifier's intent/dialogue_act when available
        # instead of ACK_WORDS list. Fallback to structural detection only.
        # ================================================================
        from core.config import settings
        
        if settings.ENABLE_SEMANTIC_ONLY_ROUTING:
            # PHASE B: Rely on semantic classifier for ack detection
            # Only use structural detection (word count, not word lists)
            if word_count <= 2:
                # Very short message - let semantic classifier decide
                # Don't hardcode ACK_WORDS - just flag as potential ack
                return {
                    'act': 'potential_ack',
                    'lane': 'conversation',
                    'confidence': 0.6,  # Lower confidence - needs semantic validation
                    'reason': f'Ultra-short message ({word_count} words) - needs semantic validation'
                }
        else:
            # LEGACY: ACK_WORDS based detection (only when flag disabled)
            ACK_WORDS = {'yes', 'ok', 'okay', 'hmm', 'sure', 'no', 'yeah', 'yep', 'nope',
                         'got', 'right', 'thanks', 'cool', 'nice', 'great', 'good', 'fine'}
            
            if word_count <= 2 and first_word in ACK_WORDS:
                return {
                    'act': 'ack',
                    'lane': 'conversation',
                    'confidence': 0.9,
                    'reason': f'Ultra-short acknowledgment ({word_count} words) [legacy]'
                }
        
        # ================================================================
        # RULE 3: Emotional indicators (structural, not keyword)
        # Messages with exclamations, emotional punctuation patterns
        # ================================================================
        exclamation_count = query_stripped.count('!')
        has_ellipsis = '...' in query_stripped or '…' in query_stripped
        has_emoji_pattern = any(ord(c) > 127 and ord(c) < 65536 for c in query_stripped)
        
        # Emotional messages often have: exclamations, ellipsis, short + feeling words
        if exclamation_count >= 2 or (has_ellipsis and word_count <= 6):
            return {
                'act': 'emotional',
                'lane': 'conversation',
                'confidence': 0.7,
                'tone': 'expressive',
                'reason': 'Emotional punctuation pattern'
            }
        
        # ================================================================
        # RULE 4: Session recall patterns (structural)
        # Questions about prior conversation (short + temporal reference)
        # ================================================================
        has_temporal_reference = any(w in query_stripped.lower() for w in ['last', 'before', 'earlier', 'previous', 'again'])
        is_recall_length = word_count <= 8  # Session recall questions are usually short
        
        if has_temporal_reference and is_recall_length and ends_with_question:
            return {
                'act': 'continue',
                'lane': 'conversation',
                'confidence': 0.8,
                'reason': 'Temporal reference + question pattern'
            }
        
        # ================================================================
        # No dialogue act detected - proceed to semantic classifier
        # ================================================================
        return None
    
    def _detect_clarification_or_switch(
        self,
        query: str,
        conversation_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        SEMANTIC detection of clarification or context switch.
        
        This uses GENERIC patterns, NOT hardcoded subject lists:
        1. Negation patterns: "not", "no", "don't want", "instead"
        2. Switch patterns: "give me", "switch to", "change to"
        3. Entity extraction: Detects what new thing user wants
        
        Returns:
            {
                'is_clarification': bool,
                'type': 'negation' | 'switch' | 'direct' | None,
                'new_entity': str or None,  # e.g., "Physics"
                'reason': str
            }
        """
        query_lower = query.lower().strip()
        
        # If no pending intent, this isn't a clarification
        if not conversation_state.get('last_user_intent'):
            return {'is_clarification': False, 'type': None, 'new_entity': None, 'reason': ''}
        
        # ============================================================
        # PATTERN 1: DIRECT CLARIFICATION PHRASES
        # ============================================================
        direct_phrases = ['no i mean', 'i meant', 'actually', 'no no', 'wait wait']
        if any(phrase in query_lower for phrase in direct_phrases):
            entity = self._extract_entity_from_query(query)
            return {
                'is_clarification': True,
                'type': 'direct',
                'new_entity': entity,
                'reason': 'Direct clarification phrase detected'
            }
        
        # ============================================================
        # PATTERN 2: NEGATION + ENTITY (Generic, not hardcoded subjects)
        # "not maths", "not that topic", "don't want chemistry"
        # ============================================================
        negation_patterns = [
            r'\bnot\s+(\w+)',           # "not X" -> captures X
            r"\bdon'?t\s+want\s+(\w+)", # "don't want X"
            r'\bno\s+(\w+)',             # "no X"
            r'\bnot\s+that',             # "not that"
        ]
        
        import re
        for pattern in negation_patterns:
            match = re.search(pattern, query_lower)
            if match:
                # User is negating something - this is a clarification
                # Try to find what they DO want
                new_entity = self._extract_entity_from_query(query)
                return {
                    'is_clarification': True,
                    'type': 'negation',
                    'new_entity': new_entity,
                    'reason': f'Negation detected: {match.group(0)}'
                }
        
        # ============================================================
        # PATTERN 3: SWITCH/CHANGE PATTERNS
        # "give me physics", "switch to bio", "change to chemistry"
        # ============================================================
        switch_patterns = [
            r'\bgive\s+(?:me\s+)?(\w+)',     # "give me X" or "give X"
            r'\bswitch\s+to\s+(\w+)',         # "switch to X"
            r'\bchange\s+to\s+(\w+)',         # "change to X"
            r'\binstead\s+(?:of\s+\w+\s+)?(\w+)?',  # "instead X" or "instead of Y, X"
            r'\bwant\s+(\w+)',                # "want X"
            r'\bneed\s+(\w+)',                # "need X"
        ]
        
        for pattern in switch_patterns:
            match = re.search(pattern, query_lower)
            if match:
                captured = match.group(1) if match.lastindex else None
                new_entity = captured or self._extract_entity_from_query(query)
                
                # Only treat as switch if there's a pending action
                if conversation_state.get('pending_action') or conversation_state.get('last_user_intent'):
                    return {
                        'is_clarification': True,
                        'type': 'switch',
                        'new_entity': new_entity,
                        'reason': f'Switch pattern detected: {match.group(0)}'
                    }
        
        # ============================================================
        # PATTERN 4: SHORT RESPONSE WITH ENTITY (Continuation signal)
        # User just says "physics" or "for physics" after being asked
        # ============================================================
        if len(query.split()) <= 3 and conversation_state.get('pending_action'):
            entity = self._extract_entity_from_query(query)
            if entity:
                return {
                    'is_clarification': True,
                    'type': 'continuation',
                    'new_entity': entity,
                    'reason': 'Short response with entity after pending action'
                }
        
        return {'is_clarification': False, 'type': None, 'new_entity': None, 'reason': ''}
    
    def _extract_entity_from_query(self, query: str) -> Optional[str]:
        """
        Extract the main entity (subject/topic) from query.
        
        This is GENERIC - detects any capitalized word or known category,
        NOT a hardcoded list of subjects.
        """
        import re
        
        query_clean = query.strip()
        
        # Strategy 1: Find capitalized words (proper nouns = likely entities)
        capitalized = re.findall(r'\b[A-Z][a-z]+\b', query_clean)
        if capitalized:
            # Filter out common non-entity words
            common_words = {'I', 'The', 'A', 'An', 'My', 'Your', 'This', 'That', 'Please', 'Thanks'}
            entities = [w for w in capitalized if w not in common_words]
            if entities:
                return entities[-1]  # Take the last one (usually the new subject)
        
        # Strategy 2: Look for common academic subject patterns
        # This is category-based, not exhaustive list
        subject_categories = {
            'science': ['physics', 'chemistry', 'biology', 'science'],
            'math': ['maths', 'math', 'mathematics', 'calculus', 'algebra', 'geometry'],
            'language': ['english', 'hindi', 'language'],
            'social': ['history', 'geography', 'civics', 'economics'],
        }
        
        query_lower = query.lower()
        for category, keywords in subject_categories.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return keyword.title()  # Return the matched keyword
        
        # Strategy 3: Take the last noun-like word (heuristic)
        words = query_clean.split()
        if words:
            # Filter to words that look like subjects (3+ chars, not common)
            candidates = [w for w in words if len(w) >= 3 and w.lower() not in 
                         {'the', 'for', 'and', 'but', 'not', 'give', 'want', 'need', 'please'}]
            if candidates:
                return candidates[-1].title()
        
        return None

    def _route_from_semantic_analysis(
        self,
        query: str,
        analysis: 'SemanticAnalysis',
        context: Dict[str, Any]
    ) -> RoutingDecision:
        """
        🆕 Route based on LLM semantic analysis.
        
        This is the INTELLIGENT routing that understands meaning, not patterns.
        """
        from services.semantic_intent_classifier import SemanticIntent
        
        intent = analysis.intent
        
        # Map semantic intents to pipelines
        if intent == SemanticIntent.GREETING:
            return self._trivial_decision(query)
        
        elif intent == SemanticIntent.FAREWELL:
            return self._trivial_decision(query)
        
        elif intent == SemanticIntent.GRATITUDE:
            return self._acknowledgment_decision(query, analysis)
        
        elif intent == SemanticIntent.ACKNOWLEDGMENT:
            return self._acknowledgment_decision(query, analysis)
        
        elif intent in [SemanticIntent.EMOTIONAL_SUPPORT, SemanticIntent.MOTIVATION_NEED]:
            # PHASE 4 FIX: Emotion modulates response, doesn't change pipeline
            # Use MULTI_AGENT with emotional context - mentor handles empathy
            return RoutingDecision(
                pipeline=RecommendedPipeline.MULTI_AGENT,  # NOT EMOTIONAL_SUPPORT
                complexity=QueryComplexity.SIMPLE,
                confidence=analysis.confidence,
                reasoning=f"Semantic (emotional): {analysis.reasoning}",
                agents_to_activate=['mentor'],  # Mentor handles emotion + content
                tools_to_enable=[],
                enable_verification=False,
                enable_visual=False,
                max_iterations=2,
                timeout_seconds=10.0,
                use_knowledge_graph=False,
                use_memory=True,
                priority_factors={'empathy': 1.0, 'support': 0.9},
                enable_agent_negotiation=False,
                extra_context={
                    'semantic_analysis': analysis.to_dict(),
                    'needs_empathy': analysis.needs_empathy,
                    'emotional_tone': analysis.emotional_tone,
                    # PHASE 4: Emotion is CONTEXT, not routing override
                    'emotional_context': {
                        'detected_emotion': analysis.emotional_tone,
                        'intensity': analysis.emotional_intensity,
                        'modulate_response': True,  # Signal to agent
                        'prioritize_empathy': True
                    }
                }
            )
        
        elif intent == SemanticIntent.CONFUSION:
            # PHASE 4 FIX: Confusion routes to doubt_resolver with emotional context
            return RoutingDecision(
                pipeline=RecommendedPipeline.MULTI_AGENT,  # NOT EMOTIONAL_SUPPORT
                complexity=QueryComplexity.SIMPLE,
                confidence=analysis.confidence,
                reasoning=f"Student confused: {analysis.reasoning}",
                agents_to_activate=['doubt_resolver', 'mentor'],  # Doubt + empathy
                tools_to_enable=[],
                enable_verification=False,
                enable_visual=False,
                max_iterations=2,
                timeout_seconds=10.0,
                use_knowledge_graph=False,
                use_memory=True,
                priority_factors={'clarity': 1.0, 'empathy': 0.8},
                enable_agent_negotiation=False,
                extra_context={
                    'semantic_analysis': analysis.to_dict(),
                    'emotional_state': 'confused',
                    # PHASE 4: Emotional context for response modulation
                    'emotional_context': {
                        'detected_emotion': 'confused',
                        'intensity': analysis.emotional_intensity,
                        'modulate_response': True,
                        'use_gentle_tone': True
                    }
                }
            )
        
        elif intent == SemanticIntent.CELEBRATION:
            return self._acknowledgment_decision(query, analysis)
        
        # ================================================================
        # 🆕 SCOPE-AWARE ROUTING (PROPORTIONAL RESPONSE SYSTEM)
        # ================================================================
        # CHECK RESPONSE EXPECTATION FIRST - this determines output scope
        # The key insight: "What should I study today?" is NOT a plan request
        
        response_expectation = getattr(analysis, 'response_expectation', 'conversational_advice')
        temporal_scope = getattr(analysis, 'temporal_scope', 'unspecified')
        delivery_mode = getattr(analysis, 'delivery_mode', 'conversational')
        urgency_level = getattr(analysis, 'urgency_level', 'medium')
        
        logger.info(f"📏 Scope analysis: response_expectation={response_expectation}, "
                   f"temporal_scope={temporal_scope}, delivery_mode={delivery_mode}, "
                   f"urgency_level={urgency_level}")
        
        # ================================================================
        # 🚨 URGENCY-AWARE OVERRIDE (SYSTEM-LEVEL INTELLIGENCE)
        # ================================================================
        # HIGH URGENCY queries (exam tomorrow, viva in 2 hours, interview tonight, etc.)
        # need STRUCTURED, ACTIONABLE responses regardless of response_expectation.
        # This is NOT keyword-based - it uses LLM-detected urgency from SemanticAnalysis.
        #
        # The principle: When time is critical, students need:
        # - Concrete action items (not vague advice)
        # - Structured format (easier to scan under pressure)
        # - Immediate value (not clarifying questions)
        #
        is_high_urgency = urgency_level == "high"
        is_time_critical = temporal_scope in ["immediate", "today"]
        
        if is_high_urgency or (is_time_critical and response_expectation == "conversational_advice"):
            logger.info(f"🚨 URGENCY OVERRIDE: High urgency ({urgency_level}) or time-critical ({temporal_scope}) "
                       f"- forcing structured response mode")
            
            # Override to structured mode - student needs actionable help NOW
            return RoutingDecision(
                pipeline=RecommendedPipeline.MULTI_AGENT,
                complexity=QueryComplexity.MODERATE,  # Not trivial - needs substance
                confidence=analysis.confidence,
                reasoning=f"URGENCY OVERRIDE: {urgency_level} urgency, {temporal_scope} scope - providing structured actionable response",
                agents_to_activate=['mentor'],
                tools_to_enable=['knowledge_search'],  # Enable knowledge tools for better content
                enable_verification=False,
                enable_visual=False,
                max_iterations=3,  # Allow more iterations for quality
                timeout_seconds=15.0,  # More time for comprehensive response
                use_knowledge_graph=True,  # Use knowledge for concrete suggestions
                use_memory=True,
                priority_factors={'actionability': 1.0, 'structure': 0.9, 'urgency': 1.0},
                enable_agent_negotiation=False,
                extra_context={
                    'semantic_analysis': analysis.to_dict(),
                    'response_expectation': 'urgent_assistance',  # New mode for mentor
                    'temporal_scope': temporal_scope,
                    'delivery_mode': 'structured',  # Force structured output
                    'is_recommendation': False,  # NOT a casual recommendation
                    'is_urgent': True,  # Flag for downstream agents
                    'urgency_level': urgency_level,
                    'avoid_comprehensive_output': False,  # Allow comprehensive help
                    'require_actionable_items': True  # Must provide concrete steps
                }
            )
        
        # ================================================================
        # PATH 1: CONVERSATIONAL ADVICE (Quick suggestions, mentor opinion)
        # ================================================================
        # Only for LOW/MEDIUM urgency, non-time-critical queries
        # This is the FIX for "What should I study today?" - NO tools, just LLM
        if response_expectation == "conversational_advice":
            logger.info(f"💬 CONVERSATIONAL ADVICE path: Quick contextual suggestion (no tools)")
            
            return RoutingDecision(
                pipeline=RecommendedPipeline.MULTI_AGENT,
                complexity=QueryComplexity.SIMPLE,
                confidence=analysis.confidence,
                reasoning=f"Conversational advice request (scope: {temporal_scope}): {analysis.reasoning}",
                agents_to_activate=['mentor'],
                tools_to_enable=[],  # NO TOOLS - pure LLM response
                enable_verification=False,
                enable_visual=False,
                max_iterations=2,
                timeout_seconds=10.0,
                use_knowledge_graph=False,
                use_memory=True,  # Use context for personalized suggestion
                priority_factors={'personalization': 1.0, 'brevity': 0.9},
                enable_agent_negotiation=False,
                extra_context={
                    'semantic_analysis': analysis.to_dict(),
                    'response_expectation': response_expectation,
                    'temporal_scope': temporal_scope,
                    'delivery_mode': delivery_mode,
                    'is_recommendation': True,  # Flag for MentorAgent
                    'max_response_scope': temporal_scope,  # Constraint for response
                    'avoid_comprehensive_output': True,  # Explicit instruction
                    'is_urgent': False,
                    'urgency_level': urgency_level
                }
            )
        
        # ================================================================
        # PATH 2: STRUCTURED DELIVERABLE (Full plans, schedules, documents)
        # ================================================================
        # Only route to StudyPlannerTool when user explicitly wants a DELIVERABLE
        if response_expectation == "structured_deliverable":
            output_type = analysis.requested_output_type
            
            # Problem solution path
            if output_type == "problem_solution":
                complexity_score = self._analyze_complexity(query, context)
                complexity = self._score_to_complexity(complexity_score, {})
                enable_verification = True
                enable_visual = True
                tools = ['calculator', 'knowledge_search']
                agents = ['professor', 'mentor']
            else:
                # study_plan, quiz, summary - use appropriate tools
                complexity = QueryComplexity.MODERATE
                enable_verification = False
                enable_visual = False
                tools = ['study_planner'] if output_type == "study_plan" else []
                agents = ['mentor']
            
            logger.info(f"📋 STRUCTURED DELIVERABLE path: output_type={output_type}, tools={tools}")
            
            return RoutingDecision(
                pipeline=RecommendedPipeline.MULTI_AGENT,
                complexity=complexity,
                confidence=analysis.confidence,
                reasoning=f"Structured deliverable ({output_type}): {analysis.reasoning}",
                agents_to_activate=agents,
                tools_to_enable=tools,
                enable_verification=enable_verification,
                enable_visual=enable_visual,
                max_iterations=5,
                timeout_seconds=30.0,
                use_knowledge_graph=output_type == "problem_solution",
                use_memory=True,
                priority_factors={'action_fulfillment': 1.0, 'structured_output': 0.9},
                enable_agent_negotiation=output_type == "problem_solution",
                extra_context={
                    'semantic_analysis': analysis.to_dict(),
                    'output_type': output_type,
                    'response_expectation': response_expectation,
                    'temporal_scope': temporal_scope,
                    'has_actionable_request': True,
                    'requires_structured_output': True
                }
            )
        
        # ================================================================
        # LEGACY: ACTIONABLE REQUEST ROUTING (Fallback for old classification)
        # ================================================================
        # This maintains backwards compatibility if response_expectation wasn't set
        if analysis.has_actionable_request and analysis.requested_output_type:
            output_type = analysis.requested_output_type
            
            # Determine complexity and tools based on output type
            if output_type == "problem_solution":
                complexity_score = self._analyze_complexity(query, context)
                complexity = self._score_to_complexity(complexity_score, {})
                enable_verification = True
                enable_visual = True
                tools = ['calculator', 'knowledge_search']
                agents = ['professor', 'mentor']
            else:
                # study_plan, quiz, summary, etc.
                complexity = QueryComplexity.MODERATE
                enable_verification = False
                enable_visual = False
                tools = ['study_planner']
                agents = ['mentor']
            
            logger.info(f"🎯 LEGACY ACTIONABLE REQUEST: output_type={output_type}")
            
            return RoutingDecision(
                pipeline=RecommendedPipeline.MULTI_AGENT,
                complexity=complexity,
                confidence=analysis.confidence,
                reasoning=f"Actionable request ({output_type}): {analysis.reasoning}",
                agents_to_activate=agents,
                tools_to_enable=tools,
                enable_verification=enable_verification,
                enable_visual=enable_visual,
                max_iterations=5,
                timeout_seconds=30.0,
                use_knowledge_graph=output_type == "problem_solution",
                use_memory=True,
                priority_factors={'action_fulfillment': 1.0, 'structured_output': 0.9},
                enable_agent_negotiation=output_type == "problem_solution",
                extra_context={
                    'semantic_analysis': analysis.to_dict(),
                    'output_type': output_type,
                    'has_actionable_request': True,
                    'requires_structured_output': True
                }
            )
        
        elif intent in [SemanticIntent.EXPLORE_NEW, SemanticIntent.CONTINUE_PREVIOUS, SemanticIntent.GET_HELP]:
            action_type = {
                SemanticIntent.EXPLORE_NEW: 'explore',
                SemanticIntent.CONTINUE_PREVIOUS: 'continue',
                SemanticIntent.GET_HELP: 'help'
            }.get(intent, 'explore')
            
            return RoutingDecision(
                pipeline=RecommendedPipeline.PROACTIVE_GUIDANCE,
                complexity=QueryComplexity.SIMPLE,
                confidence=analysis.confidence,
                reasoning=f"Action intent '{action_type}': {analysis.reasoning}",
                agents_to_activate=['mentor', 'motivation'],
                tools_to_enable=['topic_suggester'],
                enable_verification=False,
                enable_visual=False,
                max_iterations=2,
                timeout_seconds=10.0,
                use_knowledge_graph=True,
                use_memory=True,
                priority_factors={'personalization': 1.0},
                enable_agent_negotiation=False,
                extra_context={'action_intent': action_type, 'semantic_analysis': analysis.to_dict()}
            )
        
        elif intent == SemanticIntent.CHITCHAT:
            return RoutingDecision(
                pipeline=RecommendedPipeline.CHITCHAT,
                complexity=QueryComplexity.TRIVIAL,
                confidence=analysis.confidence,
                reasoning=f"Casual conversation: {analysis.reasoning}",
                agents_to_activate=['mentor'],
                tools_to_enable=[],
                enable_verification=False,
                enable_visual=False,
                max_iterations=1,
                timeout_seconds=5.0,
                use_knowledge_graph=False,
                use_memory=True,
                priority_factors={'friendliness': 1.0},
                enable_agent_negotiation=False,
                extra_context={'semantic_analysis': analysis.to_dict()}
            )
        
        elif intent == SemanticIntent.UNCLEAR:
            return self._clarification_decision(query, context)
        
        elif intent in [SemanticIntent.QUESTION, SemanticIntent.EXPLANATION_REQUEST, 
                        SemanticIntent.PRACTICE_REQUEST, SemanticIntent.CLARIFICATION]:
            # Educational queries - analyze complexity
            complexity_score = self._analyze_complexity(query, context)
            complexity = self._score_to_complexity(complexity_score, {})
            decision = self._select_pipeline(query, complexity, context, {}, analysis)
            
            # ================================================================
            # CONTINUATION RESOLVER - Inject previous topic for short follow-ups
            # ================================================================
            # If this is a short message lacking a clear topic, AND we have a
            # previous education topic, inject it so downstream agents know
            # what to "explain deeper" about.
            continuation_result = self._resolve_continuation_topic(query, context, analysis)
            if continuation_result.get('is_continuation'):
                if decision.extra_context is None:
                    decision.extra_context = {}
                decision.extra_context['is_continuation'] = True
                decision.extra_context['continuation_topic'] = continuation_result['topic']
                decision.extra_context['continuation_reason'] = continuation_result['reason']
                logger.info(f"📌 Continuation resolved | prev_topic={continuation_result['topic']} | "
                           f"msg=\"{query[:40]}\" | route=education")
            
            return decision
        
        # ================================================================
        # OFF_TOPIC & GENERAL - Use CHITCHAT pipeline with LLM
        # ================================================================
        # CRITICAL: Students can ask ANYTHING. Non-academic questions
        # should get intelligent, empathetic responses - not rejection.
        # Route to CHITCHAT which uses LLM to generate human-like replies.
        # ================================================================
        elif intent == SemanticIntent.OFF_TOPIC:
            return RoutingDecision(
                pipeline=RecommendedPipeline.CHITCHAT,
                complexity=QueryComplexity.SIMPLE,
                confidence=analysis.confidence,
                reasoning=f"Non-academic query - friendly LLM response: {analysis.reasoning}",
                agents_to_activate=['mentor'],
                tools_to_enable=[],
                enable_verification=False,
                enable_visual=False,
                max_iterations=1,
                timeout_seconds=10.0,
                use_knowledge_graph=False,
                use_memory=True,
                priority_factors={'friendliness': 1.0, 'empathy': 0.8},
                enable_agent_negotiation=False,
                extra_context={
                    'semantic_analysis': analysis.to_dict(),
                    'response_style': 'friendly_companion',
                    'allow_non_academic': True
                }
            )
        
        elif intent == SemanticIntent.GENERAL:
            # General queries - could be anything! Use LLM to understand and respond
            # Check if it seems educational first
            if analysis.topic_mentioned or '?' in query:
                complexity_score = self._analyze_complexity(query, context)
                complexity = self._score_to_complexity(complexity_score, {})
                return self._select_pipeline(query, complexity, context, {}, analysis)
            else:
                # Non-educational general - use friendly CHITCHAT pipeline
                return RoutingDecision(
                    pipeline=RecommendedPipeline.CHITCHAT,
                    complexity=QueryComplexity.SIMPLE,
                    confidence=analysis.confidence,
                    reasoning=f"General query - friendly LLM response: {analysis.reasoning}",
                    agents_to_activate=['mentor'],
                    tools_to_enable=[],
                    enable_verification=False,
                    enable_visual=False,
                    max_iterations=1,
                    timeout_seconds=10.0,
                    use_knowledge_graph=False,
                    use_memory=True,
                    priority_factors={'friendliness': 1.0},
                    enable_agent_negotiation=False,
                    extra_context={
                        'semantic_analysis': analysis.to_dict(),
                        'response_style': 'friendly_companion'
                    }
                )
        
        else:
            # Fallback for any unhandled intent - use CHITCHAT for friendly response
            # This ensures NO query ever gets blocked or rejected
            return RoutingDecision(
                pipeline=RecommendedPipeline.CHITCHAT,
                complexity=QueryComplexity.SIMPLE,
                confidence=0.7,
                reasoning=f"Unhandled intent '{intent.value}' - using friendly fallback",
                agents_to_activate=['mentor'],
                tools_to_enable=[],
                enable_verification=False,
                enable_visual=False,
                max_iterations=1,
                timeout_seconds=10.0,
                use_knowledge_graph=False,
                use_memory=True,
                priority_factors={'friendliness': 1.0},
                enable_agent_negotiation=False,
                extra_context={'semantic_analysis': analysis.to_dict() if analysis else None}
            )
    
    def _acknowledgment_decision(self, query: str, analysis: 'SemanticAnalysis' = None) -> RoutingDecision:
        """Decision for acknowledgments (great, ok, thanks, got it, etc.)"""
        return RoutingDecision(
            pipeline=RecommendedPipeline.FAST_RESPONSE,
            complexity=QueryComplexity.TRIVIAL,
            confidence=0.9,
            reasoning="Acknowledgment/gratitude - contextual response",
            agents_to_activate=['mentor'],
            tools_to_enable=[],
            enable_verification=False,
            enable_visual=False,
            max_iterations=1,
            timeout_seconds=5.0,
            use_knowledge_graph=False,
            use_memory=True,  # CRITICAL: Use memory for context
            priority_factors={'continuity': 1.0},
            enable_agent_negotiation=False,
            extra_context={
                'response_type': 'acknowledgment',
                'semantic_analysis': analysis.to_dict() if analysis else None
            }
        )
    
    def _is_gibberish(self, query: str) -> bool:
        """
        🆕 Detect if input is gibberish, typo, or nonsensical.
        
        Examples:
        - "sds" → gibberish
        - "asdfghjkl" → gibberish
        - "xyz123" → gibberish
        """
        query_clean = query.strip().lower()
        
        # Very short non-word inputs
        if len(query_clean) <= 3 and not self._is_trivial(query):
            # Check if it's a real word or common abbreviation
            real_short_words = {'hi', 'ok', 'yes', 'no', 'bye', 'hey', 'sup', 'yo', 'huh', 'wow', 'why', 'how', 'what', 'who', 'hmm', 'idk', 'lol', 'omg'}
            if query_clean not in real_short_words:
                return True
        
        # No vowels (likely gibberish) - for inputs > 3 chars
        if len(query_clean) > 3:
            vowels = set('aeiou')
            has_vowel = any(c in vowels for c in query_clean)
            if not has_vowel and query_clean.isalpha():
                return True
        
        # Repetitive characters (like "aaaaa" or "asdfasdf")
        if len(query_clean) > 4:
            # Check for same char repeated
            if len(set(query_clean.replace(' ', ''))) <= 2:
                return True
        
        return False
    
    def _detect_action_intent(self, query: str) -> Optional[str]:
        """
        🆕 Detect action-oriented intents.
        
        Types:
        - 'explore': Student wants something new
        - 'continue': Student wants to continue previous work
        - 'chitchat': Casual conversation
        - 'help': Student needs guidance
        """
        query_clean = query.strip()
        
        # Check each action intent type
        action_intents = ['explore', 'continue', 'chitchat', 'help']
        for intent in action_intents:
            if intent in self._compiled_emotional:
                for pattern in self._compiled_emotional[intent]:
                    if pattern.search(query_clean):
                        return intent
        
        return None
    
    def _clarification_decision(self, query: str, context: Dict[str, Any]) -> RoutingDecision:
        """🆕 Decision for unclear/gibberish input"""
        return RoutingDecision(
            pipeline=RecommendedPipeline.CLARIFICATION,
            complexity=QueryComplexity.TRIVIAL,
            confidence=0.9,
            reasoning=f"Input appears unclear/gibberish: '{query[:20]}' - asking for clarification",
            agents_to_activate=['mentor'],
            tools_to_enable=[],
            enable_verification=False,
            enable_visual=False,
            max_iterations=1,
            timeout_seconds=5.0,
            use_knowledge_graph=False,
            use_memory=True,
            priority_factors={'clarity': 1.0},
            enable_agent_negotiation=False
        )
    
    def _action_intent_decision(
        self, 
        query: str, 
        action_intent: str, 
        context: Dict[str, Any]
    ) -> RoutingDecision:
        """🆕 Decision for action-oriented intents (explore, continue, help, chitchat)"""
        
        if action_intent == 'chitchat':
            return RoutingDecision(
                pipeline=RecommendedPipeline.CHITCHAT,
                complexity=QueryComplexity.TRIVIAL,
                confidence=0.85,
                reasoning=f"Casual conversation detected - friendly response",
                agents_to_activate=['mentor'],
                tools_to_enable=[],
                enable_verification=False,
                enable_visual=False,
                max_iterations=1,
                timeout_seconds=5.0,
                use_knowledge_graph=False,
                use_memory=True,
                priority_factors={'friendliness': 1.0},
                enable_agent_negotiation=False
            )
        
        # For explore, continue, help - use PROACTIVE_GUIDANCE
        return RoutingDecision(
            pipeline=RecommendedPipeline.PROACTIVE_GUIDANCE,
            complexity=QueryComplexity.SIMPLE,
            confidence=0.9,
            reasoning=f"Action intent '{action_intent}' - providing personalized guidance",
            agents_to_activate=['mentor', 'motivation'],
            tools_to_enable=['topic_suggester', 'progress_tracker'],
            enable_verification=False,
            enable_visual=False,
            max_iterations=2,
            timeout_seconds=10.0,
            use_knowledge_graph=True,  # Use to find related topics
            use_memory=True,  # CRITICAL: Use memory for personalization
            priority_factors={'personalization': 1.0, 'relevance': 0.8},
            enable_agent_negotiation=False,
            # Pass the specific intent for the handler
            extra_context={'action_intent': action_intent}
        )
    
    def _detect_emotional_state(
        self, 
        query: str,
        semantic_analysis: Optional['SemanticAnalysis'] = None
    ) -> Optional[str]:
        """
        Detect emotional state from query.
        
        PHASE 1 FIX: This is now a HINT method. When semantic analysis is
        available, its emotional_tone field takes precedence. Pattern matching
        only runs when:
        1. No semantic analysis available
        2. Semantic confidence is low (< 0.5)
        
        Returns:
            Emotional state string or None
        """
        from core.config import settings
        
        # PHASE 1: Semantic analysis is authoritative when available
        if settings.ENABLE_SEMANTIC_EMOTION_DETECTION and semantic_analysis:
            # Use semantic emotional tone, not patterns
            if semantic_analysis.confidence >= 0.5:
                tone = semantic_analysis.emotional_tone
                intensity = semantic_analysis.emotional_intensity
                
                # Only return emotional state if intensity is significant
                if intensity >= 0.4:
                    # Map semantic tones to our emotion states
                    tone_to_emotion = {
                        'anxious': 'anxious',
                        'frustrated': 'frustrated',
                        'confused': 'confused',
                        'bored': 'bored',
                        'excited': 'excited',
                        'negative': 'frustrated' if intensity > 0.6 else None,
                    }
                    return tone_to_emotion.get(tone)
                return None
        
        # LEGACY FALLBACK: Pattern matching (only when semantic unavailable)
        logger.debug("📋 Using pattern-based emotion detection (semantic unavailable)")
        query_clean = query.strip()
        
        for emotion, patterns in self._compiled_emotional.items():
            for pattern in patterns:
                if pattern.search(query_clean):
                    return emotion
        
        return None
    
    def _emotional_decision(
        self,
        query: str,
        emotional_state: str,
        context: Dict[str, Any]
    ) -> RoutingDecision:
        """
        PHASE 4 FIX: Emotion modulates response, doesn't change pipeline.
        
        Emotional queries now go through MULTI_AGENT with emotional context.
        The mentor agent uses this context to modulate tone and framing.
        """
        # PHASE 4: Emotion as SIGNAL, not TRIGGER
        # All emotions route to mentor with emotional context
        return RoutingDecision(
            pipeline=RecommendedPipeline.MULTI_AGENT,  # NOT EMOTIONAL_SUPPORT
            complexity=QueryComplexity.SIMPLE,
            confidence=0.85,
            reasoning=f"Emotional signal: {emotional_state} - mentor with emotional context",
            agents_to_activate=['mentor'],  # Mentor handles both emotion and content
            tools_to_enable=[],
            enable_verification=False,
            enable_visual=False,
            max_iterations=2,
            timeout_seconds=10.0,
            use_knowledge_graph=False,
            use_memory=True,  # Need memory for context
            priority_factors={'empathy': 1.0, 'support': 0.8},
            enable_agent_negotiation=False,
            extra_context={
                # PHASE 4: Emotional context for response modulation
                'emotional_context': {
                    'detected_emotion': emotional_state,
                    'modulate_response': True,
                    'prioritize_empathy': emotional_state in ['frustrated', 'anxious', 'confused', 'bored'],
                    'celebrate_success': emotional_state in ['excited', 'success', 'happy'],
                }
            }
        )
    
    def _is_trivial(self, query: str) -> bool:
        """
        Check if query is trivial (greetings, thanks, etc.)
        
        PHASE 1 NOTE: This method uses keyword patterns. When semantic analysis
        is available, it takes precedence. This is only for fallback.
        """
        query_clean = query.strip()
        
        # Very short queries (< 4 words) that match trivial patterns
        if len(query_clean.split()) <= 4:
            for pattern in self._compiled_trivial:
                if pattern.match(query_clean):
                    return True
        
        return False
    
    def _is_trivial_structural(self, query: str) -> bool:
        """
        PHASE 1 FIX: Structural trivial detection (no keywords).
        
        Uses message STRUCTURE, not content, to detect trivial messages:
        - Very short (1-2 words)
        - No question mark
        - No educational indicators
        
        This is safe because:
        - It doesn't decide WHAT kind of trivial (greeting vs thanks)
        - It only gates routing, not response content
        - The actual response is still generated by agents
        """
        query_clean = query.strip()
        word_count = len(query_clean.split())
        
        # Structural indicators only
        is_very_short = word_count <= 2
        no_question = '?' not in query_clean
        no_complex_punct = not any(c in query_clean for c in ['?', '!', '...', '"'])
        
        # Very short, no question = likely trivial
        # But don't be too aggressive - let semantic handle most cases
        return is_very_short and no_question and no_complex_punct
    
    def _trivial_decision(self, query: str) -> RoutingDecision:
        """Return fast-path decision for trivial queries"""
        return RoutingDecision(
            pipeline=RecommendedPipeline.FAST_RESPONSE,
            complexity=QueryComplexity.TRIVIAL,
            confidence=0.95,
            reasoning="Trivial query (greeting/acknowledgment) - fast response",
            agents_to_activate=['mentor'],  # Only mentor for greetings
            tools_to_enable=[],
            enable_verification=False,
            enable_visual=False,
            max_iterations=1,
            timeout_seconds=5.0,
            use_knowledge_graph=False,
            use_memory=True,  # 🔥 CHANGED: Always use memory for continuity!
            priority_factors={'speed': 1.0, 'depth': 0.0}
        )
    
    def _analyze_complexity(
        self, 
        query: str, 
        context: Dict[str, Any],
        semantic_analysis: Optional['SemanticAnalysis'] = None
    ) -> float:
        """
        Analyze query complexity on a 0-1 scale.
        
        PHASE 1 FIX: This now uses primarily STRUCTURAL analysis,
        not keyword patterns. Keyword patterns are hints only.
        
        STRUCTURAL Factors (safe, non-semantic):
        - Mathematical notation (equations, LaTeX, functions)
        - Query length
        - Multi-part structure (conjunctions)
        - Subject difficulty
        
        Keyword patterns are demoted to low-weight hints.
        """
        query_lower = query.lower()
        score = 0.3  # Base complexity for any educational query
        
        # STRUCTURAL Factor 1: Query length (longer = more complex)
        # This is structural, not semantic
        word_count = len(query.split())
        if word_count > 20:
            score += 0.15
        elif word_count > 10:
            score += 0.08
        
        # STRUCTURAL Factor 2: Mathematical notation (safe - detects symbols, not words)
        math_indicators = [
            r'\d+\s*[+\-*/^=]\s*\d+',  # Equations
            r'f\s*\(.*\)',  # Functions
            r'd[xy]/d[xy]',  # Derivatives
            r'∫|∑|∏',  # Math symbols
            r'\\frac|\\sqrt|\\int',  # LaTeX
            r'\^[0-9n]',  # Exponents
            r'[a-z]\s*=\s*[a-z0-9]',  # Variable assignments
        ]
        for pattern in math_indicators:
            if re.search(pattern, query, re.IGNORECASE):
                score += 0.2
                break
        
        # STRUCTURAL Factor 3: Multi-part structure (conjunction count)
        # This detects sentence structure, not semantic meaning
        conjunction_count = len(re.findall(r'\b(and|also|then|after|before|while)\b', query_lower))
        score += min(0.15, conjunction_count * 0.05)
        
        # STRUCTURAL Factor 4: Subject multiplier (based on domain complexity)
        subject = context.get('subject', 'general').lower()
        multiplier = self.SUBJECT_MULTIPLIERS.get(subject, 1.0)
        score *= multiplier
        
        # PHASE 1: Keyword patterns are HINTS only (heavily downweighted)
        # These should NOT determine routing, only provide minor signals
        # Weight: 0.1x instead of 0.3x (demoted by 3x)
        if not semantic_analysis or semantic_analysis.confidence < 0.6:
            for pattern, weight in self.COMPLEXITY_PATTERNS.items():
                if pattern in query_lower:
                    score += weight * 0.1  # Demoted from 0.3 to 0.1
        
        return min(1.0, score)
    
    async def _get_student_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get student-specific context for routing"""
        student_context = {
            'mastery_level': 50,  # Default moderate
            'recent_struggles': [],
            'preferred_depth': 'moderate',
            'visual_learner': False,
        }
        
        # Try to get from context
        if 'memory_context' in context:
            mem = context['memory_context']
            student_context['mastery_level'] = mem.get('mastery_level', 50)
            student_context['recent_struggles'] = mem.get('recent_struggles', [])
        
        if 'student_profile' in context:
            profile = context['student_profile']
            student_context['preferred_depth'] = profile.get('response_style', 'moderate')
            student_context['visual_learner'] = profile.get('visual_learner', False)
        
        # Try database lookup if available
        if self.db is not None and context.get('user_id'):
            try:
                user_doc = await self.db.users.find_one({"user_id": context['user_id']})
                if user_doc:
                    student_context['mastery_level'] = user_doc.get('overall_mastery', 50)
            except Exception as e:
                logger.debug(f"Could not fetch user context: {e}")
        
        return student_context
    
    def _score_to_complexity(
        self,
        score: float,
        student_context: Dict[str, Any]
    ) -> QueryComplexity:
        """Convert complexity score to level, adjusted for student"""
        
        # Adjust thresholds based on student mastery
        # Lower mastery = lower thresholds (things seem more complex)
        mastery = student_context.get('mastery_level', 50) / 100
        
        # Adjusted thresholds
        simple_threshold = 0.3 + (mastery * 0.1)  # 0.3-0.4
        moderate_threshold = 0.5 + (mastery * 0.1)  # 0.5-0.6
        complex_threshold = 0.7 + (mastery * 0.1)  # 0.7-0.8
        
        if score < simple_threshold:
            return QueryComplexity.SIMPLE
        elif score < moderate_threshold:
            return QueryComplexity.MODERATE
        elif score < complex_threshold:
            return QueryComplexity.COMPLEX
        else:
            return QueryComplexity.DEEP_REASONING
    
    def _select_pipeline(
        self,
        query: str,
        complexity: QueryComplexity,
        context: Dict[str, Any],
        student_context: Dict[str, Any],
        semantic_analysis: 'SemanticAnalysis' = None
    ) -> RoutingDecision:
        """Select the appropriate pipeline based on complexity"""

        query_lower = query.lower()
        subject = context.get('subject', 'General').lower()
        
        # Include semantic analysis in extra_context if available
        extra_ctx = {'semantic_analysis': semantic_analysis.to_dict()} if semantic_analysis else None
        
        # === SIMPLE QUERIES ===
        # Factual lookups, definitions - multi-agent but minimal negotiation
        if complexity == QueryComplexity.SIMPLE:
            return RoutingDecision(
                pipeline=RecommendedPipeline.MULTI_AGENT,
                complexity=complexity,
                confidence=0.8,
                reasoning="Simple query - multi-agent with light verification",
                agents_to_activate=['mentor', 'professor'],
                tools_to_enable=['knowledge_search'],
                enable_verification=True,
                enable_visual=student_context.get('visual_learner', False),
                max_iterations=3,
                timeout_seconds=15.0,
                use_knowledge_graph=True,
                use_memory=True,
                priority_factors={'speed': 0.6, 'depth': 0.4},
                enable_agent_negotiation=False  # Skip for speed on simple
            )
        
        # === MODERATE QUERIES ===
        # Standard explanations - full multi-agent WITH NEGOTIATION
        # THIS IS THE KEY CHANGE: Enable negotiation for moderate queries
        elif complexity == QueryComplexity.MODERATE:
            return RoutingDecision(
                pipeline=RecommendedPipeline.MULTI_AGENT,
                complexity=complexity,
                confidence=0.85,
                reasoning="Moderate complexity - multi-agent with negotiation for quality",
                agents_to_activate=['mentor', 'professor', 'visualise'],
                tools_to_enable=['knowledge_search', 'formula_lookup', 'fact_checker'],
                enable_verification=True,
                enable_visual=True,
                max_iterations=5,
                timeout_seconds=25.0,
                use_knowledge_graph=True,
                use_memory=True,
                priority_factors={'speed': 0.4, 'depth': 0.6},
                enable_agent_negotiation=True  # NEW: Enable negotiation
            )
        
        # === COMPLEX QUERIES ===
        # Multi-step problems - hybrid reasoning with full negotiation
        elif complexity == QueryComplexity.COMPLEX:
            visual_keywords = ['diagram', 'draw', 'visualize', 'show', 'graph', 'plot']
            needs_visual_sync = any(kw in query_lower for kw in visual_keywords)
            
            return RoutingDecision(
                pipeline=RecommendedPipeline.VISUAL_SYNC if needs_visual_sync else RecommendedPipeline.HYBRID_REASONING,
                complexity=complexity,
                confidence=0.9,
                reasoning="Complex query - hybrid reasoning with full agent negotiation",
                agents_to_activate=['mentor', 'professor', 'visualise', 'doubt_resolver'],
                tools_to_enable=['knowledge_search', 'formula_lookup', 'calculator', 'fact_checker', 'code_executor'],
                enable_verification=True,
                enable_visual=True,
                max_iterations=8,
                timeout_seconds=35.0,
                use_knowledge_graph=True,
                use_memory=True,
                priority_factors={'speed': 0.2, 'depth': 0.8},
                enable_agent_negotiation=True  # Full negotiation
            )
        
        # === DEEP REASONING ===
        # Proofs, derivations, analysis - full ReAct with negotiation
        else:  # DEEP_REASONING
            return RoutingDecision(
                pipeline=RecommendedPipeline.REACT_AGENTIC,
                complexity=complexity,
                confidence=0.95,
                reasoning="Deep reasoning - full ReAct with agent negotiation and verification",
                agents_to_activate=['mentor', 'professor', 'visualise', 'doubt_resolver', 'exam_coach'],
                tools_to_enable=['knowledge_search', 'formula_lookup', 'calculator', 'fact_checker', 'code_executor'],
                enable_verification=True,
                enable_visual=True,
                max_iterations=12,
                timeout_seconds=45.0,
                use_knowledge_graph=True,
                use_memory=True,
                priority_factors={'speed': 0.1, 'depth': 0.9},
                enable_agent_negotiation=True  # Full negotiation
            )
    
    def _resolve_continuation_topic(
        self,
        query: str,
        context: Dict[str, Any],
        semantic_analysis: 'SemanticAnalysis' = None
    ) -> Dict[str, Any]:
        """
        CONTINUATION RESOLVER — Detect short follow-up messages and inject previous topic.
        
        STRUCTURE-BASED detection (NOT keyword matching):
        1. word_count <= 4 OR message is a short follow-up question
        2. Message contains no clear new noun/topic (low content density)
        3. Previous turn was Education Lane OR previous_topic exists
        4. Previous topic available from context_pack/conversation_state
        
        Returns:
            {
                'is_continuation': bool,
                'topic': str or None,
                'reason': str
            }
        """
        # Extract message structure
        query_stripped = query.strip()
        words = query_stripped.split()
        word_count = len(words)
        
        # ================================================================
        # RULE 1: Check if message is short enough to be a continuation
        # ================================================================
        # Short messages (<=4 words) OR short question (<=6 words with ?)
        is_short_message = word_count <= 4
        is_short_question = word_count <= 6 and query_stripped.endswith('?')
        
        if not (is_short_message or is_short_question):
            return {'is_continuation': False, 'topic': None, 'reason': 'message_too_long'}
        
        # ================================================================
        # RULE 2: Check if message introduces a NEW topic (has clear noun)
        # ================================================================
        # If the message contains a clear educational noun, it's NOT a continuation
        # We detect this by checking if semantic_analysis found a topic
        if semantic_analysis and hasattr(semantic_analysis, 'topic_mentioned'):
            if semantic_analysis.topic_mentioned and len(semantic_analysis.topic_mentioned) > 3:
                # Semantic analysis found a topic - this is a NEW question
                return {'is_continuation': False, 'topic': None, 'reason': 'new_topic_detected'}
        
        # Also check for capitalized proper nouns (likely new topics)
        # Skip common words that aren't topics
        NON_TOPIC_WORDS = {'I', 'The', 'A', 'An', 'My', 'This', 'That', 'It', 'What', 'How', 
                          'Why', 'Can', 'Could', 'Please', 'More', 'Explain', 'Tell', 'Me'}
        proper_nouns = [w for w in words if len(w) > 1 and w[0].isupper() and w not in NON_TOPIC_WORDS]
        if proper_nouns:
            # Has proper nouns - this is a NEW topic, not a continuation
            return {'is_continuation': False, 'topic': None, 'reason': 'proper_noun_detected'}
        
        # Check for educational subject nouns (lower case) that indicate a new topic
        # These are common subject areas that override continuation
        SUBJECT_NOUNS = {
            'photosynthesis', 'thermodynamics', 'relativity', 'calculus', 'algebra',
            'geometry', 'trigonometry', 'gravity', 'momentum', 'energy', 'friction',
            'velocity', 'acceleration', 'force', 'atom', 'molecule', 'cell', 'dna',
            'evolution', 'genetics', 'respiration', 'digestion', 'circuit', 'electron'
        }
        query_lower = query_stripped.lower()
        found_subjects = [s for s in SUBJECT_NOUNS if s in query_lower]
        if found_subjects and word_count > 2:
            # Contains a subject noun and is more than 2 words - likely a NEW question
            return {'is_continuation': False, 'topic': None, 'reason': 'subject_noun_detected'}
        
        # ================================================================
        # RULE 3: Extract previous topic from context
        # ================================================================
        previous_topic = None
        
        # Try context_pack first (preferred)
        context_pack = context.get('context_pack')
        if context_pack:
            if hasattr(context_pack, 'current_topic') and context_pack.current_topic:
                previous_topic = context_pack.current_topic
            elif hasattr(context_pack, 'previous_topic') and context_pack.previous_topic:
                previous_topic = context_pack.previous_topic
        
        # Fallback to conversation_state
        if not previous_topic:
            conversation_state = context.get('conversation_state', {})
            previous_topic = conversation_state.get('last_topic', '')
        
        # Fallback to memory context
        if not previous_topic:
            memory_ctx = context.get('memory_context', {})
            previous_topic = memory_ctx.get('current_topic', '') or memory_ctx.get('last_topic', '')
        
        # ================================================================
        # RULE 4: Check if we have a previous topic to continue
        # ================================================================
        if not previous_topic:
            return {'is_continuation': False, 'topic': None, 'reason': 'no_previous_topic'}
        
        # ================================================================
        # SUCCESS: This is a continuation request
        # ================================================================
        return {
            'is_continuation': True,
            'topic': previous_topic,
            'reason': f'short_follow_up_{word_count}_words'
        }
    
    def should_use_agentic(self, decision: RoutingDecision) -> bool:
        """Check if decision requires agentic system"""
        return decision.pipeline in [
            RecommendedPipeline.MULTI_AGENT,
            RecommendedPipeline.REACT_AGENTIC,
            RecommendedPipeline.HYBRID_REASONING,
            RecommendedPipeline.VISUAL_SYNC
        ]


# Singleton instance
_routing_engine: Optional[IntelligentRoutingEngine] = None


def get_routing_engine(db=None) -> IntelligentRoutingEngine:
    """Get or create the routing engine"""
    global _routing_engine
    if _routing_engine is None:
        _routing_engine = IntelligentRoutingEngine(db)
    return _routing_engine


async def route_query(query: str, context: Dict[str, Any], db=None) -> RoutingDecision:
    """Convenience function to route a query"""
    engine = get_routing_engine(db)
    return await engine.route(query, context)

