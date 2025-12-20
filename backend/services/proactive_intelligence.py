"""
🧠 Proactive Intelligence Engine - Makes AI Truly Intelligent
==============================================================

This engine transforms the AI from a reactive Q&A bot to a proactive mentor that:
1. Notices patterns and suggests actions
2. References past sessions naturally
3. Detects engagement and adapts
4. Offers timely recommendations
5. Celebrates progress and milestones

PHILOSOPHY: A great mentor doesn't just answer - they anticipate, guide, and support.
"""

import logging
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ProactiveActionType(Enum):
    """Types of proactive actions the AI can take"""
    CONTINUITY_REFERENCE = "continuity"      # "Last time we discussed..."
    REVIEW_SUGGESTION = "review"             # "Time to review X"
    PROGRESS_CELEBRATION = "progress"        # "You've improved at Y!"
    BREAK_SUGGESTION = "break"               # "You've been at this a while..."
    TOPIC_RECOMMENDATION = "recommend"       # "Based on your progress, try..."
    WEAK_AREA_NUDGE = "weak_area"           # "Let's strengthen your understanding of..."
    STREAK_MOTIVATION = "streak"             # "5-day streak! Keep it up!"
    QUIZ_SUGGESTION = "quiz"                 # "Want to test yourself?"
    MILESTONE_CELEBRATION = "milestone"      # "100 questions answered!"


@dataclass
class ProactiveInsight:
    """A proactive insight the AI should share"""
    action_type: ProactiveActionType
    message: str
    priority: int  # 1-10, higher = more important
    data: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.action_type.value,
            "message": self.message,
            "priority": self.priority,
            "data": self.data or {}
        }


class ProactiveIntelligenceEngine:
    """
    Engine that generates proactive insights and suggestions.
    
    This is what makes the AI feel like a real mentor - it notices things,
    remembers context, and offers guidance without being asked.
    """
    
    def __init__(self, db=None):
        self.db = db
        logger.info("🧠 ProactiveIntelligenceEngine initialized")
    
    async def get_proactive_insights(
        self,
        user_id: str,
        session_id: str,
        current_question: str,
        memory_context: Dict[str, Any],
        session_duration_mins: int = 0
    ) -> List[ProactiveInsight]:
        """
        Generate proactive insights based on current context.
        
        Returns list of insights ordered by priority.
        """
        insights = []
        
        # 1. Cross-session continuity
        continuity_insight = await self._check_session_continuity(
            user_id, session_id, current_question, memory_context
        )
        if continuity_insight:
            insights.append(continuity_insight)
        
        # 2. Spaced repetition / review needed
        review_insight = await self._check_review_needed(user_id, memory_context)
        if review_insight:
            insights.append(review_insight)
        
        # 3. Session duration / break suggestion
        break_insight = self._check_break_needed(session_duration_mins)
        if break_insight:
            insights.append(break_insight)
        
        # 4. Progress celebration
        progress_insight = await self._check_progress_milestones(user_id, memory_context)
        if progress_insight:
            insights.append(progress_insight)
        
        # 5. Weak area nudge
        weak_insight = await self._check_weak_areas(user_id, current_question, memory_context)
        if weak_insight:
            insights.append(weak_insight)
        
        # 6. Streak motivation
        streak_insight = await self._check_streak(user_id)
        if streak_insight:
            insights.append(streak_insight)
        
        # Sort by priority (highest first)
        insights.sort(key=lambda x: x.priority, reverse=True)
        
        return insights[:3]  # Return top 3 most relevant
    
    async def _check_session_continuity(
        self,
        user_id: str,
        session_id: str,
        current_question: str,
        memory_context: Dict[str, Any]
    ) -> Optional[ProactiveInsight]:
        """Check if we should reference a previous session"""
        
        # Get last session info
        continuity = memory_context.get("continuity", {})
        is_continuation = continuity.get("is_continuation", False)
        last_topic = continuity.get("last_topic", "")
        last_session_date = continuity.get("last_session_date")
        
        if not is_continuation and last_topic:
            # Check if this is a new session after a gap
            if last_session_date:
                try:
                    last_date = datetime.fromisoformat(last_session_date.replace('Z', '+00:00'))
                    gap_hours = (datetime.now(timezone.utc) - last_date).total_seconds() / 3600
                    
                    if gap_hours > 24:  # More than a day gap
                        topic_readable = last_topic.replace('_', ' ').title()
                        return ProactiveInsight(
                            action_type=ProactiveActionType.CONTINUITY_REFERENCE,
                            message=f"Welcome back! 👋 Last time we explored **{topic_readable}**. Want to continue where we left off, or start something new?",
                            priority=8,
                            data={"last_topic": last_topic, "gap_hours": gap_hours}
                        )
                except Exception:
                    pass
        
        return None
    
    async def _check_review_needed(
        self,
        user_id: str,
        memory_context: Dict[str, Any]
    ) -> Optional[ProactiveInsight]:
        """Check if any concepts need review (spaced repetition)"""

        if self.db is None:
            return None
        
        try:
            # Get concepts due for review
            now = datetime.now(timezone.utc)
            due_reviews = await self.db.user_memory_facts.find({
                "user_id": user_id,
                "next_review_at": {"$lte": now},
                "fact_type": "concept_learned"
            }).sort("next_review_at", 1).limit(3).to_list(length=3)
            
            if due_reviews:
                concepts = [r.get("topic", "a concept").replace('_', ' ') for r in due_reviews]
                if len(concepts) == 1:
                    return ProactiveInsight(
                        action_type=ProactiveActionType.REVIEW_SUGGESTION,
                        message=f"💡 Quick reminder: **{concepts[0]}** is due for review. A quick recap can help lock it in!",
                        priority=6,
                        data={"concepts": concepts}
                    )
                else:
                    return ProactiveInsight(
                        action_type=ProactiveActionType.REVIEW_SUGGESTION,
                        message=f"📚 You have {len(concepts)} concepts ready for review: {', '.join(concepts[:2])}. Quick revision?",
                        priority=6,
                        data={"concepts": concepts}
                    )
        except Exception as e:
            logger.debug(f"Review check failed: {e}")
        
        return None
    
    def _check_break_needed(self, session_duration_mins: int) -> Optional[ProactiveInsight]:
        """Check if student should take a break"""
        
        if session_duration_mins >= 45:
            return ProactiveInsight(
                action_type=ProactiveActionType.BREAK_SUGGESTION,
                message="☕ You've been studying for 45+ minutes - amazing focus! Consider a 5-minute break. Your brain consolidates learning during rest!",
                priority=7,
                data={"duration_mins": session_duration_mins}
            )
        elif session_duration_mins >= 30:
            # Don't suggest break yet, but note it
            return None
        
        return None
    
    async def _check_progress_milestones(
        self,
        user_id: str,
        memory_context: Dict[str, Any]
    ) -> Optional[ProactiveInsight]:
        """Check if student hit any progress milestones"""
        
        if self.db is None:
            return None
        
        try:
            # Get user stats
            profile = await self.db.user_learning_profile.find_one({"user_id": user_id})
            if not profile:
                return None
            
            stats = profile.get("stats", {})
            total_questions = stats.get("total_questions", 0)
            
            # Check for milestone (every 50 questions, or special numbers)
            milestones = [10, 25, 50, 100, 150, 200, 250, 500, 1000]
            for milestone in milestones:
                if total_questions == milestone:
                    return ProactiveInsight(
                        action_type=ProactiveActionType.MILESTONE_CELEBRATION,
                        message=f"🎉 **{milestone} questions answered!** You're building real knowledge. Every question is a step forward!",
                        priority=9,
                        data={"milestone": milestone, "total": total_questions}
                    )
            
            # Check mastery improvements
            mastery_level = memory_context.get("mastery_level", 0)
            mastery_bucket = memory_context.get("mastery_bucket", "beginner")
            
            if mastery_level >= 70 and mastery_bucket == "advanced":
                current_topic = memory_context.get("current_topic", "").replace('_', ' ')
                if current_topic:
                    return ProactiveInsight(
                        action_type=ProactiveActionType.PROGRESS_CELEBRATION,
                        message=f"🌟 You're becoming an expert at **{current_topic}**! Mastery: {mastery_level}%",
                        priority=7,
                        data={"topic": current_topic, "mastery": mastery_level}
                    )
        except Exception as e:
            logger.debug(f"Progress check failed: {e}")
        
        return None
    
    async def _check_weak_areas(
        self,
        user_id: str,
        current_question: str,
        memory_context: Dict[str, Any]
    ) -> Optional[ProactiveInsight]:
        """Check if we should address weak areas"""
        
        weak_topics = memory_context.get("weak_topics", [])
        
        if weak_topics and len(weak_topics) > 0:
            # Only mention if current question might be related
            question_lower = current_question.lower()
            for weak_topic in weak_topics[:2]:
                topic_words = weak_topic.replace('_', ' ').lower().split()
                if any(word in question_lower for word in topic_words):
                    return ProactiveInsight(
                        action_type=ProactiveActionType.WEAK_AREA_NUDGE,
                        message=f"💪 I noticed **{weak_topic.replace('_', ' ')}** is an area we can strengthen. Let me explain this extra clearly!",
                        priority=5,
                        data={"weak_topic": weak_topic}
                    )
        
        return None
    
    async def _check_streak(self, user_id: str) -> Optional[ProactiveInsight]:
        """Check learning streak"""

        if self.db is None:
            return None
        
        try:
            profile = await self.db.user_learning_profile.find_one({"user_id": user_id})
            if not profile:
                return None
            
            stats = profile.get("stats", {})
            streak = stats.get("current_streak_days", 0)
            
            # Celebrate streak milestones
            if streak in [3, 5, 7, 10, 14, 21, 30, 50, 100]:
                emoji = "🔥" if streak >= 7 else "⭐"
                return ProactiveInsight(
                    action_type=ProactiveActionType.STREAK_MOTIVATION,
                    message=f"{emoji} **{streak}-day learning streak!** Consistency is the secret to mastery. Keep it up!",
                    priority=8,
                    data={"streak_days": streak}
                )
        except Exception as e:
            logger.debug(f"Streak check failed: {e}")
        
        return None
    
    def format_proactive_opener(
        self,
        insights: List[ProactiveInsight],
        student_name: str = ""
    ) -> Optional[str]:
        """
        Format insights into a natural opening for the AI response.
        
        Only includes the highest priority, most relevant insight.
        """
        if not insights:
            return None
        
        # Get highest priority insight
        top_insight = insights[0]
        
        # For continuity and milestones, use the full message
        if top_insight.action_type in [
            ProactiveActionType.CONTINUITY_REFERENCE,
            ProactiveActionType.MILESTONE_CELEBRATION,
            ProactiveActionType.STREAK_MOTIVATION
        ]:
            return top_insight.message
        
        # For others, be more subtle
        return None  # Let them be shown separately in UI
    
    def get_follow_up_suggestions(
        self,
        insights: List[ProactiveInsight],
        response_topic: str
    ) -> List[Dict[str, str]]:
        """
        Generate follow-up action suggestions based on insights.
        
        These appear as clickable buttons in the UI.
        """
        suggestions = []
        
        for insight in insights:
            if insight.action_type == ProactiveActionType.REVIEW_SUGGESTION:
                concepts = insight.data.get("concepts", [])
                if concepts:
                    suggestions.append({
                        "label": f"📝 Review {concepts[0]}",
                        "action": f"explain {concepts[0]} briefly"
                    })
            
            elif insight.action_type == ProactiveActionType.QUIZ_SUGGESTION:
                suggestions.append({
                    "label": "🎯 Quick Quiz",
                    "action": f"give me a quick quiz on {response_topic}"
                })
            
            elif insight.action_type == ProactiveActionType.BREAK_SUGGESTION:
                suggestions.append({
                    "label": "☕ Take a Break",
                    "action": "suggest a 5-minute break activity"
                })
        
        # Always offer these
        suggestions.append({
            "label": "🔍 Go Deeper",
            "action": f"explain {response_topic} in more detail"
        })
        
        return suggestions[:4]  # Max 4 suggestions


# ============================================
# SINGLETON & FACTORY
# ============================================

_proactive_engine: Optional[ProactiveIntelligenceEngine] = None


def get_proactive_engine(db=None) -> ProactiveIntelligenceEngine:
    """Get or create the proactive intelligence engine"""
    global _proactive_engine
    if _proactive_engine is None:
        _proactive_engine = ProactiveIntelligenceEngine(db)
    return _proactive_engine


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

async def get_proactive_insights(
    user_id: str,
    session_id: str,
    question: str,
    memory_context: Dict[str, Any],
    session_duration_mins: int = 0,
    db = None
) -> List[Dict[str, Any]]:
    """Convenience function to get proactive insights"""
    engine = get_proactive_engine(db)
    insights = await engine.get_proactive_insights(
        user_id=user_id,
        session_id=session_id,
        current_question=question,
        memory_context=memory_context,
        session_duration_mins=session_duration_mins
    )
    return [i.to_dict() for i in insights]










