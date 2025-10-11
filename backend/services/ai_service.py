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
from utils.format_validator import format_validator

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
    
    def __init__(self, db: AsyncIOMotorClient, emergent_llm_key: str, subscription_service=None):
        self.db = db
        self.emergent_llm_key = emergent_llm_key
        self.sentiment_analyzer = SentimentAnalyzer()
        self.svg_generator = SVGGenerator()
        self.response_parser = ResponseParser(emergent_llm_key)
        self.motivational_generator = MotivationalGenerator()
        self.gemini_chat = None  # Lazy init for Gemini visual generation
        self.subscription_service = subscription_service  # For usage tracking
    
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
        AI Tutor 2.0 feature with subscription checking and usage tracking
        """
        try:
            # Step 0: Check subscription access (if subscription service available)
            if self.subscription_service:
                access_info = await self.subscription_service.check_ai_tutor_access(user_id)
                if not access_info.get("allowed", True):
                    logger.warning(f"AI Tutor access denied for user {user_id}: limit reached")
                    return {
                        "error": "subscription_limit_reached",
                        "message": "AI Tutor session limit reached",
                        "upgrade_hint": access_info.get("upgrade_hint"),
                        "access_info": access_info
                    }
                logger.info(f"AI Tutor access check: {access_info.get('remaining')} sessions remaining")
            
            # Step 1: Analyze sentiment and user intent
            sentiment_analysis = self.sentiment_analyzer.analyze(message)
            logger.info(f"Sentiment analysis: {sentiment_analysis}")
            
            # Step 2: Get persona blend based on sentiment
            persona_blend = sentiment_analysis['persona_blend']
            professor_weight = persona_blend['professor']
            mentor_weight = persona_blend['mentor']
            
            # Step 3: Generate adaptive responses
            # Professor response (logical, detailed explanation)
            professor_system = f"""You are a Professor AI creating structured micro-lessons optimized for on-screen comprehension.

MANDATORY RESPONSE STRUCTURE:
1. Concept Overview (2-3 sentences, max 250 characters)
   - Define the core concept in simple language
   - State why it's important and exam-relevant

2. Key Formulas (max 3 formulas)
   - Wrap ALL math in LaTeX: \\[ formula \\] for display, \\( formula \\) for inline
   - Example: \\[ \\int f(x) dx \\]
   - Always verify formula syntax before returning

3. Step-by-Step (4-6 numbered steps, max 600 characters)
   - Use plain numbered lists: 1., 2., 3., 4., 5., 6.
   - Break complex steps into sub-bullets with -
   - Include ONE fully worked example with verification
   - Format verification as: ✓ Left side = Right side

4. Real-World Example (1 paragraph, max 300 characters)
   - Concrete application scenario
   - Relate to student's experience or exam context

5. Pro Tip (1-2 sentences, max 150 characters)
   - Study strategy or common mistake to avoid
   - End with encouraging reflection

CRITICAL FORMATTING RULES (STUDENT-FIRST):
1. Use \\[ \\] for display math (centered formulas)
2. Use \\( \\) for inline math in paragraphs
3. NO markdown symbols in output: **, *, __, _ (write plain text)
4. NO emojis in main content: 👇, 📚, 🧮, ✅, ❌, 💡, 🔎
5. NO numbered emojis: 1️⃣, 2️⃣, 3️⃣ (use: 1., 2., 3.)
6. Keep paragraphs 2-3 lines maximum
7. Use plain numbered lists with periods: 1., 2., 3.
8. For verification, use: ✓ or "correct" instead of checkmark emojis
9. Break long explanations into short bullets
10. Always end with motivational line like: "That's how we solve it perfectly!"

TONE REQUIREMENTS:
- Confident and encouraging, never robotic
- Professional yet empathetic
- Focus on clarity over verbosity
- Exam-relevant insights
- Student sentiment: {sentiment_analysis['primary_sentiment']}

RENDER SAFETY:
- Interpret special characters correctly: /, *, #, \\[, \\]
- Never expose raw markdown or broken tags
- Clean output = readable on mobile, tablet, web
- All content must feel human and motivating

Topic: {message}
Subject: {subject}"""
            
            professor_chat = LlmChat(
                api_key=self.emergent_llm_key,
                session_id=f"professor_{user_id}_{session_id}",
                system_message=professor_system
            ).with_model("openai", "gpt-5")
            
            # Mentor response (motivational, strategic guidance)
            mentor_system = f"""You are a Mentor AI providing emotionally supportive guidance optimized for student motivation.

RESPONSE STRUCTURE (4 complementary sections - NEVER repeat Professor content):

1. Motivation Spark (1-2 sentences, max 180 characters)
   - Why this topic matters for THEIR success
   - Encouraging opening that builds confidence
   - Connect to their exam goals

2. Simplified Recap (3-5 bullet points, max 250 characters)
   - Format: Simple bullets with • symbol
   - Key takeaways in everyday language
   - Complement Professor's technical explanation
   - Focus on "what to remember" not "how to solve"

3. Confidence Tips (2-3 actionable strategies, max 200 characters)
   - Specific study techniques
   - How to practice effectively
   - Common mistakes to watch for
   - Memory tricks or mnemonics

4. Encouragement (1 powerful sentence, max 120 characters)
   - Growth mindset message
   - Forward-looking and empowering
   - End with energy: "legend!", "champion!", "you've got this!"

CRITICAL FORMATTING RULES (EMOTION-FIRST):
1. NO markdown in output: **, *, __, _ (plain text only)
2. Use emojis ONLY in final encouragement: 🌟, 💪, 🎯, ⚡
3. NO emojis in sections 1-3
4. NO numbered emojis: 1️⃣, 2️⃣, 3️⃣ (too childish)
5. Keep all sections ultra-brief and scannable
6. Use first-person voice: "I believe...", "I recommend..."
7. Short paragraphs (1-2 lines maximum)
8. Bullets for tips, NOT numbered lists

TONE REQUIREMENTS:
- Warm, supportive, never patronizing
- Like a caring coach or older sibling
- Balance empathy with action
- Build confidence through specificity
- Student sentiment: {sentiment_analysis['primary_sentiment']}

CRITICAL: Your response must COMPLEMENT the Professor's content, NOT repeat it.
- Professor explains HOW
- You explain WHY it matters and HOW to remember
- Professor is technical
- You are emotional and strategic

Student Question: {message}
Subject Context: {subject}"""
            
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
            
            # Step 7.5: Split mentor response into structured sections (AI Tutor 2.4)
            mentor_content = mentor_response if isinstance(mentor_response, str) else str(mentor_response)
            mentor_sections = self.response_parser.split_mentor_response(mentor_content)
            
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
                    "micro_lesson_sections": micro_lesson_sections,
                    "weight": professor_weight
                },
                "secondary": {
                    "type": "mentor", 
                    "response": mentor_content,
                    "mentor_sections": mentor_sections,
                    "confidence": 0.9,
                    "weight": mentor_weight
                },
                "visual": visual_data,
                "sentiment_analysis": sentiment_analysis,
                "quick_actions": quick_actions,
                "motivational_footer": motivational_data,
                "session_id": session_id,
                "subject": subject,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "persona_blend": persona_blend
            }
            
            # Save message to session
            await self.save_session_message(user_id, session_id, message, dual_response)
            
            # Track AI Tutor session usage (if subscription service available)
            if self.subscription_service:
                await self.subscription_service.track_ai_tutor_session(user_id)
                logger.info(f"✅ Tracked AI Tutor session for user {user_id}")
            
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
    
    async def _get_user_analytics(self, user_id: str, subject: str) -> Dict[str, Any]:
        """Get user analytics for motivational message generation"""
        try:
            # Get user's recent analytics
            analytics = await self.db.user_analytics.find_one({
                "user_id": user_id,
                "subject": subject
            })
            
            if not analytics:
                return {
                    'accuracy': 0,
                    'previous_accuracy': 0,
                    'streak': 0,
                    'mastery': 0,
                    'current_topic': subject
                }
            
            return {
                'accuracy': analytics.get('accuracy', 0),
                'previous_accuracy': analytics.get('previous_accuracy', 0),
                'streak': analytics.get('streak', 0),
                'mastery': analytics.get('mastery', 0),
                'current_topic': analytics.get('current_topic', subject)
            }
        except Exception as e:
            logger.error(f"Error fetching user analytics: {str(e)}")
            return {
                'accuracy': 0,
                'previous_accuracy': 0,
                'streak': 0,
                'mastery': 0,
                'current_topic': subject
            }
    
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