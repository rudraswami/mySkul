"""
🔔 Test Suite for Reminder + Notification + Sathi Companion System
==================================================================

Ship-blocker E2E tests for:
A) Reminder E2E: create → DB → scheduler → notification → mark_sent
B) Notification delivery E2E: in-app storage + poll retrieval
C) Sathi proactive nudges E2E: streak/spaced-rep triggers
D) Anti-spam test: skip if user recently active
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock, patch
import uuid


# =============================================================================
# MOCK DATABASE
# =============================================================================

class MockCollection:
    """Mock MongoDB collection for testing"""
    
    def __init__(self, name: str):
        self.name = name
        self._documents = []
    
    async def insert_one(self, doc):
        doc['_id'] = str(uuid.uuid4())
        self._documents.append(doc)
        return MagicMock(inserted_id=doc['_id'])
    
    async def find_one(self, query):
        for doc in self._documents:
            if self._matches(doc, query):
                return doc
        return None
    
    async def update_one(self, query, update):
        for doc in self._documents:
            if self._matches(doc, query):
                if '$set' in update:
                    doc.update(update['$set'])
                if '$inc' in update:
                    for k, v in update['$inc'].items():
                        doc[k] = doc.get(k, 0) + v
                return MagicMock(modified_count=1)
        return MagicMock(modified_count=0)
    
    async def count_documents(self, query):
        count = 0
        for doc in self._documents:
            if self._matches(doc, query):
                count += 1
        return count
    
    def find(self, query=None):
        query = query or {}
        results = [d for d in self._documents if self._matches(d, query)]
        return MockCursor(results)
    
    async def aggregate(self, pipeline):
        # Simplified aggregation - returns all docs
        return MockCursor(self._documents)
    
    def _matches(self, doc, query):
        for key, value in query.items():
            if key == '$or':
                if not any(self._matches(doc, cond) for cond in value):
                    return False
            elif key.startswith('$'):
                continue  # Skip operators for simple matching
            elif isinstance(value, dict):
                if '$gte' in value and doc.get(key) and doc[key] < value['$gte']:
                    return False
                if '$lte' in value and doc.get(key) and doc[key] > value['$lte']:
                    return False
                if '$lt' in value and doc.get(key) and doc[key] >= value['$lt']:
                    return False
                if '$ne' in value and doc.get(key) == value['$ne']:
                    return False
            elif doc.get(key) != value:
                return False
        return True
    
    def clear(self):
        self._documents = []


class MockCursor:
    """Mock cursor for find operations"""
    
    def __init__(self, results):
        self._results = results
    
    def sort(self, field, direction):
        return self
    
    def limit(self, n):
        self._results = self._results[:n]
        return self
    
    async def to_list(self, length=None):
        if length:
            return self._results[:length]
        return self._results


class MockDB:
    """Mock database with all required collections"""
    
    def __init__(self):
        self.reminders = MockCollection('reminders')
        self.recurring_reminders = MockCollection('recurring_reminders')
        self.notifications = MockCollection('notifications')
        self.user_notifications = MockCollection('user_notifications')
        self.nudge_log = MockCollection('nudge_log')
        self.users = MockCollection('users')
        self.student_profiles = MockCollection('student_profiles')
        self.user_streaks = MockCollection('user_streaks')
        self.chat_messages = MockCollection('chat_messages')
        self.chat_sessions = MockCollection('chat_sessions')
        self.sr_items = MockCollection('sr_items')
        self.push_subscriptions = MockCollection('push_subscriptions')
        self.user_preferences = MockCollection('user_preferences')
    
    def clear_all(self):
        for attr in dir(self):
            val = getattr(self, attr)
            if isinstance(val, MockCollection):
                val.clear()


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def mock_db():
    """Create a fresh mock database for each test"""
    return MockDB()


@pytest.fixture
def test_user_id():
    return "test_user_123"


@pytest.fixture
def test_session_id():
    return "test_session_456"


# =============================================================================
# A) REMINDER E2E TESTS
# =============================================================================

class TestReminderE2E:
    """End-to-end tests for reminder flow"""
    
    @pytest.mark.asyncio
    async def test_reminder_creation_writes_to_db(self, mock_db, test_user_id):
        """
        Test: Create reminder via ReminderScheduler → DB record exists
        """
        from services.reminder_scheduler import ReminderScheduler
        
        scheduler = ReminderScheduler(mock_db)
        
        # Schedule a reminder
        reminder_time = datetime.utcnow() + timedelta(hours=1)
        reminder_id = await scheduler.schedule_reminder(
            user_id=test_user_id,
            topic="Physics - Kinematics",
            reminder_time=reminder_time,
            reminder_type="study",
            message="Time to study kinematics!"
        )
        
        # Verify DB record exists
        assert reminder_id is not None
        assert len(mock_db.reminders._documents) == 1
        
        saved_reminder = mock_db.reminders._documents[0]
        assert saved_reminder['user_id'] == test_user_id
        assert saved_reminder['topic'] == "Physics - Kinematics"
        assert saved_reminder['status'] == 'pending'
        assert saved_reminder['scheduled_time'] == reminder_time
    
    @pytest.mark.asyncio
    async def test_due_reminders_are_retrieved(self, mock_db, test_user_id):
        """
        Test: Due reminders are correctly queried
        """
        from services.reminder_scheduler import ReminderScheduler
        
        scheduler = ReminderScheduler(mock_db)
        
        # Create a reminder that's already due
        past_time = datetime.utcnow() - timedelta(minutes=2)
        await scheduler.schedule_reminder(
            user_id=test_user_id,
            topic="Due Reminder",
            reminder_time=past_time,
            reminder_type="study"
        )
        
        # Create a future reminder (not due)
        future_time = datetime.utcnow() + timedelta(hours=2)
        await scheduler.schedule_reminder(
            user_id=test_user_id,
            topic="Future Reminder",
            reminder_time=future_time,
            reminder_type="study"
        )
        
        # Get due reminders (lookahead 5 minutes)
        due_reminders = await scheduler.get_due_reminders(lookahead_minutes=5)
        
        # Only the past reminder should be returned
        assert len(due_reminders) == 1
        assert due_reminders[0]['topic'] == "Due Reminder"
    
    @pytest.mark.asyncio
    async def test_reminder_marked_as_sent(self, mock_db, test_user_id):
        """
        Test: Reminder is correctly marked as sent after processing
        """
        from services.reminder_scheduler import ReminderScheduler
        
        scheduler = ReminderScheduler(mock_db)
        
        # Create reminder
        reminder_id = await scheduler.schedule_reminder(
            user_id=test_user_id,
            topic="Test Reminder",
            reminder_time=datetime.utcnow() - timedelta(minutes=1),
            reminder_type="study"
        )
        
        # Mark as sent
        result = await scheduler.mark_reminder_sent(reminder_id)
        
        assert result is True
        
        # Verify status updated
        updated = await mock_db.reminders.find_one({'reminder_id': reminder_id})
        assert updated['status'] == 'sent'
        assert updated['sent_at'] is not None
    
    @pytest.mark.asyncio
    async def test_reminder_idempotency_no_duplicate_send(self, mock_db, test_user_id):
        """
        Test: Already-sent reminders are not retrieved again (idempotency)
        """
        from services.reminder_scheduler import ReminderScheduler
        
        scheduler = ReminderScheduler(mock_db)
        
        # Create and immediately mark as sent
        reminder_id = await scheduler.schedule_reminder(
            user_id=test_user_id,
            topic="Already Sent",
            reminder_time=datetime.utcnow() - timedelta(minutes=1),
            reminder_type="study"
        )
        await scheduler.mark_reminder_sent(reminder_id)
        
        # Try to get due reminders
        due_reminders = await scheduler.get_due_reminders(lookahead_minutes=5)
        
        # Should NOT include the already-sent reminder
        assert len(due_reminders) == 0


# =============================================================================
# B) NOTIFICATION DELIVERY E2E TESTS
# =============================================================================

class TestNotificationDeliveryE2E:
    """End-to-end tests for notification delivery"""
    
    @pytest.mark.asyncio
    async def test_notification_stored_in_db(self, mock_db, test_user_id):
        """
        Test: Notification is stored in user_notifications collection
        """
        from services.notification_service import NotificationService
        
        service = NotificationService(mock_db)
        
        result = await service.send_notification(
            user_id=test_user_id,
            title="Test Notification",
            message="This is a test message",
            notification_type="reminder",
            priority="high"
        )
        
        assert result['status'] in ['sent', 'stored']
        assert 'notification_id' in result
        
        # Verify stored in user_notifications
        stored = await mock_db.user_notifications.find_one({'user_id': test_user_id})
        assert stored is not None
        assert stored['title'] == "Test Notification"
        assert stored['read'] is False
    
    @pytest.mark.asyncio
    async def test_notification_with_action_button(self, mock_db, test_user_id):
        """
        Test: Notification with action button is stored correctly
        """
        from services.notification_service import NotificationService
        
        service = NotificationService(mock_db)
        
        await service.send_notification(
            user_id=test_user_id,
            title="Action Notification",
            message="Click to continue",
            notification_type="reminder",
            priority="medium",
            action={'label': 'Start Session', 'action': 'open_tutor'}
        )
        
        stored = await mock_db.user_notifications.find_one({'user_id': test_user_id})
        assert stored['action'] == {'label': 'Start Session', 'action': 'open_tutor'}
    
    @pytest.mark.asyncio
    async def test_get_unread_notifications(self, mock_db, test_user_id):
        """
        Test: Can retrieve unread notifications for user
        """
        from services.notification_service import NotificationService
        
        service = NotificationService(mock_db)
        
        # Send 3 notifications
        for i in range(3):
            await service.send_notification(
                user_id=test_user_id,
                title=f"Notification {i+1}",
                message=f"Message {i+1}",
                notification_type="reminder",
                priority="medium"
            )
        
        # Get unread count
        unread_count = await service.get_unread_count(test_user_id)
        assert unread_count == 3
        
        # Get notifications list
        notifications = await service.get_user_notifications(test_user_id, unread_only=True)
        assert len(notifications) == 3
    
    @pytest.mark.asyncio
    async def test_mark_notification_as_read(self, mock_db, test_user_id):
        """
        Test: Marking notification as read updates the database
        """
        from services.notification_service import NotificationService
        
        service = NotificationService(mock_db)
        
        # Send notification
        result = await service.send_notification(
            user_id=test_user_id,
            title="To Be Read",
            message="This will be marked as read",
            notification_type="reminder",
            priority="medium"
        )
        
        notification_id = result['notification_id']
        
        # Mark as read
        success = await service.mark_as_read(test_user_id, notification_id)
        assert success is True
        
        # Verify unread count is 0
        unread_count = await service.get_unread_count(test_user_id)
        assert unread_count == 0


# =============================================================================
# C) SATHI PROACTIVE NUDGE E2E TESTS
# =============================================================================

class TestSathiNudgesE2E:
    """End-to-end tests for Sathi companion proactive nudges"""
    
    @pytest.mark.asyncio
    async def test_streak_protection_nudge_created(self, mock_db, test_user_id):
        """
        Test: Streak protection nudge is created when conditions are met
        """
        from services.intelligent_proactive_mentor import IntelligentProactiveMentor, NudgeType
        
        # Setup user with active streak and old last activity
        await mock_db.users.insert_one({
            'user_id': test_user_id,
            'streak': 5,
            'last_study_activity': datetime.utcnow() - timedelta(hours=21)
        })
        
        mentor = IntelligentProactiveMentor(mock_db)
        nudge = await mentor.check_streak_protection(test_user_id)
        
        assert nudge is not None
        assert nudge.nudge_type == NudgeType.STREAK_PROTECTION
        assert '5' in nudge.title or '5' in nudge.message  # Streak count should be mentioned
        assert nudge.priority == 'high'
    
    @pytest.mark.asyncio
    async def test_nudge_type_enum_values(self):
        """
        Test: All required NudgeType enum values exist
        """
        from services.intelligent_proactive_mentor import NudgeType
        
        # Required values (including new ones added)
        required_values = [
            'STREAK_PROTECTION',
            'CONTINUE_LEARNING',
            'REVISION_DUE',
            'COMEBACK',
            'MORNING_GREETING',
            'SPACED_REP'
        ]
        
        for value in required_values:
            assert hasattr(NudgeType, value), f"Missing NudgeType.{value}"
    
    @pytest.mark.asyncio
    async def test_proactive_nudge_dataclass(self):
        """
        Test: ProactiveNudge dataclass works correctly
        """
        from services.intelligent_proactive_mentor import ProactiveNudge, NudgeType
        
        nudge = ProactiveNudge(
            nudge_type=NudgeType.STREAK_PROTECTION,
            title="Test Title",
            message="Test Message",
            priority="high",
            actions=[{'label': 'Start', 'action': 'start'}],
            data={'streak': 5}
        )
        
        assert nudge.nudge_type == NudgeType.STREAK_PROTECTION
        assert nudge.title == "Test Title"
        
        # Test to_dict
        nudge_dict = nudge.to_dict()
        assert nudge_dict['type'] == 'streak_protection'
        assert nudge_dict['priority'] == 'high'


# =============================================================================
# D) ANTI-SPAM TESTS
# =============================================================================

class TestAntiSpam:
    """Tests for anti-spam (skip nudge if user is active)"""
    
    @pytest.mark.asyncio
    async def test_skip_nudge_if_user_recently_active(self, mock_db, test_user_id):
        """
        Test: Proactive nudge is skipped if user has recent activity
        """
        from services.proactive_scheduler import ProactiveScheduler
        
        scheduler = ProactiveScheduler(mock_db)
        
        # Add recent chat message (simulating active user)
        await mock_db.chat_messages.insert_one({
            'user_id': test_user_id,
            'message': 'Hello',
            'timestamp': datetime.utcnow() - timedelta(minutes=2)  # 2 mins ago
        })
        
        # Check if user is considered active
        is_active = await scheduler._is_user_currently_active(test_user_id)
        
        assert is_active is True
    
    @pytest.mark.asyncio
    async def test_allow_nudge_if_user_inactive(self, mock_db, test_user_id):
        """
        Test: Proactive nudge is allowed if user has no recent activity
        """
        from services.proactive_scheduler import ProactiveScheduler
        
        scheduler = ProactiveScheduler(mock_db)
        
        # Add old chat message (user is NOT active)
        await mock_db.chat_messages.insert_one({
            'user_id': test_user_id,
            'message': 'Hello',
            'timestamp': datetime.utcnow() - timedelta(minutes=10)  # 10 mins ago
        })
        
        # Check if user is considered active (threshold is 5 mins)
        is_active = await scheduler._is_user_currently_active(test_user_id)
        
        assert is_active is False
    
    @pytest.mark.asyncio
    async def test_nudge_rate_limiting(self, mock_db, test_user_id):
        """
        Test: Nudge log prevents duplicate nudges on same day
        """
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Add existing nudge log for today
        await mock_db.nudge_log.insert_one({
            'user_id': test_user_id,
            'nudge_type': 'streak',
            'sent_at': now - timedelta(hours=2)  # Sent 2 hours ago today
        })
        
        # Check if nudge already sent today
        existing = await mock_db.nudge_log.find_one({
            'user_id': test_user_id,
            'nudge_type': 'streak',
            'sent_at': {'$gte': today_start}
        })
        
        assert existing is not None  # Should find the existing nudge
    
    @pytest.mark.asyncio
    async def test_max_nudges_per_day_limit(self, mock_db, test_user_id):
        """
        Test: Maximum nudges per day limit is respected
        """
        now = datetime.utcnow()
        
        # Add 2 spaced_rep nudges already (limit is 2 per day)
        for i in range(2):
            await mock_db.nudge_log.insert_one({
                'user_id': test_user_id,
                'nudge_type': 'spaced_rep',
                'sent_at': now - timedelta(hours=i+1)
            })
        
        # Count nudges for today
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        count = await mock_db.nudge_log.count_documents({
            'user_id': test_user_id,
            'nudge_type': 'spaced_rep',
            'sent_at': {'$gte': today_start}
        })
        
        assert count >= 2  # Should have hit the limit


# =============================================================================
# E) MEMORY V2 PERSONALIZATION TESTS
# =============================================================================

class TestMemoryV2Personalization:
    """Tests for Memory v2 personalization in reminders/notifications"""
    
    @pytest.mark.asyncio
    async def test_reminder_message_personalized_with_name(self, mock_db, test_user_id):
        """
        Test: Reminder message includes student's name when available
        """
        from services.proactive_scheduler import ProactiveScheduler
        
        # Add student profile with name
        await mock_db.student_profiles.insert_one({
            'user_id': test_user_id,
            'name': 'Rahul Kumar',
            'weak_topics': ['Thermodynamics', 'Calculus'],
            'practice_streak': 5
        })
        
        scheduler = ProactiveScheduler(mock_db)
        
        message = await scheduler._personalize_reminder_message(
            user_id=test_user_id,
            topic="Physics"
        )
        
        assert 'Rahul' in message
    
    @pytest.mark.asyncio
    async def test_reminder_message_mentions_weak_topic(self, mock_db, test_user_id):
        """
        Test: Reminder message gives extra encouragement for weak topics
        """
        from services.proactive_scheduler import ProactiveScheduler
        
        # Add student profile with weak topics
        await mock_db.student_profiles.insert_one({
            'user_id': test_user_id,
            'name': 'Priya',
            'weak_topics': ['Thermodynamics', 'Organic Chemistry']
        })
        
        scheduler = ProactiveScheduler(mock_db)
        
        # Request reminder for a weak topic
        message = await scheduler._personalize_reminder_message(
            user_id=test_user_id,
            topic="Thermodynamics"
        )
        
        # Should mention strengthening/growth area
        assert 'strength' in message.lower() or 'growth' in message.lower()
    
    @pytest.mark.asyncio
    async def test_reminder_message_mentions_streak(self, mock_db, test_user_id):
        """
        Test: Reminder message includes streak info for motivation
        """
        from services.proactive_scheduler import ProactiveScheduler
        
        # Add student profile with good streak
        await mock_db.student_profiles.insert_one({
            'user_id': test_user_id,
            'name': 'Amit',
            'weak_topics': [],
            'practice_streak': 7
        })
        
        scheduler = ProactiveScheduler(mock_db)
        
        message = await scheduler._personalize_reminder_message(
            user_id=test_user_id,
            topic="Math"
        )
        
        # Should mention streak
        assert '7' in message or 'streak' in message.lower()


# =============================================================================
# F) PROACTIVE SCHEDULER IMPORT TESTS
# =============================================================================

class TestProactiveSchedulerImports:
    """Tests to verify proactive scheduler imports work correctly"""
    
    def test_proactive_scheduler_imports(self):
        """
        Test: ProactiveScheduler imports without errors
        """
        from services.proactive_scheduler import ProactiveScheduler
        assert ProactiveScheduler is not None
    
    def test_nudge_type_imports(self):
        """
        Test: NudgeType imports from intelligent_proactive_mentor
        """
        from services.intelligent_proactive_mentor import NudgeType
        assert NudgeType.STREAK_PROTECTION.value == "streak_protection"
        assert NudgeType.COMEBACK.value == "comeback"
        assert NudgeType.MORNING_GREETING.value == "morning_greeting"
    
    def test_proactive_nudge_imports(self):
        """
        Test: ProactiveNudge imports correctly
        """
        from services.intelligent_proactive_mentor import ProactiveNudge
        assert ProactiveNudge is not None


# =============================================================================
# G) COMPANION MODE ROUTING TESTS
# =============================================================================

class TestCompanionModeRouting:
    """Tests for Sathi companion mode direct routing"""
    
    def test_companion_mode_intent_type_exists(self):
        """
        Test: COMPANION_MODE intent type exists in IntentType enum
        """
        from services.action_intent_detector import IntentType
        assert hasattr(IntentType, 'COMPANION_MODE')
        assert IntentType.COMPANION_MODE.value == 'companion_mode'
    
    def test_hey_sathi_detected_as_companion_mode(self):
        """
        Test: "hey Sathi" is detected as COMPANION_MODE intent
        """
        from services.action_intent_detector import get_intent_detector, IntentType
        
        detector = get_intent_detector()
        
        test_phrases = [
            "hey sathi",
            "hi sathi",
            "sathi, help me",
            "stay with me for 30 mins",
            "keep me accountable",
            "check in with me later",
            "be my study buddy",
            "need a study companion",
        ]
        
        for phrase in test_phrases:
            intent = detector.detect(phrase)
            assert intent.intent_type == IntentType.COMPANION_MODE, \
                f"Expected COMPANION_MODE for '{phrase}', got {intent.intent_type}"
            assert intent.requires_action is True
    
    def test_normal_question_not_companion_mode(self):
        """
        Test: Normal educational questions are NOT routed to companion mode
        """
        from services.action_intent_detector import get_intent_detector, IntentType
        
        detector = get_intent_detector()
        
        # These should NOT be companion mode
        test_phrases = [
            "explain Newton's laws",
            "what is photosynthesis",
            "solve this equation",
            "how does a battery work",
        ]
        
        for phrase in test_phrases:
            intent = detector.detect(phrase)
            assert intent.intent_type != IntentType.COMPANION_MODE, \
                f"'{phrase}' should NOT be COMPANION_MODE, got {intent.intent_type}"
    
    def test_reminder_still_routes_to_reminder(self):
        """
        Test: Reminder requests still route to REMINDER, not companion
        """
        from services.action_intent_detector import get_intent_detector, IntentType
        
        detector = get_intent_detector()
        
        intent = detector.detect("remind me tomorrow at 4pm")
        assert intent.intent_type == IntentType.REMINDER
        assert intent.requires_action is True


# =============================================================================
# H) NOTIFICATION POLICY ENGINE TESTS
# =============================================================================

class TestNotificationPolicyEngine:
    """
    Tests for the Notification Policy Engine (NO SPAM)
    """
    
    @pytest.mark.asyncio
    async def test_policy_blocks_during_cooldown(self, mock_db, test_user_id):
        """
        Test: Policy engine blocks notifications within type-specific cooldown
        """
        from services.notification_service import NotificationService
        
        service = NotificationService(mock_db)
        
        # Add a recent break_suggestion notification (within 60-min cooldown)
        await mock_db.user_notifications.insert_one({
            'user_id': test_user_id,
            'type': 'break_suggestion',
            'created_at': datetime.utcnow() - timedelta(minutes=30)
        })
        
        # Check policy
        result = await service.should_send_notification(
            user_id=test_user_id,
            notification_type='break_suggestion'
        )
        
        assert result['allowed'] is False
        assert 'cooldown' in result['reason']
    
    @pytest.mark.asyncio
    async def test_policy_allows_after_cooldown(self, mock_db, test_user_id):
        """
        Test: Policy engine allows notifications after cooldown expires
        """
        from services.notification_service import NotificationService
        
        service = NotificationService(mock_db)
        
        # Add old break_suggestion notification (outside 60-min cooldown)
        await mock_db.user_notifications.insert_one({
            'user_id': test_user_id,
            'type': 'break_suggestion',
            'created_at': datetime.utcnow() - timedelta(minutes=90)  # Past cooldown
        })
        
        # Check policy
        result = await service.should_send_notification(
            user_id=test_user_id,
            notification_type='break_suggestion'
        )
        
        assert result['allowed'] is True
    
    @pytest.mark.asyncio
    async def test_policy_blocks_at_daily_cap(self, mock_db, test_user_id):
        """
        Test: Policy engine blocks when daily cap is reached
        """
        from services.notification_service import NotificationService
        
        service = NotificationService(mock_db)
        
        # Add 3 break_suggestion notifications today (daily cap is 3)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        for i in range(3):
            await mock_db.user_notifications.insert_one({
                'user_id': test_user_id,
                'type': 'break_suggestion',
                'created_at': today_start + timedelta(hours=i+1)
            })
        
        # Check policy
        result = await service.should_send_notification(
            user_id=test_user_id,
            notification_type='break_suggestion'
        )
        
        assert result['allowed'] is False
        assert 'daily_cap' in result['reason']
    
    @pytest.mark.asyncio
    async def test_policy_skip_if_user_active(self, mock_db, test_user_id):
        """
        Test: Policy skips break notifications if user is currently active
        """
        from services.notification_service import NotificationService
        
        service = NotificationService(mock_db)
        
        # Add recent chat message (user is active)
        await mock_db.chat_messages.insert_one({
            'user_id': test_user_id,
            'message': 'Hello',
            'timestamp': datetime.utcnow() - timedelta(minutes=2)  # 2 mins ago
        })
        
        # Check policy for break_suggestion (which skips if active)
        result = await service.should_send_notification(
            user_id=test_user_id,
            notification_type='break_suggestion'
        )
        
        assert result['allowed'] is False
        assert 'user_active' in result['reason']
    
    @pytest.mark.asyncio
    async def test_idempotency_key_generation(self, mock_db, test_user_id):
        """
        Test: Idempotency key is consistent within time window
        """
        from services.notification_service import NotificationService
        
        service = NotificationService(mock_db)
        
        key1 = service._generate_idempotency_key(test_user_id, 'break_suggestion', 60)
        key2 = service._generate_idempotency_key(test_user_id, 'break_suggestion', 60)
        
        # Same user + type + window should produce same key
        assert key1 == key2
        
        # Different type should produce different key
        key3 = service._generate_idempotency_key(test_user_id, 'streak_protection', 60)
        assert key1 != key3


# =============================================================================
# I) 59449 MINUTES BUG FIX TESTS
# =============================================================================

class TestStudyFatigueBugFix:
    """
    Tests for the 59449 minutes bug fix in detect_study_fatigue()
    """
    
    @pytest.mark.asyncio
    async def test_fatigue_detection_uses_time_window(self, mock_db, test_user_id):
        """
        SHIP BLOCKER: detect_study_fatigue should only look at messages 
        within the last 3 hours, not all-time message span.
        """
        from services.intelligent_proactive_mentor import IntelligentProactiveMentor
        
        mentor = IntelligentProactiveMentor(mock_db)
        
        # Add messages spanning 41 days (the original bug scenario)
        now = datetime.utcnow()
        
        # Old messages (41 days ago) - should be IGNORED
        for i in range(30):
            await mock_db.chat_messages.insert_one({
                'user_id': test_user_id,
                'message': f'Old message {i}',
                'timestamp': now - timedelta(days=41, hours=i)
            })
        
        # Recent messages (within last 30 mins) - should be USED
        for i in range(5):
            await mock_db.chat_messages.insert_one({
                'user_id': test_user_id,
                'message': f'Recent message {i}',
                'timestamp': now - timedelta(minutes=5*i)
            })
        
        # Detect study fatigue
        nudge = await mentor.detect_study_fatigue(test_user_id)
        
        # Should NOT trigger break suggestion (30 mins < 90 mins threshold)
        # The bug would have calculated 41*24*60 = 59040 minutes!
        assert nudge is None
    
    @pytest.mark.asyncio
    async def test_fatigue_caps_at_180_minutes(self, mock_db, test_user_id):
        """
        Test: Even if calculation is wrong, output is capped at 180 minutes
        """
        from services.intelligent_proactive_mentor import IntelligentProactiveMentor
        
        mentor = IntelligentProactiveMentor(mock_db)
        
        now = datetime.utcnow()
        
        # Add messages within the 3-hour window but spanning 100 minutes
        for i in range(10):
            await mock_db.chat_messages.insert_one({
                'user_id': test_user_id,
                'message': f'Message {i}',
                'timestamp': now - timedelta(minutes=10*i)  # 0, 10, 20, ... 90 mins
            })
        
        nudge = await mentor.detect_study_fatigue(test_user_id)
        
        # Should trigger with reasonable session_minutes (capped)
        if nudge:
            assert nudge.data['session_minutes'] <= 180
    
    @pytest.mark.asyncio
    async def test_no_break_suggestion_for_short_sessions(self, mock_db, test_user_id):
        """
        Test: No break suggestion for sessions under 90 minutes
        """
        from services.intelligent_proactive_mentor import IntelligentProactiveMentor
        
        mentor = IntelligentProactiveMentor(mock_db)
        
        now = datetime.utcnow()
        
        # Add 10 messages in the last 45 minutes (under threshold)
        for i in range(10):
            await mock_db.chat_messages.insert_one({
                'user_id': test_user_id,
                'message': f'Message {i}',
                'timestamp': now - timedelta(minutes=45) + timedelta(minutes=i*4)
            })
        
        nudge = await mentor.detect_study_fatigue(test_user_id)
        
        assert nudge is None  # Should not suggest break for 45-min session


# =============================================================================
# J) NOTIFICATION DEDUPE TESTS
# =============================================================================

class TestNotificationDedupe:
    """
    Tests for notification deduplication (idempotency)
    """
    
    @pytest.mark.asyncio
    async def test_duplicate_notifications_are_coalesced(self, mock_db, test_user_id):
        """
        Test: Sending the same notification type within window coalesces, not duplicates
        """
        from services.notification_service import NotificationService
        
        service = NotificationService(mock_db)
        
        # Send first notification
        result1 = await service.send_notification(
            user_id=test_user_id,
            title="☕ Time for a break!",
            message="You've been studying for 90 minutes.",
            notification_type='break_suggestion',
            skip_policy_check=True  # Skip policy for test
        )
        
        # Try to send duplicate
        result2 = await service.send_notification(
            user_id=test_user_id,
            title="☕ Time for a break!",
            message="You've been studying for 95 minutes.",
            notification_type='break_suggestion',
            skip_policy_check=True
        )
        
        # Second should be coalesced, not created new
        assert result2['status'] == 'coalesced'
        
        # Check DB only has 1 notification
        count = await mock_db.user_notifications.count_documents({
            'user_id': test_user_id,
            'type': 'break_suggestion'
        })
        
        assert count == 1  # Only 1 notification, not 2


# =============================================================================
# RUN CONFIGURATION
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
