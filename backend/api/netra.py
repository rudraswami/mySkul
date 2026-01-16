"""
🔮 NETRA API - Intelligent Visual Reasoning Engine
===================================================

LLM-powered concept understanding for generating educational visuals.
This is the backend brain of the NETRA visual engine.

Endpoints:
- POST /api/netra/parse-concept - Parse question into visual specification
- POST /api/netra/generate-scene - Generate complete scene graph
"""

import os
import json
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/netra", tags=["netra"])

# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class ParseConceptRequest(BaseModel):
    """Request to parse a student question into visual components"""
    question: str = Field(..., description="Student's question")
    subject: Optional[str] = Field(None, description="Subject context (physics, chemistry, etc.)")
    level: Optional[str] = Field("high_school", description="Education level")
    language: Optional[str] = Field("en", description="Language preference")


class Entity(BaseModel):
    """A visual entity (object, force, concept)"""
    id: str
    type: str  # body, force, vector, structure, process, etc.
    label: str
    variant: Optional[str] = None
    properties: Dict[str, Any] = {}


class Relationship(BaseModel):
    """A relationship between entities"""
    from_entity: str = Field(..., alias="from")
    to_entity: str = Field(..., alias="to")
    type: str  # acts_on, causes, contains, opposite_to, etc.
    label: Optional[str] = None
    
    class Config:
        populate_by_name = True


class VisualHint(BaseModel):
    """Visual rendering hints"""
    layout_strategy: str  # force_diagram, causal_flow, cycle, structure, etc.
    emphasis: List[str] = []  # Entity IDs to emphasize
    style: str = "sketch"  # sketch, technical, colorful
    annotations: List[str] = []  # Key points to annotate


class ConceptGraphResponse(BaseModel):
    """Parsed concept ready for visual generation"""
    success: bool
    domain: str
    topic: str
    entities: List[Entity]
    relationships: List[Relationship]
    constraints: List[str] = []
    visual_hints: VisualHint
    title: str
    summary: str
    generation_time_ms: int


# ============================================
# LLM PROMPT TEMPLATE
# ============================================

CONCEPT_PARSER_PROMPT = '''You are an expert educational visual designer. Your job is to analyze a student's question and break it down into components that can be visualized.

## Student Question
"{question}"

## Subject Context
{subject}

## Your Task
Analyze this question and extract:

1. **Domain**: The subject area (physics, chemistry, biology, mathematics)
2. **Topic**: The specific concept being asked about
3. **Entities**: Objects, forces, structures, or concepts that should be shown
4. **Relationships**: How entities interact or relate
5. **Visual Layout**: Best way to display this (force_diagram, process_flow, structure, comparison, etc.)

## Entity Types
- **body**: Physical objects (ball, block, car, rocket, pendulum)
- **force**: Forces (gravity, friction, tension, normal, applied)
- **vector**: Directional quantities (velocity, acceleration, momentum)
- **structure**: Structures (cell, atom, molecule, organ, container)
- **process**: Process steps (reaction, transformation, cycle step)
- **concept**: Abstract concepts (energy, heat, wave)
- **label**: Text annotations

## Relationship Types
- **acts_on**: Force acts on body
- **causes**: A causes B
- **contains**: A contains B
- **opposite_to**: Equal and opposite (Newton's 3rd law)
- **becomes**: A transforms into B
- **connects**: A connects to B

## Layout Strategies
- **force_diagram**: Central body with forces around it (physics)
- **causal_flow**: Left-to-right cause-effect chain
- **cycle**: Circular process (water cycle, cell cycle)
- **structure**: Hierarchical containment (cell structure, atom structure)
- **comparison**: Side-by-side comparison
- **timeline**: Sequential events
- **graph**: Mathematical function plot

## Response Format
Respond with ONLY valid JSON (no markdown, no explanation):
{{
  "domain": "physics|chemistry|biology|mathematics",
  "topic": "Brief topic name",
  "title": "Visual Title (short, engaging)",
  "summary": "One sentence explaining the concept",
  "entities": [
    {{
      "id": "unique_id",
      "type": "body|force|vector|structure|process|concept|label",
      "label": "Display label",
      "variant": "optional variant (ball, box, gravitational, friction, etc.)",
      "properties": {{
        "direction": "up|down|left|right (for forces/vectors)",
        "color": "#hexcolor (optional)",
        "importance": "high|normal|low",
        "mass": "m (for bodies)",
        "formula": "F=ma (for concepts)"
      }}
    }}
  ],
  "relationships": [
    {{
      "from": "entity_id",
      "to": "entity_id", 
      "type": "acts_on|causes|contains|opposite_to|becomes|connects",
      "label": "optional label"
    }}
  ],
  "constraints": ["List of physics/chemistry laws that apply"],
  "visual_hints": {{
    "layout_strategy": "force_diagram|causal_flow|cycle|structure|comparison|timeline|graph",
    "emphasis": ["entity_ids to highlight"],
    "style": "sketch|technical|colorful",
    "annotations": ["Key points to show as labels"]
  }}
}}

## Example: "Explain friction"
{{
  "domain": "physics",
  "topic": "Friction",
  "title": "Forces on a Block with Friction",
  "summary": "Friction is a force that opposes motion between surfaces in contact",
  "entities": [
    {{"id": "block", "type": "body", "label": "Block", "variant": "box", "properties": {{"mass": "m", "importance": "high"}}}},
    {{"id": "surface", "type": "structure", "label": "Rough Surface", "variant": "ground", "properties": {{"importance": "normal"}}}},
    {{"id": "weight", "type": "force", "label": "Weight (W=mg)", "variant": "gravitational", "properties": {{"direction": "down"}}}},
    {{"id": "normal", "type": "force", "label": "Normal (N)", "variant": "normal", "properties": {{"direction": "up"}}}},
    {{"id": "friction", "type": "force", "label": "Friction (f=μN)", "variant": "friction", "properties": {{"direction": "left", "color": "#E67E22", "importance": "high"}}}},
    {{"id": "applied", "type": "force", "label": "Applied (F)", "variant": "applied", "properties": {{"direction": "right"}}}}
  ],
  "relationships": [
    {{"from": "weight", "to": "block", "type": "acts_on"}},
    {{"from": "normal", "to": "block", "type": "acts_on"}},
    {{"from": "friction", "to": "block", "type": "acts_on"}},
    {{"from": "applied", "to": "block", "type": "acts_on"}},
    {{"from": "normal", "to": "weight", "type": "opposite_to", "label": "Equal magnitude"}},
    {{"from": "friction", "to": "applied", "type": "opposite_to", "label": "Opposes motion"}}
  ],
  "constraints": ["Newton's Second Law: ΣF = ma", "f = μN where μ is coefficient of friction"],
  "visual_hints": {{
    "layout_strategy": "force_diagram",
    "emphasis": ["friction", "block"],
    "style": "sketch",
    "annotations": ["f = μN", "Friction opposes motion"]
  }}
}}

Now analyze the student's question and respond with JSON only:'''


# ============================================
# LLM INTEGRATION
# ============================================

async def call_concept_parser_llm(question: str, subject: str = None) -> Dict[str, Any]:
    """
    Call LLM to parse concept into visual components
    """
    from services.llm_service import call_llm
    from core.config import settings
    
    # Get API key - use OPENAI_API_KEY (gpt-4.1-mini is our base model)
    api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("No OPENAI_API_KEY found in settings or environment")
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    
    # Build prompt
    subject_context = f"Subject: {subject}" if subject else "Subject: Auto-detect from question"
    prompt = CONCEPT_PARSER_PROMPT.format(
        question=question,
        subject=subject_context
    )
    
    try:
        logger.info(f"🔮 [NETRA] Calling LLM for concept parsing: {question[:50]}...")
        
        # Use configured model (gpt-4o-mini by default - fast and reliable)
        model = settings.BASE_MODEL or "gpt-4o-mini"
        
        response = await call_llm(
            prompt=prompt,
            api_key=api_key,
            temperature=0.3,  # Low temperature for consistent structured output
            max_tokens=2000,
            model=model,
            system_message="You are an expert educational visual designer. Respond with valid JSON only."
        )
        
        # Parse JSON from response
        # Handle potential markdown code blocks
        json_str = response.strip()
        if json_str.startswith("```"):
            # Extract JSON from code block
            json_str = re.sub(r'^```(?:json)?\n?', '', json_str)
            json_str = re.sub(r'\n?```$', '', json_str)
        
        parsed = json.loads(json_str)
        logger.info(f"✅ [NETRA] LLM parsed concept: {parsed.get('topic', 'Unknown')}")
        
        return parsed
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ [NETRA] Failed to parse LLM JSON response: {e}")
        logger.error(f"Response was: {response[:500] if response else 'None'}")
        raise HTTPException(status_code=500, detail=f"LLM returned invalid JSON: {str(e)}")
    except Exception as e:
        logger.error(f"❌ [NETRA] LLM call failed: {e}")
        raise HTTPException(status_code=500, detail=f"LLM call failed: {str(e)}")


# ============================================
# API ENDPOINTS
# ============================================

@router.post("/parse-concept", response_model=ConceptGraphResponse)
async def parse_concept(request: ParseConceptRequest):
    """
    🔮 Parse a student question into a visual concept graph using LLM
    
    This is the core intelligence of NETRA - understanding what to visualize.
    
    PERFORMANCE: Hard 5s timeout to prevent frontend hanging
    """
    import asyncio
    start_time = datetime.now()
    
    # Hard SLA: 5 seconds max for visual parsing
    NETRA_PARSE_TIMEOUT = 5.0
    
    logger.info(f"🔮 [NETRA] Parsing concept (timeout={NETRA_PARSE_TIMEOUT}s): {request.question[:60]}")
    
    try:
        # Call LLM to parse concept WITH TIMEOUT
        parsed = await asyncio.wait_for(
            call_concept_parser_llm(
                question=request.question,
                subject=request.subject
            ),
            timeout=NETRA_PARSE_TIMEOUT
        )
        
        # Build response
        entities = []
        for e in parsed.get("entities", []):
            entities.append(Entity(
                id=e["id"],
                type=e["type"],
                label=e["label"],
                variant=e.get("variant"),
                properties=e.get("properties", {})
            ))
        
        relationships = []
        for r in parsed.get("relationships", []):
            relationships.append(Relationship(
                from_entity=r["from"],
                to_entity=r["to"],
                type=r["type"],
                label=r.get("label")
            ))
        
        visual_hints_data = parsed.get("visual_hints", {})
        visual_hints = VisualHint(
            layout_strategy=visual_hints_data.get("layout_strategy", "causal_flow"),
            emphasis=visual_hints_data.get("emphasis", []),
            style=visual_hints_data.get("style", "sketch"),
            annotations=visual_hints_data.get("annotations", [])
        )
        
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        response = ConceptGraphResponse(
            success=True,
            domain=parsed.get("domain", "physics"),
            topic=parsed.get("topic", "Concept"),
            entities=entities,
            relationships=relationships,
            constraints=parsed.get("constraints", []),
            visual_hints=visual_hints,
            title=parsed.get("title", request.question),
            summary=parsed.get("summary", ""),
            generation_time_ms=elapsed_ms
        )
        
        logger.info(f"✅ [NETRA] Concept parsed in {elapsed_ms}ms: {response.topic} ({len(entities)} entities)")
        
        return response
        
    except asyncio.TimeoutError:
        # TIMEOUT: Return fast fallback instead of hanging
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        logger.warning(f"⏰ [NETRA] Parse timeout (>{NETRA_PARSE_TIMEOUT}s) - returning fallback")
        return ConceptGraphResponse(
            success=True,  # Still success - just simplified
            domain=request.subject or "general",
            topic=request.question[:50],
            entities=[Entity(id="main_concept", type="concept", label=request.question[:40])],
            relationships=[],
            constraints=[],
            visual_hints=VisualHint(
                layout_strategy="simple",
                emphasis=["main_concept"],
                style="sketch",
                annotations=[]
            ),
            title=request.question[:50],
            summary="Quick visualization generated",
            generation_time_ms=elapsed_ms
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [NETRA] Concept parsing failed: {e}")
        # Graceful fallback - return minimal valid response instead of 500
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        return ConceptGraphResponse(
            success=False,
            domain="general",
            topic=request.question[:50],
            entities=[Entity(id="concept", type="concept", label=request.question[:30])],
            relationships=[],
            constraints=[],
            visual_hints=VisualHint(
                layout_strategy="simple",
                emphasis=[],
                style="sketch",
                annotations=[]
            ),
            title=request.question[:50],
            summary=f"Visual generation unavailable: {str(e)[:50]}",
            generation_time_ms=elapsed_ms
        )


@router.get("/health")
async def health_check():
    """Health check for NETRA API"""
    return {
        "status": "healthy",
        "service": "NETRA Visual Reasoning Engine",
        "version": "1.0.0"
    }

