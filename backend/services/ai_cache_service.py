"""
AI Response Caching Service
Caches AI responses based on message hash and user context to reduce latency
"""
import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class AICacheService:
    """Service for caching AI responses"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.cache_collection = db.ai_response_cache
        self.cache_ttl_hours = 24  # Cache responses for 24 hours
        
    async def initialize(self):
        """Initialize cache collection with indexes"""
        try:
            # Index on cache key for fast lookup
            await self.cache_collection.create_index("cache_key", unique=True)
            
            # TTL index to auto-expire old cache entries
            await self.cache_collection.create_index(
                "expires_at",
                expireAfterSeconds=0
            )
            
            # Index on created_at for analytics
            await self.cache_collection.create_index("created_at")
            
            logger.info("AI cache indexes initialized")
        except Exception as e:
            logger.error(f"Failed to initialize AI cache indexes: {e}")
    
    def _generate_cache_key(
        self, 
        message: str, 
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a unique cache key based on message content and context
        
        Args:
            message: User's question/prompt
            user_id: User ID (for personalization)
            context: Additional context (subject, exam_type, mode, etc.)
        
        Returns:
            Unique cache key (SHA256 hash)
        """
        # Normalize message (lowercase, strip whitespace)
        normalized_message = message.lower().strip()
        
        # Include relevant context
        cache_data = {
            "message": normalized_message,
            "user_id": user_id,
            "subject": context.get("subject") if context else None,
            "exam_type": context.get("exam_type") if context else None,
            "mode": context.get("mode") if context else None,
        }
        
        # Generate hash
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_string.encode()).hexdigest()
    
    async def get_cached_response(
        self,
        message: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached AI response if available
        
        Returns:
            Cached response dict or None if not found
        """
        try:
            cache_key = self._generate_cache_key(message, user_id, context)
            
            cached = await self.cache_collection.find_one({
                "cache_key": cache_key,
                "expires_at": {"$gt": datetime.now(timezone.utc)}
            })
            
            if cached:
                logger.info(f"Cache HIT for key: {cache_key[:16]}...")
                # Update hit count
                await self.cache_collection.update_one(
                    {"cache_key": cache_key},
                    {
                        "$inc": {"hit_count": 1},
                        "$set": {"last_accessed": datetime.now(timezone.utc)}
                    }
                )
                return cached.get("response")
            
            logger.info(f"Cache MISS for key: {cache_key[:16]}...")
            return None
            
        except Exception as e:
            logger.error(f"Cache lookup error: {e}")
            return None
    
    async def cache_response(
        self,
        message: str,
        user_id: str,
        response: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        ttl_hours: Optional[int] = None
    ) -> bool:
        """
        Cache an AI response
        
        Args:
            message: Original user message
            user_id: User ID
            response: AI response to cache
            context: Additional context
            ttl_hours: Time to live in hours (default: 24)
        
        Returns:
            True if cached successfully
        """
        try:
            cache_key = self._generate_cache_key(message, user_id, context)
            ttl = ttl_hours or self.cache_ttl_hours
            
            cache_entry = {
                "cache_key": cache_key,
                "message": message,
                "user_id": user_id,
                "context": context or {},
                "response": response,
                "created_at": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc) + timedelta(hours=ttl),
                "hit_count": 0,
                "last_accessed": datetime.now(timezone.utc)
            }
            
            # Upsert (update if exists, insert if not)
            await self.cache_collection.update_one(
                {"cache_key": cache_key},
                {"$set": cache_entry},
                upsert=True
            )
            
            logger.info(f"Cached response for key: {cache_key[:16]}...")
            return True
            
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
            return False
    
    async def invalidate_user_cache(self, user_id: str) -> int:
        """
        Invalidate all cached responses for a user
        
        Returns:
            Number of entries deleted
        """
        try:
            result = await self.cache_collection.delete_many({"user_id": user_id})
            logger.info(f"Invalidated {result.deleted_count} cache entries for user {user_id}")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return 0
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            total_entries = await self.cache_collection.count_documents({})
            
            # Total hits
            pipeline = [
                {"$group": {
                    "_id": None,
                    "total_hits": {"$sum": "$hit_count"},
                    "avg_hits": {"$avg": "$hit_count"}
                }}
            ]
            stats = await self.cache_collection.aggregate(pipeline).to_list(1)
            
            return {
                "total_entries": total_entries,
                "total_hits": stats[0]["total_hits"] if stats else 0,
                "avg_hits_per_entry": stats[0]["avg_hits"] if stats else 0,
                "hit_rate": "N/A"  # Would need to track misses to calculate
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {}


# Mentor Tips Pre-generation Service
class MentorTipsCache:
    """Pre-generated mentor tips for common topics"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.tips_collection = db.mentor_tips_cache
        
    async def initialize(self):
        """Initialize with indexes"""
        try:
            await self.tips_collection.create_index(
                [("subject", 1), ("topic", 1)],
                unique=True
            )
            await self.tips_collection.create_index("popularity")
            logger.info("Mentor tips cache initialized")
        except Exception as e:
            logger.error(f"Failed to initialize mentor tips cache: {e}")
    
    async def get_tip(self, subject: str, topic: str) -> Optional[str]:
        """Get pre-generated tip"""
        try:
            tip = await self.tips_collection.find_one({
                "subject": subject.lower(),
                "topic": topic.lower()
            })
            
            if tip:
                # Update access count
                await self.tips_collection.update_one(
                    {"_id": tip["_id"]},
                    {
                        "$inc": {"access_count": 1},
                        "$set": {"last_accessed": datetime.now(timezone.utc)}
                    }
                )
                return tip.get("tip_content")
            
            return None
        except Exception as e:
            logger.error(f"Mentor tip lookup error: {e}")
            return None
    
    async def store_tip(
        self,
        subject: str,
        topic: str,
        tip_content: str,
        popularity: int = 1
    ) -> bool:
        """Store a pre-generated tip"""
        try:
            await self.tips_collection.update_one(
                {
                    "subject": subject.lower(),
                    "topic": topic.lower()
                },
                {
                    "$set": {
                        "subject": subject.lower(),
                        "topic": topic.lower(),
                        "tip_content": tip_content,
                        "popularity": popularity,
                        "created_at": datetime.now(timezone.utc),
                        "last_accessed": datetime.now(timezone.utc),
                        "access_count": 0
                    }
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Mentor tip storage error: {e}")
            return False
    
    async def get_popular_tips(self, limit: int = 20) -> list:
        """Get most popular tips for pre-generation"""
        try:
            tips = await self.tips_collection.find().sort("popularity", -1).limit(limit).to_list(limit)
            return tips
        except Exception as e:
            logger.error(f"Popular tips query error: {e}")
            return []
