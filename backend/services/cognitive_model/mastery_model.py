"""
Mastery Model - Bayesian Knowledge Tracing
===========================================

Implements a simplified Bayesian Knowledge Tracing (BKT) model
to estimate student mastery and predict performance.

Key features:
- Probabilistic mastery estimation
- Learning rate adaptation
- Slip and guess probability modeling
- Forgetting curve integration
"""

import logging
import math
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class BKTParameters:
    """Parameters for Bayesian Knowledge Tracing"""
    p_init: float = 0.1       # Initial probability of mastery
    p_learn: float = 0.3      # Probability of learning after opportunity
    p_slip: float = 0.1       # Probability of slip (known but wrong)
    p_guess: float = 0.2      # Probability of guess (unknown but right)
    p_forget: float = 0.05    # Daily forgetting rate
    
    def validate(self) -> bool:
        """Ensure parameters are valid probabilities"""
        params = [self.p_init, self.p_learn, self.p_slip, self.p_guess, self.p_forget]
        return all(0.0 <= p <= 1.0 for p in params)


@dataclass
class MasteryEstimate:
    """Mastery estimate for a skill/concept"""
    skill_id: str
    p_mastery: float  # Probability of mastery (0.0 to 1.0)
    confidence: float  # Confidence in estimate
    observations: int  # Number of observations
    last_correct: Optional[bool] = None
    last_updated: Optional[datetime] = None
    predicted_correct: float = 0.5  # Predicted probability of next correct


class MasteryModel:
    """
    Bayesian Knowledge Tracing model for mastery estimation.
    
    Uses a simplified BKT model to:
    - Estimate probability of skill mastery
    - Update estimates based on observations
    - Predict performance on future problems
    - Account for forgetting over time
    """
    
    def __init__(self, params: Optional[BKTParameters] = None):
        """Initialize with optional custom parameters"""
        self.params = params or BKTParameters()
        self._estimates: Dict[str, Dict[str, MasteryEstimate]] = {}  # user_id -> skill_id -> estimate
        logger.info("📊 MasteryModel initialized with BKT")
    
    def get_mastery(
        self,
        user_id: str,
        skill_id: str
    ) -> MasteryEstimate:
        """
        Get current mastery estimate for a skill.
        
        Args:
            user_id: Student's user ID
            skill_id: Skill/concept identifier
            
        Returns:
            MasteryEstimate with probability and confidence
        """
        if user_id not in self._estimates:
            self._estimates[user_id] = {}
        
        if skill_id not in self._estimates[user_id]:
            # Initialize with prior
            self._estimates[user_id][skill_id] = MasteryEstimate(
                skill_id=skill_id,
                p_mastery=self.params.p_init,
                confidence=0.0,
                observations=0,
                predicted_correct=self._calculate_p_correct(self.params.p_init)
            )
        
        estimate = self._estimates[user_id][skill_id]
        
        # Apply forgetting if time has passed
        if estimate.last_updated:
            estimate = self._apply_forgetting(estimate)
        
        return estimate
    
    def update_mastery(
        self,
        user_id: str,
        skill_id: str,
        correct: bool
    ) -> MasteryEstimate:
        """
        Update mastery estimate based on new observation.
        
        Uses BKT update rules:
        - If correct: P(L|correct) = P(L)*P(~slip) / P(correct)
        - If incorrect: P(L|incorrect) = P(L)*P(slip) / P(incorrect)
        
        Args:
            user_id: Student's user ID
            skill_id: Skill/concept identifier
            correct: Whether the response was correct
            
        Returns:
            Updated MasteryEstimate
        """
        estimate = self.get_mastery(user_id, skill_id)
        
        # Current mastery probability
        p_l = estimate.p_mastery
        
        # Calculate posterior using Bayes' rule
        if correct:
            # P(L|correct) = P(correct|L)*P(L) / P(correct)
            # P(correct|L) = 1 - p_slip
            # P(correct|~L) = p_guess
            # P(correct) = P(correct|L)*P(L) + P(correct|~L)*P(~L)
            
            p_correct_given_l = 1.0 - self.params.p_slip
            p_correct_given_not_l = self.params.p_guess
            p_correct = p_correct_given_l * p_l + p_correct_given_not_l * (1 - p_l)
            
            if p_correct > 0:
                p_l_given_correct = (p_correct_given_l * p_l) / p_correct
            else:
                p_l_given_correct = p_l
            
            new_p_l = p_l_given_correct
            
        else:
            # P(L|incorrect) = P(incorrect|L)*P(L) / P(incorrect)
            # P(incorrect|L) = p_slip
            # P(incorrect|~L) = 1 - p_guess
            
            p_incorrect_given_l = self.params.p_slip
            p_incorrect_given_not_l = 1.0 - self.params.p_guess
            p_incorrect = p_incorrect_given_l * p_l + p_incorrect_given_not_l * (1 - p_l)
            
            if p_incorrect > 0:
                p_l_given_incorrect = (p_incorrect_given_l * p_l) / p_incorrect
            else:
                p_l_given_incorrect = p_l
            
            new_p_l = p_l_given_incorrect
        
        # Apply learning transition (student may have learned from this opportunity)
        # P(L') = P(L|obs) + (1 - P(L|obs)) * P(T)
        new_p_l = new_p_l + (1 - new_p_l) * self.params.p_learn
        
        # Bound probability
        new_p_l = max(0.01, min(0.99, new_p_l))
        
        # Update estimate
        estimate.p_mastery = new_p_l
        estimate.observations += 1
        estimate.last_correct = correct
        estimate.last_updated = datetime.now(timezone.utc)
        estimate.confidence = min(1.0, estimate.observations / 10.0)
        estimate.predicted_correct = self._calculate_p_correct(new_p_l)
        
        # Store
        self._estimates[user_id][skill_id] = estimate
        
        logger.debug(f"Updated mastery for {skill_id}: {p_l:.3f} -> {new_p_l:.3f}")
        
        return estimate
    
    def batch_update(
        self,
        user_id: str,
        observations: List[Tuple[str, bool]]  # [(skill_id, correct), ...]
    ) -> Dict[str, MasteryEstimate]:
        """
        Batch update mastery for multiple skills.
        
        Args:
            user_id: Student's user ID
            observations: List of (skill_id, correct) tuples
            
        Returns:
            Dict of updated estimates
        """
        results = {}
        for skill_id, correct in observations:
            results[skill_id] = self.update_mastery(user_id, skill_id, correct)
        return results
    
    def predict_performance(
        self,
        user_id: str,
        skill_ids: List[str]
    ) -> Dict[str, float]:
        """
        Predict probability of correct response for skills.
        
        Args:
            user_id: Student's user ID
            skill_ids: List of skill identifiers
            
        Returns:
            Dict mapping skill_id to P(correct)
        """
        predictions = {}
        for skill_id in skill_ids:
            estimate = self.get_mastery(user_id, skill_id)
            predictions[skill_id] = estimate.predicted_correct
        return predictions
    
    def get_mastered_skills(
        self,
        user_id: str,
        threshold: float = 0.85
    ) -> List[str]:
        """Get skills where P(mastery) >= threshold"""
        if user_id not in self._estimates:
            return []
        
        return [
            skill_id for skill_id, estimate in self._estimates[user_id].items()
            if estimate.p_mastery >= threshold
        ]
    
    def get_struggling_skills(
        self,
        user_id: str,
        threshold: float = 0.4,
        min_observations: int = 3
    ) -> List[str]:
        """Get skills where student is struggling"""
        if user_id not in self._estimates:
            return []
        
        return [
            skill_id for skill_id, estimate in self._estimates[user_id].items()
            if estimate.p_mastery < threshold and estimate.observations >= min_observations
        ]
    
    def get_ready_for_advancement(
        self,
        user_id: str,
        threshold: float = 0.75
    ) -> List[Tuple[str, float]]:
        """Get skills ready for harder problems, with mastery level"""
        if user_id not in self._estimates:
            return []
        
        ready = [
            (skill_id, estimate.p_mastery)
            for skill_id, estimate in self._estimates[user_id].items()
            if threshold <= estimate.p_mastery < 0.95  # Not fully mastered but ready
        ]
        
        return sorted(ready, key=lambda x: x[1], reverse=True)
    
    def _calculate_p_correct(self, p_mastery: float) -> float:
        """Calculate probability of correct response given mastery probability"""
        # P(correct) = P(correct|L)*P(L) + P(correct|~L)*P(~L)
        # P(correct|L) = 1 - p_slip
        # P(correct|~L) = p_guess
        
        p_correct = (1 - self.params.p_slip) * p_mastery + self.params.p_guess * (1 - p_mastery)
        return p_correct
    
    def _apply_forgetting(self, estimate: MasteryEstimate) -> MasteryEstimate:
        """Apply forgetting curve to mastery estimate"""
        if not estimate.last_updated:
            return estimate
        
        days_elapsed = (datetime.now(timezone.utc) - estimate.last_updated).days
        
        if days_elapsed > 0:
            # Exponential decay
            decay_factor = math.exp(-self.params.p_forget * days_elapsed)
            
            # Apply decay but maintain a floor (knowledge isn't completely forgotten)
            new_p = estimate.p_mastery * decay_factor + self.params.p_init * (1 - decay_factor)
            
            estimate.p_mastery = max(self.params.p_init, new_p)
            estimate.predicted_correct = self._calculate_p_correct(estimate.p_mastery)
        
        return estimate
    
    def adapt_parameters(
        self,
        user_id: str,
        performance_history: List[Tuple[str, bool]]
    ) -> BKTParameters:
        """
        Adapt BKT parameters based on student's learning pattern.
        
        Some students learn faster (higher p_learn), some guess more (higher p_guess).
        This personalizes the model.
        """
        if len(performance_history) < 10:
            return self.params  # Not enough data
        
        # Calculate observed learning rate
        skill_sequences: Dict[str, List[bool]] = {}
        for skill_id, correct in performance_history:
            if skill_id not in skill_sequences:
                skill_sequences[skill_id] = []
            skill_sequences[skill_id].append(correct)
        
        # Look for learning patterns (incorrect -> correct transitions)
        learning_events = 0
        learning_opportunities = 0
        
        for skill_id, sequence in skill_sequences.items():
            for i in range(1, len(sequence)):
                if not sequence[i-1]:  # Previous was wrong
                    learning_opportunities += 1
                    if sequence[i]:  # Now correct
                        learning_events += 1
        
        # Estimate learning rate
        if learning_opportunities > 5:
            observed_p_learn = learning_events / learning_opportunities
            # Blend with prior
            adapted_p_learn = 0.7 * self.params.p_learn + 0.3 * observed_p_learn
        else:
            adapted_p_learn = self.params.p_learn
        
        return BKTParameters(
            p_init=self.params.p_init,
            p_learn=max(0.1, min(0.6, adapted_p_learn)),
            p_slip=self.params.p_slip,
            p_guess=self.params.p_guess,
            p_forget=self.params.p_forget
        )

