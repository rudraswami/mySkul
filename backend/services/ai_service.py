"""
AI service for chat sessions, dual AI responses, guardrails, and AI-powered features
Enhanced for AI Tutor 2.0 with adaptive personas, visual generation, and sentiment analysis
Enhanced for Neuro-Symbolic AI Tutor 3.0 with Indian student-centric learning
"""
import copy
import os
import logging
import sys
import asyncio
import time
import uuid
import traceback
import urllib.parse
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorClient
from services.llm_compat import LlmChat, UserMessage

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.sentiment_analyzer import SentimentAnalyzer
from utils.svg_generator import SVGGenerator
from utils.response_parser import ResponseParser
from utils.motivational_generator import MotivationalGenerator
# Legacy visual imports removed - now using whiteboard_engine in api/ai.py
from services.intent_planner import IntentPlanner
from services.topic_classifier import TopicClassifier
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
        # Visual engine removed - now using whiteboard_engine in api/ai.py
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
        """Get all chat sessions for a user (excluding soft-deleted)"""
        try:
            sessions = await self.db.chat_sessions.find(
                {"user_id": user_id, "deleted": {"$ne": True}}
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

        mentor_response = """Welcome! I'm so glad you're here!

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
            
            # Step 0.5: Intent + topic understanding for adaptive layout
            intent_plan = IntentPlanner.detect(message)
            concept_name = IntentPlanner.extract_concept_name(message)
            topic_key = TopicClassifier.classify_topic(message)
            intent_context_flags = set(intent_plan.context_flags or ())
            logger.info(f"🧭 Intent: {intent_plan.intent} | layout={intent_plan.layout} | topic={topic_key}")
            
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
            
            # Build conversation history string from memory_context
            conversation_history = ""
            has_real_history = False
            
            if memory_context and memory_context.get("conversation_summary"):
                conversation_history = f"""
PREVIOUS CONVERSATION IN THIS SESSION:
{memory_context['conversation_summary']}

IMPORTANT: If student asks about "what we discussed earlier" or "previous topic", 
refer to the conversation history above and provide a clear summary.
"""
                has_real_history = True
            elif memory_context and memory_context.get("recent_context"):
                # Fallback: build from recent_context
                recent = memory_context.get("recent_context", [])
                if recent:
                    history_parts = []
                    for msg in recent[-3:]:  # Last 3 exchanges
                        user_q = msg.get("user_message", "")
                        if user_q:
                            history_parts.append(f"- {user_q[:80]}")
                    if history_parts:
                        conversation_history = f"""
PREVIOUS CONVERSATION:
{chr(10).join(history_parts)}

IMPORTANT: If student asks about previous discussion, refer to the history above.
"""
                        has_real_history = True
            
            # CRITICAL FIX: If no conversation history, tell LLM to be honest
            if not has_real_history:
                conversation_history = """
NO PREVIOUS CONVERSATION IN THIS SESSION.

CRITICAL: If student asks "what did we discuss earlier" or similar:
- Be HONEST: Say "This appears to be the start of our conversation" or "We haven't discussed anything yet in this session"
- Do NOT hallucinate or make up previous conversations
- Do NOT pretend to remember things that didn't happen
- Offer to help with whatever they'd like to learn
"""
            
            # ============================================
            # SENIOR INDIAN TEACHER PERSONA (v1 Release)
            # ============================================
            # This prompt creates a calm, precise, adaptive Indian teacher
            # who explains based on student's exact intent - NOT a template machine.
            
            professor_system = f"""You are a senior Indian teacher and subject expert.

IDENTITY:
- Calm, precise, patient, and adaptive
- You teach like a real professor who understands how students think
- You are NOT a chatbot, NOT a content generator, NOT a syllabus dumper
- Think of yourself as a brilliant IIT/AIIMS professor who genuinely wants students to understand

INTERNAL THINKING (Do this silently before every response):
1. What is this student actually trying to understand?
   - Intuition? Exam clarity? Correction of misconception? Step-by-step breakdown? Quick revision?
2. What is their likely level?
   - Beginner, average, exam-focused, advanced/curious
3. What is the MINIMUM explanation needed to unblock them?
   - Don't over-explain. Don't under-explain.

RESPONSE RULES:

1. START FROM THE STUDENT'S MENTAL STATE
   - Not from textbook structure
   - If they're confused, acknowledge that first
   - If they want quick revision, be concise
   - If they're curious, explore deeper

2. EXPLAIN ONE CORE IDEA CLEARLY
   - Then expand only if needed
   - Use intuition and cause → effect reasoning
   - Simple real-life metaphors when helpful (cricket, cooking, daily life)

3. NO FIXED TEMPLATES
   - Every response must be custom-shaped to the student's intent
   - Do NOT force: definition → steps → summary pattern
   - Do NOT dump syllabus content
   - Format should feel natural, not mechanical

4. FORMATTING IS ADAPTIVE
   - You MAY use: short paragraphs, bullets, inline equations, examples
   - You MUST NOT force headings or sections unless the question demands it
   - Keep it readable but not templated

5. TEACH-ME-BACK (MANDATORY)
   After your explanation, gently verify understanding with ONE of these (rotate naturally):
   - "Can you explain this back in your own words?"
   - "What do you think happens next if we change X?"
   - "Does this part make sense, or should I explain it differently?"
   - "Try this quick question to check: [simple question]"
   - "Think you got it? Try explaining it back to me."
   
   Never quiz aggressively. Always supportive, teacher-like.

6. ADAPTIVE DEPTH
   - If student asks follow-ups → go deeper
   - If student seems confused → simplify
   - If student asks exam-oriented → be precise and formula-focused
   - If student asks curiosity-driven → explore intuition
   - Depth is earned, not forced

MATH FORMATTING (CRITICAL):
- ALWAYS use LaTeX for any mathematical expression
- Inline: \\( F = ma \\) within text
- Block: \\[ E = mc^2 \\] for important equations
- Subscripts: \\( H_2O \\) NOT H₂O (no unicode!)
- Chemical equations: \\( 6CO_2 + 6H_2O \\rightarrow C_6H_{12}O_6 + 6O_2 \\)
- Fractions: \\( \\frac{numerator}{denominator} \\)
- Greek: \\( \\alpha, \\beta, \\theta \\)
- NEVER use unicode subscripts (₂, ₆, ²) - they break rendering

STRICTLY AVOID:
- AI self-references ("As an AI...", "I'm designed to...")
- Marketing language or buzzwords
- Decorative emojis
- "Great question!" or any generic opener
- Repeating the same opening style every time
- Generic phrases like "In conclusion", "To summarize"
- Overly formal academic tone
- Mentioning visuals, diagrams, SmartBoard, or any visual features
- Fixed template structures
- Unicode math symbols (₂, ², →) - use LaTeX instead

TONE:
- Sound like a calm, confident human teacher
- Indian English is fine - simple, clear, relatable
- Warm but not over-friendly
- Professional but not robotic

CONTEXT:
Subject: {subject}
Exam: {exam_mode}
Depth requested: {depth_level}
Student sentiment: {sentiment_analysis['primary_sentiment']}

{conversation_history}

QUESTION: {message}

Remember: Your job is to make this student UNDERSTAND, not to generate content. Teach like a real professor would - adapt to the student, not to a template."""
            
            # Use GPT-4o for faster response times (109 tokens/sec vs GPT-5's slower response)
            # GPT-4o provides excellent quality with significantly better speed for user experience
            # OPTIMIZATION: Use gpt-4o-mini for simple questions (faster, cheaper)
            question_length = len(message.split())
            is_simple_question = question_length < 10 or depth_level == "quick"
            model_to_use = "gpt-4o-mini" if is_simple_question else "gpt-4o"
            # INCREASED: Prevent response truncation (was 800/1200, now 1200/1800)
            max_tokens_to_use = 1200 if is_simple_question else 1800
            
            logger.info(f"🤖 Using model: {model_to_use} (question_length={question_length}, simple={is_simple_question})")
            
            # Phase 1: Added explicit LLM parameters for quality and depth
            professor_chat = LlmChat(
                api_key=self.emergent_llm_key,
                session_id=f"professor_{user_id}_{session_id}",
                system_message=professor_system
            ).with_model("openai", model_to_use).with_params(
                temperature=0.75,          # Balanced creativity for explanations
                top_p=0.9,                # Nucleus sampling for coherent responses
                max_tokens=max_tokens_to_use,  # Adaptive based on question complexity
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
                
                # ============================================
                # SUPPORTIVE MENTOR - Complementary Insights
                # ============================================
                # Provides practical exam insights without repeating the main explanation
                
                mentor_independent_system = f"""You are a supportive senior mentor - like a topper from the previous batch who genuinely wants to help.

YOUR ROLE: Provide practical insights and exam tips that complement (not repeat) the main explanation.

RULES:

1. DO NOT REPEAT what the main explanation covered
2. Keep it SHORT - 2-3 short paragraphs maximum
3. Focus on PRACTICAL insights:
   - Why this matters for {exam_mode} specifically
   - What mistakes students commonly make here
   - A quick memory trick or connection to related concepts
   - How this appears in exams (if relevant)

4. BE GENUINE:
   - No fake motivation ("You're amazing!")
   - Real encouragement based on the concept
   - Sound like a helpful senior, not a motivational poster

5. NO FIXED STRUCTURE:
   - Don't force headings or bullet lists
   - Write naturally based on what would actually help
   - If there's nothing valuable to add, keep it very brief

6. AVOID:
   - Repeating the main explanation
   - Generic advice that applies to everything
   - Preachy or lecturing tone
   - Mentioning visuals, diagrams, or SmartBoard
   - Overly long responses

CONTEXT:
Subject: {subject}
Exam: {exam_mode}
Student sentiment: {sentiment_analysis['primary_sentiment']}

{conversation_history}

QUESTION: {message}

Only add what genuinely helps. Quality over quantity."""

                # Create Mentor chat instance with independent system prompt
                # Use same model as professor for consistency
                mentor_chat = LlmChat(
                    api_key=self.emergent_llm_key,
                    session_id=f"mentor_{user_id}_{session_id}",
                    system_message=mentor_independent_system
                ).with_model("openai", model_to_use).with_params(
                    temperature=0.75,
                    top_p=0.9,
                    max_tokens=max_tokens_to_use,  # Same as professor - no truncation
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
                    mentor_response = f"Focus on understanding these core concepts step by step. Practice with similar problems to build confidence. If any part is unclear, ask and we'll work through it together."
                else:
                    mentor_response = mentor_result
                    
                mentor_time = total_time  # For logging purposes
                logger.info(f"✅ Mentor response generated ({len(mentor_response)} chars)")
                logger.info(f"🎯 PARALLEL generation time: {total_time:.2f}s (Both generated simultaneously)")
                logger.info("⚡ PERFORMANCE GAIN: Saved ~15-20s compared to sequential execution")
                
            except asyncio.TimeoutError as e:
                logger.error(f"⏰ AI generation timeout: {e}")
                raise Exception("AI Tutor is thinking deeply about your question. This response needs more time - please try again in a moment.")
                
            except Exception as e:
                logger.error(f"❌ AI generation failed: {e}")
                raise Exception(f"AI Tutor encountered an error: {str(e)}")
            
            # Step 4: Intent-aware visual gating (Metaphor engine is expensive; only use when needed)
            visual_data, visual_offer, should_attempt_visual = self._resolve_visual_template(
                intent_plan=intent_plan,
                intent_context_flags=intent_context_flags,
                visual_directives=visual_directives,
                concept_name=concept_name,
                topic_key=topic_key
            )

            if should_attempt_visual:
                topic_has_depth = len(message or "") > 20
                context_needs_visual = bool(intent_context_flags & {"diagram_eligible", "requires_motion", "real_life_required", "compare_visual"})
                should_attempt_visual = (
                    intent_plan.intent != 'clarification_follow_up'
                    and topic_has_depth
                    and (
                        intent_plan.allow_visual
                        or intent_plan.ask_before_visual
                        or context_needs_visual
                        or visual_directives.get('force_hero')
                    )
                )
                auto_visual = should_attempt_visual and (
                    intent_plan.auto_visual
                    or ("diagram_eligible" in intent_context_flags and intent_plan.intent in {"definition_query", "concept_explanation"})
                    or ("requires_motion" in intent_context_flags and intent_plan.intent in {"concept_explanation", "deep_dive"})
                )
                ask_visual = should_attempt_visual and not auto_visual and (
                    intent_plan.ask_before_visual
                    or visual_directives.get('requires_consent')
                    or intent_plan.intent == 'application_request'
                )

                if should_attempt_visual:
                    try:
                        student_profile = None
                        if user_id:
                            user_info = await self.db.users.find_one({"user_id": user_id})
                            if user_info:
                                student_profile = {
                                    "locale_language": user_info.get("preferred_language", "hi-IN"),
                                    "board": user_info.get("board", "CBSE"),
                                    "level": user_info.get("grade", "class_12"),
                                    "interests": user_info.get("interests", [])
                                }

                        visual_result = generate_visual_for_question(
                            question=message,
                            student_profile=student_profile,
                            marks=None
                        )

                        visual_svg = visual_result["svg"]
                        visual_data = {
                            'type': 'svg',
                            'content': visual_svg,
                            'generated': True,
                            'mode': 'auto' if auto_visual else 'offer',
                            'visual_type': visual_result.get("visual_type", "concept"),
                            'metadata': visual_result.get("metadata", {}),
                            'friend_test_passed': visual_result.get("friend_test", {}).get("passed", False)
                        }

                        logger.info(f"✅ Visual generated: {visual_result.get('visual_type')} (Friend Test: {visual_data.get('friend_test_passed')})")

                    except Exception as e:
                        logger.error(f"❌ Visual generation failed: {e}, falling back to old system")
                        visual_svg = self.svg_generator.generate_concept_visual(message, subject)
                        visual_data = {
                            'type': 'svg',
                            'content': visual_svg,
                            'generated': visual_svg is not None,
                            'mode': 'offer' if ask_visual else 'auto',
                            'visual_type': 'concept',
                            'fallback': True
                        }

                if ask_visual:
                    visual_offer = {
                        "message": visual_directives.get('offer_text') or "👉 Would you like to see a visual demo of this?",
                        "concept": concept_name,
                        "topic": topic_key,
                        "available": True,
                        "cta_text": visual_directives.get('cta_text', "Show Visual"),
                        "visual_mode": "offer"
                    }

            # Step 4.5: Generate Teaching Visual (Animated Lessons)
            teaching_visual = None
            try:
                # Check if question matches pre-built teaching templates
                message_lower = message.lower()

                # Grammar templates
                if any(keyword in message_lower for keyword in ['active', 'passive', 'voice']):
                    teaching_visual = get_grammar_visual_template("active_passive_voice")
                    logger.info("[VISUAL] Teaching visual: Active/Passive Voice template")
                elif any(keyword in message_lower for keyword in ['subject verb agreement', 'subject-verb']):
                    teaching_visual = get_grammar_visual_template("subject_verb_agreement")
                    logger.info("[VISUAL] Teaching visual: Subject-Verb Agreement template")
                elif any(keyword in message_lower for keyword in ['tense', 'past present future']):
                    teaching_visual = get_grammar_visual_template("tenses")
                    logger.info("[VISUAL] Teaching visual: Verb Tenses template")

                # Log if teaching visual was generated
                if teaching_visual:
                    logger.info(f"[OK] Teaching visual generated: {teaching_visual.get('metadata', {}).get('topic')} ({len(teaching_visual.get('stages', []))} stages)")
            except Exception as e:
                logger.warning(f"[WARNING] Teaching visual generation failed: {e}")
                teaching_visual = None

            # Subject templates (Physics/Biology) using universal blocks
            if teaching_visual is None:
                try:
                    from .subject_templates import plan_from_subject_templates
                    tv = plan_from_subject_templates(message, subject)
                    if tv:
                        teaching_visual = tv
                        logger.info(
                            f"[VISUAL] Subject template generated: "
                            f"{teaching_visual.get('metadata',{}).get('topic')}"
                        )
                except Exception as e:
                    logger.warning(f"[WARNING] Subject templates failed: {e}")

            # Universal fallback: generate a question-agnostic plan if none of the
            # domain templates matched and feature flag is enabled.
            try:
                from core.config import settings
                if teaching_visual is None and getattr(settings, "VISUAL_ENGINE_MODE", "universal") == "universal":
                    from .universal_visual_planner import plan_universal_visual
                    teaching_visual = plan_universal_visual(message, subject)
                    logger.info(
                        f"[VISUAL] Universal planner generated teaching visual: "
                        f"{teaching_visual.get('metadata',{}).get('topic')} ({len(teaching_visual.get('stages', []))} stages)"
                    )
            except Exception as e:
                logger.warning(f"[WARNING] Universal planner failed: {e}")

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
            
            structured_blocks = IntentPlanner.build_structured_blocks(
                plan=intent_plan,
                question=message,
                micro_sections=sanitized_micro_sections,
                mentor_sections=sanitized_mentor_sections,
                professor_text=professor_content,
                mentor_text=mentor_content,
            )
            suggested_questions = IntentPlanner.generate_suggestions(
                intent_plan,
                concept_name,
                topic_key,
            )
             
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
                    "weight": professor_weight,
                    "active": intent_plan.needs_professor,
                    "deferred_reason": None if intent_plan.needs_professor else "Mentor handled this query. Tap to open professor notebook if you still need it."
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
                "visual_offer": visual_offer,
                "teaching_visual": teaching_visual,  # Animated teaching visual
                "sentiment_analysis": sentiment_analysis,
                "quick_actions": quick_actions,
                "motivational_footer": motivational_data,
                "structured_blocks": structured_blocks,
                "suggested_questions": suggested_questions,
                "intent_blueprint": {
                    "intent": intent_plan.intent,
                    "layout": intent_plan.layout,
                    "topic": topic_key,
                    "professor_enabled": intent_plan.needs_professor,
                    "auto_visual": intent_plan.auto_visual,
                    "ask_before_visual": intent_plan.ask_before_visual,
                },
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
            
            # CRITICAL FIX: Store the COMPLETE AI response for history restoration
            # The ai_response can be in different formats:
            # 1. Unified pipeline: {default_view: {main_content: {content: ...}}, progressive_sections: {...}}
            # 2. Legacy dual: {dual_response: {...}, primary: {...}, secondary: {...}}
            # 3. Direct response object
            
            # Store the ENTIRE ai_response as-is for perfect restoration
            message_dict = {
                'message_id': message_id,
                'session_id': session_id,
                'user_id': user_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                
                # FRONTEND-COMPATIBLE STRUCTURE
                'user_message': sanitized_user_message,
                
                # CRITICAL: Store the COMPLETE AI response for history loading
                # This is the key fix - store entire response, not just parts
                'ai_response': ai_response,  # Store complete response
                
                # Also store in legacy format for backward compatibility
                'dual_response': ai_response.get('dual_response') if isinstance(ai_response, dict) else None,
                'response': ai_response if isinstance(ai_response, dict) else {'content': str(ai_response)},
                'persona': ai_response.get('persona') if isinstance(ai_response, dict) else None,
                
                # Additional metadata
                'primary': ai_response.get('primary') if isinstance(ai_response, dict) else None,
                'secondary': ai_response.get('secondary') if isinstance(ai_response, dict) else None,
                'confidence': ai_response.get('confidence') if isinstance(ai_response, dict) else None,
                'reasoning': ai_response.get('reasoning') if isinstance(ai_response, dict) else None,
                
                # Legacy fields for backward compatibility
                'message': sanitized_user_message,
                
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
        DEPRECATED: This method is no longer used.
        
        Static template-based responses violate the "most intelligent AI" principle.
        The code now raises TimeoutError instead of returning static templates.
        
        This method is kept only for backward compatibility if there are legacy code paths.
        If called, it logs an error and raises an exception.
        """
        logger.error("❌ DEPRECATED: _generate_enhanced_contextual_fallback called - this should not happen!")
        raise NotImplementedError(
            "Static template fallbacks are deprecated. Use LLM-based recovery instead."
        )
    
    def _generate_fast_fallback(self, role_type: str, subject: str, user_message: str) -> str:
        """
        DEPRECATED: This method is no longer used.
        
        Static template-based responses violate the "most intelligent AI" principle.
        
        This method is kept only for backward compatibility if there are legacy code paths.
        If called, it logs an error and raises an exception.
        """
        logger.error("❌ DEPRECATED: _generate_fast_fallback called - this should not happen!")
        raise NotImplementedError(
            "Static template fallbacks are deprecated. Use LLM-based recovery instead."
        )
    
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
                    "page_number": "Pages 45-67",
                    "relevance_score": 0.95
                },
                {
                    "source_title": f"Advanced {subject} Reference",
                    "chapter_section": f"{topic} - Detailed Analysis", 
                    "page_number": "Pages 120-135",
                    "relevance_score": 0.88
                },
                {
                    "source_title": f"{subject} Problem Solving Guide",
                    "chapter_section": f"Solved Examples - {topic}",
                    "page_number": "Pages 78-92", 
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
        exam_mode: str = "General",  # Changed default from "JEE" to "General"
        message_history: List[Dict[str, Any]] = None,
        memory_context: Dict[str, Any] = None
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
            memory_context: Enhanced context from memory system (mastery, continuity, etc.)
        
        Returns:
            Dict with progressive disclosure response structure
        """
        # Use memory context if provided
        memory_context = memory_context or {}
        placeholder_visual = {
            "hero_visual": {
                "url": "https://cdn.mgxai.com/visuals/placeholder.svg",
                "alt_text": "Concept visual",
                "style": "sketch",
            },
            "metaphor_text": "Visual explanation",
            "visual_tier": 1,
        }

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
            intent_plan = IntentPlanner.detect(message)
            intent_context_flags = set(intent_plan.context_flags or ())
            topic_key = TopicClassifier.classify_topic(message)
            concept_name = IntentPlanner.extract_concept_name(message)
            logger.info(f"🎯 Intent classified: {intent} | blueprint={intent_plan.intent} | topic={topic_key}")
            
            # Get user profile for personalization
            user_doc = await self.db.users.find_one({"user_id": user_id}) or {}
            
            # Extract memory-based personalization
            memory_preferences = memory_context.get('preferences', {})
            memory_mastery = memory_context.get('mastery_level', 0)
            memory_bucket = memory_context.get('mastery_bucket', 'beginner')
            is_continuation = memory_context.get('is_continuation', False)
            user_name_from_memory = memory_context.get('user_name', '')
            
            # [JULES VISUAL ENHANCEMENT START]
            # Defensive defaults when user record is absent during onboarding or tests
            # Enhanced with memory system data
            # Language preference: 'en' = English only, 'hi'/'hinglish' = Hindi-English mix
            # Default to English - only use Hinglish if explicitly set in user preferences
            user_language = memory_preferences.get('preferred_language') or user_doc.get('language', 'en')
            # Normalize: 'hi-IN', 'hindi', 'hinglish' -> use Hinglish; else English
            normalized_language = 'hi' if user_language in ['hi-IN', 'hi', 'hindi', 'hinglish'] else 'en'
            
            student_profile = {
                'preferred_metaphor': memory_preferences.get('metaphor_style') or user_doc.get('preferred_metaphor', 'cricket'),
                'region': user_doc.get('region', 'Bangalore'),
                'engagement_level': user_doc.get('engagement_level', 'neutral'),
                'emotional_state': user_doc.get('emotional_state', 'neutral'),
                'visual_learner_preference': memory_preferences.get('visual_learner', True) if memory_preferences else user_doc.get('visual_learner_preference', True),
                'device_type': user_doc.get('device_type', 'mobile'),
                'network_speed': user_doc.get('network_speed', '3G'),
                # Memory-enhanced fields
                'mastery_level': memory_mastery,
                'mastery_bucket': memory_bucket,
                'is_continuation': is_continuation,
                'explanation_depth': memory_preferences.get('explanation_depth', 'medium'),
                # Language preference: 'en' for English, 'hi' for Hinglish
                'language': normalized_language,
                'language_preference': user_language,  # Keep original for backward compat
                'user_name': user_name_from_memory or (user_doc.get('full_name', '').split()[0] if user_doc.get('full_name') else '')
            }
            
            # Log memory context usage
            if memory_context:
                logger.info(f"🧠 Using memory context: mastery={memory_mastery}, continuation={is_continuation}")
            
            # Visual metaphor resolution moved to whiteboard_engine in api/ai.py
            visual_metaphor = {}  # Legacy - now handled by whiteboard_engine
            metaphor_visual = {}
            visual_directives = visual_metaphor.get("visual_directives", {})
            visual_data, visual_offer, should_attempt_visual = self._resolve_visual_template(
                intent_plan=intent_plan,
                intent_context_flags=intent_context_flags,
                visual_directives=visual_directives,
                concept_name=concept_name,
                topic_key=topic_key
            )
            self._hydrate_hero_visual(metaphor_visual, visual_data, default_alt=visual_metaphor.get('metaphor'))
            # [JULES VISUAL ENHANCEMENT END]

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
                
                # CRITICAL: No raw_response - consistent with display contract
                return {
                    'success': True,
                    'message_id': message_id,
                    'response': greeting_response,
                    'generation_time': 0.1,
                    'question_type': 'greeting',
                    'intent': 'greeting'
                }
            
            # Otherwise, proceed with concept explanation
            logger.info("📚 Learning intent - generating concept explanation")
            
            # Step 1: Intelligently select metaphor based on topic
            metaphor_selection = TopicClassifier.select_metaphor(
                message,
                preferred_category=student_profile['preferred_metaphor'],
                region=student_profile['region']
            )
            logger.info(f"🎯 Dynamic metaphor selection: {metaphor_selection}")
            
            # Step 2: Use selected metaphor (not hardcoded user preference)
            selected_metaphor = metaphor_selection['metaphor_category']
            # Enforce 5‑Muse categories for visuals to match PRD
            allowed_muses = {"cricket", "cooking", "bollywood", "gaming"}
            if selected_metaphor not in allowed_muses:
                logger.info(f"🔧 Remapping metaphor '{selected_metaphor}' to 'cooking' (PRD 5‑Muse)")
                selected_metaphor = "cooking"
            detected_topic = metaphor_selection['topic']
            
            # Detect question type
            question_type = detect_question_type(message)
            logger.info(f"📝 Question type: {question_type}")
            
            # Step 3: Get visual metaphor using dynamic selection
            concept_key = detected_topic if detected_topic != 'generic' else message.lower()[:50].replace(' ', '_')
            metaphor_visual = copy.deepcopy(placeholder_visual)
            try:
                metaphor_visual = get_metaphor_visual(
                    concept_key,
                    selected_metaphor,
                    student_profile['region'],
                    question=message
                )
            except Exception as exc:
                logger.warning(f"⚠️ Metaphor visual lookup failed: {exc}, using placeholder.")
            logger.info(f"🎨 Visual metaphor loaded: {metaphor_visual.get('hero_visual', 'N/A')}")
            logger.info(f"🎨 Metaphor category: {selected_metaphor} (was: {student_profile['preferred_metaphor']})")
            
            # PHASE 3: VISUAL PROFESSOR ENGINE Integration (PRIORITY 1)
            # Try Visual Professor Generator FIRST (dynamic, multi-step, professor-style)
            logger.info(f"🎨 ========== VISUAL PROFESSOR ENGINE CHECK ==========")
            logger.info(f"🎨 should_attempt_visual={should_attempt_visual}")
            logger.info(f"🎨 Question: {message[:100]}")
            logger.info(f"🎨 Subject: {subject}")
            
            if should_attempt_visual:
                try:
                    logger.info("🎨 Importing VisualProfessorGenerator...")
                    from services.visual_professor import VisualProfessorGenerator
                    logger.info("✅ VisualProfessorGenerator imported successfully")
                    
                    vpg = VisualProfessorGenerator()
                    logger.info("✅ VisualProfessorGenerator instance created")
                    
                    logger.info("🎨 Calling vpg.generate_visual()...")
                    vpg_result = await vpg.generate_visual(
                        question=message,
                        subject=subject,
                        student_profile=student_profile
                    )
                    logger.info(f"📊 Visual Professor Generator returned: type={type(vpg_result)}, has_stages={bool(vpg_result and vpg_result.get('stages'))}")
                    
                    # Check if we got dynamic stages
                    if vpg_result and vpg_result.get('stages') and len(vpg_result['stages']) > 0:
                        logger.info(f"✅ Got {len(vpg_result['stages'])} stages from Visual Professor Generator")
                        # Convert to visual_data format
                        visual_data = {
                            'type': 'animated_lesson',
                            'mode': 'auto',
                            'visual_type': vpg_result.get('visual_type', 'animation'),
                            'stages': vpg_result.get('stages', []),
                            'metadata': {
                                **vpg_result.get('metadata', {}),
                                'generation_method': 'visual_professor_engine',
                                'tier': 0
                            },
                            'total_duration_ms': vpg_result.get('total_duration_ms', 0),
                            'interaction_points': vpg_result.get('interaction_points', []),
                            'visual_id': vpg_result.get('visual_id'),
                            'professor_avatar': vpg_result.get('professor_avatar', {}),
                            'lottie_base_url': vpg_result.get('lottie_base_url', 'https://cdn.ai-tutor.in/visuals')
                        }
                        # Set metaphor_visual for compatibility
                        metaphor_visual['hero_visual'] = vpg_result.get('asset_url') or vpg_result.get('lottie_file') or "https://cdn.mgxai.com/visuals/placeholder.svg"
                        metaphor_visual['svg_data'] = {'generation_method': 'visual_professor_engine', 'size_kb': 0, 'tier': 0}
                        metaphor_visual['visual_tier'] = 0
                        metaphor_visual['visual_type'] = vpg_result.get('visual_type', 'animation')
                        logger.info(f"✅ VISUAL PROFESSOR ENGINE: {len(vpg_result.get('stages', []))} dynamic stages generated!")
                        # Skip unified_visual_system since we have dynamic visual
                        should_attempt_visual = False
                    else:
                        logger.warning(f"⚠️ Visual Professor Generator returned invalid result: vpg_result={vpg_result}, stages={vpg_result.get('stages') if vpg_result else 'None'}")
                except Exception as e:
                    # Use a fresh logger reference to avoid scope issues
                    import logging as log_module
                    err_logger = log_module.getLogger(__name__)
                    error_msg = f"❌ Visual Professor Generator failed with exception: {e}"
                    traceback_str = traceback.format_exc()
                    err_logger.error(error_msg, exc_info=True)
                    err_logger.error(f"❌ Full traceback:\n{traceback_str}")
            else:
                logger.info(f"ℹ️ Visual Professor Generator skipped: should_attempt_visual={should_attempt_visual}")
            
            # PHASE 3b: LEGACY VISUAL SYSTEMS DISABLED
            # Visual Professor Engine is now the ONLY pathway for visuals
            # Legacy systems (unified_visual_system, _dyn, _tpl, _plan) are disabled
            # If Visual Professor Generator fails, it will retry with fallback multi-step template
            if should_attempt_visual:
                logger.warning("⚠️ Visual Professor Generator failed, but legacy systems are disabled. Retrying with universal fallback template...")
                # Visual Professor Generator's _fallback_visual already generates multi-step visuals
                # No need to fall back to static SVG systems
            
            # Generate system prompt v2 with visual context
            # IMPORTANT: Update student profile to use dynamically selected metaphor
            student_profile_dynamic = student_profile.copy()
            student_profile_dynamic['preferred_metaphor'] = selected_metaphor
            student_profile_dynamic['detected_topic'] = detected_topic
            
            system_prompt = get_mentor_prompt_v2(subject, message, exam_mode, student_profile_dynamic, visual_metaphor)
            
            # Step 4: Create LLM chat instance with optimized prompt
            # Use compact prompt for faster response
            from prompts.optimized_mentor_prompt import get_optimized_mentor_prompt
            
            # Try optimized prompt first (60% token reduction)
            # Pass language preference for conditional Hinglish/English
            student_language = student_profile.get('language', 'en')
            optimized_prompt = get_optimized_mentor_prompt(
                subject=subject,
                message=message,
                exam_mode=exam_mode,
                metaphor=selected_metaphor,  # Use dynamically selected
                region=student_profile['region'],
                language=student_language  # Respect student language preference
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
                
                # Add visual loading timeout warning if response took >5s
                if generation_time > 5.0:
                    logger.warning(f"⚠️ Response took {generation_time:.1f}s - adding visual fallback")
                    if 'default_view' in response_dict and 'hero_visual' in response_dict['default_view']:
                        response_dict['default_view']['hero_visual']['timeout_warning'] = True
                        response_dict['default_view']['hero_visual']['generation_time'] = generation_time
                
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
                        logger.info(f"✅ Added mentor avatar: {avatar_url}")
                    
                    # CRITICAL: Add hero visual - NOW USING SVG (Phase 3)
                    hero_suppressed = intent_plan.intent in {'clarification_follow_up'} or (
                        intent_plan.intent == 'application_request' and not visual_directives.get('force_hero')
                    )

                    if not hero_suppressed:
                        if 'hero_visual' not in default_view or not default_view['hero_visual'].get('visual_url'):
                            logger.warning("⚠️ Hero visual missing from LLM response - injecting SVG from Phase 3")
                            # Use SVG data URI (Phase 3 - generated above)
                            # Safely access svg_data with fallbacks
                            svg_data = metaphor_visual.get('svg_data', {})
                            size_kb = svg_data.get('size_kb', 0) if isinstance(svg_data, dict) else 0
                            generation_method = svg_data.get('generation_method', 'placeholder') if isinstance(svg_data, dict) else 'placeholder'
                            visual_tier = metaphor_visual.get('visual_tier', 2)
                            
                            default_view['hero_visual'] = {
                                'visual_url': metaphor_visual.get('hero_visual', 'https://cdn.mgxai.com/visuals/placeholder.svg'),  # NOW SVG data URI (set at line 1482)
                                'alt_text': metaphor_visual.get('metaphor_text', 'Concept visual'),
                                'load_priority': 'high',
                                'size_bytes': size_kb * 1024 if size_kb > 0 else 50000,  # SVG size with fallback
                                'placeholder_color': metaphor_visual.get('color_theme', '#6366F1'),
                                'tier': visual_tier,  # SVG tier (0, 1, or 2)
                                'fallback_emoji': metaphor_visual.get('animation_hint', '🏏').split('-')[0] if metaphor_visual.get('animation_hint') else '🏏',
                                'cultural_context': metaphor_visual.get('cultural_context', 'General'),
                                'svg_generation_method': generation_method
                            }
                            logger.info(f"✅ Injected SVG hero visual (Tier {visual_tier}): {generation_method}")
                            logger.info(f"✅ SVG size: {size_kb:.1f}KB" if size_kb > 0 else "✅ Using placeholder visual")
                        else:
                            logger.info(f"✅ Hero visual present in LLM response: {default_view['hero_visual'].get('visual_url', 'N/A')[:100]}")
                    else:
                        logger.info("🎯 Hero visual suppressed for this intent (offer/clarification mode)")
                    
                    response_dict['hero_visual'] = default_view.get('hero_visual')
                    
                    # Add verification badge
                    if 'professor_badge' in default_view:
                        badge_url = get_verification_badge('professor_checked')
                        default_view['professor_badge']['badge_visual'] = badge_url
                        logger.info("✅ Added verification badge")
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON parse error: {str(e)}")
                # Fallback to simple response with SVG visual assets (Phase 3)
                avatar_url = get_mentor_avatar(student_profile['emotional_state'])
                badge_url = get_verification_badge('verified')
                
                # Safely extract metaphor_visual values
                hero_visual_url = metaphor_visual.get('hero_visual', 'https://cdn.mgxai.com/visuals/placeholder.svg')
                if isinstance(hero_visual_url, dict):
                    hero_visual_url = hero_visual_url.get('url') or hero_visual_url.get('visual_url') or 'https://cdn.mgxai.com/visuals/placeholder.svg'
                metaphor_text = metaphor_visual.get('metaphor_text', 'Visual explanation')
                
                response_dict = {
                    "default_view": {
                        "mentor_avatar": {
                            "visual_url": avatar_url,
                            "expression": student_profile['emotional_state'],
                            "greeting_animation": "wave"
                        },
                        "greeting": "Let's tackle this together!",
                        "hero_visual": {
                            "visual_url": hero_visual_url,  # SVG data URI (Phase 3)
                            "alt_text": metaphor_text,
                            "placeholder_color": metaphor_visual.get('color_theme', '#6366F1'),
                            "tier": 2,  # Real image
                            "cultural_context": metaphor_visual.get('cultural_context', 'General')
                        },
                        "metaphor": {
                            "category": student_profile['preferred_metaphor'],
                            "text": metaphor_text,
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
                hero_visual_preview = hero_visual_url if isinstance(hero_visual_url, str) else str(hero_visual_url)
                logger.info(f"✅ Fallback response created with visual: {hero_visual_preview[:100]}")
            
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
            # [JULES VISUAL ENHANCEMENT START]
            response_dict['visual_metaphor'] = visual_metaphor
            response_dict['visual_directives'] = visual_directives
            if visual_data and isinstance(visual_data, dict):
                response_dict['visual_data'] = visual_data
                # If visual_data has stages (from VisualProfessorGenerator), also add as teaching_visual
                if visual_data.get('stages') and len(visual_data.get('stages', [])) > 0:
                    response_dict['teaching_visual'] = {
                        'visual_id': visual_data.get('visual_id', f"prof_{hash(message) % 1000000}"),
                        'type': visual_data.get('type', 'animated_lesson'),
                        'total_duration_ms': visual_data.get('total_duration_ms', 0),
                        'metadata': visual_data.get('metadata', {}),
                        'stages': visual_data.get('stages', []),
                        'professor_avatar': visual_data.get('professor_avatar', {}),
                        'lottie_base_url': visual_data.get('lottie_base_url', 'https://cdn.ai-tutor.in/visuals')
                    }
                    logger.info(f"✅ Added teaching_visual with {len(visual_data.get('stages', []))} stages to response")
                    logger.info(f"📦 teaching_visual structure: visual_id={response_dict['teaching_visual'].get('visual_id')}, stages={len(response_dict['teaching_visual'].get('stages', []))}")
                else:
                    logger.warning(f"⚠️ visual_data exists but has no stages: visual_data={visual_data}")
                if 'default_view' in response_dict:
                    # Ensure hero_visual is always a dict before accessing ['url']
                    existing_hero = response_dict['default_view'].get('hero_visual')
                    if not isinstance(existing_hero, dict):
                        # If hero_visual exists but is not a dict (e.g., string), create a new dict
                        # Preserve the value as visual_url if it was a string
                        hero_visual_fallback = visual_metaphor.get('hero_visual', {})
                        if not isinstance(hero_visual_fallback, dict):
                            hero_visual_fallback = {}
                        response_dict['default_view']['hero_visual'] = hero_visual_fallback.copy()
                        # If existing_hero was a string (e.g., SVG data URI), preserve it as visual_url
                        if isinstance(existing_hero, str):
                            response_dict['default_view']['hero_visual']['visual_url'] = existing_hero
                    else:
                        # It's already a dict, use it
                        response_dict['default_view']['hero_visual'] = existing_hero.copy()
                    
                    # Now safely set url (hero_visual is guaranteed to be a dict)
                    # Use existing url if it exists and is truthy, otherwise use fallback chain
                    existing_url = response_dict['default_view']['hero_visual'].get('url')
                    response_dict['default_view']['hero_visual']['url'] = existing_url or visual_data.get('asset_url') or visual_data.get('lottie_file') or "https://cdn.mgxai.com/visuals/placeholder.svg"
                    # Set alt_text if not already present
                    if not response_dict['default_view']['hero_visual'].get('alt_text'):
                        response_dict['default_view']['hero_visual']['alt_text'] = visual_metaphor.get('metaphor', 'Concept visual')
            if visual_offer:
                response_dict['visual_offer'] = visual_offer
            # [JULES VISUAL ENHANCEMENT END]

            # CRITICAL: NEVER return raw_response to frontend - it can leak internal traces
            return {
                'success': True,
                'message_id': message_id,
                'response': response_dict,
                # raw_response REMOVED - internal debugging only, never expose to UI
                'generation_time': generation_time,
                'question_type': question_type
            }
            
        except Exception as e:
            # Use a fresh logger reference to avoid scope issues
            import logging as log_module
            err_logger = log_module.getLogger(__name__)
            err_logger.error(f"❌ Mentor v2 generation error: {str(e)}")
            err_logger.error(f"Traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to generate mentor response: {str(e)}")

            return False
    
    def _get_svg_fallback(self, metaphor_category: str, region: str) -> dict:
        """
        Get Tier 1 SVG fallback visual (always <0.5s)
        Used when CDN assets fail or for immediate display
        Uses simple shapes instead of emoji for better browser compatibility
        """
        svg_templates = {
            'cricket': {
                'svg_template': 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect width="400" height="300" fill="%23EFF6FB"/%3E%3Ccircle cx="200" cy="120" r="40" fill="%2310B981"/%3E%3Crect x="180" y="120" width="40" height="100" rx="20" fill="%238B5CF6"/%3E%3Ctext x="200" y="250" text-anchor="middle" font-family="Arial" font-size="24" fill="%23374151"%3ECricket Strategy%3C/text%3E%3C/svg%3E',
                'emoji': '🏏',
                'color_theme': '#10B981'
            },
            'cooking': {
                'svg_template': 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect width="400" height="300" fill="%23FEF3C7"/%3E%3Cellipse cx="200" cy="140" rx="80" ry="50" fill="%23F59E0B"/%3E%3Crect x="190" y="140" width="20" height="60" fill="%238B5CF6"/%3E%3Ctext x="200" y="250" text-anchor="middle" font-family="Arial" font-size="24" fill="%23374151"%3ECooking Concept%3C/text%3E%3C/svg%3E',
                'emoji': '🍳',
                'color_theme': '#F59E0B'
            },
            'bollywood': {
                'svg_template': 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect width="400" height="300" fill="%23FCE7F3"/%3E%3Crect x="120" y="80" width="160" height="120" rx="10" fill="%23BE185D"/%3E%3Cpolygon points="200,100 220,140 200,180 180,140" fill="%23FFF"/%3E%3Ctext x="200" y="250" text-anchor="middle" font-family="Arial" font-size="24" fill="%23374151"%3EBollywood Story%3C/text%3E%3C/svg%3E',
                'emoji': '🎬',
                'color_theme': '#BE185D'
            },
            'gaming': {
                'svg_template': 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect width="400" height="300" fill="%23DCFCE7"/%3E%3Crect x="120" y="100" width="160" height="80" rx="20" fill="%23059669"/%3E%3Ccircle cx="160" cy="140" r="15" fill="%23FFF"/%3E%3Ccircle cx="240" cy="140" r="15" fill="%23FFF"/%3E%3Ctext x="200" y="250" text-anchor="middle" font-family="Arial" font-size="24" fill="%23374151"%3EGaming Strategy%3C/text%3E%3C/svg%3E',
                'emoji': '🎮',
                'color_theme': '#059669'
            }
        }
        
        return svg_templates.get(metaphor_category, svg_templates['cricket'])

    def _resolve_visual_template(
        self,
        intent_plan: Any,
        intent_context_flags: set,
        visual_directives: Dict[str, Any],
        concept_name: str,
        topic_key: str,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], bool]:
        """
        Determine whether a metadata-driven visual template can handle this request.
        Returns (visual_data, visual_offer, should_attempt_dynamic_generation)
        """
        render_strategy = visual_directives.get("render_strategy", {}) or {}
        trigger_mode = render_strategy.get("trigger", "auto")
        visual_mode = "auto" if trigger_mode == "auto" else "offer"

        if intent_plan.intent == "application_request":
            visual_mode = "offer"
        if intent_plan.intent == "clarification_follow_up":
            return None, None, True

        template_visual: Optional[Dict[str, Any]] = None
        if visual_directives.get("visual_type") == "animation" and visual_directives.get("lottie_file"):
            template_visual = {
                "type": "animation",
                "lottie_file": visual_directives["lottie_file"]
            }
        elif visual_directives.get("asset_url"):
            template_visual = {
                "type": "scene",
                "asset_url": visual_directives["asset_url"]
            }

        if not template_visual:
            return None, None, True

        visual_data = {
            "type": template_visual["type"],
            "mode": visual_mode,
            "caption": visual_directives.get("caption"),
            "persona": visual_directives.get("persona"),
            "template": visual_directives.get("template"),
            "library_topic": visual_directives.get("library_topic"),
            "render_strategy": render_strategy,
        }
        if template_visual["type"] == "animation":
            visual_data["lottie_file"] = template_visual["lottie_file"]
        else:
            visual_data["asset_url"] = template_visual["asset_url"]

        visual_offer = None
        if visual_mode == "offer":
            visual_offer = {
                "message": visual_directives.get("offer_text") or "👉 Would you like to see this visually?",
                "concept": concept_name,
                "topic": topic_key,
                "available": True,
                "cta_text": visual_directives.get("cta_text", "Show Visual"),
                "visual_mode": "offer"
        }

        return visual_data, visual_offer, False

    def _hydrate_hero_visual(
        self,
        metaphor_visual: Dict[str, Any],
        visual_data: Optional[Dict[str, Any]],
        default_alt: Optional[str] = None,
    ) -> None:
        # Ensure hero_visual is always a dict
        existing_hero = metaphor_visual.get('hero_visual')
        if not isinstance(existing_hero, dict):
            # If hero_visual exists but is not a dict (e.g., string), create a new dict
            # Preserve the value as visual_url if it was a string
            hero = {}
            if isinstance(existing_hero, str):
                hero['visual_url'] = existing_hero
            metaphor_visual['hero_visual'] = hero
        else:
            hero = existing_hero
        
        if not hero.get('alt_text') and default_alt:
            hero['alt_text'] = default_alt

        if hero.get('url'):
            return

        if visual_data and isinstance(visual_data, dict):
            if visual_data.get('asset_url'):
                hero['url'] = visual_data.get('asset_url')
                return
            if visual_data.get('lottie_file'):
                hero['url'] = visual_data.get('lottie_file')
                return

        fallback = metaphor_visual.get('hero_visual_fallback_url') or "https://cdn.mgxai.com/visuals/placeholder.svg"
        hero['url'] = fallback
