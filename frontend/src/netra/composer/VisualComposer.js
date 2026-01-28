/**
 * 🎨 VISUAL COMPOSER
 * ==================
 * 
 * LLM-powered composition generator.
 * 
 * Takes a question + context and generates a CompositionSpec
 * that defines atoms, behaviors, narration, and interactions.
 * 
 * NO HARDCODED TEMPLATES - LLM decides everything dynamically.
 */

import { getRegisteredTypes, validateParams } from '../atoms/AtomRegistry';
import { COMPOSITION_LIMITS, isValidId, isValidAtomType } from '../types/CompositionSpec';
import { qualityGateAutoFix } from './QualityGateAutoFixer';

// ============================================
// DOMAIN COLOR PALETTES
// ============================================

const DOMAIN_COLORS = {
  biology: { primary: '#10B981', secondary: '#34D399', accent: '#FCD34D', background: ['#ECFDF5', '#D1FAE5'] },
  chemistry: { primary: '#8B5CF6', secondary: '#A78BFA', accent: '#F59E0B', background: ['#F5F3FF', '#EDE9FE'] },
  physics: { primary: '#3B82F6', secondary: '#60A5FA', accent: '#F472B6', background: ['#EFF6FF', '#DBEAFE'] },
  math: { primary: '#6366F1', secondary: '#818CF8', accent: '#14B8A6', background: ['#EEF2FF', '#E0E7FF'] },
  general: { primary: '#6B7280', secondary: '#9CA3AF', accent: '#F59E0B', background: ['#F9FAFB', '#F3F4F6'] },
};

// 🔧 GLOBAL DEDUPLICATION: Shared across all VisualComposer instances
// This prevents duplicate API calls even when multiple instances exist
const GLOBAL_INFLIGHT_REQUESTS = new Map();
const GLOBAL_CACHE = new Map();

// ============================================
// COMPOSER PROMPT
// ============================================

const COMPOSER_SYSTEM_PROMPT = `You are NETRA, world's most advanced Visual Simulation Director.
You create ANIMATED INTERACTIVE SIMULATIONS that teach through MOTION and CAUSALITY.

🚨 CRITICAL: You are NOT creating diagrams. You are creating MINI GAMES / SIMULATIONS.

═══════════════════════════════════════════════════════════════════
❌ ABSOLUTE REJECTION CRITERIA (if ANY of these, output is INVALID)
═══════════════════════════════════════════════════════════════════

Your output is INVALID if it looks like:
- Labeled circles/boxes scattered on canvas
- A flowchart or node graph
- Text with arrows connecting them
- Static diagram with no real animation
- "PowerPoint slide" aesthetic

🎯 VALID OUTPUT = A simulation where things MOVE, TRANSFORM, and RESPOND.

═══════════════════════════════════════════════════════════════════
✅ MANDATORY STRUCTURE: INPUT → PROCESS → OUTPUT
═══════════════════════════════════════════════════════════════════

Every visual MUST show a CAUSAL CHAIN:

1. INPUT ZONE (left side, x: 80-200)
   - What enters the system (energy, molecules, force, data)
   - These should ANIMATE INTO the scene (moveTo behavior)

2. PROCESS ZONE (center, x: 280-440) 
   - The HERO OBJECT where transformation happens
   - Must be LARGE (width: 200-350px)
   - Must have REACTION ANIMATION (pulse, glow, particles)

3. OUTPUT ZONE (right side, x: 520-640)
   - What exits the system (products, results, effects)
   - These should ANIMATE OUT from the process

═══════════════════════════════════════════════════════════════════
🎬 3-ACT ANIMATION STRUCTURE (MANDATORY)
═══════════════════════════════════════════════════════════════════

ACT 1 - SETUP (0-1500ms):
  - Environment fades in
  - Hero object appears dramatically (scaleIn)
  - Inputs begin approaching

ACT 2 - TRANSFORMATION (1500-4000ms):
  - Inputs reach the process zone
  - REACTION happens (glow, pulse, particle burst)
  - State change occurs
  - Outputs begin forming

ACT 3 - RESOLUTION (4000-6000ms):
  - Outputs complete their journey
  - System reaches new state
  - Key insight highlighted

═══════════════════════════════════════════════════════════════════
ATOM SPECIFICATIONS (SIZE AND POSITION)
═══════════════════════════════════════════════════════════════════

Canvas: 720x520px

HERO OBJECT (process zone):
  id: "hero_[concept]"
  type: "Entity" or "RigidBody"  
  position: {x: 360, y: 260}  // CENTER
  params:
    width: 200-350  // LARGE
    height: 150-250
    fill: Domain color (see below)
    stroke: Darker variant
    strokeWidth: 4
    cornerRadius: 20 (for organic), 8 (for mechanical)
    glow: true
    label: Short name inside

INPUT ATOMS (flowing in):
  id: "input_[name]"
  type: "Entity"
  position: {x: 80-150, y: varies}  // LEFT SIDE - starting position
  params:
    width: 60-100
    height: 60-100
    shape: "circle" for molecules, "rect" for energy/data
    fill: Input color
    animated: true

OUTPUT ATOMS (flowing out):
  id: "output_[name]"
  type: "Entity"
  position: {x: 360, y: 260}  // START at hero, will animate out
  params:
    width: 60-100
    height: 60-100
    fill: Output color
  initialState: {visible: false}  // Hidden until produced

ENVIRONMENT:
  id: "env_container"
  type: "Region"
  position: {x: 360, y: 280}
  params:
    width: 650
    height: 420
    fill: "rgba(domain_color, 0.1)"
    stroke: "rgba(domain_color, 0.3)"
    cornerRadius: 30
  zIndex: -10

═══════════════════════════════════════════════════════════════════
BEHAVIOR CHOREOGRAPHY (MINIMUM 8 BEHAVIORS)
═══════════════════════════════════════════════════════════════════

ACT 1 behaviors:
  {trigger: {type: "scene_ready", delay: 0}, action: {type: "fadeIn", target: "env_container", duration: 500}}
  {trigger: {type: "scene_ready", delay: 300}, action: {type: "scaleIn", target: "hero_*", duration: 600}}
  {trigger: {type: "scene_ready", delay: 800}, action: {type: "fadeIn", target: "input_*", duration: 400}}

ACT 2 behaviors:
  {trigger: {type: "scene_ready", delay: 1200}, action: {type: "moveTo", target: "input_*", x: 280, y: 260, duration: 1000}}
  {trigger: {type: "scene_ready", delay: 2200}, action: {type: "pulse", target: "hero_*", loop: false, duration: 800}}
  {trigger: {type: "scene_ready", delay: 2500}, action: {type: "show", target: "output_*"}}

ACT 3 behaviors:
  {trigger: {type: "scene_ready", delay: 3000}, action: {type: "moveTo", target: "output_*", x: 580, y: 260, duration: 1000}}
  {trigger: {type: "scene_ready", delay: 4500}, action: {type: "highlight", target: "output_*", duration: 2000}}

═══════════════════════════════════════════════════════════════════
NARRATION (EXACTLY 3 - SYNCED TO ACTS)
═══════════════════════════════════════════════════════════════════

[
  {
    "trigger": {"type": "scene_ready", "delay": 500},
    "text": "[ACT 1] Setup context - what we're about to see",
    "emphasis": "normal"
  },
  {
    "trigger": {"type": "scene_ready", "delay": 2200},
    "text": "[ACT 2] Explain the transformation happening",
    "emphasis": "high"
  },
  {
    "trigger": {"type": "scene_ready", "delay": 4000},
    "text": "[ACT 3] Key insight - what was produced/learned",
    "emphasis": "normal"
  }
]

═══════════════════════════════════════════════════════════════════
INTERACTIONS (MINIMUM 1)
═══════════════════════════════════════════════════════════════════

Include at least ONE:
{
  "id": "control_slider",
  "type": "slider",
  "target": "hero_*",
  "property": "reactionSpeed|intensity|rate",
  "min": 0.5,
  "max": 2.0,
  "default": 1.0,
  "label": "Adjust [parameter]"
}

OR drag interaction:
{
  "id": "drag_input",
  "type": "drag",
  "target": "input_*",
  "bounds": {"minX": 50, "maxX": 400, "minY": 100, "maxY": 400}
}

═══════════════════════════════════════════════════════════════════
DOMAIN COLOR PALETTES
═══════════════════════════════════════════════════════════════════

BIOLOGY: 
  hero: "#10B981" (green), inputs: "#3B82F6" (blue), outputs: "#F59E0B" (amber)

PHYSICS:
  hero: "#3B82F6" (blue), inputs: "#EF4444" (red), outputs: "#8B5CF6" (purple)

CHEMISTRY:
  hero: "#8B5CF6" (purple), inputs: "#06B6D4" (cyan), outputs: "#F59E0B" (amber)

MATH:
  hero: "#6366F1" (indigo), secondary: "#EC4899" (pink), accent: "#14B8A6" (teal)

═══════════════════════════════════════════════════════════════════
EXAMPLE: PHOTOSYNTHESIS (WORLD-CLASS QUALITY)
═══════════════════════════════════════════════════════════════════

{
  "sceneDirection": {
    "goal": "Understand photosynthesis as energy transformation",
    "heroObject": "Chloroplast reaction chamber",
    "inputFlow": "Sunlight + CO₂ + H₂O flowing in",
    "outputFlow": "O₂ released + Glucose stored",
    "interactionFocus": "Sunlight intensity slider"
  },
  "atoms": [
    {"id": "env_leaf", "type": "Region", "position": {"x": 360, "y": 280}, "params": {"width": 650, "height": 420, "fill": "rgba(16, 185, 129, 0.1)", "stroke": "rgba(16, 185, 129, 0.3)", "cornerRadius": 50}, "zIndex": -10},
    
    {"id": "hero_chloroplast", "type": "Entity", "position": {"x": 360, "y": 280}, "params": {"shape": "ellipse", "width": 280, "height": 180, "fill": "#10B981", "stroke": "#059669", "strokeWidth": 6, "label": "Chloroplast", "labelColor": "#FFFFFF", "glow": true}},
    
    {"id": "input_sunlight", "type": "Entity", "position": {"x": 100, "y": 120}, "params": {"shape": "circle", "width": 70, "height": 70, "fill": "#FCD34D", "stroke": "#F59E0B", "label": "☀️", "glow": true}},
    {"id": "input_co2", "type": "Entity", "position": {"x": 80, "y": 280}, "params": {"shape": "circle", "width": 60, "height": 60, "fill": "#94A3B8", "stroke": "#64748B", "label": "CO₂"}},
    {"id": "input_h2o", "type": "Entity", "position": {"x": 100, "y": 400}, "params": {"shape": "circle", "width": 60, "height": 60, "fill": "#3B82F6", "stroke": "#2563EB", "label": "H₂O"}},
    
    {"id": "output_o2", "type": "Entity", "position": {"x": 360, "y": 280}, "params": {"shape": "circle", "width": 55, "height": 55, "fill": "#A7F3D0", "stroke": "#34D399", "label": "O₂"}, "initialState": {"visible": false}},
    {"id": "output_glucose", "type": "Entity", "position": {"x": 360, "y": 280}, "params": {"shape": "hexagon", "width": 70, "height": 70, "fill": "#FDE68A", "stroke": "#F59E0B", "label": "C₆H₁₂O₆"}, "initialState": {"visible": false}}
  ],
  "behaviors": [
    {"trigger": {"type": "scene_ready", "delay": 0}, "action": {"type": "fadeIn", "target": "env_leaf", "duration": 400}},
    {"trigger": {"type": "scene_ready", "delay": 200}, "action": {"type": "scaleIn", "target": "hero_chloroplast", "duration": 600}},
    {"trigger": {"type": "scene_ready", "delay": 600}, "action": {"type": "fadeIn", "target": "input_sunlight", "duration": 300}},
    {"trigger": {"type": "scene_ready", "delay": 700}, "action": {"type": "fadeIn", "target": "input_co2", "duration": 300}},
    {"trigger": {"type": "scene_ready", "delay": 800}, "action": {"type": "fadeIn", "target": "input_h2o", "duration": 300}},
    {"trigger": {"type": "scene_ready", "delay": 1200}, "action": {"type": "moveTo", "target": "input_sunlight", "x": 280, "y": 200, "duration": 1200}},
    {"trigger": {"type": "scene_ready", "delay": 1400}, "action": {"type": "moveTo", "target": "input_co2", "x": 280, "y": 280, "duration": 1000}},
    {"trigger": {"type": "scene_ready", "delay": 1600}, "action": {"type": "moveTo", "target": "input_h2o", "x": 280, "y": 340, "duration": 800}},
    {"trigger": {"type": "scene_ready", "delay": 2600}, "action": {"type": "pulse", "target": "hero_chloroplast", "duration": 1000, "scale": 1.1}},
    {"trigger": {"type": "scene_ready", "delay": 3200}, "action": {"type": "show", "target": "output_o2"}},
    {"trigger": {"type": "scene_ready", "delay": 3400}, "action": {"type": "show", "target": "output_glucose"}},
    {"trigger": {"type": "scene_ready", "delay": 3500}, "action": {"type": "moveTo", "target": "output_o2", "x": 580, "y": 150, "duration": 1200}},
    {"trigger": {"type": "scene_ready", "delay": 3700}, "action": {"type": "moveTo", "target": "output_glucose", "x": 580, "y": 350, "duration": 1000}},
    {"trigger": {"type": "scene_ready", "delay": 5000}, "action": {"type": "highlight", "target": "output_glucose", "duration": 2000}}
  ],
  "narration": [
    {"trigger": {"type": "scene_ready", "delay": 400}, "text": "Inside the leaf, the chloroplast captures sunlight energy", "emphasis": "normal"},
    {"trigger": {"type": "scene_ready", "delay": 2600}, "text": "Light energy transforms CO₂ and H₂O through photosynthesis", "emphasis": "high"},
    {"trigger": {"type": "scene_ready", "delay": 4800}, "text": "The result: Oxygen is released, and glucose stores the energy", "emphasis": "normal"}
  ],
  "interactions": [
    {"id": "light_intensity", "type": "slider", "label": "Sunlight Intensity", "target": "input_sunlight", "property": "opacity", "min": 0.3, "max": 1.0, "default": 0.8}
  ]
}

═══════════════════════════════════════════════════════════════════
OUTPUT REQUIREMENTS
═══════════════════════════════════════════════════════════════════

Return ONLY valid JSON with this structure. No markdown, no explanation.

MANDATORY FIELDS:
- sceneDirection: object describing the simulation
- atoms: array (minimum 5, including hero + environment + inputs + outputs)
- behaviors: array (minimum 8, choreographed with delays)
- narration: array (exactly 3, synced to acts)
- interactions: array (minimum 1)

VALIDATION:
- Hero atom width >= 200
- Environment/Region present
- At least 2 input atoms with moveTo behaviors
- At least 1 output atom that appears mid-scene
- Behaviors span 0-5000ms with proper delays`;

// ============================================
// VISUAL COMPOSER CLASS
// ============================================

// Get backend URL - same pattern as other API calls
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Log the backend URL at module load time for debugging
console.log('🎨 [VisualComposer] BACKEND_URL configured:', BACKEND_URL);

// ============================================
// CACHE CONTROL FLAGS (DEV TOGGLES)
// ============================================
// Set to true to bypass cache and force fresh backend calls
const FORCE_FRESH_COMPOSE = true; // 🔧 DEV: Set to false in production

// Use async composition (recommended for production)
const USE_ASYNC_COMPOSITION = true; // 🚀 Enables non-blocking LLM calls

// 🚀 NEW: Use SimulationScript API (v6.0)
const USE_SIMULATION_API = true; // 🎬 Enables new simulation-based visuals

// Polling settings for async composition
const ASYNC_POLL_INTERVAL_MS = 1000;  // Poll every 1 second
const ASYNC_MAX_POLL_TIME_MS = 90000; // Max wait: 90 seconds

// Minimum quality thresholds for caching (high standards for intelligent visuals)
// These match the COMPOSER_PROMPT requirements
const CACHE_QUALITY_THRESHOLDS = {
  minAtoms: 6,       // High quality: at least 6 diverse atoms
  minBehaviors: 5,   // High quality: at least 5 sequenced behaviors
  minNarration: 3,   // High quality: at least 3 progressive narration cues
  requiredPhysicsAtoms: ['RigidBody', 'Surface', 'ForceVector'], // At least 1 needed for physics
};

export class VisualComposer {
  constructor(options = {}) {
    // CRITICAL: Always use full BACKEND_URL, ignore relative path overrides
    const defaultEndpoint = `${BACKEND_URL}/api/netra/compose`;
    const asyncEndpoint = `${BACKEND_URL}/api/netra/compose-async`;
    const statusEndpoint = `${BACKEND_URL}/api/netra/compose-status`;
    
    // 🚀 NEW: Simulation API endpoints (v6.0)
    const simulateEndpoint = `${BACKEND_URL}/api/netra/simulate-async`;
    const simulateStatusEndpoint = `${BACKEND_URL}/api/netra/simulate-status`;
    
    // If options.apiEndpoint is provided but is a relative URL, ignore it
    let finalEndpoint = defaultEndpoint;
    if (options.apiEndpoint && options.apiEndpoint.startsWith('http')) {
      finalEndpoint = options.apiEndpoint;
    }
    
    this.options = {
      apiEndpoint: finalEndpoint,
      asyncEndpoint: asyncEndpoint,
      statusEndpoint: statusEndpoint,
      simulateEndpoint: simulateEndpoint,
      simulateStatusEndpoint: simulateStatusEndpoint,
      timeout: options.timeout || 15000,  // Increased timeout for LLM generation
      fallbackEnabled: options.fallbackEnabled !== false,
      useAsync: USE_ASYNC_COMPOSITION,
      useSimulation: USE_SIMULATION_API,
      ...options,
      apiEndpoint: finalEndpoint,  // Ensure this is last to override any spread
    };
    
    console.log('🎨 [VisualComposer] Initialized with endpoint:', this.options.apiEndpoint);
    console.log('🎨 [VisualComposer] Async mode:', this.options.useAsync ? 'ENABLED' : 'disabled');
    console.log('🎬 [VisualComposer] Simulation mode:', this.options.useSimulation ? 'ENABLED (v6.0)' : 'disabled');
    
    this.cache = new Map();
    
    // 🔧 DEDUPLICATION: Track in-flight requests to prevent duplicate calls
    this.inflightRequests = new Map();  // cacheKey -> Promise
  }
  
  // ============================================
  // 🚀 SIMULATION API (v6.0) - NEW
  // ============================================
  
  /**
   * Generate SimulationScript using new v6.0 API
   * Returns placeholder immediately, then polls for full script
   * 
   * @param {string} question - The question to visualize
   * @param {object} context - Context (domain, intent, etc.)
   * @param {function} onScriptReady - Callback when full script is ready
   * @returns {object} - Placeholder for immediate display
   */
  async generateSimulation(question, context = {}, onScriptReady = null) {
    const startTime = Date.now();
    
    console.log('════════════════════════════════════════════════════════════');
    console.log('🎬 [SIMULATE] Starting simulation generation (v6.0)');
    console.log('🎬 [SIMULATE] Question:', question.substring(0, 60));
    console.log('════════════════════════════════════════════════════════════');
    
    try {
      // Step 1: Call simulate-async - returns placeholder immediately
      const response = await fetch(this.options.simulateEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, context })
      });
      
      if (!response.ok) {
        throw new Error(`Simulate API failed: ${response.status}`);
      }
      
      const { task_id, placeholder, poll_url } = await response.json();
      
      console.log(`🎬 [SIMULATE] Task: ${task_id}`);
      console.log(`🎬 [SIMULATE] Placeholder ready in ${Date.now() - startTime}ms`);
      
      // Step 2: Start background polling for full script
      if (onScriptReady) {
        this._pollForSimulationScript(task_id, startTime, onScriptReady);
      }
      
      // Return placeholder immediately for instant rendering
      return {
        type: 'simulation',
        script: placeholder,
        taskId: task_id,
        isPlaceholder: true
      };
      
    } catch (error) {
      console.error('❌ [SIMULATE] Error:', error.message);
      
      // Return minimal placeholder on error
      return {
        type: 'simulation',
        script: this._generateFallbackSimulation(question, context),
        isPlaceholder: true,
        error: error.message
      };
    }
  }
  
  /**
   * Poll for full SimulationScript
   */
  async _pollForSimulationScript(taskId, startTime, onScriptReady) {
    const pollEndpoint = `${this.options.simulateStatusEndpoint}/${taskId}`;
    let pollCount = 0;
    const maxPolls = Math.ceil(ASYNC_MAX_POLL_TIME_MS / ASYNC_POLL_INTERVAL_MS);
    
    while (pollCount < maxPolls) {
      await this.sleep(ASYNC_POLL_INTERVAL_MS);
      pollCount++;
      
      try {
        const response = await fetch(pollEndpoint);
        if (!response.ok) {
          console.warn(`⚠️ [SIMULATE] Poll ${pollCount} failed`);
          continue;
        }
        
        const result = await response.json();
        const elapsed = Date.now() - startTime;
        
        if (result.status === 'complete' && result.script) {
          console.log('════════════════════════════════════════════════════════════');
          console.log(`🎬 [SIMULATE] ✅ Script ready in ${elapsed}ms`);
          console.log(`🎬 [SIMULATE] Entities: ${result.script.entities?.length || 0}`);
          console.log(`🎬 [SIMULATE] Rules: ${result.script.rules?.length || 0}`);
          console.log(`🎬 [SIMULATE] Quality: entropy=${result.quality?.entropy?.toFixed(2)}`);
          console.log('════════════════════════════════════════════════════════════');
          
          onScriptReady({
            type: 'simulation',
            script: result.script,
            quality: result.quality,
            generationTimeMs: result.generation_time_ms,
            isPlaceholder: false
          });
          return;
        }
        
        if (result.status === 'failed') {
          console.error(`❌ [SIMULATE] Task failed: ${result.error}`);
          return;
        }
        
        if (pollCount % 5 === 0) {
          console.log(`⏳ [SIMULATE] Still generating... (${elapsed}ms)`);
        }
        
      } catch (err) {
        console.warn(`⚠️ [SIMULATE] Poll error: ${err.message}`);
      }
    }
    
    console.warn('⏰ [SIMULATE] Timeout waiting for script');
  }
  
  /**
   * Generate fallback simulation script
   */
  _generateFallbackSimulation(question, context) {
    return {
      "$schema": "netra/simulation/v1",
      ontology: "abstract_relational",
      world: "hierarchy_tree",
      title: "Exploring the Concept",
      entities: [
        { id: "main", role: "subject", template: "flow_node", label: question.substring(0, 30) },
        { id: "detail_1", role: "environment", template: "region", label: "Aspect 1" },
        { id: "detail_2", role: "environment", template: "region", label: "Aspect 2" }
      ],
      constants: {},
      state: { initial: "idle", variables: {} },
      rules: [],
      interactions: [],
      narration: [
        { id: "intro", event: "start", text: `Let's explore: ${question.substring(0, 50)}...` }
      ],
      _meta: { isFallback: true, domain: context.domain || 'general' }
    };
  }

  /**
   * Generate composition from question
   * Uses async polling if enabled for long-running LLM calls
   */
  async compose(question, context = {}) {
    const { intent, domain, difficulty } = context;
    const cacheKey = this.getCacheKey(question, context);
    
    // ============================================
    // DEDUPLICATION CHECK - Reuse in-flight requests (GLOBAL)
    // ============================================
    if (GLOBAL_INFLIGHT_REQUESTS.has(cacheKey)) {
      console.log('🔄 [DEDUPE] Reusing GLOBAL in-flight request for:', cacheKey.substring(0, 40));
      return GLOBAL_INFLIGHT_REQUESTS.get(cacheKey);
    }
    
    // ============================================
    // CACHE BYPASS CHECK
    // ============================================
    if (FORCE_FRESH_COMPOSE) {
      console.log('🔄 [CACHE] bypassed (FORCE_FRESH_COMPOSE=true)');
      // Delete existing cache entry to force fresh generation
      if (GLOBAL_CACHE.has(cacheKey)) {
        console.log('🗑️ [CACHE] Deleting stale entry for:', cacheKey.substring(0, 40));
        GLOBAL_CACHE.delete(cacheKey);
      }
    } else if (GLOBAL_CACHE.has(cacheKey)) {
      // Only return cached if it passes quality check
      const cached = GLOBAL_CACHE.get(cacheKey);
      if (this.isHighQualityComposition(cached, context)) {
        console.log('✅ [CACHE] hit (high-quality):', cacheKey.substring(0, 40));
        return cached;
      } else {
        console.log('⚠️ [CACHE] hit but LOW QUALITY - regenerating');
        GLOBAL_CACHE.delete(cacheKey);
      }
    }

    console.log(`[VisualComposer] 🚀 Composing FRESH for: "${question.substring(0, 50)}..."`);

    // Create the composition promise and track it
    const compositionPromise = this._doComposition(question, context, cacheKey);
    
    // Register as GLOBAL in-flight request
    GLOBAL_INFLIGHT_REQUESTS.set(cacheKey, compositionPromise);
    
    try {
      const result = await compositionPromise;
      return result;
    } finally {
      // Always clean up GLOBAL in-flight tracking
      GLOBAL_INFLIGHT_REQUESTS.delete(cacheKey);
    }
  }
  
  /**
   * Internal method to do actual composition
   */
  async _doComposition(question, context, cacheKey) {
    // 🎯 CRITICAL: ALWAYS detect domain from question - DON'T trust backend's 'General'
    // Backend often returns 'General' even for biology/physics questions
    const backendDomain = context.domain?.toLowerCase();
    const detectedDomain = this._detectDomain(question);
    
    // Use detected domain if backend says 'general' or is undefined
    const finalDomain = (backendDomain === 'general' || !backendDomain) ? detectedDomain : backendDomain;
    const enrichedContext = { ...context, domain: finalDomain };
    
    console.log('🎯 [DOMAIN] Backend domain:', backendDomain, '| Detected:', detectedDomain, '| Final:', finalDomain);
    
    try {
      // ============================================
      // ASYNC vs SYNC COMPOSITION
      // ============================================
      let spec;
      if (this.options.useAsync) {
        console.log('🚀 [ASYNC] Using async composition (non-blocking)');
        spec = await this.callLLMAsync(question, enrichedContext);
      } else {
        console.log('⏳ [SYNC] Using sync composition (blocking)');
        spec = await this.callLLM(question, enrichedContext);
      }
      
      // 🎯 DETECT FORMAT: New ProceduralScenePlan vs Old Atoms
      const isProceduralFormat = spec.semanticIntent && spec.proceduralScenePlan;
      
      if (isProceduralFormat) {
        console.log('🎬 [FORMAT] New ProceduralScenePlan format detected!');
        // Convert to atoms-based format for current renderer
        // TODO: Route to ProceduralSceneRenderer directly in future
        spec = this._convertProceduralToAtoms(spec, enrichedContext);
      }
      
      // Validate and fix
      const validated = this.validateAndFix(spec, question, enrichedContext);
      
      // ============================================
      // 🛡️ QUALITY GATE AUTO-FIXER (CRITICAL)
      // Detect diagrams → Convert to procedural simulations
      // All fixes happen locally - NO API RE-CALLS
      // ============================================
      console.log('🛡️ [QG] Running QualityGate AutoFixer...');
      const { composition: enhanced, qualityReport } = qualityGateAutoFix(validated, {
        domain: enrichedContext.domain || 'physics',
        processType: enrichedContext.intent || 'transformation',
      });
      
      console.log('🛡️ [QG] Result:', {
        passed: qualityReport.passed,
        fixesApplied: qualityReport.autoFixApplied.length,
        violations: qualityReport.violations.length,
      });
      
      // ============================================
      // QUALITY-BASED CACHING
      // ============================================
      if (this.isHighQualityComposition(enhanced, enrichedContext)) {
        GLOBAL_CACHE.set(cacheKey, enhanced);
        console.log('💾 [CACHE] stored (high-quality composition)');
      } else {
        console.log('⚠️ [CACHE] skip write: low quality composition');
        console.log('   - atoms:', enhanced.atoms?.length || 0);
        console.log('   - behaviors:', enhanced.behaviors?.length || 0);
        console.log('   - narration:', enhanced.narration?.length || 0);
      }
      
      console.log('[VisualComposer] ✅ Composition generated + enhanced successfully');
      return enhanced;
    } catch (error) {
      console.error('[VisualComposer] ❌ LLM call failed:', error.message);
      
      // ALWAYS return a fallback - never throw
      // ⚠️ CRITICAL: Do NOT cache fallback compositions!
      console.log('[VisualComposer] 📦 Using intelligent fallback (NOT CACHED)');
      const fallback = this.generateProceduralFallback(question, enrichedContext);
      
      console.log('[VisualComposer] ✅ Procedural fallback generated');
      return fallback;
    }
  }
  
  /**
   * 🎯 Detect domain from question keywords
   */
  _detectDomain(question) {
    const q = question.toLowerCase();
    
    // Biology keywords
    if (/photosynthesis|cell|dna|protein|enzyme|mitosis|meiosis|organ|plant|animal|bacteria|virus|respiration|chloroplast|mitochondria|nucleus|membrane|evolution|species|ecosystem|food chain|digestive|circulatory|nervous|reproductive|skeleton|muscle/.test(q)) {
      return 'biology';
    }
    
    // Chemistry keywords
    if (/atom|molecule|reaction|bond|element|compound|acid|base|ph|oxidation|reduction|electron|proton|neutron|ion|solution|catalyst|periodic|chemical/.test(q)) {
      return 'chemistry';
    }
    
    // Physics keywords
    if (/force|velocity|acceleration|momentum|energy|wave|light|sound|electricity|magnetism|gravity|friction|motion|newton|thermodynamics|quantum|relativity|circuit|resistance|current|voltage/.test(q)) {
      return 'physics';
    }
    
    // Math keywords
    if (/equation|graph|function|derivative|integral|algebra|geometry|calculus|trigonometry|probability|statistics|matrix|vector|polynomial|quadratic|linear/.test(q)) {
      return 'math';
    }
    
    return 'general';
  }
  
  /**
   * 🎬 Convert new ProceduralScenePlan format to atoms-based format
   */
  _convertProceduralToAtoms(proceduralSpec, context) {
    const { semanticIntent, proceduralScenePlan, colorPalette } = proceduralSpec;
    
    console.log('🔄 [CONVERT] Converting ProceduralScenePlan to atoms...');
    
    const atoms = [];
    const behaviors = [];
    const narration = [];
    
    // Extract layers and convert to atoms
    const layers = proceduralScenePlan?.layers || [];
    let atomIndex = 0;
    
    for (const layer of layers) {
      for (const element of layer.elements || []) {
        const atomId = element.id || `atom_${atomIndex++}`;
        const role = element.role || 'effect';
        
        // Convert position descriptions to coordinates
        const position = this._resolvePosition(element.position, role);
        const size = this._resolveSize(element.size);
        
        atoms.push({
          id: atomId,
          type: 'Entity',
          generator: element.generator,
          generatorParams: element.style || {},
          role: role,
          params: {
            shape: 'ellipse',
            width: size.width,
            height: size.height,
            fill: element.style?.fill?.colors?.[0] || colorPalette?.primary || '#3B82F6',
            stroke: element.style?.stroke?.color || colorPalette?.secondary || '#60A5FA',
            strokeWidth: element.style?.stroke?.width || 2,
            label: element.label,
            glow: element.style?.glow?.enabled || role === 'hero',
            glowColor: element.style?.glow?.color || colorPalette?.accent || '#FCD34D',
            glowIntensity: element.style?.glow?.intensity || 0.5,
            generator: element.generator,
            generatorParams: element.style || {},
          },
          position: position,
          initialState: { visible: true, opacity: 1 },
          zIndex: layer.zIndex || 0,
        });
      }
    }
    
    // Convert choreography to behaviors
    const choreography = proceduralScenePlan?.choreography || [];
    for (const beat of choreography) {
      behaviors.push({
        id: `behavior_${beat.beat}`,
        trigger: { type: 'scene_ready', delay: beat.time || 0 },
        action: {
          type: this._mapChoreographyAction(beat.action),
          target: beat.target || 'hero',
          duration: beat.duration || 500,
          params: beat,
        },
      });
    }
    
    // Convert narration
    const narrationBeats = proceduralScenePlan?.narration || [];
    for (const beat of narrationBeats) {
      const timing = choreography.find(c => c.beat === beat.beat);
      narration.push({
        id: `narr_${beat.beat}`,
        trigger: { type: 'scene_ready', delay: timing?.time || 0 },
        text: beat.text,
        emphasis: beat.emphasis || 'normal',
        duration: 3000,
      });
    }
    
    return {
      $schema: 'netra/composition/v1',
      version: '2.0.0',
      id: `proc_${Date.now()}`,
      context: {
        question: semanticIntent?.concept || context.question,
        domain: semanticIntent?.domain || context.domain,
        intent: semanticIntent?.processType || context.intent,
      },
      atoms,
      behaviors,
      narration,
      interactions: proceduralScenePlan?.interactions || [],
      stage: {
        width: 720,
        height: 520,
        background: {
          type: proceduralScenePlan?.background?.type || 'gradient',
          value: proceduralScenePlan?.background?.colors || colorPalette?.background || ['#f0f9ff', '#e0f2fe'],
          direction: proceduralScenePlan?.background?.direction || 'vertical',
        },
        physics: { enabled: false },
      },
      _meta: {
        format: 'converted_from_procedural',
        originalIntent: semanticIntent,
      },
    };
  }
  
  _resolvePosition(positionDesc, role) {
    const positions = {
      center: { x: 360, y: 260 },
      left: { x: 120, y: 260 },
      right: { x: 600, y: 260 },
      top: { x: 360, y: 100 },
      bottom: { x: 360, y: 420 },
      'top-left': { x: 120, y: 100 },
      'top-right': { x: 600, y: 100 },
      'bottom-left': { x: 120, y: 420 },
      'bottom-right': { x: 600, y: 420 },
    };
    
    if (typeof positionDesc === 'string') {
      return positions[positionDesc] || positions.center;
    }
    
    // Role-based defaults
    const rolePositions = {
      hero: positions.center,
      input: positions.left,
      output: positions.right,
      environment: positions.bottom,
    };
    
    return rolePositions[role] || positions.center;
  }
  
  _resolveSize(sizeDesc) {
    const sizes = {
      small: { width: 60, height: 60 },
      medium: { width: 120, height: 100 },
      large: { width: 200, height: 160 },
    };
    
    return sizes[sizeDesc] || sizes.medium;
  }
  
  _mapChoreographyAction(action) {
    const actionMap = {
      fade_in_environment: 'fadeIn',
      scale_in_hero: 'scaleIn',
      slide_in_inputs: 'slideIn',
      slide_in_outputs: 'slideIn',
      start_flow_particles: 'flowParticles',
      pulse_hero: 'pulse',
      emit_outputs: 'emit',
      glow: 'highlight',
    };
    
    return actionMap[action] || action;
  }
  
  /**
   * 🎬 Generate a procedural fallback (NOT atoms-based)
   * This creates a rich visual even when LLM fails
   */
  generateProceduralFallback(question, context) {
    const domain = context.domain || 'general';
    const colors = DOMAIN_COLORS[domain] || DOMAIN_COLORS.general;
    const concept = question.substring(0, 40);
    
    console.log('🎬 [FALLBACK] Generating procedural fallback for domain:', domain);
    
    // Generate domain-specific procedural fallback
    const generators = {
      biology: ['organic_cell', 'chloroplast', 'leaf'],
      chemistry: ['molecule', 'atom_orbital', 'reaction_zone'],
      physics: ['wave', 'force_field', 'ball'],
      math: ['graph', 'equation', 'shape'],
      general: ['organic_cell', 'gradient_region', 'particle_group'],
    };
    
    const domainGenerators = generators[domain] || generators.general;
    const heroGenerator = domainGenerators[0];
    const inputGenerator = domainGenerators[1] || 'particle_group';
    const outputGenerator = domainGenerators[2] || 'particle_group';
    
    return {
      $schema: 'netra/composition/v1',
      version: '2.0.0',
      id: `fallback_proc_${Date.now()}`,
      context: {
        question: question,
        domain: domain,
        intent: context.intent || 'conceptual',
        isFallback: true,
      },
      atoms: [
        // Hero - Large, centered, with procedural generator
        {
          id: 'hero_main',
          type: 'Entity',
          role: 'hero',
          generator: heroGenerator,
          generatorParams: { width: 200, height: 160, color: colors.primary },
          params: {
            shape: 'ellipse',
            width: 200,
            height: 160,
            fill: colors.primary,
            stroke: colors.secondary,
            strokeWidth: 3,
            glow: true,
            glowColor: colors.accent,
            glowIntensity: 0.6,
            isHero: true,
            generator: heroGenerator,
            generatorParams: { width: 200, height: 160, color: colors.primary },
          },
          position: { x: 360, y: 260 },
          initialState: { visible: true, opacity: 1 },
          zIndex: 1,
        },
        // Input element
        {
          id: 'input_1',
          type: 'Entity',
          role: 'input',
          generator: inputGenerator,
          params: {
            shape: 'circle',
            width: 70,
            height: 70,
            fill: colors.secondary,
            stroke: colors.primary,
            strokeWidth: 2,
            label: 'Input',
            generator: inputGenerator,
          },
          position: { x: 120, y: 260 },
          initialState: { visible: true, opacity: 1 },
          zIndex: 2,
        },
        // Output element
        {
          id: 'output_1',
          type: 'Entity',
          role: 'output',
          generator: outputGenerator,
          params: {
            shape: 'circle',
            width: 70,
            height: 70,
            fill: colors.accent,
            stroke: colors.primary,
            strokeWidth: 2,
            label: 'Output',
            generator: outputGenerator,
          },
          position: { x: 600, y: 260 },
          initialState: { visible: true, opacity: 1 },
          zIndex: 2,
        },
        // Title label
        {
          id: 'title_label',
          type: 'Label',
          params: {
            text: `Exploring: ${domain.charAt(0).toUpperCase() + domain.slice(1)}`,
            fontSize: 18,
            fontWeight: 'bold',
            color: colors.primary,
          },
          position: { x: 360, y: 60 },
          initialState: { visible: true, opacity: 1 },
          zIndex: 3,
        },
        // Concept label
        {
          id: 'concept_label',
          type: 'Label',
          params: {
            text: concept,
            fontSize: 14,
            color: '#6B7280',
          },
          position: { x: 360, y: 450 },
          initialState: { visible: true, opacity: 1 },
          zIndex: 3,
        },
        // Flow connector
        {
          id: 'flow_connector',
          type: 'Connector',
          params: {
            from: 'input_1',
            to: 'hero_main',
            style: 'dashed',
            color: colors.secondary,
            animated: true,
          },
        },
      ],
      behaviors: [
        { id: 'b1', trigger: { type: 'scene_ready', delay: 0 }, action: { type: 'fadeIn', target: 'title_label', duration: 400 } },
        { id: 'b2', trigger: { type: 'scene_ready', delay: 300 }, action: { type: 'scaleIn', target: 'hero_main', duration: 600 } },
        { id: 'b3', trigger: { type: 'scene_ready', delay: 700 }, action: { type: 'fadeIn', target: 'input_1', duration: 400 } },
        { id: 'b4', trigger: { type: 'scene_ready', delay: 1000 }, action: { type: 'fadeIn', target: 'output_1', duration: 400 } },
        { id: 'b5', trigger: { type: 'scene_ready', delay: 1500 }, action: { type: 'pulse', target: 'hero_main', duration: 2000, loop: true } },
        { id: 'b6', trigger: { type: 'scene_ready', delay: 2000 }, action: { type: 'flowParticles', from: 'input_1', to: 'hero_main', count: 5 } },
      ],
      narration: [
        { id: 'n1', trigger: { type: 'scene_ready', delay: 0 }, text: `Let's explore: ${concept}`, emphasis: 'normal', duration: 3000 },
        { id: 'n2', trigger: { type: 'scene_ready', delay: 4000 }, text: 'Watch how the process transforms inputs into outputs.', emphasis: 'key_point', duration: 3000 },
        { id: 'n3', trigger: { type: 'scene_ready', delay: 8000 }, text: 'This is the core concept to remember.', emphasis: 'key_point', duration: 3000 },
      ],
      interactions: [],
      stage: {
        width: 720,
        height: 520,
        background: { type: 'gradient', value: colors.background, direction: 'vertical' },
        physics: { enabled: false },
      },
      metadata: { isFallback: true, domain: domain },
    };
  }
  
  /**
   * 🚀 PROGRESSIVE ASYNC COMPOSITION
   * 
   * Returns immediately with a skeleton composition.
   * Polls in background and calls onUpgrade when full composition is ready.
   * 
   * @param {string} question - The question to visualize
   * @param {object} context - Context (domain, intent, etc.)
   * @param {function} onUpgrade - Callback when full composition is ready
   * @returns {object} - Skeleton composition for immediate display
   */
  async callLLMAsyncProgressive(question, context, onUpgrade = null) {
    const startTime = Date.now();
    const registeredTypes = getRegisteredTypes();
    
    const userPrompt = `Question: "${question}"
Domain: ${context.domain || 'general'}
Intent: ${context.intent || 'conceptual'}
Difficulty: ${context.difficulty || 'intermediate'}

Registered atom types: ${registeredTypes.join(', ')}

Create a CompositionSpec that visualizes this concept dynamically and interactively.`;
    
    console.log('════════════════════════════════════════════════════════════');
    console.log(`🚀 [PROGRESSIVE] Starting async composition`);
    console.log(`⏱️ [TIMING] Request started: ${new Date().toISOString()}`);
    console.log(`📤 [QUESTION] "${question.substring(0, 50)}..."`);
    console.log('════════════════════════════════════════════════════════════');
    
    // Step 1: Start async task - returns skeleton immediately
    const startResponse = await fetch(this.options.asyncEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        question, 
        context,
        user: userPrompt,
        system: COMPOSER_SYSTEM_PROMPT,
      }),
    });
    
    if (!startResponse.ok) {
      throw new Error(`Async start failed: ${startResponse.status}`);
    }
    
    const { task_id, skeleton, poll_url } = await startResponse.json();
    console.log(`🎫 [PROGRESSIVE] Task: ${task_id}`);
    console.log(`📦 [PROGRESSIVE] Skeleton ready: ${skeleton?.atoms?.length || 0} atoms`);
    
    // Step 2: Start background polling (non-blocking)
    if (onUpgrade) {
      this._pollForUpgrade(task_id, startTime, onUpgrade);
    }
    
    // Return skeleton immediately for instant display
    return skeleton || this.generateSmartFallback(question, context);
  }

  /**
   * Background polling for full composition upgrade
   */
  async _pollForUpgrade(task_id, startTime, onUpgrade) {
    const pollEndpoint = `${this.options.statusEndpoint}/${task_id}`;
    let pollCount = 0;
    const maxPolls = Math.ceil(ASYNC_MAX_POLL_TIME_MS / ASYNC_POLL_INTERVAL_MS);
    
    while (pollCount < maxPolls) {
      await this.sleep(ASYNC_POLL_INTERVAL_MS);
      pollCount++;
      
      try {
        const statusResponse = await fetch(pollEndpoint);
        if (!statusResponse.ok) {
          console.warn(`⚠️ [UPGRADE] Poll ${pollCount} failed: ${statusResponse.status}`);
          continue;
        }
        
        const result = await statusResponse.json();
        const elapsed = Date.now() - startTime;
        
        if (result.status === 'complete' && result.composition) {
          console.log('════════════════════════════════════════════════════════════');
          console.log(`🎉 [UPGRADE] Full composition ready after ${elapsed}ms`);
          console.log(`📊 [UPGRADE] atoms: ${result.composition?.atoms?.length || 0}`);
          console.log(`📊 [UPGRADE] behaviors: ${result.composition?.behaviors?.length || 0}`);
          console.log('════════════════════════════════════════════════════════════');
          
          // Check if it's a real upgrade (not skeleton/fallback)
          if (!result.composition.context?.isSkeleton && !result.composition.context?.isFallback) {
            onUpgrade(result.composition);
          }
          return;
        }
        
        if (result.status === 'failed') {
          console.error(`❌ [UPGRADE] Task failed: ${result.error}`);
          return;
        }
        
        if (pollCount % 10 === 0) {
          console.log(`⏳ [UPGRADE] Still generating... (${elapsed}ms elapsed)`);
        }
      } catch (err) {
        console.warn(`⚠️ [UPGRADE] Poll error: ${err.message}`);
      }
    }
    
    console.warn(`⏰ [UPGRADE] Timeout - no upgrade after ${ASYNC_MAX_POLL_TIME_MS}ms`);
  }

  /**
   * 🚀 Async LLM call with polling (LEGACY - still supported)
   * - Starts background task
   * - Polls for completion
   * - Returns full composition when ready
   */
  async callLLMAsync(question, context) {
    const startTime = Date.now();
    const registeredTypes = getRegisteredTypes();
    
    // Build user prompt (same format as sync callLLM)
    const userPrompt = `Question: "${question}"
Domain: ${context.domain || 'general'}
Intent: ${context.intent || 'conceptual'}
Difficulty: ${context.difficulty || 'intermediate'}

Registered atom types: ${registeredTypes.join(', ')}

Create a CompositionSpec that visualizes this concept dynamically and interactively.`;
    
    console.log('════════════════════════════════════════════════════════════');
    console.log(`🚀 [ASYNC] POST ${this.options.asyncEndpoint} called`);
    console.log(`⏱️ [TIMING] Async request started: ${new Date().toISOString()}`);
    console.log(`📤 [ASYNC] Question: "${question.substring(0, 50)}..."`);
    console.log('════════════════════════════════════════════════════════════');
    
    // Step 1: Start async task
    const startResponse = await fetch(this.options.asyncEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        question, 
        context,
        user: userPrompt,  // Include formatted prompt
        system: COMPOSER_SYSTEM_PROMPT,
      }),
    });
    
    if (!startResponse.ok) {
      throw new Error(`Async start failed: ${startResponse.status}`);
    }
    
    const { task_id, status, poll_url, skeleton } = await startResponse.json();
    console.log(`🎫 [ASYNC] Task created: ${task_id}`);
    console.log(`📍 [ASYNC] Poll URL: ${poll_url}`);
    console.log(`📦 [ASYNC] Skeleton provided: ${!!skeleton}`);
    
    // Step 2: Poll for completion
    const pollEndpoint = `${this.options.statusEndpoint}/${task_id}`;
    let pollCount = 0;
    const maxPolls = Math.ceil(ASYNC_MAX_POLL_TIME_MS / ASYNC_POLL_INTERVAL_MS);
    
    while (pollCount < maxPolls) {
      await this.sleep(ASYNC_POLL_INTERVAL_MS);
      pollCount++;
      
      const statusResponse = await fetch(pollEndpoint);
      if (!statusResponse.ok) {
        console.warn(`⚠️ [ASYNC] Poll ${pollCount} failed: ${statusResponse.status}`);
        continue;
      }
      
      const result = await statusResponse.json();
      const elapsed = Date.now() - startTime;
      
      console.log(`📊 [ASYNC] Poll ${pollCount}: status=${result.status}, elapsed=${elapsed}ms`);
      
      if (result.status === 'complete') {
        console.log('════════════════════════════════════════════════════════════');
        console.log(`✅ [ASYNC] Task complete after ${elapsed}ms`);
        console.log(`📊 [RESULT] atoms: ${result.composition?.atoms?.length || 0}`);
        console.log(`📊 [RESULT] behaviors: ${result.composition?.behaviors?.length || 0}`);
        console.log(`📊 [RESULT] narration: ${result.composition?.narration?.length || 0}`);
        console.log(`📊 [RESULT] generation_time_ms: ${result.generation_time_ms}`);
        console.log('════════════════════════════════════════════════════════════');
        
          // 🛡️ QUALITY GATE AUTO-FIXER (CRITICAL)
          // Detect diagrams → Convert to procedural simulations
          console.log('🛡️ [QG] Running QualityGate AutoFixer on async result...');
          const { composition: enhanced, qualityReport } = qualityGateAutoFix(result.composition, {
            domain: context.domain || 'physics',
            processType: context.intent || 'transformation',
          });
          
          console.log('🛡️ [QG] Async result:', {
            passed: qualityReport.passed,
            fixesApplied: qualityReport.autoFixApplied.length,
          });
          
          return enhanced;
      }
      
      if (result.status === 'failed') {
        console.error(`❌ [ASYNC] Task failed: ${result.error}`);
        throw new Error(result.error || 'Async composition failed');
      }
      
      // Still pending/generating - continue polling
      if (pollCount % 5 === 0) {
        console.log(`⏳ [ASYNC] Still generating... (${elapsed}ms elapsed)`);
      }
    }
    
    // Timeout after max polls
    throw new Error(`Async composition timeout after ${ASYNC_MAX_POLL_TIME_MS}ms`);
  }
  
  /**
   * Promise-based sleep utility
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  /**
   * Check if composition meets REAL quality threshold (not just counts)
   * 
   * Validates:
   * 1. Scene Direction present (sceneDirection object)
   * 2. Hero Object exists and is LARGE (>= 150px)
   * 3. Environment elements present (Surface, Region, background)
   * 4. Visual fills canvas (atoms spread across coordinate space)
   * 5. Interactions present (at least 1 meaningful control)
   * 6. Visual effects present (pulse, glow, flow, etc.)
   * 7. Choreographed behaviors (not all at delay=0)
   */
  isHighQualityComposition(composition, context = {}) {
    if (!composition) return false;
    
    const atoms = composition.atoms || [];
    const behaviors = composition.behaviors || [];
    const narration = composition.narration || [];
    const interactions = composition.interactions || [];
    const sceneDirection = composition.sceneDirection;
    const ontology = composition.ontology?.type;
    
    console.log('📊 [QUALITY GATE] Evaluating composition...');
    
    // ============================================
    // BASIC COUNT THRESHOLDS
    // ============================================
    if (atoms.length < CACHE_QUALITY_THRESHOLDS.minAtoms) {
      console.log(`📊 [QUALITY] ❌ atoms=${atoms.length} < ${CACHE_QUALITY_THRESHOLDS.minAtoms}`);
      return false;
    }
    if (behaviors.length < CACHE_QUALITY_THRESHOLDS.minBehaviors) {
      console.log(`📊 [QUALITY] ❌ behaviors=${behaviors.length} < ${CACHE_QUALITY_THRESHOLDS.minBehaviors}`);
      return false;
    }
    if (narration.length < CACHE_QUALITY_THRESHOLDS.minNarration) {
      console.log(`📊 [QUALITY] ❌ narration=${narration.length} < ${CACHE_QUALITY_THRESHOLDS.minNarration}`);
      return false;
    }
    
    // Check for fallback/skeleton flags
    if (composition.metadata?.isFallback || composition.context?.isFallback || composition.context?.isSkeleton) {
      console.log('📊 [QUALITY] ❌ isFallback or isSkeleton=true');
      return false;
    }
    
    // ============================================
    // 🎬 SCENE DIRECTION CHECK (NEW)
    // ============================================
    if (!sceneDirection) {
      console.log('📊 [QUALITY] ⚠️ Missing sceneDirection - composition may look like diagram');
      // Don't reject yet - legacy compositions may not have this
    } else {
      console.log('📊 [QUALITY] ✅ sceneDirection present:', sceneDirection.goal?.substring(0, 50));
    }
    
    // ============================================
    // 🦸 HERO OBJECT SIZE CHECK (NEW)
    // ============================================
    const atomTypes = atoms.map(a => a.type);
    const heroTypes = ['Entity', 'RigidBody'];
    const heroAtoms = atoms.filter(a => heroTypes.includes(a.type));
    const largeHero = heroAtoms.find(a => {
      const width = a.params?.width || 0;
      const height = a.params?.height || 0;
      return width >= 100 || height >= 80; // Relaxed from 150 to allow some flexibility
    });
    
    if (!largeHero) {
      console.log('📊 [QUALITY] ⚠️ No large hero object found (need width>=100 or height>=80)');
      // Soft warning - don't reject, LLM may have used different structure
    } else {
      console.log(`📊 [QUALITY] ✅ Hero object: ${largeHero.id} (${largeHero.params?.width}x${largeHero.params?.height})`);
    }
    
    // ============================================
    // 🌍 ENVIRONMENT CHECK (NEW)
    // ============================================
    const envTypes = ['Surface', 'Region', 'Environment'];
    const hasEnvironment = atoms.some(a => envTypes.includes(a.type));
    if (!hasEnvironment) {
      console.log('📊 [QUALITY] ⚠️ No environment element (Surface/Region) - may look like floating diagram');
      // Soft warning
    } else {
      console.log('📊 [QUALITY] ✅ Environment element present');
    }
    
    // ============================================
    // 📐 CANVAS COVERAGE CHECK (NEW)
    // ============================================
    const positions = atoms.map(a => a.position).filter(Boolean);
    if (positions.length > 0) {
      const xs = positions.map(p => p.x || 0);
      const ys = positions.map(p => p.y || 0);
      const minX = Math.min(...xs);
      const maxX = Math.max(...xs);
      const minY = Math.min(...ys);
      const maxY = Math.max(...ys);
      const xSpread = maxX - minX;
      const ySpread = maxY - minY;
      const coverage = Math.max(xSpread, ySpread);
      
      if (coverage < 200) {
        console.log(`📊 [QUALITY] ⚠️ Low canvas coverage: ${coverage}px spread (clustered in corner?)`);
        // Soft warning - could be intentional small scene
      } else {
        console.log(`📊 [QUALITY] ✅ Good canvas coverage: ${xSpread}x${ySpread}px`);
      }
    }
    
    // ============================================
    // 🎮 INTERACTION CHECK (NEW)
    // ============================================
    if (interactions.length === 0) {
      // Check behaviors for interaction triggers
      const hasInteractionBehavior = behaviors.some(b => b.trigger?.type === 'interaction');
      if (!hasInteractionBehavior) {
        console.log('📊 [QUALITY] ⚠️ No interactions defined - visual may be non-interactive');
        // Soft warning
      }
    } else {
      console.log(`📊 [QUALITY] ✅ ${interactions.length} interaction(s) defined`);
    }
    
    // ============================================
    // ✨ VISUAL EFFECTS CHECK (NEW)
    // ============================================
    const effectKeywords = ['pulse', 'glow', 'flow', 'particles', 'trail', 'highlighted'];
    const behaviorTypes = behaviors.map(b => b.action?.type).filter(Boolean);
    const atomsHaveGlow = atoms.some(a => a.params?.glow || a.params?.highlighted);
    const behaviorsHaveEffects = behaviorTypes.some(t => 
      effectKeywords.some(kw => t.toLowerCase().includes(kw))
    );
    
    if (!atomsHaveGlow && !behaviorsHaveEffects) {
      console.log('📊 [QUALITY] ⚠️ No visual effects (pulse, glow, flow) - may look static');
      // Soft warning
    } else {
      console.log('📊 [QUALITY] ✅ Visual effects present');
    }
    
    // ============================================
    // 🎼 CHOREOGRAPHY CHECK (behaviors have delays)
    // ============================================
    const delayedBehaviors = behaviors.filter(b => (b.trigger?.delay || 0) > 0);
    if (delayedBehaviors.length < 3) {
      console.log(`📊 [QUALITY] ⚠️ Only ${delayedBehaviors.length} delayed behaviors - may lack choreography`);
      // Soft warning
    } else {
      console.log(`📊 [QUALITY] ✅ ${delayedBehaviors.length} choreographed behaviors with delays`);
    }
    
    // ============================================
    // ONTOLOGY-SPECIFIC VALIDATION (Interaction Depth)
    // ============================================
    
    // PHYSICAL_MECHANICAL: Must have ForceVector + RigidBody + force-related behavior
    if (ontology === 'physical_mechanical') {
      const hasForceVector = atomTypes.includes('ForceVector');
      const hasRigidBody = atomTypes.includes('RigidBody');
      const hasForceAction = behaviorTypes.some(t => 
        ['applyForce', 'collisionReaction', 'bounce', 'moveTo'].includes(t)
      );
      
      if (!hasForceVector && !hasRigidBody) {
        console.log('📊 [QUALITY] ⚠️ physical_mechanical missing ForceVector or RigidBody');
        // Soft warning - allow through but flag
      }
      if (!hasForceAction) {
        console.log('📊 [QUALITY] ⚠️ physical_mechanical missing force-related action');
        // Soft warning
      }
    }
    
    // SYSTEMIC_CAUSAL: Must have connectors and flow-related behavior
    if (ontology === 'systemic_causal') {
      const hasConnector = atomTypes.includes('Connector');
      const hasFlowAction = behaviorTypes.some(t => 
        ['flowParticles', 'chainReaction', 'cycleLoop', 'drawLine'].includes(t)
      );
      
      if (!hasConnector) {
        console.log('📊 [QUALITY] ⚠️ systemic_causal missing Connector atoms');
      }
      if (!hasFlowAction) {
        console.log('📊 [QUALITY] ⚠️ systemic_causal missing flow-related action');
      }
    }
    
    // CHRONOLOGICAL: Must have timeline/sequence behavior
    if (ontology === 'chronological_evolutionary') {
      const hasSequenceAction = behaviorTypes.some(t => 
        ['timelineReveal', 'stageTransition', 'evolutionPath', 'fadeIn', 'scaleIn'].includes(t)
      );
      
      if (!hasSequenceAction) {
        console.log('📊 [QUALITY] ⚠️ chronological missing sequence action');
      }
    }
    
    // ============================================
    // NARRATIVE STRUCTURE VALIDATION
    // ============================================
    const hasEventTriggers = narration.some(n => 
      n.trigger?.type === 'event' || (n.trigger?.type === 'scene_ready' && n.trigger?.delay > 0)
    );
    if (!hasEventTriggers && narration.length >= 3) {
      console.log('📊 [QUALITY] ⚠️ Narration lacks event triggers - all at delay=0');
    }
    
    // For physics domain legacy check
    const domain = context.domain || composition.context?.domain;
    if (domain === 'physics' && !ontology) {
      const hasRequiredPhysics = CACHE_QUALITY_THRESHOLDS.requiredPhysicsAtoms.some(
        required => atomTypes.includes(required)
      );
      if (!hasRequiredPhysics) {
        console.log('📊 [QUALITY] ⚠️ physics domain missing required atoms:', CACHE_QUALITY_THRESHOLDS.requiredPhysicsAtoms);
      }
    }
    
    console.log('📊 [QUALITY GATE] ✅ PASSED - composition meets minimum thresholds');
    
    console.log(`📊 [QUALITY] ✅ HIGH QUALITY - ontology=${ontology}, atoms=${atoms.length}, behaviors=${behaviors.length}, narration=${narration.length}`);
    return true;
  }

  /**
   * Generate smart fallback based on question analysis
   */
  generateSmartFallback(question, context = {}) {
    const domain = context.domain || this.detectDomain(question);
    const isPhysics = domain === 'physics';
    
    // Extract key concept from question
    const concept = this.extractConcept(question);
    
    // Generate appropriate atoms based on domain
    const atoms = isPhysics 
      ? this.generatePhysicsAtoms(concept, question)
      : this.generateConceptAtoms(concept);
    
    return {
      $schema: 'netra/composition/v1',
      version: '1.0.0',
      id: this.generateId(question, context),
      generatedAt: new Date().toISOString(),
      context: {
        question,
        intent: context.intent || 'conceptual',
        domain,
        difficulty: context.difficulty || 'intermediate',
        isFallback: true,  // 🚨 Mark as fallback - DO NOT CACHE
      },
      metadata: {
        isFallback: true,  // 🚨 Duplicate flag for redundancy
        source: 'frontend_fallback',
      },
      atoms,
      behaviors: this.generateBehaviors(atoms),
      narration: this.generateNarration(question, concept, atoms),
      interactions: [],
      stage: {
        width: 800,
        height: 600,
        background: { 
          type: 'gradient', 
          value: isPhysics ? ['#f0f9ff', '#dbeafe'] : ['#faf5ff', '#ede9fe'],
          direction: 'vertical'
        },
        physics: { enabled: isPhysics, gravity: { x: 0, y: isPhysics ? 0.5 : 0 } }
      }
    };
  }

  detectDomain(question) {
    const q = question.toLowerCase();
    if (/force|motion|gravity|friction|velocity|acceleration|newton|energy|momentum|mass/.test(q)) return 'physics';
    if (/atom|molecule|reaction|element|bond|chemical|electron|ion/.test(q)) return 'chemistry';
    if (/cell|dna|protein|organism|biology|gene|photosynthesis|respiration|mitosis|meiosis|enzyme|chlorophyll/.test(q)) return 'biology';
    if (/equation|algebra|calculus|geometry|function|graph|derivative|integral/.test(q)) return 'math';
    return 'general';
  }

  generatePhysicsAtoms(concept, question) {
    const q = question.toLowerCase();
    const atoms = [];
    
    // Add surface/ground
    atoms.push({
      id: 'ground',
      type: 'Surface',
      params: { 
        width: 700, 
        height: 30, 
        friction: 0.3,
        texture: 'rough',
        fill: '#78716C',
        label: 'Surface'
      },
      position: { x: 400, y: 520 }
    });

    // Add main body based on context
    if (/block|box|object|mass/.test(q)) {
      atoms.push({
        id: 'main_body',
        type: 'RigidBody',
        params: {
          shape: 'rect',
          width: 80,
          height: 60,
          mass: 5,
          fill: '#3B82F6',
          stroke: '#1D4ED8',
          label: concept.substring(0, 10)
        },
        position: { x: 300, y: 450 }
      });
    } else {
      atoms.push({
        id: 'main_body',
        type: 'RigidBody',
        params: {
          shape: 'circle',
          radius: 35,
          mass: 2,
          fill: '#EF4444',
          stroke: '#B91C1C',
          label: 'Object'
        },
        position: { x: 300, y: 420 }
      });
    }

    // Add force vectors based on context
    if (/force|push|pull|friction/.test(q)) {
      atoms.push({
        id: 'applied_force',
        type: 'ForceVector',
        params: {
          magnitude: 80,
          direction: 0,
          color: '#22C55E',
          label: 'F',
          animated: true
        },
        position: { x: 300, y: 450 },
        attachedTo: 'main_body'
      });
    }

    if (/friction/.test(q)) {
      atoms.push({
        id: 'friction_force',
        type: 'ForceVector',
        params: {
          magnitude: 50,
          direction: 180,
          color: '#F97316',
          label: 'f',
          animated: true
        },
        position: { x: 300, y: 480 },
        attachedTo: 'main_body'
      });
    }

    // Add labels
    atoms.push({
      id: 'title_label',
      type: 'Label',
      params: {
        text: concept,
        fontSize: 20,
        color: '#1F2937',
        backgroundColor: 'rgba(255,255,255,0.9)',
        padding: 12
      },
      position: { x: 400, y: 60 }
    });

    return atoms;
  }

  generateConceptAtoms(concept) {
    return [
      {
        id: 'main_concept',
        type: 'Entity',
        params: {
          shape: 'rect',
          width: 180,
          height: 90,
          fill: '#8B5CF6',
          stroke: '#6D28D9',
          cornerRadius: 12,
          label: concept.substring(0, 20),
          shadow: true
        },
        position: { x: 400, y: 300 }
      },
      {
        id: 'title_label',
        type: 'Label',
        params: {
          text: concept,
          fontSize: 18,
          color: '#1F2937',
          backgroundColor: 'rgba(255,255,255,0.95)',
          padding: 10
        },
        position: { x: 400, y: 80 }
      }
    ];
  }

  generateBehaviors(atoms) {
    const behaviors = [
      {
        id: 'show_title',
        trigger: { type: 'scene_ready' },
        action: { type: 'show', target: 'title_label' },
        once: true
      }
    ];

    // Add sequential show behaviors
    atoms.forEach((atom, i) => {
      if (atom.id !== 'title_label') {
        behaviors.push({
          id: `show_${atom.id}`,
          trigger: { type: 'scene_ready', delay: 300 + i * 400 },
          action: { type: 'show', target: atom.id },
          once: true
        });
      }
    });

    return behaviors;
  }

  generateNarration(question, concept, atoms) {
    const narrations = [
      {
        id: 'intro',
        trigger: { type: 'scene_ready' },
        text: `Let's explore: ${concept}`,
        emphasis: 'normal',
        duration: 2500
      }
    ];

    // Add narration for physics concepts
    const hasForce = atoms.some(a => a.type === 'ForceVector');
    const hasBody = atoms.some(a => a.type === 'RigidBody');

    if (hasBody) {
      narrations.push({
        id: 'body_intro',
        trigger: { type: 'event', source: 'main_body', event: 'shown' },
        text: 'Here we have our object that will experience the forces.',
        emphasis: 'normal',
        duration: 3000
      });
    }

    if (hasForce) {
      narrations.push({
        id: 'force_intro',
        trigger: { type: 'event', source: 'applied_force', event: 'shown' },
        text: 'The green arrow shows the applied force acting on the object.',
        emphasis: 'key_point',
        duration: 3500
      });
    }

    return narrations;
  }

  /**
   * Call LLM API
   */
  async callLLM(question, context) {
    const registeredTypes = getRegisteredTypes();
    
    const userPrompt = `Question: "${question}"
Domain: ${context.domain || 'general'}
Intent: ${context.intent || 'conceptual'}
Difficulty: ${context.difficulty || 'intermediate'}

Registered atom types: ${registeredTypes.join(', ')}

Create a CompositionSpec that visualizes this concept dynamically and interactively.`;

    const requestStartTime = Date.now();
    console.log('════════════════════════════════════════════════════════════');
    console.log(`🌐 [API] POST ${this.options.apiEndpoint} called`);
    console.log(`⏱️ [TIMING] API request started: ${new Date().toISOString()}`);
    console.log(`📤 [REQUEST] question: "${question.substring(0, 60)}..."`);
    console.log(`📤 [REQUEST] domain: ${context.domain}, intent: ${context.intent}`);
    console.log('════════════════════════════════════════════════════════════');
    
    // Create abort controller for timeout (more compatible than AbortSignal.timeout)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.options.timeout);
    
    try {
      const response = await fetch(this.options.apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          system: COMPOSER_SYSTEM_PROMPT,
          user: userPrompt,
          question,
          context
        }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      const networkTime = Date.now() - requestStartTime;
      console.log(`⏱️ [TIMING] API network response: ${networkTime}ms`);

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      const totalTime = Date.now() - requestStartTime;
      
      // ============================================
      // RESULT LOGGING (VERIFY REAL BACKEND CALL)
      // ============================================
      const atomCount = data.composition?.atoms?.length || 0;
      const behaviorCount = data.composition?.behaviors?.length || 0;
      const narrationCount = data.composition?.narration?.length || 0;
      
      console.log('════════════════════════════════════════════════════════════');
      console.log(`📥 [RESULT] Backend response received`);
      console.log(`⏱️ [TIMING] Total API time: ${totalTime}ms`);
      console.log(`📊 [RESULT] success: ${data.success}`);
      console.log(`📊 [RESULT] atoms: ${atomCount} ${atomCount >= 4 ? '✅' : '⚠️ LOW'}`);
      console.log(`📊 [RESULT] behaviors: ${behaviorCount} ${behaviorCount >= 2 ? '✅' : '⚠️ LOW'}`);
      console.log(`📊 [RESULT] narration: ${narrationCount} ${narrationCount >= 2 ? '✅' : '⚠️ LOW'}`);
      console.log(`📊 [RESULT] isFallback: ${data.fallback || false}`);
      console.log('════════════════════════════════════════════════════════════');
      
      // Mark if this was a backend fallback
      if (data.fallback) {
        data.composition.metadata = { ...data.composition?.metadata, isFallback: true };
      }
      
      return data.composition || data;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new Error(`API timeout after ${this.options.timeout}ms`);
      }
      throw error;
    }
  }

  /**
   * Validate and fix composition spec
   */
  validateAndFix(spec, question, context) {
    const errors = [];
    const fixed = { ...spec };

    // Ensure required fields
    fixed.$schema = 'netra/composition/v1';
    fixed.version = '1.0.0';
    fixed.id = fixed.id || this.generateId(question, context);
    fixed.generatedAt = fixed.generatedAt || new Date().toISOString();
    
    // Fix context
    fixed.context = {
      question,
      intent: context.intent || 'conceptual',
      domain: context.domain || 'general',
      difficulty: context.difficulty || 'intermediate',
      ...fixed.context
    };

    // Fix atoms
    fixed.atoms = (fixed.atoms || []).slice(0, COMPOSITION_LIMITS.MAX_ATOMS);
    fixed.atoms = fixed.atoms.map((atom, i) => this.fixAtom(atom, i, errors));
    fixed.atoms = fixed.atoms.filter(a => a !== null);
    
    // CRITICAL: If no atoms after fixing, generate fallback atoms
    if (fixed.atoms.length === 0) {
      console.warn('[VisualComposer] No atoms after validation - generating fallback atoms');
      const domain = context.domain || this.detectDomain(question);
      fixed.atoms = domain === 'physics' 
        ? this.generatePhysicsAtoms(this.extractConcept(question), question)
        : this.generateConceptAtoms(this.extractConcept(question));
    }

    // Fix behaviors
    fixed.behaviors = (fixed.behaviors || []).slice(0, COMPOSITION_LIMITS.MAX_BEHAVIORS);
    fixed.behaviors = fixed.behaviors.map((b, i) => this.fixBehavior(b, i, fixed.atoms));
    fixed.behaviors = fixed.behaviors.filter(b => b !== null);

    // Fix narration
    fixed.narration = (fixed.narration || []).slice(0, COMPOSITION_LIMITS.MAX_NARRATION_CUES);
    fixed.narration = fixed.narration.map((n, i) => this.fixNarration(n, i));
    fixed.narration = fixed.narration.filter(n => n !== null);

    // Fix interactions
    fixed.interactions = (fixed.interactions || []).slice(0, COMPOSITION_LIMITS.MAX_INTERACTIONS);

    // Fix stage
    fixed.stage = this.fixStage(fixed.stage);

    if (errors.length > 0) {
      console.warn('[VisualComposer] Fixed errors:', errors);
    }

    return fixed;
  }

  /**
   * Fix atom instance
   */
  fixAtom(atom, index, errors) {
    if (!atom) return null;

    // Fix ID
    if (!atom.id || !isValidId(atom.id)) {
      atom.id = `atom_${index}`;
      errors.push(`Fixed invalid atom ID at index ${index}`);
    }

    // Fix type
    if (!isValidAtomType(atom.type)) {
      // Try to map common alternatives
      const typeMap = {
        'box': 'Entity',
        'rectangle': 'Entity',
        'circle': 'Entity',
        'text': 'Label',
        'arrow': 'Connector',
        'force': 'ForceVector',
        'body': 'RigidBody',
        'ground': 'Surface',
        'floor': 'Surface'
      };
      
      const mappedType = typeMap[atom.type?.toLowerCase()];
      if (mappedType) {
        atom.type = mappedType;
        errors.push(`Mapped atom type ${atom.type} → ${mappedType}`);
      } else {
        atom.type = 'Entity';
        errors.push(`Unknown atom type, defaulted to Entity`);
      }
    }

    // Ensure params object
    atom.params = atom.params || {};

    return atom;
  }

  /**
   * Fix behavior rule
   */
  fixBehavior(behavior, index, atoms) {
    if (!behavior) return null;

    // Fix ID
    if (!behavior.id) {
      behavior.id = `behavior_${index}`;
    }

    // Ensure trigger
    if (!behavior.trigger) {
      behavior.trigger = { type: 'scene_ready' };
    }

    // Ensure action
    if (!behavior.action) {
      return null; // Invalid behavior
    }

    // Validate target exists
    const targetExists = atoms.some(a => a.id === behavior.action.target) || 
                         behavior.action.target === 'scene';
    if (!targetExists && atoms.length > 0) {
      behavior.action.target = atoms[0].id;
    }

    return behavior;
  }

  /**
   * Fix narration cue
   */
  fixNarration(cue, index) {
    if (!cue || !cue.text) return null;

    // Fix ID
    if (!cue.id) {
      cue.id = `narration_${index}`;
    }

    // Ensure trigger (default to scene_ready for first, then stagger)
    if (!cue.trigger) {
      cue.trigger = index === 0 
        ? { type: 'scene_ready' }
        : { type: 'time', time: index * 3000 };
    }

    // Truncate text
    if (cue.text.length > COMPOSITION_LIMITS.MAX_NARRATION_TEXT) {
      cue.text = cue.text.substring(0, COMPOSITION_LIMITS.MAX_NARRATION_TEXT - 3) + '...';
    }

    return cue;
  }

  /**
   * Fix stage config
   */
  fixStage(stage) {
    const fixed = stage || {};

    fixed.width = Math.max(
      COMPOSITION_LIMITS.STAGE_WIDTH_MIN,
      Math.min(COMPOSITION_LIMITS.STAGE_WIDTH_MAX, fixed.width || 800)
    );

    fixed.height = Math.max(
      COMPOSITION_LIMITS.STAGE_HEIGHT_MIN,
      Math.min(COMPOSITION_LIMITS.STAGE_HEIGHT_MAX, fixed.height || 600)
    );

    fixed.background = fixed.background || {
      type: 'gradient',
      value: ['#f0f9ff', '#e0f2fe'],
      direction: 'vertical'
    };

    fixed.physics = fixed.physics || { enabled: false };

    return fixed;
  }

  /**
   * Generate fallback composition
   */
  generateFallback(question, context) {
    const id = this.generateId(question, context);
    const domain = context.domain || 'general';
    
    return {
      $schema: 'netra/composition/v1',
      version: '1.0.0',
      id,
      generatedAt: new Date().toISOString(),
      context: {
        question,
        intent: context.intent || 'conceptual',
        domain,
        difficulty: context.difficulty || 'intermediate'
      },
      atoms: [
        {
          id: 'main_concept',
          type: 'Entity',
          params: {
            shape: 'rect',
            width: 160,
            height: 80,
            fill: '#3B82F6',
            label: this.extractConcept(question)
          },
          position: { x: 400, y: 300 }
        },
        {
          id: 'concept_label',
          type: 'Label',
          params: {
            text: question.length > 60 ? question.substring(0, 57) + '...' : question,
            fontSize: 14,
            color: '#6B7280'
          },
          position: { x: 400, y: 400 }
        }
      ],
      behaviors: [
        {
          id: 'show_concept',
          trigger: { type: 'scene_ready' },
          action: { type: 'show', target: 'main_concept' }
        }
      ],
      narration: [
        {
          id: 'intro',
          trigger: { type: 'scene_ready' },
          text: `Let's explore: ${this.extractConcept(question)}`,
          emphasis: 'normal',
          duration: 3000
        }
      ],
      interactions: [],
      stage: {
        width: 800,
        height: 600,
        background: { type: 'solid', value: '#F8FAFC' },
        physics: { enabled: false }
      }
    };
  }

  /**
   * Extract concept from question
   */
  extractConcept(question) {
    // Remove common prefixes
    let concept = question
      .replace(/^(explain|what is|describe|show|tell me about|how does)\s+/i, '')
      .replace(/\?$/, '')
      .trim();
    
    // Capitalize first letter
    return concept.charAt(0).toUpperCase() + concept.slice(1);
  }

  /**
   * Generate deterministic ID
   */
  generateId(question, context) {
    const input = `${question}-${context.domain || ''}-${context.intent || ''}`;
    let hash = 0;
    for (let i = 0; i < input.length; i++) {
      const char = input.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return `comp_${Math.abs(hash).toString(16)}`;
  }

  /**
   * Get cache key
   */
  getCacheKey(question, context) {
    return `${question.toLowerCase().trim()}_${context.domain || ''}_${context.intent || ''}`;
  }

  /**
   * Clear all caches (DEV utility)
   */
  clearCache() {
    const cacheSize = this.cache.size;
    this.cache.clear();
    console.log(`🗑️ [CACHE] cleared successfully - removed ${cacheSize} entries`);
    
    // Also clear any localStorage/sessionStorage keys related to netra
    try {
      const keysToRemove = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && (key.includes('netra') || key.includes('composition') || key.includes('visual'))) {
          keysToRemove.push(key);
        }
      }
      keysToRemove.forEach(key => {
        localStorage.removeItem(key);
        console.log(`🗑️ [CACHE] localStorage removed: ${key}`);
      });
      
      // SessionStorage
      const sessionKeysToRemove = [];
      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        if (key && (key.includes('netra') || key.includes('composition') || key.includes('visual'))) {
          sessionKeysToRemove.push(key);
        }
      }
      sessionKeysToRemove.forEach(key => {
        sessionStorage.removeItem(key);
        console.log(`🗑️ [CACHE] sessionStorage removed: ${key}`);
      });
      
      console.log('✅ [CACHE] All Netra caches cleared successfully');
    } catch (e) {
      console.warn('[CACHE] Could not clear browser storage:', e.message);
    }
  }
  
  /**
   * Get cache stats (DEV utility)
   */
  getCacheStats() {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()).map(k => k.substring(0, 50)),
    };
  }
}

// ============================================
// GLOBAL CACHE CLEAR UTILITY (DEV)
// ============================================
// Usage in browser console: window.clearNetraCache()
if (typeof window !== 'undefined') {
  window.clearNetraCache = () => {
    console.log('🧹 [DEV] Clearing all Netra caches...');
    
    // Clear any global composer instances
    if (window.__netraComposer) {
      window.__netraComposer.clearCache();
    }
    
    // Clear localStorage/sessionStorage
    const keysToRemove = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && (key.includes('netra') || key.includes('composition') || key.includes('visual'))) {
        keysToRemove.push(key);
      }
    }
    keysToRemove.forEach(key => localStorage.removeItem(key));
    
    console.log('✅ [CACHE] cleared successfully');
    return 'Netra cache cleared!';
  };
  
  // Expose force fresh toggle
  window.setNetraForceFresh = (value) => {
    console.log(`🔧 [DEV] FORCE_FRESH_COMPOSE is a compile-time constant.`);
    console.log(`To change it, edit VisualComposer.js line ~80`);
    return 'See console for instructions';
  };
}

export function createVisualComposer(options) {
  const composer = new VisualComposer(options);
  
  // Register globally for DEV cache clear utility
  if (typeof window !== 'undefined') {
    window.__netraComposer = composer;
    console.log('🎨 [VisualComposer] Registered globally as window.__netraComposer');
    console.log('🎨 [VisualComposer] Use window.clearNetraCache() to clear all caches');
  }
  
  return composer;
}

export default VisualComposer;
