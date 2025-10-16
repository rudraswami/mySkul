"""
Add indexes for Gmail OAuth authentication fields
Run this script to add necessary indexes for google_id, session_token, and email
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def add_gmail_auth_indexes():
    """Add indexes for Gmail OAuth fields"""
    
    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.dhruv_ai
    
    print("🔍 Adding Gmail Auth indexes...")
    
    try:
        # Index for google_id (unique, sparse for legacy users)
        await db.users.create_index("google_id", unique=True, sparse=True)
        print("✅ Created index: google_id (unique, sparse)")
        
        # Index for session_token (for session lookup)
        await db.users.create_index("session_token", sparse=True)
        print("✅ Created index: session_token (sparse)")
        
        # Compound index for session validation
        await db.users.create_index([
            ("session_token", 1),
            ("session_expiry", 1)
        ])
        print("✅ Created compound index: session_token + session_expiry")
        
        # Index for email (ensure it exists)
        await db.users.create_index("email", unique=True)
        print("✅ Created/verified index: email (unique)")
        
        # Index for profile_completed (for routing logic)
        await db.users.create_index("profile_completed")
        print("✅ Created index: profile_completed")
        
        # Index for auth_provider (for analytics)
        await db.users.create_index("auth_provider")
        print("✅ Created index: auth_provider")
        
        print("\n✅ All Gmail Auth indexes created successfully!")
        
        # List all indexes
        print("\n📋 Current indexes on users collection:")
        indexes = await db.users.list_indexes().to_list(length=None)
        for idx in indexes:
            print(f"  - {idx['name']}: {idx.get('key', {})}")
            
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_gmail_auth_indexes())
