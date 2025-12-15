"""
🔮 NETRA v4.0 - Visual Strategy Resolver
========================================

Determines the optimal visual strategy based on CONCEPT + INTENT.
NO subject hardcoding - routes purely by what the concept is and
what the student wants to understand.

This is the brain that decides:
    - What TYPE of visual is needed
    - What STYLE suits the concept
    - What LAYOUT will communicate best
    - What ELEMENTS should be emphasized

Uses Gemini 1.5 Flash for intelligent reasoning about visual strategy.
"""

import logging
import json
import re
from typing import Optional, Dict, Any

from .contracts import (
    VisualRequest,
    ConceptAnalysis,
    VisualStrategy,
    ImagenPrompt,
    TeachingIntent,
    VisualStyle,
    ComplexityLevel,
)

logger = logging.getLogger(__name__)


# ============================================
# STRATEGY RESOLVER
# ============================================

class VisualStrategyResolver:
    """
    Resolves the optimal visual strategy for a given question.
    Uses LLM reasoning to understand concept + intent, then
    maps to visual strategy without subject hardcoding.
    """
    
    def __init__(self, gemini_api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = gemini_api_key
        self.model = model
        self._client = None
    
    async def _get_client(self):
        """Lazy initialization of Gemini client"""
        if self._client is None:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(self.model)
        return self._client
    
    async def analyze_concept(self, request: VisualRequest) -> ConceptAnalysis:
        """
        Analyze the question to extract the core concept.
        This is subject-agnostic - we care about WHAT, not WHICH subject.
        """
        client = await self._get_client()
        
        prompt = f"""Analyze this educational question and extract the core concept for visualization.

QUESTION: "{request.question}"

USER LEVEL: {request.context.user_level}

Respond with ONLY valid JSON (no markdown):
{{
    "core_concept": "The main concept being asked about (e.g., 'photosynthesis', 'Newton third law', 'quadratic equation')",
    "sub_concepts": ["Related concept 1", "Related concept 2"],
    "key_entities": ["Entity 1", "Entity 2"],
    "relationships": ["Entity1 causes Entity2", "Entity3 contains Entity4"],
    "constraints": ["Physical law or rule that applies"],
    "detected_domain": "physics/chemistry/biology/math/history/geography/general",
    "complexity": "simple/moderate/complex"
}}

Rules:
- Extract the CONCEPT, not the subject
- Focus on what needs to be VISUALIZED
- Identify relationships that should be SHOWN
- Keep it focused on visual representation needs"""

        try:
            response = await client.generate_content_async(prompt)
            json_str = response.text.strip()
            
            # Clean markdown if present
            if json_str.startswith("```"):
                json_str = re.sub(r'^```(?:json)?\n?', '', json_str)
                json_str = re.sub(r'\n?```$', '', json_str)
            
            data = json.loads(json_str)
            
            return ConceptAnalysis(
                core_concept=data.get("core_concept", request.question[:50]),
                sub_concepts=data.get("sub_concepts", []),
                key_entities=data.get("key_entities", []),
                relationships=data.get("relationships", []),
                constraints=data.get("constraints", []),
                detected_domain=data.get("detected_domain"),
                complexity=ComplexityLevel(data.get("complexity", "moderate"))
            )
            
        except Exception as e:
            logger.error(f"Concept analysis failed: {e}")
            # Fallback to basic analysis
            return ConceptAnalysis(
                core_concept=request.question[:100],
                complexity=ComplexityLevel.MODERATE
            )
    
    async def resolve_strategy(
        self, 
        request: VisualRequest, 
        concept: ConceptAnalysis
    ) -> VisualStrategy:
        """
        Determine the optimal visual strategy based on concept + intent.
        This is where the magic happens - no templates, pure reasoning.
        """
        client = await self._get_client()
        
        prompt = f"""You are a visual education expert. Determine the best visual strategy for teaching this concept.

CONCEPT: {concept.core_concept}
SUB-CONCEPTS: {', '.join(concept.sub_concepts)}
KEY ENTITIES: {', '.join(concept.key_entities)}
RELATIONSHIPS: {', '.join(concept.relationships)}
COMPLEXITY: {concept.complexity.value}
USER LEVEL: {request.context.user_level}

QUESTION: "{request.question}"

Respond with ONLY valid JSON:
{{
    "intent": "explain|compare|show_process|show_structure|derive|calculate|visualize|cause_effect|timeline|relationship",
    "style": "modern_clean|illustrated|infographic|whiteboard|scientific|conceptual",
    "layout_type": "central_focus|left_to_right|top_to_bottom|circular|hierarchical|split_comparison|radial|timeline_horizontal",
    "color_scheme": "educational_blue|nature_green|science_purple|warm_orange|neutral_gray|vibrant_multi",
    "emphasis_elements": ["What should stand out visually"],
    "visual_metaphor": "A real-world metaphor that helps understanding (or null)",
    "avoid_elements": ["generic_shapes", "clip_art", "text_heavy"]
}}

RULES:
- Choose intent based on WHAT the student wants to understand
- Choose style based on WHAT the concept is, not which subject
- Layout should match the concept's natural structure
- NEVER default to generic diagrams
- Metaphor should make the concept relatable"""

        try:
            response = await client.generate_content_async(prompt)
            json_str = response.text.strip()
            
            if json_str.startswith("```"):
                json_str = re.sub(r'^```(?:json)?\n?', '', json_str)
                json_str = re.sub(r'\n?```$', '', json_str)
            
            data = json.loads(json_str)
            
            # Handle forced overrides
            intent = request.force_intent or TeachingIntent(data.get("intent", "explain"))
            style = request.force_style or VisualStyle(data.get("style", "modern_clean"))
            
            return VisualStrategy(
                intent=intent,
                style=style,
                complexity=concept.complexity,
                layout_type=data.get("layout_type", "central_focus"),
                color_scheme=data.get("color_scheme", "educational_blue"),
                emphasis_elements=data.get("emphasis_elements", []),
                visual_metaphor=data.get("visual_metaphor"),
                avoid_elements=data.get("avoid_elements", ["generic_shapes", "clip_art"])
            )
            
        except Exception as e:
            logger.error(f"Strategy resolution failed: {e}")
            return VisualStrategy(
                intent=request.force_intent or TeachingIntent.EXPLAIN,
                style=request.force_style or VisualStyle.MODERN_CLEAN,
                complexity=concept.complexity,
                layout_type="central_focus",
                avoid_elements=["generic_shapes", "clip_art"]
            )
    
    async def compose_imagen_prompt(
        self,
        request: VisualRequest,
        concept: ConceptAnalysis,
        strategy: VisualStrategy
    ) -> ImagenPrompt:
        """
        Compose an optimized prompt for Imagen image generation.
        This is critical for producing unique, high-quality visuals.
        """
        client = await self._get_client()
        
        # Style descriptors based on strategy
        style_map = {
            VisualStyle.MODERN_CLEAN: "clean minimalist design, modern flat illustration, professional educational diagram",
            VisualStyle.ILLUSTRATED: "rich detailed illustration, educational artwork, vibrant colors, engaging visual",
            VisualStyle.INFOGRAPHIC: "infographic style, data visualization, clear labels, organized layout",
            VisualStyle.WHITEBOARD: "hand-drawn whiteboard style, sketch aesthetic, casual educational",
            VisualStyle.SCIENTIFIC: "scientific diagram, technical illustration, precise, academic style",
            VisualStyle.CONCEPTUAL: "abstract concept art, metaphorical visualization, creative interpretation"
        }
        
        style_desc = style_map.get(strategy.style, style_map[VisualStyle.MODERN_CLEAN])
        
        # Intent-based framing
        intent_framing = {
            TeachingIntent.EXPLAIN: f"educational diagram explaining {concept.core_concept}",
            TeachingIntent.COMPARE: f"comparison visual showing differences between aspects of {concept.core_concept}",
            TeachingIntent.SHOW_PROCESS: f"process flow diagram showing how {concept.core_concept} works step by step",
            TeachingIntent.SHOW_STRUCTURE: f"structural diagram showing parts and components of {concept.core_concept}",
            TeachingIntent.DERIVE: f"step-by-step derivation visual for {concept.core_concept}",
            TeachingIntent.CALCULATE: f"worked example showing calculation of {concept.core_concept}",
            TeachingIntent.VISUALIZE: f"visualization of {concept.core_concept}",
            TeachingIntent.CAUSE_EFFECT: f"cause and effect diagram showing why {concept.core_concept} happens",
            TeachingIntent.TIMELINE: f"timeline showing progression of {concept.core_concept}",
            TeachingIntent.RELATIONSHIP: f"relationship map showing connections in {concept.core_concept}"
        }
        
        base_framing = intent_framing.get(strategy.intent, intent_framing[TeachingIntent.EXPLAIN])
        
        prompt = f"""Create the perfect Imagen prompt for this educational visual.

CONCEPT: {concept.core_concept}
INTENT: {base_framing}
STYLE: {style_desc}
LAYOUT: {strategy.layout_type}
KEY ENTITIES TO SHOW: {', '.join(concept.key_entities[:5])}
RELATIONSHIPS TO VISUALIZE: {', '.join(concept.relationships[:3])}
METAPHOR (if helpful): {strategy.visual_metaphor or 'none'}
EMPHASIZE: {', '.join(strategy.emphasis_elements[:3])}

Generate a detailed, specific image generation prompt.

Respond with ONLY valid JSON:
{{
    "main_prompt": "A detailed, specific prompt that will generate a unique educational visual. Include specific visual elements, composition, style details. Be SPECIFIC not generic.",
    "negative_prompt": "Things to avoid: blurry, text-heavy, generic clip art, low quality, stock photo feel",
    "style_modifiers": ["modifier1", "modifier2", "modifier3"],
    "aspect_ratio": "16:9"
}}

CRITICAL RULES:
- The prompt must be SPECIFIC to this exact concept
- NO generic descriptions like "educational diagram" alone
- Include SPECIFIC visual elements that represent the concept
- Describe COMPOSITION (what's where in the image)
- Describe VISUAL STYLE in detail
- The result must look like premium edtech content, not a textbook diagram"""

        try:
            response = await client.generate_content_async(prompt)
            json_str = response.text.strip()
            
            if json_str.startswith("```"):
                json_str = re.sub(r'^```(?:json)?\n?', '', json_str)
                json_str = re.sub(r'\n?```$', '', json_str)
            
            data = json.loads(json_str)
            
            return ImagenPrompt(
                main_prompt=data.get("main_prompt", f"{base_framing}, {style_desc}"),
                negative_prompt=data.get("negative_prompt", "blurry, low quality, text-heavy, generic, clip art"),
                style_modifiers=data.get("style_modifiers", []),
                aspect_ratio=data.get("aspect_ratio", "16:9")
            )
            
        except Exception as e:
            logger.error(f"Prompt composition failed: {e}")
            # Fallback prompt
            return ImagenPrompt(
                main_prompt=f"{base_framing}, {style_desc}, high quality educational illustration, clear and engaging",
                negative_prompt="blurry, low quality, text-heavy, generic, clip art, stock photo",
                style_modifiers=["educational", "modern", "clear"],
                aspect_ratio="16:9"
            )
    
    async def resolve_complete(self, request: VisualRequest) -> tuple[ConceptAnalysis, VisualStrategy, ImagenPrompt]:
        """
        Complete resolution pipeline: analyze → strategize → compose prompt.
        Returns all three artifacts for the orchestrator.
        """
        concept = await self.analyze_concept(request)
        logger.info(f"🧠 Concept analyzed: {concept.core_concept} ({concept.complexity.value})")
        
        strategy = await self.resolve_strategy(request, concept)
        logger.info(f"📐 Strategy resolved: {strategy.intent.value} / {strategy.style.value}")
        
        prompt = await self.compose_imagen_prompt(request, concept, strategy)
        logger.info(f"✍️ Imagen prompt composed: {len(prompt.main_prompt)} chars")
        
        return concept, strategy, prompt


def create_strategy_resolver(gemini_api_key: str, model: str = "gemini-1.5-flash") -> VisualStrategyResolver:
    """Factory function to create a strategy resolver"""
    return VisualStrategyResolver(gemini_api_key, model)

