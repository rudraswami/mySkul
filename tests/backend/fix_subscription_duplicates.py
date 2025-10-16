#!/usr/bin/env python3
"""Fix duplicate user_id entries in user_subscriptions collection"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
from dotenv import load_dotenv
from collections import defaultdict

# Load environment variables
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

async def fix_duplicates():
    """Find and fix duplicate user_id entries"""
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    
    print("=" * 60)
    print("Fixing Duplicate user_id Entries")
    print("=" * 60)
    
    # Find all subscriptions
    subscriptions = await db.user_subscriptions.find({}).to_list(length=None)
    
    # Group by user_id
    user_groups = defaultdict(list)
    for sub in subscriptions:
        user_groups[sub['user_id']].append(sub)
    
    # Find duplicates
    duplicates = {user_id: subs for user_id, subs in user_groups.items() if len(subs) > 1}
    
    print(f"\n📊 Total subscriptions: {len(subscriptions)}")
    print(f"📊 Unique users: {len(user_groups)}")
    print(f"⚠️  Duplicate users: {len(duplicates)}")
    
    if duplicates:
        print("\n🔧 Fixing duplicates:")
        for user_id, subs in duplicates.items():
            print(f"\n   User: {user_id}")
            print(f"   Found {len(subs)} entries")
            
            # Keep the most recent one (or the one with highest tier)
            # Sort by created_at or subscription_tier
            sorted_subs = sorted(subs, key=lambda x: (
                x.get('subscription_tier') != 'FREE',  # Paid subscriptions first
                x.get('created_at', ''),  # Then by creation date
            ), reverse=True)
            
            keep = sorted_subs[0]
            remove = sorted_subs[1:]
            
            print(f"   Keeping: {keep.get('subscription_tier', 'UNKNOWN')} (created: {keep.get('created_at', 'N/A')})")
            
            # Remove duplicates
            for sub in remove:
                await db.user_subscriptions.delete_one({'_id': sub['_id']})
                print(f"   Removed: {sub.get('subscription_tier', 'UNKNOWN')} (_id: {sub['_id']})")
        
        print(f"\n✅ Cleaned up {sum(len(subs)-1 for subs in duplicates.values())} duplicate entries")
    else:
        print("\n✅ No duplicates found!")
    
    # Now try to create the unique index
    print("\n📌 Creating unique index on user_id:")
    try:
        await db.user_subscriptions.create_index("user_id", unique=True, name="user_id_unique_idx")
        print("   ✅ Created: user_id_unique_idx (unique)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Add other indexes
    try:
        await db.user_subscriptions.create_index("subscription_tier", name="subscription_tier_idx")
        print("   ✅ Created: subscription_tier_idx")
        
        await db.user_subscriptions.create_index("status", name="status_idx")
        print("   ✅ Created: status_idx")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_duplicates())
