"""
🧠 Intelligent Proactive Mentor - Level 2 & 4 Agent Intelligence
================================================================

This service makes the AI truly PROACTIVE and INTELLIGENT:

Level 2 - Proactive Learning Companion:
- Streak protection (don't let students break their streak)
- Smart nudges based on study patterns
- Exam countdown reminders
- Daily study summaries
- 🆕 Spaced repetition reminders

Level 4 - Intelligent Study Assistant:
- Concept dependency tracking
- Adaptive difficulty suggestions
- Learning pattern analysis
- Personalized recommendations

The AI doesn't just respond - it ANTICIPATES student needs!
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

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
    The brain behind proactive AI behavior.
    
    This class analyzes student patterns and generates
    intelligent, timely interventions to keep them engaged.
    """
    
    # Streak milestones for celebrations
    STREAK_MILESTONES = [3, 7, 14, 21, 30, 50, 100]
    
    # Hours of inactivity before concern
    INACTIVITY_THRESHOLD_HOURS = 20
    
    # Study session length before suggesting break (minutes)
    STUDY_SESSION_MAX_MINUTES = 90
    
    def __init__(self, db_client):
        self.db = db_client
    
    # ========================================
    # LEVEL 2: Proactive Learning Companion
    # ========================================
    
    async def check_streak_protection(self, user_id: str) -> Optional[ProactiveNudge]:
        """
        Check if user is about to break their streak and send protective nudge.
        
        This is the #1 engagement driver - preventing streak breaks!
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
                
                # Get their last studied topic for context
                last_topic = user.get('last_topic', 'your studies')
                
                # Personalize based on streak length
                if current_streak >= 30:
                    urgency = "Your incredible"
                    emoji = "🏆"
                elif current_streak >= 7:
                    urgency = "Your amazing"
                    emoji = "🔥"
                else:
                    urgency = "Your"
                    emoji = "⚡"
                
                return ProactiveNudge(
                    nudge_type=NudgeType.STREAK_PROTECTION,
                    title=f"{emoji} {urgency} {current_streak}-day streak is at risk!",
                    message=f"Quick 5-minute session on {last_topic}? Don't let your hard work go to waste!",
                    priority="high",
                    actions=[
                        {"label": "Quick 5-min Review", "action": "start_quick_review"},
                        {"label": "Remind in 1 hour", "action": "snooze_1h"},
                        {"label": "Skip today", "action": "skip_streak"}
                    ],
                    data={
                        'current_streak': current_streak,
                        'hours_inactive': round(hours_since, 1),
                        'last_topic': last_topic
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
                emoji = "🚨"
                urgency = "You're at risk of forgetting"
            elif hours_overdue > 24:
                priority = "medium"
                emoji = "⏰"
                urgency = "Time for a quick review of"
            else:
                priority = "low"
                emoji = "📚"
                urgency = "Your brain says it's time to revisit"
            
            concept = most_urgent.get('concept', most_urgent.get('topic', 'this concept'))
            subject = most_urgent.get('subject', 'your subject')
            
            message = f"{urgency} **{concept}** ({subject})."
            if total_due > 1:
                message += f"\n\n{total_due - 1} more concept{'s' if total_due > 2 else ''} also due for review."
            
            message += "\n\n*Quick 5-min revision now = months of memory retention!*"
            
            return ProactiveNudge(
                nudge_type=NudgeType.REVISION_DUE,
                title=f"{emoji} Spaced Repetition Reminder",
                message=message,
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
                    'hours_overdue': hours_overdue
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


# Singleton instance
_mentor_instance = None

async def get_proactive_mentor(db_client) -> IntelligentProactiveMentor:
    """Get singleton instance"""
    global _mentor_instance
    if _mentor_instance is None:
        _mentor_instance = IntelligentProactiveMentor(db_client)
    return _mentor_instance
