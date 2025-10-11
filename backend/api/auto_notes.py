"""
Auto-Notes router for session management, audio processing, and note generation
"""
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from typing import Dict, Any, List

from models.core import User
from models.auto_notes import (
    NoteSessionRequest, EndSessionRequest, ExplainPointRequest,
    GenerateFlashcardsRequest, CreateSpacedRepetitionRequest,
    ReviewCardRequest, SemanticSearchRequest, ClassSeriesRequest
)
from services.auto_notes_service import AutoNotesService
from dependencies import get_current_user, get_database

# Router instance
router = APIRouter(prefix="/auto-notes", tags=["auto-notes"])


# Dependency to get auto-notes service
async def get_auto_notes_service(db = Depends(get_database)) -> AutoNotesService:
    """Get auto-notes service instance"""
    return AutoNotesService(db)


@router.post("/start-session")
async def start_session(
    request: NoteSessionRequest,
    user: User = Depends(get_current_user),
    service: AutoNotesService = Depends(get_auto_notes_service)
):
    """Start a new auto-note session"""
    try:
        result = await service.create_session(
            user_id=user.user_id,
            title=request.title,
            subject=request.subject
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")


@router.get("/sessions")
async def get_sessions(
    user: User = Depends(get_current_user),
    service: AutoNotesService = Depends(get_auto_notes_service)
):
    """Get all sessions for the current user"""
    try:
        sessions = await service.get_user_sessions(user.user_id)
        return {"sessions": sessions, "total": len(sessions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sessions: {str(e)}")


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    user: User = Depends(get_current_user),
    service: AutoNotesService = Depends(get_auto_notes_service)
):
    """Get a specific session"""
    try:
        session = await service.get_session(session_id, user.user_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")


@router.get("/analytics")
async def get_analytics(
    user: User = Depends(get_current_user),
    service: AutoNotesService = Depends(get_auto_notes_service)
):
    """Get analytics for user's auto-note sessions"""
    try:
        analytics = await service.get_session_analytics(user.user_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")


@router.get("/class-series")
async def get_class_series(
    user: User = Depends(get_current_user),
    service: AutoNotesService = Depends(get_auto_notes_service)
):
    """Get all class series for the user"""
    try:
        series = await service.get_class_series(user.user_id)
        return {"series": series, "total": len(series)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get class series: {str(e)}")


# Note: Complex endpoints like upload-audio, process-audio, end-session, etc.
# remain in server.py for now as they involve heavy audio processing logic.
# These can be migrated incrementally in future iterations.
