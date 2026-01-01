"""
🧠 Human-like Agent Base - Natural Behavior & Reasoning
========================================================

This enhanced ReAct agent base provides human-like cognitive behaviors:
- Emotional awareness and empathy
- Context-aware decision making
- Natural conversation flow
- Self-doubt and correction
- Curiosity-driven exploration
- Personality traits
"""

import logging
import asyncio
import json
import random
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import abstractmethod
from datetime import datetime

from agents.core.react_agent import ReActAgent, AgentState, ThoughtAction, AgentStatus

logger = logging.getLogger(__name__)


class EmotionalState(Enum):
    """Agent's emotional state affects decision making"""
    NEUTRAL = "neutral"
    CURIOUS = "curious"
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"
    EMPATHETIC = "empathetic"
    EXCITED = "excited"
    CONCERNED = "concerned"


class CognitivePattern(Enum):
    """Different thinking patterns agents can exhibit"""
    ANALYTICAL = "analytical"  # Step-by-step logical thinking
    INTUITIVE = "intuitive"    # Pattern recognition and gut feeling
    CREATIVE = "creative"      # Lateral thinking and analogies
    EXPLORATORY = "exploratory"  # Curiosity-driven investigation
    REFLECTIVE = "reflective"  # Self-examination and meta-cognition


@dataclass
class HumanLikeState(AgentState):
    """Extended state with human-like cognitive features"""
    emotional_state: EmotionalState = EmotionalState.NEUTRAL
    cognitive_pattern: CognitivePattern = CognitivePattern.ANALYTICAL
    confidence_threshold: float = 0.7
    curiosity_level: float = 0.5  # 0-1 scale
    empathy_level: float = 0.8   # 0-1 scale
    inner_monologue: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    questions_to_explore: List[str] = field(default_factory=list)

    def add_inner_thought(self, thought: str):
        """Add to inner monologue (not shown to user)"""
        self.inner_monologue.append(thought)
        logger.debug(f"💭 Inner thought: {thought}")

    def should_double_check(self) -> bool:
        """Determine if agent should verify its thinking"""
        return (
            self.emotional_state == EmotionalState.UNCERTAIN or
            self.confidence < self.confidence_threshold or
            len(self.assumptions) > 2
        )

    def adjust_emotional_state(self, context: Dict[str, Any]):
        """Adjust emotional state based on context"""
        query = self.query.lower()

        # Detect emotional cues
        if any(word in query for word in ['confused', 'stuck', 'help', 'frustrated']):
            self.emotional_state = EmotionalState.EMPATHETIC
            self.empathy_level = min(1.0, self.empathy_level + 0.2)
        elif any(word in query for word in ['amazing', 'wow', 'brilliant', 'great']):
            self.emotional_state = EmotionalState.EXCITED
        elif any(word in query for word in ['worried', 'scared', 'anxious', 'nervous']):
            self.emotional_state = EmotionalState.CONCERNED
            self.empathy_level = min(1.0, self.empathy_level + 0.1)
        elif any(word in query for word in ['why', 'how', 'what if', 'curious']):
            self.emotional_state = EmotionalState.CURIOUS
            self.curiosity_level = min(1.0, self.curiosity_level + 0.2)


class HumanLikeAgent(ReActAgent):
    """
    Enhanced ReAct agent with human-like cognitive behaviors.

    Features:
    - Natural thinking patterns (not just logical)
    - Emotional awareness and response
    - Self-doubt and verification
    - Curiosity-driven exploration
    - Personality traits that affect behavior
    - Meta-cognition (thinking about thinking)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

        # Personality traits (can be customized per agent)
        self.personality = self._define_personality()

        # Behavioral parameters
        self.thinking_speed = config.get('thinking_speed', 'moderate')  # fast, moderate, deliberate
        self.verbosity = config.get('verbosity', 'balanced')  # concise, balanced, detailed
        self.formality = config.get('formality', 'casual')  # casual, balanced, formal

        logger.info(f"🧠 {self.get_agent_name()} initialized with personality: {self.personality['summary']}")

    @abstractmethod
    def _define_personality(self) -> Dict[str, Any]:
        """Define agent's personality traits"""
        return {
            'summary': 'Generic helpful agent',
            'traits': ['helpful', 'logical'],
            'quirks': [],
            'thinking_style': CognitivePattern.ANALYTICAL,
            'emotional_baseline': EmotionalState.NEUTRAL
        }

    def get_system_prompt(self, state: HumanLikeState) -> str:
        """Build human-like system prompt"""
        base_prompt = super().get_system_prompt(state)

        # Add emotional and cognitive context
        emotional_context = f"""

## YOUR CURRENT STATE
- Emotional State: {state.emotional_state.value}
- Confidence Level: {state.confidence:.1%}
- Thinking Pattern: {state.cognitive_pattern.value}
- Empathy Setting: {"High" if state.empathy_level > 0.7 else "Moderate"}

## BEHAVIORAL GUIDELINES
1. Think naturally - not everything needs to be perfectly logical
2. Show curiosity when you encounter interesting aspects
3. Express uncertainty when you're not sure
4. Use your personality traits: {', '.join(self.personality['traits'])}
5. Acknowledge the human's emotional state
6. Sometimes think out loud, showing your reasoning process
7. It's okay to make assumptions (but state them)
8. Ask clarifying questions when helpful

## THINKING STYLE
You tend to think in a {state.cognitive_pattern.value} way:
{self._get_thinking_style_description(state.cognitive_pattern)}

## IMPORTANT
- Be authentic and natural in your responses
- Show your thought process when it helps understanding
- Express appropriate emotion based on context
- Admit when you need to think more or verify something
"""

        return base_prompt + emotional_context

    def _get_thinking_style_description(self, pattern: CognitivePattern) -> str:
        """Get description of thinking style"""
        descriptions = {
            CognitivePattern.ANALYTICAL: "Break problems into logical steps, examine cause and effect",
            CognitivePattern.INTUITIVE: "Trust patterns you recognize, use experience-based insights",
            CognitivePattern.CREATIVE: "Make unexpected connections, use analogies and metaphors",
            CognitivePattern.EXPLORATORY: "Follow curiosity, ask 'what if' questions, investigate thoroughly",
            CognitivePattern.REFLECTIVE: "Consider implications, examine your own thinking, be metacognitive"
        }
        return descriptions.get(pattern, "Think in your natural way")

    async def run(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced run with human-like cognitive process"""
        # Create human-like state
        state = HumanLikeState(
            query=query,
            context=context,
            max_iterations=self.max_iterations,
            cognitive_pattern=self.personality.get('thinking_style', CognitivePattern.ANALYTICAL),
            emotional_state=self.personality.get('emotional_baseline', EmotionalState.NEUTRAL)
        )

        # Adjust emotional state based on query
        state.adjust_emotional_state(context)

        logger.info(f"🧠 {self.get_agent_name()} processing with {state.emotional_state.value} state")

        try:
            # Initial reflection (human-like)
            state.add_inner_thought(self._initial_reflection(query))

            # Main reasoning loop with human-like behaviors
            while state.iterations < state.max_iterations:
                state.iterations += 1

                # Simulate human thinking speed
                if self.thinking_speed == 'deliberate':
                    await asyncio.sleep(0.5)  # Thoughtful pause
                elif self.thinking_speed == 'moderate':
                    await asyncio.sleep(0.2)

                # THINK (with occasional self-doubt)
                state.status = AgentStatus.THINKING
                thought_action = await self._think_humanlike(state)

                if not thought_action:
                    state.add_inner_thought("Hmm, I'm stuck. Let me try a different approach...")
                    state.cognitive_pattern = self._switch_thinking_pattern(state.cognitive_pattern)
                    continue

                # Check for completion
                if thought_action.action == "FINISH":
                    # Double-check if uncertain
                    if state.should_double_check():
                        state.add_inner_thought("Wait, let me verify this before responding...")
                        if not await self._verify_conclusion(state):
                            continue  # Keep thinking

                    state.status = AgentStatus.COMPLETE
                    state.final_answer = await self._humanize_response(
                        thought_action.action_input.get("answer", thought_action.thought),
                        state
                    )
                    break

                # ACT (with curiosity-driven exploration)
                state.status = AgentStatus.ACTING

                # Sometimes explore tangential questions out of curiosity
                if state.curiosity_level > 0.7 and random.random() < 0.3:
                    state.add_inner_thought("I'm curious about a related aspect...")
                    await self._explore_curiosity(state)

                observation = await self._act(thought_action, state)
                thought_action.observation = observation

                # OBSERVE (with emotional response)
                state.status = AgentStatus.OBSERVING
                state.add_inner_thought(self._react_to_observation(observation))

                # Adjust confidence based on observation
                state.confidence = self._update_confidence(state, observation)

                if self.verbose:
                    logger.info(f"  Step {state.iterations}: {thought_action.action} → {observation[:100]}...")

            state.end_time = datetime.now()
            return self._format_human_response(state)

        except Exception as e:
            logger.error(f"❌ {self.get_agent_name()} error: {e}", exc_info=True)
            state.status = AgentStatus.ERROR
            state.error = str(e)
            return self._format_error_response(state)

    async def _think_humanlike(self, state: HumanLikeState) -> Optional[ThoughtAction]:
        """Generate human-like thought process"""
        try:
            # Build context-aware prompt
            system_prompt = self.get_system_prompt(state)

            # Frame the question based on emotional state
            if state.emotional_state == EmotionalState.EMPATHETIC:
                user_message = f"The student seems to be struggling. How can I help with: {state.query}"
            elif state.emotional_state == EmotionalState.CURIOUS:
                user_message = f"This is interesting! Let me explore: {state.query}"
            else:
                user_message = f"Let me think about: {state.query}"

            # Include previous observations
            if state.reasoning_chain and state.reasoning_chain[-1].observation:
                last = state.reasoning_chain[-1]
                user_message = f"""Based on {last.action}:
{last.observation}

Now, {self._get_transition_phrase()} what should I do next?"""

            # Get LLM response
            response = await self._call_llm(system_prompt, user_message)
            if not response:
                return None

            # Parse and create thought action
            parsed = self._parse_llm_response(response)

            # Make the thought more natural
            thought = self._naturalize_thought(parsed.get("thought", "Thinking..."), state)

            ta = state.add_thought(thought)
            ta.action = parsed.get("action", "FINISH")
            ta.action_input = parsed.get("action_input", {})

            # Update confidence
            state.confidence = parsed.get("confidence", 0.5)

            return ta

        except Exception as e:
            logger.error(f"Think error: {e}")
            return None

    def _naturalize_thought(self, thought: str, state: HumanLikeState) -> str:
        """Make thoughts sound more natural and human"""
        if state.emotional_state == EmotionalState.UNCERTAIN:
            prefixes = ["I'm not entirely sure, but ", "Let me think... ", "Hmm, "]
            thought = random.choice(prefixes) + thought.lower()
        elif state.emotional_state == EmotionalState.EXCITED:
            prefixes = ["Oh, this is interesting! ", "I enjoy explaining this! ", "Let me share this with you! "]
            thought = random.choice(prefixes) + thought
        elif state.emotional_state == EmotionalState.EMPATHETIC:
            prefixes = ["I understand this can be confusing. ", "Let me help clarify. ", "I see where you're coming from. "]
            thought = random.choice(prefixes) + thought

        return thought

    def _get_transition_phrase(self) -> str:
        """Get natural transition phrases"""
        phrases = [
            "based on that",
            "given this information",
            "considering what I found",
            "taking this into account",
            "with this in mind"
        ]
        return random.choice(phrases)

    def _initial_reflection(self, query: str) -> str:
        """Initial human-like reflection on the query"""
        reflections = [
            f"This is asking about {self._extract_topic(query)}",
            f"The student wants to understand {self._extract_intent(query)}",
            f"I should help explain {self._extract_topic(query)}",
            f"This seems to be about {self._extract_topic(query)}"
        ]
        return random.choice(reflections)

    def _extract_topic(self, query: str) -> str:
        """Extract topic from query (simplified)"""
        # In practice, this would use NLP
        words = query.lower().split()
        if len(words) > 5:
            return "this concept"
        return "the question"

    def _extract_intent(self, query: str) -> str:
        """Extract intent from query (simplified)"""
        query_lower = query.lower()
        if 'how' in query_lower:
            return "how something works"
        elif 'why' in query_lower:
            return "the reason behind something"
        elif 'what' in query_lower:
            return "what something means"
        return "this topic"

    def _react_to_observation(self, observation: str) -> str:
        """Human-like reaction to observations"""
        if "error" in observation.lower():
            return "Oh, that didn't work as expected. Let me try another approach."
        elif "success" in observation.lower() or "found" in observation.lower():
            return "Good, that's helpful!"
        elif len(observation) > 500:
            return "That's quite a lot of information. Let me process this."
        else:
            return "Interesting, let me think about this."

    def _update_confidence(self, state: HumanLikeState, observation: str) -> float:
        """Update confidence based on observation"""
        current = state.confidence

        if "error" in observation.lower() or "failed" in observation.lower():
            return max(0.1, current - 0.2)
        elif "verified" in observation.lower() or "confirmed" in observation.lower():
            return min(1.0, current + 0.2)
        elif "uncertain" in observation.lower() or "might" in observation.lower():
            return max(0.3, current - 0.1)
        else:
            return min(1.0, current + 0.05)  # Slight increase for progress

    def _switch_thinking_pattern(self, current: CognitivePattern) -> CognitivePattern:
        """Switch to a different thinking pattern when stuck"""
        patterns = [p for p in CognitivePattern if p != current]
        return random.choice(patterns)

    async def _verify_conclusion(self, state: HumanLikeState) -> bool:
        """Verify conclusion when uncertain"""
        if self.verifier:
            result = await self.verifier.verify_response(
                state.final_answer,
                state.context
            )
            return result.is_valid
        return True  # Assume valid if no verifier

    async def _explore_curiosity(self, state: HumanLikeState):
        """Explore tangential questions out of curiosity"""
        if state.questions_to_explore:
            question = state.questions_to_explore.pop(0)
            state.add_inner_thought(f"I wonder about: {question}")
            # Could trigger additional tool use here

    async def _humanize_response(self, response: str, state: HumanLikeState) -> str:
        """Make response more natural and human-like"""
        # Add appropriate emotional touch
        if state.emotional_state == EmotionalState.EMPATHETIC:
            if not response.startswith(("I understand", "I see")):
                response = "I understand this can be challenging. " + response
        elif state.emotional_state == EmotionalState.EXCITED:
            if not any(word in response.lower() for word in ['great', 'excellent', 'interesting']):
                response = "Let me explain this! " + response

        # Add confidence qualifier if uncertain
        if state.confidence < 0.6:
            qualifiers = [
                "Based on my understanding, ",
                "From what I can tell, ",
                "I believe ",
            ]
            response = random.choice(qualifiers) + response.lower()

        # Add offer for clarification if complex
        if state.iterations > 5:
            response += "\n\nThis was a bit complex - let me know if you'd like me to clarify any part!"

        return response

    def _format_human_response(self, state: HumanLikeState) -> Dict[str, Any]:
        """Format response with human-like metadata"""
        base_response = self._format_response(state)

        # Add human-like metadata
        base_response['metadata'].update({
            'emotional_state': state.emotional_state.value,
            'cognitive_pattern': state.cognitive_pattern.value,
            'curiosity_level': state.curiosity_level,
            'inner_monologue': state.inner_monologue[-3:] if self.verbose else [],  # Last 3 thoughts
            'assumptions_made': state.assumptions,
            'confidence_explanation': self._explain_confidence(state.confidence)
        })

        return base_response

    def _explain_confidence(self, confidence: float) -> str:
        """Explain confidence level in human terms"""
        if confidence > 0.9:
            return "Very confident in this response"
        elif confidence > 0.7:
            return "Fairly confident"
        elif confidence > 0.5:
            return "Moderately confident"
        elif confidence > 0.3:
            return "Somewhat uncertain"
        else:
            return "Low confidence - please verify"