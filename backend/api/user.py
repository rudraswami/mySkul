"""
User profile router for profile management and user operations
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone

from models.core import User, ProfileUpdateRequest
from dependencies import get_current_user, get_database


# Router instance
router = APIRouter(prefix="/user", tags=["user"])


@router.get("/profile")
async def get_user_profile(user: User = Depends(get_current_user)):
    """Get user profile"""
    return {
        "user_id": user.user_id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": getattr(user, 'phone', ''),
        "exam_type": user.exam_type,
        "grade": user.grade,
        "target_year": user.target_year,
        "current_standard": getattr(user, 'current_standard', ''),
        "institution": getattr(user, 'institution', ''),
        "subscription_type": user.subscription_type,
        "created_at": getattr(user, 'created_at', None)
    }


@router.put("/profile")
async def update_user_profile(
    profile_update: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Update user profile"""
    try:
        # Prepare update data
        update_data = {}
        
        if profile_update.full_name is not None:
            update_data["full_name"] = profile_update.full_name
        if profile_update.email is not None:
            update_data["email"] = profile_update.email
        if profile_update.phone is not None:
            update_data["phone"] = profile_update.phone
        if profile_update.exam_type is not None:
            update_data["exam_type"] = profile_update.exam_type
        if profile_update.target_year is not None:
            update_data["target_year"] = profile_update.target_year
        if profile_update.current_standard is not None:
            update_data["current_standard"] = profile_update.current_standard
        if profile_update.institution is not None:
            update_data["institution"] = profile_update.institution
        
        # Add updated timestamp
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        # Update user in database
        result = await db.users.update_one(
            {"user_id": user.user_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No changes made to profile")
        
        # Get updated user data
        updated_user = await db.users.find_one({"user_id": user.user_id})
        if not updated_user:
            raise HTTPException(status_code=404, detail="Updated user not found")
        
        return {
            "message": "Profile updated successfully",
            "user": {
                "user_id": updated_user["user_id"],
                "full_name": updated_user.get("full_name"),
                "email": updated_user.get("email"),
                "phone": updated_user.get("phone", ""),
                "exam_type": updated_user.get("exam_type"),
                "target_year": updated_user.get("target_year"),
                "current_standard": updated_user.get("current_standard", ""),
                "institution": updated_user.get("institution", ""),
                "subscription_type": updated_user.get("subscription_type")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")