"""
🎯 Semantic Model Selector — Dynamic Model Selection
=====================================================

GAP 2 IMPLEMENTATION: Model Selection as Pure Function

Model selection is a pure function:
    model = f(semantic_complexity, latency_budget, confidence_required)

ARCHITECTURAL PRINCIPLES:
- No task names in selection logic
- No agent names in selection logic
- No keywords or string matching
- Model selection occurs at EXECUTION TIME, not routing time

STRICT RULE:
Model selection must be deterministic from semantic signals only.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ModelTier(Enum):
    """Model capability tiers based on reasoning ability."""
    FAST = "fast"           # Fast, cheap, for trivial tasks
    BALANCED = "balanced"   # Good balance of speed and quality
    ADVANCED = "advanced"   # High quality reasoning
    FRONTIER = "frontier"   # Best available, for complex reasoning


class ModelProvider(Enum):
    """Available model providers."""
    GEMINI = "gemini"
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    ANTHROPIC = "anthropic"


@dataclass
class ModelCapability:
    """Capabilities of a specific model."""
    name: str
    provider: ModelProvider
    tier: ModelTier
    
    # Capability scores (0.0 - 1.0)
    reasoning_strength: float      # Complex logical reasoning
    factual_accuracy: float        # Factual correctness
    math_ability: float            # Mathematical computation
    creativity: float              # Creative/generative tasks
    instruction_following: float   # Following complex instructions
    
    # Practical constraints
    latency_ms: int                # Average response time
    cost_per_1k_tokens: float      # Cost efficiency
    max_context: int               # Maximum context window
    supports_streaming: bool = True
    supports_vision: bool = False
    supports_structured_output: bool = True


@dataclass
class ModelSelectionCriteria:
    """
    Pure semantic criteria for model selection.
    
    These are derived from SemanticAnalysis, NOT from task names or keywords.
    """
    # Semantic complexity (from SemanticAnalysis)
    semantic_complexity: float = 0.5    # 0-1: How complex is the reasoning?
    reasoning_depth_required: int = 1   # 1-5: How many reasoning steps?
    
    # Accuracy requirements
    confidence_required: float = 0.7    # Minimum confidence needed
    factual_precision_needed: bool = False  # Is this a fact-check query?
    
    # Task characteristics (semantic, not keyword)
    involves_math: bool = False
    involves_creative: bool = False
    involves_analysis: bool = False
    involves_step_by_step: bool = False
    
    # Practical constraints
    latency_budget_ms: int = 5000       # Maximum acceptable latency
    quality_vs_speed: float = 0.5       # 0=speed, 1=quality
    
    @classmethod
    def from_semantic_analysis(cls, analysis, context: Dict[str, Any] = None) -> 'ModelSelectionCriteria':
        """
        Create selection criteria from SemanticAnalysis object or dict.
        
        Handles both:
        - SemanticAnalysis object (direct attribute access)
        - Dict from to_dict() conversion in routing context
        
        Missing fields are handled gracefully with sensible defaults.
        """
        context = context or {}
        
        # Helper to safely get values from object or dict
        def _get(key: str, default=None):
            if isinstance(analysis, dict):
                return analysis.get(key, default)
            return getattr(analysis, key, default)
        
        # Extract fields with safe access
        reasoning_depth = _get('reasoning_depth', 1)  # Not in SemanticAnalysis, default to 1
        response_expectation = _get('response_expectation', 'conversational_advice')
        abstraction_level = _get('abstraction_level', 'concrete')  # Not in SemanticAnalysis
        subject_area = _get('subject_area', _get('topic_mentioned', 'General'))  # Fallback to topic_mentioned
        reasoning = _get('reasoning', '') or ''
        suggested_response_style = _get('suggested_response_style', '') or ''
        
        # Compute semantic complexity from multiple signals
        complexity = 0.3  # Base
        
        # Reasoning depth contributes to complexity
        if reasoning_depth and reasoning_depth > 2:
            complexity += 0.2
        
        # Detailed explanations need higher complexity
        if response_expectation in ["detailed_explanation", "step_by_step_solution", "structured_deliverable"]:
            complexity += 0.2
        
        # Abstract topics need more reasoning
        if abstraction_level in ["theoretical", "philosophical"]:
            complexity += 0.15
        
        complexity = min(1.0, complexity)
        
        # Determine task characteristics from semantic fields
        involves_math = any([
            subject_area in ["Mathematics", "Physics", "Chemistry", "math", "physics", "chemistry"],
            "calculation" in reasoning.lower(),
            "solve" in str(response_expectation).lower()
        ])
        
        involves_creative = any([
            response_expectation in ["analogy", "metaphor", "story"],
            "creative" in suggested_response_style.lower()
        ])
        
        involves_analysis = any([
            response_expectation in ["comparison", "evaluation", "analysis"],
            reasoning_depth and reasoning_depth > 3
        ])
        
        involves_step_by_step = any([
            response_expectation == "step_by_step_solution",
            "process" in reasoning.lower()
        ])
        
        # Accuracy requirements based on subject
        factual_precision = subject_area in [
            "Science", "Mathematics", "History", "Geography",
            "science", "math", "mathematics", "history", "geography"
        ]
        
        # Get latency budget from context
        latency_budget = context.get("latency_budget_ms", 5000)
        if context.get("is_streaming", True):
            latency_budget = 10000  # More lenient for streaming
        
        # Quality vs speed preference
        quality_preference = 0.5
        if complexity > 0.7:
            quality_preference = 0.8  # Prefer quality for complex
        elif complexity < 0.3:
            quality_preference = 0.2  # Prefer speed for simple
        
        return cls(
            semantic_complexity=complexity,
            reasoning_depth_required=reasoning_depth or 1,
            confidence_required=context.get("confidence_required", 0.7),
            factual_precision_needed=factual_precision,
            involves_math=involves_math,
            involves_creative=involves_creative,
            involves_analysis=involves_analysis,
            involves_step_by_step=involves_step_by_step,
            latency_budget_ms=latency_budget,
            quality_vs_speed=quality_preference
        )


# ============================================================================
# MODEL REGISTRY
# ============================================================================

MODEL_REGISTRY: Dict[str, ModelCapability] = {
    # FAST TIER
    "gemini-1.5-flash": ModelCapability(
        name="gemini-1.5-flash",
        provider=ModelProvider.GEMINI,
        tier=ModelTier.FAST,
        reasoning_strength=0.6,
        factual_accuracy=0.7,
        math_ability=0.6,
        creativity=0.7,
        instruction_following=0.8,
        latency_ms=800,
        cost_per_1k_tokens=0.0001,
        max_context=1000000,
        supports_vision=True
    ),
    
    # BALANCED TIER
    "gemini-1.5-pro": ModelCapability(
        name="gemini-1.5-pro",
        provider=ModelProvider.GEMINI,
        tier=ModelTier.BALANCED,
        reasoning_strength=0.8,
        factual_accuracy=0.85,
        math_ability=0.75,
        creativity=0.8,
        instruction_following=0.85,
        latency_ms=2000,
        cost_per_1k_tokens=0.00125,
        max_context=2000000,
        supports_vision=True
    ),
    "gpt-4o-mini": ModelCapability(
        name="gpt-4o-mini",
        provider=ModelProvider.OPENAI,
        tier=ModelTier.BALANCED,
        reasoning_strength=0.75,
        factual_accuracy=0.8,
        math_ability=0.7,
        creativity=0.85,
        instruction_following=0.85,
        latency_ms=1500,
        cost_per_1k_tokens=0.00015,
        max_context=128000,
        supports_vision=True
    ),
    
    # ADVANCED TIER
    "gpt-4o": ModelCapability(
        name="gpt-4o",
        provider=ModelProvider.OPENAI,
        tier=ModelTier.ADVANCED,
        reasoning_strength=0.9,
        factual_accuracy=0.9,
        math_ability=0.85,
        creativity=0.9,
        instruction_following=0.95,
        latency_ms=3000,
        cost_per_1k_tokens=0.005,
        max_context=128000,
        supports_vision=True
    ),
    "deepseek-chat": ModelCapability(
        name="deepseek-chat",
        provider=ModelProvider.DEEPSEEK,
        tier=ModelTier.ADVANCED,
        reasoning_strength=0.85,
        factual_accuracy=0.85,
        math_ability=0.9,  # DeepSeek excels at math
        creativity=0.75,
        instruction_following=0.85,
        latency_ms=2500,
        cost_per_1k_tokens=0.0014,
        max_context=128000,
        supports_vision=False
    ),
    
    # FRONTIER TIER
    "claude-3-5-sonnet": ModelCapability(
        name="claude-3-5-sonnet",
        provider=ModelProvider.ANTHROPIC,
        tier=ModelTier.FRONTIER,
        reasoning_strength=0.95,
        factual_accuracy=0.92,
        math_ability=0.88,
        creativity=0.92,
        instruction_following=0.95,
        latency_ms=4000,
        cost_per_1k_tokens=0.003,
        max_context=200000,
        supports_vision=True
    ),
    "o1-preview": ModelCapability(
        name="o1-preview",
        provider=ModelProvider.OPENAI,
        tier=ModelTier.FRONTIER,
        reasoning_strength=0.98,  # Best reasoning
        factual_accuracy=0.92,
        math_ability=0.95,
        creativity=0.8,
        instruction_following=0.9,
        latency_ms=15000,  # Much slower
        cost_per_1k_tokens=0.015,
        max_context=128000,
        supports_streaming=False  # o1 doesn't stream
    )
}


# ============================================================================
# SEMANTIC MODEL SELECTOR
# ============================================================================

class SemanticModelSelector:
    """
    Selects model based on semantic criteria ONLY.
    
    model = f(semantic_complexity, latency_budget, confidence_required)
    
    NO task names. NO agent names. NO keywords.
    """
    
    def __init__(self, available_models: List[str] = None):
        """
        Initialize with available models.
        
        Args:
            available_models: List of model names from MODEL_REGISTRY.
                            If None, uses all registered models.
        """
        if available_models:
            self.models = {k: v for k, v in MODEL_REGISTRY.items() if k in available_models}
        else:
            self.models = MODEL_REGISTRY.copy()
        
        logger.info(f"🤖 SemanticModelSelector initialized with {len(self.models)} models")
    
    def select(self, criteria: ModelSelectionCriteria) -> str:
        """
        Select the best model for given criteria.
        
        This is a PURE FUNCTION:
        - Input: semantic criteria
        - Output: model name
        - No side effects
        - Deterministic
        """
        # Score each model
        scores = {}
        
        for name, capability in self.models.items():
            score = self._score_model(capability, criteria)
            
            # Apply latency constraint as hard cutoff
            if capability.latency_ms > criteria.latency_budget_ms:
                score *= 0.1  # Heavy penalty, not elimination
            
            scores[name] = score
        
        # Select best model
        best_model = max(scores, key=scores.get)
        
        logger.info(f"🤖 Model selected: {best_model} | "
                   f"complexity={criteria.semantic_complexity:.2f} | "
                   f"quality_pref={criteria.quality_vs_speed:.2f}")
        
        return best_model
    
    def _score_model(self, capability: ModelCapability, criteria: ModelSelectionCriteria) -> float:
        """
        Score a model against criteria.
        
        Returns weighted score (0-1) based on how well model matches criteria.
        """
        score = 0.0
        
        # === REASONING MATCH ===
        # Higher complexity needs better reasoning
        reasoning_need = criteria.semantic_complexity
        reasoning_match = capability.reasoning_strength / max(0.1, reasoning_need)
        score += 0.3 * min(1.0, reasoning_match)  # Cap at 1.0
        
        # === ACCURACY MATCH ===
        if criteria.factual_precision_needed:
            score += 0.2 * capability.factual_accuracy
        else:
            score += 0.1 * capability.factual_accuracy
        
        # === TASK-SPECIFIC CAPABILITIES ===
        if criteria.involves_math:
            score += 0.15 * capability.math_ability
        
        if criteria.involves_creative:
            score += 0.1 * capability.creativity
        
        if criteria.involves_analysis or criteria.involves_step_by_step:
            score += 0.1 * capability.reasoning_strength
        
        # === QUALITY VS SPEED TRADEOFF ===
        # quality_vs_speed: 0 = prefer speed, 1 = prefer quality
        speed_factor = 1.0 - (capability.latency_ms / 20000)  # Normalize to ~0-1
        speed_factor = max(0, min(1, speed_factor))
        
        quality_factor = capability.reasoning_strength
        
        # Blend based on preference
        tradeoff_score = (
            criteria.quality_vs_speed * quality_factor +
            (1 - criteria.quality_vs_speed) * speed_factor
        )
        score += 0.15 * tradeoff_score
        
        return score
    
    def select_with_fallback(
        self,
        criteria: ModelSelectionCriteria,
        fallback_model: str = "gemini-1.5-flash"
    ) -> str:
        """
        Select model with graceful fallback.
        
        If primary selection fails (e.g., model unavailable), falls back safely.
        """
        try:
            primary = self.select(criteria)
            if primary in self.models:
                return primary
            return fallback_model
        except Exception as e:
            logger.warning(f"Model selection failed, using fallback: {e}")
            return fallback_model


# ============================================================================
# SINGLETON ACCESS
# ============================================================================

_model_selector: Optional[SemanticModelSelector] = None


def get_model_selector(available_models: List[str] = None) -> SemanticModelSelector:
    """Get or create model selector singleton."""
    global _model_selector
    if _model_selector is None:
        _model_selector = SemanticModelSelector(available_models)
    return _model_selector


def select_model_for_semantic(
    semantic_analysis: 'SemanticAnalysis',
    context: Dict[str, Any] = None
) -> str:
    """
    Convenience function to select model from SemanticAnalysis.
    
    This is the primary API for model selection.
    """
    criteria = ModelSelectionCriteria.from_semantic_analysis(semantic_analysis, context)
    selector = get_model_selector()
    return selector.select(criteria)


