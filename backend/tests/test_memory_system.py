"""
Memory System Integration Tests
Tests the complete memory pipeline: context retrieval, storage, mastery tracking, and continuity
"""
import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class MockCollection:
    """Mock MongoDB collection for testing"""
    def __init__(self):
        self.data = []
    
    async def find_one(self, query):
        for doc in self.data:
            if all(doc.get(k) == v for k, v in query.items() if not k.startswith('$')):
                return doc
        return None
    
    async def insert_one(self, doc):
        self.data.append(doc)
        return MagicMock(inserted_id="test_id")
    
    async def update_one(self, query, update, upsert=False):
        for doc in self.data:
            if all(doc.get(k) == v for k, v in query.items() if not k.startswith('$')):
                if "$set" in update:
                    # Handle nested keys like "mastery_levels.topic"
                    for key, value in update["$set"].items():
                        if "." in key:
                            parts = key.split(".")
                            target = doc
                            for part in parts[:-1]:
                                if part not in target:
                                    target[part] = {}
                                target = target[part]
                            target[parts[-1]] = value
                        else:
                            doc[key] = value
                if "$inc" in update:
                    for k, v in update["$inc"].items():
                        doc[k] = doc.get(k, 0) + v
                if "$push" in update:
                    for k, v in update["$push"].items():
                        if k not in doc:
                            doc[k] = []
                        doc[k].append(v)
                return MagicMock(modified_count=1, matched_count=1)
        
        if upsert:
            new_doc = {**query}
            if "$set" in update:
                for key, value in update["$set"].items():
                    if "." in key:
                        parts = key.split(".")
                        target = new_doc
                        for part in parts[:-1]:
                            if part not in target:
                                target[part] = {}
                            target = target[part]
                        target[parts[-1]] = value
                    else:
                        new_doc[key] = value
            self.data.append(new_doc)
            return MagicMock(modified_count=0, matched_count=0, upserted_id="new_id")
        
        return MagicMock(modified_count=0, matched_count=0)
    
    def find(self, query):
        return MockCursor([d for d in self.data if all(d.get(k) == v for k, v in query.items() if not k.startswith('$'))])


class MockCursor:
    """Mock MongoDB cursor"""
    def __init__(self, data):
        self.data = data
        self._sort_key = None
        self._sort_dir = 1
        self._limit = None
    
    def sort(self, key, direction=1):
        self._sort_key = key
        self._sort_dir = direction
        return self
    
    def limit(self, n):
        self._limit = n
        return self
    
    async def to_list(self, length=None):
        result = self.data
        if self._sort_key:
            result = sorted(result, key=lambda x: x.get(self._sort_key, 0), reverse=self._sort_dir == -1)
        if self._limit:
            result = result[:self._limit]
        return result


class MockDB:
    """Mock MongoDB database"""
    def __init__(self):
        self.chat_messages = MockCollection()
        self.chat_sessions = MockCollection()
        self.user_memory_facts = MockCollection()
        self.user_learning_profile = MockCollection()
        self.users = MockCollection()


# ==================== Test Cases ====================

class TestMemoryService:
    """Test short-term conversation context"""
    
    @pytest.fixture
    def mock_db(self):
        return MockDB()
    
    @pytest.mark.asyncio
    async def test_get_conversation_context_empty(self, mock_db):
        """Test getting context when no messages exist"""
        from services.memory_service import MemoryService
        
        service = MemoryService(mock_db)
        context = await service.get_conversation_context(
            session_id="test_session",
            user_id="test_user",
            window_size=5
        )
        
        assert context == []
    
    @pytest.mark.asyncio
    async def test_get_conversation_context_with_messages(self, mock_db):
        """Test getting context with existing messages"""
        from services.memory_service import MemoryService
        
        # Add test messages
        mock_db.chat_messages.data = [
            {"session_id": "test_session", "user_id": "test_user", "timestamp": "2025-01-01T10:00:00", "user_message": "What is calculus?"},
            {"session_id": "test_session", "user_id": "test_user", "timestamp": "2025-01-01T10:01:00", "user_message": "Explain derivatives"},
            {"session_id": "test_session", "user_id": "test_user", "timestamp": "2025-01-01T10:02:00", "user_message": "How to integrate?"},
        ]
        
        service = MemoryService(mock_db)
        context = await service.get_conversation_context(
            session_id="test_session",
            user_id="test_user",
            window_size=2
        )
        
        assert len(context) == 2
    
    @pytest.mark.asyncio
    async def test_session_summary(self, mock_db):
        """Test session summary generation"""
        from services.memory_service import MemoryService
        
        mock_db.chat_messages.data = [
            {"session_id": "test_session", "user_id": "test_user", "user_message": "Explain derivatives", "intent": "concept_explanation"},
        ]
        
        service = MemoryService(mock_db)
        summary = await service.get_session_summary("test_session", "test_user")
        
        assert "session_id" in summary
        assert summary["total_messages"] == 1


class TestMasteryTracker:
    """Test mastery level tracking"""
    
    @pytest.fixture
    def mock_db(self):
        return MockDB()
    
    @pytest.mark.asyncio
    async def test_get_mastery_level_new_user(self, mock_db):
        """Test mastery level for new user (should be 0)"""
        from services.mastery_tracker import MasteryTracker
        
        tracker = MasteryTracker(mock_db)
        mastery = await tracker.get_mastery_level("new_user", "calculus_derivatives")
        
        assert mastery == 0
    
    @pytest.mark.asyncio
    async def test_update_mastery(self, mock_db):
        """Test mastery level update"""
        from services.mastery_tracker import MasteryTracker
        
        # Setup existing profile
        mock_db.user_learning_profile.data = [
            {"user_id": "test_user", "mastery_levels": {"calculus_derivatives": 30}}
        ]
        
        tracker = MasteryTracker(mock_db)
        await tracker.update_mastery(
            user_id="test_user",
            topic="calculus_derivatives",
            delta=10,
            reason="question_answered"
        )
        
        # Check profile was updated
        profile = mock_db.user_learning_profile.data[0]
        assert profile["mastery_levels"]["calculus_derivatives"] == 40
    
    @pytest.mark.asyncio
    async def test_mastery_clamped_to_100(self, mock_db):
        """Test mastery level is clamped to 100"""
        from services.mastery_tracker import MasteryTracker
        
        mock_db.user_learning_profile.data = [
            {"user_id": "test_user", "mastery_levels": {"physics": 95}}
        ]
        
        tracker = MasteryTracker(mock_db)
        await tracker.update_mastery("test_user", "physics", delta=20, reason="test")
        
        profile = mock_db.user_learning_profile.data[0]
        assert profile["mastery_levels"]["physics"] == 100
    
    @pytest.mark.asyncio
    async def test_get_weak_topics(self, mock_db):
        """Test getting weak topics"""
        from services.mastery_tracker import MasteryTracker
        
        mock_db.user_learning_profile.data = [
            {
                "user_id": "test_user",
                "mastery_levels": {
                    "calculus": 80,
                    "physics": 25,
                    "chemistry": 35
                }
            }
        ]
        
        tracker = MasteryTracker(mock_db)
        weak = await tracker.get_weak_topics("test_user", threshold=40)
        
        assert len(weak) == 2
        assert weak[0]["topic"] == "physics"  # Weakest first
        assert weak[1]["topic"] == "chemistry"


class TestContinuityEngine:
    """Test topic continuation detection"""
    
    @pytest.fixture
    def mock_db(self):
        return MockDB()
    
    @pytest.mark.asyncio
    async def test_no_continuation_for_new_user(self, mock_db):
        """Test no continuation for new user"""
        from services.continuity_engine import ContinuityEngine
        
        engine = ContinuityEngine(mock_db)
        result = await engine.detect_topic_continuation("new_user", "What is calculus?")
        
        assert result["is_continuation"] == False
    
    @pytest.mark.asyncio
    async def test_continuation_detected(self, mock_db):
        """Test continuation is detected for related topic"""
        from services.continuity_engine import ContinuityEngine
        
        mock_db.user_learning_profile.data = [
            {
                "user_id": "test_user",
                "last_active_topic": "calculus",
                "last_active_concept_thread": ["derivatives", "integrals"],
                "updated_at": datetime.now(timezone.utc)
            }
        ]
        
        engine = ContinuityEngine(mock_db)
        result = await engine.detect_topic_continuation("test_user", "Tell me more about integrals")
        
        assert result["is_continuation"] == True
        assert "integrals" in result.get("concept_thread", [])
    
    @pytest.mark.asyncio
    async def test_update_concept_thread(self, mock_db):
        """Test concept thread update"""
        from services.continuity_engine import ContinuityEngine
        
        mock_db.user_learning_profile.data = [
            {"user_id": "test_user", "last_active_concept_thread": []}
        ]
        
        engine = ContinuityEngine(mock_db)
        await engine.update_concept_thread("test_user", "calculus", ["derivatives", "limits"])
        
        profile = mock_db.user_learning_profile.data[0]
        assert "derivatives" in profile["last_active_concept_thread"]
        assert "limits" in profile["last_active_concept_thread"]


class TestSpacedRepetition:
    """Test SM-2 spaced repetition algorithm"""
    
    def test_first_review_scheduling(self):
        """Test first review is scheduled correctly"""
        from services.spaced_repetition import SpacedRepetitionEngine
        
        engine = SpacedRepetitionEngine()
        result = engine.calculate_next_review(
            current_interval_days=0,
            quality=3,
            current_easiness=2.5
        )
        
        assert result["interval_days"] == 1
        assert result["next_review_at"] is not None
    
    def test_failed_recall_resets_interval(self):
        """Test failed recall (quality < 3) resets interval"""
        from services.spaced_repetition import SpacedRepetitionEngine
        
        engine = SpacedRepetitionEngine()
        result = engine.calculate_next_review(
            current_interval_days=10,
            quality=2,  # Failed
            current_easiness=2.5
        )
        
        assert result["interval_days"] == 1  # Reset to 1
    
    def test_successful_recall_increases_interval(self):
        """Test successful recall increases interval"""
        from services.spaced_repetition import SpacedRepetitionEngine
        
        engine = SpacedRepetitionEngine()
        result = engine.calculate_next_review(
            current_interval_days=6,
            quality=4,  # Good recall
            current_easiness=2.5
        )
        
        assert result["interval_days"] > 6
    
    def test_feedback_to_quality_mapping(self):
        """Test feedback to SM-2 quality score mapping"""
        from services.spaced_repetition import SpacedRepetitionEngine
        
        engine = SpacedRepetitionEngine()
        
        assert engine.infer_quality_from_feedback("helpful") == 4
        assert engine.infer_quality_from_feedback("very_helpful") == 5
        assert engine.infer_quality_from_feedback("not_helpful") == 2
        assert engine.infer_quality_from_feedback("confused") == 1


class TestMemoryIntegration:
    """Test the complete memory integration service"""
    
    @pytest.fixture
    def mock_db(self):
        db = MockDB()
        # Add test user
        db.users.data = [
            {"user_id": "test_user", "full_name": "Test Student"}
        ]
        return db
    
    @pytest.mark.asyncio
    async def test_get_enhanced_context(self, mock_db):
        """Test getting enhanced context for AI response"""
        from services.memory_integration import MemoryIntegrationService
        
        service = MemoryIntegrationService(mock_db)
        context = await service.get_enhanced_context(
            user_id="test_user",
            session_id="test_session",
            question="Explain calculus derivatives"
        )
        
        assert "user_id" in context
        assert "session_id" in context
        assert "mastery_level" in context
        assert "recent_context" in context
        assert "relevant_memories" in context
    
    @pytest.mark.asyncio
    async def test_process_interaction(self, mock_db):
        """Test processing a completed interaction"""
        from services.memory_integration import MemoryIntegrationService
        
        service = MemoryIntegrationService(mock_db)
        result = await service.process_interaction(
            user_id="test_user",
            session_id="test_session",
            question="Explain calculus derivatives",
            response={"content": "Derivatives measure rate of change..."},
            feedback=None
        )
        
        assert "facts_extracted" in result
        assert "memories_stored" in result
        assert "mastery_updates" in result
    
    @pytest.mark.asyncio
    async def test_personalization_context(self, mock_db):
        """Test getting personalization context"""
        from services.memory_integration import MemoryIntegrationService
        
        # Add learning profile
        mock_db.user_learning_profile.data = [
            {
                "user_id": "test_user",
                "preferences": {
                    "metaphor_style": "cricket",
                    "explanation_depth": "deep",
                    "visual_learner": True
                },
                "stats": {
                    "level": 5,
                    "current_streak_days": 7
                }
            }
        ]
        
        service = MemoryIntegrationService(mock_db)
        context = await service.get_personalization_context("test_user")
        
        assert context["preferred_metaphor"] == "cricket"
        assert context["explanation_depth"] == "deep"
        assert context["level"] == 5
        assert context["streak"] == 7


class TestMemoryExtraction:
    """Test memory fact extraction"""
    
    @pytest.fixture
    def mock_db(self):
        return MockDB()
    
    @pytest.mark.asyncio
    async def test_extract_physics_concepts(self, mock_db):
        """Test extracting physics concepts"""
        from services.memory_extraction import MemoryExtractor
        
        extractor = MemoryExtractor(mock_db)
        facts = await extractor.extract_learning_facts(
            user_id="test_user",
            question="Explain Newton's laws of motion",
            response={"content": "Newton's first law states..."},
            session_id="test_session"
        )
        
        # Should extract newton_laws_motion concept
        concept_facts = [f for f in facts if f.get("fact_type") == "concept_learned"]
        topics = [f.get("topic") for f in concept_facts]
        
        assert any("newton" in t for t in topics)
    
    @pytest.mark.asyncio
    async def test_extract_calculus_concepts(self, mock_db):
        """Test extracting calculus concepts"""
        from services.memory_extraction import MemoryExtractor
        
        extractor = MemoryExtractor(mock_db)
        facts = await extractor.extract_learning_facts(
            user_id="test_user",
            question="How do I differentiate x^2?",
            response={"content": "The derivative of x^2 is 2x..."},
            session_id="test_session"
        )
        
        concept_facts = [f for f in facts if f.get("fact_type") == "concept_learned"]
        topics = [f.get("topic") for f in concept_facts]
        
        assert any("derivative" in t or "calculus" in t for t in topics)


# ==================== Run Tests ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

