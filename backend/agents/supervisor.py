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
        
        logger.info("🤖 Supervisor initialized with TRUE AGENTIC system (Cognito OS v2.0)")
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
            
            # Step 1: Analyze query intent
            intent = self._detect_intent(query)
            logger.info(f"🎯 Detected intent: {intent}")
            
            # Step 2: Determine which agents to activate
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
                agent_responses=validated_responses
            )
            
            # Step 6: 💪 MOTIVATION MIDDLEWARE - Add emotional support if needed
            # This enhances the response with motivational content based on student state
            combined_response = self.motivation.enhance_response(
                original_response=combined_response,
                context=context
            )
            
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
    
    def _detect_intent(self, query: str) -> str:
        """
        Detect student intent from query
        
        Returns:
            Intent type: 'concept', 'derivation', 'application', 'comparison', 'doubt', etc.
        """
        query_lower = query.lower().strip()
        
        # Greeting intent (must check FIRST before other patterns)
        greeting_words = ['hi', 'hello', 'hey', 'namaste', 'hii', 'heya', 'yo']
        # Check if entire message is just a greeting (with possible punctuation)
        clean_query = query_lower.strip('!?.,:;')
        if clean_query in greeting_words or len(query_lower.split()) <= 3 and any(word in query_lower for word in greeting_words):
            return 'greeting'
        
        # DOUBT INTENT - Route to AgenticDoubtResolver (TRUE AGENT with ReAct loop)
        # Check if student is confused or has a specific doubt
        if AgenticDoubtResolver.is_doubt_query(query):
            logger.info("🎯 Detected DOUBT intent - routing to AgenticDoubtResolver")
            return 'doubt'
        
        # EXAM STRATEGY INTENT - Route to ExamCoachAgent
        # Check if student needs exam preparation guidance
        if ExamCoachAgent.is_exam_strategy_query(query):
            logger.info("🏆 Detected EXAM_STRATEGY intent - routing to ExamCoach")
            return 'exam_strategy'
        
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
        agent_responses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge agent responses into unified structure
        
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
        
        return {
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
                'supervisor_version': '1.5',  # Cognito OS v1.5
                'used_doubt_resolver': 'doubt_resolver' in agent_responses,
                'used_exam_coach': 'exam_coach' in agent_responses,
                'used_weak_area_detective': 'weak_area_detective' in agent_responses,
                'used_study_buddy': 'study_buddy' in agent_responses,
                'used_parent_report': 'parent_report' in agent_responses
            }
        }

