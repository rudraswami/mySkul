/**
 * 🎭 ENTITY TEMPLATES
 * ===================
 * 
 * Pre-built visual templates for simulation entities.
 * Each template defines how an entity looks and behaves.
 * 
 * Templates are BEAUTIFUL by default - no generic boxes.
 */

import { getPalette, getRoleColor } from './DomainPalettes';

// Template definitions
export const ENTITY_TEMPLATES = {
  // ============================================
  // PHYSICS TEMPLATES
  // ============================================
  
  rigidbody: {
    name: 'Rigid Body',
    category: 'physics',
    shape: 'circle',
    defaultSize: { width: 60, height: 60 },
    style: {
      fill: 'primary',
      stroke: 'secondary',
      strokeWidth: 3,
      shadow: true,
      gradient: 'radial'  // 3D-like appearance
    },
    physics: {
      enabled: true,
      mass: 1,
      friction: 0.1,
      restitution: 0.5
    },
    idleAnimation: 'subtle_float',  // Slight floating effect
    interactable: true
  },
  
  surface: {
    name: 'Surface',
    category: 'physics',
    shape: 'rect',
    defaultSize: { width: 600, height: 20 },
    style: {
      fill: 'surface',
      stroke: 'secondary',
      strokeWidth: 2,
      pattern: 'hatching',  // Textured surface
      gradient: 'linear'
    },
    physics: {
      enabled: true,
      isStatic: true,
      friction: 0.3
    },
    idleAnimation: null
  },
  
  force_vector: {
    name: 'Force Vector',
    category: 'physics',
    shape: 'arrow',
    defaultSize: { width: 80, height: 20 },
    style: {
      fill: 'force',
      stroke: 'force',
      strokeWidth: 3,
      arrowHead: true,
      animated: true  // Pulsing arrow
    },
    physics: {
      enabled: false
    },
    idleAnimation: 'pulse_subtle',
    attachable: true  // Can attach to other entities
  },
  
  // ============================================
  // FLOW/PROCESS TEMPLATES
  // ============================================
  
  flow_node: {
    name: 'Flow Node',
    category: 'process',
    shape: 'ellipse',
    defaultSize: { width: 100, height: 70 },
    style: {
      fill: 'primary',
      stroke: 'secondary',
      strokeWidth: 2,
      shadow: true,
      gradient: 'radial'
    },
    idleAnimation: 'glow_pulse',
    interactable: true,
    canEmitParticles: true
  },
  
  particle_emitter: {
    name: 'Particle Emitter',
    category: 'process',
    shape: 'hidden',
    defaultSize: { width: 0, height: 0 },
    style: {
      particle: {
        shape: 'circle',
        size: 6,
        color: 'accent',
        trail: true
      }
    },
    idleAnimation: 'emit_particles',
    emitConfig: {
      rate: 5,      // particles per second
      speed: 100,   // pixels per second
      lifespan: 2000
    }
  },
  
  connector: {
    name: 'Connector',
    category: 'process',
    shape: 'line',
    defaultSize: { width: 0, height: 0 },  // Dynamic based on endpoints
    style: {
      stroke: 'secondary',
      strokeWidth: 2,
      dash: null,  // Can be [5, 5] for dashed
      animated: true,
      arrowHead: true,
      flowParticles: true
    },
    idleAnimation: 'flow_particles'
  },
  
  // ============================================
  // STRUCTURE TEMPLATES
  // ============================================
  
  region: {
    name: 'Region',
    category: 'structure',
    shape: 'rect',
    defaultSize: { width: 200, height: 150 },
    style: {
      fill: 'primary',
      fillOpacity: 0.2,
      stroke: 'primary',
      strokeWidth: 2,
      dash: [8, 4],
      rounded: 12
    },
    idleAnimation: 'breathe',  // Subtle size change
    canContain: true
  },
  
  layer: {
    name: 'Layer',
    category: 'structure',
    shape: 'rect',
    defaultSize: { width: 300, height: 60 },
    style: {
      fill: 'primary',
      fillOpacity: 0.8,
      stroke: 'secondary',
      strokeWidth: 1,
      rounded: 8,
      shadow: true
    },
    idleAnimation: null,
    explodable: true  // Can separate in exploded view
  },
  
  cell_membrane: {
    name: 'Cell Membrane',
    category: 'biology',
    shape: 'ellipse',
    defaultSize: { width: 300, height: 200 },
    style: {
      fill: 'cell',
      fillOpacity: 0.3,
      stroke: 'cell',
      strokeWidth: 4,
      doubleStroke: true  // Bilayer effect
    },
    idleAnimation: 'membrane_wobble',
    canContain: true
  },
  
  // ============================================
  // MATH/GRAPH TEMPLATES
  // ============================================
  
  graph_line: {
    name: 'Graph Line',
    category: 'math',
    shape: 'path',
    defaultSize: { width: 400, height: 300 },
    style: {
      stroke: 'primary',
      strokeWidth: 3,
      fill: 'none',
      smooth: true,  // Bezier curves
      animated: true  // Draw animation
    },
    idleAnimation: 'draw_reveal',
    data: {
      points: [],  // Will be computed
      xRange: [-10, 10],
      yRange: [-10, 10]
    }
  },
  
  axis: {
    name: 'Axis',
    category: 'math',
    shape: 'line',
    defaultSize: { width: 400, height: 0 },
    style: {
      stroke: 'axis',
      strokeWidth: 2,
      arrowHead: true,
      ticks: true,
      labels: true
    },
    idleAnimation: null
  },
  
  tracer_dot: {
    name: 'Tracer Dot',
    category: 'math',
    shape: 'circle',
    defaultSize: { width: 16, height: 16 },
    style: {
      fill: 'accent',
      stroke: 'none',
      shadow: true,
      glow: true
    },
    idleAnimation: 'glow_pulse',
    followsPath: true
  },
  
  // ============================================
  // LABEL/TEXT TEMPLATES
  // ============================================
  
  label: {
    name: 'Label',
    category: 'text',
    shape: 'text',
    defaultSize: { width: 'auto', height: 'auto' },
    style: {
      fontSize: 14,
      fontWeight: 'normal',
      fontFamily: 'Inter, system-ui, sans-serif',
      color: 'text',
      background: 'none'
    },
    idleAnimation: null
  },
  
  title_label: {
    name: 'Title Label',
    category: 'text',
    shape: 'text',
    defaultSize: { width: 'auto', height: 'auto' },
    style: {
      fontSize: 20,
      fontWeight: 'bold',
      fontFamily: 'Inter, system-ui, sans-serif',
      color: 'primary',
      background: 'none'
    },
    idleAnimation: 'fade_in'
  },
  
  badge: {
    name: 'Badge',
    category: 'text',
    shape: 'pill',
    defaultSize: { width: 'auto', height: 28 },
    style: {
      fill: 'accent',
      fillOpacity: 0.2,
      stroke: 'accent',
      strokeWidth: 1,
      fontSize: 12,
      fontWeight: 'medium',
      color: 'accent',
      padding: [4, 12]
    },
    idleAnimation: null
  },
  
  // ============================================
  // INDICATOR TEMPLATES
  // ============================================
  
  value_display: {
    name: 'Value Display',
    category: 'indicator',
    shape: 'rounded_rect',
    defaultSize: { width: 120, height: 40 },
    style: {
      fill: 'background',
      stroke: 'secondary',
      strokeWidth: 1,
      rounded: 8,
      shadow: true,
      fontSize: 16,
      fontWeight: 'bold',
      color: 'primary'
    },
    idleAnimation: null,
    dynamic: true  // Updates with state
  },
  
  progress_bar: {
    name: 'Progress Bar',
    category: 'indicator',
    shape: 'progress',
    defaultSize: { width: 200, height: 12 },
    style: {
      trackFill: 'surface',
      fill: 'primary',
      rounded: 6,
      animated: true
    },
    idleAnimation: null,
    dynamic: true
  }
};

/**
 * Get a template definition
 */
export function getTemplate(templateName) {
  return ENTITY_TEMPLATES[templateName] || ENTITY_TEMPLATES.flow_node;
}

/**
 * Create an entity instance from template + script entity definition
 */
export function createEntityFromTemplate(entityDef, domain) {
  const template = getTemplate(entityDef.template);
  const palette = getPalette(domain);
  
  // Resolve colors from palette
  const resolveColor = (colorKey) => {
    if (colorKey.startsWith('#')) return colorKey;  // Already hex
    return palette[colorKey] || palette.primary;
  };
  
  // Build entity instance
  const entity = {
    id: entityDef.id,
    role: entityDef.role,
    label: entityDef.label,
    template: entityDef.template,
    
    // From template
    shape: template.shape,
    size: { ...template.defaultSize },
    physics: template.physics ? { ...template.physics } : null,
    idleAnimation: template.idleAnimation,
    interactable: template.interactable || false,
    
    // Style with resolved colors
    style: {
      ...template.style,
      fill: resolveColor(template.style.fill),
      stroke: resolveColor(template.style.stroke || template.style.fill),
      color: resolveColor(template.style.color || 'text')
    },
    
    // Position will be set by OntologyLayoutEngine
    position: { x: 0, y: 0 },
    
    // Runtime state
    state: {
      visible: true,
      opacity: 1,
      scale: 1,
      rotation: 0,
      highlighted: false,
      ...entityDef.initialState
    },
    
    // Custom properties from script
    properties: entityDef.properties || {}
  };
  
  // Apply color_hint if provided
  if (entityDef.properties?.color_hint) {
    const hintColor = palette[entityDef.properties.color_hint];
    if (hintColor) {
      entity.style.fill = hintColor;
    }
  }
  
  return entity;
}

/**
 * Get all templates for a category
 */
export function getTemplatesByCategory(category) {
  return Object.entries(ENTITY_TEMPLATES)
    .filter(([_, template]) => template.category === category)
    .map(([name, template]) => ({ name, ...template }));
}

export default ENTITY_TEMPLATES;
