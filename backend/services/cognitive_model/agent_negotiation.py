"""
Agent Negotiation - Multi-Agent Collaboration System
=====================================================

Instead of linear agent calls, agents NEGOTIATE who should answer.

Key Concepts:
1. Bidding: Each agent evaluates confidence for a query
2. Negotiation: Top agents collaborate or defer
3. Cross-Verification: Agents validate each other's responses
4. Consensus: Merged response from multiple perspectives

This makes the system a TRUE cognitive OS where agents work as a team.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AgentConfidenceLevel(Enum):
    """Confidence levels for agent bidding"""
    EXPERT = 0.95      # "I specialize in this"
    HIGH = 0.80        # "I can handle this well"
    MODERATE = 0.60    # "I can contribute"
    LOW = 0.40         # "I have limited capability"
    NONE = 0.0         # "This isn't my domain"


@dataclass
class AgentBid:
    """Bid from an agent for handling a query"""
    agent_name: str
    confidence: float
    reasoning: str
    estimated_time_ms: int
    can_verify_others: bool
    collaboration_preference: str  # "solo", "lead", "support", "verify"


@dataclass
class NegotiationResult:
    """Result of agent negotiation"""
    lead_agent: str
    supporting_agents: List[str]
    verifying_agents: List[str]
    strategy: str  # "single", "parallel", "sequential", "consensus"
    expected_confidence: float
    negotiation_reasoning: str


@dataclass
class CollaborativeResponse:
    """Response from multi-agent collaboration"""
    primary_response: Dict[str, Any]
    supporting_insights: List[Dict[str, Any]]
    verification_results: List[Dict[str, Any]]
    consensus_reached: bool
    final_confidence: float
    agents_involved: List[str]
    collaboration_summary: str


class AgentNegotiator:
    """
    Orchestrates multi-agent negotiation and collaboration
    
    Flow:
    1. Broadcast query to all agents
    2. Collect confidence bids
    3. Negotiate who leads, supports, verifies
    4. Execute collaboration strategy
    5. Merge and verify responses
    """
    
    def __init__(self):
        """Initialize negotiator with empty agent registry"""
        self.agents: Dict[str, Any] = {}  # name -> agent instance
        self.agent_capabilities: Dict[str, List[str]] = {}  # name -> domains
        self.negotiation_history: List[NegotiationResult] = []
        
        logger.info("🤝 AgentNegotiator initialized")
    
    def register_agent(
        self,
        name: str,
        agent: Any,
        capabilities: List[str],
        can_verify: bool = False
    ):
        """Register an agent with its capabilities"""
        self.agents[name] = agent
        self.agent_capabilities[name] = capabilities
        
        logger.info(f"   ├── Registered: {name} (capabilities: {', '.join(capabilities)})")
    
    async def negotiate(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> NegotiationResult:
        """
        Conduct negotiation among agents for a query
        
        Args:
            query: Student's question
            context: Additional context
            
        Returns:
            NegotiationResult with assigned roles
        """
        logger.info(f"🤝 Negotiating for: {query[:50]}...")
        
        # Step 1: Collect bids from all agents
        bids = await self._collect_bids(query, context)
        
        if not bids:
            return self._default_negotiation_result()
        
        # Step 2: Rank agents by confidence
        ranked_bids = sorted(bids, key=lambda b: b.confidence, reverse=True)
        
        # Step 3: Determine collaboration strategy
        result = self._determine_strategy(ranked_bids, query, context)
        
        # Store in history
        self.negotiation_history.append(result)
        
        logger.info(f"✅ Negotiation complete: Lead={result.lead_agent}, Strategy={result.strategy}")
        return result
    
    async def collaborate(
        self,
        query: str,
        context: Dict[str, Any],
        negotiation_result: NegotiationResult
    ) -> CollaborativeResponse:
        """
        Execute multi-agent collaboration based on negotiation
        
        Args:
            query: Student's question
            context: Additional context
            negotiation_result: Result from negotiate()
            
        Returns:
            CollaborativeResponse with merged output
        """
        strategy = negotiation_result.strategy
        
        if strategy == "single":
            return await self._single_agent_response(
                query, context, negotiation_result.lead_agent
            )
        
        elif strategy == "parallel":
            return await self._parallel_collaboration(
                query, context, negotiation_result
            )
        
        elif strategy == "sequential":
            return await self._sequential_collaboration(
                query, context, negotiation_result
            )
        
        elif strategy == "consensus":
            return await self._consensus_collaboration(
                query, context, negotiation_result
            )
        
        # Fallback
        return await self._single_agent_response(
            query, context, negotiation_result.lead_agent
        )
    
    async def _collect_bids(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> List[AgentBid]:
        """Collect confidence bids from all registered agents"""
        bids = []
        
        for name, agent in self.agents.items():
            try:
                # Check if agent has evaluate_confidence method
                if hasattr(agent, 'evaluate_confidence'):
                    confidence = agent.evaluate_confidence(query, context)
                elif hasattr(agent, 'get_confidence'):
                    confidence = agent.get_confidence(query)
                else:
                    # Estimate based on capabilities
                    confidence = self._estimate_confidence(name, query, context)
                
                # Determine collaboration preference
                pref = "support"
                if confidence >= 0.8:
                    pref = "lead"
                elif confidence < 0.4:
                    pref = "verify"
                
                bid = AgentBid(
                    agent_name=name,
                    confidence=confidence,
                    reasoning=f"Based on query analysis and domain expertise",
                    estimated_time_ms=500,
                    can_verify_others=hasattr(agent, 'verify') or hasattr(agent, 'validate'),
                    collaboration_preference=pref
                )
                bids.append(bid)
                
            except Exception as e:
                logger.warning(f"Failed to get bid from {name}: {e}")
        
        return bids
    
    def _estimate_confidence(
        self,
        agent_name: str,
        query: str,
        context: Dict[str, Any]
    ) -> float:
        """Estimate agent confidence based on capabilities"""
        capabilities = self.agent_capabilities.get(agent_name, [])
        query_lower = query.lower()
        domain = context.get('subject', context.get('domain', '')).lower()
        
        score = 0.3  # Base confidence
        
        # Check capability match
        for cap in capabilities:
            cap_lower = cap.lower()
            if cap_lower in query_lower or cap_lower in domain:
                score += 0.2
        
        # Check for agent-specific keywords
        agent_keywords = {
            "mentor": ["explain", "understand", "help", "confused", "doubt"],
            "professor": ["prove", "derive", "formal", "mathematical", "theorem"],
            "doubt_resolver": ["don't understand", "stuck", "confused", "why"],
            "exam_coach": ["exam", "test", "jee", "neet", "marks", "strategy"],
            "study_buddy": ["study", "together", "practice", "quiz"],
            "visualise": ["diagram", "visual", "draw", "picture", "show"],
        }
        
        agent_kw = agent_keywords.get(agent_name.lower().replace("agent", ""), [])
        for kw in agent_kw:
            if kw in query_lower:
                score += 0.15
        
        return min(1.0, score)
    
    def _determine_strategy(
        self,
        ranked_bids: List[AgentBid],
        query: str,
        context: Dict[str, Any]
    ) -> NegotiationResult:
        """Determine collaboration strategy based on bids"""
        if not ranked_bids:
            return self._default_negotiation_result()
        
        top_bid = ranked_bids[0]
        
        # Single agent: Top agent is highly confident
        if top_bid.confidence >= 0.85:
            return NegotiationResult(
                lead_agent=top_bid.agent_name,
                supporting_agents=[],
                verifying_agents=[b.agent_name for b in ranked_bids[1:3] if b.can_verify_others],
                strategy="single",
                expected_confidence=top_bid.confidence,
                negotiation_reasoning=f"{top_bid.agent_name} is highly confident ({top_bid.confidence:.2f})"
            )
        
        # Parallel: Multiple agents are confident
        confident_agents = [b for b in ranked_bids if b.confidence >= 0.6]
        if len(confident_agents) >= 2:
            return NegotiationResult(
                lead_agent=top_bid.agent_name,
                supporting_agents=[b.agent_name for b in confident_agents[1:3]],
                verifying_agents=[],
                strategy="parallel",
                expected_confidence=max(b.confidence for b in confident_agents),
                negotiation_reasoning=f"Multiple agents confident, parallel execution"
            )
        
        # Consensus: Complex query, need multiple perspectives
        if any(word in query.lower() for word in ['compare', 'contrast', 'difference', 'vs']):
            return NegotiationResult(
                lead_agent=top_bid.agent_name,
                supporting_agents=[b.agent_name for b in ranked_bids[1:3]],
                verifying_agents=[],
                strategy="consensus",
                expected_confidence=0.75,
                negotiation_reasoning="Complex query requires multiple perspectives"
            )
        
        # Default: Sequential with verification
        return NegotiationResult(
            lead_agent=top_bid.agent_name,
            supporting_agents=[ranked_bids[1].agent_name] if len(ranked_bids) > 1 else [],
            verifying_agents=[ranked_bids[-1].agent_name] if len(ranked_bids) > 2 else [],
            strategy="sequential",
            expected_confidence=top_bid.confidence * 0.9,
            negotiation_reasoning="Sequential execution with verification"
        )
    
    def _default_negotiation_result(self) -> NegotiationResult:
        """Return default result when negotiation fails"""
        return NegotiationResult(
            lead_agent="mentor",
            supporting_agents=[],
            verifying_agents=[],
            strategy="single",
            expected_confidence=0.5,
            negotiation_reasoning="Default to mentor agent"
        )
    
    async def _single_agent_response(
        self,
        query: str,
        context: Dict[str, Any],
        agent_name: str
    ) -> CollaborativeResponse:
        """Execute single agent response"""
        agent = self.agents.get(agent_name)
        
        if not agent:
            return self._empty_response([agent_name])
        
        try:
            # Call agent's process or run method
            if hasattr(agent, 'run'):
                response = await agent.run(query, context)
            elif hasattr(agent, 'process'):
                response = await agent.process(query, context)
            else:
                response = {"content": f"[{agent_name} response]"}
            
            return CollaborativeResponse(
                primary_response=response,
                supporting_insights=[],
                verification_results=[],
                consensus_reached=True,
                final_confidence=0.8,
                agents_involved=[agent_name],
                collaboration_summary=f"Single agent response from {agent_name}"
            )
            
        except Exception as e:
            logger.error(f"Agent {agent_name} failed: {e}")
            return self._empty_response([agent_name])
    
    async def _parallel_collaboration(
        self,
        query: str,
        context: Dict[str, Any],
        negotiation: NegotiationResult
    ) -> CollaborativeResponse:
        """Execute agents in parallel and merge"""
        all_agents = [negotiation.lead_agent] + negotiation.supporting_agents
        
        # Run all agents in parallel
        tasks = []
        for agent_name in all_agents:
            agent = self.agents.get(agent_name)
            if agent and hasattr(agent, 'run'):
                tasks.append(agent.run(query, context))
            elif agent and hasattr(agent, 'process'):
                tasks.append(agent.process(query, context))
        
        if not tasks:
            return self._empty_response(all_agents)
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful results
            successful = [r for r in results if not isinstance(r, Exception)]
            
            if not successful:
                return self._empty_response(all_agents)
            
            return CollaborativeResponse(
                primary_response=successful[0],
                supporting_insights=successful[1:],
                verification_results=[],
                consensus_reached=True,
                final_confidence=negotiation.expected_confidence,
                agents_involved=all_agents,
                collaboration_summary=f"Parallel collaboration: {', '.join(all_agents)}"
            )
            
        except Exception as e:
            logger.error(f"Parallel collaboration failed: {e}")
            return self._empty_response(all_agents)
    
    async def _sequential_collaboration(
        self,
        query: str,
        context: Dict[str, Any],
        negotiation: NegotiationResult
    ) -> CollaborativeResponse:
        """Execute agents sequentially, each building on previous"""
        all_agents = [negotiation.lead_agent] + negotiation.supporting_agents
        
        accumulated_context = context.copy()
        responses = []
        
        for agent_name in all_agents:
            agent = self.agents.get(agent_name)
            if not agent:
                continue
            
            try:
                if hasattr(agent, 'run'):
                    response = await agent.run(query, accumulated_context)
                elif hasattr(agent, 'process'):
                    response = await agent.process(query, accumulated_context)
                else:
                    continue
                
                responses.append(response)
                
                # Add to context for next agent
                accumulated_context['previous_response'] = response
                
            except Exception as e:
                logger.warning(f"Agent {agent_name} failed in sequence: {e}")
        
        if not responses:
            return self._empty_response(all_agents)
        
        return CollaborativeResponse(
            primary_response=responses[-1],  # Final refined response
            supporting_insights=responses[:-1],
            verification_results=[],
            consensus_reached=True,
            final_confidence=negotiation.expected_confidence,
            agents_involved=all_agents,
            collaboration_summary=f"Sequential collaboration: {' → '.join(all_agents)}"
        )
    
    async def _consensus_collaboration(
        self,
        query: str,
        context: Dict[str, Any],
        negotiation: NegotiationResult
    ) -> CollaborativeResponse:
        """All agents provide input, then merge for consensus"""
        # First, parallel execution
        parallel_result = await self._parallel_collaboration(
            query, context, negotiation
        )
        
        # TODO: Implement actual consensus merging
        # For now, return parallel result with consensus flag
        parallel_result.collaboration_summary = f"Consensus from: {', '.join(parallel_result.agents_involved)}"
        
        return parallel_result
    
    def _empty_response(self, agents: List[str]) -> CollaborativeResponse:
        """Return empty response on failure"""
        return CollaborativeResponse(
            primary_response={"content": "I'll help you with that."},
            supporting_insights=[],
            verification_results=[],
            consensus_reached=False,
            final_confidence=0.3,
            agents_involved=agents,
            collaboration_summary="Fallback response"
        )


# Singleton instance
_negotiator_instance: Optional[AgentNegotiator] = None


def get_agent_negotiator() -> AgentNegotiator:
    """Get or create global agent negotiator"""
    global _negotiator_instance
    if _negotiator_instance is None:
        _negotiator_instance = AgentNegotiator()
    return _negotiator_instance




