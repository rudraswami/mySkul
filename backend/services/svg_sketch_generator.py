"""
SVG Sketch Generator - AI-powered educational diagram generation
Creates hand-drawn style SVG sketches like a professor drawing on a board
"""
import re
import logging
import hashlib
import json
from typing import Dict, Any, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)


class SVGSketchGenerator:
    """
    Generates educational SVG sketches using GPT-4o
    Style: Hand-drawn, sketch-like, educational (not corporate)
    """
    
    # Template SVG patterns for common educational elements
    SVG_TEMPLATES = {
        "arrow": '<path d="M {x1} {y1} L {x2} {y2}" stroke="{color}" stroke-width="2" fill="none" marker-end="url(#arrowhead)" />',
        "label": '<text x="{x}" y="{y}" font-family="Comic Sans MS, cursive" font-size="14" fill="{color}">{text}</text>',
        "box": '<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{color}" stroke-width="2" rx="5" />',
        "circle": '<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="2" />',
        "dashed_line": '<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2" stroke-dasharray="5,5" />'
    }
    
    # Color palettes for different metaphor categories
    COLOR_THEMES = {
        "cricket": ["#DC2626", "#F59E0B", "#10B981"],  # Red, amber, green
        "cooking": ["#F59E0B", "#D97706", "#92400E"],  # Orange, brown tones
        "accommodation": ["#6366F1", "#8B5CF6", "#A78BFA"],  # Purple, indigo
        "transport": ["#10B981", "#059669", "#047857"],  # Green tones
        "gaming": ["#8B5CF6", "#A855F7", "#C084FC"],  # Purple, pink
        "default": ["#374151", "#6B7280", "#9CA3AF"]  # Gray tones
    }
    
    def __init__(self, emergent_llm_key: str):
        """Initialize with Emergent LLM key"""
        self.emergent_llm_key = emergent_llm_key
        self.llm_chat = None
        self._init_llm()
    
    def _init_llm(self):
        """Initialize LLM for SVG generation"""
        try:
            self.llm_chat = LlmChat(
                api_key=self.emergent_llm_key,
                session_id="svg_sketch_gen",
                system_message="You are an expert educational visual designer. You create clean, hand-drawn style SVG diagrams for teaching concepts."
            ).with_model("openai", "gpt-4o").with_params(
                temperature=0.7,  # Some creativity for visual variety
                max_tokens=2000,  # SVG can be verbose
                top_p=0.9
            )
            logger.info("✅ SVG Generator LLM initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize SVG LLM: {e}")
    
    async def generate_educational_sketch(
        self,
        concept: str,
        topic: str,
        metaphor_category: str,
        metaphor_text: str,
        region: str = "Bangalore"
    ) -> Dict[str, Any]:
        """
        Generate educational SVG sketch for a concept
        
        Args:
            concept: Concept name (e.g., "quantum_numbers")
            topic: Topic category (e.g., "quantum_physics")
            metaphor_category: Category like "accommodation", "cricket"
            metaphor_text: The metaphor explanation text
            region: User's region for cultural relevance
            
        Returns:
            Dict with SVG data, metadata, and fallback
        """
        try:
            logger.info(f"🎨 Generating SVG sketch for concept: {concept}")
            logger.info(f"   Topic: {topic}, Metaphor: {metaphor_category}")
            
            # Get color theme
            colors = self.COLOR_THEMES.get(metaphor_category, self.COLOR_THEMES["default"])
            
            # Generate cache key
            cache_key = self._generate_cache_key(concept, topic, metaphor_category, region)
            
            # Build educational SVG prompt
            svg_prompt = self._build_svg_prompt(
                concept=concept,
                topic=topic,
                metaphor_text=metaphor_text,
                colors=colors,
                region=region
            )
            
            # Generate SVG using GPT-4o
            user_message = UserMessage(text=svg_prompt)
            
            logger.info("🤖 Calling GPT-4o for SVG generation...")
            response = await self.llm_chat.send_message(user_message)
            
            # Extract SVG from response
            svg_code = self._extract_svg(response)
            
            if svg_code:
                # Validate and optimize SVG
                svg_optimized = self._optimize_svg(svg_code)
                size_kb = len(svg_optimized) / 1024
                
                logger.info(f"✅ SVG generated successfully: {size_kb:.1f}KB")
                
                # Convert to data URI for embedding
                svg_data_uri = self._svg_to_data_uri(svg_optimized)
                
                return {
                    "success": True,
                    "svg_code": svg_optimized,
                    "svg_data_uri": svg_data_uri,
                    "size_kb": size_kb,
                    "cache_key": cache_key,
                    "tier": 2,  # AI-generated tier
                    "generation_method": "gpt4o",
                    "fallback_used": False
                }
            else:
                logger.warning("⚠️ No valid SVG in GPT-4o response, using template fallback")
                return self._generate_template_fallback(concept, topic, metaphor_category, colors)
                
        except Exception as e:
            logger.error(f"❌ SVG generation failed: {e}")
            return self._generate_template_fallback(concept, topic, metaphor_category, colors)
    
    def _build_svg_prompt(
        self,
        concept: str,
        topic: str,
        metaphor_text: str,
        colors: list,
        region: str
    ) -> str:
        """Build prompt for educational SVG generation"""
        
        prompt = f"""Generate a clean, educational SVG diagram (like a professor drawing on a board) for this concept:

**Concept**: {concept}
**Topic**: {topic}
**Metaphor**: {metaphor_text}
**Region**: {region} (use culturally relevant elements)

**SVG REQUIREMENTS**:

1. **Style**: Hand-drawn, sketch-like (NOT corporate or polished)
   - Use slightly wavy lines (not perfectly straight)
   - Comic Sans MS or similar casual font
   - Simple, clean, educational focus

2. **Size & Optimization**:
   - ViewBox: "0 0 800 600" (fixed for consistency)
   - Width: 800px, Height: 600px
   - Target size: <200KB (keep it simple)

3. **Educational Elements**:
   - Clear labels pointing to key parts
   - Step numbers if showing a process
   - Arrows showing relationships
   - Annotations for important details

4. **Color Palette** (use these colors):
   - Primary: {colors[0]}
   - Secondary: {colors[1]}
   - Accent: {colors[2]}

5. **Structure**:
   ```xml
   <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
     <defs>
       <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
         <polygon points="0 0, 10 3, 0 6" fill="{colors[0]}" />
       </marker>
     </defs>
     <!-- Main visual elements here -->
   </svg>
   ```

6. **What to Include**:
   - Central diagram showing the main concept
   - 3-5 key labels/annotations
   - Arrows showing flow or relationships
   - Simple icons or shapes representing metaphor elements

7. **What to AVOID**:
   - No photographs or raster images
   - No external <image> tags
   - No complex gradients or filters
   - No text longer than 50 characters per label
   - No clipPath or complex masks

**IMPORTANT**: 
- Return ONLY the SVG code (starting with <svg> and ending with </svg>)
- No markdown, no explanation, just pure SVG
- Make it educational and memorable
- Think like a professor drawing to explain to a 16-year-old student

Generate the SVG now:"""

        return prompt
    
    def _extract_svg(self, response: str) -> Optional[str]:
        """Extract SVG code from LLM response"""
        if not response:
            return None
        
        # Try to find SVG tags
        svg_match = re.search(r'<svg[^>]*>.*?</svg>', response, re.DOTALL | re.IGNORECASE)
        if svg_match:
            return svg_match.group(0)
        
        # Check if entire response is SVG
        if response.strip().startswith('<svg'):
            return response.strip()
        
        return None
    
    def _optimize_svg(self, svg_code: str) -> str:
        """Optimize SVG code for size and performance"""
        # Remove comments
        svg_code = re.sub(r'<!--.*?-->', '', svg_code, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        svg_code = re.sub(r'\s+', ' ', svg_code)
        svg_code = re.sub(r'>\s+<', '><', svg_code)
        
        # Ensure proper xmlns
        if 'xmlns=' not in svg_code:
            svg_code = svg_code.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"', 1)
        
        return svg_code.strip()
    
    def _svg_to_data_uri(self, svg_code: str) -> str:
        """Convert SVG to data URI for embedding"""
        # URL encode the SVG
        import urllib.parse
        encoded = urllib.parse.quote(svg_code)
        return f"data:image/svg+xml,{encoded}"
    
    def _generate_cache_key(self, concept: str, topic: str, metaphor: str, region: str) -> str:
        """Generate cache key for SVG"""
        key_string = f"{concept}_{topic}_{metaphor}_{region}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _generate_template_fallback(
        self,
        concept: str,
        topic: str,
        metaphor_category: str,
        colors: list
    ) -> Dict[str, Any]:
        """Generate template-based fallback SVG"""
        logger.info(f"📐 Generating template fallback for {concept}")
        
        # Simple template SVG for fallback
        svg_template = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="{colors[0]}" />
    </marker>
  </defs>
  
  <!-- Background -->
  <rect width="800" height="600" fill="#F9FAFB" />
  
  <!-- Central concept box -->
  <rect x="250" y="200" width="300" height="200" rx="10" fill="none" stroke="{colors[0]}" stroke-width="3" />
  <text x="400" y="310" font-family="Comic Sans MS, cursive" font-size="24" text-anchor="middle" fill="{colors[0]}">{concept.replace('_', ' ').title()}</text>
  
  <!-- Annotation arrows -->
  <line x1="150" y1="250" x2="240" y2="280" stroke="{colors[1]}" stroke-width="2" marker-end="url(#arrowhead)" />
  <text x="80" y="250" font-family="Comic Sans MS, cursive" font-size="14" fill="{colors[1]}">Key Concept</text>
  
  <line x1="650" y1="250" x2="560" y2="280" stroke="{colors[2]}" stroke-width="2" marker-end="url(#arrowhead)" />
  <text x="660" y="250" font-family="Comic Sans MS, cursive" font-size="14" fill="{colors[2]}">Important!</text>
  
  <!-- Metaphor hint -->
  <text x="400" y="500" font-family="Comic Sans MS, cursive" font-size="16" text-anchor="middle" fill="#6B7280" opacity="0.8">Visual metaphor: {metaphor_category}</text>
</svg>'''
        
        svg_optimized = self._optimize_svg(svg_template)
        svg_data_uri = self._svg_to_data_uri(svg_optimized)
        
        return {
            "success": True,
            "svg_code": svg_optimized,
            "svg_data_uri": svg_data_uri,
            "size_kb": len(svg_optimized) / 1024,
            "cache_key": self._generate_cache_key(concept, topic, metaphor_category, "default"),
            "tier": 1,  # Template fallback tier
            "generation_method": "template",
            "fallback_used": True
        }
    
    def generate_simple_svg_icon(self, icon_type: str, color: str = "#374151") -> str:
        """Generate simple SVG icon for UI elements"""
        icons = {
            "lightbulb": f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><path d="M9 21h6M12 3a6 6 0 0 1 6 6c0 2.5-1.5 4.5-3 6v2a1 1 0 0 1-1 1h-4a1 1 0 0 1-1-1v-2c-1.5-1.5-3-3.5-3-6a6 6 0 0 1 6-6z"/></svg>',
            "checkmark": f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>',
            "star": f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}"><polygon points="12 2 15 9 22 9 17 14 19 21 12 17 5 21 7 14 2 9 9 9"/></svg>'
        }
        return icons.get(icon_type, icons["lightbulb"])


# Quick test
async def test_svg_generator():
    """Test SVG generation"""
    import os
    
    # Get key from environment
    key = os.environ.get('EMERGENT_LLM_KEY')
    if not key:
        print("❌ EMERGENT_LLM_KEY not set in environment")
        return
    
    generator = SVGSketchGenerator(key)
    
    print("\n" + "="*60)
    print("SVG SKETCH GENERATOR TEST")
    print("="*60)
    
    result = await generator.generate_educational_sketch(
        concept="quantum_numbers",
        topic="quantum_physics",
        metaphor_category="accommodation",
        metaphor_text="Like hotel floors and rooms - n is floor, l is wing, m is room number",
        region="Mumbai"
    )
    
    print(f"\n✅ SVG Generated")
    print(f"   Size: {result['size_kb']:.1f}KB")
    print(f"   Tier: {result['tier']}")
    print(f"   Method: {result['generation_method']}")
    print(f"   Fallback: {result['fallback_used']}")
    print(f"\n📏 SVG Preview (first 500 chars):")
    print(result['svg_code'][:500])
    print("\n" + "="*60)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_svg_generator())
