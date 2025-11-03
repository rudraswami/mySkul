"""
Migration script to set profile_completed=True for existing users
who already have profile fields (grade, target_year)
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone


async def migrate_profile_completed():
    """Set profile_completed=True for users with profile data"""
    
    # Get database connection
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.getenv('DATABASE_NAME', 'dhruv_ai_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"🔌 Connected to MongoDB: {db_name}")
    print(f"📊 Starting migration...")
    
    # Find users who:
    # 1. Have profile_completed = False OR profile_completed field doesn't exist
    # 2. Have profile fields: target_year, exam_type
    query = {
        "$or": [
            {"profile_completed": False},
            {"profile_completed": {"$exists": False}}
        ],
        "target_year": {"$exists": True, "$ne": None},
        "exam_type": {"$exists": True, "$ne": None}
    }
    
    users_to_update = await db.users.find(query).to_list(length=None)
    
    print(f"📝 Found {len(users_to_update)} users with profile data but profile_completed=False")
    
    if len(users_to_update) == 0:
        print("✅ No users need migration")
        return
    
    # Update users
    updated_count = 0
    for user in users_to_update:
        email = user.get('email', 'unknown')
        user_id = user.get('user_id', 'unknown')
        
        result = await db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "profile_completed": True,
                    "profile_updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        if result.modified_count > 0:
            updated_count += 1
            print(f"  ✅ Updated user: {email} (ID: {user_id[:8]}...)")
    
    print(f"\n✅ Migration complete!")
    print(f"📊 Updated {updated_count} users")
    
    client.close()


if __name__ == "__main__":
    print("=" * 60)
    print("MIGRATION: Set profile_completed=True for existing users")
    print("=" * 60)
    asyncio.run(migrate_profile_completed())
