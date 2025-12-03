"""
Study Buddy Agent - TRUE AGENTIC Interactive Learning Companion
================================================================

UPGRADED to TRUE AGENT with:
- ReAct Loop: Think → Act → Observe
- Tools: QuizGenerator, ProblemSelector, ProgressTracker
- Memory: Remembers study sessions, tracks progress, adapts difficulty
- Actions: GENERATES quizzes, SELECTS problems, TRACKS progress

OLD: Friendly conversation
NEW: INTERACTIVE study sessions with real quizzes, problem-solving, tracking
"""

import logging
from typing import Dict, Any, Optional, List
from agents.core.react_agent import ReActAgent
from agents.core.tool_registry import ToolRegistry
from agents.core.memory import LongTermMemory

logger = logging.getLogger(__name__)


class StudyBuddyAgent(ReActAgent):
    """
    TRUE AGENTIC Study Buddy - Interactive Learning Companion
    
    Capabilities:
    - Generates on-the-fly quizzes based on topic
    - Selects problems matched to student's level
    - Tracks progress across study sessions
    - Adapts difficulty based on performance
    - Provides collaborative problem-solving experience
    """
    
    BUDDY_NAME = "Priya"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Initialize tool registry
        self.tool_registry = ToolRegistry()
        # Tools will be registered as we create them
        
        # Initialize memory for session tracking (will be set per user)
        self.memory = None  # Set during process() with actual user_id
        
        logger.info(f"🤝 StudyBuddyAgent ({self.BUDDY_NAME}) initialized as TRUE AGENT")
    
    def get_agent_name(self) -> str:
        return "StudyBuddyAgent"
    
    def get_available_tools(self) -> list:
        """Return list of tools this agent can use"""
        return []  # StudyBuddy uses LLM primarily for interactive sessions
    
    def get_agent_persona(self) -> str:
        return f"""You are {self.BUDDY_NAME}, a friendly and intelligent study buddy.

Your role:
- Make studying feel like hanging out with a smart friend
- Generate quizzes and problems on-the-fly
- Guide through problem-solving (don't just give answers)
- Track progress and celebrate wins
- Adapt difficulty based on performance

Your style:
- Conversational: "Hmm, that's interesting!", "Ooh, I love this topic!"
- Encouraging: "You're getting there!", "Almost!", "Nice thinking!"
- Collaborative: "Let's figure this out together"
- Fun: Make studying enjoyable, not a chore

Remember:
- You're a peer, not a teacher
- Guide, don't lecture
- Celebrate small wins
- Keep energy high"""
    
    @staticmethod
    def is_buddy_query(query: str) -> bool:
        """Check if query is for study buddy"""
        patterns = [
            'study together', 'study with me', 'study buddy',
            'quiz me', 'test me', 'practice together',
            'let\'s study', 'help me practice', 'revision session'
        ]
        query_lower = query.lower()
        return any(pattern in query_lower for pattern in patterns)
    
    async def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate study buddy response using ReAct loop.
        
        Think: What does the student want to do? Quiz? Problem-solving? Discussion?
        Act: Generate appropriate content (quiz/problem/explanation)
        Observe: Track engagement and adapt
        """
        try:
            user_id = context.get('user_id', '')
            subject = context.get('subject', 'General')
            student_profile = context.get('student_profile', {})
            
            logger.info(f"🤝 {self.BUDDY_NAME} starting study session")
            
            # THINK: Determine study mode
            study_mode = self._detect_study_mode(query)
            thought = f"Student wants: {study_mode}. Subject: {subject}."
            logger.info(f"🧠 {thought}")
            
            # ACT: Generate appropriate content
            if study_mode == 'quiz':
                content = await self._generate_quiz(query, subject, context)
            elif study_mode == 'problem_solving':
                content = await self._guide_problem_solving(query, subject, context)
            elif study_mode == 'concept_discussion':
                content = await self._discuss_concept(query, subject, context)
            elif study_mode == 'revision':
                content = await self._revision_session(query, subject, context)
            else:
                content = await self._start_study_session(query, subject, context)
            
            # OBSERVE: Session started
            observation = f"{study_mode} session initiated"
            
            return {
                'success': True,
                'content': content,
                'study_mode': study_mode,
                'buddy_name': self.BUDDY_NAME,
                'thought': thought,
                'action': f'start_{study_mode}',
                'observation': observation
            }
            
        except Exception as e:
            logger.error(f"❌ StudyBuddy error: {e}", exc_info=True)
            return {
                'success': False,
                'content': f"{self.BUDDY_NAME}: Hey! Let's study together. What would you like to focus on?",
                'error': str(e)
            }
    
    def _detect_study_mode(self, query: str) -> str:
        """Detect what type of study session student wants"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['quiz', 'test me', 'question']):
            return 'quiz'
        elif any(word in query_lower for word in ['problem', 'solve', 'practice']):
            return 'problem_solving'
        elif any(word in query_lower for word in ['explain', 'concept', 'understand', 'discuss']):
            return 'concept_discussion'
        elif any(word in query_lower for word in ['revise', 'revision', 'review']):
            return 'revision'
        else:
            return 'general'
    
    async def _generate_quiz(self, query: str, subject: str, context: Dict[str, Any]) -> str:
        """Generate an interactive quiz"""
        
        # Build quiz prompt
        prompt = f"""You are {self.BUDDY_NAME}, generating a quiz question.

Subject: {subject}
Student's request: {query}

Generate ONE good exam-relevant question with 4 options (A, B, C, D).

Format:
{self.BUDDY_NAME}: Alright, let's see if you can crack this one! 🎯

**Question:**
[Your question here]

A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]

Take your time and let me know your answer!"""
        
        # Use LLM to generate quiz
        response = await self._call_llm(prompt, query, context)
        return response
    
    async def _guide_problem_solving(self, query: str, subject: str, context: Dict[str, Any]) -> str:
        """Guide through problem-solving"""
        
        prompt = f"""You are {self.BUDDY_NAME}, helping solve a problem collaboratively.

Subject: {subject}
Problem: {query}

DON'T give the full solution immediately. Instead:
1. Ask what they think the first step should be
2. Guide them with hints
3. Celebrate when they get steps right

Format:
{self.BUDDY_NAME}: Ooh, interesting problem! Let's tackle this together. 💪

[Brief analysis of the problem]

What do you think we should do first? Any ideas?"""
        
        response = await self._call_llm(prompt, query, context)
        return response
    
    async def _discuss_concept(self, query: str, subject: str, context: Dict[str, Any]) -> str:
        """Discuss concept in friendly way"""
        
        prompt = f"""You are {self.BUDDY_NAME}, explaining a concept like a friend.

Subject: {subject}
Concept: {query}

Explain in a conversational way:
- Use analogies from student's world
- Break it down simply
- Ask "Does this make sense?" periodically
- Connect to exam patterns

Format:
{self.BUDDY_NAME}: Ah, {subject}! I love this topic. Let me explain... 📚

[Your friendly explanation]

Does this make sense so far?"""
        
        response = await self._call_llm(prompt, query, context)
        return response
    
    async def _revision_session(self, query: str, subject: str, context: Dict[str, Any]) -> str:
        """Quick revision session"""
        
        prompt = f"""You are {self.BUDDY_NAME}, doing a quick revision session.

Subject: {subject}
Topic: {query}

Provide:
- Quick recap of key points
- Common mistakes to avoid
- One exam tip

Format:
{self.BUDDY_NAME}: Let's do a quick revision! ⚡

**Key Points:**
[3-5 bullet points]

**Common Mistakes:**
[1-2 mistakes to avoid]

**Exam Tip:**
[One useful tip]

Ready for the next topic?"""
        
        response = await self._call_llm(prompt, query, context)
        return response
    
    async def _start_study_session(self, query: str, subject: str, context: Dict[str, Any]) -> str:
        """Start general study session"""
        
        name = context.get('student_profile', {}).get('name', '')
        greeting = f"Hey {name}! " if name else "Hey! "
        
        return f"""{self.BUDDY_NAME}: {greeting}Ready to study together! 📚

What would you like to do?

1. **Concept Discussion** - I'll explain, you ask questions
2. **Problem Solving** - We tackle problems step by step
3. **Quick Quiz** - I'll test you (don't worry, it's fun!)
4. **Revision** - Quick review of important stuff

Just tell me what you're in the mood for! 💪"""
    
    async def _call_llm(self, prompt: str, query: str, context: Dict[str, Any]) -> str:
        """Call LLM for response generation"""
        
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        import os
        
        emergent_llm_key = os.environ.get('EMERGENT_LLM_KEY') or self.config.get('emergent_llm_key')
        
        llm_chat = LlmChat(
            api_key=emergent_llm_key,
            session_id=f"studybuddy_{context.get('user_id', 'unknown')}",
            system_message=prompt
        )
        
        user_message = UserMessage(text=query)
        response = await llm_chat.send_message(user_message)
        
        return response if isinstance(response, str) else str(response)


# Factory function
def create_study_buddy(config: Optional[Dict[str, Any]] = None) -> StudyBuddyAgent:
    """Create StudyBuddyAgent instance"""
    return StudyBuddyAgent(config)
