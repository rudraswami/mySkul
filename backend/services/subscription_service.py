"""
Subscription service for managing user subscriptions, plans, and access control
"""
import json
import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorClient
from models.subscription import UserSubscription, UsageTracking

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Hybrid subscription system with AI-guided upsells following 'Pay for Progress, Not Access' philosophy"""
    
    def __init__(self, db: AsyncIOMotorClient, config_path: Optional[str] = None):
        self.db = db
        self.plan_config = None
        self.config_path = config_path or str(Path(__file__).parent.parent / 'planConfig.json')
    
    async def load_plan_config(self):
        """Load plan configuration from JSON file"""
        if self.plan_config is None:
            # Try AI Tutor config first, fallback to legacy
            ai_tutor_config_path = str(Path(__file__).parent.parent / 'planConfig_ai_tutor.json')
            if Path(ai_tutor_config_path).exists():
                with open(ai_tutor_config_path, 'r') as f:
                    self.plan_config = json.load(f)
                logger.info("✅ Loaded AI Tutor subscription configuration")
            else:
                with open(self.config_path, 'r') as f:
                    self.plan_config = json.load(f)
                logger.info("✅ Loaded legacy subscription configuration")
        return self.plan_config
    
    async def get_user_subscription_info(self, user_id: str) -> Dict[str, Any]:
        """Get current user subscription information"""
        try:
            # Get user subscription
            subscription = await self.db.user_subscriptions.find_one({"user_id": user_id})
            
            if not subscription:
                # Create default FREE subscription
                await self.create_default_subscription(user_id)
                subscription = await self.db.user_subscriptions.find_one({"user_id": user_id})
            
            plan_config = await self.load_plan_config()
            tier = subscription.get('plan_name', 'FREE').upper()
            
            # Get daily usage
            daily_usage = await self.get_daily_usage(user_id)
            
            return {
                "subscription_tier": tier,
                "plan_info": plan_config.get(tier, plan_config['FREE']),
                "daily_usage": daily_usage,
                "subscription_status": subscription.get('status', 'active'),
                "current_period_end": subscription.get('current_period_end'),
                "auto_renew": subscription.get('auto_renew', True)
            }
            
        except Exception as e:
            logger.error(f"Get subscription info error: {str(e)}")
            # Return default FREE tier on error
            plan_config = await self.load_plan_config()
            return {
                "subscription_tier": "FREE",
                "plan_info": plan_config['FREE'],
                "daily_usage": {},
                "subscription_status": "active"
            }
    
    async def create_default_subscription(self, user_id: str):
        """Create default FREE subscription for new users"""
        subscription = UserSubscription(
            user_id=user_id,
            plan_id="free_plan",
            plan_name="FREE"
        )
        
        subscription_dict = subscription.dict()
        subscription_dict['current_period_start'] = subscription_dict['current_period_start'].isoformat()
        subscription_dict['current_period_end'] = subscription_dict['current_period_end'].isoformat()
        subscription_dict['created_at'] = subscription_dict['created_at'].isoformat()
        subscription_dict['updated_at'] = subscription_dict['updated_at'].isoformat()
        
        await self.db.user_subscriptions.insert_one(subscription_dict)
    
    async def check_feature_access(self, user_id: str, feature_name: str) -> Dict[str, Any]:
        """Check if user has access to a specific feature and return upsell info if needed"""
        try:
            sub_info = await self.get_user_subscription_info(user_id)
            tier = sub_info['subscription_tier']
            plan_features = sub_info['plan_info']['features']
            
            # Get appropriate usage based on feature type (daily/weekly/monthly)
            if "monthly" in feature_name:
                # Monthly features (e.g., ai_sessions_monthly)
                current_usage = await self.get_monthly_usage(user_id, feature_name)
            elif "weekly" in feature_name:
                # Weekly features (e.g., mock_tests_weekly)
                current_usage = await self.get_weekly_usage(user_id, feature_name)
            else:
                # Daily features (e.g., mentor_tips_daily, auto_note_uploads_daily)
                daily_usage = sub_info['daily_usage']
                current_usage = daily_usage.get(feature_name, 0)
            
            # Get feature limit from plan configuration
            feature_limit = plan_features.get(feature_name)
            
            if feature_limit == "unlimited":
                return {
                    "has_access": True,
                    "is_unlimited": True,
                    "current_usage": current_usage,
                    "used": current_usage,
                    "limit": -1,
                    "remaining": -1,
                    "upgrade_needed": False
                }
            elif feature_limit == "locked":
                # Feature is locked, user needs to upgrade
                upsell_info = await self.generate_upsell_message(
                    user_id, feature_name, tier, "feature_locked"
                )
                return {
                    "has_access": False,
                    "reason": "feature_locked",
                    "current_usage": 0,
                    "used": 0,
                    "limit": 0,
                    "remaining": 0,
                    "upgrade_needed": True,
                    "upsell_info": upsell_info
                }
            elif isinstance(feature_limit, int):
                # Feature has daily/weekly limit
                remaining = max(0, feature_limit - current_usage)
                has_access = remaining > 0
                
                if not has_access:
                    upsell_info = await self.generate_upsell_message(
                        user_id, feature_name, tier, "limit_reached"
                    )
                    return {
                        "has_access": False,
                        "reason": "limit_reached",
                        "current_usage": current_usage,
                        "used": current_usage,
                        "limit": feature_limit,
                        "remaining": 0,
                        "upgrade_needed": True,
                        "upsell_info": upsell_info
                    }
                else:
                    return {
                        "has_access": True,
                        "current_usage": current_usage,
                        "used": current_usage,
                        "limit": feature_limit,
                        "remaining": remaining,
                        "upgrade_needed": False
                    }
            else:
                # Unknown feature limit type, deny access
                return {
                    "has_access": False,
                    "reason": "unknown_limit_type",
                    "current_usage": current_usage,
                    "used": current_usage,
                    "limit": 0,
                    "remaining": 0,
                    "upgrade_needed": True
                }
                
        except Exception as e:
            logger.error(f"Check feature access error: {str(e)}")
            # Default to no access on error
            return {
                "has_access": False,
                "reason": "error",
                "current_usage": 0,
                "used": 0,
                "limit": 0,
                "remaining": 0,
                "upgrade_needed": True
            }
    
    async def get_daily_usage(self, user_id: str) -> Dict[str, int]:
        """Get today's feature usage for a user"""
        try:
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            
            usage_docs = await self.db.usage_tracking.find({
                "user_id": user_id,
                "usage_date": {"$gte": today, "$lt": tomorrow}
            }).to_list(length=None)
            
            usage_dict = {}
            for doc in usage_docs:
                feature_name = doc['feature_name']
                usage_dict[feature_name] = doc.get('usage_count', 0)
            
            return usage_dict
            
        except Exception as e:
            logger.error(f"Get daily usage error: {str(e)}")
            return {}
    
    async def get_weekly_usage(self, user_id: str, feature_name: str) -> int:
        """Get current week's usage for a specific feature"""
        try:
            # Get start of current week (Monday)
            today = datetime.now(timezone.utc).date()
            week_start = today - timedelta(days=today.weekday())
            week_start_dt = datetime.combine(week_start, datetime.min.time()).replace(tzinfo=timezone.utc)
            
            usage_doc = await self.db.usage_tracking.find_one({
                "user_id": user_id,
                "feature_name": feature_name,
                "usage_date": {"$gte": week_start_dt}
            })
            
            return usage_doc.get('usage_count', 0) if usage_doc else 0
            
        except Exception as e:
            logger.error(f"Get weekly usage error: {str(e)}")
            return 0
    
    async def track_usage(self, user_id: str, feature_name: str, increment: int = 1):
        """Track feature usage for a user"""
        try:
            now = datetime.now(timezone.utc)
            
            # For weekly features, use start of week as usage date
            if "weekly" in feature_name:
                today = now.date()
                week_start = today - timedelta(days=today.weekday())
                usage_date = datetime.combine(week_start, datetime.min.time()).replace(tzinfo=timezone.utc)
            else:
                # For daily features, use start of day
                usage_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Upsert usage tracking
            await self.db.usage_tracking.update_one(
                {
                    "user_id": user_id,
                    "feature_name": feature_name,
                    "usage_date": usage_date
                },
                {
                    "$inc": {"usage_count": increment},
                    "$set": {"updated_at": now}
                },
                upsert=True
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Track usage error: {str(e)}")
            return False
    
    async def generate_upsell_message(self, user_id: str, feature_name: str, current_tier: str, reason: str) -> Dict[str, Any]:
        """Generate AI-powered upsell message"""
        try:
            plan_config = await self.load_plan_config()
            
            # Determine target plan
            if current_tier == "FREE":
                target_plan = "PREMIUM"
            else:
                target_plan = "PRO"
            
            # Get growth stats (simplified version)
            growth_stats = {
                "accuracy_improvement": 15,
                "efficiency_gain": 20,
                "total_study_hours": 45
            }
            
            # Generate contextual messages
            feature_benefits = {
                "ai_conversations": {
                    "mentor_message": "🎯 You're asking great questions! Unlock unlimited AI conversations to dive deeper into complex topics and get personalized explanations.",
                    "professor_message": "📚 Your curiosity is commendable. Premium access allows continuous dialogue for thorough understanding of challenging concepts."
                },
                "mock_tests_weekly": {
                    "mentor_message": "⚡ You're on fire with practice! Upgrade to take unlimited mock tests and accelerate your preparation.",
                    "professor_message": "📈 Consistent testing leads to better results. Premium membership removes all test limitations."
                }
            }
            
            default_benefit = {
                "mentor_message": f"🚀 Ready to level up your {feature_name.replace('_', ' ')} experience?",
                "professor_message": f"📊 Enhanced access to {feature_name.replace('_', ' ')} will optimize your learning journey."
            }
            
            benefits = feature_benefits.get(feature_name, default_benefit)
            
            return {
                "mentor_message": benefits["mentor_message"],
                "professor_message": benefits["professor_message"],
                "target_plan": target_plan,
                "growth_stats": growth_stats,
                "feature_name": feature_name,
                "reason": reason,
                "interaction_tracking": {
                    "upsell_type": "feature_limit",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "user_tier": current_tier
                }
            }
            
        except Exception as e:
            logger.error(f"Generate upsell message error: {str(e)}")
            return {
                "mentor_message": "🌟 Unlock your full potential with our premium features!",
                "professor_message": "📈 Upgrade for enhanced learning capabilities.",
                "target_plan": "PREMIUM",
                "growth_stats": {},
                "feature_name": feature_name,
                "reason": reason
            }

    # ============= AI TUTOR SPECIFIC METHODS =============
    
    async def check_ai_tutor_access(self, user_id: str) -> Dict[str, Any]:
        """
        Check AI Tutor session access with 80% warning threshold
        Returns: {allowed, remaining, total, usage_percent, needs_upgrade, upgrade_hint}
        """
        try:
            sub_info = await self.get_user_subscription_info(user_id)
            tier = sub_info['subscription_tier']
            plan_features = sub_info['plan_info']['features']
            
            # Get monthly AI session limit
            session_limit = plan_features.get('ai_sessions_monthly')
            
            if session_limit == "unlimited":
                return {
                    "allowed": True,
                    "remaining": "unlimited",
                    "total": "unlimited",
                    "usage_percent": 0,
                    "needs_upgrade": False,
                    "upgrade_hint": None,
                    "current_tier": tier
                }
            
            # Get current month usage
            current_usage = await self.get_monthly_ai_tutor_usage(user_id)
            remaining = max(0, session_limit - current_usage)
            usage_percent = (current_usage / session_limit * 100) if session_limit > 0 else 100
            
            # Check if upgrade needed
            needs_upgrade = current_usage >= session_limit
            warning_threshold = usage_percent >= 80
            
            # Generate upgrade hint if needed
            upgrade_hint = None
            if needs_upgrade or warning_threshold:
                plan_config = await self.load_plan_config()
                upgrade_messages = plan_config[tier].get('upgrade_messages', {})
                
                if needs_upgrade:
                    upgrade_hint = {
                        "type": "limit_reached",
                        "mentor_message": upgrade_messages.get('mentor', '').format(
                            usage=current_usage,
                            limit=session_limit
                        ),
                        "professor_message": upgrade_messages.get('professor', ''),
                        "cta": upgrade_messages.get('cta', 'Upgrade now'),
                        "target_plan": self._get_next_tier(tier)
                    }
                elif warning_threshold:
                    upgrade_hint = {
                        "type": "approaching_limit",
                        "message": f"⚡ You've used {current_usage}/{session_limit} AI sessions ({usage_percent:.0f}%). Consider upgrading soon!",
                        "target_plan": self._get_next_tier(tier)
                    }
            
            return {
                "allowed": not needs_upgrade,
                "remaining": remaining,
                "total": session_limit,
                "current_usage": current_usage,
                "usage_percent": round(usage_percent, 1),
                "needs_upgrade": needs_upgrade,
                "upgrade_hint": upgrade_hint,
                "current_tier": tier
            }
            
        except Exception as e:
            logger.error(f"Check AI Tutor access error: {str(e)}")
            # Fail open - allow access but log error
            return {
                "allowed": True,
                "remaining": 0,
                "total": 0,
                "usage_percent": 0,
                "needs_upgrade": False,
                "upgrade_hint": None,
                "current_tier": "FREE",
                "error": str(e)
            }
    
    async def check_mentor_tip_access(self, user_id: str) -> Dict[str, Any]:
        """Check if user can access mentor tips today"""
        try:
            sub_info = await self.get_user_subscription_info(user_id)
            tier = sub_info['subscription_tier']
            plan_features = sub_info['plan_info']['features']
            
            # Get daily mentor tip limit
            tip_limit = plan_features.get('mentor_tips_daily', 0)
            
            if tip_limit == "unlimited":
                return {
                    "allowed": True,
                    "remaining": "unlimited",
                    "total": "unlimited",
                    "current_tier": tier
                }
            
            if tip_limit == 0:
                return {
                    "allowed": False,
                    "remaining": 0,
                    "total": 0,
                    "needs_upgrade": True,
                    "upgrade_hint": "Upgrade to Scholar or higher for mentor tips",
                    "current_tier": tier
                }
            
            # Get today's usage
            daily_usage = sub_info['daily_usage']
            current_usage = daily_usage.get('mentor_tips_daily', 0)
            remaining = max(0, tip_limit - current_usage)
            
            return {
                "allowed": current_usage < tip_limit,
                "remaining": remaining,
                "total": tip_limit,
                "current_usage": current_usage,
                "current_tier": tier
            }
            
        except Exception as e:
            logger.error(f"Check mentor tip access error: {str(e)}")
            return {"allowed": False, "error": str(e)}
    
    async def get_monthly_ai_tutor_usage(self, user_id: str) -> int:
        """Get current month's AI Tutor session usage"""
        try:
            # Get start of current month
            now = datetime.now(timezone.utc)
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Count AI Tutor sessions this month
            usage_docs = await self.db.usage_tracking.find({
                "user_id": user_id,
                "feature_name": "ai_tutor_session",
                "usage_date": {"$gte": month_start}
            }).to_list(length=None)
            
            total_usage = sum(doc.get('usage_count', 0) for doc in usage_docs)
            return total_usage
            
        except Exception as e:
            logger.error(f"Get monthly AI Tutor usage error: {str(e)}")
            return 0
    
    async def track_ai_tutor_session(self, user_id: str):
        """Track an AI Tutor session usage"""
        try:
            now = datetime.now(timezone.utc)
            # Use start of day as usage date for tracking
            usage_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            await self.db.usage_tracking.update_one(
                {
                    "user_id": user_id,
                    "feature_name": "ai_tutor_session",
                    "usage_date": usage_date
                },
                {
                    "$inc": {"usage_count": 1},
                    "$set": {"updated_at": now}
                },
                upsert=True
            )
            
            logger.info(f"✅ Tracked AI Tutor session for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Track AI Tutor session error: {str(e)}")
            return False
    
    async def track_mentor_tip_usage(self, user_id: str):
        """Track mentor tip usage (daily limit)"""
        return await self.track_usage(user_id, "mentor_tips_daily", increment=1)
    
    def _get_next_tier(self, current_tier: str) -> str:
        """Get the next subscription tier for upgrade suggestions"""
        tier_hierarchy = ["FREE", "STARTER", "SCHOLAR", "ACHIEVER", "LEGEND"]
        try:
            current_index = tier_hierarchy.index(current_tier.upper())
            if current_index < len(tier_hierarchy) - 1:
                return tier_hierarchy[current_index + 1]
            return current_tier  # Already at max tier
        except ValueError:
            return "STARTER"  # Default next tier
