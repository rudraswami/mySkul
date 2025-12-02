"""
👨‍🎓 Agentic Professor - True Academic Excellence Agent
========================================================

A truly agentic professor that thinks, analyzes, and teaches with academic rigor.
Uses tools, verification, and systematic reasoning to provide formal education.
"""

import logging
from typing import Dict, Any, List, Optional

from agents.core.human_like_agent import HumanLikeAgent, EmotionalState, CognitivePattern
from agents.core.shared_utils import (
    IntentDetector, QueryIntent, ResponseFormatter,
    SubjectDetector
)

logger = logging.getLogger(__name__)


class ProfessorAgent(HumanLikeAgent):
    """
    True agentic Professor with academic excellence.

    Personality: Rigorous, systematic academic who:
    - Provides structured, formal explanations
    - Uses proper terminology and notation
    - Derives concepts from first principles
    - Verifies all calculations and facts
    - Maintains high academic standards
    """

    def get_agent_name(self) -> str:
        return "ProfessorAgent"

    def _define_personality(self) -> Dict[str, Any]:
        """Define Professor's academic personality"""
        return {
            'summary': 'Rigorous academic who values precision, logic, and deep understanding',
            'traits': [
                'analytical',
                'precise',
                'thorough',
                'methodical',
                'knowledgeable',
                'formal'
            ],
            'quirks': [
                'Always defines terms before using them',
                'Loves to derive from first principles',
                'Insists on proper notation',
                'Frequently says "Let us consider..."'
            ],
            'thinking_style': CognitivePattern.ANALYTICAL,
            'emotional_baseline': EmotionalState.CONFIDENT,
            'teaching_philosophy': 'True understanding comes from rigorous analysis'
        }

    def get_agent_persona(self) -> str:
        """Professor's academic persona"""
        return """You are a distinguished professor with deep expertise and a passion for academic excellence.

YOUR CHARACTER:
- You are a respected academic who values precision and rigor
- You believe in building understanding from first principles
- You use formal language but remain approachable
- You derive satisfaction from seeing students grasp complex concepts
- You never compromise on accuracy

YOUR TEACHING STYLE:
- Structure: Always organize content logically
- Definitions: Define all terms precisely
- Derivations: Show step-by-step reasoning
- Notation: Use proper mathematical/scientific notation
- Verification: Double-check all calculations
- Context: Explain historical and theoretical background

YOUR APPROACH:
1. FOUNDATION: Establish definitions and axioms
2. DERIVATION: Build up from first principles
3. FORMALIZATION: Use proper notation and terminology
4. VERIFICATION: Validate through multiple methods
5. APPLICATION: Connect to broader theory

ACADEMIC STANDARDS:
- Use formal language: "Let us consider...", "We observe that...", "It follows that..."
- Cite principles: "According to Newton's Second Law..."
- Show all steps: Never skip logical connections
- Verify rigorously: Check units, limits, special cases

NEVER:
- Use informal slang or colloquialisms
- Skip steps in derivations
- State facts without justification
- Compromise on accuracy
- Oversimplify to the point of incorrectness"""

    def get_available_tools(self) -> List[str]:
        """Tools for academic rigor"""
        return [
            "calculator",           # Precise calculations
            "formula_lookup",       # Verify formulas
            "fact_checker",        # Verify claims
            "knowledge_search",     # Research concepts
            "code_executor",       # Demonstrate algorithms
            "diagram_generator",   # Technical diagrams
            "example_generator",   # Rigorous examples
            "quiz_generator"       # Test understanding
        ]

    async def process(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process query with professor's analytical approach
        """
        try:
            logger.info(f"👨‍🎓 Professor analyzing: {query[:50]}...")

            # Detect subject for proper terminology
            subject = SubjectDetector.detect_subject(query) or context.get('subject', 'General')
            context['subject'] = subject

            # Detect intent
            intent = IntentDetector.detect_intent(query)

            # Derivations and proofs require special handling
            if intent in [QueryIntent.DERIVATION, QueryIntent.CALCULATION]:
                context['requires_rigor'] = True
                context['show_all_steps'] = True

            # Run full agentic reasoning
            result = await self.run(query, context)

            # Ensure response maintains academic standards
            if result.get('success'):
                result['content'] = self._ensure_academic_quality(result['content'], intent, subject)

            return result

        except Exception as e:
            logger.error(f"❌ Professor error: {e}", exc_info=True)
            return ResponseFormatter.format_error_response(
                self.get_agent_name(),
                str(e),
                "I apologize for the technical difficulty. Let me provide a basic explanation while I resolve this issue."
            )

    def _ensure_academic_quality(self, content: str, intent: QueryIntent, subject: str) -> str:
        """Ensure response meets academic standards"""
        # Add formal structure if missing
        if intent == QueryIntent.DERIVATION:
            if not any(marker in content for marker in ["Proof:", "Derivation:", "We begin"]):
                content = "**Derivation:**\n\n" + content

            if "QED" not in content and "thus" not in content.lower():
                content += "\n\n□ (Q.E.D.)"

        elif intent == QueryIntent.DEFINITION:
            if not content.startswith("**Definition"):
                content = "**Definition:** " + content

        # Add subject-specific notation reminders
        if subject == "physics" and "=" in content:
            if "where" not in content.lower():
                content += "\n\n*Note: All quantities are in SI units unless specified otherwise.*"

        elif subject == "mathematics" and any(symbol in content for symbol in ["∫", "∑", "∏"]):
            if "domain" not in content.lower() and "interval" not in content.lower():
                content += "\n\n*Note: Domains and convergence conditions apply as standard.*"

        return content

    def _initial_reflection(self, query: str) -> str:
        """Professor's analytical initial thoughts"""
        reflections = [
            "An excellent question that requires systematic analysis.",
            "Let me approach this rigorously from first principles.",
            "This warrants a thorough mathematical treatment.",
            "A fundamental concept that deserves proper examination.",
        ]
        import random
        return random.choice(reflections)

    async def _think_humanlike(self, state: Any) -> Optional[Any]:
        """Professor's methodical thinking process"""
        thought_action = await super()._think_humanlike(state)

        if thought_action and state.context.get('requires_rigor'):
            # Professor always double-checks mathematical steps
            if thought_action.action == "calculator":
                state.add_inner_thought("I must verify this calculation for accuracy.")
            elif thought_action.action == "FINISH":
                state.add_inner_thought("Let me ensure all steps are properly justified.")

        return thought_action

    def _naturalize_thought(self, thought: str, state: Any) -> str:
        """Make professor's thoughts formal yet accessible"""
        # Replace informal phrases with formal ones
        replacements = {
            "I think": "I posit that",
            "Let's see": "Let us examine",
            "Looks like": "It appears that",
            "We need": "It is necessary to",
            "First,": "Initially,",
            "Next,": "Subsequently,",
            "So": "Therefore",
            "But": "However",
        }

        for informal, formal in replacements.items():
            thought = thought.replace(informal, formal)

        return thought

    def _react_to_observation(self, observation: str) -> str:
        """Professor's analytical reaction to observations"""
        if "error" in observation.lower():
            return "This requires reconsideration. Let me apply an alternative method."
        elif "verified" in observation.lower():
            return "Excellent. The verification confirms our analysis."
        elif "found" in observation.lower():
            return "This aligns with established theory. Let me elaborate."
        else:
            return "Interesting. This warrants further analysis."

    async def _verify_conclusion(self, state: Any) -> bool:
        """Professor always verifies conclusions"""
        # Use multiple verification methods
        verifications = []

        # Check mathematical correctness
        if self.verifier:
            result = await self.verifier.verify_response(
                state.final_answer,
                state.context
            )
            verifications.append(result.is_valid)

        # Check dimensional analysis for physics
        if state.context.get('subject') == 'physics':
            # Simple dimensional check (would be more sophisticated in practice)
            has_units = any(unit in state.final_answer.lower()
                          for unit in ['m/s', 'kg', 'N', 'J', 'W'])
            verifications.append(has_units or "calculation" not in state.query.lower())

        # All checks must pass
        return all(verifications) if verifications else True

    async def _humanize_response(self, response: str, state: Any) -> str:
        """Maintain formal but accessible tone"""
        # Don't over-humanize for professor
        # Keep formal structure but add slight warmth

        if state.confidence > 0.9:
            response = "**Solution:**\n\n" + response
        elif state.confidence > 0.7:
            response = "**Analysis:**\n\n" + response
        else:
            response = "**Preliminary Analysis:**\n\n" + response
            response += "\n\n*Note: Further verification may be beneficial.*"

        # Add conclusion if complex
        if state.iterations > 5:
            response += "\n\n**Conclusion:**\nThe analysis demonstrates " + \
                       f"that {self._extract_key_finding(state)}"

        return response

    def _extract_key_finding(self, state: Any) -> str:
        """Extract the key finding from the analysis"""
        # Simplified - would use NLP in practice
        if state.final_answer:
            sentences = state.final_answer.split('.')
            if sentences:
                return sentences[-2] if len(sentences) > 1 else sentences[0]
        return "the concept follows from fundamental principles"


# Factory function for backward compatibility
def create_agentic_professor(config: Optional[Dict[str, Any]] = None) -> ProfessorAgent:
    """Create an agentic professor agent"""
    from agents.core.tool_registry import create_tool_registry

    agent = ProfessorAgent(config)

    # Set up tools with emphasis on verification
    agent.tool_registry = create_tool_registry(
        include_default=True,
        include_action_tools=False
    )

    # Add professor-specific tools
    from agents.core.tools.expanded_tools import get_expanded_tools
    for tool in get_expanded_tools():
        if tool.name in agent.get_available_tools():
            agent.tool_registry.register(tool)

    # Initialize components
    try:
        from agents.core.memory import MemorySystem
        agent.memory = MemorySystem("professor")
    except:
        pass

    try:
        from agents.core.verifier import Verifier
        agent.verifier = Verifier()
    except:
        pass

    return agent