"""
🧠 Cognitive Control Layer - Meta-Reasoning About Agent Selection
=================================================================

This module implements TRUE cognitive control: reasoning about
"who should think", "who should wait", and "who should defer".

ARCHITECTURE:
- Runs BEFORE agent selection
- Analyzes query semantics and agent capabilities
- Provides recommendations via context injection
- Agents can check recommendations and self-defer

INTEGRATION:
- Called by supervisor BEFORE _select_agents()
- Injects recommendations into context['_cognitive_control']
- Agents check context and respect control signals

This is TRUE cognition: the system reasons about reasoning itself,
not just executing predetermined flows.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ControlDecision(Enum):
    """Types of cognitive control decisions"""
    SHOULD_THINK = "should_think"       # Agent should actively engage
    SHOULD_WAIT = "should_wait"         # Agent should wait for others first
    SHOULD_DEFER = "should_defer"       # Agent should defer to another
    SHOULD_VERIFY = "should_verify"     # Agent should verify others' work
    SHOULD_LEAD = "should_lead"         # Agent should take the lead
    MAY_ABSTAIN = "may_abstain"         # Agent may choose to skip


class QueryComplexity(Enum):
    """Complexity levels for cognitive control"""
    SIMPLE = "simple"           # Single-step, clear answer
    MODERATE = "moderate"       # Multi-step, needs explanation
    COMPLEX = "complex"         # Deep reasoning, multiple perspectives
    AMBIGUOUS = "ambiguous"     # Unclear, needs clarification


@dataclass
class AgentControlSignal:
    """Control signal for a specific agent"""
    agent_name: str
    decision: ControlDecision
    priority: int                    # 1 = highest priority
    reasoning: str
    defer_to: Optional[str] = None   # If deferring, who to defer to
    wait_for: List[str] = field(default_factory=list)  # Agents to wait for
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'agent': self.agent_name,
            'decision': self.decision.value,
            'priority': self.priority,
            'reasoning': self.reasoning,
            'defer_to': self.defer_to,
            'wait_for': self.wait_for
        }


@dataclass
class CognitiveControlPlan:
    """Complete control plan for a query"""
    query: str
    complexity: QueryComplexity
    primary_agents: List[str]        # Agents that should think
    supporting_agents: List[str]     # Agents that should support
    verification_agents: List[str]   # Agents that should verify
    signals: Dict[str, AgentControlSignal]  # Signals per agent
    reasoning: str                   # Why this plan
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'complexity': self.complexity.value,
            'primary': self.primary_agents,
            'supporting': self.supporting_agents,
            'verifying': self.verification_agents,
            'signals': {k: v.to_dict() for k, v in self.signals.items()},
            'reasoning': self.reasoning
        }


class CognitiveControlLayer:
    """
    Meta-reasoning layer that decides "who should think".
    
    This is TRUE cognitive control: the system reasons about its own
    reasoning process, deciding which agents are appropriate and how
    they should coordinate.
    
    Key capabilities:
    - Semantic analysis of query requirements
    - Agent capability matching
    - Priority and sequencing decisions
    - Deferral and waiting logic
    """
    
    # Agent capability profiles (what each agent is good at)
    AGENT_CAPABILITIES = {
        'mentor': {
            'strengths': ['explain', 'clarify', 'motivate', 'emotional', 'conceptual'],
            'domains': ['general', 'concepts', 'understanding'],
            'style': 'supportive'
        },
        'professor': {
            'strengths': ['solve', 'prove', 'calculate', 'verify', 'formal'],
            'domains': ['math', 'physics', 'chemistry', 'science'],
            'style': 'rigorous'
        },
        'visualise': {
            'strengths': ['diagram', 'visual', 'graph', 'chart', 'illustrate'],
            'domains': ['visual', 'spatial', 'data'],
            'style': 'visual'
        },
        'doubt_resolver': {
            'strengths': ['doubt', 'confused', 'stuck', 'misconception'],
            'domains': ['troubleshooting', 'clarification'],
            'style': 'diagnostic'
        },
        'exam_coach': {
            'strengths': ['exam', 'test', 'strategy', 'time', 'marks'],
            'domains': ['jee', 'neet', 'board', 'competitive'],
            'style': 'strategic'
        },
        'study_buddy': {
            'strengths': ['study', 'plan', 'schedule', 'revision'],
            'domains': ['planning', 'organization'],
            'style': 'collaborative'
        }
    }
    
    def __init__(self):
        self._last_plan: Optional[CognitiveControlPlan] = None
    
    def analyze_query_requirements(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze query to understand what kind of cognitive processing is needed.
        
        Returns requirements like:
        - Needs calculation
        - Needs explanation
        - Needs verification
        - Needs visualization
        - Emotional support needed
        """
        query_lower = query.lower()
        requirements = {
            'needs_calculation': False,
            'needs_explanation': False,
            'needs_verification': False,
            'needs_visualization': False,
            'needs_emotional_support': False,
            'needs_exam_strategy': False,
            'needs_doubt_resolution': False,
            'complexity_signals': []
        }
        
        # Calculation signals
        calc_signals = ['solve', 'calculate', 'find', 'compute', 'what is', 'evaluate']
        if any(s in query_lower for s in calc_signals):
            requirements['needs_calculation'] = True
            requirements['complexity_signals'].append('calculation_required')
        
        # Explanation signals
        explain_signals = ['explain', 'why', 'how does', 'what is', 'concept', 'understand']
        if any(s in query_lower for s in explain_signals):
            requirements['needs_explanation'] = True
            requirements['complexity_signals'].append('explanation_required')
        
        # Verification signals
        verify_signals = ['check', 'verify', 'is this correct', 'right', 'wrong']
        if any(s in query_lower for s in verify_signals):
            requirements['needs_verification'] = True
            requirements['complexity_signals'].append('verification_required')
        
        # Visualization signals
        visual_signals = ['diagram', 'graph', 'draw', 'visualize', 'picture', 'show me']
        if any(s in query_lower for s in visual_signals):
            requirements['needs_visualization'] = True
            requirements['complexity_signals'].append('visualization_required')
        
        # Emotional signals
        emotional_signals = ['stressed', 'worried', 'scared', 'help me', 'struggling', 'difficult']
        if any(s in query_lower for s in emotional_signals):
            requirements['needs_emotional_support'] = True
            requirements['complexity_signals'].append('emotional_support_needed')
        
        # Exam signals
        exam_signals = ['exam', 'test', 'jee', 'neet', 'marks', 'time management']
        if any(s in query_lower for s in exam_signals):
            requirements['needs_exam_strategy'] = True
            requirements['complexity_signals'].append('exam_context')
        
        # Doubt signals
        doubt_signals = ['confused', 'doubt', 'stuck', "don't understand", 'misconception']
        if any(s in query_lower for s in doubt_signals):
            requirements['needs_doubt_resolution'] = True
            requirements['complexity_signals'].append('doubt_present')
        
        return requirements
    
    def determine_complexity(self, query: str, requirements: Dict[str, Any]) -> QueryComplexity:
        """Determine query complexity based on analysis"""
        signals = requirements.get('complexity_signals', [])
        
        # Multiple requirements = complex
        requirement_count = sum([
            requirements.get('needs_calculation', False),
            requirements.get('needs_explanation', False),
            requirements.get('needs_verification', False),
            requirements.get('needs_visualization', False),
            requirements.get('needs_emotional_support', False)
        ])
        
        # Word count and structure
        word_count = len(query.split())
        has_multiple_questions = query.count('?') > 1
        
        if requirement_count >= 3 or (has_multiple_questions and word_count > 30):
            return QueryComplexity.COMPLEX
        elif requirement_count >= 2 or word_count > 20:
            return QueryComplexity.MODERATE
        elif '?' not in query and requirement_count == 0:
            return QueryComplexity.AMBIGUOUS
        else:
            return QueryComplexity.SIMPLE
    
    def match_agents_to_requirements(
        self,
        requirements: Dict[str, Any],
        available_agents: List[str]
    ) -> Dict[str, float]:
        """
        Score each agent based on how well they match requirements.
        
        Returns dict of agent_name -> match_score (0-1)
        """
        scores = {}
        
        for agent in available_agents:
            profile = self.AGENT_CAPABILITIES.get(agent, {})
            strengths = profile.get('strengths', [])
            
            score = 0.0
            matches = 0
            
            # Check each requirement against agent strengths
            if requirements.get('needs_calculation'):
                if any(s in strengths for s in ['solve', 'calculate', 'formal']):
                    score += 0.3
                    matches += 1
            
            if requirements.get('needs_explanation'):
                if any(s in strengths for s in ['explain', 'clarify', 'conceptual']):
                    score += 0.25
                    matches += 1
            
            if requirements.get('needs_verification'):
                if any(s in strengths for s in ['verify', 'formal']):
                    score += 0.2
                    matches += 1
            
            if requirements.get('needs_visualization'):
                if any(s in strengths for s in ['diagram', 'visual', 'graph']):
                    score += 0.3
                    matches += 1
            
            if requirements.get('needs_emotional_support'):
                if any(s in strengths for s in ['motivate', 'emotional']):
                    score += 0.25
                    matches += 1
            
            if requirements.get('needs_exam_strategy'):
                if any(s in strengths for s in ['exam', 'strategy']):
                    score += 0.3
                    matches += 1
            
            if requirements.get('needs_doubt_resolution'):
                if any(s in strengths for s in ['doubt', 'confused', 'misconception']):
                    score += 0.3
                    matches += 1
            
            # Normalize
            if matches > 0:
                score = min(1.0, score)
            
            scores[agent] = score
        
        return scores
    
    def create_control_plan(
        self,
        query: str,
        context: Dict[str, Any],
        available_agents: List[str]
    ) -> CognitiveControlPlan:
        """
        Create a cognitive control plan for the query.
        
        This is the main reasoning method - it decides:
        - Who should think (primary agents)
        - Who should support (secondary agents)
        - Who should verify (verification agents)
        - Who should wait or defer
        """
        # Analyze requirements
        requirements = self.analyze_query_requirements(query, context)
        complexity = self.determine_complexity(query, requirements)
        
        # Score agents
        scores = self.match_agents_to_requirements(requirements, available_agents)
        
        # Sort by score
        ranked_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Categorize agents based on scores and complexity
        primary_agents = []
        supporting_agents = []
        verification_agents = []
        signals = {}
        
        for agent, score in ranked_agents:
            if score >= 0.3:
                if len(primary_agents) < 2:  # Max 2 primary
                    primary_agents.append(agent)
                    signals[agent] = AgentControlSignal(
                        agent_name=agent,
                        decision=ControlDecision.SHOULD_THINK,
                        priority=len(primary_agents),
                        reasoning=f"High match score ({score:.2f}) for query requirements"
                    )
                elif len(supporting_agents) < 2:  # Max 2 supporting
                    supporting_agents.append(agent)
                    signals[agent] = AgentControlSignal(
                        agent_name=agent,
                        decision=ControlDecision.SHOULD_WAIT,
                        priority=len(primary_agents) + len(supporting_agents),
                        reasoning=f"Good match ({score:.2f}) but primary slots filled",
                        wait_for=primary_agents.copy()
                    )
            elif score >= 0.1:
                if complexity in [QueryComplexity.COMPLEX, QueryComplexity.MODERATE]:
                    verification_agents.append(agent)
                    signals[agent] = AgentControlSignal(
                        agent_name=agent,
                        decision=ControlDecision.SHOULD_VERIFY,
                        priority=10,  # Low priority
                        reasoning=f"Moderate match ({score:.2f}) - assigned to verify",
                        wait_for=primary_agents + supporting_agents
                    )
                else:
                    signals[agent] = AgentControlSignal(
                        agent_name=agent,
                        decision=ControlDecision.MAY_ABSTAIN,
                        priority=99,
                        reasoning=f"Low match ({score:.2f}) for this query"
                    )
            else:
                signals[agent] = AgentControlSignal(
                    agent_name=agent,
                    decision=ControlDecision.SHOULD_DEFER,
                    priority=99,
                    reasoning=f"No match ({score:.2f}) for query requirements",
                    defer_to=primary_agents[0] if primary_agents else None
                )
        
        # Ensure at least one primary agent
        if not primary_agents and ranked_agents:
            first_agent = ranked_agents[0][0]
            primary_agents.append(first_agent)
            signals[first_agent] = AgentControlSignal(
                agent_name=first_agent,
                decision=ControlDecision.SHOULD_LEAD,
                priority=1,
                reasoning="Fallback: No strong matches, selected highest scorer"
            )
        
        # Build reasoning string
        reasoning_parts = [
            f"Complexity: {complexity.value}",
            f"Requirements: {', '.join(requirements['complexity_signals']) or 'general'}",
            f"Primary agents: {', '.join(primary_agents)}",
        ]
        if supporting_agents:
            reasoning_parts.append(f"Supporting: {', '.join(supporting_agents)}")
        if verification_agents:
            reasoning_parts.append(f"Verifying: {', '.join(verification_agents)}")
        
        plan = CognitiveControlPlan(
            query=query,
            complexity=complexity,
            primary_agents=primary_agents,
            supporting_agents=supporting_agents,
            verification_agents=verification_agents,
            signals=signals,
            reasoning=" | ".join(reasoning_parts)
        )
        
        self._last_plan = plan
        logger.info(f"🧠 Cognitive control plan: {plan.reasoning}")
        
        return plan
    
    def get_agent_signal(
        self,
        agent_name: str,
        plan: CognitiveControlPlan
    ) -> Optional[AgentControlSignal]:
        """Get the control signal for a specific agent"""
        return plan.signals.get(agent_name)
    
    def should_agent_participate(
        self,
        agent_name: str,
        plan: CognitiveControlPlan
    ) -> bool:
        """Quick check if agent should participate at all"""
        signal = plan.signals.get(agent_name)
        if not signal:
            return False
        
        return signal.decision not in [
            ControlDecision.SHOULD_DEFER,
            ControlDecision.MAY_ABSTAIN
        ]


def inject_cognitive_control(
    context: Dict[str, Any],
    query: str,
    available_agents: List[str]
) -> CognitiveControlPlan:
    """
    Inject cognitive control into context.
    
    Call this in supervisor BEFORE _select_agents().
    """
    controller = CognitiveControlLayer()
    plan = controller.create_control_plan(query, context, available_agents)
    
    # Inject into context
    context['_cognitive_control'] = plan.to_dict()
    context['_cognitive_signals'] = {
        name: signal.to_dict() 
        for name, signal in plan.signals.items()
    }
    
    return plan


def get_cognitive_signal(
    context: Dict[str, Any],
    agent_name: str
) -> Optional[Dict[str, Any]]:
    """
    Get cognitive control signal for an agent from context.
    
    Agents can call this to check if they should participate.
    """
    signals = context.get('_cognitive_signals', {})
    return signals.get(agent_name)

