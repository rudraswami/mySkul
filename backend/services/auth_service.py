"""
Authentication service for business logic and utilities
"""
import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request, Header
from motor.motor_asyncio import AsyncIOMotorClient

from models.core import User


class AuthService:
    def __init__(self, db: AsyncIOMotorClient, jwt_secret: str):
        self.db = db
        self.jwt_secret = jwt_secret

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def create_jwt_token(self, user_id: str, email: str) -> str:
        """Create a JWT token for user authentication"""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')

    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    async def get_current_user(self, request: Request, authorization: Optional[str] = Header(None)) -> User:
        """
        Hybrid authentication: Session token (OAuth) OR JWT token authentication
        Priority: dhruv_ai_session > Authorization Bearer > dhruv_ai_auth (JWT)
        """
        from datetime import datetime, timezone
        
        # Priority 1: Check for OAuth session token (dhruv_ai_session cookie)
        session_token = request.cookies.get("dhruv_ai_session")
        
        if session_token:
            # Validate session token against database (OAuth flow)
            current_time_iso = datetime.now(timezone.utc).isoformat()
            user_doc = await self.db.users.find_one({
                "session_token": session_token,
                "session_expiry": {"$gt": current_time_iso}
            })
            
            if user_doc:
                return User(**user_doc)
            # Session token exists but invalid/expired - continue to other methods
        
        # Priority 2: Check Authorization Bearer header
        token = None
        if authorization and authorization.startswith('Bearer '):
            token = authorization.split(' ')[1]
        
        # Priority 3: Check JWT cookie (dhruv_ai_auth) for backward compatibility
        if not token:
            token = request.cookies.get("dhruv_ai_auth")
        
        # If we have a JWT token, validate it
        if token:
            try:
                payload = self.verify_jwt_token(token)
                user = await self.db.users.find_one({"user_id": payload['user_id']})
                
                if user:
                    return User(**user)
            except HTTPException:
                # JWT validation failed, continue to error below
                pass
        
        # No valid authentication method found
        raise HTTPException(status_code=401, detail="Authentication required - no valid session or token")

    async def get_current_user_optional(self, request: Request) -> Optional[User]:
        """Optional authentication - returns None if no valid token"""
        try:
            return await self.get_current_user(request)
        except HTTPException:
            return None

    def set_secure_cookie(self, response, token: str):
        """Set secure httpOnly cookie for authentication"""
        backend_url = os.environ.get('BACKEND_URL', 'http://localhost:8001')
        is_https = backend_url.startswith('https://')
        response.set_cookie(
            key="dhruv_ai_auth",
            value=token,
            max_age=7 * 24 * 60 * 60,  # 7 days in seconds
            expires=7 * 24 * 60 * 60,  # 7 days in seconds
            httponly=True,
            secure=is_https,  # True for HTTPS
            samesite="none",  # Allow cross-domain
            path="/",
            domain=".emergent.host" if is_https else None
        )

    def clear_secure_cookie(self, response):
        """Clear the authentication cookie"""
        backend_url = os.environ.get('BACKEND_URL', 'http://localhost:8001')
        is_https = backend_url.startswith('https://')
        response.delete_cookie(
            key="dhruv_ai_auth",
            httponly=True,
            secure=is_https,
            samesite="none"
        )