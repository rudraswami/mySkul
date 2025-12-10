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
    
    # Trivial patterns (instant response)
    TRIVIAL_PATTERNS = [
        r'^(hi|hello|hey|namaste|yo|sup)[\s!?.]*$',
        r'^(thanks?|thank you|thx|ty)[\s!?.]*$',
        r'^(bye|goodbye|see you)[\s!?.]*$',
        r'^(ok|okay|sure|yes|no|yep|nope)[\s!?.]*$',
        r'^(good|great|nice|cool|awesome)[\s!?.]*$',
    ]
    
    def __init__(self, db=None):
        """Initialize routing engine"""
        self.db = db
        self._compiled_trivial = [re.compile(p, re.IGNORECASE) for p in self.TRIVIAL_PATTERNS]
        logger.info("🧠 IntelligentRoutingEngine initialized - Smart routing active")
    
    async def route(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> RoutingDecision:
        """
        Make intelligent routing decision for a query.
        
        Args:
            query: The student's question
            context: Context including subject, user_id, mastery, etc.
            
        Returns:
            RoutingDecision with complete pipeline configuration
        """
        logger.info(f"🧠 Routing query: {query[:60]}...")
        
        # Step 1: Check for trivial queries (instant response)
        if self._is_trivial(query):
            return self._trivial_decision(query)
        
        # Step 2: Analyze query complexity
        complexity_score = self._analyze_complexity(query, context)
        
        # Step 3: Get student context (mastery, history)
        student_context = await self._get_student_context(context)
        
        # Step 4: Determine complexity level
        complexity = self._score_to_complexity(complexity_score, student_context)
        
        # Step 5: Select pipeline based on complexity
        decision = self._select_pipeline(query, complexity, context, student_context)
        
        logger.info(f"✅ Routing: {decision.pipeline.value} (complexity: {complexity.value}, confidence: {decision.confidence:.2f})")
        
        return decision
    
    def _is_trivial(self, query: str) -> bool:
        """Check if query is trivial (greetings, thanks, etc.)"""
        query_clean = query.strip()
        
        # Very short queries (< 4 words) that match trivial patterns
        if len(query_clean.split()) <= 4:
            for pattern in self._compiled_trivial:
                if pattern.match(query_clean):
                    return True
        
        return False
    
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
            use_memory=False,
            priority_factors={'speed': 1.0, 'depth': 0.0}
        )
    
    def _analyze_complexity(self, query: str, context: Dict[str, Any]) -> float:
        """
        Analyze query complexity on a 0-1 scale.
        
        Factors:
        - Pattern matching for complexity indicators
        - Query length
        - Subject difficulty
        - Question structure
        """
        query_lower = query.lower()
        score = 0.3  # Base complexity for any educational query
        
        # Factor 1: Complexity patterns
        for pattern, weight in self.COMPLEXITY_PATTERNS.items():
            if pattern in query_lower:
                score += weight * 0.3
        
        # Factor 2: Query length (longer = more complex)
        word_count = len(query.split())
        if word_count > 20:
            score += 0.15
        elif word_count > 10:
            score += 0.08
        
        # Factor 3: Mathematical content
        math_indicators = [
            r'\d+\s*[+\-*/^=]\s*\d+',  # Equations
            r'f\(x\)',  # Functions
            r'd[xy]/d[xy]',  # Derivatives
            r'∫|integral',  # Integrals
            r'\\frac|\\sqrt',  # LaTeX
        ]
        for pattern in math_indicators:
            if re.search(pattern, query, re.IGNORECASE):
                score += 0.2
                break
        
        # Factor 4: Subject multiplier
        subject = context.get('subject', 'general').lower()
        multiplier = self.SUBJECT_MULTIPLIERS.get(subject, 1.0)
        score *= multiplier
        
        # Factor 5: Multi-part questions
        if any(phrase in query_lower for phrase in ['and also', 'additionally', 'furthermore', 'as well as']):
            score += 0.15
        
        # Factor 6: Deep understanding indicators
        deep_indicators = [
            'intuition', 'fundamental', 'underlying', 'principle',
            'conceptually', 'theoretically', 'mathematically', 'rigorously'
        ]
        if any(ind in query_lower for ind in deep_indicators):
            score += 0.2
        
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
        student_context: Dict[str, Any]
    ) -> RoutingDecision:
        """Select the appropriate pipeline based on complexity"""
        
        query_lower = query.lower()
        subject = context.get('subject', 'General').lower()
        
        # === SIMPLE QUERIES ===
        # Only factual lookups, definitions - STILL use multi-agent but minimal
        if complexity == QueryComplexity.SIMPLE:
            return RoutingDecision(
                pipeline=RecommendedPipeline.MULTI_AGENT,  # NOT fast path!
                complexity=complexity,
                confidence=0.8,
                reasoning="Simple query but using multi-agent for quality",
                agents_to_activate=['mentor', 'professor'],
                tools_to_enable=['knowledge_search'],
                enable_verification=True,  # Always verify!
                enable_visual=student_context.get('visual_learner', False),
                max_iterations=3,
                timeout_seconds=15.0,
                use_knowledge_graph=True,
                use_memory=True,
                priority_factors={'speed': 0.6, 'depth': 0.4}
            )
        
        # === MODERATE QUERIES ===
        # Standard explanations - full multi-agent
        elif complexity == QueryComplexity.MODERATE:
            return RoutingDecision(
                pipeline=RecommendedPipeline.MULTI_AGENT,
                complexity=complexity,
                confidence=0.85,
                reasoning="Moderate complexity - full multi-agent orchestration",
                agents_to_activate=['mentor', 'professor', 'visualise'],
                tools_to_enable=['knowledge_search', 'formula_lookup', 'fact_checker'],
                enable_verification=True,
                enable_visual=True,
                max_iterations=5,
                timeout_seconds=25.0,
                use_knowledge_graph=True,
                use_memory=True,
                priority_factors={'speed': 0.4, 'depth': 0.6}
            )
        
        # === COMPLEX QUERIES ===
        # Multi-step problems - hybrid reasoning
        elif complexity == QueryComplexity.COMPLEX:
            # Check if it needs visual sync
            visual_keywords = ['diagram', 'draw', 'visualize', 'show', 'graph', 'plot']
            needs_visual_sync = any(kw in query_lower for kw in visual_keywords)
            
            return RoutingDecision(
                pipeline=RecommendedPipeline.VISUAL_SYNC if needs_visual_sync else RecommendedPipeline.HYBRID_REASONING,
                complexity=complexity,
                confidence=0.9,
                reasoning="Complex query - hybrid reasoning with symbolic verification",
                agents_to_activate=['mentor', 'professor', 'visualise', 'doubt_resolver'],
                tools_to_enable=['knowledge_search', 'formula_lookup', 'calculator', 'fact_checker', 'code_executor'],
                enable_verification=True,
                enable_visual=True,
                max_iterations=8,
                timeout_seconds=35.0,
                use_knowledge_graph=True,
                use_memory=True,
                priority_factors={'speed': 0.2, 'depth': 0.8}
            )
        
        # === DEEP REASONING ===
        # Proofs, derivations, analysis - full ReAct
        else:  # DEEP_REASONING
            return RoutingDecision(
                pipeline=RecommendedPipeline.REACT_AGENTIC,
                complexity=complexity,
                confidence=0.95,
                reasoning="Deep reasoning query - full ReAct with tools and verification",
                agents_to_activate=['mentor', 'professor', 'visualise', 'doubt_resolver', 'exam_coach'],
                tools_to_enable=['knowledge_search', 'formula_lookup', 'calculator', 'fact_checker', 'code_executor'],
                enable_verification=True,
                enable_visual=True,
                max_iterations=12,  # More iterations for deep reasoning
                timeout_seconds=45.0,
                use_knowledge_graph=True,
                use_memory=True,
                priority_factors={'speed': 0.1, 'depth': 0.9}
            )
    
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

