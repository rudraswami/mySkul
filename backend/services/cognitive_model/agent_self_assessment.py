"""
🤖 Agent Self-Assessment — Autonomous Agent Participation
=========================================================

GAP 1 IMPLEMENTATION: Agent Autonomy

Agents must self-assess whether to participate.
Supervisor NEVER assigns agents - it broadcasts context and collects assessments.

ARCHITECTURAL PRINCIPLES:
- Agents compete based on semantic signals, not keyword routing
- Agents can DECLINE to participate (they are autonomous)
- Supervisor is a COORDINATOR, not a brain
- Mentor is final fallback ONLY if no agent opts in

STRICT RULE:
If an agent cannot say "no", it is not autonomous.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ParticipationDecision(Enum):
    """Agent's decision about participation."""
    STRONG_YES = "strong_yes"       # Highly relevant, should lead
    YES = "yes"                     # Can contribute
    MAYBE = "maybe"                 # Could help, not primary
    NO = "no"                       # Not relevant, declines
    DEFER = "defer"                 # Defer to other agents


@dataclass
class AgentCapability:
    """
    What an agent is capable of.
    
    Declared by the agent itself, NOT assigned by supervisor.
    """
    # Semantic capabilities (what the agent understands)
    can_handle_emotion: bool = False
    can_handle_planning: bool = False
    can_handle_problem_solving: bool = False
    can_handle_explanation: bool = False
    can_handle_comparison: bool = False
    can_handle_creative: bool = False
    can_handle_analysis: bool = False
    can_handle_continuation: bool = False
    can_handle_urgency: bool = False
    
    # Subject expertise (if any)
    subject_expertise: List[str] = field(default_factory=list)
    
    # Constraints
    max_complexity: float = 1.0  # 0-1: Maximum complexity this agent can handle
    requires_context: bool = True  # Needs conversation context
    requires_memory: bool = True   # Needs memory access


@dataclass
class SelfAssessment:
    """
    Agent's self-assessment for a given query.
    
    This is NOT assigned by supervisor. The agent computes this itself
    based on its capabilities and the semantic analysis.
    """
    # The decision
    decision: ParticipationDecision
    
    # Confidence in handling this query (0-1)
    confidence: float
    
    # Relevance score (0-1)
    relevance: float
    
    # Why the agent thinks it's suitable (or not)
    reasoning: str
    
    # What the agent would contribute
    contribution_type: str = "general"  # e.g., "empathy", "structure", "explanation"
    
    # Should this agent lead if selected?
    wants_to_lead: bool = False
    
    @property
    def should_participate(self) -> bool:
        """True if agent wants to participate."""
        return self.decision in (ParticipationDecision.STRONG_YES, ParticipationDecision.YES)
    
    @property
    def participation_score(self) -> float:
        """
        Numeric score for ranking agents.
        
        Combines decision, confidence, and relevance.
        """
        decision_weight = {
            ParticipationDecision.STRONG_YES: 1.0,
            ParticipationDecision.YES: 0.7,
            ParticipationDecision.MAYBE: 0.3,
            ParticipationDecision.DEFER: 0.1,
            ParticipationDecision.NO: 0.0
        }
        
        base = decision_weight.get(self.decision, 0.0)
        return base * self.confidence * self.relevance


class AutonomousAgent(ABC):
    """
    Base class for autonomous agents.
    
    All agents MUST implement self_assess() to decide if they should participate.
    Agents can decline - this is what makes them autonomous.
    """
    
    @abstractmethod
    def get_capabilities(self) -> AgentCapability:
        """
        Declare this agent's capabilities.
        
        This is a static declaration of what the agent CAN do,
        not what it WILL do for a specific query.
        """
        pass
    
    @abstractmethod
    async def self_assess(
        self,
        semantic_analysis: 'SemanticAnalysis',
        context: Dict[str, Any]
    ) -> SelfAssessment:
        """
        Assess whether to participate in handling this query.
        
        This is the core of agent autonomy. The agent:
        1. Examines the semantic analysis
        2. Compares against its capabilities
        3. Considers the context
        4. Decides whether to participate
        5. Returns its assessment
        
        The agent CAN say NO. If it cannot, it's not autonomous.
        """
        pass
    
    @abstractmethod
    async def contribute(
        self,
        query: str,
        context: Dict[str, Any],
        lead_agent: bool = False
    ) -> Dict[str, Any]:
        """
        Contribute to the response.
        
        Called only if self_assess returned a participating decision.
        
        Args:
            query: The user's query
            context: Full context including semantic analysis
            lead_agent: True if this agent is leading the response
        
        Returns:
            Agent's contribution to the response
        """
        pass


# ============================================================================
# COORDINATOR (SUPERVISOR REPLACEMENT)
# ============================================================================

class AgentCoordinator:
    """
    Coordinates agents WITHOUT assigning them.
    
    The Supervisor is now a Coordinator. Its role is:
    1. Broadcast semantic context to all agents
    2. Collect self-assessments
    3. Resolve conflicts (if multiple want to lead)
    4. Enforce latency/safety constraints
    
    It does NOT decide "who handles this".
    """
    
    def __init__(self, agents: List[AutonomousAgent] = None, fallback_agent_name: str = "mentor"):
        """
        Initialize coordinator with available agents.
        
        Args:
            agents: List of AutonomousAgent instances
            fallback_agent_name: Agent to use if none opt in (Mentor)
        """
        self.agents = agents or []
        self.fallback_agent_name = fallback_agent_name
        logger.info(f"🤖 AgentCoordinator initialized with {len(self.agents)} agents")
    
    async def coordinate(
        self,
        query: str,
        semantic_analysis: 'SemanticAnalysis',
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinate agent participation.
        
        1. Broadcast context to all agents
        2. Collect self-assessments
        3. Select participating agents
        4. Execute contributions
        5. Merge results
        
        Returns:
            Combined response from participating agents
        """
        from core.config import settings
        
        # Check if autonomous agents are enabled
        if not getattr(settings, 'ENABLE_AGENT_AUTONOMY', True):
            logger.debug("Agent autonomy disabled, using legacy coordination")
            return await self._legacy_coordinate(query, context)
        
        # Step 1: Collect self-assessments
        assessments = await self._collect_assessments(semantic_analysis, context)
        
        # Step 2: Filter to participating agents
        participating = [
            (agent, assessment) 
            for agent, assessment in assessments 
            if assessment.should_participate
        ]
        
        if not participating:
            # No agents opted in - use fallback
            logger.info(f"🤖 No agents opted in, using fallback: {self.fallback_agent_name}")
            return await self._fallback_response(query, context)
        
        # Step 3: Sort by participation score
        participating.sort(key=lambda x: x[1].participation_score, reverse=True)
        
        # Step 4: Resolve leadership
        lead_agent, lead_assessment = participating[0]
        supporting = participating[1:3]  # Max 2 supporting agents
        
        logger.info(f"🤖 Lead agent: {lead_agent.__class__.__name__} "
                   f"(score={lead_assessment.participation_score:.2f})")
        
        # Step 5: Execute contributions
        contributions = []
        
        # Lead agent contribution
        lead_result = await lead_agent.contribute(query, context, lead_agent=True)
        contributions.append({
            'agent': lead_agent.__class__.__name__,
            'role': 'lead',
            'contribution': lead_result
        })
        
        # Supporting agent contributions (parallel)
        import asyncio
        support_tasks = [
            agent.contribute(query, context, lead_agent=False)
            for agent, _ in supporting
        ]
        if support_tasks:
            support_results = await asyncio.gather(*support_tasks, return_exceptions=True)
            for (agent, _), result in zip(supporting, support_results):
                if isinstance(result, Exception):
                    logger.warning(f"Supporting agent {agent.__class__.__name__} failed: {result}")
                    continue
                contributions.append({
                    'agent': agent.__class__.__name__,
                    'role': 'supporting',
                    'contribution': result
                })
        
        # Step 6: Merge contributions
        return self._merge_contributions(contributions, lead_assessment)
    
    async def _collect_assessments(
        self,
        semantic_analysis: 'SemanticAnalysis',
        context: Dict[str, Any]
    ) -> List[tuple]:
        """
        Broadcast to all agents and collect assessments.
        """
        import asyncio
        
        async def assess_agent(agent):
            try:
                assessment = await agent.self_assess(semantic_analysis, context)
                return (agent, assessment)
            except Exception as e:
                logger.warning(f"Agent {agent.__class__.__name__} assessment failed: {e}")
                return (agent, SelfAssessment(
                    decision=ParticipationDecision.NO,
                    confidence=0.0,
                    relevance=0.0,
                    reasoning=f"Assessment failed: {e}"
                ))
        
        results = await asyncio.gather(*[assess_agent(a) for a in self.agents])
        
        # Log assessments for observability
        for agent, assessment in results:
            logger.debug(f"🤖 {agent.__class__.__name__}: "
                        f"decision={assessment.decision.value}, "
                        f"score={assessment.participation_score:.2f}")
        
        return list(results)
    
    def _merge_contributions(
        self,
        contributions: List[Dict[str, Any]],
        lead_assessment: SelfAssessment
    ) -> Dict[str, Any]:
        """
        Merge contributions from multiple agents.
        
        Lead agent's content is primary. Supporting agents add value.
        """
        if not contributions:
            return {"success": False, "content": "", "error": "No contributions"}
        
        # Lead contribution is primary
        lead = contributions[0]['contribution']
        
        # Build merged result
        result = {
            "success": True,
            "content": lead.get('content', ''),
            "primary_agent": contributions[0]['agent'],
            "agents_contributed": [c['agent'] for c in contributions],
            "lead_confidence": lead_assessment.confidence,
            "contribution_type": lead_assessment.contribution_type,
            "metadata": lead.get('metadata', {})
        }
        
        # Add supporting insights if present
        for contrib in contributions[1:]:
            support = contrib['contribution']
            if support.get('content'):
                result['supporting_insights'] = result.get('supporting_insights', [])
                result['supporting_insights'].append({
                    'agent': contrib['agent'],
                    'insight': support.get('content', '')[:500]  # Bounded
                })
        
        return result
    
    async def _fallback_response(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate fallback when no agents opt in.
        
        Uses Mentor as the ultimate fallback.
        """
        logger.info(f"🤖 Using fallback agent: {self.fallback_agent_name}")
        
        # Find fallback agent
        for agent in self.agents:
            if agent.__class__.__name__.lower() == self.fallback_agent_name.lower():
                result = await agent.contribute(query, context, lead_agent=True)
                return {
                    "success": True,
                    "content": result.get('content', ''),
                    "primary_agent": self.fallback_agent_name,
                    "agents_contributed": [self.fallback_agent_name],
                    "is_fallback": True
                }
        
        # Ultimate fallback if no mentor
        return {
            "success": False,
            "content": "I'd love to help you with that! Could you tell me more about what you're looking for?",
            "primary_agent": "system",
            "is_fallback": True,
            "error": "No agents available"
        }
    
    async def _legacy_coordinate(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy coordination for backward compatibility.
        
        Used when ENABLE_AGENT_AUTONOMY is False.
        """
        if not self.agents:
            return await self._fallback_response(query, context)
        
        # Just use first agent (legacy behavior)
        agent = self.agents[0]
        result = await agent.contribute(query, context, lead_agent=True)
        
        return {
            "success": True,
            "content": result.get('content', ''),
            "primary_agent": agent.__class__.__name__,
            "agents_contributed": [agent.__class__.__name__],
            "legacy_mode": True
        }


# ============================================================================
# CONFIG FLAGS
# ============================================================================

def add_autonomy_config_flags():
    """Add autonomy-related config flags (call during app initialization)."""
    # Flags are added directly to core/config.py
    pass


# ============================================================================
# SINGLETON ACCESS
# ============================================================================

_coordinator: Optional[AgentCoordinator] = None


def get_agent_coordinator(agents: List[AutonomousAgent] = None) -> AgentCoordinator:
    """Get or create agent coordinator singleton."""
    global _coordinator
    if _coordinator is None:
        _coordinator = AgentCoordinator(agents)
    return _coordinator


def reset_coordinator():
    """Reset the coordinator singleton (for testing)."""
    global _coordinator
    _coordinator = None


