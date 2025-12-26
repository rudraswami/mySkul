"""
📧 Newsletter API - Email Subscription Management
=================================================

Simple newsletter subscription for landing page.
Stores email in database for future marketing campaigns.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, validator

from dependencies import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/newsletter", tags=["Newsletter"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class NewsletterSubscribeRequest(BaseModel):
    """Newsletter subscription request"""
    email: EmailStr
    source: Optional[str] = "landing_page"  # Where they subscribed from
    
    @validator('email')
    def validate_email(cls, v):
        # Additional validation for common typos
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v.lower().strip()


class NewsletterResponse(BaseModel):
    """Newsletter subscription response"""
    success: bool
    message: str
    already_subscribed: bool = False


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/subscribe", response_model=NewsletterResponse)
async def subscribe_newsletter(
    request: NewsletterSubscribeRequest,
    db = Depends(get_database)
):
    """
    📧 Subscribe to newsletter
    
    - Validates email format
    - Checks for duplicate subscriptions
    - Stores subscription in database
    """
    try:
        email = request.email.lower().strip()
        
        # Check if already subscribed
        existing = await db.newsletter_subscribers.find_one({"email": email})
        
        if existing:
            # Already subscribed - not an error, just inform
            if existing.get("status") == "unsubscribed":
                # Re-subscribe
                await db.newsletter_subscribers.update_one(
                    {"email": email},
                    {
                        "$set": {
                            "status": "active",
                            "resubscribed_at": datetime.now(timezone.utc),
                            "source": request.source
                        }
                    }
                )
                logger.info(f"📧 Newsletter re-subscription: {email}")
                return NewsletterResponse(
                    success=True,
                    message="Welcome back! You've been re-subscribed to our newsletter.",
                    already_subscribed=False
                )
            else:
                logger.info(f"📧 Newsletter already subscribed: {email}")
                return NewsletterResponse(
                    success=True,
                    message="You're already subscribed! We'll keep you updated.",
                    already_subscribed=True
                )
        
        # New subscription
        subscription_doc = {
            "email": email,
            "source": request.source,
            "status": "active",
            "subscribed_at": datetime.now(timezone.utc),
            "ip_address": None,  # Can be added via middleware if needed
            "user_agent": None
        }
        
        await db.newsletter_subscribers.insert_one(subscription_doc)
        
        logger.info(f"📧 New newsletter subscription: {email} from {request.source}")
        
        return NewsletterResponse(
            success=True,
            message="🎉 Welcome aboard! You'll receive updates about AI-powered learning.",
            already_subscribed=False
        )
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"❌ Newsletter subscription error: {e}")
        raise HTTPException(status_code=500, detail="Failed to subscribe. Please try again.")


@router.post("/unsubscribe")
async def unsubscribe_newsletter(
    request: NewsletterSubscribeRequest,
    db = Depends(get_database)
):
    """
    📧 Unsubscribe from newsletter
    """
    try:
        email = request.email.lower().strip()
        
        result = await db.newsletter_subscribers.update_one(
            {"email": email},
            {
                "$set": {
                    "status": "unsubscribed",
                    "unsubscribed_at": datetime.now(timezone.utc)
                }
            }
        )
        
        if result.matched_count == 0:
            return {"success": True, "message": "Email not found in our list."}
        
        logger.info(f"📧 Newsletter unsubscription: {email}")
        
        return {"success": True, "message": "You've been unsubscribed. We're sorry to see you go!"}
        
    except Exception as e:
        logger.error(f"❌ Newsletter unsubscription error: {e}")
        raise HTTPException(status_code=500, detail="Failed to unsubscribe. Please try again.")


@router.get("/status/{email}")
async def check_subscription_status(
    email: str,
    db = Depends(get_database)
):
    """
    📧 Check newsletter subscription status
    """
    try:
        email = email.lower().strip()
        
        subscriber = await db.newsletter_subscribers.find_one({"email": email})
        
        if not subscriber:
            return {"subscribed": False, "status": None}
        
        return {
            "subscribed": subscriber.get("status") == "active",
            "status": subscriber.get("status"),
            "subscribed_at": subscriber.get("subscribed_at")
        }
        
    except Exception as e:
        logger.error(f"❌ Newsletter status check error: {e}")
        raise HTTPException(status_code=500, detail="Failed to check status.")

























































