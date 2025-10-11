"""
Auto-Notes service for session management, audio processing, and note generation
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from models.auto_notes import AutoNoteSession, NoteSessionRequest

logger = logging.getLogger(__name__)


class AutoNotesService:
    """Service for managing auto-note sessions and processing"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def create_session(self, user_id: str, title: str, subject: str) -> Dict[str, Any]:
        """Create a new auto-note session"""
        try:
            session = AutoNoteSession(
                user_id=user_id,
                subject=subject,
                session_name=title,
                source_type="live",
                status="active"
            )
            
            # Save to database
            session_dict = session.dict()
            # Convert datetime to ISO string for MongoDB
            if isinstance(session_dict.get('created_at'), datetime):
                session_dict['created_at'] = session_dict['created_at'].isoformat()
            
            await self.db.auto_note_sessions.insert_one(session_dict)
            
            return {
                "session_id": session.session_id,
                "session_name": session.session_name,
                "subject": session.subject,
                "source_type": session.source_type,
                "status": session.status,
                "created_at": session_dict['created_at'],
                "message": "Auto-Note session started successfully"
            }
            
        except Exception as e:
            logger.error(f"Create session error: {str(e)}")
            raise Exception(f"Failed to create session: {str(e)}")
    
    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a user"""
        try:
            sessions = await self.db.auto_note_sessions.find(
                {"user_id": user_id}
            ).sort("created_at", -1).to_list(length=None)
            
            # Clean up MongoDB fields
            for session in sessions:
                if '_id' in session:
                    del session['_id']
            
            return sessions
            
        except Exception as e:
            logger.error(f"Get user sessions error: {str(e)}")
            return []
    
    async def get_session(self, session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific session"""
        try:
            session = await self.db.auto_note_sessions.find_one({
                "session_id": session_id,
                "user_id": user_id
            })
            
            if session and '_id' in session:
                del session['_id']
            
            return session
            
        except Exception as e:
            logger.error(f"Get session error: {str(e)}")
            return None
    
    async def get_session_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics for user's auto-note sessions"""
        try:
            total_sessions = await self.db.auto_note_sessions.count_documents({"user_id": user_id})
            completed_sessions = await self.db.auto_note_sessions.count_documents({
                "user_id": user_id,
                "status": "completed"
            })
            
            return {
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "active_sessions": total_sessions - completed_sessions
            }
            
        except Exception as e:
            logger.error(f"Get analytics error: {str(e)}")
            return {"total_sessions": 0, "completed_sessions": 0, "active_sessions": 0}
    
    async def get_class_series(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all class series for a user"""
        try:
            series = await self.db.class_series.find(
                {"user_id": user_id}
            ).to_list(length=None)
            
            # Clean up MongoDB fields
            for s in series:
                if '_id' in s:
                    del s['_id']
            
            return series
            
        except Exception as e:
            logger.error(f"Get class series error: {str(e)}")
            return []
