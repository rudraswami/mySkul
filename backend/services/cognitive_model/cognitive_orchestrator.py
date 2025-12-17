"""
🧠 Cognitive Orchestrator - The Brain of AI Tutor v2.0
======================================================

This orchestrator integrates cognitive engines into a unified flow:

1. StudentStateEngine → Determines depth/style based on mastery
2. ConsistencyEngine → Checks for contradictions with previous explanations
3. [AI Response Generation] → The actual explanation

NOTE: TeachMeBack has its own dedicated flow:
- Frontend: TeachMeBackModal.jsx (opens on link click)
- API: /api/ai/teach-me-back
- Backend: services/teach_me_back_evaluator.py
- This is intentional to keep the user experience clean.

THIS IS THE CORE INTEGRATION LAYER for pre/post response processing.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .student_state_engine import (
    StudentStateEngine,
    get_student_state_engine,
    StudentState,
    DepthRecommendation
)
from .consistency_engine import (
    ConsistencyEngine,
    get_consistency_engine,
    ConsistencyCheckResult,
    ConsistencyStatus
)

logger = logging.getLogger(__name__)


@dataclass
class CognitiveContext:
    """Complete cognitive context for a response"""
    student_state: StudentState
    depth_recommendation: DepthRecommendation
    depth_prompt: str                        # Prompt additions for depth
    consistency_check: Optional[ConsistencyCheckResult]
    acknowledgment: Optional[str]            # If we need to acknowledge inconsistency
    concept_name: str
    topic_key: str


@dataclass
class CognitiveResponse:
    """Response enhanced with cognitive features"""
    original_response: str                   # The AI's response
    enhanced_response: str                   # Response + acknowledgment
    cognitive_context: CognitiveContext


class CognitiveOrchestrator:
    """
    Orchestrates cognitive engines for a unified learning experience.
    
    Handles:
    - Student state tracking (mastery, depth adaptation)
    - Consistency checking (cross-session contradiction detection)
    
    Does NOT handle:
    - TeachMeBack (separate flow via TeachMeBackModal → /api/ai/teach-me-back)
    """
    
    def __init__(self, db, llm_api_key: str = None):
        self.db = db
        self.llm_api_key = llm_api_key
        
        # Initialize engines
        self.student_state_engine = get_student_state_engine(db)
        self.consistency_engine = get_consistency_engine(db)
        
        logger.info("🧠 CognitiveOrchestrator initialized - StudentState + Consistency active")
    
    async def prepare_response_context(
        self,
        user_id: str,
        session_id: str,
        question: str,
        concept_name: str,
        subject: str = "General"
    ) -> CognitiveContext:
        """
        Prepare cognitive context BEFORE generating AI response.
        
        This is called BEFORE the LLM generates the explanation.
        Returns context that should influence the response depth/style.
        """
        logger.info(f"🧠 Preparing cognitive context for '{concept_name}'")
        
        # Step 1: Get student state
        student_state = await self.student_state_engine.get_student_state(
            user_id, concept_name, subject
        )
        
        # Step 2: Get depth recommendation
        depth_recommendation = self.student_state_engine.recommend_depth(
            student_state,
            question_intent=self._detect_intent(question)
        )
        
        # Step 3: Build depth prompt for LLM
        depth_prompt = self.student_state_engine.build_depth_prompt(depth_recommendation)
        
        topic_key = self._normalize_topic(concept_name)
        
        context = CognitiveContext(
            student_state=student_state,
            depth_recommendation=depth_recommendation,
            depth_prompt=depth_prompt,
            consistency_check=None,  # Will be filled after response
            acknowledgment=None,
            concept_name=concept_name,
            topic_key=topic_key
        )
        
        logger.info(f"📊 Context: level={student_state.student_level.value}, "
                   f"depth={depth_recommendation.depth}")
        
        return context
    
    async def enhance_response(
        self,
        user_id: str,
        session_id: str,
        original_response: str,
        cognitive_context: CognitiveContext,
        subject: str = "General"
    ) -> CognitiveResponse:
        """
        Enhance AI response with cognitive features.
        
        This is called AFTER the LLM generates the explanation.
        Adds consistency acknowledgment if needed.
        """
        concept_name = cognitive_context.concept_name
        
        # Step 1: Check consistency with previous explanations
        consistency_check = await self.consistency_engine.check_consistency(
            user_id, concept_name, original_response, subject
        )
        
        # Update context with consistency check
        cognitive_context.consistency_check = consistency_check
        
        # Step 2: Build enhanced response
        enhanced_parts = []
        
        # Add acknowledgment if there's a potential conflict
        if consistency_check.should_acknowledge and consistency_check.acknowledgment_text:
            enhanced_parts.append(consistency_check.acknowledgment_text)
            cognitive_context.acknowledgment = consistency_check.acknowledgment_text
        
        # Add original response
        enhanced_parts.append(original_response)
        
        enhanced_response = "\n\n".join(enhanced_parts)
        
        # Step 3: Record explanation for future consistency checking
        await self.consistency_engine.record_explanation(
            user_id, session_id, concept_name, original_response, subject
        )
        
        # Step 4: Update student state (interaction recorded)
        await self.student_state_engine.update_student_state(
            user_id, concept_name, "question"
        )
        
        return CognitiveResponse(
            original_response=original_response,
            enhanced_response=enhanced_response,
            cognitive_context=cognitive_context
        )
    
    async def get_student_learning_summary(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Get a summary of student's learning state."""
        # Get explanation history from consistency engine
        explanation_history = await self.consistency_engine.get_explanation_history(
            user_id, limit=10
        )
        
        # Get teach-back history from database (if exists)
        teach_back_history = []
        try:
            cursor = self.db.teach_me_back_attempts.find(
                {"user_id": user_id},
                sort=[("timestamp", -1)],
                limit=10
            )
            async for doc in cursor:
                teach_back_history.append({
                    "concept": doc.get("concept"),
                    "score": doc.get("score", 50),
                    "level": doc.get("understanding_level", "partial"),
                    "timestamp": doc.get("timestamp")
                })
        except Exception as e:
            logger.warning(f"Could not fetch teach-back history: {e}")
        
        # Calculate average understanding from teach-back attempts
        scores = [h.get("score", 50) for h in teach_back_history if h.get("score")]
        avg_understanding = sum(scores) / len(scores) if scores else 50.0
        
        return {
            "average_understanding": avg_understanding,
            "recent_teach_backs": teach_back_history,
            "concepts_covered": len(explanation_history),
            "recent_explanations": explanation_history
        }
    
    async def _has_explanation_history(
        self,
        user_id: str,
        concept_name: str,
        subject: str
    ) -> bool:
        """Check if we've explained this concept before."""
        history = await self.consistency_engine.get_explanation_history(
            user_id, concept_name, limit=1
        )
        return len(history) > 0
    
    def _detect_intent(self, question: str) -> str:
        """Simple intent detection for depth recommendation."""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['exam', 'test', 'jee', 'neet', 'marks']):
            return "exam"
        elif any(word in question_lower for word in ['why', 'how does', 'intuition', 'understand']):
            return "intuition"
        elif any(word in question_lower for word in ['derive', 'prove', 'proof']):
            return "derivation"
        elif any(word in question_lower for word in ['solve', 'calculate', 'find']):
            return "problem"
        else:
            return "concept"
    
    def _normalize_topic(self, topic: str) -> str:
        """Normalize topic name."""
        return re.sub(r'[^a-z0-9]+', '_', topic.lower())


# Singleton
_cognitive_orchestrator: Optional[CognitiveOrchestrator] = None


def get_cognitive_orchestrator(db, llm_api_key: str = None) -> CognitiveOrchestrator:
    """Get or create the cognitive orchestrator."""
    global _cognitive_orchestrator
    if _cognitive_orchestrator is None:
        _cognitive_orchestrator = CognitiveOrchestrator(db, llm_api_key)
    return _cognitive_orchestrator
