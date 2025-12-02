"""
⏱️ Background Scheduler - Process Scheduled Tasks
=================================================

This module runs background tasks that enable TRUE AGENTIC behavior:
- Process scheduled reminders and send notifications
- Check for streak-breaking situations
- Send spaced repetition reminders
- Process proactive mentor triggers

Uses APScheduler for async-friendly background tasks.

Without this, scheduled reminders would NEVER be sent!
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler = None
_db_client = None


class BackgroundScheduler:
    """
    Background task scheduler for processing reminders and notifications.
    
    This is CRITICAL for true agentic behavior - without it,
    reminders scheduled by agents would never be sent.
    """
    
    def __init__(self, db_client):
        self.db = db_client
        self._running = False
        self._task = None
        logger.info("🕐 BackgroundScheduler initialized")
    
    async def start(self):
        """Start the background scheduler"""
        if self._running:
            logger.warning("Scheduler already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("✅ Background scheduler started")
    
    async def stop(self):
        """Stop the background scheduler"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Background scheduler stopped")
    
    async def _run_loop(self):
        """Main scheduler loop - runs every minute for TRUE AGENTIC behavior"""
        while self._running:
            try:
                # ======================================
                # CRITICAL: These enable TRUE AGENTS
                # Without these, agents cannot act on their own
                # ======================================
                
                # 1. Process due reminders (Agent-scheduled tasks)
                await self._process_reminders()

                # 2. Process scheduled notifications
                await self._process_scheduled_notifications()

                # 3. Check for streak protection (Gamification)
                await self._check_streaks()
                
                # 4. PROACTIVE NUDGES - Makes AI feel alive and caring
                await self._check_proactive_triggers()

            except Exception as e:
                logger.error(f"Scheduler error: {e}", exc_info=True)

            # Wait 60 seconds before next check
            await asyncio.sleep(60)
    
    async def _process_reminders(self):
        """Process due reminders and send notifications"""
        try:
            from services.reminder_scheduler import ReminderScheduler
            from services.notification_service import NotificationService
            
            scheduler = ReminderScheduler(self.db)
            notification_service = NotificationService(self.db)
            
            # Get reminders due in the next 5 minutes
            due_reminders = await scheduler.get_due_reminders(lookahead_minutes=5)
            
            if due_reminders:
                logger.info(f"📬 Processing {len(due_reminders)} due reminders")
            
            for reminder in due_reminders:
                try:
                    # Send notification
                    result = await notification_service.send_notification(
                        user_id=reminder['user_id'],
                        title="⏰ Reminder",
                        message=reminder.get('custom_message') or reminder.get('topic', 'Study reminder'),
                        notification_type="reminder",
                        priority="high",
                        data={
                            'reminder_id': reminder['reminder_id'],
                            'topic': reminder.get('topic'),
                            'reminder_type': reminder.get('reminder_type')
                        }
                    )
                    
                    if result.get('status') in ['sent', 'stored']:
                        # Mark reminder as sent
                        await scheduler.mark_reminder_sent(reminder['reminder_id'])
                        logger.info(f"✅ Reminder sent: {reminder['reminder_id']}")
                        
                        # Handle recurring reminders
                        if reminder.get('recurring'):
                            await scheduler.handle_recurring(reminder)
                    
                except Exception as e:
                    logger.error(f"Failed to process reminder {reminder.get('reminder_id')}: {e}")
                    
        except Exception as e:
            logger.error(f"Reminder processing error: {e}")
    
    async def _process_scheduled_notifications(self):
        """Process notifications scheduled for later delivery"""
        try:
            now = datetime.utcnow()
            
            # Find scheduled notifications that are now due
            due_notifications = await self.db.notifications.find({
                'status': 'scheduled',
                'scheduled_time': {'$lte': now}
            }).to_list(length=100)
            
            if due_notifications:
                logger.info(f"📬 Processing {len(due_notifications)} scheduled notifications")
            
            from services.notification_service import NotificationService
            notification_service = NotificationService(self.db)
            
            for notification in due_notifications:
                try:
                    # Deliver the notification
                    for channel in notification.get('channels', ['in_app']):
                        await notification_service._deliver_to_channel(channel, notification)
                    
                    # Update status
                    await self.db.notifications.update_one(
                        {'notification_id': notification['notification_id']},
                        {
                            '$set': {
                                'status': 'sent',
                                'sent_at': now
                            }
                        }
                    )
                    
                except Exception as e:
                    logger.error(f"Failed to send notification: {e}")
                    
        except Exception as e:
            logger.error(f"Notification processing error: {e}")
    
    async def _check_proactive_triggers(self):
        """
        TRUE AGENTIC BEHAVIOR: Proactive outreach to students
        
        This makes the AI feel alive and caring - it reaches out proactively:
        - Morning greetings with study suggestions
        - Comeback messages for inactive users
        - Time-based study nudges
        """
        try:
            now = datetime.utcnow()
            current_hour = now.hour
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            from services.notification_service import NotificationService
            notification_service = NotificationService(self.db)
            
            # ===========================================
            # 1. MORNING GREETINGS (6 AM - 8 AM window)
            # ===========================================
            if 6 <= current_hour < 8:
                await self._send_morning_greetings(notification_service, today_start)
            
            # ===========================================
            # 2. COMEBACK MESSAGES (7 PM window for inactive users)
            # ===========================================
            if 18 <= current_hour < 20:
                await self._send_comeback_messages(notification_service, today_start)
            
            # ===========================================
            # 3. EVENING REVIEW NUDGE (8 PM - 9 PM)
            # ===========================================
            if 20 <= current_hour < 21:
                await self._send_review_nudges(notification_service, today_start)
                
        except Exception as e:
            logger.error(f"Proactive trigger error: {e}")
    
    async def _send_morning_greetings(self, notification_service, today_start):
        """Send personalized morning greetings"""
        try:
            # Find active users who haven't received morning greeting today
            users = await self.db.users.find({
                'is_active': True,
                'notification_preferences.morning_greeting': {'$ne': False}
            }).to_list(length=50)
            
            for user in users:
                user_id = str(user.get('_id'))
                
                # Check if already greeted today
                existing = await self.db.user_notifications.find_one({
                    'user_id': user_id,
                    'type': 'morning_greeting',
                    'created_at': {'$gte': today_start}
                })
                
                if existing:
                    continue
                
                # Get user's weak areas for personalized suggestion
                weak_areas = await self.db.user_weak_areas.find_one({'user_id': user_id})
                topic_suggestion = weak_areas.get('top_weak_topic', 'your studies') if weak_areas else 'your studies'
                
                name = user.get('name', 'Student')
                
                await notification_service.send_notification(
                    user_id=user_id,
                    title="🌅 Good morning!",
                    message=f"Rise and shine, {name}! Today's a great day to master {topic_suggestion}. Ready to learn?",
                    notification_type="morning_greeting",
                    priority="low",
                    action={'label': "Start Learning", 'url': "/ai-tutor"}
                )
                
                logger.info(f"☀️ Morning greeting sent to {user_id}")
                
        except Exception as e:
            logger.error(f"Morning greeting error: {e}")
    
    async def _send_comeback_messages(self, notification_service, today_start):
        """Send comeback messages to inactive users"""
        try:
            # Find users inactive for 2-7 days
            two_days_ago = today_start - timedelta(days=2)
            week_ago = today_start - timedelta(days=7)
            
            inactive_users = await self.db.users.find({
                'is_active': True,
                'last_activity': {
                    '$lt': two_days_ago,
                    '$gt': week_ago
                }
            }).to_list(length=30)
            
            for user in inactive_users:
                user_id = str(user.get('_id'))
                
                # Check if already sent comeback message this week
                existing = await self.db.user_notifications.find_one({
                    'user_id': user_id,
                    'type': 'comeback_message',
                    'created_at': {'$gte': week_ago}
                })
                
                if existing:
                    continue
                
                name = user.get('name', 'there')
                days_inactive = (today_start - user.get('last_activity', today_start)).days
                
                await notification_service.send_notification(
                    user_id=user_id,
                    title="🎯 We miss you!",
                    message=f"Hey {name}, it's been {days_inactive} days! Your goals are waiting. Let's get back on track together! 💪",
                    notification_type="comeback_message",
                    priority="medium",
                    action={'label': "Continue Learning", 'url': "/ai-tutor"}
                )
                
                logger.info(f"🎯 Comeback message sent to {user_id}")
                
        except Exception as e:
            logger.error(f"Comeback message error: {e}")
    
    async def _send_review_nudges(self, notification_service, today_start):
        """Send spaced repetition review nudges"""
        try:
            now = datetime.utcnow()
            
            # Find topics due for review (spaced repetition)
            due_reviews = await self.db.spaced_repetition.find({
                'next_review': {'$lte': now},
                'status': 'pending'
            }).to_list(length=50)
            
            # Group by user
            user_reviews = {}
            for review in due_reviews:
                user_id = review.get('user_id')
                if user_id not in user_reviews:
                    user_reviews[user_id] = []
                user_reviews[user_id].append(review.get('topic'))
            
            for user_id, topics in user_reviews.items():
                # Check if already nudged today
                existing = await self.db.user_notifications.find_one({
                    'user_id': user_id,
                    'type': 'review_nudge',
                    'created_at': {'$gte': today_start}
                })
                
                if existing:
                    continue
                
                topic_list = ', '.join(topics[:3])
                more_count = len(topics) - 3 if len(topics) > 3 else 0
                more_text = f" +{more_count} more" if more_count else ""
                
                await notification_service.send_notification(
                    user_id=user_id,
                    title="📚 Review time!",
                    message=f"Time to reinforce your learning! Topics ready for review: {topic_list}{more_text}",
                    notification_type="review_nudge",
                    priority="medium",
                    action={'label': "Start Review", 'url': "/review"}
                )
                
                logger.info(f"📚 Review nudge sent to {user_id}")
                
        except Exception as e:
            logger.error(f"Review nudge error: {e}")

    async def _check_streaks(self):
        """Check for streaks that are about to break and send warnings"""       
        try:
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Find users with active streaks who haven't studied today
            # This is a simplified check - enhance based on your gamification system
            
            users_at_risk = await self.db.user_gamification.find({
                'streak': {'$gt': 3},  # Only warn users with meaningful streaks
                'last_activity_date': {'$lt': today_start}
            }).to_list(length=100)
            
            if not users_at_risk:
                return
            
            # Only send one streak warning per day (check if already sent)
            from services.notification_service import NotificationService
            notification_service = NotificationService(self.db)
            
            for user in users_at_risk:
                user_id = user.get('user_id')
                streak = user.get('streak', 0)
                
                # Check if we already warned today
                existing_warning = await self.db.user_notifications.find_one({
                    'user_id': user_id,
                    'type': 'streak_warning',
                    'created_at': {'$gte': today_start}
                })
                
                if existing_warning:
                    continue
                
                # Send streak warning
                await notification_service.send_notification(
                    user_id=user_id,
                    title="🔥 Your streak is in danger!",
                    message=f"You have a {streak}-day streak! Study now to keep it going! 💪",
                    notification_type="streak_warning",
                    priority="high",
                    action={
                        'label': "Study Now",
                        'url': "/ai-tutor"
                    }
                )
                
                logger.info(f"🔥 Streak warning sent to {user_id} (streak: {streak})")
                
        except Exception as e:
            logger.error(f"Streak check error: {e}")


# ==============================================
# Module-level functions for easy access
# ==============================================

async def start_background_scheduler(db_client):
    """Start the background scheduler"""
    global _scheduler, _db_client
    
    _db_client = db_client
    _scheduler = BackgroundScheduler(db_client)
    await _scheduler.start()
    
    return _scheduler


async def stop_background_scheduler():
    """Stop the background scheduler"""
    global _scheduler
    
    if _scheduler:
        await _scheduler.stop()
        _scheduler = None


def get_scheduler() -> Optional[BackgroundScheduler]:
    """Get the current scheduler instance"""
    return _scheduler


