"""
State Enforcer - THE LAW OF COGNITIVE OS
=========================================

THIS IS THE CORE OF TRUE COGNITIVE OS.

PRINCIPLE:
- STATE IS LAW, NOT ADVICE
- LLM IS A TOOL, NOT A DECISION-MAKER
- AGENTS ENFORCE BEHAVIOR, NOT SUGGEST IT

This module enforces that:
1. conversation_phase BLOCKS certain response types
2. last_topic REQUIRES continuation
3. pending_action REQUIRES completion
4. Fallbacks CONTINUE, never RESET

NO LLM OUTPUT, NO CLASSIFIER RESULT, NO FALLBACK PATH
may generate a response that violates state.

Author: Druv AI Engineering
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ResponseViolation(Enum):
    """Types of state violations a response can commit"""
    CONTEXT_RESET = "context_reset"           # Response ignores known context
    TOPIC_IGNORED = "topic_ignored"           # Response ignores current topic
    GREETING_MID_CONVERSATION = "greeting_mid_conversation"  # Greeting when not first turn
    CAPABILITY_MENU = "capability_menu"       # "What can I help you with?"
    PENDING_ACTION_IGNORED = "pending_action_ignored"  # Ignores pending action
    GENERIC_FALLBACK = "generic_fallback"     # Generic response when context exists


@dataclass
class EnforcementResult:
    """Result of state enforcement check"""
    is_legal: bool
    violations: List[ResponseViolation]
    required_behavior: str
    topic_to_continue: str
    must_reference: List[str]
    rejection_reason: str = ""


class StateEnforcer:
    """
    THE LAW ENFORCEMENT LAYER OF COGNITIVE OS.
    
    This class has VETO POWER over all responses.
    It can REJECT any response that violates conversation state.
    
    STATE IS LAW:
    - If conversation_phase != FIRST_TURN → greeting responses are ILLEGAL
    - If last_topic exists → topic-ignoring responses are ILLEGAL
    - If pending_action exists → action-ignoring responses are ILLEGAL
    
    NO EXCEPTIONS. NO OVERRIDES. NO "LLM KNOWS BETTER".
    """
    
    # Phrases that indicate a context reset (ILLEGAL mid-conversation)
    RESET_INDICATORS = [
        "how can i help you",
        "what can i help you with",
        "what would you like",
        "what do you want to",
        "here for you",
        "i'm here to help",
        "feel free to ask",
        "anything you'd like",
        "what's on your mind",
        "something on your mind",
        "what brings you here",
        "how may i assist",
        "let me know what",
        "tell me what you need",
        "what are you looking for",
        "what topic would you like",
        "which subject",
        "pick a topic",
        "choose a subject",
        "what subject",
        "i can help you with many things",
        "here's what i can do",
        "i can assist with"
    ]
    
    # Phrases that indicate capability menu (ILLEGAL after first turn)
    CAPABILITY_INDICATORS = [
        "i can help you with",
        "i'm able to",
        "my capabilities",
        "what i can do",
        "i'm here to",
        "i support",
        "i'm designed to"
    ]
    
    # Phrases that indicate lack of context awareness (ALWAYS ILLEGAL if context exists)
    CONTEXT_AMNESIA_INDICATORS = [
        "i don't have context",
        "i'm not sure what we discussed",
        "i can't recall",
        "i don't remember",
        "could you remind me",
        "what were we talking about",
        "i don't have access to our previous",
        "i can't see our earlier",
        "no prior context"
    ]
    
    def __init__(self):
        self.enforcement_count = 0
        self.rejection_count = 0
    
    def enforce(
        self,
        response_text: str,
        context_pack,  # ContextPack object
        conversation_state: Dict[str, Any]
    ) -> EnforcementResult:
        """
        ENFORCE STATE LAW ON A RESPONSE.
        
        This is the FINAL CHECK before any response is returned.
        If this returns is_legal=False, the response MUST BE REJECTED.
        
        Args:
            response_text: The LLM-generated response to validate
            context_pack: The ContextPack (source of truth)
            conversation_state: Current conversation state
        
        Returns:
            EnforcementResult with legality and required behavior
        """
        self.enforcement_count += 1
        
        violations = []
        must_reference = []
        topic_to_continue = ""
        required_behavior = "continue"
        
        # Extract state
        is_first_turn = self._is_first_turn(context_pack, conversation_state)
        current_topic = self._get_current_topic(context_pack, conversation_state)
        previous_topic = self._get_previous_topic(context_pack, conversation_state)
        pending_action = self._get_pending_action(context_pack, conversation_state)
        phase = self._get_phase(context_pack, conversation_state)
        
        response_lower = response_text.lower()
        
        # ================================================================
        # LAW 1: CONTEXT AMNESIA IS ALWAYS ILLEGAL (if context exists)
        # ================================================================
        if current_topic or previous_topic:
            for indicator in self.CONTEXT_AMNESIA_INDICATORS:
                if indicator in response_lower:
                    violations.append(ResponseViolation.CONTEXT_RESET)
                    logger.warning(f"⚖️ VIOLATION: Context amnesia detected when topic exists")
                    break
        
        # ================================================================
        # LAW 2: GREETING/RESET RESPONSES ARE ILLEGAL AFTER FIRST TURN
        # ================================================================
        if not is_first_turn:
            for indicator in self.RESET_INDICATORS:
                if indicator in response_lower:
                    violations.append(ResponseViolation.GREETING_MID_CONVERSATION)
                    logger.warning(f"⚖️ VIOLATION: Reset/greeting mid-conversation")
                    break
            
            for indicator in self.CAPABILITY_INDICATORS:
                if indicator in response_lower:
                    violations.append(ResponseViolation.CAPABILITY_MENU)
                    logger.warning(f"⚖️ VIOLATION: Capability menu mid-conversation")
                    break
        
        # ================================================================
        # LAW 3: IF TOPIC EXISTS, RESPONSE MUST ACKNOWLEDGE IT
        # ================================================================
        active_topic = current_topic or previous_topic
        if active_topic and not is_first_turn:
            topic_to_continue = active_topic
            must_reference.append(active_topic)
            
            # Check if response mentions the topic at all
            topic_words = active_topic.lower().replace('_', ' ').split()
            topic_mentioned = any(word in response_lower for word in topic_words if len(word) > 3)
            
            # Generic responses that don't mention topic are violations
            if not topic_mentioned and len(response_text) < 200:
                # Short responses that don't mention topic are suspicious
                if any(indicator in response_lower for indicator in self.RESET_INDICATORS):
                    violations.append(ResponseViolation.TOPIC_IGNORED)
                    logger.warning(f"⚖️ VIOLATION: Topic '{active_topic}' ignored in response")
        
        # ================================================================
        # LAW 4: PENDING ACTION MUST BE ADDRESSED
        # ================================================================
        if pending_action:
            action_type = pending_action.get('type', '')
            must_reference.append(f"pending:{action_type}")
            
            # If response is generic and doesn't address the action
            if any(indicator in response_lower for indicator in self.RESET_INDICATORS):
                violations.append(ResponseViolation.PENDING_ACTION_IGNORED)
                logger.warning(f"⚖️ VIOLATION: Pending action '{action_type}' ignored")
        
        # ================================================================
        # LAW 5: GENERIC FALLBACK IS ILLEGAL WHEN CONTEXT EXISTS
        # ================================================================
        if (current_topic or previous_topic or pending_action) and not is_first_turn:
            # Check for extremely generic responses
            generic_patterns = [
                r"^(hey|hi|hello)[\s!.,]*",
                r"it seems like you",
                r"something on your mind",
                r"what.*would you like",
                r"how can i (help|assist)",
            ]
            
            for pattern in generic_patterns:
                if re.search(pattern, response_lower):
                    violations.append(ResponseViolation.GENERIC_FALLBACK)
                    logger.warning(f"⚖️ VIOLATION: Generic fallback when context exists")
                    break
        
        # ================================================================
        # DETERMINE REQUIRED BEHAVIOR
        # ================================================================
        if pending_action:
            required_behavior = f"complete_action:{pending_action.get('type', 'unknown')}"
        elif active_topic:
            required_behavior = f"continue_topic:{active_topic}"
        elif is_first_turn:
            required_behavior = "welcome"
        else:
            required_behavior = "continue_conversation"
        
        # ================================================================
        # FINAL JUDGMENT
        # ================================================================
        is_legal = len(violations) == 0
        
        if not is_legal:
            self.rejection_count += 1
            rejection_reason = f"Response violates {len(violations)} state laws: {[v.value for v in violations]}"
            logger.error(f"⚖️ RESPONSE REJECTED: {rejection_reason}")
        else:
            rejection_reason = ""
            logger.debug(f"⚖️ Response is legal")
        
        return EnforcementResult(
            is_legal=is_legal,
            violations=violations,
            required_behavior=required_behavior,
            topic_to_continue=topic_to_continue,
            must_reference=must_reference,
            rejection_reason=rejection_reason
        )
    
    def get_continuation_prompt(
        self,
        enforcement_result: EnforcementResult,
        original_message: str
    ) -> str:
        """
        Generate a prompt that FORCES continuation behavior.
        
        This is used when the original response was REJECTED.
        The agent MUST use this prompt to regenerate.
        """
        topic = enforcement_result.topic_to_continue
        behavior = enforcement_result.required_behavior
        
        if topic:
            return f"""CRITICAL INSTRUCTION (STATE ENFORCEMENT):
The student is in an ACTIVE conversation about: {topic}
Their last message was: "{original_message}"

You MUST:
1. Continue the {topic} discussion naturally
2. Reference what was discussed before
3. NOT ask generic "how can I help" questions
4. NOT reset the conversation
5. NOT pretend you don't know the context

Respond as if you remember the full conversation about {topic}."""
        else:
            return f"""CRITICAL INSTRUCTION (STATE ENFORCEMENT):
This is NOT the first turn. The student said: "{original_message}"

You MUST:
1. Respond to their message directly
2. NOT ask "what can I help you with"
3. NOT give a generic greeting
4. Continue naturally as a friend would

Respond appropriately to what they said."""
    
    def get_stats(self) -> Dict[str, int]:
        """Get enforcement statistics"""
        return {
            "total_enforcements": self.enforcement_count,
            "total_rejections": self.rejection_count,
            "rejection_rate": self.rejection_count / max(1, self.enforcement_count)
        }
    
    # ================================================================
    # HELPER METHODS
    # ================================================================
    
    def _is_first_turn(self, context_pack, conversation_state: Dict) -> bool:
        """Determine if this is truly the first turn"""
        if context_pack and hasattr(context_pack, 'is_first_turn'):
            return context_pack.is_first_turn
        return conversation_state.get('conversation_phase') == 'first_turn'
    
    def _get_current_topic(self, context_pack, conversation_state: Dict) -> str:
        """Get current topic from context"""
        if context_pack and hasattr(context_pack, 'current_topic'):
            return context_pack.current_topic or ""
        return conversation_state.get('last_topic', '')
    
    def _get_previous_topic(self, context_pack, conversation_state: Dict) -> str:
        """Get previous topic from context"""
        if context_pack and hasattr(context_pack, 'previous_topic'):
            return context_pack.previous_topic or ""
        return ""
    
    def _get_pending_action(self, context_pack, conversation_state: Dict) -> Optional[Dict]:
        """Get pending action from context"""
        if context_pack and hasattr(context_pack, 'pending_action'):
            return context_pack.pending_action
        return conversation_state.get('pending_action')
    
    def _get_phase(self, context_pack, conversation_state: Dict) -> str:
        """Get conversation phase"""
        if context_pack and hasattr(context_pack, 'conversation_phase'):
            return context_pack.conversation_phase
        return conversation_state.get('conversation_phase', 'active')


# Singleton instance
_state_enforcer: Optional[StateEnforcer] = None


def get_state_enforcer() -> StateEnforcer:
    """Get singleton StateEnforcer instance"""
    global _state_enforcer
    if _state_enforcer is None:
        _state_enforcer = StateEnforcer()
        logger.info("⚖️ StateEnforcer initialized - STATE IS NOW LAW")
    return _state_enforcer

