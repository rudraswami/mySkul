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

Uses Gemini 2.5 Flash for intelligent reasoning about visual strategy.
Outputs optimized prompts for DALL-E 3 image generation.
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
# DALL-E 3 PROMPT TEMPLATES
# ============================================

DALLE3_STYLE_DESCRIPTORS = {
    VisualStyle.MODERN_CLEAN: "sleek modern design, clean lines, professional educational illustration, subtle gradients, premium quality, like a high-end textbook cover",
    VisualStyle.ILLUSTRATED: "richly illustrated, vibrant detailed artwork, dynamic composition, engaging colorful scene, like a premium animated educational video frame",
    VisualStyle.INFOGRAPHIC: "elegant infographic design, clear visual hierarchy, beautiful data visualization, modern icons and typography, magazine quality",
    VisualStyle.WHITEBOARD: "artistic whiteboard illustration, hand-drawn aesthetic with character, warm educational feel, like an animated explainer video",
    VisualStyle.SCIENTIFIC: "scientific illustration, precise technical detail, elegant diagram, like Nature or Science journal quality",
    VisualStyle.CONCEPTUAL: "artistic concept visualization, abstract but meaningful, creative visual metaphor, thought-provoking design"
}

DALLE3_INTENT_FRAMING = {
    TeachingIntent.EXPLAIN: "an illuminating visual that explains {concept} in a way that creates an 'aha' moment. Show the concept in action, not as abstract symbols",
    TeachingIntent.COMPARE: "a striking visual comparison that clearly shows the differences and similarities in {concept}. Use visual contrast and side-by-side elements",
    TeachingIntent.SHOW_PROCESS: "a dynamic visual showing the process of {concept} step by step. Show movement, flow, and transformation with visual cues",
    TeachingIntent.SHOW_STRUCTURE: "an elegant exploded or cross-section view revealing the structure of {concept}. Show parts, layers, and relationships clearly",
    TeachingIntent.DERIVE: "a visual journey through the derivation of {concept}, showing each logical step building on the previous",
    TeachingIntent.CALCULATE: "a visual worked example of {concept}, showing the problem-solving process in an intuitive way",
    TeachingIntent.VISUALIZE: "a vivid, immersive visualization of {concept} that makes the abstract tangible and memorable",
    TeachingIntent.CAUSE_EFFECT: "a dramatic visual showing cause and effect in {concept}. Make the causation clear through visual storytelling",
    TeachingIntent.TIMELINE: "a beautifully designed timeline of {concept} that tells a visual story through time",
    TeachingIntent.RELATIONSHIP: "an elegant visual map showing how elements of {concept} connect and relate to each other"
}


class VisualStrategyResolver:
    """
    Resolves the optimal visual strategy for a given question.
    Uses LLM reasoning to understand concept + intent, then
    maps to visual strategy without subject hardcoding.
    """
    
    def __init__(self, gemini_api_key: str, model: str = "gemini-2.5-flash"):
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
    "key_entities": ["Physical objects, forces, particles, or elements that should be SHOWN in the visual"],
    "relationships": ["How Entity1 affects Entity2", "What causes what"],
    "constraints": ["Physical law or rule that applies"],
    "detected_domain": "physics/chemistry/biology/math/history/geography/general",
    "complexity": "simple/moderate/complex",
    "real_world_scenario": "A concrete real-world situation where this concept is visible (e.g., 'a car braking suddenly' for Newton's laws)"
}}

Rules:
- Extract the CONCEPT, not the subject
- Focus on what needs to be VISUALIZED
- Identify real objects that can represent this concept
- Think about what a student could SEE in the real world"""

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
        
        prompt = f"""You are a visual education expert designing visuals for a premium edtech platform.
Determine the best visual strategy for teaching this concept to create an "aha moment".

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
    "layout_type": "central_scene|action_sequence|comparison_split|exploded_view|timeline_flow|relationship_web|dramatic_moment",
    "color_scheme": "educational_blue|nature_green|science_purple|warm_orange|neutral_gray|vibrant_multi",
    "emphasis_elements": ["The ONE thing that should be the visual focus"],
    "visual_metaphor": "A specific real-world scene or analogy that makes this concept click (e.g., 'tug of war' for Newton's third law, 'factory assembly line' for metabolism)",
    "scene_description": "Describe a SPECIFIC visual scene in 1-2 sentences. What would we SEE? Not abstract shapes, but real objects and actions.",
    "avoid_elements": ["generic_diagrams", "abstract_shapes", "text_heavy", "flowchart_boxes"]
}}

CRITICAL RULES:
- The visual_metaphor MUST be a concrete, relatable scenario
- scene_description should describe what a photographer would capture
- NEVER suggest circles, boxes, or arrows as main elements
- Think like a Pixar animator: what scene would make this concept memorable?
- The visual should tell a story, not display information"""

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
                layout_type=data.get("layout_type", "central_scene"),
                color_scheme=data.get("color_scheme", "educational_blue"),
                emphasis_elements=data.get("emphasis_elements", []),
                visual_metaphor=data.get("visual_metaphor"),
                avoid_elements=data.get("avoid_elements", ["generic_diagrams", "abstract_shapes"])
            )
            
        except Exception as e:
            logger.error(f"Strategy resolution failed: {e}")
            return VisualStrategy(
                intent=request.force_intent or TeachingIntent.EXPLAIN,
                style=request.force_style or VisualStyle.ILLUSTRATED,
                complexity=concept.complexity,
                layout_type="central_scene",
                avoid_elements=["generic_diagrams", "abstract_shapes", "flowcharts"]
            )
    
    async def compose_imagen_prompt(
        self,
        request: VisualRequest,
        concept: ConceptAnalysis,
        strategy: VisualStrategy
    ) -> ImagenPrompt:
        """
        Compose an optimized prompt for DALL-E 3 image generation.
        This is critical for producing unique, high-quality visuals.
        """
        client = await self._get_client()
        
        # Get style and intent descriptors
        style_desc = DALLE3_STYLE_DESCRIPTORS.get(strategy.style, DALLE3_STYLE_DESCRIPTORS[VisualStyle.ILLUSTRATED])
        intent_frame = DALLE3_INTENT_FRAMING.get(strategy.intent, DALLE3_INTENT_FRAMING[TeachingIntent.EXPLAIN])
        intent_frame = intent_frame.format(concept=concept.core_concept)
        
        prompt = f"""You are a prompt engineer for DALL-E 3, creating prompts for premium educational visuals.
Your prompts must generate STUNNING, MEMORABLE images that make students understand concepts instantly.

CONCEPT: {concept.core_concept}
INTENT: {intent_frame}
STYLE GUIDE: {style_desc}
VISUAL METAPHOR: {strategy.visual_metaphor or 'find a creative real-world analogy'}
KEY ELEMENTS TO SHOW: {', '.join(concept.key_entities[:5])}
RELATIONSHIPS TO VISUALIZE: {', '.join(concept.relationships[:3])}

Create a DALL-E 3 prompt that will generate an educational masterpiece.

Respond with ONLY valid JSON:
{{
    "main_prompt": "A detailed, vivid description of the scene. Start with the overall composition, then describe specific elements, colors, lighting, and mood. Be SPECIFIC - describe what we SEE, not what we learn. Max 400 words.",
    "negative_prompt": "Things to avoid",
    "style_modifiers": ["modifier1", "modifier2", "modifier3"]
}}

PROMPT ENGINEERING RULES FOR DALL-E 3:
1. Start with the subject and composition: "A [style] illustration showing..."
2. Describe the SCENE, not the concept: What would a camera capture?
3. Include specific visual details: lighting, colors, perspective, mood
4. Use cinematic language: "dramatic angle", "warm lighting", "depth of field"
5. Add quality modifiers: "highly detailed", "professional", "award-winning"
6. NEVER describe abstract concepts - only visible things
7. NEVER request text, labels, or annotations in the image
8. NEVER use generic terms like "educational diagram" or "infographic"

EXAMPLE OF A GOOD PROMPT:
"A stunning illustrated scene showing Newton's third law in action: two ice skaters in mid-push, one moving left and one moving right, their hands just separating. Dynamic motion lines and a slight motion blur suggest the equal and opposite forces. The scene is set on a pristine frozen lake at golden hour, with warm sunlight casting long shadows. Highly detailed, Pixar-quality 3D render style, soft ambient occlusion, professional educational illustration."

EXAMPLE OF A BAD PROMPT:
"An educational diagram explaining Newton's third law with arrows showing action and reaction forces, labeled boxes, and explanatory text." <- TOO ABSTRACT, GENERIC"""

        try:
            response = await client.generate_content_async(prompt)
            json_str = response.text.strip()
            
            if json_str.startswith("```"):
                json_str = re.sub(r'^```(?:json)?\n?', '', json_str)
                json_str = re.sub(r'\n?```$', '', json_str)
            
            data = json.loads(json_str)
            
            main_prompt = data.get("main_prompt", "")
            
            # Ensure the prompt has quality modifiers
            quality_suffix = " Highly detailed, professional quality, suitable for premium educational platform, no text or labels in image."
            if len(main_prompt) + len(quality_suffix) < 4000:
                main_prompt = main_prompt + quality_suffix
            
            return ImagenPrompt(
                main_prompt=main_prompt,
                negative_prompt=data.get("negative_prompt", "text, labels, annotations, diagram arrows, flowchart, generic shapes, low quality, blurry"),
                style_modifiers=data.get("style_modifiers", ["professional", "educational", "vivid"]),
                aspect_ratio="16:9"
            )
            
        except Exception as e:
            logger.error(f"Prompt composition failed: {e}")
            # Fallback to a well-crafted default prompt
            return self._create_fallback_prompt(concept, strategy)
    
    def _create_fallback_prompt(self, concept: ConceptAnalysis, strategy: VisualStrategy) -> ImagenPrompt:
        """Create a high-quality fallback prompt if LLM fails"""
        style_desc = DALLE3_STYLE_DESCRIPTORS.get(strategy.style, DALLE3_STYLE_DESCRIPTORS[VisualStyle.ILLUSTRATED])
        
        main_prompt = f"""A stunning educational illustration showing {concept.core_concept} in action. 
The scene depicts a real-world scenario that demonstrates this concept clearly and memorably. 
{style_desc}. 
Dynamic composition with clear visual hierarchy, engaging colors, and professional lighting. 
The image tells a visual story that creates an 'aha moment' for students.
Highly detailed, award-winning educational illustration quality.
No text, labels, or annotations - purely visual storytelling."""
        
        return ImagenPrompt(
            main_prompt=main_prompt,
            negative_prompt="text, labels, annotations, arrows, flowcharts, generic diagrams, abstract shapes, clip art, low quality, blurry",
            style_modifiers=["professional", "educational", "memorable", "vivid"],
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
        logger.info(f"🎭 Metaphor: {strategy.visual_metaphor or 'none'}")
        
        prompt = await self.compose_imagen_prompt(request, concept, strategy)
        logger.info(f"✍️ DALL-E 3 prompt composed: {len(prompt.main_prompt)} chars")
        
        return concept, strategy, prompt


def create_strategy_resolver(gemini_api_key: str, model: str = "gemini-2.5-flash") -> VisualStrategyResolver:
    """Factory function to create a strategy resolver"""
    return VisualStrategyResolver(gemini_api_key, model)
