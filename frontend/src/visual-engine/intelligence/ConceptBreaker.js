/**
 * 🧠 CONCEPT BREAKER
 * ==================
 * 
 * The Semantic Brain - Turns questions into visual blueprints
 * 
 * Hybrid Intelligence:
 * - Primary: GPT-4o-mini (via backend API)
 * - Fallback: Rule-based pattern matching
 * - Validation: Schema validation + sanity checks
 * - Cache: Repeated questions (via React Query)
 * 
 * Input: Natural language question
 * Output: Structured visual blueprint
 */

import { apiClient } from '../../api/client';

// ============================================
// MODE DETECTION
// ============================================

/**
 * 8 Master Modes (from PRD)
 */
export const VISUAL_MODES = {
  SCENE: 'SCENE',               // Physical scenarios, forces, motion
  COMPARISON: 'COMPARISON',     // X vs Y (split view)
  PROCESS: 'PROCESS',           // Step-wise flows
  CYCLE: 'CYCLE',               // Loops (water cycle, Krebs)
  STRUCTURE: 'STRUCTURE',       // Labeled diagrams (heart, atom)
  GRAPH: 'GRAPH',               // Math plots
  TIMELINE: 'TIMELINE',         // Historical / chronological
  HIERARCHY: 'HIERARCHY',       // Trees (taxonomy, number systems)
};

/**
 * Mode keywords for rule-based fallback
 */
const MODE_KEYWORDS = {
  [VISUAL_MODES.SCENE]: ['force', 'motion', 'velocity', 'acceleration', 'push', 'pull', 'friction', 'momentum'],
  [VISUAL_MODES.COMPARISON]: ['vs', 'versus', 'compare', 'difference between', 'contrast'],
  [VISUAL_MODES.PROCESS]: ['process', 'step', 'flow', 'how to', 'procedure', 'mechanism'],
  [VISUAL_MODES.CYCLE]: ['cycle', 'loop', 'circular', 'repeat', 'krebs', 'calvin', 'water cycle'],
  [VISUAL_MODES.STRUCTURE]: ['structure', 'anatomy', 'parts', 'labeled', 'diagram', 'atom', 'heart', 'cell'],
  [VISUAL_MODES.GRAPH]: ['graph', 'plot', 'function', 'equation', 'curve', 'y=', 'f(x)'],
  [VISUAL_MODES.TIMELINE]: ['timeline', 'history', 'sequence', 'chronological', 'evolution', 'before', 'after'],
  [VISUAL_MODES.HIERARCHY]: ['hierarchy', 'tree', 'classification', 'taxonomy', 'family tree', 'organization'],
};

// Note: INDIAN_METAPHORS moved to metaphors/MetaphorDatabase.js (Phase 8)
// Importing from centralized metaphor system
import { findMetaphorByKeyword } from '../metaphors/MetaphorDatabase';

// ============================================
// CONCEPT BREAKER CLASS
// ============================================

export class ConceptBreaker {
  constructor(options = {}) {
    this.options = {
      useLLM: true,                // Enable GPT-4o-mini
      useFallback: true,           // Enable rule-based fallback
      cacheEnabled: true,          // Cache repeated questions
      validateOutput: true,        // Validate before returning
      model: 'gpt-4o-mini',        // Model name (for backend)
      ...options,
    };
    
    this.cache = new Map();
  }
  
  /**
   * Main method: Break down question into blueprint
   * @param {string} question - Natural language question
   * @param {Object} context - Additional context (subject, level, etc.)
   * @returns {Promise<Object>} Visual blueprint
   */
  async break(question, context = {}) {
    const {
      subject = 'general',
      level = 'high_school',
      language = 'en',
      preferMetaphor = null,
    } = context;
    
    // Check cache first
    const cacheKey = this.getCacheKey(question, context);
    if (this.options.cacheEnabled && this.cache.has(cacheKey)) {
      console.log('📦 ConceptBreaker: Cache hit');
      return this.cache.get(cacheKey);
    }
    
    let blueprint = null;
    
    // Try LLM first
    if (this.options.useLLM) {
      try {
        blueprint = await this.breakWithLLM(question, context);
        console.log('🤖 ConceptBreaker: LLM success');
      } catch (error) {
        console.warn('⚠️ ConceptBreaker: LLM failed, trying fallback', error);
      }
    }
    
    // Try rule-based fallback
    if (!blueprint && this.options.useFallback) {
      blueprint = this.breakWithRules(question, context);
      console.log('📜 ConceptBreaker: Rule-based fallback');
    }
    
    // Validate output
    if (this.options.validateOutput && blueprint) {
      blueprint = this.validateBlueprint(blueprint);
    }
    
    // Cache result
    if (blueprint && this.options.cacheEnabled) {
      this.cache.set(cacheKey, blueprint);
    }
    
    return blueprint;
  }
  
  /**
   * Break using GPT-4o-mini (via backend)
   */
  async breakWithLLM(question, context) {
    const response = await apiClient.post('/ai/visual-engine/concept-break', {
      question,
      context,
      model: this.options.model,
    });
    
    return response.data.blueprint;
  }
  
  /**
   * Break using rule-based patterns (fallback)
   */
  breakWithRules(question, context) {
    const questionLower = question.toLowerCase();
    
    // Detect mode
    const mode = this.detectMode(questionLower);
    
    // Extract entities (simple keyword extraction)
    const entities = this.extractEntities(questionLower, context.subject);
    
    // Detect metaphor
    const metaphor = this.detectMetaphor(questionLower);
    
    // Generate 5-beat narrative
    const beats = this.generateDefaultBeats(question, mode);
    
    // Build blueprint
    return {
      mode,
      concept: this.extractConcept(question),
      subject: context.subject,
      level: context.level,
      metaphor,
      entities,
      relations: this.inferRelations(entities),
      controls: this.suggestControls(mode, entities),
      beats,
      highlights: [],
      confidence: 0.6, // Lower confidence for rule-based
      method: 'rules',
    };
  }
  
  /**
   * Detect mode from question keywords
   */
  detectMode(questionLower) {
    for (const [mode, keywords] of Object.entries(MODE_KEYWORDS)) {
      if (keywords.some(kw => questionLower.includes(kw))) {
        return mode;
      }
    }
    
    // Default mode
    return VISUAL_MODES.SCENE;
  }
  
  /**
   * Extract entities from question
   */
  extractEntities(questionLower, subject) {
    const entities = [];
    
    // Subject-specific entity detection
    if (subject === 'physics') {
      const physicsTerms = ['ball', 'block', 'force', 'mass', 'velocity', 'acceleration', 'energy'];
      physicsTerms.forEach((term, index) => {
        if (questionLower.includes(term)) {
          entities.push({
            id: `entity_${index}`,
            type: 'circle',
            label: term.charAt(0).toUpperCase() + term.slice(1),
            radius: 30,
          });
        }
      });
    } else if (subject === 'chemistry') {
      const chemTerms = ['atom', 'molecule', 'bond', 'electron', 'proton', 'neutron'];
      chemTerms.forEach((term, index) => {
        if (questionLower.includes(term)) {
          entities.push({
            id: `entity_${index}`,
            type: 'circle',
            label: term.charAt(0).toUpperCase() + term.slice(1),
            radius: 25,
          });
        }
      });
    } else if (subject === 'biology') {
      const bioTerms = ['cell', 'heart', 'lung', 'blood', 'organ', 'tissue'];
      bioTerms.forEach((term, index) => {
        if (questionLower.includes(term)) {
          entities.push({
            id: `entity_${index}`,
            type: 'circle',
            label: term.charAt(0).toUpperCase() + term.slice(1),
            radius: 35,
          });
        }
      });
    }
    
    // If no entities found, create generic ones
    if (entities.length === 0) {
      entities.push(
        { id: 'entity_0', type: 'circle', label: 'Object A', radius: 30 },
        { id: 'entity_1', type: 'circle', label: 'Object B', radius: 30 }
      );
    }
    
    return entities;
  }
  
  /**
   * Infer relations between entities
   */
  inferRelations(entities) {
    if (entities.length < 2) return [];
    
    return [
      {
        from: entities[0].id,
        to: entities[1].id,
        label: 'affects',
        style: 'default',
      },
    ];
  }
  
  /**
   * Suggest interactive controls based on mode
   */
  suggestControls(mode, entities) {
    const controls = [];
    
    if (mode === VISUAL_MODES.SCENE) {
      controls.push({
        id: 'speed_slider',
        type: 'slider',
        label: 'Speed',
        min: 0,
        max: 100,
        default: 50,
        target: entities[0]?.id,
      });
    } else if (mode === VISUAL_MODES.GRAPH) {
      controls.push({
        id: 'x_slider',
        type: 'slider',
        label: 'X',
        min: -10,
        max: 10,
        default: 0,
      });
    }
    
    return controls;
  }
  
  /**
   * Extract main concept from question
   */
  extractConcept(question) {
    // Simple heuristic: Take first few words after common question starters
    const questionLower = question.toLowerCase();
    const starters = ['explain', 'what is', 'how does', 'why', 'show me'];
    
    for (const starter of starters) {
      if (questionLower.startsWith(starter)) {
        return question.substring(starter.length).trim().split('.')[0];
      }
    }
    
    // Fallback: Use first 5 words
    return question.split(' ').slice(0, 5).join(' ');
  }
  
  /**
   * Detect Indian metaphor from question
   */
  detectMetaphor(questionLower) {
    // Use centralized metaphor detection (Phase 8)
    const metaphor = findMetaphorByKeyword(questionLower);
    return metaphor?.id || null;
  }
  
  /**
   * Generate default 5-beat narrative
   */
  generateDefaultBeats(question, mode) {
    const concept = this.extractConcept(question);
    
    return [
      {
        beat: 1,
        text: `Let me show you ${concept}...`,
        duration: 2,
      },
      {
        beat: 2,
        text: "Here's the main idea:",
        drawItems: ['entity_0'],
        duration: 2,
      },
      {
        beat: 3,
        text: 'See how this connects...',
        drawItems: ['entity_1'],
        duration: 2,
      },
      {
        beat: 4,
        text: 'The key insight is:',
        highlightItems: ['entity_0', 'entity_1'],
        pause: true,
        duration: 2,
      },
      {
        beat: 5,
        text: "Now you'll never forget! 💪",
        duration: 2,
      },
    ];
  }
  
  /**
   * Validate blueprint structure
   */
  validateBlueprint(blueprint) {
    // Ensure required fields
    const validated = {
      mode: blueprint.mode || VISUAL_MODES.SCENE,
      concept: blueprint.concept || 'Concept',
      subject: blueprint.subject || 'general',
      entities: Array.isArray(blueprint.entities) ? blueprint.entities : [],
      relations: Array.isArray(blueprint.relations) ? blueprint.relations : [],
      controls: Array.isArray(blueprint.controls) ? blueprint.controls : [],
      beats: Array.isArray(blueprint.beats) ? blueprint.beats : this.generateDefaultBeats('', blueprint.mode),
      metaphor: blueprint.metaphor || null,
      highlights: blueprint.highlights || [],
    };
    
    // Ensure entity IDs are unique
    const seenIds = new Set();
    validated.entities = validated.entities.filter(entity => {
      if (seenIds.has(entity.id)) return false;
      seenIds.add(entity.id);
      return true;
    });
    
    return validated;
  }
  
  /**
   * Get cache key for question + context
   */
  getCacheKey(question, context) {
    return `${question.toLowerCase()}_${context.subject}_${context.level}`;
  }
  
  /**
   * Clear cache
   */
  clearCache() {
    this.cache.clear();
  }
}

// ============================================
// REACT QUERY INTEGRATION
// ============================================

/**
 * Add ConceptBreaker endpoints to aiAPI
 */
export const conceptBreakerAPI = {
  break: (question, context) =>
    apiClient.post('/ai/visual-engine/concept-break', {
      question,
      context,
      model: 'gpt-4o-mini',
    }),
};

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Create a ConceptBreaker instance
 */
export function createConceptBreaker(options) {
  return new ConceptBreaker(options);
}

/**
 * Quick break helper
 */
export async function breakConcept(question, context, options) {
  const breaker = new ConceptBreaker(options);
  return await breaker.break(question, context);
}

export default ConceptBreaker;

