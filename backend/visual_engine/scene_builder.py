"""
Scene Builder - Composes Visual Scenes from Templates
Builds complete visual scenes with animations, narration, and interactions
"""
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class SceneBuilder:
    """
    Builds visual scenes from templates and variables
    
    Key Features:
    - Template-based scene composition
    - Variable substitution
    - Animation sequencing
    - Interactive element placement
    """
    
    def __init__(self):
        """Initialize Scene Builder with template registry"""
        self.templates = self._load_templates()
        logger.info("🎬 SceneBuilder initialized")
    
    def build_scene(
        self,
        template_id: str,
        variables: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build a complete visual scene from template
        
        Args:
            template_id: ID of visual template to use
            variables: Variables to substitute in template
            context: Additional context (subject, student_profile, etc.)
        
        Returns:
            Complete scene specification with stages and animations
        """
        try:
            logger.info(f"🎬 Building scene from template: {template_id}")
            
            # Get template
            template = self.templates.get(template_id)
            if not template:
                logger.warning(f"⚠️ Template {template_id} not found, using default")
                template = self._get_default_template()
            
            # Substitute variables
            scene = self._substitute_variables(template, variables)
            
            # Add context-specific metadata
            if context:
                scene['metadata']['context'] = context
            
            logger.info(f"✅ Scene built with {len(scene.get('stages', []))} stages")
            return scene
            
        except Exception as e:
            logger.error(f"❌ Scene building failed: {e}", exc_info=True)
            return self._get_fallback_scene(template_id)
    
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Load visual templates
        
        Returns:
            Dict of template_id -> template_spec
        """
        # Template registry - expandable with more templates
        return {
            'concept_explanation': {
                'visual_id': 'concept_tpl_1',
                'type': 'animated_lesson',
                'total_duration_ms': 6000,
                'stages': [
                    {
                        'stage_id': 1,
                        'title': 'Introduction',
                        'duration_ms': 2000,
                        'narration': 'Let\'s understand {concept_name}',
                        'animations': [
                            {
                                'element': 'title',
                                'type': 'fadeIn',
                                'delay_ms': 0,
                                'duration_ms': 500
                            }
                        ]
                    },
                    {
                        'stage_id': 2,
                        'title': 'Core Concept',
                        'duration_ms': 3000,
                        'narration': '{core_explanation}',
                        'animations': [
                            {
                                'element': 'diagram',
                                'type': 'drawPath',
                                'delay_ms': 500,
                                'duration_ms': 2000
                            }
                        ]
                    },
                    {
                        'stage_id': 3,
                        'title': 'Key Insight',
                        'duration_ms': 1000,
                        'narration': '{key_insight}',
                        'animations': [
                            {
                                'element': 'highlight',
                                'type': 'pulse',
                                'delay_ms': 0,
                                'duration_ms': 500
                            }
                        ]
                    }
                ],
                'metadata': {
                    'template_id': 'concept_explanation',
                    'subject': '{subject}',
                    'difficulty': 'medium'
                }
            },
            'step_by_step': {
                'visual_id': 'steps_tpl_1',
                'type': 'animated_lesson',
                'total_duration_ms': 10000,
                'stages': [
                    {
                        'stage_id': 1,
                        'title': 'Problem Statement',
                        'duration_ms': 2000,
                        'narration': 'Here\'s what we need to solve: {problem}',
                        'animations': []
                    },
                    {
                        'stage_id': 2,
                        'title': 'Solution Steps',
                        'duration_ms': 6000,
                        'narration': '{solution_steps}',
                        'animations': []
                    },
                    {
                        'stage_id': 3,
                        'title': 'Final Answer',
                        'duration_ms': 2000,
                        'narration': 'Therefore, the answer is: {answer}',
                        'animations': []
                    }
                ],
                'metadata': {
                    'template_id': 'step_by_step',
                    'subject': '{subject}'
                }
            }
        }
    
    def _substitute_variables(
        self,
        template: Dict[str, Any],
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Substitute variables in template
        
        Args:
            template: Template dict with {variable} placeholders
            variables: Variable values to substitute
        
        Returns:
            Template with substituted values
        """
        import json
        import re
        
        # Convert template to JSON string
        template_str = json.dumps(template)
        
        # Replace all {variable} patterns
        for var_name, var_value in variables.items():
            pattern = f'{{{var_name}}}'
            if isinstance(var_value, str):
                template_str = template_str.replace(pattern, var_value)
            else:
                template_str = template_str.replace(f'"{pattern}"', json.dumps(var_value))
        
        # Convert back to dict
        return json.loads(template_str)
    
    def _get_default_template(self) -> Dict[str, Any]:
        """Get default template when specific template not found"""
        return self.templates['concept_explanation']
    
    def _get_fallback_scene(self, template_id: str) -> Dict[str, Any]:
        """
        Get fallback scene when building fails
        
        Returns:
            Minimal valid scene specification
        """
        return {
            'visual_id': f'fallback_{template_id}',
            'type': 'static_concept',
            'total_duration_ms': 3000,
            'stages': [
                {
                    'stage_id': 1,
                    'title': 'Concept Explanation',
                    'duration_ms': 3000,
                    'narration': 'Let me explain this concept step by step.',
                    'animations': [],
                    'elements': []
                }
            ],
            'metadata': {
                'template_id': template_id,
                'is_fallback': True
            }
        }

