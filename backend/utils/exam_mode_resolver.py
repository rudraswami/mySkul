"""
Centralized Exam Mode Resolution Utility
=========================================

This module provides a single source of truth for determining a user's exam mode.
Prevents hardcoded "JEE" defaults throughout the system.

Priority Order:
1. Request parameter (explicit user choice)
2. User profile (target_exam, exam_type, exam_mode)
3. Session context
4. Default to "General" (NOT "JEE")
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


async def resolve_exam_mode(
    request_exam_mode: Optional[str] = None,
    user_id: Optional[str] = None,
    db_client = None,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Resolve exam mode with proper priority fallback.
    
    Args:
        request_exam_mode: Exam mode from API request
        user_id: User ID to fetch profile
        db_client: Database client for profile lookup
        context: Additional context (session, etc.)
    
    Returns:
        str: Resolved exam mode (never None)
    
    Examples:
        >>> await resolve_exam_mode(request_exam_mode="NEET")
        "NEET"
        
        >>> await resolve_exam_mode(user_id="user123", db_client=db)
        "JEE"  # From user profile
        
        >>> await resolve_exam_mode()
        "General"  # Default fallback
    """
    
    # Priority 1: Explicit request parameter
    if request_exam_mode and request_exam_mode.strip():
        logger.debug(f"✅ Exam mode from request: {request_exam_mode}")
        return request_exam_mode.strip()
    
    # Priority 2: User profile
    if user_id and db_client:
        try:
            user_doc = await db_client.users.find_one({"user_id": user_id})
            if user_doc:
                # Try multiple field names (backward compatibility)
                exam_mode = (
                    user_doc.get('target_exam') or
                    user_doc.get('exam_type') or
                    user_doc.get('exam_mode') or
                    user_doc.get('education_standard')
                )
                
                if exam_mode and exam_mode.strip():
                    logger.debug(f"✅ Exam mode from user profile: {exam_mode}")
                    return exam_mode.strip()
        except Exception as e:
            logger.warning(f"Failed to fetch user profile for exam mode: {e}")
    
    # Priority 3: Context (session, etc.)
    if context:
        exam_mode = context.get('exam_mode') or context.get('exam_type')
        if exam_mode and exam_mode.strip():
            logger.debug(f"✅ Exam mode from context: {exam_mode}")
            return exam_mode.strip()
    
    # Priority 4: Default (General, not JEE!)
    logger.debug("⚠️ No exam mode found, using default: General")
    return "General"


def get_exam_mode_from_request(request, default: str = "General") -> str:
    """
    Extract exam mode from FastAPI request object.
    
    Handles multiple field names for backward compatibility.
    
    Args:
        request: FastAPI request object
        default: Default value if not found
    
    Returns:
        str: Exam mode
    """
    return (
        getattr(request, 'exam_mode', None) or
        getattr(request, 'exam_type', None) or
        default
    )


# Exam mode validation
VALID_EXAM_MODES = {
    "JEE", "NEET", "UPSC", "CAT", "GATE",
    "CBSE", "ICSE", "State Board",
    "General", "Other"
}


def validate_exam_mode(exam_mode: str) -> str:
    """
    Validate and normalize exam mode.
    
    Args:
        exam_mode: Raw exam mode string
    
    Returns:
        str: Validated exam mode
    """
    if not exam_mode:
        return "General"
    
    # Normalize
    exam_mode = exam_mode.strip().upper()
    
    # Check if valid
    if exam_mode in VALID_EXAM_MODES:
        return exam_mode
    
    # Fuzzy matching for common variations
    exam_mode_lower = exam_mode.lower()
    if "jee" in exam_mode_lower:
        return "JEE"
    elif "neet" in exam_mode_lower:
        return "NEET"
    elif "upsc" in exam_mode_lower:
        return "UPSC"
    elif "cbse" in exam_mode_lower or "board" in exam_mode_lower:
        return "CBSE"
    
    # Unknown - use General
    logger.warning(f"Unknown exam mode '{exam_mode}', using 'General'")
    return "General"


