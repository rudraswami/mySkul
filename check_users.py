#!/usr/bin/env python3

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def check_users():
    try:
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ.get('DB_NAME', 'dhruv_ai')
        
        print(f"Connecting to MongoDB: {mongo_url}")
        print(f"Database: {db_name}")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Check if users collection exists and has data
        user_count = await db.users.count_documents({})
        print(f"Total users in database: {user_count}")
        
        if user_count > 0:
            print("\nExisting users:")
            users = await db.users.find({}, {"email": 1, "full_name": 1, "exam_type": 1, "created_at": 1}).limit(5).to_list(5)
            for user in users:
                print(f"- {user.get('email', 'No email')} ({user.get('full_name', 'No name')}) - {user.get('exam_type', 'No exam type')}")
        else:
            print("No users found in database")
            
        # Check collections
        collections = await db.list_collection_names()
        print(f"\nAvailable collections: {collections}")
        
        client.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_users())