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
from datetime import datetime, timezone
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









































