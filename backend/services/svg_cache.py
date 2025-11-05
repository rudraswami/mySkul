"""
Simple file-based cache for SVG sketches
Lightweight alternative to Redis for MVP
"""
import os
import json
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class SVGCache:
    """
    Simple file-based cache for SVG sketches
    Stores SVG in /tmp/svg_cache/ with TTL
    """
    
    def __init__(self, cache_dir: str = "/tmp/svg_cache", ttl_hours: int = 24):
        """
        Initialize cache
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time to live in hours (default 24h)
        """
        self.cache_dir = Path(cache_dir)
        self.ttl_hours = ttl_hours
        self.ttl_seconds = ttl_hours * 3600
        
        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📦 SVG Cache initialized: {cache_dir} (TTL: {ttl_hours}h)")
    
    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get SVG from cache
        
        Args:
            cache_key: Cache key (MD5 hash)
            
        Returns:
            Dict with SVG data or None if not found/expired
        """
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            if not cache_file.exists():
                logger.debug(f"❌ Cache miss: {cache_key}")
                return None
            
            # Read cache file
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            # Check TTL
            cached_time = datetime.fromisoformat(cached_data['cached_at'])
            age_seconds = (datetime.now(timezone.utc) - cached_time).total_seconds()
            
            if age_seconds > self.ttl_seconds:
                logger.debug(f"⏰ Cache expired: {cache_key} (age: {age_seconds/3600:.1f}h)")
                # Delete expired cache
                cache_file.unlink()
                return None
            
            logger.info(f"✅ Cache hit: {cache_key} (age: {age_seconds/60:.1f}min)")
            return cached_data['svg_data']
            
        except Exception as e:
            logger.error(f"❌ Cache read error: {e}")
            return None
    
    def set(self, cache_key: str, svg_data: Dict[str, Any]):
        """
        Store SVG in cache
        
        Args:
            cache_key: Cache key (MD5 hash)
            svg_data: SVG data to cache
        """
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            # Add timestamp
            cache_entry = {
                'cached_at': datetime.now(timezone.utc).isoformat(),
                'cache_key': cache_key,
                'svg_data': svg_data
            }
            
            # Write to file
            with open(cache_file, 'w') as f:
                json.dump(cache_entry, f, indent=2)
            
            logger.info(f"💾 Cached SVG: {cache_key} ({svg_data.get('size_kb', 0):.1f}KB)")
            
        except Exception as e:
            logger.error(f"❌ Cache write error: {e}")
    
    def clear_expired(self):
        """Clear all expired cache entries"""
        try:
            expired_count = 0
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r') as f:
                        cached_data = json.load(f)
                    
                    cached_time = datetime.fromisoformat(cached_data['cached_at'])
                    age_seconds = (datetime.now(timezone.utc) - cached_time).total_seconds()
                    
                    if age_seconds > self.ttl_seconds:
                        cache_file.unlink()
                        expired_count += 1
                        
                except Exception:
                    # Delete corrupted cache files
                    cache_file.unlink()
                    expired_count += 1
            
            if expired_count > 0:
                logger.info(f"🗑️ Cleared {expired_count} expired cache entries")
            
        except Exception as e:
            logger.error(f"❌ Cache cleanup error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            valid_count = 0
            expired_count = 0
            
            for cache_file in cache_files:
                try:
                    with open(cache_file, 'r') as f:
                        cached_data = json.load(f)
                    
                    cached_time = datetime.fromisoformat(cached_data['cached_at'])
                    age_seconds = (datetime.now(timezone.utc) - cached_time).total_seconds()
                    
                    if age_seconds > self.ttl_seconds:
                        expired_count += 1
                    else:
                        valid_count += 1
                        
                except Exception:
                    expired_count += 1
            
            return {
                'total_entries': len(cache_files),
                'valid_entries': valid_count,
                'expired_entries': expired_count,
                'total_size_kb': total_size / 1024,
                'cache_dir': str(self.cache_dir),
                'ttl_hours': self.ttl_hours
            }
            
        except Exception as e:
            logger.error(f"❌ Cache stats error: {e}")
            return {}


# Test
def test_cache():
    """Test cache functionality"""
    print("\n" + "="*60)
    print("SVG CACHE TEST")
    print("="*60)
    
    cache = SVGCache(ttl_hours=1)
    
    # Test data
    test_svg = {
        'svg_code': '<svg>test</svg>',
        'size_kb': 1.5,
        'tier': 2
    }
    
    # Set cache
    cache.set('test_key_123', test_svg)
    print("\n✅ Cache set")
    
    # Get cache
    result = cache.get('test_key_123')
    if result:
        print(f"✅ Cache retrieved: {result['size_kb']}KB")
    else:
        print("❌ Cache miss")
    
    # Get stats
    stats = cache.get_stats()
    print(f"\n📊 Cache Stats:")
    print(f"   Total entries: {stats['total_entries']}")
    print(f"   Valid entries: {stats['valid_entries']}")
    print(f"   Total size: {stats['total_size_kb']:.1f}KB")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    test_cache()
