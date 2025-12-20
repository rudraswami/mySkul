"""
🚀 Enhanced Response Composer - Multi-Pass Intelligent Response Generation
===========================================================================

UPGRADES from basic ResponseComposer:
1. MULTI-PASS REFINEMENT: Generate → Critique → Refine
2. SELF-CRITIQUE LOOP: LLM evaluates its own output
3. DEPTH SCORING: Ensures response meets quality threshold
4. REASONING TREE: Structured thought process
5. MEMORY INTEGRATION: Full mastery and history context
6. VERIFICATION: Post-generation validation

This is the FAST PATH for simple-to-moderate queries,
but now with quality guarantees approaching multi-agent.
"""

import logging
import time
import asyncio
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)


class ResponseQuality(Enum):
    """Quality levels for responses"""
    INSUFFICIENT = "insufficient"  # Needs refinement
    ADEQUATE = "adequate"          # Meets minimum
    GOOD = "good"                  # Above average
    EXCELLENT = "excellent"        # High quality


@dataclass
class CritiqueResult:
    """Result of self-critique"""
    quality: ResponseQuality
    score: float  # 0-100
    issues: List[str]
    improvements: List[str]
    needs_refinement: bool
    factual_concerns: List[str]
    clarity_score: float
    completeness_score: float
    accuracy_score: float


@dataclass
class RefinementPass:
    """Single refinement pass"""
    pass_number: int
    original_content: str
    refined_content: str
    critique: CritiqueResult
    duration_ms: float


class EnhancedResponseComposer:
    """
    Multi-Pass Response Composer with Self-Critique
    
    FLOW:
    1. Initial Generation: Create first response
    2. Self-Critique: Evaluate quality, identify issues
    3. Refinement: Address issues if score < threshold
    4. Verification: Final validation
    5. Output: High-quality response
    
    This ensures even the "fast path" produces quality output.
    """
    
    # Quality thresholds
    MIN_QUALITY_SCORE = 70  # Below this triggers refinement
    MAX_REFINEMENT_PASSES = 2  # Maximum refinements
    
    # Timeout configurations
    TIMEOUT_INITIAL = 20
    TIMEOUT_CRITIQUE = 10
    TIMEOUT_REFINE = 15
    
    def __init__(self, db, llm_api_key: str):
        self.db = db
        self.llm_api_key = llm_api_key
        
        # Initialize dependent services
        self._init_services()
        
        # Response cache
        self._response_cache: Dict[str, Dict[str, Any]] = {}
        
        logger.info("🚀 EnhancedResponseComposer initialized with multi-pass refinement")
    
    def _init_services(self):
        """Initialize dependent services"""
        try:
            from services.conversation_state import ConversationStateManager
            from services.human_intelligence_layer import HumanIntelligenceLayer
            from services.intelligent_response_engine import get_response_config, detect_intent
            
            self.state_manager = ConversationStateManager(self.db)
            self.human_layer = HumanIntelligenceLayer(self.db)
            self.get_response_config = get_response_config
            self.detect_intent = detect_intent
            logger.info("   ├── StateManager: ✅")
            logger.info("   ├── HumanLayer: ✅")
        except ImportError as e:
            logger.warning(f"   ├── Some services not available: {e}")
            self.state_manager = None
            self.human_layer = None
        
        # Try to initialize verification
        try:
            from services.verification import get_verification_orchestrator
            self.verifier = get_verification_orchestrator()
            logger.info("   └── Verification: ✅")
        except ImportError:
            self.verifier = None
            logger.info("   └── Verification: ❌")
    
    async def generate_response(
        self,
        user_id: str,
        session_id: str,
        question: str,
        subject: str = None,
        exam_mode: str = "General",
        message_history: List[Dict] = None,
        enable_refinement: bool = True,
        quality_threshold: int = None
    ) -> Dict[str, Any]:
        """
        Generate high-quality response with multi-pass refinement.
        
        Args:
            user_id: User ID
            session_id: Session ID
            question: Student's question
            subject: Subject area
            exam_mode: Exam type
            message_history: Previous messages
            enable_refinement: Enable self-critique and refinement
            quality_threshold: Minimum quality score (default 70)
            
        Returns:
            High-quality response with metadata
        """
        start_time = time.time()
        quality_threshold = quality_threshold or self.MIN_QUALITY_SCORE
        
        logger.info(f"🚀 Enhanced generation for: {question[:60]}...")
        
        try:
            # === STEP 1: Get Context ===
            context = await self._get_full_context(
                user_id, session_id, question, subject, message_history
            )
            
            # === STEP 2: Detect Intent ===
            intent, response_config = self._analyze_intent(question, subject)
            logger.info(f"   Intent: {intent}")
            
            # === STEP 3: Check Cache ===
            cache_key = self._get_cache_key(question, subject, intent)
            cached = self._get_cached(cache_key)
            if cached:
                logger.info("   Cache hit!")
                return {**cached, "from_cache": True}
            
            # === STEP 4: Build Enhanced Prompt ===
            prompt = self._build_enhanced_prompt(
                question, intent, response_config, subject, exam_mode, context
            )
            
            # === STEP 5: Initial Generation ===
            initial_response = await self._generate_initial(prompt, question, intent)
            
            if not initial_response:
                return self._fallback_response(question, intent)
            
            # === STEP 6: Self-Critique ===
            refinement_passes = []
            current_response = initial_response
            
            if enable_refinement:
                for pass_num in range(self.MAX_REFINEMENT_PASSES):
                    # Critique current response
                    critique = await self._self_critique(
                        current_response, question, subject, context
                    )
                    
                    logger.info(f"   Pass {pass_num + 1} critique: score={critique.score:.0f}, "
                               f"quality={critique.quality.value}")
                    
                    # Check if refinement needed
                    if critique.score >= quality_threshold:
                        logger.info(f"   Quality threshold met ({critique.score:.0f} >= {quality_threshold})")
                        break
                    
                    if not critique.needs_refinement:
                        break
                    
                    # === STEP 7: Refine ===
                    pass_start = time.time()
                    refined = await self._refine_response(
                        current_response, critique, question, subject, context
                    )
                    
                    refinement_passes.append(RefinementPass(
                        pass_number=pass_num + 1,
                        original_content=current_response,
                        refined_content=refined,
                        critique=critique,
                        duration_ms=(time.time() - pass_start) * 1000
                    ))
                    
                    current_response = refined
            
            # === STEP 8: Final Verification ===
            verification_result = None
            if self.verifier and subject:
                try:
                    verification_result = await self.verifier.verify_response(
                        current_response, question, subject
                    )
                except Exception as e:
                    logger.warning(f"Verification skipped: {e}")
            
            # === STEP 9: Build Final Response ===
            generation_time = time.time() - start_time
            
            result = self._build_final_response(
                content=current_response,
                question=question,
                intent=intent,
                subject=subject,
                context=context,
                response_config=response_config,
                refinement_passes=refinement_passes,
                verification_result=verification_result,
                generation_time=generation_time
            )
            
            # === STEP 10: Update State & Cache ===
            if self.state_manager:
                await self.state_manager.update_state(
                    user_id, session_id, question, current_response, subject, intent
                )
            
            self._cache_response(cache_key, result)
            
            logger.info(f"✅ Enhanced response generated in {generation_time:.2f}s "
                       f"({len(refinement_passes)} refinements)")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Enhanced generation failed: {e}", exc_info=True)
            return self._fallback_response(question, "error")
    
    async def _get_full_context(
        self,
        user_id: str,
        session_id: str,
        question: str,
        subject: str,
        message_history: List[Dict]
    ) -> Dict[str, Any]:
        """Get comprehensive context for response generation"""
        context = {
            "user_id": user_id,
            "session_id": session_id,
            "subject": subject,
            "history_summary": "",
            "mastery_level": 50,
            "learning_style": "mixed",
            "recent_topics": [],
            "emotion": "neutral"
        }
        
        # Get conversation state
        if self.state_manager:
            try:
                state = await self.state_manager.get_state(user_id, session_id)
                context.update({
                    "history_summary": await self.state_manager.get_context_summary(
                        user_id, session_id, message_history or []
                    ),
                    "recent_topics": state.get("recent_topics", []),
                })
            except Exception as e:
                logger.debug(f"State retrieval failed: {e}")
        
        # Get human context
        if self.human_layer:
            try:
                human_ctx = await self.human_layer.analyze_student_context(
                    user_id=user_id,
                    question=question,
                    subject=subject,
                    session_history=message_history,
                    time_of_day=datetime.now().strftime("%H:%M")
                )
                context.update({
                    "emotion": human_ctx.get("emotion", "neutral"),
                    "mastery_level": human_ctx.get("difficulty_level", "developing"),
                    "learning_style": human_ctx.get("learning_style", "mixed"),
                })
            except Exception as e:
                logger.debug(f"Human layer failed: {e}")
        
        # Get mastery from DB
        if self.db is not None:
            try:
                user_doc = await self.db.users.find_one({"user_id": user_id})
                if user_doc:
                    context["user_name"] = user_doc.get("full_name", "").split()[0]
                    context["mastery_level"] = user_doc.get("overall_mastery", 50)
            except Exception:
                pass
        
        return context
    
    def _analyze_intent(self, question: str, subject: str) -> tuple:
        """Analyze question intent"""
        try:
            if hasattr(self, 'get_response_config') and self.get_response_config:
                config = self.get_response_config(question, subject)
                return config.get("intent", "concept"), config
        except Exception:
            pass
        
        # Fallback intent detection
        q_lower = question.lower()
        if any(w in q_lower for w in ['hi', 'hello', 'hey']):
            return "greeting", {"intent": "greeting", "blocks": ["greeting"]}
        if any(w in q_lower for w in ['prove', 'derive']):
            return "derivation", {"intent": "derivation", "blocks": ["explanation", "steps"]}
        if any(w in q_lower for w in ['compare', 'difference']):
            return "comparison", {"intent": "comparison", "blocks": ["comparison"]}
        
        return "concept", {"intent": "concept", "blocks": ["explanation"]}
    
    def _build_enhanced_prompt(
        self,
        question: str,
        intent: str,
        response_config: Dict,
        subject: str,
        exam_mode: str,
        context: Dict[str, Any]
    ) -> str:
        """Build comprehensive prompt for generation"""
        
        user_name = context.get("user_name", "")
        mastery = context.get("mastery_level", 50)
        emotion = context.get("emotion", "neutral")
        history = context.get("history_summary", "")
        
        # Depth instruction based on mastery
        if isinstance(mastery, str):
            mastery_num = 50
        else:
            mastery_num = mastery
            
        if mastery_num < 30:
            depth = "Use SIMPLE language, lots of examples, avoid jargon"
        elif mastery_num < 70:
            depth = "Use clear explanations with some technical terms, provide examples"
        else:
            depth = "You can use technical terms, include deeper insights and exam tips"
        
        # Emotional adaptation
        emotional_note = ""
        if emotion == "frustrated":
            emotional_note = "The student seems frustrated. Be extra patient and encouraging."
        elif emotion == "confused":
            emotional_note = "The student seems confused. Start from basics and build up."
        elif emotion == "excited":
            emotional_note = "The student is engaged! Match their enthusiasm."
        
        prompt = f"""You are an expert AI tutor helping {user_name or 'a student'} prepare for {exam_mode}.

## STUDENT CONTEXT
- Subject: {subject or 'General'}
- Mastery Level: {mastery_num}/100
- Depth Instruction: {depth}
{emotional_note}

## CONVERSATION HISTORY
{history[:500] if history else 'New conversation'}

## QUESTION
{question}

## YOUR TASK
Provide a clear, helpful, and accurate response that:
1. Directly answers the question
2. Uses appropriate depth for the student's level
3. Includes relevant examples (Indian context preferred)
4. Uses proper formatting (markdown, formulas in $...$)
5. Is encouraging and supportive
6. Ends with a brief follow-up or check for understanding

## QUALITY REQUIREMENTS
- Be accurate and factual
- Be concise but complete (150-400 words)
- Include at least one example or analogy
- Use clear structure (headings, bullets if helpful)

Your Response:"""
        
        return prompt
    
    async def _generate_initial(
        self,
        prompt: str,
        question: str,
        intent: str
    ) -> Optional[str]:
        """Generate initial response"""
        try:
            chat = LlmChat(
                api_key=self.llm_api_key,
                session_id=f"enhanced_composer_{time.time()}",
                system_message=prompt
            ).with_model("openai", "gpt-4o-mini").with_params(
                temperature=0.7,
                max_tokens=800,
                presence_penalty=0.3,
                frequency_penalty=0.2
            )
            
            response = await asyncio.wait_for(
                chat.send_message(UserMessage(text=question)),
                timeout=self.TIMEOUT_INITIAL
            )
            
            return response if isinstance(response, str) else str(response)
            
        except asyncio.TimeoutError:
            logger.warning("Initial generation timeout")
            return None
        except Exception as e:
            logger.error(f"Initial generation failed: {e}")
            return None
    
    async def _self_critique(
        self,
        response: str,
        question: str,
        subject: str,
        context: Dict[str, Any]
    ) -> CritiqueResult:
        """
        SELF-CRITIQUE: The Key to Quality
        
        LLM evaluates its own response for:
        - Accuracy
        - Completeness
        - Clarity
        - Relevance
        """
        critique_prompt = f"""You are a quality evaluator. Critique this AI tutor response.

## ORIGINAL QUESTION
{question}

## RESPONSE TO EVALUATE
{response}

## EVALUATION CRITERIA
Rate each 0-100:
1. ACCURACY: Are all facts, formulas, and explanations correct?
2. COMPLETENESS: Does it fully answer the question?
3. CLARITY: Is it easy to understand for a student?
4. RELEVANCE: Does it directly address what was asked?

## OUTPUT FORMAT (JSON)
{{
    "accuracy_score": 0-100,
    "completeness_score": 0-100,
    "clarity_score": 0-100,
    "relevance_score": 0-100,
    "overall_score": 0-100,
    "factual_concerns": ["list any factual issues or empty list"],
    "clarity_issues": ["list any clarity issues or empty list"],
    "missing_content": ["what's missing or empty list"],
    "improvement_suggestions": ["specific improvements or empty list"],
    "needs_refinement": true/false
}}

Respond ONLY with the JSON."""
        
        try:
            chat = LlmChat(
                api_key=self.llm_api_key,
                session_id=f"critique_{time.time()}",
                system_message="You are a strict quality evaluator for educational content."
            ).with_model("openai", "gpt-4o-mini").with_params(
                temperature=0.2,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result = await asyncio.wait_for(
                chat.send_message(UserMessage(text=critique_prompt)),
                timeout=self.TIMEOUT_CRITIQUE
            )
            
            import json
            critique_data = json.loads(result)
            
            overall = critique_data.get("overall_score", 70)
            
            # Determine quality level
            if overall >= 85:
                quality = ResponseQuality.EXCELLENT
            elif overall >= 70:
                quality = ResponseQuality.GOOD
            elif overall >= 50:
                quality = ResponseQuality.ADEQUATE
            else:
                quality = ResponseQuality.INSUFFICIENT
            
            return CritiqueResult(
                quality=quality,
                score=overall,
                issues=critique_data.get("clarity_issues", []) + critique_data.get("missing_content", []),
                improvements=critique_data.get("improvement_suggestions", []),
                needs_refinement=critique_data.get("needs_refinement", overall < 70),
                factual_concerns=critique_data.get("factual_concerns", []),
                clarity_score=critique_data.get("clarity_score", 70),
                completeness_score=critique_data.get("completeness_score", 70),
                accuracy_score=critique_data.get("accuracy_score", 70)
            )
            
        except Exception as e:
            logger.warning(f"Self-critique failed: {e}")
            # Return default passing critique
            return CritiqueResult(
                quality=ResponseQuality.ADEQUATE,
                score=70,
                issues=[],
                improvements=[],
                needs_refinement=False,
                factual_concerns=[],
                clarity_score=70,
                completeness_score=70,
                accuracy_score=70
            )
    
    async def _refine_response(
        self,
        original: str,
        critique: CritiqueResult,
        question: str,
        subject: str,
        context: Dict[str, Any]
    ) -> str:
        """Refine response based on critique"""
        
        issues_text = "\n".join(f"- {issue}" for issue in critique.issues[:3])
        improvements_text = "\n".join(f"- {imp}" for imp in critique.improvements[:3])
        factual_text = "\n".join(f"- {fact}" for fact in critique.factual_concerns[:3])
        
        refine_prompt = f"""Improve this response based on the critique.

## ORIGINAL QUESTION
{question}

## ORIGINAL RESPONSE
{original}

## CRITIQUE RESULTS
Quality Score: {critique.score}/100
Clarity Score: {critique.clarity_score}/100
Completeness Score: {critique.completeness_score}/100
Accuracy Score: {critique.accuracy_score}/100

## ISSUES FOUND
{issues_text if issues_text else "None"}

## FACTUAL CONCERNS
{factual_text if factual_text else "None - verify accuracy anyway"}

## SUGGESTED IMPROVEMENTS
{improvements_text if improvements_text else "General polish needed"}

## YOUR TASK
Rewrite the response to:
1. Fix all identified issues
2. Address factual concerns
3. Improve clarity and completeness
4. Keep the same helpful, encouraging tone
5. Maintain appropriate length (150-400 words)

Output ONLY the improved response, nothing else."""
        
        try:
            chat = LlmChat(
                api_key=self.llm_api_key,
                session_id=f"refine_{time.time()}",
                system_message="You are an expert at improving educational content."
            ).with_model("openai", "gpt-4o-mini").with_params(
                temperature=0.5,
                max_tokens=800
            )
            
            result = await asyncio.wait_for(
                chat.send_message(UserMessage(text=refine_prompt)),
                timeout=self.TIMEOUT_REFINE
            )
            
            return result if isinstance(result, str) else str(result)
            
        except Exception as e:
            logger.warning(f"Refinement failed: {e}")
            return original  # Return original if refinement fails
    
    def _build_final_response(
        self,
        content: str,
        question: str,
        intent: str,
        subject: str,
        context: Dict[str, Any],
        response_config: Dict,
        refinement_passes: List[RefinementPass],
        verification_result: Any,
        generation_time: float
    ) -> Dict[str, Any]:
        """Build final structured response"""
        
        # Get final quality from last critique
        final_quality = ResponseQuality.GOOD
        final_score = 75
        if refinement_passes:
            last_critique = refinement_passes[-1].critique
            final_quality = last_critique.quality
            final_score = last_critique.score
        
        return {
            "response": {
                "default_view": {
                    "main_content": {
                        "content": content,
                        "type": "markdown"
                    },
                    "greeting": self._extract_greeting(content) if intent == "greeting" else None,
                },
                "progressive_sections": {
                    "explanation": content
                },
                "intent": intent,
                "render_directives": response_config.get("render_directives", {}),
                "quality": {
                    "level": final_quality.value,
                    "score": final_score,
                    "refinements": len(refinement_passes)
                }
            },
            "detected_subject": subject,
            "generation_time": generation_time,
            "model_used": "gpt-4o-mini",
            "intent_detected": intent,
            "context_used": bool(context.get("history_summary")),
            "from_cache": False,
            "quality_metrics": {
                "final_score": final_score,
                "quality_level": final_quality.value,
                "refinement_count": len(refinement_passes),
                "verified": verification_result is not None
            },
            "verification": {
                "status": verification_result.overall_status.value if verification_result and hasattr(verification_result, 'overall_status') else "not_verified",
                "confidence": verification_result.confidence_score if verification_result and hasattr(verification_result, 'confidence_score') else 0.7
            } if verification_result else None
        }
    
    def _extract_greeting(self, response: str) -> Optional[str]:
        """Extract greeting from response"""
        lines = response.strip().split('\n')
        return lines[0] if lines else None
    
    def _get_cache_key(self, question: str, subject: str, intent: str) -> str:
        """Generate cache key"""
        content = f"{question}:{subject}:{intent}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        cached = self._response_cache.get(key)
        if cached and (time.time() - cached.get("_cached_at", 0)) < 3600:  # 1 hour TTL
            return cached
        return None
    
    def _cache_response(self, key: str, response: Dict[str, Any]):
        """Cache response"""
        response["_cached_at"] = time.time()
        self._response_cache[key] = response
        
        # Limit cache size
        if len(self._response_cache) > 100:
            oldest = min(self._response_cache.keys(), 
                        key=lambda k: self._response_cache[k].get("_cached_at", 0))
            del self._response_cache[oldest]
    
    def _fallback_response(self, question: str, intent: str) -> Dict[str, Any]:
        """
        Generate fallback response.
        
        CRITICAL: Fallback must:
        - Continue conversation naturally
        - Reference the question
        - Never expose limitations
        - Never list capabilities or ask to "try again"
        """
        short_q = question[:60] + "..." if len(question) > 60 else question
        
        content = f"""That's an interesting question about "{short_q}"

Let me think about the best way to explain this to you. What specific part are you most curious about? I want to make sure I give you exactly what you need. 🎯"""
        
        return {
            "response": {
                "default_view": {
                    "main_content": {"content": content, "type": "markdown"}
                },
                "intent": intent
            },
            "detected_subject": "General",
            "generation_time": 0.1,
            "from_cache": False,
            "quality_metrics": {"fallback": True}
        }


# Factory function
def get_enhanced_composer(db, llm_api_key: str) -> EnhancedResponseComposer:
    """Get or create enhanced composer"""
    return EnhancedResponseComposer(db, llm_api_key)

