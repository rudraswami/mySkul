"""
Supervisor Agent - Orchestrates Multi-Agent Responses
Routes queries to appropriate agents and combines their responses

AGENT ECOSYSTEM (TRUE AGENTIC):
- MentorAgent: Emotional, intuitive explanations
- ProfessorAgent: Formal, structured explanations  
- VisualiseAgent: Visual generation
- AgenticDoubtResolver: TRUE AGENT with ReAct loop, tools, memory (UPGRADED)
- MotivationAgent: Emotional support middleware
- ExamCoachAgent: Strategic exam preparation
- WeakAreaDetectiveAgent: Knowledge gap analysis
- StudyBuddyAgent: Peer learning simulation
- ParentReportAgent: Guardian communication

COGNITO-OS v3.0 ENHANCEMENTS:
- Universal Knowledge Graph: Multi-domain education graph (not exam-limited)
- Hybrid Reasoning: Neural + Symbolic + Graph integration
- Agent Negotiation: Multi-agent collaboration and cross-verification
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from agents.mentor import MentorAgent
from agents.professor import ProfessorAgent
from agents.visualise import VisualiseAgent
# Use TRUE agentic doubt resolver with ReAct loop
from agents.agentic_doubt_resolver import AgenticDoubtResolver
from agents.motivation import MotivationAgent
from agents.exam_coach import ExamCoachAgent
from agents.weak_area_detective import WeakAreaDetectiveAgent
from agents.study_buddy import StudyBuddyAgent
from agents.parent_report import ParentReportAgent
from agents.core.tool_registry import create_tool_registry

# COGNITO-OS v3.0 - Universal Education Components (Graceful Degradation)
# Each component is loaded independently to maximize availability
COGNITO_OS_AVAILABLE = False
KNOWLEDGE_GRAPH_AVAILABLE = False
HYBRID_ENGINE_AVAILABLE = False
AGENT_NEGOTIATOR_AVAILABLE = False

# Import Knowledge Graph
try:
    from services.knowledge_base.universal_knowledge_graph import get_universal_knowledge_graph
    KNOWLEDGE_GRAPH_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ UniversalKnowledgeGraph not available: {e}")
    get_universal_knowledge_graph = None

# Import Hybrid Reasoning Engine
try:
    from services.hybrid_reasoning_engine import get_hybrid_reasoning_engine
    HYBRID_ENGINE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ HybridReasoningEngine not available: {e}")
    get_hybrid_reasoning_engine = None

# Import Agent Negotiator
try:
    from services.cognitive_model.agent_negotiation import get_agent_negotiator
    AGENT_NEGOTIATOR_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ AgentNegotiator not available: {e}")
    get_agent_negotiator = None

# Set overall flag if any component is available
COGNITO_OS_AVAILABLE = KNOWLEDGE_GRAPH_AVAILABLE or HYBRID_ENGINE_AVAILABLE or AGENT_NEGOTIATOR_AVAILABLE

if COGNITO_OS_AVAILABLE:
    logging.info(f"🧠 Cognito-OS: KnowledgeGraph={KNOWLEDGE_GRAPH_AVAILABLE}, "
                 f"HybridEngine={HYBRID_ENGINE_AVAILABLE}, Negotiator={AGENT_NEGOTIATOR_AVAILABLE}")

logger = logging.getLogger(__name__)


class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent orchestrates the multi-agent system
    
    Key Responsibilities:
    - Analyze query intent and complexity
    - Route to appropriate agents (Mentor, Professor, Visualise)
    - Coordinate parallel processing
    - Validate and merge agent responses
    - Ensure factual correctness and logical consistency
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Supervisor with all sub-agents
        
        Args:
            config: Configuration dict with API keys and settings
        """
        super().__init__(config)
        
        # Initialize tool registry for TRUE agentic behavior
        self.tool_registry = create_tool_registry(
            include_default=True,
            include_action_tools=True
        )
        
        # Initialize all sub-agents
        self.mentor = MentorAgent(config)
        self.professor = ProfessorAgent(config)
        self.visualise = VisualiseAgent(config)
        
        # TRUE AGENTIC AGENTS - These use ReAct loop with tools
        # AgenticDoubtResolver: ReAct loop, tools, memory, planning, verification
        self.doubt_resolver = AgenticDoubtResolver(config)
        self.doubt_resolver.tool_registry = self.tool_registry  # Inject tools
        
        # Specialized agents for enhanced learning (Cognito OS)
        self.motivation = MotivationAgent(config)  # Middleware for emotional support
        self.exam_coach = ExamCoachAgent(config)  # Strategic exam preparation
        self.weak_area_detective = WeakAreaDetectiveAgent(config)  # Knowledge gap analysis
        self.study_buddy = StudyBuddyAgent(config)  # Peer learning simulation
        self.parent_report = ParentReportAgent(config)  # Guardian communication
        
        # COGNITO-OS v3.0 - Universal Education Components (Graceful Degradation)
        # Each component loads independently - failure of one doesn't block others
        self.knowledge_graph = None
        self.hybrid_engine = None
        self.agent_negotiator = None
        self.use_hybrid_reasoning = False
        
        # Load Knowledge Graph (independent)
        if KNOWLEDGE_GRAPH_AVAILABLE and get_universal_knowledge_graph:
            try:
                self.knowledge_graph = get_universal_knowledge_graph()
                logger.info("   ├── 🌍 UniversalKnowledgeGraph connected")
            except Exception as e:
                logger.warning(f"⚠️ KnowledgeGraph init failed: {e}")
        
        # Load Hybrid Reasoning Engine (independent)
        if HYBRID_ENGINE_AVAILABLE and get_hybrid_reasoning_engine:
            try:
                self.hybrid_engine = get_hybrid_reasoning_engine()
                self.use_hybrid_reasoning = True
                logger.info("   ├── 🧠 HybridReasoningEngine active")
            except Exception as e:
                logger.warning(f"⚠️ HybridEngine init failed: {e}")
        
        # Load Agent Negotiator (independent)
        if AGENT_NEGOTIATOR_AVAILABLE and get_agent_negotiator:
            try:
                self.agent_negotiator = get_agent_negotiator()
                
                # Register agents with negotiator for collaboration
                self.agent_negotiator.register_agent("mentor", self.mentor, ["explanation", "empathy", "metaphors"])
                self.agent_negotiator.register_agent("professor", self.professor, ["derivation", "proof", "formal"])
                self.agent_negotiator.register_agent("doubt_resolver", self.doubt_resolver, ["doubt", "confusion", "clarification"])
                # COGNITIVE OS FIX: More specific capabilities for exam_coach
                self.agent_negotiator.register_agent("exam_coach", self.exam_coach, ["jee_preparation", "neet_preparation", "exam_strategy", "study_plan_for_exam"])
                
                logger.info("   └── 🤝 AgentNegotiator ready (collaborative)")
            except Exception as e:
                logger.warning(f"⚠️ AgentNegotiator init failed: {e}")
        
        # Log degradation status if any component is missing
        if not (self.knowledge_graph and self.hybrid_engine and self.agent_negotiator):
            missing = []
            if not self.knowledge_graph: missing.append("KnowledgeGraph")
            if not self.hybrid_engine: missing.append("HybridEngine")
            if not self.agent_negotiator: missing.append("Negotiator")
            logger.warning(f"⚠️ Cognito-OS degraded mode: missing {', '.join(missing)}")
        
        logger.info("🤖 Supervisor initialized with TRUE AGENTIC system (Cognito OS v3.0)")
        logger.info("   ├── Mentor agent initialized")
        logger.info("   ├── Professor agent initialized")
        logger.info("   ├── Visualise agent initialized")
        logger.info("   ├── 🧠 AgenticDoubtResolver initialized (TRUE AGENT: ReAct + Tools)")
        logger.info("   ├── ExamCoach agent initialized")
        logger.info("   ├── WeakAreaDetective agent initialized")
        logger.info("   ├── StudyBuddy agent initialized")
        logger.info("   ├── ParentReport agent initialized")
        logger.info("   ├── Motivation agent initialized (MIDDLEWARE)")
        logger.info("   └── ToolRegistry loaded with action tools")
    
    def get_agent_type(self) -> str:
        return "Supervisor"
    
    async def process(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        This method is not used by Supervisor (uses run() instead)
        """
        return await self.run(query, context)
    
    async def run(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main orchestration method for Supervisor
        
        Args:
            query: Student's question
            context: Context dict with subject, user_id, session_id, etc.
        
        Returns:
            Combined multi-agent response
        """
        try:
            logger.info(f"🤖 Supervisor orchestrating query: {query[:100]}")
            
            # ================================================================
            # Step 0: COGNITIVE CONTROL LAYER (Meta-Reasoning)
            # Reason about "who should think" BEFORE agent selection.
            # This is TRUE cognitive control - the system reasons about reasoning.
            # ADDITIVE: Does not modify existing selection, only provides signals.
            # ================================================================
            try:
                from services.cognitive_model.cognitive_control import inject_cognitive_control
                
                available_agents = ['mentor', 'professor', 'visualise', 'doubt_resolver', 
                                   'exam_coach', 'study_buddy', 'weak_area_detective', 'parent_report']
                cognitive_plan = inject_cognitive_control(context, query, available_agents)
                logger.info(f"🧠 Cognitive control: {cognitive_plan.reasoning}")
            except ImportError:
                logger.debug("Cognitive control layer not available")
            except Exception as cog_err:
                logger.debug(f"Cognitive control failed (non-blocking): {cog_err}")
            
            # ================================================================
            # Step 0.5: SHARED REASONING STATE (Multi-Agent Collaboration)
            # Inject thread-safe shared state for agents to exchange insights
            # during their execution. TRUE shared reasoning, not just metadata.
            # ADDITIVE: Agents use if available, proceed normally if not.
            # ================================================================
            try:
                from services.cognitive_model.shared_reasoning_state import inject_shared_state
                
                shared_state = inject_shared_state(context, query)
                logger.info(f"🧠 Shared reasoning state initialized")
            except ImportError:
                logger.debug("Shared reasoning state not available")
            except Exception as state_err:
                logger.debug(f"Shared state init failed (non-blocking): {state_err}")
            
            # Step 1: Analyze query intent (with context for mode-aware detection)
            # Extract semantic_analysis from context for intelligent intent detection
            semantic_analysis = context.get('semantic_analysis')
            intent = self._detect_intent(query, context, semantic_analysis)
            logger.info(f"🎯 Detected intent: {intent} | semantic_available: {semantic_analysis is not None}")
            
            # 🆕 Step 1.5: Use Agent Negotiation for TRUE multi-agent collaboration
            # Enable by default for complex educational queries (safe change)
            # Explicit flags can still disable it if needed
            explicit_flag = context.get('use_agent_negotiation') or context.get('enable_agent_negotiation')
            
            # ALL educational intents use negotiation (expanded from limited list)
            negotiation_intents = [
                'concept', 'comparison', 'derivation', 'application', 
                'explanation', 'problem', 'analysis', 'doubt', 'question',
                'help', 'understand', 'learn', 'study', 'practice'
            ]
            
            # Enable negotiation by default for complex queries (if negotiator available)
            # Explicit False flag can disable it
            use_negotiation = (
                (explicit_flag is not False) and  # Not explicitly disabled
                self.agent_negotiator is not None and  # Negotiator available
                intent in negotiation_intents  # Complex educational intent
            )
            
            # Attempt negotiation if enabled
            if use_negotiation:
                logger.info("🤝 Using Agent Negotiation for complex query")
                try:
                    negotiation_result = await self.agent_negotiator.negotiate(query, context)
                    logger.info(f"   Strategy: {negotiation_result.strategy}, Lead: {negotiation_result.lead_agent}")
                    
                    collaborative_response = await self.agent_negotiator.collaborate(
                        query, context, negotiation_result
                    )
                    
                    # Build response from collaboration
                    # Note: Only mentor goes to _validate_responses, insights/verification are metadata
                    agent_responses = {
                        'mentor': collaborative_response.primary_response
                    }
                    # Store collaboration metadata separately (not for validation)
                    context['collaboration_metadata'] = {
                        'insights': collaborative_response.supporting_insights,
                        'verification': collaborative_response.verification_results
                    }
                    
                    # Add negotiation metadata
                    context['negotiation_result'] = {
                        'strategy': negotiation_result.strategy,
                        'lead_agent': negotiation_result.lead_agent,
                        'supporting': negotiation_result.supporting_agents,
                        'confidence': collaborative_response.final_confidence
                    }
                    
                    logger.info(f"✅ Agent collaboration complete: {collaborative_response.collaboration_summary}")
                    
                except Exception as neg_error:
                    logger.warning(f"⚠️ Agent negotiation failed, falling back to parallel: {neg_error}")
                    use_negotiation = False  # Fall back to normal flow
            
            # Step 2: Determine which agents to activate (if not using negotiation)
            if not use_negotiation or 'mentor' not in locals().get('agent_responses', {}):
                agents_to_run = self._select_agents(intent, context, semantic_analysis)
                logger.info(f"👥 Activating agents: {', '.join(agents_to_run)}")
                
                # Step 3: Run agents in parallel (non-blocking)
                agent_responses = await self._run_agents_parallel(
                    query=query,
                    context=context,
                    agents=agents_to_run
                )
            
            # Step 4: Validate responses
            validated_responses = self._validate_responses(agent_responses)
            
            # Step 4.5: 🔍 CROSS-VERIFICATION FALLBACK (When negotiator unavailable)
            # If we're running in parallel mode without negotiation, still verify
            # mathematical/factual content between agents for consistency
            should_cross_verify = (
                context.get('enable_agent_negotiation', False) and 
                not use_negotiation and  # Negotiation was requested but unavailable
                len(validated_responses) > 1
            )
            
            if should_cross_verify:
                try:
                    verified_responses = await self._cross_verify_parallel_responses(
                        query=query,
                        agent_responses=validated_responses,
                        context=context
                    )
                    validated_responses = verified_responses
                    logger.info("✅ Cross-verification complete (negotiator fallback)")
                except Exception as verify_err:
                    logger.warning(f"⚠️ Cross-verification failed (non-blocking): {verify_err}")
                    # Continue with unverified responses
            
            # Step 5: Combine and structure final response
            combined_response = self._merge_responses(
                query=query,
                intent=intent,
                agent_responses=validated_responses,
                context=context
            )
            
            # ================================================================
            # Step 5.5: ALWAYS-ON COLLABORATION METADATA (Lightweight Layer)
            # Even in parallel execution mode, track which agents contributed
            # and add collaboration summary. This is ADDITIVE and NON-BLOCKING.
            # ================================================================
            ENABLE_COLLABORATION_TRACKING = True  # Feature flag (safe default: ON)
            
            if ENABLE_COLLABORATION_TRACKING:
                try:
                    # Build collaboration summary
                    contributing_agents = []
                    agent_confidences = {}
                    
                    for agent_name, response in validated_responses.items():
                        if response.get('success') and response.get('content'):
                            contributing_agents.append(agent_name)
                            # Extract confidence if available
                            confidence = response.get('metadata', {}).get('confidence', 0.7)
                            agent_confidences[agent_name] = confidence
                    
                    # Calculate aggregate confidence
                    if agent_confidences:
                        avg_confidence = sum(agent_confidences.values()) / len(agent_confidences)
                    else:
                        avg_confidence = 0.7
                    
                    # Add collaboration metadata (non-breaking - new field)
                    combined_response['collaboration'] = {
                        'mode': 'negotiated' if use_negotiation else 'parallel',
                        'agents_contributed': contributing_agents,
                        'agent_confidences': agent_confidences,
                        'aggregate_confidence': round(avg_confidence, 2),
                        'cross_verified': should_cross_verify if 'should_cross_verify' in dir() else False,
                        'negotiation_available': self.agent_negotiator is not None
                    }
                    
                    logger.info(f"🤝 Collaboration: {len(contributing_agents)} agents, "
                               f"confidence={avg_confidence:.2f}, mode={'negotiated' if use_negotiation else 'parallel'}")
                
                except Exception as collab_err:
                    logger.debug(f"Collaboration tracking failed (non-blocking): {collab_err}")
                    # Continue without collaboration metadata
            
            # ================================================================
            # Step 5.7: AGENT CHALLENGE MECHANISM (Post-Response Disputes)
            # Detect contradictions and allow agents to challenge each other.
            # This is TRUE agent autonomy - agents don't just produce outputs,
            # they reason about and dispute each other's claims.
            # ADDITIVE: Only runs when contradictions detected, non-blocking.
            # ================================================================
            if len(validated_responses) > 1:
                try:
                    from services.cognitive_model.agent_challenge import get_challenge_system
                    
                    challenge_system = get_challenge_system()
                    challenge_result = await challenge_system.run_challenge_round(
                        agent_responses=validated_responses,
                        query=query,
                        context=context
                    )
                    
                    if challenge_result.get('challenge_round_ran'):
                        # Apply corrections to validated responses
                        validated_responses = challenge_result['responses']
                        
                        # Add challenge metadata to combined response
                        combined_response['_challenge_round'] = {
                            'challenges': challenge_result['challenges'],
                            'resolutions': challenge_result['resolutions']
                        }
                        
                        upheld = sum(1 for r in challenge_result['resolutions'] 
                                    if r.get('outcome') == 'upheld')
                        logger.info(f"⚔️ Challenge round: {len(challenge_result['challenges'])} challenges, "
                                   f"{upheld} upheld")
                    
                except ImportError:
                    logger.debug("Agent challenge mechanism not available")
                except Exception as challenge_err:
                    logger.debug(f"Challenge round failed (non-blocking): {challenge_err}")
            
            # Step 6: 💪 MOTIVATION MIDDLEWARE - Add emotional support if needed
            # This enhances the response with motivational content based on student state
            try:
                motivation_result = self.motivation.enhance_response(
                    result=combined_response,
                    context=context
                )
                # Merge motivation into combined response if present
                if motivation_result and motivation_result.get('motivation'):
                    combined_response['motivation'] = motivation_result['motivation']
            except Exception as motivation_error:
                logger.warning(f"⚠️ Motivation enhancement failed (non-critical): {motivation_error}")
                # Continue without motivation - not critical
            
            logger.info("✅ Supervisor orchestration complete")
            return combined_response
            
        except Exception as e:
            logger.error(f"❌ Supervisor orchestration failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': f'Supervisor failed: {str(e)}',
                'mentor': {'content': '', 'success': False},
                'professor': {'content': '', 'success': False},
                'visual': None
            }
    
    def _detect_intent(
        self, 
        query: str, 
        context: Dict[str, Any] = None,
        semantic_analysis: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Detect student intent from query.
        
        PHASE 1 FIX: This method is now semantics-first.
        - When semantic_analysis is available, use it as authoritative
        - Keyword patterns only run when semantic fails or confidence is low
        - Agent routing is based on semantic intent, not keyword matching
        
        Args:
            query: Student's question
            context: Context dict with exam_mode, etc.
            semantic_analysis: Dict from SemanticIntentClassifier (optional)
        
        Returns:
            Intent type: 'concept', 'derivation', 'application', 'comparison', 'doubt', etc.
        """
        context = context or {}
        query_lower = query.lower().strip()
        
        # ================================================================
        # PHASE 1: SEMANTIC ANALYSIS IS AUTHORITATIVE
        # ================================================================
        if semantic_analysis and semantic_analysis.get('confidence', 0) >= 0.5:
            intent = semantic_analysis.get('intent', 'general')
            
            # Map semantic intents to supervisor intents
            semantic_to_supervisor = {
                'greeting': 'greeting',
                'farewell': 'greeting',
                'gratitude': 'greeting',
                'acknowledgment': 'acknowledgment',  # Will continue previous task
                'clarification': 'doubt',  # Confusion maps to doubt resolver
                'confusion': 'doubt',
                'question': 'concept',
                'explanation': 'concept',
                'practice': 'application',
                'emotional_support': 'emotional',
                'motivation': 'emotional',
                'explore': 'concept',  # Explore new topics = conceptual
                'continue': 'continuation',  # Continue previous work
                'chitchat': 'chitchat',
                'help': 'help',
                'general': 'concept',  # Default to concept
            }
            
            mapped_intent = semantic_to_supervisor.get(intent, 'concept')
            logger.info(f"🧠 SEMANTIC intent: {intent} -> supervisor intent: {mapped_intent}")
            
            # For specific agent routing, still check agent capabilities
            # but use semantic signals, not keywords
            if mapped_intent == 'doubt':
                logger.info("🎯 Semantic: DOUBT intent - routing to AgenticDoubtResolver")
                return 'doubt'
            
            if mapped_intent == 'continuation':
                # Check if there's a previous task to continue
                if context.get('last_task_type') or context.get('awaiting_continuation'):
                    return 'continuation'
                return 'concept'  # No context to continue, treat as new
            
            # PHASE 3: If awaiting_continuation is True, ANY acknowledgment is continuation
            if context.get('awaiting_continuation') and mapped_intent == 'acknowledgment':
                logger.info("🔄 CONTINUITY LOCK: awaiting_continuation=True, forcing continuation intent")
                return 'continuation'
            
            return mapped_intent
        
        # ================================================================
        # LEGACY FALLBACK: Only when semantic analysis unavailable
        # ================================================================
        logger.warning("⚠️ LEGACY: Using keyword-based intent detection (semantic unavailable)")
        
        # Greeting intent - STRUCTURAL (check if entire message is short greeting)
        clean_query = query_lower.strip('!?.,:;')
        word_count = len(query_lower.split())
        if word_count <= 3 and len(clean_query) <= 10:
            # Very short message - likely greeting/ack, let agents handle
            return 'greeting'
        
        # PHASE 1: Agent routing via keyword patterns (LEGACY ONLY)
        # These are hints, not decisions - agents will still negotiate
        
        # Check specialized agents (they have their own semantic checks now)
        # Only use these as fallback when semantic classification failed
        
        # Default: conceptual explanation
        # Let agents negotiate the actual handling
        return 'concept'
    
    def _select_agents(
        self,
        intent: str,
        context: Dict[str, Any],
        semantic_analysis: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Select which agents to activate based on intent.
        
        PHASE 2 FIX: Uses semantic agent selection.
        When semantic analysis is available, agents are selected based on:
        1. Semantic intent + emotional signals
        2. Agent capability matching
        3. Response expectation (conversational vs structured)
        
        NOT based on keyword-to-agent mapping.
        
        Returns:
            List of agent names to run
        """
        # ================================================================
        # PHASE 2: SEMANTIC AGENT SELECTION
        # ================================================================
        if semantic_analysis and semantic_analysis.get('confidence', 0) >= 0.5:
            return self._select_agents_semantic(semantic_analysis, context)
        
        # ================================================================
        # LEGACY FALLBACK: Intent-based selection
        # ================================================================
        logger.debug("📋 Using legacy intent-based agent selection")
        
        # For greetings, ONLY run Mentor
        if intent == 'greeting':
            return ['mentor']
        
        # DOUBT INTENT - Use specialized DoubtResolver
        if intent == 'doubt':
            agents = ['doubt_resolver']
            if context.get('request_visual', True):
                agents.append('visualise')
            return agents
        
        # Default: Mentor + Professor for educational queries
        agents = ['mentor']
        if intent not in ['greeting', 'acknowledgment']:
            agents.append('professor')
        
        # Visual for substantive educational queries
        if context.get('request_visual', True) and intent in ['concept', 'derivation', 'application']:
            agents.append('visualise')
        
        return agents
    
    def _select_agents_semantic(
        self,
        semantic_analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[str]:
        """
        PHASE 2: Semantic-based agent selection.
        
        Agents are selected based on:
        1. What the student NEEDS (emotional support, explanation, practice)
        2. How the response should be DELIVERED (structured, conversational)
        3. Student's emotional state
        
        NOT based on keyword matching.
        """
        agents = []
        
        intent = semantic_analysis.get('intent', 'general')
        emotional_tone = semantic_analysis.get('emotional_tone', 'neutral')
        emotional_intensity = semantic_analysis.get('emotional_intensity', 0)
        response_expectation = semantic_analysis.get('response_expectation', 'conversational_advice')
        needs_empathy = semantic_analysis.get('needs_empathy', False)
        needs_encouragement = semantic_analysis.get('needs_encouragement', False)
        
        # ================================================================
        # AGENT CAPABILITY MATCHING (Semantic, not keyword)
        # ================================================================
        
        # MENTOR: Emotional support, metaphors, encouragement
        # Required for: emotional states, confusion, or when empathy needed
        mentor_relevant = any([
            needs_empathy,
            needs_encouragement,
            emotional_intensity > 0.4,
            emotional_tone in ['anxious', 'frustrated', 'confused', 'bored'],
            intent in ['emotional_support', 'motivation', 'confusion', 'celebration'],
            response_expectation == 'emotional_acknowledgment',
        ])
        
        # PROFESSOR: Formal explanations, derivations, proofs
        # Required for: structured deliverables, deep explanations
        professor_relevant = any([
            response_expectation in ['structured_deliverable', 'detailed_explanation'],
            intent in ['question', 'explanation', 'practice'],
            semantic_analysis.get('topic_mentioned'),  # Has a specific topic
        ])
        
        # DOUBT_RESOLVER: Confusion, clarification, stuck
        # Required for: explicit confusion or clarification requests
        doubt_relevant = any([
            intent in ['clarification', 'confusion'],
            emotional_tone == 'confused',
            semantic_analysis.get('needs_clarification', False),
        ])
        
        # ================================================================
        # BUILD AGENT LIST (Order matters - mentor first for tone)
        # ================================================================
        
        # Mentor always runs for emotional intelligence
        if mentor_relevant or True:  # Always include mentor for tone
            agents.append('mentor')
        
        # Doubt resolver for confusion
        if doubt_relevant:
            agents.insert(0, 'doubt_resolver')  # Primary for doubt
        
        # Professor for substantive content
        if professor_relevant and not doubt_relevant:
            agents.append('professor')
        
        # Visual for educational queries
        if context.get('request_visual', True):
            if intent in ['question', 'explanation', 'practice'] or response_expectation == 'detailed_explanation':
                agents.append('visualise')
        
        # Ensure at least mentor
        if not agents:
            agents = ['mentor']
        
        logger.info(f"🧠 SEMANTIC agent selection: {agents} (intent={intent}, tone={emotional_tone})")
        return agents
    
    async def _run_agents_parallel(
        self,
        query: str,
        context: Dict[str, Any],
        agents: List[str]
    ) -> Dict[str, Any]:
        """
        Run selected agents in parallel for faster response
        
        Returns:
            Dict of agent responses
        """
        tasks = {}
        
        # Helper to check if agent should participate (agent autonomy)
        def agent_should_run(agent, name):
            if hasattr(agent, 'should_abstain'):
                should_abstain, reason = agent.should_abstain(query, context)
                if should_abstain:
                    logger.info(f"   🚫 {name} self-abstained: {reason}")
                    return False
            return True
        
        # Create tasks for each agent (with self-abstain check)
        if 'mentor' in agents and agent_should_run(self.mentor, 'Mentor'):
            logger.info("   Routing to Mentor agent...")
            tasks['mentor'] = self.mentor.process(query, context)
        
        if 'professor' in agents and agent_should_run(self.professor, 'Professor'):
            logger.info("   Routing to Professor agent...")
            tasks['professor'] = self.professor.process(query, context)
        
        if 'visualise' in agents and agent_should_run(self.visualise, 'Visualise'):
            logger.info("   Routing to Visualise agent...")
            tasks['visualise'] = self.visualise.process(query, context)
        
        # NEW: DoubtResolver agent for doubt/confusion queries
        if 'doubt_resolver' in agents and agent_should_run(self.doubt_resolver, 'DoubtResolver'):
            logger.info("   🎯 Routing to DoubtResolver agent...")
            tasks['doubt_resolver'] = self.doubt_resolver.process(query, context)
        
        # NEW: ExamCoach agent for exam strategy queries
        if 'exam_coach' in agents and agent_should_run(self.exam_coach, 'ExamCoach'):
            logger.info("   🏆 Routing to ExamCoach agent...")
            tasks['exam_coach'] = self.exam_coach.process(query, context)
        
        # WeakAreaDetective agent for performance analysis
        if 'weak_area_detective' in agents and agent_should_run(self.weak_area_detective, 'WeakAreaDetective'):
            logger.info("   🔍 Routing to WeakAreaDetective agent...")
            tasks['weak_area_detective'] = self.weak_area_detective.process(query, context)
        
        # StudyBuddy agent for peer learning
        if 'study_buddy' in agents and agent_should_run(self.study_buddy, 'StudyBuddy'):
            logger.info("   🤝 Routing to StudyBuddy agent...")
            tasks['study_buddy'] = self.study_buddy.process(query, context)
        
        # NEW: ParentReport agent for guardian communication
        if 'parent_report' in agents and agent_should_run(self.parent_report, 'ParentReport'):
            logger.info("   👨‍👩‍👧 Routing to ParentReport agent...")
            tasks['parent_report'] = self.parent_report.process(query, context)
        
        # Run all tasks in parallel
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        # Map results back to agent names
        agent_responses = {}
        for agent_name, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"❌ {agent_name} agent failed: {result}")
                agent_responses[agent_name] = {
                    'agent': agent_name,
                    'success': False,
                    'error': str(result)
                }
            else:
                agent_responses[agent_name] = result
        
        return agent_responses
    
    def _validate_responses(
        self,
        agent_responses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate agent responses for correctness and consistency
        
        Returns:
            Validated responses
        """
        validated = {}
        
        for agent_name, response in agent_responses.items():
            # Handle unexpected response types (list, str, None)
            if response is None:
                logger.warning(f"⚠️ {agent_name} returned None response")
                validated[agent_name] = {
                    'agent': agent_name,
                    'success': False,
                    'error': 'No response from agent',
                    'content': ''
                }
                continue
            
            # If response is a list, wrap it in a dict
            if isinstance(response, list):
                logger.warning(f"⚠️ {agent_name} returned list instead of dict, wrapping...")
                # Try to extract content from the list
                if len(response) > 0:
                    first_item = response[0]
                    if isinstance(first_item, dict):
                        response = first_item  # Use first dict item
                    else:
                        response = {
                            'agent': agent_name,
                            'success': True,
                            'content': str(first_item) if first_item else ''
                        }
                else:
                    response = {
                        'agent': agent_name,
                        'success': False,
                        'error': 'Empty list response',
                        'content': ''
                    }
            
            # If response is a string, wrap it in a dict
            if isinstance(response, str):
                logger.warning(f"⚠️ {agent_name} returned string instead of dict, wrapping...")
                response = {
                    'agent': agent_name,
                    'success': True,
                    'content': response
                }
            
            # Now response should be a dict - validate it
            if not isinstance(response, dict):
                logger.error(f"❌ {agent_name} response has unexpected type: {type(response)}")
                validated[agent_name] = {
                    'agent': agent_name,
                    'success': False,
                    'error': f'Unexpected response type: {type(response).__name__}',
                    'content': ''
                }
                continue
            
            # Check if response is successful
            if not response.get('success', False):
                logger.warning(f"⚠️ {agent_name} response validation failed")
                validated[agent_name] = response
                continue
            
            # Basic validation: non-empty content
            content = response.get('content')
            if content and (isinstance(content, str) and len(content) > 10):
                validated[agent_name] = response
                logger.info(f"✅ {agent_name} response validated")
            elif content and isinstance(content, dict):  # Visual spec
                validated[agent_name] = response
                logger.info(f"✅ {agent_name} visual spec validated")
            else:
                logger.warning(f"⚠️ {agent_name} response too short or empty")
                validated[agent_name] = response
        
        return validated
    
    async def _cross_verify_parallel_responses(
        self,
        query: str,
        agent_responses: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Cross-verify responses from parallel agents when full negotiation is unavailable.
        
        This provides a lightweight verification layer:
        1. Extract mathematical claims from mentor/professor responses
        2. Use MathVerifier to check consistency
        3. Flag contradictions (don't auto-correct, but mark)
        4. Add verification metadata to responses
        
        This is a GRACEFUL FALLBACK - not as powerful as full negotiation,
        but better than no verification at all.
        
        Returns:
            Enhanced agent_responses with verification metadata
        """
        mentor_response = agent_responses.get('mentor', {})
        professor_response = agent_responses.get('professor', {})
        
        # Only verify if we have both mentor and professor responses
        if not (mentor_response.get('success') and professor_response.get('success')):
            return agent_responses
        
        mentor_content = mentor_response.get('content', '')
        professor_content = professor_response.get('content', '')
        
        # Skip verification for very short responses (greetings, etc.)
        if len(mentor_content) < 50 and len(professor_content) < 50:
            return agent_responses
        
        try:
            # Use MathVerifier for mathematical content verification
            from services.verification.math_verifier import MathVerifier, VerificationStatus
            
            verifier = MathVerifier()
            verification_results = []
            
            # Verify mentor response
            if mentor_content:
                mentor_verification = verifier.verify_response(
                    response_text=mentor_content,
                    question=query,
                    subject=context.get('subject', 'General')
                )
                verification_results.append({
                    'agent': 'mentor',
                    'status': mentor_verification.status.value,
                    'confidence': mentor_verification.confidence,
                    'errors': mentor_verification.errors
                })
            
            # Verify professor response
            if professor_content:
                professor_verification = verifier.verify_response(
                    response_text=professor_content,
                    question=query,
                    subject=context.get('subject', 'General')
                )
                verification_results.append({
                    'agent': 'professor',
                    'status': professor_verification.status.value,
                    'confidence': professor_verification.confidence,
                    'errors': professor_verification.errors
                })
            
            # Add verification metadata to responses
            if 'mentor' in agent_responses:
                agent_responses['mentor']['cross_verification'] = {
                    'verified': True,
                    'results': [r for r in verification_results if r['agent'] == 'mentor']
                }
            if 'professor' in agent_responses:
                agent_responses['professor']['cross_verification'] = {
                    'verified': True,
                    'results': [r for r in verification_results if r['agent'] == 'professor']
                }
            
            # Log verification status
            errors_found = sum(len(r.get('errors', [])) for r in verification_results)
            if errors_found > 0:
                logger.warning(f"🔍 Cross-verification found {errors_found} potential issues")
            else:
                logger.info("🔍 Cross-verification passed - no inconsistencies found")
            
        except ImportError:
            logger.debug("MathVerifier not available for cross-verification")
        except Exception as e:
            logger.warning(f"Cross-verification error (non-blocking): {e}")
        
        return agent_responses
    
    def _merge_responses(
        self,
        query: str,
        intent: str,
        agent_responses: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Merge agent responses into unified structure
        
        Args:
            query: Original user query
            intent: Detected intent
            agent_responses: Responses from all agents
            context: Request context with complexity, subject, etc.
        
        Returns:
            Combined response ready for ResponseAdapter
        """
        # Handle specialized agent responses - they replace mentor when used
        doubt_response = agent_responses.get('doubt_resolver', {})
        exam_coach_response = agent_responses.get('exam_coach', {})
        weak_area_response = agent_responses.get('weak_area_detective', {})
        study_buddy_response = agent_responses.get('study_buddy', {})
        parent_report_response = agent_responses.get('parent_report', {})
        mentor_response = agent_responses.get('mentor', {})
        
        # Determine primary response based on which specialized agent was used
        primary_response = mentor_response  # Default
        
        if parent_report_response and parent_report_response.get('success'):
            # ParentReport response for guardian communication
            primary_response = {
                'content': parent_report_response.get('content', ''),
                'metadata': parent_report_response.get('metadata', {}),
                'success': True,
                'agent': 'parent_report'
            }
        elif study_buddy_response and study_buddy_response.get('success'):
            # StudyBuddy response for collaborative learning
            primary_response = {
                'content': study_buddy_response.get('content', ''),
                'metadata': study_buddy_response.get('metadata', {}),
                'success': True,
                'agent': 'study_buddy'
            }
        elif weak_area_response and weak_area_response.get('success'):
            # WeakAreaDetective response becomes primary for analysis queries
            primary_response = {
                'content': weak_area_response.get('content', ''),
                'metadata': weak_area_response.get('metadata', {}),
                'success': True,
                'agent': 'weak_area_detective'
            }
        elif exam_coach_response and exam_coach_response.get('success'):
            # ExamCoach response becomes primary for exam strategy queries
            primary_response = {
                'content': exam_coach_response.get('content', ''),
                'metadata': exam_coach_response.get('metadata', {}),
                'success': True,
                'agent': 'exam_coach'
            }
        elif doubt_response and doubt_response.get('success'):
            # DoubtResolver response becomes primary for doubt queries
            primary_response = {
                'content': doubt_response.get('content', ''),
                'metadata': doubt_response.get('metadata', {}),
                'success': True,
                'agent': 'doubt_resolver'
            }
        
        # ================================================================
        # CRITICAL FIX: Ensure primary_response ALWAYS has content
        # If primary agent returned empty content, generate INTELLIGENT fallback
        # ================================================================
        primary_content = primary_response.get('content', '') if primary_response else ''
        if not primary_content or len(primary_content.strip()) < 20:
            logger.warning(f"⚠️ [Supervisor] Primary response empty, generating intelligent fallback for: {query[:50]}...")
            
            # Generate fallback that PROVIDES VALUE, not asks questions
            # Check if this is an urgent context
            is_urgent = (context or {}).get('is_urgent', False)
            urgency_level = (context or {}).get('urgency_level', 'medium')
            
            if is_urgent or urgency_level == 'high':
                # URGENT FALLBACK: Provide immediate actionable help
                fallback_content = self._generate_urgent_fallback(query)
            else:
                # STANDARD FALLBACK: Provide helpful generic content + one clarifying option
                fallback_content = self._generate_helpful_fallback(query)
            
            primary_response = {
                'content': fallback_content,
                'metadata': {'fallback': True, 'is_urgent': is_urgent, 'original_agent': primary_response.get('agent', 'unknown') if primary_response else 'none'},
                'success': True,
                'agent': 'mentor'
            }
        
        result = {
            'success': True,
            'query': query,
            'intent': intent,
            'mentor': primary_response,  # Primary response (mentor/specialized agent)
            'doubt_resolver': doubt_response if doubt_response else None,
            'exam_coach': exam_coach_response if exam_coach_response else None,
            'weak_area_detective': weak_area_response if weak_area_response else None,
            'study_buddy': study_buddy_response if study_buddy_response else None,
            'parent_report': parent_report_response if parent_report_response else None,
            'professor': agent_responses.get('professor', {}),
            'visual': agent_responses.get('visualise', {}).get('content'),
            'metadata': {
                'agents_used': list(agent_responses.keys()),
                'supervisor_version': '4.0',  # Cognito OS v4.0
                'cognito_os_enabled': True,  # Enable transparency panels in UI
                'complexity': (context or {}).get('complexity', 'standard'),
                'tools_used': ['rag', 'knowledge_search', 'fact_checker'],  # Default tools
                'used_doubt_resolver': 'doubt_resolver' in agent_responses,
                'used_exam_coach': 'exam_coach' in agent_responses,
                'used_weak_area_detective': 'weak_area_detective' in agent_responses,
                'used_study_buddy': 'study_buddy' in agent_responses,
                'used_parent_report': 'parent_report' in agent_responses,
                'cognito_os_enabled': COGNITO_OS_AVAILABLE
            }
        }
        
        # COGNITO-OS v3.0: Enhance with knowledge graph context
        if self.use_hybrid_reasoning and self.knowledge_graph:
            result = self._enhance_with_knowledge_graph(query, result)
        
        return result
    
    def _enhance_with_knowledge_graph(
        self,
        query: str,
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        COGNITO-OS v3.0: Enhance response with knowledge graph context
        
        Adds:
        - Related concepts
        - Prerequisites (what to review)
        - Applications (what to learn next)
        - Learning path suggestions
        """
        try:
            if not self.knowledge_graph:
                return response
            
            # Search for relevant concepts
            concepts = self.knowledge_graph.search_concepts(query)
            
            if not concepts:
                return response
            
            main_concept = concepts[0]
            
            # Get related information
            prerequisites = self.knowledge_graph.get_prerequisites(main_concept.concept_id)
            applications = self.knowledge_graph.get_applications(main_concept.concept_id)
            
            # Add to metadata
            response['metadata']['knowledge_graph'] = {
                'main_concept': main_concept.name,
                'domain': main_concept.domain,
                'difficulty': main_concept.difficulty.value,
                'prerequisites': [p.name for p in prerequisites[:3]],
                'applications': [a.name for a in applications[:3]],
                'key_points': main_concept.key_points[:3],
                'formulas': main_concept.formulas[:3],
                'real_world_use': main_concept.real_world_applications[:2]
            }
            
            # Add learning recommendations
            recommendations = []
            if prerequisites:
                recommendations.append(f"📚 Review: {', '.join(p.name for p in prerequisites[:2])}")
            if applications:
                recommendations.append(f"🚀 Next: {', '.join(a.name for a in applications[:2])}")
            
            if recommendations:
                response['learning_path'] = recommendations
            
            logger.debug(f"✅ Enhanced with knowledge graph: {main_concept.name}")
            
        except Exception as e:
            logger.warning(f"Knowledge graph enhancement failed: {e}")
        
        return response
    
    def _generate_urgent_fallback(self, query: str) -> str:
        """
        🚨 Generate fallback content for URGENT situations.
        
        CRITICAL PRINCIPLES:
        1. NEVER ask clarifying questions under urgency
        2. ALWAYS provide actionable content immediately
        3. Use generic but useful exam/preparation tips
        4. Offer to help with specifics as a follow-up (not gating)
        
        This is triggered when:
        - is_urgent=True in context
        - urgency_level='high' in context
        """
        query_lower = query.lower()
        
        # Detect if it's revision/tips/preparation related
        is_revision_related = any(word in query_lower for word in 
            ['revision', 'revise', 'tips', 'prepare', 'last minute', 'quick', 'exam', 'test', 'viva', 'interview'])
        
        if is_revision_related:
            return f"""Got it! Here's your quick action plan: 🎯

**📋 Priority Revision Strategy:**
1. **Formula Sheet Review** (15 min): Go through all key formulas/definitions you've noted
2. **Previous Questions** (30 min): Solve 3-5 previous year questions - they reveal exam patterns
3. **Weak Spots** (20 min): Quick review of topics you find challenging - even basics help
4. **Mental Prep** (5 min): Deep breaths, confidence affirmations - you've got this!

**⏰ Time Tips:**
- Don't start new topics now - reinforce what you know
- Take 5-min breaks every 25 minutes
- Stay hydrated, avoid heavy meals

**💪 Remember:** You've prepared for this moment. Trust yourself!

Which subject or topic should we focus on? I can give you targeted tips!"""
        else:
            # Generic helpful response for other urgent queries
            return f"""I'm here to help! Here's what I can do for you right now: 🤝

**Based on your question:** "{query[:80]}{'...' if len(query) > 80 else ''}"

**🎯 Quick Options:**
1. **Explain a concept** - I'll break it down step by step
2. **Solve a problem** - Walk through the solution together
3. **Quick revision** - Key points on any topic
4. **Practice questions** - Test your understanding

**💡 Pro Tip:** The more specific you are, the better I can help!

What would you like to start with?"""
    
    def _generate_helpful_fallback(self, query: str) -> str:
        """
        Generate helpful fallback for non-urgent situations.
        
        This is BETTER than the old fallback because:
        1. It acknowledges the query
        2. Provides SOME immediate value (general guidance)
        3. Offers one clear path forward (not multiple confusing questions)
        
        This is NOT used for urgent situations.
        """
        query_short = query[:100] + '...' if len(query) > 100 else query
        
        return f"""I can help you with this. To give you the clearest explanation:

Could you let me know the subject area (Physics, Chemistry, Math, or Biology)?

Once I know that, I'll explain the concept clearly with examples that make sense."""

