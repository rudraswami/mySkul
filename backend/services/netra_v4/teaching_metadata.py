"""
🔮 NETRA v4.0 - Teaching Metadata Generator
===========================================

Generates the teaching layer that transforms a static image into
an interactive learning experience.

This module creates:
    - Hotspots (interactive regions)
    - Teaching steps (progressive reveal sequence)
    - Annotations (overlaid labels and notes)
    - Follow-up questions
    - Key takeaways

Uses Gemini to intelligently map teaching elements to the generated visual.
"""

import logging
import json
import re
from typing import Optional, List
import uuid

from .contracts import (
    VisualRequest,
    ConceptAnalysis,
    VisualStrategy,
    TeachingFlow,
    Hotspot,
    TeachingStep,
    Annotation,
)

logger = logging.getLogger(__name__)


class TeachingMetadataGenerator:
    """
    Generates teaching metadata that makes visuals interactive and educational.
    
    The generated metadata includes:
    - Hotspots: Clickable/tappable regions with explanations
    - Steps: Sequential teaching flow with narration
    - Annotations: Text overlays for key information
    - Follow-ups: Questions to deepen understanding
    - Takeaways: Summary points for retention
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
    
    async def generate_teaching_flow(
        self,
        request: VisualRequest,
        concept: ConceptAnalysis,
        strategy: VisualStrategy,
        imagen_prompt: str
    ) -> TeachingFlow:
        """
        Generate complete teaching metadata for a visual.
        
        This creates the interactive layer that turns a static image
        into a guided learning experience.
        """
        client = await self._get_client()
        
        prompt = f"""You are an expert educational content designer. Create teaching metadata for an educational visual.

CONCEPT: {concept.core_concept}
SUB-CONCEPTS: {', '.join(concept.sub_concepts)}
KEY ENTITIES: {', '.join(concept.key_entities)}
RELATIONSHIPS: {', '.join(concept.relationships)}
TEACHING INTENT: {strategy.intent.value}
USER LEVEL: {request.context.user_level}

THE VISUAL SHOWS: {imagen_prompt}

Generate teaching metadata to make this visual interactive and educational.

Respond with ONLY valid JSON:
{{
    "title": "Engaging title for the visual (5-10 words)",
    "summary": "One clear sentence summarizing the concept",
    
    "hotspots": [
        {{
            "id": "hotspot_1",
            "x_percent": 50,
            "y_percent": 30,
            "width_percent": 15,
            "height_percent": 15,
            "label": "Short label",
            "description": "What this element represents and why it matters",
            "order": 1
        }}
    ],
    
    "steps": [
        {{
            "step_number": 1,
            "title": "Step title",
            "narration": "What a teacher would say explaining this part",
            "focus_hotspots": ["hotspot_1"],
            "duration_ms": 4000
        }}
    ],
    
    "annotations": [
        {{
            "id": "anno_1",
            "text": "Formula or key label",
            "x_percent": 70,
            "y_percent": 20,
            "style": "formula|label|callout|note",
            "font_size": "small|medium|large",
            "show_at_step": 1
        }}
    ],
    
    "follow_up_questions": [
        "Question that deepens understanding",
        "Question that connects to related concepts"
    ],
    
    "key_takeaways": [
        "Main point 1",
        "Main point 2",
        "Main point 3"
    ]
}}

RULES:
- Create 3-6 hotspots covering the key elements in the visual
- Create 3-5 teaching steps that build understanding progressively
- Steps should feel like a teacher walking through the concept
- Position coordinates are percentages (0-100) from top-left
- Make annotations sparse - only key formulas/labels
- Follow-up questions should encourage deeper thinking
- Takeaways should be memorable and exam-relevant"""

        try:
            response = await client.generate_content_async(prompt)
            json_str = response.text.strip()
            
            # Clean markdown if present
            if json_str.startswith("```"):
                json_str = re.sub(r'^```(?:json)?\n?', '', json_str)
                json_str = re.sub(r'\n?```$', '', json_str)
            
            data = json.loads(json_str)
            
            # Parse hotspots
            hotspots = []
            for h in data.get("hotspots", []):
                hotspots.append(Hotspot(
                    id=h.get("id", f"hotspot_{uuid.uuid4().hex[:8]}"),
                    x_percent=float(h.get("x_percent", 50)),
                    y_percent=float(h.get("y_percent", 50)),
                    width_percent=float(h.get("width_percent", 10)),
                    height_percent=float(h.get("height_percent", 10)),
                    label=h.get("label", ""),
                    description=h.get("description", ""),
                    order=int(h.get("order", 0))
                ))
            
            # Parse teaching steps
            steps = []
            for s in data.get("steps", []):
                steps.append(TeachingStep(
                    step_number=int(s.get("step_number", 1)),
                    title=s.get("title", ""),
                    narration=s.get("narration", ""),
                    focus_hotspots=s.get("focus_hotspots", []),
                    duration_ms=int(s.get("duration_ms", 3000))
                ))
            
            # Parse annotations
            annotations = []
            for a in data.get("annotations", []):
                annotations.append(Annotation(
                    id=a.get("id", f"anno_{uuid.uuid4().hex[:8]}"),
                    text=a.get("text", ""),
                    x_percent=float(a.get("x_percent", 50)),
                    y_percent=float(a.get("y_percent", 50)),
                    style=a.get("style", "label"),
                    font_size=a.get("font_size", "medium"),
                    show_at_step=a.get("show_at_step")
                ))
            
            return TeachingFlow(
                title=data.get("title", concept.core_concept),
                summary=data.get("summary", f"Understanding {concept.core_concept}"),
                hotspots=hotspots,
                steps=steps,
                annotations=annotations,
                follow_up_questions=data.get("follow_up_questions", []),
                key_takeaways=data.get("key_takeaways", [])
            )
            
        except Exception as e:
            logger.error(f"Teaching metadata generation failed: {e}")
            # Return minimal fallback
            return self._create_fallback_teaching(concept, strategy)
    
    def _create_fallback_teaching(
        self, 
        concept: ConceptAnalysis, 
        strategy: VisualStrategy
    ) -> TeachingFlow:
        """Create minimal teaching flow when LLM fails"""
        return TeachingFlow(
            title=f"Understanding {concept.core_concept}",
            summary=f"This visual explains {concept.core_concept}",
            hotspots=[
                Hotspot(
                    id="main",
                    x_percent=50,
                    y_percent=50,
                    width_percent=30,
                    height_percent=30,
                    label="Main concept",
                    description=f"The core element representing {concept.core_concept}",
                    order=1
                )
            ],
            steps=[
                TeachingStep(
                    step_number=1,
                    title="Overview",
                    narration=f"Let's understand {concept.core_concept} through this visual.",
                    focus_hotspots=["main"],
                    duration_ms=5000
                )
            ],
            annotations=[],
            follow_up_questions=[
                f"What are the key components of {concept.core_concept}?",
                f"How does this connect to what you already know?"
            ],
            key_takeaways=[
                f"Core concept: {concept.core_concept}",
                f"Key entities: {', '.join(concept.key_entities[:3])}"
            ]
        )
    
    async def enhance_with_exam_tips(
        self,
        teaching_flow: TeachingFlow,
        concept: ConceptAnalysis,
        request: VisualRequest
    ) -> TeachingFlow:
        """
        Optionally enhance teaching flow with exam-specific tips.
        Called separately to keep base generation fast.
        """
        client = await self._get_client()
        
        prompt = f"""Add exam-relevant tips to this teaching content.

CONCEPT: {concept.core_concept}
CURRENT TAKEAWAYS: {teaching_flow.key_takeaways}
USER LEVEL: {request.context.user_level}

Add 2-3 exam tips that help students:
1. Remember the concept better
2. Avoid common mistakes
3. Apply in exam questions

Respond with ONLY valid JSON:
{{
    "exam_tips": [
        "Tip 1: How to remember this",
        "Tip 2: Common mistake to avoid",
        "Tip 3: How this appears in exams"
    ],
    "mnemonics": "A memorable trick if applicable (or null)"
}}"""

        try:
            response = await client.generate_content_async(prompt)
            json_str = response.text.strip()
            
            if json_str.startswith("```"):
                json_str = re.sub(r'^```(?:json)?\n?', '', json_str)
                json_str = re.sub(r'\n?```$', '', json_str)
            
            data = json.loads(json_str)
            
            # Add exam tips to takeaways
            exam_tips = data.get("exam_tips", [])
            teaching_flow.key_takeaways.extend(exam_tips)
            
            # Add mnemonic as annotation if present
            mnemonic = data.get("mnemonics")
            if mnemonic:
                teaching_flow.annotations.append(Annotation(
                    id="mnemonic",
                    text=f"💡 {mnemonic}",
                    x_percent=85,
                    y_percent=90,
                    style="note",
                    font_size="small"
                ))
            
            return teaching_flow
            
        except Exception as e:
            logger.warning(f"Exam tips enhancement failed: {e}")
            return teaching_flow


def create_teaching_generator(gemini_api_key: str, model: str = "gemini-1.5-flash") -> TeachingMetadataGenerator:
    """Factory function to create a teaching metadata generator"""
    return TeachingMetadataGenerator(gemini_api_key, model)

