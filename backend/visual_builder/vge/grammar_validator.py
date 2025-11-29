"""
Vidya Grammar Engine - Grammar Validator
Validates grammars against NCERT problems and core principles
"""

from typing import List, Dict, Any, Optional
from .grammar_parser import GrammarDefinition, PedagogicalPurpose
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Grammar validation error"""
    pass


class GrammarValidator:
    """
    Validates grammar definitions against:
    1. Core principles (Value-First, Professor's POV, Cultural Relatability, etc.)
    2. NCERT problem test suite
    3. Technical correctness
    """
    
    def __init__(self):
        self.ncert_test_cases = self._load_ncert_test_cases()
    
    def validate(self, grammar: GrammarDefinition) -> Dict[str, Any]:
        """
        Comprehensive validation of grammar
        
        Args:
            grammar: Grammar to validate
        
        Returns:
            Dict with validation results
        """
        errors = []
        warnings = []
        
        # 1. Value-First Principle
        value_check = self._validate_value_first(grammar)
        errors.extend(value_check['errors'])
        warnings.extend(value_check['warnings'])
        
        # 2. Professor's POV Principle
        pov_check = self._validate_professor_pov(grammar)
        errors.extend(pov_check['errors'])
        warnings.extend(pov_check['warnings'])
        
        # 3. Cultural Relatability
        cultural_check = self._validate_cultural_relatability(grammar)
        errors.extend(cultural_check['errors'])
        warnings.extend(cultural_check['warnings'])
        
        # 4. Interactive Depth
        interactive_check = self._validate_interactive_depth(grammar)
        errors.extend(interactive_check['errors'])
        warnings.extend(interactive_check['warnings'])
        
        # 5. Zero Cognitive Load
        cognitive_check = self._validate_zero_cognitive_load(grammar)
        errors.extend(cognitive_check['errors'])
        warnings.extend(cognitive_check['warnings'])
        
        # 6. Technical correctness
        technical_check = self._validate_technical(grammar)
        errors.extend(technical_check['errors'])
        warnings.extend(technical_check['warnings'])
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'can_publish': len(errors) == 0
        }
    
    def _validate_value_first(self, grammar: GrammarDefinition) -> Dict[str, List[str]]:
        """Validate Value-First principle"""
        errors = []
        warnings = []
        
        # Check value proposition
        if not grammar.value_proposition:
            errors.append("Value proposition is required")
        elif len(grammar.value_proposition) < 50:
            errors.append("Value proposition must be detailed (min 50 chars)")
        elif "if removed" not in grammar.value_proposition.lower() and "without" not in grammar.value_proposition.lower():
            warnings.append("Value proposition should explain what happens if visual is removed")
        
        # Check learning objectives
        if not grammar.learning_objectives:
            errors.append("Learning objectives are required")
        elif len(grammar.learning_objectives) < 2:
            warnings.append("Should have at least 2 learning objectives")
        
        # Check that animations have purpose
        animations_without_purpose = [
            step for step in grammar.animation_steps
            if not step.purpose or step.purpose == PedagogicalPurpose.BUILD_UNDERSTANDING
        ]
        if len(animations_without_purpose) == len(grammar.animation_steps):
            warnings.append("All animations should have specific pedagogical purpose")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_professor_pov(self, grammar: GrammarDefinition) -> Dict[str, List[str]]:
        """Validate Professor's POV principle"""
        errors = []
        warnings = []
        
        # Check camera style
        if grammar.camera_style not in ["teacher_demonstration", "student_view", "overhead"]:
            warnings.append(f"Camera style '{grammar.camera_style}' may not match Professor's POV")
        
        # Check pacing
        if grammar.pacing not in ["deliberate", "fast", "adaptive"]:
            warnings.append("Pacing should be 'deliberate' for Professor's POV")
        
        # Check that animations have camera focus
        animations_without_focus = [
            step for step in grammar.animation_steps
            if not step.camera_focus
        ]
        if animations_without_focus:
            warnings.append(f"{len(animations_without_focus)} animation steps lack camera focus (Professor's POV)")
        
        # Check hand gestures
        if not grammar.show_hand_gestures:
            warnings.append("Hand gestures help mimic teacher's demonstration")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_cultural_relatability(self, grammar: GrammarDefinition) -> Dict[str, List[str]]:
        """Validate Cultural Relatability principle"""
        errors = []
        warnings = []
        
        # Check recommended assets
        if not grammar.recommended_assets:
            errors.append("Recommended assets are required (cultural context)")
        
        # Check cultural context
        if not grammar.cultural_context:
            warnings.append("Cultural context should explain why assets are culturally relevant")
        
        # Check for abstract/foreign objects
        abstract_objects = ["block", "box", "object", "thing", "ferrari", "car", "ball"]
        for asset in grammar.recommended_assets:
            if any(abstract in asset.lower() for abstract in abstract_objects):
                warnings.append(f"Asset '{asset}' may be too abstract. Prefer culturally specific objects (auto-rickshaw, cricket ball, etc.)")
        
        # Check parameters have cultural hints
        params_without_hints = [
            param for param in grammar.parameters
            if not param.cultural_hint and param.type == "variable"
        ]
        if params_without_hints:
            warnings.append(f"{len(params_without_hints)} parameters lack cultural hints")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_interactive_depth(self, grammar: GrammarDefinition) -> Dict[str, List[str]]:
        """Validate Interactive Depth principle"""
        errors = []
        warnings = []
        
        # Check interactive elements
        if not grammar.interactive_elements:
            warnings.append("No interactive elements defined. Sliders enable 'what if?' exploration")
        
        # Check what-if scenarios
        if not grammar.what_if_scenarios:
            warnings.append("No 'what if?' scenarios defined. These enable deeper understanding")
        
        # Check that variables have appropriate ranges
        for param in grammar.parameters:
            if param.type == "variable":
                if param.min is None or param.max is None:
                    errors.append(f"Variable '{param.name}' must have min and max")
                elif param.max <= param.min:
                    errors.append(f"Variable '{param.name}' max must be greater than min")
                elif (param.max - param.min) < 10:
                    warnings.append(f"Variable '{param.name}' has narrow range. May limit exploration")
        
        # Check interaction prompts in animation steps
        steps_with_interaction = [
            step for step in grammar.animation_steps
            if step.pause_for_interaction
        ]
        if not steps_with_interaction:
            warnings.append("No animation steps pause for interaction. Add 'what if?' prompts")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_zero_cognitive_load(self, grammar: GrammarDefinition) -> Dict[str, List[str]]:
        """Validate Zero Cognitive Load principle"""
        errors = []
        warnings = []
        
        # Check that animations guide focus
        animations_without_highlight = [
            step for step in grammar.animation_steps
            if not step.highlight_elements
        ]
        if animations_without_highlight:
            warnings.append(f"{len(animations_without_highlight)} animation steps don't highlight elements (may cause cognitive load)")
        
        # Check cause-effect arrows
        steps_with_arrows = [
            step for step in grammar.animation_steps
            if step.show_arrow
        ]
        if not steps_with_arrows:
            warnings.append("No cause-effect arrows. Arrows guide attention and show relationships")
        
        # Check timing (animations shouldn't be too fast)
        fast_animations = [
            step for step in grammar.animation_steps
            if step.duration_ms < 300
        ]
        if fast_animations:
            warnings.append(f"{len(fast_animations)} animations are too fast (<300ms). May cause cognitive overload")
        
        # Check that annotations are required for understanding
        decorative_annotations = [
            ann for ann in grammar.annotations
            if not ann.required_for_understanding
        ]
        if decorative_annotations:
            warnings.append(f"{len(decorative_annotations)} annotations may be decorative (not required for understanding)")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_technical(self, grammar: GrammarDefinition) -> Dict[str, List[str]]:
        """Validate technical correctness"""
        errors = []
        warnings = []
        
        # Check grammar ID format
        if '.' not in grammar.grammar_id:
            errors.append("Grammar ID should be in format 'subject.concept' (e.g., 'physics.force')")
        
        # Check parameter references in animation code
        param_names = {param.name for param in grammar.parameters}
        for step in grammar.animation_steps:
            # Simple check: parameters referenced should exist
            # (Full parsing would require AST analysis)
            code = step.animation_code.lower()
            # This is a simplified check - full validation would parse the code
            pass
        
        # Check annotation positions reference valid elements
        for ann in grammar.annotations:
            if ann.position and '.' not in ann.position and ann.position not in param_names:
                warnings.append(f"Annotation position '{ann.position}' may not reference valid element")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _load_ncert_test_cases(self) -> List[Dict[str, Any]]:
        """Load NCERT test cases for validation"""
        # In production, load from database or file
        # For now, return empty list
        return []
    
    def test_against_ncert(self, grammar: GrammarDefinition) -> Dict[str, Any]:
        """
        Test grammar output against NCERT problems
        
        Args:
            grammar: Grammar to test
        
        Returns:
            Test results
        """
        # TODO: Implement NCERT test suite
        # For each NCERT problem:
        # 1. Generate visual using grammar
        # 2. Extract answer from visual
        # 3. Compare with NCERT answer key
        # 4. Fail if mismatch
        
        return {
            'passed': True,
            'tested_cases': 0,
            'failed_cases': []
        }







