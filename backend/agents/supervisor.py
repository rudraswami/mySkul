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

# COGNITO-OS v3.0 - Universal Education Components
try:
    from services.knowledge_base.universal_knowledge_graph import get_universal_knowledge_graph
    from services.hybrid_reasoning_engine import get_hybrid_reasoning_engine
    from services.cognitive_model.agent_negotiation import get_agent_negotiator
    COGNITO_OS_AVAILABLE = True
except ImportError as e:
    COGNITO_OS_AVAILABLE = False
    logging.warning(f"Cognito-OS components not available: {e}")

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
        
        # COGNITO-OS v3.0 - Universal Education Components
        self.knowledge_graph = None
        self.hybrid_engine = None
        self.agent_negotiator = None
        self.use_hybrid_reasoning = False  # Flag to enable hybrid reasoning
        
        if COGNITO_OS_AVAILABLE:
            try:
                self.knowledge_graph = get_universal_knowledge_graph()
                self.hybrid_engine = get_hybrid_reasoning_engine()
                self.agent_negotiator = get_agent_negotiator()
                
                # Register agents with negotiator for collaboration
                self.agent_negotiator.register_agent("mentor", self.mentor, ["explanation", "empathy", "metaphors"])
                self.agent_negotiator.register_agent("professor", self.professor, ["derivation", "proof", "formal"])
                self.agent_negotiator.register_agent("doubt_resolver", self.doubt_resolver, ["doubt", "confusion", "clarification"])
                # COGNITIVE OS FIX: More specific capabilities for exam_coach
                # Only activate for explicit exam preparation, not generic "strategy"
                self.agent_negotiator.register_agent("exam_coach", self.exam_coach, ["jee_preparation", "neet_preparation", "exam_strategy", "study_plan_for_exam"])
                
                self.use_hybrid_reasoning = True
                logger.info("   ├── 🌍 UniversalKnowledgeGraph connected (multi-domain)")
                logger.info("   ├── 🧠 HybridReasoningEngine active (Neural + Symbolic)")
                logger.info("   └── 🤝 AgentNegotiator ready (collaborative)")
            except Exception as e:
                logger.warning(f"⚠️ Cognito-OS components failed to load: {e}")
        
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
            
            # Step 1: Analyze query intent (with context for mode-aware detection)
            intent = self._detect_intent(query, context)
            logger.info(f"🎯 Detected intent: {intent}")
            
            # 🆕 Step 1.5: Use Agent Negotiation for TRUE multi-agent collaboration
            # EXPANDED: Now enabled for most educational intents, not just complex queries
            # This is what makes us different from chatbots - agents actually collaborate
            use_negotiation = context.get('use_agent_negotiation', False) or context.get('enable_agent_negotiation', False)
            
            # Expanded intent list - negotiation for most educational queries
            negotiation_intents = [
                'concept', 'comparison', 'derivation', 'application', 
                'explanation', 'problem', 'analysis', 'doubt'
            ]
            
            if use_negotiation and self.agent_negotiator and intent in negotiation_intents:
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
                agents_to_run = self._select_agents(intent, context)
                logger.info(f"👥 Activating agents: {', '.join(agents_to_run)}")
                
                # Step 3: Run agents in parallel (non-blocking)
                agent_responses = await self._run_agents_parallel(
                    query=query,
                    context=context,
                    agents=agents_to_run
                )
            
            # Step 4: Validate responses
            validated_responses = self._validate_responses(agent_responses)
            
            # Step 5: Combine and structure final response
            combined_response = self._merge_responses(
                query=query,
                intent=intent,
                agent_responses=validated_responses,
                context=context
            )
            
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
    
    def _detect_intent(self, query: str, context: Dict[str, Any] = None) -> str:
        """
        Detect student intent from query.
        
        COGNITIVE OS FIX: Now context-aware for mode validation.
        
        Args:
            query: Student's question
            context: Context dict with exam_mode, etc.
        
        Returns:
            Intent type: 'concept', 'derivation', 'application', 'comparison', 'doubt', etc.
        """
        context = context or {}
        query_lower = query.lower().strip()
        
        # Greeting intent (must check FIRST before other patterns)
        greeting_words = ['hi', 'hello', 'hey', 'namaste', 'hii', 'heya', 'yo']
        # Check if entire message is just a greeting (with possible punctuation)
        clean_query = query_lower.strip('!?.,:;')
        if clean_query in greeting_words or len(query_lower.split()) <= 3 and any(word in query_lower for word in greeting_words):
            return 'greeting'
        
        # DOUBT INTENT - Route to AgenticDoubtResolver ONLY for TRUE confusion
        # NOTE: is_doubt_query() is now RESTRICTIVE - normal questions go to concept/application
        if AgenticDoubtResolver.is_doubt_query(query):
            logger.info("🎯 Detected TRUE DOUBT intent (genuine confusion) - routing to AgenticDoubtResolver")
            return 'doubt'
        
        # EXAM STRATEGY INTENT - Route to ExamCoachAgent
        # COGNITIVE OS FIX: Only route to ExamCoach if BOTH conditions are met:
        # 1. Query explicitly mentions exam strategy (stricter pattern matching)
        # 2. Exam context exists (user has explicit exam mode or query mentions exam)
        exam_mode = context.get('exam_mode', 'General')
        has_explicit_exam_mode = exam_mode.upper() in ['JEE', 'NEET', 'UPSC', 'GATE', 'CAT']
        
        if ExamCoachAgent.is_exam_strategy_query(query):
            # Additional check: Even with strict pattern matching, only route if:
            # - User has explicit exam mode, OR
            # - Query explicitly mentions an exam name
            explicit_exam_in_query = any(exam in query_lower for exam in ['jee', 'neet', 'upsc', 'gate', 'cat', 'boards'])
            
            if has_explicit_exam_mode or explicit_exam_in_query:
                logger.info(f"🏆 Detected EXAM_STRATEGY intent (exam_mode={exam_mode}) - routing to ExamCoach")
                return 'exam_strategy'
            else:
                logger.info(f"⚠️ Exam-like query but exam_mode=General - NOT routing to ExamCoach")
                # Fall through to concept/other intents
        
        # WEAK AREA ANALYSIS INTENT - Route to WeakAreaDetective
        # Check if student wants to know their weak areas
        if WeakAreaDetectiveAgent.is_weak_area_query(query):
            logger.info("🔍 Detected WEAK_AREA intent - routing to WeakAreaDetective")
            return 'weak_area_analysis'
        
        # STUDY BUDDY INTENT - Route to StudyBuddy
        # Check if student wants to study together / peer learning
        if StudyBuddyAgent.is_buddy_query(query):
            logger.info("🤝 Detected STUDY_BUDDY intent - routing to StudyBuddy")
            return 'study_buddy'
        
        # PARENT REPORT INTENT (NEW) - Route to ParentReport
        # Check if request is for parent/guardian report
        if ParentReportAgent.is_parent_report_query(query):
            logger.info("👨‍👩‍👧 Detected PARENT_REPORT intent - routing to ParentReport")
            return 'parent_report'
        
        # Comparison intent
        if any(word in query_lower for word in ['compare', 'difference', 'vs', 'versus', 'contrast']):
            return 'comparison'
        
        # Derivation/proof intent
        if any(word in query_lower for word in ['derive', 'prove', 'proof', 'show that']):
            return 'derivation'
        
        # Application/problem-solving intent
        if any(word in query_lower for word in ['solve', 'calculate', 'find', 'compute']):
            return 'application'
        
        # Clarification intent - also route to doubt resolver
        if any(word in query_lower for word in ['clarify', 'explain again', 'what do you mean', 'elaborate']):
            return 'doubt'  # Changed from 'clarification' to use DoubtResolver
        
        # Default: conceptual explanation
        return 'concept'
    
    def _select_agents(
        self,
        intent: str,
        context: Dict[str, Any]
    ) -> List[str]:
        """
        Select which agents to activate based on intent
        
        Returns:
            List of agent names to run
        """
        # For greetings, ONLY run Mentor
        if intent == 'greeting':
            return ['mentor']
        
        # DOUBT INTENT - Use specialized DoubtResolver
        # DoubtResolver provides quick, empathetic, visual explanations
        if intent == 'doubt':
            agents = ['doubt_resolver']
            # Always include visual for doubts - visuals help clear confusion
            if context.get('request_visual', True):
                agents.append('visualise')
            return agents
        
        # EXAM STRATEGY INTENT - Use ExamCoach
        # ExamCoach provides strategic exam preparation guidance
        if intent == 'exam_strategy':
            # ExamCoach handles strategy alone - no need for mentor/professor
            return ['exam_coach']
        
        # WEAK AREA ANALYSIS INTENT - Use WeakAreaDetective
        # WeakAreaDetective analyzes performance and finds gaps
        if intent == 'weak_area_analysis':
            return ['weak_area_detective']
        
        # STUDY BUDDY INTENT - Use StudyBuddy
        # StudyBuddy provides peer learning simulation
        if intent == 'study_buddy':
            return ['study_buddy']
        
        # PARENT REPORT INTENT (NEW) - Use ParentReport
        # ParentReport generates guardian-focused reports
        if intent == 'parent_report':
            return ['parent_report']
        
        # Always run Mentor (emotional support)
        agents = ['mentor']
        
        # Professor for formal explanations (skip for greetings)
        if intent not in ['greeting']:
            agents.append('professor')
        
        # Visualise for concept/derivation (skip for comparisons/greetings)
        if context.get('request_visual', True) and intent in ['concept', 'derivation', 'application']:
            agents.append('visualise')
        
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
        
        # Create tasks for each agent
        if 'mentor' in agents:
            logger.info("   Routing to Mentor agent...")
            tasks['mentor'] = self.mentor.process(query, context)
        
        if 'professor' in agents:
            logger.info("   Routing to Professor agent...")
            tasks['professor'] = self.professor.process(query, context)
        
        if 'visualise' in agents:
            logger.info("   Routing to Visualise agent...")
            tasks['visualise'] = self.visualise.process(query, context)
        
        # NEW: DoubtResolver agent for doubt/confusion queries
        if 'doubt_resolver' in agents:
            logger.info("   🎯 Routing to DoubtResolver agent...")
            tasks['doubt_resolver'] = self.doubt_resolver.process(query, context)
        
        # NEW: ExamCoach agent for exam strategy queries
        if 'exam_coach' in agents:
            logger.info("   🏆 Routing to ExamCoach agent...")
            tasks['exam_coach'] = self.exam_coach.process(query, context)
        
        # WeakAreaDetective agent for performance analysis
        if 'weak_area_detective' in agents:
            logger.info("   🔍 Routing to WeakAreaDetective agent...")
            tasks['weak_area_detective'] = self.weak_area_detective.process(query, context)
        
        # StudyBuddy agent for peer learning
        if 'study_buddy' in agents:
            logger.info("   🤝 Routing to StudyBuddy agent...")
            tasks['study_buddy'] = self.study_buddy.process(query, context)
        
        # NEW: ParentReport agent for guardian communication
        if 'parent_report' in agents:
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

