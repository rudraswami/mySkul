"""
🌟 PROACTIVE COMPANION AGENT - 24/7 Learning Partner

This is not just an agent - it's a caring friend who:
- Remembers everything about the student
- Reaches out proactively (doesn't wait to be asked)
- Sends reminders at the RIGHT time
- Celebrates wins and supports during struggles
- Works across chat, notifications, email

Philosophy: "A true friend doesn't wait for you to ask for help"

HUMAN-LIKE BEHAVIORS:
1. Remembers context: "Hey, yesterday you were stuck on integration. Want to try again?"
2. Notices patterns: "I see you study better in the evening. Shall I remind you at 7 PM?"
3. Celebrates: "3 days in a row! You're on fire! 🔥"
4. Worries (genuinely): "Haven't seen you in 2 days. Everything okay?"
5. Encourages rest: "You've been at it for 2 hours. Take a break?"
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class NudgeType(Enum):
    """Types of proactive nudges"""
    REMINDER = "reminder"           # User-requested reminder
    SPACED_REP = "spaced_rep"       # Spaced repetition review
    STREAK_PROTECT = "streak"       # Streak about to break
    COMEBACK = "comeback"           # Haven't seen user in a while
    CELEBRATION = "celebration"     # Achievement unlocked
    STUDY_NUDGE = "study_nudge"     # Gentle study suggestion
    WEAK_AREA = "weak_area"         # Weak topic needs attention
    MORNING_GREET = "morning"       # Morning check-in
    NIGHT_SUMMARY = "night"         # Night summary/planning


class ProactiveCompanionAgent:
    """
    A 24/7 learning companion that thinks and acts like a caring friend.
    
    This agent runs in the background and proactively helps students:
    - Schedules and sends reminders
    - Implements spaced repetition
    - Protects streaks
    - Sends motivational check-ins
    - Notices when student is struggling or absent
    """
    
    # Companion personality
    COMPANION_NAME = "Sathi"  # The app's name, acting as a friend
    
    # Time-based messages (feels human)
    TIME_GREETINGS = {
        'morning': [
            "Good morning, {name}! ☀️ Ready to conquer today?",
            "Rise and shine, {name}! What's on the study menu today?",
            "Morning, {name}! Yesterday you were working on {topic}. Continue?"
        ],
        'afternoon': [
            "Hey {name}! Quick study break? 📚",
            "Afternoon, {name}! Perfect time for a revision session.",
        ],
        'evening': [
            "Evening, {name}! Your peak study time is here! 🌙",
            "Hey {name}! Ready for some focused learning?",
        ],
        'night': [
            "Still up, {name}? Don't forget to rest! 😴",
            "Late night warrior! Quick revision before sleep?",
        ]
    }
    
    # Streak messages (celebratory but not cringe)
    STREAK_MESSAGES = {
        1: "First step taken! Let's keep going! 🌱",
        3: "3 days strong! You're building a habit! 💪",
        7: "ONE WEEK STREAK! 🔥 You're unstoppable!",
        14: "2 WEEKS! 🏆 This is when real learning compounds!",
        30: "30 DAYS! 👑 You're in the top 5% of dedicated students!",
        100: "💯 100 DAYS! LEGENDARY! You're a learning machine!"
    }
    
    # Comeback messages (when student is away)
    COMEBACK_MESSAGES = {
        1: "Hey {name}! Missed you today. Quick 5-minute session?",
        2: "2 days without practice makes concepts rusty. Come back? 🙏",
        3: "Your streak is about to reset! Quick revision to save it?",
        7: "It's been a week, {name}. No judgment - just here when you're ready.",
        14: "Hey {name}, checking in. Exams coming up - want to restart together?"
    }
    
    def __init__(self, db_client=None, notification_service=None):
        self.db = db_client
        self.notification_service = notification_service
    
    # ===========================================
    # CORE: Intent Detection & Response
    # ===========================================
    
    @staticmethod
    def is_reminder_request(query: str) -> bool:
        """Detect if user wants to set a reminder"""
        query_lower = query.lower()
        
        reminder_phrases = [
            'remind me', 'reminder', 'remind tomorrow',
            'remind later', 'notify me', 'alert me',
            'wake me', 'call me', 'ping me',
            'याद दिलाना', 'याद करवाना',  # Hindi
            'kal yaad dilana', 'baad mein',  # Hinglish
            'schedule', 'set alarm', 'later today',
            'in the morning', 'in the evening',
            'after lunch', 'before sleep'
        ]
        
        return any(phrase in query_lower for phrase in reminder_phrases)
    
    @staticmethod
    def is_schedule_request(query: str) -> bool:
        """Detect if user wants to create a study schedule"""
        query_lower = query.lower()
        
        schedule_phrases = [
            'create schedule', 'make schedule', 'study plan',
            'daily routine', 'weekly plan', 'timetable',
            'when should i study', 'best time to study',
            'plan my day', 'organize my study'
        ]
        
        return any(phrase in query_lower for phrase in schedule_phrases)
    
    async def process_reminder_request(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a reminder request like:
        - "Remind me to revise photosynthesis tomorrow"
        - "Quiz me on force in 2 days"
        - "Remind me at 7 PM to study"
        """
        user_id = context.get('user_id')
        student = context.get('student_profile', {})
        name = student.get('user_name', 'there') or 'there'
        
        # Parse the reminder request
        parsed = await self._parse_reminder(query, context)
        
        if not parsed.get('success'):
            return self._format_response(
                content=f"I'd love to remind you, {name}! But I need a bit more detail. "
                       "When should I remind you? (e.g., 'tomorrow at 7 PM' or 'in 2 hours')",
                metadata={'needs_clarification': True}
            )
        
        # Format friendly response
        time_str = self._format_time_friendly(parsed.get('scheduled_time'))
        topic = parsed.get('topic', 'this topic')
        scheduled_time = parsed.get('scheduled_time')
        
        # Note: In production, this would save to database via ReminderScheduler
        # For now, generate a human-like acknowledgment
        reminder_id = f"rem_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Store reminder in database if available
        if self.db is not None:
            try:
                from services.reminder_scheduler import ReminderScheduler
                scheduler = ReminderScheduler(self.db)
                reminder_id = await scheduler.schedule_reminder(
                    user_id=user_id,
                    topic=topic,
                    reminder_time=scheduled_time,
                    reminder_type=parsed.get('type', 'study'),
                    message=parsed.get('custom_message'),
                    context={
                        'subject': context.get('subject'),
                        'session_id': context.get('session_id')
                    }
                )
            except Exception as e:
                logger.warning(f"Could not save reminder to DB: {e}")
        
        response = f"""Got it, {name}! 📝

I'll remind you about **{topic}** {time_str}.

Here's what I'll do:
• Send you a notification 🔔
• Have a quick quiz ready (if you want)
• Remember where we left off

Don't worry, I've got your back! See you then! ✨"""
        
        return self._format_response(
            content=response,
            metadata={
                'reminder_id': reminder_id,
                'scheduled_time': scheduled_time.isoformat() if scheduled_time else None,
                'topic': topic
            }
        )
    
    async def _parse_reminder(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse reminder request to extract time and topic"""
        import re
        from datetime import datetime, timedelta
        
        query_lower = query.lower()
        now = datetime.now()
        
        result = {
            'success': False,
            'topic': None,
            'scheduled_time': None,
            'type': 'study'
        }
        
        # Extract topic (what to remind about)
        # Pattern: "remind me to [revise/study/practice] [topic]"
        topic_patterns = [
            r'remind (?:me )?(?:to )?(?:revise|study|practice|review|learn) (.+?)(?:tomorrow|today|at|in|$)',
            r'remind (?:me )?about (.+?)(?:tomorrow|today|at|in|$)',
            r'quiz me (?:on|about) (.+?)(?:tomorrow|today|at|in|$)',
        ]
        
        for pattern in topic_patterns:
            match = re.search(pattern, query_lower)
            if match:
                result['topic'] = match.group(1).strip()
                break
        
        # If no topic found, use session context
        if not result['topic']:
            result['topic'] = context.get('subject', 'your studies')
        
        # Extract time
        # Tomorrow
        if 'tomorrow' in query_lower:
            # Default to 9 AM tomorrow
            result['scheduled_time'] = (now + timedelta(days=1)).replace(
                hour=9, minute=0, second=0, microsecond=0
            )
            result['success'] = True
        
        # Today
        elif 'today' in query_lower or 'later' in query_lower:
            # Default to 2 hours from now
            result['scheduled_time'] = now + timedelta(hours=2)
            result['success'] = True
        
        # In X hours/minutes
        time_delta_match = re.search(r'in (\d+) (hour|minute|min|hr)s?', query_lower)
        if time_delta_match:
            amount = int(time_delta_match.group(1))
            unit = time_delta_match.group(2)
            if 'hour' in unit or 'hr' in unit:
                result['scheduled_time'] = now + timedelta(hours=amount)
            else:
                result['scheduled_time'] = now + timedelta(minutes=amount)
            result['success'] = True
        
        # In X days
        days_match = re.search(r'in (\d+) days?', query_lower)
        if days_match:
            days = int(days_match.group(1))
            result['scheduled_time'] = (now + timedelta(days=days)).replace(
                hour=9, minute=0, second=0, microsecond=0
            )
            result['success'] = True
        
        # At specific time (7 PM, 19:00, etc.)
        time_match = re.search(r'at (\d{1,2})(?::(\d{2}))?\s*(am|pm)?', query_lower)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or 0)
            meridiem = time_match.group(3)
            
            if meridiem == 'pm' and hour < 12:
                hour += 12
            elif meridiem == 'am' and hour == 12:
                hour = 0
            
            # Determine if it's for today or tomorrow
            target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if target_time <= now:
                target_time += timedelta(days=1)
            
            result['scheduled_time'] = target_time
            result['success'] = True
        
        # Morning/evening/night shortcuts
        if 'morning' in query_lower:
            result['scheduled_time'] = (now + timedelta(days=1)).replace(
                hour=8, minute=0, second=0, microsecond=0
            )
            result['success'] = True
        elif 'evening' in query_lower:
            target = now.replace(hour=18, minute=0, second=0, microsecond=0)
            if target <= now:
                target += timedelta(days=1)
            result['scheduled_time'] = target
            result['success'] = True
        elif 'night' in query_lower:
            target = now.replace(hour=21, minute=0, second=0, microsecond=0)
            if target <= now:
                target += timedelta(days=1)
            result['scheduled_time'] = target
            result['success'] = True
        
        return result
    
    def _format_time_friendly(self, dt: datetime) -> str:
        """Format datetime in a friendly way"""
        if not dt:
            return "soon"
        
        now = datetime.now()
        diff = dt - now
        
        if diff.days == 0:
            if diff.seconds < 3600:
                return f"in {diff.seconds // 60} minutes"
            elif diff.seconds < 7200:
                return "in about an hour"
            else:
                return f"today at {dt.strftime('%I:%M %p')}"
        elif diff.days == 1:
            return f"tomorrow at {dt.strftime('%I:%M %p')}"
        elif diff.days < 7:
            return f"on {dt.strftime('%A')} at {dt.strftime('%I:%M %p')}"
        else:
            return f"on {dt.strftime('%B %d')} at {dt.strftime('%I:%M %p')}"
    
    # ===========================================
    # PROACTIVE NUDGES
    # ===========================================
    
    async def generate_proactive_nudge(
        self,
        user_id: str,
        nudge_type: NudgeType,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate a proactive nudge message
        This is called by the background scheduler
        """
        context = context or {}
        student = await self._get_student_profile(user_id)
        name = student.get('name', 'there')
        
        if nudge_type == NudgeType.STREAK_PROTECT:
            return await self._generate_streak_nudge(user_id, student)
        
        elif nudge_type == NudgeType.COMEBACK:
            return await self._generate_comeback_nudge(user_id, student)
        
        elif nudge_type == NudgeType.SPACED_REP:
            return await self._generate_spaced_rep_nudge(user_id, student, context)
        
        elif nudge_type == NudgeType.MORNING_GREET:
            return await self._generate_morning_nudge(user_id, student)
        
        elif nudge_type == NudgeType.CELEBRATION:
            return await self._generate_celebration_nudge(user_id, student, context)
        
        elif nudge_type == NudgeType.WEAK_AREA:
            return await self._generate_weak_area_nudge(user_id, student)
        
        else:
            return await self._generate_study_nudge(user_id, student)
    
    async def _generate_streak_nudge(
        self,
        user_id: str,
        student: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate streak protection nudge"""
        name = student.get('name', 'there')
        streak = student.get('current_streak', 0)
        
        if streak >= 7:
            urgency = "🚨"
            message = f"{urgency} {name}! Your {streak}-day streak is about to break!\n\n"
            message += "Just 2 minutes of quick revision will save it. You've worked so hard to build this!\n\n"
            message += "Tap here for a super quick review. I believe in you! 💪"
        else:
            message = f"Hey {name}! Quick heads up - your streak needs some love today! 🔥\n\n"
            message += "Even a tiny 5-minute session counts. What do you say?"
        
        return {
            'type': 'streak_protect',
            'title': '🔥 Streak Alert!',
            'message': message,
            'action': {
                'label': 'Quick 2-min Review',
                'type': 'quick_review'
            },
            'priority': 'high'
        }
    
    async def _generate_comeback_nudge(
        self,
        user_id: str,
        student: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comeback nudge for inactive users"""
        name = student.get('name', 'there')
        days_away = student.get('days_inactive', 1)
        last_topic = student.get('last_topic', 'your studies')
        
        if days_away <= 2:
            message = f"Hey {name}! Missed you today. 😊\n\n"
            message += f"We were making great progress on {last_topic}. "
            message += "Ready to pick up where we left off?"
        elif days_away <= 7:
            message = f"Hey {name}, it's been {days_away} days! No pressure, just checking in.\n\n"
            message += "Whenever you're ready, I'm here. Even 5 minutes helps! 🌱"
        else:
            message = f"Hey {name}! Long time no see. 👋\n\n"
            message += "Life gets busy, I totally get it. Whenever you're ready to restart, "
            message += "I'll be right here. No judgment, just support. ❤️"
        
        return {
            'type': 'comeback',
            'title': f"We miss you, {name}! 💫",
            'message': message,
            'action': {
                'label': 'Start a Quick Session',
                'type': 'new_session'
            },
            'priority': 'medium'
        }
    
    async def _generate_spaced_rep_nudge(
        self,
        user_id: str,
        student: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate spaced repetition review nudge"""
        name = student.get('name', 'there')
        topic = context.get('topic', 'a concept')
        days_since = context.get('days_since_learned', 3)
        
        message = f"Hey {name}! Remember **{topic}** from {days_since} days ago? 🧠\n\n"
        message += "This is the perfect time to review - your brain is just about to forget it! "
        message += "A quick 3-minute refresh will lock it in for good.\n\n"
        message += "Ready for a quick quiz? 🎯"
        
        return {
            'type': 'spaced_rep',
            'title': f"🔄 Time to Review: {topic}",
            'message': message,
            'action': {
                'label': 'Quick Review Quiz',
                'type': 'spaced_rep_quiz',
                'topic': topic
            },
            'priority': 'medium'
        }
    
    async def _generate_morning_nudge(
        self,
        user_id: str,
        student: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate morning check-in"""
        name = student.get('name', 'there')
        streak = student.get('current_streak', 0)
        last_topic = student.get('last_topic')
        
        import random
        
        greetings = [
            f"Good morning, {name}! ☀️",
            f"Rise and shine, {name}! 🌅",
            f"Morning, superstar! ⭐",
        ]
        
        greeting = random.choice(greetings)
        
        message = f"{greeting}\n\n"
        
        if streak > 0:
            message += f"You're on a {streak}-day streak! Let's keep it going. "
        
        if last_topic:
            message += f"Yesterday you were working on {last_topic}. Want to continue, or try something new?"
        else:
            message += "What would you like to learn today?"
        
        return {
            'type': 'morning',
            'title': greeting,
            'message': message,
            'action': {
                'label': 'Start Learning',
                'type': 'new_session'
            },
            'priority': 'low'
        }
    
    async def _generate_celebration_nudge(
        self,
        user_id: str,
        student: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate celebration for achievements"""
        name = student.get('name', 'there')
        achievement = context.get('achievement', 'learning milestone')
        
        message = f"🎉 AMAZING, {name}! 🎉\n\n"
        message += f"You just hit a {achievement}!\n\n"
        message += "This is exactly how toppers are made - one step at a time. "
        message += "Keep going, you're doing incredible! 🚀"
        
        return {
            'type': 'celebration',
            'title': '🏆 Achievement Unlocked!',
            'message': message,
            'action': {
                'label': 'Keep the Momentum!',
                'type': 'continue_learning'
            },
            'priority': 'high'
        }
    
    async def _generate_weak_area_nudge(
        self,
        user_id: str,
        student: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate nudge about weak areas needing attention"""
        name = student.get('name', 'there')
        weak_topics = student.get('weak_topics', [])
        
        if not weak_topics:
            return await self._generate_study_nudge(user_id, student)
        
        topic = weak_topics[0]
        
        message = f"Hey {name}! I noticed **{topic}** could use some love. 📚\n\n"
        message += "No worries - everyone has topics that need extra practice. "
        message += "Want to do a focused 10-minute session? I'll make it easy and fun!\n\n"
        message += "Small steps, big results! 💪"
        
        return {
            'type': 'weak_area',
            'title': f"💪 Let's Strengthen: {topic}",
            'message': message,
            'action': {
                'label': 'Focus Practice',
                'type': 'weak_area_practice',
                'topic': topic
            },
            'priority': 'medium'
        }
    
    async def _generate_study_nudge(
        self,
        user_id: str,
        student: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate general study nudge"""
        name = student.get('name', 'there')
        subject = student.get('primary_subject', 'your subjects')
        
        import random
        
        nudges = [
            f"Hey {name}! Got 10 minutes? Let's make them count! 📚",
            f"Perfect time for a quick {subject} session, {name}!",
            f"{name}, your future self will thank you for studying now! 🚀",
            f"Quick brain workout, {name}? Just 5 minutes! 🧠",
        ]
        
        return {
            'type': 'study_nudge',
            'title': 'Study Time! 📖',
            'message': random.choice(nudges),
            'action': {
                'label': 'Start Session',
                'type': 'new_session'
            },
            'priority': 'low'
        }
    
    # ===========================================
    # HELPERS
    # ===========================================
    
    async def _get_student_profile(self, user_id: str) -> Dict[str, Any]:
        """Get student profile from database"""
        if self.db is None:
            return {}
        
        try:
            user = await self.db.users.find_one({"user_id": user_id})
            if not user:
                return {}
            
            # Get additional data
            streak_data = await self.db.user_streaks.find_one({"user_id": user_id})
            learning_profile = await self.db.user_learning_profile.find_one({"user_id": user_id})
            
            return {
                'name': user.get('full_name', '').split()[0] if user.get('full_name') else '',
                'current_streak': streak_data.get('current_streak', 0) if streak_data else 0,
                'last_topic': learning_profile.get('last_topic') if learning_profile else None,
                'weak_topics': learning_profile.get('weak_topics', []) if learning_profile else [],
                'primary_subject': user.get('primary_subject', 'General'),
                'days_inactive': 0  # Calculate from last_activity
            }
        except Exception as e:
            logger.error(f"Failed to get student profile: {e}")
            return {}
    
    def _format_response(
        self,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Format response consistently"""
        return {
            'success': True,
            'content': content,
            'agent': 'proactive_companion',
            'metadata': metadata or {}
        }


# ===========================================
# INTEGRATION HELPERS
# ===========================================

def is_reminder_request(query: str) -> bool:
    """Module-level function for import compatibility"""
    return ProactiveCompanionAgent.is_reminder_request(query)


def is_schedule_request(query: str) -> bool:
    """Module-level function for import compatibility"""
    return ProactiveCompanionAgent.is_schedule_request(query)


