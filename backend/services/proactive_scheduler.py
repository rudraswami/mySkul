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
    
    async def _process_reminders(self):
        """Process due reminders"""
        from services.reminder_scheduler import ReminderScheduler
        from services.notification_service import NotificationService
        from agents.proactive_companion import ProactiveCompanionAgent
        
        scheduler = ReminderScheduler(self.db)
        notification_service = NotificationService(self.db)
        
        due_reminders = await scheduler.get_due_reminders(lookahead_minutes=2)
        
        for reminder in due_reminders:
            try:
                # Build notification
                topic = reminder.get('topic', 'your study session')
                custom_message = reminder.get('custom_message')
                
                if custom_message:
                    message = custom_message
                else:
                    message = f"Time to study {topic}! 📚\n\nYou asked me to remind you. Ready to dive in?"
                
                # Send notification
                await notification_service.send_notification(
                    user_id=reminder['user_id'],
                    title=f"⏰ Reminder: {topic}",
                    message=message,
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
                        'context': reminder.get('context', {})
                    }
                )
                
                # Mark as sent
                await scheduler.mark_reminder_sent(reminder['reminder_id'])
                
                # Handle recurring
                if reminder.get('recurring'):
                    await scheduler.handle_recurring(reminder)
                
                logger.info(f"⏰ Reminder sent: {reminder['reminder_id']}")
                
            except Exception as e:
                logger.error(f"Failed to process reminder {reminder['reminder_id']}: {e}")
    
    async def _check_streaks(self):
        """Check for streaks that need protection using TRUE agentic companion"""
        from agents.agentic_companion import create_agentic_companion
        from core.config import settings
        
        # Use AgenticCompanion (TRUE agent with ReAct loop + tools)
        companion = create_agentic_companion({
            'db_client': self.db,
            'emergent_llm_key': settings.EMERGENT_LLM_KEY
        })
        
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Find users with active streaks who haven't studied today
        # and it's getting late (after 8 PM in their timezone)
        # For simplicity, using UTC evening hours
        
        if not (18 <= now.hour <= 22):
            return  # Only check during evening hours
        
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
                
                # Check if we already sent streak nudge today
                nudge_sent = await self.db.nudge_log.find_one({
                    'user_id': user_id,
                    'nudge_type': 'streak',
                    'sent_at': {'$gte': today_start}
                })
                
                if nudge_sent:
                    continue
                
                # Generate and send streak nudge
                nudge = await companion.generate_proactive_nudge(
                    user_id, NudgeType.STREAK_PROTECT
                )
                
                await notification_service.send_notification(
                    user_id=user_id,
                    title=nudge['title'],
                    message=nudge['message'],
                    notification_type='streak',
                    priority='high',
                    action=nudge.get('action')
                )
                
                # Log nudge
                await self.db.nudge_log.insert_one({
                    'user_id': user_id,
                    'nudge_type': 'streak',
                    'sent_at': now
                })
                
                logger.info(f"🔥 Streak nudge sent to {user_id}")
                
        except Exception as e:
            logger.error(f"Streak check failed: {e}")
    
    async def _process_spaced_rep(self):
        """Process spaced repetition reviews"""
        from services.reminder_scheduler import SpacedRepetitionEngine
        from agents.agentic_companion import create_agentic_companion
        from core.config import settings
        
        sr_engine = SpacedRepetitionEngine(self.db)
        
        # Use AgenticCompanion (TRUE agent with ReAct loop + tools)
        companion = create_agentic_companion({
            'db_client': self.db,
            'emergent_llm_key': settings.EMERGENT_LLM_KEY
        })
        
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
                # Check rate limit - max 2 SR nudges per day
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                nudge_count = await self.db.nudge_log.count_documents({
                    'user_id': user_id,
                    'nudge_type': 'spaced_rep',
                    'sent_at': {'$gte': today_start}
                })
                
                if nudge_count >= 2:
                    continue
                
                # Generate nudge
                topic = reviews[0]['topic']
                if len(reviews) > 1:
                    topic = f"{topic} and {len(reviews)-1} more topics"
                
                nudge = await companion.generate_proactive_nudge(
                    user_id, 
                    NudgeType.SPACED_REP,
                    {'topic': topic, 'days_since_learned': 7}
                )
                
                await notification_service.send_notification(
                    user_id=user_id,
                    title=nudge['title'],
                    message=nudge['message'],
                    notification_type='spaced_rep',
                    priority='medium',
                    action=nudge.get('action'),
                    data={'topics': [r['topic'] for r in reviews[:5]]}
                )
                
                # Log nudge
                await self.db.nudge_log.insert_one({
                    'user_id': user_id,
                    'nudge_type': 'spaced_rep',
                    'sent_at': now,
                    'topics': [r['topic'] for r in reviews[:5]]
                })
                
                logger.info(f"🔄 Spaced rep nudge sent to {user_id}")
                
        except Exception as e:
            logger.error(f"Spaced repetition check failed: {e}")
    
    async def _check_comebacks(self):
        """Check for users who need comeback nudges using TRUE agentic companion"""
        from agents.agentic_companion import create_agentic_companion
        from core.config import settings
        
        # Use AgenticCompanion (TRUE agent with ReAct loop + tools)
        companion = create_agentic_companion({
            'db_client': self.db,
            'emergent_llm_key': settings.EMERGENT_LLM_KEY
        })
        
        now = datetime.utcnow()
        
        # Only run once per day (around 10 AM)
        if not (10 <= now.hour < 11):
            return
        
        # Check for already run today
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
                user_id = user['user_id']
                
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
                
                # Update student profile with days inactive
                student_profile = {
                    'name': user.get('full_name', '').split()[0] if user.get('full_name') else '',
                    'days_inactive': days_inactive,
                    'last_topic': last_session.get('subject')
                }
                
                # Generate nudge
                nudge = await companion.generate_proactive_nudge(
                    user_id, NudgeType.COMEBACK
                )
                
                await notification_service.send_notification(
                    user_id=user_id,
                    title=nudge['title'],
                    message=nudge['message'],
                    notification_type='comeback',
                    priority='medium',
                    action=nudge.get('action')
                )
                
                # Log nudge
                await self.db.nudge_log.insert_one({
                    'user_id': user_id,
                    'nudge_type': 'comeback',
                    'sent_at': now,
                    'days_inactive': days_inactive
                })
                
                logger.info(f"👋 Comeback nudge sent to {user_id} (inactive {days_inactive} days)")
                
        except Exception as e:
            logger.error(f"Comeback check failed: {e}")
    
    async def _send_morning_greetings(self):
        """Send morning greetings to active learners"""
        from services.notification_service import NotificationService
        from agents.proactive_companion import ProactiveCompanionAgent, NudgeType
        
        now = datetime.utcnow()
        
        # Only run between 7-9 AM
        if not (7 <= now.hour < 9):
            return
        
        # Only send morning greetings once per day per user
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        from agents.agentic_companion import create_agentic_companion
        from core.config import settings
        
        # Use AgenticCompanion (TRUE agent with ReAct loop + tools)
        companion = create_agentic_companion({
            'db_client': self.db,
            'emergent_llm_key': settings.EMERGENT_LLM_KEY
        })
        
        try:
            # Get users who want morning greetings and have been active recently
            active_users = await self.db.users.find({
                'preferences.morning_greeting': {'$ne': False},  # Not explicitly disabled
                'last_login': {'$gte': now - timedelta(days=7)}  # Active in last week
            }).limit(50).to_list(50)
            
            for user in active_users:
                user_id = user['user_id']
                
                # Check if already sent today
                greeting_sent = await self.db.nudge_log.find_one({
                    'user_id': user_id,
                    'nudge_type': 'morning',
                    'sent_at': {'$gte': today_start}
                })
                
                if greeting_sent:
                    continue
                
                # Generate morning nudge
                nudge = await companion.generate_proactive_nudge(
                    user_id, NudgeType.MORNING_GREET
                )
                
                await notification_service.send_notification(
                    user_id=user_id,
                    title=nudge['title'],
                    message=nudge['message'],
                    notification_type='morning',
                    priority='low',
                    action=nudge.get('action')
                )
                
                # Log
                await self.db.nudge_log.insert_one({
                    'user_id': user_id,
                    'nudge_type': 'morning',
                    'sent_at': now
                })
                
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


