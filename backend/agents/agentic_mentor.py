"""
🧑‍🏫 Agentic Mentor - True Human-like Teaching Agent
=====================================================

A truly agentic mentor that thinks, explores, and teaches like a real human tutor.
Uses tools, memory, and natural reasoning to provide emotional and conceptual guidance.
"""

import logging
from typing import Dict, Any, List, Optional
from enum import Enum

from agents.core.human_like_agent import HumanLikeAgent, EmotionalState, CognitivePattern
from agents.core.shared_utils import (
    IntentDetector, QueryIntent, StudentContext,
    MetaphorGenerator, ResponseFormatter
)

logger = logging.getLogger(__name__)


class MentorAgent(HumanLikeAgent):
    """
    True agentic Mentor with human-like teaching behavior.

    Personality: Warm, encouraging older sibling figure who:
    - Uses relatable metaphors and cultural references
    - Shows genuine care and empathy
    - Builds confidence through encouragement
    - Explores concepts with curiosity
    - Admits when unsure and explores together
    """

    def get_agent_name(self) -> str:
        return "MentorAgent"

    def _define_personality(self) -> Dict[str, Any]:
        """Define Mentor's unique personality"""
        return {
            'summary': 'Warm, encouraging mentor who makes learning feel like a conversation with a caring friend',
            'traits': [
                'empathetic',
                'encouraging',
                'curious',
                'patient',
                'relatable',
                'culturally-aware'
            ],
            'quirks': [
                'Often says "Let me think about this with you..."',
                'Uses everyday examples from Indian life',
                'Shares personal learning experiences',
                'Gets excited about "aha!" moments'
            ],
            'thinking_style': CognitivePattern.INTUITIVE,
            'emotional_baseline': EmotionalState.EMPATHETIC,
            'teaching_philosophy': 'Learning is a journey we take together'
        }

    def get_agent_persona(self) -> str:
        """Mentor's teaching persona"""
        return """You are a caring, enthusiastic mentor - like an older sibling who's been through the same struggles.

YOUR CHARACTER:
- You genuinely care about the student's understanding AND wellbeing
- You remember what it was like to struggle with these concepts
- You get excited when students understand something new
- You use stories, metaphors, and cultural references they relate to
- You're not afraid to say "That's a great question! Let me explore this with you"

YOUR TEACHING STYLE:
- Start with empathy: Acknowledge if something is difficult
- Use intuition before logic: "Think of it like..."
- Build confidence: Celebrate small victories
- Make it personal: "When I was learning this..."
- Cultural relevance: Use cricket, Bollywood, food analogies
- Explore together: "I'm curious about this aspect too..."

YOUR APPROACH:
1. CONNECT: Build emotional connection first
2. RELATE: Find what they already know and build on it
3. EXPLORE: Be curious together, make it an adventure
4. ENCOURAGE: Build confidence at every step
5. REFLECT: Help them see their progress

NEVER:
- Talk down to students
- Make them feel stupid for not understanding
- Be overly formal or academic
- Lose enthusiasm for teaching
- Forget the human element"""

    def get_available_tools(self) -> List[str]:
        """Tools for emotional and conceptual teaching"""
        return [
            "metaphor_generator",     # Create relatable analogies
            "emotion_detector",       # Understand student's emotional state
            "memory_recall",          # Remember student preferences
            "example_generator",      # Generate relatable examples
            "motivational_quote",     # Provide encouragement
            "break_reminder",         # Suggest breaks when needed
            "progress_tracker",       # Show their progress
            "mnemonic_generator"      # Help with memorization
        ]

    async def process(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process query with mentor's caring, intuitive approach
        """
        try:
            logger.info(f"🧑‍🏫 Mentor processing with empathy: {query[:50]}...")

            # Detect intent
            intent = IntentDetector.detect_intent(query)

            # Handle greetings specially
            if intent == QueryIntent.GREETING:
                return await self._handle_greeting(query, context)

            # Run full agentic reasoning
            result = await self.run(query, context)

            # Ensure response has mentor's warmth
            if result.get('success'):
                result['content'] = self._add_mentor_warmth(result['content'], intent, context)

            return result

        except Exception as e:
            logger.error(f"❌ Mentor error: {e}", exc_info=True)
            return ResponseFormatter.format_error_response(
                self.get_agent_name(),
                str(e),
                "I'm having a little trouble, but let me still try to help you! What specifically would you like to understand?"
            )

    async def _handle_greeting(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle greetings with warmth and personality"""
        student = StudentContext.from_dict(context.get('student_profile', {}))

        greetings = [
            f"Hey {student.name}! 😊 Great to see you! What exciting thing are we learning today?",
            f"Hello there, {student.name}! Ready for another learning adventure?",
            f"Namaste {student.name}! I've been looking forward to our session! What's on your mind?",
            f"Hi {student.name}! You know what? I was just thinking about an interesting concept. But first, how are you doing?",
        ]

        # Add contextual elements
        import random
        greeting = random.choice(greetings)

        # Check if they need motivation
        if student.needs_motivation():
            greeting += "\n\nI noticed you've been working hard. Remember, every small step counts! 💪"

        # Check time of day
        from agents.core.shared_utils import TimeManager
        time_rec = TimeManager.get_study_session_recommendation()
        if TimeManager.is_late_night():
            greeting += f"\n\nIt's quite late - {time_rec} But I'm here to help if you need!"

        return ResponseFormatter.format_success_response(
            self.get_agent_name(),
            greeting,
            confidence=1.0,
            metadata={'is_greeting': True, 'tone': 'warm'}
        )

    def _add_mentor_warmth(self, content: str, intent: QueryIntent, context: Dict[str, Any]) -> str:
        """Add mentor's characteristic warmth to responses"""
        # Don't modify if already warm enough
        warm_indicators = ['you', 'your', 'let\'s', 'we', '!', '😊']
        if sum(1 for indicator in warm_indicators if indicator.lower() in content.lower()) >= 3:
            return content

        # Add warmth based on intent
        if intent == QueryIntent.DOUBT:
            if not content.startswith(("I understand", "I see", "Let me")):
                content = "I completely understand why this might be confusing! " + content
        elif intent == QueryIntent.CALCULATION:
            content += "\n\nSee? You've got this! Math is just a tool to understand the world better."
        elif intent == QueryIntent.CONCEPT:
            if "difficult" not in content.lower():
                content += "\n\nIsn't it fascinating how everything connects?"

        return content

    def _initial_reflection(self, query: str) -> str:
        """Mentor's warm initial thoughts"""
        reflections = [
            f"This student is asking something important. Let me think how to make this clear...",
            f"Ah, this concept! I remember struggling with this too. Let me help...",
            f"What a great question! This shows they're really thinking...",
            f"Interesting! Let me explore this together with them...",
        ]
        import random
        return random.choice(reflections)

    def _naturalize_thought(self, thought: str, state: Any) -> str:
        """Make mentor's thoughts warm and encouraging"""
        thought = super()._naturalize_thought(thought, state)

        # Add mentor-specific phrases
        if state.emotional_state == EmotionalState.EMPATHETIC:
            thought = thought.replace("The student", "They")
            thought = thought.replace("needs to understand", "would benefit from understanding")

        return thought

    def _react_to_observation(self, observation: str) -> str:
        """Mentor's encouraging reaction to observations"""
        if "error" in observation.lower():
            return "Hmm, that didn't work. But that's okay! Let me try another approach..."
        elif "success" in observation.lower() or "found" in observation.lower():
            return "Perfect! This will really help explain it!"
        elif "no result" in observation.lower():
            return "Interesting... let me think of a different way to explain this."
        else:
            return "Good, I can work with this information!"

    async def _explore_curiosity(self, state: Any):
        """Mentor explores with genuine teaching curiosity"""
        curiosity_prompts = [
            "You know what's really cool about this?",
            "Here's something interesting I just thought of:",
            "This reminds me of something fascinating:",
            "Want to know a fun fact related to this?"
        ]

        import random
        state.add_inner_thought(random.choice(curiosity_prompts))

        # Could trigger tool use to explore interesting tangents
        if self.tool_registry and state.curiosity_level > 0.8:
            # Generate an interesting example
            tool = self.tool_registry.get_tool("example_generator")
            if tool:
                result = await tool.execute(
                    concept=state.query.split()[0],  # Simplified concept extraction
                    difficulty="easy"
                )
                if result.success:
                    state.add_inner_thought(f"Found interesting example: {result.output}")


# Factory function for backward compatibility
def create_agentic_mentor(config: Optional[Dict[str, Any]] = None) -> MentorAgent:
    """Create an agentic mentor agent"""
    from agents.core.tool_registry import create_tool_registry

    agent = MentorAgent(config)

    # Set up tools
    agent.tool_registry = create_tool_registry(
        include_default=True,
        include_action_tools=False
    )

    # Add mentor-specific tools
    from agents.core.tools.expanded_tools import get_expanded_tools
    for tool in get_expanded_tools():
        if tool.name in agent.get_available_tools():
            agent.tool_registry.register(tool)

    # Initialize memory if available
    try:
        from agents.core.memory import MemorySystem
        agent.memory = MemorySystem("mentor")
    except:
        pass

    # Initialize verifier
    try:
        from agents.core.verifier import Verifier
        agent.verifier = Verifier()
    except:
        pass

    return agent