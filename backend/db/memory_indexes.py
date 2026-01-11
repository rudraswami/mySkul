"""
Database Indexes for Memory System
Creates optimal indexes for fast memory retrieval

Production-grade: IDEMPOTENT, SAFE, NEVER FAILS
"""
import logging
from typing import Any, Dict, List, Tuple, Union
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError, OperationFailure

logger = logging.getLogger(__name__)


async def _safe_create_index(
    collection,
    index_spec: Union[str, List[Tuple[str, int]]],
    index_name: str,
    unique: bool = False,
    **kwargs
) -> Tuple[bool, str]:
    """
    Production-grade index creation - IDEMPOTENT and SAFE.
    
    Strategy:
    1. Check if index exists by name (skip if exists)
    2. Attempt creation only if missing
    3. Handle DuplicateKeyError gracefully (duplicate data)
    4. Never raise exceptions - return status
    
    Returns:
        Tuple of (success: bool, status_message: str)
    """
    collection_name = collection.name
    
    try:
        # Check if index already exists by name
        existing_indexes = await collection.list_indexes().to_list(length=None)
        existing_names = {idx.get("name") for idx in existing_indexes}
        
        if index_name in existing_names:
            return (True, "exists")
        
        # Attempt to create index
        await collection.create_index(
            index_spec,
            name=index_name,
            unique=unique,
            background=True,
            **kwargs
        )
        return (True, "created")
        
    except DuplicateKeyError:
        logger.warning(
            f"⚠️ Index '{index_name}' on {collection_name}: "
            f"SKIPPED - Duplicate data exists. Clean duplicates to enable unique index."
        )
        return (False, "duplicate_data")
        
    except OperationFailure as e:
        error_msg = str(e)
        if "IndexOptionsConflict" in error_msg or "already exists" in error_msg.lower():
            return (True, "exists_different_options")
        elif "E11000" in error_msg or "duplicate key" in error_msg.lower():
            logger.warning(
                f"⚠️ Index '{index_name}' on {collection_name}: "
                f"SKIPPED - Duplicate data prevents unique index creation."
            )
            return (False, "duplicate_data")
        else:
            logger.warning(f"⚠️ Index '{index_name}' on {collection_name}: {error_msg}")
            return (False, "operation_failure")
            
    except Exception as e:
        logger.warning(f"⚠️ Index '{index_name}' on {collection_name}: Unexpected error - {e}")
        return (False, "unexpected_error")


async def create_memory_indexes(db: AsyncIOMotorDatabase) -> bool:
    """
    Create all necessary indexes for memory system.
    
    PRODUCTION-GRADE:
    - Idempotent: Safe to run on every deploy
    - Never fails startup: Errors are logged, not raised
    - Clear logging: Each index reports its status
    
    Indexes ensure fast queries for:
    - Memory retrieval by user
    - Semantic search
    - Mastery lookups
    - Due review queries
    - Continuity checks
    """
    logger.info("📚 Initializing memory system indexes...")
    
    results = []
    
    # =========================================================================
    # Collection 1: user_memory_facts
    # =========================================================================
    
    # Index 1: User + Active (for retrieval)
    results.append(await _safe_create_index(
        db.user_memory_facts,
        [("user_id", 1), ("is_active", 1)],
        "idx_user_active"
    ))
    
    # Index 2: User + Topic + Mastery (for topic queries)
    results.append(await _safe_create_index(
        db.user_memory_facts,
        [("user_id", 1), ("topic", 1), ("mastery_level", -1)],
        "idx_user_topic_mastery"
    ))
    
    # Index 3: User + Next Review (for spaced repetition)
    results.append(await _safe_create_index(
        db.user_memory_facts,
        [("user_id", 1), ("next_review_at", 1), ("is_active", 1)],
        "idx_user_review_schedule"
    ))
    
    # Index 4: Fact ID (unique lookup)
    results.append(await _safe_create_index(
        db.user_memory_facts,
        [("fact_id", 1)],
        "idx_fact_id_unique",
        unique=True
    ))
    
    # Index 5: Created At (for temporal queries)
    results.append(await _safe_create_index(
        db.user_memory_facts,
        [("user_id", 1), ("created_at", -1)],
        "idx_user_created"
    ))
    
    logger.info("  user_memory_facts: indexes processed")
    
    # =========================================================================
    # Collection 2: user_learning_profile
    # =========================================================================
    
    # Index 1: User ID (unique) - MAY FAIL if duplicate data exists
    results.append(await _safe_create_index(
        db.user_learning_profile,
        [("user_id", 1)],
        "idx_profile_user_unique",
        unique=True
    ))
    
    # Index 2: Updated At (for recent activity)
    results.append(await _safe_create_index(
        db.user_learning_profile,
        [("updated_at", -1)],
        "idx_profile_updated"
    ))
    
    logger.info("  user_learning_profile: indexes processed")
    
    # =========================================================================
    # Collection 3: chat_messages
    # =========================================================================
    
    # Index for session-based retrieval
    results.append(await _safe_create_index(
        db.chat_messages,
        [("session_id", 1), ("timestamp", -1)],
        "idx_session_timestamp"
    ))
    
    # Index for user-based retrieval
    results.append(await _safe_create_index(
        db.chat_messages,
        [("user_id", 1), ("timestamp", -1)],
        "idx_user_timestamp"
    ))
    
    logger.info("  chat_messages: indexes processed")
    
    # =========================================================================
    # Collection 4: learning_events (Cognitive OS)
    # =========================================================================
    
    # Index 1: User + Timestamp (for recent events retrieval)
    results.append(await _safe_create_index(
        db.learning_events,
        [("user_id", 1), ("timestamp", -1)],
        "idx_events_user_time"
    ))
    
    # Index 2: User + Event Type (for pattern detection)
    results.append(await _safe_create_index(
        db.learning_events,
        [("user_id", 1), ("event_type", 1), ("timestamp", -1)],
        "idx_events_user_type"
    ))
    
    # Index 3: Session-based retrieval
    results.append(await _safe_create_index(
        db.learning_events,
        [("session_id", 1), ("timestamp", -1)],
        "idx_events_session_time"
    ))
    
    logger.info("  learning_events: indexes processed")
    
    # =========================================================================
    # Collection 5: conversation_states
    # =========================================================================
    
    # Index for user+session state lookup (unique)
    results.append(await _safe_create_index(
        db.conversation_states,
        [("user_id", 1), ("session_id", 1)],
        "idx_conv_state_user_session",
        unique=True
    ))
    
    logger.info("  conversation_states: indexes processed")
    
    # =========================================================================
    # Summary
    # =========================================================================
    successful = sum(1 for success, _ in results if success)
    total = len(results)
    skipped = total - successful
    
    if skipped == 0:
        logger.info(f"🎉 Memory system indexes ready: {successful}/{total} indexes verified/created")
    else:
        logger.warning(
            f"⚠️ Memory system indexes: {successful}/{total} ready, "
            f"{skipped} skipped (duplicate data - see warnings above)"
        )
    
    # Always return True - indexes are best-effort, don't fail startup
    return True


async def drop_memory_indexes(db: AsyncIOMotorDatabase) -> bool:
    """
    Drop all memory system indexes (for cleanup/testing).
    Safe: Ignores errors if indexes don't exist.
    """
    logger.info("🗑️ Dropping memory system indexes...")
    
    indexes_to_drop = [
        (db.user_memory_facts, "idx_user_active"),
        (db.user_memory_facts, "idx_user_topic_mastery"),
        (db.user_memory_facts, "idx_user_review_schedule"),
        (db.user_memory_facts, "idx_fact_id_unique"),
        (db.user_memory_facts, "idx_user_created"),
        (db.user_learning_profile, "idx_profile_user_unique"),
        (db.user_learning_profile, "idx_profile_updated"),
        (db.chat_messages, "idx_session_timestamp"),
        (db.chat_messages, "idx_user_timestamp"),
        (db.learning_events, "idx_events_user_time"),
        (db.learning_events, "idx_events_user_type"),
        (db.learning_events, "idx_events_session_time"),
        (db.conversation_states, "idx_conv_state_user_session"),
    ]
    
    dropped = 0
    for collection, index_name in indexes_to_drop:
        try:
            await collection.drop_index(index_name)
            dropped += 1
        except Exception:
            # Index doesn't exist - that's fine
            pass
    
    logger.info(f"✅ Dropped {dropped}/{len(indexes_to_drop)} memory indexes")
    return True

