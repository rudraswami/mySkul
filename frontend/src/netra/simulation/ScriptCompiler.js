/**
 * 🔧 SCRIPT COMPILER
 * ==================
 * 
 * Compiles SimulationScript into a runtime-ready scene graph.
 * Validates, enriches, and optimizes the script before execution.
 */

import { getTemplate, ENTITY_TEMPLATES } from './EntityTemplates';
import { getPalette } from './DomainPalettes';
import { computeLayout } from './OntologyLayoutEngine';

/**
 * Validate a SimulationScript
 */
export function validateScript(script) {
  const errors = [];
  const warnings = [];
  
  // Required fields
  if (!script.ontology) errors.push('Missing ontology');
  if (!script.world) errors.push('Missing world');
  if (!script.entities || script.entities.length === 0) errors.push('No entities defined');
  
  // Entity validation
  if (script.entities) {
    script.entities.forEach((entity, i) => {
      if (!entity.id) errors.push(`Entity ${i} missing id`);
      if (!entity.role) warnings.push(`Entity ${entity.id || i} missing role`);
      if (!entity.template) {
        warnings.push(`Entity ${entity.id || i} missing template, will use default`);
      } else if (!ENTITY_TEMPLATES[entity.template]) {
        warnings.push(`Entity ${entity.id} has unknown template: ${entity.template}`);
      }
    });
    
    // Check for unique IDs
    const ids = script.entities.map(e => e.id).filter(Boolean);
    const uniqueIds = new Set(ids);
    if (ids.length !== uniqueIds.size) {
      errors.push('Duplicate entity IDs detected');
    }
  }
  
  // Rule validation
  if (script.rules) {
    script.rules.forEach((rule, i) => {
      if (!rule.when) errors.push(`Rule ${i} missing 'when' condition`);
      if (!rule.then || !Array.isArray(rule.then)) {
        errors.push(`Rule ${i} missing 'then' actions array`);
      }
    });
  }
  
  // Quality checks
  if (script.entities && script.entities.length < 3) {
    warnings.push('Low entity count (< 3) - visual may be sparse');
  }
  if (script.rules && script.rules.length < 2) {
    warnings.push('Low rule count (< 2) - simulation may be static');
  }
  if (!script.narration || script.narration.length < 2) {
    warnings.push('Low narration count (< 2) - explanation may be incomplete');
  }
  if (!script.interactions || script.interactions.length === 0) {
    warnings.push('No interactions - user has no agency');
  }
  
  return {
    valid: errors.length === 0,
    errors,
    warnings
  };
}

/**
 * Enrich script with defaults and computed values
 */
export function enrichScript(script, options = {}) {
  const domain = script._meta?.domain || options.domain || 'general';
  const palette = getPalette(domain);
  const stageSize = { 
    width: options.width || 800, 
    height: options.height || 600 
  };
  
  // Enrich entities
  const enrichedEntities = (script.entities || []).map(entity => {
    const template = getTemplate(entity.template || 'flow_node');
    
    return {
      ...entity,
      template: entity.template || 'flow_node',
      _template: template,
      _resolvedStyle: resolveStyle(template.style, palette, entity.properties?.color_hint),
      size: template.defaultSize,
      physics: template.physics,
      idleAnimation: template.idleAnimation,
      interactable: template.interactable || false
    };
  });
  
  // Compute layout
  const layout = computeLayout({
    ...script,
    entities: enrichedEntities
  }, stageSize);
  
  // Apply layout
  enrichedEntities.forEach(entity => {
    if (layout[entity.id]) {
      entity.position = layout[entity.id];
    } else {
      entity.position = { x: stageSize.width / 2, y: stageSize.height / 2 };
    }
  });
  
  // Enrich narration with timing estimates
  const enrichedNarration = (script.narration || []).map((narr, i) => ({
    ...narr,
    _order: i,
    _estimatedDuration: estimateNarrationDuration(narr.text)
  }));
  
  // Build enriched script
  return {
    ...script,
    entities: enrichedEntities,
    narration: enrichedNarration,
    _meta: {
      ...script._meta,
      domain,
      enrichedAt: new Date().toISOString(),
      stageSize
    },
    _palette: palette
  };
}

/**
 * Resolve style colors from palette
 */
function resolveStyle(style, palette, colorHint) {
  const resolved = { ...style };
  
  const resolveColor = (key) => {
    if (typeof resolved[key] === 'string' && !resolved[key].startsWith('#')) {
      // It's a palette key
      resolved[key] = palette[resolved[key]] || palette.primary;
    }
  };
  
  resolveColor('fill');
  resolveColor('stroke');
  resolveColor('color');
  
  // Apply color hint
  if (colorHint && palette[colorHint]) {
    resolved.fill = palette[colorHint];
  }
  
  return resolved;
}

/**
 * Estimate narration duration based on text length
 */
function estimateNarrationDuration(text) {
  if (!text) return 2000;
  
  // Average reading speed: ~200 words per minute
  // = ~3.3 words per second
  const words = text.split(/\s+/).length;
  const seconds = words / 3.3;
  
  // Minimum 2 seconds, maximum 10 seconds
  return Math.max(2000, Math.min(10000, seconds * 1000));
}

/**
 * Compile SimulationScript into runtime-ready format
 */
export function compileScript(script, options = {}) {
  console.log('[ScriptCompiler] Compiling script...');
  
  // Step 1: Validate
  const validation = validateScript(script);
  if (!validation.valid) {
    console.error('[ScriptCompiler] Validation failed:', validation.errors);
    throw new Error(`Script validation failed: ${validation.errors.join(', ')}`);
  }
  if (validation.warnings.length > 0) {
    console.warn('[ScriptCompiler] Warnings:', validation.warnings);
  }
  
  // Step 2: Enrich
  const enrichedScript = enrichScript(script, options);
  
  // Step 3: Generate render-ready scene graph
  const sceneGraph = {
    // Metadata
    id: script.id || `scene_${Date.now()}`,
    ontology: script.ontology,
    world: script.world,
    title: script.title,
    
    // Stage configuration
    stage: {
      width: options.width || 800,
      height: options.height || 600,
      background: {
        type: 'gradient',
        colors: enrichedScript._palette.background || ['#F8FAFC', '#F1F5F9'],
        direction: 'vertical'
      }
    },
    
    // Entities with positions and styles
    entities: enrichedScript.entities,
    
    // Simulation state
    state: {
      initial: script.state?.initial || 'idle',
      variables: script.state?.variables || {}
    },
    
    // Constants (for interactions)
    constants: script.constants || {},
    
    // Rules
    rules: script.rules || [],
    
    // Interactions
    interactions: script.interactions || [],
    
    // Narration
    narration: enrichedScript.narration,
    
    // Palette for rendering
    palette: enrichedScript._palette,
    
    // Compilation metadata
    _compiled: {
      at: new Date().toISOString(),
      warnings: validation.warnings
    }
  };
  
  console.log(`[ScriptCompiler] Compiled: ${sceneGraph.entities.length} entities, ${sceneGraph.rules.length} rules`);
  
  return sceneGraph;
}

/**
 * Create a placeholder scene from a script
 */
export function createPlaceholderScene(script, options = {}) {
  const domain = script._meta?.domain || 'general';
  const palette = getPalette(domain);
  const stageSize = { 
    width: options.width || 800, 
    height: options.height || 600 
  };
  
  return {
    id: 'placeholder',
    ontology: script.ontology,
    world: script.world,
    title: script.title || 'Loading...',
    
    stage: {
      width: stageSize.width,
      height: stageSize.height,
      background: {
        type: 'gradient',
        colors: palette.background,
        direction: 'vertical'
      }
    },
    
    entities: script.entities.map((e, i) => ({
      id: e.id,
      label: e.label || 'Loading...',
      position: { 
        x: stageSize.width / 2, 
        y: stageSize.height / 2 
      },
      style: {
        fill: palette.primary,
        opacity: 0.3
      },
      isPlaceholder: true
    })),
    
    state: { current: 'loading', variables: {} },
    constants: {},
    rules: [],
    interactions: [],
    narration: [{
      id: 'loading',
      event: 'start',
      text: 'Generating simulation...'
    }],
    
    palette,
    _isPlaceholder: true
  };
}

export default { validateScript, enrichScript, compileScript, createPlaceholderScene };
