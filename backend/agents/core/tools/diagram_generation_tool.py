"""
Diagram Generation Tool
=======================

Generates actual diagrams (not just text descriptions) using:
- Mermaid.js for flowcharts, graphs, sequences
- ASCII art for simple diagrams
- SVG generation for custom visuals

This enables VisualiseAgent to create REAL visual content.
"""

import logging
from typing import Dict, Any, Optional
from agents.core.tools.base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class DiagramGenerationTool(BaseTool):
    """
    Tool for generating visual diagrams from descriptions.
    
    Supports:
    - Flowcharts
    - Sequence diagrams
    - Mind maps
    - Concept maps
    - Graph visualizations
    """
    
    def get_name(self) -> str:
        return "generate_diagram"
    
    def get_description(self) -> str:
        return """Generate visual diagrams from descriptions.
        
        Input:
        - diagram_type: flowchart, sequence, mindmap, graph, concept_map
        - description: Text description of what to visualize
        - elements: List of elements/nodes to include
        
        Output:
        - Mermaid.js code for rendering
        - ASCII art fallback
        - SVG code for custom diagrams
        """
    
    def get_parameters(self) -> Dict[str, str]:
        return {
            "diagram_type": "Type of diagram (flowchart, sequence, mindmap, graph, concept_map)",
            "description": "Description of what to visualize",
            "elements": "List of elements/nodes (optional)",
            "relationships": "Relationships between elements (optional)"
        }
    
    async def execute(self, **kwargs) -> ToolResult:
        """Generate diagram based on type and description"""
        try:
            diagram_type = kwargs.get('diagram_type', 'flowchart')
            description = kwargs.get('description', '')
            elements = kwargs.get('elements', [])
            relationships = kwargs.get('relationships', [])
            
            logger.info(f"🎨 Generating {diagram_type} diagram: {description[:50]}")
            
            # Generate based on type
            if diagram_type == 'flowchart':
                diagram_code = self._generate_flowchart(elements, relationships)
            elif diagram_type == 'sequence':
                diagram_code = self._generate_sequence(elements, relationships)
            elif diagram_type == 'mindmap':
                diagram_code = self._generate_mindmap(elements, relationships)
            elif diagram_type == 'graph':
                diagram_code = self._generate_graph(elements, relationships)
            elif diagram_type == 'concept_map':
                diagram_code = self._generate_concept_map(elements, relationships)
            else:
                diagram_code = self._generate_flowchart(elements, relationships)
            
            return ToolResult(
                success=True,
                output=f"Generated {diagram_type} diagram",
                data={
                    'diagram_type': diagram_type,
                    'mermaid_code': diagram_code,
                    'ascii_art': self._generate_ascii_fallback(elements),
                    'description': description
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Diagram generation failed: {e}")
            return ToolResult(
                success=False,
                output=f"Failed to generate diagram: {str(e)}",
                error=str(e)
            )
    
    def _generate_flowchart(self, elements: list, relationships: list) -> str:
        """Generate Mermaid.js flowchart code"""
        mermaid = "graph TD\n"
        
        # Add nodes
        for i, element in enumerate(elements):
            node_id = f"N{i}"
            mermaid += f"    {node_id}[{element}]\n"
        
        # Add relationships
        for rel in relationships:
            if len(rel) >= 2:
                from_idx = rel[0] if isinstance(rel[0], int) else 0
                to_idx = rel[1] if isinstance(rel[1], int) else 1
                label = rel[2] if len(rel) > 2 else ""
                mermaid += f"    N{from_idx} -->|{label}| N{to_idx}\n"
        
        return mermaid
    
    def _generate_sequence(self, elements: list, relationships: list) -> str:
        """Generate Mermaid.js sequence diagram"""
        mermaid = "sequenceDiagram\n"
        
        # Add participants
        for element in elements:
            mermaid += f"    participant {element}\n"
        
        # Add interactions
        for rel in relationships:
            if len(rel) >= 3:
                from_elem = rel[0]
                to_elem = rel[1]
                message = rel[2]
                mermaid += f"    {from_elem}->>{to_elem}: {message}\n"
        
        return mermaid
    
    def _generate_mindmap(self, elements: list, relationships: list) -> str:
        """Generate Mermaid.js mindmap"""
        if not elements:
            return "mindmap\n  root((Concept))\n"
        
        mermaid = "mindmap\n"
        mermaid += f"  root(({elements[0]}))\n"
        
        # Add child nodes
        for element in elements[1:]:
            mermaid += f"    {element}\n"
        
        return mermaid
    
    def _generate_graph(self, elements: list, relationships: list) -> str:
        """Generate Mermaid.js graph"""
        mermaid = "graph LR\n"
        
        for i, element in enumerate(elements):
            mermaid += f"    {i}({element})\n"
        
        for rel in relationships:
            if len(rel) >= 2:
                mermaid += f"    {rel[0]} --- {rel[1]}\n"
        
        return mermaid
    
    def _generate_concept_map(self, elements: list, relationships: list) -> str:
        """Generate concept map (similar to flowchart but bidirectional)"""
        mermaid = "graph TB\n"
        
        for i, element in enumerate(elements):
            mermaid += f"    N{i}[{element}]\n"
        
        for rel in relationships:
            if len(rel) >= 3:
                from_idx = rel[0]
                to_idx = rel[1]
                label = rel[2]
                mermaid += f"    N{from_idx} <-->|{label}| N{to_idx}\n"
        
        return mermaid
    
    def _generate_ascii_fallback(self, elements: list) -> str:
        """Generate simple ASCII art as fallback"""
        if not elements:
            return "No elements to visualize"
        
        ascii_art = "\n"
        ascii_art += "┌─────────────────────┐\n"
        for element in elements:
            ascii_art += f"│ {element[:19]:<19} │\n"
            ascii_art += "├─────────────────────┤\n"
        ascii_art = ascii_art[:-25] + "└─────────────────────┘\n"
        
        return ascii_art

































































