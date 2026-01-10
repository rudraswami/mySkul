"""
Database connection and initialization

OBSERVABILITY FIX (2026-01-11):
- Added get_pool_stats() for connection pool monitoring
- Added pool exhaustion detection logging
- Enhanced logging during connection issues
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Dict, Any, Optional
from .config import settings

logger = logging.getLogger(__name__)

# Global database client and database instances
_client: AsyncIOMotorClient = None
_db: AsyncIOMotorDatabase = None

# Pool configuration constants
POOL_MAX_SIZE = 200
POOL_MIN_SIZE = 10
POOL_EXHAUSTION_THRESHOLD = 0.85  # Log warning when 85% of pool is in use


def get_database() -> AsyncIOMotorDatabase:
    """
    Get database instance (dependency injection)
    """
    global _db
    if _db is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _db


def get_client() -> Optional[AsyncIOMotorClient]:
    """
    Get raw MongoDB client (for pool stats and health checks)
    
    OBSERVABILITY FIX (2026-01-11): Expose client for monitoring
    """
    global _client
    return _client


async def get_pool_stats() -> Dict[str, Any]:
    """
    Get connection pool statistics for monitoring
    
    OBSERVABILITY FIX (2026-01-11):
    - Exposes pool stats for dashboards/alerts
    - Detects pool exhaustion and logs warnings
    
    Returns:
        Dict with pool statistics and health status
    """
    global _client
    
    if _client is None:
        return {"status": "disconnected", "error": "No database client"}
    
    try:
        # Get server status
        server_status = await _client.admin.command("serverStatus")
        connections = server_status.get("connections", {})
        
        current = connections.get("current", 0)
        available = connections.get("available", 0)
        total_created = connections.get("totalCreated", 0)
        
        # Calculate utilization
        max_connections = current + available
        utilization = current / max_connections if max_connections > 0 else 0
        
        # Detect pool exhaustion
        is_exhausted = utilization > POOL_EXHAUSTION_THRESHOLD
        
        if is_exhausted:
            logger.warning(
                f"⚠️ MongoDB connection pool near exhaustion: "
                f"{current}/{max_connections} ({utilization:.1%}) - "
                f"Consider increasing maxPoolSize or reducing concurrent queries"
            )
        
        return {
            "status": "connected",
            "current_connections": current,
            "available_connections": available,
            "total_created": total_created,
            "utilization_percent": round(utilization * 100, 1),
            "pool_max_size": POOL_MAX_SIZE,
            "pool_min_size": POOL_MIN_SIZE,
            "is_near_exhaustion": is_exhausted,
            "exhaustion_threshold_percent": POOL_EXHAUSTION_THRESHOLD * 100
        }
    except Exception as e:
        logger.error(f"❌ Failed to get pool stats: {e}")
        return {"status": "error", "error": str(e)}


async def init_database():
    """
    Initialize database connection with optimized connection pool
    Called during application startup
    
    PERFORMANCE OPTIMIZED: Connection pool configuration for better scalability
    """
    global _client, _db
    
    if not settings.MONGO_URL:
        raise ValueError("MONGO_URL not configured in environment variables")
    
    print(f"[DB] Connecting to MongoDB with optimized pool settings...")
    logger.info("🔌 Initializing MongoDB connection pool...")
    
    # PERFORMANCE FIX: Optimized connection pool configuration
    _client = AsyncIOMotorClient(
        settings.MONGO_URL,
        maxPoolSize=POOL_MAX_SIZE,     # Increase pool size for better concurrency
        minPoolSize=POOL_MIN_SIZE,     # Keep connections warm
        maxIdleTimeMS=30000,           # 30s idle timeout
        serverSelectionTimeoutMS=5000, # 5s selection timeout
        connectTimeoutMS=10000,        # 10s connect timeout
        socketTimeoutMS=20000,         # 20s socket timeout
        retryWrites=True,              # Retry failed writes
        retryReads=True,               # Retry failed reads
        compressors='zstd,snappy,zlib' # Enable compression for better network performance
    )
    _db = _client[settings.DB_NAME]

    # Test connection
    try:
        await _client.admin.command('ping')
        print(f"[OK] Connected to MongoDB database: {settings.DB_NAME}")
        print(f"[OK] Connection pool: maxPoolSize={POOL_MAX_SIZE}, minPoolSize={POOL_MIN_SIZE}")
        logger.info(f"✅ MongoDB connected: pool_max={POOL_MAX_SIZE}, pool_min={POOL_MIN_SIZE}")
        
        # Log initial pool stats
        pool_stats = await get_pool_stats()
        logger.info(f"📊 Initial pool stats: {pool_stats.get('current_connections', 0)} connections")
    except Exception as e:
        print(f"[ERROR] Failed to connect to MongoDB: {e}")
        logger.error(f"❌ MongoDB connection failed: {e}")
        raise
    
    return _db


async def close_database():
    """
    Close database connection
    Called during application shutdown
    """
    global _client
    if _client:
        _client.close()
        print("[DB] MongoDB connection closed")
        logger.info("🔌 MongoDB connection closed")


# Export for convenience
__all__ = ["get_database", "get_client", "get_pool_stats", "init_database", "close_database"]
