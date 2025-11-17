"""
Memory Service - Short-Term Conversation Context Management
Handles rolling conversation windows and context retrieval
"""
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Manages short-term conversation context for AI Tutor
    
    Features:
    - Rolling window of last N messages
    - Session-based context management
    - Context trimming for token budget
    - Fast retrieval for real-time responses
    """
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.default_window_size = 10
        self.max_messages_per_session = 50
    
    async def get_conversation_context(
        self,
        session_id: str,
        user_id: str,
        window_size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get last N messages for context
        
        Args:
            session_id: Current chat session
            user_id: User ID (for security)
            window_size: Number of messages to retrieve (default: 10)
        
        Returns:
            List of messages in chronological order
        """
        try:
            window = window_size or self.default_window_size
            
            # Get last N messages
            messages = await self.db.chat_messages.find({
                "session_id": session_id,
                "user_id": user_id
            }).sort("timestamp", -1).limit(window).to_list(None)
            
            # Reverse to chronological order
            messages = list(reversed(messages))
            
            logger.info(f"📜 Retrieved {len(messages)} messages for context")
            return messages
            
        except Exception as e:
            logger.error(f"❌ Failed to get conversation context: {e}")
            return []
    
    async def save_message_to_context(
        self,
        session_id: str,
        user_id: str,
        message: Dict[str, Any]
    ):
        """
        Save message and maintain rolling window
        
        Args:
            session_id: Current session
            user_id: User ID
            message: Message data to save
        """
        try:
            # Add timestamps if missing
            if "timestamp" not in message:
                message["timestamp"] = datetime.now(timezone.utc).isoformat()
            
            # Save message
            await self.db.chat_messages.insert_one(message)
            
            # Maintain rolling window - keep only last N messages
            all_messages = await self.db.chat_messages.find({
                "session_id": session_id,
                "user_id": user_id
            }).sort("timestamp", -1).to_list(None)
            
            if len(all_messages) > self.max_messages_per_session:
                # Delete oldest messages
                old_ids = [msg["_id"] for msg in all_messages[self.max_messages_per_session:]]
                await self.db.chat_messages.delete_many({
                    "_id": {"$in": old_ids}
                })
                logger.info(f"🗑️ Deleted {len(old_ids)} old messages (rolling window)")
            
        except Exception as e:
            logger.error(f"❌ Failed to save message to context: {e}")
    
    async def get_session_summary(
        self,
        session_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get summarized context for current session
        
        Returns:
            Dict with session summary, concepts covered, etc.
        """
        try:
            # Get all messages in session
            messages = await self.db.chat_messages.find({
                "session_id": session_id,
                "user_id": user_id
            }).to_list(None)
            
            # Extract concepts discussed
            concepts = []
            for msg in messages:
                if msg.get("intent") == "concept_explanation":
                    # Extract concept from question
                    question = msg.get("user_message", "")
                    concepts.extend(self._extract_concepts_simple(question))
            
            # Count messages
            user_msgs = [m for m in messages if m.get("user_message")]
            ai_msgs = [m for m in messages if m.get("ai_response")]
            
            return {
                "session_id": session_id,
                "total_messages": len(messages),
                "user_messages": len(user_msgs),
                "ai_messages": len(ai_msgs),
                "concepts_discussed": list(set(concepts)),
                "session_duration_mins": self._calculate_duration(messages)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get session summary: {e}")
            return {}
    
    def _extract_concepts_simple(self, text: str) -> List[str]:
        """Simple concept extraction (can be enhanced with NLP)"""
        concepts = []
        text_lower = text.lower()
        
        # Physics
        if "newton" in text_lower and "law" in text_lower:
            concepts.append("newton_laws")
        if "force" in text_lower or "f=ma" in text_lower:
            concepts.append("force_acceleration")
        
        # Math
        if "derivative" in text_lower or "differentiation" in text_lower:
            concepts.append("derivatives")
        if "integral" in text_lower or "integration" in text_lower:
            concepts.append("integrals")
        if "fundamental theorem" in text_lower:
            concepts.append("fundamental_theorem_calculus")
        
        return concepts
    
    def _calculate_duration(self, messages: List[Dict]) -> int:
        """Calculate session duration in minutes"""
        if not messages or len(messages) < 2:
            return 0
        
        try:
            first = messages[0].get("timestamp")
            last = messages[-1].get("timestamp")
            
            if isinstance(first, str):
                from dateutil import parser
                first = parser.parse(first)
            if isinstance(last, str):
                from dateutil import parser
                last = parser.parse(last)
            
            duration = (last - first).total_seconds() / 60
            return int(duration)
        except:
            return 0
    
    async def consolidate_session_memory(
        self,
        session_id: str,
        user_id: str
    ) -> str:
        """
        Consolidate session into summary for long-term storage
        (Saves tokens by summarizing old conversations)
        
        Returns:
            Session summary text
        """
        try:
            messages = await self.get_conversation_context(session_id, user_id, window_size=50)
            
            if not messages:
                return ""
            
            # Build summary
            summary_parts = []
            for msg in messages:
                user_q = msg.get("user_message", "")
                if user_q:
                    summary_parts.append(f"Q: {user_q[:100]}")
            
            summary = " | ".join(summary_parts)
            return f"Session covered: {summary}"
            
        except Exception as e:
            logger.error(f"❌ Session consolidation failed: {e}")
            return ""

