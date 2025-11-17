"""
Database Indexes for Memory System
Creates optimal indexes for fast memory retrieval
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)


async def create_memory_indexes(db: AsyncIOMotorClient):
    """
    Create all necessary indexes for memory system
    
    Indexes ensure fast queries for:
    - Memory retrieval by user
    - Semantic search
    - Mastery lookups
    - Due review queries
    - Continuity checks
    """
    try:
        logger.info("📚 Creating memory system indexes...")
        
        # Collection 1: user_memory_facts
        # ================================
        
        # Index 1: User + Active (for retrieval)
        await db.user_memory_facts.create_index([
            ("user_id", 1),
            ("is_active", 1)
        ], name="idx_user_active")
        
        # Index 2: User + Topic + Mastery (for topic queries)
        await db.user_memory_facts.create_index([
            ("user_id", 1),
            ("topic", 1),
            ("mastery_level", -1)
        ], name="idx_user_topic_mastery")
        
        # Index 3: User + Next Review (for spaced repetition)
        await db.user_memory_facts.create_index([
            ("user_id", 1),
            ("next_review_at", 1),
            ("is_active", 1)
        ], name="idx_user_review_schedule")
        
        # Index 4: Fact ID (unique lookup)
        await db.user_memory_facts.create_index([
            ("fact_id", 1)
        ], unique=True, name="idx_fact_id_unique")
        
        # Index 5: Created At (for temporal queries)
        await db.user_memory_facts.create_index([
            ("user_id", 1),
            ("created_at", -1)
        ], name="idx_user_created")
        
        logger.info("✅ user_memory_facts indexes created")
        
        # Collection 2: user_learning_profile
        # ===================================
        
        # Index 1: User ID (unique)
        await db.user_learning_profile.create_index([
            ("user_id", 1)
        ], unique=True, name="idx_profile_user_unique")
        
        # Index 2: Updated At (for recent activity)
        await db.user_learning_profile.create_index([
            ("updated_at", -1)
        ], name="idx_profile_updated")
        
        logger.info("✅ user_learning_profile indexes created")
        
        # Collection 3: chat_messages (already exists, add memory-specific indexes)
        # =========================================================================
        
        # Index for session-based retrieval (if not exists)
        await db.chat_messages.create_index([
            ("session_id", 1),
            ("timestamp", -1)
        ], name="idx_session_timestamp")
        
        # Index for user-based retrieval
        await db.chat_messages.create_index([
            ("user_id", 1),
            ("timestamp", -1)
        ], name="idx_user_timestamp")
        
        logger.info("✅ chat_messages indexes created")
        
        logger.info("🎉 All memory system indexes created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create memory indexes: {e}")
        return False


async def drop_memory_indexes(db: AsyncIOMotorClient):
    """Drop all memory system indexes (for cleanup/testing)"""
    try:
        logger.info("🗑️ Dropping memory system indexes...")
        
        # Drop indexes from user_memory_facts
        await db.user_memory_facts.drop_index("idx_user_active")
        await db.user_memory_facts.drop_index("idx_user_topic_mastery")
        await db.user_memory_facts.drop_index("idx_user_review_schedule")
        await db.user_memory_facts.drop_index("idx_fact_id_unique")
        await db.user_memory_facts.drop_index("idx_user_created")
        
        # Drop indexes from user_learning_profile
        await db.user_learning_profile.drop_index("idx_profile_user_unique")
        await db.user_learning_profile.drop_index("idx_profile_updated")
        
        logger.info("✅ Memory indexes dropped")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ Some indexes might not exist: {e}")
        return False

