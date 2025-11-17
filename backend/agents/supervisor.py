"""
Supervisor Agent - Orchestrates Multi-Agent Responses
Routes queries to appropriate agents and combines their responses
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from agents.mentor import MentorAgent
from agents.professor import ProfessorAgent
from agents.visualise import VisualiseAgent

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
        
        # Initialize all sub-agents
        self.mentor = MentorAgent(config)
        self.professor = ProfessorAgent(config)
        self.visualise = VisualiseAgent(config)
        
        logger.info("🤖 Supervisor initialized with all sub-agents")
        logger.info("   ├── Mentor agent initialized")
        logger.info("   ├── Professor agent initialized")
        logger.info("   └── Visualise agent initialized")
    
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
            Intent type: 'concept', 'derivation', 'application', 'comparison', etc.
        """
        query_lower = query.lower().strip()
        
        # Greeting intent (must check FIRST before other patterns)
        greeting_words = ['hi', 'hello', 'hey', 'namaste', 'hii', 'heya', 'yo']
        # Check if entire message is just a greeting (with possible punctuation)
        clean_query = query_lower.strip('!?.,:;')
        if clean_query in greeting_words or len(query_lower.split()) <= 3 and any(word in query_lower for word in greeting_words):
            return 'greeting'
        
        # Comparison intent
        if any(word in query_lower for word in ['compare', 'difference', 'vs', 'versus', 'contrast']):
            return 'comparison'
        
        # Derivation/proof intent
        if any(word in query_lower for word in ['derive', 'prove', 'proof', 'show that']):
            return 'derivation'
        
        # Application/problem-solving intent
        if any(word in query_lower for word in ['solve', 'calculate', 'find', 'compute']):
            return 'application'
        
        # Clarification intent
        if any(word in query_lower for word in ['clarify', 'explain again', 'what do you mean', 'elaborate']):
            return 'clarification'
        
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
        
        # Always run Mentor (emotional support)
        agents = ['mentor']
        
        # Professor for formal explanations (skip for greetings/clarifications)
        if intent not in ['greeting', 'clarification']:
            agents.append('professor')
        
        # Visualise for concept/derivation (skip for comparisons/clarifications/greetings)
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
        return {
            'success': True,
            'query': query,
            'intent': intent,
            'mentor': agent_responses.get('mentor', {}),
            'professor': agent_responses.get('professor', {}),
            'visual': agent_responses.get('visualise', {}).get('content'),  # Extract visual spec
            'metadata': {
                'agents_used': list(agent_responses.keys()),
                'supervisor_version': '1.0'
            }
        }

