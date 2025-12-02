"""
Proactive Mentor System - Anticipates Student Needs
====================================================
Goes beyond answering questions to:
- Suggest next learning steps
- Detect knowledge gaps
- Offer timely revision reminders
- Generate personalized study paths
- Celebrate milestones

Philosophy: "A great mentor doesn't wait to be asked - they guide proactively."
"""

import logging
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class ProactiveActionType(Enum):
    """Types of proactive actions the mentor can take"""
    SUGGEST_NEXT_TOPIC = "suggest_next_topic"
    OFFER_PRACTICE = "offer_practice"
    REVISION_REMINDER = "revision_reminder"
    CELEBRATE_MILESTONE = "celebrate_milestone"
    CLARIFY_CONFUSION = "clarify_confusion"
    CONNECT_CONCEPTS = "connect_concepts"
    EXAM_STRATEGY = "exam_strategy"
    MOTIVATIONAL_BOOST = "motivational_boost"


class LearningPath:
    """Defines optimal learning paths for subjects"""
    
    PHYSICS_PATH = {
        "mechanics": {
            "prerequisites": [],
            "subtopics": ["kinematics", "newton's laws", "work energy", "circular motion", "rotation"],
            "next": ["gravitation", "shm"],
            "weight_jee": "25%",
            "difficulty_ramp": [1, 2, 3, 4, 5]
        },
        "electromagnetism": {
            "prerequisites": ["mechanics"],
            "subtopics": ["electrostatics", "current electricity", "magnetism", "electromagnetic induction"],
            "next": ["modern physics"],
            "weight_jee": "20%",
            "difficulty_ramp": [2, 3, 4, 5, 5]
        },
        "optics": {
            "prerequisites": ["waves"],
            "subtopics": ["ray optics", "wave optics", "interference", "diffraction"],
            "next": ["modern physics"],
            "weight_jee": "10%"
        },
        "modern physics": {
            "prerequisites": ["electromagnetism"],
            "subtopics": ["photoelectric effect", "atomic structure", "nuclear physics", "semiconductors"],
            "next": [],
            "weight_jee": "15%"
        }
    }
    
    CHEMISTRY_PATH = {
        "physical_chemistry": {
            "prerequisites": [],
            "subtopics": ["mole concept", "thermodynamics", "equilibrium", "electrochemistry", "kinetics"],
            "next": [],
            "weight_jee": "35%"
        },
        "inorganic_chemistry": {
            "prerequisites": ["physical_chemistry"],
            "subtopics": ["periodic table", "chemical bonding", "coordination compounds", "metallurgy"],
            "next": [],
            "weight_jee": "30%"
        },
        "organic_chemistry": {
            "prerequisites": [],
            "subtopics": ["hydrocarbons", "halides", "alcohols", "carbonyl compounds", "named reactions"],
            "next": [],
            "weight_jee": "35%"
        }
    }
    
    MATH_PATH = {
        "algebra": {
            "prerequisites": [],
            "subtopics": ["complex numbers", "quadratic equations", "sequences", "binomial theorem"],
            "next": ["calculus"],
            "weight_jee": "25%"
        },
        "calculus": {
            "prerequisites": ["algebra"],
            "subtopics": ["limits", "derivatives", "integration", "differential equations"],
            "next": [],
            "weight_jee": "30%"
        },
        "coordinate_geometry": {
            "prerequisites": ["algebra"],
            "subtopics": ["straight lines", "circles", "conics"],
            "next": [],
            "weight_jee": "15%"
        },
        "trigonometry": {
            "prerequisites": [],
            "subtopics": ["ratios", "identities", "equations", "properties of triangles"],
            "next": ["calculus"],
            "weight_jee": "10%"
        }
    }
    
    @classmethod
    def get_path(cls, subject: str) -> Dict:
        """Get learning path for a subject"""
        paths = {
            "physics": cls.PHYSICS_PATH,
            "chemistry": cls.CHEMISTRY_PATH,
            "mathematics": cls.MATH_PATH,
            "math": cls.MATH_PATH
        }
        return paths.get(subject.lower(), {})


class ProactiveMentor:
    """
    Generates proactive suggestions and actions based on student context.
    """
    
    # Follow-up question templates
    FOLLOW_UP_TEMPLATES = {
        "deepen_understanding": [
            "Want to see a trickier version of this? 🎯",
            "Ready to test this concept with a JEE-style problem?",
            "Should I show you how toppers solve this faster?",
            "Curious about why this formula works the way it does?"
        ],
        "connect_topics": [
            "This connects beautifully to {related_topic} - want to see how?",
            "Fun fact: The same principle appears in {related_topic}!",
            "Once you master this, {next_topic} will make so much more sense!"
        ],
        "practice_offer": [
            "Ready for a quick practice problem? I'll give you hints if needed! 💪",
            "Want me to generate a MCQ to test this concept?",
            "Should we try a numerical to cement this understanding?"
        ],
        "revision_prompt": [
            "We covered {topic} 3 days ago - want a quick refresh?",
            "Your mastery of {topic} could use a boost - shall we revisit?",
            "Perfect time to revise {topic} - spaced repetition makes it stick!"
        ],
        "encouragement": [
            "You're on a roll today! 🔥",
            "Your understanding has grown so much in this session!",
            "This is exactly how toppers build concepts - one step at a time!"
        ]
    }
    
    # Exam strategy tips
    EXAM_STRATEGIES = {
        "time_management": [
            "⏰ Pro tip: In JEE, spend max 2 minutes per question. Can't crack it? Mark & move!",
            "📊 Strategy: Attempt easy questions first, then medium, then hard. Don't get stuck!",
            "🎯 In physics numericals, eliminate wrong options by dimensional analysis first."
        ],
        "common_traps": [
            "⚠️ Trap alert: Watch out for sign conventions in this type of problem!",
            "🚨 90% students mess up the direction of {concept} - always draw a diagram!",
            "💡 Secret: The 'obvious' answer is often wrong in JEE. Double-check your logic!"
        ],
        "shortcuts": [
            "⚡ Topper hack: This can be solved in 30 seconds using {shortcut}!",
            "🔑 Memorize this: {formula} - it appears in every exam!",
            "💫 Pattern recognition: If you see {pattern}, immediately think {approach}!"
        ]
    }
    
    def __init__(self, db=None):
        self.db = db
    
    async def get_proactive_suggestions(
        self,
        user_id: str,
        current_topic: str,
        subject: str,
        session_topics: List[str] = None,
        mastery_data: Dict[str, float] = None,
        time_in_session: int = 0  # minutes
    ) -> Dict[str, Any]:
        """
        Generate proactive suggestions based on learning context.
        """
        suggestions = {
            "follow_up_questions": [],
            "next_steps": [],
            "exam_tips": [],
            "celebration": None,
            "revision_alerts": [],
            "connected_topics": []
        }
        
        # 1. Generate contextual follow-ups
        follow_ups = self._generate_follow_ups(current_topic, subject, session_topics)
        suggestions["follow_up_questions"] = follow_ups
        
        # 2. Suggest next learning steps
        next_steps = self._suggest_next_steps(current_topic, subject, mastery_data)
        suggestions["next_steps"] = next_steps
        
        # 3. Get exam-relevant tips
        exam_tips = self._get_exam_tips(current_topic, subject)
        suggestions["exam_tips"] = exam_tips
        
        # 4. Check for celebration moments
        if session_topics and len(session_topics) >= 3:
            suggestions["celebration"] = self._generate_celebration(len(session_topics), time_in_session)
        
        # 5. Find connected topics
        connections = self._find_topic_connections(current_topic, subject)
        suggestions["connected_topics"] = connections
        
        return suggestions
    
    def _generate_follow_ups(
        self,
        topic: str,
        subject: str,
        session_topics: List[str] = None
    ) -> List[Dict[str, str]]:
        """Generate smart follow-up questions"""
        follow_ups = []
        
        # Deepen understanding
        deepen = random.choice(self.FOLLOW_UP_TEMPLATES["deepen_understanding"])
        follow_ups.append({
            "text": deepen,
            "type": "deepen",
            "action": "ask_harder_question"
        })
        
        # Practice offer
        practice = random.choice(self.FOLLOW_UP_TEMPLATES["practice_offer"])
        follow_ups.append({
            "text": practice,
            "type": "practice",
            "action": "generate_mcq"
        })
        
        # Topic connection (if we know the path)
        path = LearningPath.get_path(subject)
        for chapter, info in path.items():
            if topic.lower() in str(info.get("subtopics", [])).lower():
                if info.get("next"):
                    next_topic = info["next"][0]
                    connect_template = random.choice(self.FOLLOW_UP_TEMPLATES["connect_topics"])
                    connect = connect_template.format(
                        related_topic=next_topic,
                        next_topic=next_topic
                    )
                    follow_ups.append({
                        "text": connect,
                        "type": "connect",
                        "action": "show_connection"
                    })
                break
        
        return follow_ups[:3]  # Return top 3
    
    def _suggest_next_steps(
        self,
        current_topic: str,
        subject: str,
        mastery_data: Dict[str, float] = None
    ) -> List[Dict[str, Any]]:
        """Suggest logical next learning steps"""
        suggestions = []
        path = LearningPath.get_path(subject)
        
        # Find current position in path
        for chapter, info in path.items():
            subtopics = info.get("subtopics", [])
            for i, subtopic in enumerate(subtopics):
                if current_topic.lower() in subtopic.lower():
                    # Suggest next subtopic
                    if i + 1 < len(subtopics):
                        next_sub = subtopics[i + 1]
                        suggestions.append({
                            "topic": next_sub,
                            "reason": f"Natural progression from {current_topic}",
                            "difficulty": info.get("difficulty_ramp", [3])[min(i+1, len(info.get("difficulty_ramp", [3]))-1)] if info.get("difficulty_ramp") else 3,
                            "type": "next_in_sequence"
                        })
                    
                    # Suggest next chapter
                    if info.get("next"):
                        suggestions.append({
                            "topic": info["next"][0],
                            "reason": f"Once you master {chapter}, this builds on it",
                            "type": "next_chapter"
                        })
                    break
        
        # If mastery data available, suggest weak areas
        if mastery_data:
            weak_topics = [t for t, m in mastery_data.items() if m < 0.5]
            if weak_topics:
                suggestions.append({
                    "topic": weak_topics[0],
                    "reason": "This could use some revision 📚",
                    "type": "revision_needed"
                })
        
        return suggestions[:3]
    
    def _get_exam_tips(self, topic: str, subject: str) -> List[str]:
        """Get exam-relevant tips for the topic"""
        tips = []
        
        # Time management tip
        tips.append(random.choice(self.EXAM_STRATEGIES["time_management"]))
        
        # Common trap warning
        trap = random.choice(self.EXAM_STRATEGIES["common_traps"]).format(concept=topic)
        tips.append(trap)
        
        # Shortcut (if applicable)
        shortcut = random.choice(self.EXAM_STRATEGIES["shortcuts"]).format(
            shortcut="dimensional analysis",
            formula=f"key {topic} formula",
            pattern=f"{topic} problem",
            approach="standard method"
        )
        tips.append(shortcut)
        
        return tips[:2]  # Return top 2 tips
    
    def _generate_celebration(self, topics_covered: int, time_minutes: int) -> Dict[str, str]:
        """Generate celebration for learning milestones"""
        celebrations = [
            {"message": f"🎉 Amazing! You've covered {topics_covered} concepts in this session!", "type": "quantity"},
            {"message": f"🔥 {time_minutes} minutes of focused learning - that's how champions are made!", "type": "time"},
            {"message": "⭐ Your consistency is impressive! Keep building this momentum!", "type": "consistency"},
            {"message": "🏆 You're in the top 10% of students by daily learning time!", "type": "comparison"},
            {"message": "💪 Every concept you master is one step closer to your dream college!", "type": "motivation"}
        ]
        return random.choice(celebrations)
    
    def _find_topic_connections(self, topic: str, subject: str) -> List[Dict[str, str]]:
        """Find interesting connections to other topics"""
        # Cross-subject connections
        connections = {
            "force": ["energy (same chapter!)", "momentum (conservation laws)"],
            "newton": ["gravitation (same laws extended)", "circular motion (centripetal force)"],
            "derivative": ["physics motion equations", "chemistry rate of reactions"],
            "integration": ["area under curve", "physics work calculations"],
            "electron": ["chemistry bonding", "physics current"],
            "energy": ["thermodynamics (both subjects)", "work-energy theorem"],
            "waves": ["optics (light as wave)", "sound", "electromagnetic spectrum"],
            "thermodynamics": ["chemistry equilibrium", "physics ideal gas"]
        }
        
        topic_lower = topic.lower()
        for key, related in connections.items():
            if key in topic_lower:
                return [{"topic": r, "type": "cross_connection"} for r in related[:2]]
        
        return []


class SmartFollowUpGenerator:
    """
    Generates COMPACT, concept-specific follow-up suggestions.
    
    DESIGN PRINCIPLES:
    1. COMPACT: Max 5-7 words per suggestion (fits nicely in UI chips)
    2. CONCEPT-SPECIFIC: Include actual topic name
    3. PROGRESSIVE: Based on what was just explained
    4. NO GENERIC: Every suggestion must be contextual
    """
    
    @staticmethod
    def _extract_short_topic(question: str) -> str:
        """Extract SHORT topic name (1-3 words max)"""
        q = question.lower().strip()
        
        # Strip common prefixes
        prefixes = [
            "i want to understand what is", "i want to understand",
            "what is the meaning of", "what is", "what are",
            "define", "explain", "tell me about", "help me understand",
            "how does", "how do", "why is", "why does", "why do",
            "can you explain", "please explain", "solve", "calculate",
            "find the", "find", "derive", "prove", "show"
        ]
        
        for prefix in prefixes:
            if q.startswith(prefix):
                q = q[len(prefix):].strip()
                break
        
        # Remove trailing punctuation and fillers
        q = q.rstrip('?!.,')
        fillers = ['a', 'an', 'the', 'of', 'in', 'for', 'to', 'and', 'or', 'that', 'this']
        words = [w for w in q.split() if w not in fillers and len(w) > 1]
        
        # Take first 2-3 meaningful words only
        topic = ' '.join(words[:3]) if words else "this"
        return topic.strip()
    
    @staticmethod
    def _detect_response_type(response: str) -> str:
        """Detect what type of content was in the AI response"""
        if not response:
            return "general"
        r = response.lower()
        
        if any(s in r for s in ['step 1', 'step 2', '1.', '2.', 'first,', 'then,']):
            return "steps"
        if any(s in r for s in ['=', 'formula', '∫', 'Σ', '√']):
            return "formula"
        if any(s in r for s in ['example:', 'for example', 'e.g.', 'consider']):
            return "example"
        if any(s in r for s in ['vs', 'versus', 'difference', 'compare']):
            return "comparison"
        if any(s in r for s in ['diagram', 'visual', 'figure', 'draw']):
            return "visual"
        return "conceptual"
    
    @staticmethod
    def _detect_question_type(question: str) -> str:
        """Detect the type of question asked"""
        q = question.lower()
        
        if any(w in q for w in ['what is', 'define', 'meaning']):
            return "definition"
        if any(w in q for w in ['solve', 'calculate', 'find', 'evaluate']):
            return "calculation"
        if any(w in q for w in ['derive', 'prove', 'show that']):
            return "derivation"
        if any(w in q for w in ['compare', 'difference', 'vs']):
            return "comparison"
        if any(w in q for w in ['why', 'how does', 'explain why']):
            return "reasoning"
        if any(w in q for w in ['example', 'real life', 'application']):
            return "application"
        return "general"
    
    @staticmethod
    def generate(
        question: str,
        response: str,
        subject: str,
        topic: str = None,
        emotion: str = "neutral"
    ) -> List[Dict[str, str]]:
        """
        Generate 2-3 COMPACT follow-up suggestions.
        Each suggestion: 5-7 words max, concept-specific.
        """
        
        # Get short topic (1-3 words)
        t = topic or SmartFollowUpGenerator._extract_short_topic(question)
        q_type = SmartFollowUpGenerator._detect_question_type(question)
        r_type = SmartFollowUpGenerator._detect_response_type(response)
        
        follow_ups = []
        
        # =====================================================
        # PROGRESSIVE FOLLOW-UPS BY QUESTION TYPE
        # =====================================================
        
        if q_type == "definition":
            # Asked "what is X" → offer practice, mistakes, real use
            follow_ups = [
                {"text": f"Practice problem on {t}", "intent": "practice"},
                {"text": f"Common mistakes in {t}", "intent": "mistakes"},
                {"text": f"Real-life use of {t}", "intent": "application"}
            ]
        
        elif q_type == "calculation":
            # Solved a problem → offer similar or faster method
            follow_ups = [
                {"text": "Similar problem to practice", "intent": "practice"},
                {"text": "Faster method for this?", "intent": "shortcut"},
                {"text": f"JEE-level {t} problem", "intent": "challenge"}
            ]
        
        elif q_type == "derivation":
            # Derived something → offer application
            follow_ups = [
                {"text": "Where to apply this?", "intent": "application"},
                {"text": "Key steps to memorize", "intent": "memorize"},
                {"text": f"Exam question on {t}", "intent": "exam"}
            ]
        
        elif q_type == "comparison":
            # Compared two things → decision help
            follow_ups = [
                {"text": "When to use which?", "intent": "decision"},
                {"text": "Exam trick for this", "intent": "exam"},
                {"text": "Practice problem", "intent": "practice"}
            ]
        
        elif q_type == "reasoning":
            # Asked "why" → simpler or deeper
            follow_ups = [
                {"text": "Simpler analogy please", "intent": "simplify"},
                {"text": f"Related concepts to {t}", "intent": "related"},
                {"text": "Test my understanding", "intent": "test"}
            ]
        
        elif q_type == "application":
            # Asked for example → more or test
            follow_ups = [
                {"text": "Another example please", "intent": "more"},
                {"text": "Practice problem now", "intent": "practice"},
                {"text": f"Theory behind {t}", "intent": "theory"}
            ]
        
        else:
            # General → balanced
            follow_ups = [
                {"text": f"Practice {t}", "intent": "practice"},
                {"text": "Explain simpler please", "intent": "simplify"},
                {"text": "Exam patterns for this", "intent": "exam"}
            ]
        
        # =====================================================
        # ADJUST BY RESPONSE TYPE (what AI just explained)
        # =====================================================
        
        if r_type == "formula":
            follow_ups[0] = {"text": "When to use this formula?", "intent": "application"}
        
        if r_type == "steps":
            follow_ups[0] = {"text": "Let me try these steps", "intent": "practice"}
        
        if r_type == "comparison":
            follow_ups[0] = {"text": "Which one for exams?", "intent": "decision"}
        
        # =====================================================
        # EMOTION ADJUSTMENTS
        # =====================================================
        
        if emotion == "confused":
            follow_ups.insert(0, {"text": f"Simpler explanation of {t}", "intent": "simplify"})
            follow_ups = follow_ups[:3]
        
        if emotion == "frustrated":
            follow_ups.insert(0, {"text": "Easier problem first", "intent": "easier"})
            follow_ups = follow_ups[:3]
        
        # Return only 2-3 compact suggestions
        return follow_ups[:3]


# ============================================================================
# QUICK ACCESS FUNCTIONS
# ============================================================================

async def get_proactive_suggestions(
    db,
    user_id: str,
    topic: str,
    subject: str,
    session_topics: List[str] = None
) -> Dict[str, Any]:
    """Quick helper to get proactive suggestions"""
    mentor = ProactiveMentor(db)
    return await mentor.get_proactive_suggestions(
        user_id=user_id,
        current_topic=topic,
        subject=subject,
        session_topics=session_topics
    )


def generate_follow_ups(
    question: str, 
    response: str, 
    subject: str, 
    emotion: str = "neutral",
    intent: str = None
) -> List[Dict]:
    """
    Quick helper to generate follow-up questions.
    
    CRITICAL: Skip follow-ups for greetings and conversational messages!
    """
    # Skip follow-ups for non-educational intents
    skip_intents = ["greeting", "conversational"]
    if intent and intent in skip_intents:
        return []
    
    # Detect greeting/conversational from question itself if intent not provided
    q_lower = question.lower().strip()
    greeting_patterns = [
        'hi', 'hello', 'hey', 'namaste', 'hii', 'heya', 'yo', 'gm', 'gn',
        'good morning', 'good evening', 'good night', 'what\'s up', 'whats up',
        'how are you', 'how r u', 'wassup', 'sup'
    ]
    casual_patterns = [
        'thank', 'thanks', 'okay', 'ok', 'got it', 'understood', 'cool',
        'nice', 'great', 'awesome', 'perfect', 'super', 'yes', 'no', 'sure',
        'bye', 'goodbye', 'see you', 'take care', 'ttyl', 'can we study',
        'let\'s study', 'start preparation', 'help me study', 'study together',
        'getting boring', 'bored'
    ]
    
    # Clean question for pattern matching
    q_clean = q_lower.strip('!?.,')
    
    if q_clean in greeting_patterns or any(p in q_lower for p in casual_patterns):
        return []
    
    # Short messages that are conversational
    if len(question.split()) <= 2 and not any(c.isdigit() for c in question):
        # Very short messages are likely conversational unless they're topic names
        return []
    
    return SmartFollowUpGenerator.generate(
        question=question,
        response=response,
        subject=subject,
        emotion=emotion
    )




