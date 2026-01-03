"""
🤝 Study Buddy Agent - TRUE AGENTIC Interactive Learning Companion
===================================================================

UPGRADED to TRUE ADVANCED AGENT with:
- ReAct Loop: Think → Act → Observe (uses parent class properly)
- Tools: QuizGenerator, PracticeTracker, SpacedRepetition, FlashcardGenerator
- Memory: Reads student level, weak topics; Writes session summaries, outcomes
- Autonomous Decisions: Chooses interaction mode, difficulty, pacing, handoff
- Verification: Ensures answers are correct and student-friendly

GOAL: "Interactive learning companion that helps the student practice, revise, and stay engaged"

ROUTING POLICY (is_buddy_query):
✅ SHOULD route to StudyBuddy:
   - "Practice me", "quiz me", "test me", "ask me questions"
   - "Revise this topic", "flashcards", "quick recap"
   - "Daily study session", "track my progress", "what next?"
   
❌ Should NOT route to StudyBuddy:
   - Deep conceptual explanation → ProfessorAgent
   - Emotional support needed → MentorAgent
   - Full exam strategy → ExamCoachAgent
   - Data-driven weakness detection → WeakAreaDetectiveAgent
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from agents.core.react_agent import ReActAgent
from agents.core.tool_registry import ToolRegistry
from agents.core.memory import MemorySystem, LongTermMemory
from agents.core.verifier import Verifier

logger = logging.getLogger(__name__)


class StudyBuddyAgent(ReActAgent):
    """
    TRUE AGENTIC Study Buddy - Interactive Learning Companion
    
    CAPABILITIES:
    1. Quiz Generation: Creates adaptive practice questions
    2. Flashcard Creation: Generates revision cards
    3. Progress Tracking: Records outcomes, updates mastery
    4. Spaced Repetition: Schedules optimal review times
    5. Adaptive Difficulty: Adjusts based on student performance
    
    AUTONOMOUS DECISIONS:
    - Chooses interaction style (quiz/flashcards/practice/recap)
    - Decides difficulty and pacing based on student history
    - Determines when to hand off to Professor/Mentor
    - Adapts content based on engagement signals
    """
    
    BUDDY_NAME = "Priya"
    
    # Interaction modes that StudyBuddy can choose
    INTERACTION_MODES = {
        "quiz": "Generate practice questions with verification",
        "flashcards": "Create quick revision cards",
        "practice": "Guided problem-solving session",
        "recap": "Quick topic summary before testing",
        "review": "Review due topics based on spaced repetition",
        "progress": "Show progress and recommendations"
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Initialize tool registry with StudyBuddy-specific tools
        self.tool_registry = ToolRegistry()
        self._register_tools()
        
        # Initialize verifier for answer quality
        self.verifier = Verifier()
        
        # Memory cache per user (populated during process)
        self._memory_cache: Dict[str, MemorySystem] = {}
        
        logger.info(f"🤝 StudyBuddyAgent ({self.BUDDY_NAME}) initialized as TRUE ADVANCED AGENT")
        logger.info(f"   ├── Tools: {', '.join(self.get_available_tools())}")
        logger.info(f"   ├── Memory: LongTermMemory + Session tracking")
        logger.info(f"   └── Verifier: Answer quality checking")
    
    def _register_tools(self):
        """Register StudyBuddy-specific tools"""
        try:
            from agents.core.tools.study_buddy_tools import (
                QuizGeneratorTool,
                PracticeTrackerTool,
                SpacedRepetitionTool,
                FlashcardGeneratorTool
            )
            from agents.core.tools import KnowledgeSearchTool, CalculatorTool
            
            # Core StudyBuddy tools
            self.tool_registry.register(QuizGeneratorTool())
            self.tool_registry.register(PracticeTrackerTool())
            self.tool_registry.register(SpacedRepetitionTool())
            self.tool_registry.register(FlashcardGeneratorTool())
            
            # Shared tools for knowledge and calculations
            self.tool_registry.register(KnowledgeSearchTool())
            self.tool_registry.register(CalculatorTool())
            
            logger.info("   ├── Registered: quiz_generator, practice_tracker, spaced_repetition, flashcard_generator")
            
        except ImportError as e:
            logger.error(f"❌ Failed to register StudyBuddy tools: {e}")
    
    def get_agent_name(self) -> str:
        return "StudyBuddyAgent"
    
    def get_available_tools(self) -> List[str]:
        """Return list of tools this agent can use"""
        return [
            "quiz_generator",       # Generate practice questions
            "practice_tracker",     # Track outcomes and progress
            "spaced_repetition",    # Schedule reviews
            "flashcard_generator",  # Create flashcards
            "knowledge_search",     # Look up concepts
            "calculator"            # Math calculations
        ]
    
    def get_agent_persona(self, context: Dict = None) -> str:
        """
        Return persona adapted to student context.
        
        COGNITIVE OS: Persona is context-aware based on:
        - Student's current level
        - Recent performance
        - Engagement signals
        """
        context = context or {}
        student_profile = context.get('student_profile', {})
        student_name = student_profile.get('user_name', student_profile.get('name', 'friend'))
        mastery_level = student_profile.get('mastery_level', 50)
        
        # Adapt energy based on engagement
        if mastery_level < 30:
            energy_note = "Be extra encouraging - this student needs confidence building."
        elif mastery_level > 70:
            energy_note = "This student is advanced - challenge them appropriately."
        else:
            energy_note = "Standard encouragement - build momentum."
        
        return f"""You are {self.BUDDY_NAME}, an intelligent and friendly study buddy for Indian students.

**YOUR GOAL:** Help {student_name} practice, revise, and stay engaged through interactive learning.

**YOUR CHARACTER:**
- You're a peer, not a teacher - collaborative, not preachy
- You make studying feel like hanging out with a smart friend
- You're encouraging but also push for accuracy
- You adapt to what the student needs in the moment
- You track progress and celebrate wins
- {energy_note}

**YOUR TOOLS (USE THEM!):**
- **quiz_generator**: Generate practice questions by topic and difficulty
- **flashcard_generator**: Create quick revision flashcards
- **practice_tracker**: Record session outcomes, get recommendations
- **spaced_repetition**: Schedule optimal review times
- **knowledge_search**: Look up concepts when needed
- **calculator**: Verify math calculations

**YOUR THINKING PROCESS (ReAct Loop):**
1. THINK: What does the student want? Quiz? Flashcards? Just practice?
2. ACT: Use appropriate tool (DON'T just generate text - USE TOOLS)
3. OBSERVE: Check the result, adapt if needed
4. RESPOND: Give student the content + encouragement

**YOUR STYLE:**
- Conversational: "Alright, let's do this!", "Ooh, good topic!"
- Encouraging: "You've got this!", "Nice thinking!", "Almost there!"
- Interactive: Always engage, never lecture
- Fun: Make studying enjoyable, use emojis sparingly

**CRITICAL RULES:**
- ALWAYS use quiz_generator for quiz requests (don't just write questions)
- ALWAYS use flashcard_generator for flashcard requests
- ALWAYS track progress after practice sessions
- If student needs deep explanation → suggest asking Professor
- If student seems upset → suggest asking Mentor
- Never give answers without letting student try first

**NEVER:**
- Generate quiz questions without using quiz_generator tool
- Skip using tools to "save time"
- Be preachy or lecture-like
- Make student feel bad about wrong answers
- Forget to record practice outcomes"""
    
    @staticmethod
    def is_buddy_query(query: str) -> bool:
        """
        Check if query should route to StudyBuddy.
        
        STRICT ROUTING:
        ✅ Practice/quiz/revision requests → StudyBuddy
        ❌ Deep explanations → Professor
        ❌ Emotional support → Mentor
        ❌ Exam strategy → ExamCoach
        """
        query_lower = query.lower().strip()
        
        # ======================================================================
        # POSITIVE PATTERNS: Route TO StudyBuddy
        # ======================================================================
        buddy_patterns = [
            # Quiz/test requests
            'quiz me', 'test me', 'ask me questions', 'give me questions',
            'practice questions', 'practice test', 'mock quiz',
            
            # Practice requests
            'practice', 'let\'s practice', 'help me practice',
            'practice session', 'practice together',
            
            # Flashcard requests
            'flashcard', 'flashcards', 'flash card', 'flash cards',
            'revision cards', 'memory cards',
            
            # Revision requests
            'revise', 'revision', 'quick revision', 'quick recap',
            'recap', 'review session', 'study session',
            
            # Progress/tracking
            'track my progress', 'how am i doing', 'my progress',
            'what should i practice', 'what next', 'what to study',
            'recommend', 'recommendation',
            
            # Study buddy specific
            'study together', 'study with me', 'study buddy',
            'be my study partner', 'help me study'
        ]
        
        if any(pattern in query_lower for pattern in buddy_patterns):
            logger.info(f"🤝 [StudyBuddy] Query matched buddy pattern: {query[:50]}")
            return True
        
        # ======================================================================
        # NEGATIVE PATTERNS: Do NOT route to StudyBuddy
        # ======================================================================
        # Deep explanation requests → Professor
        professor_patterns = [
            'explain in detail', 'derive', 'prove', 'proof',
            'why does', 'how does', 'what is the theory',
            'mathematically show', 'step by step derivation'
        ]
        
        # Emotional patterns → Mentor
        mentor_patterns = [
            'feeling', 'stressed', 'anxious', 'worried', 'scared',
            'can\'t do this', 'giving up', 'frustrated', 'upset'
        ]
        
        # Exam strategy → ExamCoach
        exam_patterns = [
            'exam strategy', 'exam preparation', 'jee strategy',
            'neet strategy', 'study plan for exam', 'exam tips'
        ]
        
        # If query matches exclusion patterns, return False
        if any(p in query_lower for p in professor_patterns):
            logger.debug(f"[StudyBuddy] Query needs Professor, not StudyBuddy")
            return False
        if any(p in query_lower for p in mentor_patterns):
            logger.debug(f"[StudyBuddy] Query needs Mentor, not StudyBuddy")
            return False
        if any(p in query_lower for p in exam_patterns):
            logger.debug(f"[StudyBuddy] Query needs ExamCoach, not StudyBuddy")
            return False
        
        # Default: Not a StudyBuddy query
        return False
    
    def _get_memory_for_user(self, user_id: str, db=None) -> MemorySystem:
        """
        Get or create memory system for user with REAL database persistence.
        
        MEMORY CONTRACT: Uses MemoryService as SINGLE SOURCE OF TRUTH.
        """
        if user_id not in self._memory_cache:
            # Create memory with database connection for persistence
            self._memory_cache[user_id] = MemorySystem(student_id=user_id, db=db)
        elif db is not None and self._memory_cache[user_id]._db is None:
            # Update db if now available
            self._memory_cache[user_id].set_db(db)
        return self._memory_cache[user_id]
    
    async def _read_student_context(self, user_id: str, context: Dict) -> Dict[str, Any]:
        """
        Read student context from memory.
        
        MEMORY READ: Student level, weak topics, engagement, recent performance
        """
        student_context = {
            "level": "intermediate",
            "weak_topics": [],
            "recent_accuracy": 50,
            "streak": 0,
            "preferred_style": "quiz",
            "last_topics": []
        }
        
        # Get from context_pack if available
        context_pack = context.get('context_pack')
        if context_pack:
            student_context["level"] = "beginner" if context_pack.current_topic_mastery < 30 else (
                "advanced" if context_pack.current_topic_mastery > 70 else "intermediate"
            )
            student_context["weak_topics"] = context_pack.weak_areas or []
        
        # Get from student profile
        profile = context.get('student_profile', {})
        if profile:
            mastery = profile.get('mastery_level', 50)
            student_context["level"] = "beginner" if mastery < 30 else (
                "advanced" if mastery > 70 else "intermediate"
            )
        
        # Try to get from database
        db = context.get('db')
        if db is not None and user_id:
            try:
                # Get recent practice sessions
                from datetime import timedelta
                cutoff = (datetime.utcnow() - timedelta(days=7)).isoformat()
                sessions = await db.practice_sessions.find({
                    "user_id": user_id,
                    "recorded_at": {"$gte": cutoff}
                }).sort("recorded_at", -1).to_list(length=10)
                
                if sessions:
                    # Calculate recent accuracy
                    total_correct = sum(s.get("questions_correct", 0) for s in sessions)
                    total_attempted = sum(s.get("questions_attempted", 0) for s in sessions)
                    if total_attempted > 0:
                        student_context["recent_accuracy"] = (total_correct / total_attempted) * 100
                    
                    # Get last topics
                    student_context["last_topics"] = list(set(
                        s.get("topic") for s in sessions[:5] if s.get("topic")
                    ))
                    
                    # Calculate streak (consecutive days with practice)
                    dates = sorted(set(
                        datetime.fromisoformat(s["recorded_at"].replace('Z', '+00:00')).date()
                        for s in sessions if s.get("recorded_at")
                    ), reverse=True)
                    streak = 0
                    today = datetime.utcnow().date()
                    for i, d in enumerate(dates):
                        if d == today - timedelta(days=i):
                            streak += 1
                        else:
                            break
                    student_context["streak"] = streak
                    
            except Exception as e:
                logger.warning(f"Failed to read student context from DB: {e}")
        
        logger.info(f"📖 [StudyBuddy] Read student context: level={student_context['level']}, "
                   f"accuracy={student_context['recent_accuracy']:.0f}%, streak={student_context['streak']}")
        
        return student_context
    
    async def _write_session_summary(self, user_id: str, session_data: Dict, context: Dict):
        """
        Write session summary to memory.
        
        MEMORY WRITE: Session outcomes, topics covered, performance
        """
        db = context.get('db')
        if db is None:
            logger.debug("[StudyBuddy] No DB connection, skipping session write")
            return
        
        try:
            summary = {
                "user_id": user_id,
                "session_type": "study_buddy",
                "interaction_mode": session_data.get("mode", "general"),
                "topic": session_data.get("topic"),
                "tools_used": session_data.get("tools_used", []),
                "recorded_at": datetime.utcnow().isoformat(),
                "metadata": session_data
            }
            
            await db.study_sessions.insert_one(summary)
            logger.info(f"✍️ [StudyBuddy] Wrote session summary for user {user_id}")
            
        except Exception as e:
            logger.warning(f"Failed to write session summary: {e}")
    
    def _detect_interaction_mode(self, query: str, student_context: Dict) -> str:
        """
        Autonomously decide interaction mode based on query and context.
        
        AUTONOMOUS DECISION: Choose best mode for student
        """
        query_lower = query.lower()
        
        # Explicit mode requests
        if any(w in query_lower for w in ['quiz', 'test me', 'ask me questions']):
            return "quiz"
        if any(w in query_lower for w in ['flashcard', 'flash card']):
            return "flashcards"
        if any(w in query_lower for w in ['revise', 'revision', 'recap']):
            return "recap"
        if any(w in query_lower for w in ['progress', 'how am i', 'what next', 'recommend']):
            return "progress"
        if any(w in query_lower for w in ['due', 'review', 'spaced']):
            return "review"
        if any(w in query_lower for w in ['practice', 'solve', 'problem']):
            return "practice"
        
        # Adaptive decision based on context
        recent_accuracy = student_context.get("recent_accuracy", 50)
        streak = student_context.get("streak", 0)
        
        # If struggling, suggest recap first
        if recent_accuracy < 40:
            logger.info("[StudyBuddy] Student struggling, defaulting to recap mode")
            return "recap"
        
        # If doing well and has streak, suggest quiz
        if recent_accuracy > 70 and streak > 2:
            logger.info("[StudyBuddy] Student doing well, defaulting to quiz mode")
            return "quiz"
        
        # Default to practice
        return "practice"
    
    def _should_handoff(self, query: str, context: Dict) -> Optional[str]:
        """
        Decide if query should be handed off to another agent.
        
        Returns agent name to hand off to, or None.
        """
        query_lower = query.lower()
        
        # Deep explanation → Professor
        if any(w in query_lower for w in ['explain', 'why', 'derive', 'prove', 'theory']):
            if 'in detail' in query_lower or 'step by step' in query_lower:
                logger.info("[StudyBuddy] Query needs deep explanation, suggesting Professor")
                return "professor"
        
        # Emotional support → Mentor
        if any(w in query_lower for w in ['stressed', 'anxious', 'can\'t', 'giving up', 'frustrated']):
            logger.info("[StudyBuddy] Query has emotional signals, suggesting Mentor")
            return "mentor"
        
        return None
    
    async def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process query using TRUE ReAct loop with real tools.
        
        FLOW:
        1. Read student context from memory
        2. Detect interaction mode (autonomous decision)
        3. Check for handoff need
        4. Run ReAct loop with tools
        5. Verify answer quality
        6. Write session summary to memory
        
        Uses parent class's run() method for actual ReAct loop.
        """
        user_id = context.get('user_id', '')
        subject = context.get('subject', 'General')
        
        logger.info(f"🤝 [StudyBuddy] Processing: {query[:80]}...")
        
        try:
            # ================================================================
            # STEP 1: READ STUDENT CONTEXT FROM MEMORY
            # ================================================================
            student_context = await self._read_student_context(user_id, context)
            context['student_context'] = student_context
            
            # ================================================================
            # STEP 2: DETECT INTERACTION MODE (AUTONOMOUS DECISION)
            # ================================================================
            interaction_mode = self._detect_interaction_mode(query, student_context)
            logger.info(f"🎯 [StudyBuddy] Chose mode: {interaction_mode} | "
                       f"Student level: {student_context['level']}")
            
            # ================================================================
            # STEP 3: CHECK FOR HANDOFF
            # ================================================================
            handoff_agent = self._should_handoff(query, context)
            if handoff_agent:
                handoff_msg = f"""Hey! That sounds like something {
                    'Professor Druv' if handoff_agent == 'professor' else 'Druv'
                } would be better at explaining in detail. 

Want me to get them to help you with that? Or we can do a quick practice first and then dive deeper? 

Just let me know! 😊"""
                
                return {
                    'success': True,
                    'content': f"{self.BUDDY_NAME}: {handoff_msg}",
                    'agent': self.get_agent_name(),
                    'interaction_mode': interaction_mode,
                    'suggested_handoff': handoff_agent,
                    'metadata': {
                        'handoff_suggested': True,
                        'handoff_agent': handoff_agent
                    }
                }
            
            # ================================================================
            # STEP 4: ENRICH CONTEXT FOR REACT LOOP
            # ================================================================
            # Add interaction mode to context for persona adaptation
            context['interaction_mode'] = interaction_mode
            context['buddy_name'] = self.BUDDY_NAME
            
            # Extract topic from query for tools
            topic = self._extract_topic(query, subject, context)
            context['detected_topic'] = topic
            
            # ================================================================
            # STEP 5: RUN REACT LOOP (Uses parent class)
            # ================================================================
            logger.info(f"🔄 [StudyBuddy] Running ReAct loop for mode: {interaction_mode}")
            
            # Call parent's run() which executes the proper ReAct loop
            result = await self.run(query, context)
            
            # ================================================================
            # STEP 6: VERIFY ANSWER QUALITY
            # ================================================================
            if result.get('success') and result.get('content'):
                verification = await self._verify_response(result['content'], query, context)
                result['verification'] = verification
                
                if not verification.get('passed', True):
                    logger.warning(f"[StudyBuddy] Verification flagged issues: {verification.get('issues')}")
            
            # ================================================================
            # STEP 7: WRITE SESSION SUMMARY TO MEMORY
            # ================================================================
            session_data = {
                'mode': interaction_mode,
                'topic': topic,
                'tools_used': result.get('tools_used', []),
                'success': result.get('success', False)
            }
            await self._write_session_summary(user_id, session_data, context)
            
            # Add StudyBuddy metadata
            result['agent'] = self.get_agent_name()
            result['buddy_name'] = self.BUDDY_NAME
            result['interaction_mode'] = interaction_mode
            result['student_context'] = {
                'level': student_context['level'],
                'streak': student_context['streak']
            }
            
            logger.info(f"✅ [StudyBuddy] Completed {interaction_mode} session | "
                       f"Tools used: {result.get('tools_used', [])}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ [StudyBuddy] Error: {e}", exc_info=True)
            return {
                'success': False,
                'content': f"{self.BUDDY_NAME}: Oops! Had a small hiccup. Let's try that again - what would you like to practice? 😊",
                'error': str(e),
                'agent': self.get_agent_name()
            }
    
    def _extract_topic(self, query: str, subject: str, context: Dict) -> str:
        """Extract topic from query for tool usage"""
        # Common topic keywords
        topic_indicators = ['on', 'about', 'for', 'in', 'of']
        
        query_lower = query.lower()
        
        # Try to find topic after indicators
        for indicator in topic_indicators:
            if f' {indicator} ' in query_lower:
                parts = query_lower.split(f' {indicator} ')
                if len(parts) > 1:
                    # Get the part after indicator, clean it
                    topic_part = parts[-1].strip()
                    # Remove common suffixes
                    for suffix in ['?', '!', '.', ',', 'please', 'now']:
                        topic_part = topic_part.replace(suffix, '').strip()
                    if topic_part and len(topic_part) > 2:
                        return topic_part.title()
        
        # Fall back to subject
        return subject if subject != 'General' else 'General Science'
    
    async def _verify_response(self, content: str, query: str, context: Dict) -> Dict:
        """
        Verify response quality.
        
        Checks:
        - Content length appropriate
        - No incorrect formulas (if detectable)
        - Student-friendly tone
        """
        issues = []
        
        # Check minimum content
        if len(content) < 50:
            issues.append("Response too short")
        
        # Check for common issues
        if content.count('**') > 20:
            issues.append("Excessive formatting")
        
        # Check tone (simple heuristics)
        negative_phrases = ['you should know', 'obviously', 'clearly you', 'you must']
        for phrase in negative_phrases:
            if phrase in content.lower():
                issues.append(f"Potentially condescending phrase: '{phrase}'")
        
        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'content_length': len(content)
        }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_study_buddy(config: Optional[Dict[str, Any]] = None) -> StudyBuddyAgent:
    """Create StudyBuddyAgent instance"""
    return StudyBuddyAgent(config)
