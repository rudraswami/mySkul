"""
🤖 PROACTIVE SCHEDULER - Background Task Runner

This service runs in the background and:
- Processes due reminders
- Sends streak protection nudges
- Triggers spaced repetition reviews
- Sends morning greetings
- Handles comeback nudges for inactive users

Runs every minute to check for due actions.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ProactiveScheduler:
    """
    Background scheduler for proactive student engagement
    """
    
    def __init__(self, db_client=None):
        self.db = db_client
        self._running = False
        self._task = None
    
    async def start(self):
        """Start the background scheduler"""
        if self._running:
            logger.warning("Proactive scheduler already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("🚀 Proactive scheduler started")
    
    async def stop(self):
        """Stop the background scheduler"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("⏹️ Proactive scheduler stopped")
    
    async def _run_loop(self):
        """Main background loop"""
        while self._running:
            try:
                await self._process_due_actions()
            except Exception as e:
                logger.error(f"Proactive scheduler error: {e}")
            
            # Run every minute
            await asyncio.sleep(60)
    
    async def _process_due_actions(self):
        """Process all due proactive actions"""
        if self.db is None:
            return
        
        now = datetime.utcnow()
        
        # 1. Process due reminders
        await self._process_reminders()
        
        # 2. Check streak protections
        await self._check_streaks()
        
        # 3. Send spaced repetition nudges
        await self._process_spaced_rep()
        
        # 4. Check for comeback nudges
        await self._check_comebacks()
        
        # 5. Morning greetings (if it's morning in user's timezone)
        await self._send_morning_greetings()
    
    # ================================================================
    # HELPER METHODS: Anti-spam + Memory v2 Personalization
    # ================================================================
    
    async def _is_user_currently_active(self, user_id: str, threshold_minutes: int = 5) -> bool:
        """
        ANTI-SPAM: Check if user is currently active (has activity in last N minutes).
        If active, we should delay/skip proactive nudges to avoid interrupting.
        
        Returns True if user should NOT receive proactive nudge right now.
        """
        if self.db is None:
            return False
        
        try:
            threshold = datetime.utcnow() - timedelta(minutes=threshold_minutes)
            
            # Check for recent chat messages
            recent_activity = await self.db.chat_messages.find_one({
                'user_id': user_id,
                'timestamp': {'$gte': threshold}
            })
            
            if recent_activity:
                logger.debug(f"🔇 User {user_id} is active (last message {threshold_minutes}min ago)")
                return True
            
            # Also check for active sessions
            recent_session = await self.db.chat_sessions.find_one({
                'user_id': user_id,
                'updated_at': {'$gte': threshold}
            })
            
            if recent_session:
                logger.debug(f"🔇 User {user_id} has active session")
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Activity check failed for {user_id}: {e}")
            return False  # Default to allowing nudge on error
    
    async def _personalize_reminder_message(
        self,
        user_id: str,
        topic: str,
        custom_message: str = None
    ) -> str:
        """
        MEMORY v2: Personalize reminder message using StudentProfile.
        
        Incorporates:
        - Student name
        - Weak topics (extra encouragement if topic is weak)
        - Current streak (motivation)
        - Mastery level (appropriate difficulty framing)
        """
        # If custom message provided, use it as base
        if custom_message:
            return custom_message
        
        # Default message
        base_message = f"Time to study {topic}! 📚\n\nYou asked me to remind you. Ready to dive in?"
        
        if self.db is None:
            return base_message
        
        try:
            # Load StudentProfile for personalization
            profile = await self.db.student_profiles.find_one({'user_id': user_id})
            
            if not profile:
                return base_message
            
            # Get personalization data
            name = ""
            if profile.get('name'):
                name = profile['name'].split()[0]
            
            weak_topics = profile.get('weak_topics', [])
            streak = profile.get('practice_streak', 0)
            
            # Check if topic is a weak area
            topic_lower = topic.lower()
            is_weak_topic = any(wt.lower() in topic_lower or topic_lower in wt.lower() for wt in weak_topics)
            
            # Build personalized message
            greeting = f"Hey {name}! " if name else ""
            
            if is_weak_topic:
                message = f"{greeting}Time to strengthen your {topic} skills! 💪\n\n"
                message += "This is one of your growth areas - consistent practice here will pay off big time!"
            elif streak > 3:
                message = f"{greeting}🔥 {streak}-day streak! Time for {topic}!\n\n"
                message += "Keep the momentum going - you're on a roll!"
            else:
                message = f"{greeting}Time to study {topic}! 📚\n\n"
                message += "You set this reminder earlier. Let's make progress!"
            
            return message
            
        except Exception as e:
            logger.warning(f"Personalization failed for {user_id}: {e}")
            return base_message
    
    async def _process_reminders(self):
        """Process due reminders with Memory v2 personalization"""
        from services.reminder_scheduler import ReminderScheduler
        from services.notification_service import NotificationService
        
        scheduler = ReminderScheduler(self.db)
        notification_service = NotificationService(self.db)
        
        due_reminders = await scheduler.get_due_reminders(lookahead_minutes=2)
        
        for reminder in due_reminders:
            try:
                user_id = reminder['user_id']
                
                # ================================================================
                # ANTI-SPAM: Skip if user is currently active (last 5 mins)
                # ================================================================
                if await self._is_user_currently_active(user_id):
                    logger.info(f"⏸️ Reminder {reminder['reminder_id']} delayed: user {user_id} is active")
                    continue
                
                # Build notification
                topic = reminder.get('topic', 'your study session')
                custom_message = reminder.get('custom_message')
                
                # ================================================================
                # MEMORY v2: Personalize message using StudentProfile
                # ================================================================
                personalized_message = await self._personalize_reminder_message(
                    user_id=user_id,
                    topic=topic,
                    custom_message=custom_message
                )
                
                # Send notification
                await notification_service.send_notification(
                    user_id=user_id,
                    title=f"⏰ Reminder: {topic}",
                    message=personalized_message,
                    notification_type='reminder',
                    priority='high',
                    action={
                        'label': 'Start Session',
                        'type': 'start_session',
                        'topic': topic
                    },
                    data={
                        'reminder_id': reminder['reminder_id'],
                        'topic': topic,
                        'context': reminder.get('context', {}),
                        'personalized': True
                    }
                )
                
                # Mark as sent
                await scheduler.mark_reminder_sent(reminder['reminder_id'])
                
                # Handle recurring
                if reminder.get('recurring'):
                    await scheduler.handle_recurring(reminder)
                
                logger.info(f"⏰ Reminder sent: {reminder['reminder_id']} | user={user_id} | personalized=True")
                
            except Exception as e:
                logger.error(f"Failed to process reminder {reminder['reminder_id']}: {e}")
    
    async def _check_streaks(self):
        """Check for streaks that need protection using IntelligentProactiveMentor"""
        from services.intelligent_proactive_mentor import IntelligentProactiveMentor, NudgeType
        from services.notification_service import NotificationService
        
        mentor = IntelligentProactiveMentor(self.db)
        notification_service = NotificationService(self.db)
        
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Only check during evening hours (when streaks are at risk)
        if not (18 <= now.hour <= 22):
            return
        
        try:
            # Get users with streaks but no activity today
            pipeline = [
                {
                    '$match': {
                        'current_streak': {'$gt': 0}
                    }
                },
                {
                    '$lookup': {
                        'from': 'user_sessions',
                        'let': {'uid': '$user_id'},
                        'pipeline': [
                            {
                                '$match': {
                                    '$expr': {'$eq': ['$user_id', '$$uid']},
                                    'created_at': {'$gte': today_start}
                                }
                            }
                        ],
                        'as': 'today_sessions'
                    }
                },
                {
                    '$match': {
                        'today_sessions': {'$size': 0}  # No activity today
                    }
                },
                {
                    '$limit': 50
                }
            ]
            
            at_risk_users = await self.db.user_streaks.aggregate(pipeline).to_list(50)
            
            for user in at_risk_users:
                user_id = user['user_id']
                current_streak = user.get('current_streak', 0)
                
                # ANTI-SPAM: Skip if user is currently active
                if await self._is_user_currently_active(user_id):
                    logger.debug(f"⏸️ Streak nudge skipped: user {user_id} is active")
                    continue
                
                # Check if we already sent streak nudge today
                nudge_sent = await self.db.nudge_log.find_one({
                    'user_id': user_id,
                    'nudge_type': 'streak',
                    'sent_at': {'$gte': today_start}
                })
                
                if nudge_sent:
                    continue
                
                # Use IntelligentProactiveMentor to check streak risk
                nudge = await mentor.check_streak_protection(user_id)
                
                if nudge:
                    await notification_service.send_notification(
                        user_id=user_id,
                        title=nudge.title,
                        message=nudge.message,
                        notification_type=NudgeType.STREAK_PROTECTION.value,
                        priority=nudge.priority,
                        action=nudge.actions[0] if nudge.actions else None,
                        data={'streak': current_streak, 'personalized': True}
                    )
                    
                    # Log nudge
                    await self.db.nudge_log.insert_one({
                        'user_id': user_id,
                        'nudge_type': 'streak',
                        'sent_at': now,
                        'streak_value': current_streak
                    })
                    
                    logger.info(f"🔥 Streak nudge sent | user={user_id} | streak={current_streak}")
                
        except Exception as e:
            logger.error(f"Streak check failed: {e}")
    
    async def _process_spaced_rep(self):
        """Process spaced repetition reviews using IntelligentProactiveMentor"""
        from services.intelligent_proactive_mentor import IntelligentProactiveMentor, NudgeType
        from services.notification_service import NotificationService
        
        mentor = IntelligentProactiveMentor(self.db)
        notification_service = NotificationService(self.db)
        
        now = datetime.utcnow()
        
        # Only check during active hours (9 AM - 9 PM)
        if not (9 <= now.hour <= 21):
            return
        
        try:
            # Get all users with due reviews
            due_reviews = await self.db.sr_items.find({
                'next_review': {'$lte': now}
            }).limit(100).to_list(100)
            
            # Group by user
            user_reviews = {}
            for review in due_reviews:
                user_id = review['user_id']
                if user_id not in user_reviews:
                    user_reviews[user_id] = []
                user_reviews[user_id].append(review)
            
            # Send one notification per user (batch their reviews)
            for user_id, reviews in user_reviews.items():
                # ANTI-SPAM: Skip if user is currently active
                if await self._is_user_currently_active(user_id):
                    logger.debug(f"⏸️ Spaced rep nudge skipped: user {user_id} is active")
                    continue
                
                # Check rate limit - max 2 SR nudges per day
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                nudge_count = await self.db.nudge_log.count_documents({
                    'user_id': user_id,
                    'nudge_type': 'spaced_rep',
                    'sent_at': {'$gte': today_start}
                })
                
                if nudge_count >= 2:
                    continue
                
                # Build topic list
                topics = [r['topic'] for r in reviews[:5]]
                topic_display = topics[0]
                if len(reviews) > 1:
                    topic_display = f"{topic_display} and {len(reviews)-1} more topics"
                
                # Generate personalized nudge using IntelligentProactiveMentor
                nudge = await mentor.get_revision_due_nudge(user_id)
                
                if nudge:
                    title = nudge.title
                    message = nudge.message
                else:
                    # Fallback message
                    title = "🧠 Time to Review!"
                    message = f"Ready to reinforce your learning? Topics due: {topic_display}"
                
                await notification_service.send_notification(
                    user_id=user_id,
                    title=title,
                    message=message,
                    notification_type=NudgeType.SPACED_REP.value,
                    priority='medium',
                    action={'label': 'Start Review', 'action': 'start_review'},
                    data={'topics': topics, 'personalized': nudge is not None}
                )
                
                # Log nudge
                await self.db.nudge_log.insert_one({
                    'user_id': user_id,
                    'nudge_type': 'spaced_rep',
                    'sent_at': now,
                    'topics': topics
                })
                
                logger.info(f"🔄 Spaced rep nudge sent | user={user_id} | topics={len(topics)}")
                
        except Exception as e:
            logger.error(f"Spaced repetition check failed: {e}")
    
    async def _check_comebacks(self):
        """Check for users who need comeback nudges using IntelligentProactiveMentor"""
        from services.intelligent_proactive_mentor import IntelligentProactiveMentor, NudgeType
        from services.notification_service import NotificationService
        
        mentor = IntelligentProactiveMentor(self.db)
        notification_service = NotificationService(self.db)
        
        now = datetime.utcnow()
        
        # Only run once per day (around 10 AM)
        if not (10 <= now.hour < 11):
            return
        
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        try:
            # Find inactive users (no session in last 2+ days)
            inactive_threshold = now - timedelta(days=2)
            
            pipeline = [
                {
                    '$lookup': {
                        'from': 'chat_sessions',
                        'let': {'uid': '$user_id'},
                        'pipeline': [
                            {
                                '$match': {
                                    '$expr': {'$eq': ['$user_id', '$$uid']}
                                }
                            },
                            {'$sort': {'updated_at': -1}},
                            {'$limit': 1}
                        ],
                        'as': 'last_session'
                    }
                },
                {
                    '$unwind': {
                        'path': '$last_session',
                        'preserveNullAndEmptyArrays': True
                    }
                },
                {
                    '$match': {
                        '$or': [
                            {'last_session': {'$exists': False}},
                            {'last_session.updated_at': {'$lt': inactive_threshold}}
                        ]
                    }
                },
                {'$limit': 20}
            ]
            
            inactive_users = await self.db.users.aggregate(pipeline).to_list(20)
            
            for user in inactive_users:
                user_id = user.get('user_id') or str(user.get('_id'))
                
                # Check if we already sent comeback nudge recently (last 3 days)
                recent_nudge = await self.db.nudge_log.find_one({
                    'user_id': user_id,
                    'nudge_type': 'comeback',
                    'sent_at': {'$gte': now - timedelta(days=3)}
                })
                
                if recent_nudge:
                    continue
                
                # Calculate days inactive
                last_session = user.get('last_session', {})
                last_activity = last_session.get('updated_at', now - timedelta(days=7))
                days_inactive = (now - last_activity).days
                
                # Get student name for personalization
                name = user.get('full_name', '').split()[0] if user.get('full_name') else 'there'
                last_topic = last_session.get('subject', 'your studies')
                
                # Generate personalized comeback nudge
                title = "🎯 We miss you!"
                message = f"Hey {name}, it's been {days_inactive} days! Your goals are waiting. Let's get back on track together! 💪"
                
                if last_topic and last_topic != 'your studies':
                    message = f"Hey {name}, it's been {days_inactive} days since we last worked on {last_topic}. Ready to pick up where we left off? 💪"
                
                await notification_service.send_notification(
                    user_id=user_id,
                    title=title,
                    message=message,
                    notification_type=NudgeType.COMEBACK.value,
                    priority='medium',
                    action={'label': 'Continue Learning', 'action': 'open_tutor'},
                    data={'days_inactive': days_inactive, 'last_topic': last_topic, 'personalized': True}
                )
                
                # Log nudge
                await self.db.nudge_log.insert_one({
                    'user_id': user_id,
                    'nudge_type': 'comeback',
                    'sent_at': now,
                    'days_inactive': days_inactive
                })
                
                logger.info(f"👋 Comeback nudge sent | user={user_id} | days_inactive={days_inactive}")
                
        except Exception as e:
            logger.error(f"Comeback check failed: {e}")
    
    async def _send_morning_greetings(self):
        """Send morning greetings to active learners"""
        from services.intelligent_proactive_mentor import NudgeType
        from services.notification_service import NotificationService
        
        notification_service = NotificationService(self.db)
        now = datetime.utcnow()
        
        # Only run between 7-9 AM
        if not (7 <= now.hour < 9):
            return
        
        # Only send morning greetings once per day per user
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        try:
            # Get users who want morning greetings and have been active recently
            active_users = await self.db.users.find({
                'preferences.morning_greeting': {'$ne': False},  # Not explicitly disabled
                'last_login': {'$gte': now - timedelta(days=7)}  # Active in last week
            }).limit(50).to_list(50)
            
            for user in active_users:
                user_id = user.get('user_id') or str(user.get('_id'))
                
                # Check if already sent today
                greeting_sent = await self.db.nudge_log.find_one({
                    'user_id': user_id,
                    'nudge_type': 'morning',
                    'sent_at': {'$gte': today_start}
                })
                
                if greeting_sent:
                    continue
                
                # Get student name and weak topics for personalization
                name = user.get('full_name', '').split()[0] if user.get('full_name') else ''
                name_greeting = f"{name}, " if name else ""
                
                # Try to get weak topics for personalized suggestion
                topic_suggestion = "your studies"
                try:
                    profile = await self.db.student_profiles.find_one({'user_id': user_id})
                    if profile and profile.get('weak_topics'):
                        topic_suggestion = profile['weak_topics'][0]
                except Exception:
                    pass
                
                title = "🌅 Good morning!"
                message = f"Rise and shine{', ' + name if name else ''}! Today's a great day to master {topic_suggestion}. Ready to learn?"
                
                await notification_service.send_notification(
                    user_id=user_id,
                    title=title,
                    message=message,
                    notification_type=NudgeType.MORNING_GREETING.value,
                    priority='low',
                    action={'label': 'Start Learning', 'action': 'open_tutor'},
                    data={'topic_suggestion': topic_suggestion, 'personalized': True}
                )
                
                # Log
                await self.db.nudge_log.insert_one({
                    'user_id': user_id,
                    'nudge_type': 'morning',
                    'sent_at': now
                })
                
                logger.info(f"☀️ Morning greeting sent | user={user_id}")
                
        except Exception as e:
            logger.error(f"Morning greeting failed: {e}")


# ===========================================
# STARTUP INTEGRATION
# ===========================================

_scheduler_instance: Optional[ProactiveScheduler] = None


async def start_proactive_scheduler(db_client):
    """Start the proactive scheduler (call on app startup)"""
    global _scheduler_instance
    
    _scheduler_instance = ProactiveScheduler(db_client)
    await _scheduler_instance.start()
    
    return _scheduler_instance


async def stop_proactive_scheduler():
    """Stop the proactive scheduler (call on app shutdown)"""
    global _scheduler_instance
    
    if _scheduler_instance:
        await _scheduler_instance.stop()
        _scheduler_instance = None


