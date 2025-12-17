"""
Dynamic Mentor Prompt System v2.0
================================
Creates well-structured, readable responses with proper markdown formatting
while maintaining a friendly, engaging tone.

CRITICAL: All responses MUST use proper markdown for readability.
"""
import logging
import random
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


# =============================================================================
# 📝 MANDATORY FORMATTING RULES (Applied to ALL prompt styles)
# =============================================================================
FORMATTING_RULES = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 FORMATTING GUIDELINES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**USE THESE:**
- **Bold** for key terms: "**Force** is a push or pull"
- Bullets (-) when listing genuinely separate points
- \\( inline math \\) and \\[ block math \\] for formulas
- > for important callouts
- ## Header only when starting a major new topic

**AVOID THESE TEMPLATE HEADERS:**
- ❌ "Key Characteristics" 
- ❌ "Key Points"
- ❌ "Additional Details"
- ❌ "In Simple Words"
- ❌ "Quick Example"
- ❌ "The Core Idea"
- ❌ Any header that would appear in EVERY response

**FLOW NATURALLY:**
- Write like you're explaining to a friend
- Use headers only when they genuinely help organize
- Don't force sections - if the answer is simple, keep it simple
- Don't pad responses with generic structure

**COMPLETE YOUR RESPONSE:**
- Always finish your explanation
- Don't leave formulas or sentences incomplete
- If space is limited, prioritize clarity over coverage
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


def get_dynamic_mentor_prompt(
    query: str,
    subject: str,
    student_profile: Dict[str, Any],
    memory_context: Dict[str, Any] = None,
    user_id: str = "anonymous"
) -> str:
    """
    Generate a well-formatted mentor prompt.
    All responses use proper markdown for readability.
    """
    return DynamicMentorPrompts.get_varied_prompt(
        query=query,
        subject=subject,
        student_profile=student_profile,
        memory_context=memory_context,
        user_id=user_id
    )


class DynamicMentorPrompts:
    """Generates structured, readable mentor prompts with proper formatting"""
    
    # Track recent styles to add variety
    _recent_styles: Dict[str, List[str]] = {}
    
    @staticmethod
    def get_varied_prompt(
        query: str,
        subject: str,
        student_profile: Dict[str, Any],
        memory_context: Dict[str, Any] = None,
        user_id: str = "anonymous"
    ) -> str:
        """Generate a structured, readable mentor prompt"""
        
        # Select appropriate style based on query
        prompt_style = DynamicMentorPrompts._select_prompt_style(user_id, query, student_profile)
        
        # Build prompt with formatting rules
        prompt_builders = {
            "conceptual": DynamicMentorPrompts._build_conceptual,
            "problem_solving": DynamicMentorPrompts._build_problem_solving,
            "comparison": DynamicMentorPrompts._build_comparison,
            "definition": DynamicMentorPrompts._build_definition,
            "exam_focused": DynamicMentorPrompts._build_exam_focused,
            "intuitive": DynamicMentorPrompts._build_intuitive,
            "step_by_step": DynamicMentorPrompts._build_step_by_step,
            "application": DynamicMentorPrompts._build_application,
        }
        
        builder = prompt_builders.get(prompt_style, DynamicMentorPrompts._build_conceptual)
        
        prompt = builder(
            query=query,
            subject=subject,
            student_profile=student_profile,
            memory_context=memory_context
        )
        
        logger.info(f"🎭 Using structured prompt style: {prompt_style}")
        
        return prompt
    
    @staticmethod
    def _select_prompt_style(user_id: str, query: str, student_profile: Dict[str, Any]) -> str:
        """Select appropriate prompt style based on query type"""
        query_lower = query.lower()
        
        # Problem/calculation
        if any(w in query_lower for w in ['solve', 'calculate', 'find', 'compute', 'evaluate']):
            return 'problem_solving'
        
        # Comparison
        if any(w in query_lower for w in ['difference', 'compare', 'vs', 'versus', 'distinguish']):
            return 'comparison'
        
        # Definition
        if any(w in query_lower for w in ['what is', 'what are', 'define', 'meaning']):
            return 'definition'
        
        # Process/steps
        if any(w in query_lower for w in ['how to', 'steps', 'process', 'procedure']):
            return 'step_by_step'
        
        # Exam focus
        if any(w in query_lower for w in ['exam', 'test', 'important', 'marks']):
            return 'exam_focused'
        
        # Why/explanation
        if any(w in query_lower for w in ['why', 'explain', 'how does', 'reason']):
            return 'conceptual'
        
        # Application
        if any(w in query_lower for w in ['example', 'application', 'real life', 'use']):
            return 'application'
        
        # Default: conceptual explanation
        return 'conceptual'
    
    # ========== PROMPT BUILDERS (All with formatting rules) ==========
    
    @staticmethod
    def _build_conceptual(**kwargs) -> str:
        """Conceptual explanation - CONVERSATIONAL, not template"""
        query = kwargs['query']
        subject = kwargs['subject']
        student_profile = kwargs['student_profile']
        
        name = student_profile.get('name', 'student')
        interests = student_profile.get('interests', ['cricket', 'daily life'])
        
        return f"""You are an expert {subject} teacher helping {name} understand a concept.

**Question:** {query}

{FORMATTING_RULES}

**RESPONSE GUIDELINES:**

1. **NO RIGID TEMPLATES** - Don't use fixed section headers like "The Core Idea", "How It Works", etc.
2. **FLOW NATURALLY** - Structure your response based on what the student actually needs
3. **BE CONVERSATIONAL** - Explain like you're talking to a friend who's curious
4. **USE HEADERS MEANINGFULLY** - Only use ## headers if they help clarity, not as mandatory sections
5. **ADAPT TO THE QUESTION** - A "what is force" needs different structure than "why does friction occur"

**WHAT TO INCLUDE (as needed, not as template):**
- Clear definition using **bold** for key terms
- Simple explanation that builds understanding
- Formula with \\[ LaTeX \\] if relevant
- A relatable example from {interests[0]} or daily life
- > Important callout for key points

**DON'T:**
- Force all sections if they don't fit
- Use generic headers like "Key Characteristics" on every response
- Create walls of bullet points
- Sound like a textbook

Explain naturally, like a great teacher would.

> **Key Takeaway:** One sentence summary.

**TONE:** Friendly like a senior friend explaining, but ALWAYS structured and readable.
**LENGTH:** 200-300 words, well-organized."""
    
    @staticmethod
    def _build_definition(**kwargs) -> str:
        """Clear definition - CONVERSATIONAL style"""
        query = kwargs['query']
        subject = kwargs['subject']
        student_profile = kwargs['student_profile']
        interests = student_profile.get('interests', ['cricket', 'daily life'])
        
        return f"""You are explaining a {subject} concept clearly.

**Question:** {query}

{FORMATTING_RULES}

**RESPONSE GUIDELINES:**

1. Start with a **concise definition** using bold for the key term
2. Immediately follow with a simple explanation or analogy
3. Add 2-3 bullet points ONLY if they add real value (not just to fill space)
4. Include formula with \\[ LaTeX \\] only if it's essential to the concept
5. End with a memorable insight or {interests[0]}-related example

**DON'T USE THESE TEMPLATE HEADERS:**
- ❌ "Key Points" 
- ❌ "Key Characteristics"
- ❌ "Quick Example"
- ❌ "In Simple Words"

**DO THIS INSTEAD:**
Write naturally. If you're explaining "What is Force", just say:

**Force** is a push or pull that can change an object's motion.

Think about it: When you push a door open, that's force in action. When Dhoni hits a six, his bat applies force to the ball.

The stronger the force, the bigger the effect. Newton figured this out:

\\[ F = ma \\]

> **Key insight:** Everything that moves or stops moving does so because of force.

**TONE:** Helpful friend explaining, not textbook reciting.
**LENGTH:** 100-150 words - crisp and clear."""
    
    @staticmethod
    def _build_problem_solving(**kwargs) -> str:
        """Step-by-step problem solving"""
        query = kwargs['query']
        subject = kwargs['subject']
        
        return f"""You are solving a {subject} problem step-by-step.

**Question:** {query}

{FORMATTING_RULES}

**YOUR RESPONSE STRUCTURE:**

## Solution

**Given:**
- Known value 1
- Known value 2

**To Find:** What we need to calculate

**Formula:**
\\[ Required formula \\]

**Solution:**

1. **Step 1:** Explanation and calculation
2. **Step 2:** Continue solving
3. **Step 3:** Final calculation

**Answer:** \\( result \\) with units

> **Quick Check:** How to verify your answer is correct.

**TONE:** Clear, methodical, exam-ready.
**LENGTH:** Complete solution, properly formatted."""
    
    @staticmethod
    def _build_comparison(**kwargs) -> str:
        """Comparison with table"""
        query = kwargs['query']
        subject = kwargs['subject']
        
        return f"""You are comparing two {subject} concepts.

**Question:** {query}

{FORMATTING_RULES}

**YOUR RESPONSE STRUCTURE:**

## [Concept A] vs [Concept B]

| Aspect | [A] | [B] |
|--------|-----|-----|
| Definition | ... | ... |
| Key Feature | ... | ... |
| Formula | ... | ... |
| Example | ... | ... |
| Application | ... | ... |

### Key Differences

1. **Main Difference:** Explain
2. **Important Distinction:** Explain

### When to Use Which

- Use **[A]** when...
- Use **[B]** when...

> **Exam Tip:** What examiners often ask about these.

**TONE:** Clear comparison, easy to memorize.
**LENGTH:** Complete comparison with all key aspects."""
    
    @staticmethod
    def _build_exam_focused(**kwargs) -> str:
        """Exam-focused quick explanation"""
        query = kwargs['query']
        subject = kwargs['subject']
        student_profile = kwargs['student_profile']
        
        exam = student_profile.get('exam', 'exam')
        
        return f"""You are giving a focused {exam} preparation explanation.

**Question:** {query}

{FORMATTING_RULES}

**YOUR RESPONSE STRUCTURE:**

## {subject}: Exam Quick Guide

### What Examiners Ask

- Common question type 1
- Common question type 2

### Key Points to Remember

1. **Point 1:** Must remember
2. **Point 2:** Must remember
3. **Point 3:** Must remember

### Important Formula(s)

\\[ Key formula \\]

### Common Mistakes to Avoid

- ❌ Wrong approach
- ✅ Correct approach

### Quick Memory Trick

A mnemonic or simple way to remember.

> **Marks Alert:** What gets you full marks.

**TONE:** Quick, focused, exam-ready.
**LENGTH:** 150-250 words, high-value content."""
    
    @staticmethod
    def _build_step_by_step(**kwargs) -> str:
        """Process or procedure explanation"""
        query = kwargs['query']
        subject = kwargs['subject']
        
        return f"""You are explaining a {subject} process step-by-step.

**Question:** {query}

{FORMATTING_RULES}

**YOUR RESPONSE STRUCTURE:**

## How [Process Name] Works

### Overview

Brief 1-2 sentence explanation of what this process achieves.

### Step-by-Step Process

1. **Step 1: [Name]**
   - What happens
   - Why it matters

2. **Step 2: [Name]**
   - What happens
   - Why it matters

3. **Step 3: [Name]**
   - What happens
   - Result

### Visual Understanding

Describe what you would see if you could watch this happen.

> **Key Insight:** The most important thing to understand about this process.

**TONE:** Clear progression, easy to follow.
**LENGTH:** 200-300 words."""
    
    @staticmethod
    def _build_intuitive(**kwargs) -> str:
        """Intuitive understanding with analogy"""
        query = kwargs['query']
        subject = kwargs['subject']
        student_profile = kwargs['student_profile']
        
        interests = student_profile.get('interests', ['cricket', 'daily life'])
        
        return f"""You are building intuitive understanding of {subject}.

**Question:** {query}

{FORMATTING_RULES}

**YOUR RESPONSE STRUCTURE:**

## Understanding [Concept]

### The Simple Idea

One clear sentence explaining the core concept.

### Think of It Like This

Use a relatable analogy from {interests[0]} or daily life.

**The Analogy:**
- In real life: [everyday example]
- In {subject}: [how concept works similarly]

### Why It Makes Sense

Explain the "aha!" moment - why this concept exists.

### The Technical Version

Now the formal definition/formula:
\\[ Formula if applicable \\]

> **Connection:** How the intuition connects to the formula/theory.

**TONE:** Build understanding before formality.
**LENGTH:** 200-250 words."""
    
    @staticmethod
    def _build_application(**kwargs) -> str:
        """Real-world application focus"""
        query = kwargs['query']
        subject = kwargs['subject']
        student_profile = kwargs['student_profile']
        
        region = student_profile.get('region', 'India')
        
        return f"""You are showing real-world applications of {subject}.

**Question:** {query}

{FORMATTING_RULES}

**YOUR RESPONSE STRUCTURE:**

## [Concept] in the Real World

### What Is It?

Brief definition (1-2 sentences).

### Real-World Applications

1. **In Daily Life:**
   How you encounter this in {region} daily life.

2. **In Technology:**
   How modern technology uses this.

3. **In Nature:**
   Where you see this in the natural world.

### Practical Example

A specific, detailed example with numbers if applicable.

**Situation:** [Setup]
**Application:** [How concept applies]
**Result:** [What happens]

> **Fun Fact:** An interesting application most students don't know.

**TONE:** Make it real and relatable.
**LENGTH:** 200-300 words."""


# Backwards compatibility
def get_formatted_prompt(query: str, subject: str, **kwargs) -> str:
    """Alias for get_dynamic_mentor_prompt"""
    return get_dynamic_mentor_prompt(query, subject, kwargs.get('student_profile', {}))
