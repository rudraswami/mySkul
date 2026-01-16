"""
🎯 AGENT SELECTOR - Strategy Selection (Not Competition)
========================================================

This module selects the BEST agent for a query using RULES (not LLM).
Only ONE agent processes each request - no competition, no parallel calls.

Key Principle:
    Agent Competition → Cascading LLM calls → Timeout storms
    Agent Selection → Single LLM call → Predictable execution
"""

import logging
import re
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Available agent types"""
    MENTOR = "MentorAgent"         # Explains concepts, teaches
    PROFESSOR = "ProfessorAgent"   # Solves problems, derives
    EXAM_COACH = "ExamCoachAgent"  # Exam tips, strategies
    SIMPLE = "SimpleAgent"         # Quick factual responses


class AgentSelector:
    """
    Rule-based agent selector.
    
    Selects the best agent for a query using pattern matching.
    NO LLM calls - purely deterministic.
    
    Selection Rules:
    1. Greeting/simple → SimpleAgent (no LLM needed)
    2. "solve", "calculate", "derive" → ProfessorAgent
    3. "exam", "tips", "strategy", "marks" → ExamCoachAgent
    4. "explain", "what is", "why", "how" → MentorAgent (default)
    """
    
    # Pattern definitions (compiled for performance)
    SIMPLE_PATTERNS = [
        r'^(hi|hello|hey|thanks|thank you|ok|okay|bye|good)\b',
        r'^(yes|no|sure|got it|understood)\b',
        r'^(hmm|oh|ah|wow)\b',
    ]
    
    PROFESSOR_PATTERNS = [
        r'\b(solve|calculate|compute|derive|find the value|prove)\b',
        r'\b(equation|formula|numerical|step by step solution)\b',
        r'\b(integrate|differentiate|simplify)\b',
        r'\b(\d+\s*[\+\-\*\/]\s*\d+)',  # Math expressions
    ]
    
    EXAM_COACH_PATTERNS = [
        r'\b(exam|test|jee|neet|board|marks|score)\b',
        r'\b(tips|strategy|revision|important questions)\b',
        r'\b(time management|prepare|preparation)\b',
        r'\b(previous year|pyq|pattern)\b',
    ]
    
    MENTOR_PATTERNS = [
        r'\b(explain|what is|what are|why|how does|describe)\b',
        r'\b(concept|understand|meaning|definition)\b',
        r'\b(difference between|compare|versus|vs)\b',
        r'\b(example|analogy|real world|daily life)\b',
    ]
    
    @classmethod
    def select_agent(cls, query: str, subject: Optional[str] = None) -> AgentType:
        """
        Select the best agent for a query.
        
        Args:
            query: User's question
            subject: Optional subject hint
        
        Returns:
            AgentType for the selected agent
        """
        query_lower = query.lower().strip()
        
        # Check for simple/greeting patterns first
        for pattern in cls.SIMPLE_PATTERNS:
            if re.search(pattern, query_lower):
                logger.info(f"🎯 Agent selected: SimpleAgent (greeting/simple)")
                return AgentType.SIMPLE
        
        # Check for professor patterns (problem solving)
        for pattern in cls.PROFESSOR_PATTERNS:
            if re.search(pattern, query_lower):
                logger.info(f"🎯 Agent selected: ProfessorAgent (problem solving)")
                return AgentType.PROFESSOR
        
        # Check for exam coach patterns
        for pattern in cls.EXAM_COACH_PATTERNS:
            if re.search(pattern, query_lower):
                logger.info(f"🎯 Agent selected: ExamCoachAgent (exam/strategy)")
                return AgentType.EXAM_COACH
        
        # Check for mentor patterns (concept explanation)
        for pattern in cls.MENTOR_PATTERNS:
            if re.search(pattern, query_lower):
                logger.info(f"🎯 Agent selected: MentorAgent (concept explanation)")
                return AgentType.MENTOR
        
        # Default to MentorAgent for educational content
        logger.info(f"🎯 Agent selected: MentorAgent (default)")
        return AgentType.MENTOR
    
    @classmethod
    def get_agent_config(cls, agent_type: AgentType) -> Dict[str, Any]:
        """
        Get configuration for the selected agent.
        
        Returns agent-specific settings like system prompts, temperature, etc.
        """
        configs = {
            AgentType.SIMPLE: {
                "name": "SimpleAgent",
                "system_prompt": "You are a friendly educational assistant. Give brief, helpful responses.",
                "temperature": 0.7,
                "max_tokens": 200,
                "needs_llm": False,  # Can respond without LLM for greetings
            },
            AgentType.MENTOR: {
                "name": "MentorAgent",
                "system_prompt": """You are Sathi, a friendly Indian AI tutor for students.
Explain concepts clearly using relatable Indian examples (cricket, chai, local scenarios).
Use simple language, break down complex topics, and encourage the student.
Format: Start with a warm greeting, explain the concept, give an example, end with encouragement.""",
                "temperature": 0.7,
                "max_tokens": 600,
                "needs_llm": True,
            },
            AgentType.PROFESSOR: {
                "name": "ProfessorAgent", 
                "system_prompt": """You are a precise problem-solving tutor.
Solve problems step-by-step with clear mathematical notation.
Show your working, state formulas used, and verify the answer.
Format: Given → Find → Solution Steps → Answer → Verification""",
                "temperature": 0.3,
                "max_tokens": 800,
                "needs_llm": True,
            },
            AgentType.EXAM_COACH: {
                "name": "ExamCoachAgent",
                "system_prompt": """You are an exam preparation coach for Indian competitive exams.
Give practical tips, time management strategies, and important topics.
Focus on JEE, NEET, and board exam patterns.
Format: Key Points → Strategy → Common Mistakes → Quick Tips""",
                "temperature": 0.5,
                "max_tokens": 500,
                "needs_llm": True,
            },
        }
        
        return configs.get(agent_type, configs[AgentType.MENTOR])


class SimpleResponseGenerator:
    """
    Generates responses for simple queries WITHOUT LLM.
    
    Used for greetings, acknowledgments, and simple interactions
    that don't need expensive LLM calls.
    """
    
    RESPONSES = {
        "greeting": [
            "Hey! 👋 I'm Sathi, your study buddy. What would you like to learn today?",
            "Hi there! Ready to learn something awesome? Ask me anything! 📚",
            "Hello! I'm here to help you understand any concept. What's on your mind?",
        ],
        "thanks": [
            "You're welcome! 😊 Feel free to ask if you have more questions!",
            "Happy to help! Keep those questions coming! 💪",
            "Anytime! That's what I'm here for. What else would you like to know?",
        ],
        "acknowledgment": [
            "Great! Let me know if you need any clarification.",
            "Got it! Feel free to ask follow-up questions.",
            "Understood! I'm here if you need more help.",
        ],
        "farewell": [
            "Bye! Good luck with your studies! 📖✨",
            "See you later! Keep learning! 🌟",
            "Take care! Come back anytime you need help!",
        ],
    }
    
    @classmethod
    def generate(cls, query: str) -> Optional[str]:
        """
        Generate a simple response without LLM.
        
        Returns None if the query needs LLM processing.
        """
        query_lower = query.lower().strip()
        
        # Detect greeting
        if re.search(r'^(hi|hello|hey|good morning|good evening)\b', query_lower):
            import random
            return random.choice(cls.RESPONSES["greeting"])
        
        # Detect thanks
        if re.search(r'\b(thanks|thank you|thx)\b', query_lower):
            import random
            return random.choice(cls.RESPONSES["thanks"])
        
        # Detect acknowledgment
        if re.search(r'^(ok|okay|got it|understood|yes|sure)\b', query_lower):
            import random
            return random.choice(cls.RESPONSES["acknowledgment"])
        
        # Detect farewell
        if re.search(r'\b(bye|goodbye|see you|later)\b', query_lower):
            import random
            return random.choice(cls.RESPONSES["farewell"])
        
        # Not a simple query - needs LLM
        return None


def select_and_configure_agent(query: str, subject: Optional[str] = None) -> Dict[str, Any]:
    """
    Main entry point for agent selection.
    
    Returns:
        {
            "agent_type": AgentType,
            "config": {...},
            "simple_response": str or None  # If set, no LLM needed
        }
    """
    # First check if it's a simple query
    simple_response = SimpleResponseGenerator.generate(query)
    if simple_response:
        return {
            "agent_type": AgentType.SIMPLE,
            "config": AgentSelector.get_agent_config(AgentType.SIMPLE),
            "simple_response": simple_response,
            "needs_llm": False,
        }
    
    # Select appropriate agent
    agent_type = AgentSelector.select_agent(query, subject)
    config = AgentSelector.get_agent_config(agent_type)
    
    return {
        "agent_type": agent_type,
        "config": config,
        "simple_response": None,
        "needs_llm": config.get("needs_llm", True),
    }
