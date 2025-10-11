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