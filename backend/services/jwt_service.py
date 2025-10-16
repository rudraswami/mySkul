"""
JWT Token Service - Access and Refresh Token Management
Implements secure token generation, validation, and rotation
"""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
import jwt
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.config import settings


class JWTService:
    """
    Handles JWT access and refresh tokens with rotation and revocation
    """
    
    # Token expiration times
    ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Short-lived
    REFRESH_TOKEN_EXPIRE_DAYS = 7     # Long-lived
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.secret = settings.JWT_SECRET
        self.algorithm = settings.JWT_ALGORITHM
    
    def create_access_token(self, user_id: str, email: str) -> str:
        """
        Create short-lived access token (15 minutes)
        Used for API authentication
        """
        expires_delta = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.now(timezone.utc) + expires_delta
        
        payload = {
            "sub": user_id,  # Subject (user ID)
            "email": email,
            "type": "access",
            "exp": expire,
            "iat": datetime.now(timezone.utc),  # Issued at
        }
        
        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        return token
    
    async def create_refresh_token(self, user_id: str) -> str:
        """
        Create long-lived refresh token (7 days)
        Stored in database for revocation capability
        """
        expires_delta = timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        expire = datetime.now(timezone.utc) + expires_delta
        
        # Generate unique token ID for tracking
        token_id = secrets.token_urlsafe(32)
        
        payload = {
            "sub": user_id,
            "type": "refresh",
            "jti": token_id,  # JWT ID for revocation
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
        
        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        
        # Store refresh token in database
        await self.db.refresh_tokens.insert_one({
            "token_id": token_id,
            "user_id": user_id,
            "expires_at": expire.isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "revoked": False,
            "used": False
        })
        
        return token
    
    async def create_token_pair(self, user_id: str, email: str) -> Dict[str, str]:
        """
        Create both access and refresh tokens
        Returns: {"access_token": "...", "refresh_token": "...", "token_type": "bearer"}
        """
        access_token = self.create_access_token(user_id, email)
        refresh_token = await self.create_refresh_token(user_id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds
        }
    
    def verify_access_token(self, token: str) -> Optional[Dict]:
        """
        Verify and decode access token
        Returns payload if valid, None if invalid/expired
        """
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm]
            )
            
            # Verify token type
            if payload.get("type") != "access":
                return None
            
            return payload
        
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    async def verify_refresh_token(self, token: str) -> Optional[Dict]:
        """
        Verify refresh token and check if revoked
        Returns payload if valid and not revoked, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm]
            )
            
            # Verify token type
            if payload.get("type") != "refresh":
                return None
            
            token_id = payload.get("jti")
            if not token_id:
                return None
            
            # Check if token exists and is not revoked
            token_doc = await self.db.refresh_tokens.find_one({
                "token_id": token_id,
                "revoked": False,
                "used": False
            })
            
            if not token_doc:
                return None
            
            # Check expiry from database
            expires_at = datetime.fromisoformat(token_doc["expires_at"])
            if datetime.now(timezone.utc) > expires_at:
                return None
            
            return payload
        
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    async def rotate_refresh_token(self, old_token: str, user_id: str) -> Optional[Tuple[str, str]]:
        """
        Rotate refresh token (revoke old, create new)
        Returns: (new_access_token, new_refresh_token) or None if invalid
        """
        # Verify old token
        payload = await self.verify_refresh_token(old_token)
        if not payload:
            return None
        
        # Verify user_id matches
        if payload.get("sub") != user_id:
            return None
        
        # Mark old token as used
        token_id = payload.get("jti")
        await self.db.refresh_tokens.update_one(
            {"token_id": token_id},
            {"$set": {"used": True, "used_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        # Get user email for access token
        user_doc = await self.db.users.find_one({"user_id": user_id})
        if not user_doc:
            return None
        
        # Create new token pair
        token_pair = await self.create_token_pair(user_id, user_doc["email"])
        
        return (token_pair["access_token"], token_pair["refresh_token"])
    
    async def revoke_refresh_token(self, token: str) -> bool:
        """
        Revoke a refresh token (logout)
        Returns True if revoked, False if not found
        """
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                options={"verify_exp": False}  # Allow revocation of expired tokens
            )
            
            token_id = payload.get("jti")
            if not token_id:
                return False
            
            result = await self.db.refresh_tokens.update_one(
                {"token_id": token_id},
                {"$set": {
                    "revoked": True,
                    "revoked_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            return result.modified_count > 0
        
        except jwt.JWTError:
            return False
    
    async def revoke_all_user_tokens(self, user_id: str) -> int:
        """
        Revoke all refresh tokens for a user (logout from all devices)
        Returns number of tokens revoked
        """
        result = await self.db.refresh_tokens.update_many(
            {"user_id": user_id, "revoked": False},
            {"$set": {
                "revoked": True,
                "revoked_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return result.modified_count
    
    async def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired refresh tokens from database
        Should be run periodically (e.g., daily cron job)
        Returns number of tokens deleted
        """
        current_time = datetime.now(timezone.utc).isoformat()
        
        result = await self.db.refresh_tokens.delete_many({
            "expires_at": {"$lt": current_time}
        })
        
        return result.deleted_count
