"""
🔄 Recurring Reminder Tool - Daily/Weekly Study Reminders
=========================================================

Enables TRUE habit-building agentic behavior:
- "remind me daily at 6pm to study physics"
- "weekly revision every Sunday at 10am"
- "remind me every weekday morning to practice math"

This creates ACTUAL recurring reminders with streak tracking!
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import re
import uuid

from .base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)

# IST offset for Indian students
IST_OFFSET = timedelta(hours=5, minutes=30)


class RecurringReminderTool(BaseTool):
    """
    Tool for scheduling recurring reminders - builds study habits.
    
    Supports:
    - Daily reminders
    - Weekly reminders (specific days)
    - Weekday-only reminders
    - Custom intervals
    """
    
    name = "schedule_recurring_reminder"
    description = """Schedule a recurring/repeating reminder. Use this when student wants regular reminders.
    Examples: "remind me daily at 6pm", "weekly revision on Sunday", "every morning remind me to study"
    This creates habit-building reminders with streak tracking!"""
    
    parameters = {
        "message": "What to remind about (string)",
        "time": "Time of day like '6pm', '9:30am', 'morning', 'evening' (string)",
        "frequency": "How often: daily, weekly, weekdays, weekends (string)",
        "days": "For weekly: specific days like 'monday,wednesday,friday' (optional string)",
        "subject": "Subject if study-related (optional string)"
    }
    
    # Time of day defaults (in 24-hour format)
    TIME_DEFAULTS = {
        'morning': 9,
        'afternoon': 14,
        'evening': 18,
        'night': 21
    }
    
    async def execute(
        self,
        message: str,
        time: str,
        frequency: str = "daily",
        days: str = None,
        subject: str = None,
        context: Dict[str, Any] = None,
        **kwargs
    ) -> ToolResult:
        """Schedule a recurring reminder"""
        try:
            user_id = context.get('user_id') if context else None
            if not user_id:
                return ToolResult(
                    success=False,
                    output="Cannot schedule reminder: user not identified",
                    error="Missing user_id in context"
                )
            
            # Parse time
            hour, minute = self._parse_time(time)
            if hour is None:
                return ToolResult(
                    success=False,
                    output=f"I couldn't understand the time '{time}'. Try '6pm', '9:30am', or 'morning'.",
                    error=f"Failed to parse time: {time}"
                )
            
            # Parse frequency and days
            frequency = frequency.lower().strip()
            if frequency not in ['daily', 'weekly', 'weekdays', 'weekends', 'custom']:
                frequency = 'daily'
            
            # Parse specific days for weekly
            day_list = None
            if days:
                day_list = [d.strip().lower() for d in days.split(',')]
            elif frequency == 'weekdays':
                day_list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
            elif frequency == 'weekends':
                day_list = ['saturday', 'sunday']
            
            # Get database
            db = context.get('db') if context else None
            if db is None:
                try:
                    from dependencies import get_database
                    db = await get_database()
                except Exception:
                    return ToolResult(
                        success=False,
                        output="Cannot connect to database.",
                        error="Database not available"
                    )
            
            # Create recurring reminder document
            reminder_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            # Calculate first occurrence
            first_occurrence = self._calculate_next_occurrence(
                hour, minute, frequency, day_list, now
            )
            
            recurring_doc = {
                'recurring_id': reminder_id,
                'user_id': user_id,
                'message': message,
                'subject': subject,
                'hour': hour,
                'minute': minute,
                'frequency': frequency,
                'days': day_list,
                'timezone': 'Asia/Kolkata',  # Default IST
                'is_active': True,
                'streak_count': 0,
                'total_completed': 0,
                'total_missed': 0,
                'created_at': now,
                'updated_at': now,
                'next_occurrence': first_occurrence,
                'last_sent': None,
                'last_completed': None
            }
            
            await db.recurring_reminders.insert_one(recurring_doc)
            
            # Also schedule the first actual reminder
            from services.reminder_scheduler import ReminderScheduler
            scheduler = ReminderScheduler(db)
            
            await scheduler.schedule_reminder(
                user_id=user_id,
                topic=message,
                reminder_time=first_occurrence,
                reminder_type='recurring',
                message=message,
                context={
                    'recurring_id': reminder_id,
                    'frequency': frequency,
                    'subject': subject
                },
                recurring=True,
                recurrence_pattern=frequency
            )
            
            # Format friendly response
            time_str = self._format_time_display(hour, minute)
            freq_str = self._format_frequency(frequency, day_list)
            
            logger.info(f"✅ Recurring reminder created: {reminder_id} - {freq_str} at {time_str}")
            
            return ToolResult(
                success=True,
                output=f"Done! I'll remind you {freq_str} at {time_str} IST for \"{message}\" 🔔\n\nI'll also track your streak! Complete reminders to build your study habit. 🔥",
                data={
                    'recurring_id': reminder_id,
                    'frequency': frequency,
                    'time': f"{hour:02d}:{minute:02d}",
                    'days': day_list,
                    'message': message,
                    'first_occurrence': first_occurrence.isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Recurring reminder error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                output="Sorry, I couldn't set the recurring reminder. Please try again.",
                error=str(e)
            )
    
    def _parse_time(self, time_str: str) -> tuple:
        """Parse time string to hour, minute"""
        time_str = time_str.lower().strip()
        
        # Check for keywords
        if time_str in self.TIME_DEFAULTS:
            return self.TIME_DEFAULTS[time_str], 0
        
        # Parse "6pm", "6:30pm", "18:00"
        match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', time_str)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            ampm = match.group(3)
            
            if ampm == 'pm' and hour != 12:
                hour += 12
            elif ampm == 'am' and hour == 12:
                hour = 0
            
            return hour, minute
        
        return None, None
    
    def _calculate_next_occurrence(
        self,
        hour: int,
        minute: int,
        frequency: str,
        days: List[str],
        now: datetime
    ) -> datetime:
        """Calculate the next occurrence of the reminder"""
        
        # Start with today at the specified time (in UTC, accounting for IST)
        # Since user specifies IST time, we need to convert to UTC
        # IST is UTC+5:30, so UTC = IST - 5:30
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        target = target - IST_OFFSET  # Convert IST to UTC
        
        # If time already passed today, start from tomorrow
        if target <= now:
            target += timedelta(days=1)
        
        if frequency == 'daily':
            return target
        
        elif frequency in ['weekly', 'weekdays', 'weekends'] and days:
            day_map = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2,
                'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
            }
            target_days = [day_map[d] for d in days if d in day_map]
            
            # Find next matching day
            for i in range(7):
                check_date = target + timedelta(days=i)
                if check_date.weekday() in target_days:
                    return check_date
        
        return target
    
    def _format_time_display(self, hour: int, minute: int) -> str:
        """Format time for display"""
        period = 'AM' if hour < 12 else 'PM'
        display_hour = hour if hour <= 12 else hour - 12
        if display_hour == 0:
            display_hour = 12
        
        if minute == 0:
            return f"{display_hour} {period}"
        return f"{display_hour}:{minute:02d} {period}"
    
    def _format_frequency(self, frequency: str, days: List[str]) -> str:
        """Format frequency for display"""
        if frequency == 'daily':
            return 'every day'
        elif frequency == 'weekdays':
            return 'every weekday (Mon-Fri)'
        elif frequency == 'weekends':
            return 'every weekend (Sat-Sun)'
        elif frequency == 'weekly' and days:
            day_names = [d.capitalize() for d in days]
            if len(day_names) == 1:
                return f'every {day_names[0]}'
            return f"every {', '.join(day_names[:-1])} and {day_names[-1]}"
        return frequency
