"""
Authentication service for business logic and utilities
"""
import os
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request, Header
from motor.motor_asyncio import AsyncIOMotorClient

from ..models.core import User


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
        Hybrid authentication: Secure cookie-based OR Bearer token authentication
        Prioritizes cookies (more secure) but falls back to Bearer tokens for compatibility
        """
        # Try cookie-based authentication first (more secure)
        token = request.cookies.get("dhruv_ai_auth")
        
        # Fall back to Bearer token for backward compatibility
        if not token and authorization and authorization.startswith('Bearer '):
            token = authorization.split(' ')[1]
        
        if not token:
            raise HTTPException(status_code=401, detail="Authentication required - no session cookie or Bearer token")
        
        payload = self.verify_jwt_token(token)
        user = await self.db.users.find_one({"user_id": payload['user_id']})
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return User(**user)

    async def get_current_user_optional(self, request: Request) -> Optional[User]:
        """Optional authentication - returns None if no valid token"""
        try:
            return await self.get_current_user(request)
        except HTTPException:
            return None

    def set_secure_cookie(self, response, token: str):
        """Set secure httpOnly cookie for authentication"""
        is_production = os.environ.get('ENVIRONMENT', 'development') == 'production'
        response.set_cookie(
            key="dhruv_ai_auth",
            value=token,
            max_age=7 * 24 * 60 * 60,  # 7 days in seconds
            expires=7 * 24 * 60 * 60,  # 7 days in seconds
            httponly=True,
            secure=is_production,  # HTTPS only in production
            samesite="lax"  # CSRF protection
        )

    def clear_secure_cookie(self, response):
        """Clear the authentication cookie"""
        is_production = os.environ.get('ENVIRONMENT', 'development') == 'production'
        response.delete_cookie(
            key="dhruv_ai_auth",
            httponly=True,
            secure=is_production,
            samesite="lax"
        )