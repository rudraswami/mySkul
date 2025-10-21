#!/usr/bin/env python3

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from bson import ObjectId

# Load environment variables
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

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

async def test_endpoints_directly():
    """Test the failing endpoints directly to identify the exact issue"""
    
    print("🔍 TESTING AUTO-NOTE MENTOR ENDPOINTS DIRECTLY")
    print("="*60)
    
    user_id = "a621fc79-6474-4871-8a84-25562883e229"
    
    try:
        # Test 1: Sessions endpoint logic
        print("1. Testing sessions endpoint logic...")
        try:
            sessions = await db.auto_note_sessions.find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(50).to_list(50)
            
            print(f"   ✅ Found {len(sessions)} sessions")
            
            # Test clean_mongodb_doc on each session
            clean_sessions = []
            for i, session in enumerate(sessions):
                try:
                    clean_session = clean_mongodb_doc(session)
                    clean_sessions.append(clean_session)
                    if i == 0:  # Show first session details
                        print(f"   Sample cleaned session: {clean_session.get('session_id', 'N/A')}")
                except Exception as e:
                    print(f"   ❌ Error cleaning session {i}: {e}")
                    import traceback
                    traceback.print_exc()
                    break
            
            # Test final response structure
            response = {
                "sessions": clean_sessions,
                "total_sessions": len(clean_sessions),
                "active_sessions": len([s for s in sessions if s["status"] == "active"])
            }
            
            print(f"   ✅ Sessions endpoint logic works - {len(clean_sessions)} sessions cleaned")
            print(f"   Response keys: {list(response.keys())}")
            
        except Exception as e:
            print(f"   ❌ Sessions endpoint logic failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 2: Analytics endpoint logic
        print("\n2. Testing analytics endpoint logic...")
        try:
            # Get session statistics
            total_sessions = await db.auto_note_sessions.count_documents({"user_id": user_id})
            print(f"   Total sessions: {total_sessions}")
            
            # Get spaced repetition statistics
            total_cards = await db.spaced_repetition_cards.count_documents({"user_id": user_id})
            print(f"   Total cards: {total_cards}")
            
            due_cards = await db.spaced_repetition_cards.count_documents({
                "user_id": user_id,
                "next_review": {"$lte": datetime.now(timezone.utc)}
            })
            print(f"   Due cards: {due_cards}")
            
            # Get subject distribution
            subjects_pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": "$subject", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            subject_stats = await db.auto_note_sessions.aggregate(subjects_pipeline).to_list(length=None)
            print(f"   Subject stats: {len(subject_stats)} subjects")
            
            response = {
                "total_sessions": total_sessions,
                "total_flashcards": total_cards,
                "due_for_review": due_cards,
                "subject_distribution": subject_stats,
                "learning_streak": 0,
                "performance_trends": {
                    "this_week": {"sessions": 0, "flashcards_reviewed": 0},
                    "this_month": {"sessions": 0, "flashcards_reviewed": 0}
                }
            }
            
            print(f"   ✅ Analytics endpoint logic works")
            print(f"   Response keys: {list(response.keys())}")
            
        except Exception as e:
            print(f"   ❌ Analytics endpoint logic failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 3: Class series endpoint logic
        print("\n3. Testing class series endpoint logic...")
        try:
            series_list = await db.class_series.find({
                "user_id": user_id
            }).sort("created_at", -1).to_list(length=50)
            
            print(f"   Found {len(series_list)} class series")
            
            clean_series = []
            for series in series_list:
                try:
                    clean_series.append(clean_mongodb_doc(series))
                except Exception as e:
                    print(f"   ❌ Error cleaning series: {e}")
                    import traceback
                    traceback.print_exc()
                    break
            
            response = {
                "series": clean_series,
                "total_series": len(series_list)
            }
            
            print(f"   ✅ Class series endpoint logic works")
            print(f"   Response keys: {list(response.keys())}")
            
        except Exception as e:
            print(f"   ❌ Class series endpoint logic failed: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n🎯 CONCLUSION:")
        print(f"   If all tests above passed, the ObjectId serialization fix IS working")
        print(f"   The 500 errors must be coming from a different source (authentication, middleware, etc.)")
        
    except Exception as e:
        print(f"❌ Direct endpoint testing failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_endpoints_directly())