"""
Learning Profile Service - Cross-Session Memory Management
Tracks and manages student learning across sessions
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)


class LearningProfileService:
    """
    Manages student learning profiles for cross-session memory
    """

    def __init__(self, db: AsyncIOMotorClient):
        self.db = db

    async def get_learning_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get or create learning profile for user
        """
        try:
            user = await self.db.users.find_one({"user_id": user_id})

            if not user or 'learning_profile' not in user:
                # Create default learning profile
                default_profile = {
                    'user_id': user_id,
                    'topics_mastered': [],
                    'weak_areas': [],
                    'recent_sessions': [],
                    'preferences': {
                        'preferred_metaphors': {},
                        'preferred_visual_types': {},
                        'learning_pace': 'moderate',
                        'depth_preference': 'standard',
                        'subjects_of_interest': []
                    },
                    'total_sessions': 0,
                    'total_questions_asked': 0,
                    'total_topics_explored': 0,
                    'current_streak_days': 0,
                    'longest_streak_days': 0,
                    'last_active_date': None,
                    'current_topic_focus': None,
                    'recommended_next_topics': [],
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }

                # Store in user document
                await self.db.users.update_one(
                    {"user_id": user_id},
                    {"$set": {"learning_profile": default_profile}},
                    upsert=True
                )

                return default_profile

            return user.get('learning_profile', {})

        except Exception as e:
            logger.error(f"Failed to get learning profile: {e}")
            return {}

    async def update_topic_mastery(
        self,
        user_id: str,
        topic: str,
        subject: str,
        metaphor_used: str = None,
        performance_score: float = 0.5
    ):
        """
        Update mastery level for a topic
        """
        try:
            profile = await self.get_learning_profile(user_id)
            topics_mastered = profile.get('topics_mastered', [])

            # Find existing topic mastery
            topic_found = False
            for tm in topics_mastered:
                if tm.get('topic') == topic and tm.get('subject') == subject:
                    # Update existing mastery
                    tm['times_reviewed'] = tm.get('times_reviewed', 0) + 1
                    tm['last_reviewed'] = datetime.now(timezone.utc).isoformat()

                    # Exponential moving average for mastery level
                    current_mastery = tm.get('mastery_level', 0.0)
                    tm['mastery_level'] = current_mastery * 0.7 + performance_score * 0.3

                    # Track metaphors
                    if metaphor_used and metaphor_used not in tm.get('metaphors_used', []):
                        tm.setdefault('metaphors_used', []).append(metaphor_used)

                    topic_found = True
                    break

            if not topic_found:
                # Add new topic mastery
                topics_mastered.append({
                    'topic': topic,
                    'subject': subject,
                    'mastery_level': performance_score,
                    'times_reviewed': 1,
                    'last_reviewed': datetime.now(timezone.utc).isoformat(),
                    'correct_answers': 0,
                    'total_attempts': 0,
                    'metaphors_used': [metaphor_used] if metaphor_used else [],
                    'notes': None
                })

            # Update profile
            await self.db.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "learning_profile.topics_mastered": topics_mastered,
                        "learning_profile.updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )

            logger.info(f"Updated topic mastery: {topic} for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to update topic mastery: {e}")

    async def add_weak_area(
        self,
        user_id: str,
        topic: str,
        subject: str,
        mistake: str = None
    ):
        """
        Track a weak area / topic where student struggles
        """
        try:
            profile = await self.get_learning_profile(user_id)
            weak_areas = profile.get('weak_areas', [])

            # Find existing weak area
            area_found = False
            for wa in weak_areas:
                if wa.get('topic') == topic and wa.get('subject') == subject:
                    wa['struggle_count'] = wa.get('struggle_count', 0) + 1
                    wa['last_struggled'] = datetime.now(timezone.utc).isoformat()
                    if mistake and mistake not in wa.get('common_mistakes', []):
                        wa.setdefault('common_mistakes', []).append(mistake)
                    area_found = True
                    break

            if not area_found:
                weak_areas.append({
                    'topic': topic,
                    'subject': subject,
                    'struggle_count': 1,
                    'last_struggled': datetime.now(timezone.utc).isoformat(),
                    'common_mistakes': [mistake] if mistake else [],
                    'needs_revision': True
                })

            await self.db.users.update_one(
                {"user_id": user_id},
                {"$set": {"learning_profile.weak_areas": weak_areas}}
            )

        except Exception as e:
            logger.error(f"Failed to add weak area: {e}")

    async def update_preferences(
        self,
        user_id: str,
        metaphor_used: str = None,
        visual_type: str = None,
        learning_pace: str = None
    ):
        """
        Update learning preferences based on usage patterns
        """
        try:
            profile = await self.get_learning_profile(user_id)
            preferences = profile.get('preferences', {})

            # Track metaphor usage
            if metaphor_used:
                preferred_metaphors = preferences.get('preferred_metaphors', {})
                preferred_metaphors[metaphor_used] = preferred_metaphors.get(metaphor_used, 0) + 1
                preferences['preferred_metaphors'] = preferred_metaphors

            # Track visual type usage
            if visual_type:
                preferred_visuals = preferences.get('preferred_visual_types', {})
                preferred_visuals[visual_type] = preferred_visuals.get(visual_type, 0) + 1
                preferences['preferred_visual_types'] = preferred_visuals

            # Update learning pace if specified
            if learning_pace:
                preferences['learning_pace'] = learning_pace

            await self.db.users.update_one(
                {"user_id": user_id},
                {"$set": {"learning_profile.preferences": preferences}}
            )

        except Exception as e:
            logger.error(f"Failed to update preferences: {e}")

    async def record_session_summary(
        self,
        user_id: str,
        session_id: str,
        topics_covered: List[str],
        subjects: List[str],
        message_count: int
    ):
        """
        Record summary of a learning session
        """
        try:
            session_summary = {
                'session_id': session_id,
                'date': datetime.now(timezone.utc).isoformat(),
                'duration_minutes': 0,  # Can be calculated later
                'topics_covered': topics_covered,
                'messages_count': message_count,
                'subjects': list(set(subjects)),  # Unique subjects
                'engagement_level': 'medium',
                'summary': f"Discussed {len(topics_covered)} topics"
            }

            # Add to recent sessions (keep last 10)
            await self.db.users.update_one(
                {"user_id": user_id},
                {
                    "$push": {
                        "learning_profile.recent_sessions": {
                            "$each": [session_summary],
                            "$slice": -10  # Keep only last 10 sessions
                        }
                    },
                    "$inc": {"learning_profile.total_sessions": 1},
                    "$set": {
                        "learning_profile.last_active_date": datetime.now(timezone.utc).isoformat()
                    }
                }
            )

            logger.info(f"Recorded session summary for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to record session summary: {e}")

    async def get_welcome_back_message(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate personalized welcome back message based on learning history
        """
        try:
            profile = await self.get_learning_profile(user_id)

            if not profile or profile.get('total_sessions', 0) == 0:
                return None  # New user, no history

            last_active = profile.get('last_active_date')
            recent_sessions = profile.get('recent_sessions', [])
            current_focus = profile.get('current_topic_focus')
            weak_areas = profile.get('weak_areas', [])

            # Build welcome message
            message = {
                'has_history': True,
                'streak_days': profile.get('current_streak_days', 0),
                'total_sessions': profile.get('total_sessions', 0)
            }

            # Last session info
            if recent_sessions:
                last_session = recent_sessions[-1]
                message['last_session'] = {
                    'topics': last_session.get('topics_covered', []),
                    'date': last_session.get('date'),
                    'summary': last_session.get('summary')
                }

            # Current focus
            if current_focus:
                message['current_focus'] = current_focus

            # Weak areas needing attention
            if weak_areas:
                needs_revision = [wa for wa in weak_areas if wa.get('needs_revision')]
                if needs_revision:
                    message['needs_revision'] = [wa.get('topic') for wa in needs_revision[:3]]

            # Suggested next topics
            message['suggested_topics'] = profile.get('recommended_next_topics', [])

            return message

        except Exception as e:
            logger.error(f"Failed to generate welcome message: {e}")
            return None

    async def get_learning_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Generate learning insights based on profile
        """
        try:
            profile = await self.get_learning_profile(user_id)
            insights = []

            # Progress insight
            topics_mastered = profile.get('topics_mastered', [])
            if topics_mastered:
                mastered_count = len([t for t in topics_mastered if t.get('mastery_level', 0) > 0.7])
                if mastered_count > 0:
                    insights.append({
                        'type': 'progress',
                        'message': f"Great progress! You've mastered {mastered_count} topics",
                        'topics': [t.get('topic') for t in topics_mastered if t.get('mastery_level', 0) > 0.7][:5],
                        'confidence': 0.9
                    })

            # Weak area insight
            weak_areas = profile.get('weak_areas', [])
            if weak_areas:
                top_weak = sorted(weak_areas, key=lambda x: x.get('struggle_count', 0), reverse=True)[:2]
                insights.append({
                    'type': 'weakness',
                    'message': f"Let's strengthen: {', '.join([w.get('topic') for w in top_weak])}",
                    'topics': [w.get('topic') for w in top_weak],
                    'confidence': 0.8
                })

            # Streak insight
            streak = profile.get('current_streak_days', 0)
            if streak > 3:
                insights.append({
                    'type': 'motivation',
                    'message': f"Amazing! {streak} day learning streak! Keep it going! 🔥",
                    'topics': [],
                    'confidence': 1.0
                })

            return insights

        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            return []
