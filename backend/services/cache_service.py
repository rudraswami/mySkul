"""
In-Memory Caching Service
Provides fast caching for frequently accessed data
For production, replace with Redis for distributed caching
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Dict
from collections import OrderedDict
import json

logger = logging.getLogger(__name__)


class InMemoryCache:
    """
    LRU (Least Recently Used) in-memory cache
    Thread-safe async implementation
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Initialize cache
        
        Args:
            max_size: Maximum number of items in cache
            default_ttl: Default time-to-live in seconds
        """
        self._cache = OrderedDict()
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()
        self._hits = 0
        self._misses = 0
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry['expires_at'] < datetime.now(timezone.utc):
                del self._cache[key]
                self._misses += 1
                return None
            
            # Move to end (mark as recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            
            return entry['value']
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        async with self._lock:
            # Remove oldest item if cache is full
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._cache.popitem(last=False)
            
            ttl_seconds = ttl or self._default_ttl
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
            
            self._cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': datetime.now(timezone.utc)
            }
            
            # Move to end (mark as recently used)
            self._cache.move_to_end(key)
            
            return True
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def clear(self):
        """Clear all cache entries"""
        async with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        async with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": f"{hit_rate:.2f}%",
                "total_requests": total_requests
            }


# Global cache instances
_plan_config_cache = InMemoryCache(max_size=10, default_ttl=3600)  # 1 hour
_user_profile_cache = InMemoryCache(max_size=500, default_ttl=600)  # 10 minutes
_session_cache = InMemoryCache(max_size=1000, default_ttl=1800)  # 30 minutes


async def get_plan_config_cache() -> InMemoryCache:
    """Get plan configuration cache"""
    return _plan_config_cache


async def get_user_profile_cache() -> InMemoryCache:
    """Get user profile cache"""
    return _user_profile_cache


async def get_session_cache() -> InMemoryCache:
    """Get session cache"""
    return _session_cache


# Decorator for caching function results
def cache_result(cache_key_func, ttl=300):
    """
    Decorator to cache function results
    
    Usage:
        @cache_result(lambda user_id: f"user:{user_id}", ttl=600)
        async def get_user(user_id):
            # expensive operation
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_key_func(*args, **kwargs)
            
            # Try to get from cache
            cached_value = await _session_cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache HIT for {cache_key}")
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await _session_cache.set(cache_key, result, ttl=ttl)
            logger.debug(f"Cache MISS for {cache_key} - stored result")
            
            return result
        
        return wrapper
    return decorator


# HTTP Cache Headers Helper
class HTTPCacheHeaders:
    """Helper for setting HTTP cache headers"""
    
    @staticmethod
    def no_cache():
        """Headers to prevent caching"""
        return {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    
    @staticmethod
    def public_cache(max_age: int = 3600):
        """Headers for public caching (static assets)"""
        return {
            "Cache-Control": f"public, max-age={max_age}",
            "Expires": (datetime.now(timezone.utc) + timedelta(seconds=max_age)).strftime("%a, %d %b %Y %H:%M:%S GMT")
        }
    
    @staticmethod
    def private_cache(max_age: int = 600):
        """Headers for private caching (user-specific data)"""
        return {
            "Cache-Control": f"private, max-age={max_age}",
            "Expires": (datetime.now(timezone.utc) + timedelta(seconds=max_age)).strftime("%a, %d %b %Y %H:%M:%S GMT")
        }
    
    @staticmethod
    def stale_while_revalidate(max_age: int = 300, stale_time: int = 60):
        """Headers for stale-while-revalidate caching"""
        return {
            "Cache-Control": f"max-age={max_age}, stale-while-revalidate={stale_time}"
        }


# Pre-warm cache on startup
async def prewarm_caches():
    """Pre-load frequently accessed data into cache"""
    logger.info("Pre-warming caches...")
    
    # Add plan config preloading here
    # Example:
    # plan_config = await load_plan_config()
    # await _plan_config_cache.set("plan_config", plan_config)
    
    logger.info("Cache pre-warming complete")
