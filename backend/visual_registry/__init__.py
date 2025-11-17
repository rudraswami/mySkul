"""
Visual Template Registry
Central registry for all visual templates with dynamic selection
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class VisualTemplateRegistry:
    """
    Registry of visual templates for different concepts and subjects
    
    Features:
    - Subject-aware template selection
    - Concept-type mapping
    - Difficulty-based templates
    - Metaphor-specific variations
    """
    
    def __init__(self):
        """Initialize registry with built-in templates"""
        self.templates = self._load_builtin_templates()
        logger.info(f"📚 Visual Template Registry initialized with {len(self.templates)} templates")
    
    def get_template(
        self,
        concept_type: str,
        subject: Optional[str] = None,
        difficulty: str = "medium",
        metaphor: str = "cricket"
    ) -> Optional[Dict[str, Any]]:
        """
        Get appropriate template for concept
        
        Args:
            concept_type: Type of concept (explanation, derivation, comparison, etc.)
            subject: Subject area (Mathematics, Physics, etc.)
            difficulty: Difficulty level (easy, medium, hard)
            metaphor: Preferred metaphor category
        
        Returns:
            Template specification or None if not found
        """
        # Build template key
        template_key = f"{subject}_{concept_type}" if subject else concept_type
        
        # Try exact match
        if template_key in self.templates:
            return self.templates[template_key]
        
        # Fallback to generic concept type
        if concept_type in self.templates:
            return self.templates[concept_type]
        
        # Default fallback
        logger.warning(f"⚠️ No template found for {template_key}, using default")
        return self.templates.get('default_explanation')
    
    def list_templates(self, subject: Optional[str] = None) -> List[str]:
        """
        List available templates
        
        Args:
            subject: Filter by subject (optional)
        
        Returns:
            List of template IDs
        """
        if subject:
            return [
                tid for tid in self.templates.keys()
                if tid.startswith(subject) or tid.startswith('default')
            ]
        return list(self.templates.keys())
    
    def _load_builtin_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Load built-in visual templates
        
        Returns:
            Dict of template_id -> template_spec
        """
        return {
            'default_explanation': {
                'template_id': 'default_explanation',
                'concept_type': 'explanation',
                'stages': 3,
                'animation_style': 'progressive',
                'metaphor_compatible': ['cricket', 'cooking', 'bollywood', 'gaming'],
                'structure': {
                    'intro': {'duration': 2000, 'elements': ['title', 'metaphor_hook']},
                    'core': {'duration': 4000, 'elements': ['diagram', 'labels', 'animations']},
                    'conclusion': {'duration': 2000, 'elements': ['key_insight', 'summary']}
                }
            },
            'Mathematics_derivation': {
                'template_id': 'math_derivation',
                'concept_type': 'derivation',
                'stages': 4,
                'animation_style': 'step_by_step',
                'metaphor_compatible': ['gaming', 'cricket'],
                'structure': {
                    'given': {'duration': 1500, 'elements': ['given_info', 'formula']},
                    'step1': {'duration': 3000, 'elements': ['equation', 'transformation']},
                    'step2': {'duration': 3000, 'elements': ['equation', 'simplification']},
                    'result': {'duration': 2000, 'elements': ['final_formula', 'verification']}
                }
            },
            'Physics_concept': {
                'template_id': 'physics_concept',
                'concept_type': 'explanation',
                'stages': 4,
                'animation_style': 'dynamic',
                'metaphor_compatible': ['cricket', 'bollywood'],
                'structure': {
                    'phenomenon': {'duration': 2000, 'elements': ['observation', 'question']},
                    'principle': {'duration': 3000, 'elements': ['law', 'equation']},
                    'application': {'duration': 3000, 'elements': ['example', 'calculation']},
                    'insight': {'duration': 2000, 'elements': ['key_point', 'real_world']}
                }
            },
            'Chemistry_reaction': {
                'template_id': 'chemistry_reaction',
                'concept_type': 'process',
                'stages': 5,
                'animation_style': 'transformation',
                'metaphor_compatible': ['cooking', 'gaming'],
                'structure': {
                    'reactants': {'duration': 1500, 'elements': ['molecules', 'properties']},
                    'conditions': {'duration': 1500, 'elements': ['temperature', 'catalyst']},
                    'reaction': {'duration': 3000, 'elements': ['bond_breaking', 'bond_forming']},
                    'products': {'duration': 2000, 'elements': ['new_molecules', 'properties']},
                    'summary': {'duration': 1500, 'elements': ['equation', 'yield']}
                }
            },
            'comparison': {
                'template_id': 'comparison',
                'concept_type': 'comparison',
                'stages': 3,
                'animation_style': 'side_by_side',
                'metaphor_compatible': ['cricket', 'bollywood'],
                'structure': {
                    'intro': {'duration': 1500, 'elements': ['title', 'items']},
                    'compare': {'duration': 4000, 'elements': ['side_a', 'side_b', 'connectors']},
                    'conclusion': {'duration': 2000, 'elements': ['key_differences', 'summary']}
                }
            }
        }
    
    def add_template(
        self,
        template_id: str,
        template_spec: Dict[str, Any]
    ) -> bool:
        """
        Add custom template to registry
        
        Args:
            template_id: Unique template identifier
            template_spec: Template specification
        
        Returns:
            True if added successfully
        """
        try:
            self.templates[template_id] = template_spec
            logger.info(f"✅ Added template: {template_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add template {template_id}: {e}")
            return False


# Global registry instance
_registry = None

def get_registry() -> VisualTemplateRegistry:
    """Get global template registry instance"""
    global _registry
    if _registry is None:
        _registry = VisualTemplateRegistry()
    return _registry

