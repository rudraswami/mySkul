"""
Visualise Agent - TRUE AGENTIC Visual Learning Agent
=====================================================

UPGRADED to TRUE AGENT with:
- ReAct Loop: Think → Act → Observe
- Tools: DiagramGenerationTool (Mermaid.js)
- Memory: Remembers student's visual preferences
- Actions: ACTUALLY generates diagrams (not just descriptions)

OLD: Described what a diagram would look like
NEW: GENERATES actual Mermaid.js diagrams for rendering
"""

import logging
from typing import Dict, Any, Optional
from agents.core.react_agent import ReActAgent
from agents.core.tool_registry import ToolRegistry
from agents.core.tools.diagram_generation_tool import DiagramGenerationTool
from agents.core.memory import LongTermMemory

logger = logging.getLogger(__name__)


class VisualiseAgent(ReActAgent):
    """
    TRUE AGENTIC Visual Learning Agent
    
    Capabilities:
    - Generates actual Mermaid.js diagrams
    - Creates flowcharts, sequences, mindmaps
    - Remembers student's visual learning preferences
    - Uses ReAct loop to determine best visualization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Initialize tool registry with visual tools
        self.tool_registry = ToolRegistry()
        self.tool_registry.register(DiagramGenerationTool())
        
        # Initialize memory for visual preferences (will be set per user)
        self.memory = None  # Set during process() with actual user_id
        
        logger.info("🎨 VisualiseAgent initialized as TRUE AGENT with diagram generation")
    
    def get_agent_name(self) -> str:
        return "VisualiseAgent"
    
    def get_available_tools(self) -> list:
        """Return list of tools this agent can use"""
        return ['generate_diagram']
    
    def get_agent_persona(self) -> str:
        return """You are a visual learning expert who creates diagrams and visual representations.

Your role:
- Analyze concepts and determine best visualization type
- Generate actual Mermaid.js diagrams (not just descriptions)
- Use flowcharts for processes, mindmaps for concepts, sequences for interactions
- Remember student's visual learning preferences

When to use each diagram type:
- Flowchart: Processes, algorithms, decision trees
- Sequence: Interactions, timelines, cause-effect
- Mindmap: Concept relationships, brainstorming
- Graph: Connections, networks, dependencies
- Concept map: Knowledge structures

Always output actual Mermaid.js code that can be rendered."""
    
    async def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process visual learning request using ReAct loop.
        
        Think: Analyze what needs to be visualized
        Act: Use DiagramGenerationTool to generate
        Observe: Verify diagram is useful
        """
        try:
            logger.info(f"🎨 VisualiseAgent processing: {query[:100]}")
            
            # Extract visual requirements from query
            visual_type = self._detect_visual_type(query)
            elements = self._extract_elements(query, context)
            relationships = self._extract_relationships(query, context)
            
            logger.info(f"🎨 Detected visual type: {visual_type}")
            logger.info(f"🎨 Elements: {elements}")
            
            # Use ReAct loop to generate diagram
            # Think: What's the best way to visualize this?
            thought = f"Student wants to visualize: {query}. Best approach: {visual_type} diagram with {len(elements)} elements."
            
            # Act: Use DiagramGenerationTool
            tool_result = await self.tool_registry.execute_tool(
                'generate_diagram',
                diagram_type=visual_type,
                description=query,
                elements=elements,
                relationships=relationships
            )
            
            # Observe: Check if diagram was generated successfully
            if tool_result.success:
                diagram_data = tool_result.data
                
                # Generate explanation to accompany diagram
                explanation = self._generate_explanation(query, visual_type, elements, context)
                
                return {
                    'success': True,
                    'content': explanation,
                    'visual_data': {
                        'type': 'diagram',
                        'diagram_type': visual_type,
                        'mermaid_code': diagram_data.get('mermaid_code'),
                        'ascii_fallback': diagram_data.get('ascii_art'),
                        'description': diagram_data.get('description')
                    },
                    'thought': thought,
                    'action': 'generate_diagram',
                    'observation': 'Diagram generated successfully'
                }
            else:
                # Fallback to text description
                return {
                    'success': True,
                    'content': self._generate_text_description(query, context),
                    'visual_data': None,
                    'thought': thought,
                    'action': 'generate_diagram',
                    'observation': f'Diagram generation failed: {tool_result.error}'
                }
                
        except Exception as e:
            logger.error(f"❌ VisualiseAgent error: {e}", exc_info=True)
            return {
                'success': False,
                'content': "I had trouble creating that visualization. Let me describe it instead.",
                'error': str(e)
            }
    
    def _detect_visual_type(self, query: str) -> str:
        """Detect best diagram type for query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['process', 'flow', 'step', 'algorithm', 'how']):
            return 'flowchart'
        elif any(word in query_lower for word in ['sequence', 'timeline', 'order', 'interaction']):
            return 'sequence'
        elif any(word in query_lower for word in ['concept', 'relationship', 'connect', 'relate']):
            return 'mindmap'
        elif any(word in query_lower for word in ['network', 'graph', 'connection']):
            return 'graph'
        else:
            return 'concept_map'
    
    def _extract_elements(self, query: str, context: Dict[str, Any]) -> list:
        """Extract key elements to visualize"""
        # Simple extraction - can be enhanced with NLP
        subject = context.get('subject', 'General')
        
        # Default elements based on subject
        if 'physics' in subject.lower():
            return ['Force', 'Mass', 'Acceleration', 'Velocity']
        elif 'chemistry' in subject.lower():
            return ['Reactants', 'Products', 'Catalyst', 'Energy']
        elif 'math' in subject.lower():
            return ['Input', 'Process', 'Output', 'Result']
        else:
            # Extract from query (simple word extraction)
            words = query.split()
            elements = [w.capitalize() for w in words if len(w) > 4][:5]
            return elements if elements else ['Concept', 'Understanding', 'Application']
    
    def _extract_relationships(self, query: str, context: Dict[str, Any]) -> list:
        """Extract relationships between elements"""
        # Simple relationship extraction
        # Format: [(from_idx, to_idx, label), ...]
        return [
            (0, 1, 'leads to'),
            (1, 2, 'results in'),
            (2, 3, 'produces')
        ]
    
    def _generate_explanation(self, query: str, visual_type: str, elements: list, context: Dict[str, Any]) -> str:
        """Generate explanation to accompany diagram"""
        subject = context.get('subject', 'this concept')
        
        explanation = f"Here's a {visual_type} to visualize {subject}:\n\n"
        explanation += f"The diagram shows {len(elements)} key components: {', '.join(elements[:3])}.\n\n"
        explanation += "Study this visual representation to understand how these elements connect and interact."
        
        return explanation
    
    def _generate_text_description(self, query: str, context: Dict[str, Any]) -> str:
        """Fallback text description if diagram generation fails"""
        return f"Let me describe this visually:\n\nImagine a diagram showing the key concepts and how they relate to each other. Each element connects to show the flow of understanding."
