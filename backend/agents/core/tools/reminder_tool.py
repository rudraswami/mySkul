"""
⏰ Reminder Tool - Schedule Reminders for Students
==================================================

This tool allows agents to schedule actual reminders that will
trigger notifications at the specified time.

TRUE AGENTIC BEHAVIOR:
- When user says "remind me tomorrow at 4pm"
- Agent calls this tool
- Actual reminder is created in database
- Background worker sends notification at 4pm
- User receives push/in-app notification

NOT just saying "I'll remind you" and doing nothing!
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import re
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

from .base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class ReminderTool(BaseTool):
    """
    Tool for scheduling reminders - enables TRUE agentic behavior.
    
    When a student asks to be reminded about something, this tool
    actually creates a reminder that will trigger a notification.
    """
    
    name = "schedule_reminder"
    description = """Schedule a reminder for the student. Use this when the student asks to be reminded about something.
    Examples: "remind me tomorrow", "remind me at 5pm to study", "set a reminder for Monday"
    This creates an ACTUAL reminder that will send a notification at the specified time."""
    
    parameters = {
        "message": "What to remind about (string)",
        "remind_at": "When to remind - natural language like 'tomorrow 4pm', '2 hours', 'Monday 9am' (string)",
        "reminder_type": "Type: study, quiz, revision, custom (default: custom)"
    }
    
    # Time parsing patterns
    TIME_PATTERNS = {
        r'(\d+)\s*(minute|min|m)s?\s*(from now|later)?': 'minutes',
        r'(\d+)\s*(hour|hr|h)s?\s*(from now|later)?': 'hours',
        r'(\d+)\s*(day|d)s?\s*(from now|later)?': 'days',
        r'(\d+)\s*(week|wk|w)s?\s*(from now|later)?': 'weeks',
        r'tomorrow': 'tomorrow',
        r'today': 'today',
        r'tonight': 'tonight',
        r'this evening': 'evening',
        r'this afternoon': 'afternoon',
        r'this morning': 'morning',
    }
    
    async def execute(
        self,
        message: str,
        remind_at: str,
        reminder_type: str = "custom",
        context: Dict[str, Any] = None,
        **kwargs
    ) -> ToolResult:
        """
        Schedule a reminder for the user.
        
        Args:
            message: What to remind about
            remind_at: When to remind (natural language)
            reminder_type: Type of reminder
            context: Must contain user_id
        
        Returns:
            ToolResult with reminder_id if successful
        """
        try:
            # Get user_id from context
            user_id = context.get('user_id') if context else None
            if not user_id:
                return ToolResult(
                    success=False,
                    output="Cannot schedule reminder: user not identified",
                    error="Missing user_id in context"
                )
            
            # Parse the reminder time
            reminder_time = self._parse_time(remind_at)
            if not reminder_time:
                return ToolResult(
                    success=False,
                    output=f"I couldn't understand the time '{remind_at}'. Try something like 'tomorrow 4pm' or '2 hours from now'.",
                    error=f"Failed to parse time: {remind_at}"
                )
            
            # Validate - can't schedule in the past
            if reminder_time <= datetime.utcnow():
                return ToolResult(
                    success=False,
                    output="I can't set a reminder for the past! Please specify a future time.",
                    error="Reminder time is in the past"
                )
            
            # Get database client from context (passed by agentic router)
            db = context.get('db') if context else None
            if db is None:
                # Fallback: try to get from dependencies
                try:
                    from dependencies import get_database
                    db = get_database()
                except Exception:
                    return ToolResult(
                        success=False,
                        output="Cannot connect to database to save reminder.",
                        error="Database not available"
                    )
            
            # Import and use ReminderScheduler
            from services.reminder_scheduler import ReminderScheduler
            scheduler = ReminderScheduler(db)
            
            # Schedule the reminder
            reminder_id = await scheduler.schedule_reminder(
                user_id=user_id,
                topic=message,
                reminder_time=reminder_time,
                reminder_type=reminder_type,
                message=message,
                context={
                    'source': 'ai_chat',
                    'original_request': remind_at
                }
            )
            
            # Format friendly confirmation
            time_str = self._format_time(reminder_time)
            
            logger.info(f"✅ Reminder scheduled: {reminder_id} for user {user_id} at {reminder_time}")
            
            return ToolResult(
                success=True,
                output=f"Done! I've set a reminder for {time_str}. I'll notify you: \"{message}\"",
                data={
                    'reminder_id': reminder_id,
                    'scheduled_time': reminder_time.isoformat(),
                    'message': message,
                    'reminder_type': reminder_type
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Reminder tool error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                output="Sorry, I couldn't set the reminder. Please try again.",
                error=str(e)
            )
    
    def _parse_time(self, time_str: str) -> Optional[datetime]:
        """
        Parse natural language time to datetime.
        
        Supports:
        - "tomorrow", "tomorrow 4pm", "tomorrow morning"
        - "in 2 hours", "2 hours from now"
        - "Monday 9am", "next Monday"
        - "5pm", "17:00"
        - ISO format
        - Typos like "5mis", "5mns", "5min" for minutes
        """
        time_str = time_str.lower().strip()
        now = datetime.utcnow()
        
        # Normalize common typos FIRST
        # Handle "5mis", "5mns", "5mins", "5min" -> "5 minutes"
        time_str = re.sub(r'(\d+)\s*(mis|mns|mins?|m)\b', r'\1 minutes', time_str)
        # Handle "5hrs", "5hr", "5h" -> "5 hours"
        time_str = re.sub(r'(\d+)\s*(hrs?|h)\b', r'\1 hours', time_str)
        # Handle "5secs", "5sec", "5s" -> "5 seconds" (just ignore for reminders)
        time_str = re.sub(r'(\d+)\s*(secs?|s)\b', r'\1 seconds', time_str)
        
        logger.info(f"🕐 Parsing time (normalized): '{time_str}'")
        
        try:
            # Try relative time patterns first
            
            # "in X minutes/hours/days" or just "X minutes/hours"
            match = re.search(r'(?:in\s+)?(\d+)\s*(minutes?|hours?|days?|weeks?|seconds?)', time_str)
            if match:
                amount = int(match.group(1))
                unit = match.group(2)
                logger.info(f"🕐 Matched relative time: {amount} {unit}")
                if 'minute' in unit:
                    return now + timedelta(minutes=amount)
                elif 'hour' in unit:
                    return now + timedelta(hours=amount)
                elif 'day' in unit:
                    return now + timedelta(days=amount)
                elif 'week' in unit:
                    return now + timedelta(weeks=amount)
                elif 'second' in unit:
                    # For seconds, minimum 1 minute for practical purposes
                    return now + timedelta(minutes=1)
            
            # "X minutes/hours from now" (legacy pattern)
            match = re.search(r'(\d+)\s*(minute|min|hour|hr|day|week)s?\s*(from now|later)', time_str)
            if match:
                amount = int(match.group(1))
                unit = match.group(2)
                if 'min' in unit:
                    return now + timedelta(minutes=amount)
                elif 'hour' in unit or 'hr' in unit:
                    return now + timedelta(hours=amount)
                elif 'day' in unit:
                    return now + timedelta(days=amount)
                elif 'week' in unit:
                    return now + timedelta(weeks=amount)
            
            # "tomorrow" variants
            if 'tomorrow' in time_str:
                tomorrow = now + timedelta(days=1)
                
                # Extract time if specified
                time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', time_str)
                if time_match:
                    hour = int(time_match.group(1))
                    minute = int(time_match.group(2)) if time_match.group(2) else 0
                    ampm = time_match.group(3)
                    
                    if ampm == 'pm' and hour != 12:
                        hour += 12
                    elif ampm == 'am' and hour == 12:
                        hour = 0
                    
                    return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # Time of day keywords
                if 'morning' in time_str:
                    return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
                elif 'afternoon' in time_str:
                    return tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
                elif 'evening' in time_str:
                    return tomorrow.replace(hour=18, minute=0, second=0, microsecond=0)
                elif 'night' in time_str:
                    return tomorrow.replace(hour=21, minute=0, second=0, microsecond=0)
                
                # Default to 9am
                return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
            
            # "today" with time
            if 'today' in time_str:
                time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', time_str)
                if time_match:
                    hour = int(time_match.group(1))
                    minute = int(time_match.group(2)) if time_match.group(2) else 0
                    ampm = time_match.group(3)
                    
                    if ampm == 'pm' and hour != 12:
                        hour += 12
                    elif ampm == 'am' and hour == 12:
                        hour = 0
                    
                    return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Just a time like "4pm", "16:00"
            time_match = re.search(r'^(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$', time_str)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2)) if time_match.group(2) else 0
                ampm = time_match.group(3)
                
                if ampm == 'pm' and hour != 12:
                    hour += 12
                elif ampm == 'am' and hour == 12:
                    hour = 0
                
                result = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                # If time already passed today, schedule for tomorrow
                if result <= now:
                    result += timedelta(days=1)
                return result
            
            # Day names (Monday, Tuesday, etc.)
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for i, day in enumerate(days):
                if day in time_str:
                    current_day = now.weekday()
                    target_day = i
                    days_ahead = target_day - current_day
                    if days_ahead <= 0:
                        days_ahead += 7
                    
                    target_date = now + timedelta(days=days_ahead)
                    
                    # Check for time
                    time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', time_str)
                    if time_match:
                        hour = int(time_match.group(1))
                        minute = int(time_match.group(2)) if time_match.group(2) else 0
                        ampm = time_match.group(3)
                        
                        if ampm == 'pm' and hour != 12:
                            hour += 12
                        elif ampm == 'am' and hour == 12:
                            hour = 0
                        
                        return target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    # Default to 9am
                    return target_date.replace(hour=9, minute=0, second=0, microsecond=0)
            
            # Try dateutil parser as fallback
            try:
                parsed = date_parser.parse(time_str, fuzzy=True)
                if parsed:
                    # If no date component, assume today/tomorrow
                    if parsed.date() == datetime(1900, 1, 1).date():
                        parsed = parsed.replace(year=now.year, month=now.month, day=now.day)
                        if parsed <= now:
                            parsed += timedelta(days=1)
                    return parsed
            except:
                pass
            
            return None
            
        except Exception as e:
            logger.error(f"Time parsing error: {e}")
            return None
    
    def _format_time(self, dt: datetime) -> str:
        """Format datetime for friendly display"""
        now = datetime.utcnow()
        
        # Today
        if dt.date() == now.date():
            return f"today at {dt.strftime('%I:%M %p').lstrip('0')}"
        
        # Tomorrow
        if dt.date() == (now + timedelta(days=1)).date():
            return f"tomorrow at {dt.strftime('%I:%M %p').lstrip('0')}"
        
        # This week
        if (dt - now).days < 7:
            return f"{dt.strftime('%A')} at {dt.strftime('%I:%M %p').lstrip('0')}"
        
        # Further out
        return dt.strftime('%B %d at %I:%M %p').lstrip('0')





