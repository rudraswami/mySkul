"""
Magic Notebook Engine V6 - Backend API
=======================================

Endpoint for ConceptBreaker (GPT-4o-mini integration)
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import logging

# Import OpenAI (assuming you have it configured)
try:
    from openai import OpenAI
    import os
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai/visual-engine", tags=["visual-engine"])

# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class ConceptBreakRequest(BaseModel):
    question: str
    context: Dict[str, Any] = {}
    model: str = "gpt-4o-mini"

class Entity(BaseModel):
    id: str
    type: str
    label: str
    radius: Optional[int] = 30

class Relation(BaseModel):
    from_: str  # 'from' is reserved
    to: str
    label: Optional[str] = ""

class Beat(BaseModel):
    beat: int
    text: str
    duration: float = 2.0
    drawItems: Optional[List[str]] = []
    highlightItems: Optional[List[str]] = []
    pause: bool = False

class Control(BaseModel):
    id: str
    type: str
    label: str
    min: Optional[float] = 0
    max: Optional[float] = 100
    default: Optional[float] = 50

class Blueprint(BaseModel):
    mode: str
    concept: str
    subject: str
    level: Optional[str] = "high_school"
    entities: List[Entity]
    relations: List[Relation]
    beats: List[Beat]
    metaphor: Optional[str] = None
    controls: Optional[List[Control]] = []
    highlights: Optional[List[str]] = []
    confidence: float = 0.9
    method: str = "llm"

class ConceptBreakResponse(BaseModel):
    blueprint: Blueprint

# ============================================
# GPT-4o-mini SYSTEM PROMPT
# ============================================

SYSTEM_PROMPT = """You are a visual education AI that converts questions into structured visual blueprints for the Magic Notebook Engine.

Your job is to analyze educational questions and generate a complete visual teaching blueprint.

OUTPUT STRUCTURE (JSON):
{
  "mode": "SCENE|COMPARISON|PROCESS|CYCLE|STRUCTURE|GRAPH|TIMELINE|HIERARCHY",
  "concept": "Main concept name (e.g., 'Newton\\'s Second Law')",
  "subject": "physics|chemistry|biology|math",
  "level": "high_school",
  "entities": [
    {"id": "entity_0", "type": "circle", "label": "Ball", "radius": 30},
    {"id": "entity_1", "type": "circle", "label": "Force", "radius": 25}
  ],
  "relations": [
    {"from": "entity_0", "to": "entity_1", "label": "F = ma"}
  ],
  "beats": [
    {"beat": 1, "text": "Let me show you Newton\\'s second law...", "duration": 2},
    {"beat": 2, "text": "When force is applied to an object...", "drawItems": ["entity_0"], "duration": 2},
    {"beat": 3, "text": "...it causes acceleration!", "drawItems": ["entity_1"], "duration": 2},
    {"beat": 4, "text": "The key formula is F = ma", "highlightItems": ["entity_0", "entity_1"], "pause": true, "duration": 2},
    {"beat": 5, "text": "Now you\\'ll never forget! 💪", "duration": 2}
  ],
  "metaphor": "cricket|auto_rickshaw|chai|dosa|diwali|holi|monsoon|local_train|market|classroom|null",
  "controls": [
    {"id": "mass_slider", "type": "slider", "label": "Mass (kg)", "min": 1, "max": 100, "default": 10}
  ]
}

MODE SELECTION GUIDE:
- SCENE: Physical scenarios, forces, motion (e.g., "force on ball")
- COMPARISON: X vs Y, pros/cons (e.g., "AC vs DC current")
- PROCESS: Step-by-step flows (e.g., "photosynthesis steps")
- CYCLE: Circular processes (e.g., "water cycle")
- STRUCTURE: Labeled diagrams (e.g., "heart anatomy")
- GRAPH: Math functions (e.g., "plot y=x²")
- TIMELINE: Historical events (e.g., "evolution timeline")
- HIERARCHY: Trees, classification (e.g., "animal taxonomy")

INDIAN METAPHORS (use when relevant):
- cricket: For force, motion, momentum, projectile motion
- auto_rickshaw: For friction, acceleration, mass
- local_train: For momentum, kinetic energy
- chai: For heat transfer, evaporation, temperature
- dosa: For heat conduction, chemical reactions
- diwali: For light, energy, combustion
- holi: For dispersion, projectile motion
- monsoon: For water cycle, weather
- market: For supply-demand, measurement
- classroom: For sound, reflection

5-BEAT NARRATIVE STRUCTURE:
Beat 1: Setup - "Let me show you..."
Beat 2: Concept - Draw main idea
Beat 3: Connection - "See how this relates..."
Beat 4: Insight - Key formula/idea (with pause)
Beat 5: Memory Hook - "Now you'll never forget!"

IMPORTANT:
- Always include ALL 5 beats
- Entity IDs must be unique (entity_0, entity_1, etc.)
- Relations use entity IDs in "from" and "to" fields
- Metaphor should be null if not applicable
- Keep labels concise (max 20 chars)
"""

# ============================================
# ENDPOINT
# ============================================

@router.post("/concept-break", response_model=ConceptBreakResponse)
async def break_concept(
    request: ConceptBreakRequest,
    # Add your auth dependency here:
    # current_user = Depends(get_current_user)
):
    """
    Break down educational concept into visual blueprint
    
    Uses GPT-4o-mini to generate structured visual teaching plans.
    Falls back to rule-based system if LLM unavailable.
    """
    
    try:
        # Extract context
        subject = request.context.get('subject', 'general')
        level = request.context.get('level', 'high_school')
        
        # Try LLM first
        if OPENAI_AVAILABLE:
            try:
                blueprint = await break_with_llm(
                    request.question,
                    subject,
                    level,
                    request.model
                )
                return ConceptBreakResponse(blueprint=blueprint)
            except Exception as llm_error:
                logger.warning(f"LLM failed: {llm_error}, falling back to rules")
        
        # Fallback to rule-based
        blueprint = break_with_rules(request.question, subject, level)
        return ConceptBreakResponse(blueprint=blueprint)
        
    except Exception as e:
        logger.error(f"Concept breaking failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# LLM IMPLEMENTATION
# ============================================

async def break_with_llm(
    question: str,
    subject: str,
    level: str,
    model: str = "gpt-4o-mini"
) -> Blueprint:
    """Use GPT-4o-mini to generate blueprint"""
    
    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")
    
    client = OpenAI(api_key=api_key)
    
    # Create user prompt
    user_prompt = f"""Question: {question}
Subject: {subject}
Level: {level}

Generate a complete visual blueprint for this concept."""
    
    # Call GPT-4o-mini
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
        max_tokens=2000
    )
    
    # Parse response
    blueprint_dict = json.loads(response.choices[0].message.content)
    
    # Add metadata
    blueprint_dict["confidence"] = 0.9
    blueprint_dict["method"] = "llm"
    
    # Convert to Pydantic model
    blueprint = Blueprint(**blueprint_dict)
    
    return blueprint

# ============================================
# RULE-BASED FALLBACK
# ============================================

def break_with_rules(question: str, subject: str, level: str) -> Blueprint:
    """Rule-based fallback when LLM unavailable"""
    
    question_lower = question.lower()
    
    # Detect mode
    mode = "SCENE"  # default
    if any(word in question_lower for word in ['vs', 'versus', 'compare']):
        mode = "COMPARISON"
    elif any(word in question_lower for word in ['cycle', 'loop']):
        mode = "CYCLE"
    elif any(word in question_lower for word in ['process', 'step', 'how to']):
        mode = "PROCESS"
    elif any(word in question_lower for word in ['graph', 'plot', 'function']):
        mode = "GRAPH"
    
    # Detect metaphor
    metaphor = None
    if 'cricket' in question_lower:
        metaphor = "cricket"
    elif 'auto' in question_lower or 'rickshaw' in question_lower:
        metaphor = "auto_rickshaw"
    elif 'chai' in question_lower or 'tea' in question_lower:
        metaphor = "chai"
    
    # Extract concept
    concept = question.split('?')[0].strip()
    if concept.lower().startswith(('explain', 'what is', 'how does')):
        concept = ' '.join(concept.split()[2:])
    
    # Create simple blueprint
    blueprint = Blueprint(
        mode=mode,
        concept=concept,
        subject=subject,
        level=level,
        entities=[
            Entity(id="entity_0", type="circle", label="Object A", radius=30),
            Entity(id="entity_1", type="circle", label="Object B", radius=30),
        ],
        relations=[
            Relation(from_="entity_0", to="entity_1", label="affects")
        ],
        beats=[
            Beat(beat=1, text=f"Let me show you {concept}...", duration=2),
            Beat(beat=2, text="Here's the main idea:", drawItems=["entity_0"], duration=2),
            Beat(beat=3, text="See how this connects...", drawItems=["entity_1"], duration=2),
            Beat(beat=4, text="The key insight is:", highlightItems=["entity_0", "entity_1"], pause=True, duration=2),
            Beat(beat=5, text="Now you'll never forget! 💪", duration=2),
        ],
        metaphor=metaphor,
        controls=[],
        confidence=0.6,
        method="rules"
    )
    
    return blueprint

# ============================================
# HEALTH CHECK
# ============================================

@router.get("/health")
async def health_check():
    """Check if visual engine API is working"""
    return {
        "status": "ok",
        "openai_available": OPENAI_AVAILABLE,
        "version": "v6.0"
    }

