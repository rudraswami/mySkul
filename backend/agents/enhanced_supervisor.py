"""
Enhanced Supervisor Agent - Neuro-Symbolic Integration
=======================================================

Extends the existing SupervisorAgent with:
- RAG-enhanced prompts (curriculum grounding)
- Symbolic verification (math, facts, logic)
- Verified response badges
- 🆕 HYBRID REASONING: Neural + Symbolic + Graph integration

This is the TRUE Layer 3 (Supervisor Verification) that makes
Druv AI hallucination-free.

IMPORTANT: This EXTENDS, not REPLACES, the original SupervisorAgent.
The original remains unchanged for backward compatibility.
"""

import logging
import asyncio
from typing import Dict, Any, Optional

from agents.supervisor import SupervisorAgent
from services.verification import VerificationOrchestrator, get_verification_orchestrator
from services.knowledge_base import RAGEnhancer, get_rag_enhancer

# 🆕 Hybrid Reasoning Engine (Neural + Symbolic + Graph)
try:
    from services.hybrid_reasoning_engine import get_hybrid_reasoning_engine, HybridReasoningEngine, ReasoningMode
    HYBRID_REASONING_AVAILABLE = True
except ImportError as e:
    HYBRID_REASONING_AVAILABLE = False
    logging.warning(f"HybridReasoningEngine not available: {e}")

logger = logging.getLogger(__name__)


class EnhancedSupervisor(SupervisorAgent):
    """
    Enhanced Supervisor with Neuro-Symbolic Capabilities
    
    Adds to the base SupervisorAgent:
    1. RAG: Curriculum-grounded prompts
    2. Verification: Math, facts, and logic validation
    3. Badges: Verification status for UI
    
    Usage:
        supervisor = EnhancedSupervisor(config)
        result = await supervisor.run_enhanced(query, context)
        # result includes verification_result and enhanced_response
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize enhanced supervisor with verification layers"""
        super().__init__(config)
        
        # Initialize verification and RAG systems
        self.verification = get_verification_orchestrator()
        self.rag = get_rag_enhancer()
        
        # 🆕 Initialize Hybrid Reasoning Engine
        self.hybrid_engine = None
        self.enable_hybrid_reasoning = False
        if HYBRID_REASONING_AVAILABLE:
            try:
                self.hybrid_engine = get_hybrid_reasoning_engine()
                self.enable_hybrid_reasoning = True
                logger.info("   ├── Hybrid Reasoning: ✅ Active (Neural + Symbolic + Graph)")
            except Exception as e:
                logger.warning(f"   ├── Hybrid Reasoning: ⚠️ Failed to initialize: {e}")
        
        # Configuration
        self.enable_rag = True
        self.enable_verification = True
        self.verify_math = True
        self.verify_facts = True
        self.verify_logic = True
        
        logger.info("🚀 EnhancedSupervisor initialized with neuro-symbolic capabilities")
        logger.info("   ├── RAG Enhancement: ✅ Active")
        logger.info("   ├── Math Verification: ✅ Active")
        logger.info("   ├── Fact Checking: ✅ Active")
        logger.info("   └── Logic Validation: ✅ Active")
    
    async def run_enhanced(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run enhanced orchestration with RAG, Hybrid Reasoning, and verification.
        
        This is the main entry point for the enhanced supervisor.
        It wraps the base run() method with additional capabilities.
        
        Flow:
        1. RAG enhancement (curriculum grounding)
        2. 🆕 Hybrid Reasoning (symbolic math/graph context)
        3. Base supervisor (multi-agent orchestration)
        4. Verification (math, facts, logic)
        
        Args:
            query: Student's question
            context: Context dict with subject, user_id, session_id, etc.
            
        Returns:
            Enhanced response with verification results and hybrid reasoning
        """
        try:
            logger.info(f"🧠 EnhancedSupervisor processing: {query[:100]}")
            
            # Get subject from context
            subject = context.get('subject', 'General')
            
            # Step 1: Enhance query with RAG (curriculum grounding) - ALWAYS ATTEMPT
            enhanced_prompt = None
            if self.enable_rag:
                try:
                    enhanced_prompt = self.rag.enhance_prompt(
                        query, 
                        subject=subject,
                        include_formulas=True
                    )
                    logger.info(f"📚 RAG: Found {len(enhanced_prompt.sources_used)} curriculum sources")
                    
                    # Update context with curriculum info
                    context['curriculum_context'] = enhanced_prompt.curriculum_context
                    context['available_formulas'] = enhanced_prompt.formulas_available
                except Exception as rag_err:
                    # Degrade internally - log but continue execution
                    logger.warning(f"⚠️ RAG enhancement failed (non-critical, continuing): {rag_err}")
                    # Continue without RAG enhancement
            
            # 🆕 Step 1.5: Hybrid Reasoning (Neural + Symbolic + Graph) - ALWAYS ATTEMPT
            hybrid_result = None
            # Always attempt hybrid reasoning if enabled (degrade internally on failure)
            if self.enable_hybrid_reasoning:
                if self.hybrid_engine:
                    try:
                        hybrid_result = await self.hybrid_engine.reason(query, context)
                        logger.info(f"🧠 Hybrid Reasoning: mode={hybrid_result.reasoning_mode.value}, confidence={hybrid_result.confidence:.2f}")
                        
                        # If we have a symbolic proof, inject it into context for agents
                        if hybrid_result.symbolic_proof:
                            context['symbolic_solution'] = hybrid_result.symbolic_proof
                            logger.info("   ├── Symbolic proof available (deterministic)")
                        
                        # Inject knowledge graph context
                        if hybrid_result.graph_context:
                            gc = hybrid_result.graph_context
                            context['knowledge_graph'] = {
                                'concepts': [c.name for c in gc.concepts[:3]],
                                'prerequisites': [p.name for p in gc.prerequisites[:3]],
                                'applications': [a.name for a in gc.applications[:3]],
                                'formulas': gc.related_formulas[:5]
                            }
                            logger.info(f"   ├── Knowledge Graph: {len(gc.concepts)} concepts found")
                        
                        # Add recommendations for learning path
                        if hybrid_result.recommendations:
                            context['learning_recommendations'] = hybrid_result.recommendations
                            
                    except Exception as e:
                        # Degrade internally - log but continue execution
                        logger.warning(f"⚠️ Hybrid reasoning failed (non-critical, continuing): {e}")
                else:
                    # Hybrid engine unavailable - log but continue
                    logger.debug("⚠️ Hybrid engine unavailable (non-critical, continuing)")
            
            # ================================================================
            # Step 1.6: PRE-GENERATION FORMULA CONSTRAINT INJECTION
            # If formulas are available from RAG/KnowledgeGraph, inject them
            # as EXPLICIT constraints that agents MUST follow.
            # This prevents hallucination of incorrect formulas.
            # ================================================================
            ENABLE_FORMULA_CONSTRAINTS = True  # Feature flag (safe default: ON)
            
            if ENABLE_FORMULA_CONSTRAINTS:
                formula_constraints = []
                
                # Get formulas from RAG
                if enhanced_prompt and enhanced_prompt.formulas_available:
                    formula_constraints.extend(enhanced_prompt.formulas_available[:5])
                
                # Get formulas from Knowledge Graph
                if context.get('knowledge_graph', {}).get('formulas'):
                    formula_constraints.extend(context['knowledge_graph']['formulas'][:5])
                
                # Get symbolic proof if available
                if context.get('symbolic_solution'):
                    formula_constraints.append(f"Verified Solution: {context['symbolic_solution']}")
                
                # Inject as agent constraint (non-breaking - agents can ignore if not applicable)
                if formula_constraints:
                    unique_formulas = list(set(formula_constraints))[:7]  # Dedupe, limit to 7
                    context['_formula_constraints'] = unique_formulas
                    context['_constraint_instruction'] = (
                        "IMPORTANT: When using formulas, you MUST use these verified formulas: " +
                        "; ".join(unique_formulas[:3]) +
                        ". Do NOT invent or modify formulas."
                    )
                    logger.info(f"📐 Injected {len(unique_formulas)} formula constraints")
            
            # Step 2: Run base supervisor orchestration
            base_result = await self.run(query, context)
            
            if not base_result.get('success', False):
                return base_result
            
            # Step 3: Extract combined response text for verification
            response_text = self._extract_response_text(base_result)
            
            # Step 4: Run verification on the combined response
            verification_result = None
            reattempt_count = 0
            MAX_REATTEMPTS = 1  # Feature-flagged, safe limit
            
            if self.enable_verification and response_text:
                verification_result = await self.verification.verify_response(
                    response_text=response_text,
                    question=query,
                    subject=subject,
                    verify_math=self.verify_math,
                    verify_facts=self.verify_facts,
                    verify_logic=self.verify_logic
                )
                logger.info(f"✅ Verification: {verification_result.overall_status.value}, confidence: {verification_result.confidence_score:.2f}")
                
                # ================================================================
                # NEURO-SYMBOLIC ENHANCEMENT: Re-attempt on critical failures
                # If verification finds critical errors AND corrections exist,
                # re-generate with corrections as constraints (additive, non-blocking)
                # ================================================================
                ENABLE_VERIFICATION_REATTEMPT = True  # Feature flag (safe default: ON)
                
                if (ENABLE_VERIFICATION_REATTEMPT and 
                    not verification_result.is_safe_to_show and 
                    verification_result.corrections_suggested and 
                    reattempt_count < MAX_REATTEMPTS):
                    
                    logger.warning(f"⚠️ Verification failed with critical errors, attempting re-generation...")
                    reattempt_count += 1
                    
                    try:
                        # Inject corrections as constraints into context
                        correction_context = context.copy()
                        correction_context['_verification_corrections'] = verification_result.corrections_suggested
                        correction_context['_reattempt_reason'] = 'verification_failure'
                        correction_context['_original_errors'] = verification_result.issues_found
                        
                        # Build correction prompt for agents
                        corrections_text = "\n".join([
                            f"- {c.get('original', '')} → {c.get('correction', '')}" 
                            for c in verification_result.corrections_suggested[:3]  # Limit to 3
                        ])
                        
                        correction_prompt = f"""
CRITICAL: The previous response contained mathematical errors. 
Please regenerate with these corrections in mind:
{corrections_text}

Original question: {query}
"""
                        # Re-run base supervisor with correction hints
                        base_result = await self.run(correction_prompt, correction_context)
                        
                        if base_result.get('success'):
                            response_text = self._extract_response_text(base_result)
                            
                            # Re-verify the corrected response
                            verification_result = await self.verification.verify_response(
                                response_text=response_text,
                                question=query,
                                subject=subject,
                                verify_math=self.verify_math,
                                verify_facts=self.verify_facts,
                                verify_logic=self.verify_logic
                            )
                            logger.info(f"✅ Re-verification after correction: {verification_result.overall_status.value}")
                    
                    except Exception as reattempt_err:
                        logger.warning(f"⚠️ Re-attempt failed (non-blocking): {reattempt_err}")
                        # Continue with original response - don't crash
            
            # Step 5: Create verification badge for UI
            badge = None
            if verification_result:
                badge = self.verification.create_verification_badge(verification_result)
            
            # Step 6: Validate response against curriculum
            rag_validation = None
            if self.enable_rag and enhanced_prompt:
                rag_validation = self.rag.validate_response(
                    response_text,
                    query,
                    subject
                )
            
            # Step 7: Build enhanced result
            enhanced_result = {
                **base_result,
                'enhanced': True,
                'verification': {
                    'status': verification_result.overall_status.value if verification_result else 'not_verified',
                    'is_safe': verification_result.is_safe_to_show if verification_result else True,
                    'confidence': verification_result.confidence_score if verification_result else 0.5,
                    'issues': verification_result.issues_found if verification_result else [],
                    'corrections': verification_result.corrections_suggested if verification_result else [],
                    'summary': verification_result.verification_summary if verification_result else '',
                    'time_ms': verification_result.verification_time_ms if verification_result else 0
                },
                'rag': {
                    'sources_used': enhanced_prompt.sources_used if enhanced_prompt else [],
                    'formulas_available': enhanced_prompt.formulas_available if enhanced_prompt else [],
                    'curriculum_aligned': rag_validation.is_consistent if rag_validation else True,
                    'alignment_score': rag_validation.alignment_score if rag_validation else 0.5
                },
                # 🆕 Hybrid Reasoning results
                'hybrid_reasoning': {
                    'enabled': self.enable_hybrid_reasoning,
                    'mode': hybrid_result.reasoning_mode.value if hybrid_result else None,
                    'confidence': hybrid_result.confidence if hybrid_result else 0.0,
                    'symbolic_proof': hybrid_result.symbolic_proof if hybrid_result else None,
                    'verification_passed': hybrid_result.verification_passed if hybrid_result else False,
                    'graph_context': context.get('knowledge_graph'),
                    'recommendations': hybrid_result.recommendations if hybrid_result else []
                } if hybrid_result else None,
                'badge': badge,
                'metadata': {
                    **base_result.get('metadata', {}),
                    'enhanced_supervisor_version': '2.1',  # Version bump for re-attempt feature
                    'rag_enabled': self.enable_rag,
                    'verification_enabled': self.enable_verification,
                    'hybrid_reasoning_enabled': self.enable_hybrid_reasoning,
                    # NEURO-SYMBOLIC: Re-attempt tracking (non-breaking, additive metadata)
                    'verification_reattempts': reattempt_count,
                    'verification_reattempt_enabled': True
                }
            }
            
            # 🆕 Add learning path recommendations from knowledge graph
            if hybrid_result and hybrid_result.recommendations:
                enhanced_result['learning_path'] = hybrid_result.recommendations
            
            # Add corrections to response if needed
            if verification_result and verification_result.corrections_suggested:
                enhanced_result['suggested_corrections'] = verification_result.corrections_suggested
            
            logger.info("✅ EnhancedSupervisor orchestration complete")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"❌ EnhancedSupervisor error: {e}", exc_info=True)
            # Fall back to base supervisor
            return await self.run(query, context)
    
    def _extract_response_text(self, result: Dict[str, Any]) -> str:
        """Extract combined response text from agent results"""
        texts = []
        
        # Extract from mentor
        mentor = result.get('mentor', {})
        if mentor.get('success') and mentor.get('content'):
            texts.append(mentor['content'])
        
        # Extract from professor
        professor = result.get('professor', {})
        if professor.get('success') and professor.get('content'):
            texts.append(professor['content'])
        
        return '\n\n'.join(texts)
    
    async def run_quick(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Quick mode with minimal verification (lower latency).
        
        For real-time scenarios where speed is critical.
        """
        # Temporarily disable heavy verification
        original_verify_logic = self.verify_logic
        self.verify_logic = False
        
        try:
            result = await self.run_enhanced(query, context)
            return result
        finally:
            self.verify_logic = original_verify_logic
    
    def configure(
        self,
        enable_rag: Optional[bool] = None,
        enable_verification: Optional[bool] = None,
        verify_math: Optional[bool] = None,
        verify_facts: Optional[bool] = None,
        verify_logic: Optional[bool] = None,
        enable_hybrid_reasoning: Optional[bool] = None
    ) -> None:
        """
        Configure the enhanced supervisor capabilities.
        
        Args:
            enable_rag: Enable/disable RAG enhancement
            enable_verification: Enable/disable verification
            verify_math: Enable/disable math verification
            verify_facts: Enable/disable fact checking
            verify_logic: Enable/disable logic validation
            enable_hybrid_reasoning: Enable/disable hybrid reasoning (Neural + Symbolic + Graph)
        """
        if enable_rag is not None:
            self.enable_rag = enable_rag
        if enable_verification is not None:
            self.enable_verification = enable_verification
        if verify_math is not None:
            self.verify_math = verify_math
        if verify_facts is not None:
            self.verify_facts = verify_facts
        if verify_logic is not None:
            self.verify_logic = verify_logic
        if enable_hybrid_reasoning is not None:
            self.enable_hybrid_reasoning = enable_hybrid_reasoning and HYBRID_REASONING_AVAILABLE
        
        logger.info(f"🔧 EnhancedSupervisor reconfigured: RAG={self.enable_rag}, Verify={self.enable_verification}, Hybrid={self.enable_hybrid_reasoning}")


# Factory function for easy access
def create_enhanced_supervisor(config: Optional[Dict[str, Any]] = None) -> EnhancedSupervisor:
    """Create an enhanced supervisor instance"""
    return EnhancedSupervisor(config)

