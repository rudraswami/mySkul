#!/usr/bin/env python3
"""
Create a test user and generate JWT token for testing
"""
import asyncio
import sys
import os
import uuid
from datetime import datetime, timezone, timedelta
import jwt

# Add backend to path
sys.path.insert(0, '/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings

async def create_test_user():
    """Create a test user in MongoDB"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.DB_NAME]
    
    # Test user data
    user_id = str(uuid.uuid4())
    email = "test_mock_tests@example.com"
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": email})
    if existing_user:
        print(f"✅ Test user already exists: {email}")
        user_id = existing_user['user_id']
    else:
        # Create new user
        user_doc = {
            "user_id": user_id,
            "email": email,
            "full_name": "Test User Mock Tests",
            "google_id": f"test_google_id_{user_id}",
            "profile_picture": "https://example.com/avatar.jpg",
            "subscription_tier": "ACHIEVER",  # Give full access
            "subscription_status": "active",
            "subscription_start_date": datetime.now(timezone.utc).isoformat(),
            "subscription_end_date": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_login": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "preferences": {},
            "usage_stats": {
                "ai_mentor": {"used": 0, "limit": 999999},
                "mock_tests": {"used": 0, "limit": 999999},
                "auto_notes": {"used": 0, "limit": 999999}
            }
        }
        
        await db.users.insert_one(user_doc)
        print(f"✅ Created test user: {email}")
        print(f"   User ID: {user_id}")
        print(f"   Subscription: ACHIEVER (unlimited access)")
    
    # Generate JWT token
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(days=1)
    }
    
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    
    print(f"\n🔑 JWT Token:")
    print(token)
    print(f"\n📋 Use this in Authorization header:")
    print(f"Authorization: Bearer {token}")
    
    # Close connection
    client.close()
    
    return user_id, token

if __name__ == "__main__":
    user_id, token = asyncio.run(create_test_user())
