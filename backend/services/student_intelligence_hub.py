"""
Student Intelligence Hub - The Brain Behind Every Student Interaction
=====================================================================

This is the CORE intelligence layer that makes Druv AI truly understand,
remember, and actively help students win.

PHILOSOPHY (Non-Negotiable):
- Agents are DECISION-MAKERS, not LLM wrappers
- Intelligence is ACTIVE, not passive
- Every interaction should feel personalized
- Students should feel KNOWN and REMEMBERED

IMPLEMENTS ALL 10 STRATEGIC GAPS:
1. Active Intelligence (Gap 1) - Passive data becomes active insights
2. Learning Loop Closer (Gap 2) - Auto-update mastery after every interaction
3. Magic Moments (Gap 3) - Personalized context in every response
4. Agent Collaboration (Gap 4) - Agents consult each other
5. Exam Journey (Gap 5) - Countdown, priorities, daily goals
6. Dashboard Intelligence (Gap 6) - Expose intelligence to UI
7. Study Buddy (Gap 7) - Quiz me, Pomodoro, flashcards
8. Emotional Profile (Gap 8) - Remember emotional patterns
9. Learning Path (Gap 9) - Visual journey
10. Proactive Outreach (Gap 10) - AI initiates contact

Author: Druv AI Engineering
"""

import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS & DATA CLASSES
# =============================================================================

class ResponseMode(Enum):
    """How the agent should respond based on context"""
    MENTOR = "mentor"           # Teaching mode
    FRIEND = "friend"           # Casual, warm
    LISTENER = "listener"       # Emotional support
    GUIDE = "guide"             # Study planning
    CHALLENGER = "challenger"   # Quiz/practice mode
    CELEBRATOR = "celebrator"   # Achievement mode


class ExamUrgency(Enum):
    """Exam urgency levels"""
    CRITICAL = "critical"       # < 7 days
    HIGH = "high"               # 7-30 days
    MEDIUM = "medium"           # 30-90 days
    NORMAL = "normal"           # > 90 days


class EmotionalState(Enum):
    """Detected emotional states"""
    STRESSED = "stressed"
    ANXIOUS = "anxious"
    FRUSTRATED = "frustrated"
    CONFUSED = "confused"
    MOTIVATED = "motivated"
    CONFIDENT = "confident"
    NEUTRAL = "neutral"
    HAPPY = "happy"
    TIRED = "tired"


@dataclass
class MagicContext:
    """Context that creates 'WOW' moments - makes AI feel truly personal"""
    # Identity
    student_name: str = ""
    greeting_style: str = "warm"  # warm, casual, formal
    
    # Exam Journey
    exam_name: str = ""
    days_to_exam: Optional[int] = None
    exam_urgency: ExamUrgency = ExamUrgency.NORMAL
    syllabus_coverage: float = 0.0  # 0-100%
    daily_goal: str = ""
    
    # Current Topic Intelligence
    topic_mastery: int = 0  # 0-100
    is_weak_area: bool = False
    times_asked_before: int = 0
    last_struggle_point: str = ""
    
    # Continuity
    is_continuation: bool = False
    previous_topic: str = ""
    hours_since_last: Optional[float] = None
    
    # Emotional Intelligence
    current_emotion: EmotionalState = EmotionalState.NEUTRAL
    emotional_pattern: str = ""  # e.g., "stressed on Sundays"
    needs_encouragement: bool = False
    
    # Preferences
    preferred_metaphor: str = "cricket"
    explanation_depth: str = "medium"
    learns_better_with: str = "examples"
    
    # Achievements
    current_streak: int = 0
    recent_achievement: str = ""
    total_xp: int = 0
    level: int = 1
    
    # Proactive Insights
    due_reviews: List[str] = field(default_factory=list)
    recommended_next: str = ""
    priority_topics: List[str] = field(default_factory=list)
    
    # Error Genome™ - Common mistake patterns
    common_mistake_types: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_name": self.student_name,
            "exam_name": self.exam_name,
            "days_to_exam": self.days_to_exam,
            "exam_urgency": self.exam_urgency.value if self.exam_urgency else None,
            "syllabus_coverage": self.syllabus_coverage,
            "daily_goal": self.daily_goal,
            "topic_mastery": self.topic_mastery,
            "is_weak_area": self.is_weak_area,
            "times_asked_before": self.times_asked_before,
            "is_continuation": self.is_continuation,
            "previous_topic": self.previous_topic,
            "current_emotion": self.current_emotion.value if self.current_emotion else None,
            "needs_encouragement": self.needs_encouragement,
            "preferred_metaphor": self.preferred_metaphor,
            "current_streak": self.current_streak,
            "due_reviews": self.due_reviews,
            "priority_topics": self.priority_topics,
            "common_mistake_types": self.common_mistake_types
        }
    
    def get_magic_prompts(self) -> List[str]:
        """Generate magic context prompts that make responses personal"""
        prompts = []
        
        # Exam countdown magic - ENHANCED with natural reference
        if self.days_to_exam is not None:
            if self.days_to_exam <= 7:
                prompts.append(f"URGENT: Only {self.days_to_exam} days to {self.exam_name}! Say: 'With just {self.days_to_exam} days left, let's focus on...'")
            elif self.days_to_exam <= 30:
                prompts.append(f"Exam alert: {self.days_to_exam} days to {self.exam_name}. Reference time naturally: 'With {self.days_to_exam} days to go...'")
            elif self.days_to_exam <= 60:
                prompts.append(f"Preparing for {self.exam_name} in {self.days_to_exam} days. Mention exam relevance of this topic.")
        
        # Weak area magic
        if self.is_weak_area:
            prompts.append(f"This is a WEAK AREA (mastery: {self.topic_mastery}%). Explain more carefully with examples.")
        
        # Continuity magic
        if self.is_continuation:
            prompts.append(f"CONTINUING from previous session on {self.previous_topic}. Reference earlier learning.")
        
        # Repetition magic - ENHANCED with different approach hint
        if self.times_asked_before > 1:
            prompts.append(f"Student has asked about this {self.times_asked_before} times. Say: 'Let me try explaining this differently...' and use a NEW approach.")
        
        # Emotional magic
        if self.current_emotion in [EmotionalState.STRESSED, EmotionalState.ANXIOUS, EmotionalState.FRUSTRATED]:
            prompts.append("Student seems stressed. Be extra patient and encouraging. Start with reassurance.")
        
        # Streak magic
        if self.current_streak >= 5:
            prompts.append(f"Amazing {self.current_streak}-day streak! Acknowledge their consistency naturally.")
        
        # Achievement magic
        if self.recent_achievement:
            prompts.append(f"Recent achievement: {self.recent_achievement}. Celebrate progress!")
        
        # ==========================================================
        # ERROR GENOME™ - Mistake Pattern Awareness (Phase 1)
        # ==========================================================
        if self.common_mistake_types:
            mistake_guidance = []
            for pattern in self.common_mistake_types[:2]:  # Top 2 patterns only
                if pattern == "calculation_error":
                    mistake_guidance.append("calculation errors → emphasize step-by-step arithmetic and double-checking")
                elif pattern == "conceptual_confusion":
                    mistake_guidance.append("conceptual confusion → clarify the 'why' before 'how', use analogies")
                elif pattern == "formula_misuse":
                    mistake_guidance.append("formula misapplication → explain WHEN each formula applies, conditions matter")
                elif pattern == "sign_error":
                    mistake_guidance.append("sign errors → highlight direction conventions, draw diagrams")
                elif pattern == "unit_error":
                    mistake_guidance.append("unit errors → emphasize unit conversions and dimensional analysis")
                elif pattern == "reading_error":
                    mistake_guidance.append("reading errors → encourage re-reading the question, highlight key words")
            if mistake_guidance:
                prompts.append(f"ERROR GENOME: Student commonly makes {'; '.join(mistake_guidance)}. Proactively address these.")
        
        # ==========================================================
        # TRUST SIGNALS - AI Attribution (Phase 1)
        # ==========================================================
        # These are injected as guidance, not as specific phrases
        prompts.append("TRUST SIGNAL: Use one of these naturally: 'Based on your learning pattern...', 'DRON AI noticed...', 'From your recent sessions...'")
        
        return prompts


@dataclass
class LearningLoopResult:
    """Result of closing the learning loop after an interaction"""
    mastery_updated: bool = False
    mastery_delta: int = 0
    new_mastery: int = 0
    concepts_extracted: List[str] = field(default_factory=list)
    understanding_level: str = "unknown"  # poor, partial, good, excellent
    needs_review: bool = False
    next_review_date: Optional[datetime] = None
    xp_earned: int = 0
    streak_updated: bool = False
    achievements_unlocked: List[str] = field(default_factory=list)


@dataclass 
class ExamJourneyState:
    """Complete exam journey state for a student"""
    exam_name: str = ""
    exam_date: Optional[datetime] = None
    days_remaining: Optional[int] = None
    urgency: ExamUrgency = ExamUrgency.NORMAL
    
    # Coverage
    syllabus_coverage: float = 0.0
    topics_completed: List[str] = field(default_factory=list)
    topics_remaining: List[str] = field(default_factory=list)
    
    # Priorities
    priority_topics: List[str] = field(default_factory=list)
    hours_needed: Dict[str, float] = field(default_factory=dict)
    
    # Daily tracking
    daily_goal: str = ""
    daily_minutes_target: int = 120
    minutes_studied_today: int = 0
    
    # Progress
    weak_areas: List[str] = field(default_factory=list)
    improved_areas: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "exam_name": self.exam_name,
            "exam_date": self.exam_date.isoformat() if self.exam_date else None,
            "days_remaining": self.days_remaining,
            "urgency": self.urgency.value,
            "syllabus_coverage": self.syllabus_coverage,
            "topics_completed": self.topics_completed,
            "topics_remaining": self.topics_remaining,
            "priority_topics": self.priority_topics,
            "hours_needed": self.hours_needed,
            "daily_goal": self.daily_goal,
            "daily_minutes_target": self.daily_minutes_target,
            "minutes_studied_today": self.minutes_studied_today,
            "weak_areas": self.weak_areas,
            "improved_areas": self.improved_areas
        }


# =============================================================================
# STUDENT INTELLIGENCE HUB - Main Class
# =============================================================================

class StudentIntelligenceHub:
    """
    The central brain that orchestrates ALL student intelligence.
    
    This is what makes Druv AI truly intelligent:
    - Agents CONSULT this hub before making decisions
    - Every response is enriched with personalized context
    - Learning is tracked and mastery updated automatically
    - Proactive insights are generated continuously
    
    CRITICAL: This hub makes DECISIONS, not just provides data.
    Agents should ask: "What should I do for THIS student right now?"
    """
    
    def __init__(self, db):
        self.db = db
        
        # Lazy-loaded services
        self._mastery_tracker = None
        self._continuity_engine = None
        self._spaced_repetition = None
        self._memory_integration = None
        self._proactive_engine = None
        
        logger.info("🧠 StudentIntelligenceHub initialized - Ready to make students feel KNOWN")
    
    # =========================================================================
    # LAZY-LOADED SERVICES
    # =========================================================================
    
    @property
    def mastery_tracker(self):
        if not self._mastery_tracker:
            from services.mastery_tracker import MasteryTracker
            self._mastery_tracker = MasteryTracker(self.db)
        return self._mastery_tracker
    
    @property
    def continuity_engine(self):
        if not self._continuity_engine:
            from services.continuity_engine import ContinuityEngine
            self._continuity_engine = ContinuityEngine(self.db)
        return self._continuity_engine
    
    @property
    def spaced_repetition(self):
        if not self._spaced_repetition:
            from services.spaced_repetition import SpacedRepetitionEngine
            self._spaced_repetition = SpacedRepetitionEngine(self.db)
        return self._spaced_repetition
    
    @property
    def memory_integration(self):
        if not self._memory_integration:
            from services.memory_integration import MemoryIntegrationService
            self._memory_integration = MemoryIntegrationService(self.db)
        return self._memory_integration
    
    @property
    def proactive_engine(self):
        if not self._proactive_engine:
            from services.proactive_intelligence import ProactiveIntelligenceEngine
            self._proactive_engine = ProactiveIntelligenceEngine(self.db)
        return self._proactive_engine
    
    # =========================================================================
    # GAP 3: MAGIC MOMENTS - Personalized Context for Every Response
    # =========================================================================
    
    async def get_magic_context(
        self,
        user_id: str,
        session_id: str,
        current_query: str,
        detected_topic: str = None
    ) -> MagicContext:
        """
        Generate MAGIC context that makes every response feel personal.
        
        This is the KEY to making students feel KNOWN.
        Every agent should call this before generating a response.
        
        Args:
            user_id: Student identifier
            session_id: Current session
            current_query: What the student asked
            detected_topic: Topic detected from query (optional)
        
        Returns:
            MagicContext with all personalization data
        """
        logger.info(f"🪄 Generating magic context for {user_id}")
        
        context = MagicContext()
        
        try:
            # Parallel fetch for performance
            profile_task = self._get_user_profile(user_id)
            exam_task = self._get_exam_journey_state(user_id)
            mastery_task = self._get_topic_intelligence(user_id, current_query, detected_topic)
            continuity_task = self.continuity_engine.detect_topic_continuation(user_id, current_query)
            emotional_task = self._detect_current_emotion(current_query, user_id)
            
            profile, exam_state, topic_intel, continuity, emotion = await asyncio.gather(
                profile_task, exam_task, mastery_task, continuity_task, emotional_task
            )
            
            # Identity
            context.student_name = profile.get("name", "")
            
            # Exam Journey (Gap 5)
            if exam_state:
                context.exam_name = exam_state.exam_name
                context.days_to_exam = exam_state.days_remaining
                context.exam_urgency = exam_state.urgency
                context.syllabus_coverage = exam_state.syllabus_coverage
                context.daily_goal = exam_state.daily_goal
                context.priority_topics = exam_state.priority_topics[:3]
            
            # Topic Intelligence (Gap 1 & 3)
            context.topic_mastery = topic_intel.get("mastery", 0)
            context.is_weak_area = topic_intel.get("is_weak", False)
            context.times_asked_before = topic_intel.get("times_asked", 0)
            context.last_struggle_point = topic_intel.get("last_struggle", "")
            
            # Continuity (Gap 3)
            context.is_continuation = continuity.get("is_continuation", False)
            context.previous_topic = continuity.get("last_topic", "")
            context.hours_since_last = continuity.get("hours_since_last")
            
            # Emotional Intelligence (Gap 8)
            context.current_emotion = emotion.get("state", EmotionalState.NEUTRAL)
            context.emotional_pattern = emotion.get("pattern", "")
            context.needs_encouragement = emotion.get("needs_encouragement", False)
            
            # Preferences
            prefs = profile.get("preferences", {})
            context.preferred_metaphor = prefs.get("metaphor_style", "cricket")
            context.explanation_depth = prefs.get("explanation_depth", "medium")
            context.learns_better_with = prefs.get("learns_better_with", "examples")
            
            # Achievements
            stats = profile.get("stats", {})
            context.current_streak = stats.get("current_streak_days", 0)
            context.total_xp = stats.get("total_xp", 0)
            context.level = stats.get("level", 1)
            
            # Recent achievement check
            recent_achievement = await self._check_recent_achievement(user_id)
            context.recent_achievement = recent_achievement
            
            # Proactive Insights (Gap 10)
            due_reviews = await self.continuity_engine.get_due_reviews(user_id, limit=3)
            context.due_reviews = [r.get("topic", "") for r in due_reviews]
            
            # Error Genome™ - Fetch common mistake patterns (Phase 1)
            try:
                learning_profile = await self.db.learning_profiles.find_one({"user_id": user_id})
                if learning_profile:
                    context.common_mistake_types = learning_profile.get("common_mistake_types", [])
            except Exception as e:
                logger.warning(f"Could not fetch mistake patterns: {e}")
                context.common_mistake_types = []
            
            logger.info(f"🪄 Magic context generated: exam in {context.days_to_exam} days, "
                       f"topic mastery {context.topic_mastery}%, "
                       f"emotion: {context.current_emotion.value}")
            
        except Exception as e:
            logger.error(f"❌ Error generating magic context: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return context
    
    # =========================================================================
    # GAP 2: LEARNING LOOP CLOSER - Update Mastery After Every Interaction
    # =========================================================================
    
    async def close_learning_loop(
        self,
        user_id: str,
        session_id: str,
        query: str,
        response: Dict[str, Any],
        detected_topic: str = None,
        interaction_quality: str = "completed"  # completed, struggled, mastered
    ) -> LearningLoopResult:
        """
        Close the learning loop after every interaction.
        
        This is what makes learning ACTUALLY work:
        1. Extract concepts from interaction
        2. Assess understanding level
        3. Update mastery automatically
        4. Schedule spaced repetition
        5. Update streak and XP
        
        Args:
            user_id: Student identifier
            session_id: Current session
            query: What student asked
            response: AI response given
            detected_topic: Topic (optional, auto-detected if not provided)
            interaction_quality: How well the student engaged
        
        Returns:
            LearningLoopResult with all updates made
        """
        logger.info(f"📚 Closing learning loop for {user_id}")
        
        result = LearningLoopResult()
        
        try:
            # 1. Extract concepts from query
            concepts = self._extract_concepts(query)
            result.concepts_extracted = concepts
            
            # 2. Determine topic if not provided
            topic = detected_topic or self._extract_main_topic(query)
            
            # 3. Assess understanding from response and interaction
            understanding = await self._assess_understanding(
                query=query,
                response=response,
                interaction_quality=interaction_quality
            )
            result.understanding_level = understanding
            
            # 4. Calculate mastery delta
            mastery_delta = self._calculate_mastery_delta(
                understanding=understanding,
                interaction_quality=interaction_quality
            )
            result.mastery_delta = mastery_delta
            
            # 5. Update mastery
            if mastery_delta != 0 and topic != "general_concept":
                current_mastery = await self.mastery_tracker.get_mastery_level(user_id, topic)
                
                await self.mastery_tracker.update_mastery(
                    user_id=user_id,
                    topic=topic,
                    delta=mastery_delta,
                    reason=f"interaction_{interaction_quality}"
                )
                
                result.mastery_updated = True
                result.new_mastery = min(100, max(0, current_mastery + mastery_delta))
                
                logger.info(f"📈 Mastery updated: {topic} -> {result.new_mastery}% (+{mastery_delta})")
            
            # 6. Schedule spaced repetition if needed
            if understanding in ["good", "excellent"] and topic != "general_concept":
                quality = 4 if understanding == "good" else 5
                review_schedule = self.spaced_repetition.calculate_next_review(
                    current_interval_days=1,
                    quality=quality,
                    current_easiness=2.5
                )
                result.next_review_date = review_schedule.get("next_review_at")
                result.needs_review = False
            elif understanding == "partial":
                result.needs_review = True
                result.next_review_date = datetime.now(timezone.utc) + timedelta(days=1)
            
            # 7. Update XP and streak
            xp_earned = self._calculate_xp(
                understanding=understanding,
                interaction_quality=interaction_quality
            )
            result.xp_earned = xp_earned
            
            if xp_earned > 0:
                streak_updated = await self._update_xp_and_streak(user_id, xp_earned)
                result.streak_updated = streak_updated
            
            # 8. Check for achievements
            achievements = await self._check_and_unlock_achievements(
                user_id=user_id,
                topic=topic,
                new_mastery=result.new_mastery,
                streak_updated=result.streak_updated
            )
            result.achievements_unlocked = achievements
            
            # 9. Update concept thread
            if concepts:
                await self.continuity_engine.update_concept_thread(
                    user_id=user_id,
                    topic=topic,
                    concepts=concepts
                )
            
            logger.info(f"📚 Learning loop closed: mastery +{mastery_delta}, XP +{xp_earned}, "
                       f"achievements: {achievements}")
            
        except Exception as e:
            logger.error(f"❌ Error closing learning loop: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return result
    
    # =========================================================================
    # GAP 5: EXAM JOURNEY ORCHESTRATOR
    # =========================================================================
    
    async def get_exam_journey(self, user_id: str) -> ExamJourneyState:
        """
        Get complete exam journey state for a student.
        
        This powers the "countdown to D-Day" experience.
        
        Returns:
            ExamJourneyState with all exam-related intelligence
        """
        return await self._get_exam_journey_state(user_id)
    
    async def update_exam_target(
        self,
        user_id: str,
        exam_name: str,
        exam_date: datetime,
        daily_hours: int = 4
    ) -> ExamJourneyState:
        """
        Set or update student's target exam.
        
        This is called when student says "I'm preparing for JEE 2025"
        """
        logger.info(f"🎯 Setting exam target: {exam_name} on {exam_date} for {user_id}")
        
        try:
            days_remaining = (exam_date - datetime.now(timezone.utc)).days
            urgency = self._calculate_exam_urgency(days_remaining)
            
            # Calculate hours needed per subject (simplified)
            # In production, this would be based on syllabus and mastery
            hours_needed = {
                "Physics": 100,
                "Chemistry": 100,
                "Mathematics": 120
            }
            
            # Generate daily goal
            daily_minutes = daily_hours * 60
            daily_goal = f"Complete {daily_hours} hours of focused study"
            
            exam_data = {
                "user_id": user_id,
                "exam_name": exam_name,
                "exam_date": exam_date,
                "daily_hours": daily_hours,
                "daily_minutes_target": daily_minutes,
                "hours_needed": hours_needed,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            await self.db.user_exam_targets.update_one(
                {"user_id": user_id},
                {"$set": exam_data},
                upsert=True
            )
            
            # Get updated state
            return await self._get_exam_journey_state(user_id)
            
        except Exception as e:
            logger.error(f"❌ Error setting exam target: {e}")
            return ExamJourneyState()
    
    async def update_daily_progress(
        self,
        user_id: str,
        minutes_studied: int,
        topics_covered: List[str] = None
    ):
        """Update daily study progress"""
        try:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            
            await self.db.user_daily_progress.update_one(
                {"user_id": user_id, "date": today},
                {
                    "$inc": {"minutes_studied": minutes_studied},
                    "$addToSet": {"topics_covered": {"$each": topics_covered or []}},
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                },
                upsert=True
            )
            
            logger.info(f"📊 Updated daily progress: +{minutes_studied} mins")
            
        except Exception as e:
            logger.error(f"❌ Error updating daily progress: {e}")
    
    # =========================================================================
    # GAP 4: AGENT COLLABORATION HUB
    # =========================================================================
    
    async def consult_for_response(
        self,
        user_id: str,
        query: str,
        agent_type: str = "mentor"
    ) -> Dict[str, Any]:
        """
        Agents call this to get collaborative intelligence before responding.
        
        This is what makes agents SMART - they consult multiple
        intelligence sources before making a decision.
        
        Args:
            user_id: Student identifier
            query: What student asked
            agent_type: Which agent is asking (mentor, professor, etc.)
        
        Returns:
            Dict with collaborative intelligence for the agent
        """
        logger.info(f"🤝 Agent '{agent_type}' consulting hub for: {query[:50]}...")
        
        try:
            # Get magic context (Gap 3)
            magic_ctx = await self.get_magic_context(user_id, "", query)
            
            # Determine recommended response mode
            response_mode = self._decide_response_mode(
                query=query,
                magic_context=magic_ctx,
                agent_type=agent_type
            )
            
            # Get weak areas insight
            weak_areas = await self.mastery_tracker.get_weak_topics(user_id, threshold=40)
            weak_topics = [w["topic"] for w in weak_areas]
            
            # Check if topic is in weak areas
            current_topic = self._extract_main_topic(query)
            is_weak_topic = current_topic in weak_topics
            
            # Get recommended approach
            approach = self._get_recommended_approach(
                query=query,
                topic=current_topic,
                mastery=magic_ctx.topic_mastery,
                is_weak=is_weak_topic,
                emotion=magic_ctx.current_emotion
            )
            
            collaboration = {
                "magic_context": magic_ctx.to_dict(),
                "magic_prompts": magic_ctx.get_magic_prompts(),
                "response_mode": response_mode.value,
                "current_topic": current_topic,
                "is_weak_topic": is_weak_topic,
                "mastery_level": magic_ctx.topic_mastery,
                "recommended_approach": approach,
                "weak_areas": weak_topics[:5],
                "exam_urgency": magic_ctx.exam_urgency.value if magic_ctx.exam_urgency else None,
                "days_to_exam": magic_ctx.days_to_exam,
                "needs_encouragement": magic_ctx.needs_encouragement,
                "student_name": magic_ctx.student_name,
                "preferred_metaphor": magic_ctx.preferred_metaphor,
                "times_asked_before": magic_ctx.times_asked_before,
                "is_continuation": magic_ctx.is_continuation
            }
            
            logger.info(f"🤝 Collaboration ready: mode={response_mode.value}, "
                       f"mastery={magic_ctx.topic_mastery}%, weak={is_weak_topic}")
            
            return collaboration
            
        except Exception as e:
            logger.error(f"❌ Error in agent consultation: {e}")
            return {
                "magic_context": {},
                "response_mode": ResponseMode.MENTOR.value,
                "recommended_approach": "default"
            }
    
    # =========================================================================
    # GAP 8: EMOTIONAL PROFILE TRACKER
    # =========================================================================
    
    async def track_emotional_signal(
        self,
        user_id: str,
        emotion: EmotionalState,
        trigger: str = None,
        timestamp: datetime = None
    ):
        """
        Track emotional signal for pattern detection.
        
        Over time, this builds a picture of student's emotional patterns:
        - "Gets stressed on Sundays"
        - "More anxious before Physics"
        - "Needs encouragement after wrong answers"
        """
        try:
            ts = timestamp or datetime.now(timezone.utc)
            
            emotional_entry = {
                "user_id": user_id,
                "emotion": emotion.value,
                "trigger": trigger,
                "timestamp": ts,
                "day_of_week": ts.strftime("%A"),
                "hour_of_day": ts.hour
            }
            
            await self.db.user_emotional_history.insert_one(emotional_entry)
            
            # Update emotional patterns periodically
            # (In production, this would be a background job)
            await self._update_emotional_patterns(user_id)
            
            logger.info(f"💭 Tracked emotion: {emotion.value} for {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error tracking emotion: {e}")
    
    async def get_emotional_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get emotional profile for personalization.
        
        Returns patterns like:
        - stress_by_day: {"Sunday": 0.7, "Monday": 0.3, ...}
        - common_triggers: ["exams", "physics", ...]
        - needs_encouragement_after: ["wrong_answers", ...]
        """
        try:
            profile = await self.db.user_emotional_profile.find_one({"user_id": user_id})
            
            if not profile:
                return {
                    "stress_by_day": {},
                    "common_triggers": [],
                    "preferred_comfort_style": "encouraging",
                    "resilience_score": 0.5
                }
            
            return profile
            
        except Exception as e:
            logger.error(f"❌ Error getting emotional profile: {e}")
            return {}
    
    # =========================================================================
    # GAP 7: STUDY SESSION ORCHESTRATOR
    # =========================================================================
    
    async def start_study_session(
        self,
        user_id: str,
        session_type: str,  # "quiz", "review", "learn", "practice"
        topic: str = None,
        duration_minutes: int = 25
    ) -> Dict[str, Any]:
        """
        Start a structured study session.
        
        This powers:
        - "Quiz me on what I learned today"
        - "Start a 25-minute Pomodoro"
        - "Review my flashcards"
        - "Give me 5 practice problems"
        """
        logger.info(f"📖 Starting {session_type} session for {user_id}")
        
        try:
            session = {
                "session_id": f"study_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "user_id": user_id,
                "type": session_type,
                "topic": topic,
                "duration_minutes": duration_minutes,
                "started_at": datetime.now(timezone.utc),
                "status": "active"
            }
            
            if session_type == "quiz":
                # Generate quiz based on recent learning or weak areas
                quiz_content = await self._generate_quiz_session(user_id, topic)
                session["content"] = quiz_content
                
            elif session_type == "review":
                # Get concepts due for review
                due_reviews = await self.continuity_engine.get_due_reviews(user_id, limit=10)
                session["content"] = {"flashcards": due_reviews}
                
            elif session_type == "practice":
                # Generate practice problems
                problems = await self._generate_practice_problems(user_id, topic)
                session["content"] = {"problems": problems}
                
            elif session_type == "learn":
                # Get next recommended topic
                next_topic = await self._get_next_recommended_topic(user_id)
                session["content"] = {"topic": next_topic}
            
            # Save session
            await self.db.study_sessions.insert_one(session)
            
            logger.info(f"📖 Session started: {session['session_id']}")
            
            return session
            
        except Exception as e:
            logger.error(f"❌ Error starting study session: {e}")
            return {"error": str(e)}
    
    async def complete_study_session(
        self,
        session_id: str,
        results: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Complete a study session and update learning loop"""
        try:
            session = await self.db.study_sessions.find_one({"session_id": session_id})
            
            if not session:
                return {"error": "Session not found"}
            
            # Calculate duration
            started_at = session.get("started_at")
            duration_mins = 0
            if started_at:
                duration = datetime.now(timezone.utc) - started_at
                duration_mins = int(duration.total_seconds() / 60)
            
            # Update session
            await self.db.study_sessions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "status": "completed",
                        "completed_at": datetime.now(timezone.utc),
                        "actual_duration_minutes": duration_mins,
                        "results": results
                    }
                }
            )
            
            # Update daily progress
            await self.update_daily_progress(
                user_id=session["user_id"],
                minutes_studied=duration_mins,
                topics_covered=[session.get("topic")] if session.get("topic") else []
            )
            
            logger.info(f"📖 Session completed: {session_id} ({duration_mins} mins)")
            
            return {
                "session_id": session_id,
                "duration_minutes": duration_mins,
                "xp_earned": duration_mins * 2,  # 2 XP per minute
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Error completing study session: {e}")
            return {"error": str(e)}
    
    # =========================================================================
    # GAP 6 & 9: DASHBOARD & LEARNING PATH APIs
    # =========================================================================
    
    async def get_dashboard_intelligence(self, user_id: str) -> Dict[str, Any]:
        """
        Get all intelligence for the dashboard.
        
        This powers the student/parent dashboard with:
        - Mastery map
        - Weak areas
        - Exam readiness
        - Progress over time
        """
        try:
            # Parallel fetch
            profile_task = self._get_user_profile(user_id)
            exam_task = self._get_exam_journey_state(user_id)
            mastery_task = self.mastery_tracker.get_all_masteries(user_id)
            weak_task = self.mastery_tracker.get_weak_topics(user_id)
            strong_task = self.mastery_tracker.get_strong_topics(user_id)
            
            profile, exam_state, masteries, weak, strong = await asyncio.gather(
                profile_task, exam_task, mastery_task, weak_task, strong_task
            )
            
            dashboard = {
                "student": {
                    "name": profile.get("name", ""),
                    "level": profile.get("stats", {}).get("level", 1),
                    "total_xp": profile.get("stats", {}).get("total_xp", 0),
                    "current_streak": profile.get("stats", {}).get("current_streak_days", 0),
                    "questions_answered": profile.get("stats", {}).get("total_questions", 0)
                },
                "exam_journey": exam_state.to_dict() if exam_state else None,
                "mastery_map": masteries,
                "weak_areas": weak[:5],
                "strong_areas": strong[:5],
                "today_progress": await self._get_today_progress(user_id),
                "recent_achievements": await self._get_recent_achievements(user_id),
                "due_reviews": await self.continuity_engine.get_due_reviews(user_id, limit=5),
                "recommended_focus": await self._get_recommended_focus(user_id)
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"❌ Error getting dashboard: {e}")
            return {}
    
    async def get_learning_path(
        self,
        user_id: str,
        subject: str
    ) -> Dict[str, Any]:
        """
        Get visual learning path for a subject.
        
        Returns graph structure for visualization:
        - nodes: concepts with mastery levels
        - edges: prerequisites
        - current_position: where student is
        - next_recommended: what to learn next
        """
        try:
            # Get all masteries
            masteries = await self.mastery_tracker.get_all_masteries(user_id)
            
            # Define subject-specific learning paths
            # In production, this would come from a curriculum database
            path_definitions = self._get_curriculum_path(subject)
            
            # Build nodes with mastery
            nodes = []
            for concept in path_definitions.get("concepts", []):
                concept_id = concept.get("id")
                nodes.append({
                    "id": concept_id,
                    "name": concept.get("name"),
                    "mastery": masteries.get(concept_id, 0),
                    "status": self._get_node_status(masteries.get(concept_id, 0)),
                    "prerequisites": concept.get("prerequisites", [])
                })
            
            # Find current position and next recommended
            current = None
            next_recommended = None
            
            for node in nodes:
                if 20 <= node["mastery"] < 70:
                    current = node["id"]
                    break
            
            for node in nodes:
                if node["mastery"] < 20:
                    # Check if prerequisites are met
                    prereqs_met = all(
                        masteries.get(p, 0) >= 50
                        for p in node.get("prerequisites", [])
                    )
                    if prereqs_met:
                        next_recommended = node["id"]
                        break
            
            return {
                "subject": subject,
                "nodes": nodes,
                "edges": path_definitions.get("edges", []),
                "current_position": current,
                "next_recommended": next_recommended,
                "overall_progress": sum(n["mastery"] for n in nodes) / len(nodes) if nodes else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting learning path: {e}")
            return {}
    
    # =========================================================================
    # GAP 10: PROACTIVE OUTREACH SERVICE
    # =========================================================================
    
    async def get_proactive_nudges(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get proactive nudges for a student.
        
        These are messages the AI should proactively send:
        - "It's been 3 days since we practiced integrals"
        - "Your streak is at risk!"
        - "You've almost mastered Thermodynamics - one more session!"
        """
        nudges = []
        
        try:
            profile = await self._get_user_profile(user_id)
            
            # Check due reviews
            due_reviews = await self.continuity_engine.get_due_reviews(user_id, limit=5)
            if due_reviews:
                topics = [r.get("topic", "").replace("_", " ").title() for r in due_reviews[:2]]
                nudges.append({
                    "type": "review_reminder",
                    "priority": 2,
                    "message": f"Time to review {' and '.join(topics)}! Quick revision strengthens memory.",
                    "action": "start_review"
                })
            
            # Check streak risk
            last_active = profile.get("updated_at")
            if last_active:
                hours_since = (datetime.now(timezone.utc) - last_active).total_seconds() / 3600
                streak = profile.get("stats", {}).get("current_streak_days", 0)
                
                if hours_since > 20 and streak > 0:
                    nudges.append({
                        "type": "streak_risk",
                        "priority": 1,
                        "message": f"Your {streak}-day streak is at risk! Quick - solve one problem to keep it going!",
                        "action": "quick_problem"
                    })
            
            # Check near-mastery topics
            masteries = await self.mastery_tracker.get_all_masteries(user_id)
            for topic, level in masteries.items():
                if 80 <= level < 100:
                    nudges.append({
                        "type": "near_mastery",
                        "priority": 3,
                        "message": f"You're SO close to mastering {topic.replace('_', ' ').title()}! "
                                  f"Just {100 - level}% more!",
                        "action": "practice_topic",
                        "topic": topic
                    })
            
            # Exam urgency nudge
            exam_state = await self._get_exam_journey_state(user_id)
            if exam_state and exam_state.days_remaining and exam_state.days_remaining <= 30:
                nudges.append({
                    "type": "exam_countdown",
                    "priority": 1,
                    "message": f"Only {exam_state.days_remaining} days to {exam_state.exam_name}! "
                              f"Focus on: {', '.join(exam_state.priority_topics[:2])}",
                    "action": "exam_prep"
                })
            
            # Sort by priority
            nudges.sort(key=lambda x: x["priority"])
            
            return nudges[:5]  # Return top 5 nudges
            
        except Exception as e:
            logger.error(f"❌ Error getting proactive nudges: {e}")
            return []
    
    async def schedule_proactive_outreach(
        self,
        user_id: str,
        nudge_type: str,
        scheduled_time: datetime,
        message: str
    ):
        """Schedule a proactive outreach message"""
        try:
            outreach = {
                "user_id": user_id,
                "type": nudge_type,
                "message": message,
                "scheduled_time": scheduled_time,
                "status": "pending",
                "created_at": datetime.now(timezone.utc)
            }
            
            await self.db.scheduled_outreach.insert_one(outreach)
            
            logger.info(f"📤 Scheduled outreach for {user_id} at {scheduled_time}")
            
        except Exception as e:
            logger.error(f"❌ Error scheduling outreach: {e}")
    
    # =========================================================================
    # PRIVATE HELPER METHODS
    # =========================================================================
    
    async def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile with learning data"""
        try:
            profile = await self.db.user_learning_profile.find_one({"user_id": user_id})
            
            if profile:
                # Get name from users collection
                user = await self.db.users.find_one({"user_id": user_id})
                if user:
                    full_name = user.get("full_name", "")
                    profile["name"] = full_name.split()[0] if full_name else ""
                return profile
            
            # Return default profile
            return {
                "user_id": user_id,
                "name": "",
                "preferences": {
                    "metaphor_style": "cricket",
                    "explanation_depth": "medium",
                    "learns_better_with": "examples"
                },
                "stats": {
                    "total_questions": 0,
                    "current_streak_days": 0,
                    "total_xp": 0,
                    "level": 1
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting user profile: {e}")
            return {}
    
    async def _get_exam_journey_state(self, user_id: str) -> Optional[ExamJourneyState]:
        """Get complete exam journey state"""
        try:
            exam_target = await self.db.user_exam_targets.find_one({"user_id": user_id})
            
            if not exam_target:
                return None
            
            exam_date = exam_target.get("exam_date")
            days_remaining = None
            
            if exam_date:
                if isinstance(exam_date, str):
                    from dateutil import parser
                    exam_date = parser.parse(exam_date)
                days_remaining = (exam_date - datetime.now(timezone.utc)).days
            
            urgency = self._calculate_exam_urgency(days_remaining)
            
            # Get weak areas
            weak_topics = await self.mastery_tracker.get_weak_topics(user_id, threshold=50)
            
            # Get today's progress
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            daily_progress = await self.db.user_daily_progress.find_one({
                "user_id": user_id,
                "date": today
            })
            
            state = ExamJourneyState(
                exam_name=exam_target.get("exam_name", ""),
                exam_date=exam_date,
                days_remaining=days_remaining,
                urgency=urgency,
                daily_minutes_target=exam_target.get("daily_minutes_target", 120),
                minutes_studied_today=daily_progress.get("minutes_studied", 0) if daily_progress else 0,
                weak_areas=[w["topic"] for w in weak_topics],
                priority_topics=[w["topic"] for w in weak_topics[:3]],
                hours_needed=exam_target.get("hours_needed", {})
            )
            
            # Generate daily goal
            if days_remaining and days_remaining <= 7:
                state.daily_goal = f"CRITICAL: Focus only on {state.priority_topics[0] if state.priority_topics else 'weak areas'}!"
            elif state.priority_topics:
                state.daily_goal = f"Practice {state.priority_topics[0].replace('_', ' ').title()} today"
            else:
                state.daily_goal = "Complete your daily study target"
            
            return state
            
        except Exception as e:
            logger.error(f"❌ Error getting exam journey state: {e}")
            return None
    
    async def _get_topic_intelligence(
        self,
        user_id: str,
        query: str,
        detected_topic: str = None
    ) -> Dict[str, Any]:
        """Get intelligence about the topic being asked"""
        try:
            topic = detected_topic or self._extract_main_topic(query)
            
            mastery = await self.mastery_tracker.get_mastery_level(user_id, topic)
            weak_topics = await self.mastery_tracker.get_weak_topics(user_id, threshold=40)
            weak_list = [w["topic"] for w in weak_topics]
            
            # Count times asked before (from memory)
            times_asked = 0
            try:
                count = await self.db.user_memory_facts.count_documents({
                    "user_id": user_id,
                    "topic": topic
                })
                times_asked = count
            except:
                pass
            
            return {
                "topic": topic,
                "mastery": mastery,
                "is_weak": topic in weak_list,
                "times_asked": times_asked,
                "last_struggle": ""
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting topic intelligence: {e}")
            return {"mastery": 0, "is_weak": False, "times_asked": 0}
    
    async def _detect_current_emotion(
        self,
        query: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Detect current emotional state from query and patterns"""
        query_lower = query.lower()
        
        # Simple keyword detection (in production, use LLM)
        emotional_keywords = {
            EmotionalState.STRESSED: ["stressed", "stress", "pressure", "overwhelmed", "too much"],
            EmotionalState.ANXIOUS: ["anxious", "worried", "nervous", "scared", "fear"],
            EmotionalState.FRUSTRATED: ["frustrated", "annoyed", "angry", "stuck", "can't understand"],
            EmotionalState.CONFUSED: ["confused", "don't understand", "don't get", "unclear"],
            EmotionalState.TIRED: ["tired", "exhausted", "sleepy", "can't focus"],
            EmotionalState.MOTIVATED: ["motivated", "excited", "ready", "let's do this"],
            EmotionalState.HAPPY: ["happy", "great", "awesome", "love it", "thanks"]
        }
        
        detected = EmotionalState.NEUTRAL
        for state, keywords in emotional_keywords.items():
            if any(kw in query_lower for kw in keywords):
                detected = state
                break
        
        # Get emotional pattern
        pattern = ""
        try:
            profile = await self.db.user_emotional_profile.find_one({"user_id": user_id})
            if profile:
                pattern = profile.get("dominant_pattern", "")
        except:
            pass
        
        needs_encouragement = detected in [
            EmotionalState.STRESSED,
            EmotionalState.ANXIOUS,
            EmotionalState.FRUSTRATED,
            EmotionalState.TIRED
        ]
        
        return {
            "state": detected,
            "pattern": pattern,
            "needs_encouragement": needs_encouragement
        }
    
    async def _check_recent_achievement(self, user_id: str) -> str:
        """Check for recent achievements to celebrate"""
        try:
            recent = await self.db.user_achievements.find_one(
                {"user_id": user_id},
                sort=[("unlocked_at", -1)]
            )
            
            if recent:
                unlocked_at = recent.get("unlocked_at")
                if unlocked_at:
                    hours_since = (datetime.now(timezone.utc) - unlocked_at).total_seconds() / 3600
                    if hours_since < 24:
                        return recent.get("name", "")
            
            return ""
            
        except Exception as e:
            logger.error(f"❌ Error checking achievements: {e}")
            return ""
    
    async def _update_emotional_patterns(self, user_id: str):
        """Update emotional patterns based on history"""
        try:
            # Get last 50 emotional entries
            history = await self.db.user_emotional_history.find({
                "user_id": user_id
            }).sort("timestamp", -1).limit(50).to_list(None)
            
            if len(history) < 5:
                return
            
            # Analyze patterns
            stress_by_day = {}
            for entry in history:
                day = entry.get("day_of_week", "Unknown")
                emotion = entry.get("emotion", "neutral")
                
                if day not in stress_by_day:
                    stress_by_day[day] = {"stress": 0, "total": 0}
                
                stress_by_day[day]["total"] += 1
                if emotion in ["stressed", "anxious", "frustrated"]:
                    stress_by_day[day]["stress"] += 1
            
            # Calculate stress ratios
            stress_patterns = {
                day: data["stress"] / data["total"]
                for day, data in stress_by_day.items()
                if data["total"] > 0
            }
            
            # Find dominant pattern
            max_stress_day = max(stress_patterns, key=stress_patterns.get) if stress_patterns else None
            dominant_pattern = f"More stressed on {max_stress_day}s" if max_stress_day and stress_patterns.get(max_stress_day, 0) > 0.5 else ""
            
            # Update profile
            await self.db.user_emotional_profile.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "stress_by_day": stress_patterns,
                        "dominant_pattern": dominant_pattern,
                        "updated_at": datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"❌ Error updating emotional patterns: {e}")
    
    async def _assess_understanding(
        self,
        query: str,
        response: Dict[str, Any],
        interaction_quality: str
    ) -> str:
        """Assess understanding level from interaction"""
        # Simple heuristic (in production, use more sophisticated analysis)
        if interaction_quality == "mastered":
            return "excellent"
        elif interaction_quality == "completed":
            return "good"
        elif interaction_quality == "struggled":
            return "partial"
        else:
            return "unknown"
    
    def _calculate_mastery_delta(
        self,
        understanding: str,
        interaction_quality: str
    ) -> int:
        """Calculate mastery change based on understanding"""
        deltas = {
            "excellent": 10,
            "good": 5,
            "partial": 2,
            "poor": -3,
            "unknown": 1
        }
        return deltas.get(understanding, 0)
    
    def _calculate_xp(
        self,
        understanding: str,
        interaction_quality: str
    ) -> int:
        """Calculate XP earned"""
        base_xp = 10
        multipliers = {
            "excellent": 2.0,
            "good": 1.5,
            "partial": 1.0,
            "poor": 0.5,
            "unknown": 0.8
        }
        return int(base_xp * multipliers.get(understanding, 1.0))
    
    async def _update_xp_and_streak(self, user_id: str, xp: int) -> bool:
        """Update XP and streak"""
        try:
            profile = await self._get_user_profile(user_id)
            
            current_xp = profile.get("stats", {}).get("total_xp", 0)
            current_level = profile.get("stats", {}).get("level", 1)
            current_streak = profile.get("stats", {}).get("current_streak_days", 0)
            
            new_xp = current_xp + xp
            new_level = self._calculate_level(new_xp)
            
            # Check if streak should update
            last_active = profile.get("updated_at")
            streak_updated = False
            new_streak = current_streak
            
            if last_active:
                # Ensure last_active is timezone-aware for comparison
                if last_active.tzinfo is None:
                    last_active = last_active.replace(tzinfo=timezone.utc)
                days_since = (datetime.now(timezone.utc) - last_active).days
                if days_since == 1:
                    new_streak = current_streak + 1
                    streak_updated = True
                elif days_since > 1:
                    new_streak = 1
                    streak_updated = True
            else:
                new_streak = 1
                streak_updated = True
            
            await self.db.user_learning_profile.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "stats.total_xp": new_xp,
                        "stats.level": new_level,
                        "stats.current_streak_days": new_streak,
                        "updated_at": datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )
            
            return streak_updated
            
        except Exception as e:
            logger.error(f"❌ Error updating XP and streak: {e}")
            return False
    
    def _calculate_level(self, xp: int) -> int:
        """Calculate level from XP"""
        # Simple formula: level = 1 + xp/100
        return 1 + (xp // 100)
    
    async def _check_and_unlock_achievements(
        self,
        user_id: str,
        topic: str,
        new_mastery: int,
        streak_updated: bool
    ) -> List[str]:
        """Check and unlock achievements"""
        achievements = []
        
        try:
            # Check mastery achievements
            if new_mastery >= 100:
                achievements.append(f"Master of {topic.replace('_', ' ').title()}")
            elif new_mastery >= 50 and new_mastery < 60:
                achievements.append(f"Halfway through {topic.replace('_', ' ').title()}")
            
            # Check streak achievements
            profile = await self._get_user_profile(user_id)
            streak = profile.get("stats", {}).get("current_streak_days", 0)
            
            streak_achievements = {
                7: "Week Warrior",
                30: "Monthly Champion",
                100: "Century Legend"
            }
            
            if streak in streak_achievements:
                achievements.append(streak_achievements[streak])
            
            # Store achievements
            for achievement in achievements:
                await self.db.user_achievements.insert_one({
                    "user_id": user_id,
                    "name": achievement,
                    "unlocked_at": datetime.now(timezone.utc)
                })
            
            return achievements
            
        except Exception as e:
            logger.error(f"❌ Error checking achievements: {e}")
            return []
    
    def _decide_response_mode(
        self,
        query: str,
        magic_context: MagicContext,
        agent_type: str,
        semantic_analysis: Optional[Dict[str, Any]] = None  # PHASE B: Accept semantic analysis
    ) -> ResponseMode:
        """
        Decide the best response mode for this interaction.
        
        PHASE B FIX: Uses semantic analysis fields instead of keyword matching
        when ENABLE_SEMANTIC_MODE_SELECTION is enabled.
        """
        from core.config import settings
        
        # Emotional priority (from magic_context, not keywords)
        if magic_context.current_emotion in [EmotionalState.STRESSED, EmotionalState.ANXIOUS]:
            return ResponseMode.LISTENER
        
        # Celebratory mode for achievements
        if magic_context.recent_achievement:
            return ResponseMode.CELEBRATOR
        
        # PHASE B: Semantic-based mode selection (no keywords)
        if settings.ENABLE_SEMANTIC_MODE_SELECTION and semantic_analysis:
            # Use semantic analysis fields for mode decision
            emotional_tone = semantic_analysis.get('emotional_tone', 'neutral')
            has_actionable = semantic_analysis.get('has_actionable_request', False)
            output_type = semantic_analysis.get('requested_output_type', '')
            intent = semantic_analysis.get('intent', '')
            
            # Emotional tones → LISTENER or FRIEND
            if emotional_tone in ['anxious', 'frustrated', 'lonely', 'negative']:
                return ResponseMode.LISTENER
            if emotional_tone in ['bored', 'casual']:
                return ResponseMode.FRIEND
            
            # Actionable requests → GUIDE
            if has_actionable and output_type in ['study_plan', 'schedule', 'timetable']:
                return ResponseMode.GUIDE
            
            # Quiz/test requests → CHALLENGER
            if has_actionable and output_type in ['quiz', 'test', 'practice']:
                return ResponseMode.CHALLENGER
            
            # Greeting/chitchat → FRIEND
            if intent in ['greeting', 'chitchat', 'acknowledgment']:
                return ResponseMode.FRIEND
            
            # Default to MENTOR for educational queries
            return ResponseMode.MENTOR
        
        # LEGACY: Keyword-based mode selection (only when flag disabled)
        query_lower = query.lower()
        if "quiz" in query_lower or "test" in query_lower:
            return ResponseMode.CHALLENGER
        if "plan" in query_lower or "schedule" in query_lower:
            return ResponseMode.GUIDE
        
        # Casual detection (legacy)
        casual_indicators = ["hi", "hello", "what's up", "how are you", "bored"]
        if any(ind in query_lower for ind in casual_indicators):
            return ResponseMode.FRIEND
        
        # Default based on agent type
        return ResponseMode.MENTOR
    
    def _get_recommended_approach(
        self,
        query: str,
        topic: str,
        mastery: int,
        is_weak: bool,
        emotion: EmotionalState
    ) -> str:
        """Get recommended teaching approach"""
        if is_weak and mastery < 30:
            return "beginner_friendly"  # Use simple language, lots of examples
        elif mastery < 50:
            return "scaffolded"  # Build on basics, check understanding
        elif mastery >= 70:
            return "advanced"  # Challenge them, less hand-holding
        else:
            return "balanced"  # Standard approach
    
    def _extract_main_topic(self, text: str) -> str:
        """Extract main topic from text"""
        text_lower = text.lower()
        
        topic_keywords = {
            "newton_laws_motion": ["newton", "f=ma", "first law", "second law", "third law"],
            "force_mechanics": ["force", "friction", "tension", "normal force"],
            "kinematics": ["velocity", "acceleration", "motion", "projectile"],
            "calculus_derivatives": ["derivative", "differentiation", "d/dx", "rate of change"],
            "calculus_integrals": ["integral", "integration", "area under"],
            "limits": ["limit", "lim", "approaching"],
            "quadratic_equations": ["quadratic", "x squared", "polynomial"],
            "acids_bases": ["acid", "base", "ph", "buffer"],
            "organic_chemistry": ["organic", "carbon", "hydrocarbon"],
            "thermodynamics": ["heat", "entropy", "enthalpy", "temperature"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return topic
        
        return "general_concept"
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract all concepts from text"""
        concepts = []
        text_lower = text.lower()
        
        concept_keywords = {
            "derivatives": ["derivative", "differentiation"],
            "integrals": ["integral", "integration"],
            "limits": ["limit"],
            "newton_laws": ["newton"],
            "force": ["force"],
            "kinematics": ["velocity", "acceleration"]
        }
        
        for concept, keywords in concept_keywords.items():
            if any(kw in text_lower for kw in keywords):
                concepts.append(concept)
        
        return concepts
    
    def _calculate_exam_urgency(self, days: Optional[int]) -> ExamUrgency:
        """Calculate exam urgency level"""
        if days is None:
            return ExamUrgency.NORMAL
        if days <= 7:
            return ExamUrgency.CRITICAL
        elif days <= 30:
            return ExamUrgency.HIGH
        elif days <= 90:
            return ExamUrgency.MEDIUM
        else:
            return ExamUrgency.NORMAL
    
    async def _get_today_progress(self, user_id: str) -> Dict[str, Any]:
        """Get today's study progress"""
        try:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            progress = await self.db.user_daily_progress.find_one({
                "user_id": user_id,
                "date": today
            })
            
            if progress:
                return {
                    "minutes_studied": progress.get("minutes_studied", 0),
                    "topics_covered": progress.get("topics_covered", []),
                    "questions_answered": progress.get("questions_answered", 0)
                }
            
            return {"minutes_studied": 0, "topics_covered": [], "questions_answered": 0}
            
        except Exception as e:
            logger.error(f"❌ Error getting today progress: {e}")
            return {}
    
    async def _get_recent_achievements(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent achievements"""
        try:
            achievements = await self.db.user_achievements.find({
                "user_id": user_id
            }).sort("unlocked_at", -1).limit(limit).to_list(None)
            
            return [
                {
                    "name": a.get("name", ""),
                    "unlocked_at": a.get("unlocked_at")
                }
                for a in achievements
            ]
            
        except Exception as e:
            logger.error(f"❌ Error getting achievements: {e}")
            return []
    
    async def _get_recommended_focus(self, user_id: str) -> str:
        """Get recommended focus area"""
        try:
            weak_topics = await self.mastery_tracker.get_weak_topics(user_id, threshold=50)
            
            if weak_topics:
                top_weak = weak_topics[0]["topic"]
                return f"Focus on {top_weak.replace('_', ' ').title()} to strengthen your foundation"
            
            return "Great progress! Try tackling advanced problems"
            
        except Exception as e:
            return "Keep up the great work!"
    
    async def _generate_quiz_session(
        self,
        user_id: str,
        topic: str = None
    ) -> Dict[str, Any]:
        """Generate quiz session content"""
        # In production, this would generate actual questions
        return {
            "topic": topic or "mixed",
            "question_count": 5,
            "estimated_time_minutes": 10
        }
    
    async def _generate_practice_problems(
        self,
        user_id: str,
        topic: str = None
    ) -> List[Dict[str, Any]]:
        """Generate practice problems"""
        # In production, this would generate actual problems
        return [{
            "topic": topic or "mixed",
            "difficulty": "medium",
            "problem": "Practice problem placeholder"
        }]
    
    async def _get_next_recommended_topic(self, user_id: str) -> str:
        """Get next recommended topic to learn"""
        try:
            weak_topics = await self.mastery_tracker.get_weak_topics(user_id, threshold=70)
            
            if weak_topics:
                return weak_topics[0]["topic"]
            
            return "advanced_topics"
            
        except Exception as e:
            return "general_concepts"
    
    def _get_curriculum_path(self, subject: str) -> Dict[str, Any]:
        """Get curriculum learning path definition"""
        # Simplified curriculum paths
        # In production, this would come from a database
        paths = {
            "mathematics": {
                "concepts": [
                    {"id": "limits", "name": "Limits", "prerequisites": []},
                    {"id": "calculus_derivatives", "name": "Derivatives", "prerequisites": ["limits"]},
                    {"id": "calculus_integrals", "name": "Integrals", "prerequisites": ["calculus_derivatives"]},
                    {"id": "differential_equations", "name": "Differential Equations", "prerequisites": ["calculus_integrals"]}
                ],
                "edges": [
                    {"from": "limits", "to": "calculus_derivatives"},
                    {"from": "calculus_derivatives", "to": "calculus_integrals"},
                    {"from": "calculus_integrals", "to": "differential_equations"}
                ]
            },
            "physics": {
                "concepts": [
                    {"id": "kinematics", "name": "Kinematics", "prerequisites": []},
                    {"id": "newton_laws_motion", "name": "Newton's Laws", "prerequisites": ["kinematics"]},
                    {"id": "work_energy", "name": "Work & Energy", "prerequisites": ["newton_laws_motion"]},
                    {"id": "rotational_motion", "name": "Rotational Motion", "prerequisites": ["work_energy"]}
                ],
                "edges": [
                    {"from": "kinematics", "to": "newton_laws_motion"},
                    {"from": "newton_laws_motion", "to": "work_energy"},
                    {"from": "work_energy", "to": "rotational_motion"}
                ]
            }
        }
        
        return paths.get(subject.lower(), {"concepts": [], "edges": []})
    
    def _get_node_status(self, mastery: int) -> str:
        """Get node status from mastery level"""
        if mastery >= 80:
            return "mastered"
        elif mastery >= 50:
            return "learning"
        elif mastery > 0:
            return "started"
        else:
            return "locked"


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def get_student_intelligence_hub(db) -> StudentIntelligenceHub:
    """Factory function to create StudentIntelligenceHub"""
    return StudentIntelligenceHub(db)



