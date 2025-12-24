"""
ResponseComposer - Unified Adaptive AI Response Engine
======================================================
Single entry point for ALL AI Tutor responses.
Replaces: dual Professor+Mentor calls, rigid JSON templates, legacy prompts.

Key Principles:
1. ONE LLM call per question (not 2 parallel calls)
2. Adaptive structure based on question intent
3. Natural markdown output (not rigid JSON)
4. Context-aware with conversation state
5. Visual integration when relevant

PERFORMANCE OPTIMIZATIONS (v2.0):
- Aggressive timeouts (15s for simple, 45s for complex)
- Smart model selection (gpt-4o-mini for 70%+ of questions)
- Response caching for common patterns
- Intent-based token limits
"""

import asyncio
import logging
import time
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from functools import lru_cache
from emergentintegrations.llm.chat import LlmChat, UserMessage

from .intelligent_response_engine import (
    detect_intent, 
    get_response_config, 
    QuestionIntent
)
from .conversation_state import ConversationStateManager
from .whiteboard_engine import whiteboard_engine, generate_whiteboard_visual
from .human_intelligence_layer import HumanIntelligenceLayer, get_human_context
from .proactive_mentor import generate_follow_ups, ProactiveMentor

# 🆕 Knowledge Tracking - Update student cognitive model after interactions
try:
    from .cognitive_model import get_adaptive_engine
    COGNITIVE_MODEL_AVAILABLE = True
except ImportError:
    COGNITIVE_MODEL_AVAILABLE = False
    logging.warning("Cognitive Model not available for knowledge tracking")

logger = logging.getLogger(__name__)


# =============================================================================
# 🎨 DYNAMIC SECTION ENGINE - No More Templates!
# =============================================================================
class DynamicSectionEngine:
    """
    Generates response structure dynamically based on query analysis.
    
    NO static templates - every response is handcrafted based on:
    - Query intent (concept / derivation / comparison / problem / doubt)
    - Difficulty level (beginner / intermediate / advanced)
    - Subject area (Physics / Chemistry / Math / Biology)
    - Student emotional state (confused / exploring / confident)
    - Visual relevance
    - Exam relevance
    """
    
    # Available sections with descriptions
    AVAILABLE_SECTIONS = {
        'title': '🏷️ Engaging title for the concept',
        'simple_explanation': '🧠 Simple, intuitive explanation',
        'deep_explanation': '🔬 Rigorous, detailed explanation',
        'examples': '🧪 Practical examples and applications',
        'visual_concept': '📘 Mental diagram or visualization',
        'exam_tip': '🎯 Topic-specific exam insight',
        'analogy': '💡 Relatable analogy or insight',
        'formula_box': '📐 Key formulas with explanations',
        'common_mistakes': '⚠️ Common pitfalls to avoid',
        'follow_up': '❓ Engagement prompt for deeper learning',
        'memory_hook': '🧲 Memory trick or mnemonic',
        'quick_answer': '⚡ Direct answer for quick reference',
        'steps': '📝 Step-by-step solution',
        'comparison': '⚖️ Comparison table or analysis',
        'historical_context': '📜 History and discovery story',
    }
    
    @classmethod
    def analyze_and_select(cls, query: str, subject: str, context: dict = None) -> dict:
        """
        Analyze query and select appropriate sections dynamically.
        
        Returns:
            {
                'sections': ['section1', 'section2', ...],
                'tone': 'warm' | 'formal' | 'encouraging',
                'depth': 'surface' | 'moderate' | 'deep',
                'visual_needed': bool,
                'exam_relevant': bool,
                'structure_hint': str  # For LLM guidance
            }
        """
        query_lower = query.lower()
        context = context or {}
        
        # Default structure
        result = {
            'sections': [],
            'tone': 'warm',
            'depth': 'moderate',
            'visual_needed': False,
            'exam_relevant': False,
            'structure_hint': ''
        }
        
        # ======================
        # 1. DETECT QUERY TYPE
        # ======================
        
        # Derivation/Proof queries
        if any(w in query_lower for w in ['derive', 'proof', 'prove', 'show that']):
            result['sections'] = ['title', 'simple_explanation', 'steps', 'formula_box', 'exam_tip']
            result['depth'] = 'deep'
            result['structure_hint'] = 'Start with intuition, then rigorous derivation with each step justified'
        
        # Comparison queries
        elif any(w in query_lower for w in ['difference', 'compare', 'versus', 'vs', 'distinguish']):
            result['sections'] = ['title', 'simple_explanation', 'comparison', 'examples', 'exam_tip']
            result['structure_hint'] = 'Use clear comparison with specific differences highlighted'
        
        # Problem-solving queries
        elif any(w in query_lower for w in ['solve', 'calculate', 'find', 'determine', 'compute']):
            result['sections'] = ['quick_answer', 'steps', 'formula_box', 'common_mistakes', 'exam_tip']
            result['depth'] = 'deep'
            result['structure_hint'] = 'Show clear step-by-step solution with formula usage'
        
        # Definition/Concept queries
        elif any(w in query_lower for w in ['what is', 'what are', 'define', 'meaning of']):
            result['sections'] = ['title', 'simple_explanation', 'examples', 'visual_concept', 'follow_up']
            result['depth'] = 'moderate'
            result['structure_hint'] = 'Start with simple definition, build to deeper understanding'
        
        # Explanation queries
        elif any(w in query_lower for w in ['why', 'how does', 'explain', 'reason']):
            result['sections'] = ['title', 'simple_explanation', 'deep_explanation', 'analogy', 'examples']
            result['depth'] = 'moderate'
            result['structure_hint'] = 'Build intuition first, then explain mechanism'
        
        # Doubt/Confusion queries
        elif any(w in query_lower for w in ['confused', "don't understand", 'stuck', 'help']):
            result['sections'] = ['simple_explanation', 'analogy', 'visual_concept', 'examples', 'follow_up']
            result['tone'] = 'encouraging'
            result['structure_hint'] = 'Start with reassurance, use simple analogies, check understanding'
        
        # Default: balanced explanation
        else:
            result['sections'] = ['title', 'simple_explanation', 'examples', 'follow_up']
            result['structure_hint'] = 'Provide clear, engaging explanation with practical examples'
        
        # ======================
        # 2. ADJUST FOR SUBJECT
        # ======================
        subject_lower = (subject or '').lower()
        
        if 'physics' in subject_lower:
            if 'visual_concept' not in result['sections']:
                result['sections'].insert(2, 'visual_concept')
            result['visual_needed'] = True
            
        elif 'math' in subject_lower:
            if 'formula_box' not in result['sections']:
                result['sections'].append('formula_box')
            if 'steps' not in result['sections'] and 'solve' in query_lower:
                result['sections'].insert(1, 'steps')
                
        elif 'chemistry' in subject_lower:
            if 'visual_concept' not in result['sections']:
                result['sections'].insert(2, 'visual_concept')
            result['visual_needed'] = True
            
        elif 'biology' in subject_lower:
            if 'examples' not in result['sections']:
                result['sections'].append('examples')
        
        # ======================
        # 3. EXAM RELEVANCE
        # ======================
        exam_indicators = ['jee', 'neet', 'cbse', 'board', 'exam', 'important', 'pyq']
        if any(ind in query_lower for ind in exam_indicators):
            result['exam_relevant'] = True
            if 'exam_tip' not in result['sections']:
                result['sections'].append('exam_tip')
        
        # ======================
        # 4. STUDENT CONTEXT ADJUSTMENT
        # ======================
        if context.get('emotion') == 'frustrated':
            result['tone'] = 'encouraging'
            if 'analogy' not in result['sections']:
                result['sections'].insert(1, 'analogy')
        
        if context.get('mastery_level', 50) < 30:
            result['depth'] = 'surface'
            result['sections'] = [s for s in result['sections'] if s != 'deep_explanation']
            
        elif context.get('mastery_level', 50) > 80:
            result['depth'] = 'deep'
            if 'deep_explanation' not in result['sections']:
                result['sections'].insert(2, 'deep_explanation')
        
        # Limit to max 6 sections for readability
        result['sections'] = result['sections'][:6]
        
        return result
    
    @classmethod
    def build_structure_prompt(cls, analysis: dict) -> str:
        """Build LLM prompt guidance based on analysis"""
        sections = analysis['sections']
        tone = analysis['tone']
        depth = analysis['depth']
        hint = analysis['structure_hint']
        
        section_guides = []
        for section in sections:
            desc = cls.AVAILABLE_SECTIONS.get(section, section)
            section_guides.append(f"- {desc}")
        
        prompt = f"""━━━ DYNAMIC STRUCTURE ━━━

INCLUDE THESE ELEMENTS:
{chr(10).join(section_guides)}

TONE: {tone.upper()} - {'Be warm and friendly' if tone == 'warm' else 'Be supportive and patient' if tone == 'encouraging' else 'Be clear and professional'}

DEPTH: {depth.upper()} - {'Simple language, basics only' if depth == 'surface' else 'Balanced accessibility' if depth == 'moderate' else 'Thorough and rigorous'}

GUIDANCE: {hint}

━━━ FORMAT REQUIREMENTS ━━━
✅ Use ## headers for main sections
✅ Use **bold** for key terms and definitions
✅ Use bullet points (-) for lists
✅ Use numbered lists (1. 2. 3.) for steps
✅ Use \\( \\) for inline math, \\[ \\] for block math
✅ Use > for important callouts
✅ Use | | | for tables
✅ Add blank lines between sections

❌ NO walls of unformatted text
❌ NO missing structure
❌ NO casual paragraph dumps"""
        
        return prompt


class ResponseComposer:
    """
    Unified response generation engine.
    Replaces the fragmented Professor+Mentor dual-call system.
    
    PERFORMANCE OPTIMIZED:
    - Response cache for identical questions
    - Aggressive timeouts (15s simple, 45s complex)
    - Smart model selection
    """
    
    # Class-level response cache (survives across instances)
    _response_cache: Dict[str, Dict] = {}
    _cache_hits = 0
    _cache_misses = 0
    
    # Timeout configurations
    TIMEOUT_SIMPLE = 15  # 15 seconds for simple questions
    TIMEOUT_STANDARD = 30  # 30 seconds for standard questions
    TIMEOUT_COMPLEX = 45  # 45 seconds for complex derivations
    
    def __init__(self, db, llm_api_key: str):
        self.db = db
        self.llm_api_key = llm_api_key
        self.state_manager = ConversationStateManager(db)
        self.human_layer = HumanIntelligenceLayer(db)  # NEW: Human Intelligence Layer
    
    def _get_cache_key(self, question: str, subject: str, intent: str) -> str:
        """Generate cache key for response caching."""
        normalized = f"{question.lower().strip()}|{subject}|{intent}"
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Get cached response if available."""
        if cache_key in self._response_cache:
            ResponseComposer._cache_hits += 1
            logger.info(f"🚀 Cache HIT (hits: {self._cache_hits}, misses: {self._cache_misses})")
            return self._response_cache[cache_key]
        ResponseComposer._cache_misses += 1
        return None
    
    def _cache_response(self, cache_key: str, response: Dict):
        """Cache a response (with size limit)."""
        # Limit cache size to 500 entries
        if len(self._response_cache) > 500:
            # Remove oldest 100 entries
            keys_to_remove = list(self._response_cache.keys())[:100]
            for k in keys_to_remove:
                del self._response_cache[k]
        
        self._response_cache[cache_key] = response
    
    def _extract_topic_from_question(self, question: str) -> str:
        """
        Extract the main topic/concept from a student's question.
        CRITICAL for follow-up continuity - ensures AI knows what we're discussing.
        """
        if not question:
            return ""
        
        q_lower = question.lower().strip()
        
        # Remove common question prefixes to get to the core topic
        prefixes = [
            "i want to understand what is",
            "i want to understand",
            "i need help with",
            "can you explain",
            "please explain",
            "help me understand",
            "what is the meaning of",
            "what does",
            "what is",
            "what are",
            "define",
            "explain",
            "tell me about",
            "how does",
            "how do",
            "why is",
            "why does",
            "solve",
            "calculate"
        ]
        
        topic = q_lower
        for prefix in prefixes:
            if topic.startswith(prefix):
                topic = topic[len(prefix):].strip()
                break
        
        # Remove trailing punctuation and common suffixes
        topic = topic.rstrip('?!.,')
        suffixes = [" work", " works", " mean", " means"]
        for suffix in suffixes:
            if topic.endswith(suffix):
                topic = topic[:-len(suffix)]
        
        # If topic is too long, take key words
        words = topic.split()
        if len(words) > 5:
            # Keep first 4-5 meaningful words
            topic = ' '.join(words[:5])
        
        # Capitalize properly
        return topic.title() if topic else ""
    
    async def generate_response(
        self,
        user_id: str,
        session_id: str,
        question: str,
        subject: str = None,
        exam_mode: str = "General",  # Changed default from "JEE"
        message_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate an adaptive AI response.
        
        This is the SINGLE entry point for all AI Tutor responses.
        No more dual Professor+Mentor calls.
        """
        start_time = time.time()
        
        # Step 1: Get conversation state and context
        state = await self.state_manager.get_state(user_id, session_id)
        context_summary = await self.state_manager.get_context_summary(
            user_id, session_id, message_history or []
        )
        
        # Step 2: Detect intent and get response configuration
        response_config = get_response_config(question, subject)
        intent = response_config["intent"]
        blocks = response_config["blocks"]
        
        logger.info(f"🎯 Intent: {intent}, Blocks: {blocks}")
        
        # Step 3: Auto-detect subject if not provided
        if not subject or subject.strip() == "":
            subject = self._detect_subject(question)
        
        # Step 3.5: 🧠 HUMAN INTELLIGENCE LAYER - Understand student context
        human_context = {}
        try:
            human_context = await self.human_layer.analyze_student_context(
                user_id=user_id,
                question=question,
                subject=subject,
                session_history=message_history,
                time_of_day=datetime.now().strftime("%H:%M")
            )
            logger.info(f"🧠 HIL: emotion={human_context.get('emotion')}, "
                       f"difficulty={human_context.get('difficulty_level')}, "
                       f"learning_style={human_context.get('learning_style')}")
        except Exception as e:
            logger.warning(f"⚠️ Human Intelligence Layer failed (non-critical): {e}")
        
        # Step 4: Build adaptive prompt (short, focused)
        base_prompt = self._build_adaptive_prompt(
            question=question,
            intent=intent,
            blocks=blocks,
            subject=subject,
            exam_mode=exam_mode,
            context_summary=context_summary,
            state=state
        )
        
        # Step 4.5: Enhance prompt with Human Intelligence
        if human_context:
            prompt = self.human_layer.build_enhanced_prompt(base_prompt, human_context)
        else:
            prompt = base_prompt
        
        # Step 5: Check cache first (PERFORMANCE OPTIMIZATION)
        cache_key = self._get_cache_key(question, subject, intent)
        cached = self._get_cached_response(cache_key)
        if cached:
            cached_copy = cached.copy()
            cached_copy["from_cache"] = True
            cached_copy["generation_time"] = 0.01
            return cached_copy
        
        # Step 6: Intelligent model selection and call
        provider, model_name = self._select_model(intent, question)
        max_tokens = self._get_max_tokens(intent)
        timeout = self._get_timeout(intent)
        
        logger.info(f"🤖 Using {provider}/{model_name}, max_tokens: {max_tokens}, timeout: {timeout}s")
        
        try:
            # === GEMINI - Primary (fast + intelligent) ===
            if provider == "gemini":
                raw_response = await self._call_gemini(
                    prompt=prompt,
                    question=question,
                    model=model_name,
                    max_tokens=max_tokens,
                    timeout=timeout
                )
            # === OpenAI - Fallback ===
            else:
                llm_chat = LlmChat(
                    api_key=self.llm_api_key,
                    session_id=f"tutor_{user_id}_{session_id}",
                    system_message=prompt
                ).with_model("openai", model_name).with_params(
                    temperature=0.8,
                    top_p=0.92,
                    max_tokens=max_tokens,
                    presence_penalty=0.4,
                    frequency_penalty=0.3
                )
                
                user_message = UserMessage(text=question)
                
                raw_response = await asyncio.wait_for(
                    llm_chat.send_message(user_message),
                    timeout=timeout
                )
            
        except asyncio.TimeoutError:
            logger.warning(f"⏰ LLM call timeout after {timeout}s - using fallback")
            raw_response = self._get_fallback_response(question, intent)
            
        except Exception as e:
            logger.error(f"❌ LLM call failed: {e}")
            raw_response = self._get_fallback_response(question, intent)
        
        generation_time = time.time() - start_time
        logger.info(f"✅ Response generated in {generation_time:.2f}s")
        
        # Step 6: Check if visual is needed
        visual_data = None
        if response_config.get("include_visual"):
            visual_data = await self._get_visual_data(question, subject)
        
        # Step 7: Update conversation state
        await self.state_manager.update_state(
            user_id=user_id,
            session_id=session_id,
            question=question,
            response=raw_response,
            subject=subject,
            intent=intent
        )
        
        # Step 8: Structure the response with Human Intelligence data
        result = {
            "response": {
                "default_view": {
                    "main_content": {
                        "content": raw_response,
                        "type": "markdown"
                    },
                    "greeting": self._extract_greeting(raw_response) if intent == "greeting" else None,
                    # Human Intelligence Layer additions
                    "encouragement": human_context.get("encouragement") if human_context else None,
                    "detected_emotion": human_context.get("emotion") if human_context else None,
                },
                "progressive_sections": {
                    "explanation": raw_response
                },
                "intent": intent,
                "render_directives": response_config.get("render_directives", {}),
                # Human-like interaction metadata
                "human_context": {
                    "emotion": human_context.get("emotion") if human_context else "neutral",
                    "difficulty_level": human_context.get("difficulty_level") if human_context else "developing",
                    "learning_style": human_context.get("learning_style") if human_context else "mixed",
                    "used_socratic": human_context.get("use_socratic", False) if human_context else False,
                    "streak_days": human_context.get("streak_days", 0) if human_context else 0,
                    "exam_tip": human_context.get("exam_insights", {}).get("exam_advice") if human_context else None
                }
            },
            "visual_data": visual_data,
            "visual_sketch": visual_data,  # Alias for frontend compatibility
            "detected_subject": subject,
            "generation_time": generation_time,
            "model_used": model,
            "intent_detected": intent,
            "blocks_used": blocks,
            "context_used": bool(context_summary),
            "from_cache": False,
            # Human Intelligence summary
            "human_intelligence": {
                "emotion_detected": human_context.get("emotion") if human_context else "neutral",
                "adapted_for_style": human_context.get("learning_style") if human_context else "mixed",
                "difficulty_calibrated": human_context.get("difficulty_level") if human_context else "developing"
            }
        }
        
        # Step 9: Add smart follow-up suggestions with topic context
        # CRITICAL: Skip follow-ups for greetings/conversational messages
        try:
            emotion = human_context.get("emotion", "neutral") if human_context else "neutral"
            follow_ups = generate_follow_ups(
                question=question,
                response=raw_response,
                subject=subject,
                emotion=emotion,
                intent=intent  # Pass intent to skip follow-ups for non-educational messages
            )
            result["response"]["follow_up_suggestions"] = follow_ups
            result["response"]["default_view"]["follow_ups"] = follow_ups
            
            # CRITICAL: Store the original question context for follow-up continuity
            result["response"]["original_question"] = question
            result["response"]["conversation_topic"] = self._extract_topic_from_question(question)
        except Exception as e:
            logger.warning(f"⚠️ Follow-up generation failed: {e}")
            result["response"]["follow_up_suggestions"] = []
            result["response"]["original_question"] = question
        
        # Step 10: Cache successful responses (for common questions)
        if generation_time < 30:  # Only cache fast responses
            self._cache_response(cache_key, result)
        
        # 🆕 Step 11: Track learning interaction (update student cognitive model)
        # This runs in background, non-blocking
        asyncio.create_task(self._track_learning_interaction(
            user_id=user_id,
            subject=subject,
            topic=result["response"].get("conversation_topic", "General"),
            intent=intent,
            question=question
        ))
        
        return result
    
    async def _track_learning_interaction(
        self,
        user_id: str,
        subject: str,
        topic: str,
        intent: str,
        question: str
    ) -> None:
        """
        🆕 Track learning interaction to update student cognitive model.
        
        This runs in background (non-blocking) to:
        - Update topic exposure counts
        - Track concepts covered
        - Feed spaced repetition system
        - Build learning profile
        
        Args:
            user_id: Student user ID
            subject: Subject area
            topic: Topic being discussed
            intent: Question intent type
            question: Original question
        """
        if not COGNITIVE_MODEL_AVAILABLE:
            return
            
        # Skip tracking for non-educational intents
        if intent in ['greeting', 'acknowledgment', 'off_topic']:
            return
        
        try:
            engine = get_adaptive_engine(self.db)
            
            # Extract concepts from the question
            concepts = self._extract_concepts_from_question(question, subject)
            
            if not concepts:
                concepts = [topic]  # Use topic as fallback
            
            # Record the interaction
            await engine.knowledge_tracker.record_interaction(
                user_id=user_id,
                subject=subject or "General",
                topic=topic or "General",
                concepts=concepts,
                performance={}  # No performance data for question-answer (only for quizzes)
            )
            
            logger.info(f"📝 Tracked learning interaction: {user_id} | {subject}/{topic} | {len(concepts)} concepts")
            
        except Exception as e:
            # Non-critical - don't fail the main request
            logger.warning(f"⚠️ Knowledge tracking failed (non-critical): {e}")
    
    def _extract_concepts_from_question(self, question: str, subject: str) -> List[str]:
        """Extract concepts from a question for tracking."""
        concepts = []
        q_lower = question.lower()
        
        # Physics concepts
        physics_concepts = {
            'force': 'Newton Laws', 'motion': 'Kinematics', 'velocity': 'Kinematics',
            'acceleration': 'Kinematics', 'momentum': 'Momentum', 'energy': 'Energy',
            'gravity': 'Gravitation', 'friction': 'Friction', 'wave': 'Waves',
            'sound': 'Sound', 'light': 'Optics', 'lens': 'Optics', 'mirror': 'Optics',
            'current': 'Current Electricity', 'voltage': 'Current Electricity',
            'resistance': 'Current Electricity', 'magnet': 'Magnetism', 'circuit': 'Circuits',
            'capacitor': 'Capacitors', 'inductor': 'Inductance', 'thermodynamics': 'Thermodynamics',
            'heat': 'Heat Transfer', 'temperature': 'Heat Transfer'
        }
        
        # Chemistry concepts
        chemistry_concepts = {
            'atom': 'Atomic Structure', 'electron': 'Atomic Structure', 'proton': 'Atomic Structure',
            'bond': 'Chemical Bonding', 'ionic': 'Chemical Bonding', 'covalent': 'Chemical Bonding',
            'reaction': 'Chemical Reactions', 'oxidation': 'Redox Reactions',
            'acid': 'Acids and Bases', 'base': 'Acids and Bases', 'ph': 'Acids and Bases',
            'organic': 'Organic Chemistry', 'carbon': 'Organic Chemistry',
            'mole': 'Stoichiometry', 'equilibrium': 'Chemical Equilibrium'
        }
        
        # Math concepts
        math_concepts = {
            'derivative': 'Derivatives', 'differentiation': 'Derivatives',
            'integral': 'Integration', 'integration': 'Integration',
            'limit': 'Limits', 'continuity': 'Continuity', 'function': 'Functions',
            'equation': 'Equations', 'quadratic': 'Quadratic Equations',
            'matrix': 'Matrices', 'determinant': 'Determinants',
            'vector': 'Vectors', 'probability': 'Probability', 'statistics': 'Statistics',
            'trigonometry': 'Trigonometry', 'sin': 'Trigonometry', 'cos': 'Trigonometry'
        }
        
        # Biology concepts
        biology_concepts = {
            'cell': 'Cell Biology', 'nucleus': 'Cell Biology', 'mitochondria': 'Cell Biology',
            'dna': 'Genetics', 'rna': 'Genetics', 'gene': 'Genetics', 'chromosome': 'Genetics',
            'photosynthesis': 'Photosynthesis', 'respiration': 'Respiration',
            'digestion': 'Digestive System', 'circulation': 'Circulatory System',
            'evolution': 'Evolution', 'ecology': 'Ecology', 'ecosystem': 'Ecology'
        }
        
        # Choose concept map based on subject
        concept_maps = {
            'physics': physics_concepts,
            'chemistry': chemistry_concepts,
            'mathematics': math_concepts,
            'math': math_concepts,
            'biology': biology_concepts
        }
        
        subject_lower = (subject or '').lower()
        
        # If subject is known, use that concept map
        if subject_lower in concept_maps:
            for keyword, concept in concept_maps[subject_lower].items():
                if keyword in q_lower and concept not in concepts:
                    concepts.append(concept)
        else:
            # Check all concept maps
            for concept_map in concept_maps.values():
                for keyword, concept in concept_map.items():
                    if keyword in q_lower and concept not in concepts:
                        concepts.append(concept)
        
        return concepts[:5]  # Limit to 5 concepts per question
    
    def _build_adaptive_prompt(
        self,
        question: str,
        intent: str,
        blocks: List[str],
        subject: str,
        exam_mode: str,
        context_summary: str,
        state: Dict
    ) -> str:
        """
        Build a SHORT, FOCUSED prompt based on intent.
        No more 500-line mega-prompts.
        
        CRITICAL: For follow-up questions, we MUST reference conversation context.
        """
        
        # Base personality - HUMAN-LIKE, NATURAL, and WELL-FORMATTED
        base = """You are Druv, a brilliant IIT senior and AI mentor who genuinely cares about students.

YOUR PERSONALITY:
- You remember being a student yourself - the exam stress, the late nights, the breakthroughs
- You celebrate every small win and never make students feel dumb
- You're patient when they're confused, energetic when they're curious, calm when they're anxious

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 FORMATTING RULES (CRITICAL - ALWAYS FOLLOW):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. **STRUCTURE** - Use markdown headers for sections:
   ## Main Section (for major topics)
   ### Subsection (for subtopics)

2. **KEY TERMS** - Always bold important terms:
   The **force** acting on a body causes **acceleration**.

3. **LISTS** - Use proper markdown bullets:
   - First point with detail
   - Second point with explanation
   - Third point with example

4. **NUMBERED STEPS** - For processes/solutions:
   1. First step explained
   2. Second step explained
   3. Final step with result

5. **MATH** - Use LaTeX properly:
   - Inline: \\( F = ma \\) within text
   - Block for important equations:
     \\[ F = \\frac{dp}{dt} = ma \\]

6. **FORMULAS** - Box key formulas:
   > **Key Formula:** \\( v = u + at \\)

7. **TABLES** - For comparisons:
   | Aspect | Value A | Value B |
   |--------|---------|---------|
   | Speed  | Fast    | Slow    |

8. **DEFINITIONS** - Structure clearly:
   **Definition:** A clear, concise definition here.
   
   **In Simple Words:** Easy explanation with analogy.

9. **EXAMPLES** - Mark clearly:
   **Example:** Consider a cricket ball...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEVER output plain, unformatted paragraphs.
ALWAYS structure your response with headers, bullets, and proper spacing.
Each response should be scannable and easy to read.

RESPONSE STYLE:
- Talk like a friend explaining, but with STRUCTURE
- One idea per paragraph
- Use whitespace to separate concepts
- Match your depth to the question complexity

HUMAN TOUCHES (pick 1-2 per response):
- Acknowledge their struggle: "This topic trips up most students..."
- Share insider tips: "Here's what toppers do differently..."
- Use cricket/Bollywood analogies for Indian students
- End with genuine encouragement"""

        # Context injection - CRITICAL for follow-ups
        context_block = ""
        if context_summary:
            context_block = f"""

CONVERSATION HISTORY (IMPORTANT - Reference this for follow-up questions):
{context_summary}

If the student asks about "what we discussed" or "earlier", refer to the topics above."""
        
        # State-aware adjustments
        state_block = ""
        if state.get("current_topic"):
            state_block = f"\nCurrent topic being discussed: {state['current_topic']}"
        if state.get("topics_covered") and len(state.get("topics_covered", [])) > 0:
            recent = state["topics_covered"][-3:]
            state_block += f"\nRecent topics: {', '.join(recent)}"
        if state.get("confusion_level", 0) > 0.3:
            state_block += "\n⚠️ Student seems confused - use simpler language."
        
        # Intent-specific instructions (SHORT!)
        intent_instructions = self._get_intent_instructions(intent, blocks, exam_mode)
        
        # Subject context
        subject_block = f"\nSUBJECT: {subject}" if subject else ""
        
        # 🎨 DYNAMIC SECTION ENGINE - No more templates!
        dynamic_analysis = DynamicSectionEngine.analyze_and_select(
            query=question,
            subject=subject or 'General',
            context={
                'emotion': state.get('emotion'),
                'mastery_level': state.get('mastery_level', 50)
            }
        )
        dynamic_structure = DynamicSectionEngine.build_structure_prompt(dynamic_analysis)
        
        # Combine with dynamic structure
        prompt = f"""{base}
{context_block}
{state_block}
{subject_block}

{intent_instructions}

{dynamic_structure}

Answer naturally. Make it feel premium and handcrafted."""
        
        return prompt
    
    def _get_intent_instructions(self, intent: str, blocks: List[str], exam_mode: str) -> str:
        """Get SHORT, NATURAL instructions based on intent type."""
        
        instructions = {
            "greeting": "Respond warmly in 1-2 sentences. Be friendly, no long explanations!",
            
            "conversational": "Keep it casual and brief. 1-2 sentences max.",
            
            "simple_fact": "Give a direct, factual answer. 1-2 sentences, no elaboration needed.",
            
            "definition": """Structure your definition:
## [Concept Name]

**Definition:** A clear, precise definition.

**In Simple Words:** Easy explanation with a relatable analogy.

**Key Points:**
- Important aspect 1
- Important aspect 2

Keep it under 150 words.""",
            
            "explanation": f"""Structure for {exam_mode} prep:

## Understanding [Topic]

Start with the core concept - why does this matter?

### The Key Idea
Explain the fundamental principle clearly.

### How It Works
- Step or aspect 1
- Step or aspect 2

### Formula (if applicable)
\\[ Your formula here \\]

### Real Example
A relatable example from daily life.

Keep it under 300 words, well-structured.""",
            
            "calculation": """Structure your solution:

## Solution

**Given:**
- Known value 1 = ...
- Known value 2 = ...

**To Find:** What we need to calculate

**Formula:**
\\[ Required formula \\]

**Solution Steps:**
1. First step with calculation
2. Second step with substitution
3. Final calculation

**Answer:** \\( result \\) with proper units

> **Quick Check:** Verify your answer makes sense.""",
            
            "derivation": """Structure your derivation:

## Derivation of [Formula/Theorem]

**Starting Point:**
\\[ Initial equation or principle \\]

**Step-by-Step:**
1. First transformation - explain why
2. Apply rule/theorem - show work
3. Simplify - explain each step

**Final Result:**
\\[ \\boxed{{Final formula}} \\]

> **Remember:** Key insight to remember.""",
            
            "comparison": """Structure your comparison:

## [A] vs [B]

| Aspect | [A] | [B] |
|--------|-----|-----|
| Property 1 | ... | ... |
| Property 2 | ... | ... |
| Property 3 | ... | ... |

### Key Differences
- **Main difference 1:** Explanation
- **Main difference 2:** Explanation

### When to Use Which
Brief guidance on practical application.""",
            
            "process": """Explain with numbered steps:

## How [Process] Works

1. **Step 1:** What happens and why
2. **Step 2:** Next action with detail
3. **Step 3:** Continuation
4. **Result:** Final outcome

> **Tip:** A useful insight for remembering.""",
            
            "example": """Structure your example:

## Example: [Brief title]

**Scenario:** Set up the problem/situation.

**Analysis:**
- Key observation 1
- Key observation 2

**Solution/Outcome:**
Show how the concept applies.

**Key Takeaway:** What this example teaches.""",
            
            "practice": """Structure practice problem:

## Practice Problem

**Question:** Clear problem statement.

**Hint:** 
> Think about [concept/approach]...

**Approach:**
1. First step to consider
2. Key formula to use
3. What to calculate

Try it yourself first! Solution approach above.""",
            
            "follow_up": """FOLLOW-UP: Reference the CONVERSATION HISTORY above.
- If asked "what did we discuss?": List actual topics from history
- If asked to continue: Build on previous explanation, don't restart
- Be direct and structured""",

            "revision": """Quick revision format:

## Quick Revision: [Topic]

**Key Points:**
- Point 1
- Point 2
- Point 3

**Important Formulas:**
\\[ Formula 1 \\]
\\[ Formula 2 \\]

**Memory Trick:** A helpful mnemonic or analogy.""",
            
            "confusion": """Help the confused student:

## Let's Simplify This

**The Simple Version:**
Explain in the most basic terms possible.

**Think of it Like:**
A very relatable analogy they'll understand.

**Key Things to Remember:**
- Just this one thing
- And this simple fact

Does this make more sense? What part is still unclear?""",
            
            "verification": """Verify and correct:

## Checking Your Understanding

**Your approach:** Brief summary of what they did.

**The Issue:** What went wrong (if anything).

**Correct Approach:**
1. Right step 1
2. Right step 2

**Key Insight:** What to remember for next time."""
        }
        
        return instructions.get(intent, instructions["explanation"])
    
    def _select_model(
        self, 
        intent: str, 
        question: str,
        routing_decision: Any = None,  # PHASE B: Accept routing decision for semantic info
        semantic_analysis: Dict[str, Any] = None  # PHASE B: Accept semantic analysis
    ) -> tuple:
        """
        Select the best model based on complexity and intent.
        
        PHASE B FIX: Uses routing decision complexity and semantic analysis
        instead of keyword matching when ENABLE_SEMANTIC_MODEL_SELECTION is enabled.
        
        PRIORITY:
        1. Gemini 2.0 Flash - Primary (fast + intelligent)
        2. Gemini 1.5 Pro - Deep reasoning (proofs, derivations)
        3. GPT-4o - Fallback for specific cases
        
        Returns:
            tuple: (provider, model_name)
            - provider: "gemini" | "openai"
            - model_name: specific model identifier
        """
        from core.config import settings
        
        word_count = len(question.split())
        
        # Check if Gemini is available
        use_gemini = getattr(settings, 'USE_GEMINI_PRIMARY', True) and getattr(settings, 'GEMINI_API_KEY', '')
        
        # PHASE B: Semantic-based model selection (no keywords)
        if settings.ENABLE_SEMANTIC_MODEL_SELECTION and routing_decision:
            # Use routing decision complexity
            complexity = getattr(routing_decision, 'complexity', None)
            
            # Simple/Trivial → Fast model
            if complexity and complexity.value in ['trivial', 'simple']:
                if use_gemini:
                    return ("gemini", "gemini-2.0-flash")
                return ("openai", "gpt-4o-mini")
            
            # Complex/Expert → Pro model
            if complexity and complexity.value in ['complex', 'expert']:
                if use_gemini:
                    return ("gemini", "gemini-1.5-pro")
                return ("openai", "gpt-4o")
            
            # Check for actionable requests that need more power
            if semantic_analysis:
                has_actionable = semantic_analysis.get('has_actionable_request', False)
                output_type = semantic_analysis.get('requested_output_type', '')
                
                # Deliverables need more reasoning power
                if has_actionable and output_type in ['study_plan', 'problem_solution', 'quiz']:
                    if use_gemini:
                        return ("gemini", "gemini-1.5-pro")
                    return ("openai", "gpt-4o")
            
            # Default to flash for moderate complexity
            if use_gemini:
                return ("gemini", "gemini-2.0-flash")
            return ("openai", "gpt-4o-mini")
        
        # LEGACY: Keyword-based model selection (only when flag disabled)
        q_lower = question.lower()
        
        # Fast intents - use Gemini Flash (lightning fast)
        fast_intents = {
            "greeting", "conversational", "simple_fact", 
            "verification", "definition", "example",
            "follow_up", "revision", "practice"
        }
        
        if intent in fast_intents:
            if use_gemini:
                return ("gemini", "gemini-2.0-flash")
            return ("openai", "gpt-4o-mini")
        
        # Short questions - fast model
        if word_count < 12:
            if use_gemini:
                return ("gemini", "gemini-2.0-flash")
            return ("openai", "gpt-4o-mini")
        
        # Casual patterns - fast model (LEGACY)
        casual_patterns = [
            "remind", "hello", "hi ", "hey", "thanks", "thank you",
            "good morning", "good night", "how are", "bye", "ok",
            "yes", "no", "sure", "cool", "nice", "great", "awesome",
            "preparation", "study", "schedule", "plan", "tomorrow"
        ]
        if any(pat in q_lower for pat in casual_patterns):
            if use_gemini:
                return ("gemini", "gemini-2.0-flash")
            return ("openai", "gpt-4o-mini")
        
        # Complex academic work - use Gemini Pro for deep reasoning (LEGACY)
        complex_patterns = [
            "derive", "prove", "derivation", "proof",
            "step by step", "detailed explanation",
            "compare and contrast", "analyze", "evaluate",
            "explain why", "how does", "mechanism"
        ]
        
        if any(pat in q_lower for pat in complex_patterns) and word_count > 15:
            if use_gemini:
                return ("gemini", "gemini-1.5-pro")  # Deep reasoning
            return ("openai", "gpt-4o")
        
        # Default - Gemini Flash (best balance of speed + intelligence)
        if use_gemini:
            return ("gemini", "gemini-2.0-flash")
        return ("openai", "gpt-4o-mini")
    
    def _get_timeout(self, intent: str) -> int:
        """Get appropriate timeout based on intent complexity."""
        
        # Super fast responses
        fast_intents = {"greeting", "conversational", "simple_fact", "verification"}
        if intent in fast_intents:
            return self.TIMEOUT_SIMPLE  # 15s
        
        # Standard responses
        standard_intents = {"definition", "example", "follow_up", "revision", "practice"}
        if intent in standard_intents:
            return self.TIMEOUT_STANDARD  # 30s
        
        # Complex responses
        return self.TIMEOUT_COMPLEX  # 45s
    
    async def _call_gemini(
        self,
        prompt: str,
        question: str,
        model: str = "gemini-2.0-flash",
        max_tokens: int = 1000,
        timeout: int = 30
    ) -> str:
        """
        Call Gemini API for intelligent, fast responses.
        
        Gemini advantages:
        - Lightning-fast responses (especially Flash model)
        - Deep conceptual understanding
        - Better at educational content
        - Long context window
        
        Args:
            prompt: System prompt with personality and context
            question: Student's question
            model: Gemini model to use
            max_tokens: Maximum response tokens
            timeout: Request timeout in seconds
        
        Returns:
            Response text from Gemini
        """
        try:
            import google.generativeai as genai
            from core.config import settings
            
            # Configure Gemini
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            logger.info(f"⚡ Calling Gemini ({model}) for response...")
            
            # Create the model with configuration
            generation_config = genai.GenerationConfig(
                temperature=0.8,
                max_output_tokens=max_tokens,
                top_p=0.95,
                top_k=40
            )
            
            model_instance = genai.GenerativeModel(
                model_name=model,
                generation_config=generation_config,
                system_instruction=prompt
            )
            
            # Generate response with timeout
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: model_instance.generate_content(question)
                ),
                timeout=timeout
            )
            
            result = response.text
            logger.info(f"✅ Gemini response received ({len(result)} chars)")
            
            return result
            
        except ImportError:
            logger.error("❌ google-generativeai not installed")
            # Fallback to OpenAI
            return await self._call_openai_fallback(prompt, question, max_tokens, timeout)
            
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Gemini timeout after {timeout}s")
            raise
            
        except Exception as e:
            logger.error(f"❌ Gemini call failed: {e}")
            # Fallback to OpenAI
            return await self._call_openai_fallback(prompt, question, max_tokens, timeout)
    
    async def _call_openai_fallback(
        self,
        prompt: str,
        question: str,
        max_tokens: int,
        timeout: int
    ) -> str:
        """Fallback to OpenAI if Gemini fails"""
        logger.info("↩️ Falling back to OpenAI...")
        
        llm_chat = LlmChat(
            api_key=self.llm_api_key,
            session_id=f"fallback_{time.time()}",
            system_message=prompt
        ).with_model("openai", "gpt-4o-mini").with_params(
            temperature=0.8,
            max_tokens=max_tokens
        )
        
        user_message = UserMessage(text=question)
        
        response = await asyncio.wait_for(
            llm_chat.send_message(user_message),
            timeout=timeout
        )
        
        return response if isinstance(response, str) else str(response)
    
    def _get_max_tokens(self, intent: str) -> int:
        """Get appropriate token limit based on intent."""
        
        token_map = {
            "greeting": 100,
            "conversational": 150,
            "simple_fact": 200,
            "verification": 300,
            "definition": 400,
            "example": 500,
            "explanation": 800,
            "calculation": 800,
            "comparison": 600,
            "process": 700,
            "derivation": 1000,
            "revision": 500,
            "confusion": 600,
            "practice": 500,
            "follow_up": 600
        }
        
        return token_map.get(intent, 800)
    
    def _detect_subject(self, question: str) -> str:
        """Auto-detect subject from question."""
        q = question.lower()
        
        physics_keywords = ['force', 'motion', 'velocity', 'acceleration', 'gravity', 'energy', 'momentum', 'wave', 'light', 'electricity', 'circuit', 'newton', 'friction']
        chemistry_keywords = ['atom', 'molecule', 'reaction', 'bond', 'element', 'compound', 'acid', 'base', 'oxidation', 'electron', 'orbital', 'periodic']
        biology_keywords = ['cell', 'dna', 'gene', 'protein', 'enzyme', 'photosynthesis', 'respiration', 'mitosis', 'meiosis', 'evolution', 'ecology', 'organ']
        math_keywords = ['equation', 'solve', 'integral', 'derivative', 'function', 'graph', 'triangle', 'circle', 'algebra', 'calculus', 'probability', 'matrix']
        
        if any(kw in q for kw in physics_keywords):
            return "Physics"
        if any(kw in q for kw in chemistry_keywords):
            return "Chemistry"
        if any(kw in q for kw in biology_keywords):
            return "Biology"
        if any(kw in q for kw in math_keywords):
            return "Mathematics"
        
        return "General"
    
    async def _get_visual_data(self, question: str, subject: str) -> Optional[Dict]:
        """Get visual data if concept supports it using Whiteboard Engine V3."""
        try:
            concept = whiteboard_engine.extract_concept(question)
            
            if concept:
                visual = generate_whiteboard_visual(
                    concept=concept,
                    subject=subject.lower() if subject else "physics",
                    question=question
                )
                return {
                    "has_visual": True,
                    "concept": concept,
                    "subject": visual.get("subject", subject),
                    "whiteboard_visual": visual,
                    "beats": visual.get("beats", []),
                    "title": visual.get("title", ""),
                    "template": visual.get("template", "")
                }
        except Exception as e:
            logger.warning(f"Visual detection failed: {e}")
        
        return None
    
    def _extract_greeting(self, response: str) -> str:
        """Extract greeting from response."""
        lines = response.strip().split('\n')
        return lines[0] if lines else "Hello!"
    
    def _get_fallback_response(self, question: str, intent: str) -> str:
        """
        Fallback response if LLM fails.
        
        CRITICAL: Fallback must:
        - Continue the conversation naturally
        - Reference what they asked
        - Never expose limitations or ask to "try again"
        - Never list capabilities mid-conversation
        """
        if intent == "greeting":
            return "Hey! 👋 Great to have you here. What's on your mind?"
        
        # Natural continuation that references their question
        # NO capability menus, NO "try again" language
        short_question = question[:50] + "..." if len(question) > 50 else question
        
        return f"""Let me think about "{short_question}" for a moment.

This is an interesting question! I want to give you a really good answer.

Could you tell me a bit more about what specifically you're trying to understand? That way I can explain it in the most helpful way for you. 🎯"""


# Singleton instance for easy import
_composer_instance = None

def get_response_composer(db, llm_api_key: str) -> ResponseComposer:
    """Get or create ResponseComposer instance."""
    global _composer_instance
    if _composer_instance is None:
        _composer_instance = ResponseComposer(db, llm_api_key)
    return _composer_instance

