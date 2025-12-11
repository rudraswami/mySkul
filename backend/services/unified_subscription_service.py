"""
Unified Subscription Service - Student-Centric Feature Access Control
Centralizes all subscription and feature-access logic for consistency

Philosophy: "Pay for Progress, Not Access"
- Students get essential learning tools for free
- Premium features enhance learning experience
- Clear, empowering upgrade messaging
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple
from enum import Enum

from motor.motor_asyncio import AsyncIOMotorDatabase
from core.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# SUBSCRIPTION TIERS
# =============================================================================

class SubscriptionTier(str, Enum):
    """Student subscription tiers"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"


class FeatureName(str, Enum):
    """Available features with student-friendly names"""
    AI_MENTOR = "ai_mentor"              # AI Tutor conversations
    MOCK_TESTS = "mock_tests"            # Practice exams
    AUTO_NOTES = "auto_notes"            # AI-generated study notes
    DETAILED_ANALYSIS = "detailed_analysis"  # In-depth performance insights
    EXAM_STRATEGIES = "exam_strategies"  # Personalized exam tips
    DOUBT_SOLVING = "doubt_solving"      # Quick doubt resolution


# =============================================================================
# FEATURE ACCESS RESULT
# =============================================================================

class FeatureAccessResult:
    """
    Result of feature access check
    Student-friendly with actionable information
    """
    
    def __init__(
        self,
        allowed: bool,
        current_tier: str,
        used: int,
        limit: int,
        remaining: int,
        message: str = "",
        upgrade_message: str = "",
        next_reset: Optional[datetime] = None
    ):
        self.allowed = allowed
        self.current_tier = current_tier
        self.used = used
        self.limit = limit
        self.remaining = remaining
        self.message = message
        self.upgrade_message = upgrade_message
        self.next_reset = next_reset
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "allowed": self.allowed,
            "current_tier": self.current_tier,
            "usage": {
                "used": self.used,
                "limit": self.limit,
                "remaining": self.remaining
            },
            "message": self.message,
            "upgrade_message": self.upgrade_message if not self.allowed else None,
            "next_reset": self.next_reset.isoformat() if self.next_reset else None
        }


# =============================================================================
# UNIFIED SUBSCRIPTION SERVICE
# =============================================================================

class UnifiedSubscriptionService:
    """
    Centralized subscription and feature-access management
    Single source of truth for all subscription logic
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
        # Feature limits per tier (from settings)
        self.feature_limits = {
            SubscriptionTier.FREE: {
                FeatureName.AI_MENTOR: settings.FREE_TIER_AI_MENTOR_LIMIT,
                FeatureName.MOCK_TESTS: settings.FREE_TIER_MOCK_TEST_LIMIT,
                FeatureName.AUTO_NOTES: settings.FREE_TIER_AUTO_NOTES_LIMIT,
                FeatureName.DETAILED_ANALYSIS: 0,  # Premium only
                FeatureName.EXAM_STRATEGIES: 0,    # Premium only
                FeatureName.DOUBT_SOLVING: 5,      # Limited for free
            },
            SubscriptionTier.BASIC: {
                FeatureName.AI_MENTOR: settings.BASIC_TIER_AI_MENTOR_LIMIT,
                FeatureName.MOCK_TESTS: settings.BASIC_TIER_MOCK_TEST_LIMIT,
                FeatureName.AUTO_NOTES: settings.BASIC_TIER_AUTO_NOTES_LIMIT,
                FeatureName.DETAILED_ANALYSIS: 10,  # Limited
                FeatureName.EXAM_STRATEGIES: 10,    # Limited
                FeatureName.DOUBT_SOLVING: 50,      # More for basic
            },
            SubscriptionTier.PREMIUM: {
                FeatureName.AI_MENTOR: -1,  # Unlimited
                FeatureName.MOCK_TESTS: -1,  # Unlimited
                FeatureName.AUTO_NOTES: -1,  # Unlimited
                FeatureName.DETAILED_ANALYSIS: -1,  # Unlimited
                FeatureName.EXAM_STRATEGIES: -1,    # Unlimited
                FeatureName.DOUBT_SOLVING: -1,      # Unlimited
            }
        }
        
        # Student-friendly upgrade messages
        self.upgrade_messages = {
            SubscriptionTier.FREE: {
                "default": "🎯 You've used your free access! Upgrade to Basic for 10x more practice, or Premium for unlimited learning.",
                FeatureName.AI_MENTOR: "🤖 AI Mentor limit reached! Upgrade for unlimited conversations with your AI study buddy.",
                FeatureName.MOCK_TESTS: "📝 Free mock tests completed! Upgrade to practice more and ace your exams.",
                FeatureName.AUTO_NOTES: "📔 Free auto-notes used! Upgrade for unlimited AI-generated study materials.",
                FeatureName.DETAILED_ANALYSIS: "📊 Detailed analysis is a Premium feature. Unlock deep insights into your performance!",
                FeatureName.EXAM_STRATEGIES: "🎯 Personalized exam strategies available in Premium. Level up your preparation!",
            },
            SubscriptionTier.BASIC: {
                "default": "🚀 You're doing great! Upgrade to Premium for unlimited access to all features.",
                FeatureName.AI_MENTOR: "🤖 Basic limit reached! Go Premium for unlimited AI Mentor conversations.",
                FeatureName.MOCK_TESTS: "📝 Basic mock tests completed! Premium gives you unlimited practice.",
                FeatureName.AUTO_NOTES: "📔 Basic auto-notes used! Premium unlocks unlimited study materials.",
                FeatureName.DETAILED_ANALYSIS: "📊 More detailed analysis available in Premium!",
                FeatureName.EXAM_STRATEGIES: "🎯 Unlock unlimited exam strategies with Premium!",
            }
        }
    
    # =========================================================================
    # SUBSCRIPTION MANAGEMENT
    # =========================================================================
    
    async def get_user_tier(self, user_id: str) -> str:
        """
        Get user's current subscription tier
        Creates default FREE tier if not exists
        """
        try:
            # Check subscriptions collection
            subscription = await self.db.subscriptions.find_one({"user_id": user_id})
            
            if subscription:
                # Validate tier
                tier = subscription.get("subscription_type", "free").lower()
                if tier in [t.value for t in SubscriptionTier]:
                    return tier
            
            # Check user collection for legacy subscription_type
            user = await self.db.users.find_one({"user_id": user_id})
            if user and user.get("subscription_type"):
                tier = user["subscription_type"].lower()
                if tier in [t.value for t in SubscriptionTier]:
                    return tier
            
            # Default to FREE tier
            await self._ensure_subscription_record(user_id, SubscriptionTier.FREE)
            return SubscriptionTier.FREE.value
            
        except Exception as e:
            logger.error(f"Error getting user tier: {e}")
            return SubscriptionTier.FREE.value
    
    async def _ensure_subscription_record(self, user_id: str, tier: SubscriptionTier):
        """Ensure subscription record exists"""
        try:
            # Check if exists
            existing = await self.db.subscriptions.find_one({"user_id": user_id})
            if existing:
                return
            
            # Create new subscription
            await self.db.subscriptions.insert_one({
                "user_id": user_id,
                "subscription_type": tier.value,
                "status": "active",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            })
            
            logger.info(f"Created {tier.value} subscription for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error ensuring subscription record: {e}")
    
    # =========================================================================
    # FEATURE ACCESS CONTROL - CORE LOGIC
    # =========================================================================
    
    async def check_feature_access(
        self,
        user_id: str,
        feature: str,
        requested_amount: int = 1
    ) -> FeatureAccessResult:
        """
        Check if user can access a feature
        Returns FeatureAccessResult with student-friendly information
        
        Args:
            user_id: User's unique identifier
            feature: Feature name (from FeatureName enum)
            requested_amount: Number of uses requested (default 1)
        
        Returns:
            FeatureAccessResult with access decision and helpful context
        """
        try:
            # Validate feature
            if feature not in [f.value for f in FeatureName]:
                logger.warning(f"Invalid feature name: {feature}")
                return FeatureAccessResult(
                    allowed=False,
                    current_tier="unknown",
                    used=0,
                    limit=0,
                    remaining=0,
                    message="Invalid feature"
                )
            
            # Get user's tier
            tier = await self.get_user_tier(user_id)
            tier_enum = SubscriptionTier(tier)
            
            # Get feature limit for this tier
            limit = self.feature_limits[tier_enum].get(feature, 0)
            
            # Unlimited access (-1)
            if limit == -1:
                return FeatureAccessResult(
                    allowed=True,
                    current_tier=tier,
                    used=0,
                    limit=-1,
                    remaining=-1,
                    message=f"✨ Unlimited {feature.replace('_', ' ').title()} access!"
                )
            
            # Feature not available for this tier
            if limit == 0:
                upgrade_msg = self.upgrade_messages.get(tier_enum, {}).get(
                    feature,
                    self.upgrade_messages[tier_enum]["default"]
                )
                
                return FeatureAccessResult(
                    allowed=False,
                    current_tier=tier,
                    used=0,
                    limit=0,
                    remaining=0,
                    message=f"This feature requires an upgrade",
                    upgrade_message=upgrade_msg
                )
            
            # Check current usage
            current_usage = await self._get_current_usage(user_id, feature)
            remaining = max(0, limit - current_usage)
            
            # Check if user has enough quota
            if current_usage + requested_amount > limit:
                upgrade_msg = self.upgrade_messages.get(tier_enum, {}).get(
                    feature,
                    self.upgrade_messages[tier_enum]["default"]
                )
                
                next_reset = await self._get_next_reset_time(feature)
                
                # Better error message based on feature type
                period_text = "weekly" if feature == FeatureName.MOCK_TESTS.value else "daily"
                
                return FeatureAccessResult(
                    allowed=False,
                    current_tier=tier,
                    used=current_usage,
                    limit=limit,
                    remaining=0,
                    message=f"{period_text.capitalize()} limit reached ({current_usage}/{limit} used)",
                    upgrade_message=upgrade_msg,
                    next_reset=next_reset
                )
            
            # Access granted!
            return FeatureAccessResult(
                allowed=True,
                current_tier=tier,
                used=current_usage,
                limit=limit,
                remaining=remaining - requested_amount,
                message=f"✅ Access granted! {remaining - requested_amount} remaining today"
            )
            
        except Exception as e:
            logger.error(f"Error checking feature access: {e}")
            # Fail open for better UX (allow access on error)
            return FeatureAccessResult(
                allowed=True,
                current_tier="unknown",
                used=0,
                limit=-1,
                remaining=-1,
                message="Access granted (error in validation)"
            )
    
    async def _get_current_usage(self, user_id: str, feature: str) -> int:
        """
        Get current usage count for a feature with smart reset logic
        - AI Mentor: daily reset
        - Mock Tests: WEEKLY reset (per plan config)
        - Auto Notes: daily reset
        """
        try:
            now = datetime.now(timezone.utc)
            
            # Determine reset period based on feature
            if feature == FeatureName.AI_MENTOR.value or feature == FeatureName.AUTO_NOTES.value:
                # Daily reset
                reset_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                reset_end = reset_start + timedelta(days=1)
            elif feature == FeatureName.MOCK_TESTS.value:
                # WEEKLY reset for mock tests (plan says mock_tests_weekly)
                # Week starts Monday (weekday 0)
                days_since_monday = now.weekday()
                reset_start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
                reset_end = reset_start + timedelta(days=7)
            else:
                # Default: monthly reset
                reset_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                # Next month's first day
                if now.month == 12:
                    reset_end = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                else:
                    reset_end = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            
            usage_doc = await self.db.usage_tracking.find_one({
                "user_id": user_id,
                "feature_name": feature,
                "usage_date": {"$gte": reset_start, "$lt": reset_end}
            })
            
            current_usage = usage_doc.get("usage_count", 0) if usage_doc else 0
            
            logger.info(f"📊 Usage check for {user_id} - {feature}: {current_usage} (period: {reset_start} to {reset_end})")
            return current_usage
            
        except Exception as e:
            logger.error(f"Error getting current usage: {e}")
            return 0
    
    async def _get_next_reset_time(self, feature: str) -> datetime:
        """
        Get next reset time based on feature type
        - AI Mentor: midnight UTC (daily)
        - Mock Tests: Next Monday at midnight (weekly)
        - Auto Notes: midnight UTC (daily)
        """
        now = datetime.now(timezone.utc)
        
        if feature == FeatureName.AI_MENTOR.value or feature == FeatureName.AUTO_NOTES.value:
            # Next day at midnight
            tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            return tomorrow
        elif feature == FeatureName.MOCK_TESTS.value:
            # Next Monday at midnight (weekly reset)
            days_until_monday = (7 - now.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7  # If today is Monday, next reset is next Monday
            next_monday = (now + timedelta(days=days_until_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
            return next_monday
        else:
            # First day of next month
            if now.month == 12:
                next_reset = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                next_reset = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            return next_reset
    
    # =========================================================================
    # USAGE TRACKING
    # =========================================================================
    
    async def track_feature_use(
        self,
        user_id: str,
        feature: str,
        amount: int = 1
    ) -> bool:
        """
        Track feature usage after successful use with smart reset periods
        - AI Mentor: daily tracking
        - Mock Tests: WEEKLY tracking
        - Auto Notes: daily tracking
        
        Args:
            user_id: User's unique identifier
            feature: Feature name
            amount: Number of uses to track (default 1)
        
        Returns:
            True if tracked successfully, False otherwise
        """
        try:
            now = datetime.now(timezone.utc)
            
            # Determine tracking period based on feature
            if feature == FeatureName.AI_MENTOR.value or feature == FeatureName.AUTO_NOTES.value:
                # Daily tracking
                tracking_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                reset_period = "daily"
            elif feature == FeatureName.MOCK_TESTS.value:
                # WEEKLY tracking for mock tests (week starts Monday)
                days_since_monday = now.weekday()
                tracking_date = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
                reset_period = "weekly"
            else:
                # Monthly tracking for other features
                tracking_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                reset_period = "monthly"
            
            await self.db.usage_tracking.update_one(
                {
                    "user_id": user_id,
                    "feature_name": feature,
                    "usage_date": tracking_date
                },
                {
                    "$inc": {"usage_count": amount},
                    "$set": {
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                        "reset_period": reset_period
                    }
                },
                upsert=True
            )
            
            logger.info(f"✅ Usage tracked: {user_id} - {feature} +{amount} (reset_period: {reset_period})")
            
            logger.info(f"Tracked {amount} use(s) of {feature} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking feature use: {e}")
            return False
    
    # =========================================================================
    # SUBSCRIPTION UPGRADES
    # =========================================================================
    
    async def upgrade_subscription(
        self,
        user_id: str,
        new_tier: str,
        payment_method: str = "manual"
    ) -> Tuple[bool, str]:
        """
        Upgrade user's subscription tier
        
        Args:
            user_id: User's unique identifier
            new_tier: New tier (free/basic/premium)
            payment_method: How payment was made
        
        Returns:
            (success: bool, message: str)
        """
        try:
            # Validate tier
            if new_tier not in [t.value for t in SubscriptionTier]:
                return False, f"Invalid tier: {new_tier}"
            
            new_tier_enum = SubscriptionTier(new_tier)
            
            # Update subscription
            result = await self.db.subscriptions.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "subscription_type": new_tier,
                        "status": "active",
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                        "payment_method": payment_method
                    }
                },
                upsert=True
            )
            
            # Also update user record for backward compatibility
            await self.db.users.update_one(
                {"user_id": user_id},
                {"$set": {"subscription_type": new_tier}}
            )
            
            logger.info(f"Upgraded user {user_id} to {new_tier}")
            
            return True, f"🎉 Successfully upgraded to {new_tier.title()}!"
            
        except Exception as e:
            logger.error(f"Error upgrading subscription: {e}")
            return False, "Upgrade failed. Please try again."
    
    # =========================================================================
    # ANALYTICS & INSIGHTS
    # =========================================================================
    
    async def get_usage_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive usage summary for student dashboard
        Student-friendly with actionable insights
        """
        try:
            tier = await self.get_user_tier(user_id)
            tier_enum = SubscriptionTier(tier)
            
            # Get today's usage for all features
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            
            usage_docs = await self.db.usage_tracking.find({
                "user_id": user_id,
                "usage_date": {"$gte": today, "$lt": tomorrow}
            }).to_list(length=None)
            
            usage_by_feature = {doc["feature_name"]: doc.get("usage_count", 0) for doc in usage_docs}
            
            # Build feature summary
            features = {}
            for feature in FeatureName:
                limit = self.feature_limits[tier_enum].get(feature.value, 0)
                used = usage_by_feature.get(feature.value, 0)
                
                if limit == -1:
                    remaining = -1
                    status = "unlimited"
                elif limit == 0:
                    remaining = 0
                    status = "locked"
                else:
                    remaining = max(0, limit - used)
                    status = "active" if remaining > 0 else "exhausted"
                
                features[feature.value] = {
                    "used": used,
                    "limit": limit,
                    "remaining": remaining,
                    "status": status
                }
            
            return {
                "tier": tier,
                "features": features,
                "next_reset": (today + timedelta(days=1)).isoformat(),
                "upgrade_available": tier != SubscriptionTier.PREMIUM.value
            }
            
        except Exception as e:
            logger.error(f"Error getting usage summary: {e}")
            return {"error": "Failed to fetch usage summary"}


# =============================================================================
# CONVENIENCE DECORATOR FOR ROUTES
# =============================================================================

def require_feature_access(feature: str, amount: int = 1):
    """
    Decorator to check feature access before executing route
    Usage:
        @require_feature_access(FeatureName.AI_MENTOR.value)
        async def ai_tutor_endpoint(...)
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user and db from kwargs
            user = kwargs.get('user') or kwargs.get('current_user')
            db = kwargs.get('db')
            
            if not user or db is None:
                from fastapi import HTTPException
                raise HTTPException(status_code=500, detail="Missing user or database context")
            
            # Check access
            service = UnifiedSubscriptionService(db)
            access_result = await service.check_feature_access(
                user.user_id,
                feature,
                amount
            )
            
            if not access_result.allowed:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=402,  # Payment Required
                    detail=access_result.to_dict()
                )
            
            # Track usage after successful execution
            result = await func(*args, **kwargs)
            await service.track_feature_use(user.user_id, feature, amount)
            
            return result
        
        return wrapper
    return decorator
