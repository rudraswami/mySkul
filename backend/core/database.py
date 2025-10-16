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
    Initialize database connection
    Called during application startup
    """
    global _client, _db
    
    if not settings.MONGO_URL:
        raise ValueError("MONGO_URL not configured in environment variables")
    
    print(f"🔌 Connecting to MongoDB...")
    _client = AsyncIOMotorClient(settings.MONGO_URL)
    _db = _client[settings.DB_NAME]
    
    # Test connection
    try:
        await _client.admin.command('ping')
        print(f"✅ Connected to MongoDB database: {settings.DB_NAME}")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
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
        print("🔌 MongoDB connection closed")


# Export for convenience
__all__ = ["get_database", "init_database", "close_database"]
