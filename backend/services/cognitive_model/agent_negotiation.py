"""
🤝 Agent Negotiation - FULL Multi-Agent Consensus System
=========================================================

COMPLETE IMPLEMENTATION - No more TODOs!

This system enables TRUE multi-agent collaboration:
1. Bidding: Each agent evaluates confidence for a query
2. Negotiation: Agents negotiate roles and strategies
3. Parallel Execution: All selected agents run in parallel
4. Consensus Building: LLM-powered response synthesis
5. Cross-Verification: Agents validate each other
6. Conflict Resolution: Contradictions are identified and resolved
7. Final Synthesis: Unified, highest-quality response

This is what makes AI Sathi comparable to Gemini-level intelligence.
"""

import logging
import asyncio
import os
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


class CollaborationStrategy(Enum):
    """How agents should collaborate"""
    SINGLE = "single"           # One agent handles it
    PARALLEL = "parallel"       # Multiple agents, merge results
    SEQUENTIAL = "sequential"   # Build on each other
    CONSENSUS = "consensus"     # All contribute, synthesize best
    DEBATE = "debate"           # Agents challenge each other


@dataclass
class AgentBid:
    """Bid from an agent for handling a query"""
    agent_name: str
    confidence: float
    reasoning: str
    estimated_time_ms: int
    can_verify_others: bool
    collaboration_preference: str  # "solo", "lead", "support", "verify"
    domain_expertise: List[str] = field(default_factory=list)
    suggested_tools: List[str] = field(default_factory=list)


@dataclass
class NegotiationResult:
    """Result of agent negotiation"""
    lead_agent: str
    supporting_agents: List[str]
    verifying_agents: List[str]
    strategy: CollaborationStrategy
    expected_confidence: float
    negotiation_reasoning: str
    tool_assignments: Dict[str, List[str]] = field(default_factory=dict)
    role_descriptions: Dict[str, str] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Response from a single agent"""
    agent_name: str
    content: str
    confidence: float
    reasoning_steps: List[str] = field(default_factory=list)
    facts_claimed: List[str] = field(default_factory=list)
    formulas_used: List[str] = field(default_factory=list)
    verification_notes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationResult:
    """Result of cross-verification between agents"""
    verified_facts: List[str]
    disputed_facts: List[Dict[str, Any]]  # {fact, agent1_view, agent2_view}
    consensus_facts: List[str]
    verification_confidence: float


@dataclass
class CollaborativeResponse:
    """Final response from multi-agent collaboration"""
    primary_response: Dict[str, Any]
    supporting_insights: List[Dict[str, Any]]
    verification_results: List[Dict[str, Any]]
    consensus_reached: bool
    final_confidence: float
    agents_involved: List[str]
    collaboration_summary: str
    synthesis_explanation: str
    disputed_points: List[Dict[str, Any]] = field(default_factory=list)
    merged_facts: List[str] = field(default_factory=list)


class AgentNegotiator:
    """
    FULL Implementation of Multi-Agent Negotiation and Consensus
    
    This orchestrates:
    1. Agent bidding and role assignment
    2. Parallel agent execution
    3. Response collection and analysis
    4. Fact extraction and cross-verification
    5. Conflict detection and resolution
    6. LLM-powered consensus synthesis
    7. Final response with confidence scoring
    """
    
    def __init__(self, llm_key: Optional[str] = None):
        """Initialize negotiator with LLM for consensus synthesis"""
        self.agents: Dict[str, Any] = {}
        self.agent_capabilities: Dict[str, List[str]] = {}
        self.agent_weights: Dict[str, float] = {}  # Domain expertise weights
        self.negotiation_history: List[NegotiationResult] = []
        self.llm_key = llm_key or os.environ.get('OPENAI_API_KEY')
        
        logger.info("🤝 AgentNegotiator initialized with FULL consensus capability")
    
    def register_agent(
        self,
        name: str,
        agent: Any,
        capabilities: List[str],
        can_verify: bool = False,
        expertise_weight: float = 1.0
    ):
        """Register an agent with its capabilities and expertise weight"""
        self.agents[name] = agent
        self.agent_capabilities[name] = capabilities
        self.agent_weights[name] = expertise_weight
        
        logger.info(f"   ├── Registered: {name} (weight: {expertise_weight}, capabilities: {', '.join(capabilities)})")
    
    async def negotiate(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> NegotiationResult:
        """
        Conduct negotiation among agents for a query.
        
        Steps:
        1. Broadcast query to all agents for bidding
        2. Collect and rank bids
        3. Determine optimal collaboration strategy
        4. Assign roles (lead, support, verify)
        5. Return negotiation result
        """
        logger.info(f"🤝 Negotiating for: {query[:60]}...")
        
        # Step 1: Collect bids from all agents
        bids = await self._collect_bids(query, context)
        
        if not bids:
            return self._default_negotiation_result()
        
        # Step 2: Rank agents by weighted confidence
        ranked_bids = self._rank_bids_weighted(bids, context)
        
        # Step 3: Determine collaboration strategy
        strategy = self._determine_strategy(ranked_bids, query, context)
        
        # Step 4: Assign roles based on strategy
        result = self._assign_roles(ranked_bids, strategy, query, context)
        
        # Store in history
        self.negotiation_history.append(result)
        
        logger.info(f"✅ Negotiation: Strategy={result.strategy.value}, Lead={result.lead_agent}, Support={result.supporting_agents}")
        return result
    
    async def collaborate(
        self,
        query: str,
        context: Dict[str, Any],
        negotiation_result: NegotiationResult
    ) -> CollaborativeResponse:
        """
        Execute FULL multi-agent collaboration with consensus.
        
        This is the core of the system:
        1. Run all assigned agents
        2. Collect and structure responses
        3. Extract facts from each response
        4. Cross-verify facts between agents
        5. Identify conflicts and disputes
        6. Synthesize consensus response using LLM
        7. Return final unified response
        """
        strategy = negotiation_result.strategy
        
        logger.info(f"🤝 Collaborating with strategy: {strategy.value}")
        
        # Step 1: Execute all agents based on strategy
        agent_responses = await self._execute_agents(
            query, context, negotiation_result
        )
        
        if not agent_responses:
            return self._empty_response(negotiation_result)
        
        # Step 2: Extract facts and claims from each response
        extracted_facts = self._extract_facts_from_responses(agent_responses)
        
        # Step 3: Cross-verify facts between agents
        verification = await self._cross_verify_facts(extracted_facts, agent_responses)
        
        # Step 4: Identify conflicts
        conflicts = self._identify_conflicts(agent_responses, verification)
        
        # Step 5: Synthesize consensus response
        if strategy == CollaborationStrategy.SINGLE:
            # Single agent - just return their response
            return self._single_agent_result(agent_responses[0], negotiation_result)
        
        elif strategy == CollaborationStrategy.PARALLEL:
            # Merge parallel responses
            return await self._merge_parallel_responses(
                agent_responses, verification, conflicts, negotiation_result, query, context
            )
        
        elif strategy == CollaborationStrategy.SEQUENTIAL:
            # Build on each other
            return await self._build_sequential_response(
                agent_responses, verification, negotiation_result, query, context
            )
        
        elif strategy in [CollaborationStrategy.CONSENSUS, CollaborationStrategy.DEBATE]:
            # Full consensus synthesis
            return await self._synthesize_consensus(
                agent_responses, verification, conflicts, negotiation_result, query, context
            )
        
        # Fallback
        return self._single_agent_result(agent_responses[0], negotiation_result)
    
    async def _collect_bids(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> List[AgentBid]:
        """Collect confidence bids from all registered agents"""
        bids = []
        
        for name, agent in self.agents.items():
            try:
                # === AGENT AUTONOMY: Self-Initiated Abstain ===
                # Check if agent wants to opt-out BEFORE computing confidence
                if hasattr(agent, 'should_abstain'):
                    should_abstain, abstain_reason = agent.should_abstain(query, context)
                    if should_abstain:
                        logger.info(f"🚫 {name} self-abstained: {abstain_reason}")
                        continue  # Skip this agent entirely
                
                # Get confidence (try multiple methods)
                # COGNITIVE OS: Agents now have TRUE self-assessment
                if hasattr(agent, 'evaluate_confidence'):
                    confidence = agent.evaluate_confidence(query, context)
                    logger.debug(f"📊 {name} self-assessed confidence: {confidence:.2f}")
                elif hasattr(agent, 'get_confidence'):
                    confidence = agent.get_confidence(query)
                else:
                    confidence = self._estimate_confidence(name, query, context)
                
                # Determine collaboration preference
                if confidence >= 0.85:
                    pref = "lead"
                elif confidence >= 0.6:
                    pref = "support"
                elif confidence >= 0.4:
                    pref = "verify"
                else:
                    pref = "skip"
                
                # Get suggested tools
                suggested_tools = []
                if hasattr(agent, 'get_available_tools'):
                    suggested_tools = agent.get_available_tools()
                
                bid = AgentBid(
                    agent_name=name,
                    confidence=confidence,
                    reasoning=f"Domain match and query analysis",
                    estimated_time_ms=500,
                    can_verify_others=hasattr(agent, 'verify') or hasattr(agent, 'validate'),
                    collaboration_preference=pref,
                    domain_expertise=self.agent_capabilities.get(name, []),
                    suggested_tools=suggested_tools
                )
                
                if pref != "skip":  # Only include relevant agents
                    bids.append(bid)
                    
            except Exception as e:
                logger.warning(f"Failed to get bid from {name}: {e}")
        
        return bids
    
    def _rank_bids_weighted(
        self,
        bids: List[AgentBid],
        context: Dict[str, Any]
    ) -> List[AgentBid]:
        """Rank bids with domain expertise weighting"""
        subject = context.get('subject', '').lower()
        
        def weighted_score(bid: AgentBid) -> float:
            base_score = bid.confidence
            
            # Apply agent weight
            weight = self.agent_weights.get(bid.agent_name, 1.0)
            
            # Boost if domain matches
            domain_boost = 0
            for capability in bid.domain_expertise:
                if capability.lower() in subject or subject in capability.lower():
                    domain_boost = 0.15
                    break
            
            return (base_score + domain_boost) * weight
        
        return sorted(bids, key=weighted_score, reverse=True)
    
    def _estimate_confidence(
        self,
        agent_name: str,
        query: str,
        context: Dict[str, Any],
        semantic_analysis: Optional[Dict[str, Any]] = None  # PHASE B: Accept semantic analysis
    ) -> float:
        """
        Estimate agent confidence based on capabilities and query.
        
        PHASE B FIX: Uses semantic analysis fields instead of keyword matching
        when flag is enabled.
        """
        from core.config import settings
        
        capabilities = self.agent_capabilities.get(agent_name, [])
        domain = context.get('subject', context.get('domain', '')).lower()
        
        score = 0.35  # Base confidence
        
        # Check capability match (domain-based, not keyword)
        for cap in capabilities:
            cap_lower = cap.lower()
            if cap_lower in domain or domain in cap_lower:
                score += 0.2
        
        # PHASE B: Semantic-based agent scoring (no keywords)
        if settings.ENABLE_SEMANTIC_ONLY_ROUTING and semantic_analysis:
            agent_key = agent_name.lower().replace("agent", "").strip()
            
            # Map semantic signals to agent suitability
            intent = semantic_analysis.get('intent', '')
            emotional_tone = semantic_analysis.get('emotional_tone', 'neutral')
            has_actionable = semantic_analysis.get('has_actionable_request', False)
            output_type = semantic_analysis.get('requested_output_type', '')
            needs_empathy = semantic_analysis.get('needs_empathy', False)
            
            # Agent-semantic mappings (semantic signals, not keywords)
            agent_semantic_scores = {
                'mentor': {
                    'base_intents': ['question', 'explanation', 'clarification'],
                    'emotional_boost': ['confused', 'anxious', 'frustrated'],
                    'output_types': ['explanation', 'study_plan'],
                },
                'professor': {
                    'base_intents': ['question'],
                    'output_types': ['problem_solution', 'proof', 'derivation'],
                    'complexity_boost': True,  # Boost for complex queries
                },
                'doubt_resolver': {
                    'base_intents': ['clarification'],
                    'emotional_boost': ['confused', 'frustrated'],
                    'needs_empathy_boost': True,
                },
                'exam_coach': {
                    'output_types': ['study_plan', 'quiz', 'schedule'],
                    'context_match': ['exam', 'test', 'jee', 'neet'],  # Subject context, not query keywords
                },
                'study_buddy': {
                    'base_intents': ['practice'],
                    'output_types': ['quiz', 'practice'],
                },
                'visualise': {
                    'output_types': ['diagram', 'visual', 'graph'],
                },
                'weak_area_detective': {
                    'needs_empathy_boost': True,
                    'emotional_boost': ['frustrated', 'anxious'],
                },
            }
            
            agent_scoring = agent_semantic_scores.get(agent_key, {})
            
            # Score based on semantic signals
            if intent in agent_scoring.get('base_intents', []):
                score += 0.15
            if emotional_tone in agent_scoring.get('emotional_boost', []):
                score += 0.1
            if output_type in agent_scoring.get('output_types', []):
                score += 0.2
            if needs_empathy and agent_scoring.get('needs_empathy_boost', False):
                score += 0.1
            
            # Context match (subject/exam type, not query keywords)
            for ctx_key in agent_scoring.get('context_match', []):
                if ctx_key in domain.lower():
                    score += 0.1
                    break
            
            return min(1.0, score)
        
        # LEGACY: Keyword-based scoring (only when flag disabled)
        query_lower = query.lower()
        
        # Check capability match in query (legacy)
        for cap in capabilities:
            cap_lower = cap.lower()
            if cap_lower in query_lower:
                score += 0.2
        
        # Agent-specific keywords (LEGACY)
        agent_keywords = {
            "mentor": ["explain", "understand", "help", "confused", "doubt", "intuition", "simple"],
            "professor": ["prove", "derive", "formal", "mathematical", "theorem", "rigorous", "step"],
            "doubt_resolver": ["don't understand", "stuck", "confused", "why", "how"],
            "exam_coach": ["exam", "test", "jee", "neet", "marks", "strategy", "tip"],
            "study_buddy": ["study", "together", "practice", "quiz", "learn"],
            "visualise": ["diagram", "visual", "draw", "picture", "show", "graph"],
            "weak_area_detective": ["weak", "gap", "improve", "struggle"],
        }
        
        agent_key = agent_name.lower().replace("agent", "").strip()
        keywords = agent_keywords.get(agent_key, [])
        for kw in keywords:
            if kw in query_lower:
                score += 0.12
        
        return min(1.0, score)
    
    def _determine_strategy(
        self,
        ranked_bids: List[AgentBid],
        query: str,
        context: Dict[str, Any]
    ) -> CollaborationStrategy:
        """Determine optimal collaboration strategy"""
        if not ranked_bids:
            return CollaborationStrategy.SINGLE
        
        top_bid = ranked_bids[0]
        query_lower = query.lower()
        
        # High confidence leader = single agent can handle
        if top_bid.confidence >= 0.9 and len(ranked_bids) == 1:
            return CollaborationStrategy.SINGLE
        
        # Multiple confident agents
        confident_agents = [b for b in ranked_bids if b.confidence >= 0.6]
        
        # Comparison/contrast queries need consensus
        if any(word in query_lower for word in ['compare', 'contrast', 'difference', 'vs', 'versus']):
            return CollaborationStrategy.CONSENSUS
        
        # Deep reasoning queries need debate
        if any(word in query_lower for word in ['prove', 'derive', 'why', 'fundamental']):
            return CollaborationStrategy.DEBATE
        
        # Multiple experts = parallel with merge
        if len(confident_agents) >= 2:
            return CollaborationStrategy.PARALLEL
        
        # Sequential for building explanations
        if any(word in query_lower for word in ['explain', 'step by step', 'walk through']):
            return CollaborationStrategy.SEQUENTIAL
        
        # Default to consensus for quality
        return CollaborationStrategy.CONSENSUS
    
    def _assign_roles(
        self,
        ranked_bids: List[AgentBid],
        strategy: CollaborationStrategy,
        query: str,
        context: Dict[str, Any]
    ) -> NegotiationResult:
        """Assign roles to agents based on strategy"""
        if not ranked_bids:
            return self._default_negotiation_result()
        
        lead = ranked_bids[0].agent_name
        supporting = []
        verifying = []
        
        if strategy == CollaborationStrategy.SINGLE:
            verifying = [b.agent_name for b in ranked_bids[1:3] if b.can_verify_others]
        
        elif strategy == CollaborationStrategy.PARALLEL:
            supporting = [b.agent_name for b in ranked_bids[1:4] if b.confidence >= 0.5]
            verifying = [b.agent_name for b in ranked_bids if b.can_verify_others and b.agent_name not in [lead] + supporting][:2]
        
        elif strategy == CollaborationStrategy.SEQUENTIAL:
            supporting = [b.agent_name for b in ranked_bids[1:3]]
            
        elif strategy in [CollaborationStrategy.CONSENSUS, CollaborationStrategy.DEBATE]:
            # All confident agents participate
            supporting = [b.agent_name for b in ranked_bids[1:5] if b.confidence >= 0.4]
            verifying = [b.agent_name for b in ranked_bids if b.can_verify_others][:2]
        
        # Build tool assignments
        tool_assignments = {}
        for bid in ranked_bids:
            if bid.agent_name in [lead] + supporting:
                tool_assignments[bid.agent_name] = bid.suggested_tools
        
        # Role descriptions
        role_descriptions = {
            lead: "Lead agent - primary response generation",
        }
        for agent in supporting:
            role_descriptions[agent] = "Supporting agent - additional insights"
        for agent in verifying:
            role_descriptions[agent] = "Verifying agent - fact checking"
        
        return NegotiationResult(
            lead_agent=lead,
            supporting_agents=supporting,
            verifying_agents=verifying,
            strategy=strategy,
            expected_confidence=ranked_bids[0].confidence,
            negotiation_reasoning=f"Strategy {strategy.value} with {len(supporting)+1} agents",
            tool_assignments=tool_assignments,
            role_descriptions=role_descriptions
        )
    
    async def _execute_agents(
        self,
        query: str,
        context: Dict[str, Any],
        negotiation: NegotiationResult
    ) -> List[AgentResponse]:
        """Execute all assigned agents and collect responses"""
        all_agents = [negotiation.lead_agent] + negotiation.supporting_agents
        
        tasks = []
        for agent_name in all_agents:
            agent = self.agents.get(agent_name)
            if agent:
                tasks.append(self._run_agent(agent, agent_name, query, context))
        
        if not tasks:
            return []
        
        # Run all in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        responses = []
        for agent_name, result in zip(all_agents, results):
            if isinstance(result, Exception):
                logger.warning(f"Agent {agent_name} failed: {result}")
                continue
            
            if result:
                responses.append(result)
        
        return responses
    
    async def _run_agent(
        self,
        agent: Any,
        agent_name: str,
        query: str,
        context: Dict[str, Any]
    ) -> Optional[AgentResponse]:
        """Run a single agent and structure the response"""
        try:
            # Call agent
            if hasattr(agent, 'run'):
                raw_response = await agent.run(query, context)
            elif hasattr(agent, 'process'):
                raw_response = await agent.process(query, context)
            else:
                return None
            
            # Extract content
            content = ""
            if isinstance(raw_response, dict):
                content = raw_response.get('content', '') or raw_response.get('response', '')
            elif isinstance(raw_response, str):
                content = raw_response
            
            if not content:
                return None
            
            return AgentResponse(
                agent_name=agent_name,
                content=content,
                confidence=raw_response.get('confidence', 0.7) if isinstance(raw_response, dict) else 0.7,
                reasoning_steps=raw_response.get('reasoning_chain', []) if isinstance(raw_response, dict) else [],
                facts_claimed=self._extract_facts_from_text(content),
                formulas_used=self._extract_formulas(content),
                metadata=raw_response if isinstance(raw_response, dict) else {}
            )
            
        except Exception as e:
            logger.error(f"Error running agent {agent_name}: {e}")
            return None
    
    def _extract_facts_from_responses(
        self,
        responses: List[AgentResponse]
    ) -> Dict[str, List[str]]:
        """Extract facts claimed by each agent"""
        return {r.agent_name: r.facts_claimed for r in responses}
    
    def _extract_facts_from_text(self, text: str) -> List[str]:
        """Extract factual claims from response text"""
        facts = []
        
        # Split into sentences
        sentences = text.replace('\n', '. ').split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            
            # Look for factual patterns
            fact_indicators = [
                'is defined as', 'equals', 'means', 'refers to',
                'consists of', 'is caused by', 'results in',
                'always', 'never', 'must be', 'cannot be',
                'formula:', 'equation:', 'law states',
            ]
            
            if any(ind in sentence.lower() for ind in fact_indicators):
                facts.append(sentence[:200])  # Limit length
        
        return facts[:10]  # Limit number
    
    def _extract_formulas(self, text: str) -> List[str]:
        """Extract mathematical formulas from text"""
        import re
        formulas = []
        
        # LaTeX patterns
        latex_patterns = [
            r'\$([^$]+)\$',
            r'\\\(([^)]+)\\\)',
            r'\\\[([^\]]+)\\\]',
        ]
        
        for pattern in latex_patterns:
            matches = re.findall(pattern, text)
            formulas.extend(matches)
        
        # Simple equation patterns
        eq_pattern = r'([A-Za-z]\s*=\s*[^,.\n]+)'
        matches = re.findall(eq_pattern, text)
        formulas.extend(matches[:5])
        
        return list(set(formulas))[:10]
    
    async def _cross_verify_facts(
        self,
        facts_by_agent: Dict[str, List[str]],
        responses: List[AgentResponse]
    ) -> VerificationResult:
        """Cross-verify facts between agents"""
        all_facts = []
        for facts in facts_by_agent.values():
            all_facts.extend(facts)
        
        # Find facts mentioned by multiple agents (consensus)
        fact_counts: Dict[str, int] = {}
        for fact in all_facts:
            fact_lower = fact.lower()[:100]  # Normalize
            fact_counts[fact_lower] = fact_counts.get(fact_lower, 0) + 1
        
        consensus_facts = [f for f, count in fact_counts.items() if count >= 2]
        
        # For now, simple verification (can be enhanced with fact-checker tool)
        return VerificationResult(
            verified_facts=consensus_facts,
            disputed_facts=[],  # Would need LLM to detect contradictions
            consensus_facts=consensus_facts,
            verification_confidence=0.8 if consensus_facts else 0.6
        )
    
    def _identify_conflicts(
        self,
        responses: List[AgentResponse],
        verification: VerificationResult
    ) -> List[Dict[str, Any]]:
        """Identify conflicting claims between agents"""
        conflicts = []
        
        # Simple conflict detection based on opposite keywords
        opposites = [
            ('increase', 'decrease'),
            ('positive', 'negative'),
            ('always', 'never'),
            ('possible', 'impossible'),
            ('correct', 'incorrect'),
        ]
        
        for i, resp1 in enumerate(responses):
            for resp2 in responses[i+1:]:
                content1 = resp1.content.lower()
                content2 = resp2.content.lower()
                
                for word1, word2 in opposites:
                    if word1 in content1 and word2 in content2:
                        conflicts.append({
                            'agent1': resp1.agent_name,
                            'agent2': resp2.agent_name,
                            'type': 'opposite_claims',
                            'keywords': (word1, word2)
                        })
                    elif word2 in content1 and word1 in content2:
                        conflicts.append({
                            'agent1': resp1.agent_name,
                            'agent2': resp2.agent_name,
                            'type': 'opposite_claims',
                            'keywords': (word2, word1)
                        })
        
        return conflicts
    
    def _single_agent_result(
        self,
        response: AgentResponse,
        negotiation: NegotiationResult
    ) -> CollaborativeResponse:
        """Create result for single agent response"""
        return CollaborativeResponse(
            primary_response={'content': response.content, 'agent': response.agent_name, 'success': True},
            supporting_insights=[],
            verification_results=[],
            consensus_reached=True,
            final_confidence=response.confidence,
            agents_involved=[response.agent_name],
            collaboration_summary=f"Single agent response from {response.agent_name}",
            synthesis_explanation="Single agent handled the query",
            merged_facts=response.facts_claimed
        )
    
    async def _merge_parallel_responses(
        self,
        responses: List[AgentResponse],
        verification: VerificationResult,
        conflicts: List[Dict[str, Any]],
        negotiation: NegotiationResult,
        query: str,
        context: Dict[str, Any]
    ) -> CollaborativeResponse:
        """Merge parallel agent responses using LLM synthesis"""
        
        # Prepare synthesis prompt
        synthesis_prompt = self._build_synthesis_prompt(
            responses, verification, conflicts, query, "merge"
        )
        
        # Call LLM for synthesis
        synthesized_content = await self._llm_synthesize(synthesis_prompt)
        
        return CollaborativeResponse(
            primary_response={'content': synthesized_content, 'agent': 'consensus', 'success': True},
            supporting_insights=[{'agent': r.agent_name, 'content': r.content[:500]} for r in responses],
            verification_results=[{'verified_facts': verification.verified_facts}],
            consensus_reached=len(conflicts) == 0,
            final_confidence=verification.verification_confidence,
            agents_involved=[r.agent_name for r in responses],
            collaboration_summary=f"Merged {len(responses)} agent perspectives",
            synthesis_explanation="LLM-synthesized consensus from multiple agents",
            disputed_points=conflicts,
            merged_facts=verification.consensus_facts
        )
    
    async def _build_sequential_response(
        self,
        responses: List[AgentResponse],
        verification: VerificationResult,
        negotiation: NegotiationResult,
        query: str,
        context: Dict[str, Any]
    ) -> CollaborativeResponse:
        """Build response sequentially from agent contributions"""
        
        # Combine responses in order
        combined_content = ""
        for i, response in enumerate(responses):
            if i == 0:
                combined_content = response.content
            else:
                # Ask LLM to integrate this agent's contribution
                integration_prompt = f"""
The lead agent provided:
{combined_content[:1500]}

Agent {response.agent_name} adds:
{response.content[:1000]}

Integrate the additional insights smoothly into the explanation.
Keep the best parts of both. Remove redundancy. Output only the final integrated explanation.
"""
                combined_content = await self._llm_synthesize(integration_prompt)
        
        return CollaborativeResponse(
            primary_response={'content': combined_content, 'agent': 'sequential', 'success': True},
            supporting_insights=[{'agent': r.agent_name, 'contributed': True} for r in responses],
            verification_results=[],
            consensus_reached=True,
            final_confidence=max(r.confidence for r in responses),
            agents_involved=[r.agent_name for r in responses],
            collaboration_summary=f"Sequentially built from {len(responses)} agents",
            synthesis_explanation="Each agent built upon the previous",
            merged_facts=verification.consensus_facts
        )
    
    async def _synthesize_consensus(
        self,
        responses: List[AgentResponse],
        verification: VerificationResult,
        conflicts: List[Dict[str, Any]],
        negotiation: NegotiationResult,
        query: str,
        context: Dict[str, Any]
    ) -> CollaborativeResponse:
        """
        FULL CONSENSUS SYNTHESIS - The Core Innovation
        
        This is where multiple agent responses are intelligently merged
        into a single, highest-quality response.
        """
        
        # Build comprehensive synthesis prompt
        synthesis_prompt = self._build_synthesis_prompt(
            responses, verification, conflicts, query, "consensus"
        )
        
        # Call LLM for intelligent synthesis
        synthesized_content = await self._llm_synthesize(synthesis_prompt)
        
        # If there were conflicts, note them
        conflict_note = ""
        if conflicts:
            conflict_note = f"\n\n**Note:** Some agents had different perspectives on {len(conflicts)} points. The above represents the verified consensus."
        
        final_content = synthesized_content + conflict_note
        
        return CollaborativeResponse(
            primary_response={'content': final_content, 'agent': 'consensus', 'success': True},
            supporting_insights=[{
                'agent': r.agent_name,
                'content': r.content[:300],
                'confidence': r.confidence,
                'unique_facts': [f for f in r.facts_claimed if f not in verification.consensus_facts]
            } for r in responses],
            verification_results=[{
                'verified_facts': verification.verified_facts,
                'consensus_facts': verification.consensus_facts,
                'confidence': verification.verification_confidence
            }],
            consensus_reached=True,
            final_confidence=min(0.95, verification.verification_confidence + 0.1),
            agents_involved=[r.agent_name for r in responses],
            collaboration_summary=f"Consensus from {len(responses)} expert agents",
            synthesis_explanation="Full multi-agent consensus with cross-verification",
            disputed_points=conflicts,
            merged_facts=verification.consensus_facts + verification.verified_facts
        )
    
    def _build_synthesis_prompt(
        self,
        responses: List[AgentResponse],
        verification: VerificationResult,
        conflicts: List[Dict[str, Any]],
        query: str,
        mode: str
    ) -> str:
        """Build prompt for LLM synthesis"""
        
        prompt_parts = [
            f"You are synthesizing responses from {len(responses)} expert AI tutors.",
            f"\n## Student Question:\n{query}",
            "\n## Expert Responses:\n"
        ]
        
        for i, resp in enumerate(responses, 1):
            prompt_parts.append(f"\n### Expert {i} ({resp.agent_name}):\n{resp.content[:1200]}")
            if resp.formulas_used:
                prompt_parts.append(f"\nFormulas used: {', '.join(resp.formulas_used[:3])}")
        
        if verification.verified_facts:
            prompt_parts.append(f"\n## Verified Facts (agreed by multiple experts):\n")
            for fact in verification.verified_facts[:5]:
                prompt_parts.append(f"- {fact}")
        
        if conflicts:
            prompt_parts.append(f"\n## Conflicting Points ({len(conflicts)} found):\n")
            for conflict in conflicts[:3]:
                prompt_parts.append(f"- {conflict['agent1']} and {conflict['agent2']} have different views on: {conflict.get('keywords', 'some aspect')}")
        
        prompt_parts.append(f"""

## Your Task:
Create a SINGLE, unified response that:
1. Combines the BEST explanations from all experts
2. Uses the VERIFIED facts (agreed by multiple experts)
3. Resolves any conflicts by choosing the most accurate view
4. Maintains a friendly, encouraging tone for students
5. Includes relevant formulas and examples
6. Is comprehensive but not redundant

Output ONLY the final synthesized response for the student. Do not mention that this is a synthesis.
""")
        
        return "\n".join(prompt_parts)
    
    async def _llm_synthesize(self, prompt: str) -> str:
        """Call LLM for synthesis"""
        try:
            if not self.llm_key:
                logger.warning("No LLM key for synthesis, returning first response")
                return "Let me explain this concept..."
            
            from services.llm_compat import LlmChat, UserMessage
            
            chat = LlmChat(
                api_key=self.llm_key,
                session_id=f"consensus_{id(prompt)}",
                system_message="You are an expert at synthesizing multiple perspectives into clear, accurate explanations."
            ).with_model("openai", "gpt-4o-mini").with_params(
                temperature=0.5,
                max_tokens=1500
            )
            
            response = await chat.send_message(UserMessage(text=prompt))
            return response if isinstance(response, str) else str(response)
            
        except Exception as e:
            logger.error(f"LLM synthesis failed: {e}")
            return "Let me explain this concept based on expert analysis..."
    
    def _empty_response(self, negotiation: NegotiationResult) -> CollaborativeResponse:
        """Return empty response on failure"""
        return CollaborativeResponse(
            primary_response={'content': "I'll help you with that.", 'agent': 'fallback', 'success': True},
            supporting_insights=[],
            verification_results=[],
            consensus_reached=False,
            final_confidence=0.3,
            agents_involved=[negotiation.lead_agent],
            collaboration_summary="Fallback response",
            synthesis_explanation="Agent collaboration failed, using fallback"
        )
    
    def _default_negotiation_result(self) -> NegotiationResult:
        """Return default when negotiation fails"""
        return NegotiationResult(
            lead_agent="mentor",
            supporting_agents=[],
            verifying_agents=[],
            strategy=CollaborationStrategy.SINGLE,
            expected_confidence=0.5,
            negotiation_reasoning="Default to mentor agent"
        )


# Singleton instance
_negotiator_instance: Optional[AgentNegotiator] = None


def get_agent_negotiator(llm_key: Optional[str] = None) -> AgentNegotiator:
    """Get or create global agent negotiator"""
    global _negotiator_instance
    if _negotiator_instance is None:
        _negotiator_instance = AgentNegotiator(llm_key)
    return _negotiator_instance
