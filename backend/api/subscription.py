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
        # Map old feature names to new FeatureName enum for backward compatibility
        feature_name_mapping = {
            "ai_sessions_monthly": "ai_mentor",
            "ai_tutor": "ai_mentor",
            "mentor_tips_daily": "ai_mentor",
            "mock_tests_weekly": "mock_tests",
            "auto_note_uploads_daily": "auto_notes",
            "file_uploads": "auto_notes"
        }
        
        feature_name = feature_name_mapping.get(request.feature_name, request.feature_name)
        
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
    unified_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service)
):
    """Get user's current usage statistics (MIGRATED to Unified Service)"""
    try:
        # Get comprehensive usage summary from unified service
        usage_summary = await unified_service.get_usage_summary(user.user_id)
        
        # Format for backward compatibility
        tier = usage_summary.get("tier", "free")
        features = usage_summary.get("features", {})
        
        # Convert to expected format
        usage_by_feature = {}
        for feature_name, feature_data in features.items():
            usage_by_feature[feature_name] = {
                "used": feature_data.get("used", 0),
                "limit": feature_data.get("limit", 0),
                "remaining": feature_data.get("remaining", 0),
                "has_access": feature_data.get("status") in ["active", "unlimited"]
            }
        
        return {
            "subscription_tier": tier,
            "usage": usage_by_feature,
            "next_reset": usage_summary.get("next_reset")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage info: {str(e)}")




# ============= AI TUTOR SPECIFIC ENDPOINTS =============

@router.get("/check-ai-tutor-access")
async def check_ai_tutor_access(
    user: User = Depends(get_current_user),
    unified_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service)
):
    """
    Check if user can access AI Tutor (MIGRATED to Unified Service)
    Returns: {allowed, remaining, total, usage_percent, needs_upgrade, upgrade_hint}
    """
    try:
        access_result = await unified_service.check_feature_access(
            user.user_id,
            FeatureName.AI_MENTOR.value,
            requested_amount=1
        )
        
        # Calculate usage percentage
        usage_percent = 0
        if access_result.limit > 0:
            usage_percent = int((access_result.used / access_result.limit) * 100)
        
        return {
            "allowed": access_result.allowed,
            "remaining": access_result.remaining if access_result.remaining >= 0 else "unlimited",
            "total": access_result.limit if access_result.limit >= 0 else "unlimited",
            "used": access_result.used,
            "usage_percent": usage_percent,
            "needs_upgrade": not access_result.allowed,
            "upgrade_hint": access_result.upgrade_message if not access_result.allowed else None,
            "message": access_result.message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check AI Tutor access: {str(e)}")


@router.post("/track-ai-tutor-session")
async def track_ai_tutor_session(
    user: User = Depends(get_current_user),
    unified_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service)
):
    """Track an AI Tutor session usage (MIGRATED to Unified Service)"""
    try:
        # First check if user has access
        access_result = await unified_service.check_feature_access(
            user.user_id,
            FeatureName.AI_MENTOR.value,
            requested_amount=1
        )
        
        if not access_result.allowed:
            raise HTTPException(
                status_code=402,
                detail={
                    "message": "AI Tutor session limit reached",
                    "upgrade_hint": access_result.upgrade_message,
                    "needs_upgrade": True,
                    "used": access_result.used,
                    "limit": access_result.limit
                }
            )
        
        # Track the session
        success = await unified_service.track_feature_use(
            user.user_id,
            FeatureName.AI_MENTOR.value,
            amount=1
        )
        if not success:
            raise HTTPException(status_code=500, detail="Failed to track session")
        
        # Return updated access info
        updated_access = await unified_service.check_feature_access(
            user.user_id,
            FeatureName.AI_MENTOR.value,
            requested_amount=0
        )
        
        return {
            "message": "Session tracked successfully",
            "access_info": {
                "allowed": updated_access.allowed,
                "remaining": updated_access.remaining,
                "total": updated_access.limit,
                "used": updated_access.used
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track AI Tutor session: {str(e)}")


@router.get("/check-mentor-tip-access")
async def check_mentor_tip_access(
    user: User = Depends(get_current_user),
    unified_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service)
):
    """Check if user can access mentor tips today (MIGRATED to Unified Service)"""
    try:
        # Note: DOUBT_SOLVING is used as mentor tips feature
        access_result = await unified_service.check_feature_access(
            user.user_id,
            FeatureName.DOUBT_SOLVING.value,
            requested_amount=1
        )
        
        return {
            "allowed": access_result.allowed,
            "remaining": access_result.remaining if access_result.remaining >= 0 else "unlimited",
            "total": access_result.limit if access_result.limit >= 0 else "unlimited",
            "used": access_result.used,
            "needs_upgrade": not access_result.allowed,
            "upgrade_hint": access_result.upgrade_message if not access_result.allowed else None,
            "message": access_result.message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check mentor tip access: {str(e)}")


@router.post("/track-mentor-tip-usage")
async def track_mentor_tip_usage(
    user: User = Depends(get_current_user),
    unified_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service)
):
    """Track mentor tip usage (MIGRATED to Unified Service)"""
    try:
        # Check access first
        access_result = await unified_service.check_feature_access(
            user.user_id,
            FeatureName.DOUBT_SOLVING.value,
            requested_amount=1
        )
        
        if not access_result.allowed:
            raise HTTPException(
                status_code=402,
                detail={
                    "message": "Mentor tip limit reached for today",
                    "upgrade_hint": access_result.upgrade_message,
                    "needs_upgrade": True
                }
            )
        
        # Track usage
        success = await unified_service.track_feature_use(
            user.user_id,
            FeatureName.DOUBT_SOLVING.value,
            amount=1
        )
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
    unified_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service)
):
    """Upgrade user subscription (MIGRATED to Unified Service)"""
    try:
        # Use unified service to upgrade
        success, message = await unified_service.upgrade_subscription(
            user.user_id,
            request.plan_name.lower(),  # Normalize to lowercase
            payment_method="manual"
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return {
            "message": message,
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


# ==================== RAZORPAY PAYMENT INTEGRATION ====================

@router.post("/razorpay/create-order")
async def create_razorpay_order(
    request: Dict[str, Any],
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Create Razorpay order for subscription purchase
    
    Request body: {
        "plan_name": "PREMIUM" | "PRO",
        "billing_cycle": "monthly" | "yearly"
        # amount is NOT needed - backend calculates from plan config
    }
    """
    try:
        import razorpay
        import os
        from core.config import settings
        
        # Initialize Razorpay client with production credentials
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        plan_name = request.get("plan_name", "PREMIUM")
        billing_cycle = request.get("billing_cycle", "monthly")
        
        # FIX: Log received request for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Creating Razorpay order - Plan: {plan_name}, Cycle: {billing_cycle}, User: {user.user_id}")
        
        # Get plan configuration
        subscription_service = SubscriptionService(db)
        plan_config = await subscription_service.load_plan_config()
        
        if plan_name not in plan_config:
            raise HTTPException(status_code=400, detail=f"Invalid plan: {plan_name}")
        
        plan_data = plan_config[plan_name]
        
        # Get price based on billing cycle - BACKEND CALCULATES THIS, NOT FRONTEND
        if billing_cycle == "yearly":
            amount_inr = plan_data.get("price_yearly", plan_data.get("price_monthly", 0) * 10)
        else:
            amount_inr = plan_data.get("price_monthly", 0)
        
        # FIX: Ensure amount is valid
        if amount_inr <= 0:
            raise HTTPException(status_code=400, detail=f"Invalid plan amount: {amount_inr}")
        
        # Convert to paise (Razorpay uses paise: ₹1 = 100 paise)
        amount_paise = int(amount_inr * 100)
        
        logger.info(f"Amount calculated - INR: {amount_inr}, Paise: {amount_paise}")
        
        # Create Razorpay order
        order_data = {
            "amount": amount_paise,  # MUST be in paise
            "currency": "INR",
            "receipt": f"order_{user.user_id}_{int(datetime.now(timezone.utc).timestamp())}",
            "notes": {
                "user_id": user.user_id,
                "plan_name": plan_name,
                "billing_cycle": billing_cycle,
                "email": user.email or ""
            }
        }
        
        razorpay_order = client.order.create(data=order_data)
        
        logger.info(f"Razorpay order created successfully: {razorpay_order['id']}")
        
        # Store order in database for verification later
        order_record = {
            "order_id": razorpay_order["id"],
            "user_id": user.user_id,
            "plan_name": plan_name,
            "billing_cycle": billing_cycle,
            "amount_inr": amount_inr,
            "amount_paise": amount_paise,
            "status": "created",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "razorpay_order": razorpay_order
        }
        
        await db.razorpay_orders.insert_one(order_record)
        
        # FIX: Return amount in PAISE for Razorpay frontend SDK
        return {
            "order_id": razorpay_order["id"],
            "amount": amount_paise,  # CRITICAL: Must be paise for Razorpay SDK
            "amount_inr": amount_inr,  # For display purposes
            "currency": "INR",
            "key_id": settings.RAZORPAY_KEY_ID,
            "plan_name": plan_name,
            "billing_cycle": billing_cycle
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Razorpay order creation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")
            "plan_name": plan_name,
            "billing_cycle": billing_cycle
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Razorpay order creation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")


@router.post("/razorpay/verify-payment")
async def verify_razorpay_payment(
    request: Dict[str, Any],
    user: User = Depends(get_current_user),
    db = Depends(get_database),
    unified_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service)
):
    """
    Verify Razorpay payment and activate subscription
    
    Request body: {
        "razorpay_order_id": "order_xxx",
        "razorpay_payment_id": "pay_xxx",
        "razorpay_signature": "signature_xxx"
    }
    """
    try:
        import razorpay
        import hmac
        import hashlib
        from core.config import settings
        
        razorpay_order_id = request.get("razorpay_order_id")
        razorpay_payment_id = request.get("razorpay_payment_id")
        razorpay_signature = request.get("razorpay_signature")
        
        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            raise HTTPException(status_code=400, detail="Missing payment verification parameters")
        
        # Verify signature
        generated_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        if generated_signature != razorpay_signature:
            raise HTTPException(status_code=400, detail="Invalid payment signature")
        
        # Get order from database
        order = await db.razorpay_orders.find_one({"order_id": razorpay_order_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order.get("user_id") != user.user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        # Fetch payment details from Razorpay
        payment = client.payment.fetch(razorpay_payment_id)
        
        if payment["status"] != "captured" and payment["status"] != "authorized":
            raise HTTPException(status_code=400, detail=f"Payment not successful: {payment['status']}")
        
        # Activate subscription using unified service
        plan_name = order.get("plan_name", "PREMIUM")
        billing_cycle = order.get("billing_cycle", "monthly")
        
        # Upgrade user to paid plan
        success = await unified_service.upgrade_subscription(
            user.user_id,
            plan_name,
            billing_cycle
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to activate subscription")
        
        # Update order status
        await db.razorpay_orders.update_one(
            {"order_id": razorpay_order_id},
            {
                "$set": {
                    "status": "completed",
                    "payment_id": razorpay_payment_id,
                    "signature": razorpay_signature,
                    "payment_details": payment,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Create subscription record
        await db.subscriptions.update_one(
            {"user_id": user.user_id},
            {
                "$set": {
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": razorpay_payment_id,
                    "payment_method": "razorpay",
                    "last_payment_date": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return {
            "success": True,
            "message": "Payment verified and subscription activated",
            "subscription": {
                "tier": plan_name,
                "billing_cycle": billing_cycle,
                "status": "active"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Payment verification failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Payment verification failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel subscription: {str(e)}")