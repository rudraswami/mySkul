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
    
    async def find_one(self, query, projection=None):
        for doc in self.data:
            if all(doc.get(k) == v for k, v in query.items() if not k.startswith('$')):
                if projection:
                    return {k: doc.get(k) for k in projection.keys() if doc.get(k) is not None}
                return doc
        return None
    
    async def insert_one(self, doc):
        self.data.append(doc.copy())
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
                        if "." in k:
                            parts = k.split(".")
                            target = doc
                            for part in parts[:-1]:
                                if part not in target:
                                    target[part] = {}
                                target = target[part]
                            target[parts[-1]] = target.get(parts[-1], 0) + v
                        else:
                            doc[k] = doc.get(k, 0) + v
                if "$push" in update:
                    for k, v in update["$push"].items():
                        if k not in doc:
                            doc[k] = []
                        # Handle $each and $slice
                        if isinstance(v, dict) and "$each" in v:
                            doc[k].extend(v["$each"])
                            if "$slice" in v:
                                doc[k] = doc[k][v["$slice"]:]
                        else:
                            doc[k].append(v)
                if "$addToSet" in update:
                    for k, v in update["$addToSet"].items():
                        if k not in doc:
                            doc[k] = []
                        if isinstance(v, dict) and "$each" in v:
                            for item in v["$each"]:
                                if item not in doc[k]:
                                    doc[k].append(item)
                        elif v not in doc[k]:
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
            if "$push" in update:
                for k, v in update["$push"].items():
                    if k not in new_doc:
                        new_doc[k] = []
                    if isinstance(v, dict) and "$each" in v:
                        new_doc[k].extend(v["$each"])
                        if "$slice" in v:
                            new_doc[k] = new_doc[k][v["$slice"]:]
                    else:
                        new_doc[k].append(v)
            if "$addToSet" in update:
                for k, v in update["$addToSet"].items():
                    if k not in new_doc:
                        new_doc[k] = []
                    if isinstance(v, dict) and "$each" in v:
                        for item in v["$each"]:
                            if item not in new_doc[k]:
                                new_doc[k].append(item)
            self.data.append(new_doc)
            return MagicMock(modified_count=0, matched_count=0, upserted_id="new_id")
        
        return MagicMock(modified_count=0, matched_count=0)
    
    async def count_documents(self, query):
        """Count matching documents"""
        count = 0
        for doc in self.data:
            if all(doc.get(k) == v for k, v in query.items() if not k.startswith('$')):
                count += 1
        return count
    
    async def delete_many(self, query):
        """Delete matching documents"""
        initial_count = len(self.data)
        if "$in" in str(query):
            # Handle {"_id": {"$in": [...]}}
            ids_to_delete = query.get("_id", {}).get("$in", [])
            self.data = [d for d in self.data if d.get("_id") not in ids_to_delete]
        else:
            self.data = [d for d in self.data if not all(d.get(k) == v for k, v in query.items())]
        return MagicMock(deleted_count=initial_count - len(self.data))
    
    def find(self, query, projection=None):
        filtered = [d for d in self.data if all(d.get(k) == v for k, v in query.items() if not k.startswith('$'))]
        return MockCursor(filtered)


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
        # Memory v2 collections
        self.session_states = MockCollection()
        self.student_profiles = MockCollection()
        self.memory_events = MockCollection()


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


# ==================== MEMORY v2 SHIP-BLOCKER TESTS ====================

class TestMemoryV2SessionPersistence:
    """
    SHIP-BLOCKER TEST 1: Session memory survives restart
    """
    
    @pytest.fixture
    def mock_db(self):
        db = MockDB()
        db.session_states = MockCollection()
        db.student_profiles = MockCollection()
        db.memory_events = MockCollection()
        return db
    
    @pytest.mark.asyncio
    async def test_session_state_persists(self, mock_db):
        """Session state must survive service restart (re-init)"""
        from services.memory_service import MemoryService
        
        user_id = "test_user_123"
        session_id = "session_abc"
        
        # First service instance - save state
        service1 = MemoryService(mock_db)
        await service1.save_session_state(
            user_id=user_id,
            session_id=session_id,
            state={
                "last_turns": [{"user": "What is calculus?", "ai": "Calculus is..."}],
                "session_summary": "Discussed calculus basics",
                "active_task": "learning calculus"
            }
        )
        
        # Simulate restart - create NEW service instance
        service2 = MemoryService(mock_db)
        
        # Load state - should be preserved
        loaded_state = await service2.get_session_state(user_id, session_id)
        
        assert loaded_state is not None
        assert len(loaded_state.get("last_turns", [])) == 1
        assert loaded_state.get("session_summary") == "Discussed calculus basics"
        assert loaded_state.get("active_task") == "learning calculus"
    
    @pytest.mark.asyncio
    async def test_session_turns_bounded(self, mock_db):
        """Session turns must be bounded to 10"""
        from services.memory_service import MemoryService
        
        service = MemoryService(mock_db)
        user_id = "test_user"
        session_id = "test_session"
        
        # Add 15 turns
        for i in range(15):
            await service.update_session_turn(
                user_id=user_id,
                session_id=session_id,
                user_message=f"Question {i}",
                ai_response=f"Answer {i}"
            )
        
        # Load state
        state = await service.get_session_state(user_id, session_id)
        
        # Must be bounded to 10
        assert len(state.get("last_turns", [])) <= 10


class TestMemoryV2MultiTenantIsolation:
    """
    SHIP-BLOCKER TEST 2: No cross-user leakage
    """
    
    @pytest.fixture
    def mock_db(self):
        db = MockDB()
        db.session_states = MockCollection()
        db.student_profiles = MockCollection()
        db.memory_events = MockCollection()
        return db
    
    @pytest.mark.asyncio
    async def test_no_cross_user_session_leakage(self, mock_db):
        """User A's session must NOT be visible to User B"""
        from services.memory_service import MemoryService
        
        service = MemoryService(mock_db)
        
        # User A writes session
        await service.save_session_state(
            user_id="user_A",
            session_id="session_A",
            state={
                "session_summary": "User A's private content",
                "last_turns": [{"user": "A's question", "ai": "A's answer"}]
            }
        )
        
        # User B tries to access User A's session
        user_b_state = await service.get_session_state(
            user_id="user_B",
            session_id="session_A"  # Same session ID
        )
        
        # Must NOT see User A's content
        assert user_b_state.get("session_summary", "") != "User A's private content"
        assert len(user_b_state.get("last_turns", [])) == 0
    
    @pytest.mark.asyncio
    async def test_no_cross_user_profile_leakage(self, mock_db):
        """User A's profile must NOT be visible to User B"""
        from services.memory_service import MemoryService
        
        service = MemoryService(mock_db)
        
        # User A's profile
        await service.update_student_profile(
            user_id="user_A",
            updates={
                "exam_target": "JEE",
                "weak_topics": ["physics", "chemistry"]
            }
        )
        
        # User B's profile - should be independent
        user_b_profile = await service.get_student_profile("user_B")
        
        # Must NOT see User A's data
        assert user_b_profile.get("exam_target") != "JEE"
        assert "physics" not in user_b_profile.get("weak_topics", [])


class TestMemoryV2BoundedGrowth:
    """
    SHIP-BLOCKER TEST 3: Memory growth is bounded
    """
    
    @pytest.fixture
    def mock_db(self):
        db = MockDB()
        db.session_states = MockCollection()
        db.student_profiles = MockCollection()
        db.memory_events = MockCollection()
        return db
    
    @pytest.mark.asyncio
    async def test_session_summary_bounded(self, mock_db):
        """Session summary must be bounded to 800 chars"""
        from services.memory_service import MemoryService
        
        service = MemoryService(mock_db)
        
        # Create very long summary
        long_summary = "X" * 2000
        
        await service.update_session_summary(
            user_id="test_user",
            session_id="test_session",
            summary=long_summary
        )
        
        state = await service.get_session_state("test_user", "test_session")
        
        # Must be truncated to 800
        assert len(state.get("session_summary", "")) <= 800
    
    @pytest.mark.asyncio
    async def test_weak_topics_bounded(self, mock_db):
        """Weak topics must be bounded to 10"""
        from services.memory_service import MemoryService
        
        service = MemoryService(mock_db)
        
        # Add 15 weak topics
        topics = [f"topic_{i}" for i in range(15)]
        
        await service.update_student_profile(
            user_id="test_user",
            updates={"weak_topics": topics}
        )
        
        profile = await service.get_student_profile("test_user")
        
        # Must be bounded to 10
        assert len(profile.get("weak_topics", [])) <= 10


class TestMemoryV2SelectiveRecall:
    """
    SHIP-BLOCKER TEST 4: Relevance recall works correctly
    """
    
    @pytest.fixture
    def mock_db(self):
        db = MockDB()
        db.session_states = MockCollection()
        db.student_profiles = MockCollection()
        db.memory_events = MockCollection()
        db.user_memory_facts = MockCollection()
        db.users = MockCollection()
        return db
    
    @pytest.mark.asyncio
    async def test_memory_context_pack_structure(self, mock_db):
        """MemoryContextPack must have all required fields"""
        from services.memory_integration import MemoryIntegrationService
        
        service = MemoryIntegrationService(mock_db)
        
        pack = await service.get_memory_context_pack(
            user_id="test_user",
            session_id="test_session",
            query="Explain friction",
            route_type="educational"
        )
        
        # Must have all contract fields
        required_fields = [
            "user_id", "session_id", "student_name", "exam_target",
            "current_mastery", "mastery_bucket", "relevant_memories",
            "session_summary", "active_task", "last_topic",
            "preferred_explanation", "pacing", "is_weak_area", "needs_encouragement"
        ]
        
        for field in required_fields:
            assert field in pack, f"Missing required field: {field}"
    
    @pytest.mark.asyncio
    async def test_relevant_memories_bounded(self, mock_db):
        """Relevant memories must be bounded to 5"""
        from services.memory_integration import MemoryIntegrationService
        
        # Add many memories
        for i in range(20):
            mock_db.user_memory_facts.data.append({
                "user_id": "test_user",
                "fact_id": f"fact_{i}",
                "content": f"Memory about friction #{i}",
                "topic": "friction",
                "subject": "physics",
                "is_active": True,
                "created_at": datetime.now(timezone.utc)
            })
        
        service = MemoryIntegrationService(mock_db)
        
        pack = await service.get_memory_context_pack(
            user_id="test_user",
            session_id="test_session",
            query="Explain friction",
            route_type="educational"
        )
        
        # Must be bounded to 5
        assert len(pack.get("relevant_memories", [])) <= 5


class TestMemoryV2AgentConsistency:
    """
    SHIP-BLOCKER TEST 5: All agents consume memory consistently
    """
    
    def test_memory_contract_schema_exists(self):
        """Memory contract schemas must exist"""
        from models.memory import (
            StudentProfile,
            SessionState,
            MemoryEvent,
            MemoryContextPack,
            MEMORY_SCHEMA_VERSION
        )
        
        assert MEMORY_SCHEMA_VERSION == 2
        assert StudentProfile is not None
        assert SessionState is not None
        assert MemoryEvent is not None
        assert MemoryContextPack is not None
    
    def test_student_profile_has_required_fields(self):
        """StudentProfile must have all canonical fields"""
        from models.memory import StudentProfile
        
        # Create profile
        profile = StudentProfile(user_id="test")
        
        # Check required fields exist
        assert hasattr(profile, 'user_id')
        assert hasattr(profile, 'schema_version')
        assert hasattr(profile, 'mastery_by_topic')
        assert hasattr(profile, 'weak_topics')
        assert hasattr(profile, 'strong_topics')
        assert hasattr(profile, 'preferred_explanation')
        assert hasattr(profile, 'pacing')
    
    def test_session_state_has_required_fields(self):
        """SessionState must have all canonical fields"""
        from models.memory import SessionState
        
        # Create session state
        state = SessionState(user_id="test", session_id="session")
        
        # Check required fields exist
        assert hasattr(state, 'user_id')
        assert hasattr(state, 'session_id')
        assert hasattr(state, 'schema_version')
        assert hasattr(state, 'last_turns')
        assert hasattr(state, 'session_summary')
        assert hasattr(state, 'active_task')
        assert hasattr(state, 'last_used_agent')


class TestMemoryV2WritePolicy:
    """
    SHIP-BLOCKER TEST: Memory write policy enforcement
    """
    
    @pytest.fixture
    def mock_db(self):
        db = MockDB()
        db.session_states = MockCollection()
        db.student_profiles = MockCollection()
        db.memory_events = MockCollection()
        db.user_memory_facts = MockCollection()
        return db
    
    @pytest.mark.asyncio
    async def test_write_memory_after_response(self, mock_db):
        """write_memory_after_response must work correctly"""
        from services.memory_integration import MemoryIntegrationService
        
        service = MemoryIntegrationService(mock_db)
        
        result = await service.write_memory_after_response(
            user_id="test_user",
            session_id="test_session",
            user_message="Explain friction",
            ai_response="Friction is a force that opposes motion...",
            agent_name="mentor",
            topics=["friction", "forces"],
            request_id="req_123"
        )
        
        assert result.get("turn_added") == True
        assert result.get("event_logged") == True
        assert len(result.get("errors", [])) == 0


# ==================== Run Tests ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

