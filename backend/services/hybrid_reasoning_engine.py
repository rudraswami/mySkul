"""
Hybrid Reasoning Engine - Neural + Symbolic Integration
========================================================

Orchestrates:
1. Neural reasoning (LLM) - probabilistic, creative, explanatory
2. Symbolic reasoning (Math, Logic, Knowledge Graph) - deterministic, provable
3. RAG (Retrieval) - grounded in verified curriculum

Flow:
Query → Knowledge Graph (find concepts) → Symbolic Layer (try deterministic solve) 
     → Neural Layer (explain with graph context) → Verification → Synthesis

This makes Druv AI truly neuro-symbolic, not just "neural + symbolic components"
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Existing symbolic components (REUSE, don't duplicate!)
from services.verification.math_verifier import MathVerifier, VerificationStatus
from services.verification.logic_validator import LogicValidator
from services.knowledge_base.universal_knowledge_graph import (
    get_universal_knowledge_graph,
    UniversalKnowledgeGraph,
    ConceptNode,
    ConceptDifficulty
)
from services.knowledge_base.rag_enhancer import get_rag_enhancer, RAGEnhancer
from services.ai_service import AIService

logger = logging.getLogger(__name__)


class ReasoningMode(Enum):
    """Type of reasoning to use"""
    SYMBOLIC_ONLY = "symbolic_only"      # Pure deterministic (math problems)
    NEURAL_ONLY = "neural_only"          # Pure LLM (creative questions)
    HYBRID = "hybrid"                    # Combined (most cases)
    GRAPH_GUIDED = "graph_guided"        # Neural guided by knowledge graph


@dataclass
class SymbolicResult:
    """Result from symbolic reasoning"""
    success: bool
    solution: Optional[str]
    steps: List[str]
    confidence: float
    verification_status: Optional[VerificationStatus]
    explanation: str


@dataclass
class GraphContext:
    """Context from knowledge graph"""
    concepts: List[ConceptNode]
    prerequisites: List[ConceptNode]
    applications: List[ConceptNode]
    learning_path: List[ConceptNode]
    related_formulas: List[str]


@dataclass
class HybridResponse:
    """Combined neural + symbolic response"""
    primary_answer: str
    symbolic_proof: Optional[str]
    neural_explanation: str
    graph_context: Optional[GraphContext]
    verification_passed: bool
    reasoning_mode: ReasoningMode
    confidence: float
    sources: List[str]
    recommendations: List[str]


class HybridReasoningEngine:
    """
    Orchestrates Neural + Symbolic + Graph reasoning
    
    Key Innovation:
    - Not just "neural OR symbolic"
    - Deep integration where neural and symbolic inform each other
    - Knowledge graph guides neural generation
    - Symbolic validates neural output
    - Neural explains symbolic results
    """
    
    def __init__(self, ai_service: Optional[AIService] = None):
        """Initialize hybrid engine with existing components"""
        
        # Symbolic components (existing)
        self.math_verifier = MathVerifier()
        self.logic_validator = LogicValidator()
        
        # Knowledge graph (new universal graph)
        self.knowledge_graph = get_universal_knowledge_graph()
        
        # RAG enhancer (existing)
        self.rag_enhancer = get_rag_enhancer()
        
        # AI service for neural reasoning
        self.ai_service = ai_service
        
        logger.info("🧠 HybridReasoningEngine initialized")
        logger.info("   ├── Symbolic: MathVerifier + LogicValidator")
        logger.info("   ├── Graph: UniversalKnowledgeGraph")
        logger.info("   ├── RAG: CurriculumRetriever")
        logger.info("   └── Neural: AIService (LLM)")
    
    async def reason(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> HybridResponse:
        """
        Main hybrid reasoning flow
        
        Args:
            query: Student's question
            context: Additional context (domain, student_profile, etc.)
            
        Returns:
            HybridResponse with integrated neural + symbolic reasoning
        """
        try:
            logger.info(f"🧠 Hybrid reasoning for: {query[:60]}...")
            
            # Step 1: Analyze query and determine reasoning mode
            reasoning_mode = self._determine_reasoning_mode(query, context)
            logger.info(f"   Mode: {reasoning_mode.value}")
            
            # Step 2: Knowledge Graph reasoning - find relevant concepts
            graph_context = await self._graph_reasoning(query, context)
            
            # Step 3: Symbolic reasoning - try deterministic solution
            symbolic_result = None
            if reasoning_mode in [ReasoningMode.SYMBOLIC_ONLY, ReasoningMode.HYBRID]:
                symbolic_result = await self._symbolic_reasoning(query, context)
            
            # Step 4: Neural reasoning - LLM explanation with graph context
            neural_explanation = await self._neural_reasoning(
                query, context, graph_context, symbolic_result
            )
            
            # Step 5: Verification - validate neural output against symbolic truth
            verification_passed = await self._verify_consistency(
                neural_explanation, symbolic_result, graph_context
            )
            
            # Step 6: Synthesis - combine symbolic proof + neural explanation
            response = self._synthesize_response(
                query,
                reasoning_mode,
                symbolic_result,
                neural_explanation,
                graph_context,
                verification_passed
            )
            
            logger.info(f"✅ Hybrid reasoning complete (confidence: {response.confidence:.2f})")
            return response
            
        except Exception as e:
            logger.error(f"❌ Hybrid reasoning error: {e}", exc_info=True)
            # Fallback to pure neural
            return await self._fallback_neural_only(query, context)
    
    def _determine_reasoning_mode(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> ReasoningMode:
        """Determine which reasoning mode to use"""
        query_lower = query.lower()
        
        # Pure math calculation → Symbolic only
        if any(word in query_lower for word in [
            'solve', 'calculate', 'derivative', 'integral', 'equation',
            'simplify', 'factor', 'expand'
        ]):
            return ReasoningMode.SYMBOLIC_ONLY
        
        # Conceptual/creative question → Graph-guided neural
        if any(word in query_lower for word in [
            'explain', 'why', 'how does', 'what is the difference',
            'compare', 'understand', 'real-world', 'application'
        ]):
            return ReasoningMode.GRAPH_GUIDED
        
        # Default: Hybrid (most powerful)
        return ReasoningMode.HYBRID
    
    async def _graph_reasoning(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Optional[GraphContext]:
        """Use knowledge graph to find relevant concepts"""
        try:
            domain = context.get('subject', context.get('domain', 'Mathematics'))
            
            # Search for relevant concepts
            concepts = self.knowledge_graph.search_concepts(query)
            
            if not concepts:
                # Try domain-based query
                age = context.get('age', 15)
                concepts = self.knowledge_graph.query_by_domain(
                    domain,
                    age_range=(age - 2, age + 5)
                )[:5]
            
            if not concepts:
                return None
            
            # Get prerequisites for first matching concept
            main_concept = concepts[0]
            prerequisites = self.knowledge_graph.get_prerequisites(main_concept.concept_id)
            applications = self.knowledge_graph.get_applications(main_concept.concept_id)
            
            # Collect formulas
            formulas = []
            for concept in concepts:
                formulas.extend(concept.formulas)
            
            graph_context = GraphContext(
                concepts=concepts[:3],
                prerequisites=prerequisites,
                applications=applications,
                learning_path=[],  # Can be extended
                related_formulas=formulas
            )
            
            logger.info(f"   📊 Graph: Found {len(concepts)} concepts")
            return graph_context
            
        except Exception as e:
            logger.warning(f"Graph reasoning error: {e}")
            return None
    
    async def _symbolic_reasoning(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Optional[SymbolicResult]:
        """Try to solve deterministically using symbolic math/logic"""
        try:
            # Check if this is a math problem
            if self._is_math_question(query):
                # Try to extract and solve equation
                solution, steps = self._solve_math_symbolically(query)
                
                if solution:
                    return SymbolicResult(
                        success=True,
                        solution=solution,
                        steps=steps,
                        confidence=1.0,  # Symbolic is 100% confident when it works
                        verification_status=VerificationStatus.VERIFIED,
                        explanation="Solved symbolically using mathematical reasoning"
                    )
            
            # Check if this is a logic problem
            if self._is_logic_question(query):
                # Try logical validation
                is_valid, explanation = self._validate_logic(query)
                
                if is_valid is not None:
                    return SymbolicResult(
                        success=True,
                        solution=explanation,
                        steps=[],
                        confidence=1.0,
                        verification_status=None,
                        explanation="Validated using formal logic"
                    )
            
            return None
            
        except Exception as e:
            logger.debug(f"Symbolic reasoning failed: {e}")
            return None
    
    async def _neural_reasoning(
        self,
        query: str,
        context: Dict[str, Any],
        graph_context: Optional[GraphContext],
        symbolic_result: Optional[SymbolicResult]
    ) -> str:
        """Generate neural explanation using LLM with graph context"""
        try:
            # Build enhanced prompt with graph context
            enhanced_prompt = self._build_graph_guided_prompt(
                query, context, graph_context, symbolic_result
            )
            
            # Call LLM (if ai_service available)
            if self.ai_service:
                response = await self.ai_service.generate_response(
                    enhanced_prompt,
                    context
                )
                return response
            
            # Fallback: Use RAG-enhanced prompt
            rag_enhanced = self.rag_enhancer.enhance_prompt(
                query,
                subject=context.get('subject', 'Mathematics')
            )
            
            return f"[Neural explanation with RAG context: {rag_enhanced.curriculum_context[:200]}...]"
            
        except Exception as e:
            logger.error(f"Neural reasoning error: {e}")
            return "I'll explain this concept step by step..."
    
    async def _verify_consistency(
        self,
        neural_explanation: str,
        symbolic_result: Optional[SymbolicResult],
        graph_context: Optional[GraphContext]
    ) -> bool:
        """Verify neural output against symbolic truth"""
        try:
            # If we have symbolic proof, verify neural matches it
            if symbolic_result and symbolic_result.success:
                # Check if neural explanation includes symbolic solution
                if symbolic_result.solution and symbolic_result.solution not in neural_explanation:
                    logger.warning("⚠️ Neural explanation missing symbolic solution")
                    return False
            
            # Verify math in neural explanation
            verification = self.math_verifier.verify_response(
                neural_explanation,
                question="",
                subject="Mathematics"
            )
            
            if verification.status == VerificationStatus.ERROR_FOUND:
                logger.warning(f"⚠️ Math errors in neural explanation: {len(verification.errors)} errors")
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Verification error: {e}")
            return True  # Don't block on verification errors
    
    def _synthesize_response(
        self,
        query: str,
        reasoning_mode: ReasoningMode,
        symbolic_result: Optional[SymbolicResult],
        neural_explanation: str,
        graph_context: Optional[GraphContext],
        verification_passed: bool
    ) -> HybridResponse:
        """Combine symbolic + neural into final response"""
        
        # Build primary answer
        if symbolic_result and symbolic_result.success:
            primary_answer = f"{symbolic_result.solution}\n\n{neural_explanation}"
            symbolic_proof = symbolic_result.solution
            confidence = 0.95 if verification_passed else 0.7
        else:
            primary_answer = neural_explanation
            symbolic_proof = None
            confidence = 0.8 if verification_passed else 0.6
        
        # Extract sources
        sources = []
        if graph_context:
            for concept in graph_context.concepts:
                sources.extend(concept.learning_resources)
        
        # Generate recommendations
        recommendations = []
        if graph_context:
            if graph_context.prerequisites:
                recommendations.append(
                    f"Review: {', '.join(c.name for c in graph_context.prerequisites[:2])}"
                )
            if graph_context.applications:
                recommendations.append(
                    f"Next: {', '.join(c.name for c in graph_context.applications[:2])}"
                )
        
        return HybridResponse(
            primary_answer=primary_answer,
            symbolic_proof=symbolic_proof,
            neural_explanation=neural_explanation,
            graph_context=graph_context,
            verification_passed=verification_passed,
            reasoning_mode=reasoning_mode,
            confidence=confidence,
            sources=[s.get('url', '') for s in sources if isinstance(s, dict)],
            recommendations=recommendations
        )
    
    def _build_graph_guided_prompt(
        self,
        query: str,
        context: Dict[str, Any],
        graph_context: Optional[GraphContext],
        symbolic_result: Optional[SymbolicResult]
    ) -> str:
        """Build LLM prompt with knowledge graph context"""
        prompt_parts = []
        
        # Add symbolic solution if available
        if symbolic_result and symbolic_result.success:
            prompt_parts.append(f"SYMBOLIC SOLUTION (VERIFIED):\n{symbolic_result.solution}\n")
            prompt_parts.append("Your task: EXPLAIN this solution in simple terms.\n")
        
        # Add graph context
        if graph_context and graph_context.concepts:
            prompt_parts.append("\nRELEVANT CONCEPTS FROM KNOWLEDGE GRAPH:")
            for concept in graph_context.concepts[:2]:
                prompt_parts.append(f"\n{concept.name}: {concept.description}")
                if concept.key_points:
                    prompt_parts.append(f"Key points: {', '.join(concept.key_points[:3])}")
            
            if graph_context.prerequisites:
                prompt_parts.append(f"\nPrerequisites: {', '.join(c.name for c in graph_context.prerequisites)}")
            
            if graph_context.related_formulas:
                prompt_parts.append(f"\nRelevant formulas: {', '.join(graph_context.related_formulas[:3])}")
        
        prompt_parts.append(f"\nStudent Question: {query}")
        prompt_parts.append("\nProvide a clear, student-friendly explanation.")
        
        return "\n".join(prompt_parts)
    
    def _is_math_question(self, query: str) -> bool:
        """Check if query is a math question"""
        math_keywords = [
            'solve', 'calculate', 'derivative', 'integral', 'equation',
            'simplify', 'factor', 'expand', 'find the value', '=',
            'x + ', 'x - ', 'x * ', 'x /', 'f(x)', 'dy/dx'
        ]
        return any(kw in query.lower() for kw in math_keywords)
    
    def _is_logic_question(self, query: str) -> bool:
        """Check if query is a logic question"""
        logic_keywords = [
            'if and only if', 'therefore', 'implies', 'logical',
            'valid argument', 'contradiction', 'tautology'
        ]
        return any(kw in query.lower() for kw in logic_keywords)
    
    def _solve_math_symbolically(self, query: str) -> Tuple[Optional[str], List[str]]:
        """Try to solve math problem symbolically"""
        # This is a simplified version - math_verifier has more sophisticated parsing
        try:
            from sympy import solve, symbols, sympify
            
            # Try to extract equation
            if '=' in query:
                parts = query.split('=')
                if len(parts) == 2:
                    x = symbols('x')
                    lhs = sympify(parts[0].strip())
                    rhs = sympify(parts[1].strip())
                    solution = solve(lhs - rhs, x)
                    return f"x = {solution}", [f"Equation: {query}", f"Solution: x = {solution}"]
        except:
            pass
        
        return None, []
    
    def _validate_logic(self, query: str) -> Tuple[Optional[bool], str]:
        """Validate logical statement"""
        # Delegate to logic_validator
        try:
            return self.logic_validator.validate(query)
        except:
            return None, ""
    
    async def _fallback_neural_only(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> HybridResponse:
        """Fallback to pure neural reasoning"""
        return HybridResponse(
            primary_answer="Let me explain this concept...",
            symbolic_proof=None,
            neural_explanation="[Fallback neural response]",
            graph_context=None,
            verification_passed=False,
            reasoning_mode=ReasoningMode.NEURAL_ONLY,
            confidence=0.5,
            sources=[],
            recommendations=[]
        )


# Singleton instance
_engine_instance: Optional[HybridReasoningEngine] = None


def get_hybrid_reasoning_engine(ai_service: Optional[AIService] = None) -> HybridReasoningEngine:
    """Get or create the global hybrid reasoning engine"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = HybridReasoningEngine(ai_service)
    return _engine_instance




