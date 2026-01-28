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
import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ============================================
# ASYNC COMPOSITION TASK STORAGE
# ============================================
# In-memory store for composition tasks (use Redis in production)
COMPOSITION_TASKS: Dict[str, Dict[str, Any]] = {}

# Task status constants
TASK_STATUS_PENDING = "pending"
TASK_STATUS_GENERATING = "generating"
TASK_STATUS_COMPLETE = "complete"
TASK_STATUS_FAILED = "failed"

# TTL for task results (5 minutes)
TASK_TTL_SECONDS = 300

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
    
    # Hard SLA: 10 seconds max for visual parsing (increased from 5s for LLM reliability)
    NETRA_PARSE_TIMEOUT = 10.0
    
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


# ============================================
# NETRA v5.0 - COMPOSITION API
# ============================================

class ComposeRequest(BaseModel):
    """Request to generate a CompositionSpec"""
    system: Optional[str] = None
    user: Optional[str] = None  # Optional - can be derived from question
    question: str
    context: Optional[Dict[str, Any]] = {}


# ============================================
# VISUAL ONTOLOGY DEFINITIONS
# ============================================
# Classification system for question types to determine visual strategy

VISUAL_ONTOLOGIES = {
    "systemic_causal": {
        "description": "Cause-effect chains, processes, cycles, transformations",
        "examples": ["How does photosynthesis work?", "What causes earthquakes?", "How do vaccines work?"],
        "visual_strategy": "flow_simulation",
        "key_atoms": ["Entity", "ForceVector", "Connector", "Label"],
        "key_behaviors": ["animate_flow", "highlight_sequence", "pulse", "moveTo"],
    },
    "abstract_relational": {
        "description": "Relationships, comparisons, hierarchies, categories",
        "examples": ["What is the relationship between force and acceleration?", "Compare mitosis and meiosis", "Types of chemical bonds"],
        "visual_strategy": "relational_graph",
        "key_atoms": ["Entity", "Connector", "Region", "Label"],
        "key_behaviors": ["highlight", "drawLine", "fadeIn", "scaleIn"],
    },
    "chronological_evolutionary": {
        "description": "Timelines, evolution, historical progression, stages",
        "examples": ["How did life evolve?", "Stages of cell division", "History of the universe"],
        "visual_strategy": "timeline_progression",
        "key_atoms": ["Entity", "Connector", "Label", "Region"],
        "key_behaviors": ["fadeIn", "moveTo", "drawLine", "scaleIn"],
    },
    "spatial_structural": {
        "description": "Anatomy, structure, spatial arrangement, 3D models",
        "examples": ["Structure of an atom", "Parts of a cell", "Anatomy of the heart"],
        "visual_strategy": "structural_diagram",
        "key_atoms": ["Entity", "Region", "Label", "Connector"],
        "key_behaviors": ["scaleIn", "highlight", "fadeIn", "pulse"],
    },
    "quantitative_mathematical": {
        "description": "Numbers, graphs, equations, mathematical relationships",
        "examples": ["Graph of quadratic function", "What is exponential growth?", "Pythagorean theorem"],
        "visual_strategy": "dynamic_graph",
        "key_atoms": ["Entity", "Label", "Connector", "ForceVector"],
        "key_behaviors": ["animate", "moveTo", "drawLine", "highlight"],
    },
    "physical_mechanical": {
        "description": "Physics simulations, forces, motion, mechanics",
        "examples": ["Newton's laws of motion", "How does friction work?", "Projectile motion"],
        "visual_strategy": "physics_simulation",
        "key_atoms": ["RigidBody", "Surface", "ForceVector", "Label"],
        "key_behaviors": ["applyForce", "moveTo", "bounce", "highlight"],
    }
}


# ============================================
# 🚀 NETRA v6.0 - SIMULATION SCRIPT ARCHITECTURE
# ============================================
# LLM outputs ONLY simulation logic, NOT visual coordinates.
# Frontend handles all rendering, layout, and visual polish.

SIMULATION_PROMPT = '''You are NETRA, a Simulation Director for educational visualizations.

QUESTION: "{question}"
DOMAIN: {domain}

YOUR TASK: Output a compact SimulationScript (JSON) that describes:
1. What entities exist in this concept
2. What physical/logical rules govern their behavior
3. What the student can interact with
4. What narration explains the concept

DO NOT OUTPUT:
- Pixel coordinates (x, y positions)
- Color hex codes
- Animation durations
- Visual styling details
- SVG paths or shapes

The frontend rendering engine handles ALL visual decisions.

═══════════════════════════════════════════════════════════════════
ONTOLOGY TYPES (pick ONE that best fits)
═══════════════════════════════════════════════════════════════════
- physical_mechanical: Forces, motion, collisions, friction, projectiles
- systemic_causal: Processes, cycles, cause-effect chains, flows
- spatial_structural: Anatomy, layers, parts, 3D arrangements
- chronological_evolutionary: Timelines, stages, evolution, history
- quantitative_mathematical: Graphs, equations, functions, data
- abstract_relational: Comparisons, hierarchies, categories, relationships

═══════════════════════════════════════════════════════════════════
WORLD TYPES (pick ONE based on ontology)
═══════════════════════════════════════════════════════════════════
physical_mechanical:
  - surface_friction: Object moving on surface with friction
  - projectile_motion: Object launched with velocity
  - collision_system: Multiple objects colliding
  - pendulum_swing: Oscillating motion
  - spring_system: Elastic force simulation

systemic_causal:
  - cyclic_process: Repeating cycle (water cycle, carbon cycle)
  - chain_reaction: Sequential cause-effect
  - flow_network: Particles/energy flowing between nodes
  - feedback_loop: Self-regulating system

spatial_structural:
  - layered_explode: Layers that separate to show internals
  - radial_structure: Center with orbiting/surrounding parts
  - nested_containers: Parts inside parts
  - cross_section: Slice view of structure

chronological_evolutionary:
  - timeline_horizontal: Left-to-right progression
  - stage_morph: One form transforming into another
  - branching_tree: Evolutionary branches

quantitative_mathematical:
  - function_graph: Y vs X with animated tracer
  - bar_comparison: Animated bar chart
  - pie_distribution: Animated pie/donut chart

abstract_relational:
  - venn_overlap: Overlapping circles for comparison
  - hierarchy_tree: Parent-child relationships
  - comparison_split: Side-by-side comparison

═══════════════════════════════════════════════════════════════════
OUTPUT FORMAT (Valid JSON only, ~400 tokens max)
═══════════════════════════════════════════════════════════════════
{{
  "ontology": "physical_mechanical",
  "world": "surface_friction",
  "title": "Short title for the simulation",
  "entities": [
    {{
      "id": "unique_id",
      "role": "subject|environment|force|label|indicator",
      "template": "rigidbody|surface|force_vector|particle_emitter|label|region|connector|graph_line",
      "label": "Display name",
      "properties": {{"mass": 5, "color_hint": "primary"}}
    }}
  ],
  "constants": {{
    "variable_name": {{"value": 10, "unit": "m/s", "editable": true, "min": 0, "max": 100}}
  }},
  "state": {{
    "initial": "state_name",
    "variables": {{"velocity": "initial_velocity", "position": 0}}
  }},
  "rules": [
    {{"when": "state == 'moving' && velocity > 0", "then": ["velocity -= friction * dt", "emit('moving')"]}}
  ],
  "interactions": [
    {{"target": "friction", "type": "slider", "label": "Adjust Friction"}}
  ],
  "narration": [
    {{"id": "intro", "event": "start", "text": "Introduction text..."}},
    {{"id": "explain", "event": "moving", "text": "Explanation of what's happening..."}},
    {{"id": "conclude", "event": "stopped", "text": "Conclusion..."}}
  ]
}}

═══════════════════════════════════════════════════════════════════
RULES SYNTAX
═══════════════════════════════════════════════════════════════════
- "when": Condition using state variables and constants
- "then": Array of actions:
  - "variable = expression" (update state)
  - "show(entity_id)" / "hide(entity_id)"
  - "emit('event_name')" (trigger narration)
  - "state = 'new_state'" (change state machine)
  - "highlight(entity_id)" / "unhighlight(entity_id)"

═══════════════════════════════════════════════════════════════════
QUALITY REQUIREMENTS
═══════════════════════════════════════════════════════════════════
✓ Minimum 3 entities (diverse roles)
✓ Minimum 2 rules (state changes)
✓ Minimum 2 narration beats (intro + conclusion)
✓ At least 1 interaction (user can change something)
✓ State variables that CHANGE over time (not static)

GENERATE NOW - Valid JSON only.'''


# ============================================
# SIMULATION SCRIPT VALIDATOR
# ============================================

def validate_simulation_script(script: dict) -> tuple[bool, list[str]]:
    """
    Validate SimulationScript for quality and completeness.
    Returns (is_valid, list_of_errors).
    """
    errors = []
    
    # Required fields
    required_fields = ['ontology', 'world', 'entities', 'rules', 'narration']
    for field in required_fields:
        if field not in script:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return False, errors
    
    # Entity validation
    entities = script.get('entities', [])
    if len(entities) < 3:
        errors.append(f"Too few entities: {len(entities)} < 3 minimum")
    
    # Check entity diversity
    roles = set(e.get('role') for e in entities)
    if len(roles) < 2:
        errors.append("Low entity diversity: all entities have same role")
    
    # Rule validation
    rules = script.get('rules', [])
    if len(rules) < 2:
        errors.append(f"Too few rules: {len(rules)} < 2 minimum")
    
    # Check for static rules (no state changes)
    has_state_change = any(
        any('=' in action and 'emit' not in action for action in rule.get('then', []))
        for rule in rules
    )
    if not has_state_change:
        errors.append("No state-changing rules: simulation will be static")
    
    # Narration validation
    narration = script.get('narration', [])
    if len(narration) < 2:
        errors.append(f"Too few narration beats: {len(narration)} < 2 minimum")
    
    # Interaction validation
    interactions = script.get('interactions', [])
    if len(interactions) < 1:
        errors.append("No interactions: user has no agency")
    
    # Anti-PowerPoint check
    templates = [e.get('template') for e in entities]
    if templates.count('label') > len(entities) * 0.5:
        errors.append("Too text-heavy: more than 50% labels")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def calculate_script_entropy(script: dict) -> float:
    """
    Calculate entropy score (0-1) for simulation complexity.
    Higher = more dynamic, Lower = more static.
    """
    score = 0.0
    
    # Entity variety
    entities = script.get('entities', [])
    unique_templates = len(set(e.get('template') for e in entities))
    score += min(unique_templates / 4, 0.25)  # Max 0.25
    
    # Rule complexity
    rules = script.get('rules', [])
    state_changes = sum(
        len([a for a in rule.get('then', []) if '=' in a and 'emit' not in a])
        for rule in rules
    )
    score += min(state_changes / 4, 0.25)  # Max 0.25
    
    # Interaction depth
    interactions = script.get('interactions', [])
    score += min(len(interactions) / 2, 0.25)  # Max 0.25
    
    # Narration coverage
    narration = script.get('narration', [])
    unique_events = len(set(n.get('event') for n in narration))
    score += min(unique_events / 3, 0.25)  # Max 0.25
    
    return score

COMPOSER_PROMPT = '''You are NETRA, the world's most advanced Visual Intelligence Engine.

🚨 CRITICAL: You do NOT generate shapes, coordinates, or drawing code!
You describe WHAT to visualize and HOW it should behave. The renderer handles the rest.

QUESTION: "{question}"
DOMAIN: {domain}
INTENT: {intent}

═══════════════════════════════════════════════════════════════════
OUTPUT: SemanticIntent + ProceduralScenePlan (NOT atoms/shapes!)
═══════════════════════════════════════════════════════════════════

{{
  "$schema": "netra/procedural/v2",
  "semanticIntent": {{
    "concept": "The main concept being explained (e.g., 'photosynthesis', 'friction', 'DNA replication')",
    "domain": "biology|chemistry|physics|math|general",
    "processType": "transformation|cycle|structure|comparison|timeline|mechanics",
    "story": {{
      "setup": "What we're looking at (1 sentence)",
      "action": "What happens / the process (1-2 sentences)",
      "insight": "What the learner should understand (1 sentence)"
    }},
    "keyEntities": [
      {{"role": "hero", "name": "Main object name", "description": "What it looks like"}},
      {{"role": "input", "name": "Input name", "description": "What enters the process"}},
      {{"role": "output", "name": "Output name", "description": "What the process produces"}},
      {{"role": "environment", "name": "Context element", "description": "Background/setting"}}
    ],
    "interactionGoal": "What the user can control or explore"
  }},
  
  "proceduralScenePlan": {{
    "background": {{
      "type": "gradient|solid|textured",
      "colors": ["#color1", "#color2"],
      "direction": "vertical|horizontal|radial",
      "atmosphere": "warm|cool|neutral|dramatic"
    }},
    
    "layers": [
      {{
        "id": "environment_layer",
        "zIndex": 0,
        "elements": [
          {{
            "type": "procedural",
            "generator": "gradient_region|surface|depth_field",
            "role": "environment",
            "coverage": "full|left|right|bottom|top",
            "style": {{"opacity": 0.3, "blur": 2}}
          }}
        ]
      }},
      {{
        "id": "hero_layer",
        "zIndex": 1,
        "elements": [
          {{
            "type": "procedural",
            "generator": "organic_cell|chloroplast|leaf|molecule|wave|ball|box|custom",
            "role": "hero",
            "size": "large",
            "position": "center",
            "style": {{
              "fill": {{"type": "gradient", "colors": ["#primary", "#secondary"]}},
              "stroke": {{"color": "#border", "width": 3}},
              "glow": {{"enabled": true, "color": "#accent", "intensity": 0.5}},
              "shadow": true
            }},
            "innerDetails": [
              {{"type": "internal_structure", "pattern": "organelles|layers|particles"}}
            ]
          }}
        ]
      }},
      {{
        "id": "inputs_layer",
        "zIndex": 2,
        "elements": [
          {{
            "type": "procedural",
            "generator": "molecule|particle_group|arrow|label",
            "role": "input",
            "size": "small",
            "position": "left",
            "label": "Input Label",
            "style": {{"fill": "#inputColor"}}
          }}
        ]
      }},
      {{
        "id": "outputs_layer",
        "zIndex": 2,
        "elements": [
          {{
            "type": "procedural", 
            "generator": "molecule|particle_group|arrow|label",
            "role": "output",
            "size": "small",
            "position": "right",
            "label": "Output Label",
            "style": {{"fill": "#outputColor"}}
          }}
        ]
      }},
      {{
        "id": "effects_layer",
        "zIndex": 3,
        "elements": [
          {{
            "type": "particle_system",
            "generator": "flow_particles|sparkles|energy_burst|ambient_dust",
            "emitter": "hero",
            "direction": "toward_outputs",
            "count": 20,
            "speed": "slow|medium|fast",
            "style": {{"color": "#particleColor", "size": 3, "trail": true}}
          }}
        ]
      }}
    ],
    
    "choreography": [
      {{"beat": 1, "time": 0, "action": "fade_in_environment", "duration": 500}},
      {{"beat": 2, "time": 500, "action": "scale_in_hero", "target": "hero", "duration": 800}},
      {{"beat": 3, "time": 1300, "action": "slide_in_inputs", "from": "left", "duration": 600}},
      {{"beat": 4, "time": 2000, "action": "start_flow_particles", "from": "inputs", "to": "hero"}},
      {{"beat": 5, "time": 3500, "action": "pulse_hero", "intensity": 1.2}},
      {{"beat": 6, "time": 4000, "action": "emit_outputs", "from": "hero", "to": "right"}},
      {{"beat": 7, "time": 5000, "action": "slide_in_outputs", "from": "hero", "duration": 600}}
    ],
    
    "interactions": [
      {{
        "type": "slider|toggle|drag|tap",
        "target": "hero|inputs|outputs|rate",
        "label": "Control label",
        "effect": "Description of what changes"
      }}
    ],
    
    "narration": [
      {{"beat": 2, "text": "Setup narration - what we're looking at", "emphasis": "normal"}},
      {{"beat": 4, "text": "Action narration - what's happening", "emphasis": "key_point"}},
      {{"beat": 6, "text": "Insight narration - what we learned", "emphasis": "key_point"}}
    ]
  }},
  
  "colorPalette": {{
    "primary": "#hexcode",
    "secondary": "#hexcode", 
    "accent": "#hexcode",
    "background": ["#hexcode1", "#hexcode2"],
    "text": "#hexcode"
  }}
}}

═══════════════════════════════════════════════════════════════════
GENERATOR VOCABULARY (use these in "generator" field):
═══════════════════════════════════════════════════════════════════

BIOLOGY:
- organic_cell: Irregular cell-like shape with membrane
- chloroplast: Green organelle with internal stacks
- mitochondria: Elongated organelle with cristae folds
- nucleus: Round organelle with chromatin
- leaf: Leaf shape with veins
- dna_helix: Double helix structure

CHEMISTRY:
- molecule: Ball-and-stick molecular structure
- atom_orbital: Atom with electron shells
- reaction_zone: Highlighted reaction area
- beaker: Lab equipment

PHYSICS:
- wave: Sinusoidal wave pattern
- force_field: Gradient force visualization
- motion_trail: Path with motion blur
- surface: Ground/platform with texture
- ball: Physics-enabled sphere
- vector_arrow: Force/velocity arrow

UNIVERSAL:
- gradient_region: Soft background region
- particle_group: Collection of small particles
- flow_particles: Animated flowing particles
- label: Text annotation
- connector: Line/arrow between elements

═══════════════════════════════════════════════════════════════════
DOMAIN COLOR PALETTES (use appropriate colors):
═══════════════════════════════════════════════════════════════════

BIOLOGY: primary=#10B981, secondary=#34D399, accent=#FCD34D, bg=[#ECFDF5, #D1FAE5]
CHEMISTRY: primary=#8B5CF6, secondary=#A78BFA, accent=#F59E0B, bg=[#F5F3FF, #EDE9FE]  
PHYSICS: primary=#3B82F6, secondary=#60A5FA, accent=#F472B6, bg=[#EFF6FF, #DBEAFE]
MATH: primary=#6366F1, secondary=#818CF8, accent=#14B8A6, bg=[#EEF2FF, #E0E7FF]

═══════════════════════════════════════════════════════════════════
QUALITY RULES (MUST FOLLOW):
═══════════════════════════════════════════════════════════════════

✅ MUST have: hero element (large, centered, detailed)
✅ MUST have: at least 3 layers (environment, hero, effects)
✅ MUST have: choreography with 5+ beats
✅ MUST have: 3 narration cues (setup, action, insight)
✅ MUST have: particle effects or flow animations
✅ MUST use: domain-appropriate color palette

❌ DO NOT: Output coordinates (x, y positions) - renderer calculates these
❌ DO NOT: Output pixel sizes - use "small", "medium", "large"
❌ DO NOT: Create basic shapes (rect, circle) - use procedural generators
❌ DO NOT: Make static diagrams - must have animation choreography

GENERATE NOW - Valid JSON only, no markdown.'''


@router.post("/compose")
async def compose_visual(request: ComposeRequest):
    """
    🎨 NETRA v5.0 - Generate a CompositionSpec for dynamic rendering
    
    This endpoint generates atom-based compositions that the frontend
    DynamicVisualRenderer can render with behaviors and narration.
    """
    from services.llm_service import call_llm, VISUAL_COMPOSITION_TIMEOUT
    from core.config import settings
    
    # 🎨 CRITICAL LOG: Confirm endpoint is reached
    logger.info(f"🎨 [NETRA_COMPOSE] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info(f"🎨 [NETRA_COMPOSE] Request received")
    logger.info(f"🎨 [NETRA_COMPOSE] Question: {request.question[:60] if request.question else 'N/A'}...")
    logger.info(f"🎨 [NETRA_COMPOSE] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    start_time = datetime.now()
    
    logger.info(f"🎨 [NETRA v5] Composing visual: {request.question[:60]}...")
    logger.info(f"⏱️ [NETRA v5] Using extended timeout: {VISUAL_COMPOSITION_TIMEOUT}s")
    
    try:
        api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
        
        # Build prompt
        context = request.context or {}
        prompt = COMPOSER_PROMPT.format(
            question=request.question,
            domain=context.get('domain', 'general'),
            intent=context.get('intent', 'conceptual')
        )
        
        # Call LLM with EXTENDED timeout (passes directly to call_llm)
        # ⚠️ FIX: Pass timeout to call_llm, NOT using asyncio.wait_for wrapper
        model = settings.BASE_MODEL or "gpt-4o-mini"
        
        llm_start = datetime.now()
        logger.info(f"⏱️ [TIMING] LLM call starting - model: {model}, timeout: {VISUAL_COMPOSITION_TIMEOUT}s")
        
        response = await call_llm(
            prompt=prompt,
            api_key=api_key,
            temperature=0.4,
            max_tokens=3000,
            model=model,
            system_message=request.system or "You are NETRA, a Cognitive Visual Thinking Engine. Output valid JSON only.",
            timeout=VISUAL_COMPOSITION_TIMEOUT  # ✅ FIX: Pass extended timeout directly
        )
        
        llm_elapsed = int((datetime.now() - llm_start).total_seconds() * 1000)
        logger.info(f"⏱️ [TIMING] LLM returned in {llm_elapsed}ms")
        
        # Parse JSON
        json_str = response.strip()
        if json_str.startswith("```"):
            json_str = re.sub(r'^```(?:json)?\n?', '', json_str)
            json_str = re.sub(r'\n?```$', '', json_str)
        
        composition = json.loads(json_str)
        
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        logger.info(f"✅ [NETRA v5] Composition generated in {elapsed_ms}ms")
        logger.info(f"✅ Atoms: {len(composition.get('atoms', []))}")
        
        # CRITICAL: If LLM returned empty atoms, use fallback
        if not composition.get('atoms') or len(composition.get('atoms', [])) == 0:
            logger.warning("⚠️ [NETRA v5] LLM returned empty atoms - using fallback")
            composition = generate_fallback_composition(request.question, request.context)
        
        return {
            "success": True,
            "composition": composition,
            "generation_time_ms": elapsed_ms
        }
        
    except asyncio.TimeoutError:
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        logger.warning(f"⏰ [NETRA v5] Compose timeout (>{COMPOSE_TIMEOUT}s)")
        
        # Return fallback composition
        return {
            "success": True,
            "composition": generate_fallback_composition(request.question, request.context),
            "generation_time_ms": elapsed_ms,
            "fallback": True
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ [NETRA v5] Invalid JSON from LLM: {e}")
        return {
            "success": True,
            "composition": generate_fallback_composition(request.question, request.context),
            "error": f"JSON parse error: {str(e)[:50]}",
            "fallback": True
        }
        
    except Exception as e:
        logger.error(f"❌ [NETRA v5] Compose failed: {e}")
        return {
            "success": False,
            "composition": generate_fallback_composition(request.question, request.context),
            "error": str(e)[:100],
            "fallback": True
        }


# ============================================
# 🚀 ASYNC COMPOSITION ENDPOINTS
# ============================================

class ComposeAsyncResponse(BaseModel):
    """Response for async composition request"""
    status: str
    task_id: str
    poll_url: str
    message: str

class ComposeStatusResponse(BaseModel):
    """Response for composition status check"""
    status: str
    task_id: str
    composition: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    generation_time_ms: Optional[int] = None


async def _generate_composition_async(task_id: str, question: str, context: Dict[str, Any]):
    """Background task to generate composition"""
    from services.llm_service import call_llm, VISUAL_COMPOSITION_TIMEOUT
    from core.config import settings
    
    start_time = datetime.now()
    
    # Update status to generating
    COMPOSITION_TASKS[task_id]["status"] = TASK_STATUS_GENERATING
    COMPOSITION_TASKS[task_id]["started_at"] = start_time.isoformat()
    
    logger.info(f"🎨 [ASYNC] Task {task_id} - Starting composition generation")
    
    try:
        api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("OPENAI_API_KEY not configured")
        
        # Build prompt
        prompt = COMPOSER_PROMPT.format(
            question=question,
            domain=context.get('domain', 'general'),
            intent=context.get('intent', 'conceptual')
        )
        
        model = settings.BASE_MODEL or "gpt-4o-mini"
        
        logger.info(f"⏱️ [ASYNC] Task {task_id} - LLM call starting (timeout: {VISUAL_COMPOSITION_TIMEOUT}s)")
        
        # Call LLM with extended timeout for visual composition
        response = await call_llm(
            prompt=prompt,
            api_key=api_key,
            temperature=0.4,
            max_tokens=3000,
            model=model,
            system_message="You are NETRA, a Cognitive Visual Thinking Engine. Output valid JSON only.",
            timeout=VISUAL_COMPOSITION_TIMEOUT  # Use extended timeout
        )
        
        # Parse JSON
        json_str = response.strip()
        if json_str.startswith("```"):
            json_str = re.sub(r'^```(?:json)?\n?', '', json_str)
            json_str = re.sub(r'\n?```$', '', json_str)
        
        composition = json.loads(json_str)
        
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # 🎯 CRITICAL: Detect and convert new ProceduralScenePlan format to atoms
        if 'semanticIntent' in composition and 'proceduralScenePlan' in composition:
            logger.info(f"🎬 [ASYNC] Task {task_id} - Converting ProceduralScenePlan to atoms")
            composition = convert_procedural_to_atoms(composition, context)
        
        # Check quality
        atom_count = len(composition.get('atoms', []))
        if atom_count == 0:
            logger.warning(f"⚠️ [ASYNC] Task {task_id} - LLM returned 0 atoms, using fallback")
            composition = generate_fallback_composition(question, context)
            composition['metadata'] = {'isFallback': True}
        
        # Update task with result
        COMPOSITION_TASKS[task_id].update({
            "status": TASK_STATUS_COMPLETE,
            "composition": composition,
            "generation_time_ms": elapsed_ms,
            "completed_at": datetime.now().isoformat(),
        })
        
        logger.info(f"✅ [ASYNC] Task {task_id} - Complete in {elapsed_ms}ms (atoms: {atom_count})")
        
    except Exception as e:
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        logger.error(f"❌ [ASYNC] Task {task_id} - Failed: {e}")
        
        # Store fallback composition
        fallback = generate_fallback_composition(question, context)
        fallback['metadata'] = {'isFallback': True, 'error': str(e)[:100]}
        
        COMPOSITION_TASKS[task_id].update({
            "status": TASK_STATUS_COMPLETE,  # Still complete, but with fallback
            "composition": fallback,
            "error": str(e)[:100],
            "generation_time_ms": elapsed_ms,
            "completed_at": datetime.now().isoformat(),
        })


def generate_skeleton_composition(question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    🚀 Generate a MINIMAL skeleton composition for immediate display (<100ms).
    
    This skeleton shows a loading state with basic elements that will be
    upgraded when the full composition is ready.
    """
    context = context or {}
    domain = context.get("domain") or detect_domain_from_question(question)
    theme = DOMAIN_THEMES.get(domain, DOMAIN_THEMES['general'])
    
    short_question = question[:40] + '...' if len(question) > 40 else question
    
    return {
        "$schema": "netra/composition/v1",
        "version": "1.0.0",
        "id": f"skeleton_{hash(question) % 10000}",
        "generatedAt": datetime.now().isoformat(),
        "context": {
            "question": question,
            "intent": context.get("intent", "conceptual"),
            "domain": domain,
            "difficulty": "intermediate",
            "isSkeleton": True  # Mark as skeleton for frontend
        },
        "atoms": [
            {
                "id": "loading_title",
                "type": "Label",
                "params": {
                    "text": f"Generating: {domain.capitalize()} Visual",
                    "fontSize": 16,
                    "fontWeight": "bold",
                    "color": theme['primary']
                },
                "position": {"x": 400, "y": 100}
            },
            {
                "id": "loading_spinner",
                "type": "Entity",
                "params": {
                    "shape": "circle",
                    "width": 60,
                    "height": 60,
                    "fill": theme['primary'],
                    "stroke": theme['secondary'],
                    "strokeWidth": 4,
                    "opacity": 0.8
                },
                "position": {"x": 400, "y": 280}
            },
            {
                "id": "loading_text",
                "type": "Label",
                "params": {
                    "text": short_question,
                    "fontSize": 14,
                    "color": "#6B7280",
                    "maxWidth": 400
                },
                "position": {"x": 400, "y": 420}
            }
        ],
        "behaviors": [
            {
                "id": "fade_in_title",
                "trigger": {"type": "scene_ready"},
                "action": {"type": "fadeIn", "target": "loading_title", "duration": 200}
            },
            {
                "id": "pulse_spinner",
                "trigger": {"type": "scene_ready", "delay": 100},
                "action": {"type": "pulse", "target": "loading_spinner", "loop": True, "duration": 1000}
            },
            {
                "id": "fade_in_text",
                "trigger": {"type": "scene_ready", "delay": 200},
                "action": {"type": "fadeIn", "target": "loading_text", "duration": 300}
            }
        ],
        "narration": [
            {
                "id": "loading_narration",
                "trigger": {"type": "scene_ready"},
                "text": f"Creating an intelligent visual for: {short_question}",
                "emphasis": "normal",
                "duration": 2000
            }
        ],
        "interactions": [],
        "stage": {
            "width": 800,
            "height": 600,
            "background": {"type": "solid", "value": "#F8FAFC"},
            "physics": {"enabled": False}
        }
    }


class ComposeAsyncResponseWithSkeleton(BaseModel):
    """Response for async composition with progressive skeleton"""
    status: str
    task_id: str
    poll_url: str
    message: str
    skeleton: Optional[Dict[str, Any]] = None  # Immediate skeleton for display


@router.post("/compose-async")
async def compose_visual_async(request: ComposeRequest, background_tasks: BackgroundTasks):
    """
    🚀 NETRA v5.0 ASYNC - Progressive composition generation
    
    Returns IMMEDIATELY with:
    - task_id for polling
    - skeleton composition for instant display (<100ms)
    
    Frontend should:
    1. Display skeleton immediately
    2. Poll for full composition
    3. Upgrade visual when ready
    """
    task_id = f"netra_{uuid.uuid4().hex[:12]}"
    
    logger.info(f"🎨 [ASYNC] ════════════════════════════════════════════════")
    logger.info(f"🎨 [ASYNC] New task: {task_id}")
    logger.info(f"🎨 [ASYNC] Question: {request.question[:60] if request.question else 'N/A'}...")
    logger.info(f"🎨 [ASYNC] Context: {request.context}")
    logger.info(f"🎨 [ASYNC] Has user prompt: {bool(request.user)}")
    logger.info(f"🎨 [ASYNC] ════════════════════════════════════════════════")
    
    # Initialize task
    context = request.context or {}
    context['domain'] = context.get('domain') or detect_domain_from_question(request.question)
    
    # Generate skeleton IMMEDIATELY (< 100ms)
    skeleton = generate_skeleton_composition(request.question, context)
    
    COMPOSITION_TASKS[task_id] = {
        "task_id": task_id,
        "status": TASK_STATUS_PENDING,
        "question": request.question,
        "context": context,
        "created_at": datetime.now().isoformat(),
        "skeleton": skeleton,  # Store skeleton for reference
    }
    
    # Start background task for FULL composition
    background_tasks.add_task(_generate_composition_async, task_id, request.question, context)
    
    logger.info(f"✅ [ASYNC] Skeleton returned immediately, full composition in background")
    
    return {
        "status": TASK_STATUS_PENDING,
        "task_id": task_id,
        "poll_url": f"/api/netra/compose-status/{task_id}",
        "message": "Skeleton ready, full composition generating in background.",
        "skeleton": skeleton  # Return skeleton for immediate display
    }


@router.get("/compose-status/{task_id}", response_model=ComposeStatusResponse)
async def get_compose_status(task_id: str):
    """
    📊 Get status of async composition task
    
    Returns:
    - pending: Task queued, not started
    - generating: LLM is working
    - complete: Composition ready
    - failed: Task failed (fallback composition provided)
    """
    if task_id not in COMPOSITION_TASKS:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    task = COMPOSITION_TASKS[task_id]
    
    return ComposeStatusResponse(
        status=task["status"],
        task_id=task_id,
        composition=task.get("composition"),
        error=task.get("error"),
        generation_time_ms=task.get("generation_time_ms"),
    )


@router.delete("/compose-task/{task_id}")
async def delete_compose_task(task_id: str):
    """🗑️ Delete completed task (cleanup)"""
    if task_id in COMPOSITION_TASKS:
        del COMPOSITION_TASKS[task_id]
        return {"deleted": True, "task_id": task_id}
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


def detect_domain_from_question(question: str) -> str:
    """Detect domain from question keywords using word boundaries"""
    import re
    q_lower = question.lower()
    
    # 🎯 CRITICAL: Use word boundary matching to avoid substring matches
    # e.g., "ph" should not match "photosynthesis"
    def has_word(words):
        pattern = r'\b(' + '|'.join(re.escape(w) for w in words) + r')\b'
        return bool(re.search(pattern, q_lower))
    
    # Check BIOLOGY FIRST - it has more specific terms like "photosynthesis"
    biology_words = ['cell', 'dna', 'gene', 'protein', 'enzyme', 'photosynthesis', 'respiration', 
                     'evolution', 'mitosis', 'meiosis', 'neuron', 'organ', 'tissue', 'chlorophyll', 
                     'plant', 'animal', 'bacteria', 'virus', 'ecosystem', 'species', 'chromosome',
                     'membrane', 'organelle', 'ribosome', 'nucleus', 'chloroplast', 'mitochondria']
    if has_word(biology_words):
        return 'biology'
    
    physics_words = ['force', 'velocity', 'acceleration', 'newton', 'gravity', 'momentum', 
                     'energy', 'mass', 'motion', 'wave', 'electric', 'magnetic', 'circuit', 
                     'current', 'voltage', 'friction', 'projectile', 'thermodynamics', 'optics',
                     'quantum', 'relativity', 'mechanics']
    if has_word(physics_words):
        return 'physics'
    
    chemistry_words = ['atom', 'molecule', 'reaction', 'bond', 'chemical', 'element', 'compound', 
                       'ion', 'electron', 'orbital', 'acid', 'base', 'oxidation', 'periodic',
                       'solution', 'catalyst', 'equilibrium', 'mole', 'stoichiometry']
    # Note: Removed 'ph' to avoid matching "photosynthesis"
    if has_word(chemistry_words):
        return 'chemistry'
    
    math_words = ['equation', 'graph', 'function', 'derivative', 'integral', 'matrix', 'vector', 
                  'triangle', 'circle', 'angle', 'slope', 'quadratic', 'polynomial', 'calculus',
                  'algebra', 'geometry', 'trigonometry', 'probability', 'statistics']
    if has_word(math_words):
        return 'math'
    
    return 'general'

# Domain-specific procedural generators
DOMAIN_GENERATORS = {
    'biology': {
        'hero': 'organic_shape',
        'input': 'molecule',
        'output': 'molecule',
        'environment': 'leaf',
    },
    'chemistry': {
        'hero': 'reaction_zone',
        'input': 'atom_orbital',
        'output': 'atom_orbital',
        'environment': None,
    },
    'physics': {
        'hero': 'force_field',
        'input': None,
        'output': 'motion_trail',
        'environment': 'surface',
    },
    'math': {
        'hero': 'graph',
        'input': None,
        'output': None,
        'environment': None,
    },
    'general': {
        'hero': 'organic_shape',
        'input': 'particle_group',
        'output': 'particle_group',
        'environment': 'gradient_region',
    },
}

# Domain-specific color palettes and shapes
DOMAIN_THEMES = {
    'physics': {
        'primary': '#3B82F6',  # Blue
        'secondary': '#60A5FA',
        'accent': '#FBBF24',   # Yellow for energy
        'shapes': ['circle', 'rect', 'arrow'],
    },
    'chemistry': {
        'primary': '#10B981',  # Green
        'secondary': '#34D399',
        'accent': '#F59E0B',   # Orange for reactions
        'shapes': ['circle', 'hexagon', 'diamond'],
    },
    'biology': {
        'primary': '#8B5CF6',  # Purple
        'secondary': '#A78BFA',
        'accent': '#22C55E',   # Green for life
        'shapes': ['ellipse', 'blob', 'cell'],
    },
    'math': {
        'primary': '#EC4899',  # Pink
        'secondary': '#F472B6',
        'accent': '#06B6D4',   # Cyan for graphs
        'shapes': ['rect', 'triangle', 'line'],
    },
    'general': {
        'primary': '#6366F1',  # Indigo
        'secondary': '#818CF8',
        'accent': '#F97316',   # Orange
        'shapes': ['rect', 'circle', 'diamond'],
    }
}

def convert_procedural_to_atoms(procedural_composition: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    🎬 Convert SemanticIntent + ProceduralScenePlan format to atoms-based format.
    
    This bridges the gap between the new LLM output format and existing renderer.
    """
    context = context or {}
    semantic = procedural_composition.get('semanticIntent', {})
    plan = procedural_composition.get('proceduralScenePlan', {})
    
    domain = semantic.get('domain', context.get('domain', 'general'))
    theme = DOMAIN_THEMES.get(domain, DOMAIN_THEMES['general'])
    
    atoms = []
    behaviors = []
    narration = []
    
    # 🎨 CONCEPT-TO-GENERATOR MAPPING (Not just domain!)
    # This maps specific concepts to beautiful procedural generators
    CONCEPT_GENERATORS = {
        # Biology concepts
        'photosynthesis': {'hero': 'chloroplast', 'secondary': ['leaf', 'molecule']},
        'chloroplast': {'hero': 'chloroplast', 'secondary': ['organic_shape']},
        'cell': {'hero': 'nucleus', 'secondary': ['mitochondria', 'organic_shape']},
        'mitochondria': {'hero': 'mitochondria', 'secondary': ['organic_shape']},
        'dna': {'hero': 'dna_helix', 'secondary': ['nucleus']},
        'reproduction': {'hero': 'nucleus', 'secondary': ['organic_shape', 'dna_helix']},
        'respiration': {'hero': 'mitochondria', 'secondary': ['molecule', 'organic_shape']},
        'leaf': {'hero': 'leaf', 'secondary': ['chloroplast']},
        'plant': {'hero': 'leaf', 'secondary': ['chloroplast', 'organic_shape']},
        # Chemistry concepts  
        'atom': {'hero': 'atom_orbital', 'secondary': ['molecule']},
        'molecule': {'hero': 'molecule', 'secondary': ['atom_orbital']},
        'reaction': {'hero': 'reaction_zone', 'secondary': ['molecule']},
        'bond': {'hero': 'molecule', 'secondary': ['atom_orbital']},
        # Physics concepts
        'wave': {'hero': 'wave', 'secondary': ['motion_trail']},
        'force': {'hero': 'force_field', 'secondary': ['motion_trail']},
        'motion': {'hero': 'motion_trail', 'secondary': ['surface']},
        'friction': {'hero': 'surface', 'secondary': ['motion_trail', 'force_field']},
    }
    
    # Extract concept from semantic intent
    concept = semantic.get('concept', '').lower()
    question_lower = context.get('question', '').lower()
    
    # Find matching concept generator
    matched_generator = None
    for key, gen_config in CONCEPT_GENERATORS.items():
        if key in concept or key in question_lower:
            matched_generator = gen_config
            logger.info(f"🎨 [CONVERT] Matched concept '{key}' → hero={gen_config['hero']}")
            break
    
    # Fallback to domain-based if no concept match
    if not matched_generator:
        DOMAIN_FALLBACK = {
            'biology': {'hero': 'organic_shape', 'secondary': ['organic_shape']},
            'chemistry': {'hero': 'molecule', 'secondary': ['atom_orbital']},
            'physics': {'hero': 'wave', 'secondary': ['surface']},
            'math': {'hero': 'force_field', 'secondary': ['motion_trail']},
            'general': {'hero': 'organic_shape', 'secondary': ['organic_shape']}
        }
        matched_generator = DOMAIN_FALLBACK.get(domain, DOMAIN_FALLBACK['general'])
    
    hero_generator = matched_generator['hero']
    secondary_generators = matched_generator.get('secondary', ['organic_shape'])
    
    # Process layers from procedural plan
    layers = plan.get('layers', [])
    y_offset = 100
    atom_id = 0
    
    for layer_idx, layer in enumerate(layers):
        layer_type = layer.get('type', 'content')
        elements = layer.get('elements', [])
        
        for elem_idx, elem in enumerate(elements):
            atom_id += 1
            elem_type = elem.get('type', 'entity')
            label = elem.get('label', elem.get('id', f'element_{atom_id}'))
            
            # Determine position
            pos_x = 200 + (elem_idx * 180)
            pos_y = y_offset + (layer_idx * 150)
            
            # Create atom based on element type
            if elem_type in ['hero', 'main', 'central']:
                # Hero object - large and centered with CONCEPT-SPECIFIC procedural generator
                atoms.append({
                    "id": f"hero_{atom_id}",
                    "type": "Entity",
                    "role": "hero",
                    "position": {"x": 360, "y": 260},
                    "params": {
                        "shape": "organic",
                        "width": 220,
                        "height": 160,
                        "fill": theme['primary'],
                        "stroke": theme['secondary'],
                        "label": label,
                        "glow": True,
                        "glowColor": theme['accent'],
                        "glowIntensity": 0.6
                    },
                    "generator": hero_generator,  # 🎨 Use CONCEPT-SPECIFIC generator!
                    "generatorParams": {
                        "color": theme['primary'],
                        "innerColor": theme['secondary'],
                        "complexity": elem.get('complexity', 0.7),
                        "width": 220,
                        "height": 160,
                    }
                })
            elif elem_type == 'environment' or layer_type == 'background':
                # Environment - region or surface
                atoms.append({
                    "id": f"env_{atom_id}",
                    "type": "Region",
                    "role": "environment",
                    "position": {"x": 360, "y": 480},
                    "params": {
                        "width": 680,
                        "height": 80,
                        "fill": theme.get('background', '#E2E8F0'),
                        "opacity": 0.4,
                        "label": elem.get('label', 'Environment')
                    }
                })
            elif elem_type in ['label', 'text', 'annotation']:
                atoms.append({
                    "id": f"label_{atom_id}",
                    "type": "Label",
                    "position": {"x": pos_x, "y": pos_y},
                    "params": {
                        "text": label,
                        "fontSize": 14,
                        "color": "#1F2937"
                    }
                })
            elif elem_type in ['connector', 'flow', 'arrow']:
                atoms.append({
                    "id": f"connector_{atom_id}",
                    "type": "Connector",
                    "position": {"x": pos_x, "y": pos_y},
                    "params": {
                        "fromId": elem.get('from', 'hero_1'),
                        "toId": elem.get('to', f'element_{atom_id + 1}'),
                        "style": "curved",
                        "animated": True,
                        "color": theme['accent']
                    }
                })
            elif elem_type in ['particle', 'effect']:
                atoms.append({
                    "id": f"particle_{atom_id}",
                    "type": "Entity",
                    "role": "effect",
                    "position": {"x": pos_x, "y": pos_y},
                    "params": {
                        "shape": "circle",
                        "width": 8,
                        "height": 8,
                        "fill": theme['accent'],
                        "opacity": 0.7
                    },
                    "generator": "particle_system",
                    "generatorParams": {
                        "count": elem.get('count', 20),
                        "spread": elem.get('spread', 50)
                    }
                })
            else:
                # Default entity with SECONDARY procedural generator (varied for richness)
                secondary_gen = secondary_generators[atom_id % len(secondary_generators)]
                atoms.append({
                    "id": f"entity_{atom_id}",
                    "type": "Entity",
                    "role": "content",
                    "position": {"x": pos_x, "y": pos_y},
                    "params": {
                        "shape": elem.get('shape', 'organic'),
                        "width": elem.get('width', 100),
                        "height": elem.get('height', 80),
                        "fill": theme['primary'],
                        "stroke": theme['secondary'],
                        "label": label
                    },
                    "generator": secondary_gen,  # 🎨 Use varied SECONDARY generators!
                    "generatorParams": {
                        "color": theme['primary'],
                        "innerColor": theme['secondary'],
                        "width": elem.get('width', 100),
                        "height": elem.get('height', 80),
                    }
                })
    
    # If no atoms from layers, create default hero + environment
    if not atoms:
        concept_label = semantic.get('concept', context.get('question', 'Concept')[:30])
        atoms = [
            {
                "id": "hero_main",
                "type": "Entity",
                "role": "hero",
                "position": {"x": 360, "y": 260},
                "params": {
                    "shape": "organic",
                    "width": 220,
                    "height": 160,
                    "fill": theme['primary'],
                    "stroke": theme['secondary'],
                    "label": concept_label,
                    "glow": True,
                    "glowColor": theme['accent'],
                    "glowIntensity": 0.6
                },
                "generator": hero_generator,  # 🎨 Use CONCEPT-SPECIFIC hero generator!
                "generatorParams": {
                    "color": theme['primary'],
                    "innerColor": theme['secondary'],
                    "width": 220,
                    "height": 160,
                    "seed": 42,
                    "palette": [theme['primary'], theme['secondary'], theme['accent']]
                }
            },
            {
                "id": "env_surface",
                "type": "Region",
                "role": "environment",
                "position": {"x": 360, "y": 480},
                "params": {
                    "width": 680,
                    "height": 80,
                    "fill": theme.get('background', '#E2E8F0'),
                    "opacity": 0.4
                }
            }
        ]
    
    # Convert choreography to behaviors
    choreography = plan.get('choreography', [])
    for beat_idx, beat in enumerate(choreography):
        target = beat.get('target', atoms[0]['id'] if atoms else 'hero_main')
        action = beat.get('action', 'show')
        delay = beat.get('delay', beat_idx * 1000)
        
        behaviors.append({
            "id": f"behavior_{beat_idx + 1}",
            "trigger": {"type": "timeline", "delay": delay},
            "actions": [{"type": action, "targets": [target], "params": beat.get('params', {})}]
        })
    
    # Default behaviors if none
    if not behaviors:
        behaviors = [
            {"id": "b1_intro", "trigger": {"type": "timeline", "delay": 0}, "actions": [{"type": "fadeIn", "targets": [atoms[0]['id'] if atoms else 'hero_main']}]},
            {"id": "b2_env", "trigger": {"type": "timeline", "delay": 500}, "actions": [{"type": "fadeIn", "targets": ["env_surface"]}]},
            {"id": "b3_pulse", "trigger": {"type": "timeline", "delay": 1500}, "actions": [{"type": "pulse", "targets": [atoms[0]['id'] if atoms else 'hero_main']}]}
        ]
    
    # Convert narration
    narration_beats = plan.get('narration', semantic.get('story', {}).get('beats', []))
    if isinstance(narration_beats, list):
        for i, beat in enumerate(narration_beats):
            if isinstance(beat, str):
                narration.append({"text": beat, "triggerEvent": f"behavior_{i + 1}", "emphasis": "normal"})
            elif isinstance(beat, dict):
                narration.append({
                    "text": beat.get('text', beat.get('content', '')),
                    "triggerEvent": beat.get('trigger', f"behavior_{i + 1}"),
                    "emphasis": beat.get('emphasis', 'normal')
                })
    
    # Default narration if none
    if not narration:
        concept = semantic.get('concept', 'this concept')
        narration = [
            {"text": f"Let's explore {concept}.", "triggerEvent": "scene_start", "emphasis": "intro"},
            {"text": f"Watch how {concept} works in action.", "triggerEvent": "b1_intro", "emphasis": "normal"},
            {"text": f"This is how {concept} comes together.", "triggerEvent": "b3_pulse", "emphasis": "conclusion"}
        ]
    
    # Build final composition
    return {
        "$schema": "netra/composition/v1",
        "version": "1.0.0",
        "id": f"comp_{domain}_{hash(str(procedural_composition)) % 100000}",
        "generatedAt": datetime.now().isoformat(),
        "context": {
            "question": context.get('question', semantic.get('concept', '')),
            "intent": semantic.get('intent', 'explanation'),
            "domain": domain,
            "difficulty": semantic.get('difficulty', 'intermediate'),
            "convertedFromProcedural": True
        },
        "stage": {
            "width": 720,
            "height": 520,
            "background": {
                "type": "gradient",
                "colors": [theme.get('background', '#F8FAFC'), '#FFFFFF'],
                "direction": "vertical"
            }
        },
        "atoms": atoms,
        "behaviors": behaviors,
        "narration": narration,
        "interactions": plan.get('interactions', [
            {"type": "click", "targetId": atoms[0]['id'] if atoms else 'hero_main', "action": "highlight"}
        ]),
        "metadata": {
            "ontology": semantic.get('ontology', 'GENERAL'),
            "heroGenerator": hero_generator,
            "secondaryGenerators": secondary_generators,
            "convertedFromProcedural": True
        }
    }


def generate_fallback_composition(question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate a domain-aware fallback composition when LLM fails"""
    context = context or {}
    domain = context.get("domain") or detect_domain_from_question(question)
    theme = DOMAIN_THEMES.get(domain, DOMAIN_THEMES['general'])
    
    concept = question[:50] if len(question) > 50 else question
    short_concept = concept[:25] + '...' if len(concept) > 25 else concept
    
    logger.info(f"🎨 [FALLBACK] Generating domain-aware fallback for: {domain}")
    
    return {
        "$schema": "netra/composition/v1",
        "version": "1.0.0",
        "id": f"fallback_{hash(question) % 10000}",
        "generatedAt": datetime.now().isoformat(),
        "context": {
            "question": question,
            "intent": context.get("intent", "conceptual"),
            "domain": domain,
            "difficulty": context.get("difficulty", "intermediate"),
            "isFallback": True
        },
        "atoms": [
            # Central concept entity - HERO with procedural generator
            {
                "id": "main_concept",
                "type": "Entity",
                "role": "hero",
                "generator": DOMAIN_GENERATORS.get(domain, {}).get('hero', 'organic_shape'),
                "generatorParams": {
                    "width": 200,
                    "height": 150,
                    "color": theme['primary'],
                    "irregularity": 0.15 if domain == 'biology' else 0,
                },
                "params": {
                    "shape": "ellipse",
                    "width": 200,
                    "height": 150,
                    "fill": theme['primary'],
                    "stroke": theme['secondary'],
                    "strokeWidth": 3,
                    "label": short_concept,
                    "labelColor": "#FFFFFF",
                    "glow": True,
                    "glowColor": theme['accent'],
                    "glowIntensity": 0.5,
                    "isHero": True,
                    "generator": DOMAIN_GENERATORS.get(domain, {}).get('hero', 'organic_shape'),
                },
                "position": {"x": 360, "y": 260},
                "zIndex": 1
            },
            # Title label
            {
                "id": "title_label",
                "type": "Label",
                "params": {
                    "text": f"Exploring: {domain.capitalize()}",
                    "fontSize": 20,
                    "fontWeight": "bold",
                    "color": theme['primary']
                },
                "position": {"x": 360, "y": 60},
                "zIndex": 3
            },
            # Concept description
            {
                "id": "concept_desc",
                "type": "Label",
                "params": {
                    "text": concept,
                    "fontSize": 14,
                    "color": "#6B7280",
                    "maxWidth": 350
                },
                "position": {"x": 360, "y": 450},
                "zIndex": 3
            },
            # Input element with generator
            {
                "id": "input_element",
                "type": "Entity",
                "role": "input",
                "generator": DOMAIN_GENERATORS.get(domain, {}).get('input', 'particle_group'),
                "params": {
                    "shape": "circle",
                    "width": 70,
                    "height": 70,
                    "fill": theme['secondary'],
                    "stroke": theme['primary'],
                    "strokeWidth": 2,
                    "label": "Input",
                    "generator": DOMAIN_GENERATORS.get(domain, {}).get('input', 'particle_group'),
                },
                "position": {"x": 120, "y": 260},
                "zIndex": 2
            },
            # Output element with generator
            {
                "id": "output_element",
                "type": "Entity",
                "role": "output",
                "generator": DOMAIN_GENERATORS.get(domain, {}).get('output', 'particle_group'),
                "params": {
                    "shape": "circle",
                    "width": 70,
                    "height": 70,
                    "fill": theme['accent'],
                    "stroke": theme['primary'],
                    "strokeWidth": 2,
                    "label": "Output",
                    "generator": DOMAIN_GENERATORS.get(domain, {}).get('output', 'particle_group'),
                },
                "position": {"x": 600, "y": 260},
                "zIndex": 2
            },
            # Flow connector
            {
                "id": "flow_connector",
                "type": "Connector",
                "params": {
                    "from": "input_element",
                    "to": "main_concept",
                    "style": "dashed",
                    "color": theme['secondary'],
                    "animated": True
                }
            }
        ],
        "behaviors": [
            {
                "id": "b1_fade_title",
                "trigger": {"type": "scene_ready", "delay": 0},
                "action": {"type": "fadeIn", "target": "title_label", "duration": 400}
            },
            {
                "id": "b2_scale_hero",
                "trigger": {"type": "scene_ready", "delay": 300},
                "action": {"type": "scaleIn", "target": "main_concept", "duration": 600}
            },
            {
                "id": "b3_fade_input",
                "trigger": {"type": "scene_ready", "delay": 700},
                "action": {"type": "fadeIn", "target": "input_element", "duration": 400}
            },
            {
                "id": "b4_fade_output",
                "trigger": {"type": "scene_ready", "delay": 1000},
                "action": {"type": "fadeIn", "target": "output_element", "duration": 400}
            },
            {
                "id": "b5_draw_flow",
                "trigger": {"type": "scene_ready", "delay": 1400},
                "action": {"type": "drawLine", "target": "flow_connector", "duration": 500}
            },
            {
                "id": "b6_pulse_hero",
                "trigger": {"type": "scene_ready", "delay": 2000},
                "action": {"type": "pulse", "target": "main_concept", "loop": True, "duration": 2000}
            }
        ],
        "narration": [
            {
                "id": "n1_intro",
                "trigger": {"type": "scene_ready", "delay": 0},
                "text": f"Let's explore: {concept}",
                "emphasis": "normal",
                "duration": 3000
            },
            {
                "id": "n2_process",
                "trigger": {"type": "scene_ready", "delay": 4000},
                "text": "Watch how inputs transform through the process.",
                "emphasis": "key_point",
                "duration": 3000
            },
            {
                "id": "n3_conclusion",
                "trigger": {"type": "scene_ready", "delay": 8000},
                "text": "This is the key concept to remember.",
                "emphasis": "key_point",
                "duration": 3000
            }
        ],
        "interactions": [],
        "stage": {
            "width": 720,
            "height": 520,
            "background": {"type": "gradient", "value": ["#F8FAFC", "#F1F5F9"], "direction": "vertical"},
            "physics": {"enabled": False}
        },
        "metadata": {"isFallback": True, "domain": domain}
    }


# ============================================
# 🚀 NETRA v6.0 - SIMULATION API ENDPOINTS
# ============================================

class SimulateRequest(BaseModel):
    """Request to generate a SimulationScript"""
    question: str
    context: Optional[Dict[str, Any]] = {}


class SimulateAsyncResponse(BaseModel):
    """Response for async simulation generation"""
    status: str
    task_id: str
    poll_url: str
    message: str
    placeholder: Optional[Dict[str, Any]] = None


# In-memory store for simulation tasks
SIMULATION_TASKS: Dict[str, Dict[str, Any]] = {}


def generate_instant_placeholder(question: str, context: dict) -> dict:
    """
    Generate an instant placeholder scene (<100ms).
    This renders BEFORE LLM returns, giving immediate visual feedback.
    """
    domain = context.get('domain', detect_domain_from_question(question))
    
    # Guess ontology from question keywords
    q_lower = question.lower()
    
    if any(w in q_lower for w in ['force', 'motion', 'friction', 'velocity', 'acceleration', 'gravity', 'newton']):
        ontology = 'physical_mechanical'
        world = 'surface_friction'
    elif any(w in q_lower for w in ['cycle', 'process', 'how does', 'works', 'flow', 'chain']):
        ontology = 'systemic_causal'
        world = 'flow_network'
    elif any(w in q_lower for w in ['structure', 'parts', 'anatomy', 'cell', 'layers']):
        ontology = 'spatial_structural'
        world = 'layered_explode'
    elif any(w in q_lower for w in ['timeline', 'evolution', 'history', 'stages', 'develop']):
        ontology = 'chronological_evolutionary'
        world = 'timeline_horizontal'
    elif any(w in q_lower for w in ['graph', 'equation', 'function', 'calculate', 'number']):
        ontology = 'quantitative_mathematical'
        world = 'function_graph'
    else:
        ontology = 'abstract_relational'
        world = 'hierarchy_tree'
    
    return {
        "$schema": "netra/simulation/v1",
        "ontology": ontology,
        "world": world,
        "title": f"Loading: {question[:40]}...",
        "entities": [
            {"id": "placeholder_1", "role": "subject", "template": "rigidbody", "label": "Loading..."},
            {"id": "placeholder_2", "role": "environment", "template": "surface", "label": ""},
            {"id": "placeholder_3", "role": "indicator", "template": "label", "label": "Generating simulation..."}
        ],
        "constants": {},
        "state": {"initial": "loading", "variables": {}},
        "rules": [],
        "interactions": [],
        "narration": [
            {"id": "loading", "event": "start", "text": f"Creating simulation for: {question[:50]}..."}
        ],
        "_meta": {
            "isPlaceholder": True,
            "domain": domain,
            "guessedOntology": ontology
        }
    }


async def _generate_simulation_async(task_id: str, question: str, context: Dict[str, Any]):
    """Background task to generate SimulationScript via LLM"""
    from services.llm_service import call_llm
    from core.config import settings
    
    start_time = datetime.now()
    
    SIMULATION_TASKS[task_id]["status"] = TASK_STATUS_GENERATING
    SIMULATION_TASKS[task_id]["started_at"] = start_time.isoformat()
    
    logger.info(f"🎬 [SIMULATE] Task {task_id} - Starting simulation generation")
    
    try:
        api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("OPENAI_API_KEY not configured")
        
        domain = context.get('domain', detect_domain_from_question(question))
        
        prompt = SIMULATION_PROMPT.format(
            question=question,
            domain=domain
        )
        
        model = settings.BASE_MODEL or "gpt-4o-mini"
        
        logger.info(f"⏱️ [SIMULATE] Task {task_id} - LLM call (max_tokens: 1000)")
        
        response = await call_llm(
            prompt=prompt,
            api_key=api_key,
            temperature=0.5,
            max_tokens=1000,
            model=model,
            system_message="You are NETRA, a simulation director. Output valid JSON only, no markdown.",
            timeout=60.0
        )
        
        json_str = response.strip()
        if json_str.startswith("```"):
            json_str = re.sub(r'^```(?:json)?\n?', '', json_str)
            json_str = re.sub(r'\n?```$', '', json_str)
        
        script = json.loads(json_str)
        
        is_valid, errors = validate_simulation_script(script)
        entropy = calculate_script_entropy(script)
        
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        if is_valid and entropy >= 0.3:
            logger.info(f"✅ [SIMULATE] Task {task_id} - Valid script (entropy: {entropy:.2f}) in {elapsed_ms}ms")
            SIMULATION_TASKS[task_id].update({
                "status": TASK_STATUS_COMPLETE,
                "script": script,
                "generation_time_ms": elapsed_ms,
                "quality": {
                    "entropy": entropy,
                    "entities": len(script.get('entities', [])),
                    "rules": len(script.get('rules', [])),
                    "narration": len(script.get('narration', []))
                }
            })
        else:
            logger.warning(f"⚠️ [SIMULATE] Task {task_id} - Low quality (entropy: {entropy:.2f}, errors: {errors})")
            SIMULATION_TASKS[task_id].update({
                "status": TASK_STATUS_COMPLETE,
                "script": script,
                "generation_time_ms": elapsed_ms,
                "quality": {
                    "entropy": entropy,
                    "valid": is_valid,
                    "errors": errors
                },
                "_warning": "Low quality script"
            })
            
    except json.JSONDecodeError as e:
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        logger.error(f"❌ [SIMULATE] Task {task_id} - JSON parse error: {e}")
        SIMULATION_TASKS[task_id].update({
            "status": TASK_STATUS_FAILED,
            "error": f"JSON parse error: {str(e)[:100]}",
            "generation_time_ms": elapsed_ms
        })
        
    except Exception as e:
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        logger.error(f"❌ [SIMULATE] Task {task_id} - Failed: {e}")
        SIMULATION_TASKS[task_id].update({
            "status": TASK_STATUS_FAILED,
            "error": str(e)[:100],
            "generation_time_ms": elapsed_ms
        })


@router.post("/simulate-async")
async def simulate_async(request: SimulateRequest, background_tasks: BackgroundTasks):
    """
    🚀 NETRA v6.0 - Generate SimulationScript asynchronously
    
    Returns IMMEDIATELY with:
    - task_id for polling
    - placeholder for instant display (<100ms)
    """
    task_id = f"sim_{uuid.uuid4().hex[:12]}"
    
    logger.info(f"🎬 [SIMULATE] ════════════════════════════════════════════════")
    logger.info(f"🎬 [SIMULATE] New task: {task_id}")
    logger.info(f"🎬 [SIMULATE] Question: {request.question[:60]}...")
    logger.info(f"🎬 [SIMULATE] ════════════════════════════════════════════════")
    
    context = request.context or {}
    context['domain'] = context.get('domain') or detect_domain_from_question(request.question)
    placeholder = generate_instant_placeholder(request.question, context)
    
    SIMULATION_TASKS[task_id] = {
        "task_id": task_id,
        "status": TASK_STATUS_PENDING,
        "question": request.question,
        "context": context,
        "created_at": datetime.now().isoformat(),
        "placeholder": placeholder
    }
    
    background_tasks.add_task(_generate_simulation_async, task_id, request.question, context)
    
    logger.info(f"✅ [SIMULATE] Placeholder returned immediately")
    
    return SimulateAsyncResponse(
        status=TASK_STATUS_PENDING,
        task_id=task_id,
        poll_url=f"/api/netra/simulate-status/{task_id}",
        message="Placeholder ready, simulation generating in background.",
        placeholder=placeholder
    )


@router.get("/simulate-status/{task_id}")
async def get_simulate_status(task_id: str):
    """📊 Get status of simulation generation task"""
    if task_id not in SIMULATION_TASKS:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    task = SIMULATION_TASKS[task_id]
    
    return {
        "status": task["status"],
        "task_id": task_id,
        "script": task.get("script"),
        "error": task.get("error"),
        "generation_time_ms": task.get("generation_time_ms"),
        "quality": task.get("quality")
    }
