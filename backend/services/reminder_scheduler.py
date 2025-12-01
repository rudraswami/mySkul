"""
⏰ REMINDER SCHEDULER - Smart Study Reminder System

This service handles:
- Scheduling reminders (one-time and recurring)
- Managing reminder queue
- Triggering notifications at the right time
- Spaced repetition scheduling (SM-2 algorithm)

Works with:
- ProactiveCompanionAgent
- NotificationService
- Background task runner
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class ReminderType(Enum):
    """Types of reminders"""
    STUDY = "study"                  # General study reminder
    QUIZ = "quiz"                    # Quiz/practice reminder
    REVISION = "revision"            # Revision reminder
    SPACED_REP = "spaced_rep"        # Spaced repetition review
    STREAK = "streak"                # Streak protection
    CUSTOM = "custom"                # User-defined


class ReminderStatus(Enum):
    """Reminder status"""
    PENDING = "pending"
    SENT = "sent"
    SNOOZED = "snoozed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class ReminderScheduler:
    """
    Manages study reminders and spaced repetition scheduling
    """
    
    # Spaced Repetition intervals (SM-2 inspired)
    # Day 1, Day 3, Day 7, Day 14, Day 30, Day 60
    SR_INTERVALS = [1, 3, 7, 14, 30, 60]
    
    # Default reminder times based on student patterns
    DEFAULT_TIMES = {
        'morning': 8,      # 8 AM
        'afternoon': 14,   # 2 PM
        'evening': 18,     # 6 PM
        'night': 21        # 9 PM
    }
    
    def __init__(self, db_client=None):
        self.db = db_client
    
    async def schedule_reminder(
        self,
        user_id: str,
        topic: str,
        reminder_time: datetime,
        reminder_type: str = "study",
        message: str = None,
        context: Dict[str, Any] = None,
        recurring: bool = False,
        recurrence_pattern: str = None  # daily, weekly, etc.
    ) -> str:
        """
        Schedule a new reminder
        
        Returns: reminder_id
        """
        reminder_id = str(uuid.uuid4())
        
        reminder_doc = {
            'reminder_id': reminder_id,
            'user_id': user_id,
            'topic': topic,
            'scheduled_time': reminder_time,
            'reminder_type': reminder_type,
            'custom_message': message,
            'context': context or {},
            'recurring': recurring,
            'recurrence_pattern': recurrence_pattern,
            'status': ReminderStatus.PENDING.value,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'sent_at': None,
            'snooze_count': 0
        }
        
        if self.db is not None:
            try:
                await self.db.reminders.insert_one(reminder_doc)
                logger.info(f"📅 Reminder scheduled: {reminder_id} for {reminder_time}")
            except Exception as e:
                logger.error(f"Failed to save reminder: {e}")
        
        return reminder_id
    
    async def schedule_spaced_repetition(
        self,
        user_id: str,
        topic: str,
        subject: str,
        initial_quality: int = 3  # 0-5, how well they learned it
    ) -> List[str]:
        """
        Schedule spaced repetition reviews for a topic
        
        Uses SM-2 inspired intervals:
        - Quality 3 (okay): 1, 3, 7, 14 days
        - Quality 4 (good): 1, 7, 14, 30 days
        - Quality 5 (perfect): 3, 14, 30, 60 days
        
        Returns: List of reminder_ids
        """
        reminder_ids = []
        now = datetime.utcnow()
        
        # Adjust intervals based on initial quality
        if initial_quality >= 5:
            intervals = [3, 14, 30, 60]
        elif initial_quality >= 4:
            intervals = [1, 7, 14, 30]
        else:
            intervals = [1, 3, 7, 14]
        
        for i, days in enumerate(intervals):
            review_time = now + timedelta(days=days)
            # Set to a reasonable time (evening by default)
            review_time = review_time.replace(hour=18, minute=0, second=0, microsecond=0)
            
            reminder_id = await self.schedule_reminder(
                user_id=user_id,
                topic=topic,
                reminder_time=review_time,
                reminder_type="spaced_rep",
                message=f"Time to review {topic}! This is review #{i+1} of {len(intervals)}.",
                context={
                    'subject': subject,
                    'review_number': i + 1,
                    'total_reviews': len(intervals),
                    'days_since_learned': days
                }
            )
            reminder_ids.append(reminder_id)
        
        logger.info(f"📚 Spaced repetition scheduled: {len(reminder_ids)} reviews for '{topic}'")
        return reminder_ids
    
    async def get_due_reminders(
        self,
        lookahead_minutes: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get reminders that are due now or within lookahead window
        Used by background task to send notifications
        """
        if self.db is None:
            return []
        
        now = datetime.utcnow()
        window_end = now + timedelta(minutes=lookahead_minutes)
        
        try:
            cursor = self.db.reminders.find({
                'status': ReminderStatus.PENDING.value,
                'scheduled_time': {
                    '$gte': now - timedelta(minutes=5),  # Grace period
                    '$lte': window_end
                }
            })
            
            reminders = await cursor.to_list(length=100)
            return reminders
            
        except Exception as e:
            logger.error(f"Failed to get due reminders: {e}")
            return []
    
    async def get_user_reminders(
        self,
        user_id: str,
        status: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get reminders for a user"""
        if self.db is None:
            return []
        
        query = {'user_id': user_id}
        if status:
            query['status'] = status
        
        try:
            cursor = self.db.reminders.find(query).sort(
                'scheduled_time', 1
            ).limit(limit)
            
            return await cursor.to_list(length=limit)
            
        except Exception as e:
            logger.error(f"Failed to get user reminders: {e}")
            return []
    
    async def mark_reminder_sent(self, reminder_id: str) -> bool:
        """Mark reminder as sent"""
        if self.db is None:
            return False
        
        try:
            result = await self.db.reminders.update_one(
                {'reminder_id': reminder_id},
                {
                    '$set': {
                        'status': ReminderStatus.SENT.value,
                        'sent_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to mark reminder sent: {e}")
            return False
    
    async def snooze_reminder(
        self,
        reminder_id: str,
        snooze_minutes: int = 30
    ) -> bool:
        """Snooze a reminder for later"""
        if self.db is None:
            return False
        
        new_time = datetime.utcnow() + timedelta(minutes=snooze_minutes)
        
        try:
            result = await self.db.reminders.update_one(
                {'reminder_id': reminder_id},
                {
                    '$set': {
                        'scheduled_time': new_time,
                        'status': ReminderStatus.PENDING.value,
                        'updated_at': datetime.utcnow()
                    },
                    '$inc': {'snooze_count': 1}
                }
            )
            
            logger.info(f"⏰ Reminder {reminder_id} snoozed to {new_time}")
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to snooze reminder: {e}")
            return False
    
    async def cancel_reminder(self, reminder_id: str) -> bool:
        """Cancel a reminder"""
        if self.db is None:
            return False
        
        try:
            result = await self.db.reminders.update_one(
                {'reminder_id': reminder_id},
                {
                    '$set': {
                        'status': ReminderStatus.CANCELLED.value,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to cancel reminder: {e}")
            return False
    
    async def mark_completed(self, reminder_id: str) -> bool:
        """Mark reminder as completed (user engaged)"""
        if self.db is None:
            return False
        
        try:
            result = await self.db.reminders.update_one(
                {'reminder_id': reminder_id},
                {
                    '$set': {
                        'status': ReminderStatus.COMPLETED.value,
                        'completed_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to mark reminder completed: {e}")
            return False
    
    async def handle_recurring(self, reminder: Dict[str, Any]) -> Optional[str]:
        """
        Handle recurring reminders - create next occurrence
        """
        if not reminder.get('recurring'):
            return None
        
        pattern = reminder.get('recurrence_pattern', 'daily')
        current_time = reminder.get('scheduled_time')
        
        # Calculate next occurrence
        if pattern == 'daily':
            next_time = current_time + timedelta(days=1)
        elif pattern == 'weekly':
            next_time = current_time + timedelta(weeks=1)
        elif pattern == 'weekdays':
            next_time = current_time + timedelta(days=1)
            while next_time.weekday() >= 5:  # Skip weekends
                next_time += timedelta(days=1)
        else:
            return None
        
        # Create next reminder
        return await self.schedule_reminder(
            user_id=reminder['user_id'],
            topic=reminder['topic'],
            reminder_time=next_time,
            reminder_type=reminder['reminder_type'],
            message=reminder.get('custom_message'),
            context=reminder.get('context'),
            recurring=True,
            recurrence_pattern=pattern
        )


# ===========================================
# SPACED REPETITION ENGINE (SM-2)
# ===========================================

class SpacedRepetitionEngine:
    """
    Implements SM-2 algorithm for optimal review scheduling
    
    The algorithm:
    - Tracks ease factor (how easy the item is)
    - Adjusts intervals based on recall quality
    - Schedules reviews at optimal forgetting curve points
    """
    
    # Initial ease factor
    INITIAL_EASE = 2.5
    
    # Minimum ease factor
    MIN_EASE = 1.3
    
    def __init__(self, db_client=None):
        self.db = db_client
    
    async def record_review(
        self,
        user_id: str,
        topic: str,
        quality: int  # 0-5: 0=complete failure, 5=perfect
    ) -> Dict[str, Any]:
        """
        Record a review and calculate next review date
        
        Quality scale:
        0 - Complete blackout
        1 - Incorrect, but recognized after seeing answer
        2 - Incorrect, but easy to recall after seeing answer
        3 - Correct with significant difficulty
        4 - Correct with hesitation
        5 - Perfect recall
        """
        if self.db is None:
            return self._calculate_next_review(quality, 0, self.INITIAL_EASE, 1)
        
        # Get current item data
        item = await self.db.sr_items.find_one({
            'user_id': user_id,
            'topic': topic
        })
        
        if item:
            repetitions = item.get('repetitions', 0)
            ease_factor = item.get('ease_factor', self.INITIAL_EASE)
            interval = item.get('interval', 1)
        else:
            repetitions = 0
            ease_factor = self.INITIAL_EASE
            interval = 1
        
        # Calculate next review
        result = self._calculate_next_review(quality, repetitions, ease_factor, interval)
        
        # Save updated data
        await self.db.sr_items.update_one(
            {'user_id': user_id, 'topic': topic},
            {
                '$set': {
                    'ease_factor': result['new_ease_factor'],
                    'interval': result['new_interval'],
                    'repetitions': result['new_repetitions'],
                    'next_review': result['next_review_date'],
                    'last_review': datetime.utcnow(),
                    'last_quality': quality,
                    'updated_at': datetime.utcnow()
                },
                '$setOnInsert': {
                    'user_id': user_id,
                    'topic': topic,
                    'created_at': datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return result
    
    def _calculate_next_review(
        self,
        quality: int,
        repetitions: int,
        ease_factor: float,
        interval: int
    ) -> Dict[str, Any]:
        """
        SM-2 algorithm implementation
        """
        # If quality < 3, reset to beginning
        if quality < 3:
            new_repetitions = 0
            new_interval = 1
        else:
            # Successful recall
            new_repetitions = repetitions + 1
            
            if new_repetitions == 1:
                new_interval = 1
            elif new_repetitions == 2:
                new_interval = 6
            else:
                new_interval = round(interval * ease_factor)
        
        # Update ease factor
        new_ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ease_factor = max(self.MIN_EASE, new_ease_factor)
        
        # Calculate next review date
        next_review_date = datetime.utcnow() + timedelta(days=new_interval)
        
        return {
            'new_interval': new_interval,
            'new_repetitions': new_repetitions,
            'new_ease_factor': round(new_ease_factor, 2),
            'next_review_date': next_review_date,
            'days_until_review': new_interval
        }
    
    async def get_due_reviews(
        self,
        user_id: str,
        subject: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get topics due for review"""
        if self.db is None:
            return []
        
        query = {
            'user_id': user_id,
            'next_review': {'$lte': datetime.utcnow()}
        }
        
        if subject:
            query['subject'] = subject
        
        try:
            cursor = self.db.sr_items.find(query).sort(
                'next_review', 1
            ).limit(limit)
            
            return await cursor.to_list(length=limit)
            
        except Exception as e:
            logger.error(f"Failed to get due reviews: {e}")
            return []


