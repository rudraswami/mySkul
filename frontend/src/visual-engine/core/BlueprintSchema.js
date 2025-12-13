/**
 * 📐 Blueprint Schema & Validation
 * =================================
 * 
 * JSON schema for visual blueprints consumed by UniversalSketchRenderer
 */

// ============================================
// BLUEPRINT SCHEMA
// ============================================

/**
 * @typedef {Object} BlueprintItem
 * @property {string} id - Unique identifier
 * @property {'circle'|'rect'|'node'|'path'} type - Shape type
 * @property {string} [label] - Text label
 * @property {{x: number, y: number}} [position] - Absolute position
 * @property {number} [radius] - Circle radius
 * @property {number} [width] - Rectangle width
 * @property {number} [height] - Rectangle height
 * @property {string} [fill] - Fill color
 * @property {string} [stroke] - Stroke color
 * @property {string} [d] - SVG path data (for path type)
 */

/**
 * @typedef {Object} BlueprintArrow
 * @property {string} from - Source item ID
 * @property {string} to - Target item ID
 * @property {string} [label] - Arrow label
 * @property {string} [style] - 'default' | 'energy' | 'flow'
 * @property {boolean} [curved] - Use curved arrow
 */

/**
 * @typedef {Object} BlueprintLabel
 * @property {string} text - Label text
 * @property {number} x - X position
 * @property {number} y - Y position
 * @property {number} [fontSize] - Font size
 * @property {string} [color] - Text color
 * @property {boolean} [underline] - Underline text
 * @property {boolean} [typewriter] - Use typewriter effect
 */

/**
 * @typedef {Object} BlueprintFigure
 * @property {number} x - X position
 * @property {number} y - Y position
 * @property {number} [size] - Figure size
 * @property {'standing'|'pushing'|'running'|'thinking'} [pose] - Figure pose
 * @property {'happy'|'sad'|'surprised'|'neutral'} [expression] - Face expression
 */

/**
 * @typedef {Object} BlueprintDoodle
 * @property {number} x - X position
 * @property {number} y - Y position
 * @property {'star'|'sparkle'|'spiral'|'burst'|'cloud'} type - Doodle type
 * @property {number} [size] - Doodle size
 * @property {string} [color] - Doodle color
 */

/**
 * @typedef {Object} BlueprintControl
 * @property {string} id - Control identifier
 * @property {'slider'|'toggle'|'button'} type - Control type
 * @property {string} label - Control label
 * @property {number} [min] - Slider min value
 * @property {number} [max] - Slider max value
 * @property {number} [value] - Initial value
 * @property {string} [color] - Control color
 */

/**
 * @typedef {Object} NarrativeBeat
 * @property {number} beat - Beat number (1-5)
 * @property {string} text - Narrative text
 * @property {string[]} [drawItems] - Item IDs to draw in this beat
 * @property {string[]} [highlightItems] - Item IDs to highlight
 * @property {boolean} [pause] - Pause after this beat
 * @property {number} [duration] - Beat duration in seconds
 */

/**
 * @typedef {Object} Blueprint
 * @property {'SCENE'|'COMPARISON'|'PROCESS'|'CYCLE'|'STRUCTURE'|'GRAPH'|'TIMELINE'|'HIERARCHY'} mode - Rendering mode
 * @property {string} [concept] - Main concept
 * @property {string} [subject] - Subject (physics, chemistry, biology, math)
 * @property {BlueprintItem[]} [items] - Shapes to draw
 * @property {BlueprintArrow[]} [arrows] - Connections
 * @property {BlueprintLabel[]} [labels] - Text labels
 * @property {string[]} [highlights] - Item IDs to highlight
 * @property {BlueprintFigure[]} [figures] - Stick figures
 * @property {BlueprintDoodle[]} [doodles] - Decorative elements
 * @property {BlueprintControl[]} [controls] - Interactive controls
 * @property {NarrativeBeat[]} [beats] - 5-beat narrative structure
 * @property {string} [metaphor] - Cultural metaphor ('cricket', 'chai', etc.)
 */

// ============================================
// VALIDATION FUNCTIONS
// ============================================

/**
 * Validate a blueprint object
 * @param {Blueprint} blueprint - Blueprint to validate
 * @returns {{valid: boolean, errors: string[]}}
 */
export function validateBlueprint(blueprint) {
  const errors = [];
  
  if (!blueprint || typeof blueprint !== 'object') {
    return { valid: false, errors: ['Blueprint must be an object'] };
  }
  
  // Validate mode
  const validModes = ['SCENE', 'COMPARISON', 'PROCESS', 'CYCLE', 'STRUCTURE', 'GRAPH', 'TIMELINE', 'HIERARCHY'];
  if (blueprint.mode && !validModes.includes(blueprint.mode)) {
    errors.push(`Invalid mode: ${blueprint.mode}. Must be one of: ${validModes.join(', ')}`);
  }
  
  // Validate items
  if (blueprint.items && !Array.isArray(blueprint.items)) {
    errors.push('items must be an array');
  } else if (blueprint.items) {
    blueprint.items.forEach((item, i) => {
      if (!item.id) errors.push(`Item ${i} missing required 'id' field`);
      if (!item.type) errors.push(`Item ${i} missing required 'type' field`);
      if (!['circle', 'rect', 'node', 'path'].includes(item.type)) {
        errors.push(`Item ${i} has invalid type: ${item.type}`);
      }
    });
  }
  
  // Validate arrows
  if (blueprint.arrows && !Array.isArray(blueprint.arrows)) {
    errors.push('arrows must be an array');
  } else if (blueprint.arrows) {
    blueprint.arrows.forEach((arrow, i) => {
      if (!arrow.from) errors.push(`Arrow ${i} missing 'from' field`);
      if (!arrow.to) errors.push(`Arrow ${i} missing 'to' field`);
    });
  }
  
  // Validate labels
  if (blueprint.labels && !Array.isArray(blueprint.labels)) {
    errors.push('labels must be an array');
  } else if (blueprint.labels) {
    blueprint.labels.forEach((label, i) => {
      if (!label.text) errors.push(`Label ${i} missing 'text' field`);
      if (typeof label.x !== 'number') errors.push(`Label ${i} missing numeric 'x' field`);
      if (typeof label.y !== 'number') errors.push(`Label ${i} missing numeric 'y' field`);
    });
  }
  
  // Validate beats
  if (blueprint.beats && !Array.isArray(blueprint.beats)) {
    errors.push('beats must be an array');
  } else if (blueprint.beats) {
    if (blueprint.beats.length > 5) {
      errors.push('Maximum 5 narrative beats allowed');
    }
    blueprint.beats.forEach((beat, i) => {
      if (typeof beat.beat !== 'number') errors.push(`Beat ${i} missing numeric 'beat' field`);
      if (!beat.text) errors.push(`Beat ${i} missing 'text' field`);
    });
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Create an empty blueprint with defaults
 * @param {string} mode - Rendering mode
 * @returns {Blueprint}
 */
export function createEmptyBlueprint(mode = 'SCENE') {
  return {
    mode,
    items: [],
    arrows: [],
    labels: [],
    highlights: [],
    figures: [],
    doodles: [],
    controls: [],
    beats: [],
  };
}

/**
 * Merge two blueprints (useful for layering)
 * @param {Blueprint} base - Base blueprint
 * @param {Blueprint} overlay - Overlay blueprint
 * @returns {Blueprint}
 */
export function mergeBlueprints(base, overlay) {
  return {
    ...base,
    ...overlay,
    items: [...(base.items || []), ...(overlay.items || [])],
    arrows: [...(base.arrows || []), ...(overlay.arrows || [])],
    labels: [...(base.labels || []), ...(overlay.labels || [])],
    highlights: [...(base.highlights || []), ...(overlay.highlights || [])],
    figures: [...(base.figures || []), ...(overlay.figures || [])],
    doodles: [...(base.doodles || []), ...(overlay.doodles || [])],
    controls: [...(base.controls || []), ...(overlay.controls || [])],
    beats: [...(base.beats || []), ...(overlay.beats || [])],
  };
}

/**
 * Clone a blueprint (deep copy)
 * @param {Blueprint} blueprint - Blueprint to clone
 * @returns {Blueprint}
 */
export function cloneBlueprint(blueprint) {
  return JSON.parse(JSON.stringify(blueprint));
}

// ============================================
// EXPORTS
// ============================================
export const BlueprintSchema = {
  validate: validateBlueprint,
  createEmpty: createEmptyBlueprint,
  merge: mergeBlueprints,
  clone: cloneBlueprint,
};

export default BlueprintSchema;

