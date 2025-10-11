"""
Subscription router for managing user subscriptions, plans, and access control
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any
from datetime import datetime, timezone

from models.core import User
from models.subscription import (
    SubscriptionRequest, FeatureAccessRequest, CheckoutRequest,
    SubscriptionPlan, UserSubscription, UsageTracking
)
from services.subscription_service import SubscriptionService
from dependencies import get_current_user, get_database


# Router instance
router = APIRouter(prefix="/subscription", tags=["subscription"])


# Dependency to get subscription service
async def get_subscription_service(db = Depends(get_database)) -> SubscriptionService:
    """Get subscription service instance"""
    return SubscriptionService(db)


@router.get("/plans")
async def get_subscription_plans(
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """Get all available subscription plans (UNIFIED ENDPOINT - removes duplicates)"""
    try:
        plan_config = await subscription_service.load_plan_config()
        
        # Convert plan config to proper format
        plans = []
        for plan_name, plan_data in plan_config.items():
            plan = {
                "name": plan_name,
                "display_name": plan_data.get("display_name", plan_name),
                "price_monthly": plan_data.get("price_monthly", 0),
                "price_yearly": plan_data.get("price_yearly", 0),
                "features": plan_data.get("features", {}),
                "is_popular": plan_data.get("is_popular", False),
                "description": plan_data.get("description", ""),
            }
            plans.append(plan)
        
        return {
            "plans": plans,
            "currency": "INR",
            "billing_cycles": ["monthly", "yearly"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subscription plans: {str(e)}")


@router.get("/info")
async def get_subscription_info(
    user: User = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """Get current user subscription information"""
    try:
        info = await subscription_service.get_user_subscription_info(user.user_id)
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subscription info: {str(e)}")


@router.get("/current")
async def get_current_subscription(
    user: User = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """Get current subscription details"""
    try:
        info = await subscription_service.get_user_subscription_info(user.user_id)
        return {
            "plan_name": info["subscription_tier"],
            "status": info["subscription_status"],
            "current_period_end": info.get("current_period_end"),
            "auto_renew": info.get("auto_renew", True),
            "plan_info": info["plan_info"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get current subscription: {str(e)}")


@router.post("/check-access")
async def check_feature_access(
    request: FeatureAccessRequest,
    user: User = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """
    Check if user has access to a specific feature
    #BACKEND-FIX-PHASE3 - Returns 200 OK with access info if access granted,
    402 Payment Required with upsell info if access denied
    """
    try:
        access_info = await subscription_service.check_feature_access(user.user_id, request.feature_name)
        
        # Return 200 OK with access info if user has access
        if access_info.get("has_access", False):
            return {
                "has_access": True,
                "feature": request.feature_name,
                "remaining": access_info.get("remaining", 0),
                "limit": access_info.get("limit", 0),
                "used": access_info.get("used", 0),
                "subscription_tier": access_info.get("subscription_tier", "FREE")
            }
        
        # Return 402 Payment Required if access is denied and upgrade needed
        if access_info.get("upgrade_needed", False):
            raise HTTPException(
                status_code=402,
                detail={
                    "message": f"Access denied for {request.feature_name}",
                    "reason": access_info.get("reason", "limit_reached"),
                    "upsell_info": access_info.get("upsell_info", {}),
                    "has_access": False,
                    "upgrade_needed": True,
                    **access_info
                }
            )
        
        # Default: return access info with 200 OK
        return access_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check feature access: {str(e)}")


@router.post("/track-usage")
async def track_feature_usage(
    request: FeatureAccessRequest,
    user: User = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """Track usage for a specific feature"""
    try:
        success = await subscription_service.track_usage(user.user_id, request.feature_name)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to track usage")
        
        return {"message": "Usage tracked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track usage: {str(e)}")


@router.get("/usage")
async def get_usage_info(
    user: User = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """Get user's current usage statistics"""
    try:
        info = await subscription_service.get_user_subscription_info(user.user_id)
        daily_usage = info["daily_usage"]
        plan_features = info["plan_info"]["features"]
        
        usage_summary = {}
        for feature_name, limit in plan_features.items():
            if isinstance(limit, int):
                used = daily_usage.get(feature_name, 0)
                remaining = max(0, limit - used)
            elif limit == "unlimited":
                used = daily_usage.get(feature_name, 0)
                remaining = -1  # Unlimited
            else:
                used = 0
                remaining = 0
            
            usage_summary[feature_name] = {
                "used": used,
                "limit": limit,
                "remaining": remaining,
                "has_access": remaining != 0
            }
        
        return {
            "subscription_tier": info["subscription_tier"],
            "usage": usage_summary,
            "daily_usage": daily_usage
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage info: {str(e)}")


@router.post("/upgrade")
async def upgrade_subscription(
    request: SubscriptionRequest,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Upgrade user subscription (placeholder for payment integration)"""
    try:
        # This is a simplified upgrade endpoint
        # In production, this would integrate with payment processors
        
        # Update user subscription
        update_result = await db.user_subscriptions.update_one(
            {"user_id": user.user_id},
            {
                "$set": {
                    "plan_name": request.plan_name.upper(),
                    "billing_cycle": request.billing_cycle,
                    "status": "active",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        if update_result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        return {
            "message": "Subscription upgraded successfully",
            "plan_name": request.plan_name.upper(),
            "billing_cycle": request.billing_cycle
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upgrade subscription: {str(e)}")


@router.post("/upsell-response")
async def track_upsell_response(
    response_data: Dict[str, Any],
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Track user response to upsell messages"""
    try:
        # Store upsell interaction for analytics
        interaction_record = {
            "user_id": user.user_id,
            "interaction_type": "upsell_response",
            "response_data": response_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        await db.user_interactions.insert_one(interaction_record)
        
        return {"message": "Upsell response tracked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track upsell response: {str(e)}")


@router.post("/cancel")
async def cancel_subscription(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Cancel user subscription"""
    try:
        update_result = await db.user_subscriptions.update_one(
            {"user_id": user.user_id},
            {
                "$set": {
                    "status": "cancelled",
                    "auto_renew": False,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        if update_result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        return {"message": "Subscription cancelled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel subscription: {str(e)}")