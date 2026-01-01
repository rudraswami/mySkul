"""
Human Intelligence Layer (HIL) - The Brain Behind Human-Like AI Responses
==========================================================================
Makes the AI tutor behave like a real human mentor with:
- Emotional Intelligence (mood detection & adaptation)
- Adaptive Difficulty (auto-calibrate to student level)
- Socratic Teaching (guide through questions, not just answers)
- Personalized Encouragement (genuine, not generic)
- Learning Pattern Recognition (visual/auditory/kinesthetic)
- Exam Pattern Awareness (PYQ patterns, common mistakes)

Philosophy: "A great teacher doesn't just answer - they understand, adapt, and inspire."
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import random

logger = logging.getLogger(__name__)


# ============================================================================
# EMOTIONAL INTELLIGENCE LAYER
# ============================================================================

class EmotionalState(Enum):
    """Student emotional states - affects tone and approach"""
    CONFIDENT = "confident"       # "I know this!" → Challenge them
    CURIOUS = "curious"           # "How does this work?" → Explore together
    CONFUSED = "confused"         # "I don't get it" → Simplify & comfort
    FRUSTRATED = "frustrated"     # "This is impossible!" → Empathize first
    ANXIOUS = "anxious"           # "Exam tomorrow!" → Quick & reassuring
    BORED = "bored"               # "Okay whatever" → Make it exciting
    EXCITED = "excited"           # "This is cool!" → Match energy
    TIRED = "tired"               # Late night studying → Be concise
    NEUTRAL = "neutral"           # Default → Balanced approach


class MoodDetector:
    """
    Detects student's emotional state from their message.
    Affects: tone, depth, encouragement style, response structure.
    """
    
    EMOTION_PATTERNS = {
        EmotionalState.CONFUSED: [
            r"don'?t\s+(get|understand)", r"confused", r"unclear", r"what\s+do\s+you\s+mean",
            r"can'?t\s+figure", r"makes\s+no\s+sense", r"lost", r"help\s+me",
            r"samajh\s+nahi\s+aa", r"kya\s+matlab", r"pataa\s+nahi"  # Hinglish
        ],
        EmotionalState.FRUSTRATED: [
            r"impossible", r"hate\s+this", r"so\s+hard", r"give\s+up", r"ugh",
            r"argh", r"frustrated", r"stuck", r"can'?t\s+do", r"worst",
            r"bahut\s+mushkil", r"ho\s+nahi\s+raha", r"pagal"  # Hinglish
        ],
        EmotionalState.ANXIOUS: [
            r"exam\s+tomorrow", r"test\s+today", r"please\s+fast", r"urgent",
            r"quickly", r"running\s+out\s+of\s+time", r"scared", r"nervous",
            r"kal\s+exam", r"jaldi\s+batao", r"tension"  # Hinglish
        ],
        EmotionalState.CONFIDENT: [
            r"i\s+know\s+this", r"easy", r"simple", r"i\s+got\s+this",
            r"of\s+course", r"obviously", r"clear", r"understood",
            r"ye\s+toh\s+aasan", r"pata\s+hai"  # Hinglish
        ],
        EmotionalState.CURIOUS: [
            r"how\s+does", r"why\s+does", r"what\s+if", r"interesting",
            r"curious", r"wonder", r"want\s+to\s+know", r"fascinating",
            r"kaise\s+hota", r"kyun"  # Hinglish
        ],
        EmotionalState.EXCITED: [
            r"wow", r"amazing", r"cool", r"awesome", r"love\s+this",
            r"this\s+is\s+great", r"excited", r"!{2,}",
            r"mast", r"zabardast", r"badhiya"  # Hinglish
        ],
        EmotionalState.BORED: [
            r"whatever", r"okay\s+fine", r"boring", r"yawn", r"meh",
            r"i\s+guess", r"if\s+you\s+say\s+so", r"\.{3,}",
            r"theek\s+hai", r"chalo"  # Hinglish
        ],
        EmotionalState.TIRED: [
            r"late\s+night", r"so\s+tired", r"exhausted", r"sleepy",
            r"2\s*am", r"3\s*am", r"midnight", r"can'?t\s+focus",
            r"neend\s+aa\s+rahi", r"thak\s+gaya"  # Hinglish
        ]
    }
    
    @classmethod
    def detect(cls, message: str, time_of_day: str = None) -> Tuple[EmotionalState, float]:
        """
        Detect emotional state and confidence score.
        Returns: (EmotionalState, confidence 0.0-1.0)
        """
        message_lower = message.lower()
        
        # Check patterns
        for emotion, patterns in cls.EMOTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return (emotion, 0.85)
        
        # Time-based inference
        if time_of_day:
            hour = int(time_of_day.split(":")[0]) if ":" in time_of_day else 12
            if hour >= 23 or hour <= 4:
                return (EmotionalState.TIRED, 0.6)
        
        # Default
        return (EmotionalState.NEUTRAL, 0.5)
    
    @classmethod
    def get_tone_adjustment(cls, emotion: EmotionalState) -> Dict[str, Any]:
        """Get response tone adjustments based on emotion."""
        adjustments = {
            EmotionalState.CONFUSED: {
                "tone": "patient and reassuring",
                "complexity": "simplified",
                "examples": "multiple",
                "pace": "slow",
                "encouragement": "empathetic",
                "opener": "No worries, let me break this down for you step by step..."
            },
            EmotionalState.FRUSTRATED: {
                "tone": "calm and supportive",
                "complexity": "very simple",
                "examples": "relatable",
                "pace": "gentle",
                "encouragement": "acknowledge struggle first",
                "opener": "I completely understand the frustration - this topic trips up many students. Let's tackle it differently..."
            },
            EmotionalState.ANXIOUS: {
                "tone": "calm and efficient",
                "complexity": "exam-focused",
                "examples": "PYQ-focused",
                "pace": "quick and structured",
                "encouragement": "reassuring",
                "opener": "Deep breath! Let me give you exactly what you need for tomorrow..."
            },
            EmotionalState.CONFIDENT: {
                "tone": "challenging",
                "complexity": "advanced",
                "examples": "tricky edge cases",
                "pace": "fast",
                "encouragement": "push further",
                "opener": "Great that you've got the basics! Let me show you something that'll really test your understanding..."
            },
            EmotionalState.CURIOUS: {
                "tone": "exploratory and enthusiastic",
                "complexity": "deep dive",
                "examples": "fascinating applications",
                "pace": "engaging",
                "encouragement": "fuel curiosity",
                "opener": "Let me explain this — it's quite interesting..."
            },
            EmotionalState.EXCITED: {
                "tone": "equally enthusiastic",
                "complexity": "detailed with cool facts",
                "examples": "mind-blowing applications",
                "pace": "energetic",
                "encouragement": "match energy",
                "opener": "YES! I love this topic too! Let me show you why it's even cooler than you think..."
            },
            EmotionalState.BORED: {
                "tone": "engaging and surprising",
                "complexity": "start with wow factor",
                "examples": "unexpected real-world",
                "pace": "dynamic",
                "encouragement": "spark interest",
                "opener": "Here's something that might change your mind about this topic..."
            },
            EmotionalState.TIRED: {
                "tone": "concise and kind",
                "complexity": "essentials only",
                "examples": "quick memorable",
                "pace": "efficient",
                "encouragement": "acknowledge effort",
                "opener": "I'll keep this short and sweet since you're burning the midnight oil..."
            },
            EmotionalState.NEUTRAL: {
                "tone": "friendly and balanced",
                "complexity": "appropriate",
                "examples": "varied",
                "pace": "natural",
                "encouragement": "genuine",
                "opener": ""
            }
        }
        return adjustments.get(emotion, adjustments[EmotionalState.NEUTRAL])


# ============================================================================
# ADAPTIVE DIFFICULTY CALIBRATION
# ============================================================================

class DifficultyLevel(Enum):
    """Student mastery levels"""
    BEGINNER = "beginner"         # First time seeing concept
    DEVELOPING = "developing"     # Has basic understanding
    PROFICIENT = "proficient"     # Can solve standard problems
    ADVANCED = "advanced"         # Ready for competition level
    EXPERT = "expert"             # Can teach others


class DifficultyCalibrator:
    """
    Automatically calibrates explanation depth based on:
    - Student's past performance on topic
    - Question complexity signals
    - Explicit level indicators
    """
    
    BEGINNER_SIGNALS = [
        r"basic", r"simple", r"beginner", r"first\s+time", r"new\s+to",
        r"start\s+from\s+scratch", r"eli5", r"like\s+i'?m\s+5",
        r"naya\s+topic", r"shuruat"  # Hinglish
    ]
    
    ADVANCED_SIGNALS = [
        r"advanced", r"jee\s+advanced", r"olympiad", r"competition",
        r"tricky", r"edge\s+case", r"deep\s+dive", r"in\s+depth",
        r"derivation", r"proof", r"rigorous"
    ]
    
    @classmethod
    def calibrate(
        cls,
        question: str,
        student_mastery: Dict[str, float] = None,
        topic: str = None
    ) -> DifficultyLevel:
        """Determine appropriate difficulty level."""
        q_lower = question.lower()
        
        # Check explicit signals
        for pattern in cls.BEGINNER_SIGNALS:
            if re.search(pattern, q_lower):
                return DifficultyLevel.BEGINNER
        
        for pattern in cls.ADVANCED_SIGNALS:
            if re.search(pattern, q_lower):
                return DifficultyLevel.ADVANCED
        
        # Check student mastery on topic
        if student_mastery and topic:
            mastery = student_mastery.get(topic, 0.5)
            if mastery < 0.3:
                return DifficultyLevel.BEGINNER
            elif mastery < 0.5:
                return DifficultyLevel.DEVELOPING
            elif mastery < 0.7:
                return DifficultyLevel.PROFICIENT
            elif mastery < 0.9:
                return DifficultyLevel.ADVANCED
            else:
                return DifficultyLevel.EXPERT
        
        return DifficultyLevel.DEVELOPING  # Safe default
    
    @classmethod
    def get_depth_instructions(cls, level: DifficultyLevel) -> str:
        """Get prompt instructions for appropriate depth."""
        instructions = {
            DifficultyLevel.BEGINNER: """
DEPTH: BEGINNER LEVEL
- Start from absolute basics, assume no prior knowledge
- Use simple everyday language, avoid jargon
- One concept at a time, don't overwhelm
- Lots of simple analogies (cooking, sports, daily life)
- Step-by-step with tiny steps
- Celebrate small wins""",
            
            DifficultyLevel.DEVELOPING: """
DEPTH: DEVELOPING LEVEL
- Build on basic concepts they likely know
- Introduce terminology with clear definitions
- Connect to what they already understand
- Include one or two practice applications
- Gentle challenge questions""",
            
            DifficultyLevel.PROFICIENT: """
DEPTH: PROFICIENT LEVEL
- Focus on understanding WHY, not just HOW
- Include standard exam-type examples
- Point out common mistakes and traps
- Mention exam patterns and weightage
- Encourage them to try variations""",
            
            DifficultyLevel.ADVANCED: """
DEPTH: ADVANCED LEVEL
- Skip basics, go straight to insights
- Include JEE Advanced/Olympiad level thinking
- Discuss edge cases and exceptions
- Show connections to other topics
- Challenge with thought experiments
- Include competition-level tricks""",
            
            DifficultyLevel.EXPERT: """
DEPTH: EXPERT LEVEL
- Treat as peer discussion
- Focus on elegant solutions and proofs
- Discuss historical context and real research
- Explore open questions in the field
- Encourage them to find patterns and generalize"""
        }
        return instructions.get(level, instructions[DifficultyLevel.DEVELOPING])


# ============================================================================
# SOCRATIC TEACHING MODE
# ============================================================================

class SocraticTeacher:
    """
    Implements Socratic method - guide through questions, not just answers.
    Makes learning active, not passive.
    """
    
    SOCRATIC_QUESTION_TYPES = {
        "clarification": [
            "What do you mean by...?",
            "Can you give me an example?",
            "How would you explain this to a friend?"
        ],
        "probing_assumptions": [
            "What are you assuming here?",
            "Is that always true?",
            "What if we changed this condition?"
        ],
        "probing_reasoning": [
            "Why do you think that?",
            "How does this connect to what we discussed?",
            "What evidence supports this?"
        ],
        "exploring_implications": [
            "If this is true, what else must be true?",
            "What are the consequences of this?",
            "How does this affect real-world scenarios?"
        ],
        "questioning_viewpoints": [
            "Is there another way to look at this?",
            "What would someone who disagrees say?",
            "How might this be wrong?"
        ]
    }
    
    @classmethod
    def should_use_socratic(cls, question: str, emotion: EmotionalState) -> bool:
        """Determine if Socratic method is appropriate."""
        # Don't use when student is anxious or frustrated
        if emotion in {EmotionalState.ANXIOUS, EmotionalState.FRUSTRATED, EmotionalState.TIRED}:
            return False
        
        # Use for conceptual questions
        conceptual_signals = ["why", "how does", "explain", "what is", "concept"]
        q_lower = question.lower()
        
        return any(signal in q_lower for signal in conceptual_signals)
    
    @classmethod
    def generate_guided_questions(cls, topic: str, level: DifficultyLevel) -> List[str]:
        """Generate questions to guide student thinking."""
        questions = []
        
        if level == DifficultyLevel.BEGINNER:
            questions = [
                f"Before we dive in - what do you already know about {topic}?",
                f"Can you think of something in daily life that might work like {topic}?",
                "What's the first thing that comes to mind when you hear this term?"
            ]
        elif level in {DifficultyLevel.DEVELOPING, DifficultyLevel.PROFICIENT}:
            questions = [
                f"Why do you think {topic} works this way?",
                f"What would happen if we changed one condition in {topic}?",
                f"Can you predict what comes next in {topic}?"
            ]
        else:  # Advanced/Expert
            questions = [
                f"What's the most elegant way to think about {topic}?",
                f"Where might {topic} break down or have exceptions?",
                f"How does {topic} connect to other areas you've studied?"
            ]
        
        return questions[:2]  # Don't overwhelm
    
    @classmethod
    def get_socratic_prompt_addition(cls, topic: str, level: DifficultyLevel) -> str:
        """Get Socratic elements to add to prompt."""
        questions = cls.generate_guided_questions(topic, level)
        
        return f"""
SOCRATIC TEACHING MODE:
Instead of just giving the answer, guide the student's thinking:
1. Start with a thought-provoking question
2. Build understanding step by step
3. Let them "discover" insights
4. End with: "{random.choice(questions)}"

This makes learning stick better than passive reading!"""


# ============================================================================
# PERSONALIZED ENCOURAGEMENT ENGINE
# ============================================================================

class EncouragementEngine:
    """
    Generates genuine, personalized encouragement - not generic "You can do it!"
    Based on: context, progress, emotional state, and student history.
    """
    
    ENCOURAGEMENT_TEMPLATES = {
        "first_attempt": [
            "Starting a new topic takes courage - you're doing great just by asking!",
            "Every expert was once a beginner. This is your first step to mastery! 🚀",
            "The fact that you're asking shows you care about learning. That's already half the battle."
        ],
        "after_confusion": [
            "That 'click' you just felt? That's your brain building new connections. It gets easier from here!",
            "Confusion is a sign of learning - your brain is literally rewiring right now.",
            "The concepts that confuse us most often become our strongest areas. Keep going!"
        ],
        "streak_recognition": [
            "Day {days} of consistent learning! You're building something unstoppable. 🔥",
            "{days} days straight - that's not luck, that's dedication. Future you is grateful!",
            "Your consistency is impressive! Small daily progress = massive yearly growth."
        ],
        "topic_mastery": [
            "Look how far you've come with {topic}! Remember when this felt impossible?",
            "You've leveled up in {topic}! Time to flex those skills on harder problems.",
            "{topic} mastery unlocked! Your future self in the exam hall will thank you."
        ],
        "late_night_study": [
            "Burning the midnight oil for your dreams - that's real commitment. 🌙",
            "While others sleep, you're building your future. Just remember to rest too!",
            "Late night grind recognized. You're putting in the work that most won't."
        ],
        "after_struggle": [
            "You pushed through when it got tough. That's the real skill that matters in life.",
            "Most students quit when it gets hard. You didn't. That separates toppers from the rest.",
            "Struggle today = strength tomorrow. This hard work compounds, I promise."
        ],
        "exam_prep": [
            "You're preparing while others procrastinate. That's already an advantage!",
            "Every question you practice now is one less surprise in the exam.",
            "Exam stress is normal - but so is your ability to handle it. You've got this!"
        ]
    }
    
    @classmethod
    def generate(
        cls,
        context: str,
        emotion: EmotionalState,
        streak_days: int = 0,
        topic: str = None,
        is_late_night: bool = False
    ) -> str:
        """Generate contextual encouragement."""
        
        # Select appropriate template category
        if emotion == EmotionalState.CONFUSED:
            templates = cls.ENCOURAGEMENT_TEMPLATES["after_confusion"]
        elif emotion == EmotionalState.FRUSTRATED:
            templates = cls.ENCOURAGEMENT_TEMPLATES["after_struggle"]
        elif emotion == EmotionalState.ANXIOUS:
            templates = cls.ENCOURAGEMENT_TEMPLATES["exam_prep"]
        elif is_late_night:
            templates = cls.ENCOURAGEMENT_TEMPLATES["late_night_study"]
        elif streak_days >= 3:
            templates = cls.ENCOURAGEMENT_TEMPLATES["streak_recognition"]
        elif topic:
            templates = cls.ENCOURAGEMENT_TEMPLATES["topic_mastery"]
        else:
            templates = cls.ENCOURAGEMENT_TEMPLATES["first_attempt"]
        
        encouragement = random.choice(templates)
        
        # Fill in variables
        encouragement = encouragement.format(
            days=streak_days,
            topic=topic or "this concept"
        )
        
        return encouragement


# ============================================================================
# LEARNING PATTERN DETECTION
# ============================================================================

class LearningStyle(Enum):
    """Student learning preferences"""
    VISUAL = "visual"           # Prefers diagrams, charts, images
    AUDITORY = "auditory"       # Prefers step-by-step verbal explanations
    KINESTHETIC = "kinesthetic" # Prefers examples, practice, hands-on
    READING = "reading"         # Prefers detailed text explanations
    MIXED = "mixed"             # Uses all styles


class LearningPatternDetector:
    """
    Detects student's preferred learning style and adapts content delivery.
    """
    
    STYLE_SIGNALS = {
        LearningStyle.VISUAL: [
            r"show\s+me", r"diagram", r"picture", r"visualize", r"graph",
            r"draw", r"image", r"see", r"look\s+at", r"chart"
        ],
        LearningStyle.AUDITORY: [
            r"explain", r"tell\s+me", r"walk\s+me\s+through", r"step\s+by\s+step",
            r"describe", r"talk\s+about", r"sounds\s+like"
        ],
        LearningStyle.KINESTHETIC: [
            r"example", r"practice", r"try", r"hands-on", r"apply",
            r"use\s+case", r"real\s+life", r"exercise", r"problem"
        ],
        LearningStyle.READING: [
            r"detail", r"in-depth", r"comprehensive", r"thorough",
            r"full\s+explanation", r"everything\s+about"
        ]
    }
    
    @classmethod
    def detect(cls, question: str, history: List[str] = None) -> LearningStyle:
        """Detect preferred learning style."""
        q_lower = question.lower()
        
        scores = {style: 0 for style in LearningStyle}
        
        # Check current question
        for style, patterns in cls.STYLE_SIGNALS.items():
            for pattern in patterns:
                if re.search(pattern, q_lower):
                    scores[style] += 1
        
        # Check history if available
        if history:
            for past_q in history[-5:]:  # Last 5 questions
                for style, patterns in cls.STYLE_SIGNALS.items():
                    for pattern in patterns:
                        if re.search(pattern, past_q.lower()):
                            scores[style] += 0.5
        
        # Get highest scoring style
        max_score = max(scores.values())
        if max_score == 0:
            return LearningStyle.MIXED
        
        for style, score in scores.items():
            if score == max_score:
                return style
        
        return LearningStyle.MIXED
    
    @classmethod
    def get_style_adaptations(cls, style: LearningStyle) -> Dict[str, Any]:
        """Get content adaptations for learning style."""
        adaptations = {
            LearningStyle.VISUAL: {
                "include_diagram": True,
                "use_tables": True,
                "format": "visual-heavy",
                "prompt_hint": "Include ASCII diagrams, flowcharts, or describe visual representations"
            },
            LearningStyle.AUDITORY: {
                "include_diagram": False,
                "use_tables": False,
                "format": "conversational-steps",
                "prompt_hint": "Explain as if speaking aloud, use clear step-by-step narrative"
            },
            LearningStyle.KINESTHETIC: {
                "include_diagram": True,
                "use_tables": False,
                "format": "example-heavy",
                "prompt_hint": "Focus on practical examples, include practice problems, show real applications"
            },
            LearningStyle.READING: {
                "include_diagram": False,
                "use_tables": True,
                "format": "detailed-text",
                "prompt_hint": "Provide comprehensive written explanation with all details"
            },
            LearningStyle.MIXED: {
                "include_diagram": True,
                "use_tables": True,
                "format": "balanced",
                "prompt_hint": "Balance explanation, examples, and visual elements"
            }
        }
        return adaptations.get(style, adaptations[LearningStyle.MIXED])


# ============================================================================
# EXAM PATTERN AWARENESS
# ============================================================================

class ExamPatternAnalyzer:
    """
    Knows exam patterns, PYQ trends, common mistakes, and weightage.
    Makes responses exam-focused and strategic.
    """
    
    JEE_PATTERNS = {
        "physics": {
            "high_weightage": ["mechanics", "electromagnetism", "optics", "modern physics"],
            "common_mistakes": ["sign conventions", "direction of vectors", "unit conversion"],
            "pyq_tips": ["Numerical heavy - practice calculations", "Concepts from rotation often combined with other topics"]
        },
        "chemistry": {
            "high_weightage": ["organic reactions", "chemical bonding", "coordination compounds", "thermodynamics"],
            "common_mistakes": ["stereochemistry", "mechanism arrows", "oxidation states"],
            "pyq_tips": ["Memory-based in inorganic - make charts", "Organic reactions repeat - know 20 key reactions"]
        },
        "mathematics": {
            "high_weightage": ["calculus", "coordinate geometry", "algebra", "probability"],
            "common_mistakes": ["domain restrictions", "missing cases", "calculation errors"],
            "pyq_tips": ["Integration techniques repeat - master all methods", "Matrix questions often have elegant shortcuts"]
        }
    }
    
    @classmethod
    def get_exam_insights(cls, subject: str, topic: str = None) -> Dict[str, Any]:
        """Get exam-specific insights for a topic."""
        subject_lower = subject.lower()
        
        patterns = cls.JEE_PATTERNS.get(subject_lower, {})
        
        insights = {
            "is_high_weightage": topic and any(topic.lower() in hw.lower() for hw in patterns.get("high_weightage", [])),
            "common_mistakes": patterns.get("common_mistakes", []),
            "pyq_tips": patterns.get("pyq_tips", []),
            "exam_advice": cls._generate_exam_advice(subject_lower, topic)
        }
        
        return insights
    
    @classmethod
    def _generate_exam_advice(cls, subject: str, topic: str = None) -> str:
        """Generate specific exam advice."""
        advice_templates = [
            f"📝 **Exam Tip**: This concept has appeared in JEE Main 3 times in the last 5 years. Master it!",
            f"⚠️ **Common Trap**: Many students lose marks here due to silly mistakes. Double-check your {subject} fundamentals.",
            f"🎯 **Strategy**: In exams, start with concepts you're confident about. Come back to tricky ones.",
            f"💡 **Topper Hack**: Convert this to a mental formula - it saves 30 seconds per question in exams."
        ]
        return random.choice(advice_templates)


# ============================================================================
# MAIN HUMAN INTELLIGENCE LAYER (ORCHESTRATOR)
# ============================================================================

class HumanIntelligenceLayer:
    """
    Orchestrates all human-like AI capabilities.
    Single entry point for making AI responses feel human.
    """
    
    def __init__(self, db=None):
        self.db = db
        self.mood_detector = MoodDetector()
        self.difficulty_calibrator = DifficultyCalibrator()
        self.socratic_teacher = SocraticTeacher()
        self.encouragement_engine = EncouragementEngine()
        self.learning_detector = LearningPatternDetector()
        self.exam_analyzer = ExamPatternAnalyzer()
    
    async def analyze_student_context(
        self,
        user_id: str,
        question: str,
        subject: str = None,
        session_history: List[Dict] = None,
        time_of_day: str = None
    ) -> Dict[str, Any]:
        """
        Complete analysis of student context.
        Returns everything needed to generate a human-like response.
        """
        # Detect emotional state
        emotion, emotion_confidence = self.mood_detector.detect(question, time_of_day)
        tone_adjustment = self.mood_detector.get_tone_adjustment(emotion)
        
        # Get student mastery (if db available)
        student_mastery = {}
        streak_days = 0
        if self.db is not None and user_id:
            try:
                user_doc = await self.db.users.find_one({"user_id": user_id})
                if user_doc:
                    student_mastery = user_doc.get("topic_mastery", {})
                    streak_days = user_doc.get("streak_days", 0)
            except Exception:
                pass
        
        # Calibrate difficulty
        topic = self._extract_topic(question, subject)
        difficulty = self.difficulty_calibrator.calibrate(question, student_mastery, topic)
        depth_instructions = self.difficulty_calibrator.get_depth_instructions(difficulty)
        
        # Detect learning style
        history_questions = [h.get("question", "") for h in (session_history or []) if h.get("type") == "user"]
        learning_style = self.learning_detector.detect(question, history_questions)
        style_adaptations = self.learning_detector.get_style_adaptations(learning_style)
        
        # Check Socratic mode
        use_socratic = self.socratic_teacher.should_use_socratic(question, emotion)
        socratic_addition = ""
        if use_socratic:
            socratic_addition = self.socratic_teacher.get_socratic_prompt_addition(topic, difficulty)
        
        # Get exam insights
        exam_insights = self.exam_analyzer.get_exam_insights(subject or "general", topic)
        
        # Generate encouragement
        is_late = time_of_day and int(time_of_day.split(":")[0]) in range(23, 24) or int(time_of_day.split(":")[0]) in range(0, 5) if time_of_day else False
        encouragement = self.encouragement_engine.generate(
            context="general",
            emotion=emotion,
            streak_days=streak_days,
            topic=topic,
            is_late_night=is_late
        )
        
        return {
            # Emotional Intelligence
            "emotion": emotion.value,
            "emotion_confidence": emotion_confidence,
            "tone_adjustment": tone_adjustment,
            
            # Difficulty Calibration
            "difficulty_level": difficulty.value,
            "depth_instructions": depth_instructions,
            "student_mastery": student_mastery,
            
            # Learning Style
            "learning_style": learning_style.value,
            "style_adaptations": style_adaptations,
            
            # Socratic Teaching
            "use_socratic": use_socratic,
            "socratic_addition": socratic_addition,
            
            # Exam Awareness
            "exam_insights": exam_insights,
            
            # Encouragement
            "encouragement": encouragement,
            "streak_days": streak_days,
            
            # Topic
            "detected_topic": topic
        }
    
    def _extract_topic(self, question: str, subject: str = None) -> str:
        """Extract main topic from question."""
        # Simple extraction - can be enhanced with NLP
        q_lower = question.lower()
        
        topic_patterns = {
            "newton": "Newton's Laws",
            "gravity": "Gravitation",
            "force": "Forces",
            "motion": "Motion",
            "energy": "Energy",
            "momentum": "Momentum",
            "wave": "Waves",
            "light": "Optics",
            "electricity": "Electricity",
            "magnet": "Magnetism",
            "atom": "Atomic Structure",
            "bond": "Chemical Bonding",
            "organic": "Organic Chemistry",
            "reaction": "Chemical Reactions",
            "calculus": "Calculus",
            "derivative": "Derivatives",
            "integral": "Integration",
            "matrix": "Matrices",
            "probability": "Probability",
            "geometry": "Geometry",
            "cell": "Cell Biology",
            "dna": "Genetics",
            "evolution": "Evolution",
        }
        
        for pattern, topic in topic_patterns.items():
            if pattern in q_lower:
                return topic
        
        return subject or "General"
    
    def build_enhanced_prompt(self, base_prompt: str, context: Dict[str, Any]) -> str:
        """
        Enhance base prompt with human intelligence insights.
        """
        enhancements = []
        
        # Add tone adjustment
        tone = context.get("tone_adjustment", {})
        if tone.get("opener"):
            enhancements.append(f"START WITH: {tone['opener']}")
        enhancements.append(f"TONE: {tone.get('tone', 'friendly')}")
        
        # Add depth instructions
        enhancements.append(context.get("depth_instructions", ""))
        
        # Add learning style hint
        style = context.get("style_adaptations", {})
        if style.get("prompt_hint"):
            enhancements.append(f"CONTENT STYLE: {style['prompt_hint']}")
        
        # Add Socratic elements
        if context.get("use_socratic"):
            enhancements.append(context.get("socratic_addition", ""))
        
        # Add exam insights
        exam = context.get("exam_insights", {})
        if exam.get("common_mistakes"):
            enhancements.append(f"MENTION COMMON MISTAKES: {', '.join(exam['common_mistakes'][:2])}")
        if exam.get("exam_advice"):
            enhancements.append(f"INCLUDE: {exam['exam_advice']}")
        
        # Add encouragement instruction
        enhancements.append(f"END WITH ENCOURAGEMENT: {context.get('encouragement', '')}")
        
        # Combine
        enhancement_block = "\n".join([e for e in enhancements if e.strip()])
        
        return f"""{base_prompt}

=== HUMAN INTELLIGENCE LAYER ENHANCEMENTS ===
{enhancement_block}
=== END ENHANCEMENTS ===""" 


# ============================================================================
# QUICK USAGE EXAMPLE
# ============================================================================

async def get_human_context(db, user_id: str, question: str, subject: str = None) -> Dict[str, Any]:
    """
    Quick helper to get human intelligence context.
    Use this in your response_composer.py
    """
    hil = HumanIntelligenceLayer(db)
    return await hil.analyze_student_context(
        user_id=user_id,
        question=question,
        subject=subject,
        time_of_day=datetime.now().strftime("%H:%M")
    )


