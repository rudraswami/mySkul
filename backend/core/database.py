"""
Database connection and initialization
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .config import settings

# Global database client and database instances
_client: AsyncIOMotorClient = None
_db: AsyncIOMotorDatabase = None


def get_database() -> AsyncIOMotorDatabase:
    """
    Get database instance (dependency injection)
    """
    global _db
    if _db is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _db


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
    
    # PERFORMANCE FIX: Optimized connection pool configuration
    _client = AsyncIOMotorClient(
        settings.MONGO_URL,
        maxPoolSize=200,              # Increase pool size for better concurrency
        minPoolSize=10,               # Keep connections warm
        maxIdleTimeMS=30000,          # 30s idle timeout
        serverSelectionTimeoutMS=5000, # 5s selection timeout
        connectTimeoutMS=10000,       # 10s connect timeout
        socketTimeoutMS=20000,        # 20s socket timeout
        retryWrites=True,             # Retry failed writes
        retryReads=True,              # Retry failed reads
        compressors='zstd,snappy,zlib' # Enable compression for better network performance
    )
    _db = _client[settings.DB_NAME]

    # Test connection
    try:
        await _client.admin.command('ping')
        print(f"[OK] Connected to MongoDB database: {settings.DB_NAME}")
        print(f"[OK] Connection pool: maxPoolSize=200, minPoolSize=10")
    except Exception as e:
        print(f"[ERROR] Failed to connect to MongoDB: {e}")
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


# Export for convenience
__all__ = ["get_database", "init_database", "close_database"]
