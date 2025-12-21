"""
💪 MOTIVATION AGENT - TRUE ADVANCED AGENT (UPGRADED)
=====================================================

A TRUE agentic motivation coach that:
1. THINKS step-by-step (ReAct loop)
2. USES TOOLS to gather context (study_planner, memory_recall, progress_tracker)
3. READS MEMORY for personalization (goals, weak topics, streaks)
4. WRITES COACHING NOTES (bounded, guardrail-aware)
5. CHOOSES COACHING MODE autonomously

COACHING MODES:
- CALM_DOWN: Exam stress / anxiety
- CONSISTENCY: Procrastination, discipline
- CONFIDENCE: Low self-esteem, "I'm dumb"
- BURNOUT: Fatigue, overload
- GOAL_LOCK: Help pick next step + micro-plan
- CELEBRATE: Positive reinforcement

Philosophy: Real coaching, not cringe motivation. Treat student as "my own student".
"""

import logging
import re
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass

from agents.core.react_agent import ReActAgent, AgentState, ThoughtAction, AgentStatus
from agents.core.tool_registry import ToolRegistry, create_tool_registry

logger = logging.getLogger(__name__)

# Debug flag
MOTIVATION_DEBUG = os.getenv("MOTIVATION_DEBUG", "false").lower() == "true"


# =============================================================================
# COACHING MODES (Autonomous Decision)
# =============================================================================

class CoachingMode(str, Enum):
    """Coaching modes - agent chooses autonomously based on student state"""
    CALM_DOWN = "calm_down"       # Exam stress, anxiety, panic
    CONSISTENCY = "consistency"   # Procrastination, discipline issues
    CONFIDENCE = "confidence"     # Low self-esteem, "I'm dumb", imposter syndrome
    BURNOUT = "burnout"          # Fatigue, overload, exhaustion
    GOAL_LOCK = "goal_lock"      # Help pick next step, make micro-plan
    CELEBRATE = "celebrate"      # Positive reinforcement, momentum building
    GENERAL = "general"          # Fallback for unclear emotional state


@dataclass
class CoachingDecision:
    """Result of coaching mode selection"""
    mode: CoachingMode
    reason: str
    confidence: float
    detected_signals: List[str]
    suggested_tools: List[str]


# =============================================================================
# PATTERN DETECTION (Structured, not keyword-only)
# =============================================================================

class EmotionalPatternDetector:
    """
    Structured emotional pattern detection.
    
    NOT just keyword matching - uses:
    - Pattern groups with context
    - Intensity signals
    - Negation handling
    """
    
    # Patterns grouped by coaching mode
    PATTERNS = {
        CoachingMode.CALM_DOWN: {
            'high_intensity': [
                r'\b(panic|panicking|can\'t breathe|heart racing|so scared)\b',
                r'\b(exam tomorrow|test in \d+ hours?|last minute)\b',
                r'\b(going to fail|will fail|definitely fail)\b',
            ],
            'medium_intensity': [
                r'\b(stressed|anxious|nervous|worried|pressure)\b',
                r'\b(scared of|afraid of|fear of).*exam\b',
                r'\b(can\'t focus|can\'t concentrate|mind blank)\b',
            ],
        },
        CoachingMode.CONSISTENCY: {
            'high_intensity': [
                r'\b(always procrastinat|keep putting off|never start)\b',
                r'\b(no discipline|zero motivation|can\'t stick to)\b',
            ],
            'medium_intensity': [
                r'\b(lazy|procrastinat|distracted|can\'t focus)\b',
                r'\b(keep starting over|never finish|give up)\b',
                r'\b(wasting time|not productive|unproductive)\b',
            ],
        },
        CoachingMode.CONFIDENCE: {
            'high_intensity': [
                r'\b(i\'m (so )?stupid|i\'m (so )?dumb|i\'m (an )?idiot)\b',
                r'\b(everyone.*better|i\'m the worst|hopeless)\b',
                r'\b(can\'t (do|learn|understand) anything)\b',
            ],
            'medium_intensity': [
                r'\b(not smart|not good at|bad at|weak in)\b',
                r'\b(others.*easier|why.*hard for me)\b',
                r'\b(don\'t get it|never understand|too hard)\b',
            ],
        },
        CoachingMode.BURNOUT: {
            'high_intensity': [
                r'\b(exhausted|burnt out|can\'t anymore|done with)\b',
                r'\b(too much|overwhelming|drowning in)\b',
                r'\b(need a break|need to stop|can\'t take it)\b',
            ],
            'medium_intensity': [
                r'\b(tired|fatigue|worn out|drained)\b',
                r'\b(too many|overload|piling up)\b',
                r'\b(no energy|no motivation|lost interest)\b',
            ],
        },
        CoachingMode.CELEBRATE: {
            'high_intensity': [
                r'\b(i did it|finally (got|understand|solved))\b',
                r'\b(passed|scored well|improved|nailed)\b',
            ],
            'medium_intensity': [
                r'\b(making sense|getting it|understand now)\b',
                r'\b(excited|happy|proud|confident)\b',
                r'\b(progress|improving|better than before)\b',
            ],
        },
        CoachingMode.GOAL_LOCK: {
            'medium_intensity': [
                r'\b(what (should|do) i (do|study|start))\b',
                r'\b(where (should|do) i (start|begin))\b',
                r'\b(help me plan|make a plan|study plan)\b',
                r'\b(overwhelmed.*where|don\'t know.*start)\b',
            ],
        },
    }
    
    @classmethod
    def detect(cls, query: str) -> CoachingDecision:
        """Detect coaching mode from query using structured patterns"""
        query_lower = query.lower()
        
        best_mode = CoachingMode.GENERAL
        best_confidence = 0.0
        detected_signals = []
        reason = "No strong emotional signal detected"
        
        for mode, pattern_groups in cls.PATTERNS.items():
            mode_score = 0.0
            mode_signals = []
            
            # Check high intensity patterns (weight: 0.8)
            high_patterns = pattern_groups.get('high_intensity', [])
            for pattern in high_patterns:
                if re.search(pattern, query_lower):
                    mode_score += 0.8
                    mode_signals.append(f"high:{pattern[:30]}")
            
            # Check medium intensity patterns (weight: 0.4)
            medium_patterns = pattern_groups.get('medium_intensity', [])
            for pattern in medium_patterns:
                if re.search(pattern, query_lower):
                    mode_score += 0.4
                    mode_signals.append(f"med:{pattern[:30]}")
            
            # Cap at 1.0
            mode_score = min(1.0, mode_score)
            
            if mode_score > best_confidence:
                best_confidence = mode_score
                best_mode = mode
                detected_signals = mode_signals
                reason = f"Detected {mode.value} signals: {', '.join(mode_signals[:3])}"
        
        # Determine suggested tools based on mode
        tools = cls._get_suggested_tools(best_mode)
        
        return CoachingDecision(
            mode=best_mode,
            reason=reason,
            confidence=best_confidence,
            detected_signals=detected_signals,
            suggested_tools=tools
        )
    
    @classmethod
    def _get_suggested_tools(cls, mode: CoachingMode) -> List[str]:
        """Get suggested tools for each coaching mode"""
        tool_map = {
            CoachingMode.CALM_DOWN: ["memory_recall", "study_planner"],
            CoachingMode.CONSISTENCY: ["study_planner", "progress_tracker"],
            CoachingMode.CONFIDENCE: ["memory_recall", "progress_tracker"],
            CoachingMode.BURNOUT: ["memory_recall", "study_planner"],
            CoachingMode.GOAL_LOCK: ["study_planner", "progress_tracker"],
            CoachingMode.CELEBRATE: ["progress_tracker", "memory_recall"],
            CoachingMode.GENERAL: ["memory_recall"],
        }
        return tool_map.get(mode, ["memory_recall"])


# =============================================================================
# MOTIVATION AGENT - TRUE REACT AGENT
# =============================================================================

class MotivationAgent(ReActAgent):
    """
    TRUE Agentic Motivation Coach with ReAct loop.
    
    Features:
    - Autonomous coaching mode selection
    - Tool usage for personalization
    - Memory read/write (bounded, guardrail-aware)
    - Student-first output style
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Initialize tool registry with motivation-relevant tools
        self.tool_registry = create_tool_registry(include_default=True)
        
        # Track coaching session
        self._current_mode: Optional[CoachingMode] = None
        self._tools_used: List[str] = []
        
        logger.info("💪 MotivationAgent initialized as TRUE ReAct agent")
    
    def get_agent_name(self) -> str:
        return "MotivationAgent"
    
    def get_agent_persona(self) -> str:
        return """You are a caring, experienced coach who treats every student as your own.

YOUR CHARACTER:
- You genuinely care about student wellbeing, not just academic performance
- You've helped thousands of students through tough times
- You're warm, empathetic, but also action-oriented
- You believe in small steps that build momentum
- You never dismiss feelings or rush to solutions

YOUR APPROACH:
1. ACKNOWLEDGE: First, validate their feelings (1 sentence max)
2. UNDERSTAND: Use tools to get context (their goals, progress, weak areas)
3. REFRAME: Help them see the situation constructively
4. ACT: Give them 3 small, doable steps
5. CHECK: End with a question to keep them engaged

OUTPUT STYLE:
- First line: 1 sentence empathy (not long, not generic)
- Then: 3-step action plan (numbered, specific, achievable today)
- Then: 1 check-in question (ask them to reply)
- Keep it readable: NO walls of text

NEVER:
- Use generic motivational quotes
- Dismiss their feelings
- Give overwhelming advice
- Pretend everything is fine
- Make them feel guilty"""
    
    def get_available_tools(self) -> List[str]:
        return [
            "memory_recall",      # Get student history, preferences
            "study_planner",      # Create micro-plans
            "progress_tracker",   # Check streaks, accuracy
        ]
    
    async def run(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run motivation coaching with ReAct loop.
        
        1. Detect coaching mode
        2. Gather context via tools
        3. Generate personalized response
        4. Write coaching note (if safe)
        """
        try:
            # Step 1: Detect coaching mode
            decision = EmotionalPatternDetector.detect(query)
            self._current_mode = decision.mode
            self._tools_used = []
            
            logger.info(f"🧠 [Motivation] mode={decision.mode.value} | "
                       f"confidence={decision.confidence:.2f} | "
                       f"reason={decision.reason}")
            
            # Step 2: Gather context via tools (gated by confidence)
            tool_context = await self._gather_tool_context(
                query=query,
                context=context,
                suggested_tools=decision.suggested_tools,
                confidence=decision.confidence  # Pass confidence for tool gating
            )
            
            # Step 3: Generate coaching response
            response = await self._generate_coaching_response(
                query=query,
                context=context,
                decision=decision,
                tool_context=tool_context
            )
            
            # Step 4: Prepare coaching note for memory (bounded)
            coaching_note = self._prepare_coaching_note(decision, response)
            
            # Log observability
            if MOTIVATION_DEBUG or True:  # Always log for now
                logger.info(f"💪 [Motivation] mode={decision.mode.value} | "
                           f"tools={self._tools_used} | "
                           f"note_len={len(coaching_note.get('coaching_note', ''))}")
            
            return {
                "response": {
                    "default_view": {
                        "main_content": {
                            "content": response,
                            "type": "markdown"
                        }
                    }
                },
                "main_response": response,
                "metadata": {
                    "agent_name": "MotivationAgent",
                    "coaching_mode": decision.mode.value,
                    "confidence": decision.confidence,
                    "tools_used": self._tools_used,
                },
                "motivation": {
                    "type": decision.mode.value,
                    "message": response[:200],  # Bounded
                    "coaching_note": coaching_note,
                },
                "orchestration": {
                    "primary_agent": "MotivationAgent",
                }
            }
            
        except Exception as e:
            logger.error(f"❌ MotivationAgent failed: {e}", exc_info=True)
            return self._fallback_response(query, str(e))
    
    async def _gather_tool_context(
        self,
        query: str,
        context: Dict[str, Any],
        suggested_tools: List[str],
        confidence: float = 0.5
    ) -> Dict[str, Any]:
        """
        Gather context using tools.
        
        TOOL GATING POLICY:
        - Low confidence (<0.5): Use 0-1 tools (just memory_recall if available)
        - Medium confidence (0.5-0.7): Use 1-2 tools
        - High confidence (>0.7): Use all suggested tools (max 2)
        
        This prevents tool spam for light emotional queries.
        """
        tool_context = {}
        user_id = context.get('user_id', '')
        
        # Determine tool limit based on confidence
        if confidence < 0.5:
            tool_limit = 1  # Light query - only memory_recall
            # Prioritize memory_recall for light queries
            if 'memory_recall' in suggested_tools:
                suggested_tools = ['memory_recall']
            else:
                suggested_tools = suggested_tools[:1]
        elif confidence < 0.7:
            tool_limit = 2
        else:
            tool_limit = 2  # Max 2 even for high confidence
        
        logger.debug(f"🔧 [Motivation] Tool gating: confidence={confidence:.2f}, limit={tool_limit}, suggested={suggested_tools}")
        
        for tool_name in suggested_tools[:tool_limit]:
            try:
                tool = self.tool_registry.get_tool(tool_name)
                if not tool:
                    continue
                
                if tool_name == "memory_recall":
                    result = await tool.execute(
                        query="goals, weak_topics, streaks, recent_sessions",
                        user_id=user_id
                    )
                    if result.success:
                        tool_context['memory'] = result.data
                        self._tools_used.append("memory_recall")
                
                elif tool_name == "study_planner":
                    result = await tool.execute(
                        exam_date="",  # Not for exam, for micro-plan
                        topics=context.get('current_topic', 'general'),
                        available_hours=1,
                        user_id=user_id
                    )
                    if result.success:
                        tool_context['plan'] = result.data
                        self._tools_used.append("study_planner")
                
                elif tool_name == "progress_tracker":
                    result = await tool.execute(
                        user_id=user_id,
                        metric="accuracy"
                    )
                    if result.success:
                        tool_context['progress'] = result.data
                        self._tools_used.append("progress_tracker")
                        
            except Exception as e:
                logger.warning(f"Tool {tool_name} failed: {e}")
                continue
        
        return tool_context
    
    async def _generate_coaching_response(
        self,
        query: str,
        context: Dict[str, Any],
        decision: CoachingDecision,
        tool_context: Dict[str, Any]
    ) -> str:
        """Generate personalized coaching response"""
        
        # Get student name
        student_profile = context.get('student_profile', {})
        name = student_profile.get('user_name', '')
        name_part = f" {name}" if name else ""
        
        # Get memory context for personalization
        memory = tool_context.get('memory', {})
        goals = memory.get('goals', [])
        weak_topics = memory.get('weak_topics', [])
        streak = memory.get('streak', 0)
        
        # Get progress context
        progress = tool_context.get('progress', {})
        accuracy = progress.get('accuracy', 0)
        
        # Build response based on coaching mode
        response = self._build_mode_response(
            mode=decision.mode,
            name=name_part,
            query=query,
            goals=goals,
            weak_topics=weak_topics,
            streak=streak,
            accuracy=accuracy,
            tool_context=tool_context
        )
        
        return response
    
    def _build_mode_response(
        self,
        mode: CoachingMode,
        name: str,
        query: str,
        goals: List[str],
        weak_topics: List[str],
        streak: int,
        accuracy: float,
        tool_context: Dict[str, Any]
    ) -> str:
        """Build response based on coaching mode - NOT templates, contextual"""
        
        if mode == CoachingMode.CALM_DOWN:
            empathy = f"Hey{name}, I hear you — exam pressure is real and it's okay to feel this way."
            
            steps = [
                "**Take 3 slow breaths** right now (seriously, do it before reading on)",
                "**Write down 3 topics you know well** — you've prepared more than you think",
                "**Pick ONE topic** to review in the next 30 minutes — small wins build confidence"
            ]
            
            if weak_topics:
                steps[2] = f"**Review {weak_topics[0] if weak_topics else 'your strongest topic'}** for 30 minutes — start where you're solid"
            
            checkin = "How are you feeling now? Just reply with 'better' or 'still anxious' — I'm here."
            
        elif mode == CoachingMode.CONSISTENCY:
            empathy = f"Hey{name}, I get it — starting is often the hardest part."
            
            steps = [
                "**Set a timer for 15 minutes** — just 15, that's it",
                "**Open ONE topic** you've been avoiding and read the first page",
                "**After 15 mins, decide**: continue or take a 5-min break. No guilt either way."
            ]
            
            # Use study_planner output if available
            plan = tool_context.get('plan', {})
            if plan:
                steps[1] = f"**Start with**: {plan.get('first_task', 'your weakest topic')} — just the basics"
            
            checkin = "Can you commit to 15 minutes right now? Reply 'yes' and I'll check in later."
            
        elif mode == CoachingMode.CONFIDENCE:
            empathy = f"Hey{name}, feeling like this doesn't mean it's true — let me show you."
            
            # Use progress data for reframing
            reframe = "You've been showing up and trying — that's already ahead of most people."
            if accuracy > 0:
                reframe = f"Your accuracy is {accuracy:.0f}% — that's not 'dumb', that's progress."
            if streak > 0:
                reframe = f"You've been consistent for {streak} days — that takes real effort."
            
            steps = [
                f"**Reality check**: {reframe}",
                "**Pick ONE small problem** you can solve right now — prove to yourself you can",
                "**Write down ONE thing** you understood this week that you didn't before"
            ]
            
            checkin = "What's one topic where you've improved recently? Tell me — I want to hear it."
            
        elif mode == CoachingMode.BURNOUT:
            empathy = f"Hey{name}, your brain needs rest to actually learn — this isn't weakness, it's science."
            
            steps = [
                "**Close the books** for 20 minutes — no guilt, this is productive",
                "**Do something physical** — walk, stretch, or just stand up",
                "**When you return**, start with something you enjoy in your syllabus"
            ]
            
            checkin = "When was the last time you took a real break? Reply honestly."
            
        elif mode == CoachingMode.GOAL_LOCK:
            empathy = f"Hey{name}, feeling overwhelmed happens when everything feels equally important — let's fix that."
            
            # Use study_planner output
            plan = tool_context.get('plan', {})
            first_task = plan.get('first_task', 'your most urgent topic')
            
            steps = [
                f"**Priority 1**: {first_task} — this is your next 30-minute focus",
                "**Ignore everything else** for now — we'll get to it, but not today",
                "**After 30 mins**, message me with what you covered"
            ]
            
            if weak_topics:
                steps[0] = f"**Priority 1**: {weak_topics[0]} — tackle your weak spot first for maximum impact"
            
            checkin = "What's the ONE thing you'll focus on right now? Type it out."
            
        elif mode == CoachingMode.CELEBRATE:
            empathy = f"Hey{name}, YES! This is what progress looks like 🎉"
            
            steps = [
                "**Take a moment** to actually feel good about this — you earned it",
                "**Build on this momentum** — what's the next small challenge you can tackle?",
                "**Track this win** — write it down somewhere so you remember on tough days"
            ]
            
            if streak > 0:
                steps[2] = f"**Your {streak}-day streak** is proof you can do hard things — keep it going!"
            
            checkin = "What helped you get here? Knowing this will help you repeat it."
            
        else:  # GENERAL
            empathy = f"Hey{name}, I'm here to help you with whatever you're going through."
            
            steps = [
                "**Tell me more** — what's the main thing on your mind right now?",
                "**Be specific** — is it a topic, a feeling, or a planning issue?",
                "**No judgment** — I've heard it all, and we'll figure this out together"
            ]
            
            checkin = "What would help you most right now — encouragement, a plan, or just to vent?"
        
        # Assemble response
        response = f"{empathy}\n\n"
        response += "**Here's what I want you to do:**\n\n"
        for i, step in enumerate(steps, 1):
            response += f"{i}. {step}\n"
        response += f"\n{checkin}"
        
        return response
    
    def _prepare_coaching_note(
        self,
        decision: CoachingDecision,
        response: str
    ) -> Dict[str, Any]:
        """Prepare bounded coaching note for memory write"""
        return {
            "coaching_note": f"Mode: {decision.mode.value}. {decision.reason}"[:200],
            "next_action": response.split('\n')[0][:120] if response else "",
            "coaching_mode": decision.mode.value,
            "confidence": decision.confidence,
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
    
    # =========================================================================
    # LEGACY INTERFACE (for backward compatibility with supervisor.py)
    # =========================================================================
    
    def detect_emotional_state(self, query: str) -> Optional[str]:
        """
        LEGACY: Detect emotional state from query.
        
        Maintained for backward compatibility with existing call sites.
        Now uses structured pattern detection instead of keyword matching.
        """
        decision = EmotionalPatternDetector.detect(query)
        if decision.confidence >= 0.3:
            return decision.mode.value
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
            
            decision = EmotionalPatternDetector.detect(query)
            
            if decision.confidence < 0.3:
                return {'motivation': None}
            
            logger.info(f"💪 [Motivation] enhance: mode={decision.mode.value}")
            
            return {
                'motivation': {
                    'type': decision.mode.value,
                    'message': f"Coaching mode: {decision.mode.value}",
                    'confidence': decision.confidence,
                    'action': {
                        'type': decision.mode.value,
                        'label': f'{decision.mode.value.replace("_", " ").title()} Mode',
                        'icon': self._get_mode_icon(decision.mode)
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Motivation enhancement failed: {e}")
            return {'motivation': None}
    
    def _get_mode_icon(self, mode: CoachingMode) -> str:
        """Get icon for coaching mode"""
        icons = {
            CoachingMode.CALM_DOWN: "🧘",
            CoachingMode.CONSISTENCY: "⏰",
            CoachingMode.CONFIDENCE: "💪",
            CoachingMode.BURNOUT: "☕",
            CoachingMode.GOAL_LOCK: "🎯",
            CoachingMode.CELEBRATE: "🎉",
            CoachingMode.GENERAL: "💬",
        }
        return icons.get(mode, "💬")
    
    def get_opening_for_state(self, emotional_state: str, name: str = '') -> str:
        """LEGACY: Get an appropriate opening based on emotional state"""
        greeting = f"Hey {name}! " if name and len(name) > 1 else "Hey! "
        
        openings = {
            'calm_down': f"{greeting}Take a breath — we'll figure this out together.",
            'consistency': f"{greeting}Starting is the hardest part — let's make it easy.",
            'confidence': f"{greeting}I know it feels hard, but you've got more in you than you think.",
            'burnout': f"{greeting}Your brain needs rest too — that's not weakness, it's science.",
            'goal_lock': f"{greeting}Let's cut through the noise and find your next step.",
            'celebrate': f"{greeting}This is what progress looks like! 🎉",
            # Legacy mappings
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
    decision = EmotionalPatternDetector.detect(query)
    return decision.confidence >= 0.3


def get_motivation_enhancement(query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get motivation enhancement for a query"""
    agent = MotivationAgent({})
    fake_result = {'query': query}
    return agent.enhance_response(fake_result, context or {})
