"""
Response Adapter - Converts Agentic Responses to Neuro-Symbolic Format
Bridges agentic architecture with existing frontend expectations
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ResponseAdapter:
    """
    Adapts multi-agent responses to neuro-symbolic format
    
    Converts:
    - Mentor + Professor responses → neuro-symbolic structure
    - Visual specifications → teaching_visual format
    - Metadata → frontend-compatible fields
    """
    
    @staticmethod
    def adapt_agentic_to_neuro_symbolic(
        agentic_response: Dict[str, Any],
        query: str,
        subject: str,
        intent: str = None
    ) -> Dict[str, Any]:
        """
        Convert agentic multi-agent response to neuro-symbolic format
        
        Args:
            agentic_response: Response from SupervisorAgent.run()
            query: Original student query
            subject: Subject area
        
        Returns:
            Neuro-symbolic formatted response compatible with frontend
        """
        try:
            logger.info("🔄 Adapting agentic response to neuro-symbolic format")
            
            # Extract agent responses
            mentor_response = agentic_response.get('mentor', {})
            professor_response = agentic_response.get('professor', {})
            visual_response = agentic_response.get('visual', {})
            
            # Detect if this is a greeting response
            # Extract intent from agentic response if not provided
            if intent is None:
                intent = agentic_response.get('intent', '')
            
            is_greeting = (
                intent == 'greeting' or 
                mentor_response.get('metadata', {}).get('is_greeting', False) or
                mentor_response.get('metadata', {}).get('approach') == 'greeting'
            )
            
            # Build default_view (quick summary)
            # CRITICAL: Match frontend MentorResponseV2 expected structure
            mentor_content = mentor_response.get('content', '')
            professor_content = professor_response.get('content', '')
            metaphor_used = mentor_response.get('metadata', {}).get('metaphor_used', 'cricket')
            
            # For greetings, use simpler structure
            if is_greeting:
                default_view = {
                    'greeting': mentor_content,  # Use actual greeting as header
                    'quick_summary': '',  # Empty for greetings
                    'key_insight': '',  # No key insight for greetings
                    'confidence_boost': '',  # Empty for greetings
                    # For greetings, main_content should be EMPTY to avoid duplication
                    'main_content': {
                        'title': '',
                        'content': '',  # EMPTY! Greeting already shown in header
                        'key_insight': ''
                    },
                    # NO metaphor for greetings (suppress metaphor card)
                    'metaphor': None
                }
            else:
                # For concept questions, use full structure
                # CRITICAL FIX: Separate metaphor (short intro) from main content (full explanation)
                # Extract first paragraph/sentence as metaphor, rest as main content
                mentor_parts = mentor_content.split('\n\n', 1) if '\n\n' in mentor_content else mentor_content.split('. ', 1)
                metaphor_intro = mentor_parts[0] if len(mentor_parts) > 0 else mentor_content[:150]
                main_explanation = mentor_parts[1] if len(mentor_parts) > 1 else mentor_content
                
                # If metaphor intro is too short, take first 150 chars
                if len(metaphor_intro) < 50 and len(mentor_content) > 150:
                    metaphor_intro = mentor_content[:150] + '...'
                    main_explanation = mentor_content
                
                default_view = {
                    'greeting': 'Hey! Let me help you understand this concept. 👋',
                    'quick_summary': metaphor_intro,
                    'key_insight': ResponseAdapter._extract_key_insight(professor_response),
                    'confidence_boost': ResponseAdapter._generate_confidence_message(),
                    # Add main_content that frontend expects
                    'main_content': {
                        'title': 'Detailed Explanation',
                        'content': main_explanation,  # REST of mentor content (not duplicate!)
                        'key_insight': ResponseAdapter._extract_key_insight(professor_response)
                    },
                    # Add metaphor that frontend expects
                    'metaphor': {
                        'text': metaphor_intro,  # FIRST part only (not full content!)
                        'category': metaphor_used
                    }
                }
            
            # Build progressive_sections (expandable content)
            # For greetings, keep it minimal - no expandable sections needed
            if is_greeting:
                progressive_sections = {}
            else:
                progressive_sections = {
                    'intuition': {
                        'title': '🎯 Intuitive Understanding',
                        'content': mentor_content,
                        'metaphor': metaphor_used,
                        'expandable': True
                    },
                    'formal_explanation': {
                        'title': '📚 Formal Explanation',
                        'content': professor_content,
                        'structure': 'step_by_step',
                        'expandable': True
                    },
                    'strategy': {
                        'title': '💡 Problem-Solving Strategy',
                        'steps': ResponseAdapter._extract_steps(professor_response),
                        'expandable': True
                    },
                    # Add additional sections for compatibility
                    'explanation': mentor_content,  # Legacy field
                    'key_takeaways': ResponseAdapter._extract_key_insight(professor_response)
                }
            
            # Build visual_metaphor (if visual was generated)
            visual_metaphor = {}
            if visual_response and visual_response.get('content'):
                visual_spec = visual_response['content']
                if visual_spec:  # Not None
                    visual_metaphor = {
                        'hero_visual': {
                            'type': visual_spec.get('type', 'animated_lesson'),
                            'visual_id': visual_spec.get('visual_id', 'visual_1'),
                            'url': 'generated_visual',  # Placeholder
                            'alt_text': f'Visual explanation of {query[:50]}'
                        },
                        'metaphor': visual_spec.get('metadata', {}).get('metaphor', 'cricket'),
                        'visual_tier': 1
                    }
            
            # Build student_profile
            student_profile = {
                'region': 'India',
                'emotional_state': 'Confident',
                'preferred_metaphor': mentor_response.get('metadata', {}).get('metaphor_used', 'cricket')
            }
            
            # Complete neuro-symbolic response
            # Add render directives based on intent
            render_directives = {}
            if is_greeting:
                render_directives = {
                    'skip_greeting': False,  # Show greeting header
                    'suppress_metaphor': True,  # NO metaphor card for greetings
                    'suppress_cta': True,  # No call-to-action buttons
                    'suppress_basic_steps': True,  # No step sections
                    'suppress_main_content': True,  # ✅ HIDE main_content box (prevents duplicate)
                    'suppress_visual_placeholder': True,  # ✅ HIDE empty lightbulb box
                    'greeting_only': True  # ✅ Tell frontend this is greeting-only mode
                }
            else:
                render_directives = {
                    'prefer_paragraph_first': True
                }
            
            neuro_symbolic_response = {
                'success': True,
                'response': {
                    'default_view': default_view,
                    'progressive_sections': progressive_sections,
                    'visual_metaphor': visual_metaphor,
                    'student_profile': student_profile,
                    'intent': intent if intent else 'conceptual_explanation',
                    'render_directives': render_directives
                },
                'raw_response': f"Mentor: {mentor_response.get('content', '')}\n\nProfessor: {professor_response.get('content', '')}",
                'question_type': 'greeting' if is_greeting else 'concept_explanation',
                'generation_time': 2.5
            }
            
            logger.info("✅ Agentic response adapted successfully")
            return neuro_symbolic_response
            
        except Exception as e:
            logger.error(f"❌ Response adaptation failed: {e}", exc_info=True)
            # Return minimal fallback response
            return {
                'success': False,
                'error': f'Response adaptation failed: {str(e)}',
                'response': {
                    'default_view': {
                        'quick_summary': 'An error occurred while processing your request.'
                    }
                }
            }
    
    @staticmethod
    def _generate_greeting(mentor_response: Dict[str, Any]) -> str:
        """Generate friendly greeting"""
        return "Hey! Let me help you understand this concept. 👋"
    
    @staticmethod
    def _extract_key_insight(professor_response: Dict[str, Any]) -> str:
        """Extract key insight from professor response"""
        content = professor_response.get('content', '')
        # Extract first sentence or first 100 chars
        if '.' in content:
            return content.split('.')[0] + '.'
        return content[:100] + '...'
    
    @staticmethod
    def _generate_confidence_message() -> str:
        """Generate encouraging message"""
        messages = [
            "You're doing great! Keep going. 💪",
            "This concept is within your reach! 🎯",
            "One step at a time, you've got this! 🚀",
            "Building understanding like a pro! ⭐"
        ]
        import random
        return random.choice(messages)
    
    @staticmethod
    def _extract_steps(professor_response: Dict[str, Any]) -> list:
        """Extract problem-solving steps from professor response"""
        content = professor_response.get('content', '')
        steps = []
        
        # Try to find "Step 1:", "Step 2:", etc.
        import re
        step_matches = re.findall(r'Step \d+:([^\n]+)', content)
        
        if step_matches:
            for i, step_text in enumerate(step_matches, 1):
                steps.append({
                    'step_number': i,
                    'description': step_text.strip(),
                    'detail': ''
                })
        else:
            # Fallback: split by sentences
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            for i, sentence in enumerate(sentences[:5], 1):  # Max 5 steps
                steps.append({
                    'step_number': i,
                    'description': sentence,
                    'detail': ''
                })
        
        return steps

