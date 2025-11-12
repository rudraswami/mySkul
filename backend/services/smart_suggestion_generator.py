"""
Smart Suggestion Generator - Context-Aware Follow-up Questions
Generates intelligent next-step suggestions based on what student just learned
"""
from typing import List, Dict, Optional


class SmartSuggestionGenerator:
    """
    Generates context-aware suggestion questions that:
    1. Build logically on current topic
    2. Address common misconceptions
    3. Progress naturally through learning path
    4. Avoid generic "Show me!" phrasing
    """

    # Topic progression graph: topic -> [logical next topics]
    TOPIC_GRAPH = {
        # Chemistry
        'atomic_structure': ['quantum_numbers', 'orbitals', 'electron_configuration'],
        'quantum_numbers': ['aufbau_principle', 'hunds_rule', 'pauli_exclusion'],
        'orbitals': ['electron_configuration', 'hybridization', 'molecular_orbitals'],
        'electron_configuration': ['periodic_trends', 'atomic_radius', 'ionization_energy'],
        'periodic_table': ['periodic_trends', 'electronegativity', 'metallic_character'],
        'ionic_bond': ['lattice_energy', 'ionic_compounds', 'solubility'],
        'covalent_bond': ['lewis_structures', 'vsepr_theory', 'molecular_geometry'],
        'chemical_bonding': ['ionic_bond', 'covalent_bond', 'metallic_bond'],
        'catalyst': ['activation_energy', 'rate_of_reaction', 'enzyme_catalysis'],
        'acids_bases': ['ph_scale', 'buffer_solutions', 'acid_strength'],
        'valency': ['chemical_bonding', 'oxidation_states', 'ionic_formulas'],

        # Physics
        'newtons_laws': ['force', 'momentum', 'energy'],
        'force': ['friction', 'tension', 'normal_force'],
        'motion': ['velocity', 'acceleration', 'displacement'],
        'velocity': ['acceleration', 'speed_vs_velocity', 'relative_motion'],
        'work': ['energy', 'power', 'work_energy_theorem'],
        'energy': ['kinetic_energy', 'potential_energy', 'conservation_of_energy'],
        'electricity': ['current', 'voltage', 'resistance'],
        'current': ['ohms_law', 'circuits', 'power'],
        'circuits': ['series_circuits', 'parallel_circuits', 'kirchhoffs_laws'],
        'magnetism': ['magnetic_field', 'electromagnetic_induction', 'motors'],

        # Mathematics
        'differentiation': ['chain_rule', 'product_rule', 'quotient_rule'],
        'integration': ['integration_by_parts', 'substitution', 'definite_integrals'],
        'integration_by_parts': ['integration_techniques', 'reduction_formulas', 'applications'],
        'limits': ['continuity', 'lhopitals_rule', 'infinite_limits'],
        'functions': ['domain_range', 'inverse_functions', 'composite_functions'],
        'trigonometry': ['trigonometric_identities', 'inverse_trig', 'trigonometric_equations'],

        # Biology
        'cell': ['cell_membrane', 'organelles', 'cell_division'],
        'mitosis': ['cell_cycle', 'meiosis', 'cancer'],
        'dna': ['replication', 'transcription', 'translation'],
        'photosynthesis': ['light_reaction', 'dark_reaction', 'chloroplast'],
        'respiration': ['glycolysis', 'krebs_cycle', 'electron_transport_chain'],
    }

    # Common misconceptions for each topic
    COMMON_MISCONCEPTIONS = {
        'quantum_numbers': "Why can't two electrons have the same set of all 4 quantum numbers?",
        'aufbau_principle': "Why do Chromium and Copper violate the Aufbau principle?",
        'ionic_bond': "Why do ionic compounds conduct electricity when dissolved but not when solid?",
        'covalent_bond': "Can covalent bonds be polar? How is that different from ionic?",
        'catalyst': "Does a catalyst change the equilibrium position? Why or why not?",
        'newtons_laws': "If action and reaction are equal, why do things move?",
        'force': "Is friction always opposing motion? Are there cases where it helps?",
        'integration_by_parts': "How do you know which function to choose as 'u' using LIATE rule?",
        'valency': "Why does iron have variable valency (Fe²⁺ and Fe³⁺)?",
        'acids_bases': "Can water act as both acid and base? (Amphoteric behavior)",
    }

    # Application-based follow-ups
    APPLICATION_SUGGESTIONS = {
        'catalyst': "How do catalytic converters in cars reduce pollution?",
        'newtons_laws': "Why do we feel pushed back when a car accelerates?",
        'force': "How do cricket/football players use friction to their advantage?",
        'electricity': "Why do birds on power lines not get shocked?",
        'acids_bases': "What makes antacids neutralize stomach acid?",
        'photosynthesis': "How do plants adapt to low light in forests?",
        'energy': "How does regenerative braking in electric vehicles work?",
        'circuits': "Why do appliances at home run on parallel circuits, not series?",
    }

    @staticmethod
    def generate_suggestions(
        current_topic: str,
        intent: str,
        conversation_history: List[str] = None
    ) -> List[Dict[str, str]]:
        """
        Generate 3 smart suggestion questions based on context

        Args:
            current_topic: Topic just discussed (e.g., "quantum_numbers")
            intent: Intent type of current query
            conversation_history: Previous topics discussed

        Returns:
            List of suggestion dicts: [{'text': '...', 'type': 'next_topic'|'misconception'|'application'}]
        """
        suggestions = []
        topic_lower = current_topic.lower().replace(' ', '_')

        # 1. Logical Next Topic (from graph)
        if topic_lower in SmartSuggestionGenerator.TOPIC_GRAPH:
            next_topics = SmartSuggestionGenerator.TOPIC_GRAPH[topic_lower]
            # Pick first topic not in conversation history
            for next_topic in next_topics:
                if not conversation_history or next_topic not in conversation_history:
                    suggestions.append({
                        'text': SmartSuggestionGenerator._format_next_topic_question(next_topic),
                        'type': 'next_topic',
                        'topic': next_topic
                    })
                    break

        # 2. Common Misconception
        if topic_lower in SmartSuggestionGenerator.COMMON_MISCONCEPTIONS:
            suggestions.append({
                'text': SmartSuggestionGenerator.COMMON_MISCONCEPTIONS[topic_lower],
                'type': 'misconception',
                'topic': topic_lower
            })

        # 3. Real-world Application
        if topic_lower in SmartSuggestionGenerator.APPLICATION_SUGGESTIONS:
            suggestions.append({
                'text': SmartSuggestionGenerator.APPLICATION_SUGGESTIONS[topic_lower],
                'type': 'application',
                'topic': topic_lower
            })

        # 4. If we don't have 3 yet, add generic but smart ones
        while len(suggestions) < 3:
            generic_suggestions = SmartSuggestionGenerator._get_generic_for_intent(intent, topic_lower)
            for sugg in generic_suggestions:
                if len(suggestions) < 3 and sugg not in [s['text'] for s in suggestions]:
                    suggestions.append(sugg)

        return suggestions[:3]  # Return max 3

    @staticmethod
    def _format_next_topic_question(next_topic: str) -> str:
        """Format next topic as a natural question"""
        topic_readable = next_topic.replace('_', ' ').title()

        # Topic-specific question formats
        question_formats = {
            'aufbau_principle': "How do electrons actually fill orbitals? (Aufbau principle)",
            'hunds_rule': "Why do electrons fill orbitals singly first? (Hund's rule)",
            'periodic_trends': "How does position in periodic table affect properties?",
            'electron_configuration': "How do we write electron configurations?",
            'lewis_structures': "How do we draw Lewis structures for molecules?",
            'chain_rule': "What if we have a function inside another function? (Chain rule)",
            'integration_by_parts': "How do we integrate products of functions?",
            'krebs_cycle': "What happens to pyruvate after glycolysis? (Krebs cycle)",
        }

        if next_topic in question_formats:
            return question_formats[next_topic]

        # Default format
        return f"What about {topic_readable}? How does that connect?"

    @staticmethod
    def _get_generic_for_intent(intent: str, topic: str) -> List[Dict[str, str]]:
        """Generate intent-appropriate generic suggestions"""
        topic_readable = topic.replace('_', ' ')

        if intent == 'definition_query':
            return [
                {'text': f"Can you show an example of {topic_readable} in use?", 'type': 'example', 'topic': topic},
                {'text': f"How is {topic_readable} applied in real scenarios?", 'type': 'application', 'topic': topic}
            ]

        elif intent == 'deep_dive':
            return [
                {'text': f"What are the edge cases or exceptions for {topic_readable}?", 'type': 'advanced', 'topic': topic},
                {'text': f"What's the historical context of {topic_readable}?", 'type': 'context', 'topic': topic}
            ]

        elif intent == 'compare_query':
            return [
                {'text': f"When should I use one over the other in practice?", 'type': 'application', 'topic': topic},
                {'text': f"What are common mistakes when choosing between them?", 'type': 'misconception', 'topic': topic}
            ]

        elif intent == 'application_request':
            return [
                {'text': f"Are there other real-world examples of {topic_readable}?", 'type': 'application', 'topic': topic},
                {'text': f"How would this look different in another scenario?", 'type': 'variation', 'topic': topic}
            ]

        else:  # conceptual_explanation or clarification
            return [
                {'text': f"Can you explain {topic_readable} with a different metaphor?", 'type': 'alternative', 'topic': topic},
                {'text': f"What's a practice problem for {topic_readable}?", 'type': 'practice', 'topic': topic}
            ]


def test_suggestion_generator():
    """Test the smart suggestion generator"""
    test_cases = [
        ('quantum_numbers', 'conceptual_explanation'),
        ('catalyst', 'definition_query'),
        ('newtons_laws', 'application_request'),
        ('integration_by_parts', 'deep_dive'),
    ]

    print("Testing Smart Suggestion Generator:\n")
    for topic, intent in test_cases:
        suggestions = SmartSuggestionGenerator.generate_suggestions(topic, intent)
        print(f"📚 Topic: {topic} | Intent: {intent}")
        for i, sugg in enumerate(suggestions, 1):
            print(f"   {i}. [{sugg['type']}] {sugg['text']}")
        print()


if __name__ == "__main__":
    test_suggestion_generator()
