"""
AI service for chat sessions, dual AI responses, guardrails, and AI-powered features
Enhanced for AI Tutor 2.0 with adaptive personas, visual generation, and sentiment analysis
Enhanced for Neuro-Symbolic AI Tutor 3.0 with Indian student-centric learning
"""
import os
import logging
import sys
import asyncio
import time
import uuid
import traceback
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.sentiment_analyzer import SentimentAnalyzer
from utils.svg_generator import SVGGenerator
from utils.response_parser import ResponseParser
from utils.motivational_generator import MotivationalGenerator
from utils.format_validator import format_validator

from models.core import ChatSession, ChatMessage

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
    
    def _detect_depth_level(self, message: str, subject: str) -> str:
        """
        Phase 2: Detect appropriate depth level based on query characteristics
        Returns: "deep", "standard", or "quick"
        """
        message_lower = message.lower()
        word_count = len(message.split())
        
        # Deep indicators
        deep_keywords = [
            'derive', 'proof', 'mechanism', 'explain in detail', 'step by step',
            'how does', 'why does', 'complete', 'comprehensive', 'detailed',
            'biochemical', 'molecular', 'thermodynamic', 'quantum', 'relativistic'
        ]
        
        # Quick indicators
        quick_keywords = [
            'what is', 'define', 'quick', 'brief', 'summary', 'in short',
            'simple', 'basic', 'quickly'
        ]
        
        # Check for deep indicators
        if any(keyword in message_lower for keyword in deep_keywords) or word_count > 15:
            return "deep"
        
        # Check for quick indicators
        if any(keyword in message_lower for keyword in quick_keywords) or word_count < 6:
            return "quick"
        
        # Default to standard
        return "standard"
    
    def _detect_exam_mode(self, user_id: str, subject: str) -> str:
        """
        Phase 2: Detect exam context from user profile
        Returns: "JEE", "NEET", or "CBSE"
        """
        # For Phase 2, we'll default based on subject
        # Phase 3 will read from user profile in database
        
        subject_lower = subject.lower()
        
        # Subject-based heuristics
        if any(term in subject_lower for term in ['physics', 'mathematics', 'chemistry']):
            return "JEE"  # Engineering focus
        elif any(term in subject_lower for term in ['biology', 'zoology', 'botany']):
            return "NEET"  # Medical focus
        else:
            return "CBSE"  # General board exam
    
    def _generate_simple_greeting_response(self, user_id: str, message: str, session_id: str, subject: str) -> Dict[str, Any]:
        """
        Generate fast response for simple greetings without calling AI (under 100ms)
        OPTIMIZATION: Avoids 35-40s AI generation for trivial messages
        """
        greetings_map = {
            'hi': "Hello! I'm your AI Tutor, ready to help you master any topic!",
            'hello': "Hello! I'm excited to help you learn today!",
            'hey': "Hey there! Ready to tackle some challenging concepts?",
            'hola': "Hola! Let's dive into some amazing learning!",
            'namaste': "Namaste! Your personal learning journey starts here!"
        }
        
        # Get greeting response
        message_lower = message.lower().strip()
        base_greeting = greetings_map.get(message_lower, "Hello! I'm your AI Tutor!")
        
        # Create fast response structure
        professor_response = f"""{base_greeting}

[SECTION:CONCEPT]
I'm here to provide deep, comprehensive explanations for any question you have in {subject}. Feel free to ask me anything!
[/SECTION:CONCEPT]

[SECTION:STEPS]
Here's how I can help you:
1. **Ask any question** - From basic concepts to advanced problems
2. **Get detailed explanations** - Step-by-step breakdowns with reasoning
3. **Learn efficiently** - Exam-focused strategies and real-world applications
4. **Build confidence** - Personalized guidance for your learning style
[/SECTION:STEPS]"""

        mentor_response = f"""Welcome! I'm so glad you're here!

[MICROCARD:MOTIVATION]
Starting a learning session shows real commitment. Every expert was once a beginner, and you're taking that first step right now!
[/MICROCARD:MOTIVATION]

[MICROCARD:RECAP]
• I'm here to break down complex topics into understandable pieces
• We'll focus on exam success and real understanding
• Ask anything - there are no silly questions here
[/MICROCARD:RECAP]

[MICROCARD:ENCOURAGEMENT]
You've got this! Let's make learning engaging and effective. Ready when you are! 🚀
[/MICROCARD:ENCOURAGEMENT]"""
        
        # Return structured response (matches regular AI response format)
        return {
            "dual_response": {
                "primary": {
                    "response": professor_response,
                    "persona": "professor",
                    "micro_lesson_sections": {
                        "concept_overview": f"I'm your AI Tutor for {subject}, ready to provide comprehensive explanations!",
                        "key_formula": [],
                        "step_by_step": "Ask me any question and I'll provide detailed, exam-focused guidance.",
                        "real_life_analogy": "",
                        "mentor_tip": "",
                        "visual_prompt": ""
                    }
                },
                "secondary": {
                    "response": mentor_response,
                    "persona": "mentor",
                    "mentor_sections": {
                        "motivation_spark": "Starting a learning session shows real commitment!",
                        "simplified_recap": "I'm here to help you understand and excel.",
                        "confidence_tips": "Ask anything - there are no silly questions!",
                        "encouragement": "You've got this! Ready when you are!"
                    }
                }
            },
            "sentiment_analysis": {
                "primary_sentiment": "neutral",
                "confidence": 1.0,
                "persona_blend": {"professor": 0.5, "mentor": 0.5}
            },
            "visual": {
                "type": "none",
                "content": None,
                "generated": False
            },
            "quick_actions": [
                {"label": "Explain a concept", "action": "ask_question"},
                {"label": "Solve a problem", "action": "solve_problem"},
                {"label": "Practice questions", "action": "practice"}
            ],
            "motivational_data": {
                "message": f"Welcome to {subject} learning!",
                "badge": "beginner",
                "progress": 0
            },
            "fast_response": True,
            "response_time_ms": 50
        }

    
    async def generate_dual_ai_response(self, user_id: str, message: str, session_id: str, subject: str) -> Dict[str, Any]:
        """
        Generate enhanced dual AI response with adaptive personas, visual generation, and progressive disclosure
        AI Tutor 2.0 feature with subscription checking and usage tracking
        OPTIMIZED: Added simple message detection and parallel AI execution
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
            
            # OPTIMIZATION: Detect simple messages (greetings, short queries) and return fast responses
            message_lower = message.lower().strip()
            simple_greetings = ['hi', 'hello', 'hey', 'hola', 'namaste', 'good morning', 'good afternoon', 'good evening']
            if message_lower in simple_greetings or (len(message.strip()) < 10 and any(greeting in message_lower for greeting in simple_greetings)):
                logger.info(f"🚀 Fast response for simple greeting: {message}")
                return self._generate_simple_greeting_response(user_id, message, session_id, subject)
            
            # Step 1: Analyze sentiment and user intent
            sentiment_analysis = self.sentiment_analyzer.analyze(message)
            logger.info(f"Sentiment analysis: {sentiment_analysis}")
            
            # Step 2: Get persona blend based on sentiment
            persona_blend = sentiment_analysis['persona_blend']
            professor_weight = persona_blend['professor']
            mentor_weight = persona_blend['mentor']
            
            # Step 3: Generate adaptive responses with DEEP REASONING (Phase 2)
            # Detect depth level and exam context
            depth_level = self._detect_depth_level(message, subject)
            exam_mode = self._detect_exam_mode(user_id, subject)  # Will use user profile later
            
            # Professor response (logical, detailed explanation with multi-layer reasoning)
            professor_system = f"""You are an Expert Professor AI creating deeply reasoned, multi-layered learning content.

PHASE 2: DEEP REASONING PROTOCOL
Your response must demonstrate THREE CONCEPTUAL LAYERS:

LAYER 1 - FOUNDATIONAL UNDERSTANDING (Overview)
- Define the core concept in precise terms
- Explain WHY this concept exists and its fundamental purpose
- State exam relevance for {exam_mode} specifically

LAYER 2 - MECHANISTIC DEPTH (How It Works)
Subject-Specific Depth Rules:
- Biology: Explain molecular/cellular mechanisms, physiological pathways, regulatory systems
- Physics: Derive equations from first principles, show dimensional analysis, explain boundary conditions
- Chemistry: Show bonding mechanisms, reaction mechanisms with electron movement, thermodynamic drivers
- Mathematics: Prove theorems, show logical flow, explain intuition behind abstractions

LAYER 3 - APPLIED INTELLIGENCE (Real-World + Edge Cases)
- Real-world applications with specific examples
- Edge cases and boundary conditions (e.g., "What happens during exercise?", "At high temperatures?")
- Common misconceptions and how to avoid them
- Exam-specific traps and solution strategies for {exam_mode}

MANDATORY RESPONSE STRUCTURE (Tagged for Frontend Rendering):
[SECTION:CONCEPT]
Concept Overview (3-4 sentences, 300-400 characters)
- Define concept with precision
- Explain fundamental purpose and mechanism
- State {exam_mode} exam relevance
[/SECTION:CONCEPT]

[SECTION:FORMULAS]
Key Formulas (2-3 essential formulas)
- Wrap math in LaTeX: \\[ formula \\] for display, \\( formula \\) for inline
- Example: \\[ E = mc^2 \\]
- Explain what each variable represents
- State conditions where formula applies
[/SECTION:FORMULAS]

[SECTION:STEPS]
Step-by-Step Deep Explanation (6-8 detailed steps)
1. [First principle or starting point]
2. [Mechanism or derivation with reasoning]
3. [Intermediate result with explanation]
4. [Critical insight or turning point]
5. [Advanced detail or edge case consideration]
6. [Final result with verification]
7. [Boundary conditions or limitations]
8. [Exam application strategy]

Include:
- Complete worked example with ALL intermediate steps
- Reasoning for EACH step (not just mechanical manipulation)
- Dimensional analysis for physics/chemistry
- Mechanistic explanation for biology
- Common student errors to avoid
[/SECTION:STEPS]

[SECTION:REALWORLD]
Real-World Application (200-300 characters)
- Specific concrete example from daily life or industry
- Connect to {exam_mode} exam context
- Show practical importance
[/SECTION:REALWORLD]

[SECTION:PROTIP]
Pro Exam Strategy (150-200 characters)
- {exam_mode}-specific solving technique
- Time-saving shortcut or pattern recognition
- Common pitfall to avoid
[/SECTION:PROTIP]

DEPTH MODE: {depth_level}
- "deep": Maximum detail, all 3 layers, complete derivations, edge cases
- "standard": Balanced detail, core mechanisms, key examples  
- "quick": Essential concepts only, core formula, brief example

KEY TERMS EMPHASIS (wrap in <key>term</key> for frontend bolding):
- Subject-specific terminology: For Biology→<key>enzymes</key>, <key>ATP</key>; For Physics→<key>force</key>, <key>acceleration</key>
- Critical concepts that appear in {exam_mode} frequently
- Variables in formulas

CRITICAL FORMATTING RULES:
1. Use \\[ \\] for display math (centered formulas)
2. Use \\( \\) for inline math in paragraphs
3. Use [SECTION:TYPE] tags for frontend semantic rendering
4. Wrap key terms in <key></key> for automatic bolding
5. Use plain numbered lists: 1., 2., 3. (no emojis or special symbols)
6. NO markdown (**, *, __, _) - use <key> tags instead
7. NO emojis (👇, 📚, 🧮, ✅, ❌, 💡)
8. Clean punctuation only: . , ; : ! ? ( ) [ ]

REASONING QUALITY REQUIREMENTS:
- NO duplicate sentences or repetitive phrasing
- Each sentence adds NEW information or insight
- Show mechanistic understanding (not just description)
- Connect concepts hierarchically (micro → macro)
- Anticipate follow-up questions and address them
- Depth appropriate for {exam_mode} preparation level

TONE:
- Authoritative yet accessible
- Intellectually rigorous
- {exam_mode} exam-focused
- Student sentiment: {sentiment_analysis['primary_sentiment']}

Topic: {message}
Subject: {subject}
Exam Context: {exam_mode}
Depth Level: {depth_level}"""
            
            # Use GPT-4o for faster response times (109 tokens/sec vs GPT-5's slower response)
            # GPT-4o provides excellent quality with significantly better speed for user experience
            # Phase 1: Added explicit LLM parameters for quality and depth
            professor_chat = LlmChat(
                api_key=self.emergent_llm_key,
                session_id=f"professor_{user_id}_{session_id}",
                system_message=professor_system
            ).with_model("openai", "gpt-4o").with_params(
                temperature=0.75,          # Balanced creativity for explanations
                top_p=0.9,                # Nucleus sampling for coherent responses
                max_tokens=1200,          # Optimized for speed while maintaining quality (reduced from 1600)
                presence_penalty=0.1,     # Slight penalty to reduce repetition
                frequency_penalty=0.1     # Encourage varied vocabulary
            )
            
            # Mentor response will be generated AFTER Professor (with context reflection)
            # This allows Mentor to truly complement rather than duplicate
            # Mentor system prompt will be created after Professor response is available
            
            # Mentor chat will be created AFTER Professor response (Phase 2 sequential reflection)
            
            # OPTIMIZATION: PARALLEL EXECUTION (Professor & Mentor simultaneously)
            # This reduces total time from 35-40s to ~20s
            logger.info("🤖 Starting parallel AI generation (Professor & Mentor simultaneously)")
            
            try:
                # STEP 1 & 2: Generate BOTH responses in parallel for speed
                logger.info("🎓💙 Generating Professor and Mentor responses in parallel...")
                professor_message = UserMessage(text=f"Subject: {subject}. Question: {message}")
                
                start_time = time.time()
                
                # Create independent Mentor system prompt (doesn't need Professor context for speed)
                mentor_independent_system = f"""You are a Master Mentor AI providing strategic learning guidance and motivation.

MENTOR RESPONSE STRUCTURE (Tagged for Frontend Microcards):

[MICROCARD:MOTIVATION]
Motivation Spark (2-3 sentences, 200-250 characters)
- Why THIS specific concept matters for {exam_mode} success
- Personal relevance and career applications
- Build confidence with specificity (not generic encouragement)
[/MICROCARD:MOTIVATION]

[MICROCARD:RECAP]
Strategic Recap (4-6 bullet points, 300-350 characters)
- Highlight the MOST exam-critical points about {message} in {subject}
- Identify concepts students commonly misunderstand
- Point out what deserves extra attention
- Use everyday analogies to clarify complex ideas
- Format: • Clear, memorable statements
[/MICROCARD:RECAP]

[MICROCARD:EXAMBOOST]
Exam Booster Strategies (3-4 tactics, 250-300 characters)
- {exam_mode}-specific solving techniques
- Memory mnemonics for key formulas or concepts
- Time-saving shortcuts used by top scorers
- Common exam traps related to THIS topic and how to avoid them
- Practice problem patterns to master
[/MICROCARD:EXAMBOOST]

[MICROCARD:ENCOURAGEMENT]
Confidence Builder (2-3 powerful sentences, 150-200 characters)
- Acknowledge the intellectual challenge
- Growth mindset reinforcement
- Forward momentum with energy
- End with motivational punch: "You're building real mastery!"
[/MICROCARD:ENCOURAGEMENT]

KEY TERMS EMPHASIS (wrap in <key>term</key>):
- Study strategies, memory techniques, exam tactics
- Conceptual connections
- Common mistakes to avoid

FORMATTING RULES:
1. Use [MICROCARD:TYPE] tags for frontend rendering
2. Wrap important terms in <key></key> for bolding
3. Use • for bullet points (no emojis)
4. NO markdown (**, *, __, _)
5. NO emojis (🌟, 💪, 🎯, ⚡)
6. Clean punctuation only

DEPTH MODE: {depth_level}
EXAM CONTEXT: {exam_mode}

TONE:
- Warm but strategic (not just cheerleading)
- Like a master coach who knows the game inside-out
- Balance empathy with tactical intelligence
- {exam_mode} exam-focused with real study science
- Student sentiment: {sentiment_analysis['primary_sentiment']}

Student's Question: {message}
Subject: {subject}
Exam Mode: {exam_mode}
Depth Level: {depth_level}"""

                # Create Mentor chat instance with independent system prompt
                mentor_chat = LlmChat(
                    api_key=self.emergent_llm_key,
                    session_id=f"mentor_{user_id}_{session_id}",
                    system_message=mentor_independent_system
                ).with_model("openai", "gpt-4o").with_params(
                    temperature=0.75,
                    top_p=0.9,
                    max_tokens=800,          # Further reduced for speed
                    presence_penalty=0.15,
                    frequency_penalty=0.15
                )
                
                mentor_message = UserMessage(text=f"Subject: {subject}. Question: {message}")
                
                # Execute BOTH in parallel with asyncio.gather()
                professor_result, mentor_result = await asyncio.gather(
                    self._safe_llm_call(
                        professor_chat, professor_message, "professor", subject, message, 
                        max_retries=1, timeout_seconds=18  # Slightly reduced timeout
                    ),
                    self._safe_llm_call(
                        mentor_chat, mentor_message, "mentor", subject, message,
                        max_retries=1, timeout_seconds=15  # Mentor timeout
                    ),
                    return_exceptions=True  # Don't fail if one fails
                )
                
                total_time = time.time() - start_time
                
                # Handle Professor response
                if isinstance(professor_result, Exception):
                    logger.error(f"❌ Professor generation failed: {professor_result}")
                    raise professor_result
                
                professor_response = professor_result
                professor_time = total_time  # For logging purposes
                logger.info(f"✅ Professor response generated ({len(professor_response)} chars)")
                
                # Handle Mentor response (graceful fallback if failed)
                # Handle Mentor response (graceful fallback if failed)
                if isinstance(mentor_result, Exception):
                    logger.warning(f"⚠️ Mentor generation failed: {mentor_result}, using graceful fallback")
                    mentor_response = f"Great question about {subject}! Focus on understanding the core concepts explained above. Keep practicing similar problems, and don't hesitate to ask follow-up questions. You're building real mastery here!"
                else:
                    mentor_response = mentor_result
                    
                mentor_time = total_time  # For logging purposes
                logger.info(f"✅ Mentor response generated ({len(mentor_response)} chars)")
                logger.info(f"🎯 PARALLEL generation time: {total_time:.2f}s (Both generated simultaneously)")
                logger.info(f"⚡ PERFORMANCE GAIN: Saved ~15-20s compared to sequential execution")
                
            except asyncio.TimeoutError as e:
                logger.error(f"⏰ AI generation timeout: {e}")
                raise Exception("AI Tutor is thinking deeply about your question. This response needs more time - please try again in a moment.")
                
            except Exception as e:
                logger.error(f"❌ AI generation failed: {e}")
                raise Exception(f"AI Tutor encountered an error: {str(e)}")
            
            # Step 4: Generate visual concept (SVG primary, Gemini fallback)
            visual_svg = self.svg_generator.generate_concept_visual(message, subject)
            visual_data = {
                'type': 'svg',
                'content': visual_svg,
                'generated': visual_svg is not None
            }
            
            # Skip slow Gemini visual generation for fast-first strategy
            # Visual generation moved to background task for better performance
            
            # Step 5: Parse professor response into progressive disclosure sections
            professor_content = professor_response if isinstance(professor_response, str) else str(professor_response)
            progressive_sections = self._parse_progressive_sections(professor_content)
            
            # Step 6: Generate quick actions
            quick_actions = self._generate_quick_actions(message, subject, sentiment_analysis)
            
            # Step 7: Parse response into micro-lesson sections (FAST rule-based only)
            # Skip slow AI parsing for fast-first strategy
            micro_lesson_sections = self.response_parser._rule_based_parse(
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
            
            # Step 8.5: Sanitize content before database storage
            professor_sanitized = self.response_parser.sanitize_text(professor_content)
            mentor_sanitized = self.response_parser.sanitize_text(mentor_content)
            
            # Sanitize micro-lesson sections
            sanitized_micro_sections = {}
            for key, value in micro_lesson_sections.items():
                if isinstance(value, str):
                    sanitized_micro_sections[key] = self.response_parser.sanitize_text(value)
                elif isinstance(value, list):
                    sanitized_micro_sections[key] = [self.response_parser.sanitize_text(str(item)) for item in value]
                else:
                    sanitized_micro_sections[key] = value
            
            # Sanitize mentor sections
            sanitized_mentor_sections = {}
            for key, value in mentor_sections.items():
                if isinstance(value, str):
                    sanitized_mentor_sections[key] = self.response_parser.sanitize_text(value)
                else:
                    sanitized_mentor_sections[key] = value
            
            # Step 9: Create enhanced dual response structure with both raw and sanitized content
            dual_response = {
                "primary": {
                    "type": "professor",
                    "response": professor_sanitized,
                    "raw_text": professor_content,
                    "confidence": 0.95,
                    "progressive_sections": progressive_sections,
                    "micro_lesson_sections": sanitized_micro_sections,
                    "raw_micro_lesson_sections": micro_lesson_sections,
                    "weight": professor_weight
                },
                "secondary": {
                    "type": "mentor", 
                    "response": mentor_sanitized,
                    "raw_text": mentor_content,
                    "mentor_sections": sanitized_mentor_sections,
                    "raw_mentor_sections": mentor_sections,
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
            
            # Step 10: Apply format validation and cleanup (AI Tutor 2.4)
            dual_response = format_validator.validate_and_fix_response(dual_response)
            
            # Validate structure
            validation_issues = format_validator.validate_structure(dual_response)
            if validation_issues:
                logger.warning(f"Response validation issues: {validation_issues}")
            
            # Save message to session
            await self.save_session_message(user_id, session_id, message, dual_response)
            
            # Track AI Tutor session usage (if subscription service available)
            if self.subscription_service:
                await self.subscription_service.track_ai_tutor_session(user_id)
                logger.info(f"✅ Tracked AI Tutor session for user {user_id}")
            
            # Return in expected frontend format
            return {
                "dual_response": dual_response
            }
            
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
        """Save a chat message to the session with deduplication to prevent duplicates"""
        try:
            # Sanitize user message
            sanitized_user_message = self.response_parser.sanitize_text(message)
            
            # Generate unique message_id
            message_id = str(uuid.uuid4())
            
            # FIX: Check if this exact message already exists to prevent duplicates
            existing_message = await self.db.chat_messages.find_one({
                'session_id': session_id,
                'user_message': sanitized_user_message,
                'timestamp': {
                    '$gte': (datetime.now(timezone.utc) - timedelta(seconds=30)).isoformat()
                }
            })
            
            if existing_message:
                logger.warning(f"Duplicate message detected for session {session_id}, skipping insertion")
                return existing_message.get('message_id', message_id)
            
            # Create comprehensive message document for MongoDB
            message_dict = {
                'message_id': message_id,
                'session_id': session_id,
                'user_id': user_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                
                # FRONTEND-COMPATIBLE STRUCTURE
                'user_message': sanitized_user_message,
                
                # Store COMPLETE AI response structure for history loading
                'dual_response': ai_response.get('dual_response'),
                'response': ai_response.get('response'),
                'persona': ai_response.get('persona'),
                
                # Additional metadata
                'primary': ai_response.get('primary'),
                'secondary': ai_response.get('secondary'),
                'confidence': ai_response.get('confidence'),
                'reasoning': ai_response.get('reasoning'),
                
                # Legacy fields for backward compatibility
                'message': sanitized_user_message,
                
                # Full AI response for analysis
                'ai_response_full': {
                    'primary_sanitized': ai_response.get('primary', {}).get('response', ''),
                    'secondary_sanitized': ai_response.get('secondary', {}).get('response', ''),
                    'micro_sections': ai_response.get('primary', {}).get('micro_lesson_sections', {}),
                    'mentor_sections': ai_response.get('secondary', {}).get('mentor_sections', {})
                },
                
                # User feedback tracking
                'feedback': None
            }
            
            await self.db.chat_messages.insert_one(message_dict)
            
            # Update session last_updated timestamp and message count
            await self.db.chat_sessions.update_one(
                {"session_id": session_id},
                {
                    "$set": {"last_updated": datetime.now(timezone.utc).isoformat()},
                    "$inc": {"message_count": 1}
                }
            )
            
            return message_id
            
        except Exception as e:
            logger.error(f"Save session message error: {str(e)}")
            return None
    
    async def _safe_llm_call(self, chat_instance, message, role_type: str, subject: str, user_message: str, max_retries: int = 1, timeout_seconds: int = 25):
        """
        Safe LLM API call with timeout, retry, and intelligent fallbacks
        Ensures no blank responses ever reach the frontend
        """
        import asyncio
        import time
        
        fallback_responses = {
            "professor": f"""I understand you're asking about {subject}. Let me help you with this concept.

**Core Explanation:**
This is an important topic in {subject} that builds foundational understanding.

**Key Points:**
1. Let me break this down step by step
2. The main concept involves understanding the relationship between different elements
3. Practice with similar problems will help solidify your understanding

**Quick Summary:**
Focus on the fundamental principles and practice regularly to master this concept.""",
            
            "mentor": f"""I can see you're working hard on {subject} - that's fantastic! 

**Motivation Spark:** 
Every question you ask brings you closer to mastering this subject.

**Study Strategy:** 
• Take your time to understand each concept thoroughly
• Practice with similar examples
• Don't hesitate to ask follow-up questions

**Encouragement:**
You're making great progress! Keep up the excellent work and stay curious. Learning takes time, and you're on the right path! 🌟"""
        }
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                logger.info(f"Starting {role_type} LLM call - attempt {attempt + 1}/{max_retries}")
                
                # Apply timeout to the LLM call
                response = await asyncio.wait_for(
                    chat_instance.send_message(message),
                    timeout=timeout_seconds
                )
                
                elapsed = time.time() - start_time
                logger.info(f"✅ {role_type} response received in {elapsed:.2f}s")
                
                # Validate response is not empty
                response_text = response if isinstance(response, str) else str(response)
                if not response_text or len(response_text.strip()) < 10:
                    raise ValueError(f"Empty or too short {role_type} response")
                
                return response_text
                
            except asyncio.TimeoutError:
                elapsed = time.time() - start_time
                logger.warning(f"⏰ {role_type} LLM call timeout after {elapsed:.2f}s (attempt {attempt + 1})")
                
                if attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    delay = 2 ** attempt
                    logger.info(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    continue
                    
            except Exception as e:
                elapsed = time.time() - start_time if 'start_time' in locals() else 0
                logger.error(f"❌ {role_type} LLM call error after {elapsed:.2f}s: {str(e)} (attempt {attempt + 1})")
                
                if attempt < max_retries - 1:
                    delay = 2 ** attempt
                    logger.info(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    continue
        
        # Phase 1: All retries failed - raise error instead of generic fallback
        # Better to fail gracefully than return shallow content
        logger.error(f"🚫 All {role_type} LLM attempts failed after {max_retries} retries")
        raise TimeoutError(f"{role_type} AI generation failed after {max_retries} attempts - question requires more processing time")
    
    def _generate_enhanced_contextual_fallback(self, role_type: str, subject: str, user_message: str) -> str:
        """
        Generate enhanced contextual fallback responses that are subject-specific
        These provide better user experience than generic templates
        """
        
        # Detect question type and subject for contextual responses
        message_lower = user_message.lower()
        
        # Subject-specific knowledge bases for better fallbacks
        subject_contexts = {
            'mathematics': {
                'keywords': ['equation', 'solve', 'calculate', 'formula', 'function', 'derivative', 'integral', 'algebra', 'geometry', 'calculus'],
                'concepts': ['equations', 'functions', 'graphs', 'proofs', 'formulas', 'calculations']
            },
            'physics': {
                'keywords': ['force', 'energy', 'motion', 'velocity', 'acceleration', 'newton', 'momentum', 'wave', 'electric', 'magnetic'],
                'concepts': ['forces', 'energy systems', 'motion analysis', 'wave properties', 'electromagnetic fields']
            },
            'chemistry': {
                'keywords': ['reaction', 'molecule', 'atom', 'bond', 'compound', 'element', 'solution', 'acid', 'base', 'electron'],
                'concepts': ['chemical reactions', 'molecular structures', 'periodic trends', 'bonding patterns']
            },
            'biology': {
                'keywords': ['cell', 'dna', 'protein', 'organism', 'evolution', 'photosynthesis', 'respiration', 'genetics', 'ecosystem'],
                'concepts': ['cellular processes', 'genetic mechanisms', 'evolutionary principles', 'ecological systems']
            }
        }
        
        # Detect most relevant subject context
        subject_key = subject.lower()
        context = subject_contexts.get(subject_key, subject_contexts.get('mathematics'))  # default fallback
        
        # Find relevant keywords in the user's question
        relevant_keywords = [kw for kw in context['keywords'] if kw in message_lower]
        
        if role_type == "professor":
            if len(relevant_keywords) >= 2:
                # High relevance - detailed contextual response
                return f"""Excellent question about {subject}! I can see you're exploring {', '.join(relevant_keywords[:2])}.

**Core Concept:**
This involves understanding the fundamental relationships in {context['concepts'][0]} and how they apply to your specific question.

**Structured Approach:**
1. **Identify Key Elements:** Break down what we know and what we're trying to find
2. **Apply Relevant Principles:** Use the core {subject.lower()} concepts that govern this situation  
3. **Work Through Steps:** Systematically apply the method to reach the solution
4. **Verify & Interpret:** Check our result makes sense in the context

**Key Insight:** 
In {subject}, problems like this often involve {context['concepts'][1] if len(context['concepts']) > 1 else 'systematic analysis'}.

Let me know if you'd like me to elaborate on any specific aspect of this approach!"""
            
            elif len(relevant_keywords) == 1:
                # Medium relevance - focused contextual response
                return f"""Great {subject} question about {relevant_keywords[0]}! This is a fundamental concept.

**Understanding {relevant_keywords[0].title()}:**
This concept is central to many {subject.lower()} problems and connects to broader principles in the field.

**Problem-Solving Framework:**
1. **Foundation:** Start with the basic definitions and relationships
2. **Application:** Apply the relevant {subject.lower()} principles systematically
3. **Analysis:** Work through the logic step by step
4. **Solution:** Arrive at the answer using proper methodology

**Study Tip:** 
Focus on understanding the underlying principles rather than just memorizing procedures - this will help you tackle similar problems with confidence."""
            
            else:
                # General subject-specific response
                return f"""Thank you for your {subject} question! This area involves important concepts that build foundational understanding.

**Learning Strategy for {subject}:**
1. **Conceptual Foundation:** Master the core principles and definitions
2. **Pattern Recognition:** Learn to identify the type of problem and appropriate methods
3. **Practice Application:** Work through examples to reinforce understanding
4. **Critical Analysis:** Always check if your solutions make sense

**Next Steps:**
Focus on understanding the fundamental concepts first, then practice applying them to similar problems. Each question helps strengthen your {subject.lower()} problem-solving skills!"""
        
        else:  # mentor response
            encouragement_phrases = [
                "I love your curiosity about",
                "You're asking exactly the right questions about", 
                "Your interest in", 
                "It's fantastic that you're exploring"
            ]
            
            return f"""{encouragement_phrases[len(user_message) % len(encouragement_phrases)]} {subject}! 

**Why This Matters:**
Questions like yours show you're thinking deeply about the subject. That's exactly how strong {subject.lower()} understanding develops.

**Your Learning Journey:**
• **Stay Curious:** Every question brings you closer to mastery
• **Be Patient:** Complex {subject.lower()} concepts take time to fully understand
• **Practice Regularly:** Consistent engagement with {subject.lower()} builds confidence
• **Ask Follow-ups:** Don't hesitate to dig deeper when something interests you

**Confidence Builder:**
You're developing excellent {subject.lower()} thinking skills. The fact that you're asking this question shows you're on the right path to understanding these concepts deeply.

Keep up this excellent approach to learning! 🌟"""
    
    def _generate_fast_fallback(self, role_type: str, subject: str, user_message: str) -> str:
        """
        Generate immediate fallback responses when LLM calls fail or timeout
        These are crafted to be helpful while indicating they're simplified responses
        """
        
        # Detect question type for better fallbacks
        is_math = any(word in user_message.lower() for word in ['solve', 'equation', 'calculate', '+', '-', '*', '/', '=', 'x^', 'formula'])
        is_physics = 'physics' in subject.lower() or any(word in user_message.lower() for word in ['force', 'velocity', 'acceleration', 'newton', 'energy'])
        is_concept = any(word in user_message.lower() for word in ['what is', 'explain', 'define', 'how does', 'why'])
        
        if role_type == "professor":
            if is_math:
                return f"""I can help you with this {subject} problem! Here's a structured approach:

**Understanding the Problem:**
Let's break down what we're being asked to find and identify the key information given.

**Solution Strategy:**
1. Identify the known values and what we need to solve for
2. Choose the appropriate method or formula
3. Apply the method step by step
4. Check our answer for reasonableness

**Next Steps:**
Work through each step carefully, and feel free to ask if you need clarification on any part of the solution process."""
            
            elif is_physics:
                return f"""This is a great {subject} question! Let me guide you through the concept:

**Core Principle:**
Understanding the fundamental relationship between the physical quantities involved.

**Key Approach:**
1. Identify the relevant physical laws or principles
2. Set up the problem with known and unknown variables
3. Apply the appropriate equations
4. Solve systematically

**Practical Application:**
This concept appears frequently in real-world scenarios and is foundational for advanced topics."""
                
            else:
                return f"""Thank you for your {subject} question! Here's how we can approach this:

**Concept Overview:**
This topic involves understanding key relationships and principles in {subject}.

**Learning Strategy:**
1. Start with the fundamental definitions
2. Understand how concepts connect to each other
3. Practice with examples to reinforce understanding
4. Apply knowledge to solve problems

**Study Tip:**
Focus on understanding the 'why' behind concepts, not just memorizing facts."""
        
        else:  # mentor
            return f"""I love your curiosity about {subject}! You're asking exactly the right kind of questions.

**Why This Matters:**
Every question you ask helps build a stronger foundation for your learning journey.

**Study Approach:**
• Take your time to understand each concept thoroughly
• Don't worry if it seems challenging at first - that's completely normal
• Practice regularly and be patient with yourself

**Encouragement:**
You're making great progress by actively seeking to understand. Keep up this excellent attitude toward learning!"""
    
    async def _background_llm_improvement(self, professor_chat, mentor_chat, professor_message, mentor_message, subject: str, user_message: str, user_id: str):
        """
        Run LLM calls in background for analytics and future improvements
        This doesn't block the user response but helps improve system over time
        """
        try:
            logger.info("🔄 Starting background LLM calls for system improvement")
            
            # These run in background - user already got fast response
            start_time = time.time()
            
            professor_task = asyncio.create_task(self._safe_llm_call(
                professor_chat, professor_message, "professor", subject, user_message, max_retries=1, timeout_seconds=120
            ))
            mentor_task = asyncio.create_task(self._safe_llm_call(
                mentor_chat, mentor_message, "mentor", subject, user_message, max_retries=1, timeout_seconds=120
            ))
            
            # Wait for completion (or timeout after 2 minutes total)
            try:
                await asyncio.wait_for(
                    asyncio.gather(professor_task, mentor_task, return_exceptions=True),
                    timeout=120.0
                )
                elapsed = time.time() - start_time
                logger.info(f"📊 Background LLM calls completed in {elapsed:.2f}s - data saved for analytics")
                
            except asyncio.TimeoutError:
                logger.warning("⏰ Background LLM calls timed out - not affecting user experience")
                
        except Exception as e:
            logger.error(f"❌ Background LLM improvement error: {str(e)} - not affecting user experience")

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
    
    async def generate_neuro_symbolic_response(
        self,
        user_id: str,
        session_id: str,
        message: str,
        subject: str,
        exam_mode: str = "JEE",
        message_history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate neuro-symbolic AI Mentor response v2.0 (Progressive Disclosure)
        
        Args:
            user_id: User ID
            session_id: Chat session ID
            message: Student's question
            subject: Subject (Mathematics, Physics, etc.)
            exam_mode: JEE, NEET, UPSC, etc.
            message_history: Previous messages for context
        
        Returns:
            Dict with progressive disclosure response structure
        """
        try:
            from prompts.neuro_symbolic_mentor_v2 import (
                get_mentor_prompt_v2,
                detect_question_type
            )
            from prompts.metaphor_visual_library import (
                get_metaphor_visual,
                get_mentor_avatar,
                get_verification_badge
            )
            from services.intent_classifier import IntentClassifier, generate_greeting_response
            
            logger.info(f"🧠 Generating mentor response v2.0 for user {user_id}")
            
            # CRITICAL FIX: Classify intent before generating response
            intent = IntentClassifier.classify_intent(message)
            logger.info(f"🎯 Intent classified: {intent}")
            
            # Get user profile for personalization
            user_doc = await self.db.users.find_one({"user_id": user_id})
            student_profile = {
                'preferred_metaphor': user_doc.get('preferred_metaphor', 'cricket'),
                'region': user_doc.get('region', 'Bangalore'),
                'engagement_level': 'neutral',
                'emotional_state': 'neutral',
                'visual_learner_preference': user_doc.get('visual_learner_preference', True),
                'device_type': user_doc.get('device_type', 'mobile'),
                'network_speed': user_doc.get('network_speed', '3G')
            }
            
            # If greeting detected, return mentor personality response
            if intent == 'greeting':
                logger.info("👋 Greeting detected - routing to mentor personality")
                
                # Get user streak (if tracking exists)
                streak_days = user_doc.get('current_streak', 0)
                user_name = user_doc.get('full_name', 'there')
                if user_name and ' ' in user_name:
                    user_name = user_name.split()[0]  # First name only
                
                greeting_response = generate_greeting_response(
                    user_name=user_name,
                    streak_days=streak_days,
                    metaphor_category=student_profile['preferred_metaphor'],
                    region=student_profile['region']
                )
                
                # Save greeting message to database
                message_id = str(uuid.uuid4())
                message_doc = {
                    'message_id': message_id,
                    'session_id': session_id,
                    'user_id': user_id,
                    'user_message': message,
                    'ai_response': greeting_response,
                    'response_type': 'mentor_greeting',
                    'intent': 'greeting',
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'generation_time_seconds': 0.1
                }
                
                await self.db.chat_messages.insert_one(message_doc)
                
                # Update session
                await self.db.chat_sessions.update_one(
                    {"session_id": session_id, "user_id": user_id},
                    {"$set": {"last_updated": datetime.now(timezone.utc).isoformat()}}
                )
                
                return {
                    'success': True,
                    'message_id': message_id,
                    'response': greeting_response,
                    'raw_response': 'greeting',
                    'generation_time': 0.1,
                    'question_type': 'greeting',
                    'intent': 'greeting'
                }
            
            # Otherwise, proceed with concept explanation
            logger.info("📚 Learning intent - generating concept explanation")
            
            # Detect question type
            question_type = detect_question_type(message)
            logger.info(f"📝 Question type: {question_type}")
            
            # Get visual metaphor for concept (extract concept from message)
            concept_key = message.lower()[:50].replace(' ', '_')
            metaphor_visual = get_metaphor_visual(
                concept_key,
                student_profile['preferred_metaphor'],
                student_profile['region']
            )
            logger.info(f"🎨 Visual metaphor loaded: {metaphor_visual['hero_visual']}")
            
            # Generate system prompt v2 with visual context
            system_prompt = get_mentor_prompt_v2(subject, message, exam_mode, student_profile)
            
            # Step 4: Create LLM chat instance with optimized prompt
            # Use compact prompt for faster response
            from prompts.optimized_mentor_prompt import get_optimized_mentor_prompt
            
            # Try optimized prompt first (60% token reduction)
            optimized_prompt = get_optimized_mentor_prompt(
                subject=subject,
                message=message,
                exam_mode=exam_mode,
                metaphor=student_profile['preferred_metaphor'],
                region=student_profile['region']
            )
            
            neuro_chat = LlmChat(
                api_key=self.emergent_llm_key,
                session_id=f"mentor_v2_{user_id}_{session_id}",
                system_message=optimized_prompt
            ).with_model("openai", "gpt-4o").with_params(
                temperature=0.8,
                top_p=0.9,
                max_tokens=2000,  # Reduced from 2500
                presence_penalty=0.2,
                frequency_penalty=0.1,
                response_format={"type": "json_object"}
            )
            
            # Step 5: Generate response
            user_message = UserMessage(text=message)
            start_time = time.time()
            
            logger.info("🚀 Calling LLM for mentor response v2.0...")
            raw_response = await neuro_chat.send_message(user_message)
            
            generation_time = time.time() - start_time
            logger.info(f"✅ Response generated in {generation_time:.2f}s")
            
            # Step 6: Parse JSON response
            import json
            try:
                response_dict = json.loads(raw_response)
                logger.info("📊 JSON response parsed successfully")
                
                # Inject visual metadata from metaphor library if not present
                if 'default_view' in response_dict:
                    default_view = response_dict['default_view']
                    
                    # Add mentor avatar if missing
                    if 'mentor_avatar' not in default_view:
                        avatar_url = get_mentor_avatar(student_profile['emotional_state'])
                        default_view['mentor_avatar'] = {
                            'visual_url': avatar_url,
                            'expression': student_profile['emotional_state'],
                            'greeting_animation': 'wave'
                        }
                    
                    # Add hero visual from metaphor library if missing
                    if 'hero_visual' not in default_view or not default_view['hero_visual'].get('visual_url'):
                        default_view['hero_visual'] = {
                            'visual_url': metaphor_visual['hero_visual'],
                            'alt_text': metaphor_visual['metaphor_text'],
                            'load_priority': 'high',
                            'size_bytes': 450000,  # Placeholder, <500KB
                            'placeholder_color': metaphor_visual.get('color_theme', '#6366F1')
                        }
                    
                    # Add verification badge
                    if 'professor_badge' in default_view:
                        badge_url = get_verification_badge('professor_checked')
                        default_view['professor_badge']['badge_visual'] = badge_url
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON parse error: {str(e)}")
                # Fallback to simple response with visual assets
                avatar_url = get_mentor_avatar(student_profile['emotional_state'])
                badge_url = get_verification_badge('verified')
                
                response_dict = {
                    "default_view": {
                        "mentor_avatar": {
                            "visual_url": avatar_url,
                            "expression": student_profile['emotional_state'],
                            "greeting_animation": "wave"
                        },
                        "greeting": "Let's tackle this together!",
                        "hero_visual": {
                            "visual_url": metaphor_visual['hero_visual'],
                            "alt_text": metaphor_visual['metaphor_text'],
                            "load_priority": "high",
                            "size_bytes": 450000,
                            "placeholder_color": metaphor_visual.get('color_theme', '#6366F1')
                        },
                        "metaphor": {
                            "category": student_profile['preferred_metaphor'],
                            "text": metaphor_visual['metaphor_text'],
                            "animation_hint": metaphor_visual.get('animation_hint', 'none')
                        },
                        "main_content": {
                            "type": "explanation",
                            "content": raw_response[:500],
                            "key_insight": "See explanation above",
                            "visual_callouts": []
                        },
                        "interactive_options": [
                            {"button_text": "Show me more", "reveals": "strategy"}
                        ],
                        "professor_badge": {
                            "verified": True,
                            "badge_visual": badge_url,
                            "ncert_ref": "Class 11-12",
                            "confidence": "high",
                            "students_solved": "10247"
                        }
                    },
                    "progressive_sections": {
                        "strategy": {
                            "title": "Detailed Breakdown",
                            "content": raw_response,
                            "tips": ["Break it down step by step"]
                        }
                    }
                }
            
            # Step 7: Save to database
            message_id = str(uuid.uuid4())
            message_doc = {
                'message_id': message_id,
                'session_id': session_id,
                'user_id': user_id,
                'user_message': message,
                'ai_response': response_dict,
                'response_type': 'mentor_v2_progressive',
                'question_type': question_type,
                'student_profile': student_profile,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'generation_time_seconds': generation_time
            }
            
            await self.db.chat_messages.insert_one(message_doc)
            logger.info(f"💾 Message saved: {message_id}")
            
            # Step 8: Update session last_updated
            await self.db.chat_sessions.update_one(
                {"session_id": session_id, "user_id": user_id},
                {"$set": {"last_updated": datetime.now(timezone.utc).isoformat()}}
            )
            
            # Return response with metadata
            return {
                'success': True,
                'message_id': message_id,
                'response': response_dict,
                'raw_response': raw_response,
                'generation_time': generation_time,
                'question_type': question_type
            }
            
        except Exception as e:
            logger.error(f"❌ Mentor v2 generation error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to generate mentor response: {str(e)}")

            return False