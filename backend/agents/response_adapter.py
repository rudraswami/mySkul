"""
Response Adapter - Converts Agentic Responses to Neuro-Symbolic Format
Bridges agentic architecture with existing frontend expectations
NOW WITH DYNAMIC TEMPLATES: Varied response structures based on intent and student profile
"""
import logging
from typing import Dict, Any, Optional

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
        intent: str = None,
        user_id: Optional[str] = None,
        student_profile: Optional[Dict[str, Any]] = None
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
            
            # Import dynamic template system
            from services.dynamic_response_templates import (
                ResponseTemplateVariety,
                DynamicResponseBuilder
            )
            from services.intent_planner import IntentPlanner
            from services.response_section_variety import SectionTitleVariety
            from services.intelligent_formatter import IntelligentFormatter
            
            # Extract agent responses
            mentor_response = agentic_response.get('mentor', {})
            professor_response = agentic_response.get('professor', {})
            visual_response = agentic_response.get('visual', {})
            
            # Detect if this is a greeting response
            # Extract intent from agentic response if not provided
            if intent is None:
                intent = agentic_response.get('intent', '')
            
            # Normalize intent to match IntentPlanner format
            intent_plan = IntentPlanner.detect(query)
            normalized_intent = intent_plan.intent if intent_plan else (intent or 'concept_explanation')
            
            is_greeting = (
                intent == 'greeting' or 
                normalized_intent == 'greeting' or
                mentor_response.get('metadata', {}).get('is_greeting', False) or
                mentor_response.get('metadata', {}).get('approach') == 'greeting'
            )
            
            # Extract concept name for personalization
            concept_name = IntentPlanner.extract_concept_name(query) if not is_greeting else ""
            
            # Extract content
            mentor_content = mentor_response.get('content', '')
            professor_content = professor_response.get('content', '')
            metaphor_used = mentor_response.get('metadata', {}).get('metaphor_used', 'cricket')
            
            # ========== INTELLIGENT FORMATTING ==========
            # Detect question type and format appropriately
            intelligent_format = IntelligentFormatter.format_response(
                question=query,
                mentor_content=mentor_content,
                professor_content=professor_content
            )
            
            format_type = intelligent_format.get('format_type')
            
            # ========== DYNAMIC TEMPLATE SYSTEM ==========
            # Select template style based on intent, avoiding repetition
            if is_greeting:
                # Greetings use simple structure
                template_style = 'quick_recap'  # Simple greeting template
            else:
                # Get dynamic template style
                template_style = ResponseTemplateVariety.get_template_style(
                    user_id=user_id or 'anonymous',
                    intent=normalized_intent,
                    student_profile=student_profile,
                    question_complexity='medium'  # Could be detected from query
                )
                logger.info(f"🎨 Using template style: {template_style} for intent: {normalized_intent}")
            
            # Build response structure using dynamic template
            dynamic_structure = DynamicResponseBuilder.build_response_structure(
                template_style=template_style,
                intent=normalized_intent,
                mentor_content=mentor_content,
                professor_content=professor_content,
                metaphor_used=metaphor_used,
                student_profile=student_profile,
                question=query,
                concept_name=concept_name
            )
            
            # Extract structure components
            default_view = dynamic_structure.get('default_view', {})
            progressive_sections = dynamic_structure.get('progressive_sections', {})
            template_directives = dynamic_structure.get('render_directives', {})
            
            # For greetings, ensure proper structure
            if is_greeting:
                default_view = {
                    'greeting': mentor_content,
                    'quick_summary': '',
                    'key_insight': '',
                    'confidence_boost': '',
                    'main_content': {
                        'title': '',
                        'content': '',
                        'key_insight': ''
                    },
                    'metaphor': None
                }
                progressive_sections = {}
            else:
                # ========== APPLY SECTION VARIETY ==========
                # Get varied section titles based on template style
                section_config = SectionTitleVariety.get_varied_sections(template_style, normalized_intent)
                
                # Get varied greeting
                student_name = student_profile.get('name', '') if student_profile else ''
                varied_greeting = SectionTitleVariety.get_greeting_variation(template_style, student_name)
                
                # Override greeting if not already set by template
                if not default_view.get('greeting') or 'Hey! Let me help' in default_view.get('greeting', ''):
                    default_view['greeting'] = varied_greeting
                
                # Update section titles if progressive_sections exist
                if progressive_sections:
                    # Update main content title
                    if default_view.get('main_content') and section_config.get('main_title'):
                        default_view['main_content']['title'] = section_config['main_title']
                    
                    # Update expandable section titles
                    if section_config.get('expandable_title'):
                        # Find first expandable section and update its title
                        for key in ['intuition', 'formal_explanation', 'strategy']:
                            if key in progressive_sections:
                                progressive_sections[key]['title'] = section_config['expandable_title']
                                break
                    
                    # Determine if key insight should be separate or integrated
                    if not SectionTitleVariety.should_show_key_insight_separately(template_style):
                        # Integrate key insight into main content instead of separate yellow box
                        if default_view.get('main_content', {}).get('key_insight'):
                            default_view['main_content']['key_insight'] = None  # Suppress separate box
                    
                    # Hide metaphor box if configured
                    if not section_config.get('show_metaphor_separately', True):
                        if default_view.get('metaphor'):
                            # Integrate metaphor into content instead of showing separately
                            template_directives['suppress_metaphor'] = True
            
            # Merge template directives with base directives
            base_directives = template_directives.copy()
            
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
            # Merge render directives (template directives + base directives)
            render_directives = base_directives.copy()
            if is_greeting:
                render_directives.update({
                    'skip_greeting': False,
                    'suppress_metaphor': True,
                    'suppress_cta': True,
                    'suppress_basic_steps': True,
                    'suppress_main_content': True,
                    'suppress_visual_placeholder': True,
                    'greeting_only': True
                })
            else:
                # Add template style metadata for frontend
                render_directives['template_style'] = template_style
                render_directives['intent'] = normalized_intent
            
            neuro_symbolic_response = {
                'success': True,
                'response': {
                    'default_view': default_view,
                    'progressive_sections': progressive_sections,
                    'visual_metaphor': visual_metaphor,
                    'student_profile': student_profile or {
                        'region': 'India',
                        'emotional_state': 'Confident',
                        'preferred_metaphor': metaphor_used
                    },
                    'intent': normalized_intent,
                    'render_directives': render_directives,
                    'template_metadata': {
                        'template_style': template_style,
                        'intent': normalized_intent,
                        'variety_enabled': True
                    },
                    # ========== INTELLIGENT FORMATTING DATA ==========
                    'intelligent_format': intelligent_format,  # Pass formatted data to frontend
                    'format_type': format_type,  # comparison, definition, steps, list, explanation
                    
                    # ========== COGNITO-OS v4.0: TRANSPARENCY DATA ==========
                    # Pass through metadata for UI transparency panels
                    'metadata': agentic_response.get('metadata', {
                        'cognito_os_enabled': True,
                        'supervisor_version': '4.0',
                        'agents_used': list(set([
                            'mentor' if mentor_response else None,
                            'professor' if professor_response else None,
                            'visualise' if visual_response else None
                        ]) - {None}),
                        'tools_used': ['rag', 'knowledge_search']
                    }),
                    'verification': agentic_response.get('verification', {}),
                    'rag': agentic_response.get('rag', {}),
                    'learning_path': agentic_response.get('learning_path', [])
                },
                'raw_response': f"Mentor: {mentor_response.get('content', '')}\n\nProfessor: {professor_response.get('content', '')}",
                'question_type': 'greeting' if is_greeting else normalized_intent,
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

