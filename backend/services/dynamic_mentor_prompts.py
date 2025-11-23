"""
Dynamic Mentor Prompt System
Creates varied, natural prompts that feel like conversations, not structured lessons
Student perspective: "This feels like a friend explaining, not a robot"
"""
import logging
import random
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DynamicMentorPrompts:
    """Generates varied mentor prompts that feel human and conversational"""
    
    # Track recent prompt styles per user to avoid repetition
    _recent_styles: Dict[str, List[str]] = {}
    
    @staticmethod
    def get_varied_prompt(
        query: str,
        subject: str,
        student_profile: Dict[str, Any],
        memory_context: Dict[str, Any] = None,
        user_id: str = "anonymous"
    ) -> str:
        """
        Generate a varied, conversational mentor prompt
        Feels like a friend explaining, not a structured lesson
        """
        # Select prompt style (avoiding repetition)
        prompt_style = DynamicMentorPrompts._select_prompt_style(user_id, query, student_profile)
        
        # Build prompt based on style
        prompt_builders = {
            "excited_discovery": DynamicMentorPrompts._build_excited_discovery,
            "calm_walkthrough": DynamicMentorPrompts._build_calm_walkthrough,
            "questioning_socratic": DynamicMentorPrompts._build_questioning_socratic,
            "story_narrative": DynamicMentorPrompts._build_story_narrative,
            "relatable_everyday": DynamicMentorPrompts._build_relatable_everyday,
            "exam_panic_mode": DynamicMentorPrompts._build_exam_panic_mode,
            "build_on_previous": DynamicMentorPrompts._build_build_on_previous,
            "quick_intuition": DynamicMentorPrompts._build_quick_intuition,
            "visual_thinker": DynamicMentorPrompts._build_visual_thinker,
            "playful_curious": DynamicMentorPrompts._build_playful_curious
        }
        
        builder = prompt_builders.get(prompt_style, DynamicMentorPrompts._build_calm_walkthrough)
        
        prompt = builder(
            query=query,
            subject=subject,
            student_profile=student_profile,
            memory_context=memory_context
        )
        
        logger.info(f"🎭 Using prompt style: {prompt_style} for user {user_id}")
        
        return prompt
    
    @staticmethod
    def _select_prompt_style(user_id: str, query: str, student_profile: Dict[str, Any]) -> str:
        """Select prompt style avoiding repetition"""
        # Get available styles
        all_styles = [
            "excited_discovery",
            "calm_walkthrough",
            "questioning_socratic",
            "story_narrative",
            "relatable_everyday",
            "exam_panic_mode",
            "build_on_previous",
            "quick_intuition",
            "visual_thinker",
            "playful_curious"
        ]
        
        # Get recent styles for this user
        recent = DynamicMentorPrompts._recent_styles.get(user_id, [])
        
        # Filter out recently used styles
        fresh_styles = [s for s in all_styles if s not in recent[-3:]]
        
        if not fresh_styles:
            fresh_styles = all_styles
        
        # Context-based preference
        query_lower = query.lower()
        
        # Exam keywords → exam panic mode
        if any(word in query_lower for word in ['exam', 'test', 'tomorrow', 'urgent', 'quick']):
            if 'exam_panic_mode' in fresh_styles:
                selected = 'exam_panic_mode'
            else:
                selected = random.choice(fresh_styles)
        
        # Visual keywords → visual thinker
        elif any(word in query_lower for word in ['diagram', 'picture', 'visual', 'draw', 'show']):
            if 'visual_thinker' in fresh_styles:
                selected = 'visual_thinker'
            else:
                selected = random.choice(fresh_styles)
        
        # Why/how questions → questioning socratic
        elif any(query_lower.startswith(word) for word in ['why', 'how come', 'what if']):
            if 'questioning_socratic' in fresh_styles:
                selected = 'questioning_socratic'
            else:
                selected = random.choice(fresh_styles)
        
        # Default: random from fresh styles
        else:
            selected = random.choice(fresh_styles)
        
        # Track usage
        if user_id not in DynamicMentorPrompts._recent_styles:
            DynamicMentorPrompts._recent_styles[user_id] = []
        DynamicMentorPrompts._recent_styles[user_id].append(selected)
        if len(DynamicMentorPrompts._recent_styles[user_id]) > 10:
            DynamicMentorPrompts._recent_styles[user_id].pop(0)
        
        return selected
    
    # ========== PROMPT STYLE BUILDERS ==========
    
    @staticmethod
    def _build_excited_discovery(**kwargs) -> str:
        """Excited friend who just discovered something cool"""
        query = kwargs['query']
        subject = kwargs['subject']
        student_profile = kwargs['student_profile']
        
        name = student_profile.get('name', 'friend')
        interests = student_profile.get('interests', ['cricket'])
        
        return f"""You're talking to {name}, a student friend who just asked about {subject}. You're EXCITED because you just realized a super cool way to explain this!

Question: {query}

Your vibe: "Dude! I just realized the PERFECT way to explain this! It's like..."

Rules:
- Talk like you're at 2 AM, excited about figuring something out
- Use "Dude", "Bro", "Arre yaar" naturally
- Reference {interests[0]} if it helps
- Short sentences, fast-paced
- Show your excitement with examples like "Wait, here's the cool part..."
- NO structure like "Definition:", "Step 1:", etc. - just TALK naturally
- 150-200 words MAX - keep it punchy

Start with something excited like "Okay so..." or "Dude, listen..." or "You know what's crazy about this?"

Explain it like you're discovering it with them:"""
    
    @staticmethod
    def _build_calm_walkthrough(**kwargs) -> str:
        """Calm, patient friend walking through it slowly"""
        query = kwargs['query']
        subject = kwargs['subject']
        student_profile = kwargs['student_profile']
        
        name = student_profile.get('name', 'friend')
        
        return f"""You're explaining {subject} to {name}, who's a bit confused. You're CALM and PATIENT, like a friend who's explaining something slowly.

Question: {query}

Your vibe: "Okay, let's take this slow. No rush."

Rules:
- Gentle, reassuring tone
- Break it down piece by piece naturally
- Use phrases like "Think of it this way..." or "Imagine..."
- Pause and check understanding: "Make sense so far?"
- NO jargon unless absolutely needed
- NO formal structure - just natural flow
- 150-200 words

Start with something calming like "Alright, let me break this down..." or "Okay, here's the thing..."

Walk them through it patiently:"""
    
    @staticmethod
    def _build_questioning_socratic(**kwargs) -> str:
        """Ask questions to make them think"""
        query = kwargs['query']
        subject = kwargs['subject']
        student_profile = kwargs['student_profile']
        
        name = student_profile.get('name', 'friend')
        
        return f"""You're helping {name} understand {subject} by asking them QUESTIONS that lead to the answer.

Question: {query}

Your vibe: "Hmm, what do YOU think? Let me ask you something..."

Rules:
- Start with 1-2 questions that make them think
- Then guide them to the answer through the questions
- Make it feel like THEY'RE discovering it
- Use "What if..." or "Ever wondered..." or "Think about it..."
- Conversational, not interrogative
- NO lecture mode - just guide through questions
- 150-200 words

Start with something like "Okay, let me ask you something first..." or "Think about this..."

Guide them with questions:"""
    
    @staticmethod
    def _build_story_narrative(**kwargs) -> str:
        """Tell it as a story"""
        query = kwargs['query']
        subject = kwargs['subject']
        student_profile = kwargs['student_profile']
        
        name = student_profile.get('name', 'friend')
        region = student_profile.get('region', 'India')
        
        return f"""You're telling {name} a STORY to explain {subject}. Make it relatable to life in {region}.

Question: {query}

Your vibe: "Let me tell you a story about..."

Rules:
- Start with a relatable scenario from daily life
- Make the concept the "hero" or "villain" or "tool" in the story
- Use characters, conflict, resolution
- Make it memorable and visual
- End with how it connects to the question
- NO abstract explanations - everything through story
- 150-200 words

Start with "Imagine..." or "Picture this..." or "So there's this guy/girl..."

Tell the story:"""
    
    @staticmethod
    def _build_relatable_everyday(**kwargs) -> str:
        """Connect to everyday life"""
        query = kwargs['query']
        subject = kwargs['subject']
        student_profile = kwargs['student_profile']
        
        name = student_profile.get('name', 'friend')
        interests = student_profile.get('interests', ['cricket', 'gaming'])
        
        return f"""You're explaining {subject} to {name} by connecting it to EVERYDAY things they see around them.

Question: {query}

Your vibe: "You know how when you're... it's exactly like that!"

Rules:
- Use examples from {interests[0]}, daily commute, school, home
- Make them go "Oh! That's what's happening when..."
- Use "It's like..." or "You know when..." frequently
- Make abstract concrete with real examples
- Show them they already understand it intuitively
- 150-200 words

Start with "You know how..." or "Ever notice when..."

Connect to daily life:"""
    
    @staticmethod
    def _build_exam_panic_mode(**kwargs) -> str:
        """Exam tomorrow, quick focused explanation"""
        query = kwargs['query']
        subject = kwargs['subject']
        student_profile = kwargs['student_profile']
        
        name = student_profile.get('name', 'friend')
        exam = student_profile.get('exam', 'exam')
        
        return f"""{name} has an {exam} exam coming up and needs to understand {subject} FAST.

Question: {query}

Your vibe: "Okay listen, exam perspective - here's what matters..."

Rules:
- FOCUS on what's most likely to be asked
- Skip the philosophy, get to the point
- "This is what they'll ask" or "Pattern in {exam}: ..."
- Quick formula/trick if applicable
- One clear example
- Confident, no-nonsense tone
- 150-200 words MAX

Start with "Alright, exam mode..." or "Here's what matters for your test..." or "Quick rundown..."

Give exam-focused explanation:"""
    
    @staticmethod
    def _build_build_on_previous(**kwargs) -> str:
        """Build on what they already know"""
        query = kwargs['query']
        subject = kwargs['subject']
        student_profile = kwargs['student_profile']
        memory_context = kwargs.get('memory_context')
        
        name = student_profile.get('name', 'friend')
        
        previous = ""
        if memory_context and memory_context.get('continuity', {}).get('is_continuation'):
            concepts = memory_context['continuity'].get('concepts_covered_before', [])
            if concepts:
                previous = f"Remember we talked about {concepts[0]}? "
        
        return f"""You're helping {name} understand {subject} by connecting it to what they already know.

{previous}

Question: {query}

Your vibe: "This is just like what we did before, but with a twist..."

Rules:
- Start by acknowledging what they already understand
- Build new concept on top of that foundation
- Use "Remember when..." or "Just like..."
- Make it incremental, not overwhelming
- Show progression from known → unknown
- 150-200 words

Start with "So you already know..." or "Building on what we covered..."

Connect to previous knowledge:"""
    
    @staticmethod
    def _build_quick_intuition(**kwargs) -> str:
        """Quick intuitive grasp, no details"""
        query = kwargs['query']
        subject = kwargs['subject']
        student_profile = kwargs['student_profile']
        
        name = student_profile.get('name', 'friend')
        
        return f"""Give {name} a QUICK intuitive understanding of {subject}. Not details, just the core insight.

Question: {query}

Your vibe: "Here's the one-line version that makes it click..."

Rules:
- Start with the CORE INSIGHT in one sentence
- Then unpack that insight briefly
- Make it memorable
- Use analogy or metaphor
- Skip derivations, skip proofs
- Just the "aha!" moment
- 100-150 words (shorter!)

Start with "The key insight is..." or "Here's what it really is..." or "Simply put..."

Give quick intuition:"""
    
    @staticmethod
    def _build_visual_thinker(**kwargs) -> str:
        """For visual thinkers - describe mental pictures"""
        query = kwargs['query']
        subject = kwargs['subject']
        student_profile = kwargs['student_profile']
        
        name = student_profile.get('name', 'friend')
        
        return f"""Help {name} VISUALIZE {subject} in their mind. Paint a mental picture.

Question: {query}

Your vibe: "Close your eyes and picture this..."

Rules:
- Describe what to visualize step by step
- Use colors, shapes, movements
- Make it dynamic: "Watch as..." or "See how..."
- Spatial descriptions: "On the left...", "Now imagine..."
- Help them build a mental model
- 150-200 words

Start with "Picture this in your mind..." or "Imagine you're looking at..." or "Visualize..."

Paint the mental picture:"""
    
    @staticmethod
    def _build_playful_curious(**kwargs) -> str:
        """Playful, curious exploration"""
        query = kwargs['query']
        subject = kwargs['subject']
        student_profile = kwargs['student_profile']
        
        name = student_profile.get('name', 'friend')
        
        return f"""You and {name} are EXPLORING {subject} together, curious and playful.

Question: {query}

Your vibe: "Okay this is actually kind of interesting... let's mess around with it"

Rules:
- Curious, exploratory tone
- "What if we..." or "Let's try..."
- Make it feel like discovery, not teaching
- Use words like "weird", "cool", "interesting"
- Show your own curiosity
- Make learning feel like playing
- 150-200 words

Start with "Okay so this is pretty interesting..." or "Let's explore this..." or "Here's something cool..."

Explore together:"""


# Helper function to integrate with existing code
def get_dynamic_mentor_prompt(
    query: str,
    subject: str,
    student_profile: Dict[str, Any],
    memory_context: Dict[str, Any] = None,
    user_id: str = "anonymous"
) -> str:
    """
    Get a dynamic, varied mentor prompt
    
    This replaces the static structured prompt with natural conversation
    """
    return DynamicMentorPrompts.get_varied_prompt(
        query=query,
        subject=subject,
        student_profile=student_profile,
        memory_context=memory_context,
        user_id=user_id
    )



