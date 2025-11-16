"""
Visual Template Registry
Centralized mapping of concepts → intents → visual templates
AUTO-GENERATES universal professor-led templates for ANY concept
No manual template entries required
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from .universal_template_schema import UniversalTemplateGenerator, UniversalProfessorTemplate

logger = logging.getLogger(__name__)


class VisualTemplateRegistry:
    """
    Manages visual templates organized by concept and intent
    Integrates with existing template system
    """
    
    def __init__(self, template_path: Optional[Path] = None, student_profile: Optional[Dict[str, Any]] = None):
        """
        Initialize template registry with universal template generator
        
        Args:
            template_path: Path to template JSON file (defaults to existing templates.json)
            student_profile: Student profile for metaphor selection
        """
        if template_path is None:
            # Use existing template file (for reference only, not required)
            template_path = Path(__file__).resolve().parents[2] / "visual_library" / "templates.json"
        
        self.template_path = template_path
        self.templates: Dict[str, Any] = self._load_templates()
        self.concept_intent_map: Dict[str, Dict[str, str]] = self._build_concept_intent_map()
        self.student_profile = student_profile
        self.universal_generator = UniversalTemplateGenerator(student_profile=student_profile)  # Auto-generate templates
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load templates from JSON file"""
        try:
            if self.template_path.exists():
                with open(self.template_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Template file not found: {self.template_path}")
                return self._default_templates()
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
            return self._default_templates()
    
    def _build_concept_intent_map(self) -> Dict[str, Dict[str, str]]:
        """
        Build concept → intent → template mapping from existing templates
        Enhances existing topic-based system with intent-aware routing
        """
        concept_map: Dict[str, Dict[str, str]] = {}
        
        for topic_key, template_data in self.templates.items():
            if topic_key == "generic":
                continue
            
            # Extract intent types from template
            intent_types = template_data.get("intent_types", [])
            template_name = template_data.get("template", topic_key)
            visual_type = template_data.get("visual_type", "scene")
            
            # Create concept key (normalize topic)
            concept_key = topic_key.lower().replace('_', '.')
            
            # Map each intent to template
            if concept_key not in concept_map:
                concept_map[concept_key] = {}
            
            for intent in intent_types:
                # Use template name for this intent
                concept_map[concept_key][intent] = template_name
            
            # Also add generic mapping if no specific intent match
            if "generic" not in concept_map[concept_key]:
                concept_map[concept_key]["generic"] = template_name
        
        return concept_map
    
    def get_template(
        self,
        concept_key: str,
        intent: str,
        fallback_intent: str = "concept_explanation",
        concept_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get visual template for concept and intent
        AUTO-GENERATES universal professor-led template if not found in manual templates
        
        Args:
            concept_key: Concept key (e.g., "chemistry.valency")
            intent: Intent type (e.g., "definition_query")
            fallback_intent: Fallback intent if primary not found
            concept_metadata: Optional concept metadata for auto-generation
            
        Returns:
            Template data dict (ALWAYS returns a template, never None)
        """
        # Normalize concept key
        concept_key_normalized = concept_key.lower().replace(' ', '_').replace('.', '_')
        
        # PRIORITY 1: Try manual template from templates.json (for curated concepts)
        manual_template = self._get_manual_template(concept_key_normalized, intent, fallback_intent)
        if manual_template:
            logger.info(f"✅ Using manual template for {concept_key}")
            return manual_template
        
        # PRIORITY 2: AUTO-GENERATE universal professor-led template
        logger.info(f"🎨 Auto-generating universal professor template for {concept_key} (intent: {intent})")
        
        # Extract concept info from concept_key or metadata
        if concept_metadata:
            concept = concept_metadata.get('concept', concept_key.split('.')[-1].replace('_', ' ').title())
            subject = concept_metadata.get('subject', concept_key.split('.')[0] if '.' in concept_key else 'general')
            concept_type = concept_metadata.get('concept_type', 'process')
            key_elements = concept_metadata.get('key_elements', [])
            complexity = concept_metadata.get('complexity', 'medium')
        else:
            # Parse from concept_key
            parts = concept_key.split('.')
            if len(parts) > 1:
                subject = parts[0]
                concept = parts[-1].replace('_', ' ').title()
            else:
                subject = 'general'
                concept = concept_key.replace('_', ' ').title()
            concept_type = 'process'  # Default
            key_elements = []
            complexity = 'medium'
        
        # Generate universal template
        universal_template = self.universal_generator.generate_template(
            concept=concept,
            subject=subject,
            intent=intent,
            concept_type=concept_type,
            key_elements=key_elements,
            complexity=complexity
        )
        
        # Convert to dict format compatible with existing system
        template_dict = universal_template.to_dict()
        
        # Add compatibility fields
        template_dict["intent_types"] = [intent, fallback_intent]
        template_dict["template"] = universal_template.template_id
        template_dict["metaphor"] = f"Professor explaining {concept}"
        template_dict["caption"] = f"Step-by-step explanation of {concept}"
        template_dict["offer_text"] = f"Watch the professor explain {concept}"
        template_dict["render_strategy"] = {"trigger": "auto"}
        template_dict["context_flags"] = []
        
        logger.info(f"✅ Generated universal template: {universal_template.template_id} with {len(universal_template.stages)} stages")
        
        return template_dict
    
    def _get_manual_template(
        self,
        concept_key: str,
        intent: str,
        fallback_intent: str
    ) -> Optional[Dict[str, Any]]:
        """Try to get manual template from templates.json"""
        # Try exact concept key match
        if concept_key in self.concept_intent_map:
            intent_map = self.concept_intent_map[concept_key]
            template_name = intent_map.get(intent) or intent_map.get(fallback_intent) or intent_map.get("generic")
            
            if template_name:
                # Find template by name in existing templates
                for topic, data in self.templates.items():
                    if data.get("template") == template_name:
                        return data
        
        # Try topic-based lookup
        if concept_key in self.templates:
            template_data = self.templates[concept_key]
            intent_types = template_data.get("intent_types", [])
            if intent in intent_types or "generic" in intent_types:
                return template_data
        
        # Try partial match
        concept_parts = concept_key.split('.')
        if len(concept_parts) > 1:
            topic_part = concept_parts[-1]
            if topic_part in self.templates:
                template_data = self.templates[topic_part]
                intent_types = template_data.get("intent_types", [])
                if intent in intent_types or len(intent_types) == 0:
                    return template_data
        
        return None
    
    def add_template(
        self,
        concept_key: str,
        intent: str,
        template_data: Dict[str, Any]
    ) -> None:
        """
        Add or update a template in the registry
        
        Args:
            concept_key: Concept key (e.g., "chemistry.valency")
            intent: Intent type
            template_data: Template data dict
        """
        concept_key = concept_key.lower().replace(' ', '_')
        
        # Add to templates dict
        self.templates[concept_key] = template_data
        
        # Update concept-intent map
        if concept_key not in self.concept_intent_map:
            self.concept_intent_map[concept_key] = {}
        
        self.concept_intent_map[concept_key][intent] = template_data.get("template", concept_key)
    
    def list_templates_for_concept(self, concept_key: str) -> List[str]:
        """List all available templates for a concept"""
        concept_key = concept_key.lower().replace(' ', '_')
        
        if concept_key in self.concept_intent_map:
            return list(self.concept_intent_map[concept_key].keys())
        
        return []
    
    def _default_templates(self) -> Dict[str, Any]:
        """Default templates if file not found"""
        return {
            "generic": {
                "intent_types": ["definition_query", "concept_explanation", "application_request", "deep_dive"],
                "visual_type": "scene",
                "template": "chalkboard_story",
                "metaphor": "Friendly chalkboard walkthrough",
                "asset_url": "https://cdn.mgxai.com/visuals/placeholder.svg",
                "caption": "Dhruv sketches the idea on a chalkboard.",
                "offer_text": "Want a quick sketch?",
                "render_strategy": {
                    "trigger": "on_click"
                },
                "context_flags": []
            }
        }

