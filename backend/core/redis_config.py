"""
Redis Configuration for Production Caching and Rate Limiting
"""
import os
from typing import Optional
import redis
from redis import Redis
import logging

logger = logging.getLogger(__name__)


class RedisConfig:
    """Redis connection configuration and management"""
    
    _instance: Optional[Redis] = None
    _rate_limit_instance: Optional[Redis] = None
    
    @classmethod
    def get_redis_client(cls, db: int = 0) -> Optional[Redis]:
        """
        Get Redis client for caching
        
        Args:
            db: Redis database number (default: 0)
        
        Returns:
            Redis client or None if Redis not configured
        """
        if cls._instance is None:
            redis_url = os.getenv("REDIS_URL", "")
            
            if not redis_url:
                logger.warning("REDIS_URL not configured - using memory-only caching")
                return None
            
            try:
                cls._instance = redis.from_url(
                    redis_url,
                    db=db,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                
                # Test connection
                cls._instance.ping()
                logger.info(f"✅ Redis connected successfully (db={db})")
                
            except Exception as e:
                logger.error(f"❌ Redis connection failed: {e}")
                logger.warning("Falling back to memory-only caching")
                cls._instance = None
        
        return cls._instance
    
    @classmethod
    def get_rate_limit_client(cls) -> Optional[Redis]:
        """
        Get Redis client for rate limiting
        
        Returns:
            Redis client or None if Redis not configured
        """
        if cls._rate_limit_instance is None:
            redis_url = os.getenv("RATE_LIMIT_STORAGE_URI", "")
            
            if not redis_url or redis_url == "memory://":
                logger.warning("Rate limiting using memory storage (not recommended for production)")
                return None
            
            try:
                cls._rate_limit_instance = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                
                # Test connection
                cls._rate_limit_instance.ping()
                logger.info("✅ Redis rate limiting connected successfully")
                
            except Exception as e:
                logger.error(f"❌ Redis rate limiting connection failed: {e}")
                cls._rate_limit_instance = None
        
        return cls._rate_limit_instance
    
    @classmethod
    def close_connections(cls):
        """Close all Redis connections"""
        if cls._instance:
            cls._instance.close()
            cls._instance = None
            logger.info("Redis cache connection closed")
        
        if cls._rate_limit_instance:
            cls._rate_limit_instance.close()
            cls._rate_limit_instance = None
            logger.info("Redis rate limit connection closed")


# Convenience functions
def get_redis() -> Optional[Redis]:
    """Get Redis client for caching"""
    return RedisConfig.get_redis_client()


def get_rate_limit_redis() -> Optional[Redis]:
    """Get Redis client for rate limiting"""
    return RedisConfig.get_rate_limit_client()


def close_redis():
    """Close all Redis connections"""
    RedisConfig.close_connections()

