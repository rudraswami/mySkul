"""
🔔 NOTIFICATION SERVICE - Multi-Channel Notification Delivery

This service handles sending notifications through multiple channels:
- In-App notifications (real-time via WebSocket)
- Push notifications (browser/mobile)
- Email notifications
- SMS (future)
- WhatsApp (future)

Features:
- Priority-based delivery
- Rate limiting (don't spam students)
- Quiet hours respect
- Channel preferences
- Retry logic with exponential backoff
- Dead-letter queue for failed notifications
- Graceful fallback (WebSocket → polling, push/email → retry)
"""

import logging
import os
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from enum import Enum
import uuid
import asyncio

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAYS = [30, 120, 300]  # Seconds: 30s, 2min, 5min


class NotificationChannel(Enum):
    """Available notification channels"""
    IN_APP = "in_app"           # In-app notification center
    PUSH = "push"               # Browser/mobile push
    EMAIL = "email"             # Email notification
    SMS = "sms"                 # SMS (future)
    WHATSAPP = "whatsapp"       # WhatsApp (future)


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"           # Can be batched, delayed
    MEDIUM = "medium"     # Send soon but respect quiet hours
    HIGH = "high"         # Send immediately, but respect Do Not Disturb
    URGENT = "urgent"     # Send immediately, override DND (streak about to break)


class NotificationService:
    """
    Multi-channel notification service with smart delivery
    """
    
    # Quiet hours (don't disturb during these times)
    DEFAULT_QUIET_HOURS = {
        'start': 22,  # 10 PM
        'end': 7      # 7 AM
    }
    
    # Rate limits (per user per day)
    RATE_LIMITS = {
        'low': 10,
        'medium': 5,
        'high': 3,
        'urgent': 1
    }
    
    # ================================================================
    # 🎯 NOTIFICATION POLICY ENGINE - Zero Spam
    # ================================================================
    
    # Per-type cooldowns (minimum minutes between same type)
    TYPE_COOLDOWNS = {
        'break_suggestion': 60,      # 1 hour between break nudges
        'streak_protection': 240,    # 4 hours between streak warnings
        'spaced_rep': 180,           # 3 hours between review nudges
        'revision_due': 180,         # 3 hours between revision nudges (same as spaced_rep)
        'morning_greeting': 1440,    # Once per day
        'daily_summary': 1440,       # Once per day
        'comeback': 4320,            # 3 days between comeback nudges
        'reminder': 5,               # User-requested, allow frequent
        'motivation': 120,           # 2 hours between motivation
    }
    
    # Daily caps per type
    DAILY_CAPS = {
        'break_suggestion': 3,       # Max 3 break nudges/day
        'streak_protection': 2,      # Max 2 streak warnings/day
        'spaced_rep': 2,             # Max 2 review nudges/day
        'revision_due': 2,           # Max 2 revision nudges/day (same as spaced_rep)
        'morning_greeting': 1,       # Max 1/day
        'daily_summary': 1,          # Max 1/day
        'comeback': 1,               # Max 1/day
        'motivation': 3,             # Max 3/day
        'reminder': 20,              # User-requested, high cap
    }
    
    # Skip if user active (for these types)
    SKIP_IF_ACTIVE_TYPES = {'break_suggestion', 'motivation', 'spaced_rep'}
    ACTIVE_THRESHOLD_MINUTES = 5
    
    def __init__(self, db_client=None, websocket_manager=None):
        self.db = db_client
        self.ws_manager = websocket_manager
        self._notification_queue = asyncio.Queue()
        
        # Auto-inject WebSocket manager if not provided
        if self.ws_manager is None:
            try:
                from services.websocket_manager import get_websocket_manager
                self.ws_manager = get_websocket_manager()
            except ImportError:
                logger.debug("WebSocket manager not available")
            except Exception as e:
                logger.debug(f"Could not get WebSocket manager: {e}")
    
    # ================================================================
    # 🎯 POLICY ENGINE: should_send_notification()
    # ================================================================
    
    async def should_send_notification(
        self,
        user_id: str,
        notification_type: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        POLICY ENGINE: Check if notification is allowed.
        
        Returns:
            {
                'allowed': bool,
                'reason': str,
                'next_allowed_at': datetime (if blocked)
            }
        """
        if self.db is None:
            return {'allowed': True, 'reason': 'no_db'}
        
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 1. Check quiet hours (except urgent)
        if self._is_quiet_hours(user_id):
            next_time = self._get_next_active_time()
            return {
                'allowed': False,
                'reason': 'quiet_hours',
                'next_allowed_at': next_time
            }
        
        # 2. Check if user is currently active (for certain types)
        if notification_type in self.SKIP_IF_ACTIVE_TYPES:
            if await self._is_user_active(user_id):
                return {
                    'allowed': False,
                    'reason': 'user_active',
                    'next_allowed_at': now + timedelta(minutes=self.ACTIVE_THRESHOLD_MINUTES)
                }
        
        # 3. Check type-specific cooldown
        cooldown_minutes = self.TYPE_COOLDOWNS.get(notification_type, 30)
        cooldown_threshold = now - timedelta(minutes=cooldown_minutes)
        
        recent_same_type = await self.db.user_notifications.find_one({
            'user_id': user_id,
            'type': notification_type,
            'created_at': {'$gte': cooldown_threshold}
        })
        
        if recent_same_type:
            last_sent = recent_same_type.get('created_at', now)
            next_allowed = last_sent + timedelta(minutes=cooldown_minutes)
            return {
                'allowed': False,
                'reason': f'cooldown_{notification_type}',
                'next_allowed_at': next_allowed,
                'last_sent': last_sent
            }
        
        # 4. Check daily cap
        daily_cap = self.DAILY_CAPS.get(notification_type, 10)
        today_count = await self.db.user_notifications.count_documents({
            'user_id': user_id,
            'type': notification_type,
            'created_at': {'$gte': today_start}
        })
        
        if today_count >= daily_cap:
            tomorrow_start = today_start + timedelta(days=1)
            return {
                'allowed': False,
                'reason': f'daily_cap_{notification_type}',
                'next_allowed_at': tomorrow_start,
                'count_today': today_count,
                'cap': daily_cap
            }
        
        # 5. Check for snooze/dismiss backoff
        dismiss_count = await self._get_recent_dismiss_count(user_id, notification_type)
        if dismiss_count >= 3:
            # User dismissed 3+ times recently, back off
            return {
                'allowed': False,
                'reason': 'user_dismissed_repeatedly',
                'dismiss_count': dismiss_count
            }
        
        # All checks passed
        logger.debug(f"✅ Policy ALLOW: {notification_type} for user {user_id}")
        return {'allowed': True, 'reason': 'passed_all_checks'}
    
    async def _is_user_active(self, user_id: str) -> bool:
        """Check if user has recent activity (chat, session)"""
        if self.db is None:
            return False
        
        threshold = datetime.utcnow() - timedelta(minutes=self.ACTIVE_THRESHOLD_MINUTES)
        
        # Check recent chat messages
        recent_msg = await self.db.chat_messages.find_one({
            'user_id': user_id,
            'timestamp': {'$gte': threshold}
        })
        if recent_msg:
            return True
        
        # Check active sessions
        recent_session = await self.db.chat_sessions.find_one({
            'user_id': user_id,
            'updated_at': {'$gte': threshold}
        })
        if recent_session:
            return True
        
        return False
    
    async def _get_recent_dismiss_count(self, user_id: str, notification_type: str) -> int:
        """Count how many times user dismissed this type recently (last 24h)"""
        if self.db is None:
            return 0
        
        threshold = datetime.utcnow() - timedelta(hours=24)
        
        return await self.db.notification_actions.count_documents({
            'user_id': user_id,
            'notification_type': notification_type,
            'action': 'dismiss',
            'timestamp': {'$gte': threshold}
        })
    
    def _generate_idempotency_key(
        self,
        user_id: str,
        notification_type: str,
        window_minutes: int = 60
    ) -> str:
        """
        Generate idempotency key to prevent duplicates.
        Key changes every `window_minutes` to allow periodic notifications.
        """
        import hashlib
        now = datetime.utcnow()
        # Round to window
        window_start = now.replace(
            minute=(now.minute // window_minutes) * window_minutes if window_minutes < 60 else 0,
            second=0,
            microsecond=0
        )
        if window_minutes >= 60:
            window_start = window_start.replace(hour=(now.hour // (window_minutes // 60)) * (window_minutes // 60))
        
        key_string = f"{user_id}:{notification_type}:{window_start.isoformat()}"
        return hashlib.md5(key_string.encode()).hexdigest()[:16]
    
    async def send_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str,
        priority: str = "medium",
        channels: List[str] = None,
        action: Dict[str, Any] = None,
        data: Dict[str, Any] = None,
        schedule_time: datetime = None,
        skip_policy_check: bool = False
    ) -> Dict[str, Any]:
        """
        Send notification through specified channels
        
        Args:
            user_id: Target user
            title: Notification title
            message: Notification body
            notification_type: Type (reminder, streak, achievement, etc.)
            priority: low/medium/high/urgent
            channels: List of channels (defaults to user preference)
            action: Action button config
            data: Additional data
            schedule_time: Future delivery time (optional)
            skip_policy_check: Skip policy engine (for urgent user-requested)
        
        Returns:
            Notification result with status per channel
        """
        notification_id = str(uuid.uuid4())
        
        # ================================================================
        # 🎯 POLICY ENGINE CHECK (unless skipped for urgent/user-requested)
        # ================================================================
        if not skip_policy_check and priority != 'urgent':
            policy_result = await self.should_send_notification(
                user_id=user_id,
                notification_type=notification_type,
                context={'priority': priority, 'title': title}
            )
            
            if not policy_result.get('allowed', True):
                reason = policy_result.get('reason', 'policy_blocked')
                logger.info(f"🚫 Policy BLOCKED: {notification_type} for {user_id} | reason={reason}")
                return {
                    'notification_id': notification_id,
                    'status': 'blocked_by_policy',
                    'reason': reason,
                    'next_allowed_at': policy_result.get('next_allowed_at')
                }
        
        # ================================================================
        # DEDUPE: Check idempotency key to prevent duplicates
        # ================================================================
        cooldown = self.TYPE_COOLDOWNS.get(notification_type, 60)
        idempotency_key = self._generate_idempotency_key(user_id, notification_type, cooldown)
        
        if self.db is not None:
            existing = await self.db.user_notifications.find_one({
                'user_id': user_id,
                'idempotency_key': idempotency_key
            })
            
            if existing:
                # Update existing instead of creating duplicate
                # ✅ FIX: Update title, message, AND created_at to show latest intelligent content
                now = datetime.utcnow()
                await self.db.user_notifications.update_one(
                    {'_id': existing['_id']},
                    {
                        '$set': {
                            'title': title,      # ✅ Update title with new intelligent content
                            'message': message,  # ✅ Update message with new intelligent content
                            'created_at': now,   # ✅ Update timestamp so it appears as new
                            'updated_at': now,
                            'read': False        # ✅ Mark as unread again
                        },
                        '$inc': {'coalesce_count': 1}
                    }
                )
                logger.info(f"🔄 Notification coalesced (refreshed): {notification_type} for {user_id}")
                return {
                    'notification_id': existing.get('notification_id'),
                    'status': 'coalesced',
                    'coalesce_count': existing.get('coalesce_count', 1) + 1
                }
        
        # Check rate limits
        if not await self._check_rate_limit(user_id, priority):
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return {
                'notification_id': notification_id,
                'status': 'rate_limited',
                'message': 'Too many notifications sent today'
            }
        
        # Check quiet hours (except for urgent)
        if priority != 'urgent' and self._is_quiet_hours(user_id):
            # Queue for later delivery
            if schedule_time is None:
                schedule_time = self._get_next_active_time()
            logger.info(f"Quiet hours - scheduling notification for {schedule_time}")
        
        # Get user's channel preferences
        if channels is None:
            channels = await self._get_user_channels(user_id)
        
        # Build notification document WITH idempotency key
        notification = {
            'notification_id': notification_id,
            'user_id': user_id,
            'title': title,
            'message': message,
            'type': notification_type,
            'priority': priority,
            'channels': channels,
            'action': action,
            'data': data or {},
            'created_at': datetime.utcnow(),
            'scheduled_time': schedule_time,
            'status': 'pending',
            'delivery_status': {channel: 'pending' for channel in channels},
            'idempotency_key': idempotency_key,  # ✅ Dedupe key
            'coalesce_count': 1
        }
        
        # Save to database
        if self.db is not None:
            await self.db.notifications.insert_one(notification)
        
        # Send immediately or queue
        if schedule_time and schedule_time > datetime.utcnow():
            return {
                'notification_id': notification_id,
                'status': 'scheduled',
                'scheduled_time': schedule_time.isoformat()
            }
        
        # Deliver through each channel with retry support
        results = {}
        failed_channels = []
        
        for channel in channels:
            try:
                result = await self._deliver_to_channel(
                    channel, notification
                )
                results[channel] = result
                
                # Track failures for retry
                if result.get('status') == 'failed':
                    failed_channels.append(channel)
                    
            except Exception as e:
                logger.error(f"Failed to deliver to {channel}: {e}")
                results[channel] = {'status': 'failed', 'error': str(e)}
                failed_channels.append(channel)
        
        # Queue failed channels for retry (dead-letter queue)
        if failed_channels and self.db is not None:
            await self._queue_for_retry(notification, failed_channels, results)
        
        # Update delivery status
        if self.db is not None:
            await self.db.notifications.update_one(
                {'notification_id': notification_id},
                {
                    '$set': {
                        'delivery_status': results,
                        'status': 'sent' if not failed_channels else 'partial',
                        'sent_at': datetime.utcnow(),
                        'failed_channels': failed_channels
                    }
                }
            )
        
        logger.info(f"✅ Notification sent: {notification_type} to {user_id}")
        return {
            'notification_id': notification_id,
            'status': 'sent',
            'channels': results
        }
    
    async def _deliver_to_channel(
        self,
        channel: str,
        notification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deliver notification to specific channel"""
        
        if channel == NotificationChannel.IN_APP.value:
            return await self._send_in_app(notification)
        
        elif channel == NotificationChannel.PUSH.value:
            return await self._send_push(notification)
        
        elif channel == NotificationChannel.EMAIL.value:
            return await self._send_email(notification)
        
        else:
            return {'status': 'unsupported', 'channel': channel}
    
    async def _send_in_app(
        self,
        notification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send in-app notification (real-time via WebSocket)"""
        user_id = notification['user_id']
        idempotency_key = notification.get('idempotency_key')
        
        # Store in notification center with dedupe
        if self.db is not None:
            # Check for existing notification with same idempotency key
            if idempotency_key:
                existing = await self.db.user_notifications.find_one({
                    'user_id': user_id,
                    'idempotency_key': idempotency_key
                })
                
                if existing:
                    # Update existing instead of inserting duplicate
                    # ✅ FIX: Update title, message, AND created_at to show latest intelligent content
                    now = datetime.utcnow()
                    await self.db.user_notifications.update_one(
                        {'_id': existing['_id']},
                        {
                            '$set': {
                                'title': notification['title'],    # ✅ Update title
                                'message': notification['message'],  # ✅ Update message
                                'created_at': now,                   # ✅ Update timestamp so it appears new
                                'updated_at': now,
                                'read': False  # Mark unread again
                            },
                            '$inc': {'coalesce_count': 1}
                        }
                    )
                    logger.debug(f"🔄 In-app notification coalesced (refreshed) for {user_id}")
                    return {'status': 'coalesced', 'existing_id': existing.get('notification_id')}
            
            # Insert new notification
            await self.db.user_notifications.insert_one({
                'user_id': user_id,
                'notification_id': notification['notification_id'],
                'title': notification['title'],
                'message': notification['message'],
                'type': notification['type'],
                'action': notification.get('action'),
                'data': notification.get('data'),
                'read': False,
                'created_at': datetime.utcnow(),
                'idempotency_key': idempotency_key,
                'coalesce_count': 1
            })
        
        # Send via WebSocket if user is online
        if self.ws_manager:
            try:
                await self.ws_manager.send_to_user(user_id, {
                    'type': 'notification',
                    'notification': {
                        'id': notification['notification_id'],
                        'title': notification['title'],
                        'message': notification['message'],
                        'type': notification['type'],
                        'action': notification.get('action')
                    }
                })
                return {'status': 'delivered', 'realtime': True}
            except Exception as e:
                logger.debug(f"WebSocket delivery failed (user may be offline): {e}")
                return {'status': 'stored', 'realtime': False}
        
        return {'status': 'stored', 'realtime': False}
    
    async def _send_push(
        self,
        notification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send browser/mobile push notification"""
        user_id = notification['user_id']
        
        # Get user's push subscription
        if self.db is None:
            return {'status': 'no_db'}
        
        subscriptions = await self.db.push_subscriptions.find(
            {'user_id': user_id}
        ).to_list(length=10)
        
        if not subscriptions:
            return {'status': 'no_subscription'}
        
        # Build push payload
        push_payload = json.dumps({
            'title': notification['title'],
            'body': notification['message'],
            'icon': '/icon-192.png',
            'badge': '/badge-72.png',
            'data': {
                'notification_id': notification.get('notification_id'),
                'type': notification.get('type'),
                'url': f"/dashboard?notification={notification.get('notification_id')}",
                **(notification.get('data') or {})
            },
            'actions': [
                {'action': 'open', 'title': 'Open'},
                {'action': 'dismiss', 'title': 'Dismiss'}
            ]
        })
        
        # Get VAPID keys from environment
        vapid_private_key = os.environ.get('VAPID_PRIVATE_KEY', '')
        vapid_email = os.environ.get('VAPID_EMAIL', 'mailto:support@druvai.com')
        
        if not vapid_private_key:
            logger.warning("⚠️ VAPID_PRIVATE_KEY not configured - push notifications disabled")
            return {'status': 'not_configured', 'reason': 'VAPID keys missing'}
        
        # Send push notifications
        success_count = 0
        failed_subscriptions = []
        
        try:
            from pywebpush import webpush, WebPushException
            
            for sub in subscriptions:
                try:
                    webpush(
                        subscription_info=sub.get('subscription', sub),
                        data=push_payload,
                        vapid_private_key=vapid_private_key,
                        vapid_claims={'sub': vapid_email}
                    )
                    success_count += 1
                except WebPushException as e:
                    logger.warning(f"Push failed for subscription: {e}")
                    failed_subscriptions.append(sub.get('_id'))
                    
                    # Remove invalid subscriptions (410 Gone)
                    if e.response and e.response.status_code == 410:
                        await self.db.push_subscriptions.delete_one({'_id': sub['_id']})
                        logger.info(f"Removed expired push subscription")
                except Exception as e:
                    logger.warning(f"Push send error: {e}")
                    failed_subscriptions.append(sub.get('_id'))
            
            if success_count > 0:
                logger.info(f"📱 Push sent to {user_id}: {success_count}/{len(subscriptions)} subscriptions")
                return {
                    'status': 'sent',
                    'success_count': success_count,
                    'failed_count': len(failed_subscriptions),
                    'subscriptions': len(subscriptions)
                }
            else:
                return {
                    'status': 'failed',
                    'reason': 'all_subscriptions_failed',
                    'failed_count': len(failed_subscriptions)
                }
                
        except ImportError:
            logger.warning("⚠️ pywebpush not installed - push notifications unavailable")
            return {'status': 'not_available', 'reason': 'pywebpush not installed'}
    
    async def _send_email(
        self,
        notification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send email notification"""
        user_id = notification['user_id']
        
        if self.db is None:
            return {'status': 'no_db'}
        
        # Get user email
        user = await self.db.users.find_one({'user_id': user_id})
        if not user or not user.get('email'):
            return {'status': 'no_email'}
        
        email = user['email']
        
        # Build email content
        email_body = self._build_email_template(notification)
        
        # Use real email service
        try:
            from services.email_service import get_email_service
            
            email_service = get_email_service()
            result = await email_service.send_email(
                to=email,
                subject=notification['title'],
                html_content=email_body
            )
            
            if result.success:
                logger.info(f"📧 Email sent to {email}: {notification['title']}")
                return {
                    'status': 'sent',
                    'email': email,
                    'message_id': result.message_id,
                    'provider': result.provider
                }
            else:
                logger.warning(f"📧 Email failed to {email}: {result.error}")
                return {
                    'status': 'failed',
                    'email': email,
                    'error': result.error,
                    'provider': result.provider
                }
                
        except ImportError:
            logger.warning("⚠️ Email service not available")
            return {'status': 'not_available', 'reason': 'email_service_missing'}
        except Exception as e:
            logger.error(f"📧 Email send error: {e}")
            return {'status': 'failed', 'email': email, 'error': str(e)}
    
    # ================================================================
    # 🔄 RETRY LOGIC + DEAD-LETTER QUEUE
    # ================================================================
    
    async def _queue_for_retry(
        self,
        notification: Dict[str, Any],
        failed_channels: List[str],
        results: Dict[str, Any]
    ):
        """
        Queue failed notification deliveries for retry.
        
        Uses exponential backoff: 30s, 2min, 5min
        After MAX_RETRY_ATTEMPTS, moves to dead-letter queue.
        """
        notification_id = notification.get('notification_id')
        retry_count = notification.get('retry_count', 0)
        
        if retry_count >= MAX_RETRY_ATTEMPTS:
            # Move to dead-letter queue
            await self._move_to_dead_letter(notification, failed_channels, results)
            return
        
        # Calculate next retry time
        delay_seconds = RETRY_DELAYS[min(retry_count, len(RETRY_DELAYS) - 1)]
        next_retry = datetime.utcnow() + timedelta(seconds=delay_seconds)
        
        # Create retry record
        retry_doc = {
            'notification_id': notification_id,
            'notification': notification,
            'failed_channels': failed_channels,
            'retry_count': retry_count + 1,
            'next_retry_at': next_retry,
            'last_error': {channel: results.get(channel, {}).get('error') for channel in failed_channels},
            'created_at': datetime.utcnow(),
            'status': 'pending'
        }
        
        try:
            await self.db.notification_retry_queue.insert_one(retry_doc)
            logger.info(f"🔄 Queued for retry: {notification_id}, attempt {retry_count + 1}, next at {next_retry}")
        except Exception as e:
            logger.error(f"Failed to queue for retry: {e}")
    
    async def _move_to_dead_letter(
        self,
        notification: Dict[str, Any],
        failed_channels: List[str],
        results: Dict[str, Any]
    ):
        """
        Move permanently failed notification to dead-letter queue.
        
        Notifications here need manual review or are unrecoverable.
        """
        notification_id = notification.get('notification_id')
        
        dead_letter_doc = {
            'notification_id': notification_id,
            'notification': notification,
            'failed_channels': failed_channels,
            'final_errors': {channel: results.get(channel, {}).get('error') for channel in failed_channels},
            'retry_count': notification.get('retry_count', 0),
            'moved_at': datetime.utcnow(),
            'reason': 'max_retries_exceeded'
        }
        
        try:
            await self.db.notification_dead_letters.insert_one(dead_letter_doc)
            logger.warning(f"💀 Moved to dead-letter: {notification_id} after {notification.get('retry_count', 0)} retries")
        except Exception as e:
            logger.error(f"Failed to move to dead-letter: {e}")
    
    async def process_retry_queue(self):
        """
        Process pending retries from the retry queue.
        Call this periodically from the background scheduler.
        """
        if self.db is None:
            return 0
        
        now = datetime.utcnow()
        processed = 0
        
        try:
            # Get due retries
            pending_retries = await self.db.notification_retry_queue.find({
                'status': 'pending',
                'next_retry_at': {'$lte': now}
            }).to_list(length=50)
            
            for retry in pending_retries:
                notification = retry.get('notification', {})
                notification['retry_count'] = retry.get('retry_count', 0)
                failed_channels = retry.get('failed_channels', [])
                
                # Retry delivery for failed channels only
                results = {}
                still_failed = []
                
                for channel in failed_channels:
                    try:
                        result = await self._deliver_to_channel(channel, notification)
                        results[channel] = result
                        if result.get('status') == 'failed':
                            still_failed.append(channel)
                    except Exception as e:
                        results[channel] = {'status': 'failed', 'error': str(e)}
                        still_failed.append(channel)
                
                # Update retry status
                if still_failed:
                    # Queue for another retry or move to dead-letter
                    await self._queue_for_retry(notification, still_failed, results)
                
                # Mark this retry as processed
                await self.db.notification_retry_queue.update_one(
                    {'_id': retry['_id']},
                    {'$set': {'status': 'processed', 'processed_at': now}}
                )
                
                processed += 1
                logger.info(f"🔄 Processed retry: {notification.get('notification_id')}, still_failed={len(still_failed)}")
            
            if processed > 0:
                logger.info(f"🔄 Processed {processed} notification retries")
                
        except Exception as e:
            logger.error(f"Error processing retry queue: {e}")
        
        return processed
    
    async def get_dead_letter_count(self) -> int:
        """Get count of notifications in dead-letter queue"""
        if self.db is None:
            return 0
        return await self.db.notification_dead_letters.count_documents({})
    
    async def get_pending_retry_count(self) -> int:
        """Get count of notifications pending retry"""
        if self.db is None:
            return 0
        return await self.db.notification_retry_queue.count_documents({'status': 'pending'})
    
    def _build_email_template(
        self,
        notification: Dict[str, Any]
    ) -> str:
        """Build HTML email template"""
        action = notification.get('action', {})
        action_button = ""
        if action:
            action_button = f"""
            <a href="https://app.druvai.com/action/{notification['notification_id']}" 
               style="background: #6366f1; color: white; padding: 12px 24px; 
                      text-decoration: none; border-radius: 8px; display: inline-block;">
                {action.get('label', 'Open App')}
            </a>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); 
                          color: white; padding: 20px; border-radius: 12px 12px 0 0; }}
                .content {{ background: #f8fafc; padding: 20px; border-radius: 0 0 12px 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">🎓 Sathi</h1>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">Your AI Learning Companion</p>
                </div>
                <div class="content">
                    <h2>{notification['title']}</h2>
                    <p>{notification['message']}</p>
                    <br>
                    {action_button}
                    <br><br>
                    <p style="color: #64748b; font-size: 12px;">
                        You're receiving this because you have notifications enabled on MySckul.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    async def _check_rate_limit(
        self,
        user_id: str,
        priority: str
    ) -> bool:
        """Check if we can send more notifications to this user"""
        if self.db is None:
            return True
        
        limit = self.RATE_LIMITS.get(priority, 5)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        count = await self.db.notifications.count_documents({
            'user_id': user_id,
            'created_at': {'$gte': today_start},
            'priority': priority
        })
        
        return count < limit
    
    def _is_quiet_hours(self, user_id: str) -> bool:
        """Check if current time is in user's quiet hours"""
        # Default quiet hours: 10 PM - 7 AM (IST)
        # TODO: Make this user-configurable in profile settings
        now = datetime.now()
        hour = now.hour
        
        quiet_start = self.DEFAULT_QUIET_HOURS['start']
        quiet_end = self.DEFAULT_QUIET_HOURS['end']
        
        if quiet_start > quiet_end:  # Spans midnight
            return hour >= quiet_start or hour < quiet_end
        else:
            return quiet_start <= hour < quiet_end
    
    def _get_next_active_time(self) -> datetime:
        """Get next time outside quiet hours"""
        now = datetime.now()
        quiet_end = self.DEFAULT_QUIET_HOURS['end']
        
        next_time = now.replace(hour=quiet_end, minute=0, second=0, microsecond=0)
        if next_time <= now:
            next_time += timedelta(days=1)
        
        return next_time
    
    async def _get_user_channels(self, user_id: str) -> List[str]:
        """Get user's notification channel preferences"""
        if self.db is None:
            return [NotificationChannel.IN_APP.value]
        
        preferences = await self.db.user_preferences.find_one({
            'user_id': user_id
        })
        
        if preferences and preferences.get('notification_channels'):
            return preferences['notification_channels']
        
        # Default channels
        return [NotificationChannel.IN_APP.value, NotificationChannel.PUSH.value]
    
    # ===========================================
    # USER-FACING METHODS
    # ===========================================
    
    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get notifications for user's notification center"""
        if self.db is None:
            return []
        
        query = {'user_id': user_id}
        if unread_only:
            query['read'] = False
        
        cursor = self.db.user_notifications.find(query).sort(
            'created_at', -1
        ).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    async def cleanup_old_notifications(
        self,
        user_id: str,
        max_per_user: int = 100
    ) -> int:
        """
        Retention cleanup: Keep only the last N notifications per user.
        Run periodically to prevent notification bloat.
        
        Returns: Number of notifications deleted
        """
        if self.db is None:
            return 0
        
        # Get count of user's notifications
        total_count = await self.db.user_notifications.count_documents({'user_id': user_id})
        
        if total_count <= max_per_user:
            return 0
        
        # Find oldest notifications to delete
        to_delete = total_count - max_per_user
        
        oldest = await self.db.user_notifications.find(
            {'user_id': user_id},
            {'_id': 1}
        ).sort('created_at', 1).limit(to_delete).to_list(to_delete)
        
        if not oldest:
            return 0
        
        ids_to_delete = [doc['_id'] for doc in oldest]
        
        result = await self.db.user_notifications.delete_many({
            '_id': {'$in': ids_to_delete}
        })
        
        logger.info(f"🧹 Cleaned {result.deleted_count} old notifications for user {user_id}")
        return result.deleted_count
    
    async def record_notification_action(
        self,
        user_id: str,
        notification_id: str,
        notification_type: str,
        action: str
    ) -> bool:
        """
        Record user's response to a notification (for backoff policy).
        Actions: 'dismiss', 'snooze', 'click', 'complete'
        """
        if self.db is None:
            return False
        
        await self.db.notification_actions.insert_one({
            'user_id': user_id,
            'notification_id': notification_id,
            'notification_type': notification_type,
            'action': action,
            'timestamp': datetime.utcnow()
        })
        
        return True
    
    async def mark_as_read(
        self,
        user_id: str,
        notification_id: str = None
    ) -> bool:
        """Mark notification(s) as read"""
        if self.db is None:
            return False
        
        query = {'user_id': user_id}
        if notification_id:
            query['notification_id'] = notification_id
        
        result = await self.db.user_notifications.update_many(
            query,
            {'$set': {'read': True, 'read_at': datetime.utcnow()}}
        )
        
        return result.modified_count > 0
    
    async def get_unread_count(self, user_id: str) -> int:
        """Get unread notification count"""
        if self.db is None:
            return 0
        
        return await self.db.user_notifications.count_documents({
            'user_id': user_id,
            'read': False
        })
    
    # ===========================================
    # 🎯 OUTCOME TRACKING (For Mentor Learning)
    # ===========================================
    
    async def track_notification_outcome(
        self,
        user_id: str,
        notification_id: str,
        outcome: str,
        details: Dict[str, Any] = None
    ) -> bool:
        """
        Track the outcome of a notification for learning.
        
        Outcomes:
        - "clicked": User clicked/opened the notification
        - "dismissed": User dismissed without action
        - "studied": User started studying within 30 mins
        - "ignored": No interaction for 2+ hours
        - "snoozed": User snoozed the notification
        
        This data feeds back into the Mentor Companion to improve future decisions.
        """
        if self.db is None:
            return False
        
        try:
            await self.db.notification_outcomes.insert_one({
                'user_id': user_id,
                'notification_id': notification_id,
                'outcome': outcome,
                'details': details or {},
                'created_at': datetime.utcnow()
            })
            
            logger.info(f"📊 Outcome tracked: {notification_id} → {outcome}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track outcome: {e}")
            return False
    
    async def get_notification_effectiveness(self, user_id: str) -> Dict[str, Any]:
        """
        Compute notification effectiveness metrics for a user.
        
        Returns:
        - response_rate: Percentage of notifications that got positive response
        - best_time: Time of day with highest engagement
        - ignored_count: Recent notifications ignored
        """
        if self.db is None:
            return {"response_rate": 0.5, "ignored_count": 0}
        
        try:
            now = datetime.utcnow()
            thirty_days_ago = now - timedelta(days=30)
            
            # Total sent
            total_sent = await self.db.user_notifications.count_documents({
                'user_id': user_id,
                'created_at': {'$gte': thirty_days_ago}
            })
            
            if total_sent == 0:
                return {"response_rate": 0.5, "ignored_count": 0}
            
            # Positive outcomes
            positive_outcomes = await self.db.notification_outcomes.count_documents({
                'user_id': user_id,
                'outcome': {'$in': ['clicked', 'studied']},
                'created_at': {'$gte': thirty_days_ago}
            })
            
            # Ignored count (recent)
            forty_eight_hours_ago = now - timedelta(hours=48)
            ignored_recent = await self.db.notification_outcomes.count_documents({
                'user_id': user_id,
                'outcome': 'ignored',
                'created_at': {'$gte': forty_eight_hours_ago}
            })
            
            return {
                "response_rate": positive_outcomes / total_sent if total_sent > 0 else 0.5,
                "total_sent_30d": total_sent,
                "positive_outcomes_30d": positive_outcomes,
                "ignored_count_48h": ignored_recent
            }
            
        except Exception as e:
            logger.error(f"Failed to compute effectiveness: {e}")
            return {"response_rate": 0.5, "ignored_count": 0}
    
    async def auto_track_ignored_notifications(self, user_id: str):
        """
        Automatically mark old unresponded notifications as 'ignored'.
        Run periodically to keep outcome data accurate.
        """
        if self.db is None:
            return
        
        try:
            two_hours_ago = datetime.utcnow() - timedelta(hours=2)
            
            # Find notifications sent > 2 hours ago with no outcome
            old_notifications = await self.db.user_notifications.find({
                'user_id': user_id,
                'created_at': {'$lt': two_hours_ago},
                'read': False
            }).to_list(length=50)
            
            for notif in old_notifications:
                notification_id = notif.get('notification_id')
                
                # Check if outcome already tracked
                existing = await self.db.notification_outcomes.find_one({
                    'notification_id': notification_id
                })
                
                if not existing:
                    await self.track_notification_outcome(
                        user_id=user_id,
                        notification_id=notification_id,
                        outcome='ignored',
                        details={'auto_tracked': True, 'hours_old': 2}
                    )
            
        except Exception as e:
            logger.error(f"Failed to auto-track ignored: {e}")


# ===========================================
# BACKGROUND TASK: Process Scheduled Notifications
# ===========================================

async def process_scheduled_notifications(db_client):
    """
    Background task to process scheduled notifications
    Run this every minute via task scheduler
    """
    service = NotificationService(db_client)
    
    now = datetime.utcnow()
    
    # Get due notifications
    due_notifications = await db_client.notifications.find({
        'status': 'pending',
        'scheduled_time': {'$lte': now}
    }).to_list(length=100)
    
    for notification in due_notifications:
        try:
            # Re-process the notification
            for channel in notification.get('channels', []):
                await service._deliver_to_channel(channel, notification)
            
            # Update status
            await db_client.notifications.update_one(
                {'notification_id': notification['notification_id']},
                {'$set': {'status': 'sent', 'sent_at': now}}
            )
            
        except Exception as e:
            logger.error(f"Failed to process notification {notification['notification_id']}: {e}")


