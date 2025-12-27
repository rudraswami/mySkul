"""
🎯 Response Confidence — Explicit Uncertainty Awareness
=======================================================

GAP 4 IMPLEMENTATION: Real-Time Confidence Calibration

This module provides:
1. ResponseConfidence dataclass - explicit confidence metadata for every response
2. ConfidenceAwareResponseHandler - adaptive behavior based on confidence
3. ConfidenceCalibrator - learns accuracy over time to calibrate confidence

ARCHITECTURAL PRINCIPLES:
- Every response MUST carry explicit confidence metadata
- Low confidence MUST change behavior (clarification, hedging, escalation)
- Confidence is NEVER inferred from response length or verbosity
- System must be honest about uncertainty

STRICT RULE:
If confidence is low and the system responds with high certainty, that is a BUG.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """Confidence levels for response quality."""
    HIGH = "high"           # > 0.8 - Very confident, proceed normally
    MEDIUM = "medium"       # 0.6-0.8 - Moderately confident, minor hedging
    LOW = "low"             # 0.4-0.6 - Uncertain, add qualifiers
    VERY_LOW = "very_low"   # < 0.4 - Should clarify or escalate


@dataclass
class ResponseConfidence:
    """
    Explicit confidence metadata for every response.
    
    This is NOT inferred. It is computed by the LLM during response generation
    through explicit self-assessment prompting.
    """
    # Core confidence scores (0.0 - 1.0)
    overall_confidence: float = 0.7       # Composite confidence
    factual_confidence: float = 0.7       # Confidence in stated facts
    reasoning_confidence: float = 0.7     # Confidence in logical steps
    completeness_confidence: float = 0.7  # Confidence response is complete
    
    # Uncertainty signals
    ambiguity_flags: List[str] = field(default_factory=list)      # What was ambiguous?
    uncertainty_sources: List[str] = field(default_factory=list)  # Why uncertain?
    
    # Calibration factor (from historical accuracy)
    calibration_factor: float = 1.0  # Multiplier based on past accuracy
    
    @property
    def calibrated_confidence(self) -> float:
        """Confidence adjusted by historical calibration."""
        return min(1.0, self.overall_confidence * self.calibration_factor)
    
    @property
    def level(self) -> ConfidenceLevel:
        """Categorized confidence level."""
        conf = self.calibrated_confidence
        if conf >= 0.8:
            return ConfidenceLevel.HIGH
        elif conf >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif conf >= 0.4:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    @property
    def is_low_confidence(self) -> bool:
        """True if confidence is below acceptable threshold."""
        return self.calibrated_confidence < 0.6
    
    @property
    def needs_clarification(self) -> bool:
        """True if we should ask for clarification instead of guessing."""
        return len(self.ambiguity_flags) > 0 and self.calibrated_confidence < 0.5
    
    @property
    def needs_hedging(self) -> bool:
        """True if we should add uncertainty language."""
        return self.calibrated_confidence < 0.7
    
    @property
    def needs_escalation(self) -> bool:
        """True if we should escalate to more capable model."""
        return self.factual_confidence < 0.4 and self.reasoning_confidence < 0.4
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for response metadata."""
        return {
            "overall_confidence": self.overall_confidence,
            "factual_confidence": self.factual_confidence,
            "reasoning_confidence": self.reasoning_confidence,
            "completeness_confidence": self.completeness_confidence,
            "calibrated_confidence": self.calibrated_confidence,
            "confidence_level": self.level.value,
            "ambiguity_flags": self.ambiguity_flags,
            "uncertainty_sources": self.uncertainty_sources,
            "needs_clarification": self.needs_clarification,
            "needs_hedging": self.needs_hedging
        }
    
    @classmethod
    def from_llm_assessment(cls, assessment: Dict[str, Any], calibration_factor: float = 1.0) -> 'ResponseConfidence':
        """
        Create from LLM's self-assessment response.
        
        The LLM is prompted to provide confidence scores explicitly.
        """
        return cls(
            overall_confidence=assessment.get('overall_confidence', 0.7),
            factual_confidence=assessment.get('factual_confidence', 0.7),
            reasoning_confidence=assessment.get('reasoning_confidence', 0.7),
            completeness_confidence=assessment.get('completeness_confidence', 0.7),
            ambiguity_flags=assessment.get('ambiguity_flags', []),
            uncertainty_sources=assessment.get('uncertainty_sources', []),
            calibration_factor=calibration_factor
        )
    
    @classmethod
    def high_confidence(cls) -> 'ResponseConfidence':
        """Factory for high-confidence responses (greetings, acknowledgments)."""
        return cls(
            overall_confidence=0.95,
            factual_confidence=0.95,
            reasoning_confidence=0.95,
            completeness_confidence=0.95
        )
    
    @classmethod
    def default(cls) -> 'ResponseConfidence':
        """Factory for default confidence when not computed."""
        return cls()


# ============================================================================
# CONFIDENCE SELF-ASSESSMENT PROMPT
# ============================================================================

CONFIDENCE_ASSESSMENT_PROMPT = """
After generating your response, you MUST assess your confidence honestly.

Provide a JSON block at the end of your response with this exact structure:

```json
{
  "confidence_assessment": {
    "overall_confidence": 0.0-1.0,
    "factual_confidence": 0.0-1.0,
    "reasoning_confidence": 0.0-1.0,
    "completeness_confidence": 0.0-1.0,
    "ambiguity_flags": ["list of unclear aspects in the question"],
    "uncertainty_sources": ["list of what made you uncertain"]
  }
}
```

SCORING GUIDE:
- 0.9-1.0: Absolutely certain, textbook knowledge, no doubt
- 0.7-0.9: Very confident, well-understood topic
- 0.5-0.7: Moderately confident, some uncertainty
- 0.3-0.5: Uncertain, this might not be fully accurate
- 0.0-0.3: Very uncertain, likely guessing

HONESTY RULES:
- If the question is ambiguous, say so in ambiguity_flags
- If you're not sure about facts, lower factual_confidence
- If your reasoning might have gaps, lower reasoning_confidence
- If you didn't fully address the question, lower completeness_confidence
- NEVER claim high confidence when you're guessing

Example for uncertain response:
```json
{
  "confidence_assessment": {
    "overall_confidence": 0.5,
    "factual_confidence": 0.4,
    "reasoning_confidence": 0.6,
    "completeness_confidence": 0.5,
    "ambiguity_flags": ["unclear which formula version they mean"],
    "uncertainty_sources": ["topic at edge of training data", "multiple valid interpretations"]
  }
}
```
"""


# ============================================================================
# CONFIDENCE-AWARE RESPONSE HANDLER
# ============================================================================

class ConfidenceAwareResponseHandler:
    """
    Handles responses based on confidence level.
    
    LOW CONFIDENCE MUST CHANGE BEHAVIOR:
    - Clarification questions when ambiguous
    - Hedging language when uncertain
    - Escalation when very uncertain
    
    This is NOT optional. Silent guessing is forbidden.
    """
    
    def __init__(self, db=None):
        self.db = db
        logger.info("🎯 ConfidenceAwareResponseHandler initialized")
    
    async def process_response(
        self,
        content: str,
        confidence: ResponseConfidence,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process response based on confidence level.
        
        Returns modified response with appropriate handling.
        
        NEW: Applies historical calibration factor to adjust stated confidence.
        """
        from core.config import settings
        
        # Check if confidence handling is enabled
        if not getattr(settings, 'ENABLE_CONFIDENCE_CALIBRATION', True):
            return {
                'content': content,
                'confidence': confidence.to_dict(),
                'confidence_handled': False
            }
        
        # === PERSISTENT LEARNING INTEGRATION ===
        # Apply calibration factor from historical accuracy data
        # This makes confidence adaptive across sessions
        enable_persistent_calibration = getattr(settings, 'ENABLE_PERSISTENT_CALIBRATION', True)
        if enable_persistent_calibration:
            try:
                user_id = context.get('user_id')
                calibration_factor = await self.get_calibration_factor(user_id)
                
                if calibration_factor != 1.0:
                    # Adjust calibrated confidence based on historical accuracy
                    original_confidence = confidence.calibrated_confidence
                    adjusted_confidence = min(1.0, max(0.0, original_confidence * calibration_factor))
                    confidence.calibrated_confidence = adjusted_confidence
                    
                    # Update level if needed
                    if adjusted_confidence >= 0.85:
                        confidence.level = ConfidenceLevel.HIGH
                    elif adjusted_confidence >= 0.5:
                        confidence.level = ConfidenceLevel.MEDIUM
                    else:
                        confidence.level = ConfidenceLevel.LOW
                    
                    logger.info(f"📊 Persistent calibration applied: {original_confidence:.2f} → {adjusted_confidence:.2f} (factor={calibration_factor:.2f})")
            except Exception as e:
                # Non-blocking - continue with original confidence
                logger.debug(f"Calibration factor not applied: {e}")
        
        # === CLARIFICATION PATH ===
        if confidence.needs_clarification:
            logger.info(f"🤔 Low confidence + ambiguity → Requesting clarification")
            clarification = await self._generate_clarification_request(
                query=query,
                ambiguity_flags=confidence.ambiguity_flags,
                context=context
            )
            return {
                'content': clarification,
                'confidence': confidence.to_dict(),
                'confidence_handled': True,
                'action_taken': 'clarification_requested'
            }
        
        # === ESCALATION PATH ===
        if confidence.needs_escalation and context.get('allow_escalation', True):
            logger.info(f"⬆️ Very low confidence → Escalation recommended")
            # Don't escalate here, just flag it - the orchestrator decides
            return {
                'content': content,
                'confidence': confidence.to_dict(),
                'confidence_handled': True,
                'action_taken': 'escalation_recommended',
                'should_escalate': True
            }
        
        # === HEDGING PATH ===
        if confidence.needs_hedging:
            logger.info(f"📝 Moderate uncertainty → Adding hedging language")
            hedged_content = self._add_hedging(content, confidence)
            return {
                'content': hedged_content,
                'confidence': confidence.to_dict(),
                'confidence_handled': True,
                'action_taken': 'hedging_added'
            }
        
        # === HIGH CONFIDENCE PATH ===
        return {
            'content': content,
            'confidence': confidence.to_dict(),
            'confidence_handled': True,
            'action_taken': 'none_needed'
        }
    
    async def _generate_clarification_request(
        self,
        query: str,
        ambiguity_flags: List[str],
        context: Dict[str, Any]
    ) -> str:
        """
        Generate a clarification request instead of guessing.
        
        This is NOT a cop-out. It's intellectual honesty.
        """
        student_name = context.get('student_name', '')
        name_part = f" {student_name}" if student_name else ""
        
        # Build clarification based on specific ambiguities
        if ambiguity_flags:
            ambiguity_list = "\n".join(f"- {flag}" for flag in ambiguity_flags[:3])
            return f"""I want to make sure I help you correctly{name_part}! 🤔

Your question could mean a few different things:
{ambiguity_list}

Could you clarify which one you're asking about? That way I can give you the most accurate and helpful answer! 💡"""
        
        # Generic clarification
        return f"""I want to help you properly{name_part}, but I'm not 100% sure what you're asking about.

Could you give me a bit more context or rephrase your question? That'll help me give you a much better answer! 🎯"""
    
    def _add_hedging(self, content: str, confidence: ResponseConfidence) -> str:
        """
        Add appropriate hedging language based on confidence type.
        
        This makes uncertainty explicit without being annoying.
        """
        # Different hedging based on what's uncertain
        hedging_prefix = ""
        
        if confidence.factual_confidence < 0.5:
            hedging_prefix = "Based on my understanding (though I'd recommend verifying): "
        elif confidence.reasoning_confidence < 0.5:
            hedging_prefix = "Here's my reasoning, though there might be other valid approaches: "
        elif confidence.completeness_confidence < 0.5:
            hedging_prefix = "Here's what I can address, though there may be more to consider: "
        else:
            hedging_prefix = "From what I understand: "
        
        # Add offer to clarify at the end if not already present
        if confidence.calibrated_confidence < 0.6:
            if "let me know" not in content.lower() and "would you like" not in content.lower():
                content = content.rstrip() + "\n\nLet me know if you'd like me to explain this differently or go deeper on any part! 💡"
        
        return hedging_prefix + content


# ============================================================================
# CONFIDENCE CALIBRATOR (LEARNS FROM OUTCOMES)
# ============================================================================

class ConfidenceCalibrator:
    """
    Calibrates confidence based on actual accuracy over time.
    
    If we're consistently overconfident (high stated, low accuracy):
    → calibration_factor < 1.0 (reduce stated confidence)
    
    If we're consistently underconfident (low stated, high accuracy):
    → calibration_factor > 1.0 (increase stated confidence)
    
    This is NOT model retraining. It's statistical calibration.
    """
    
    def __init__(self, db=None):
        self.db = db
        self._cache: Dict[str, float] = {}  # user_id → calibration_factor
        logger.info("📊 ConfidenceCalibrator initialized")
    
    async def record_outcome(
        self,
        response_id: str,
        stated_confidence: float,
        was_correct: bool,
        user_id: Optional[str] = None
    ) -> None:
        """
        Record the outcome of a response for calibration learning.
        
        This should be called when:
        - User gives feedback (helpful/not helpful)
        - User corrects the AI
        - User asks for clarification (implicit low accuracy)
        """
        if not self.db:
            return
        
        try:
            await self.db.confidence_outcomes.insert_one({
                'response_id': response_id,
                'stated_confidence': stated_confidence,
                'was_correct': was_correct,
                'user_id': user_id,
                'timestamp': datetime.now(timezone.utc)
            })
            
            # Invalidate cache for this user
            if user_id and user_id in self._cache:
                del self._cache[user_id]
                
            logger.debug(f"📊 Recorded outcome: conf={stated_confidence:.2f}, correct={was_correct}")
            
        except Exception as e:
            logger.warning(f"Failed to record confidence outcome: {e}")
    
    async def get_calibration_factor(self, user_id: Optional[str] = None) -> float:
        """
        Get the calibration factor based on historical accuracy.
        
        Returns a factor to multiply stated confidence by.
        
        Range: 0.7 - 1.3 (bounded to prevent extreme adjustments)
        """
        # Check cache first
        cache_key = user_id or 'global'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        if not self.db:
            return 1.0
        
        try:
            # Get recent outcomes (last 7 days)
            cutoff = datetime.now(timezone.utc) - timedelta(days=7)
            query = {'timestamp': {'$gte': cutoff}}
            if user_id:
                query['user_id'] = user_id
            
            outcomes = await self.db.confidence_outcomes.find(query).to_list(500)
            
            if len(outcomes) < 20:
                # Not enough data for reliable calibration
                return 1.0
            
            # Calculate calibration
            # Group by confidence buckets
            high_conf = [o for o in outcomes if o['stated_confidence'] >= 0.7]
            low_conf = [o for o in outcomes if o['stated_confidence'] < 0.5]
            
            factor = 1.0
            
            # Check if we're overconfident
            if high_conf:
                high_conf_accuracy = sum(1 for o in high_conf if o['was_correct']) / len(high_conf)
                if high_conf_accuracy < 0.7:
                    # We're overconfident - stated high but often wrong
                    factor = 0.85
                    logger.info(f"📊 Calibration: Overconfident (high_conf_accuracy={high_conf_accuracy:.2f})")
            
            # Check if we're underconfident
            if low_conf:
                low_conf_accuracy = sum(1 for o in low_conf if o['was_correct']) / len(low_conf)
                if low_conf_accuracy > 0.8:
                    # We're underconfident - stated low but usually right
                    factor = 1.15
                    logger.info(f"📊 Calibration: Underconfident (low_conf_accuracy={low_conf_accuracy:.2f})")
            
            # Bound the factor
            factor = max(0.7, min(1.3, factor))
            
            # Cache it
            self._cache[cache_key] = factor
            
            return factor
            
        except Exception as e:
            logger.warning(f"Failed to compute calibration factor: {e}")
            return 1.0


# ============================================================================
# CONFIDENCE EXTRACTOR (PARSES LLM SELF-ASSESSMENT)
# ============================================================================

def extract_confidence_from_response(response_text: str) -> Optional[ResponseConfidence]:
    """
    Extract confidence assessment from LLM response.
    
    The LLM is prompted to include a JSON block with confidence scores.
    This function parses that block.
    """
    import re
    import json
    
    try:
        # Look for JSON block with confidence_assessment
        json_pattern = r'```json\s*({[^`]*"confidence_assessment"[^`]*})\s*```'
        match = re.search(json_pattern, response_text, re.DOTALL)
        
        if match:
            json_str = match.group(1)
            data = json.loads(json_str)
            assessment = data.get('confidence_assessment', {})
            return ResponseConfidence.from_llm_assessment(assessment)
        
        # Try to find inline JSON
        inline_pattern = r'"confidence_assessment"\s*:\s*({[^}]+})'
        match = re.search(inline_pattern, response_text)
        
        if match:
            assessment = json.loads(match.group(1))
            return ResponseConfidence.from_llm_assessment(assessment)
        
        return None
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.debug(f"Could not extract confidence from response: {e}")
        return None


def strip_confidence_block(response_text: str) -> str:
    """
    Remove the confidence assessment JSON block from response text.
    
    The block is metadata, not content for the student.
    """
    import re
    
    # Remove JSON code block
    response_text = re.sub(
        r'```json\s*{[^`]*"confidence_assessment"[^`]*}\s*```',
        '',
        response_text,
        flags=re.DOTALL
    )
    
    return response_text.strip()


# ============================================================================
# SINGLETON ACCESS
# ============================================================================

_confidence_handler: Optional[ConfidenceAwareResponseHandler] = None
_confidence_calibrator: Optional[ConfidenceCalibrator] = None


def get_confidence_handler(db=None) -> ConfidenceAwareResponseHandler:
    """Get or create confidence handler singleton."""
    global _confidence_handler
    if _confidence_handler is None:
        _confidence_handler = ConfidenceAwareResponseHandler(db)
    return _confidence_handler


def get_confidence_calibrator(db=None) -> ConfidenceCalibrator:
    """Get or create confidence calibrator singleton."""
    global _confidence_calibrator
    if _confidence_calibrator is None:
        _confidence_calibrator = ConfidenceCalibrator(db)
    return _confidence_calibrator


