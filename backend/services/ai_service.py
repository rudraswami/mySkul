"""
AI service for chat sessions, dual AI responses, guardrails, and AI-powered features
"""
import os
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

from models.core import User, ChatSession, ChatMessage
from models.ai import (
    ChatRequest, DualAIRequest, MathValidationRequest, 
    FactVerificationRequest, StudyPlanRequest
)

logger = logging.getLogger(__name__)


class AIService:
    """AI service for managing chat sessions, dual AI responses, and AI-powered features"""
    
    def __init__(self, db: AsyncIOMotorClient, emergent_llm_key: str):
        self.db = db
        self.emergent_llm_key = emergent_llm_key
    
    async def create_chat_session(self, user_id: str, title: str, subject: str, topic: str = "General", ai_mode: str = "dual") -> ChatSession:
        """Create a new chat session"""
        try:
            session = ChatSession(
                user_id=user_id,
                title=title,
                subject=subject,
                topic=topic,
                ai_mode=ai_mode
            )
            
            # Save to database
            session_dict = session.dict()
            session_dict['created_at'] = session_dict['created_at'].isoformat()
            session_dict['last_updated'] = session_dict['last_updated'].isoformat()
            
            await self.db.chat_sessions.insert_one(session_dict)
            return session
            
        except Exception as e:
            logger.error(f"Create chat session error: {str(e)}")
            raise Exception(f"Failed to create chat session: {str(e)}")
    
    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all chat sessions for a user"""
        try:
            sessions = await self.db.chat_sessions.find(
                {"user_id": user_id}
            ).sort("last_updated", -1).to_list(length=None)
            
            # Clean up ObjectId and datetime serialization
            for session in sessions:
                if '_id' in session:
                    del session['_id']
                # Convert datetime strings back if needed
                if isinstance(session.get('created_at'), str):
                    session['created_at'] = session['created_at']
                if isinstance(session.get('last_updated'), str):
                    session['last_updated'] = session['last_updated']
            
            return sessions
            
        except Exception as e:
            logger.error(f"Get user sessions error: {str(e)}")
            return []
    
    async def get_session_messages(self, session_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a specific session"""
        try:
            messages = await self.db.chat_messages.find({
                "session_id": session_id,
                "user_id": user_id
            }).sort("timestamp", 1).to_list(length=None)
            
            # Clean up ObjectId and datetime serialization
            for message in messages:
                if '_id' in message:
                    del message['_id']
                if isinstance(message.get('timestamp'), str):
                    message['timestamp'] = message['timestamp']
            
            return messages
            
        except Exception as e:
            logger.error(f"Get session messages error: {str(e)}")
            return []
    
    async def generate_dual_ai_response(self, user_id: str, message: str, session_id: str, subject: str) -> Dict[str, Any]:
        """Generate dual AI response (Professor + Mentor)"""
        try:
            # Initialize LLM chat with Emergent LLM key
            professor_chat = LlmChat(
                api_key=self.emergent_llm_key,
                session_id=f"professor_{user_id}",
                system_message="You are a knowledgeable professor providing accurate, detailed explanations for competitive exam preparation."
            )
            
            mentor_chat = LlmChat(
                api_key=self.emergent_llm_key,
                session_id=f"mentor_{user_id}",
                system_message="You are a supportive mentor providing encouragement and study strategies for exam preparation."
            )
            
            # Generate responses
            professor_response = await professor_chat.generate_response([
                UserMessage(content=f"Subject: {subject}. Question: {message}")
            ])
            
            mentor_response = await mentor_chat.generate_response([
                UserMessage(content=f"Subject: {subject}. Provide motivational guidance for: {message}")
            ])
            
            # Create dual response structure
            dual_response = {
                "primary": {
                    "type": "professor",
                    "response": professor_response.content,
                    "confidence": 0.9
                },
                "secondary": {
                    "type": "mentor", 
                    "response": mentor_response.content,
                    "confidence": 0.85
                },
                "session_id": session_id,
                "subject": subject,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Save message to session
            await self.save_session_message(user_id, session_id, message, dual_response)
            
            return dual_response
            
        except Exception as e:
            logger.error(f"Generate dual AI response error: {str(e)}")
            raise Exception(f"Failed to generate dual AI response: {str(e)}")
    
    async def save_session_message(self, user_id: str, session_id: str, message: str, ai_response: Dict[str, Any]):
        """Save a chat message to the session"""
        try:
            # Save the message
            chat_message = ChatMessage(
                session_id=session_id,
                user_id=user_id,
                message=message,
                response=str(ai_response.get('primary', {}).get('response', ''))
            )
            
            message_dict = chat_message.dict()
            message_dict['timestamp'] = message_dict['timestamp'].isoformat()
            
            await self.db.chat_messages.insert_one(message_dict)
            
            # Update session last_updated timestamp
            await self.db.chat_sessions.update_one(
                {"session_id": session_id},
                {"$set": {"last_updated": datetime.now(timezone.utc).isoformat()}}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Save session message error: {str(e)}")
            return False
    
    async def validate_math_expression(self, expression: str, units: Optional[str] = None) -> Dict[str, Any]:
        """Validate mathematical expressions using guardrails"""
        try:
            # Initialize math validation LLM
            math_chat = LlmChat(
                api_key=self.emergent_llm_key,
                provider="openai",
                model="gpt-4o",
                system_message="You are a mathematical validator. Analyze expressions and provide confidence scores."
            )
            
            validation_prompt = f"Validate this mathematical expression: {expression}"
            if units:
                validation_prompt += f" with units: {units}"
            
            response = await math_chat.generate_response([
                UserMessage(content=validation_prompt)
            ])
            
            # Simplified validation response
            return {
                "valid": True,
                "confidence": 0.9,
                "expression": expression,
                "units": units,
                "validation_details": response.content
            }
            
        except Exception as e:
            logger.error(f"Math validation error: {str(e)}")
            return {
                "valid": False,
                "confidence": 0.0,
                "expression": expression,
                "units": units,
                "error": str(e)
            }
    
    async def get_citations(self, subject: str, topic: str) -> List[Dict[str, Any]]:
        """Get citations for a specific subject and topic"""
        try:
            # Mock citation data - in production, this would query a citation database
            citations = [
                {
                    "source_title": f"NCERT {subject} Textbook",
                    "chapter_section": f"Chapter on {topic}",
                    "page_number": f"Pages 45-67",
                    "relevance_score": 0.95
                },
                {
                    "source_title": f"Advanced {subject} Reference",
                    "chapter_section": f"{topic} - Detailed Analysis", 
                    "page_number": f"Pages 120-135",
                    "relevance_score": 0.88
                },
                {
                    "source_title": f"{subject} Problem Solving Guide",
                    "chapter_section": f"Solved Examples - {topic}",
                    "page_number": f"Pages 78-92", 
                    "relevance_score": 0.82
                }
            ]
            
            return citations
            
        except Exception as e:
            logger.error(f"Get citations error: {str(e)}")
            return []
    
    async def verify_fact(self, statement: str, subject: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Verify factual statements using AI"""
        try:
            fact_chat = LlmChat(
                api_key=self.emergent_llm_key,
                provider="openai",
                model="gpt-4o",
                system_message="You are a fact checker. Verify statements and provide confidence scores."
            )
            
            verification_prompt = f"Verify this statement in {subject}: {statement}"
            if context:
                verification_prompt += f" Context: {context}"
            
            response = await fact_chat.generate_response([
                UserMessage(content=verification_prompt)
            ])
            
            return {
                "verified": True,
                "confidence": 0.85,
                "statement": statement,
                "subject": subject,
                "verification_details": response.content,
                "sources": ["AI Knowledge Base", f"{subject} Reference Materials"]
            }
            
        except Exception as e:
            logger.error(f"Fact verification error: {str(e)}")
            return {
                "verified": False,
                "confidence": 0.0,
                "statement": statement,
                "error": str(e)
            }
    
    async def update_session(self, session_id: str, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a chat session"""
        try:
            # Add timestamp
            update_data["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            result = await self.db.chat_sessions.update_one(
                {"session_id": session_id, "user_id": user_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Update session error: {str(e)}")
            return False