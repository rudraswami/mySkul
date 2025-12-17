"""
🎓 Student State Engine - Mastery-Driven Depth Adaptation
=========================================================

This engine makes depth depend on STUDENT STATE, not keywords.

CURRENT PROBLEM:
- Depth is determined by question keywords ("derive" = deep, "what is" = simple)
- Same question → same depth, regardless of who's asking
- Beginner and expert get the same explanation

SOLUTION:
- Track student's mastery level per topic
- Track confusion history (where they've struggled)
- Track learning velocity (how fast they learn)
- ADAPT depth based on student state, not question

A beginner asking "What is momentum?" gets a gentle introduction.
An expert asking "What is momentum?" gets a concise refresher + advanced insight.

THIS IS WHAT MAKES US DIFFERENT FROM CHATBOTS.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class StudentLevel(Enum):
    """Student understanding level for a topic"""
    NOVICE = "novice"           # 0-20 mastery - needs basics
    BEGINNER = "beginner"       # 21-40 mastery - building foundation
    DEVELOPING = "developing"   # 41-60 mastery - gaining confidence
    PROFICIENT = "proficient"   # 61-80 mastery - solid understanding
    EXPERT = "expert"           # 81-100 mastery - advanced insights


class ConfusionPattern(Enum):
    """Types of confusion patterns"""
    CONCEPTUAL = "conceptual"       # Doesn't understand the concept
    PROCEDURAL = "procedural"       # Doesn't know how to apply
    MATHEMATICAL = "mathematical"   # Struggles with math parts
    TERMINOLOGY = "terminology"     # Confused by terms
    CONNECTIONS = "connections"     # Can't connect to other concepts


@dataclass
class StudentState:
    """Complete state of a student for a topic"""
    user_id: str
    topic: str
    mastery_level: int              # 0-100
    student_level: StudentLevel     # Classification
    confusion_history: List[str]    # Recent confusion points
    learning_velocity: float        # How fast they learn (1.0 = normal)
    last_interaction: Optional[datetime]
    consecutive_successes: int      # Streak of successful teach-backs
    consecutive_struggles: int      # Streak of struggles
    preferred_style: str            # analogy, formal, step-by-step, visual
    emotion_state: str              # confident, anxious, curious, frustrated


@dataclass
class DepthRecommendation:
    """Recommended response depth based on student state"""
    depth: str                      # surface, moderate, deep, expert
    explanation_style: str          # intuitive, balanced, rigorous
    include_basics: bool            # Should we include foundational info?
    include_advanced: bool          # Should we include advanced insights?
    use_analogies: bool             # Should we use analogies?
    step_by_step: bool              # Should we break into steps?
    encourage_first: bool           # Should we encourage before explaining?
    max_complexity: str             # simple, moderate, complex
    suggested_examples: str         # daily_life, academic, exam_oriented
    tone: str                       # supportive, neutral, challenging


class StudentStateEngine:
    """
    Engine that tracks and uses student state for adaptive responses.
    
    This is the CORE of personalization.
    Every response is shaped by WHO is asking, not just WHAT they're asking.
    """
    
    def __init__(self, db):
        self.db = db
        logger.info("🎓 StudentStateEngine initialized - Adaptive depth active")
    
    async def get_student_state(
        self,
        user_id: str,
        topic: str,
        subject: str = "General"
    ) -> StudentState:
        """
        Get complete student state for a topic.
        
        This is the foundation for adaptive responses.
        """
        # Get learning profile
        profile = await self.db.user_learning_profile.find_one({"user_id": user_id})
        
        if not profile:
            # Create default profile
            return self._create_default_state(user_id, topic)
        
        # Get mastery level
        topic_key = self._normalize_topic(topic)
        mastery = profile.get("mastery_levels", {}).get(topic_key, 30)
        
        # Get confusion history
        confusion_history = await self._get_confusion_history(user_id, topic)
        
        # Calculate learning velocity
        velocity = await self._calculate_learning_velocity(user_id, topic)
        
        # Get streaks
        successes, struggles = await self._get_streaks(user_id, topic)
        
        # Get preferred style
        preferred_style = profile.get("preferences", {}).get("learning_style", "balanced")
        
        # Get emotion state (from recent interactions)
        emotion = await self._detect_emotion_state(user_id)
        
        # Get last interaction
        last_interaction = profile.get("last_topics", {}).get(topic_key, {}).get("timestamp")
        
        state = StudentState(
            user_id=user_id,
            topic=topic,
            mastery_level=mastery,
            student_level=self._mastery_to_level(mastery),
            confusion_history=confusion_history,
            learning_velocity=velocity,
            last_interaction=last_interaction,
            consecutive_successes=successes,
            consecutive_struggles=struggles,
            preferred_style=preferred_style,
            emotion_state=emotion
        )
        
        logger.info(f"📊 Student state: {state.student_level.value}, mastery={mastery}, velocity={velocity:.2f}")
        
        return state
    
    def recommend_depth(
        self,
        student_state: StudentState,
        question_intent: str = "concept"
    ) -> DepthRecommendation:
        """
        Recommend response depth based on student state.
        
        THIS IS THE KEY FUNCTION.
        It determines how deep/simple the response should be.
        """
        level = student_state.student_level
        mastery = student_state.mastery_level
        velocity = student_state.learning_velocity
        struggles = student_state.consecutive_struggles
        emotion = student_state.emotion_state
        
        # Base recommendations by level
        if level == StudentLevel.NOVICE:
            depth = "surface"
            style = "intuitive"
            include_basics = True
            include_advanced = False
            use_analogies = True
            step_by_step = True
            encourage = True
            max_complexity = "simple"
            examples = "daily_life"
            tone = "supportive"
        
        elif level == StudentLevel.BEGINNER:
            depth = "surface" if struggles > 1 else "moderate"
            style = "intuitive"
            include_basics = True
            include_advanced = False
            use_analogies = True
            step_by_step = struggles > 0
            encourage = struggles > 0
            max_complexity = "simple"
            examples = "daily_life"
            tone = "supportive"
        
        elif level == StudentLevel.DEVELOPING:
            depth = "moderate"
            style = "balanced"
            include_basics = struggles > 1
            include_advanced = velocity > 1.2
            use_analogies = True
            step_by_step = False
            encourage = False
            max_complexity = "moderate"
            examples = "academic"
            tone = "neutral"
        
        elif level == StudentLevel.PROFICIENT:
            depth = "deep" if velocity > 1.0 else "moderate"
            style = "balanced"
            include_basics = False
            include_advanced = True
            use_analogies = False  # They don't need them
            step_by_step = False
            encourage = False
            max_complexity = "complex"
            examples = "exam_oriented"
            tone = "neutral"
        
        else:  # EXPERT
            depth = "expert"
            style = "rigorous"
            include_basics = False
            include_advanced = True
            use_analogies = False
            step_by_step = False
            encourage = False
            max_complexity = "complex"
            examples = "exam_oriented"
            tone = "challenging"
        
        # Adjust for emotion state
        if emotion == "anxious" or emotion == "frustrated":
            depth = self._reduce_depth(depth)
            encourage = True
            tone = "supportive"
            step_by_step = True
        
        elif emotion == "curious":
            include_advanced = True
            if depth != "expert":
                depth = self._increase_depth(depth)
        
        # Adjust for learning velocity
        if velocity < 0.7:  # Slow learner
            depth = self._reduce_depth(depth)
            step_by_step = True
            use_analogies = True
        
        elif velocity > 1.5:  # Fast learner
            depth = self._increase_depth(depth)
            include_advanced = True
        
        # Adjust for question intent
        if question_intent == "exam":
            examples = "exam_oriented"
            include_advanced = level in [StudentLevel.PROFICIENT, StudentLevel.EXPERT]
        
        elif question_intent == "intuition":
            use_analogies = True
            style = "intuitive"
        
        recommendation = DepthRecommendation(
            depth=depth,
            explanation_style=style,
            include_basics=include_basics,
            include_advanced=include_advanced,
            use_analogies=use_analogies,
            step_by_step=step_by_step,
            encourage_first=encourage,
            max_complexity=max_complexity,
            suggested_examples=examples,
            tone=tone
        )
        
        logger.info(f"📝 Depth recommendation: {depth}, style={style}, basics={include_basics}, advanced={include_advanced}")
        
        return recommendation
    
    def build_depth_prompt(self, recommendation: DepthRecommendation) -> str:
        """
        Build prompt additions based on depth recommendation.
        
        This is injected into the system prompt to guide the LLM.
        """
        prompts = []
        
        # Depth guidance
        depth_guidance = {
            "surface": "Keep the explanation simple and accessible. Use basic vocabulary. Focus on the core idea only.",
            "moderate": "Provide a balanced explanation. Cover the main concept and important details.",
            "deep": "Give a thorough explanation. Include nuances, edge cases, and deeper insights.",
            "expert": "Provide an advanced explanation. Assume strong foundation. Focus on sophisticated aspects and exam-level insights."
        }
        prompts.append(depth_guidance.get(recommendation.depth, ""))
        
        # Style guidance
        if recommendation.explanation_style == "intuitive":
            prompts.append("Use intuitive explanations. Start with 'why' before 'what'. Build mental models.")
        elif recommendation.explanation_style == "rigorous":
            prompts.append("Be precise and rigorous. Use proper terminology. Include mathematical formalism where relevant.")
        
        # Basics
        if recommendation.include_basics:
            prompts.append("Include foundational context - don't assume prior knowledge.")
        else:
            prompts.append("Skip basics - student already has a foundation.")
        
        # Advanced
        if recommendation.include_advanced:
            prompts.append("Include advanced insights, connections to other topics, and exam-level perspectives.")
        
        # Analogies
        if recommendation.use_analogies:
            prompts.append("Use relatable analogies (cricket, cooking, daily life) to illustrate concepts.")
        
        # Step by step
        if recommendation.step_by_step:
            prompts.append("Break down into clear steps. One idea at a time.")
        
        # Encourage
        if recommendation.encourage_first:
            prompts.append("Start with encouragement. Acknowledge this can be tricky. Build confidence.")
        
        # Tone
        if recommendation.tone == "supportive":
            prompts.append("Use a warm, supportive tone. Be patient.")
        elif recommendation.tone == "challenging":
            prompts.append("Challenge the student intellectually. Push for deeper thinking.")
        
        # Examples
        if recommendation.suggested_examples == "daily_life":
            prompts.append("Use everyday examples the student can relate to.")
        elif recommendation.suggested_examples == "exam_oriented":
            prompts.append("Include exam-relevant examples and problem patterns.")
        
        return "\n".join(filter(None, prompts))
    
    async def update_student_state(
        self,
        user_id: str,
        topic: str,
        interaction_type: str,  # question, teach_back, struggle, success
        details: Dict[str, Any] = None
    ):
        """
        Update student state after an interaction.
        """
        topic_key = self._normalize_topic(topic)
        details = details or {}
        
        update_doc = {
            "$set": {
                f"last_topics.{topic_key}": {
                    "timestamp": datetime.now(timezone.utc),
                    "interaction_type": interaction_type
                },
                "updated_at": datetime.now(timezone.utc)
            }
        }
        
        # Track confusion if struggle
        if interaction_type == "struggle":
            update_doc["$push"] = {
                "confusion_events": {
                    "topic": topic,
                    "timestamp": datetime.now(timezone.utc),
                    "details": details.get("confusion_point", "")
                }
            }
        
        await self.db.user_learning_profile.update_one(
            {"user_id": user_id},
            update_doc,
            upsert=True
        )
        
        logger.info(f"📝 Student state updated: {interaction_type} for {topic}")
    
    async def _get_confusion_history(
        self,
        user_id: str,
        topic: str,
        limit: int = 5
    ) -> List[str]:
        """Get recent confusion points for this topic."""
        profile = await self.db.user_learning_profile.find_one({"user_id": user_id})
        
        if not profile:
            return []
        
        confusion_events = profile.get("confusion_events", [])
        topic_lower = topic.lower()
        
        relevant = [
            e.get("details", "")
            for e in confusion_events[-20:]  # Check last 20
            if topic_lower in e.get("topic", "").lower()
        ]
        
        return relevant[-limit:]
    
    async def _calculate_learning_velocity(
        self,
        user_id: str,
        topic: str
    ) -> float:
        """
        Calculate how fast the student learns.
        
        1.0 = normal, <1.0 = slower, >1.0 = faster
        """
        # Get teach-back history
        cursor = self.db.teach_back_requests.find(
            {"user_id": user_id, "status": "evaluated"},
            sort=[("evaluated_at", -1)],
            limit=10
        )
        
        scores = []
        timestamps = []
        
        async for doc in cursor:
            eval_data = doc.get("evaluation", {})
            if eval_data.get("score"):
                scores.append(eval_data["score"])
                timestamps.append(doc.get("evaluated_at"))
        
        if len(scores) < 3:
            return 1.0  # Not enough data
        
        # Calculate improvement rate
        recent_avg = sum(scores[:5]) / min(5, len(scores))
        older_avg = sum(scores[5:]) / max(1, len(scores) - 5) if len(scores) > 5 else recent_avg
        
        if older_avg > 0:
            improvement = recent_avg / older_avg
        else:
            improvement = 1.0
        
        # Normalize to 0.5-2.0 range
        velocity = max(0.5, min(2.0, improvement))
        
        return velocity
    
    async def _get_streaks(
        self,
        user_id: str,
        topic: str
    ) -> tuple:
        """Get consecutive successes and struggles."""
        # Get recent teach-backs for this topic
        topic_lower = topic.lower()
        
        cursor = self.db.teach_back_requests.find(
            {"user_id": user_id, "status": "evaluated"},
            sort=[("evaluated_at", -1)],
            limit=10
        )
        
        successes = 0
        struggles = 0
        streak_type = None
        
        async for doc in cursor:
            if topic_lower not in doc.get("concept_name", "").lower():
                continue
            
            score = doc.get("evaluation", {}).get("score", 50)
            
            if streak_type is None:
                streak_type = "success" if score >= 70 else "struggle"
            
            if score >= 70:
                if streak_type == "success":
                    successes += 1
                else:
                    break
            else:
                if streak_type == "struggle":
                    struggles += 1
                else:
                    break
        
        return successes, struggles
    
    async def _detect_emotion_state(self, user_id: str) -> str:
        """Detect student's current emotional state from recent interactions."""
        # Get recent messages
        cursor = self.db.session_messages.find(
            {"user_id": user_id},
            sort=[("timestamp", -1)],
            limit=5
        )
        
        anxiety_indicators = ["help", "stuck", "confused", "don't understand", "struggling"]
        frustration_indicators = ["not working", "still don't", "why won't", "impossible"]
        curiosity_indicators = ["what if", "how does", "why do", "interesting", "tell me more"]
        
        async for doc in cursor:
            message = doc.get("content", "").lower()
            
            if any(ind in message for ind in frustration_indicators):
                return "frustrated"
            if any(ind in message for ind in anxiety_indicators):
                return "anxious"
            if any(ind in message for ind in curiosity_indicators):
                return "curious"
        
        return "neutral"
    
    def _mastery_to_level(self, mastery: int) -> StudentLevel:
        """Convert mastery score to student level."""
        if mastery <= 20:
            return StudentLevel.NOVICE
        elif mastery <= 40:
            return StudentLevel.BEGINNER
        elif mastery <= 60:
            return StudentLevel.DEVELOPING
        elif mastery <= 80:
            return StudentLevel.PROFICIENT
        else:
            return StudentLevel.EXPERT
    
    def _normalize_topic(self, topic: str) -> str:
        """Normalize topic name for storage."""
        import re
        return re.sub(r'[^a-z0-9]+', '_', topic.lower())
    
    def _reduce_depth(self, depth: str) -> str:
        """Reduce depth by one level."""
        order = ["surface", "moderate", "deep", "expert"]
        idx = order.index(depth) if depth in order else 1
        return order[max(0, idx - 1)]
    
    def _increase_depth(self, depth: str) -> str:
        """Increase depth by one level."""
        order = ["surface", "moderate", "deep", "expert"]
        idx = order.index(depth) if depth in order else 1
        return order[min(len(order) - 1, idx + 1)]
    
    def _create_default_state(self, user_id: str, topic: str) -> StudentState:
        """Create default state for new student/topic."""
        return StudentState(
            user_id=user_id,
            topic=topic,
            mastery_level=30,  # Assume beginner
            student_level=StudentLevel.BEGINNER,
            confusion_history=[],
            learning_velocity=1.0,
            last_interaction=None,
            consecutive_successes=0,
            consecutive_struggles=0,
            preferred_style="balanced",
            emotion_state="neutral"
        )


# Singleton
_student_state_engine: Optional[StudentStateEngine] = None


def get_student_state_engine(db) -> StudentStateEngine:
    """Get or create the student state engine."""
    global _student_state_engine
    if _student_state_engine is None:
        _student_state_engine = StudentStateEngine(db)
    return _student_state_engine
