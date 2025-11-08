/**
 * SVG Generation Utilities
 * Programmatic SVG generation for concept visualization
 */

/**
 * Generate SVG for mathematical concepts
 * @param {string} topic - The mathematical topic
 * @returns {string} - SVG string
 */
function generateMathSVG(topic) {
  const normalizedTopic = topic.toLowerCase();
  
  if (normalizedTopic.includes('triangle') || normalizedTopic.includes('trigonometry')) {
    return `
      <svg width="120" height="100" viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="triangleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#5E81F4;stop-opacity:0.8" />
            <stop offset="100%" style="stop-color:#9E7BF5;stop-opacity:0.6" />
          </linearGradient>
        </defs>
        <polygon points="60,15 15,85 105,85" fill="url(#triangleGrad)" stroke="#5E81F4" stroke-width="2"/>
        <circle cx="60" cy="15" r="3" fill="#5E81F4"/>
        <circle cx="15" cy="85" r="3" fill="#5E81F4"/>
        <circle cx="105" cy="85" r="3" fill="#5E81F4"/>
        <text x="60" y="12" text-anchor="middle" font-size="10" fill="#5E81F4">A</text>
        <text x="12" y="95" text-anchor="middle" font-size="10" fill="#5E81F4">B</text>
        <text x="108" y="95" text-anchor="middle" font-size="10" fill="#5E81F4">C</text>
      </svg>
    `;
  }
  
  if (normalizedTopic.includes('circle') || normalizedTopic.includes('radius')) {
    return `
      <svg width="120" height="100" viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <radialGradient id="circleGrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" style="stop-color:#5E81F4;stop-opacity:0.3" />
            <stop offset="100%" style="stop-color:#5E81F4;stop-opacity:0.8" />
          </radialGradient>
        </defs>
        <circle cx="60" cy="50" r="35" fill="url(#circleGrad)" stroke="#5E81F4" stroke-width="2"/>
        <line x1="60" y1="50" x2="95" y2="50" stroke="#9E7BF5" stroke-width="2"/>
        <circle cx="60" cy="50" r="3" fill="#5E81F4"/>
        <text x="77" y="45" font-size="10" fill="#5E81F4">r</text>
      </svg>
    `;
  }
  
  if (normalizedTopic.includes('graph') || normalizedTopic.includes('function') || normalizedTopic.includes('equation')) {
    return `
      <svg width="120" height="100" viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="graphGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#57D2A9;stop-opacity:0.8" />
            <stop offset="100%" style="stop-color:#5E81F4;stop-opacity:0.8" />
          </linearGradient>
        </defs>
        <!-- Axes -->
        <line x1="20" y1="80" x2="100" y2="80" stroke="#666" stroke-width="1"/>
        <line x1="20" y1="80" x2="20" y2="20" stroke="#666" stroke-width="1"/>
        <!-- Curve -->
        <path d="M20,75 Q40,45 60,50 T100,30" stroke="url(#graphGrad)" stroke-width="3" fill="none"/>
        <!-- Points -->
        <circle cx="20" cy="75" r="2" fill="#5E81F4"/>
        <circle cx="60" cy="50" r="2" fill="#57D2A9"/>
        <circle cx="100" cy="30" r="2" fill="#9E7BF5"/>
      </svg>
    `;
  }
  
  // Default mathematical concept
  return `
    <svg width="120" height="100" viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="defaultMathGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#5E81F4;stop-opacity:0.6" />
          <stop offset="100%" style="stop-color:#9E7BF5;stop-opacity:0.8" />
        </linearGradient>
      </defs>
      <rect x="10" y="10" width="100" height="80" rx="10" fill="url(#defaultMathGrad)" stroke="#5E81F4" stroke-width="2"/>
      <text x="60" y="45" text-anchor="middle" font-size="24" fill="white" font-weight="bold">∑</text>
      <text x="60" y="65" text-anchor="middle" font-size="10" fill="white">Math</text>
    </svg>
  `;
}

/**
 * Generate SVG for physics concepts
 * @param {string} topic - The physics topic
 * @returns {string} - SVG string
 */
function generatePhysicsSVG(topic) {
  const normalizedTopic = topic.toLowerCase();
  
  if (normalizedTopic.includes('force') || normalizedTopic.includes('newton')) {
    return `
      <svg width="120" height="100" viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="forceGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#57D2A9;stop-opacity:0.8" />
            <stop offset="100%" style="stop-color:#5E81F4;stop-opacity:0.8" />
          </linearGradient>
        </defs>
        <!-- Block -->
        <rect x="40" y="60" width="40" height="25" fill="url(#forceGrad)" stroke="#5E81F4" stroke-width="2" rx="3"/>
        <!-- Force arrow -->
        <line x1="85" y1="72" x2="105" y2="72" stroke="#57D2A9" stroke-width="3" marker-end="url(#arrowhead)"/>
        <defs>
          <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#57D2A9"/>
          </marker>
        </defs>
        <text x="93" y="67" text-anchor="middle" font-size="10" fill="#57D2A9">F</text>
        <text x="60" y="80" text-anchor="middle" font-size="8" fill="#5E81F4">m</text>
      </svg>
    `;
  }
  
  if (normalizedTopic.includes('wave') || normalizedTopic.includes('frequency')) {
    return `
      <svg width="120" height="100" viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="waveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#9E7BF5;stop-opacity:0.8" />
            <stop offset="50%" style="stop-color:#5E81F4;stop-opacity:0.6" />
            <stop offset="100%" style="stop-color:#57D2A9;stop-opacity:0.8" />
          </linearGradient>
        </defs>
        <!-- Wave -->
        <path d="M10,50 Q25,25 40,50 T70,50 T100,50" stroke="url(#waveGrad)" stroke-width="3" fill="none"/>
        <!-- Amplitude lines -->
        <line x1="10" y1="25" x2="100" y2="25" stroke="#9E7BF5" stroke-width="1" opacity="0.5" stroke-dasharray="2,2"/>
        <line x1="10" y1="75" x2="100" y2="75" stroke="#9E7BF5" stroke-width="1" opacity="0.5" stroke-dasharray="2,2"/>
        <text x="105" y="30" font-size="8" fill="#9E7BF5">+A</text>
        <text x="105" y="80" font-size="8" fill="#9E7BF5">-A</text>
      </svg>
    `;
  }
  
  // Default physics concept
  return `
    <svg width="120" height="100" viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="defaultPhysicsGrad" cx="50%" cy="50%" r="50%">
          <stop offset="0%" style="stop-color:#57D2A9;stop-opacity:0.6" />
          <stop offset="100%" style="stop-color:#5E81F4;stop-opacity:0.8" />
        </radialGradient>
      </defs>
      <circle cx="60" cy="50" r="40" fill="url(#defaultPhysicsGrad)" stroke="#5E81F4" stroke-width="2"/>
      <text x="60" y="45" text-anchor="middle" font-size="20" fill="white" font-weight="bold">⚡</text>
      <text x="60" y="65" text-anchor="middle" font-size="10" fill="white">Physics</text>
    </svg>
  `;
}

/**
 * Generate SVG for chemistry concepts
 * @param {string} topic - The chemistry topic
 * @returns {string} - SVG string
 */
function generateChemistrySVG(topic) {
  const normalizedTopic = topic.toLowerCase();
  
  if (normalizedTopic.includes('molecule') || normalizedTopic.includes('bond') || normalizedTopic.includes('atom')) {
    return `
      <svg width="120" height="100" viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <radialGradient id="atomGrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" style="stop-color:#57D2A9;stop-opacity:0.8" />
            <stop offset="100%" style="stop-color:#57D2A9;stop-opacity:0.6" />
          </radialGradient>
        </defs>
        <!-- Atoms -->
        <circle cx="40" cy="40" r="12" fill="url(#atomGrad)" stroke="#57D2A9" stroke-width="2"/>
        <circle cx="80" cy="40" r="12" fill="url(#atomGrad)" stroke="#57D2A9" stroke-width="2"/>
        <circle cx="60" cy="70" r="12" fill="url(#atomGrad)" stroke="#57D2A9" stroke-width="2"/>
        <!-- Bonds -->
        <line x1="52" y1="40" x2="68" y2="40" stroke="#5E81F4" stroke-width="2"/>
        <line x1="48" y1="52" x2="64" y2="62" stroke="#5E81F4" stroke-width="2"/>
        <line x1="72" y1="52" x2="66" y2="62" stroke="#5E81F4" stroke-width="2"/>
        <!-- Labels -->
        <text x="40" y="45" text-anchor="middle" font-size="8" fill="white" font-weight="bold">C</text>
        <text x="80" y="45" text-anchor="middle" font-size="8" fill="white" font-weight="bold">O</text>
        <text x="60" y="75" text-anchor="middle" font-size="8" fill="white" font-weight="bold">H</text>
      </svg>
    `;
  }
  
  // Default chemistry concept
  return `
    <svg width="120" height="100" viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="defaultChemGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#57D2A9;stop-opacity:0.6" />
          <stop offset="100%" style="stop-color:#9E7BF5;stop-opacity:0.8" />
        </linearGradient>
      </defs>
      <circle cx="60" cy="50" r="40" fill="url(#defaultChemGrad)" stroke="#57D2A9" stroke-width="2"/>
      <text x="60" y="45" text-anchor="middle" font-size="20" fill="white" font-weight="bold">🧪</text>
      <text x="60" y="65" text-anchor="middle" font-size="10" fill="white">Chemistry</text>
    </svg>
  `;
}

/**
 * Generate concept visualization SVG
 * @param {string} topic - The topic/concept to visualize
 * @param {string} subject - The subject area (math, physics, chemistry, etc.)
 * @returns {string} - SVG string
 */
export function generateConceptSVG(topic, subject = 'general') {
  if (!topic) {
    return generateDefaultSVG();
  }
  
  const normalizedSubject = subject.toLowerCase();
  const normalizedTopic = topic.toLowerCase();
  
  // Determine subject if not provided
  let detectedSubject = normalizedSubject;
  if (normalizedSubject === 'general') {
    if (normalizedTopic.includes('math') || normalizedTopic.includes('algebra') || 
        normalizedTopic.includes('calculus') || normalizedTopic.includes('geometry')) {
      detectedSubject = 'mathematics';
    } else if (normalizedTopic.includes('physics') || normalizedTopic.includes('force') || 
               normalizedTopic.includes('energy') || normalizedTopic.includes('wave')) {
      detectedSubject = 'physics';
    } else if (normalizedTopic.includes('chemistry') || normalizedTopic.includes('chemical') || 
               normalizedTopic.includes('molecule') || normalizedTopic.includes('atom')) {
      detectedSubject = 'chemistry';
    }
  }
  
  // Generate subject-specific SVG
  switch (detectedSubject) {
    case 'mathematics':
    case 'math':
      return generateMathSVG(topic);
    case 'physics':
      return generatePhysicsSVG(topic);
    case 'chemistry':
      return generateChemistrySVG(topic);
    default:
      return generateDefaultSVG(topic);
  }
}

/**
 * Generate default concept SVG
 * @param {string} topic - Optional topic for generic visualization
 * @returns {string} - SVG string
 */
function generateDefaultSVG(topic = '') {
  return `
    <svg width="120" height="100" viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="defaultGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#9E7BF5;stop-opacity:0.6" />
          <stop offset="50%" style="stop-color:#5E81F4;stop-opacity:0.7" />
          <stop offset="100%" style="stop-color:#57D2A9;stop-opacity:0.8" />
        </linearGradient>
      </defs>
      <rect x="10" y="10" width="100" height="80" rx="15" fill="url(#defaultGrad)" stroke="#5E81F4" stroke-width="2"/>
      <circle cx="35" cy="35" r="8" fill="white" opacity="0.8"/>
      <circle cx="85" cy="35" r="8" fill="white" opacity="0.8"/>
      <circle cx="60" cy="65" r="8" fill="white" opacity="0.8"/>
      <line x1="35" y1="43" x2="60" y2="57" stroke="white" stroke-width="2" opacity="0.8"/>
      <line x1="85" y1="43" x2="60" y2="57" stroke="white" stroke-width="2" opacity="0.8"/>
      <text x="60" y="90" text-anchor="middle" font-size="10" fill="#5E81F4">Concept</text>
    </svg>
  `;
}

/**
 * Get fallback Gemini image generation prompt
 * @param {string} topic - The topic to visualize
 * @param {string} subject - The subject area
 * @returns {string} - Gemini prompt for image generation
 */
export function getGeminiPrompt(topic, subject = 'general') {
  return `Create a clean, minimal, educational illustration of ${topic} in ${subject}. 
  Style: Simple line art, soft colors, suitable for student learning. 
  No text labels, focus on visual concept clarity. 
  Educational diagram style, similar to textbook illustrations.`;
}

// Build a dynamic scene based on semantic visual context, not theme keywords
export function buildSceneFromContext(visualContext, subject = 'general', palette = {}) {
  // Chemistry: Bond formation and energy change
  const buildChemistryScene = () => ({
    // Explanatory, not decorative: shows atoms bonding and energy change
    type: 'story_scene',
    generated: true,
    subject,
    scene_json: {
      canvas: { width: 480, height: 270, background: '#fffefa' },
      palette,
      elements: [
        { id: 'axis_energy', type: 'label', x: 20, y: 28, text: 'Energy' },
        { id: 'a_atom', type: 'circle', cx: 120, cy: 150, r: 24, fill: '#E0F2FE', stroke: '#60A5FA' },
        { id: 'a_label', type: 'label', x: 114, y: 153, text: 'A' },
        { id: 'b_atom', type: 'circle', cx: 360, cy: 150, r: 24, fill: '#FEE2E2', stroke: '#F87171' },
        { id: 'b_label', type: 'label', x: 354, y: 153, text: 'B' },
        { id: 'bond_arrow', type: 'arrow', from: [144,150], to: [336,150], color: (palette.saffron || '#FF9933') },
        { id: 'energy_down', type: 'arrow', from: [240, 70], to: [240, 110], color: (palette.green || '#138808') },
        { id: 'molecule', type: 'motion', points: [[200,150],[220,150],[240,150],[260,150],[280,150]], color: '#6EE7B7' },
        { id: 'bond_label', type: 'label', x: 210, y: 170, text: 'Bond forms (A–B)' }
      ]
    },
    neuro_symbolic_map: [
      { concept: 'atoms', symbol: 'circles', element_id: 'a_atom' },
      { concept: 'bond', symbol: 'arrow', element_id: 'bond_arrow' },
      { concept: 'energy_change', symbol: 'arrow_down', element_id: 'energy_down' }
    ],
    caption_text: 'Atoms A and B approach, bond forms, and energy decreases as a stable molecule forms.',
    interaction_flow: [
      { id: 'c1', highlight: ['a_atom','b_atom'], caption: 'Separate atoms A and B.' },
      { id: 'c2', highlight: ['bond_arrow'], caption: 'Attractive forces pull atoms together.' },
      { id: 'c3', highlight: ['energy_down','molecule','bond_label'], caption: 'Bond forms; energy drops to a stable state.' }
    ],
    interactivity: { tap_to_frame: [ { elementId: 'a_atom', goto: 'c2' }, { elementId: 'b_atom', goto: 'c2' } ], show_reset: true },
    preview_svg: generateConceptSVG('bond', 'chemistry')
  });

  // History: Timeline of events with cause-effect arrows
  const buildHistoryScene = () => ({
    type: 'story_scene',
    generated: true,
    subject,
    scene_json: {
      canvas: { width: 480, height: 270, background: '#ffffff' },
      palette,
      elements: [
        { id: 'timeline', type: 'rect', x: 60, y: 140, w: 360, h: 2, fill: '#9CA3AF' },
        { id: 'e1', type: 'circle', cx: 100, cy: 140, r: 6, fill: (palette.saffron || '#FF9933') },
        { id: 'e1_t', type: 'label', x: 80, y: 120, text: 'Causes' },
        { id: 'e2', type: 'circle', cx: 200, cy: 140, r: 6, fill: (palette.green || '#138808') },
        { id: 'e2_t', type: 'label', x: 180, y: 120, text: 'Turning Point' },
        { id: 'e3', type: 'circle', cx: 300, cy: 140, r: 6, fill: (palette.gold || '#FFD700') },
        { id: 'e3_t', type: 'label', x: 280, y: 120, text: 'Aftermath' },
        { id: 'e4', type: 'circle', cx: 380, cy: 140, r: 6, fill: '#60A5FA' },
        { id: 'e4_t', type: 'label', x: 360, y: 120, text: 'Outcome' },
        { id: 'arrow12', type: 'arrow', from: [106,140], to: [194,140], color: '#6B7280' },
        { id: 'arrow23', type: 'arrow', from: [206,140], to: [294,140], color: '#6B7280' },
        { id: 'arrow34', type: 'arrow', from: [306,140], to: [374,140], color: '#6B7280' },
        { id: 'cause', type: 'label', x: 60, y: 200, text: 'Cause → Effect over time' }
      ]
    },
    neuro_symbolic_map: [
      { concept: 'timeline', symbol: 'line', element_id: 'timeline' },
      { concept: 'events', symbol: 'nodes', element_id: 'e2' },
      { concept: 'causality', symbol: 'arrows', element_id: 'arrow23' }
    ],
    caption_text: 'Events unfold along a timeline; arrows show cause and effect leading to outcomes.',
    interaction_flow: [
      { id: 'h1', highlight: ['e1','arrow12'], caption: 'Event 1 triggers the sequence.' },
      { id: 'h2', highlight: ['e2','arrow23'], caption: 'Event 2 continues the cause-effect chain.' },
      { id: 'h3', highlight: ['e3','arrow34','e4'], caption: 'Events culminate in an outcome.' }
    ],
    interactivity: { tap_to_frame: [ { elementId: 'e1', goto: 'h1' }, { elementId: 'e2', goto: 'h2' }, { elementId: 'e3', goto: 'h3' } ], show_reset: true },
    preview_svg: generateConceptSVG('timeline', 'history')
  });

  // Probability/Expectation: dynamic bars + simple trial slider
  const buildProbabilityScene = () => ({
    type: 'story_scene',
    generated: true,
    subject,
    scene_json: {
      canvas: { width: 480, height: 270, background: '#ffffff' },
      palette,
      elements: [
        { id: 'title', type: 'label', x: 40, y: 36, text: 'Probability (Heads vs Tails)' },
        { id: 'bar_heads_bg', type: 'rect', x: 40, y: 80, w: 400, h: 18, fill: '#F3F4F6', stroke: '#E5E7EB' },
        { id: 'bar_tails_bg', type: 'rect', x: 40, y: 120, w: 400, h: 18, fill: '#F3F4F6', stroke: '#E5E7EB' },
        { id: 'bar_heads', type: 'rect', x: 40, y: 80, w: 200, h: 18, fill: (palette.saffron || '#FF9933'), bindWidth: { sliderId: 'k', from: 0, to: 400 } },
        { id: 'bar_tails', type: 'rect', x: 40, y: 120, w: 200, h: 18, fill: (palette.green || '#138808'), bindWidth: { sliderId: 'k', from: 400, to: 0 } },
        { id: 'k', type: 'slider', x: 40, y: 160, w: 400, min: 0, max: 100, step: 1, value: 50, ariaLabel: 'percent heads' },
        { id: 'p_text', type: 'label', x: 40, y: 200, text: 'P(Heads) ≈ 50%' }
      ]
    },
    neuro_symbolic_map: [
      { concept: 'probability', symbol: 'bars', element_id: 'bar_heads' },
      { concept: 'complement', symbol: 'bars', element_id: 'bar_tails' }
    ],
    caption_text: 'Adjust trials to see changing proportions; expectation centers near 50% for a fair coin.',
    interaction_flow: [
      { id: 'p1', highlight: ['bar_heads'], caption: 'Heads proportion increases.' },
      { id: 'p2', highlight: ['bar_tails'], caption: 'Tails proportion decreases accordingly.' }
    ],
    interactivity: { 
      show_reset: true,
      slider_bind: { bindings: [ { sliderId: 'k', targets: [ { elementId: 'p_text', template: 'P(Heads) ≈ {k}%' } ] } ] }
    },
    preview_svg: generateConceptSVG('probability', 'math')
  });
  const buildIntegrationScene = () => ({
    type: 'story_scene',
    generated: true,
    subject,
    scene_json: {
      canvas: { width: 480, height: 270, background: '#fffefa' },
      palette,
      elements: [
        { id: 'axis_x', type: 'rect', x: 40, y: 200, w: 400, h: 1, fill: '#D1D5DB' },
        { id: 'axis_y', type: 'rect', x: 40, y: 60, w: 1, h: 140, fill: '#D1D5DB' },
        { id: 'cos_wave', type: 'motion', points: [[40,200],[80,160],[120,140],[160,150],[200,175],[240,200],[280,225],[320,240],[360,235],[400,210],[440,200]], color: (palette.saffron || '#FF9933') },
        { id: 'area_fill', type: 'rect', x: 40, y: 160, w: 0, h: 40, fill: (palette.gold || '#FFD700'), stroke: (palette.gold || '#FFD700'), bindWidth: { sliderId: 't', from: 0, to: 400 } },
        { id: 'sin_wave', type: 'motion', points: [[40,200],[80,220],[120,240],[160,250],[200,245],[240,230],[280,200],[320,170],[360,155],[400,160],[440,180]], color: (palette.green || '#138808') },
        { id: 't', type: 'slider', x: 40, y: 220, w: 400, min: 0, max: 400, step: 10, value: 0, ariaLabel: 'integration limit' },
        { id: 'area_value', type: 'label', x: 40, y: 250, text: 'Current Area: 0.00' }
      ]
    },
    neuro_symbolic_map: [
      { concept: 'integrand', symbol: 'wave', element_id: 'cos_wave' },
      { concept: 'accumulation', symbol: 'area', element_id: 'area_fill' },
      { concept: 'antiderivative', symbol: 'wave', element_id: 'sin_wave' }
    ],
    caption_text: 'Integration as accumulation: area fills under the curve; sin emerges from cos.',
    interaction_flow: [
      { id: 'i1', highlight: ['cos_wave'], caption: 'cos(x) curve appears.' },
      { id: 'i2', highlight: ['area_fill'], caption: 'Area fills under the curve (accumulation).' },
      { id: 'i3', highlight: ['sin_wave'], caption: 'sin(x) emerges as antiderivative.' }
    ],
    interactivity: { type: 'slider_bind', slider_bind: { bindings: [{ sliderId: 't', targets: [{ elementId: 'area_value', template: 'Current Area: {sin(t)}' }] }] } },
    preview_svg: generateConceptSVG('integration', 'math')
  });

  const buildQuadraticScene = () => ({
    type: 'story_scene',
    generated: true,
    subject,
    scene_json: {
      canvas: { width: 480, height: 270, background: '#fffefa' },
      palette,
      elements: [
        { id: 'ground', type: 'rect', x: 40, y: 210, w: 400, h: 2, fill: '#D1D5DB' },
        { id: 'launch', type: 'icon', x: 40, y: 210, icon: '🎯' },
        { id: 'path', type: 'motion', points: [[40,210],[90,180],[140,160],[190,150],[240,152],[290,165],[340,190],[390,210],[440,220]], color: (palette.saffron || '#FF9933') },
        { id: 'ball', type: 'circle', cx: 40, cy: 210, r: 7, fill: '#FF5252' },
        { id: 'gravity', type: 'arrow', from: [90,170], to: [90,200], color: (palette.green || '#138808') }
      ]
    },
    neuro_symbolic_map: [
      { concept: 'trajectory', symbol: 'parabola', element_id: 'path' },
      { concept: 'gravity', symbol: 'arrow', element_id: 'gravity' }
    ],
    caption_text: 'Quadratic behavior as parabolic motion: a projectile path under gravity.',
    interaction_flow: [
      { id: 'q1', highlight: ['launch','ball'], caption: 'Launch point set.' },
      { id: 'q2', highlight: ['path'], caption: 'Projectile follows a parabolic path.' },
      { id: 'q3', highlight: ['gravity'], caption: 'Gravity pulls downward; path bends.' }
    ],
    preview_svg: generateConceptSVG('parabola', 'math')
  });

  const buildNewtonScene = () => ({
    type: 'story_scene',
    generated: true,
    subject,
    scene_json: {
      canvas: { width: 480, height: 270, background: palette.deepBlue ? palette.deepBlue : '#ffffff' },
      palette,
      elements: [
        { id: 'ball', type: 'circle', cx: 120, cy: 150, r: 6, fill: '#ff5252', label: 'Ball' },
        { id: 'force_arrow', type: 'arrow', from: [120, 150], to: [330, 150], color: (palette.saffron || '#FF9933'), label: 'Force' },
        { id: 'inertia_lines', type: 'motion', points: [[135,150],[150,150],[165,150]], color: (palette.green || '#138808'), label: 'Inertia' },
        { id: 'reaction_arc', type: 'arc', c: [360,150], r: 40, a0: -1.4, a1: -0.2, color: (palette.green || '#138808'), label: 'Action-Reaction' },
        { id: 'n1', type: 'label', x: 60, y: 40, text: 'N1: Inertia' },
        { id: 'n2', type: 'label', x: 180, y: 40, text: 'N2: F = m·a' },
        { id: 'n3', type: 'label', x: 320, y: 40, text: 'N3: Action = -Reaction' }
      ]
    },
    neuro_symbolic_map: [
      { concept: 'force', symbol: 'arrow', element_id: 'force_arrow' },
      { concept: 'inertia', symbol: 'motion-lines', element_id: 'inertia_lines' },
      { concept: 'action_reaction', symbol: 'arc', element_id: 'reaction_arc' }
    ],
    caption_text: 'Motion dynamics: inertia, applied force, and reaction illustrated.',
    interaction_flow: [
      { id: 'n1f', highlight: ['ball','inertia_lines'], caption: 'N1: State persists unless acted upon.' },
      { id: 'n2f', highlight: ['force_arrow'], caption: 'N2: Acceleration proportional to force.' },
      { id: 'n3f', highlight: ['reaction_arc'], caption: 'N3: Equal and opposite reaction.' }
    ],
    preview_svg: generateConceptSVG('force', 'physics')
  });

  const buildRelationScene = () => ({
    type: 'story_scene',
    generated: true,
    subject,
    scene_json: {
      canvas: { width: 480, height: 270, background: palette.deepBlue ? palette.deepBlue : '#ffffff' },
      palette,
      elements: [
        { id: 'rangoli', type: 'pattern', x: 100, y: 60, w: 280, h: 160, style: 'rangoli', label: 'Relations' },
        { id: 'center_dot', type: 'circle', cx: 240, cy: 140, r: 6, fill: (palette.gold || '#FFD700') },
        { id: 'inner_ring', type: 'circle', cx: 240, cy: 140, r: 16, fill: 'none', stroke: (palette.green || '#138808') },
        { id: 'outer_ring', type: 'circle', cx: 240, cy: 140, r: 24, fill: 'none', stroke: (palette.saffron || '#FF9933') },
        { id: 'p1', type: 'circle', cx: 240, cy: 100, r: 10, fill: (palette.saffron || '#FF9933') },
        { id: 'p2', type: 'circle', cx: 277, cy: 112, r: 10, fill: (palette.green || '#138808') },
        { id: 'p3', type: 'circle', cx: 289, cy: 149, r: 10, fill: (palette.saffron || '#FF9933') },
        { id: 'p4', type: 'circle', cx: 277, cy: 186, r: 10, fill: (palette.green || '#138808') },
        { id: 'concept', type: 'label', x: 120, y: 230, text: 'Concept relations like rangoli patterns' }
      ]
    },
    neuro_symbolic_map: [ { concept: 'relations', symbol: 'pattern', element_id: 'rangoli' } ],
    caption_text: 'Concept structure: interlinked motifs represent relationships.',
    interaction_flow: [ { id: 'r0', highlight: ['center_dot','inner_ring','outer_ring'], caption: 'Center and rings form.' } ],
    preview_svg: generateConceptSVG('relations', subject)
  });

  // English: Composition flow (intro → body → conclusion)
  const buildCompositionScene = () => ({
    type: 'story_scene',
    generated: true,
    subject,
    scene_json: {
      canvas: { width: 480, height: 270, background: '#fffefa' },
      palette,
      elements: [
        { id: 'title', type: 'label', x: 40, y: 40, text: 'Essay Structure' },
        { id: 'intro', type: 'rect', x: 40, y: 80, w: 120, h: 40, fill: '#FFFFFF', stroke: '#9CA3AF' },
        { id: 'intro_t', type: 'label', x: 50, y: 105, text: 'Introduction' },
        { id: 'body', type: 'rect', x: 200, y: 80, w: 120, h: 40, fill: '#FFFFFF', stroke: '#9CA3AF' },
        { id: 'body_t', type: 'label', x: 220, y: 105, text: 'Body' },
        { id: 'concl', type: 'rect', x: 360, y: 80, w: 120, h: 40, fill: '#FFFFFF', stroke: '#9CA3AF' },
        { id: 'concl_t', type: 'label', x: 370, y: 105, text: 'Conclusion' },
        { id: 'flow1', type: 'arrow', from: [160, 100], to: [200, 100], color: (palette.saffron || '#FF9933') },
        { id: 'flow2', type: 'arrow', from: [320, 100], to: [360, 100], color: (palette.saffron || '#FF9933') },
        { id: 'hooks', type: 'label', x: 40, y: 140, text: 'Hook → Thesis → Topic → Evidence → Closing' }
      ]
    },
    neuro_symbolic_map: [
      { concept: 'introduction', symbol: 'box', element_id: 'intro' },
      { concept: 'body', symbol: 'box', element_id: 'body' },
      { concept: 'conclusion', symbol: 'box', element_id: 'concl' }
    ],
    caption_text: 'Composition flow: introduction → body → conclusion with logical progression.',
    interaction_flow: [
      { id: 'e1', highlight: ['intro','flow1'], caption: 'Start with a hook and thesis.' },
      { id: 'e2', highlight: ['body','flow2'], caption: 'Develop topic sentences with evidence.' },
      { id: 'e3', highlight: ['concl'], caption: 'Summarize and close.' }
    ],
    interactivity: { show_reset: true },
    animation: { autoAdvance: true, intervalMs: 1400 },
    preview_svg: generateConceptSVG('essay', subject)
  });

  // Geology: Rock cycle (igneous → sedimentary → metamorphic → igneous)
  const buildRockCycleScene = () => ({
    type: 'story_scene',
    generated: true,
    subject,
    scene_json: {
      canvas: { width: 480, height: 270, background: '#fffefa' },
      palette,
      elements: [
        { id: 'igneous', type: 'rect', x: 60, y: 100, w: 90, h: 40, fill: '#FFFFFF', stroke: '#9CA3AF' },
        { id: 'igneous_t', type: 'label', x: 68, y: 125, text: 'Igneous' },
        { id: 'sed', type: 'rect', x: 200, y: 60, w: 110, h: 40, fill: '#FFFFFF', stroke: '#9CA3AF' },
        { id: 'sed_t', type: 'label', x: 210, y: 85, text: 'Sedimentary' },
        { id: 'meta', type: 'rect', x: 200, y: 140, w: 110, h: 40, fill: '#FFFFFF', stroke: '#9CA3AF' },
        { id: 'meta_t', type: 'label', x: 210, y: 165, text: 'Metamorphic' },
        { id: 'cycle1', type: 'arrow', from: [150, 120], to: [200, 80], color: (palette.green || '#138808') },
        { id: 'cycle2', type: 'arrow', from: [310, 80], to: [310, 160], color: (palette.green || '#138808') },
        { id: 'cycle3', type: 'arrow', from: [200, 160], to: [150, 120], color: (palette.green || '#138808') }
      ]
    },
    neuro_symbolic_map: [
      { concept: 'igneous', symbol: 'box', element_id: 'igneous' },
      { concept: 'sedimentary', symbol: 'box', element_id: 'sed' },
      { concept: 'metamorphic', symbol: 'box', element_id: 'meta' }
    ],
    caption_text: 'Rock cycle: igneous → sedimentary → metamorphic → back again.',
    interaction_flow: [
      { id: 'g1', highlight: ['igneous','cycle1'], caption: 'Weathering/erosion moves material.' },
      { id: 'g2', highlight: ['sed','cycle2'], caption: 'Heat/pressure transform sediments.' },
      { id: 'g3', highlight: ['meta','cycle3'], caption: 'Melting/cooling returns to igneous.' }
    ],
    interactivity: { show_reset: true },
    animation: { autoAdvance: true, intervalMs: 1400 },
    preview_svg: generateConceptSVG('rock cycle', subject)
  });

  // English: Grammar tree (Sentence → Clause → Phrase)
  const buildGrammarTreeScene = () => ({
    type: 'story_scene',
    generated: true,
    subject,
    scene_json: {
      canvas: { width: 480, height: 270, background: '#fffefa' },
      palette,
      elements: [
        { id: 'sent', type: 'rect', x: 190, y: 50, w: 100, h: 32, fill: '#FFFFFF', stroke: '#9CA3AF' },
        { id: 'sent_t', type: 'label', x: 200, y: 70, text: 'Sentence' },
        { id: 's_to_c', type: 'arrow', from: [240, 82], to: [240, 110], color: (palette.saffron || '#FF9933') },
        { id: 'clause', type: 'rect', x: 160, y: 110, w: 160, h: 32, fill: '#FFFFFF', stroke: '#9CA3AF' },
        { id: 'clause_t', type: 'label', x: 170, y: 130, text: 'Independent Clause' },
        { id: 'c_to_p1', type: 'arrow', from: [200, 142], to: [140, 170], color: (palette.green || '#138808') },
        { id: 'c_to_p2', type: 'arrow', from: [280, 142], to: [340, 170], color: (palette.green || '#138808') },
        { id: 'phrase1', type: 'rect', x: 100, y: 170, w: 120, h: 32, fill: '#FFFFFF', stroke: '#9CA3AF' },
        { id: 'phrase1_t', type: 'label', x: 110, y: 190, text: 'Noun Phrase' },
        { id: 'phrase2', type: 'rect', x: 320, y: 170, w: 120, h: 32, fill: '#FFFFFF', stroke: '#9CA3AF' },
        { id: 'phrase2_t', type: 'label', x: 330, y: 190, text: 'Verb Phrase' }
      ]
    },
    neuro_symbolic_map: [
      { concept: 'sentence', symbol: 'box', element_id: 'sent' },
      { concept: 'clause', symbol: 'box', element_id: 'clause' },
      { concept: 'phrase', symbol: 'box', element_id: 'phrase1' }
    ],
    caption_text: 'Grammar tree: a sentence contains a clause, which expands into phrases.',
    interaction_flow: [
      { id: 'gr1', highlight: ['sent','s_to_c'], caption: 'Start with the full sentence.' },
      { id: 'gr2', highlight: ['clause'], caption: 'Identify the main clause.' },
      { id: 'gr3', highlight: ['phrase1','phrase2'], caption: 'See how phrases fill roles.' }
    ],
    interactivity: { show_reset: true },
    animation: { autoAdvance: true, intervalMs: 1400 },
    preview_svg: generateConceptSVG('grammar', subject)
  });

  // Geology: Plate tectonics (divergent / convergent / transform boundaries)
  const buildPlateTectonicsScene = () => ({
    type: 'story_scene',
    generated: true,
    subject,
    scene_json: {
      canvas: { width: 480, height: 270, background: '#fffefa' },
      palette,
      elements: [
        // Divergent: arrows away
        { id: 'div_left', type: 'rect', x: 80, y: 120, w: 80, h: 20, fill: '#FFFFFF', stroke: '#9CA3AF' },
        { id: 'div_right', type: 'rect', x: 180, y: 120, w: 80, h: 20, fill: '#FFFFFF', stroke: '#9CA3AF' },
        { id: 'div_ar_l', type: 'arrow', from: [120, 110], to: [100, 110], color: (palette.green || '#138808') },
        { id: 'div_ar_r', type: 'arrow', from: [220, 110], to: [240, 110], color: (palette.green || '#138808') },
        { id: 'div_t', type: 'label', x: 120, y: 150, text: 'Divergent' },
        // Convergent: arrows toward
        { id: 'conv_left', type: 'rect', x: 280, y: 120, w: 80, h: 20, fill: '#FFFFFF', stroke: '#9CA3AF' },
        { id: 'conv_right', type: 'rect', x: 380, y: 120, w: 80, h: 20, fill: '#FFFFFF', stroke: '#9CA3AF' },
        { id: 'conv_ar_l', type: 'arrow', from: [320, 110], to: [340, 110], color: (palette.saffron || '#FF9933') },
        { id: 'conv_ar_r', type: 'arrow', from: [420, 110], to: [400, 110], color: (palette.saffron || '#FF9933') },
        { id: 'conv_t', type: 'label', x: 320, y: 150, text: 'Convergent' },
        // Transform: parallel, opposite arrows
        { id: 'trans_left', type: 'rect', x: 80, y: 190, w: 80, h: 12, fill: '#FFFFFF', stroke: '#9CA3AF' },
        { id: 'trans_right', type: 'rect', x: 180, y: 190, w: 80, h: 12, fill: '#FFFFFF', stroke: '#9CA3AF' },
        { id: 'trans_ar_l', type: 'arrow', from: [120, 180], to: [140, 180], color: '#666' },
        { id: 'trans_ar_r', type: 'arrow', from: [220, 200], to: [200, 200], color: '#666' },
        { id: 'trans_t', type: 'label', x: 120, y: 215, text: 'Transform' }
      ]
    },
    neuro_symbolic_map: [
      { concept: 'divergent', symbol: 'plate', element_id: 'div_left' },
      { concept: 'convergent', symbol: 'plate', element_id: 'conv_left' },
      { concept: 'transform', symbol: 'plate', element_id: 'trans_left' }
    ],
    caption_text: 'Plate tectonics: divergent (apart), convergent (together), transform (side-by-side).',
    interaction_flow: [
      { id: 'pt1', highlight: ['div_left','div_right','div_ar_l','div_ar_r'], caption: 'Divergent boundary: plates move apart.' },
      { id: 'pt2', highlight: ['conv_left','conv_right','conv_ar_l','conv_ar_r'], caption: 'Convergent: plates push together.' },
      { id: 'pt3', highlight: ['trans_left','trans_right','trans_ar_l','trans_ar_r'], caption: 'Transform: plates slide past.' }
    ],
    interactivity: { show_reset: true },
    animation: { autoAdvance: true, intervalMs: 1400 },
    preview_svg: generateConceptSVG('plate tectonics', subject)
  });

  // Earth Science: Water Cycle (Evaporation → Condensation → Precipitation → Collection)
  const buildWaterCycleScene = () => ({
    type: 'story_scene',
    generated: true,
    subject,
    scene_json: {
      canvas: { width: 480, height: 270, background: '#fffefa' },
      palette,
      elements: [
        { id: 'ocean', type: 'rect', x: 40, y: 200, w: 400, h: 40, fill: '#DBEAFE', stroke: '#93C5FD' },
        { id: 'sun', type: 'label', x: 60, y: 40, text: 'Sun ☀' },
        { id: 'evap', type: 'arrow', from: [120, 200], to: [120, 120], color: (palette.saffron || '#FF9933') },
        { id: 'cloud', type: 'circle', cx: 240, cy: 100, r: 18, fill: '#E5E7EB', stroke: '#9CA3AF' },
        { id: 'condense', type: 'label', x: 220, y: 80, text: 'Condensation' },
        { id: 'rain', type: 'arrow', from: [240, 118], to: [240, 180], color: (palette.green || '#138808') },
        { id: 'river', type: 'motion', points: [[300,210],[330,205],[360,208],[390,212],[420,210]], color: '#60A5FA' },
        { id: 'labels', type: 'label', x: 80, y: 240, text: 'Evaporation → Condensation → Precipitation → Collection' }
      ]
    },
    neuro_symbolic_map: [
      { concept: 'evaporation', symbol: 'arrow', element_id: 'evap' },
      { concept: 'condensation', symbol: 'cloud', element_id: 'cloud' },
      { concept: 'precipitation', symbol: 'arrow', element_id: 'rain' },
      { concept: 'collection', symbol: 'river', element_id: 'river' }
    ],
    caption_text: 'Water cycle: sun drives evaporation, clouds form, rain falls, water collects and flows back.',
    interaction_flow: [
      { id: 'w1', highlight: ['sun','evap'], caption: 'Sun heats water; evaporation.' },
      { id: 'w2', highlight: ['cloud','condense'], caption: 'Vapor cools; condensation forms clouds.' },
      { id: 'w3', highlight: ['rain'], caption: 'Precipitation returns water to land/ocean.' },
      { id: 'w4', highlight: ['river'], caption: 'Collection and flow complete the cycle.' }
    ],
    interactivity: { tap_to_frame: [ { elementId: 'sun', goto: 'w1' }, { elementId: 'cloud', goto: 'w2' }, { elementId: 'rain', goto: 'w3' } ], show_reset: true },
    preview_svg: generateConceptSVG('water_cycle', 'earth_science')
  });

  switch (visualContext) {
    case 'accumulation_process':
      return buildIntegrationScene();
    case 'parabolic_motion':
      return buildQuadraticScene();
    case 'motion_dynamics':
      return buildNewtonScene();
    case 'composition_flow':
      return buildCompositionScene();
    case 'chemistry_reaction':
      return buildChemistryScene();
    case 'history_timeline':
      return buildHistoryScene();
    case 'probability_sim':
      return buildProbabilityScene();
    case 'grammar_tree':
      return buildGrammarTreeScene();
    case 'rock_cycle':
      return buildRockCycleScene();
    case 'water_cycle':
      return buildWaterCycleScene();
    case 'plate_tectonics':
      return buildPlateTectonicsScene();
    default:
      return buildRelationScene();
  }
}

/**
 * buildSceneFromMetaphor
 * Create a dynamic neuro-symbolic scene description using Indian cultural metaphors.
 * Returns an object that includes scene_json, neuro_symbolic_map, caption_text, interaction_flow,
 * plus a small inline svg preview for backward compatibility consumers.
 */
export function buildSceneFromMetaphor(seedText = '', subject = 'general', opts = {}) {
  // Determine semantic visual context from concept/question, not theme keywords
  const conceptText = String(seedText || '').toLowerCase();
  const getVisualContext = (c) => {
    if (/integration|integrate|area/.test(c)) return 'accumulation_process';
    if (/quadratic|parabola|trajectory|projectile/.test(c)) return 'parabolic_motion';
    if (/newton|force|inertia|motion/.test(c)) return 'motion_dynamics';
    if (/essay|composition|paragraph|summary|thesis|introduction|conclusion/.test(c)) return 'composition_flow';
    if (/chemistry|molecule|atom|bond|reaction|electron|valence|ionic|covalent/.test(c)) return 'chemistry_reaction';
    if (/history|historical|revolt|timeline|war|empire|independence|ancient|medieval|modern/.test(c)) return 'history_timeline';
    if (/probability|expectation|expected value|distribution|random|coin|dice|outcome|likelihood/.test(c)) return 'probability_sim';
    if (/(water cycle|evaporation|condensation|precipitation|collection|water vapor)/.test(c)) return 'water_cycle';
    if (/grammar|sentence|parts of speech|syntax|clause|phrase/.test(c)) return 'grammar_tree';
    if (/plate tectonics|tectonic|convergent|divergent|transform boundary/.test(c)) return 'plate_tectonics';
    if (/geology|rock|igneous|sedimentary|metamorphic|erosion|earthquake|volcano/.test(c)) return 'rock_cycle';
    return 'concept_structure';
  };
  const theme = (opts && opts.theme) || 'cricket'; // Theme only influences palette/accents
  const themePalettes = {
    cricket: { field: '#E8F5E9', sky: '#E0F2FE', saffron: '#FF9933', green: '#138808', gold: '#FFD700' },
    bollywood: { backdrop: '#E3F2FD', stage: '#FFF8E1', navy: '#000080', yellow: '#FFC107', magenta: '#E91E63' },
    cooking: { warm1: '#FFEBD6', warm2: '#FFF5DC', orange: '#FF8A00', yellow: '#FFC107', brown: '#8D6E63' },
    festival: { deepBlue: '#001A4D', saffron: '#FF9933', gold: '#FFD700', green: '#138808' }
  };
  const selectedPalette = themePalettes[theme] || themePalettes.cricket;
  const text = conceptText;
  // Subject-aware biasing: if explicit subject suggests a domain, prefer it
  const subj = String(subject || '').toLowerCase();
  const subjectBiased = (() => {
    if (/chem/.test(subj)) return 'chemistry_reaction';
    if (/history|social/.test(subj)) return 'history_timeline';
    if (/prob|stat|applied math|expect/.test(subj)) return 'probability_sim';
    if (/geo|earth|environment/.test(subj)) return 'water_cycle';
    return null;
  })();
  const context = subjectBiased || getVisualContext(text);
  try {
    const sem = buildSceneFromContext(context, subject, selectedPalette);
    if (sem) return sem;
  } catch {}

  // Simple metaphor routing (extendable): cricket for Newton/force/motion; hotel for quantum
  const isNewton = /newton|force|inertia|motion|law/.test(text);
  const isQuantum = /quantum|orbital|spin|energy|number/.test(text);

  if (isNewton) {
    const scene_json = {
      canvas: { width: 480, height: 270, background: theme === 'festival' ? selectedPalette.deepBlue || '#ffffff' : '#ffffff' },
      palette: selectedPalette,
      elements: [
        { id: 'pitch', type: 'rect', x: 40, y: 60, w: 400, h: 150, fill: (selectedPalette.field || '#e6f7ff'), stroke: '#b3e5fc' },
        { id: 'bowler', type: 'icon', x: 60, y: 140, icon: '🏃', label: 'Bowler' },
        { id: 'ball', type: 'circle', cx: 120, cy: 150, r: 6, fill: '#ff5252', label: 'Ball' },
        { id: 'batsman', type: 'icon', x: 360, y: 140, icon: '🏏', label: 'Batsman' },
        { id: 'force_arrow', type: 'arrow', from: [120, 150], to: [330, 150], color: (selectedPalette.saffron || '#ff7043'), label: 'Force' },
        { id: 'inertia_lines', type: 'motion', points: [[135,150],[150,150],[165,150]], color: '#9ccc65', label: 'Inertia' },
        { id: 'bat_swing', type: 'arc', c: [360,150], r: 40, a0: -1.4, a1: -0.2, color: (selectedPalette.green || '#7e57c2'), label: 'Action-Reaction' },
        { id: 'labels_n1', type: 'label', x: 60, y: 40, text: 'N1: Inertia' },
        { id: 'labels_n2', type: 'label', x: 180, y: 40, text: 'N2: F = m·a' },
        { id: 'labels_n3', type: 'label', x: 320, y: 40, text: 'N3: Action = -Reaction' }
      ]
    };
    // richer theme presets (non-breaking)
    try {
      if (theme === 'bollywood') {
        scene_json.elements.push({ id: 'film_set', type: 'label', x: 70, y: 70, text: '🎬' });
      } else if (theme === 'cooking') {
        scene_json.elements.push({ id: 'cook_pot', type: 'icon', x: 70, y: 70, icon: '🍲' });
      } else if (theme === 'festival') {
        scene_json.elements.push({ id: 'festival_diya', type: 'icon', x: 70, y: 70, icon: '🪔' });
      }
    } catch {}
    // Theme accents (non-breaking, subtle)
    try {
      if (theme === 'cricket') {
        scene_json.elements.push({ id: 'accent_rangoli', type: 'pattern', x: 70, y: 70, w: 60, h: 40, style: 'rangoli', label: 'Accent' });
      } else if (theme === 'bollywood') {
        scene_json.elements.push({ id: 'accent_clapper', type: 'icon', x: 70, y: 70, icon: '🎬', label: 'Set' });
      } else if (theme === 'cooking') {
        scene_json.elements.push({ id: 'accent_spice', type: 'label', x: 70, y: 70, text: '🧂' });
      } else if (theme === 'festival') {
        scene_json.elements.push({ id: 'accent_diya', type: 'icon', x: 70, y: 70, icon: '🪔' });
      }
    } catch {}

    const neuro_symbolic_map = [
      { concept: 'force', symbol: 'arrow', element_id: 'force_arrow' },
      { concept: 'inertia', symbol: 'motion-lines', element_id: 'inertia_lines' },
      { concept: 'action_reaction', symbol: 'arc', element_id: 'bat_swing' }
    ];

    const interaction_flow = [
      { id: 'frame1', highlight: ['ball', 'inertia_lines'], caption: 'N1: Ball stays unless acted upon.' },
      { id: 'frame2', highlight: ['force_arrow'], caption: 'N2: Greater force → greater acceleration.' },
      { id: 'frame3', highlight: ['bat_swing'], caption: 'N3: Bat hits ball; equal-opposite reaction.' }
    ];

    return {
      type: 'story_scene',
      generated: true,
      subject,
      scene_json,
      neuro_symbolic_map,
      caption_text: "Cricket metaphor: ball, force arrows, and bat swing explain Newton's laws visually.",
      interaction_flow,
      // Back-compat small preview svg
      preview_svg: generateConceptSVG('force', 'physics')
    };
  }

  if (isQuantum) {
    const scene_json = {
      canvas: { width: 480, height: 270, background: '#ffffff' },
      palette: selectedPalette,
      elements: [
        { id: 'hotel', type: 'rect', x: 60, y: 40, w: 360, h: 190, fill: '#fff8e1', stroke: '#ffe082', label: 'Hotel' },
        { id: 'floor1', type: 'label', x: 70, y: 210, text: 'n=1 (Ground floor)' },
        { id: 'floor2', type: 'label', x: 70, y: 170, text: 'n=2' },
        { id: 'floor3', type: 'label', x: 70, y: 130, text: 'n=3' },
        { id: 'rooms', type: 'grid', x: 120, y: 70, rows: 3, cols: 4, cell: [60, 40], label: 'Orbitals' },
        { id: 'spin', type: 'icon', x: 360, y: 80, icon: '🛏️', label: 'Spin (bed)' }
      ]
    };
    try {
      if (theme === 'festival') scene_json.elements.push({ id: 'hotel_diya', type: 'icon', x: 420, y: 60, icon: '🪔' });
      if (theme === 'bollywood') scene_json.elements.push({ id: 'hotel_camera', type: 'icon', x: 420, y: 60, icon: '🎥' });
      if (theme === 'cooking') scene_json.elements.push({ id: 'hotel_spice', type: 'label', x: 420, y: 60, text: '🧂' });
    } catch {}
    try {
      if (theme === 'festival') {
        scene_json.elements.push({ id: 'hotel_diya', type: 'icon', x: 420, y: 60, icon: '🪔' });
      } else if (theme === 'bollywood') {
        scene_json.elements.push({ id: 'hotel_camera', type: 'icon', x: 420, y: 60, icon: '🎥' });
      }
    } catch {}

    const neuro_symbolic_map = [
      { concept: 'principal_quantum_number', symbol: 'floor', element_id: 'floor1' },
      { concept: 'orbital', symbol: 'room', element_id: 'rooms' },
      { concept: 'spin', symbol: 'bed', element_id: 'spin' }
    ];

    const interaction_flow = [
      { id: 'q1', highlight: ['floor1'], caption: 'Energy levels like floors: n=1,2,3…' },
      { id: 'q2', highlight: ['rooms'], caption: 'Orbitals like rooms on each floor.' },
      { id: 'q3', highlight: ['spin'], caption: 'Spin like bed orientation: up/down.' }
    ];

    return {
      type: 'story_scene',
      generated: true,
      subject,
      scene_json,
      neuro_symbolic_map,
      caption_text: 'Hotel metaphor: floors, rooms, and beds explain quantum numbers.',
      interaction_flow,
      preview_svg: generateConceptSVG('orbitals', 'physics')
    };
  }

  // Default generic scene (rangoli lines as relations)
  const scene_json = {
    canvas: { width: 480, height: 270, background: theme === 'festival' ? (selectedPalette.deepBlue || '#ffffff') : '#ffffff' },
    palette: selectedPalette,
    elements: [
      // Rangoli area
      { id: 'rangoli', type: 'pattern', x: 100, y: 60, w: 280, h: 160, style: 'rangoli', label: 'Relations' },
      // Center motif and rings
      { id: 'center_dot', type: 'circle', cx: 240, cy: 140, r: 6, fill: (selectedPalette.gold || '#FFD700') },
      { id: 'inner_ring', type: 'circle', cx: 240, cy: 140, r: 16, fill: 'none', stroke: (selectedPalette.green || '#138808') },
      { id: 'outer_ring', type: 'circle', cx: 240, cy: 140, r: 24, fill: 'none', stroke: (selectedPalette.saffron || '#FF9933') },
      // Petals (8)
      { id: 'p1', type: 'circle', cx: 240, cy: 100, r: 10, fill: (selectedPalette.saffron || '#FF9933') },
      { id: 'p2', type: 'circle', cx: 277, cy: 112, r: 10, fill: (selectedPalette.green || '#138808') },
      { id: 'p3', type: 'circle', cx: 289, cy: 149, r: 10, fill: (selectedPalette.saffron || '#FF9933') },
      { id: 'p4', type: 'circle', cx: 277, cy: 186, r: 10, fill: (selectedPalette.green || '#138808') },
      { id: 'p5', type: 'circle', cx: 240, cy: 198, r: 10, fill: (selectedPalette.saffron || '#FF9933') },
      { id: 'p6', type: 'circle', cx: 203, cy: 186, r: 10, fill: (selectedPalette.green || '#138808') },
      { id: 'p7', type: 'circle', cx: 191, cy: 149, r: 10, fill: (selectedPalette.saffron || '#FF9933') },
      { id: 'p8', type: 'circle', cx: 203, cy: 112, r: 10, fill: (selectedPalette.green || '#138808') },
      // Dots ring (8)
      { id: 'd1', type: 'circle', cx: 240, cy: 118, r: 4, fill: (selectedPalette.gold || '#FFD700') },
      { id: 'd2', type: 'circle', cx: 262, cy: 124, r: 4, fill: (selectedPalette.gold || '#FFD700') },
      { id: 'd3', type: 'circle', cx: 268, cy: 146, r: 4, fill: (selectedPalette.gold || '#FFD700') },
      { id: 'd4', type: 'circle', cx: 262, cy: 168, r: 4, fill: (selectedPalette.gold || '#FFD700') },
      { id: 'd5', type: 'circle', cx: 240, cy: 174, r: 4, fill: (selectedPalette.gold || '#FFD700') },
      { id: 'd6', type: 'circle', cx: 218, cy: 168, r: 4, fill: (selectedPalette.gold || '#FFD700') },
      { id: 'd7', type: 'circle', cx: 212, cy: 146, r: 4, fill: (selectedPalette.gold || '#FFD700') },
      { id: 'd8', type: 'circle', cx: 218, cy: 124, r: 4, fill: (selectedPalette.gold || '#FFD700') },
      // Diagonal guides (4)
      { id: 'g1', type: 'arrow', from: [240, 140], to: [240, 96], color: (selectedPalette.gold || '#FFD700') },
      { id: 'g2', type: 'arrow', from: [240, 140], to: [284, 140], color: (selectedPalette.gold || '#FFD700') },
      { id: 'g3', type: 'arrow', from: [240, 140], to: [240, 184], color: (selectedPalette.gold || '#FFD700') },
      { id: 'g4', type: 'arrow', from: [240, 140], to: [196, 140], color: (selectedPalette.gold || '#FFD700') },
      // Caption
      { id: 'concept', type: 'label', x: 120, y: 230, text: 'Concept relations like rangoli patterns' }
    ]
  };
  try {
    if (theme === 'bollywood') scene_json.elements.push({ id: 'accent_camera', type: 'icon', x: 60, y: 40, icon: '🎥' });
    if (theme === 'cooking') scene_json.elements.push({ id: 'accent_pot', type: 'icon', x: 60, y: 40, icon: '🍲' });
    if (theme === 'festival') scene_json.elements.push({ id: 'accent_firework', type: 'label', x: 60, y: 40, text: '✨' });
  } catch {}
  try {
    if (theme === 'bollywood') scene_json.elements.push({ id: 'accent_camera', type: 'icon', x: 60, y: 40, icon: '🎥' });
    if (theme === 'cooking') scene_json.elements.push({ id: 'accent_pot', type: 'icon', x: 60, y: 40, icon: '🍲' });
    if (theme === 'festival') scene_json.elements.push({ id: 'accent_firework', type: 'label', x: 60, y: 40, text: '✨' });
  } catch {}

  const neuro_symbolic_map = [
    { concept: 'relations', symbol: 'pattern', element_id: 'rangoli' },
    { concept: 'center', symbol: 'motif', element_id: 'center_dot' }
  ];

  const interaction_flow = [
    { id: 'r0', highlight: ['center_dot','inner_ring','outer_ring'], caption: 'Rangoli center forms.' },
    { id: 'r1', highlight: ['p1','p5'], caption: 'Petals emerge.' },
    { id: 'r2', highlight: ['p2','p6'], caption: 'More petals.' },
    { id: 'r3', highlight: ['p3','p7'], caption: 'Symmetry builds.' },
    { id: 'r4', highlight: ['p4','p8','d1','d3','d5','d7'], caption: 'Dots glow.' }
  ];

  const interactivity = {
    type: 'tap_to_frame',
    tap_to_frame: [
      { elementId: 'p1', goto: 'r1' },
      { elementId: 'p2', goto: 'r2' },
      { elementId: 'p3', goto: 'r3' },
      { elementId: 'p4', goto: 'r4' }
    ]
  };

  return {
    type: 'story_scene',
    generated: true,
    subject,
    scene_json,
    neuro_symbolic_map,
    caption_text: 'Rangoli metaphor: interlinked patterns represent concept relations.',
    interaction_flow,
    interactivity,
    preview_svg: generateConceptSVG('', subject)
  };
}


