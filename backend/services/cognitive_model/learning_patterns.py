"""
Learning Pattern Analyzer - Understand How Each Student Learns
===============================================================

Analyzes student behavior to identify:
- Preferred learning style (visual, textual, interactive)
- Best time of day for learning
- Optimal session duration
- Most effective explanation types
- Common mistake patterns
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class LearningStyle(Enum):
    """Types of learning preferences"""
    VISUAL = "visual"           # Prefers diagrams, visual explanations
    TEXTUAL = "textual"         # Prefers detailed text explanations
    INTERACTIVE = "interactive"  # Prefers practice problems
    EXAMPLE_BASED = "example"   # Learns best from examples
    CONCEPTUAL = "conceptual"   # Prefers understanding underlying concepts


@dataclass
class SessionPattern:
    """Pattern of a learning session"""
    start_time: datetime
    duration_minutes: float
    questions_asked: int
    topics_covered: List[str]
    engagement_score: float  # 0.0 to 1.0
    performance_score: float  # 0.0 to 1.0


@dataclass
class LearningProfile:
    """Complete learning profile for a student"""
    user_id: str
    
    # Learning style preferences (scores 0.0 to 1.0)
    visual_preference: float = 0.5
    textual_preference: float = 0.5
    interactive_preference: float = 0.5
    example_preference: float = 0.5
    conceptual_preference: float = 0.5
    
    # Temporal patterns
    best_hours: List[int] = field(default_factory=lambda: [10, 11, 15, 16])  # Hours of day
    best_days: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])  # 0=Monday
    optimal_session_duration: int = 30  # minutes
    
    # Engagement patterns
    avg_session_length: float = 20.0
    avg_questions_per_session: float = 5.0
    avg_engagement: float = 0.5
    
    # Performance patterns
    strongest_subjects: List[str] = field(default_factory=list)
    weakest_subjects: List[str] = field(default_factory=list)
    common_mistake_types: List[str] = field(default_factory=list)
    
    # Preferences
    preferred_explanation_length: str = "medium"  # short, medium, long
    prefers_hinglish: bool = False
    preferred_metaphor_category: str = "cricket"
    
    @property
    def primary_learning_style(self) -> LearningStyle:
        """Get the dominant learning style"""
        styles = {
            LearningStyle.VISUAL: self.visual_preference,
            LearningStyle.TEXTUAL: self.textual_preference,
            LearningStyle.INTERACTIVE: self.interactive_preference,
            LearningStyle.EXAMPLE_BASED: self.example_preference,
            LearningStyle.CONCEPTUAL: self.conceptual_preference
        }
        return max(styles, key=styles.get)


class LearningPatternAnalyzer:
    """
    Analyzes and tracks student learning patterns.
    
    Uses interaction history to:
    - Identify learning style preferences
    - Find optimal study times
    - Detect common mistake patterns
    - Recommend personalized adaptations
    """
    
    def __init__(self, db=None):
        """Initialize the analyzer"""
        self.db = db
        self._profiles: Dict[str, LearningProfile] = {}
        self._sessions: Dict[str, List[SessionPattern]] = {}
        logger.info("🔬 LearningPatternAnalyzer initialized")
    
    async def get_learning_profile(
        self,
        user_id: str
    ) -> LearningProfile:
        """
        Get or create learning profile for a student.
        
        Args:
            user_id: Student's user ID
            
        Returns:
            LearningProfile with all patterns
        """
        if user_id in self._profiles:
            return self._profiles[user_id]
        
        # Try to load from database
        if self.db is not None:
            try:
                record = await self.db.learning_profiles.find_one({"user_id": user_id})
                if record:
                    profile = self._deserialize_profile(record)
                    self._profiles[user_id] = profile
                    return profile
            except Exception as e:
                logger.warning(f"Failed to load profile: {e}")
        
        # Create new profile
        profile = LearningProfile(user_id=user_id)
        self._profiles[user_id] = profile
        return profile
    
    async def record_interaction(
        self,
        user_id: str,
        interaction_type: str,  # "visual_engaged", "example_requested", etc.
        topic: str,
        subject: str,
        duration_seconds: float,
        engagement_signals: Dict[str, Any] = None
    ) -> None:
        """
        Record an interaction to update learning patterns.
        
        Args:
            user_id: Student's user ID
            interaction_type: Type of interaction
            topic: Topic being studied
            subject: Subject area
            duration_seconds: Time spent
            engagement_signals: Additional signals (scrolls, clicks, etc.)
        """
        profile = await self.get_learning_profile(user_id)
        
        # Update style preferences based on interaction type
        engagement = engagement_signals or {}
        
        if interaction_type in ["visual_clicked", "diagram_expanded", "animation_watched"]:
            profile.visual_preference = self._update_preference(
                profile.visual_preference, positive=True
            )
        
        elif interaction_type in ["example_requested", "more_examples_clicked"]:
            profile.example_preference = self._update_preference(
                profile.example_preference, positive=True
            )
        
        elif interaction_type in ["practice_started", "quiz_attempted"]:
            profile.interactive_preference = self._update_preference(
                profile.interactive_preference, positive=True
            )
        
        elif interaction_type in ["derivation_expanded", "proof_viewed"]:
            profile.conceptual_preference = self._update_preference(
                profile.conceptual_preference, positive=True
            )
        
        elif interaction_type in ["long_text_read", "explanation_scrolled"]:
            profile.textual_preference = self._update_preference(
                profile.textual_preference, positive=True
            )
        
        # Update temporal patterns
        now = datetime.now(timezone.utc)
        hour = now.hour
        day = now.weekday()
        
        # Track good study times (based on engagement)
        if engagement.get("engagement_score", 0.5) > 0.7:
            if hour not in profile.best_hours:
                profile.best_hours.append(hour)
                profile.best_hours = profile.best_hours[-8:]  # Keep last 8
            
            if day not in profile.best_days:
                profile.best_days.append(day)
                profile.best_days = list(set(profile.best_days))
        
        # Save profile
        self._profiles[user_id] = profile
        await self._save_profile(profile)
    
    async def record_session(
        self,
        user_id: str,
        session_data: Dict[str, Any]
    ) -> None:
        """Record a complete learning session"""
        profile = await self.get_learning_profile(user_id)
        
        if user_id not in self._sessions:
            self._sessions[user_id] = []
        
        session = SessionPattern(
            start_time=datetime.fromisoformat(session_data.get("start_time", datetime.now(timezone.utc).isoformat())),
            duration_minutes=session_data.get("duration_minutes", 0),
            questions_asked=session_data.get("questions_asked", 0),
            topics_covered=session_data.get("topics_covered", []),
            engagement_score=session_data.get("engagement_score", 0.5),
            performance_score=session_data.get("performance_score", 0.5)
        )
        
        self._sessions[user_id].append(session)
        
        # Update profile with session stats
        sessions = self._sessions[user_id]
        profile.avg_session_length = sum(s.duration_minutes for s in sessions) / len(sessions)
        profile.avg_questions_per_session = sum(s.questions_asked for s in sessions) / len(sessions)
        profile.avg_engagement = sum(s.engagement_score for s in sessions) / len(sessions)
        
        # Update optimal session duration (based on best performing sessions)
        high_performance_sessions = [s for s in sessions if s.performance_score > 0.7]
        if high_performance_sessions:
            profile.optimal_session_duration = int(
                sum(s.duration_minutes for s in high_performance_sessions) / len(high_performance_sessions)
            )
        
        await self._save_profile(profile)
    
    async def record_mistake(
        self,
        user_id: str,
        mistake_type: str,
        topic: str,
        subject: str,
        details: str = None
    ) -> None:
        """
        Record a common mistake for pattern detection.
        
        Mistake types:
        - "calculation_error": Arithmetic mistakes
        - "conceptual_confusion": Misunderstanding of concept
        - "formula_misuse": Wrong formula application
        - "unit_error": Unit conversion mistakes
        - "sign_error": Positive/negative mistakes
        - "reading_error": Misread the question
        """
        profile = await self.get_learning_profile(user_id)
        
        # Track mistake patterns
        if mistake_type not in profile.common_mistake_types:
            profile.common_mistake_types.append(mistake_type)
            # Keep only top 5 most recent
            profile.common_mistake_types = profile.common_mistake_types[-5:]
        
        # Update weak subjects
        if subject not in profile.weakest_subjects:
            profile.weakest_subjects.append(subject)
            profile.weakest_subjects = profile.weakest_subjects[-3:]
        
        await self._save_profile(profile)
    
    async def get_adaptation_recommendations(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get recommendations for adapting content to this student.
        
        Returns:
            Dict with recommendations for content adaptation
        """
        profile = await self.get_learning_profile(user_id)
        
        recommendations = {
            "primary_style": profile.primary_learning_style.value,
            "include_visuals": profile.visual_preference > 0.5,
            "include_examples": profile.example_preference > 0.5,
            "include_practice": profile.interactive_preference > 0.5,
            "explanation_depth": self._get_explanation_depth(profile),
            "use_metaphors": profile.preferred_metaphor_category,
            "use_hinglish": profile.prefers_hinglish,
            "optimal_length": profile.preferred_explanation_length,
            "watch_for_mistakes": profile.common_mistake_types[:3],
            "best_study_time": self._format_best_times(profile),
            "suggested_session_length": profile.optimal_session_duration
        }
        
        # Add personalized tips
        recommendations["tips"] = self._generate_tips(profile)
        
        return recommendations
    
    async def is_good_study_time(
        self,
        user_id: str
    ) -> Tuple[bool, str]:
        """Check if current time is good for this student to study"""
        profile = await self.get_learning_profile(user_id)
        now = datetime.now(timezone.utc)
        
        is_good_hour = now.hour in profile.best_hours
        is_good_day = now.weekday() in profile.best_days
        
        if is_good_hour and is_good_day:
            return True, "Great time to study! You usually perform well at this time."
        elif is_good_hour:
            return True, f"Good hour for you. Your best days are usually {self._format_days(profile.best_days)}."
        elif is_good_day:
            return True, f"Good day for studying. You're usually most focused around {self._format_hours(profile.best_hours)}."
        else:
            return False, f"Consider studying at {self._format_hours(profile.best_hours)} for better focus."
    
    def _update_preference(self, current: float, positive: bool) -> float:
        """Update a preference score with decay"""
        if positive:
            # Increase towards 1.0
            return min(1.0, current + 0.05)
        else:
            # Decrease towards 0.0
            return max(0.0, current - 0.02)
    
    def _get_explanation_depth(self, profile: LearningProfile) -> str:
        """Determine preferred explanation depth"""
        if profile.conceptual_preference > 0.7:
            return "deep"
        elif profile.example_preference > 0.7:
            return "example_heavy"
        elif profile.textual_preference < 0.3:
            return "concise"
        else:
            return "balanced"
    
    def _format_best_times(self, profile: LearningProfile) -> str:
        """Format best study times as readable string"""
        if not profile.best_hours:
            return "No clear pattern yet"
        
        hours = sorted(profile.best_hours)
        return ", ".join(f"{h}:00" for h in hours[:3])
    
    def _format_hours(self, hours: List[int]) -> str:
        """Format hours list"""
        if not hours:
            return "anytime"
        return ", ".join(f"{h}:00" for h in sorted(hours)[:3])
    
    def _format_days(self, days: List[int]) -> str:
        """Format days list"""
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return ", ".join(day_names[d] for d in sorted(days)[:3])
    
    def _generate_tips(self, profile: LearningProfile) -> List[str]:
        """Generate personalized learning tips"""
        tips = []
        
        if profile.visual_preference > 0.7:
            tips.append("You learn best with visuals - look for diagrams and animations!")
        
        if profile.interactive_preference > 0.7:
            tips.append("Practice problems help you learn - try solving before reading solutions.")
        
        if profile.avg_session_length < 15:
            tips.append("Try slightly longer study sessions (20-30 min) for deeper understanding.")
        
        if "calculation_error" in profile.common_mistake_types:
            tips.append("Double-check your calculations - this is a common slip for you.")
        
        if "conceptual_confusion" in profile.common_mistake_types:
            tips.append("Focus on understanding 'why' before 'how' - concepts over formulas.")
        
        return tips[:3]
    
    async def _save_profile(self, profile: LearningProfile) -> None:
        """Save profile to database"""
        if self.db is None:
            return
        
        try:
            await self.db.learning_profiles.update_one(
                {"user_id": profile.user_id},
                {"$set": self._serialize_profile(profile)},
                upsert=True
            )
        except Exception as e:
            logger.warning(f"Failed to save learning profile: {e}")
    
    def _serialize_profile(self, profile: LearningProfile) -> Dict:
        """Serialize profile for storage"""
        return {
            "user_id": profile.user_id,
            "visual_preference": profile.visual_preference,
            "textual_preference": profile.textual_preference,
            "interactive_preference": profile.interactive_preference,
            "example_preference": profile.example_preference,
            "conceptual_preference": profile.conceptual_preference,
            "best_hours": profile.best_hours,
            "best_days": profile.best_days,
            "optimal_session_duration": profile.optimal_session_duration,
            "avg_session_length": profile.avg_session_length,
            "avg_questions_per_session": profile.avg_questions_per_session,
            "common_mistake_types": profile.common_mistake_types,
            "preferred_explanation_length": profile.preferred_explanation_length,
            "prefers_hinglish": profile.prefers_hinglish,
            "preferred_metaphor_category": profile.preferred_metaphor_category,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def _deserialize_profile(self, data: Dict) -> LearningProfile:
        """Deserialize profile from storage"""
        return LearningProfile(
            user_id=data["user_id"],
            visual_preference=data.get("visual_preference", 0.5),
            textual_preference=data.get("textual_preference", 0.5),
            interactive_preference=data.get("interactive_preference", 0.5),
            example_preference=data.get("example_preference", 0.5),
            conceptual_preference=data.get("conceptual_preference", 0.5),
            best_hours=data.get("best_hours", [10, 11, 15, 16]),
            best_days=data.get("best_days", [0, 1, 2, 3, 4]),
            optimal_session_duration=data.get("optimal_session_duration", 30),
            avg_session_length=data.get("avg_session_length", 20.0),
            avg_questions_per_session=data.get("avg_questions_per_session", 5.0),
            common_mistake_types=data.get("common_mistake_types", []),
            preferred_explanation_length=data.get("preferred_explanation_length", "medium"),
            prefers_hinglish=data.get("prefers_hinglish", False),
            preferred_metaphor_category=data.get("preferred_metaphor_category", "cricket")
        )



