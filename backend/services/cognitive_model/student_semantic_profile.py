"""
📚 Student Semantic Profile — Cross-Session Learning
=====================================================

GAP 3 IMPLEMENTATION: Cross-Session Semantic Learning

Store structured semantic signals, not raw transcripts.
Learning influences behavior ONLY through context injection.

ARCHITECTURAL PRINCIPLES:
- Store semantic signals only (not transcripts)
- No embeddings stored
- No per-user model training
- Learning through context injection, never hidden state

STRICT RULE:
Learning may influence behavior only through context injection,
never through hidden or implicit state.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timezone, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class LearningPatternType(Enum):
    """Types of learning patterns we track."""
    CONCEPT_STRUGGLE = "concept_struggle"       # Repeated difficulty with concept
    EXPLANATION_PREFERENCE = "explanation_pref" # Preferred explanation style
    LEARNING_PACE = "learning_pace"             # Fast/slow learner signals
    EMOTIONAL_PATTERN = "emotional_pattern"     # Recurring emotional states
    TIME_PATTERN = "time_pattern"               # When student studies best
    RESPONSE_PREFERENCE = "response_pref"       # Prefers detailed/concise


@dataclass
class SemanticSignal:
    """
    A single semantic signal extracted from an interaction.
    
    These are STRUCTURED signals, not raw text.
    """
    signal_type: str              # e.g., "struggled_with", "mastered", "prefers"
    subject: str                  # Subject area
    concept: str                  # Specific concept
    value: Any                    # Signal value (structured)
    confidence: float             # How confident we are in this signal (0-1)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_type": self.signal_type,
            "subject": self.subject,
            "concept": self.concept,
            "value": self.value,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SemanticSignal':
        return cls(
            signal_type=data["signal_type"],
            subject=data["subject"],
            concept=data["concept"],
            value=data["value"],
            confidence=data["confidence"],
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now(timezone.utc)
        )


@dataclass
class LearningPattern:
    """
    An aggregated learning pattern derived from semantic signals.
    
    Patterns are higher-level insights, not raw signals.
    """
    pattern_type: LearningPatternType
    subject: Optional[str]        # Subject if applicable
    description: str              # Human-readable description
    strength: float               # Pattern strength (0-1)
    evidence_count: int           # How many signals support this
    first_observed: datetime
    last_observed: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_type": self.pattern_type.value,
            "subject": self.subject,
            "description": self.description,
            "strength": self.strength,
            "evidence_count": self.evidence_count,
            "first_observed": self.first_observed.isoformat(),
            "last_observed": self.last_observed.isoformat()
        }


@dataclass
class StudentSemanticProfile:
    """
    Aggregated semantic profile of a student.
    
    This is what gets injected into context to influence behavior.
    NO raw transcripts. NO embeddings. ONLY structured signals.
    """
    user_id: str
    
    # Aggregated understanding
    strong_subjects: List[str] = field(default_factory=list)
    weak_subjects: List[str] = field(default_factory=list)
    struggling_concepts: List[str] = field(default_factory=list)
    mastered_concepts: List[str] = field(default_factory=list)
    
    # Preferences (learned, not configured)
    preferred_explanation_style: str = "balanced"  # detailed, concise, visual, analogical
    preferred_pace: str = "normal"                 # fast, normal, slow
    prefers_encouragement: bool = True
    prefers_structure: bool = True
    
    # Patterns
    learning_patterns: List[LearningPattern] = field(default_factory=list)
    
    # Recent semantic signals (limited buffer)
    recent_signals: List[SemanticSignal] = field(default_factory=list)
    
    # Metadata
    profile_version: int = 1
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    signal_count: int = 0
    
    def get_context_injection(self) -> Dict[str, Any]:
        """
        Get structured data for context injection.
        
        This is THE ONLY way learning influences behavior.
        """
        return {
            "student_learning_profile": {
                # Strengths and weaknesses
                "strong_subjects": self.strong_subjects[:5],
                "weak_subjects": self.weak_subjects[:5],
                "struggling_concepts": self.struggling_concepts[:10],
                "mastered_concepts": self.mastered_concepts[:10],
                
                # Preferences
                "preferred_explanation_style": self.preferred_explanation_style,
                "preferred_pace": self.preferred_pace,
                "prefers_encouragement": self.prefers_encouragement,
                "prefers_structure": self.prefers_structure,
                
                # Top patterns
                "key_patterns": [
                    {
                        "type": p.pattern_type.value,
                        "description": p.description,
                        "strength": p.strength
                    }
                    for p in sorted(self.learning_patterns, key=lambda x: x.strength, reverse=True)[:5]
                ],
                
                # Meta
                "signal_count": self.signal_count,
                "last_updated": self.last_updated.isoformat() if self.last_updated else None
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "strong_subjects": self.strong_subjects,
            "weak_subjects": self.weak_subjects,
            "struggling_concepts": self.struggling_concepts,
            "mastered_concepts": self.mastered_concepts,
            "preferred_explanation_style": self.preferred_explanation_style,
            "preferred_pace": self.preferred_pace,
            "prefers_encouragement": self.prefers_encouragement,
            "prefers_structure": self.prefers_structure,
            "learning_patterns": [p.to_dict() for p in self.learning_patterns],
            "recent_signals": [s.to_dict() for s in self.recent_signals[-50:]],  # Bounded
            "profile_version": self.profile_version,
            "last_updated": self.last_updated.isoformat(),
            "signal_count": self.signal_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StudentSemanticProfile':
        patterns = []
        for p in data.get("learning_patterns", []):
            patterns.append(LearningPattern(
                pattern_type=LearningPatternType(p["pattern_type"]),
                subject=p.get("subject"),
                description=p["description"],
                strength=p["strength"],
                evidence_count=p.get("evidence_count", 1),
                first_observed=datetime.fromisoformat(p["first_observed"]),
                last_observed=datetime.fromisoformat(p["last_observed"])
            ))
        
        signals = [SemanticSignal.from_dict(s) for s in data.get("recent_signals", [])]
        
        return cls(
            user_id=data["user_id"],
            strong_subjects=data.get("strong_subjects", []),
            weak_subjects=data.get("weak_subjects", []),
            struggling_concepts=data.get("struggling_concepts", []),
            mastered_concepts=data.get("mastered_concepts", []),
            preferred_explanation_style=data.get("preferred_explanation_style", "balanced"),
            preferred_pace=data.get("preferred_pace", "normal"),
            prefers_encouragement=data.get("prefers_encouragement", True),
            prefers_structure=data.get("prefers_structure", True),
            learning_patterns=patterns,
            recent_signals=signals,
            profile_version=data.get("profile_version", 1),
            last_updated=datetime.fromisoformat(data["last_updated"]) if data.get("last_updated") else datetime.now(timezone.utc),
            signal_count=data.get("signal_count", 0)
        )


# ============================================================================
# SEMANTIC LEARNING EXTRACTOR
# ============================================================================

class SemanticLearningExtractor:
    """
    Extracts semantic learning signals from interactions.
    
    RULES:
    - Extract structured signals, not raw text
    - No transcripts stored
    - No embeddings computed
    - All learning is through context injection
    """
    
    def __init__(self, db=None):
        self.db = db
        logger.info("📚 SemanticLearningExtractor initialized")
    
    async def extract_signals(
        self,
        query: str,
        response: Dict[str, Any],
        semantic_analysis: 'SemanticAnalysis',
        context: Dict[str, Any]
    ) -> List[SemanticSignal]:
        """
        Extract semantic signals from an interaction.
        
        Returns structured signals, NOT raw text.
        """
        signals = []
        now = datetime.now(timezone.utc)
        subject = semantic_analysis.subject_area if semantic_analysis else "General"
        
        # Signal 1: Topic engagement
        if semantic_analysis and semantic_analysis.main_topic:
            signals.append(SemanticSignal(
                signal_type="engaged_topic",
                subject=subject,
                concept=semantic_analysis.main_topic,
                value={"depth": semantic_analysis.reasoning_depth or 1},
                confidence=0.8,
                timestamp=now
            ))
        
        # Signal 2: Response style acceptance
        response_type = response.get("metadata", {}).get("response_type", "unknown")
        if response_type != "unknown":
            signals.append(SemanticSignal(
                signal_type="received_style",
                subject=subject,
                concept=response_type,
                value={"accepted": True},  # Can be updated by feedback
                confidence=0.7,
                timestamp=now
            ))
        
        # Signal 3: Complexity level
        complexity = semantic_analysis.complexity_score if semantic_analysis else 0.5
        signals.append(SemanticSignal(
            signal_type="query_complexity",
            subject=subject,
            concept="complexity_level",
            value={"score": complexity},
            confidence=0.9,
            timestamp=now
        ))
        
        # Signal 4: Emotional state (if detected)
        if semantic_analysis and semantic_analysis.emotional_tone:
            signals.append(SemanticSignal(
                signal_type="emotional_state",
                subject=subject,
                concept="emotion",
                value={"tone": semantic_analysis.emotional_tone},
                confidence=0.7,
                timestamp=now
            ))
        
        return signals
    
    async def extract_from_feedback(
        self,
        feedback_type: str,  # "helpful", "not_helpful", "unclear"
        response_type: str,
        subject: str
    ) -> List[SemanticSignal]:
        """
        Extract signals from user feedback.
        """
        now = datetime.now(timezone.utc)
        
        if feedback_type == "helpful":
            return [SemanticSignal(
                signal_type="response_preference",
                subject=subject,
                concept="preferred_style",
                value={"style": response_type, "liked": True},
                confidence=0.9,
                timestamp=now
            )]
        elif feedback_type == "not_helpful":
            return [SemanticSignal(
                signal_type="response_preference",
                subject=subject,
                concept="avoided_style",
                value={"style": response_type, "liked": False},
                confidence=0.9,
                timestamp=now
            )]
        elif feedback_type == "unclear":
            return [SemanticSignal(
                signal_type="clarity_issue",
                subject=subject,
                concept="needs_clearer",
                value={"original_style": response_type},
                confidence=0.85,
                timestamp=now
            )]
        
        return []


# ============================================================================
# PROFILE MANAGER
# ============================================================================

class SemanticProfileManager:
    """
    Manages student semantic profiles.
    
    Handles:
    - Loading/saving profiles
    - Aggregating signals into patterns
    - Generating context injections
    """
    
    def __init__(self, db=None):
        self.db = db
        self.extractor = SemanticLearningExtractor(db)
        self._cache: Dict[str, StudentSemanticProfile] = {}
        logger.info("📚 SemanticProfileManager initialized")
    
    async def get_profile(self, user_id: str) -> StudentSemanticProfile:
        """
        Get or create student's semantic profile.
        """
        # Check cache
        if user_id in self._cache:
            return self._cache[user_id]
        
        # Try to load from DB
        if self.db:
            try:
                profile_data = await self.db.semantic_profiles.find_one({"user_id": user_id})
                if profile_data:
                    profile = StudentSemanticProfile.from_dict(profile_data)
                    self._cache[user_id] = profile
                    return profile
            except Exception as e:
                logger.warning(f"Failed to load semantic profile: {e}")
        
        # Create new profile
        profile = StudentSemanticProfile(user_id=user_id)
        self._cache[user_id] = profile
        return profile
    
    async def add_signals(
        self,
        user_id: str,
        signals: List[SemanticSignal]
    ) -> StudentSemanticProfile:
        """
        Add semantic signals to student's profile.
        
        Signals are aggregated, not stored raw.
        """
        profile = await self.get_profile(user_id)
        
        for signal in signals:
            # Add to recent signals (bounded buffer)
            profile.recent_signals.append(signal)
            if len(profile.recent_signals) > 100:
                profile.recent_signals = profile.recent_signals[-50:]
            
            profile.signal_count += 1
            
            # Update aggregated data based on signal type
            await self._aggregate_signal(profile, signal)
        
        profile.last_updated = datetime.now(timezone.utc)
        
        # Save to DB
        await self._save_profile(profile)
        
        return profile
    
    async def _aggregate_signal(self, profile: StudentSemanticProfile, signal: SemanticSignal):
        """
        Aggregate a signal into the profile.
        
        This is where we convert raw signals into patterns.
        """
        if signal.signal_type == "engaged_topic":
            # Track concepts being learned
            concept = signal.concept
            if concept and concept not in profile.mastered_concepts:
                # Could be struggling or learning
                pass
        
        elif signal.signal_type == "response_preference":
            # Update explanation style preference
            if signal.value.get("liked"):
                style = signal.value.get("style", "balanced")
                if style in ["detailed", "concise", "visual", "analogical"]:
                    profile.preferred_explanation_style = style
        
        elif signal.signal_type == "clarity_issue":
            # Student needs clearer explanations
            profile.prefers_structure = True
        
        elif signal.signal_type == "emotional_state":
            tone = signal.value.get("tone", "neutral")
            if tone in ["anxious", "stressed", "frustrated"]:
                profile.prefers_encouragement = True
    
    async def _save_profile(self, profile: StudentSemanticProfile):
        """Save profile to DB."""
        if not self.db:
            return
        
        try:
            await self.db.semantic_profiles.update_one(
                {"user_id": profile.user_id},
                {"$set": profile.to_dict()},
                upsert=True
            )
        except Exception as e:
            logger.warning(f"Failed to save semantic profile: {e}")
    
    async def learn_from_interaction(
        self,
        user_id: str,
        query: str,
        response: Dict[str, Any],
        semantic_analysis: 'SemanticAnalysis',
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Learn from an interaction.
        
        Returns context injection for future responses.
        """
        # Extract signals
        signals = await self.extractor.extract_signals(
            query, response, semantic_analysis, context
        )
        
        # Add to profile
        profile = await self.add_signals(user_id, signals)
        
        # Return context injection
        return profile.get_context_injection()
    
    async def get_context_injection(self, user_id: str) -> Dict[str, Any]:
        """
        Get context injection for a user.
        
        This is THE ONLY way learning influences behavior.
        """
        profile = await self.get_profile(user_id)
        return profile.get_context_injection()


# ============================================================================
# SINGLETON ACCESS
# ============================================================================

_profile_manager: Optional[SemanticProfileManager] = None


def get_semantic_profile_manager(db=None) -> SemanticProfileManager:
    """Get or create semantic profile manager singleton."""
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = SemanticProfileManager(db)
    return _profile_manager


def reset_profile_manager():
    """Reset the profile manager singleton (for testing)."""
    global _profile_manager
    _profile_manager = None


