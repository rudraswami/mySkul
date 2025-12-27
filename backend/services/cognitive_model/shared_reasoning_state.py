"""
🧠 Shared Reasoning State - Thread-Safe State for Multi-Agent Collaboration
==========================================================================

This module provides a shared state object that agents can read/write to
during their execution, enabling TRUE shared reasoning without modifying
execution paths.

ARCHITECTURE:
- SharedReasoningState is injected via context['_reasoning_state']
- Agents read/write during their run() execution
- Thread-safe via asyncio.Lock
- Non-blocking: agents can proceed without waiting for state

INTEGRATION:
- Supervisor injects state into context BEFORE running agents
- Agents check context for state and use if available
- No modification to agent execution logic required

This is TRUE cognition: agents share insights as they reason,
not just after they complete.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)


class InsightType(Enum):
    """Types of insights agents can share"""
    HYPOTHESIS = "hypothesis"      # Tentative conclusion
    FACT = "fact"                  # Verified fact from tool use
    WARNING = "warning"            # Potential issue detected
    QUESTION = "question"          # Agent is uncertain, asking for help
    CORRECTION = "correction"      # Agent correcting earlier insight
    VERIFICATION = "verification"  # Agent verified another's insight


@dataclass
class SharedInsight:
    """An insight shared by an agent during reasoning"""
    agent_name: str
    insight_type: InsightType
    content: str
    confidence: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    related_insight_id: Optional[str] = None  # For corrections/verifications
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'agent': self.agent_name,
            'type': self.insight_type.value,
            'content': self.content,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'related_to': self.related_insight_id,
            'metadata': self.metadata
        }


class SharedReasoningState:
    """
    Thread-safe shared state for multi-agent reasoning.
    
    Agents can:
    - Post insights (hypotheses, facts, warnings)
    - Query insights from other agents
    - Post corrections to previous insights
    - Request help from other agents
    
    This enables TRUE shared reasoning: agents see each other's
    intermediate thoughts as they work, not just final outputs.
    """
    
    def __init__(self, query: str, context: Dict[str, Any]):
        self._lock = asyncio.Lock()
        self._insights: List[SharedInsight] = []
        self._insight_counter = 0
        self.query = query
        self.context = context
        self._active_agents: Dict[str, datetime] = {}
        self._help_requests: List[Dict[str, Any]] = []
        
        logger.info("🧠 SharedReasoningState initialized for multi-agent collaboration")
    
    async def post_insight(
        self,
        agent_name: str,
        insight_type: InsightType,
        content: str,
        confidence: float = 0.7,
        related_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Post an insight to the shared state.
        
        Args:
            agent_name: Name of the posting agent
            insight_type: Type of insight
            content: The insight content
            confidence: Agent's confidence in this insight (0-1)
            related_to: ID of related insight (for corrections/verifications)
            metadata: Additional metadata
        
        Returns:
            Unique insight ID
        """
        async with self._lock:
            self._insight_counter += 1
            insight_id = f"{agent_name}_{self._insight_counter}"
            
            insight = SharedInsight(
                agent_name=agent_name,
                insight_type=insight_type,
                content=content,
                confidence=confidence,
                related_insight_id=related_to,
                metadata=metadata or {}
            )
            insight.metadata['insight_id'] = insight_id
            
            self._insights.append(insight)
            logger.debug(f"📝 {agent_name} posted {insight_type.value}: {content[:50]}...")
            
            return insight_id
    
    async def get_insights(
        self,
        exclude_agent: Optional[str] = None,
        insight_type: Optional[InsightType] = None,
        min_confidence: float = 0.0
    ) -> List[SharedInsight]:
        """
        Get insights from the shared state.
        
        Args:
            exclude_agent: Exclude insights from this agent
            insight_type: Filter by insight type
            min_confidence: Minimum confidence threshold
        
        Returns:
            List of matching insights
        """
        async with self._lock:
            insights = self._insights.copy()
        
        # Filter
        if exclude_agent:
            insights = [i for i in insights if i.agent_name != exclude_agent]
        if insight_type:
            insights = [i for i in insights if i.insight_type == insight_type]
        if min_confidence > 0:
            insights = [i for i in insights if i.confidence >= min_confidence]
        
        return insights
    
    async def get_latest_insights(
        self,
        exclude_agent: Optional[str] = None,
        limit: int = 5
    ) -> List[SharedInsight]:
        """Get the most recent insights for quick context"""
        async with self._lock:
            insights = self._insights.copy()
        
        if exclude_agent:
            insights = [i for i in insights if i.agent_name != exclude_agent]
        
        # Sort by timestamp descending, take limit
        insights.sort(key=lambda x: x.timestamp, reverse=True)
        return insights[:limit]
    
    async def request_help(
        self,
        requesting_agent: str,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Agent requests help from other agents.
        
        This is a signal that the agent is uncertain and would
        benefit from another agent's input.
        """
        async with self._lock:
            self._help_requests.append({
                'from': requesting_agent,
                'question': question,
                'context': context or {},
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            logger.info(f"❓ {requesting_agent} requested help: {question[:50]}...")
    
    async def get_help_requests(
        self,
        for_agent: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get pending help requests"""
        async with self._lock:
            requests = self._help_requests.copy()
        
        if for_agent:
            # Return requests not from this agent
            requests = [r for r in requests if r['from'] != for_agent]
        
        return requests
    
    async def register_active(self, agent_name: str):
        """Register that an agent is actively reasoning"""
        async with self._lock:
            self._active_agents[agent_name] = datetime.now(timezone.utc)
    
    async def get_active_agents(self) -> List[str]:
        """Get list of currently active agents"""
        async with self._lock:
            return list(self._active_agents.keys())
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the shared state for debugging"""
        return {
            'total_insights': len(self._insights),
            'active_agents': list(self._active_agents.keys()),
            'help_requests': len(self._help_requests),
            'insights_by_type': {
                t.value: len([i for i in self._insights if i.insight_type == t])
                for t in InsightType
            }
        }


def inject_shared_state(context: Dict[str, Any], query: str) -> SharedReasoningState:
    """
    Inject shared reasoning state into context.
    
    This is the main integration point - call this in supervisor
    before running agents.
    """
    state = SharedReasoningState(query=query, context=context)
    context['_reasoning_state'] = state
    return state


def get_shared_state(context: Dict[str, Any]) -> Optional[SharedReasoningState]:
    """
    Get shared state from context (for agents to use).
    
    Returns None if not available - agents should handle gracefully.
    """
    return context.get('_reasoning_state')

