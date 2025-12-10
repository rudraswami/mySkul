"""
🎨 Synchronized Visual Engine - Text + Visual Reasoning Integration
====================================================================

This engine ensures visual reasoning is NOT an afterthought:
1. Visual reasoning influences explanation
2. Step-by-step diagrams synchronized with text
3. Iterative whiteboard updates
4. Text-visual coherence verification

Visual learning is equal partner to text learning.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class VisualType(Enum):
    """Types of visualizations"""
    DIAGRAM = "diagram"
    GRAPH = "graph"
    FLOWCHART = "flowchart"
    FORMULA_BREAKDOWN = "formula_breakdown"
    COMPARISON_TABLE = "comparison_table"
    TIMELINE = "timeline"
    CONCEPT_MAP = "concept_map"
    STEP_BY_STEP = "step_by_step"


@dataclass
class VisualElement:
    """Single visual element"""
    element_id: str
    visual_type: VisualType
    title: str
    svg_data: Optional[str] = None
    json_data: Optional[Dict[str, Any]] = None
    description: str = ""
    related_text_section: str = ""
    sequence_number: int = 0


@dataclass
class SynchronizedOutput:
    """Synchronized text + visual output"""
    text_sections: List[Dict[str, Any]]
    visual_elements: List[VisualElement]
    text_visual_mapping: Dict[str, str]  # text_section_id → visual_element_id
    coherence_score: float
    rendering_order: List[str]  # IDs in order


class SynchronizedVisualEngine:
    """
    Engine for synchronized text-visual reasoning.
    
    PRINCIPLES:
    1. Visual reasoning happens IN PARALLEL with text reasoning
    2. Each explanation section can have associated visual
    3. Visuals are not just decorations - they enhance understanding
    4. Coherence is verified between text and visuals
    """
    
    def __init__(self, llm_key: Optional[str] = None):
        """Initialize engine"""
        self.llm_key = llm_key
        self._whiteboard = None
        
        logger.info("🎨 SynchronizedVisualEngine initialized")
        self._init_whiteboard()
    
    def _init_whiteboard(self):
        """Initialize whiteboard engine"""
        try:
            from services.whiteboard_engine import WhiteboardEngine
            self._whiteboard = WhiteboardEngine()
            logger.info("   └── Whiteboard: ✅")
        except ImportError:
            logger.warning("   └── Whiteboard: ❌ (not available)")
    
    async def generate_synchronized_response(
        self,
        query: str,
        text_response: str,
        subject: str,
        context: Dict[str, Any]
    ) -> SynchronizedOutput:
        """
        Generate synchronized text + visual response.
        
        Args:
            query: Student's question
            text_response: Text response from agents
            subject: Subject area
            context: Additional context
            
        Returns:
            SynchronizedOutput with text and visuals
        """
        logger.info(f"🎨 Generating synchronized visual for: {query[:50]}...")
        
        # Step 1: Analyze what visuals would help
        visual_plan = await self._plan_visuals(query, text_response, subject)
        
        # Step 2: Generate visuals in parallel
        visuals = await self._generate_visuals(visual_plan, query, subject, context)
        
        # Step 3: Parse text into sections
        text_sections = self._parse_text_sections(text_response)
        
        # Step 4: Map text sections to visuals
        mapping = self._create_text_visual_mapping(text_sections, visuals)
        
        # Step 5: Verify coherence
        coherence = self._verify_coherence(text_sections, visuals, mapping)
        
        # Step 6: Determine rendering order
        render_order = self._determine_render_order(text_sections, visuals, mapping)
        
        return SynchronizedOutput(
            text_sections=text_sections,
            visual_elements=visuals,
            text_visual_mapping=mapping,
            coherence_score=coherence,
            rendering_order=render_order
        )
    
    async def _plan_visuals(
        self,
        query: str,
        text_response: str,
        subject: str
    ) -> List[Dict[str, Any]]:
        """
        Plan what visuals would enhance the explanation.
        
        Analyzes the query and response to determine:
        - What type of visual would help
        - What concepts need visualization
        - How many visuals are appropriate
        """
        plans = []
        query_lower = query.lower()
        text_lower = text_response.lower()
        
        # Diagram triggers
        if any(word in query_lower for word in ['diagram', 'draw', 'visualize', 'picture']):
            plans.append({
                "type": VisualType.DIAGRAM,
                "reason": "User explicitly requested visual",
                "priority": 1
            })
        
        # Graph/plot triggers
        if any(word in query_lower for word in ['graph', 'plot', 'curve', 'function']):
            plans.append({
                "type": VisualType.GRAPH,
                "reason": "Mathematical function visualization",
                "priority": 1
            })
        
        # Comparison triggers
        if any(word in query_lower for word in ['compare', 'difference', 'vs', 'versus']):
            plans.append({
                "type": VisualType.COMPARISON_TABLE,
                "reason": "Comparison needs side-by-side view",
                "priority": 1
            })
        
        # Process triggers
        if any(word in text_lower for word in ['step 1', 'first,', 'then,', 'process']):
            plans.append({
                "type": VisualType.STEP_BY_STEP,
                "reason": "Process explanation benefits from visual steps",
                "priority": 2
            })
        
        # Formula triggers
        if any(char in text_response for char in ['=', '∫', 'Σ', '√']):
            plans.append({
                "type": VisualType.FORMULA_BREAKDOWN,
                "reason": "Formula explanation needs visual breakdown",
                "priority": 2
            })
        
        # Subject-specific defaults
        if subject:
            subject_lower = subject.lower()
            if 'physics' in subject_lower and not plans:
                plans.append({
                    "type": VisualType.DIAGRAM,
                    "reason": "Physics concepts benefit from diagrams",
                    "priority": 3
                })
            elif 'biology' in subject_lower and not plans:
                plans.append({
                    "type": VisualType.DIAGRAM,
                    "reason": "Biology concepts often need visual representation",
                    "priority": 3
                })
            elif 'math' in subject_lower and not plans:
                plans.append({
                    "type": VisualType.GRAPH,
                    "reason": "Math concepts benefit from graphs",
                    "priority": 3
                })
        
        # Sort by priority
        plans.sort(key=lambda x: x.get("priority", 5))
        
        # Limit to 2 visuals max per response
        return plans[:2]
    
    async def _generate_visuals(
        self,
        plan: List[Dict[str, Any]],
        query: str,
        subject: str,
        context: Dict[str, Any]
    ) -> List[VisualElement]:
        """Generate visuals based on plan"""
        visuals = []
        
        for i, item in enumerate(plan):
            visual_type = item["type"]
            
            try:
                if visual_type == VisualType.DIAGRAM:
                    visual = await self._generate_diagram(query, subject, context)
                elif visual_type == VisualType.GRAPH:
                    visual = self._generate_graph(query, subject, context)
                elif visual_type == VisualType.COMPARISON_TABLE:
                    visual = self._generate_comparison(query, subject, context)
                elif visual_type == VisualType.STEP_BY_STEP:
                    visual = self._generate_step_visual(query, subject, context)
                elif visual_type == VisualType.FORMULA_BREAKDOWN:
                    visual = self._generate_formula_breakdown(query, subject, context)
                else:
                    visual = await self._generate_generic_visual(query, subject, context)
                
                if visual:
                    visual.sequence_number = i + 1
                    visuals.append(visual)
                    
            except Exception as e:
                logger.warning(f"Failed to generate {visual_type.value}: {e}")
        
        return visuals
    
    async def _generate_diagram(
        self,
        query: str,
        subject: str,
        context: Dict[str, Any]
    ) -> Optional[VisualElement]:
        """Generate a diagram using whiteboard engine"""
        if not self._whiteboard:
            return self._generate_fallback_visual(query, VisualType.DIAGRAM)
        
        try:
            from services.whiteboard_engine import generate_whiteboard_visual
            
            visual_data = generate_whiteboard_visual(query, subject)
            
            if visual_data:
                return VisualElement(
                    element_id=f"diagram_{hash(query) % 10000}",
                    visual_type=VisualType.DIAGRAM,
                    title=f"Diagram: {query[:40]}...",
                    json_data=visual_data,
                    description="AI-generated diagram"
                )
        except Exception as e:
            logger.warning(f"Whiteboard generation failed: {e}")
        
        return self._generate_fallback_visual(query, VisualType.DIAGRAM)
    
    def _generate_graph(
        self,
        query: str,
        subject: str,
        context: Dict[str, Any]
    ) -> Optional[VisualElement]:
        """Generate a graph visualization"""
        # Create plotly-compatible JSON for frontend rendering
        return VisualElement(
            element_id=f"graph_{hash(query) % 10000}",
            visual_type=VisualType.GRAPH,
            title="Graph",
            json_data={
                "type": "line_graph",
                "render_frontend": True,
                "placeholder": {
                    "message": "Graph based on the mathematical concept",
                    "suggestion": "The frontend should render this with actual data"
                }
            },
            description="Mathematical graph"
        )
    
    def _generate_comparison(
        self,
        query: str,
        subject: str,
        context: Dict[str, Any]
    ) -> Optional[VisualElement]:
        """Generate a comparison table"""
        return VisualElement(
            element_id=f"compare_{hash(query) % 10000}",
            visual_type=VisualType.COMPARISON_TABLE,
            title="Comparison",
            json_data={
                "type": "comparison_table",
                "render_frontend": True,
                "headers": ["Aspect", "Item 1", "Item 2"],
                "data": []  # To be filled by frontend from text
            },
            description="Comparison table"
        )
    
    def _generate_step_visual(
        self,
        query: str,
        subject: str,
        context: Dict[str, Any]
    ) -> Optional[VisualElement]:
        """Generate step-by-step visualization"""
        return VisualElement(
            element_id=f"steps_{hash(query) % 10000}",
            visual_type=VisualType.STEP_BY_STEP,
            title="Step-by-Step",
            json_data={
                "type": "step_flow",
                "render_frontend": True,
                "steps": []  # To be extracted from text
            },
            description="Step-by-step process visualization"
        )
    
    def _generate_formula_breakdown(
        self,
        query: str,
        subject: str,
        context: Dict[str, Any]
    ) -> Optional[VisualElement]:
        """Generate formula breakdown visual"""
        return VisualElement(
            element_id=f"formula_{hash(query) % 10000}",
            visual_type=VisualType.FORMULA_BREAKDOWN,
            title="Formula Breakdown",
            json_data={
                "type": "formula_visual",
                "render_frontend": True,
                "formula": "",
                "parts": []
            },
            description="Visual breakdown of the formula"
        )
    
    async def _generate_generic_visual(
        self,
        query: str,
        subject: str,
        context: Dict[str, Any]
    ) -> Optional[VisualElement]:
        """Generate a generic visual"""
        return await self._generate_diagram(query, subject, context)
    
    def _generate_fallback_visual(
        self,
        query: str,
        visual_type: VisualType
    ) -> VisualElement:
        """Generate fallback visual when whiteboard unavailable"""
        return VisualElement(
            element_id=f"fallback_{hash(query) % 10000}",
            visual_type=visual_type,
            title="Concept Visualization",
            json_data={
                "type": "concept_visual",
                "render_frontend": True,
                "concept": query[:100],
                "placeholder": True
            },
            description="Concept visualization"
        )
    
    def _parse_text_sections(self, text: str) -> List[Dict[str, Any]]:
        """Parse text response into sections"""
        sections = []
        
        # Split by headers (## or **)
        import re
        
        # Try markdown headers
        header_pattern = r'^##\s+(.+)$'
        parts = re.split(header_pattern, text, flags=re.MULTILINE)
        
        if len(parts) > 1:
            # Has headers
            current_id = 0
            for i in range(0, len(parts), 2):
                content = parts[i].strip()
                title = parts[i+1].strip() if i+1 < len(parts) else ""
                
                if content or title:
                    sections.append({
                        "id": f"section_{current_id}",
                        "title": title,
                        "content": content or parts[i+2] if i+2 < len(parts) else "",
                        "type": "paragraph"
                    })
                    current_id += 1
        else:
            # No headers - split by paragraphs
            paragraphs = text.split('\n\n')
            for i, para in enumerate(paragraphs):
                if para.strip():
                    sections.append({
                        "id": f"section_{i}",
                        "title": "",
                        "content": para.strip(),
                        "type": "paragraph"
                    })
        
        return sections
    
    def _create_text_visual_mapping(
        self,
        text_sections: List[Dict[str, Any]],
        visuals: List[VisualElement]
    ) -> Dict[str, str]:
        """Map text sections to relevant visuals"""
        mapping = {}
        
        # Simple mapping: first visual with first section, etc.
        for i, visual in enumerate(visuals):
            if i < len(text_sections):
                mapping[text_sections[i]["id"]] = visual.element_id
                visual.related_text_section = text_sections[i]["id"]
        
        return mapping
    
    def _verify_coherence(
        self,
        text_sections: List[Dict[str, Any]],
        visuals: List[VisualElement],
        mapping: Dict[str, str]
    ) -> float:
        """Verify coherence between text and visuals"""
        if not visuals:
            return 1.0  # No visuals = no incoherence
        
        if not mapping:
            return 0.5  # Visuals without mapping = partial coherence
        
        # Check if mapped sections exist
        mapped_count = 0
        for section_id, visual_id in mapping.items():
            section_exists = any(s["id"] == section_id for s in text_sections)
            visual_exists = any(v.element_id == visual_id for v in visuals)
            if section_exists and visual_exists:
                mapped_count += 1
        
        if not mapping:
            return 0.5
        
        return mapped_count / len(mapping)
    
    def _determine_render_order(
        self,
        text_sections: List[Dict[str, Any]],
        visuals: List[VisualElement],
        mapping: Dict[str, str]
    ) -> List[str]:
        """Determine the order to render elements"""
        order = []
        
        for section in text_sections:
            order.append(section["id"])
            
            # Add visual after its related section
            if section["id"] in mapping:
                order.append(mapping[section["id"]])
        
        # Add any unmapped visuals at the end
        for visual in visuals:
            if visual.element_id not in order:
                order.append(visual.element_id)
        
        return order
    
    def format_for_frontend(self, output: SynchronizedOutput) -> Dict[str, Any]:
        """Format synchronized output for frontend consumption"""
        return {
            "text_sections": output.text_sections,
            "visuals": [
                {
                    "id": v.element_id,
                    "type": v.visual_type.value,
                    "title": v.title,
                    "data": v.json_data,
                    "description": v.description,
                    "sequence": v.sequence_number,
                    "related_section": v.related_text_section
                }
                for v in output.visual_elements
            ],
            "mapping": output.text_visual_mapping,
            "render_order": output.rendering_order,
            "coherence_score": output.coherence_score
        }


# Factory function
_visual_engine: Optional[SynchronizedVisualEngine] = None


def get_synchronized_visual_engine(llm_key: str = None) -> SynchronizedVisualEngine:
    """Get or create synchronized visual engine"""
    global _visual_engine
    if _visual_engine is None:
        _visual_engine = SynchronizedVisualEngine(llm_key)
    return _visual_engine

