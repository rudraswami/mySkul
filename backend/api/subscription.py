"""
Subscription router for managing user subscriptions, plans, and access control
MIGRATED TO USE UNIFIED SUBSCRIPTION SERVICE (Phase 1 - Stability)
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from datetime import datetime, timezone

from models.core import User
from models.subscription import (
    SubscriptionRequest, FeatureAccessRequest
)
from services.subscription_service import SubscriptionService  # Legacy - kept for plan config
from services.unified_subscription_service import UnifiedSubscriptionService, FeatureName
from dependencies import get_current_user, get_database, get_unified_subscription_service


# Router instance
router = APIRouter(prefix="/subscription", tags=["subscription"])


# Dependency to get subscription service (Legacy - for plan config only)
async def get_subscription_service(db = Depends(get_database)) -> SubscriptionService:
    """Get legacy subscription service instance (for plan config only)"""
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
            # Convert features object to user-friendly array for frontend
            features_obj = plan_data.get("features", {})
            features_array = []
            
            # AI Tutor specific features
            if features_obj.get("ai_sessions_monthly"):
                sessions = features_obj["ai_sessions_monthly"]
                if sessions == "unlimited":
                    features_array.append("🚀 Unlimited AI Tutor sessions - Ask anything, anytime")
                else:
                    features_array.append(f"🎯 {sessions} AI Tutor sessions per month")
            
            # Mentor tips
            if features_obj.get("mentor_tips_daily"):
                tips = features_obj["mentor_tips_daily"]
                if tips == "unlimited":
                    features_array.append("💙 Unlimited mentor motivational tips")
                elif tips > 0:
                    features_array.append(f"💙 {tips} mentor tips per day")
            
            # Mock tests
            if features_obj.get("mock_tests_weekly"):
                tests = features_obj["mock_tests_weekly"]
                if tests == "unlimited":
                    features_array.append("📝 Unlimited mock tests weekly")
                else:
                    features_array.append(f"📝 {tests} mock tests per week")
            
            # Auto notes
            if features_obj.get("auto_note_uploads_daily"):
                uploads = features_obj["auto_note_uploads_daily"]
                if uploads == "unlimited":
                    features_array.append("📁 Unlimited note uploads daily")
                else:
                    features_array.append(f"📁 {uploads} note upload(s) daily")
            
            # Advanced features
            if features_obj.get("analytics_access"):
                tier = features_obj.get("analytics_tier", "basic")
                features_array.append(f"📊 {tier.capitalize()} analytics & insights")
            
            if features_obj.get("offline_mode"):
                features_array.append("📱 Offline mode enabled")
            
            if features_obj.get("priority_support"):
                features_array.append("⚡ Priority customer support")
            
            if features_obj.get("export_notes"):
                features_array.append("💾 Export notes & reports")
            
            if features_obj.get("concept_tagging"):
                features_array.append("🔗 Advanced concept tagging")
            
            if features_obj.get("emotion_sync"):
                features_array.append("🧠 Emotion-aware AI tutor")
            
            plan = {
                "name": plan_name,
                "display_name": plan_data.get("display_name", plan_name),
                "tier": plan_name,
                "tagline": plan_data.get("tagline", ""),
                "price_monthly": plan_data.get("price_monthly", 0),
                "price_yearly": plan_data.get("price_yearly", 0),
                "price_quarterly": plan_data.get("price_quarterly", 0),
                "features": features_array,  # Now an array!
                "is_popular": plan_data.get("is_popular", plan_name == "SCHOLAR"),
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
    unified_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service),
    legacy_service: SubscriptionService = Depends(get_subscription_service)
):
    """Get current user subscription information (MIGRATED to Unified Service)"""
    try:
        # Get tier from unified service
        tier = await unified_service.get_user_tier(user.user_id)
        
        # Get usage summary from unified service
        usage_summary = await unified_service.get_usage_summary(user.user_id)
        
        # Get plan info from legacy service (for plan config)
        plan_config = await legacy_service.load_plan_config()
        plan_info = plan_config.get(tier.upper(), {})
        
        return {
            "subscription_tier": tier,
            "subscription_status": "active",  # From unified service
            "plan_info": plan_info,
            "usage_summary": usage_summary,
            "features": usage_summary.get("features", {}),
            "next_reset": usage_summary.get("next_reset")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subscription info: {str(e)}")


@router.get("/current")
async def get_current_subscription(
    user: User = Depends(get_current_user),
    unified_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service),
    legacy_service: SubscriptionService = Depends(get_subscription_service)
):
    """Get current subscription details (MIGRATED to Unified Service)"""
    try:
        # Get tier from unified service
        tier = await unified_service.get_user_tier(user.user_id)
        
        # Get plan info from legacy service
        plan_config = await legacy_service.load_plan_config()
        plan_info = plan_config.get(tier.upper(), {})
        
        return {
            "plan_name": tier,
            "status": "active",
            "current_period_end": None,  # TODO: Add subscription expiry tracking
            "auto_renew": True,
            "plan_info": plan_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get current subscription: {str(e)}")


@router.post("/check-access")
async def check_feature_access(
    request: FeatureAccessRequest,
    user: User = Depends(get_current_user),
    unified_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service)
):
    """
    Check if user has access to a specific feature (MIGRATED to Unified Service)
    Returns 200 OK with access info if access granted,
    402 Payment Required with upsell info if access denied
    """
    try:
        # Map old feature names to new FeatureName enum if needed
        feature_name = request.feature_name
        
        # Check access using unified service
        access_result = await unified_service.check_feature_access(
            user.user_id,
            feature_name,
            requested_amount=1
        )
        
        # Return 200 OK with access info if user has access
        if access_result.allowed:
            return {
                "has_access": True,
                "feature": feature_name,
                "remaining": access_result.remaining,
                "limit": access_result.limit,
                "used": access_result.used,
                "subscription_tier": access_result.current_tier,
                "message": access_result.message
            }
        
        # Return 402 Payment Required if access is denied
        raise HTTPException(
            status_code=402,
            detail={
                "message": access_result.message,
                "reason": "limit_reached" if access_result.used >= access_result.limit else "feature_locked",
                "upsell_info": {
                    "upgrade_message": access_result.upgrade_message,
                    "current_tier": access_result.current_tier,
                    "next_reset": access_result.next_reset.isoformat() if access_result.next_reset else None
                },
                "has_access": False,
                "upgrade_needed": True,
                "used": access_result.used,
                "limit": access_result.limit,
                "remaining": 0
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check feature access: {str(e)}")


@router.post("/track-usage")
async def track_feature_usage(
    request: FeatureAccessRequest,
    user: User = Depends(get_current_user),
    unified_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service)
):
    """Track usage for a specific feature (MIGRATED to Unified Service)"""
    try:
        success = await unified_service.track_feature_use(
            user.user_id,
            request.feature_name,
            amount=1
        )
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




# ============= AI TUTOR SPECIFIC ENDPOINTS =============

@router.get("/check-ai-tutor-access")
async def check_ai_tutor_access(
    user: User = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """
    Check if user can access AI Tutor
    Returns: {allowed, remaining, total, usage_percent, needs_upgrade, upgrade_hint}
    """
    try:
        access_info = await subscription_service.check_ai_tutor_access(user.user_id)
        return access_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check AI Tutor access: {str(e)}")


@router.post("/track-ai-tutor-session")
async def track_ai_tutor_session(
    user: User = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """Track an AI Tutor session usage"""
    try:
        # First check if user has access
        access_info = await subscription_service.check_ai_tutor_access(user.user_id)
        
        if not access_info.get("allowed", False):
            raise HTTPException(
                status_code=402,
                detail={
                    "message": "AI Tutor session limit reached",
                    "upgrade_hint": access_info.get("upgrade_hint"),
                    "needs_upgrade": True
                }
            )
        
        # Track the session
        success = await subscription_service.track_ai_tutor_session(user.user_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to track session")
        
        # Return updated access info
        updated_access = await subscription_service.check_ai_tutor_access(user.user_id)
        return {
            "message": "Session tracked successfully",
            "access_info": updated_access
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track AI Tutor session: {str(e)}")


@router.get("/check-mentor-tip-access")
async def check_mentor_tip_access(
    user: User = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """Check if user can access mentor tips today"""
    try:
        access_info = await subscription_service.check_mentor_tip_access(user.user_id)
        return access_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check mentor tip access: {str(e)}")


@router.post("/track-mentor-tip-usage")
async def track_mentor_tip_usage(
    user: User = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """Track mentor tip usage"""
    try:
        # Check access first
        access_info = await subscription_service.check_mentor_tip_access(user.user_id)
        
        if not access_info.get("allowed", False):
            raise HTTPException(
                status_code=402,
                detail={
                    "message": "Mentor tip limit reached for today",
                    "upgrade_hint": access_info.get("upgrade_hint"),
                    "needs_upgrade": access_info.get("needs_upgrade", False)
                }
            )
        
        # Track usage
        success = await subscription_service.track_mentor_tip_usage(user.user_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to track usage")
        
        return {"message": "Mentor tip usage tracked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track mentor tip usage: {str(e)}")


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