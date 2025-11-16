"""
Visual Professor Generator
Generates dynamic, interactive, professor-style animated explanations
Integrates with existing visual systems
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional, Any

from .concept_detector import UnifiedConceptDetector, ConceptMetadata
from .template_registry import VisualTemplateRegistry
from ..visual_teaching_engine import VisualTeachingEngine, TeachingVisual

logger = logging.getLogger(__name__)


class VisualProfessorGenerator:
    """
    Main generator for Visual Professor Engine
    Creates dynamic, concept-aware, interactive visual explanations
    """
    
    def __init__(self, student_profile: Optional[Dict[str, Any]] = None):
        self.concept_detector = UnifiedConceptDetector()
        self.template_registry = VisualTemplateRegistry(student_profile=student_profile)
        self.teaching_engine = VisualTeachingEngine()
        self.narration_generator = ProfessorNarrationGenerator()
        self.student_profile = student_profile
    
    async def generate_visual(
        self,
        question: str,
        subject: Optional[str] = None,
        student_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete visual professor explanation
        
        Args:
            question: Student's question
            subject: Optional subject hint
            student_profile: Optional student profile for personalization
            
        Returns:
            Dict with visual data, steps, interactions, narration
        """
        try:
            # Step 1: Detect concept metadata
            metadata = self.concept_detector.detect(question, subject)
            logger.info(f"📊 Detected: {metadata.subject}.{metadata.concept} | Intent: {metadata.intent} | Type: {metadata.concept_type}")
            
            # Step 2: Get template from registry (AUTO-GENERATES if not found)
            primary_intent = metadata.intent[0] if metadata.intent else "concept_explanation"
            template = self.template_registry.get_template(
                concept_key=self.concept_detector.get_visual_key(metadata),
                intent=primary_intent,
                concept_metadata={
                    'concept': metadata.concept,
                    'subject': metadata.subject,
                    'concept_type': metadata.concept_type,
                    'key_elements': metadata.key_elements,
                    'complexity': metadata.complexity
                }
            )
            
            # Template is ALWAYS returned (never None) - universal generator ensures this
            logger.info(f"✅ Template resolved: {template.get('template', 'universal')}")
            
            # Step 3: Check if template is universal (auto-generated)
            is_universal_template = template.get('generation_method') == 'universal_professor_template' or \
                                   template.get('template', '').startswith('professor_')
            
            if is_universal_template:
                # Use universal template directly (already has stages, Lottie, avatar)
                logger.info(f"✅ Using universal professor template with {len(template.get('stages', []))} stages")
                visual_data = self._convert_universal_template_to_visual_data(template, metadata, question)
            else:
                # Step 3b: Generate teaching visual using existing engine (for manual templates)
                teaching_visual = await self.teaching_engine.generate_teaching_visual(
                    question=question,
                    subject=metadata.subject,
                    student_profile=student_profile
                )
                
                # Step 4: Enhance with template-specific data
                visual_data = self._enhance_with_template(teaching_visual, template, metadata)
            
            # Step 5: Generate professor narration for each stage
            visual_data = self._add_professor_narration(visual_data, metadata, question)
            
            # Step 6: Add interaction points
            visual_data = self._add_interactions(visual_data, metadata)
            
            logger.info(f"✅ Generated visual professor explanation: {len(visual_data.get('stages', []))} stages")
            
            return visual_data
            
        except Exception as e:
            logger.error(f"❌ Error generating visual: {e}", exc_info=True)
            # Return fallback visual
            return self._fallback_visual(question, subject)
    
    def _enhance_with_template(
        self,
        teaching_visual: TeachingVisual,
        template: Dict[str, Any],
        metadata: ConceptMetadata
    ) -> Dict[str, Any]:
        """Enhance teaching visual with template-specific data"""
        visual_dict = {
            "visual_id": teaching_visual.visual_id,
            "type": teaching_visual.type,
            "visual_type": template.get("visual_type", "scene"),
            "template": template.get("template", "generic"),
            "stages": [],
            "total_duration_ms": teaching_visual.total_duration_ms,
            "interaction_points": teaching_visual.interaction_points,
            "metadata": {
                **teaching_visual.metadata,
                "concept": metadata.concept,
                "subject": metadata.subject,
                "topic": metadata.topic,
                "intent": metadata.intent,
                "concept_type": metadata.concept_type,
                "template_name": template.get("template"),
                "metaphor": template.get("metaphor"),
            }
        }
        
        # Convert stages to dict format
        for stage in teaching_visual.stages:
            stage_dict = {
                "stage_id": stage.stage_id,
                "duration_ms": stage.duration_ms,
                "narration": stage.narration,
                "animations": stage.animations,
                "interactions": stage.interactions or [],
                "emphasis": stage.emphasis,
            }
            visual_dict["stages"].append(stage_dict)
        
        # Add template-specific assets
        if template.get("lottie_file"):
            visual_dict["lottie_file"] = template["lottie_file"]
        if template.get("asset_url"):
            visual_dict["asset_url"] = template["asset_url"]
        
        return visual_dict
    
    def _add_professor_narration(
        self,
        visual_data: Dict[str, Any],
        metadata: ConceptMetadata,
        question: str
    ) -> Dict[str, Any]:
        """Add professor-style narration to each stage"""
        stages = visual_data.get("stages", [])
        
        for i, stage in enumerate(stages):
            if not stage.get("narration") or stage["narration"].strip() == "":
                # Generate professor narration
                narration = self.narration_generator.generate_narration(
                    stage=stage,
                    metadata=metadata,
                    stage_index=i,
                    total_stages=len(stages),
                    question=question
                )
                stage["narration"] = narration
                stage["narration_style"] = "professor"  # Mark as professor narration
        
        return visual_data
    
    def _add_interactions(
        self,
        visual_data: Dict[str, Any],
        metadata: ConceptMetadata
    ) -> Dict[str, Any]:
        """Add interactive elements based on concept type"""
        stages = visual_data.get("stages", [])
        
        for stage in stages:
            if not stage.get("interactions"):
                stage["interactions"] = []
            
            # Add concept-type-specific interactions
            if metadata.concept_type == "comparison":
                stage["interactions"].append({
                    "type": "hover",
                    "target": "comparison_items",
                    "description": "Hover to see detailed differences"
                })
            elif metadata.concept_type == "process":
                stage["interactions"].append({
                    "type": "scrub",
                    "target": "timeline",
                    "description": "Drag to see each step"
                })
            elif metadata.concept_type == "transformation":
                stage["interactions"].append({
                    "type": "click",
                    "target": "transformation_arrow",
                    "description": "Click to see transformation"
                })
        
        return visual_data
    
    def _convert_universal_template_to_visual_data(
        self,
        template: Dict[str, Any],
        metadata: ConceptMetadata,
        question: str
    ) -> Dict[str, Any]:
        """Convert universal template to visual_data format"""
        stages = template.get('stages', [])
        
        # Convert VisualStage dataclass objects to dicts if needed
        serialized_stages = []
        for stage in stages:
            if hasattr(stage, '__dict__'):
                # It's a dataclass, convert to dict
                from dataclasses import asdict
                stage_dict = asdict(stage)
            elif isinstance(stage, dict):
                # Already a dict
                stage_dict = stage
            else:
                logger.warning(f"⚠️ Unknown stage type: {type(stage)}")
                continue
            
            # Ensure all nested objects are serializable
            serialized_stage = self._serialize_stage(stage_dict)
            serialized_stages.append(serialized_stage)
        
        # Ensure minimum 3 stages
        if len(serialized_stages) < 3:
            logger.warning(f"⚠️ Template has only {len(serialized_stages)} stages, expanding to minimum 3")
            while len(serialized_stages) < 3:
                serialized_stages.append({
                    "stage_id": f"detail_{len(serialized_stages)}",
                    "duration_ms": 2500,
                    "narration": f"Let's explore this concept further.",
                    "narration_style": "professor",
                    "lottie_assets": [],
                    "blocks": [],
                    "interactions": [],
                    "highlights": [],
                    "transitions": {},
                    "emphasis": None
                })
        
        return {
            "visual_id": template.get('template_id', f"prof_{hash(question) % 1000000}"),
            "type": "animated_lesson",
            "visual_type": "professor_led",
            "template": template.get('template_id', 'universal_professor'),
            "stages": serialized_stages,
            "total_duration_ms": template.get('total_duration_ms', sum(s.get('duration_ms', 2500) for s in serialized_stages)),
            "interaction_points": template.get('interaction_points', []),
            "professor_avatar": template.get('professor_avatar', {}),
            "lottie_base_url": template.get('lottie_base_url', 'https://cdn.ai-tutor.in/visuals'),
            "metadata": {
                **template.get('metadata', {}),
                "concept": metadata.concept,
                "subject": metadata.subject,
                "intent": metadata.intent,
                "concept_type": metadata.concept_type,
                "generation_method": "universal_professor_template"
            }
        }
    
    def _serialize_stage(self, stage_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure stage is JSON-serializable"""
        serialized = {}
        
        for key, value in stage_dict.items():
            if value is None:
                serialized[key] = None
            elif isinstance(value, (str, int, float, bool)):
                serialized[key] = value
            elif isinstance(value, list):
                serialized[key] = [self._serialize_value(v) for v in value]
            elif isinstance(value, dict):
                serialized[key] = {k: self._serialize_value(v) for k, v in value.items()}
            elif hasattr(value, '__dict__'):
                from dataclasses import asdict
                serialized[key] = asdict(value)
            else:
                serialized[key] = str(value)
        
        return serialized
    
    def _serialize_value(self, value: Any) -> Any:
        """Serialize a single value"""
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        elif isinstance(value, list):
            return [self._serialize_value(v) for v in value]
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        elif hasattr(value, '__dict__'):
            from dataclasses import asdict
            return asdict(value)
        else:
            return str(value)
    
    def _fallback_visual(self, question: str, subject: Optional[str] = None) -> Dict[str, Any]:
        """Generate a multi-step fallback visual (NEVER single-stage)"""
        # Use universal generator for fallback too
        from .universal_template_schema import UniversalTemplateGenerator
        
        generator = UniversalTemplateGenerator()
        fallback_template = generator.generate_template(
            concept=question.split()[0] if question else "Concept",
            subject=subject or "general",
            intent="concept_explanation",
            concept_type="process",
            key_elements=[],
            complexity="medium"
        )
        
        return self._convert_universal_template_to_visual_data(
            fallback_template.to_dict(),
            ConceptMetadata(
                subject=subject or "general",
                topic="generic",
                concept=question.split()[0] if question else "Concept",
                intent=["concept_explanation"],
                concept_type="process",
                key_elements=[],
                complexity="medium",
                confidence=0.5
            ),
            question
        )


class ProfessorNarrationGenerator:
    """Generates professor-style narration for animation stages"""
    
    def __init__(self):
        # Import concept library for narration content
        try:
            from .concept_library import get_concept_content
            self.get_concept = get_concept_content
        except ImportError:
            self.get_concept = None
    
    def generate_narration(
        self,
        stage: Dict[str, Any],
        metadata: ConceptMetadata,
        stage_index: int,
        total_stages: int,
        question: str
    ) -> str:
        """
        Generate professor narration for a stage
        PRIORITY 1: Use concept library narration (for hero concepts)
        PRIORITY 2: Generate educational narration (not placeholders!)
        
        Style: Clear, precise, step-by-step, like a real professor teaching on board
        """
        # PRIORITY 1: Check if narration already exists (from concept library)
        existing_narration = stage.get("narration", "")
        if existing_narration and existing_narration.strip():
            return existing_narration
        
        # PRIORITY 2: Try to get from concept library
        if self.get_concept:
            concept_data = self.get_concept(metadata.concept.lower())
            if concept_data and 'stages' in concept_data:
                stages_list = concept_data['stages']
                if 0 <= stage_index < len(stages_list):
                    lib_narration = stages_list[stage_index].get('narration', '')
                    if lib_narration:
                        return lib_narration
        
        # PRIORITY 3: Generate educational narration based on concept type and stage
        stage_id = stage.get("stage_id", "")
        animations = stage.get("animations", [])
        
        # Educational narration patterns (NO PLACEHOLDERS!)
        if metadata.concept_type == "comparison":
            return self._generate_comparison_narration(metadata, stage_index)
        elif metadata.concept_type == "process":
            return self._generate_process_narration(metadata, stage_index, stage_id)
        elif metadata.concept_type == "transformation":
            return self._generate_transformation_narration(metadata, stage_index)
        elif metadata.concept_type == "cause_effect":
            return self._generate_cause_effect_narration(metadata, stage_index)
        else:
            return self._generate_generic_educational_narration(metadata, stage_index, total_stages, question)
    
    def _generate_comparison_narration(self, metadata: ConceptMetadata, stage_index: int) -> str:
        """Generate educational narration for comparison concepts"""
        element1 = metadata.key_elements[0] if metadata.key_elements else 'the first concept'
        element2 = metadata.key_elements[1] if len(metadata.key_elements) > 1 else 'the second concept'
        
        narrations = [
            f"Let's compare {element1} and {element2} to understand their key differences.",
            f"First, let's examine {element1} in detail. Notice its unique characteristics.",
            f"Now, let's look at {element2}. See how it differs from {element1}?",
            f"Here are the crucial differences between {element1} and {element2} that you need to remember."
        ]
        return narrations[min(stage_index, len(narrations)-1)]
    
    def _generate_process_narration(self, metadata: ConceptMetadata, stage_index: int, stage_id: str) -> str:
        """Generate educational narration for process concepts"""
        concept = metadata.concept
        
        if stage_index == 0:
            return f"Let's understand how {concept} works by breaking it down into clear steps."
        elif 'summary' in stage_id.lower() or 'conclusion' in stage_id.lower():
            return f"And that's the complete process of {concept}. Notice how each step builds on the previous one."
        else:
            element = metadata.key_elements[stage_index-1] if stage_index-1 < len(metadata.key_elements) else f"this key step"
            return f"Step {stage_index}: {element}. This is a crucial part of {concept}."
    
    def _generate_transformation_narration(self, metadata: ConceptMetadata, stage_index: int) -> str:
        """Generate educational narration for transformation concepts"""
        from_state = metadata.key_elements[0] if metadata.key_elements else 'the initial state'
        to_state = metadata.key_elements[1] if len(metadata.key_elements) > 1 else 'the final state'
        
        narrations = [
            f"Watch how {metadata.concept} transforms {from_state} into something completely different.",
            f"We start with {from_state}. Pay attention to what happens next.",
            f"Now observe the transformation in action. The structure is changing.",
            f"And we arrive at {to_state}. This transformation is the heart of {metadata.concept}."
        ]
        return narrations[min(stage_index, len(narrations)-1)]
    
    def _generate_cause_effect_narration(self, metadata: ConceptMetadata, stage_index: int) -> str:
        """Generate educational narration for cause-effect concepts"""
        cause = metadata.key_elements[0] if metadata.key_elements else 'the initial cause'
        effect = metadata.key_elements[1] if len(metadata.key_elements) > 1 else 'the resulting effect'
        
        narrations = [
            f"Let's explore the cause-effect relationship in {metadata.concept}.",
            f"Here's the cause: {cause}. This triggers a chain of events.",
            f"Watch how {cause} leads to {effect}. This connection is key.",
            f"Understanding this cause-effect relationship helps us predict and control {metadata.concept}."
        ]
        return narrations[min(stage_index, len(narrations)-1)]
    
    def _generate_generic_educational_narration(
        self,
        metadata: ConceptMetadata,
        stage_index: int,
        total_stages: int,
        question: str
    ) -> str:
        """Generate educational narration for any concept (NO PLACEHOLDERS!)"""
        concept = metadata.concept
        
        if stage_index == 0:
            return f"Let's understand {concept} together. I'll break it down into clear, digestible steps."
        elif stage_index == total_stages - 1:
            return f"And that's {concept} explained! Remember the key points we covered. Any questions?"
        elif stage_index == 1:
            return f"First, let's look at what makes {concept} important and how it works."
        elif stage_index == 2:
            return f"Now let's examine the practical aspects of {concept} and how we use it."
        else:
            return f"Here's another important aspect of {concept} that completes our understanding."
    
    def _extract_step_description(self, animations: List[Dict], stage_id: str) -> str:
        """Extract step description from animations"""
        if animations:
            # Try to get description from first animation
            first_anim = animations[0]
            if isinstance(first_anim, dict):
                desc = first_anim.get("description", "")
                if desc:
                    return desc
        
        # Fallback to cleaned stage ID
        return stage_id.replace("_", " ").replace("step", "").strip().title() or "this important step"

