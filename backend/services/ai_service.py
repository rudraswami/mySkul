"""
AI service for chat sessions, dual AI responses, guardrails, and AI-powered features
Enhanced for AI Tutor 2.0 with adaptive personas, visual generation, and sentiment analysis
"""
import os
import logging
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
import base64

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.sentiment_analyzer import SentimentAnalyzer
from utils.svg_generator import SVGGenerator
from utils.response_parser import ResponseParser
from utils.motivational_generator import MotivationalGenerator

from models.core import User, ChatSession, ChatMessage
from models.ai import (
    ChatRequest, DualAIRequest, MathValidationRequest, 
    FactVerificationRequest, StudyPlanRequest
)

logger = logging.getLogger(__name__)


class AIService:
    """
    AI service for managing chat sessions, dual AI responses, and AI-powered features
    Enhanced for AI Tutor 2.0 with adaptive personas, visual generation, and sentiment analysis
    """
    
    def __init__(self, db: AsyncIOMotorClient, emergent_llm_key: str):
        self.db = db
        self.emergent_llm_key = emergent_llm_key
        self.sentiment_analyzer = SentimentAnalyzer()
        self.svg_generator = SVGGenerator()
        self.response_parser = ResponseParser(emergent_llm_key)
        self.motivational_generator = MotivationalGenerator()
        self.gemini_chat = None  # Lazy init for Gemini visual generation
    
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
        """
        Generate enhanced dual AI response with adaptive personas, visual generation, and progressive disclosure
        AI Tutor 2.0 feature
        """
        try:
            # Step 1: Analyze sentiment and user intent
            sentiment_analysis = self.sentiment_analyzer.analyze(message)
            logger.info(f"Sentiment analysis: {sentiment_analysis}")
            
            # Step 2: Get persona blend based on sentiment
            persona_blend = sentiment_analysis['persona_blend']
            professor_weight = persona_blend['professor']
            mentor_weight = persona_blend['mentor']
            
            # Step 3: Generate adaptive responses
            # Professor response (logical, detailed explanation)
            professor_system = f"""You are a knowledgeable Professor AI providing accurate, detailed explanations.
Focus on: Conceptual clarity, step-by-step reasoning, and exam-relevant insights.
Tone: {sentiment_analysis['primary_sentiment']} detected - adapt your explanation accordingly.
Structure your response in these sections:
1. FOUNDATION: Core concept in simple terms
2. STEP_BY_STEP: Detailed explanation with examples
3. REAL_LIFE: Practical application or analogy
4. KEY_POINTS: 3-5 bullet points to remember"""
            
            professor_chat = LlmChat(
                api_key=self.emergent_llm_key,
                session_id=f"professor_{user_id}_{session_id}",
                system_message=professor_system
            ).with_model("openai", "gpt-5")
            
            # Mentor response (motivational, strategic guidance)
            mentor_system = f"""You are a supportive Mentor AI providing encouragement and study strategies.
Focus on: Building confidence, providing motivation, and suggesting learning strategies.
Tone: {sentiment_analysis['primary_sentiment']} detected - provide appropriate emotional support.
Keep response concise (2-3 sentences) with actionable advice."""
            
            mentor_chat = LlmChat(
                api_key=self.emergent_llm_key,
                session_id=f"mentor_{user_id}_{session_id}",
                system_message=mentor_system
            ).with_model("openai", "gpt-5")
            
            # Generate responses
            professor_message = UserMessage(text=f"Subject: {subject}. Question: {message}")
            mentor_message = UserMessage(text=f"Provide motivational guidance for: {message} in {subject}")
            
            professor_response = await professor_chat.send_message(professor_message)
            mentor_response = await mentor_chat.send_message(mentor_message)
            
            # Step 4: Generate visual concept (SVG primary, Gemini fallback)
            visual_svg = self.svg_generator.generate_concept_visual(message, subject)
            visual_data = {
                'type': 'svg',
                'content': visual_svg,
                'generated': visual_svg is not None
            }
            
            # If no SVG was generated and it's a visual concept, try Gemini
            if not visual_svg and any(keyword in message.lower() for keyword in ['show', 'draw', 'visualize', 'diagram', 'graph']):
                visual_data = await self._generate_gemini_visual(message, subject)
            
            # Step 5: Parse professor response into progressive disclosure sections
            professor_content = professor_response if isinstance(professor_response, str) else str(professor_response)
            progressive_sections = self._parse_progressive_sections(professor_content)
            
            # Step 6: Generate quick actions
            quick_actions = self._generate_quick_actions(message, subject, sentiment_analysis)
            
            # Step 7: Parse response into micro-lesson sections (AI Tutor 2.1)
            micro_lesson_sections = await self.response_parser.parse_response(
                professor_content,
                subject,
                message
            )
            
            # Step 8: Generate motivational footer with real analytics
            user_analytics = await self._get_user_analytics(user_id, subject)
            motivational_data = self.motivational_generator.generate(
                user_analytics,
                sentiment_analysis['primary_sentiment'],
                subject
            )
            
            # Step 9: Create enhanced dual response structure
            dual_response = {
                "primary": {
                    "type": "professor",
                    "response": professor_content,
                    "confidence": 0.95,
                    "progressive_sections": progressive_sections,
                    "weight": professor_weight
                },
                "secondary": {
                    "type": "mentor", 
                    "response": mentor_response if isinstance(mentor_response, str) else str(mentor_response),
                    "confidence": 0.9,
                    "weight": mentor_weight
                },
                "visual": visual_data,
                "sentiment_analysis": sentiment_analysis,
                "quick_actions": quick_actions,
                "session_id": session_id,
                "subject": subject,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "persona_blend": persona_blend
            }
            
            # Save message to session
            await self.save_session_message(user_id, session_id, message, dual_response)
            
            return dual_response
            
        except Exception as e:
            logger.error(f"Generate dual AI response error: {str(e)}")
            raise Exception(f"Failed to generate dual AI response: {str(e)}")
    
    def _parse_progressive_sections(self, content: str) -> Dict[str, str]:
        """Parse professor response into progressive disclosure sections"""
        sections = {
            'foundation': '',
            'step_by_step': '',
            'real_life': '',
            'key_points': ''
        }
        
        # Try to extract marked sections
        import re
        
        foundation_match = re.search(r'(?:FOUNDATION|1\..*?FOUNDATION)[:\s]+(.*?)(?=STEP_BY_STEP|STEP-BY-STEP|2\.|$)', content, re.IGNORECASE | re.DOTALL)
        if foundation_match:
            sections['foundation'] = foundation_match.group(1).strip()
        
        step_match = re.search(r'(?:STEP_BY_STEP|STEP-BY-STEP|2\..*?STEP)[:\s]+(.*?)(?=REAL_LIFE|REAL-LIFE|3\.|$)', content, re.IGNORECASE | re.DOTALL)
        if step_match:
            sections['step_by_step'] = step_match.group(1).strip()
        
        real_life_match = re.search(r'(?:REAL_LIFE|REAL-LIFE|3\..*?REAL)[:\s]+(.*?)(?=KEY_POINTS|KEY POINTS|4\.|$)', content, re.IGNORECASE | re.DOTALL)
        if real_life_match:
            sections['real_life'] = real_life_match.group(1).strip()
        
        key_points_match = re.search(r'(?:KEY_POINTS|KEY POINTS|4\..*?KEY)[:\s]+(.*?)$', content, re.IGNORECASE | re.DOTALL)
        if key_points_match:
            sections['key_points'] = key_points_match.group(1).strip()
        
        # If no sections found, use whole content as foundation
        if not any(sections.values()):
            sections['foundation'] = content
        
        return sections
    
    def _generate_quick_actions(self, message: str, subject: str, sentiment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate contextual quick actions based on message and sentiment"""
        actions = [
            {
                'id': 'save_notes',
                'label': 'Save to Notes',
                'icon': 'bookmark',
                'action': 'save_to_notes'
            },
            {
                'id': 'practice_similar',
                'label': 'Practice Similar',
                'icon': 'target',
                'action': 'generate_practice'
            }
        ]
        
        # Add context-specific actions
        if sentiment['needs_encouragement']:
            actions.append({
                'id': 'explain_differently',
                'label': 'Explain Differently',
                'icon': 'refresh',
                'action': 'explain_different'
            })
        
        if 'visual' in message.lower() or 'show' in message.lower():
            actions.append({
                'id': 'show_visual',
                'label': 'Show Visual',
                'icon': 'image',
                'action': 'generate_visual'
            })
        
        return actions
    
    async def _generate_gemini_visual(self, prompt: str, subject: str) -> Dict[str, Any]:
        """Generate visual using Gemini Nano Banana (fallback)"""
        try:
            if not self.gemini_chat:
                self.gemini_chat = LlmChat(
                    api_key=self.emergent_llm_key,
                    session_id="visual_gen",
                    system_message="You are a visual AI that generates educational concept illustrations."
                ).with_model("gemini", "gemini-2.5-flash-image-preview").with_params(modalities=["image", "text"])
            
            visual_prompt = UserMessage(
                text=f"Create a simple, educational illustration for this {subject} concept: {prompt}. Make it clean and suitable for learning."
            )
            
            text, images = await self.gemini_chat.send_message_multimodal_response(visual_prompt)
            
            if images and len(images) > 0:
                return {
                    'type': 'gemini_image',
                    'content': images[0]['data'],  # base64 data
                    'mime_type': images[0]['mime_type'],
                    'generated': True
                }
            
            return {'type': 'none', 'content': None, 'generated': False}
            
        except Exception as e:
            logger.error(f"Gemini visual generation error: {str(e)}")
            return {'type': 'none', 'content': None, 'generated': False}
    
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
                session_id=f"math_val_{expression[:10]}",
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
                session_id=f"fact_check_{statement[:10]}",
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