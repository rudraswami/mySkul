#!/usr/bin/env python3
"""
Add performance indexes to MongoDB collections
Optimizes queries for usage tracking, subscription checks, and dashboard analytics
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

async def add_indexes():
    """Add optimized indexes for performance"""
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    
    print("=" * 60)
    print("Adding Performance Indexes")
    print("=" * 60)
    
    # 1. USAGE_TRACKING COLLECTION - Critical for subscription checks
    print("\n📊 usage_tracking collection:")
    try:
        # Compound index for user_id + feature_name + usage_date (most frequent query)
        await db.usage_tracking.create_index(
            [("user_id", 1), ("feature_name", 1), ("usage_date", -1)],
            name="user_feature_date_idx"
        )
        print("   ✅ Created: user_feature_date_idx (user_id + feature_name + usage_date)")
        
        # Index for feature_name queries
        await db.usage_tracking.create_index("feature_name", name="feature_name_idx")
        print("   ✅ Created: feature_name_idx")
        
        # Index for date range queries
        await db.usage_tracking.create_index("usage_date", name="usage_date_idx")
        print("   ✅ Created: usage_date_idx")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. USER_SUBSCRIPTIONS COLLECTION - For subscription lookups
    print("\n💳 user_subscriptions collection:")
    try:
        # Unique index on user_id for fast subscription lookups
        await db.user_subscriptions.create_index("user_id", unique=True, name="user_id_unique_idx")
        print("   ✅ Created: user_id_unique_idx (unique)")
        
        # Index on subscription_tier for analytics
        await db.user_subscriptions.create_index("subscription_tier", name="subscription_tier_idx")
        print("   ✅ Created: subscription_tier_idx")
        
        # Index on status for active subscription queries
        await db.user_subscriptions.create_index("status", name="status_idx")
        print("   ✅ Created: status_idx")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. MOCK_TESTS COLLECTION - For test analytics and dashboard
    print("\n🎯 mock_tests collection:")
    try:
        # Compound index for user_id + created_at (dashboard queries)
        await db.mock_tests.create_index(
            [("user_id", 1), ("created_at", -1)],
            name="user_created_idx"
        )
        print("   ✅ Created: user_created_idx (user_id + created_at)")
        
        # Compound index for user_id + exam_type + status
        await db.mock_tests.create_index(
            [("user_id", 1), ("exam_type", 1), ("status", 1)],
            name="user_exam_status_idx"
        )
        print("   ✅ Created: user_exam_status_idx (user_id + exam_type + status)")
        
        # Index on status for filtering
        await db.mock_tests.create_index("status", name="mock_status_idx")
        print("   ✅ Created: mock_status_idx")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. AUTO_NOTE_SESSIONS COLLECTION - For notes dashboard
    print("\n📝 auto_note_sessions collection:")
    try:
        # Compound index for user_id + created_at
        await db.auto_note_sessions.create_index(
            [("user_id", 1), ("created_at", -1)],
            name="user_created_notes_idx"
        )
        print("   ✅ Created: user_created_notes_idx (user_id + created_at)")
        
        # Compound index for user_id + status
        await db.auto_note_sessions.create_index(
            [("user_id", 1), ("status", 1)],
            name="user_status_notes_idx"
        )
        print("   ✅ Created: user_status_notes_idx (user_id + status)")
        
        # Index on subject for filtering
        await db.auto_note_sessions.create_index("subject", name="subject_idx")
        print("   ✅ Created: subject_idx")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 5. CHAT_SESSIONS COLLECTION - For AI Tutor session management
    print("\n💬 chat_sessions collection:")
    try:
        # Compound index for user_id + last_updated
        await db.chat_sessions.create_index(
            [("user_id", 1), ("last_updated", -1)],
            name="user_last_updated_idx"
        )
        print("   ✅ Created: user_last_updated_idx (user_id + last_updated)")
        
        # Index on is_pinned for quick access
        await db.chat_sessions.create_index("is_pinned", name="is_pinned_idx")
        print("   ✅ Created: is_pinned_idx")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 6. CHAT_MESSAGES COLLECTION - For message history
    print("\n💭 chat_messages collection:")
    try:
        # Compound index for session_id + timestamp
        await db.chat_messages.create_index(
            [("session_id", 1), ("timestamp", 1)],
            name="session_timestamp_idx"
        )
        print("   ✅ Created: session_timestamp_idx (session_id + timestamp)")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Index Creation Complete!")
    print("=" * 60)
    
    # Verify all indexes were created
    print("\n🔍 Verification:")
    collections = ['usage_tracking', 'user_subscriptions', 'mock_tests', 
                   'auto_note_sessions', 'chat_sessions', 'chat_messages']
    
    for coll_name in collections:
        indexes = await db[coll_name].list_indexes().to_list(length=None)
        print(f"   {coll_name}: {len(indexes)} indexes")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(add_indexes())
