"""
Clear Old Notifications Script
==================================

Run this to clear all old notification data and start fresh.
This is useful when resetting the notification system.

Usage:
    python scripts/clear_old_notifications.py
"""

import asyncio
import os
import sys

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Load .env file
from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def clear_notifications():
    """Clear all notification-related data."""
    
    # Get MongoDB connection - use same env vars as main app
    mongo_uri = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'dhruv_ai')
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    print(f"[INFO] Connected to database: {db_name}")
    
    print("[CLEAR] Clearing old notification data...")
    print("=" * 50)
    
    # 1. Clear user notifications
    result = await db.user_notifications.delete_many({})
    print(f"[OK] Deleted {result.deleted_count} notifications")
    
    # 2. Clear notification outcomes (learning data)
    result = await db.notification_outcomes.delete_many({})
    print(f"[OK] Deleted {result.deleted_count} notification outcomes")
    
    # 3. Clear mentor events
    result = await db.mentor_events.delete_many({})
    print(f"[OK] Deleted {result.deleted_count} mentor events")
    
    # 4. Clear mentor decisions (optional - for debugging)
    result = await db.mentor_decisions.delete_many({})
    print(f"[OK] Deleted {result.deleted_count} mentor decisions")
    
    # 5. Clear mentor learning profiles (optional - reset personalization)
    result = await db.mentor_learning_profiles.delete_many({})
    print(f"[OK] Deleted {result.deleted_count} learning profiles")
    
    print("=" * 50)
    print("[DONE] All notification data cleared!")
    print("")
    print("The Mentor Companion will now start fresh and learn")
    print("from your interactions over time.")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(clear_notifications())

