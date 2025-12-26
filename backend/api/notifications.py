"""
🔔 Notifications API - Real-time Notification Delivery
========================================================

Endpoints for the frontend to:
- Poll for new notifications
- Mark notifications as read
- Get notification history
- Manage notification preferences

This is CRITICAL for reminders to work!
Without this, scheduled reminders have no way to reach the user.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from dependencies import get_current_user, get_database
from models.core import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class NotificationResponse(BaseModel):
    """Single notification"""
    notification_id: str
    title: str
    message: str
    type: str
    data: dict = {}
    read: bool
    created_at: str
    action: Optional[dict] = None


class NotificationsListResponse(BaseModel):
    """List of notifications"""
    notifications: List[NotificationResponse]
    unread_count: int
    total: int


class MarkReadRequest(BaseModel):
    """Mark notification(s) as read"""
    notification_ids: List[str] = None  # If None, mark all as read


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/", response_model=NotificationsListResponse)
async def get_notifications(
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    🔔 Get user's notifications
    
    This is polled by the frontend to show reminder notifications.
    
    Args:
        limit: Max notifications to return
        unread_only: Only return unread notifications
        
    Returns:
        List of notifications with unread count
    """
    try:
        query = {"user_id": user.user_id}
        if unread_only:
            query["read"] = False
        
        # Get notifications (newest first)
        cursor = db.user_notifications.find(query).sort("created_at", -1).limit(limit)
        notifications_list = await cursor.to_list(length=limit)
        
        # Get unread count
        unread_count = await db.user_notifications.count_documents({
            "user_id": user.user_id,
            "read": False
        })
        
        # Format response
        notifications = []
        for n in notifications_list:
            created_at = n.get("created_at")
            if created_at:
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                created_at_str = created_at.isoformat()
            else:
                created_at_str = datetime.now(timezone.utc).isoformat()
            
            notifications.append(NotificationResponse(
                notification_id=n.get("notification_id", str(n.get("_id", ""))),
                title=n.get("title", "Notification"),
                message=n.get("message", ""),
                type=n.get("type", "general"),
                data=n.get("data", {}),
                read=n.get("read", False),
                created_at=created_at_str,
                action=n.get("action")
            ))
        
        logger.info(f"📬 Fetched {len(notifications)} notifications for {user.user_id}, unread: {unread_count}")
        
        return NotificationsListResponse(
            notifications=notifications,
            unread_count=unread_count,
            total=len(notifications)
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to get notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/poll")
async def poll_notifications(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    🔄 Quick poll for new notifications (lightweight)
    
    Frontend should call this every 30-60 seconds to check for new notifications.
    Returns only unread count and newest unread notification.
    
    Returns:
        unread_count: Number of unread notifications
        latest: Latest unread notification (if any)
    """
    try:
        # Get unread count
        unread_count = await db.user_notifications.count_documents({
            "user_id": user.user_id,
            "read": False
        })
        
        # Get latest unread notification
        latest = None
        if unread_count > 0:
            latest_doc = await db.user_notifications.find_one(
                {"user_id": user.user_id, "read": False},
                sort=[("created_at", -1)]
            )
            if latest_doc:
                created_at = latest_doc.get("created_at")
                if created_at and created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                
                latest = {
                    "notification_id": latest_doc.get("notification_id", str(latest_doc.get("_id", ""))),
                    "title": latest_doc.get("title", ""),
                    "message": latest_doc.get("message", ""),
                    "type": latest_doc.get("type", "reminder"),
                    "created_at": created_at.isoformat() if created_at else None
                }
        
        return {
            "unread_count": unread_count,
            "latest": latest,
            "has_new": unread_count > 0
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to poll notifications: {e}")
        return {"unread_count": 0, "latest": None, "has_new": False}


@router.post("/mark-read")
async def mark_notifications_read(
    request: MarkReadRequest,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    ✅ Mark notification(s) as read
    
    Args:
        notification_ids: List of IDs to mark as read, or None to mark all
        
    Returns:
        Number of notifications marked as read
    """
    try:
        query = {"user_id": user.user_id}
        
        if request.notification_ids:
            query["notification_id"] = {"$in": request.notification_ids}
        
        result = await db.user_notifications.update_many(
            query,
            {"$set": {"read": True, "read_at": datetime.now(timezone.utc)}}
        )
        
        logger.info(f"✅ Marked {result.modified_count} notifications as read for {user.user_id}")
        
        return {
            "success": True,
            "marked_count": result.modified_count
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to mark notifications as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    🗑️ Delete a notification
    """
    try:
        result = await db.user_notifications.delete_one({
            "user_id": user.user_id,
            "notification_id": notification_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {"success": True, "deleted": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/")
async def clear_all_notifications(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    🗑️ Clear all notifications for user
    """
    try:
        result = await db.user_notifications.delete_many({
            "user_id": user.user_id
        })
        
        logger.info(f"🗑️ Cleared {result.deleted_count} notifications for {user.user_id}")
        
        return {
            "success": True,
            "deleted_count": result.deleted_count
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to clear notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/old")
async def clear_old_notifications(
    hours: int = Query(24, ge=1, le=168, description="Clear notifications older than N hours"),
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    🧹 Clear old notifications (older than specified hours)
    
    Useful for cleaning up stale notifications and getting fresh AI-generated content.
    Default: 24 hours. Max: 168 hours (7 days).
    """
    try:
        threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        result = await db.user_notifications.delete_many({
            "user_id": user.user_id,
            "created_at": {"$lt": threshold}
        })
        
        logger.info(f"🧹 Cleared {result.deleted_count} old notifications (>{hours}h) for {user.user_id}")
        
        return {
            "success": True,
            "deleted_count": result.deleted_count,
            "cleared_older_than": f"{hours} hours"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to clear old notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 🎯 OUTCOME TRACKING - For Mentor Companion Learning
# ============================================================================

class OutcomeRequest(BaseModel):
    """Track notification outcome"""
    notification_id: str
    outcome: str  # "clicked" | "dismissed" | "snoozed" | "studied"
    details: Optional[dict] = None


@router.post("/outcome")
async def track_notification_outcome(
    request: OutcomeRequest,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    📊 Track notification outcome for Mentor Companion learning.
    
    This helps the AI learn what works and what doesn't for each student:
    - clicked: User engaged with notification
    - dismissed: User dismissed without action
    - snoozed: User snoozed for later
    - studied: User started studying after notification
    
    The Mentor Companion uses this data to:
    - Adjust notification frequency
    - Calibrate tone and timing
    - Back off when being ignored
    """
    try:
        from services.notification_service import NotificationService
        
        notification_service = NotificationService(db)
        
        success = await notification_service.track_notification_outcome(
            user_id=user.user_id,
            notification_id=request.notification_id,
            outcome=request.outcome,
            details=request.details
        )
        
        if success:
            logger.info(f"📊 Outcome tracked: {request.notification_id} → {request.outcome}")
        
        return {
            "success": success,
            "notification_id": request.notification_id,
            "outcome": request.outcome
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to track outcome: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/effectiveness")
async def get_notification_effectiveness(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    📈 Get notification effectiveness metrics for user.
    
    Returns:
    - response_rate: How often user engages with notifications
    - total_sent_30d: Total notifications in last 30 days
    - ignored_count_48h: Recently ignored notifications
    
    Used by the frontend to show notification health.
    """
    try:
        from services.notification_service import NotificationService
        
        notification_service = NotificationService(db)
        effectiveness = await notification_service.get_notification_effectiveness(user.user_id)
        
        return {
            "success": True,
            **effectiveness
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get effectiveness: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 🎓 PHASE 2: LEARNING PROFILE ENDPOINTS
# ============================================================================

@router.get("/learning-profile")
async def get_learning_profile(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    🧠 Get the Mentor's learning profile for this user.
    
    Shows what the AI has learned about your notification preferences:
    - Best times to notify you
    - What types of notifications work
    - Your preferred tone
    - Engagement patterns
    
    This is transparency into the personalization.
    """
    try:
        from services.intelligent_proactive_mentor import get_proactive_mentor
        
        mentor = await get_proactive_mentor(db)
        profile = await mentor.get_learning_profile(user.user_id)
        
        return {
            "success": True,
            "learning_profile": {
                "engagement_rate": f"{profile.overall_engagement_rate:.0%}",
                "study_conversion_rate": f"{profile.study_conversion_rate:.0%}",
                "preferred_frequency": profile.preferred_frequency,
                "max_daily_notifications": profile.max_daily_notifications,
                "min_hours_between": profile.min_hours_between,
                "best_hour_of_day": profile.best_hour_of_day,
                "preferred_tone": profile.preferred_tone,
                "intent_effectiveness": {
                    "help": f"{profile.help_effectiveness:.0%}",
                    "protect": f"{profile.protect_effectiveness:.0%}",
                    "celebrate": f"{profile.celebrate_effectiveness:.0%}",
                    "guide": f"{profile.guide_effectiveness:.0%}"
                },
                "consecutive_ignores": profile.consecutive_ignores,
                "in_backoff": profile.backoff_until is not None and profile.backoff_until > datetime.now(timezone.utc),
                "total_analyzed": profile.total_notifications_analyzed,
                "last_updated": profile.last_updated.isoformat() if profile.last_updated else None
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get learning profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learn")
async def trigger_learning(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    🔄 Manually trigger learning analysis for your profile.
    
    Analyzes your notification outcomes and updates preferences.
    Usually runs automatically every 30 minutes.
    """
    try:
        from services.intelligent_proactive_mentor import get_proactive_mentor
        
        mentor = await get_proactive_mentor(db)
        profile = await mentor.analyze_and_learn(user.user_id)
        
        return {
            "success": True,
            "message": "Learning analysis complete",
            "notifications_analyzed": profile.total_notifications_analyzed,
            "engagement_rate": f"{profile.overall_engagement_rate:.0%}",
            "preferred_tone": profile.preferred_tone,
            "preferred_frequency": profile.preferred_frequency
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to run learning: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset-learning")
async def reset_learning_profile(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    🔄 Reset learning profile to defaults.
    
    Use this if notifications aren't working well and you want
    the Mentor to re-learn your preferences from scratch.
    """
    try:
        # Delete the learning profile
        result = await db.mentor_learning_profiles.delete_one({
            "user_id": user.user_id
        })
        
        # Clear consecutive ignores from outcomes
        await db.notification_outcomes.delete_many({
            "user_id": user.user_id
        })
        
        logger.info(f"🔄 Learning profile reset for {user.user_id}")
        
        return {
            "success": True,
            "message": "Learning profile reset. The Mentor will re-learn your preferences."
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to reset learning: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 🎯 PHASE 3: EVENT-DRIVEN ENDPOINTS
# ============================================================================

class EventRequest(BaseModel):
    """Emit a mentor event"""
    event_type: str  # "session_ended", "frustration", "confusion", etc.
    topic: Optional[str] = None
    session_duration_minutes: Optional[int] = None
    details: Optional[dict] = None


@router.post("/event")
async def emit_event(
    request: EventRequest,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    📡 Emit a mentor event.
    
    This triggers the Mentor Companion to evaluate if a notification is needed.
    Events are more intelligent than scheduled checks - they respond to
    meaningful moments in the student's journey.
    
    Event types:
    - session_ended: Student finished a study session
    - frustration: Student showing frustration signals
    - confusion: Student seems confused
    - comeback: Student returned after absence
    
    Returns the mentor's decision (notify or not).
    """
    try:
        from services.intelligent_proactive_mentor import emit_mentor_event, MentorEvent
        from services.notification_service import NotificationService
        
        # Map string to enum
        event_map = {
            "session_ended": MentorEvent.SESSION_ENDED,
            "long_session": MentorEvent.LONG_SESSION,
            "inactivity": MentorEvent.INACTIVITY_DETECTED,
            "comeback": MentorEvent.COMEBACK,
            "frustration": MentorEvent.FRUSTRATION_DETECTED,
            "confusion": MentorEvent.CONFUSION_DETECTED,
            "streak_at_risk": MentorEvent.STREAK_AT_RISK,
            "streak_milestone": MentorEvent.STREAK_MILESTONE,
            "exam_approaching": MentorEvent.EXAM_APPROACHING,
            "review_overdue": MentorEvent.REVIEW_OVERDUE
        }
        
        event_type = event_map.get(request.event_type)
        if not event_type:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown event type: {request.event_type}. Valid types: {list(event_map.keys())}"
            )
        
        # Emit the event and get decision
        decision = await emit_mentor_event(
            db_client=db,
            event_type=event_type,
            user_id=user.user_id,
            topic=request.topic,
            session_duration_minutes=request.session_duration_minutes,
            source="api"
        )
        
        if decision is None:
            return {
                "success": True,
                "decision": "no_handler",
                "notification_sent": False
            }
        
        # If approved, send the notification
        if decision.approved and decision.message:
            notification_service = NotificationService(db)
            
            result = await notification_service.send_notification(
                user_id=user.user_id,
                title=decision.message.get("title", ""),
                message=decision.message.get("message", ""),
                notification_type=decision.intent.value,
                priority="medium" if decision.intent.value != "help" else "high",
                data={
                    "event_type": request.event_type,
                    "mentor_intent": decision.intent.value,
                    "mentor_tone": decision.tone,
                    "mentor_confidence": decision.confidence
                },
                skip_policy_check=True
            )
            
            logger.info(f"📡 Event {request.event_type} → notification sent to {user.user_id}")
            
            return {
                "success": True,
                "decision": decision.action,
                "intent": decision.intent.value,
                "tone": decision.tone,
                "notification_sent": True,
                "notification_id": result.get("notification_id")
            }
        else:
            return {
                "success": True,
                "decision": decision.action,
                "reason": decision.reason,
                "notification_sent": False
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to emit event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/types")
async def get_event_types():
    """
    📋 Get list of available mentor event types.
    """
    return {
        "event_types": [
            {
                "type": "session_ended",
                "description": "Student finished a study session",
                "params": ["topic", "session_duration_minutes"]
            },
            {
                "type": "long_session",
                "description": "Student studied for 90+ minutes",
                "params": ["session_duration_minutes"]
            },
            {
                "type": "frustration",
                "description": "Student showing frustration signals",
                "params": ["topic"]
            },
            {
                "type": "confusion",
                "description": "Student seems confused",
                "params": ["topic"]
            },
            {
                "type": "comeback",
                "description": "Student returned after absence",
                "params": []
            },
            {
                "type": "streak_at_risk",
                "description": "Student's streak is at risk",
                "params": []
            },
            {
                "type": "streak_milestone",
                "description": "Student hit a streak milestone",
                "params": []
            },
            {
                "type": "review_overdue",
                "description": "Spaced repetition reviews are overdue",
                "params": []
            }
        ]
    }


# ============================================================================
# REMINDERS ENDPOINTS (for debugging/testing)
# ============================================================================

@router.get("/reminders")
async def get_user_reminders(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    ⏰ Get all pending reminders for user
    
    This endpoint helps debug why reminders aren't triggering.
    """
    try:
        from services.reminder_scheduler import ReminderScheduler
        
        scheduler = ReminderScheduler(db)
        
        # Get all user reminders
        reminders = await scheduler.get_user_reminders(user.user_id, limit=50)
        
        # Also get pending ones
        pending_reminders = await scheduler.get_user_reminders(
            user.user_id, 
            status="pending",
            limit=20
        )
        
        # Format for display
        formatted = []
        for r in reminders:
            scheduled_time = r.get("scheduled_time")
            if scheduled_time:
                # Convert to IST for display
                if scheduled_time.tzinfo is None:
                    scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
                ist_time = scheduled_time.astimezone(timezone(timedelta(hours=5, minutes=30)))
                time_str = ist_time.strftime("%Y-%m-%d %I:%M %p IST")
            else:
                time_str = "N/A"
            
            formatted.append({
                "reminder_id": r.get("reminder_id"),
                "topic": r.get("topic"),
                "message": r.get("custom_message"),
                "scheduled_time_utc": r.get("scheduled_time").isoformat() if r.get("scheduled_time") else None,
                "scheduled_time_ist": time_str,
                "status": r.get("status"),
                "created_at": r.get("created_at").isoformat() if r.get("created_at") else None
            })
        
        return {
            "total_reminders": len(reminders),
            "pending_count": len(pending_reminders),
            "reminders": formatted,
            "current_time_utc": datetime.now(timezone.utc).isoformat(),
            "current_time_ist": datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d %I:%M %p IST")
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get reminders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reminders/test")
async def test_reminder_notification(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    🧪 Send a test notification immediately
    
    This helps verify that the notification system is working.
    """
    try:
        from services.notification_service import NotificationService
        
        notification_service = NotificationService(db)
        
        result = await notification_service.send_notification(
            user_id=user.user_id,
            title="⏰ Test Reminder",
            message="This is a test notification! If you see this, notifications are working! 🎉",
            notification_type="reminder",
            priority="high",
            data={"test": True, "timestamp": datetime.now(timezone.utc).isoformat()}
        )
        
        logger.info(f"🧪 Test notification sent to {user.user_id}: {result}")
        
        return {
            "success": True,
            "message": "Test notification sent! Check the notification bell.",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to send test notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))





























































