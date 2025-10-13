"""
OAuth state management using MongoDB
Provides a reliable state store for OAuth flows in distributed environments
"""
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import secrets

class OAuthStateStore:
    """Store and verify OAuth state tokens in MongoDB"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.oauth_states
    
    async def create_state(self) -> str:
        """Create and store a new OAuth state token"""
        state = secrets.token_urlsafe(32)
        expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
        
        await self.collection.insert_one({
            "state": state,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": expiry.isoformat(),
            "used": False
        })
        
        return state
    
    async def verify_state(self, state: str) -> bool:
        """Verify and consume an OAuth state token"""
        state_doc = await self.collection.find_one({
            "state": state,
            "used": False
        })
        
        if not state_doc:
            return False
        
        # Check if expired
        expires_at = datetime.fromisoformat(state_doc["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            # Clean up expired state
            await self.collection.delete_one({"state": state})
            return False
        
        # Mark as used
        await self.collection.update_one(
            {"state": state},
            {"$set": {"used": True}}
        )
        
        return True
    
    async def cleanup_expired(self):
        """Clean up expired state tokens"""
        now = datetime.now(timezone.utc).isoformat()
        await self.collection.delete_many({
            "expires_at": {"$lt": now}
        })
