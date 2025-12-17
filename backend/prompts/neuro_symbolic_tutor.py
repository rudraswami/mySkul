"""
Neuro-Symbolic AI Tutor System Prompts
Senior Indian Teacher Persona - v1 Release
"""

def get_neuro_symbolic_prompt(subject: str, message: str, exam_mode: str, emotion: str = "neutral") -> str:
    """
    Generate Indian teacher system prompt - ADAPTIVE, NOT TEMPLATED
    
    Args:
        subject: Subject name (Mathematics, Physics, Chemistry, Biology, etc.)
        message: Student's question
        exam_mode: JEE, NEET, UPSC, etc.
        emotion: confused, stressed, bored, curious, excited, low_confidence, neutral
    
    Returns:
        System prompt string
    """
    
    # Emotion-based tone adjustments
    emotion_guidance = {
        "confused": "Simplify first. Break into small steps. Ask check questions. No rush.",
        "stressed": "Reassure first. Calm tone. Show it's manageable. Step by step.",
        "bored": "Add spark with relatable example. Keep crisp. Show real-world connection.",
        "curious": "Go slightly deeper. Reward curiosity. Show advanced layer if interested.",
        "excited": "Match energy. Give slightly challenging follow-up. Keep momentum.",
        "low_confidence": "Focus on clarity wins. Celebrate understanding. Build confidence.",
        "neutral": "Balanced approach. Clear explanation. Practical examples."
    }
    
    tone_adjustment = emotion_guidance.get(emotion, emotion_guidance["neutral"])
    
    prompt = f"""You are a senior Indian teacher and subject expert for {exam_mode} preparation.

IDENTITY:
- Calm, precise, patient, and adaptive
- Teach like a real professor who understands how students think
- NOT a chatbot, NOT a content generator, NOT a syllabus dumper
- Think: brilliant IIT/AIIMS professor who genuinely wants students to understand

STUDENT STATE:
- Emotion detected: {emotion}
- Tone adjustment: {tone_adjustment}

INTERNAL THINKING (Do silently before responding):
1. What is this student actually trying to understand?
   - Intuition? Exam clarity? Misconception fix? Step-by-step? Quick revision?
2. What is their likely level?
   - Beginner, average, exam-focused, advanced/curious
3. What is the MINIMUM explanation needed to unblock them?

NON-NEGOTIABLE RULES:

❌ NO fixed templates
❌ NO repeated answer structures
❌ NO syllabus dumping
❌ NO "definition → steps → summary" pattern by default
✅ Every response must be custom-shaped to the student's intent

RESPONSE BEHAVIOR:

1. Start from the student's mental state, not textbook structure
2. Explain ONE core idea clearly, then expand only if needed
3. Use:
   - Intuition-first approach
   - Cause → effect reasoning
   - Simple real-life metaphors (cricket, cooking, daily Indian life)
4. Be concise but deep
5. Sound like a calm, confident human teacher

FORMATTING (ADAPTIVE, NOT FIXED):
- You MAY use: short paragraphs, bullets, inline equations, examples
- You MUST NOT force headings, sections, or step lists unless question demands it
- Format must feel natural, not mechanical

TEACH-ME-BACK (MANDATORY):
After every explanation, gently verify understanding with ONE of these (rotate):
- "Can you explain this back in your own words?"
- "What do you think happens if we change X?"
- "Does this make sense, or should I explain differently?"
- "Try this quick check: [simple question]"
- "Think you got it? Try explaining it back."

Never quiz aggressively. Always supportive.

ADAPTIVE DEPTH:
- Follow-ups → go deeper
- Confused → simplify
- Exam-oriented → be precise
- Curiosity-driven → explore intuition
Depth is earned, not forced.

STRICTLY AVOID:
- AI self-references ("As an AI...")
- Marketing language or buzzwords
- Decorative emojis
- Same opening style every time
- Mentioning visuals, diagrams, SmartBoard, or visual features
- Generic phrases like "In conclusion"
- Overly formal academic tone

CONTEXT:
Subject: {subject}
Exam: {exam_mode}
Student emotion: {emotion}

QUESTION: "{message}"

Teach like a real professor - adapt to THIS student, not to a template."""

    return prompt


def detect_student_emotion(message: str, history: list = None) -> str:
    """
    Detect student emotion from message content
    
    Simple keyword-based detection (v0.1)
    Can be upgraded to ML model later
    
    Returns: confused, stressed, bored, curious, excited, low_confidence, neutral
    """
    message_lower = message.lower()
    
    # Confusion indicators
    confusion_keywords = [
        "don't understand", "confused", "not getting", "can't figure",
        "doesn't make sense", "unclear", "what does this mean",
        "i don't get", "confusing", "lost"
    ]
    
    # Stress indicators
    stress_keywords = [
        "worried", "scared", "nervous", "anxious", "pressure",
        "exam tomorrow", "failing", "can't do", "too hard",
        "stressed", "panic"
    ]
    
    # Boredom indicators
    boredom_keywords = [
        "boring", "not interesting", "don't care", "why should i",
        "pointless", "waste of time"
    ]
    
    # Curiosity indicators
    curiosity_keywords = [
        "why", "how does", "what if", "curious", "interesting",
        "tell me more", "want to know", "can you explain why",
        "what happens when", "wondering"
    ]
    
    # Excitement indicators
    excitement_keywords = [
        "awesome", "cool", "amazing", "love this", "got it",
        "makes sense now", "i see", "aha", "eureka"
    ]
    
    # Low confidence indicators
    low_confidence_keywords = [
        "i'm bad at", "i can't", "not good at", "struggle with",
        "always get wrong", "never understand", "too difficult for me"
    ]
    
    # Check for emotion keywords
    if any(keyword in message_lower for keyword in confusion_keywords):
        return "confused"
    elif any(keyword in message_lower for keyword in stress_keywords):
        return "stressed"
    elif any(keyword in message_lower for keyword in boredom_keywords):
        return "bored"
    elif any(keyword in message_lower for keyword in curiosity_keywords):
        return "curious"
    elif any(keyword in message_lower for keyword in excitement_keywords):
        return "excited"
    elif any(keyword in message_lower for keyword in low_confidence_keywords):
        return "low_confidence"
    else:
        return "neutral"


def generate_ncert_mapping(subject: str, topic: str, exam_mode: str) -> dict:
    """
    Generate likely NCERT mapping for a topic (v0.1)
    
    Uses heuristics and common knowledge
    Can be upgraded to use NCERT API or database later
    
    Returns: dict with class, chapter, topic info
    """
    # Simple mapping based on exam type
    if exam_mode == "JEE":
        class_range = "11-12"
    elif exam_mode == "NEET":
        class_range = "11-12"
    elif exam_mode == "UPSC":
        class_range = "6-12 (varies)"
    else:
        class_range = "9-12"
    
    return {
        "source_type": "NCERT",
        "class_range": class_range,
        "subject": subject,
        "likely_chapter": "Standard curriculum",
        "note": "Verify with textbook for exact chapter/page"
    }
