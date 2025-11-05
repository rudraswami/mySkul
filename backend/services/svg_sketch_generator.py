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
        
        STRATEGY: Template-first approach (GPT-4o generates too generic visuals)
        - Use concept-specific templates (fast, educational, guaranteed quality)
        - Only use GPT-4o for unmapped concepts
        - Validate output for generic terms and reject if found
        
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
            
            # STRATEGY CHANGE: Template-first (GPT-4o unreliable for concept-specific visuals)
            # Try template first for known concepts
            template_result = self._try_concept_template(concept, topic, metaphor_category, colors, region)
            
            if template_result:
                logger.info(f"✅ Using concept-specific template (Tier 1): {template_result['size_kb']:.1f}KB")
                return template_result
            
            # If no template exists, generate with GPT-4o (with strict validation)
            logger.info("🤖 No template found, trying GPT-4o generation with strict validation...")
            
            # Generate cache key
            cache_key = self._generate_cache_key(concept, topic, metaphor_category, region)
            
            # Build STRICT educational SVG prompt
            svg_prompt = self._build_strict_svg_prompt(
                concept=concept,
                topic=topic,
                metaphor_text=metaphor_text,
                colors=colors,
                region=region
            )
            
            # Generate SVG using GPT-4o
            user_message = UserMessage(text=svg_prompt)
            
            logger.info("🤖 Calling GPT-4o for SVG generation with strict validation...")
            response = await self.llm_chat.send_message(user_message)
            
            # Extract SVG from response
            svg_code = self._extract_svg(response)
            
            if svg_code:
                # CRITICAL: Validate for generic terms
                is_valid, rejection_reason = self._validate_svg_educational(svg_code, concept)
                
                if not is_valid:
                    logger.warning(f"⚠️ SVG rejected: {rejection_reason}")
                    logger.warning("🔄 Falling back to template...")
                    return self._generate_template_fallback(concept, topic, metaphor_category, colors, region)
                
                # Validate and optimize SVG
                svg_optimized = self._optimize_svg(svg_code)
                size_kb = len(svg_optimized) / 1024
                
                logger.info(f"✅ SVG generated and validated: {size_kb:.1f}KB")
                
                # Convert to data URI for embedding
                svg_data_uri = self._svg_to_data_uri(svg_optimized)
                
                return {
                    "success": True,
                    "svg_code": svg_optimized,
                    "svg_data_uri": svg_data_uri,
                    "size_kb": size_kb,
                    "cache_key": cache_key,
                    "tier": 2,  # AI-generated tier
                    "generation_method": "gpt4o_validated",
                    "fallback_used": False
                }
            else:
                logger.warning("⚠️ No valid SVG in GPT-4o response, using template fallback")
                return self._generate_template_fallback(concept, topic, metaphor_category, colors, region)
                
        except Exception as e:
            logger.error(f"❌ SVG generation failed: {e}")
            return self._generate_template_fallback(concept, topic, metaphor_category, colors, region)
    
    def _validate_svg_educational(self, svg_code: str, concept: str) -> tuple[bool, str]:
        """
        Validate SVG is educational and concept-specific (not generic)
        
        Returns: (is_valid, rejection_reason)
        """
        svg_lower = svg_code.lower()
        
        # FORBIDDEN generic terms
        forbidden_terms = [
            'reactant a', 'reactant b', 'reactant c',
            'product a', 'product b', 'product c',
            'object a', 'object b', 'object c',
            'component 1', 'component 2', 'component 3',
            'element 1', 'element 2', 'element 3',
            'process 1', 'process 2', 'process 3',
            'step a', 'step b', 'step c',
            'reaction vessel', 'generic'
        ]
        
        for term in forbidden_terms:
            if term in svg_lower:
                return False, f"Contains forbidden generic term: '{term}'"
        
        # Check if SVG has meaningful content (not just boxes)
        has_text = len(re.findall(r'<text[^>]*>([^<]+)</text>', svg_code)) >= 3
        has_shapes = len(re.findall(r'<(rect|circle|ellipse|path|polygon)', svg_code)) >= 3
        
        if not has_text or not has_shapes:
            return False, "SVG lacks sufficient educational elements"
        
        return True, "Valid educational SVG"
    
    def _try_concept_template(self, concept: str, topic: str, metaphor: str, colors: list, region: str) -> Optional[Dict[str, Any]]:
        """Try to use concept-specific template first (template-first strategy)"""
        
        concept_lower = concept.lower()
        
        # Check if we have a template for this concept
        if 'photosynthesis' in concept_lower or 'catalyst' in concept_lower or 'weather' in concept_lower or 'climate' in concept_lower:
            logger.info(f"✅ Found concept-specific template for: {concept}")
            return self._generate_template_fallback(concept, topic, metaphor, colors, region)
        
        return None
    
    def _build_svg_prompt(
        self,
        concept: str,
        topic: str,
        metaphor_text: str,
        colors: list,
        region: str
    ) -> str:
        """Build concept-specific, metaphor-aligned SVG generation prompt"""
        
        # Get concept-specific guidance
        concept_guidance = self._get_concept_specific_guidance(concept, topic, metaphor_text, region)
        
        prompt = f"""Generate an educational SVG sketch that visually explains this concept step-by-step:

**Concept**: {concept}
**Topic**: {topic}
**Metaphor**: {metaphor_text}
**Region**: {region}

{concept_guidance}

**CRITICAL REQUIREMENTS**:

1. **CONCEPT-SPECIFIC VISUALS** (NOT generic placeholders):
   - Draw ACTUAL elements of the concept (e.g., plants for photosynthesis, NOT "Object A")
   - Show the METAPHOR visually (e.g., if metaphor is solar cooking, show solar cooker analogy)
   - NO generic boxes labeled "Reactant A/B" or "Process 1/2"
   - Every element should be recognizable and meaningful

2. **METAPHOR ALIGNMENT**:
   - The sketch MUST visually represent the metaphor
   - If metaphor is "solar cooking", show a solar cooker with labeled parts
   - If metaphor is "cricket strategy", show cricket field with player positions
   - If metaphor is "train journey", show train compartments with connections
   - The visual IS the metaphor, not a separate element

3. **EDUCATIONAL FLOW** (3-6 steps):
   - Show clear progression: Input → Process → Output
   - Number each step (1, 2, 3...)
   - Use arrows to show flow direction
   - Each step should teach something specific

4. **HAND-DRAWN SKETCH STYLE**:
   - Slightly wavy lines (not perfectly straight)
   - Comic Sans MS or cursive font
   - Friendly, approachable, professor-drawing-on-board feel
   - NOT corporate, NOT abstract, NOT generic

5. **INDIAN CULTURAL ELEMENTS** (where appropriate):
   - Use culturally relevant icons: tiffin, dosa tawa, cricket bat, train, auto-rickshaw
   - Regional foods: {self._get_regional_foods(region)}
   - Make it relatable to Indian students

6. **SIZE & STRUCTURE**:
   - ViewBox: "0 0 800 600"
   - Width: 800px, Height: 600px
   - Size target: <200KB (use simple shapes, avoid complexity)
   
   ```xml
   <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
     <defs>
       <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
         <polygon points="0 0, 10 3, 0 6" fill="{colors[0]}" />
       </marker>
     </defs>
     
     <!-- Metaphor callout at top -->
     <text x="400" y="30" font-family="Comic Sans MS, cursive" font-size="16" text-anchor="middle" fill="{colors[0]}">
       💡 Think of this like: {metaphor_text[:60]}...
     </text>
     
     <!-- Step-by-step visual explanation -->
     <!-- Step 1: [Actual concept element] -->
     <!-- Step 2: [Process happening] -->
     <!-- Step 3: [Result/output] -->
     
     <!-- Arrows showing flow -->
     <!-- Labels explaining each part -->
   </svg>
   ```

7. **COLOR PALETTE**:
   - Primary: {colors[0]}
   - Secondary: {colors[1]}
   - Accent: {colors[2]}

8. **WHAT TO AVOID**:
   - ❌ Generic placeholders ("Object A", "Reactant 1")
   - ❌ Abstract boxes with no meaning
   - ❌ Photos or raster images
   - ❌ Corporate-style diagrams
   - ❌ Complex gradients or filters
   - ❌ Text longer than 40 characters per label

**SUCCESS CRITERIA**:
- A 16-year-old student should understand the concept from the visual ALONE
- The metaphor should be clearly visible in the sketch
- Each step should be numbered and labeled
- Cultural elements should make it relatable

**IMPORTANT**: 
- Return ONLY the SVG code (starting with <svg> and ending with </svg>)
- No markdown formatting, no explanation text, just pure SVG
- Make it educational, clear, and memorable
- The visual should tell the story

Generate the concept-specific SVG now:"""

        return prompt
    
    def _get_concept_specific_guidance(self, concept: str, topic: str, metaphor_text: str, region: str) -> str:
        """Get ultra-specific visual guidance for each concept with emotional storytelling"""
        
        concept_lower = concept.lower()
        
        # Weather vs Climate (Geography)
        if 'weather' in concept_lower or 'climate' in concept_lower:
            return """**VISUAL STORYTELLING FOR WEATHER VS CLIMATE**:

**BACKGROUND**: Soft cream (#FEF7ED) - warm, neutral, educational

**CORE VISUAL CONCEPT**: Show a student's wardrobe/lifestyle analogy

**LEFT SIDE - WEATHER (Daily Choice)**:
- Draw a student figure looking at TODAY'S outfit
- Wardrobe with TODAY label (torn calendar page showing "Monday")
- Clothes hanging: Raincoat, Umbrella (for today's rain)
- Weather icons above: ☁️ Dark clouds, 🌧️ Rain drops falling
- Label: "WEATHER = What to wear TODAY"
- Emotion: Student checking weather app on phone

**RIGHT SIDE - CLIMATE (Seasonal Pattern)**:
- Same student looking at FULL WARDROBE for the YEAR
- 4 sections labeled: Summer (☀️), Monsoon (🌧️), Winter (❄️), Spring (🌸)
- Each section has appropriate Indian clothes:
  * Summer: Cotton kurta, sunglasses
  * Monsoon: Raincoat, umbrella, boots
  * Winter: Sweater, jacket
  * Spring: Light clothes, flowers
- Label: "CLIMATE = What to keep for the SEASON"
- Calendar showing full year pattern

**CONNECTING ELEMENT**:
- Arrow from left to right: "Daily → Patterns → Climate"
- Text: "Many weather days = Climate pattern!"

**VISUAL STYLE**:
- Hand-drawn figures (simple stick figures with Indian clothes)
- Actual clothing items drawn (not boxes)
- Use icons: ☀️ 🌧️ ❄️ 🌸 ☁️
- Color code: Warm colors for summer, blue for rain, cool for winter
- Thought bubbles showing student thinking

**EMOTIONAL DESIGN**:
- Student expression: Curious, figuring it out
- Relatable scenario: Getting ready for school
- Indian context: Monsoon season, cotton clothes, etc.

**NO BOXES**: Draw actual clothes, weather icons, student figure, wardrobe shelves"""
        
        # Photosynthesis
        elif 'photosynthesis' in concept_lower:
            return """**VISUAL STORYTELLING FOR PHOTOSYNTHESIS**:

**BACKGROUND**: Light green (#F0FDF4) - nature, growth

**CORE VISUAL**: Solar cooking analogy (Indian context)

**TOP SECTION - THE SETUP**:
- Draw simple solar cooker (parabolic dish) reflecting sunlight
- Label: "1️⃣ ENERGY SOURCE"
- Sun rays hitting reflector → Focus point
- Emotion: Efficient, concentrated energy

**MIDDLE SECTION - THE PLANT (Parallel to cooker)**:
- Draw actual plant with distinct parts:
  * 🌿 Green leaves (chlorophyll)
  * Roots drawing 💧 H₂O from soil
  * Stomata (tiny holes) taking 🌬️ CO₂ from air
- Label: "2️⃣ INGREDIENTS COLLECTION"
- Arrows showing inputs converging

**BOTTOM SECTION - THE MAGIC**:
- Inside leaf: Tiny factory icon (chloroplast)
- Chemical equation simplified: 
  * "6CO₂ + 6H₂O + ☀️ → C₆H₁₂O₆ (Glucose) + 6O₂"
- Label: "3️⃣ FOOD PRODUCTION"
- Glucose shown as energy packets (batteries 🔋)
- O₂ bubbles floating up

**PARALLEL SHOWN**:
- Side-by-side comparison box:
  * Solar Cooker: Sun → Heat → Food Cooked
  * Photosynthesis: Sun → Chlorophyll → Glucose Made

**EMOTIONAL DESIGN**:
- Green = Life, growth
- Sun rays = Energy, warmth
- Plant = Friendly character
- Glucose = Energy fuel (show as battery icons)

**NO GENERIC SHAPES**: Draw actual leaf structure, sun with rays, roots, chemical molecules"""
        
        # Quantum numbers
        elif 'quantum' in concept_lower:
            return """**VISUAL STORYTELLING FOR QUANTUM NUMBERS**:
**BACKGROUND**: Soft lavender (#F5F3FF)
- Draw Indian hotel/apartment building showing n (floors), l (wings), m (rooms), s (beds)
- Show electron character finding its room with address tag
- Use building metaphor with visual organization
- Label clearly: n=1,2,3... l=0,1,2... m=-l to +l, s=↑↓"""
        
        # Ionic bonding  
        elif 'ionic' in concept_lower and 'bond' in concept_lower:
            return """**VISUAL STORYTELLING FOR IONIC BONDING**:
**BACKGROUND**: Warm orange (#FEF3C7)
- Draw Indian tiffin dabba sharing metaphor
- Show Na student giving electron to Cl student
- Show attraction and bond formation with expressive characters
- Use Indian tiffin box style (stacked circular containers)"""
        
        # Newton's laws
        elif 'newton' in concept_lower:
            return """**VISUAL STORYTELLING FOR NEWTON'S LAWS**:
**BACKGROUND**: Sky blue (#EBF8FF)
Three panel story showing:
1. Ball at rest (inertia)
2. Force and acceleration comparison (F=ma)
3. Action-reaction with cricket scenario
Use cricket context with player and ball, show forces visually"""
        
        # Generic fallback
        else:
            return f"""**VISUAL STORYTELLING FOR {concept.upper()}**:
**BACKGROUND**: Soft cream (#FEF7ED) - neutral, educational

CORE REQUIREMENTS:
- NO GENERIC BOXES - Draw actual concept elements
- STORYTELLING FLOW: Beginning → Process → Result  
- EMOTIONAL DESIGN: Characters with expressions
- INDIAN CONTEXT: Familiar objects and scenarios
- VISUAL METAPHOR: {metaphor_text} shown visually

STRUCTURE:
- Left: Starting point
- Middle: Process happening
- Right: Result achieved

Include: Simple characters, actual objects, arrows, thought bubbles, icons, numbered steps"""
    
    def _get_regional_foods(self, region: str) -> str:
        """Get regional foods for cultural context"""
        foods = {
            'Delhi': 'butter chicken, paratha, chole',
            'Mumbai': 'vada pav, pav bhaji, bhel puri',
            'Chennai': 'dosa, idli, filter coffee',
            'Kolkata': 'rasgulla, mishti doi, phuchka',
            'Bangalore': 'dosa, bisi bele bath, filter coffee'
        }
        return foods.get(region, 'Indian food items')
    
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
        colors: list,
        region: str = "Bangalore"
    ) -> Dict[str, Any]:
        """Generate concept-aware template-based fallback SVG"""
        logger.info(f"📐 Generating concept-aware template fallback for {concept}")
        
        # Get concept-specific template
        svg_template = self._get_concept_template(concept, topic, metaphor_category, colors, region)
        
        svg_optimized = self._optimize_svg(svg_template)
        svg_data_uri = self._svg_to_data_uri(svg_optimized)
        
        return {
            "success": True,
            "svg_code": svg_optimized,
            "svg_data_uri": svg_data_uri,
            "size_kb": len(svg_optimized) / 1024,
            "cache_key": self._generate_cache_key(concept, topic, metaphor_category, "default"),
            "tier": 1,  # Template fallback tier
            "generation_method": "template_concept_aware",
            "fallback_used": True
        }
    
    def _get_concept_template(self, concept: str, topic: str, metaphor_category: str, colors: list, region: str) -> str:
        """Get concept-specific SVG template (not generic) - EXPANDED LIBRARY"""
        
        concept_lower = concept.lower()
        
        # CATALYST / CHEMICAL REACTION template
        if 'catalyst' in concept_lower or 'speed up' in concept_lower or ('chemical' in concept_lower and 'reaction' in concept_lower):
            return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="{colors[0]}" />
    </marker>
  </defs>
  <rect width="800" height="600" fill="#FEF7ED" />
  
  <!-- Title -->
  <text x="400" y="35" font-family="Comic Sans MS, cursive" font-size="20" text-anchor="middle" fill="{colors[0]}" font-weight="bold">
    💡 Catalyst: Like Adding Tadka to Speed Up Cooking!
  </text>
  
  <!-- TOP ROW - WITHOUT CATALYST (Slow) -->
  <text x="150" y="100" font-family="Comic Sans MS, cursive" font-size="16" fill="{colors[0]}" font-weight="bold">WITHOUT Catalyst (Slow 🐢)</text>
  
  <!-- Reactants -->
  <circle cx="100" cy="180" r="30" fill="#93C5FD" stroke="{colors[0]}" stroke-width="2" />
  <text x="100" y="190" font-family="Comic Sans MS, cursive" font-size="18" text-anchor="middle" fill="{colors[0]}">H₂</text>
  
  <circle cx="200" cy="180" r="30" fill="#FCA5A5" stroke="{colors[0]}" stroke-width="2" />
  <text x="200" y="190" font-family="Comic Sans MS, cursive" font-size="18" text-anchor="middle" fill="{colors[0]}">O₂</text>
  
  <!-- Slow arrow -->
  <line x1="240" y1="180" x2="330" y2="180" stroke="{colors[1]}" stroke-width="2" marker-end="url(#arrowhead)" stroke-dasharray="10,5" />
  <text x="285" y="165" font-family="Comic Sans MS, cursive" font-size="12" fill="{colors[1]}">Slow reaction</text>
  <text x="285" y="200" font-family="Comic Sans MS, cursive" font-size="12" fill="{colors[1]}">High energy needed</text>
  
  <!-- Product -->
  <ellipse cx="400" cy="180" rx="50" ry="35" fill="#D9F99D" stroke="{colors[0]}" stroke-width="2" />
  <text x="400" y="190" font-family="Comic Sans MS, cursive" font-size="16" text-anchor="middle" fill="{colors[0]}">H₂O</text>
  <text x="400" y="235" font-family="Comic Sans MS, cursive" font-size="12" text-anchor="middle" fill="{colors[1]}">⏰ Takes long time!</text>
  
  <!-- BOTTOM ROW - WITH CATALYST (Fast) -->
  <text x="150" y="320" font-family="Comic Sans MS, cursive" font-size="16" fill="{colors[0]}" font-weight="bold">WITH Catalyst (Fast ⚡)</text>
  
  <!-- Reactants -->
  <circle cx="100" cy="400" r="30" fill="#93C5FD" stroke="{colors[0]}" stroke-width="2" />
  <text x="100" y="410" font-family="Comic Sans MS, cursive" font-size="18" text-anchor="middle" fill="{colors[0]}">H₂</text>
  
  <circle cx="200" cy="400" r="30" fill="#FCA5A5" stroke="{colors[0]}" stroke-width="2" />
  <text x="200" y="410" font-family="Comic Sans MS, cursive" font-size="18" text-anchor="middle" fill="{colors[0]}">O₂</text>
  
  <!-- CATALYST (Tadka spoon!) -->
  <rect x="260" y="370" width="70" height="60" rx="8" fill="#FCD34D" stroke="{colors[0]}" stroke-width="3" />
  <text x="295" y="395" font-family="Comic Sans MS, cursive" font-size="14" text-anchor="middle" fill="{colors[0]}" font-weight="bold">🥄 Pt</text>
  <text x="295" y="415" font-family="Comic Sans MS, cursive" font-size="10" text-anchor="middle" fill="#78350F">Catalyst</text>
  
  <!-- Fast arrow with boost -->
  <line x1="340" y1="400" x2="430" y2="400" stroke="#10B981" stroke-width="4" marker-end="url(#arrowhead)" />
  <text x="385" y="385" font-family="Comic Sans MS, cursive" font-size="13" fill="#10B981" font-weight="bold">⚡ FAST!</text>
  <text x="385" y="425" font-family="Comic Sans MS, cursive" font-size="11" fill="#10B981">Lower energy path</text>
  
  <!-- Product (same) -->
  <ellipse cx="500" cy="400" rx="50" ry="35" fill="#D9F99D" stroke="{colors[0]}" stroke-width="2" />
  <text x="500" y="410" font-family="Comic Sans MS, cursive" font-size="16" text-anchor="middle" fill="{colors[0]}">H₂O</text>
  <text x="500" y="455" font-family="Comic Sans MS, cursive" font-size="12" text-anchor="middle" fill="#10B981">✅ Quick reaction!</text>
  
  <!-- Explanation box -->
  <rect x="550" y="150" width="220" height="250" rx="10" fill="#FFFBEB" stroke="{colors[0]}" stroke-width="2" />
  <text x="660" y="180" font-family="Comic Sans MS, cursive" font-size="14" text-anchor="middle" fill="{colors[0]}" font-weight="bold">🥘 Tadka Analogy:</text>
  <text x="570" y="210" font-family="Comic Sans MS, cursive" font-size="12" fill="#78350F">• Dal cooks slowly</text>
  <text x="570" y="235" font-family="Comic Sans MS, cursive" font-size="12" fill="#78350F">• Add tadka (cumin,</text>
  <text x="570" y="255" font-family="Comic Sans MS, cursive" font-size="12" fill="#78350F">  mustard seeds)</text>
  <text x="570" y="280" font-family="Comic Sans MS, cursive" font-size="12" fill="#10B981">• Flavor spreads FAST!</text>
  <text x="570" y="310" font-family="Comic Sans MS, cursive" font-size="12" fill="#78350F">Same way, catalyst</text>
  <text x="570" y="330" font-family="Comic Sans MS, cursive" font-size="12" fill="#78350F">speeds reaction</text>
  <text x="570" y="350" font-family="Comic Sans MS, cursive" font-size="12" fill="#78350F">without getting used!</text>
  
  <!-- Bottom summary -->
  <text x="400" y="530" font-family="Comic Sans MS, cursive" font-size="14" text-anchor="middle" fill="{colors[0]}">Key: Catalyst = Reaction Speed Booster (Like Tadka in Cooking!) 🥘</text>
  <text x="400" y="560" font-family="Comic Sans MS, cursive" font-size="12" text-anchor="middle" fill="#6B7280">Lower activation energy → Faster product formation</text>
</svg>'''
        
        # Photosynthesis template
        if 'photosynthesis' in concept_lower:
            return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="{colors[0]}" />
    </marker>
  </defs>
  <rect width="800" height="600" fill="#F0FDF4" />
  
  <!-- Title/Metaphor -->
  <text x="400" y="30" font-family="Comic Sans MS, cursive" font-size="18" text-anchor="middle" fill="{colors[0]}" font-weight="bold">
    💡 Photosynthesis: Like Solar Cooking - Sun's Energy Makes Food!
  </text>
  
  <!-- Sun -->
  <circle cx="100" cy="100" r="40" fill="#FCD34D" stroke="{colors[0]}" stroke-width="2" />
  <text x="100" y="170" font-family="Comic Sans MS, cursive" font-size="14" text-anchor="middle" fill="{colors[0]}">☀️ Sunlight</text>
  
  <!-- Sunlight rays -->
  <line x1="140" y1="120" x2="250" y2="250" stroke="{colors[0]}" stroke-width="3" marker-end="url(#arrowhead)" stroke-dasharray="5,5" />
  
  <!-- Plant/Leaf -->
  <ellipse cx="300" cy="300" rx="80" ry="60" fill="#86EFAC" stroke="{colors[0]}" stroke-width="3" />
  <text x="300" y="305" font-family="Comic Sans MS, cursive" font-size="16" text-anchor="middle" fill="{colors[0]}" font-weight="bold">🌿 Leaf</text>
  <text x="300" y="325" font-family="Comic Sans MS, cursive" font-size="12" text-anchor="middle" fill="#065F46">(Chlorophyll)</text>
  
  <!-- CO2 input -->
  <text x="150" y="350" font-family="Comic Sans MS, cursive" font-size="14" fill="{colors[1]}">CO₂</text>
  <line x1="180" y1="345" x2="230" y2="310" stroke="{colors[1]}" stroke-width="2" marker-end="url(#arrowhead)" />
  
  <!-- H2O input -->
  <text x="150" y="400" font-family="Comic Sans MS, cursive" font-size="14" fill="#0EA5E9">H₂O</text>
  <line x1="180" y1="395" x2="230" y2="330" stroke="#0EA5E9" stroke-width="2" marker-end="url(#arrowhead)" />
  
  <!-- Glucose output -->
  <rect x="420" y="260" width="120" height="80" rx="10" fill="#FEF3C7" stroke="{colors[0]}" stroke-width="3" />
  <text x="480" y="295" font-family="Comic Sans MS, cursive" font-size="16" text-anchor="middle" fill="{colors[0]}" font-weight="bold">🍬 Glucose</text>
  <text x="480" y="315" font-family="Comic Sans MS, cursive" font-size="12" text-anchor="middle" fill="#78350F">(C₆H₁₂O₆)</text>
  <line x1="380" y1="300" x2="415" y2="300" stroke="{colors[0]}" stroke-width="3" marker-end="url(#arrowhead)" />
  
  <!-- O2 output -->
  <text x="300" y="220" font-family="Comic Sans MS, cursive" font-size="14" fill="{colors[2]}">O₂ ↑</text>
  <line x1="300" y1="240" x2="300" y2="230" stroke="{colors[2]}" stroke-width="2" marker-end="url(#arrowhead)" />
  
  <!-- Step labels -->
  <text x="50" y="500" font-family="Comic Sans MS, cursive" font-size="14" fill="{colors[0]}">1️⃣ Sun gives energy</text>
  <text x="250" y="500" font-family="Comic Sans MS, cursive" font-size="14" fill="{colors[0]}">2️⃣ Leaf absorbs light</text>
  <text x="450" y="500" font-family="Comic Sans MS, cursive" font-size="14" fill="{colors[0]}">3️⃣ Makes glucose + O₂</text>
</svg>'''
        
        # Quantum numbers (hotel) template
        elif 'quantum' in concept_lower:
            return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="{colors[0]}" />
    </marker>
  </defs>
  <rect width="800" height="600" fill="#F5F3FF" />
  
  <!-- Title -->
  <text x="400" y="30" font-family="Comic Sans MS, cursive" font-size="18" text-anchor="middle" fill="{colors[0]}" font-weight="bold">
    💡 Quantum Numbers: Like Hotel Room Address!
  </text>
  
  <!-- Hotel building -->
  <rect x="200" y="100" width="400" height="400" fill="#E0E7FF" stroke="{colors[0]}" stroke-width="3" />
  
  <!-- Floors (n) -->
  <line x1="200" y1="200" x2="600" y2="200" stroke="{colors[0]}" stroke-width="2" />
  <line x1="200" y1="300" x2="600" y2="300" stroke="{colors[0]}" stroke-width="2" />
  <line x1="200" y1="400" x2="600" y2="400" stroke="{colors[0]}" stroke-width="2" />
  
  <!-- Floor labels (n) -->
  <text x="150" y="150" font-family="Comic Sans MS, cursive" font-size="16" text-anchor="end" fill="{colors[0]}" font-weight="bold">n=3</text>
  <text x="150" y="250" font-family="Comic Sans MS, cursive" font-size="16" text-anchor="end" fill="{colors[0]}" font-weight="bold">n=2</text>
  <text x="150" y="350" font-family="Comic Sans MS, cursive" font-size="16" text-anchor="end" fill="{colors[0]}" font-weight="bold">n=1</text>
  <text x="150" y="450" font-family="Comic Sans MS, cursive" font-size="16" text-anchor="end" fill="{colors[0]}" font-weight="bold">n=0</text>
  
  <!-- Wings (l) -->
  <line x1="400" y1="100" x2="400" y2="500" stroke="{colors[1]}" stroke-width="2" stroke-dasharray="5,5" />
  <text x="300" y="90" font-family="Comic Sans MS, cursive" font-size="14" text-anchor="middle" fill="{colors[1]}">Wing A (l=0)</text>
  <text x="500" y="90" font-family="Comic Sans MS, cursive" font-size="14" text-anchor="middle" fill="{colors[1]}">Wing B (l=1)</text>
  
  <!-- Rooms (m) -->
  <circle cx="300" cy="250" r="20" fill="{colors[2]}" stroke="{colors[0]}" stroke-width="2" />
  <text x="300" y="255" font-family="Comic Sans MS, cursive" font-size="12" text-anchor="middle" fill="white" font-weight="bold">m</text>
  
  <!-- Electron -->
  <circle cx="300" cy="250" r="8" fill="#EF4444" />
  <text x="300" y="285" font-family="Comic Sans MS, cursive" font-size="12" text-anchor="middle" fill="{colors[0]}">⚡ e⁻</text>
  
  <!-- Legend -->
  <text x="50" y="540" font-family="Comic Sans MS, cursive" font-size="13" fill="{colors[0]}">n = Floor (energy level)</text>
  <text x="250" y="540" font-family="Comic Sans MS, cursive" font-size="13" fill="{colors[1]}">l = Wing (orbital shape)</text>
  <text x="450" y="540" font-family="Comic Sans MS, cursive" font-size="13" fill="{colors[2]}">m = Room (orientation)</text>
  <text x="650" y="540" font-family="Comic Sans MS, cursive" font-size="13" fill="#EF4444">s = Bed (spin ↑↓)</text>
</svg>'''
        
        # Generic fallback (improved)
        else:
            concept_display = concept.replace('_', ' ').title()
            return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="{colors[0]}" />
    </marker>
  </defs>
  <rect width="800" height="600" fill="#F9FAFB" />
  
  <!-- Title -->
  <text x="400" y="40" font-family="Comic Sans MS, cursive" font-size="20" text-anchor="middle" fill="{colors[0]}" font-weight="bold">
    {concept_display}
  </text>
  
  <!-- Main concept area -->
  <rect x="200" y="150" width="400" height="250" rx="15" fill="white" stroke="{colors[0]}" stroke-width="3" />
  <text x="400" y="280" font-family="Comic Sans MS, cursive" font-size="18" text-anchor="middle" fill="{colors[0]}">
    📚 Learning about
  </text>
  <text x="400" y="310" font-family="Comic Sans MS, cursive" font-size="16" text-anchor="middle" fill="{colors[1]}">
    {concept_display}
  </text>
  
  <!-- Step indicators -->
  <circle cx="250" cy="450" r="30" fill="{colors[0]}" />
  <text x="250" y="460" font-family="Comic Sans MS, cursive" font-size="20" text-anchor="middle" fill="white" font-weight="bold">1</text>
  
  <line x1="280" y1="450" x2="320" y2="450" stroke="{colors[0]}" stroke-width="3" marker-end="url(#arrowhead)" />
  
  <circle cx="400" cy="450" r="30" fill="{colors[1]}" />
  <text x="400" y="460" font-family="Comic Sans MS, cursive" font-size="20" text-anchor="middle" fill="white" font-weight="bold">2</text>
  
  <line x1="430" y1="450" x2="470" y2="450" stroke="{colors[1]}" stroke-width="3" marker-end="url(#arrowhead)" />
  
  <circle cx="550" cy="450" r="30" fill="{colors[2]}" />
  <text x="550" y="460" font-family="Comic Sans MS, cursive" font-size="20" text-anchor="middle" fill="white" font-weight="bold">3</text>
  
  <!-- Metaphor category hint -->
  <text x="400" y="550" font-family="Comic Sans MS, cursive" font-size="14" text-anchor="middle" fill="#6B7280">
    💡 Metaphor: {metaphor_category.replace('_', ' ').title()}
  </text>
</svg>'''
    
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
