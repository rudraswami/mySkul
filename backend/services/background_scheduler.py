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
        """Stop the background scheduler gracefully"""
        self._running = False
        
        # Give ongoing tasks a moment to complete
        await asyncio.sleep(0.5)
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Background scheduler stopped")
    
    async def _run_loop(self):
        """Main scheduler loop - runs every minute for TRUE AGENTIC behavior"""
        loop_count = 0
        
        while self._running:
            try:
                loop_count += 1
                
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
                
                # 5. 🆕 LEARNING ENGINE - Run every 30 minutes (every 30 loops)
                if loop_count % 30 == 0:
                    await self._run_learning_engine()
                
                # 6. 🆕 EVENT DETECTION - Detect session ends, inactivity (every 5 mins)
                if loop_count % 5 == 0:
                    await self._detect_and_handle_events()
                
                # 7. 🔄 NOTIFICATION RETRY QUEUE - Process failed notifications
                await self._process_notification_retries()
                
                # 8. 🔌 WEBSOCKET CLEANUP - Remove stale connections (every 2 mins)
                if loop_count % 2 == 0:
                    await self._cleanup_websocket_connections()

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
            
            # Always log - even if 0 reminders (for debugging)
            logger.info(f"⏰ Checking reminders: {len(due_reminders)} due")
            
            if due_reminders:
                logger.info(f"📬 Processing {len(due_reminders)} due reminders")
            
            for reminder in due_reminders:
                try:
                    # Build meaningful notification content
                    topic = reminder.get('topic', '')
                    custom_msg = reminder.get('custom_message', '')
                    reminder_type = reminder.get('reminder_type', 'study')
                    
                    # Create better title based on type
                    if reminder_type == 'spaced_rep':
                        title = "🧠 Time to Review!"
                    elif reminder_type == 'quiz':
                        title = "📝 Quiz Time!"
                    elif reminder_type == 'revision':
                        title = "📖 Revision Reminder"
                    else:
                        title = "⏰ Study Reminder"
                    
                    # Create meaningful message
                    if custom_msg and len(custom_msg) > 10:
                        message = custom_msg
                    elif topic and topic.lower() not in ['study', 'reminder', '']:
                        message = f"Time to study: {topic}! You set this reminder earlier. Let's make progress! 📚"
                    else:
                        message = "Hey! It's study time. You've got this! Let's learn something amazing today. 💪"
                    
                    # Send notification
                    result = await notification_service.send_notification(
                        user_id=reminder['user_id'],
                        title=title,
                        message=message,
                        notification_type="reminder",
                        priority="high",
                        data={
                            'reminder_id': reminder['reminder_id'],
                            'topic': topic,
                            'reminder_type': reminder_type,
                            'custom_message': custom_msg
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
    
    async def _process_notification_retries(self):
        """
        Process failed notification deliveries from the retry queue.
        
        Uses exponential backoff to retry failed push/email deliveries.
        """
        try:
            from services.notification_service import NotificationService
            
            notification_service = NotificationService(self.db)
            processed = await notification_service.process_retry_queue()
            
            if processed > 0:
                logger.info(f"🔄 Processed {processed} notification retries")
                
        except Exception as e:
            logger.error(f"Notification retry processing error: {e}")
    
    async def _cleanup_websocket_connections(self):
        """
        Clean up stale WebSocket connections.
        
        Removes connections that haven't responded to heartbeat.
        """
        try:
            from services.websocket_manager import get_websocket_manager
            
            ws_manager = get_websocket_manager()
            await ws_manager.cleanup_stale_connections()
            
        except ImportError:
            pass  # WebSocket manager not available
        except Exception as e:
            logger.debug(f"WebSocket cleanup error: {e}")
    
    async def _check_proactive_triggers(self):
        """
        TRUE AGENTIC BEHAVIOR: Proactive outreach to students
        
        This makes the AI feel alive and caring - it reaches out proactively:
        - Morning greetings with study suggestions
        - Comeback messages for inactive users
        - Time-based study nudges
        - Streak protection (Level 2)
        - Intelligent nudges (Level 4)
        """
        try:
            now = datetime.utcnow()
            current_hour = now.hour
            # Convert to IST for timing decisions
            ist_hour = (current_hour + 5) % 24  # Approximate IST
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            from services.notification_service import NotificationService
            notification_service = NotificationService(self.db)
            
            # ===========================================
            # 🧠 INTELLIGENT PROACTIVE MENTOR (Level 2 & 4)
            # ===========================================
            await self._process_intelligent_nudges(notification_service)
            
            # ===========================================
            # 1. MORNING GREETINGS (6 AM - 8 AM IST)
            # ===========================================
            if 6 <= ist_hour < 8:
                await self._send_morning_greetings(notification_service, today_start)
            
            # ===========================================
            # 2. COMEBACK MESSAGES (6 PM - 8 PM IST)
            # ===========================================
            if 18 <= ist_hour < 20:
                await self._send_comeback_messages(notification_service, today_start)
            
            # ===========================================
            # 3. EVENING REVIEW NUDGE (8 PM - 9 PM IST)
            # ===========================================
            if 20 <= ist_hour < 21:
                await self._send_review_nudges(notification_service, today_start)
            
            # ===========================================
            # 4. DAILY SUMMARY (9 PM IST)
            # ===========================================
            if ist_hour == 21:
                await self._send_daily_summaries(notification_service)
                
        except Exception as e:
            logger.error(f"Proactive trigger error: {e}")
    
    async def _process_intelligent_nudges(self, notification_service):
        """
        🧠 MENTOR COMPANION - Intelligent Notification Decision Engine
        
        This is NOT a "send notifications" function.
        This asks: "Does each student NEED something from us right now?"
        
        Architecture:
        1. For each active user
        2. Compute student state (cognitive, emotional, momentum)
        3. Reason about intent (HELP > PROTECT > CELEBRATE > GUIDE > SILENCE)
        4. Check interruption gate (should we actually interrupt?)
        5. Only if approved: calibrate tone and compose message
        6. Track outcome for learning
        
        Default outcome: SILENCE (most common, most respectful)
        """
        try:
            from services.intelligent_proactive_mentor import (
                get_proactive_mentor,
                MentorIntent
            )
            
            mentor = await get_proactive_mentor(self.db)
            
            # Get active users (limit to prevent overload)
            active_users = await self.db.users.find({
                'is_active': True
            }).limit(100).to_list(length=100)
            
            # Statistics for logging
            stats = {
                "evaluated": 0,
                "silence": 0,
                "wait": 0,
                "backoff": 0,
                "notified": 0
            }
            
            for user in active_users:
                user_id = user.get('user_id') or str(user.get('_id'))
                
                try:
                    stats["evaluated"] += 1
                    
                    # ===================================================
                    # 🎯 MENTOR COMPANION DECISION FLOW (with Learning)
                    # Phase 2: Uses learned preferences to personalize
                    # ===================================================
                    
                    decision = await mentor.make_mentor_decision_with_learning(user_id)
                    
                    # Log the decision for observability
                    await self._log_mentor_decision(user_id, decision)
                    
                    if decision.action == "WAIT":
                        stats["wait"] += 1
                        continue
                    
                    if decision.action == "BACKOFF":
                        stats["backoff"] += 1
                        continue
                    
                    if decision.intent == MentorIntent.SILENCE:
                        stats["silence"] += 1
                        continue
                    
                    # ===================================================
                    # Decision approved - send notification
                    # ===================================================
                    if decision.approved and decision.message:
                        result = await notification_service.send_notification(
                            user_id=user_id,
                            title=decision.message.get("title", ""),
                            message=decision.message.get("message", ""),
                            notification_type=decision.intent.value,
                            priority="high" if decision.intent == MentorIntent.HELP else "medium",
                            data={
                                'mentor_intent': decision.intent.value,
                                'mentor_tone': decision.tone,
                                'mentor_confidence': decision.confidence,
                                'mentor_reason': decision.reason
                            },
                            skip_policy_check=True  # We already did intelligent checks
                        )
                        
                        if result.get('status') in ['sent', 'coalesced', 'stored']:
                            stats["notified"] += 1
                            logger.info(
                                f"🧠 Mentor SENT to {user_id}: "
                                f"intent={decision.intent.value}, tone={decision.tone}"
                            )
                        
                except Exception as e:
                    logger.error(f"Error in mentor decision for {user_id}: {e}")
                    continue
            
            # Log summary statistics
            logger.info(
                f"🧠 Mentor Companion Summary: "
                f"evaluated={stats['evaluated']}, "
                f"silence={stats['silence']}, "
                f"wait={stats['wait']}, "
                f"backoff={stats['backoff']}, "
                f"notified={stats['notified']}"
            )
            
            # Auto-track ignored notifications for learning
            await self._auto_track_ignored_notifications(notification_service)
                
        except Exception as e:
            logger.error(f"Mentor Companion processing error: {e}")
    
    async def _log_mentor_decision(self, user_id: str, decision):
        """Log mentor decision for analysis and debugging."""
        try:
            await self.db.mentor_decisions.insert_one({
                'user_id': user_id,
                'action': decision.action,
                'intent': decision.intent.value,
                'approved': decision.approved,
                'reason': decision.reason,
                'tone': decision.tone,
                'confidence': decision.confidence,
                'timestamp': datetime.utcnow()
            })
        except Exception as e:
            logger.debug(f"Failed to log mentor decision: {e}")
    
    async def _auto_track_ignored_notifications(self, notification_service):
        """Auto-track notifications that were ignored (no response in 2+ hours)."""
        try:
            # Get users who had notifications sent recently
            two_hours_ago = datetime.utcnow() - timedelta(hours=2)
            four_hours_ago = datetime.utcnow() - timedelta(hours=4)
            
            old_unread = await self.db.user_notifications.find({
                'created_at': {'$gte': four_hours_ago, '$lt': two_hours_ago},
                'read': False
            }).to_list(length=100)
            
            for notif in old_unread:
                user_id = notif.get('user_id')
                notification_id = notif.get('notification_id')
                
                if user_id and notification_id:
                    # Check if outcome already tracked
                    existing = await self.db.notification_outcomes.find_one({
                        'notification_id': notification_id
                    })
                    
                    if not existing:
                        await notification_service.track_notification_outcome(
                            user_id=user_id,
                            notification_id=notification_id,
                            outcome='ignored',
                            details={'auto_tracked': True}
                        )
            
        except Exception as e:
            logger.debug(f"Auto-track ignored error: {e}")
    
    # ==========================================================================
    # 🎓 PHASE 2: LEARNING ENGINE
    # ==========================================================================
    
    async def _run_learning_engine(self):
        """
        🧠 LEARNING ENGINE - Analyze outcomes and update student profiles.
        
        Runs every 30 minutes to:
        1. Analyze notification outcomes for each active student
        2. Update learning profiles with what works
        3. Adjust frequency, timing, and tone preferences
        
        This is what makes the Mentor Companion get smarter over time.
        """
        try:
            from services.intelligent_proactive_mentor import get_proactive_mentor
            
            mentor = await get_proactive_mentor(self.db)
            
            # Get users who have notification outcomes in the last 24 hours
            # (Only analyze users with recent activity)
            twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
            
            users_with_outcomes = await self.db.notification_outcomes.aggregate([
                {"$match": {"created_at": {"$gte": twenty_four_hours_ago}}},
                {"$group": {"_id": "$user_id"}},
                {"$limit": 50}  # Process max 50 users per run
            ]).to_list(length=50)
            
            if not users_with_outcomes:
                logger.debug("📚 Learning Engine: No recent outcomes to analyze")
                return
            
            learned_count = 0
            
            for user_doc in users_with_outcomes:
                user_id = user_doc.get("_id")
                if not user_id:
                    continue
                
                try:
                    # Run learning analysis for this user
                    profile = await mentor.analyze_and_learn(user_id)
                    
                    if profile.total_notifications_analyzed >= 5:
                        learned_count += 1
                        
                except Exception as e:
                    logger.warning(f"Learning failed for {user_id}: {e}")
                    continue
            
            if learned_count > 0:
                logger.info(f"📚 Learning Engine: Updated {learned_count} student profiles")
            
        except Exception as e:
            logger.error(f"Learning Engine error: {e}")
    
    # ==========================================================================
    # 🎯 PHASE 3: EVENT DETECTION
    # ==========================================================================
    
    async def _detect_and_handle_events(self):
        """
        🎯 PHASE 3: Detect meaningful events and handle them.
        
        Instead of just polling "should we notify?", we detect:
        - Session endings (opportunity for follow-up)
        - Inactivity (re-engagement opportunity)
        - Streak risks (protection)
        
        This runs every 5 minutes to catch events without polling every minute.
        """
        try:
            from services.intelligent_proactive_mentor import (
                get_proactive_mentor,
                MentorEvent,
                MentorEventData
            )
            from services.notification_service import NotificationService
            
            mentor = await get_proactive_mentor(self.db)
            notification_service = NotificationService(self.db)
            
            now = datetime.utcnow()
            
            # Get recently active users (activity in last 2 hours)
            two_hours_ago = now - timedelta(hours=2)
            
            recent_users = await self.db.chat_messages.aggregate([
                {"$match": {"timestamp": {"$gte": two_hours_ago}}},
                {"$group": {"_id": "$user_id"}},
                {"$limit": 50}
            ]).to_list(length=50)
            
            events_detected = 0
            events_handled = 0
            
            for user_doc in recent_users:
                user_id = user_doc.get("_id")
                if not user_id:
                    continue
                
                try:
                    # ===== DETECT SESSION END =====
                    session_event = await mentor.detect_session_end(user_id)
                    
                    if session_event:
                        events_detected += 1
                        
                        # Check if we already handled this session end
                        already_handled = await self.db.mentor_events.find_one({
                            "user_id": user_id,
                            "event_type": "session_ended",
                            "logged_at": {"$gte": now - timedelta(minutes=30)}
                        })
                        
                        if not already_handled:
                            decision = await mentor.handle_event(session_event)
                            
                            if decision and decision.approved and decision.message:
                                await notification_service.send_notification(
                                    user_id=user_id,
                                    title=decision.message.get("title", ""),
                                    message=decision.message.get("message", ""),
                                    notification_type=decision.intent.value,
                                    priority="medium",
                                    data={
                                        "event_type": "session_ended",
                                        "mentor_intent": decision.intent.value,
                                        "mentor_tone": decision.tone
                                    },
                                    skip_policy_check=True
                                )
                                events_handled += 1
                                logger.info(f"📡 Session end handled for {user_id}")
                    
                except Exception as e:
                    logger.warning(f"Event detection error for {user_id}: {e}")
                    continue
            
            # ===== DETECT INACTIVITY =====
            # Check users who were active yesterday but not today
            yesterday_start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0)
            today_start = now.replace(hour=0, minute=0, second=0)
            
            # Only run inactivity check during afternoon/evening (14:00 - 20:00)
            if 14 <= now.hour <= 20:
                inactive_pipeline = [
                    # Users with activity yesterday
                    {"$match": {
                        "timestamp": {"$gte": yesterday_start, "$lt": today_start}
                    }},
                    {"$group": {"_id": "$user_id"}},
                    {"$limit": 30}
                ]
                
                yesterday_users = await self.db.chat_messages.aggregate(inactive_pipeline).to_list(30)
                
                for user_doc in yesterday_users:
                    user_id = user_doc.get("_id")
                    if not user_id:
                        continue
                    
                    try:
                        # Check if they have activity today
                        today_activity = await self.db.chat_messages.find_one({
                            "user_id": user_id,
                            "timestamp": {"$gte": today_start}
                        })
                        
                        if not today_activity:
                            # Check if we already sent inactivity notification today
                            already_notified = await self.db.user_notifications.find_one({
                                "user_id": user_id,
                                "type": {"$in": ["protect", "guide"]},
                                "created_at": {"$gte": today_start}
                            })
                            
                            if not already_notified:
                                inactivity_event = MentorEventData(
                                    event_type=MentorEvent.INACTIVITY_DETECTED,
                                    user_id=user_id,
                                    timestamp=now,
                                    inactivity_hours=float((now - today_start).total_seconds() / 3600),
                                    source="scheduler"
                                )
                                
                                decision = await mentor.handle_event(inactivity_event)
                                
                                if decision and decision.approved and decision.message:
                                    await notification_service.send_notification(
                                        user_id=user_id,
                                        title=decision.message.get("title", ""),
                                        message=decision.message.get("message", ""),
                                        notification_type=decision.intent.value,
                                        priority="medium",
                                        data={
                                            "event_type": "inactivity",
                                            "mentor_intent": decision.intent.value,
                                            "mentor_tone": decision.tone
                                        },
                                        skip_policy_check=True
                                    )
                                    events_handled += 1
                                    logger.info(f"📡 Inactivity handled for {user_id}")
                        
                    except Exception as e:
                        logger.warning(f"Inactivity detection error for {user_id}: {e}")
                        continue
            
            if events_detected > 0 or events_handled > 0:
                logger.info(f"📡 Event Detection: detected={events_detected}, handled={events_handled}")
            
        except Exception as e:
            logger.error(f"Event detection error: {e}")
    
    async def _send_daily_summaries(self, notification_service):
        """Send end-of-day study summaries"""
        try:
            from services.intelligent_proactive_mentor import get_proactive_mentor
            
            mentor = await get_proactive_mentor(self.db)
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
            
            # Find users who studied today
            active_today = await self.db.chat_sessions.aggregate([
                {'$match': {'updated_at': {'$gte': today_start}}},
                {'$group': {'_id': '$user_id'}}
            ]).to_list(length=100)
            
            for user_doc in active_today:
                user_id = user_doc['_id']
                
                try:
                    # Check if summary already sent
                    existing = await self.db.user_notifications.find_one({
                        'user_id': user_id,
                        'type': 'daily_summary',
                        'created_at': {'$gte': today_start}
                    })
                    
                    if existing:
                        continue
                    
                    # Generate summary
                    summary_nudge = await mentor.generate_daily_summary(user_id)
                    
                    if summary_nudge:
                        await notification_service.send_notification(
                            user_id=user_id,
                            title=summary_nudge.title,
                            message=summary_nudge.message,
                            notification_type='daily_summary',
                            priority='low',
                            data=summary_nudge.data
                        )
                        
                except Exception as e:
                    logger.error(f"Daily summary error for {user_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Daily summaries error: {e}")
    
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


