"""
🔔 Notification Tool - Send Notifications to Students
=====================================================

This tool allows agents to send immediate notifications
to students through various channels.

TRUE AGENTIC BEHAVIOR:
- When agent needs to alert the student
- Sends actual push/in-app/email notification
- User receives it on their device

Use Cases:
- Urgent updates
- Achievement unlocked
- Study streak about to break
- Important announcements
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from .base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class NotificationTool(BaseTool):
    """
    Tool for sending notifications - enables proactive agent behavior.
    
    Agents can use this to alert students about important things.
    """
    
    name = "send_notification"
    description = """Send a notification to the student. Use this to alert them about something important.
    This sends an ACTUAL notification to their device/browser.
    Use sparingly - only for genuinely important alerts."""
    
    parameters = {
        "title": "Notification title (short, attention-grabbing)",
        "message": "Notification body (the actual message)",
        "priority": "low, medium, high, or urgent (default: medium)",
        "notification_type": "Type: achievement, reminder, alert, tip, streak (default: alert)"
    }
    
    async def execute(
        self,
        title: str,
        message: str,
        priority: str = "medium",
        notification_type: str = "alert",
        context: Dict[str, Any] = None,
        **kwargs
    ) -> ToolResult:
        """
        Send a notification to the user.
        
        Args:
            title: Notification title
            message: Notification body
            priority: low/medium/high/urgent
            notification_type: Type of notification
            context: Must contain user_id
        
        Returns:
            ToolResult with notification status
        """
        try:
            # Get user_id from context
            user_id = context.get('user_id') if context else None
            if not user_id:
                return ToolResult(
                    success=False,
                    output="Cannot send notification: user not identified",
                    error="Missing user_id in context"
                )
            
            # Validate priority
            valid_priorities = ['low', 'medium', 'high', 'urgent']
            if priority not in valid_priorities:
                priority = 'medium'
            
            # Get database client
            from db.mongo import get_database
            db = await get_database()
            
            # Import and use NotificationService
            from services.notification_service import NotificationService
            notification_service = NotificationService(db)
            
            # Send the notification
            result = await notification_service.send_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                data={
                    'source': 'ai_agent',
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            if result.get('status') in ['sent', 'scheduled', 'stored']:
                logger.info(f"✅ Notification sent to {user_id}: {title}")
                return ToolResult(
                    success=True,
                    output=f"Notification sent: {title}",
                    data=result
                )
            else:
                return ToolResult(
                    success=False,
                    output=f"Notification may not have been delivered: {result.get('status')}",
                    data=result
                )
            
        except Exception as e:
            logger.error(f"❌ Notification tool error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                output="Sorry, I couldn't send the notification.",
                error=str(e)
            )


class StudySummaryTool(BaseTool):
    """
    Tool for sending study summaries to students.
    
    Generates and sends a summary of recent study activity.
    """
    
    name = "send_study_summary"
    description = """Send a study summary to the student via email or notification.
    Use when student asks for a summary of what they've learned or their progress."""
    
    parameters = {
        "period": "Time period: today, week, month (default: week)",
        "channel": "How to send: notification, email (default: notification)"
    }
    
    async def execute(
        self,
        period: str = "week",
        channel: str = "notification",
        context: Dict[str, Any] = None,
        **kwargs
    ) -> ToolResult:
        """Generate and send study summary"""
        try:
            user_id = context.get('user_id') if context else None
            if not user_id:
                return ToolResult(
                    success=False,
                    output="Cannot send summary: user not identified",
                    error="Missing user_id"
                )
            
            # Get database
            from db.mongo import get_database
            db = await get_database()
            
            # Get study stats
            # This would fetch from analytics/gamification
            stats = await self._get_study_stats(db, user_id, period)
            
            # Format summary message
            summary = self._format_summary(stats, period)
            
            # Send via notification
            from services.notification_service import NotificationService
            notification_service = NotificationService(db)
            
            result = await notification_service.send_notification(
                user_id=user_id,
                title=f"📊 Your {period.capitalize()} Study Summary",
                message=summary,
                notification_type="summary",
                priority="low",
                channels=['in_app', 'email'] if channel == 'email' else ['in_app']
            )
            
            return ToolResult(
                success=True,
                output=f"Study summary sent! {summary}",
                data={'summary': summary, 'stats': stats}
            )
            
        except Exception as e:
            logger.error(f"Study summary error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                output="Couldn't generate study summary.",
                error=str(e)
            )
    
    async def _get_study_stats(self, db, user_id: str, period: str) -> Dict:
        """Fetch study statistics"""
        from datetime import timedelta
        
        now = datetime.utcnow()
        if period == 'today':
            start = now.replace(hour=0, minute=0, second=0)
        elif period == 'week':
            start = now - timedelta(days=7)
        else:
            start = now - timedelta(days=30)
        
        # Count sessions
        sessions = await db.chat_sessions.count_documents({
            'user_id': user_id,
            'created_at': {'$gte': start}
        })
        
        # Count messages
        messages = await db.chat_messages.count_documents({
            'user_id': user_id,
            'timestamp': {'$gte': start}
        })
        
        # Get XP if gamification exists
        xp = 0
        try:
            user_stats = await db.user_gamification.find_one({'user_id': user_id})
            if user_stats:
                xp = user_stats.get('xp', 0)
        except:
            pass
        
        return {
            'sessions': sessions,
            'questions_asked': messages // 2,  # Rough estimate
            'xp_earned': xp,
            'period': period
        }
    
    def _format_summary(self, stats: Dict, period: str) -> str:
        """Format stats into readable summary"""
        return (
            f"This {period}, you had {stats['sessions']} study sessions and "
            f"asked {stats['questions_asked']} questions. "
            f"Keep up the great work! 💪"
        )





