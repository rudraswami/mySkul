"""
🏆 EXAM COACH AGENT - Strategic Exam Preparation Expert

This agent provides intelligent exam preparation guidance:
- Exam-specific strategies (JEE, NEET, CBSE boards)
- Time management and study plans
- PYQ pattern analysis
- Last-minute tips
- Topper strategies

Persona: A mentor who has coached hundreds of toppers
"""

import logging
from typing import Dict, Any, Optional
from agents.intelligent_agent_base import IntelligentAgentBase

logger = logging.getLogger(__name__)


class ExamCoachAgent(IntelligentAgentBase):
    """
    Intelligent exam coach that uses LLM for personalized strategies
    """
    
    # Exam-specific knowledge base
    EXAM_INFO = {
        'JEE': {
            'full_name': 'JEE Main/Advanced',
            'subjects': ['Physics', 'Chemistry', 'Mathematics'],
            'marks': {'Physics': 100, 'Chemistry': 100, 'Mathematics': 100},
            'duration': '3 hours',
            'key_tip': 'Focus on NCERT + HC Verma + PYQs'
        },
        'NEET': {
            'full_name': 'NEET-UG',
            'subjects': ['Physics', 'Chemistry', 'Biology'],
            'marks': {'Physics': 180, 'Chemistry': 180, 'Biology': 360},
            'duration': '3 hours 20 minutes',
            'key_tip': 'Biology is 50% - master NCERT line by line'
        },
        'CBSE': {
            'full_name': 'CBSE Board Exams',
            'subjects': ['All'],
            'key_tip': 'NCERT is the Bible. Practice sample papers.'
        }
    }
    
    @staticmethod
    def is_exam_strategy_query(query: str) -> bool:
        """Detect if this is an exam strategy query"""
        query_lower = query.lower()
        
        strategy_phrases = [
            # Strategy requests
            'prepare for', 'preparation', 'strategy', 'plan',
            'how to study', 'study plan', 'revision plan',
            'time management', 'schedule',
            
            # Exam-specific
            'jee', 'neet', 'cbse', 'board exam', 'boards',
            'upsc', 'entrance', 'competitive',
            
            # Tips requests
            'tips', 'tricks', 'hacks', 'secrets',
            'topper', 'rank', 'score',
            
            # Timeline queries
            'days left', 'one month', 'last minute',
            'before exam', 'exam tomorrow', 'week before'
        ]
        
        return any(phrase in query_lower for phrase in strategy_phrases)
    
    def get_agent_type(self) -> str:
        return 'exam_coach'
    
    def get_agent_persona(self) -> str:
        """Expert exam coach persona"""
        return """You are an experienced exam coach who has mentored hundreds of JEE/NEET toppers.

YOUR CHARACTER:
- You've seen what works and what doesn't
- You give practical, actionable advice - not vague motivation
- You understand Indian exam pressure and family expectations
- You're direct but encouraging

YOUR STYLE:
- Be specific: "Study 4 hours of Physics: 2 hours theory, 2 hours problems"
- Share insider knowledge: "JEE loves rotational mechanics - 3-4 questions guaranteed"
- Be realistic about time: "With 30 days left, here's what's actually possible..."
- Reference real patterns: "Last 5 years, this topic appeared 90% of times"

AVOID:
- Generic advice like "study hard"
- Unrealistic schedules
- Ignoring student's current level
- Cookie-cutter plans
"""
    
    def get_specialized_instructions(self, query: str, context: Dict[str, Any]) -> str:
        """Instructions based on the exam strategy query"""
        
        query_lower = query.lower()
        subject = context.get('subject', 'General')
        
        # Detect which exam
        exam = 'JEE'  # Default
        if 'neet' in query_lower:
            exam = 'NEET'
        elif 'cbse' in query_lower or 'board' in query_lower:
            exam = 'CBSE'
        elif 'upsc' in query_lower:
            exam = 'UPSC'
        
        exam_info = self.EXAM_INFO.get(exam, self.EXAM_INFO['JEE'])
        
        # Detect timeline
        timeline_context = ""
        if any(w in query_lower for w in ['tomorrow', 'one day', '1 day']):
            timeline_context = """
TIMELINE: 1 DAY LEFT
- Focus on formulas and key concepts only
- Review previous mistakes
- Don't start anything new
- Get proper sleep - it's MORE important than one more hour of study
"""
        elif any(w in query_lower for w in ['week', '7 days', 'one week']):
            timeline_context = """
TIMELINE: 1 WEEK LEFT
- Focus on high-weightage topics only
- Solve 2-3 previous year papers
- Revise formula sheets daily
- Identify and drop lowest-ROI topics
"""
        elif any(w in query_lower for w in ['month', '30 days']):
            timeline_context = """
TIMELINE: 1 MONTH LEFT
- Complete syllabus revision possible
- Daily: 2 hours revision + 3 hours practice
- Weekly mock tests (full length)
- Focus on weak areas first 2 weeks, then strengthen strong areas
"""
        else:
            timeline_context = """
TIMELINE: General preparation
- Give a balanced, sustainable plan
- Include breaks and rest
- Suggest milestone checkpoints
"""
        
        return f"""
EXAM: {exam} ({exam_info.get('full_name', exam)})
SUBJECT: {subject}

{timeline_context}

EXAM INSIDER TIP: {exam_info.get('key_tip', 'Focus on fundamentals and PYQs')}

RESPONSE STRUCTURE:
1. Quick assessment of their situation (based on query)
2. Specific, actionable strategy (with time allocations)
3. Priority topics for {subject} in {exam}
4. One "topper secret" that most students miss
5. Encouraging close: "You've got this" (not cringe)

BE SPECIFIC:
- Name actual books/resources
- Give hour-by-hour plans if asked
- Reference actual exam patterns
- Share chapter-wise weightage if relevant
"""
    
    def _get_fallback_response(self, query: str, context: Dict[str, Any]) -> str:
        """Fallback if LLM fails"""
        exam = context.get('student_profile', {}).get('exam', 'JEE')
        
        return f"""Here's a focused strategy for {exam} preparation:

🎯 **Priority Framework**
1. **High-weightage topics first** - 60% of marks from 40% of syllabus
2. **PYQ patterns** - Last 5 years questions are gold
3. **NCERT mastery** - The foundation that toppers never skip

📊 **Daily Schedule Template**
- 3 hours: New concept learning
- 2 hours: Problem practice
- 1 hour: Revision of previous topics

💡 **Topper Secret**
The difference between 90% and 99% isn't more studying - it's *strategic* studying.

What specific area would you like me to help you plan? Subject, timeline, or overall strategy?"""


# ============================================
# COMPATIBILITY
# ============================================

def is_exam_strategy_query(query: str) -> bool:
    """Module-level function for import compatibility"""
    return ExamCoachAgent.is_exam_strategy_query(query)
