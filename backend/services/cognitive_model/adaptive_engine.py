"""
Adaptive Engine - Orchestrates Personalized Learning
=====================================================

The heart of the Cognitive OS - brings together:
- Knowledge tracking
- Mastery estimation
- Learning pattern analysis

To provide truly personalized, adaptive education.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timezone

from .knowledge_tracker import KnowledgeTracker
from .mastery_model import MasteryModel
from .learning_patterns import LearningPatternAnalyzer, LearningProfile

logger = logging.getLogger(__name__)


@dataclass
class AdaptiveContext:
    """Context for adapting AI responses to a specific student"""
    user_id: str
    
    # Knowledge state
    current_topic_mastery: float
    related_topics_mastery: Dict[str, float]
    knowledge_gaps: List[str]
    
    # Learning profile
    primary_learning_style: str
    include_visuals: bool
    include_examples: bool
    include_practice: bool
    explanation_depth: str
    use_metaphors: str
    
    # Personalization
    difficulty_level: str  # "easier", "appropriate", "challenging"
    focus_areas: List[str]  # Concepts to emphasize
    avoid_areas: List[str]  # Areas student is frustrated with
    
    # Engagement
    current_session_length: int
    optimal_session_length: int
    engagement_status: str  # "engaged", "neutral", "disengaged"
    
    # Recommendations
    recommended_next_topics: List[str]
    review_needed: List[str]


class AdaptiveEngine:
    """
    Main orchestrator for adaptive learning.
    
    Combines all cognitive model components to:
    1. Understand where the student is
    2. Determine optimal next steps
    3. Personalize content delivery
    4. Track and adapt in real-time
    """
    
    def __init__(self, db=None):
        """Initialize with optional database connection"""
        self.db = db
        self.knowledge_tracker = KnowledgeTracker(db)
        self.mastery_model = MasteryModel()
        self.learning_analyzer = LearningPatternAnalyzer(db)
        
        logger.info("🧠 AdaptiveEngine initialized - Cognitive OS ready")
    
    async def get_adaptive_context(
        self,
        user_id: str,
        subject: str,
        topic: str,
        current_session_length: int = 0
    ) -> AdaptiveContext:
        """
        Get complete adaptive context for personalizing a response.
        
        This is called before generating any AI response to understand
        exactly how to tailor the content for this student.
        
        Args:
            user_id: Student's user ID
            subject: Current subject
            topic: Current topic
            current_session_length: Minutes in current session
            
        Returns:
            AdaptiveContext with all personalization parameters
        """
        # Get knowledge state
        knowledge = await self.knowledge_tracker.get_student_knowledge(user_id, subject)
        current_mastery = await self.knowledge_tracker.get_mastery_level(user_id, subject, topic)
        
        # Get related topics mastery
        related_mastery = {}
        if knowledge.get("subjects", {}).get(subject, {}).get("topics"):
            for t_name, t_data in knowledge["subjects"][subject]["topics"].items():
                if t_name != topic:
                    related_mastery[t_name] = t_data.get("mastery", 0.0)
        
        # Get learning profile
        profile = await self.learning_analyzer.get_learning_profile(user_id)
        adaptations = await self.learning_analyzer.get_adaptation_recommendations(user_id)
        
        # Get weak areas
        weak_areas = await self.knowledge_tracker.get_weak_areas(user_id, subject, limit=3)
        knowledge_gaps = [w["topic"] for w in weak_areas]
        
        # Get review queue
        review_queue = await self.knowledge_tracker.get_review_queue(user_id, limit=5)
        review_needed = [r["concept"] for r in review_queue]
        
        # Determine difficulty level
        if current_mastery < 0.3:
            difficulty = "easier"
        elif current_mastery > 0.8:
            difficulty = "challenging"
        else:
            difficulty = "appropriate"
        
        # Determine engagement status
        if current_session_length > profile.optimal_session_duration * 1.5:
            engagement = "potentially_fatigued"
        elif current_session_length < 5:
            engagement = "just_started"
        else:
            engagement = "engaged"
        
        # Get recommended next topics
        recommended = knowledge.get("recommended_topics", [])
        next_topics = [r["topic"] for r in recommended[:3]] if recommended else []
        
        return AdaptiveContext(
            user_id=user_id,
            current_topic_mastery=current_mastery,
            related_topics_mastery=related_mastery,
            knowledge_gaps=knowledge_gaps,
            primary_learning_style=adaptations.get("primary_style", "balanced"),
            include_visuals=adaptations.get("include_visuals", True),
            include_examples=adaptations.get("include_examples", True),
            include_practice=adaptations.get("include_practice", False),
            explanation_depth=adaptations.get("explanation_depth", "balanced"),
            use_metaphors=adaptations.get("use_metaphors", "cricket"),
            difficulty_level=difficulty,
            focus_areas=knowledge_gaps[:2],  # Focus on gaps
            avoid_areas=[],  # Could be populated from frustration signals
            current_session_length=current_session_length,
            optimal_session_length=profile.optimal_session_duration,
            engagement_status=engagement,
            recommended_next_topics=next_topics,
            review_needed=review_needed
        )
    
    async def adapt_prompt(
        self,
        base_prompt: str,
        context: AdaptiveContext,
        mistake_patterns: List[str] = None,
        days_to_exam: int = None,
        exam_name: str = None
    ) -> str:
        """
        Adapt an AI prompt based on student context.
        
        Injects personalization instructions into the prompt.
        
        Args:
            base_prompt: Original system prompt
            context: AdaptiveContext with personalization parameters
            mistake_patterns: Error Genome™ - common mistake types
            days_to_exam: Days remaining to exam
            exam_name: Name of target exam
            
        Returns:
            Enhanced prompt with personalization
        """
        # Build adaptation block
        adaptations = []
        
        # Learning style
        style = context.primary_learning_style
        if style == "visual":
            adaptations.append("- Include visual descriptions and suggest diagrams")
        elif style == "example":
            adaptations.append("- Lead with concrete examples before theory")
        elif style == "interactive":
            adaptations.append("- Include practice problems or thought exercises")
        elif style == "conceptual":
            adaptations.append("- Focus on underlying principles and 'why'")
        
        # Difficulty adjustment
        if context.difficulty_level == "easier":
            adaptations.append("- Use simpler language and break into smaller steps")
            adaptations.append("- Start with basic concepts before advancing")
        elif context.difficulty_level == "challenging":
            adaptations.append("- Include advanced applications and edge cases")
            adaptations.append("- Challenge with deeper questions")
        
        # Knowledge gaps
        if context.knowledge_gaps:
            gaps_str = ", ".join(context.knowledge_gaps[:2])
            adaptations.append(f"- Student has gaps in: {gaps_str}. Build connections to these.")
        
        # Session fatigue
        if context.engagement_status == "potentially_fatigued":
            adaptations.append("- Keep response concise - student may be fatigued")
            adaptations.append("- Consider suggesting a break")
        
        # Review reminders
        if context.review_needed:
            review_str = ", ".join(context.review_needed[:2])
            adaptations.append(f"- If relevant, briefly connect to: {review_str} (needs review)")
        
        # ==========================================================
        # ERROR GENOME™ - Mistake Pattern Awareness (Phase 1)
        # ==========================================================
        if mistake_patterns:
            mistake_guidance = []
            for pattern in mistake_patterns[:3]:
                if pattern == "calculation_error":
                    mistake_guidance.append("calculation errors - emphasize step-by-step arithmetic")
                elif pattern == "conceptual_confusion":
                    mistake_guidance.append("conceptual confusion - clarify the 'why' before 'how'")
                elif pattern == "formula_misuse":
                    mistake_guidance.append("formula misapplication - explain when each formula applies")
                elif pattern == "sign_error":
                    mistake_guidance.append("sign errors - highlight direction conventions")
                elif pattern == "unit_error":
                    mistake_guidance.append("unit errors - emphasize unit conversions")
            if mistake_guidance:
                adaptations.append(f"- ⚠️ ERROR GENOME: Watch for {', '.join(mistake_guidance)}")
        
        # ==========================================================
        # EXAM URGENCY AWARENESS (Phase 1)
        # ==========================================================
        if days_to_exam is not None and days_to_exam <= 90:
            if days_to_exam <= 7:
                adaptations.append(f"- 🚨 CRITICAL: Only {days_to_exam} days to {exam_name}! Focus on high-yield, exam-ready content.")
            elif days_to_exam <= 30:
                adaptations.append(f"- ⏰ URGENT: {days_to_exam} days to {exam_name}. Reference time naturally in response.")
            else:
                adaptations.append(f"- 📅 Preparing for {exam_name} in {days_to_exam} days. Connect to exam relevance.")
        
        # Build the adaptation section
        if adaptations:
            adaptation_section = f"""

PERSONALIZATION FOR THIS STUDENT:
{chr(10).join(adaptations)}

Current mastery of this topic: {context.current_topic_mastery:.0%}

TRUST SIGNALS (use 1-2 naturally):
- "Based on your learning patterns..."
- "MySckul noticed..."
- "From your previous sessions..."
"""
            return base_prompt + adaptation_section
        
        return base_prompt
    
    async def record_response_interaction(
        self,
        user_id: str,
        subject: str,
        topic: str,
        concepts_covered: List[str],
        response_type: str,
        engagement_signals: Dict[str, Any] = None
    ) -> None:
        """
        Record a response interaction to update the cognitive model.
        
        Called after every AI response to update:
        - Knowledge tracking
        - Learning patterns
        - Session data
        
        Args:
            user_id: Student's user ID
            subject: Subject area
            topic: Topic covered
            concepts_covered: List of concepts in the response
            response_type: Type of response (explanation, example, visual, etc.)
            engagement_signals: Engagement data from frontend
        """
        engagement = engagement_signals or {}
        
        # Update knowledge tracker
        # Assume exposure = learning (performance tracked separately)
        performance = {concept: True for concept in concepts_covered}
        await self.knowledge_tracker.record_interaction(
            user_id=user_id,
            subject=subject,
            topic=topic,
            concepts=concepts_covered,
            performance=performance
        )
        
        # Update learning patterns
        await self.learning_analyzer.record_interaction(
            user_id=user_id,
            interaction_type=response_type,
            topic=topic,
            subject=subject,
            duration_seconds=engagement.get("view_duration", 10),
            engagement_signals=engagement
        )
        
        # Update mastery model
        for concept in concepts_covered:
            skill_id = f"{subject}:{topic}:{concept}".lower().replace(" ", "_")
            # For viewing, we assume slight positive update
            self.mastery_model.update_mastery(
                user_id=user_id,
                skill_id=skill_id,
                correct=True  # Viewing = positive exposure
            )
        
        logger.info(f"📊 Updated cognitive model for {user_id}: {topic} ({len(concepts_covered)} concepts)")
    
    async def record_assessment(
        self,
        user_id: str,
        subject: str,
        topic: str,
        concept: str,
        correct: bool,
        mistake_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record an assessment result (quiz, practice problem).
        
        This is the primary way to update mastery - actual performance data.
        
        Args:
            user_id: Student's user ID
            subject: Subject area
            topic: Topic
            concept: Specific concept tested
            correct: Whether the answer was correct
            mistake_type: Type of mistake if incorrect
            
        Returns:
            Updated mastery information
        """
        skill_id = f"{subject}:{topic}:{concept}".lower().replace(" ", "_")
        
        # Update mastery model
        estimate = self.mastery_model.update_mastery(
            user_id=user_id,
            skill_id=skill_id,
            correct=correct
        )
        
        # Update knowledge tracker
        await self.knowledge_tracker.record_interaction(
            user_id=user_id,
            subject=subject,
            topic=topic,
            concepts=[concept],
            performance={concept: correct}
        )
        
        # Record mistake pattern
        if not correct and mistake_type:
            await self.learning_analyzer.record_mistake(
                user_id=user_id,
                mistake_type=mistake_type,
                topic=topic,
                subject=subject
            )
        
        return {
            "skill_id": skill_id,
            "new_mastery": estimate.p_mastery,
            "confidence": estimate.confidence,
            "predicted_next_correct": estimate.predicted_correct,
            "is_mastered": estimate.p_mastery >= 0.85
        }
    
    async def get_recommended_content(
        self,
        user_id: str,
        subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get recommended content for a student.
        
        Returns:
            Dict with recommended topics, review items, and practice areas
        """
        # Get knowledge state
        knowledge = await self.knowledge_tracker.get_student_knowledge(user_id, subject)
        
        # Get weak areas
        weak_areas = await self.knowledge_tracker.get_weak_areas(user_id, subject)
        
        # Get review queue
        review_queue = await self.knowledge_tracker.get_review_queue(user_id)
        
        # Get ready for advancement
        ready = self.mastery_model.get_ready_for_advancement(user_id)
        
        return {
            "user_id": user_id,
            "overall_mastery": knowledge.get("overall_mastery", 0),
            "weak_areas": weak_areas,
            "needs_review": review_queue,
            "ready_for_advancement": [
                {"skill": skill, "mastery": mastery}
                for skill, mastery in ready
            ],
            "recommended_topics": knowledge.get("recommended_topics", []),
            "knowledge_gaps": knowledge.get("knowledge_gaps", []),
            "study_suggestion": self._generate_study_suggestion(
                knowledge, weak_areas, review_queue
            )
        }
    
    async def get_session_summary(
        self,
        user_id: str,
        session_topics: List[str],
        session_duration: int
    ) -> Dict[str, Any]:
        """
        Generate end-of-session summary and recommendations.
        
        Args:
            user_id: Student's user ID
            session_topics: Topics covered in session
            session_duration: Session length in minutes
            
        Returns:
            Summary with progress and next steps
        """
        # Get current knowledge state
        knowledge = await self.knowledge_tracker.get_student_knowledge(user_id)
        profile = await self.learning_analyzer.get_learning_profile(user_id)
        
        # Calculate session progress
        topic_progress = {}
        for topic in session_topics:
            # Find topic in knowledge
            for subject, subj_data in knowledge.get("subjects", {}).items():
                if topic in subj_data.get("topics", {}):
                    topic_progress[topic] = subj_data["topics"][topic].get("mastery", 0.5)
        
        # Record session
        await self.learning_analyzer.record_session(user_id, {
            "start_time": datetime.now(timezone.utc).isoformat(),
            "duration_minutes": session_duration,
            "questions_asked": len(session_topics),
            "topics_covered": session_topics,
            "engagement_score": 0.7,  # Default, should come from frontend
            "performance_score": sum(topic_progress.values()) / max(1, len(topic_progress))
        })
        
        return {
            "session_duration": session_duration,
            "topics_covered": len(session_topics),
            "topic_progress": topic_progress,
            "overall_mastery": knowledge.get("overall_mastery", 0),
            "concepts_learned": knowledge.get("total_concepts_learned", 0),
            "optimal_next_session": profile.optimal_session_duration,
            "recommended_next": knowledge.get("recommended_topics", [])[:3],
            "encouragement": self._generate_encouragement(session_duration, topic_progress)
        }
    
    def _generate_study_suggestion(
        self,
        knowledge: Dict,
        weak_areas: List,
        review_queue: List
    ) -> str:
        """Generate personalized study suggestion"""
        if weak_areas:
            top_weak = weak_areas[0]
            return f"Focus on {top_weak['topic']} in {top_weak['subject']} - currently at {top_weak['mastery']:.0%} mastery."
        
        if review_queue:
            top_review = review_queue[0]
            return f"Time to review {top_review['concept']} ({top_review['topic']})."
        
        if knowledge.get("overall_mastery", 0) > 0.8:
            return "Great progress! Try some challenging problems to push further."
        
        return "Keep up the good work! Consistent practice leads to mastery."
    
    def _generate_encouragement(
        self,
        duration: int,
        progress: Dict[str, float]
    ) -> str:
        """Generate encouraging end-of-session message"""
        avg_progress = sum(progress.values()) / max(1, len(progress))
        
        if duration >= 30 and avg_progress >= 0.7:
            return "Amazing session! 🎉 You're making excellent progress!"
        elif duration >= 20:
            return "Great job staying focused! 💪 Consistency is key."
        elif avg_progress >= 0.8:
            return "Strong understanding! 🌟 Keep it up!"
        else:
            return "Good effort! 📚 Every session moves you forward."


# ============================================================================
# FACTORY & SINGLETON
# ============================================================================

_adaptive_engine: Optional[AdaptiveEngine] = None


def get_adaptive_engine(db=None) -> AdaptiveEngine:
    """Get or create the adaptive engine singleton"""
    global _adaptive_engine
    if _adaptive_engine is None:
        _adaptive_engine = AdaptiveEngine(db)
    return _adaptive_engine

