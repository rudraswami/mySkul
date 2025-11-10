"""
Memory Context Builder for AI Tutor
Builds structured conversation memory for maintaining context across turns
"""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class MemoryContextBuilder:
    """
    Builds structured memory context from conversation history
    Extracts topics, metaphors, visuals, and learning artifacts
    """

    @staticmethod
    def build_memory_context(
        message_history: List[Dict[str, Any]],
        max_messages: int = 5,
        include_full_responses: bool = False
    ) -> Dict[str, Any]:
        """
        Build structured memory context from message history

        Args:
            message_history: List of previous messages
            max_messages: Maximum number of messages to include
            include_full_responses: Whether to include full AI responses

        Returns:
            Dict with structured memory context
        """
        if not message_history:
            return {
                'has_history': False,
                'topics_covered': [],
                'metaphors_used': [],
                'concepts_explained': [],
                'questions_asked': [],
                'last_topic': None,
                'conversation_summary': "This is the first question in this session."
            }

        # Limit to recent messages
        recent_history = message_history[-max_messages:] if len(message_history) > max_messages else message_history

        # Extract learning artifacts
        topics_covered = []
        metaphors_used = []
        concepts_explained = []
        questions_asked = []
        visuals_shown = []

        for msg in recent_history:
            # Extract user question
            if 'user_message' in msg:
                questions_asked.append(msg['user_message'])

            # Extract AI response artifacts
            if 'ai_response' in msg:
                ai_resp = msg['ai_response']

                # Extract topic/subject
                if isinstance(ai_resp, dict):
                    # Extract from neuro-symbolic response
                    if 'topic' in ai_resp:
                        topics_covered.append(ai_resp['topic'])

                    # Extract metaphor
                    if 'metaphor' in ai_resp:
                        metaphors_used.append(ai_resp['metaphor'])

                    # Extract concepts from practical_explanation
                    if 'practical_explanation' in ai_resp:
                        concepts_explained.append(ai_resp['practical_explanation'][:100] + "...")

                    # Track visual usage
                    if 'visual_schema' in ai_resp or 'hero_visual' in ai_resp:
                        visual_type = ai_resp.get('visual_schema', {}).get('diagram_type', 'visual')
                        visuals_shown.append(visual_type)

        # Build conversation summary
        summary_parts = []

        if topics_covered:
            unique_topics = list(dict.fromkeys(topics_covered))  # Remove duplicates, preserve order
            summary_parts.append(f"Topics discussed: {', '.join(unique_topics[-3:])}")  # Last 3 topics

        if metaphors_used:
            summary_parts.append(f"Metaphors used: {', '.join(metaphors_used[-2:])}")  # Last 2 metaphors

        if visuals_shown:
            summary_parts.append(f"Visuals shown: {', '.join(visuals_shown[-2:])}")

        conversation_summary = " | ".join(summary_parts) if summary_parts else "Previous conversation in progress."

        # Get last topic
        last_topic = topics_covered[-1] if topics_covered else None

        # Build memory context string for LLM
        memory_context_str = MemoryContextBuilder._build_memory_prompt(
            questions_asked=questions_asked,
            concepts_explained=concepts_explained,
            last_topic=last_topic
        )

        return {
            'has_history': True,
            'topics_covered': list(dict.fromkeys(topics_covered)),  # Unique topics
            'metaphors_used': list(dict.fromkeys(metaphors_used)),
            'concepts_explained': concepts_explained,
            'questions_asked': questions_asked,
            'visuals_shown': visuals_shown,
            'last_topic': last_topic,
            'conversation_summary': conversation_summary,
            'memory_context_str': memory_context_str,
            'message_count': len(recent_history)
        }

    @staticmethod
    def _build_memory_prompt(
        questions_asked: List[str],
        concepts_explained: List[str],
        last_topic: Optional[str]
    ) -> str:
        """
        Build memory context string for injection into LLM prompt
        """
        if not questions_asked:
            return ""

        memory_lines = [
            "\n═══════════════════════════════════════════════════",
            "📝 **CONVERSATION MEMORY** (Use this to maintain continuity)",
            "═══════════════════════════════════════════════════"
        ]

        # Add previous questions
        memory_lines.append("\n**Previous Questions in this Session:**")
        for i, q in enumerate(questions_asked[-3:], 1):  # Last 3 questions
            memory_lines.append(f"  {i}. \"{q}\"")

        # Add last topic
        if last_topic:
            memory_lines.append(f"\n**Last Topic Discussed:** {last_topic}")

        # Add concepts covered
        if concepts_explained:
            memory_lines.append("\n**Concepts Already Explained:**")
            for i, concept in enumerate(concepts_explained[-3:], 1):  # Last 3 concepts
                memory_lines.append(f"  {i}. {concept}")

        # Add instructions
        memory_lines.extend([
            "\n**Instructions for Using Memory:**",
            "- DON'T repeat explanations already given",
            "- If student says \"continue\" or \"next\", build upon previous topic",
            "- If student references earlier concepts, acknowledge them",
            "- If student asks for clarification, refer back to what was already discussed",
            "- Progress naturally from previous topics",
            "═══════════════════════════════════════════════════\n"
        ])

        return "\n".join(memory_lines)

    @staticmethod
    def should_use_memory(user_message: str) -> bool:
        """
        Detect if user message is referencing previous conversation

        Returns True if message contains keywords like:
        - "continue", "next", "more", "also"
        - "you said", "earlier", "before"
        - "that", "this", "it" (referring to previous topic)
        """
        message_lower = user_message.lower()

        continuation_keywords = [
            'continue', 'next', 'more', 'also', 'further',
            'you said', 'earlier', 'before', 'previous', 'last time',
            'what about', 'and', 'similarly', 'like that',
            'explain more', 'go deeper', 'clarify'
        ]

        # Check for continuation keywords
        if any(keyword in message_lower for keyword in continuation_keywords):
            return True

        # Check for short messages that likely reference context
        word_count = len(user_message.split())
        if word_count <= 5:  # Short messages likely need context
            return True

        return False


def test_memory_builder():
    """Test the memory builder with sample data"""
    sample_history = [
        {
            'user_message': 'Explain atomic orbitals',
            'ai_response': {
                'topic': 'Atomic Orbitals',
                'metaphor': 'Like cricket field positions',
                'practical_explanation': 'Atomic orbitals are regions where electrons are most likely to be found...',
                'visual_schema': {'diagram_type': 'hierarchy'}
            }
        },
        {
            'user_message': 'What about d orbitals?',
            'ai_response': {
                'topic': 'd-Orbitals',
                'metaphor': 'Like complex dance moves',
                'practical_explanation': 'd orbitals have more complex shapes with 5 different orientations...'
            }
        }
    ]

    memory = MemoryContextBuilder.build_memory_context(sample_history)
    print("Memory Context:")
    print(f"Topics: {memory['topics_covered']}")
    print(f"Summary: {memory['conversation_summary']}")
    print(f"\nMemory Prompt:\n{memory['memory_context_str']}")


if __name__ == "__main__":
    test_memory_builder()
