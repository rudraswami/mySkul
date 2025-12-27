"""
💪 MOTIVATION AGENT - TRUE AGENTIC EMOTIONAL MENTOR
====================================================

A TRUE agentic motivation coach that:
1. REASONS about student emotional state using LLM (not keywords)
2. UNDERSTANDS why the student feels demotivated (context, not patterns)
3. ADAPTS tone and depth based on:
   - Recent interactions and conversation history
   - Study load and exam proximity
   - Past motivational effectiveness (memory)
4. RESPONDS like a human mentor: calm, reassuring, non-judgmental
5. MAINTAINS continuity (remembers what helped before)

IMPLEMENTATION:
- Uses ReAct loop from parent class (Think → Act → Observe)
- LLM-based emotional understanding via get_agent_persona()
- Memory integration for personalization
- NO keyword patterns, NO hardcoded templates

Philosophy: Real coaching, not cringe motivation. Treat student as "my own student".
"""

import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum

from agents.core.react_agent import ReActAgent, AgentState
from agents.core.tool_registry import create_tool_registry

logger = logging.getLogger(__name__)

# Debug flag
MOTIVATION_DEBUG = os.getenv("MOTIVATION_DEBUG", "false").lower() == "true"


# =============================================================================
# COACHING MODES (For Legacy Compatibility + Observability)
# =============================================================================
# Note: These are now INFERRED by the LLM during reasoning, not pattern-matched

class CoachingMode(str, Enum):
    """Coaching modes - inferred by LLM reasoning, not pattern matching"""
    CALM_DOWN = "calm_down"       # Exam stress, anxiety, panic
    CONSISTENCY = "consistency"   # Procrastination, discipline issues
    CONFIDENCE = "confidence"     # Low self-esteem, imposter syndrome
    BURNOUT = "burnout"          # Fatigue, overload, exhaustion
    GOAL_LOCK = "goal_lock"      # Help pick next step, make micro-plan
    CELEBRATE = "celebrate"      # Positive reinforcement
    GENERAL = "general"          # Conversational support


# =============================================================================
# MOTIVATION AGENT - TRUE AGENTIC EMOTIONAL MENTOR
# =============================================================================

class MotivationAgent(ReActAgent):
    """
    TRUE Agentic Motivation Coach using ReAct loop.
    
    ARCHITECTURE (matches MentorAgent/ProfessorAgent):
    - Uses parent's ReAct loop for multi-step reasoning
    - LLM-based emotional understanding (not keyword patterns)
    - Context-aware persona that adapts to student state
    - Memory integration for personalized support
    - NO hardcoded templates - all responses are LLM-generated
    
    REASONING FLOW:
    1. THINK: Understand emotional state from context + message
    2. ACT: Use tools (memory, progress) to gather personalization data
    3. OBSERVE: Learn what has helped this student before
    4. RESPOND: Generate empathetic, actionable, contextual response
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Initialize tool registry with motivation-relevant tools
        self.tool_registry = create_tool_registry(include_default=True)
        
        # Register Study Planner Tool for goal-setting support
        from agents.core.tools.planner import StudyPlannerTool
        self.tool_registry.register(StudyPlannerTool())
        
        logger.info("💪 MotivationAgent initialized as TRUE ReAct agent (LLM-based reasoning)")
    
    def get_agent_name(self) -> str:
        return "MotivationAgent"
    
    def get_agent_persona(self, context: dict = None) -> str:
        """
        Return context-aware persona for emotional mentoring.
        
        Unlike pattern-matching, this persona guides the LLM to:
        1. REASON about the student's emotional state
        2. UNDERSTAND underlying causes (not surface keywords)
        3. ADAPT response based on what's known about this student
        """
        context = context or {}
        student_profile = context.get('student_profile', {})
        student_name = student_profile.get('user_name', 'student')
        exam_mode = context.get('exam_mode', 'General')
        
        # Build context-aware instructions
        memory_context = ""
        if context.get('memory_context'):
            mem = context.get('memory_context', {})
            if mem.get('past_struggles'):
                memory_context += f"\nPast struggles: {mem.get('past_struggles')}"
            if mem.get('what_helped_before'):
                memory_context += f"\nWhat helped before: {mem.get('what_helped_before')}"
            if mem.get('streak'):
                memory_context += f"\nCurrent streak: {mem.get('streak')} days"
        
        return f"""You are a caring, experienced emotional mentor who treats every student as your own child.

## YOUR CORE IDENTITY
You are NOT a generic motivational speaker. You are:
- A wise mentor who has guided thousands of students through tough times
- Warm and empathetic, but also practical and action-oriented
- Someone who believes in small wins that build momentum
- Never dismissive of feelings, never rushing to solutions

## EMOTIONAL REASONING PROCESS
Before responding, THINK step-by-step:
1. **What is this student actually feeling?** (not keywords, but underlying emotion)
2. **WHY might they feel this way?** (exam pressure? fatigue? self-doubt? overwhelm?)
3. **What does this specific student need right now?** (validation? direction? rest? small win?)
4. **What has worked for them before?** (use memory_recall tool if available)
5. **What's the ONE thing that will help them most in this moment?**

## STUDENT CONTEXT
- Name: {student_name}
- Exam Mode: {exam_mode}
{memory_context}

## RESPONSE PRINCIPLES

### First: Acknowledge (1-2 sentences max)
- Validate their feeling without dismissing or exaggerating
- Show you understand the specific situation, not generic empathy
- Use their name naturally if known

### Then: Reframe (brief)
- Help them see the situation constructively
- Use data from progress_tracker if available (accuracy, streak)
- Never toxic positivity - be realistic and honest

### Finally: Small Action (3 steps max)
- Give them ONE clear thing to do right now
- Make it achievable in the next 15-30 minutes
- End with a check-in question to keep dialogue open

## OUTPUT FORMAT
- Keep it conversational, like a WhatsApp message from a caring friend
- NO walls of text - students are already overwhelmed
- NO generic motivational quotes
- NO lecturing or preaching
- Markdown for emphasis, but sparingly
- End with a question to show you care about their response

## TOOL USAGE
- Use **memory_recall** to understand this student's history
- Use **progress_tracker** to get concrete data for reframing (streak, accuracy)
- Use **study_planner** ONLY if they explicitly need direction on what to study

## WHAT NEVER TO DO
- Don't use phrases like "I understand how you feel" without specifics
- Don't give 10-step plans when they're overwhelmed
- Don't dismiss fatigue by pushing harder
- Don't use cringe motivation like "You've got this!" without substance
- Don't pretend everything is fine when they're struggling

## COACHING MODES (for your reasoning)
Based on your analysis, the student may be experiencing:
- **Anxiety/Stress**: Needs calming, grounding, perspective
- **Burnout**: Needs permission to rest, not more work
- **Self-doubt**: Needs evidence of their progress, not just reassurance
- **Overwhelm**: Needs ONE priority, not a full plan
- **Procrastination**: Needs tiny first step, no guilt
- **Victory**: Needs celebration and momentum-building

Choose your approach based on what they NEED, not what they SAY."""

    def get_available_tools(self, context: dict = None) -> List[str]:
        """Return tools for emotional mentoring"""
        return [
            "memory_recall",      # Get student history, past struggles, what helped
            "progress_tracker",   # Get concrete data for reframing (streak, accuracy)
            "study_planner",      # For goal-lock situations only
        ]
    
    async def process(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process emotional support request using TRUE ReAct loop.
        
        This method:
        1. Enriches context with any available memory
        2. Delegates to parent's ReAct loop for reasoning
        3. Formats the output for emotional support use case
        """
        try:
            user_id = context.get('user_id', '')
            
            logger.info(f"💪 [MotivationAgent] Processing (TRUE AGENTIC): {query[:80]}...")
            
            # Enrich context with memory if available
            enriched_context = await self._enrich_context_with_memory(context, user_id)
            
            # =================================================================
            # 🚀 USE PARENT's ReAct LOOP - TRUE REASONING
            # =================================================================
            # This is the key difference from the old implementation.
            # Instead of pattern matching + templates, we use the full
            # ReAct loop that THINKS, ACTS, OBSERVES, and REASONS.
            result = await super().run(query, enriched_context)
            
            # Infer coaching mode from response for observability
            inferred_mode = self._infer_coaching_mode_from_response(result.get('content', ''))
            
            # Format for emotional support output structure
            return self._format_motivation_response(result, inferred_mode)
            
        except Exception as e:
            logger.error(f"❌ MotivationAgent failed: {e}", exc_info=True)
            return self._fallback_response(query, str(e))
    
    async def _enrich_context_with_memory(
        self,
        context: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Enrich context with memory for personalized emotional support.
        
        This runs BEFORE the ReAct loop to give the agent relevant
        history about what has helped this student before.
        """
        enriched = dict(context)
        
        try:
            # Try to get memory context
            if self.tool_registry:
                memory_tool = self.tool_registry.get_tool('memory_recall')
                if memory_tool:
                    result = await memory_tool.execute(
                        query="emotional_history, past_struggles, what_helped_before, streak, weak_topics",
                        user_id=user_id,
                        context=context
                    )
                    if result.success and result.data:
                        enriched['memory_context'] = result.data
                        logger.debug(f"[MotivationAgent] Enriched with memory context")
        except Exception as e:
            logger.debug(f"[MotivationAgent] Memory enrichment skipped: {e}")
        
        return enriched
    
    def _infer_coaching_mode_from_response(self, content: str) -> str:
        """
        Infer coaching mode from LLM response for observability.
        
        This is ONLY for logging/metrics - NOT for response generation.
        The response is already generated by the ReAct loop.
        """
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['breath', 'calm', 'relax', 'anxiety', 'stress']):
            return CoachingMode.CALM_DOWN.value
        elif any(word in content_lower for word in ['rest', 'break', 'tired', 'exhausted', 'burnout']):
            return CoachingMode.BURNOUT.value
        elif any(word in content_lower for word in ['proud', 'great job', 'congrat', 'celebrate', 'amazing']):
            return CoachingMode.CELEBRATE.value
        elif any(word in content_lower for word in ['15 minutes', 'start small', 'just begin', 'first step']):
            return CoachingMode.CONSISTENCY.value
        elif any(word in content_lower for word in ['you can', 'proof', 'evidence', 'progress', 'streak']):
            return CoachingMode.CONFIDENCE.value
        elif any(word in content_lower for word in ['priority', 'focus on', 'one thing', 'next step']):
            return CoachingMode.GOAL_LOCK.value
        else:
            return CoachingMode.GENERAL.value
    
    def _format_motivation_response(
        self,
        result: Dict[str, Any],
        inferred_mode: str
    ) -> Dict[str, Any]:
        """Format ReAct result for emotional support output structure"""
        content = result.get('content', '')
        
        return {
            "response": {
                "default_view": {
                    "main_content": {
                        "content": content,
                        "type": "markdown"
                    }
                }
            },
            "main_response": content,
            "metadata": {
                "agent_name": "MotivationAgent",
                "coaching_mode": inferred_mode,
                "tools_used": result.get('tools_used', []),
                "iterations": result.get('iterations', 0),
                "reasoning_steps": result.get('metadata', {}).get('reasoning_steps', 0)
            },
            "motivation": {
                "type": inferred_mode,
                "message": content[:200] if content else "",
            },
            "orchestration": {
                "primary_agent": "MotivationAgent",
            }
        }
    
    def _fallback_response(self, query: str, error: str) -> Dict[str, Any]:
        """Fallback response when agent fails"""
        return {
            "response": {
                "default_view": {
                    "main_content": {
                        "content": "Hey, I'm here for you. Tell me more about what's going on — I want to help.",
                        "type": "markdown"
                    }
                }
            },
            "main_response": "Hey, I'm here for you. Tell me more about what's going on — I want to help.",
            "metadata": {
                "agent_name": "MotivationAgent",
                "error": error,
                "fallback": True
            }
        }
    
    # Alias run -> process for compatibility with orchestrator
    async def run(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for process() to maintain interface compatibility"""
        return await self.process(query, context)
    
    # =========================================================================
    # LEGACY INTERFACE (for backward compatibility with supervisor.py)
    # =========================================================================
    
    def detect_emotional_state(self, query: str) -> Optional[str]:
        """
        LEGACY: Detect emotional state from query.
        
        Now uses LLM-inferred mode instead of pattern matching.
        For sync contexts, returns a simple heuristic-based detection.
        """
        # Simple heuristic for sync detection (non-blocking)
        query_lower = query.lower()
        
        # These are NOT for response generation - just for legacy interface
        if any(word in query_lower for word in ['panic', 'scared', 'stress', 'anxious', 'nervous']):
            return CoachingMode.CALM_DOWN.value
        elif any(word in query_lower for word in ['tired', 'exhausted', 'burnout', 'overwhelmed']):
            return CoachingMode.BURNOUT.value
        elif any(word in query_lower for word in ['did it', 'passed', 'finally', 'happy', 'excited']):
            return CoachingMode.CELEBRATE.value
        elif any(word in query_lower for word in ['dumb', 'stupid', 'can\'t', 'hopeless']):
            return CoachingMode.CONFIDENCE.value
        elif any(word in query_lower for word in ['lazy', 'procrastinat', 'distracted']):
            return CoachingMode.CONSISTENCY.value
        elif any(word in query_lower for word in ['where to start', 'what to do', 'help me plan']):
            return CoachingMode.GOAL_LOCK.value
        elif any(word in query_lower for word in ['feeling', 'sad', 'demotivated', 'low']):
            return CoachingMode.GENERAL.value
        
        return None
    
    def enhance_response(
        self,
        result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        LEGACY: Enhance a response with emotional support elements.
        
        Maintained for backward compatibility with supervisor.py middleware.
        """
        try:
            query = result.get('query', context.get('original_query', ''))
            
            detected_state = self.detect_emotional_state(query)
            
            if not detected_state:
                return {'motivation': None}
            
            logger.info(f"💪 [Motivation] enhance: mode={detected_state}")
            
            return {
                'motivation': {
                    'type': detected_state,
                    'message': f"Coaching mode: {detected_state}",
                    'action': {
                        'type': detected_state,
                        'label': f'{detected_state.replace("_", " ").title()} Mode',
                        'icon': self._get_mode_icon(detected_state)
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Motivation enhancement failed: {e}")
            return {'motivation': None}
    
    def _get_mode_icon(self, mode_value: str) -> str:
        """Get icon for coaching mode"""
        icons = {
            'calm_down': "🧘",
            'consistency': "⏰",
            'confidence': "💪",
            'burnout': "☕",
            'goal_lock': "🎯",
            'celebrate': "🎉",
            'general': "💬",
        }
        return icons.get(mode_value, "💬")
    
    def get_opening_for_state(self, emotional_state: str, name: str = '') -> str:
        """LEGACY: Get an appropriate opening based on emotional state"""
        greeting = f"Hey {name}! " if name and len(name) > 1 else "Hey! "
        
        # These are ONLY for legacy callers - new flow uses LLM
        openings = {
            'calm_down': f"{greeting}Take a breath — we'll figure this out together.",
            'consistency': f"{greeting}Starting is the hardest part — let's make it easy.",
            'confidence': f"{greeting}I know it feels hard, but you've got more in you than you think.",
            'burnout': f"{greeting}Your brain needs rest too — that's not weakness, it's science.",
            'goal_lock': f"{greeting}Let's cut through the noise and find your next step.",
            'celebrate': f"{greeting}This is what progress looks like! 🎉",
            'general': f"{greeting}I'm here for you.",
            # Legacy mappings for old state names
            'bored': f"{greeting}Let's make this more interesting!",
            'frustrated': f"{greeting}I get it — let's try a different angle.",
            'anxious': f"{greeting}Take a breath — we'll figure this out together.",
            'excited': f"{greeting}Love the energy! Let's channel it! 🚀",
            'confident': f"{greeting}You're on fire! Keep it going! 🔥",
        }
        
        return openings.get(emotional_state, greeting)


# =============================================================================
# INTEGRATION HELPERS (for backward compatibility)
# =============================================================================

def should_trigger_motivation(query: str) -> bool:
    """Check if query indicates need for emotional support"""
    agent = MotivationAgent({})
    detected = agent.detect_emotional_state(query)
    return detected is not None


def get_motivation_enhancement(query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get motivation enhancement for a query"""
    agent = MotivationAgent({})
    fake_result = {'query': query}
    return agent.enhance_response(fake_result, context or {})
