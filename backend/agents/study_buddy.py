"""
🤝 STUDY BUDDY AGENT - Intelligent Peer Learning Companion

This agent creates a friendly, intelligent study partner experience.
Unlike template-based agents, this uses LLM to generate natural responses.

Features:
- Natural conversation like studying with a friend
- Adapts to student's mood and energy level
- Collaborative problem-solving
- Quiz generation on-the-fly
- Concept discussions
- Revision sessions

Persona: "Priya" - A friendly senior student who's been through the same exams
"""

import logging
from typing import Dict, Any, Optional, List
from agents.intelligent_agent_base import IntelligentAgentBase

logger = logging.getLogger(__name__)


class StudyBuddyAgent(IntelligentAgentBase):
    """
    Intelligent Study Buddy that uses LLM for natural conversations
    """
    
    BUDDY_NAME = "Priya"
    
    @staticmethod
    def is_buddy_query(query: str) -> bool:
        """Detect if this is a study buddy request"""
        query_lower = query.lower()
        
        buddy_phrases = [
            'study together', 'study with me', 'study buddy',
            'practice together', 'let\'s study', 'lets study',
            'quiz me', 'test me', 'help me practice',
            'revise together', 'revision session',
            'discuss', 'explain to me', 'teach me',
            'study partner', 'study session'
        ]
        
        return any(phrase in query_lower for phrase in buddy_phrases)
    
    def get_agent_type(self) -> str:
        return 'study_buddy'
    
    def get_agent_persona(self) -> str:
        """Priya - the friendly study buddy"""
        return f"""You are {self.BUDDY_NAME}, a friendly and intelligent study buddy.

YOUR CHARACTER:
- You're like an older sister/friend who topped the same exams
- Warm, encouraging, but also focused on actual learning
- You use simple language, occasional humor, and relatable examples
- You celebrate small wins and gently correct mistakes
- You're patient but keep things moving

YOUR STYLE:
- Start responses with just "{self.BUDDY_NAME}:" (not every time, only occasionally to show it's you)
- Be conversational - "Hmm, that's a good question!" or "Ooh, I love this topic!"
- Use encouraging phrases: "You're getting there!", "Almost!", "Nice thinking!"
- When student is stuck, don't give answers directly - guide them
- Make studying feel like a fun activity, not a chore"""
    
    def get_specialized_instructions(self, query: str, context: Dict[str, Any]) -> str:
        """Instructions based on what the student wants to do"""
        
        query_lower = query.lower()
        subject = context.get('subject', 'General')
        
        # Detect what type of study session
        if any(w in query_lower for w in ['quiz', 'test me', 'question']):
            return f"""
STUDY MODE: Quick Quiz
- Ask ONE good question about {subject}
- Make it exam-relevant
- After student answers, give feedback
- Keep it fun: "Let's see if you can crack this one!"
"""
        
        elif any(w in query_lower for w in ['problem', 'solve', 'practice']):
            return f"""
STUDY MODE: Problem Solving
- Pick a relevant problem from {subject}
- Guide step by step, don't just give answer
- "What do you think we should do first?"
- Celebrate when they get steps right
"""
        
        elif any(w in query_lower for w in ['explain', 'concept', 'understand', 'discuss']):
            return f"""
STUDY MODE: Concept Discussion
- Explain like you're chatting, not lecturing
- Use analogies from student's world
- Ask "Does this make sense?" periodically
- Connect to exam patterns: "They love asking this in JEE/NEET!"
"""
        
        elif any(w in query_lower for w in ['revise', 'revision', 'review']):
            return f"""
STUDY MODE: Revision Session
- Quick recap of key points
- "Remember when we discussed..." 
- Flag common mistakes
- End with "What topic next?"
"""
        
        else:
            # General study together
            return f"""
STUDY MODE: Starting Study Session
- Welcome them warmly (use their name if available)
- Ask what they want to focus on today
- Offer options:
  * Concept discussion
  * Problem solving
  * Quick quiz
  * Revision
- Be genuinely helpful, not just listing options robotically
"""
    
    def _get_fallback_response(self, query: str, context: Dict[str, Any]) -> str:
        """Fallback if LLM fails"""
        name = context.get('student_profile', {}).get('user_name', '')
        greeting = f"Hey {name}! " if name and len(name) > 1 else "Hey! "
        
        return f"""{self.BUDDY_NAME}: {greeting}Ready to study together! 📚

What would you like to do?

1. **Concept Discussion** - I'll explain, you ask questions
2. **Problem Solving** - We tackle problems step by step
3. **Quick Quiz** - I'll test you (don't worry, it's fun!)
4. **Revision** - Quick review of important stuff

Just tell me what you're in the mood for! 💪"""
    
    def _post_process_response(
        self,
        response: str,
        query: str,
        context: Dict[str, Any]
    ) -> str:
        """Clean up the response"""
        
        # Remove any duplicate "Priya:" if LLM added extra
        if response.startswith(f"{self.BUDDY_NAME}: {self.BUDDY_NAME}:"):
            response = response.replace(f"{self.BUDDY_NAME}: {self.BUDDY_NAME}:", f"{self.BUDDY_NAME}:", 1)
        
        return response


# ============================================
# COMPATIBILITY: Old interface
# ============================================

async def create_study_session(
    student_id: str,
    subject: str,
    topic: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new study buddy session"""
    agent = StudyBuddyAgent({})
    context = {
        'student_profile': {'user_id': student_id},
        'subject': subject,
        'session_data': {'topic': topic}
    }
    
    return await agent.process(
        "Let's study together",
        context
    )
