"""
🧠 MENTOR COMPANION - Intelligent Notification Agent
====================================================

This is NOT a notification system. This is a MENTOR COMPANION.

Core Philosophy:
- Every notification is an INTERRUPTION
- Every interruption must EARN its place
- The default is SILENCE, not noise
- The goal is to make the student feel UNDERSTOOD

Architecture:
1. Student State Engine → Unified understanding of student
2. Intent Reasoner → What does student NEED right now?
3. Interruption Gate → Should we interrupt? (Default: NO)
4. Tone Calibration → Match communication style to state
5. Message Composer → Context-aware, relationship-aware
6. Outcome Tracker → Learn from what works

Phase 3 - Event-Driven:
7. Event System → Trigger on meaningful moments, not time
8. Smart Events: session_end, inactivity, emotion_change, milestone

The student should feel:
"This understands me and has my back."
"""

import logging
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# 🎯 MENTOR COMPANION DATA STRUCTURES
# =============================================================================

# =============================================================================
# 🎯 PHASE 3: EVENT-DRIVEN SYSTEM
# =============================================================================

class MentorEvent(Enum):
    """
    Events that trigger mentor evaluation.
    Instead of polling every minute, we respond to meaningful moments.
    """
    # Study Events
    SESSION_STARTED = "session_started"       # Student began studying
    SESSION_ENDED = "session_ended"           # Student stopped studying (5+ min inactive)
    LONG_SESSION = "long_session"             # Student studied for 90+ minutes
    
    # Engagement Events
    INACTIVITY_DETECTED = "inactivity"        # No activity for extended period
    COMEBACK = "comeback"                     # Student returned after absence
    
    # Emotional Events
    FRUSTRATION_DETECTED = "frustration"      # Student showing frustration signals
    CONFUSION_DETECTED = "confusion"          # Student seems confused
    CONFIDENCE_BOOST = "confidence"           # Student doing well
    
    # Achievement Events
    STREAK_MILESTONE = "streak_milestone"     # Hit a streak milestone
    TOPIC_MASTERED = "topic_mastered"         # Mastered a topic
    GOAL_PROGRESS = "goal_progress"           # Made progress on goal
    
    # Urgency Events
    STREAK_AT_RISK = "streak_at_risk"         # Streak about to break
    EXAM_APPROACHING = "exam_approaching"     # Exam is imminent
    REVIEW_OVERDUE = "review_overdue"         # Spaced rep reviews overdue


@dataclass
class MentorEventData:
    """
    Data associated with a mentor event.
    Contains context needed to make intelligent decisions.
    """
    event_type: MentorEvent
    user_id: str
    timestamp: datetime
    
    # Context (varies by event type)
    topic: Optional[str] = None
    session_duration_minutes: Optional[int] = None
    inactivity_hours: Optional[float] = None
    emotional_signals: Optional[List[str]] = None
    streak_days: Optional[int] = None
    days_to_exam: Optional[int] = None
    
    # Source
    source: str = "system"  # "chat", "session", "scheduler", "system"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "topic": self.topic,
            "session_duration_minutes": self.session_duration_minutes,
            "inactivity_hours": self.inactivity_hours,
            "emotional_signals": self.emotional_signals,
            "streak_days": self.streak_days,
            "days_to_exam": self.days_to_exam,
            "source": self.source
        }


class MentorIntent(Enum):
    """
    What does the student NEED right now?
    Ordered by priority - HELP is most important, SILENCE is most common.
    """
    HELP = "help"           # Student is stuck, confused, needs support
    PROTECT = "protect"     # Something valuable at risk (streak, commitment)
    CELEBRATE = "celebrate" # Achievement deserves acknowledgment
    GUIDE = "guide"         # Helpful direction available (review, next step)
    SILENCE = "silence"     # Best response is NO response (most common)


class StudentMomentum(Enum):
    """Learning momentum state"""
    BUILDING = "building"   # On a roll, improving
    STABLE = "stable"       # Consistent, maintaining
    DECLINING = "declining" # Slowing down, losing steam
    STALLED = "stalled"     # Inactive, needs re-engagement


class CognitiveLoad(Enum):
    """Current mental state"""
    FRESH = "fresh"         # Ready to learn, low fatigue
    MODERATE = "moderate"   # Working but not overloaded
    FATIGUED = "fatigued"   # Needs rest, long session


class EmotionalState(Enum):
    """Detected emotional state"""
    CONFIDENT = "confident"     # Doing well, positive
    NEUTRAL = "neutral"         # Normal, no strong signals
    STRUGGLING = "struggling"   # Finding it difficult
    FRUSTRATED = "frustrated"   # Showing frustration signals
    ANXIOUS = "anxious"         # Worried, stressed


@dataclass
class StudentState:
    """
    Unified snapshot of student's current state.
    This is the SINGLE SOURCE OF TRUTH for mentor decisions.
    """
    user_id: str
    name: str
    
    # Cognitive State
    cognitive_load: CognitiveLoad
    currently_studying: bool
    minutes_since_last_activity: int
    study_minutes_today: int
    
    # Emotional State
    emotional_state: EmotionalState
    emotional_confidence: float  # 0.0-1.0, how sure are we about emotional state
    
    # Learning Momentum
    streak_days: int
    momentum: StudentMomentum
    consistency_score: float  # 0.0-1.0, recent pattern regularity
    
    # Notification Receptiveness
    notifications_ignored_recently: int  # Last 48 hours
    hours_since_last_notification: float
    notification_response_rate: float  # Historical engagement rate
    
    # Context
    last_topic: str
    days_to_exam: Optional[int]
    weak_topics: List[str]
    due_reviews: List[str]
    
    # Computed Flags
    is_receptive: bool  # Computed: likely to respond positively
    needs_space: bool   # Computed: should we back off?


# =============================================================================
# 🎓 PHASE 2: LEARNING PROFILE - What works for each student
# =============================================================================

@dataclass
class StudentLearningProfile:
    """
    What the Mentor has LEARNED about this student's notification preferences.
    
    This is built over time from outcome data and used to personalize:
    - Frequency (how often to reach out)
    - Timing (when they're most receptive)
    - Tone (what style resonates)
    - Intent priorities (what matters to them)
    """
    user_id: str
    
    # Engagement Metrics (0.0 to 1.0)
    overall_engagement_rate: float = 0.5      # % of notifications that got positive response
    study_conversion_rate: float = 0.3        # % that led to actual studying
    
    # Frequency Preference
    preferred_frequency: str = "moderate"     # "low" | "moderate" | "high"
    max_daily_notifications: int = 3          # Learned optimal cap
    min_hours_between: float = 3.0            # Learned minimum gap
    
    # Timing Intelligence
    best_hour_of_day: Optional[int] = None    # Hour with highest engagement (0-23)
    worst_hour_of_day: Optional[int] = None   # Hour to avoid
    active_days: List[str] = field(default_factory=list)  # Days they're most active
    
    # Tone Preference
    preferred_tone: str = "warm"              # "warm" | "encouraging" | "direct" | "gentle"
    responds_to_urgency: bool = True          # Do urgent messages work?
    responds_to_celebration: bool = True      # Do they like being celebrated?
    
    # Intent Effectiveness (which intents work best, 0.0 to 1.0)
    help_effectiveness: float = 0.7
    protect_effectiveness: float = 0.5
    celebrate_effectiveness: float = 0.6
    guide_effectiveness: float = 0.4
    
    # Backoff Learning
    consecutive_ignores: int = 0              # Current ignore streak
    backoff_until: Optional[datetime] = None  # If in backoff, until when
    
    # Meta
    last_updated: Optional[datetime] = None
    total_notifications_analyzed: int = 0


@dataclass
class MentorDecision:
    """
    The output of the mentor's decision process.
    Every decision is logged and tracked for learning.
    """
    action: str  # "NOTIFY" | "WAIT" | "BACKOFF"
    intent: MentorIntent
    approved: bool
    reason: str
    
    # If approved
    tone: Optional[str] = None  # "warm" | "encouraging" | "calm" | "celebratory"
    message: Optional[Dict[str, str]] = None  # {"title": ..., "message": ...}
    
    # For learning
    confidence: float = 0.5  # How confident are we in this decision?
    retry_after_minutes: Optional[int] = None  # When to check again
    
    def to_log_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "intent": self.intent.value,
            "approved": self.approved,
            "reason": self.reason,
            "tone": self.tone,
            "confidence": self.confidence
        }

# Import LLM service for intelligent message generation
try:
    from services.llm_service import call_gemini
    from core.config import settings
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    settings = None
    logger.warning("LLM service not available for intelligent nudges")

# 🆕 Spaced Repetition Integration
try:
    from .spaced_repetition import SpacedRepetitionEngine
    SPACED_REPETITION_AVAILABLE = True
except ImportError:
    SPACED_REPETITION_AVAILABLE = False
    logger.warning("SpacedRepetitionEngine not available for revision nudges")

# IST offset
IST_OFFSET = timedelta(hours=5, minutes=30)


class NudgeType(Enum):
    """Types of proactive nudges"""
    STREAK_PROTECTION = "streak_protection"
    CONTINUE_LEARNING = "continue_learning"
    REVISION_DUE = "revision_due"
    EXAM_COUNTDOWN = "exam_countdown"
    WEAK_TOPIC_FOCUS = "weak_topic_focus"
    BREAK_SUGGESTION = "break_suggestion"
    MOTIVATION = "motivation"
    DAILY_SUMMARY = "daily_summary"
    # Added for proactive_scheduler compatibility
    COMEBACK = "comeback"
    MORNING_GREETING = "morning_greeting"
    SPACED_REP = "spaced_rep"  # Alias for REVISION_DUE in scheduler context


@dataclass
class ProactiveNudge:
    """A proactive nudge to send to student"""
    nudge_type: NudgeType
    title: str
    message: str
    priority: str  # high, medium, low
    actions: List[Dict[str, str]]  # Button actions
    data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.nudge_type.value,
            'title': self.title,
            'message': self.message,
            'priority': self.priority,
            'actions': self.actions,
            'data': self.data
        }


class IntelligentProactiveMentor:
    """
    🧠 MENTOR COMPANION - The brain behind intelligent, caring outreach.
    
    This is NOT a notification scheduler.
    This is a mentor that THINKS before reaching out.
    
    Core Question: "What does this student NEED from me right now?"
    Default Answer: "Nothing. Silence is respect."
    """
    
    # Streak milestones for celebrations
    STREAK_MILESTONES = [3, 7, 14, 21, 30, 50, 100]
    
    # Hours of inactivity before concern
    INACTIVITY_THRESHOLD_HOURS = 20
    
    # Study session length before suggesting break (minutes)
    STUDY_SESSION_MAX_MINUTES = 90
    
    # Interruption gate thresholds
    MIN_HOURS_BETWEEN_NOTIFICATIONS = 3
    MAX_IGNORED_BEFORE_BACKOFF = 3
    BACKOFF_HOURS = 24
    
    def __init__(self, db_client):
        self.db = db_client
    
    # ==========================================================================
    # 🎯 LAYER 1: STUDENT STATE ENGINE
    # ==========================================================================
    
    async def compute_student_state(self, user_id: str) -> StudentState:
        """
        Compute a unified snapshot of the student's current state.
        This is the SINGLE SOURCE OF TRUTH for all mentor decisions.
        
        Combines:
        - Activity patterns (cognitive load, studying status)
        - Emotional signals (from chat, performance)
        - Learning momentum (streak, consistency)
        - Notification history (receptiveness)
        - Context (topics, exams, weak areas)
        """
        now = datetime.now(timezone.utc)
        
        # Default state (safe fallback)
        state = StudentState(
            user_id=user_id,
            name="",
            cognitive_load=CognitiveLoad.FRESH,
            currently_studying=False,
            minutes_since_last_activity=9999,
            study_minutes_today=0,
            emotional_state=EmotionalState.NEUTRAL,
            emotional_confidence=0.3,
            streak_days=0,
            momentum=StudentMomentum.STABLE,
            consistency_score=0.5,
            notifications_ignored_recently=0,
            hours_since_last_notification=9999,
            notification_response_rate=0.5,
            last_topic="",
            days_to_exam=None,
            weak_topics=[],
            due_reviews=[],
            is_receptive=True,
            needs_space=False
        )
        
        if self.db is None:
            return state
        
        try:
            # ===== USER PROFILE =====
            user = await self.db.users.find_one({"user_id": user_id})
            if user:
                state.name = (user.get("full_name") or user.get("name") or "").split()[0]
                state.streak_days = user.get("streak", 0)
                
                if user.get("exam_date"):
                    exam_date = user["exam_date"]
                    if isinstance(exam_date, str):
                        exam_date = datetime.fromisoformat(exam_date.replace('Z', '+00:00'))
                    state.days_to_exam = max(0, (exam_date - now).days)
            
            # ===== ACTIVITY ANALYSIS =====
            # Recent activity check (last 5 minutes = currently studying)
            five_mins_ago = now - timedelta(minutes=5)
            recent_activity = await self.db.chat_messages.find_one({
                "user_id": user_id,
                "timestamp": {"$gte": five_mins_ago}
            })
            state.currently_studying = recent_activity is not None
            
            # Last activity time
            last_message = await self.db.chat_messages.find_one(
                {"user_id": user_id},
                sort=[("timestamp", -1)]
            )
            if last_message and last_message.get("timestamp"):
                last_time = last_message["timestamp"]
                if isinstance(last_time, str):
                    last_time = datetime.fromisoformat(last_time.replace('Z', '+00:00'))
                if last_time.tzinfo is None:
                    last_time = last_time.replace(tzinfo=timezone.utc)
                state.minutes_since_last_activity = int((now - last_time).total_seconds() / 60)
            
            # Today's study time
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_messages = await self.db.chat_messages.count_documents({
                "user_id": user_id,
                "timestamp": {"$gte": today_start},
                "role": "user"
            })
            state.study_minutes_today = today_messages * 2  # Rough estimate
            
            # ===== COGNITIVE LOAD =====
            # Check if in long session (last 2 hours)
            two_hours_ago = now - timedelta(hours=2)
            session_messages = await self.db.chat_messages.count_documents({
                "user_id": user_id,
                "timestamp": {"$gte": two_hours_ago},
                "role": "user"
            })
            
            if session_messages > 30:
                state.cognitive_load = CognitiveLoad.FATIGUED
            elif session_messages > 15:
                state.cognitive_load = CognitiveLoad.MODERATE
            else:
                state.cognitive_load = CognitiveLoad.FRESH
            
            # ===== EMOTIONAL STATE =====
            emotional_result = await self.get_emotional_state(user_id)
            state.emotional_state = EmotionalState(emotional_result.get("state", "neutral"))
            state.emotional_confidence = emotional_result.get("confidence", 0.5)
            
            # ===== MOMENTUM =====
            state.momentum = await self._compute_momentum(user_id)
            state.consistency_score = await self._compute_consistency(user_id)
            
            # ===== NOTIFICATION HISTORY =====
            forty_eight_hours_ago = now - timedelta(hours=48)
            
            # Count ignored notifications
            sent_notifications = await self.db.user_notifications.count_documents({
                "user_id": user_id,
                "created_at": {"$gte": forty_eight_hours_ago}
            })
            
            engaged_notifications = await self.db.notification_outcomes.count_documents({
                "user_id": user_id,
                "created_at": {"$gte": forty_eight_hours_ago},
                "outcome": {"$in": ["clicked", "studied", "engaged"]}
            })
            
            state.notifications_ignored_recently = max(0, sent_notifications - engaged_notifications)
            
            # Last notification time
            last_notification = await self.db.user_notifications.find_one(
                {"user_id": user_id},
                sort=[("created_at", -1)]
            )
            if last_notification and last_notification.get("created_at"):
                last_notif_time = last_notification["created_at"]
                if last_notif_time.tzinfo is None:
                    last_notif_time = last_notif_time.replace(tzinfo=timezone.utc)
                state.hours_since_last_notification = (now - last_notif_time).total_seconds() / 3600
            
            # Response rate (historical)
            total_sent = await self.db.user_notifications.count_documents({"user_id": user_id})
            total_engaged = await self.db.notification_outcomes.count_documents({
                "user_id": user_id,
                "outcome": {"$in": ["clicked", "studied", "engaged"]}
            })
            if total_sent > 0:
                state.notification_response_rate = total_engaged / total_sent
            
            # ===== CONTEXT =====
            recent_session = await self.db.chat_sessions.find_one(
                {"user_id": user_id},
                sort=[("updated_at", -1)]
            )
            if recent_session:
                state.last_topic = recent_session.get("topic", recent_session.get("title", ""))
            
            # Weak topics
            learning_profile = await self.db.learning_profiles.find_one({"user_id": user_id})
            if learning_profile:
                state.weak_topics = learning_profile.get("weak_topics", [])[:3]
            
            # Due reviews
            due_reviews = await self.db.sr_items.find({
                "user_id": user_id,
                "next_review": {"$lte": now}
            }).limit(5).to_list(length=5)
            state.due_reviews = [r.get("topic", "") for r in due_reviews if r.get("topic")]
            
            # ===== COMPUTED FLAGS =====
            state.is_receptive = (
                state.notification_response_rate > 0.3 and
                state.notifications_ignored_recently < self.MAX_IGNORED_BEFORE_BACKOFF and
                not state.currently_studying
            )
            
            state.needs_space = (
                state.notifications_ignored_recently >= self.MAX_IGNORED_BEFORE_BACKOFF or
                (state.emotional_state == EmotionalState.FRUSTRATED and
                 state.emotional_confidence > 0.6)
            )
            
        except Exception as e:
            logger.error(f"Error computing student state for {user_id}: {e}")
        
        return state
    
    async def _compute_momentum(self, user_id: str) -> StudentMomentum:
        """Compute learning momentum from recent activity patterns."""
        if self.db is None:
            return StudentMomentum.STABLE
        
        now = datetime.now(timezone.utc)
        
        try:
            # Get activity for last 7 days
            days_with_activity = 0
            for i in range(7):
                day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0)
                day_end = day_start + timedelta(days=1)
                
                activity = await self.db.chat_messages.find_one({
                    "user_id": user_id,
                    "timestamp": {"$gte": day_start, "$lt": day_end}
                })
                if activity:
                    days_with_activity += 1
            
            # Momentum based on recent activity density
            if days_with_activity >= 5:
                return StudentMomentum.BUILDING
            elif days_with_activity >= 3:
                return StudentMomentum.STABLE
            elif days_with_activity >= 1:
                return StudentMomentum.DECLINING
            else:
                return StudentMomentum.STALLED
                
        except Exception as e:
            logger.warning(f"Error computing momentum: {e}")
            return StudentMomentum.STABLE
    
    async def _compute_consistency(self, user_id: str) -> float:
        """Compute consistency score (0-1) based on study patterns."""
        if self.db is None:
            return 0.5
        
        now = datetime.now(timezone.utc)
        
        try:
            # Check last 14 days
            active_days = 0
            for i in range(14):
                day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0)
                day_end = day_start + timedelta(days=1)
                
                activity = await self.db.chat_messages.find_one({
                    "user_id": user_id,
                    "timestamp": {"$gte": day_start, "$lt": day_end}
                })
                if activity:
                    active_days += 1
            
            return active_days / 14.0
            
        except Exception as e:
            logger.warning(f"Error computing consistency: {e}")
            return 0.5
    
    # ==========================================================================
    # 🎯 LAYER 2: INTENT REASONER
    # ==========================================================================
    
    async def reason_about_intent(self, state: StudentState) -> MentorIntent:
        """
        Determine what the student actually NEEDS right now.
        
        This is NOT "what notification should we send?"
        This is "does this student need anything from me?"
        
        Intent Priority (highest to lowest):
        1. HELP - Student showing distress signals
        2. PROTECT - Something valuable at risk
        3. CELEBRATE - Achievement deserves recognition
        4. GUIDE - Helpful direction available
        5. SILENCE - Default, most common outcome
        """
        
        # ===== HELP: Student showing distress signals =====
        if state.emotional_state in [EmotionalState.FRUSTRATED, EmotionalState.STRUGGLING]:
            if state.emotional_confidence > 0.5:
                logger.info(f"🆘 Intent: HELP - Student {state.user_id} showing {state.emotional_state.value}")
                return MentorIntent.HELP
        
        # ===== PROTECT: Something valuable at risk =====
        # Streak at risk (meaningful streak, inactive today)
        if state.streak_days >= 3:
            if state.minutes_since_last_activity > 60 * 18:  # 18+ hours inactive
                if state.study_minutes_today == 0:  # No activity today
                    logger.info(f"🛡️ Intent: PROTECT - Streak ({state.streak_days} days) at risk")
                    return MentorIntent.PROTECT
        
        # Exam imminent and not studying enough
        if state.days_to_exam is not None and state.days_to_exam <= 7:
            if state.study_minutes_today < 30 and state.minutes_since_last_activity > 60 * 8:
                logger.info(f"🛡️ Intent: PROTECT - Exam in {state.days_to_exam} days, low activity")
                return MentorIntent.PROTECT
        
        # ===== CELEBRATE: Achievement deserves recognition =====
        # Milestone streak (only if we haven't celebrated recently)
        if state.streak_days in self.STREAK_MILESTONES:
            logger.info(f"🎉 Intent: CELEBRATE - Streak milestone: {state.streak_days} days")
            return MentorIntent.CELEBRATE
        
        # ===== GUIDE: Helpful direction available =====
        # Due reviews, but only if student seems receptive
        if len(state.due_reviews) >= 3 and state.is_receptive:
            if state.momentum in [StudentMomentum.BUILDING, StudentMomentum.STABLE]:
                logger.info(f"📚 Intent: GUIDE - {len(state.due_reviews)} reviews due")
                return MentorIntent.GUIDE
        
        # ===== DEFAULT: SILENCE =====
        logger.debug(f"🤫 Intent: SILENCE - No intervention needed for {state.user_id}")
        return MentorIntent.SILENCE
    
    # ==========================================================================
    # 🎯 LAYER 3: INTERRUPTION GATE
    # ==========================================================================
    
    async def check_interruption_gate(
        self,
        state: StudentState,
        intent: MentorIntent
    ) -> Tuple[bool, str]:
        """
        Should we actually interrupt this student?
        
        Default answer is NO.
        Every notification must earn its place.
        
        Returns: (approved: bool, reason: str)
        """
        
        # ===== RULE 0: SILENCE intent = always NO =====
        if intent == MentorIntent.SILENCE:
            return False, "Intent is SILENCE - no intervention needed"
        
        # ===== RULE 1: Never interrupt active study =====
        if state.currently_studying:
            return False, "Student is currently studying - don't break flow"
        
        # ===== RULE 2: Respect cooldowns (except HELP) =====
        if intent != MentorIntent.HELP:
            if state.hours_since_last_notification < self.MIN_HOURS_BETWEEN_NOTIFICATIONS:
                return False, f"Too soon since last notification ({state.hours_since_last_notification:.1f}h < {self.MIN_HOURS_BETWEEN_NOTIFICATIONS}h)"
        
        # ===== RULE 3: Back off if being ignored =====
        if state.needs_space:
            if intent != MentorIntent.HELP:
                return False, f"Student has ignored {state.notifications_ignored_recently} recent notifications - backing off"
        
        # ===== RULE 4: Protect emotional safety =====
        if state.emotional_state == EmotionalState.ANXIOUS:
            if intent == MentorIntent.PROTECT:
                return False, "Student is anxious - PROTECT would add pressure"
        
        if state.emotional_state == EmotionalState.FRUSTRATED:
            if intent in [MentorIntent.GUIDE, MentorIntent.PROTECT]:
                return False, "Student is frustrated - only HELP or CELEBRATE allowed"
        
        # ===== RULE 5: Value vs Cost calculation =====
        value = self._compute_notification_value(intent, state)
        cost = self._compute_interruption_cost(state)
        
        if value < cost:
            return False, f"Value ({value:.2f}) doesn't justify interruption cost ({cost:.2f})"
        
        # ===== APPROVED =====
        return True, f"Approved: Intent={intent.value}, Value={value:.2f} > Cost={cost:.2f}"
    
    def _compute_notification_value(self, intent: MentorIntent, state: StudentState) -> float:
        """
        Compute the value of this notification (0-1).
        Higher = more valuable to send.
        """
        base_values = {
            MentorIntent.HELP: 0.9,       # Helping struggling student is always valuable
            MentorIntent.PROTECT: 0.7,    # Protecting achievements is valuable
            MentorIntent.CELEBRATE: 0.6,  # Recognition is nice but not urgent
            MentorIntent.GUIDE: 0.4,      # Guidance is helpful but interruptible
            MentorIntent.SILENCE: 0.0     # No value in silence notification
        }
        
        value = base_values.get(intent, 0.3)
        
        # Boost value if exam is imminent
        if state.days_to_exam is not None and state.days_to_exam <= 7:
            value = min(1.0, value + 0.2)
        
        # Boost value if high receptiveness
        if state.notification_response_rate > 0.6:
            value = min(1.0, value + 0.1)
        
        # Reduce value if student needs space
        if state.needs_space:
            value *= 0.5
        
        return value
    
    def _compute_interruption_cost(self, state: StudentState) -> float:
        """
        Compute the cost of interrupting (0-1).
        Higher = more costly to interrupt.
        """
        cost = 0.3  # Base cost - interruptions always have some cost
        
        # Higher cost if cognitively loaded
        if state.cognitive_load == CognitiveLoad.FATIGUED:
            cost += 0.2
        elif state.cognitive_load == CognitiveLoad.MODERATE:
            cost += 0.1
        
        # Higher cost if emotionally sensitive
        if state.emotional_state in [EmotionalState.ANXIOUS, EmotionalState.FRUSTRATED]:
            cost += 0.3
        elif state.emotional_state == EmotionalState.STRUGGLING:
            cost += 0.1
        
        # Higher cost if recently notified
        if state.hours_since_last_notification < 6:
            cost += 0.2
        
        # Higher cost if ignoring notifications
        if state.notifications_ignored_recently > 0:
            cost += 0.1 * state.notifications_ignored_recently
        
        return min(1.0, cost)
    
    # ==========================================================================
    # 🎯 LAYER 4: TONE CALIBRATION
    # ==========================================================================
    
    def calibrate_tone(self, state: StudentState, intent: MentorIntent) -> str:
        """
        Calibrate communication tone based on student state and intent.
        
        Returns: "warm" | "encouraging" | "calm" | "celebratory" | "supportive"
        """
        # Emotional state takes priority
        if state.emotional_state == EmotionalState.FRUSTRATED:
            return "supportive"  # Warm, non-judgmental
        
        if state.emotional_state == EmotionalState.ANXIOUS:
            return "calm"  # Reassuring, practical
        
        if state.emotional_state == EmotionalState.STRUGGLING:
            return "warm"  # Patient, encouraging
        
        # Intent-based tone
        if intent == MentorIntent.HELP:
            return "supportive"
        
        if intent == MentorIntent.CELEBRATE:
            return "celebratory"
        
        if intent == MentorIntent.PROTECT:
            if state.streak_days > 7:
                return "encouraging"  # You've built something great
            return "warm"  # Gentle reminder
        
        if intent == MentorIntent.GUIDE:
            if state.momentum == StudentMomentum.BUILDING:
                return "encouraging"  # Keep the momentum
            return "warm"
        
        return "warm"  # Default
    
    # ==========================================================================
    # 🎯 MASTER DECISION FUNCTION
    # ==========================================================================
    
    async def make_mentor_decision(self, user_id: str) -> MentorDecision:
        """
        The MAIN entry point for the Mentor Companion.
        
        This function answers: "Should I reach out to this student right now?"
        
        Returns a MentorDecision with:
        - action: "NOTIFY" | "WAIT" | "BACKOFF"
        - All context needed to send or not send
        """
        
        # LAYER 1: Compute student state
        state = await self.compute_student_state(user_id)
        logger.info(f"🧠 Student State: {user_id} | emotional={state.emotional_state.value} | momentum={state.momentum.value} | studying={state.currently_studying}")
        
        # LAYER 2: Reason about intent
        intent = await self.reason_about_intent(state)
        
        # LAYER 3: Check interruption gate
        approved, reason = await self.check_interruption_gate(state, intent)
        
        if not approved:
            logger.info(f"🚫 Gate DENIED for {user_id}: {reason}")
            
            # Determine if this is a temporary wait or backoff
            action = "BACKOFF" if state.needs_space else "WAIT"
            retry_after = self.BACKOFF_HOURS * 60 if action == "BACKOFF" else 60
            
            return MentorDecision(
                action=action,
                intent=intent,
                approved=False,
                reason=reason,
                retry_after_minutes=retry_after
            )
        
        # LAYER 4: Calibrate tone
        tone = self.calibrate_tone(state, intent)
        
        # LAYER 5: Compose message
        student_context = await self._get_student_intelligence(user_id)
        student_context["emotional_state"] = state.emotional_state.value
        student_context["momentum"] = state.momentum.value
        student_context["tone"] = tone
        
        message = await self._generate_mentor_message(
            intent=intent,
            tone=tone,
            student_context=student_context,
            state=state
        )
        
        logger.info(f"✅ Mentor APPROVED for {user_id}: intent={intent.value}, tone={tone}")
        
        return MentorDecision(
            action="NOTIFY",
            intent=intent,
            approved=True,
            reason=reason,
            tone=tone,
            message=message,
            confidence=0.7 if state.emotional_confidence > 0.5 else 0.5
        )
    
    async def _generate_mentor_message(
        self,
        intent: MentorIntent,
        tone: str,
        student_context: Dict[str, Any],
        state: StudentState
    ) -> Dict[str, str]:
        """
        Generate a message that feels like a real mentor, not a bot.
        
        Key requirements:
        - Reference REAL context (specific topic, specific streak, specific situation)
        - Match the calibrated tone
        - Never repeat recent messages
        - Never leak internal metadata
        """
        if not LLM_AVAILABLE or not settings:
            return self._get_mentor_fallback_message(intent, tone, state)
        
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key:
            return self._get_mentor_fallback_message(intent, tone, state)
        
        # Build context-aware prompt
        name = student_context.get("name") or "there"
        streak = state.streak_days
        last_topic = state.last_topic or "your studies"
        days_to_exam = state.days_to_exam
        weak_topics = state.weak_topics[:2] if state.weak_topics else []
        due_reviews = state.due_reviews[:2] if state.due_reviews else []
        
        # Intent-specific context
        intent_context = {
            MentorIntent.HELP: "The student seems to be struggling or frustrated. Offer support without being pushy.",
            MentorIntent.PROTECT: f"The student has a {streak}-day streak that's at risk. Gently encourage without guilt-tripping.",
            MentorIntent.CELEBRATE: f"Celebrate the student's {streak}-day streak milestone! Be genuinely happy for them.",
            MentorIntent.GUIDE: f"There are {len(due_reviews)} topics due for review. Suggest lightly, don't push."
        }
        
        tone_instructions = {
            "warm": "Be like a caring older sibling - gentle, understanding, patient.",
            "supportive": "Be extra gentle - the student is having a tough time. No pressure.",
            "calm": "Be reassuring and practical. Help them feel less anxious.",
            "celebratory": "Be genuinely excited! This is an achievement worth recognizing.",
            "encouraging": "Be motivating but not pushy. Acknowledge their hard work."
        }
        
        prompt = f"""You are Sathi, a mentor who genuinely cares about this student.
Generate a SHORT notification (2 sentences max) that feels like a real friend checking in.

STUDENT:
- Name: {name}
- Last studied: {last_topic}
- Streak: {streak} days
{f"- Exam in: {days_to_exam} days" if days_to_exam else ""}
{f"- Weak areas: {', '.join(weak_topics)}" if weak_topics else ""}
{f"- Topics to review: {', '.join(due_reviews)}" if due_reviews else ""}
- Current emotional state: {state.emotional_state.value}
- Learning momentum: {state.momentum.value}

INTENT: {intent.value}
{intent_context.get(intent, "")}

TONE: {tone}
{tone_instructions.get(tone, "Be warm and friendly.")}

CRITICAL RULES:
1. Reference SPECIFIC context (actual topic names, actual streak number)
2. Sound like a FRIEND, not a system
3. Max 2 sentences
4. One emoji max, at start or end
5. Include a soft, optional action (not demanding)
6. NEVER say things like "general_concept" or expose internal data
7. If you can't make it personal, don't send anything generic

OUTPUT FORMAT (JSON only):
{{"title": "short title", "message": "personalized message"}}

Generate:"""

        try:
            response = await asyncio.wait_for(
                call_gemini(
                    prompt=prompt,
                    api_key=api_key,
                    temperature=0.7,
                    max_tokens=150,
                    model="gemini-2.0-flash",
                    system_message="You write notifications that feel human. Output only valid JSON."
                ),
                timeout=5.0
            )
            
            import json
            import re
            
            # Extract JSON
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                result = json.loads(json_match.group())
                if "title" in result and "message" in result:
                    # Sanitize - remove any internal metadata leaks
                    result["title"] = self._sanitize_message(result["title"])
                    result["message"] = self._sanitize_message(result["message"])
                    logger.info(f"✅ Mentor message generated for {intent.value}")
                    return result
            
            logger.warning(f"Invalid LLM response for mentor message: {response[:100]}")
            
        except asyncio.TimeoutError:
            logger.warning("Mentor message generation timed out")
        except Exception as e:
            logger.warning(f"Mentor message generation failed: {e}")
        
        return self._get_mentor_fallback_message(intent, tone, state)
    
    def _sanitize_message(self, text: str) -> str:
        """Remove any internal metadata that might leak into messages."""
        if not text:
            return text
        
        # Remove common internal patterns
        import re
        
        # Remove patterns like "general_concept (general)"
        text = re.sub(r'\w+_\w+\s*\([^)]+\)', '', text)
        # Remove patterns like "topic_id: xxx"
        text = re.sub(r'\w+_id:\s*\w+', '', text)
        # Remove double spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _get_mentor_fallback_message(
        self,
        intent: MentorIntent,
        tone: str,
        state: StudentState
    ) -> Dict[str, str]:
        """
        Fallback messages when LLM is unavailable.
        Still personalized, still respectful of tone.
        """
        name = state.name or "there"
        streak = state.streak_days
        topic = state.last_topic or "your studies"
        
        messages = {
            (MentorIntent.HELP, "supportive"): {
                "title": "💙 Here if you need me",
                "message": f"Hey {name}, I noticed you might be working through something tricky. No pressure, but I'm here if you want to talk it through."
            },
            (MentorIntent.HELP, "warm"): {
                "title": "💭 Need a hand?",
                "message": f"{name}, sometimes a fresh perspective helps. Want to tackle this together?"
            },
            (MentorIntent.PROTECT, "warm"): {
                "title": f"🔥 {streak} days strong",
                "message": f"Hey {name}, your streak is still going! Even 5 minutes on {topic} keeps the momentum."
            },
            (MentorIntent.PROTECT, "encouraging"): {
                "title": f"💪 Day {streak} waiting",
                "message": f"{name}, you've built something great. A quick session keeps it alive!"
            },
            (MentorIntent.CELEBRATE, "celebratory"): {
                "title": f"🎉 {streak} days!",
                "message": f"Wow {name}! {streak} days of consistency is incredible. You should be proud!"
            },
            (MentorIntent.GUIDE, "warm"): {
                "title": "📚 Quick review?",
                "message": f"Hey {name}, a few topics are ready for review. No rush - whenever you're ready."
            },
            (MentorIntent.GUIDE, "encouraging"): {
                "title": "🚀 Keep the momentum",
                "message": f"{name}, you're on a roll! A quick review would lock in what you've learned."
            }
        }
        
        # Get message or use generic
        key = (intent, tone)
        if key in messages:
            return messages[key]
        
        # Generic fallback
        return {
            "title": "👋 Hey there",
            "message": f"Hi {name}, just checking in. I'm here when you need me."
        }
    
    # ========================================
    # 🧠 INTELLIGENT NUDGE GENERATION (Phase 1)
    # ========================================
    
    async def _get_student_intelligence(self, user_id: str) -> Dict[str, Any]:
        """
        Fetch comprehensive student context for intelligent nudge generation.
        Combines Error Genome™, exam urgency, mastery, and learning patterns.
        """
        context = {
            "name": "",
            "days_to_exam": None,
            "exam_name": "exam",
            "current_streak": 0,
            "weak_topics": [],
            "mastery_levels": {},
            "common_mistakes": [],
            "recent_topic": "",
            "due_reviews": [],
            "total_questions_today": 0,
            "accuracy_today": 0
        }
        
        if self.db is None:
            return context
        
        try:
            # Get user profile
            user = await self.db.users.find_one({"user_id": user_id})
            if user:
                context["name"] = (user.get("full_name") or user.get("name") or "").split()[0]
                context["current_streak"] = user.get("streak", 0)
                
                # Exam info
                if user.get("exam_date"):
                    exam_date = user["exam_date"]
                    if isinstance(exam_date, str):
                        exam_date = datetime.fromisoformat(exam_date.replace('Z', '+00:00'))
                    context["days_to_exam"] = max(0, (exam_date - datetime.now(timezone.utc)).days)
                    context["exam_name"] = user.get("exam_type", "exam")
            
            # Get learning profile for Error Genome™
            learning_profile = await self.db.learning_profiles.find_one({"user_id": user_id})
            if learning_profile:
                context["weak_topics"] = learning_profile.get("weak_topics", [])[:3]
                context["common_mistakes"] = learning_profile.get("common_mistake_types", [])[:3]
                context["mastery_levels"] = learning_profile.get("topic_mastery", {})
            
            # Get recent session
            recent_session = await self.db.chat_sessions.find_one(
                {"user_id": user_id},
                sort=[("updated_at", -1)]
            )
            if recent_session:
                context["recent_topic"] = recent_session.get("topic", recent_session.get("title", ""))
            
            # Get due reviews (spaced repetition)
            now = datetime.now(timezone.utc)
            due_reviews = await self.db.sr_items.find({
                "user_id": user_id,
                "next_review": {"$lte": now}
            }).limit(3).to_list(length=3)
            context["due_reviews"] = [r.get("topic", "") for r in due_reviews]
            
            # Get today's activity
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_messages = await self.db.chat_messages.count_documents({
                "user_id": user_id,
                "timestamp": {"$gte": today_start},
                "role": "user"
            })
            context["total_questions_today"] = today_messages
            
        except Exception as e:
            logger.warning(f"Failed to get student intelligence: {e}")
        
        return context
    
    async def _generate_intelligent_message(
        self,
        nudge_type: str,
        student_context: Dict[str, Any],
        base_context: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """
        Generate intelligent, personalized nudge content using LLM.
        Returns {"title": ..., "message": ...}
        
        This is what makes nudges feel like a real mentor, not templates.
        """
        if not LLM_AVAILABLE or not settings:
            return self._get_fallback_message(nudge_type, student_context, base_context)
        
        # Check if API key is available
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key:
            logger.warning("No Gemini API key configured - using fallback messages")
            return self._get_fallback_message(nudge_type, student_context, base_context)
        
        # Build context string for LLM
        name = student_context.get("name") or "there"
        days_to_exam = student_context.get("days_to_exam")
        exam_name = student_context.get("exam_name", "exam")
        streak = student_context.get("current_streak", 0)
        weak_topics = student_context.get("weak_topics", [])
        mistakes = student_context.get("common_mistakes", [])
        recent_topic = student_context.get("recent_topic", "")
        due_reviews = student_context.get("due_reviews", [])
        
        # Build prompt based on nudge type
        prompt = f"""You are Sathi, a warm and intelligent AI mentor for Indian students.
Generate a SHORT notification message (max 2 sentences) for this student.

STUDENT CONTEXT:
- Name: {name}
- Current streak: {streak} days
{"- Days to " + exam_name + ": " + str(days_to_exam) if days_to_exam else ""}
{"- Weak topics: " + ", ".join(weak_topics) if weak_topics else ""}
{"- Common mistake patterns: " + ", ".join(mistakes) if mistakes else ""}
{"- Last studied: " + recent_topic if recent_topic else ""}
{"- Topics due for review: " + ", ".join(due_reviews) if due_reviews else ""}

NUDGE TYPE: {nudge_type}
{"ADDITIONAL CONTEXT: " + str(base_context) if base_context else ""}

RULES:
1. Be warm and friendly like a supportive elder sibling
2. Reference SPECIFIC student data (exam days, weak topics, mistakes)
3. Keep it SHORT - max 2 sentences
4. Include ONE clear action suggestion
5. Never guilt-trip or be negative
6. Use 1 emoji max

OUTPUT FORMAT (JSON):
{{"title": "short title with emoji", "message": "personalized message"}}

Generate the notification:"""

        try:
            response = await asyncio.wait_for(
                call_gemini(
                    prompt=prompt,
                    api_key=api_key,
                    temperature=0.7,
                    max_tokens=150,
                    model="gemini-2.0-flash",
                    system_message="You are a notification writer. Output only valid JSON."
                ),
                timeout=5.0  # Fast timeout for nudges
            )
            
            # Parse JSON response
            import json
            import re
            
            # Clean response - extract JSON
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                result = json.loads(json_match.group())
                if "title" in result and "message" in result:
                    logger.info(f"✅ Intelligent nudge generated for {nudge_type}")
                    return result
            
            logger.warning(f"LLM response not valid JSON: {response[:100] if response else 'empty'}")
            
        except asyncio.TimeoutError:
            logger.warning("LLM nudge generation timed out - using fallback")
        except Exception as e:
            logger.warning(f"LLM nudge generation failed: {e} - using fallback")
        
        # Fallback to template if LLM fails
        return self._get_fallback_message(nudge_type, student_context, base_context)
    
    def _get_fallback_message(
        self,
        nudge_type: str,
        student_context: Dict[str, Any],
        base_context: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """
        Fallback template-based messages when LLM is unavailable.
        Still personalized with available data.
        """
        name = student_context.get("name") or "there"
        days = student_context.get("days_to_exam")
        exam = student_context.get("exam_name", "exam")
        streak = student_context.get("current_streak", 0)
        weak = student_context.get("weak_topics", [])
        recent = student_context.get("recent_topic", "your studies")
        mistakes = student_context.get("common_mistakes", [])
        
        # Build contextual suffix
        exam_suffix = f" ({days} days to {exam})" if days and days <= 60 else ""
        
        templates = {
            "streak_protection": {
                "title": f"🔥 Your {streak}-day streak needs you!",
                "message": f"Hey {name}, quick 5-min session on {recent} to keep your streak alive?{exam_suffix}"
            },
            "continue_learning": {
                "title": "📚 Pick up where you left off",
                "message": f"Ready to continue {recent}, {name}?{exam_suffix}"
            },
            "revision_due": {
                "title": "🧠 Time for a quick review",
                "message": f"{name}, spaced repetition works! Let's reinforce what you learned.{exam_suffix}"
            },
            "weak_topic_focus": {
                "title": f"💪 Let's strengthen {weak[0] if weak else 'a topic'}",
                "message": f"{name}, focused practice on {weak[0] if weak else 'weak areas'} will boost your confidence!{exam_suffix}"
            },
            "exam_countdown": {
                "title": f"📅 {days} days to {exam}!",
                "message": f"{name}, let's make today count. Focus on high-yield topics!"
            },
            "motivation": {
                "title": "⭐ You're doing great!",
                "message": f"Keep up the momentum, {name}! Every session brings you closer to your goal.{exam_suffix}"
            },
            "error_pattern": {
                "title": f"🎯 Quick fix for {mistakes[0] if mistakes else 'common errors'}",
                "message": f"{name}, I noticed you sometimes struggle with {mistakes[0] if mistakes else 'certain patterns'}. Let's practice!{exam_suffix}"
            }
        }
        
        return templates.get(nudge_type, {
            "title": "👋 Hey there!",
            "message": f"Ready to learn something new, {name}?{exam_suffix}"
        })
    
    # ========================================
    # 🧠 PHASE 3: Cross-Agent Awareness
    # ========================================
    
    async def get_recent_nudges(self, user_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get nudges sent to this user in the last N hours.
        Used for cross-agent awareness (companion knows what notifications were sent).
        """
        if self.db is None:
            return []
        
        try:
            threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            nudges = await self.db.nudge_log.find({
                "user_id": user_id,
                "sent_at": {"$gte": threshold}
            }).sort("sent_at", -1).limit(10).to_list(length=10)
            
            return [{
                "type": n.get("nudge_type", "unknown"),
                "sent_at": n.get("sent_at"),
                "topic": n.get("topic"),
                "action_taken": n.get("action_taken")
            } for n in nudges]
            
        except Exception as e:
            logger.warning(f"Failed to get recent nudges: {e}")
            return []
    
    async def get_emotional_state(self, user_id: str) -> Dict[str, Any]:
        """
        Detect student's emotional state from recent interactions.
        Used for emotional calibration in nudges.
        
        Returns:
            {
                "state": "confident|struggling|frustrated|neutral",
                "confidence": 0.0-1.0,
                "signals": ["list of detected signals"]
            }
        """
        if self.db is None:
            return {"state": "neutral", "confidence": 0.5, "signals": []}
        
        try:
            now = datetime.now(timezone.utc)
            recent_threshold = now - timedelta(hours=24)
            
            # Get recent chat messages
            recent_messages = await self.db.chat_messages.find({
                "user_id": user_id,
                "timestamp": {"$gte": recent_threshold},
                "role": "user"
            }).sort("timestamp", -1).limit(20).to_list(length=20)
            
            if not recent_messages:
                return {"state": "neutral", "confidence": 0.3, "signals": ["no_recent_activity"]}
            
            signals = []
            state = "neutral"
            confidence = 0.5
            
            # Analyze message patterns
            message_texts = [m.get("content", "").lower() for m in recent_messages]
            combined_text = " ".join(message_texts)
            
            # Frustration signals
            frustration_words = ["don't understand", "confused", "not getting", "wrong again", 
                               "still wrong", "why is this", "help me", "frustrated", "stuck"]
            frustration_count = sum(1 for w in frustration_words if w in combined_text)
            
            if frustration_count >= 2:
                signals.append("multiple_frustration_indicators")
                state = "frustrated"
                confidence = 0.7
            
            # Struggling signals - repeated questions on same topic
            topics_mentioned = {}
            for msg in recent_messages:
                topic = msg.get("detected_topic", "")
                if topic:
                    topics_mentioned[topic] = topics_mentioned.get(topic, 0) + 1
            
            repeated_topics = [t for t, c in topics_mentioned.items() if c >= 3]
            if repeated_topics:
                signals.append(f"struggling_with_{repeated_topics[0]}")
                if state == "neutral":
                    state = "struggling"
                    confidence = 0.6
            
            # Confidence signals
            confidence_words = ["got it", "understood", "makes sense", "easy", "simple", "thanks"]
            confidence_count = sum(1 for w in confidence_words if w in combined_text)
            
            if confidence_count >= 2 and frustration_count == 0:
                signals.append("positive_comprehension")
                state = "confident"
                confidence = 0.7
            
            # Check recent performance (if available)
            try:
                recent_assessments = await self.db.assessments.find({
                    "user_id": user_id,
                    "completed_at": {"$gte": recent_threshold}
                }).sort("completed_at", -1).limit(5).to_list(length=5)
                
                if recent_assessments:
                    avg_score = sum(a.get("score", 50) for a in recent_assessments) / len(recent_assessments)
                    if avg_score < 40:
                        signals.append("low_recent_scores")
                        if state == "neutral":
                            state = "struggling"
                    elif avg_score > 80:
                        signals.append("high_recent_scores")
                        if state == "neutral":
                            state = "confident"
            except Exception:
                pass
            
            return {
                "state": state,
                "confidence": confidence,
                "signals": signals
            }
            
        except Exception as e:
            logger.warning(f"Failed to detect emotional state: {e}")
            return {"state": "neutral", "confidence": 0.3, "signals": ["detection_error"]}
    
    async def get_context_for_companion(self, user_id: str) -> Dict[str, Any]:
        """
        Get full context for AI Companion including:
        - Student intelligence
        - Recent nudges sent
        - Emotional state
        
        This enables cross-agent awareness between Notification Agent and Companion.
        """
        context = await self._get_student_intelligence(user_id)
        
        # Add recent nudges
        recent_nudges = await self.get_recent_nudges(user_id, hours=24)
        context["recent_nudges"] = recent_nudges
        context["nudge_count_24h"] = len(recent_nudges)
        
        # Add emotional state
        emotional = await self.get_emotional_state(user_id)
        context["emotional_state"] = emotional["state"]
        context["emotional_confidence"] = emotional["confidence"]
        context["emotional_signals"] = emotional["signals"]
        
        return context
    
    def adapt_tone_for_emotion(self, emotional_state: str, base_message: Dict[str, str]) -> Dict[str, str]:
        """
        Adapt message tone based on emotional state.
        
        - Frustrated → Softer, more encouraging
        - Struggling → Offer help, simplify suggestions
        - Confident → Can be more challenging
        - Neutral → Standard warm tone
        """
        state = emotional_state.lower()
        title = base_message.get("title", "")
        message = base_message.get("message", "")
        
        if state == "frustrated":
            # Soften the message, be extra supportive
            if "!" in title:
                title = title.replace("!", "")  # Remove excitement
            message = f"I know this can be tough. {message} Take it one step at a time."
            
        elif state == "struggling":
            # Offer simpler path
            message = f"No pressure. {message} We can start with something easier if you'd like."
            
        elif state == "confident":
            # Can be more challenging
            message = f"{message} Ready for a challenge?"
        
        return {"title": title, "message": message}
    
    # ========================================
    # LEVEL 2: Proactive Learning Companion
    # ========================================
    
    async def check_streak_protection(self, user_id: str) -> Optional[ProactiveNudge]:
        """
        Check if user is about to break their streak and send protective nudge.
        
        This is the #1 engagement driver - preventing streak breaks!
        Enhanced with LLM-powered personalized messages.
        """
        try:
            user = await self.db.users.find_one({'user_id': user_id})
            if not user:
                return None
            
            current_streak = user.get('streak', 0)
            last_activity = user.get('last_study_activity')
            
            if not last_activity:
                return None
            
            # Calculate hours since last activity
            if isinstance(last_activity, str):
                last_activity = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
            
            now = datetime.utcnow()
            hours_since = (now - last_activity).total_seconds() / 3600
            
            # Check if streak is at risk (> 20 hours without activity)
            if hours_since >= self.INACTIVITY_THRESHOLD_HOURS and current_streak > 0:
                
                last_topic = user.get('last_topic', 'your studies')
                
                # 🧠 Get full student intelligence for personalized message
                student_context = await self._get_student_intelligence(user_id)
                student_context["current_streak"] = current_streak
                student_context["recent_topic"] = last_topic
                
                # 🧠 Generate intelligent message
                message_data = await self._generate_intelligent_message(
                    nudge_type="streak_protection",
                    student_context=student_context,
                    base_context={"hours_inactive": round(hours_since, 1)}
                )
                
                return ProactiveNudge(
                    nudge_type=NudgeType.STREAK_PROTECTION,
                    title=message_data["title"],
                    message=message_data["message"],
                    priority="high",
                    actions=[
                        {"label": "Quick 5-min Review", "action": "start_quick_review"},
                        {"label": "Remind in 1 hour", "action": "snooze_1h"},
                        {"label": "Skip today", "action": "skip_streak"}
                    ],
                    data={
                        'current_streak': current_streak,
                        'hours_inactive': round(hours_since, 1),
                        'last_topic': last_topic,
                        'intelligent': True
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Streak protection check error: {e}")
            return None
    
    async def get_continue_learning_nudge(self, user_id: str) -> Optional[ProactiveNudge]:
        """
        Suggest continuing where they left off.
        "Pick up where you left off" - like Netflix!
        """
        try:
            # Get user's recent sessions
            recent_sessions = await self.db.chat_sessions.find({
                'user_id': user_id
            }).sort('updated_at', -1).limit(3).to_list(length=3)
            
            if not recent_sessions:
                return None
            
            last_session = recent_sessions[0]
            topic = last_session.get('topic', last_session.get('title', 'your topic'))
            subject = last_session.get('subject', '')
            
            # Get time since last session
            last_update = last_session.get('updated_at')
            if last_update:
                if isinstance(last_update, str):
                    last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                # Ensure timezone-aware comparison
                if last_update.tzinfo is not None:
                    from datetime import timezone
                    now = datetime.now(timezone.utc)
                else:
                    now = datetime.utcnow()
                hours_ago = (now - last_update).total_seconds() / 3600
                
                if 2 <= hours_ago <= 48:  # Between 2 hours and 2 days
                    return ProactiveNudge(
                        nudge_type=NudgeType.CONTINUE_LEARNING,
                        title="📚 Continue where you left off?",
                        message=f"You were learning about {topic}. Ready to continue?",
                        priority="medium",
                        actions=[
                            {"label": "Continue Learning", "action": "continue_session", "session_id": last_session.get('session_id')},
                            {"label": "Start Fresh", "action": "new_session"},
                            {"label": "Later", "action": "dismiss"}
                        ],
                        data={
                            'session_id': last_session.get('session_id'),
                            'topic': topic,
                            'subject': subject,
                            'hours_ago': round(hours_ago, 1)
                        }
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Continue learning nudge error: {e}")
            return None
    
    async def get_exam_countdown_nudge(self, user_id: str) -> Optional[ProactiveNudge]:
        """
        Send exam countdown reminders at key milestones.
        90 days, 60 days, 30 days, 14 days, 7 days, 3 days, 1 day
        """
        try:
            user = await self.db.users.find_one({'user_id': user_id})
            if not user:
                return None
            
            exam_date = user.get('exam_date')
            exam_type = user.get('exam_type', 'exam')
            
            if not exam_date:
                return None
            
            if isinstance(exam_date, str):
                exam_date = datetime.fromisoformat(exam_date.replace('Z', '+00:00'))
            
            days_left = (exam_date - datetime.utcnow()).days
            
            # Key milestone days
            milestones = {
                90: ("📅 90 days to go!", "Time to start intensive preparation. Let's create your study plan!", "high"),
                60: ("📅 60 days left!", "Two months to go! Focus on weak areas now.", "high"),
                30: ("🚨 30 days to {exam}!", "One month left! Time for revision mode.", "high"),
                14: ("⚡ 2 weeks to {exam}!", "Focus on practice tests and revision.", "high"),
                7: ("🔥 1 week to {exam}!", "Final week! Quick revision and rest well.", "high"),
                3: ("💪 3 days to {exam}!", "Light revision only. You've got this!", "medium"),
                1: ("🌟 Tomorrow is {exam}!", "Relax today. You're prepared. Sleep well!", "low")
            }
            
            if days_left in milestones:
                title, message, priority = milestones[days_left]
                title = title.format(exam=exam_type)
                message = message.format(exam=exam_type)
                
                return ProactiveNudge(
                    nudge_type=NudgeType.EXAM_COUNTDOWN,
                    title=title,
                    message=message,
                    priority=priority,
                    actions=[
                        {"label": "See Study Plan", "action": "view_study_plan"},
                        {"label": "Practice Test", "action": "start_test"},
                        {"label": "Revision", "action": "start_revision"}
                    ],
                    data={
                        'days_left': days_left,
                        'exam_date': exam_date.isoformat(),
                        'exam_type': exam_type
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Exam countdown nudge error: {e}")
            return None
    
    async def generate_daily_summary(self, user_id: str) -> Optional[ProactiveNudge]:
        """
        Generate end-of-day study summary.
        Sent around 9 PM IST.
        """
        try:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0) - IST_OFFSET
            
            # Get today's activity
            sessions = await self.db.chat_sessions.find({
                'user_id': user_id,
                'updated_at': {'$gte': today_start}
            }).to_list(length=100)
            
            if not sessions:
                return ProactiveNudge(
                    nudge_type=NudgeType.DAILY_SUMMARY,
                    title="📊 Daily Summary",
                    message="No study activity today. Tomorrow is a new day! 💪",
                    priority="low",
                    actions=[
                        {"label": "Quick 10-min Session", "action": "start_quick"},
                        {"label": "See Tomorrow's Plan", "action": "view_plan"}
                    ],
                    data={'sessions_count': 0, 'topics': []}
                )
            
            # Calculate stats
            topics = list(set([s.get('topic', s.get('title', 'General')) for s in sessions]))
            subjects = list(set([s.get('subject', 'General') for s in sessions if s.get('subject')]))
            
            message = f"You studied {len(sessions)} topic(s) today"
            if subjects:
                message += f" in {', '.join(subjects[:3])}"
            message += ". Great job! 🌟"
            
            return ProactiveNudge(
                nudge_type=NudgeType.DAILY_SUMMARY,
                title="📊 Your Daily Summary",
                message=message,
                priority="low",
                actions=[
                    {"label": "See Details", "action": "view_details"},
                    {"label": "Continue Tomorrow", "action": "set_reminder"}
                ],
                data={
                    'sessions_count': len(sessions),
                    'topics': topics[:5],
                    'subjects': subjects
                }
            )
            
        except Exception as e:
            logger.error(f"Daily summary error: {e}")
            return None
    
    # ========================================
    # LEVEL 4: Intelligent Study Assistant
    # ========================================
    
    async def analyze_weak_topics(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Analyze user's performance to identify weak topics.
        Based on:
        - Quiz/test scores
        - Time spent on topics
        - Questions asked repeatedly
        - Confusion signals in messages
        """
        try:
            weak_topics = []
            
            # Get test results
            test_results = await self.db.mock_test_results.find({
                'user_id': user_id
            }).sort('created_at', -1).limit(20).to_list(length=20)
            
            topic_scores = {}
            for result in test_results:
                for topic_score in result.get('topic_scores', []):
                    topic = topic_score.get('topic')
                    score = topic_score.get('score', 0)
                    
                    if topic not in topic_scores:
                        topic_scores[topic] = []
                    topic_scores[topic].append(score)
            
            # Calculate average and identify weak topics (< 60% average)
            for topic, scores in topic_scores.items():
                avg_score = sum(scores) / len(scores)
                if avg_score < 60:
                    weak_topics.append({
                        'topic': topic,
                        'average_score': round(avg_score, 1),
                        'attempts': len(scores),
                        'trend': 'improving' if len(scores) > 1 and scores[-1] > scores[0] else 'needs_work'
                    })
            
            # Sort by weakest first
            weak_topics.sort(key=lambda x: x['average_score'])
            
            return weak_topics[:5]  # Top 5 weakest
            
        except Exception as e:
            logger.error(f"Weak topics analysis error: {e}")
            return []
    
    async def get_weak_topic_nudge(self, user_id: str) -> Optional[ProactiveNudge]:
        """
        Suggest focusing on weak topics.
        """
        weak_topics = await self.analyze_weak_topics(user_id)
        
        if not weak_topics:
            return None
        
        weakest = weak_topics[0]
        
        return ProactiveNudge(
            nudge_type=NudgeType.WEAK_TOPIC_FOCUS,
            title=f"🎯 Let's strengthen {weakest['topic']}",
            message=f"Your average is {weakest['average_score']}% here. A quick focused session can boost this!",
            priority="medium",
            actions=[
                {"label": f"Practice {weakest['topic']}", "action": "practice_topic", "topic": weakest['topic']},
                {"label": "See All Weak Areas", "action": "view_weak_topics"},
                {"label": "Later", "action": "dismiss"}
            ],
            data={
                'weak_topics': weak_topics,
                'focus_topic': weakest
            }
        )
    
    async def get_concept_dependencies(self, topic: str, subject: str) -> Dict[str, Any]:
        """
        Get prerequisite concepts for a topic.
        Helps suggest what to learn first.
        """
        # Concept dependency graph (simplified - could be from DB)
        dependencies = {
            'physics': {
                'projectile_motion': ['kinematics', 'vectors'],
                'circular_motion': ['kinematics', 'vectors', 'forces'],
                'gravitation': ['circular_motion', 'forces'],
                'oscillations': ['circular_motion', 'energy'],
                'waves': ['oscillations'],
                'electrostatics': ['vectors', 'calculus_basics'],
                'current_electricity': ['electrostatics'],
                'magnetism': ['current_electricity', 'vectors'],
                'electromagnetic_induction': ['magnetism', 'calculus_basics'],
            },
            'mathematics': {
                'integration': ['differentiation', 'algebra'],
                'differential_equations': ['integration', 'differentiation'],
                'vectors_3d': ['vectors_2d', 'coordinate_geometry'],
                'probability': ['permutations_combinations', 'algebra'],
                'matrices': ['algebra', 'linear_equations'],
            },
            'chemistry': {
                'chemical_bonding': ['atomic_structure', 'periodic_table'],
                'thermodynamics': ['states_of_matter', 'chemical_bonding'],
                'equilibrium': ['thermodynamics'],
                'electrochemistry': ['redox_reactions', 'thermodynamics'],
                'organic_reactions': ['chemical_bonding', 'hybridization'],
            }
        }
        
        topic_lower = topic.lower().replace(' ', '_')
        subject_lower = subject.lower()
        
        if subject_lower in dependencies:
            prereqs = dependencies[subject_lower].get(topic_lower, [])
            return {
                'topic': topic,
                'prerequisites': prereqs,
                'has_dependencies': len(prereqs) > 0
            }
        
        return {'topic': topic, 'prerequisites': [], 'has_dependencies': False}
    
    async def suggest_learning_path(self, user_id: str, target_topic: str, subject: str) -> Dict[str, Any]:
        """
        Suggest optimal learning path based on what user already knows.
        """
        try:
            # Get concepts user has already learned
            learned = await self.db.user_learned_concepts.find({
                'user_id': user_id,
                'subject': subject.lower()
            }).to_list(length=100)
            
            learned_topics = set([l.get('topic', '').lower() for l in learned])
            
            # Get dependencies for target topic
            deps = await self.get_concept_dependencies(target_topic, subject)
            
            # Find missing prerequisites
            missing = [p for p in deps['prerequisites'] if p.lower() not in learned_topics]
            
            if not missing:
                return {
                    'ready': True,
                    'target': target_topic,
                    'message': f"You're ready to learn {target_topic}! 🎯",
                    'path': [target_topic]
                }
            
            return {
                'ready': False,
                'target': target_topic,
                'message': f"Before {target_topic}, I'd suggest learning: {', '.join(missing)}",
                'path': missing + [target_topic],
                'missing_prerequisites': missing
            }
            
        except Exception as e:
            logger.error(f"Learning path suggestion error: {e}")
            return {
                'ready': True,
                'target': target_topic,
                'path': [target_topic]
            }
    
    async def detect_study_fatigue(self, user_id: str) -> Optional[ProactiveNudge]:
        """
        Detect if student has been studying too long and suggest a break.
        Prevents burnout!
        
        🔧 FIX: Only count CONTINUOUS session time (last 3 hours max), not all-time message span.
        """
        try:
            # ================================================================
            # FIX: Only look at messages from the CURRENT SESSION (last 3 hours)
            # This prevents the "59449 minutes" bug caused by old message spans
            # ================================================================
            session_window = datetime.utcnow() - timedelta(hours=3)
            
            recent_messages = await self.db.chat_messages.find({
                'user_id': user_id,
                'timestamp': {'$gte': session_window}  # ✅ TIME-BOUNDED
            }).sort('timestamp', -1).limit(50).to_list(length=50)
            
            # Need at least 5 messages in the window to consider it a "session"
            if len(recent_messages) < 5:
                return None
            
            # Check for continuous activity (not just message span)
            if recent_messages:
                latest = recent_messages[0].get('timestamp')
                earliest = recent_messages[-1].get('timestamp')
                
                if latest and earliest:
                    if isinstance(latest, str):
                        latest = datetime.fromisoformat(latest.replace('Z', '+00:00'))
                    if isinstance(earliest, str):
                        earliest = datetime.fromisoformat(earliest.replace('Z', '+00:00'))
                    
                    # Make timezone-aware if needed
                    if latest.tzinfo is None:
                        latest = latest.replace(tzinfo=timezone.utc)
                    if earliest.tzinfo is None:
                        earliest = earliest.replace(tzinfo=timezone.utc)
                    
                    session_minutes = (latest - earliest).total_seconds() / 60
                    
                    # ================================================================
                    # SANITY CHECK: Cap at 180 minutes (3 hours) to prevent bad data
                    # If calculation shows > 180 mins, something is wrong - skip
                    # ================================================================
                    if session_minutes > 180:
                        logger.warning(f"⚠️ Fatigue detection: session_minutes={session_minutes} > 180, skipping (bad data)")
                        return None
                    
                    if session_minutes >= self.STUDY_SESSION_MAX_MINUTES:
                        # Round to reasonable number
                        display_minutes = min(int(session_minutes), 180)
                        
                        return ProactiveNudge(
                            nudge_type=NudgeType.BREAK_SUGGESTION,
                            title="☕ Time for a break!",
                            message=f"You've been focused for {display_minutes} minutes straight - amazing! A quick 10-minute break helps your brain consolidate learning.",
                            priority="medium",
                            actions=[
                                {"label": "Start 10-min Break", "action": "start_break", "duration": 10},
                                {"label": "Snooze 30m", "action": "snooze_30min"},
                                {"label": "I'm in the zone!", "action": "dismiss"}
                            ],
                            data={
                                'session_minutes': display_minutes,
                                'messages_count': len(recent_messages),
                                'confidence': 'high' if len(recent_messages) >= 10 else 'medium'
                            }
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"Study fatigue detection error: {e}")
            return None
    
    async def get_motivation_nudge(self, user_id: str) -> Optional[ProactiveNudge]:
        """
        Send motivational nudge based on user's progress.
        Celebrate achievements!
        """
        try:
            user = await self.db.users.find_one({'user_id': user_id})
            if not user:
                return None
            
            streak = user.get('streak', 0)
            xp = user.get('xp', 0)
            
            # Check for streak milestones
            if streak in self.STREAK_MILESTONES:
                return ProactiveNudge(
                    nudge_type=NudgeType.MOTIVATION,
                    title=f"🎉 {streak}-Day Streak!",
                    message=f"Incredible! You've studied for {streak} days in a row. You're building a champion's habit!",
                    priority="high",
                    actions=[
                        {"label": "Keep Going!", "action": "continue"},
                        {"label": "Share Achievement", "action": "share"}
                    ],
                    data={
                        'streak': streak,
                        'xp': xp,
                        'milestone': True
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Motivation nudge error: {e}")
            return None
    
    # ========================================
    # SPACED REPETITION - Revision Due Nudges
    # ========================================
    
    async def get_revision_due_nudge(self, user_id: str) -> Optional[ProactiveNudge]:
        """
        🆕 Check for concepts due for revision using SM-2 spaced repetition.
        
        This is scientifically proven to optimize long-term retention!
        Enhanced with Error Genome™ awareness and intelligent messaging.
        """
        if not SPACED_REPETITION_AVAILABLE:
            return None
            
        try:
            sr_engine = SpacedRepetitionEngine(self.db)
            due_reviews = await sr_engine.get_due_reviews(user_id, limit=5)
            
            if not due_reviews:
                return None
            
            # Get the most urgent review
            most_urgent = due_reviews[0]
            total_due = len(due_reviews)
            
            # Build message based on urgency
            hours_overdue = most_urgent.get('due_since_hours', 0)
            
            if hours_overdue > 48:
                priority = "high"
            elif hours_overdue > 24:
                priority = "medium"
            else:
                priority = "low"
            
            concept = most_urgent.get('concept', most_urgent.get('topic', 'this concept'))
            subject = most_urgent.get('subject', 'your subject')
            
            # 🧠 Get full student intelligence for personalized message
            student_context = await self._get_student_intelligence(user_id)
            student_context["due_reviews"] = [r.get('concept', r.get('topic', '')) for r in due_reviews[:3]]
            
            # 🧠 Generate intelligent message with Error Genome™ context
            message_data = await self._generate_intelligent_message(
                nudge_type="revision_due",
                student_context=student_context,
                base_context={
                    "concept": concept,
                    "subject": subject,
                    "total_due": total_due,
                    "hours_overdue": hours_overdue
                }
            )
            
            return ProactiveNudge(
                nudge_type=NudgeType.REVISION_DUE,
                title=message_data["title"],
                message=message_data["message"],
                priority=priority,
                actions=[
                    {'label': '📖 Review Now', 'action': 'start_quick_review', 'data': {'concept': concept}},
                    {'label': '⏰ In 30 mins', 'action': 'snooze_30m'},
                    {'label': '🌙 Tomorrow', 'action': 'snooze_tomorrow'}
                ],
                data={
                    'due_reviews': due_reviews[:3],  # Top 3
                    'total_due': total_due,
                    'most_urgent_concept': concept,
                    'hours_overdue': hours_overdue,
                    'intelligent': True
                }
            )
            
        except Exception as e:
            logger.error(f"Revision due nudge error: {e}")
            return None
    
    # ========================================
    # Main Entry Point
    # ========================================
    
    async def get_all_nudges(self, user_id: str) -> List[ProactiveNudge]:
        """
        Get all applicable nudges for a user.
        Called by background scheduler.
        """
        nudges = []
        
        # Check each nudge type (including spaced repetition!)
        checks = [
            self.check_streak_protection(user_id),
            self.get_continue_learning_nudge(user_id),
            self.get_exam_countdown_nudge(user_id),
            self.get_weak_topic_nudge(user_id),
            self.get_revision_due_nudge(user_id),  # 🆕 Spaced repetition
            self.detect_study_fatigue(user_id),
            self.get_motivation_nudge(user_id),
        ]
        
        for check in checks:
            try:
                nudge = await check
                if nudge:
                    nudges.append(nudge)
            except Exception as e:
                logger.error(f"Nudge check error: {e}")
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        nudges.sort(key=lambda n: priority_order.get(n.priority, 1))
        
        return nudges
    
    async def process_nudge_action(
        self,
        user_id: str,
        nudge_type: str,
        action: str,
        data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process user's response to a nudge.
        """
        if action == 'snooze_1h':
            # Schedule reminder for 1 hour later
            return {'status': 'snoozed', 'snooze_minutes': 60}
        
        elif action == 'start_quick_review':
            # Start a quick review session
            return {'status': 'started', 'session_type': 'quick_review'}
        
        elif action == 'skip_streak':
            # User chose to skip - log but don't punish
            await self.db.users.update_one(
                {'user_id': user_id},
                {'$set': {'streak_skipped_today': True}}
            )
            return {'status': 'skipped'}
        
        elif action == 'start_break':
            duration = data.get('duration', 10) if data else 10
            return {'status': 'break_started', 'duration_minutes': duration}
        
        return {'status': 'acknowledged'}
    
    # ==========================================================================
    # 🎓 PHASE 2: LEARNING ENGINE - Learn what works for each student
    # ==========================================================================
    
    async def get_learning_profile(self, user_id: str) -> StudentLearningProfile:
        """
        Get or create the learning profile for a student.
        
        The learning profile stores what we've learned about this student's
        notification preferences from analyzing past outcomes.
        """
        if self.db is None:
            return StudentLearningProfile(user_id=user_id)
        
        try:
            # Try to load existing profile
            profile_doc = await self.db.mentor_learning_profiles.find_one({
                "user_id": user_id
            })
            
            if profile_doc:
                return StudentLearningProfile(
                    user_id=user_id,
                    overall_engagement_rate=profile_doc.get("overall_engagement_rate", 0.5),
                    study_conversion_rate=profile_doc.get("study_conversion_rate", 0.3),
                    preferred_frequency=profile_doc.get("preferred_frequency", "moderate"),
                    max_daily_notifications=profile_doc.get("max_daily_notifications", 3),
                    min_hours_between=profile_doc.get("min_hours_between", 3.0),
                    best_hour_of_day=profile_doc.get("best_hour_of_day"),
                    worst_hour_of_day=profile_doc.get("worst_hour_of_day"),
                    active_days=profile_doc.get("active_days", []),
                    preferred_tone=profile_doc.get("preferred_tone", "warm"),
                    responds_to_urgency=profile_doc.get("responds_to_urgency", True),
                    responds_to_celebration=profile_doc.get("responds_to_celebration", True),
                    help_effectiveness=profile_doc.get("help_effectiveness", 0.7),
                    protect_effectiveness=profile_doc.get("protect_effectiveness", 0.5),
                    celebrate_effectiveness=profile_doc.get("celebrate_effectiveness", 0.6),
                    guide_effectiveness=profile_doc.get("guide_effectiveness", 0.4),
                    consecutive_ignores=profile_doc.get("consecutive_ignores", 0),
                    backoff_until=profile_doc.get("backoff_until"),
                    last_updated=profile_doc.get("last_updated"),
                    total_notifications_analyzed=profile_doc.get("total_notifications_analyzed", 0)
                )
            
            # Return default profile for new users
            return StudentLearningProfile(user_id=user_id)
            
        except Exception as e:
            logger.warning(f"Error loading learning profile for {user_id}: {e}")
            return StudentLearningProfile(user_id=user_id)
    
    async def update_learning_profile(
        self,
        user_id: str,
        profile: StudentLearningProfile
    ) -> bool:
        """Save the updated learning profile to database."""
        if self.db is None:
            return False
        
        try:
            profile.last_updated = datetime.now(timezone.utc)
            
            await self.db.mentor_learning_profiles.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "user_id": user_id,
                        "overall_engagement_rate": profile.overall_engagement_rate,
                        "study_conversion_rate": profile.study_conversion_rate,
                        "preferred_frequency": profile.preferred_frequency,
                        "max_daily_notifications": profile.max_daily_notifications,
                        "min_hours_between": profile.min_hours_between,
                        "best_hour_of_day": profile.best_hour_of_day,
                        "worst_hour_of_day": profile.worst_hour_of_day,
                        "active_days": profile.active_days,
                        "preferred_tone": profile.preferred_tone,
                        "responds_to_urgency": profile.responds_to_urgency,
                        "responds_to_celebration": profile.responds_to_celebration,
                        "help_effectiveness": profile.help_effectiveness,
                        "protect_effectiveness": profile.protect_effectiveness,
                        "celebrate_effectiveness": profile.celebrate_effectiveness,
                        "guide_effectiveness": profile.guide_effectiveness,
                        "consecutive_ignores": profile.consecutive_ignores,
                        "backoff_until": profile.backoff_until,
                        "last_updated": profile.last_updated,
                        "total_notifications_analyzed": profile.total_notifications_analyzed
                    }
                },
                upsert=True
            )
            
            logger.debug(f"📚 Learning profile updated for {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating learning profile: {e}")
            return False
    
    async def analyze_and_learn(self, user_id: str) -> StudentLearningProfile:
        """
        🧠 LEARNING ENGINE: Analyze outcomes and update the learning profile.
        
        This is the core of Phase 2 - we analyze what has worked for this student
        and update their learning profile accordingly.
        
        Called periodically (e.g., daily) or after significant outcome data.
        """
        if self.db is None:
            return StudentLearningProfile(user_id=user_id)
        
        try:
            profile = await self.get_learning_profile(user_id)
            now = datetime.now(timezone.utc)
            thirty_days_ago = now - timedelta(days=30)
            
            # ===== ANALYZE OUTCOMES =====
            outcomes = await self.db.notification_outcomes.find({
                "user_id": user_id,
                "created_at": {"$gte": thirty_days_ago}
            }).to_list(length=500)
            
            if len(outcomes) < 5:
                # Not enough data to learn from
                logger.debug(f"📚 Not enough outcomes to learn for {user_id} ({len(outcomes)} outcomes)")
                return profile
            
            profile.total_notifications_analyzed = len(outcomes)
            
            # ===== ENGAGEMENT RATE =====
            positive_outcomes = [o for o in outcomes if o.get("outcome") in ["clicked", "studied"]]
            profile.overall_engagement_rate = len(positive_outcomes) / len(outcomes)
            
            # ===== STUDY CONVERSION RATE =====
            studied_outcomes = [o for o in outcomes if o.get("outcome") == "studied"]
            profile.study_conversion_rate = len(studied_outcomes) / len(outcomes)
            
            # ===== FREQUENCY PREFERENCE =====
            if profile.overall_engagement_rate > 0.6:
                profile.preferred_frequency = "moderate"
                profile.max_daily_notifications = 4
            elif profile.overall_engagement_rate > 0.3:
                profile.preferred_frequency = "moderate"
                profile.max_daily_notifications = 3
            else:
                profile.preferred_frequency = "low"
                profile.max_daily_notifications = 2
            
            # ===== TIMING ANALYSIS =====
            hour_engagement = {}
            for outcome in outcomes:
                created_at = outcome.get("created_at")
                if created_at:
                    hour = created_at.hour
                    if hour not in hour_engagement:
                        hour_engagement[hour] = {"total": 0, "positive": 0}
                    hour_engagement[hour]["total"] += 1
                    if outcome.get("outcome") in ["clicked", "studied"]:
                        hour_engagement[hour]["positive"] += 1
            
            # Find best and worst hours
            best_rate = 0
            worst_rate = 1
            for hour, data in hour_engagement.items():
                if data["total"] >= 3:  # Need at least 3 data points
                    rate = data["positive"] / data["total"]
                    if rate > best_rate:
                        best_rate = rate
                        profile.best_hour_of_day = hour
                    if rate < worst_rate:
                        worst_rate = rate
                        profile.worst_hour_of_day = hour
            
            # ===== INTENT EFFECTIVENESS =====
            intent_outcomes = {}
            for outcome in outcomes:
                intent = outcome.get("details", {}).get("mentor_intent")
                if intent:
                    if intent not in intent_outcomes:
                        intent_outcomes[intent] = {"total": 0, "positive": 0}
                    intent_outcomes[intent]["total"] += 1
                    if outcome.get("outcome") in ["clicked", "studied"]:
                        intent_outcomes[intent]["positive"] += 1
            
            for intent, data in intent_outcomes.items():
                if data["total"] >= 3:
                    effectiveness = data["positive"] / data["total"]
                    if intent == "help":
                        profile.help_effectiveness = effectiveness
                    elif intent == "protect":
                        profile.protect_effectiveness = effectiveness
                    elif intent == "celebrate":
                        profile.celebrate_effectiveness = effectiveness
                        profile.responds_to_celebration = effectiveness > 0.4
                    elif intent == "guide":
                        profile.guide_effectiveness = effectiveness
            
            # ===== TONE PREFERENCE ANALYSIS =====
            tone_outcomes = {}
            for outcome in outcomes:
                tone = outcome.get("details", {}).get("mentor_tone")
                if tone:
                    if tone not in tone_outcomes:
                        tone_outcomes[tone] = {"total": 0, "positive": 0}
                    tone_outcomes[tone]["total"] += 1
                    if outcome.get("outcome") in ["clicked", "studied"]:
                        tone_outcomes[tone]["positive"] += 1
            
            best_tone_rate = 0
            for tone, data in tone_outcomes.items():
                if data["total"] >= 3:
                    rate = data["positive"] / data["total"]
                    if rate > best_tone_rate:
                        best_tone_rate = rate
                        profile.preferred_tone = tone
            
            # ===== CONSECUTIVE IGNORES (recent) =====
            recent_outcomes = sorted(outcomes, key=lambda x: x.get("created_at", now), reverse=True)[:10]
            consecutive = 0
            for outcome in recent_outcomes:
                if outcome.get("outcome") in ["ignored", "dismissed"]:
                    consecutive += 1
                else:
                    break
            profile.consecutive_ignores = consecutive
            
            # ===== BACKOFF CALCULATION =====
            if profile.consecutive_ignores >= 5:
                # Extended backoff - student clearly doesn't want notifications
                profile.backoff_until = now + timedelta(hours=48)
                profile.min_hours_between = 12.0
                logger.info(f"📚 Extended backoff for {user_id}: 5+ consecutive ignores")
            elif profile.consecutive_ignores >= 3:
                # Standard backoff
                profile.backoff_until = now + timedelta(hours=24)
                profile.min_hours_between = 6.0
            else:
                profile.backoff_until = None
                # Adjust based on engagement
                if profile.overall_engagement_rate > 0.5:
                    profile.min_hours_between = 2.0
                else:
                    profile.min_hours_between = 4.0
            
            # ===== SAVE UPDATED PROFILE =====
            await self.update_learning_profile(user_id, profile)
            
            logger.info(
                f"📚 Learning complete for {user_id}: "
                f"engagement={profile.overall_engagement_rate:.0%}, "
                f"best_hour={profile.best_hour_of_day}, "
                f"freq={profile.preferred_frequency}, "
                f"tone={profile.preferred_tone}"
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"Error in analyze_and_learn for {user_id}: {e}")
            return StudentLearningProfile(user_id=user_id)
    
    async def apply_learning_to_decision(
        self,
        state: StudentState,
        intent: MentorIntent,
        base_decision: Tuple[bool, str]
    ) -> Tuple[bool, str, Optional[str]]:
        """
        🧠 Apply learning profile to modify the decision.
        
        Takes the base decision from the interruption gate and adjusts it
        based on what we've learned about this student.
        
        Returns: (approved, reason, adjusted_tone)
        """
        approved, reason = base_decision
        adjusted_tone = None
        
        try:
            profile = await self.get_learning_profile(state.user_id)
            now = datetime.now(timezone.utc)
            
            # ===== CHECK BACKOFF =====
            if profile.backoff_until and profile.backoff_until > now:
                remaining = (profile.backoff_until - now).total_seconds() / 3600
                return False, f"In learned backoff period ({remaining:.1f}h remaining)", None
            
            # ===== CHECK LEARNED TIMING =====
            current_hour = now.hour
            if profile.worst_hour_of_day is not None:
                if current_hour == profile.worst_hour_of_day:
                    if intent not in [MentorIntent.HELP]:  # Allow HELP anytime
                        return False, f"Hour {current_hour} has low engagement for this student", None
            
            # ===== CHECK DAILY LIMIT =====
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_count = 0
            if self.db is not None:
                today_count = await self.db.user_notifications.count_documents({
                    "user_id": state.user_id,
                    "created_at": {"$gte": today_start}
                })
            
            if today_count >= profile.max_daily_notifications:
                if intent not in [MentorIntent.HELP]:
                    return False, f"Daily limit reached ({today_count}/{profile.max_daily_notifications})", None
            
            # ===== CHECK LEARNED MIN HOURS =====
            if state.hours_since_last_notification < profile.min_hours_between:
                if intent not in [MentorIntent.HELP]:
                    return (
                        False, 
                        f"Too soon (learned min: {profile.min_hours_between}h, actual: {state.hours_since_last_notification:.1f}h)",
                        None
                    )
            
            # ===== APPLY INTENT EFFECTIVENESS =====
            if approved:
                effectiveness = {
                    MentorIntent.HELP: profile.help_effectiveness,
                    MentorIntent.PROTECT: profile.protect_effectiveness,
                    MentorIntent.CELEBRATE: profile.celebrate_effectiveness,
                    MentorIntent.GUIDE: profile.guide_effectiveness
                }.get(intent, 0.5)
                
                # If this intent type rarely works for this student, be more selective
                if effectiveness < 0.3:
                    if intent != MentorIntent.HELP:  # Always allow HELP
                        return (
                            False,
                            f"Intent {intent.value} has low effectiveness ({effectiveness:.0%}) for this student",
                            None
                        )
            
            # ===== APPLY TONE PREFERENCE =====
            if approved:
                adjusted_tone = profile.preferred_tone
            
            return approved, reason, adjusted_tone
            
        except Exception as e:
            logger.warning(f"Error applying learning: {e}")
            return approved, reason, None
    
    async def make_mentor_decision_with_learning(self, user_id: str) -> MentorDecision:
        """
        🧠 PHASE 2: Enhanced decision with learning integration.
        
        This is the new main entry point that combines:
        1. State computation
        2. Intent reasoning
        3. Interruption gate
        4. Learning-based adjustments
        5. Tone calibration (with learned preference)
        6. Message composition
        """
        
        # LAYER 1: Compute student state
        state = await self.compute_student_state(user_id)
        logger.info(
            f"🧠 Student State: {user_id} | "
            f"emotional={state.emotional_state.value} | "
            f"momentum={state.momentum.value} | "
            f"studying={state.currently_studying}"
        )
        
        # LAYER 2: Reason about intent
        intent = await self.reason_about_intent(state)
        
        # LAYER 3: Check interruption gate
        base_approved, base_reason = await self.check_interruption_gate(state, intent)
        
        # 🆕 LAYER 3.5: Apply learning
        approved, reason, learned_tone = await self.apply_learning_to_decision(
            state=state,
            intent=intent,
            base_decision=(base_approved, base_reason)
        )
        
        if not approved:
            logger.info(f"🚫 Decision DENIED for {user_id}: {reason}")
            
            action = "BACKOFF" if state.needs_space else "WAIT"
            retry_after = 24 * 60 if action == "BACKOFF" else 60
            
            return MentorDecision(
                action=action,
                intent=intent,
                approved=False,
                reason=reason,
                retry_after_minutes=retry_after
            )
        
        # LAYER 4: Calibrate tone (use learned preference if available)
        tone = learned_tone or self.calibrate_tone(state, intent)
        
        # LAYER 5: Compose message
        student_context = await self._get_student_intelligence(user_id)
        student_context["emotional_state"] = state.emotional_state.value
        student_context["momentum"] = state.momentum.value
        student_context["tone"] = tone
        
        message = await self._generate_mentor_message(
            intent=intent,
            tone=tone,
            student_context=student_context,
            state=state
        )
        
        logger.info(f"✅ Mentor APPROVED for {user_id}: intent={intent.value}, tone={tone}")
        
        return MentorDecision(
            action="NOTIFY",
            intent=intent,
            approved=True,
            reason=reason,
            tone=tone,
            message=message,
            confidence=0.7 if state.emotional_confidence > 0.5 else 0.5
        )
    
    # ==========================================================================
    # 🎯 PHASE 3: EVENT-DRIVEN SYSTEM
    # ==========================================================================
    
    async def handle_event(self, event: MentorEventData) -> Optional[MentorDecision]:
        """
        🎯 PHASE 3: Handle a mentor event.
        
        This is the main entry point for event-driven notifications.
        Instead of polling, we respond to meaningful moments.
        
        Returns a MentorDecision or None if no action needed.
        """
        logger.info(f"📡 Event received: {event.event_type.value} for {event.user_id}")
        
        # Route to appropriate handler based on event type
        handlers = {
            MentorEvent.SESSION_ENDED: self._handle_session_ended,
            MentorEvent.LONG_SESSION: self._handle_long_session,
            MentorEvent.INACTIVITY_DETECTED: self._handle_inactivity,
            MentorEvent.COMEBACK: self._handle_comeback,
            MentorEvent.FRUSTRATION_DETECTED: self._handle_frustration,
            MentorEvent.CONFUSION_DETECTED: self._handle_confusion,
            MentorEvent.STREAK_AT_RISK: self._handle_streak_at_risk,
            MentorEvent.STREAK_MILESTONE: self._handle_streak_milestone,
            MentorEvent.EXAM_APPROACHING: self._handle_exam_approaching,
            MentorEvent.REVIEW_OVERDUE: self._handle_review_overdue,
        }
        
        handler = handlers.get(event.event_type)
        if not handler:
            logger.debug(f"No handler for event type: {event.event_type.value}")
            return None
        
        try:
            # Log the event
            await self._log_event(event)
            
            # Handle the event
            decision = await handler(event)
            
            return decision
            
        except Exception as e:
            logger.error(f"Error handling event {event.event_type.value}: {e}")
            return None
    
    async def _log_event(self, event: MentorEventData):
        """Log event for analysis and debugging."""
        if self.db is None:
            return
        
        try:
            await self.db.mentor_events.insert_one({
                **event.to_dict(),
                "logged_at": datetime.now(timezone.utc)
            })
        except Exception as e:
            logger.debug(f"Failed to log event: {e}")
    
    # ===== EVENT HANDLERS =====
    
    async def _handle_session_ended(self, event: MentorEventData) -> Optional[MentorDecision]:
        """
        Handle session ended event.
        
        Opportunity for:
        - Celebrating effort ("Great session!")
        - Suggesting break if long session
        - Follow-up on what they learned
        """
        state = await self.compute_student_state(event.user_id)
        
        # Don't interrupt if they just stopped briefly
        if state.minutes_since_last_activity < 10:
            return None
        
        # Get learning profile
        profile = await self.get_learning_profile(event.user_id)
        
        # Check if we should reach out
        if profile.overall_engagement_rate < 0.3:
            # Low engagement - probably don't want session-end messages
            return None
        
        session_minutes = event.session_duration_minutes or 0
        
        # Determine intent based on session
        if session_minutes >= 60:
            # Long session - celebrate!
            intent = MentorIntent.CELEBRATE
            tone = "celebratory"
            message = await self._generate_session_end_message(
                state=state,
                session_minutes=session_minutes,
                tone=tone
            )
        elif session_minutes >= 20:
            # Good session - gentle acknowledgment
            intent = MentorIntent.GUIDE
            tone = "warm"
            message = await self._generate_session_end_message(
                state=state,
                session_minutes=session_minutes,
                tone=tone
            )
        else:
            # Short session - maybe they'll continue, don't interrupt
            return None
        
        # Apply learning gate
        approved, reason, learned_tone = await self.apply_learning_to_decision(
            state=state,
            intent=intent,
            base_decision=(True, "Session ended event")
        )
        
        if not approved:
            logger.debug(f"Session end notification blocked: {reason}")
            return None
        
        return MentorDecision(
            action="NOTIFY",
            intent=intent,
            approved=True,
            reason=f"Session ended after {session_minutes} minutes",
            tone=learned_tone or tone,
            message=message,
            confidence=0.6
        )
    
    async def _handle_long_session(self, event: MentorEventData) -> Optional[MentorDecision]:
        """
        Handle long session event (90+ minutes continuous).
        
        Suggest a break - this is for student wellbeing.
        """
        state = await self.compute_student_state(event.user_id)
        
        if not state.currently_studying:
            # They already stopped
            return None
        
        session_minutes = event.session_duration_minutes or 90
        
        message = {
            "title": "☕ You've earned a break!",
            "message": f"Wow, {session_minutes} minutes of focused work! Your brain needs a quick rest to absorb all that. A 10-minute break will help you retain more."
        }
        
        return MentorDecision(
            action="NOTIFY",
            intent=MentorIntent.GUIDE,
            approved=True,
            reason=f"Long session: {session_minutes} minutes",
            tone="warm",
            message=message,
            confidence=0.8  # High confidence - breaks are important
        )
    
    async def _handle_inactivity(self, event: MentorEventData) -> Optional[MentorDecision]:
        """
        Handle inactivity event.
        
        This is a smart re-engagement, but must be very careful:
        - Respect learned preferences
        - Don't pile on if they're ignoring us
        - Adjust message based on how long they've been away
        """
        state = await self.compute_student_state(event.user_id)
        profile = await self.get_learning_profile(event.user_id)
        
        # If in backoff, don't reach out
        if profile.backoff_until and profile.backoff_until > datetime.now(timezone.utc):
            return None
        
        # If they need space, don't reach out
        if state.needs_space:
            return None
        
        inactivity_hours = event.inactivity_hours or state.minutes_since_last_activity / 60
        
        # Determine intent based on context
        if state.streak_days >= 3 and inactivity_hours > 18:
            intent = MentorIntent.PROTECT
            reason = f"Streak ({state.streak_days} days) at risk after {inactivity_hours:.0f}h inactivity"
        else:
            intent = MentorIntent.GUIDE
            reason = f"Re-engagement after {inactivity_hours:.0f}h inactivity"
        
        # Apply learning gate
        approved, gate_reason, learned_tone = await self.apply_learning_to_decision(
            state=state,
            intent=intent,
            base_decision=(True, reason)
        )
        
        if not approved:
            return None
        
        # Generate contextual message
        student_context = await self._get_student_intelligence(event.user_id)
        message = await self._generate_mentor_message(
            intent=intent,
            tone=learned_tone or "warm",
            student_context=student_context,
            state=state
        )
        
        return MentorDecision(
            action="NOTIFY",
            intent=intent,
            approved=True,
            reason=reason,
            tone=learned_tone or "warm",
            message=message,
            confidence=0.5
        )
    
    async def _handle_comeback(self, event: MentorEventData) -> Optional[MentorDecision]:
        """
        Handle comeback event (student returned after 2+ days).
        
        Welcome them back warmly, no guilt.
        """
        state = await self.compute_student_state(event.user_id)
        
        # Don't send if they're actively studying now
        if state.currently_studying:
            return None
        
        message = {
            "title": "👋 Welcome back!",
            "message": f"Hey {state.name or 'there'}! Good to see you. Pick up wherever feels right - no pressure."
        }
        
        return MentorDecision(
            action="NOTIFY",
            intent=MentorIntent.GUIDE,
            approved=True,
            reason="Comeback after extended absence",
            tone="welcoming",
            message=message,
            confidence=0.6
        )
    
    async def _handle_frustration(self, event: MentorEventData) -> Optional[MentorDecision]:
        """
        Handle frustration detected event.
        
        This is a HELP intent - offer support without being pushy.
        """
        state = await self.compute_student_state(event.user_id)
        
        # HELP can always pass the gate (almost)
        topic = event.topic or state.last_topic or "what you're working on"
        
        message = {
            "title": "💙 Here for you",
            "message": f"I notice {topic} might be tricky right now. Want to try a different approach? Sometimes a fresh angle helps."
        }
        
        return MentorDecision(
            action="NOTIFY",
            intent=MentorIntent.HELP,
            approved=True,
            reason=f"Frustration detected: {event.emotional_signals}",
            tone="supportive",
            message=message,
            confidence=0.7
        )
    
    async def _handle_confusion(self, event: MentorEventData) -> Optional[MentorDecision]:
        """
        Handle confusion detected event.
        
        Offer clarification help.
        """
        state = await self.compute_student_state(event.user_id)
        topic = event.topic or state.last_topic or "this"
        
        message = {
            "title": "🤔 Need a hand?",
            "message": f"Looks like {topic} has some tricky parts. Want me to explain it differently or break it down?"
        }
        
        return MentorDecision(
            action="NOTIFY",
            intent=MentorIntent.HELP,
            approved=True,
            reason="Confusion detected",
            tone="warm",
            message=message,
            confidence=0.6
        )
    
    async def _handle_streak_at_risk(self, event: MentorEventData) -> Optional[MentorDecision]:
        """
        Handle streak at risk event.
        
        Protect valuable streaks without guilt-tripping.
        """
        state = await self.compute_student_state(event.user_id)
        profile = await self.get_learning_profile(event.user_id)
        
        # Don't pile on if they need space
        if state.needs_space:
            return None
        
        # Apply learning gate
        approved, reason, learned_tone = await self.apply_learning_to_decision(
            state=state,
            intent=MentorIntent.PROTECT,
            base_decision=(True, "Streak at risk event")
        )
        
        if not approved:
            return None
        
        streak = event.streak_days or state.streak_days
        
        message = {
            "title": f"🔥 {streak} days strong",
            "message": f"Hey {state.name or 'there'}, your streak is still going! Even 5 minutes keeps it alive."
        }
        
        return MentorDecision(
            action="NOTIFY",
            intent=MentorIntent.PROTECT,
            approved=True,
            reason=f"Streak ({streak} days) at risk",
            tone=learned_tone or "encouraging",
            message=message,
            confidence=0.7
        )
    
    async def _handle_streak_milestone(self, event: MentorEventData) -> Optional[MentorDecision]:
        """
        Handle streak milestone event.
        
        Celebrate achievements!
        """
        state = await self.compute_student_state(event.user_id)
        profile = await self.get_learning_profile(event.user_id)
        
        # Check if student responds to celebration
        if not profile.responds_to_celebration:
            return None
        
        streak = event.streak_days or state.streak_days
        
        message = {
            "title": f"🎉 {streak} days!",
            "message": f"Incredible, {state.name or 'you'}! {streak} days of consistency is remarkable. You're building something powerful."
        }
        
        return MentorDecision(
            action="NOTIFY",
            intent=MentorIntent.CELEBRATE,
            approved=True,
            reason=f"Streak milestone: {streak} days",
            tone="celebratory",
            message=message,
            confidence=0.8
        )
    
    async def _handle_exam_approaching(self, event: MentorEventData) -> Optional[MentorDecision]:
        """
        Handle exam approaching event.
        
        Gentle reminder about upcoming exam.
        """
        state = await self.compute_student_state(event.user_id)
        
        # Don't add stress if student is anxious
        if state.emotional_state == EmotionalState.ANXIOUS:
            return None
        
        days = event.days_to_exam or state.days_to_exam or 7
        
        if days <= 3:
            message = {
                "title": f"📅 {days} days to go",
                "message": f"You've got this, {state.name or 'you'}. Focus on what you know, light revision only. Rest well!"
            }
            tone = "calm"
        elif days <= 7:
            message = {
                "title": f"📚 {days} days to exam",
                "message": f"Final stretch! Time for focused revision on high-yield topics. You're prepared."
            }
            tone = "encouraging"
        else:
            return None  # Too far out, don't spam
        
        return MentorDecision(
            action="NOTIFY",
            intent=MentorIntent.PROTECT,
            approved=True,
            reason=f"Exam in {days} days",
            tone=tone,
            message=message,
            confidence=0.6
        )
    
    async def _handle_review_overdue(self, event: MentorEventData) -> Optional[MentorDecision]:
        """
        Handle review overdue event.
        
        Gentle nudge about spaced repetition reviews.
        """
        state = await self.compute_student_state(event.user_id)
        profile = await self.get_learning_profile(event.user_id)
        
        # Check if GUIDE intents work for this student
        if profile.guide_effectiveness < 0.3:
            return None
        
        # Apply learning gate
        approved, reason, learned_tone = await self.apply_learning_to_decision(
            state=state,
            intent=MentorIntent.GUIDE,
            base_decision=(True, "Reviews overdue")
        )
        
        if not approved:
            return None
        
        due_count = len(state.due_reviews)
        topics = state.due_reviews[:2]
        
        message = {
            "title": "📚 Quick review?",
            "message": f"{due_count} topics ready for review{' including ' + ', '.join(topics) if topics else ''}. A quick session locks in what you learned!"
        }
        
        return MentorDecision(
            action="NOTIFY",
            intent=MentorIntent.GUIDE,
            approved=True,
            reason=f"{due_count} reviews overdue",
            tone=learned_tone or "warm",
            message=message,
            confidence=0.5
        )
    
    async def _generate_session_end_message(
        self,
        state: StudentState,
        session_minutes: int,
        tone: str
    ) -> Dict[str, str]:
        """Generate message for session end."""
        name = state.name or "there"
        topic = state.last_topic or "today's session"
        
        if tone == "celebratory":
            return {
                "title": f"⭐ {session_minutes} minutes!",
                "message": f"Amazing focus, {name}! {session_minutes} minutes on {topic} is real progress. Well done!"
            }
        else:
            return {
                "title": "💪 Good work!",
                "message": f"Nice session, {name}. {session_minutes} minutes of effort adds up. See you next time!"
            }
    
    # ==========================================================================
    # 🎯 EVENT DETECTION (for integration into other services)
    # ==========================================================================
    
    async def detect_session_end(self, user_id: str) -> Optional[MentorEventData]:
        """
        Detect if a study session just ended.
        
        Called when checking for session transitions.
        Returns event data if session ended, None otherwise.
        """
        if self.db is None:
            return None
        
        now = datetime.now(timezone.utc)
        
        try:
            # Get last message time
            last_message = await self.db.chat_messages.find_one(
                {"user_id": user_id},
                sort=[("timestamp", -1)]
            )
            
            if not last_message:
                return None
            
            last_time = last_message.get("timestamp")
            if isinstance(last_time, str):
                last_time = datetime.fromisoformat(last_time.replace('Z', '+00:00'))
            if last_time.tzinfo is None:
                last_time = last_time.replace(tzinfo=timezone.utc)
            
            minutes_since = (now - last_time).total_seconds() / 60
            
            # Session ended if 5-30 minutes since last activity
            # (More than 30 = they've been gone a while, don't trigger)
            if 5 <= minutes_since <= 30:
                # Calculate session duration
                session_start = await self._find_session_start(user_id, last_time)
                session_minutes = int((last_time - session_start).total_seconds() / 60)
                
                if session_minutes >= 5:  # Only count real sessions
                    return MentorEventData(
                        event_type=MentorEvent.SESSION_ENDED,
                        user_id=user_id,
                        timestamp=now,
                        session_duration_minutes=session_minutes,
                        source="detection"
                    )
            
            return None
            
        except Exception as e:
            logger.warning(f"Error detecting session end: {e}")
            return None
    
    async def _find_session_start(self, user_id: str, session_end: datetime) -> datetime:
        """Find when the current session started (gap of 30+ minutes before)."""
        try:
            # Get messages in reverse order
            messages = await self.db.chat_messages.find({
                "user_id": user_id,
                "timestamp": {"$lte": session_end}
            }).sort("timestamp", -1).limit(100).to_list(length=100)
            
            if not messages:
                return session_end
            
            prev_time = session_end
            for msg in messages:
                msg_time = msg.get("timestamp")
                if isinstance(msg_time, str):
                    msg_time = datetime.fromisoformat(msg_time.replace('Z', '+00:00'))
                if msg_time.tzinfo is None:
                    msg_time = msg_time.replace(tzinfo=timezone.utc)
                
                gap = (prev_time - msg_time).total_seconds() / 60
                if gap > 30:  # 30 minute gap = new session
                    return prev_time
                
                prev_time = msg_time
            
            # No gap found, session started at first message
            return prev_time
            
        except Exception as e:
            logger.warning(f"Error finding session start: {e}")
            return session_end
    
    async def detect_emotional_change(
        self,
        user_id: str,
        message_content: str
    ) -> Optional[MentorEventData]:
        """
        Detect emotional change from message content.
        
        Called after processing a chat message.
        Returns event data if significant emotional signal detected.
        """
        content_lower = message_content.lower()
        
        # Frustration signals
        frustration_signals = [
            "don't understand", "not getting", "so confused",
            "why is this", "stuck on", "can't figure",
            "this is hard", "frustrated", "giving up"
        ]
        
        frustration_found = [s for s in frustration_signals if s in content_lower]
        if len(frustration_found) >= 1:
            return MentorEventData(
                event_type=MentorEvent.FRUSTRATION_DETECTED,
                user_id=user_id,
                timestamp=datetime.now(timezone.utc),
                emotional_signals=frustration_found,
                source="chat"
            )
        
        # Confusion signals
        confusion_signals = [
            "what does this mean", "explain again", "still don't get",
            "confused about", "not sure", "can you clarify"
        ]
        
        confusion_found = [s for s in confusion_signals if s in content_lower]
        if len(confusion_found) >= 1:
            return MentorEventData(
                event_type=MentorEvent.CONFUSION_DETECTED,
                user_id=user_id,
                timestamp=datetime.now(timezone.utc),
                emotional_signals=confusion_found,
                source="chat"
            )
        
        return None


# Singleton instance
_mentor_instance = None

async def get_proactive_mentor(db_client) -> IntelligentProactiveMentor:
    """Get singleton instance"""
    global _mentor_instance
    if _mentor_instance is None:
        _mentor_instance = IntelligentProactiveMentor(db_client)
    return _mentor_instance


# =============================================================================
# 🎯 EVENT EMITTER - For use by other services
# =============================================================================

async def emit_mentor_event(
    db_client,
    event_type: MentorEvent,
    user_id: str,
    **kwargs
) -> Optional[MentorDecision]:
    """
    Emit a mentor event and get a decision.
    
    This is the main interface for other services to trigger mentor evaluation.
    
    Usage:
        from services.intelligent_proactive_mentor import emit_mentor_event, MentorEvent
        
        decision = await emit_mentor_event(
            db_client=db,
            event_type=MentorEvent.SESSION_ENDED,
            user_id=user_id,
            session_duration_minutes=45
        )
        
        if decision and decision.approved:
            await send_notification(...)
    """
    mentor = await get_proactive_mentor(db_client)
    
    event = MentorEventData(
        event_type=event_type,
        user_id=user_id,
        timestamp=datetime.now(timezone.utc),
        topic=kwargs.get("topic"),
        session_duration_minutes=kwargs.get("session_duration_minutes"),
        inactivity_hours=kwargs.get("inactivity_hours"),
        emotional_signals=kwargs.get("emotional_signals"),
        streak_days=kwargs.get("streak_days"),
        days_to_exam=kwargs.get("days_to_exam"),
        source=kwargs.get("source", "api")
    )
    
    return await mentor.handle_event(event)
