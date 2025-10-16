"""
Database Index Initialization Script
Idempotent index creation for all collections

Run this script to ensure all required database indexes exist:
    python -m scripts.init_indexes
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings


async def create_indexes():
    """
    Create all required database indexes (idempotent)
    """
    print("🔍 Initializing database indexes...")
    print(f"📊 Database: {settings.DB_NAME}")
    
    # Connect to database
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.DB_NAME]
    
    def safe_create_index(collection, index_spec, collection_name):
        """Helper to create index with proper error handling"""
        try:
            if isinstance(index_spec[0], list):
                # Compound index
                collection.create_index(index_spec[0], **index_spec[1])
                index_name = "_".join([f"{f[0]}_{f[1]}" for f in index_spec[0]])
            else:
                # Single field index
                collection.create_index(index_spec[0], **index_spec[1])
                index_name = index_spec[0]
            
            print(f"   ✓ {index_name}")
        except Exception as e:
            error_msg = str(e)
            if isinstance(index_spec[0], list):
                index_name = "_".join([f"{f[0]}_{f[1]}" for f in index_spec[0]])
            else:
                index_name = index_spec[0]
            
            if "DuplicateKey" in error_msg:
                print(f"   ⚠️  {index_name} (unique constraint violated - clean {collection_name} data)")
            elif "IndexOptionsConflict" in error_msg or "already exists" in error_msg:
                print(f"   ℹ️  {index_name} (already exists)")
            else:
                print(f"   ❌ {index_name} failed: {error_msg}")
                raise
    
    try:
        # =========================================================================
        # USERS COLLECTION
        # =========================================================================
        print("\n👤 Creating indexes for 'users' collection...")
        
        users_indexes = [
            # Unique indexes
            ("email", {"unique": True, "sparse": True}),
            ("google_id", {"unique": True, "sparse": True}),
            
            # Query optimization indexes
            ("session_token", {"sparse": True}),
            ("auth_provider", {}),
            ("exam_type", {}),
            ("subscription_type", {}),
            
            # Compound indexes for common queries
            ([("session_token", 1), ("session_expiry", 1)], {"sparse": True}),
            ([("email", 1), ("auth_provider", 1)], {}),
        ]
        
        for index_spec in users_indexes:
            await safe_create_index(db.users, index_spec, "users")
        
        # =========================================================================
        # CHAT SESSIONS COLLECTION
        # =========================================================================
        print("\n💬 Creating indexes for 'chat_sessions' collection...")
        
        chat_sessions_indexes = [
            ("user_id", {}),
            ("created_at", {}),
            ("subject", {}),
            ([("user_id", 1), ("created_at", -1)], {}),
        ]
        
        for index_spec in chat_sessions_indexes:
            if isinstance(index_spec[0], list):
                await db.chat_sessions.create_index(index_spec[0], **index_spec[1])
                index_name = "_".join([f"{f[0]}_{f[1]}" for f in index_spec[0]])
            else:
                await db.chat_sessions.create_index(index_spec[0], **index_spec[1])
                index_name = index_spec[0]
            
            print(f"   ✓ {index_name}")
        
        # =========================================================================
        # MESSAGES COLLECTION
        # =========================================================================
        print("\n📨 Creating indexes for 'messages' collection...")
        
        messages_indexes = [
            ("session_id", {}),
            ("user_id", {}),
            ("timestamp", {}),
            ([("session_id", 1), ("timestamp", 1)], {}),
        ]
        
        for index_spec in messages_indexes:
            if isinstance(index_spec[0], list):
                await db.messages.create_index(index_spec[0], **index_spec[1])
                index_name = "_".join([f"{f[0]}_{f[1]}" for f in index_spec[0]])
            else:
                await db.messages.create_index(index_spec[0], **index_spec[1])
                index_name = index_spec[0]
            
            print(f"   ✓ {index_name}")
        
        # =========================================================================
        # SUBSCRIPTIONS COLLECTION
        # =========================================================================
        print("\n💳 Creating indexes for 'subscriptions' collection...")
        
        subscriptions_indexes = [
            ("user_id", {"unique": True}),
            ("subscription_type", {}),
            ("status", {}),
            ("end_date", {}),
            ([("user_id", 1), ("status", 1)], {}),
        ]
        
        for index_spec in subscriptions_indexes:
            if isinstance(index_spec[0], list):
                await db.subscriptions.create_index(index_spec[0], **index_spec[1])
                index_name = "_".join([f"{f[0]}_{f[1]}" for f in index_spec[0]])
            else:
                await db.subscriptions.create_index(index_spec[0], **index_spec[1])
                index_name = index_spec[0]
            
            print(f"   ✓ {index_name}")
        
        # =========================================================================
        # USAGE TRACKING COLLECTION
        # =========================================================================
        print("\n📊 Creating indexes for 'usage_tracking' collection...")
        
        usage_tracking_indexes = [
            ("user_id", {}),
            ("feature", {}),
            ("month", {}),
            ([("user_id", 1), ("feature", 1), ("month", 1)], {"unique": True}),
        ]
        
        for index_spec in usage_tracking_indexes:
            try:
                if isinstance(index_spec[0], list):
                    await db.usage_tracking.create_index(index_spec[0], **index_spec[1])
                    index_name = "_".join([f"{f[0]}_{f[1]}" for f in index_spec[0]])
                else:
                    await db.usage_tracking.create_index(index_spec[0], **index_spec[1])
                    index_name = index_spec[0]
                
                print(f"   ✓ {index_name}")
            except Exception as e:
                if "DuplicateKey" in str(e):
                    print(f"   ⚠️  {index_name} (skipped - unique constraint violated, clean data first)")
                elif "IndexOptionsConflict" in str(e) or "already exists" in str(e):
                    print(f"   ℹ️  {index_name} (already exists)")
                else:
                    raise
        
        # =========================================================================
        # MOCK TESTS COLLECTION (Enhanced for Phase 1 - Stability)
        # =========================================================================
        print("\n📝 Creating indexes for 'mock_tests' collection...")
        
        mock_tests_indexes = [
            # Primary queries
            ("test_id", {"unique": True}),
            ("user_id", {}),
            ("student_id", {}),  # Legacy field support
            ("status", {}),
            ("generated_at", {}),
            
            # Dashboard optimization - most common query patterns
            ([("user_id", 1), ("status", 1)], {}),
            ([("student_id", 1), ("status", 1)], {}),
            ([("user_id", 1), ("generated_at", -1)], {}),
            ([("student_id", 1), ("generated_at", -1)], {}),
            
            # Detailed review optimization
            ([("test_id", 1), ("user_id", 1)], {}),
            ([("test_id", 1), ("student_id", 1)], {}),
        ]
        
        for index_spec in mock_tests_indexes:
            if isinstance(index_spec[0], list):
                await db.mock_tests.create_index(index_spec[0], **index_spec[1])
                index_name = "_".join([f"{f[0]}_{f[1]}" for f in index_spec[0]])
            else:
                await db.mock_tests.create_index(index_spec[0], **index_spec[1])
                index_name = index_spec[0]
            
            print(f"   ✓ {index_name}")
        
        # =========================================================================
        # TEST ATTEMPTS COLLECTION (NEW - Phase 1 Optimization)
        # =========================================================================
        print("\n📊 Creating indexes for 'test_attempts' collection...")
        
        test_attempts_indexes = [
            ("test_id", {}),
            ("student_id", {}),
            ("submitted_at", {}),
            
            # Performance trends optimization
            ([("student_id", 1), ("submitted_at", 1)], {}),
            ([("test_id", 1), ("student_id", 1)], {}),
            ([("test_id", 1), ("submitted_at", -1)], {}),
        ]
        
        for index_spec in test_attempts_indexes:
            if isinstance(index_spec[0], list):
                await db.test_attempts.create_index(index_spec[0], **index_spec[1])
                index_name = "_".join([f"{f[0]}_{f[1]}" for f in index_spec[0]])
            else:
                await db.test_attempts.create_index(index_spec[0], **index_spec[1])
                index_name = index_spec[0]
            
            print(f"   ✓ {index_name}")
        
        # =========================================================================
        # AUTO NOTES COLLECTION
        # =========================================================================
        print("\n📔 Creating indexes for 'auto_notes' collection...")
        
        auto_notes_indexes = [
            ("user_id", {}),
            ("subject", {}),
            ("created_at", {}),
            ([("user_id", 1), ("created_at", -1)], {}),
        ]
        
        for index_spec in auto_notes_indexes:
            if isinstance(index_spec[0], list):
                await db.auto_notes.create_index(index_spec[0], **index_spec[1])
                index_name = "_".join([f"{f[0]}_{f[1]}" for f in index_spec[0]])
            else:
                await db.auto_notes.create_index(index_spec[0], **index_spec[1])
                index_name = index_spec[0]
            
            print(f"   ✓ {index_name}")
        
        # =========================================================================
        # OAUTH STATES COLLECTION (for OAuth flow)
        # =========================================================================
        print("\n🔐 Creating indexes for 'oauth_states' collection...")
        
        oauth_states_indexes = [
            ("state", {"unique": True}),
            ("expires_at", {"expireAfterSeconds": 600}),  # TTL index (10 minutes)
        ]
        
        for index_spec in oauth_states_indexes:
            await db.oauth_states.create_index(index_spec[0], **index_spec[1])
            print(f"   ✓ {index_spec[0]}")
        
        # =========================================================================
        # SUMMARY
        # =========================================================================
        print("\n" + "="*60)
        print("✅ All indexes created successfully!")
        print("="*60)
        
        # Print index statistics
        collections = [
            "users", "chat_sessions", "messages", "subscriptions",
            "usage_tracking", "mock_tests", "test_attempts", "auto_notes", "oauth_states"
        ]
        
        print("\n📈 Index Statistics:")
        for collection_name in collections:
            collection = db[collection_name]
            indexes = await collection.list_indexes().to_list(length=None)
            print(f"   {collection_name}: {len(indexes)} indexes")
        
    except Exception as e:
        print(f"\n❌ Error creating indexes: {e}")
        raise
    
    finally:
        client.close()
        print("\n🔌 Database connection closed")


if __name__ == "__main__":
    print("="*60)
    print("  DATABASE INDEX INITIALIZATION")
    print("="*60)
    
    # Run async function
    asyncio.run(create_indexes())
    
    print("\n✨ Index initialization complete!")
