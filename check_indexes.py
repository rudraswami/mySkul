#!/usr/bin/env python3
"""Check MongoDB indexes for performance optimization"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

async def check_indexes():
    """Check existing indexes on critical collections"""
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    
    collections = [
        'usage_tracking',
        'user_subscriptions', 
        'mock_tests',
        'auto_note_sessions',
        'chat_sessions',
        'chat_messages'
    ]
    
    print("=" * 60)
    print("MongoDB Index Analysis")
    print("=" * 60)
    
    for coll_name in collections:
        try:
            indexes = await db[coll_name].list_indexes().to_list(length=None)
            print(f"\n📋 Collection: {coll_name}")
            print(f"   Total indexes: {len(indexes)}")
            
            for idx in indexes:
                key_str = ', '.join([f"{k}: {v}" for k, v in idx.get('key', {}).items()])
                print(f"   ✓ {idx['name']}")
                print(f"     Keys: {key_str}")
                if 'unique' in idx and idx['unique']:
                    print(f"     Unique: Yes")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    client.close()

if __name__ == "__main__":
    asyncio.run(check_indexes())
