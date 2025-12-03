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
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum
import uuid
import asyncio

logger = logging.getLogger(__name__)


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
    
    def __init__(self, db_client=None, websocket_manager=None):
        self.db = db_client
        self.ws_manager = websocket_manager
        self._notification_queue = asyncio.Queue()
    
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
        schedule_time: datetime = None
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
        
        Returns:
            Notification result with status per channel
        """
        notification_id = str(uuid.uuid4())
        
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
        
        # Build notification document
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
            'delivery_status': {channel: 'pending' for channel in channels}
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
        
        # Deliver through each channel
        results = {}
        for channel in channels:
            try:
                result = await self._deliver_to_channel(
                    channel, notification
                )
                results[channel] = result
            except Exception as e:
                logger.error(f"Failed to deliver to {channel}: {e}")
                results[channel] = {'status': 'failed', 'error': str(e)}
        
        # Update delivery status
        if self.db is not None:
            await self.db.notifications.update_one(
                {'notification_id': notification_id},
                {
                    '$set': {
                        'delivery_status': results,
                        'status': 'sent',
                        'sent_at': datetime.utcnow()
                    }
                }
            )
        
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
        
        # Store in notification center
        if self.db is not None:
            await self.db.user_notifications.insert_one({
                'user_id': user_id,
                'notification_id': notification['notification_id'],
                'title': notification['title'],
                'message': notification['message'],
                'type': notification['type'],
                'action': notification.get('action'),
                'data': notification.get('data'),
                'read': False,
                'created_at': datetime.utcnow()
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
        
        # In production, use webpush library
        # For now, log and mark as sent
        logger.info(f"📱 Push notification to {user_id}: {notification['title']}")
        
        # Example structure for actual implementation:
        # from pywebpush import webpush, WebPushException
        # for sub in subscriptions:
        #     try:
        #         webpush(
        #             subscription_info=sub['subscription'],
        #             data=json.dumps({
        #                 'title': notification['title'],
        #                 'body': notification['message'],
        #                 'data': notification.get('data')
        #             }),
        #             vapid_private_key=os.environ.get('VAPID_PRIVATE_KEY'),
        #             vapid_claims={'sub': 'mailto:support@druvai.com'}
        #         )
        #     except WebPushException as e:
        #         logger.error(f"Push failed: {e}")
        
        return {'status': 'sent', 'subscriptions': len(subscriptions)}
    
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
        
        # In production, use email service (SendGrid, SES, etc.)
        logger.info(f"📧 Email to {email}: {notification['title']}")
        
        # Example structure for actual implementation:
        # from services.email_service import send_email
        # await send_email(
        #     to=email,
        #     subject=notification['title'],
        #     html=email_body
        # )
        
        return {'status': 'sent', 'email': email}
    
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
                        You're receiving this because you have notifications enabled on Druv AI.
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


