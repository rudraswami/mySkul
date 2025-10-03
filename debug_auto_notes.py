#!/usr/bin/env python3

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def debug_auto_notes():
    """Debug Auto-Note Mentor database issues"""
    
    print("🔍 DEBUGGING AUTO-NOTE MENTOR DATABASE ISSUES")
    print("="*60)
    
    try:
        # Test database connection
        print("1. Testing database connection...")
        server_info = await client.server_info()
        print(f"   ✅ Connected to MongoDB: {server_info['version']}")
        
        # Check if auto_note_sessions collection exists
        print("\n2. Checking auto_note_sessions collection...")
        collections = await db.list_collection_names()
        print(f"   Available collections: {collections}")
        
        if 'auto_note_sessions' in collections:
            print("   ✅ auto_note_sessions collection exists")
            
            # Count documents
            count = await db.auto_note_sessions.count_documents({})
            print(f"   Total documents in auto_note_sessions: {count}")
            
            # Get sample documents
            if count > 0:
                print("\n3. Sample documents from auto_note_sessions:")
                sample_docs = await db.auto_note_sessions.find({}).limit(3).to_list(3)
                for i, doc in enumerate(sample_docs):
                    print(f"   Document {i+1}:")
                    print(f"     session_id: {doc.get('session_id', 'N/A')}")
                    print(f"     user_id: {doc.get('user_id', 'N/A')}")
                    print(f"     subject: {doc.get('subject', 'N/A')}")
                    print(f"     created_at: {doc.get('created_at', 'N/A')} (type: {type(doc.get('created_at', 'N/A'))})")
                    print(f"     _id: {doc.get('_id', 'N/A')} (type: {type(doc.get('_id', 'N/A'))})")
                    print()
            else:
                print("   ⚠️  No documents found in auto_note_sessions")
        else:
            print("   ❌ auto_note_sessions collection does not exist")
        
        # Test the specific user
        print("\n4. Testing specific user: test@dhruvai.com")
        user_id = "a621fc79-6474-4871-8a84-255628883e229"  # From the test logs
        print(f"   Looking for sessions with user_id: {user_id}")
        
        user_sessions = await db.auto_note_sessions.find({"user_id": user_id}).to_list(10)
        print(f"   Found {len(user_sessions)} sessions for this user")
        
        if user_sessions:
            for i, session in enumerate(user_sessions):
                print(f"   Session {i+1}:")
                print(f"     session_id: {session.get('session_id', 'N/A')}")
                print(f"     subject: {session.get('subject', 'N/A')}")
                print(f"     status: {session.get('status', 'N/A')}")
                print(f"     created_at: {session.get('created_at', 'N/A')}")
        
        # Test clean_mongodb_doc function
        print("\n5. Testing clean_mongodb_doc function...")
        if user_sessions:
            from bson import ObjectId
            
            def clean_mongodb_doc(doc: dict) -> dict:
                """Remove ObjectId and serialize datetime objects for JSON response"""
                if not doc:
                    return doc
                    
                clean_doc = {}
                for k, v in doc.items():
                    if k == '_id':
                        continue
                    elif isinstance(v, ObjectId):
                        clean_doc[k] = str(v)  # Convert ObjectId to string
                    elif isinstance(v, datetime):
                        try:
                            clean_doc[k] = v.isoformat()
                        except Exception as e:
                            print(f"     ⚠️  Datetime serialization error for {k}: {e}")
                            clean_doc[k] = str(v)  # Fallback to string conversion
                    elif isinstance(v, list):
                        clean_doc[k] = [
                            clean_mongodb_doc(item) if isinstance(item, dict) 
                            else str(item) if isinstance(item, ObjectId)
                            else item.isoformat() if isinstance(item, datetime)
                            else item for item in v
                        ]
                    elif isinstance(v, dict):
                        clean_doc[k] = clean_mongodb_doc(v)
                    else:
                        clean_doc[k] = v
                return clean_doc
            
            try:
                test_session = user_sessions[0]
                print(f"   Testing clean_mongodb_doc on session: {test_session.get('session_id', 'N/A')}")
                cleaned = clean_mongodb_doc(test_session)
                print(f"   ✅ clean_mongodb_doc worked successfully")
                print(f"   Cleaned keys: {list(cleaned.keys())}")
                print(f"   Sample cleaned data: {str(cleaned)[:200]}...")
            except Exception as e:
                print(f"   ❌ clean_mongodb_doc failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Test other collections
        print("\n6. Checking other related collections...")
        for collection_name in ['class_series', 'spaced_repetition_cards']:
            if collection_name in collections:
                count = await db[collection_name].count_documents({})
                print(f"   {collection_name}: {count} documents")
            else:
                print(f"   {collection_name}: collection does not exist")
        
    except Exception as e:
        print(f"❌ Database debug failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(debug_auto_notes())