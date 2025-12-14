/**
 * 🎯 SEMANTIC POSITIONER
 * ======================
 * 
 * Positions elements based on their MEANING, not just grid layout.
 * 
 * Key insight: Forces don't float in space. They:
 * - Emanate FROM a body
 * - Point in a specific direction
 * - Have a point of application
 * 
 * This engine understands physics and positions accordingly:
 * - Weight: Center of mass, pointing DOWN
 * - Normal: Contact point with surface, pointing UP
 * - Friction: Contact point, opposing motion
 * - Applied force: Where you push, in push direction
 * 
 * The result is a FREE BODY DIAGRAM that looks like textbook physics.
 */

// ============================================
// SEMANTIC POSITION RULES
// ============================================

/**
 * Force attachment rules - where forces connect to bodies
 */
const FORCE_ATTACHMENT_RULES = {
  // Gravitational/Weight forces attach at center of mass
  gravitational: {
    attachPoint: 'center',
    direction: 'down',
    offset: { x: 0, y: 0 },
  },
  weight: {
    attachPoint: 'center',
    direction: 'down',
    offset: { x: 0, y: 0 },
  },
  
  // Normal force attaches at contact point with surface
  normal: {
    attachPoint: 'bottom_center',
    direction: 'up',
    offset: { x: 0, y: 0 },
  },
  
  // Friction attaches at contact point, opposes motion
  friction: {
    attachPoint: 'bottom_center',
    direction: 'opposite_to_motion',
    offset: { x: -10, y: 0 }, // Slight offset to not overlap normal
  },
  
  // Applied force - side of object
  applied: {
    attachPoint: 'left_center',
    direction: 'right',
    offset: { x: 0, y: 0 },
  },
  push: {
    attachPoint: 'left_center',
    direction: 'right',
    offset: { x: 0, y: 0 },
  },
  
  // Tension - along the string/rope
  tension: {
    attachPoint: 'top_center',
    direction: 'up',
    offset: { x: 0, y: 0 },
  },
  
  // Spring force
  spring: {
    attachPoint: 'right_center',
    direction: 'dynamic', // Based on compression/extension
    offset: { x: 0, y: 0 },
  },
};

// ============================================
// BODY POSITION TEMPLATES
// ============================================

/**
 * Where to position main bodies based on scenario
 */
const SCENARIO_LAYOUTS = {
  // Single body on surface
  'body_on_surface': {
    body: { x: 0.35, y: 0.4 },     // Left-center, above surface
    surface: { x: 0.1, y: 0.55 },  // Below body
  },
  
  // Two bodies interacting (Newton's 3rd law)
  'two_body_interaction': {
    body1: { x: 0.25, y: 0.45 },
    body2: { x: 0.65, y: 0.45 },
  },
  
  // Inclined plane
  'inclined_plane': {
    body: { x: 0.4, y: 0.35 },
    incline: { x: 0.2, y: 0.3 },
    ground: { x: 0.1, y: 0.7 },
  },
  
  // Pulley system
  'pulley': {
    pulley: { x: 0.5, y: 0.15 },
    body1: { x: 0.3, y: 0.5 },
    body2: { x: 0.7, y: 0.5 },
  },
  
  // Projectile
  'projectile': {
    projectile: { x: 0.2, y: 0.6 },
    trajectory_peak: { x: 0.5, y: 0.2 },
    landing: { x: 0.8, y: 0.6 },
  },
  
  // Free body diagram (centered focus)
  'free_body': {
    body: { x: 0.5, y: 0.45 },
  },
};

// ============================================
// SEMANTIC POSITIONER CLASS
// ============================================

export class SemanticPositioner {
  constructor(options = {}) {
    this.options = {
      width: options.width || 600,
      height: options.height || 500,
      margin: options.margin || 40,
      forceVectorLength: options.forceVectorLength || 80,
      bodySize: options.bodySize || 60,
      ...options,
    };
  }
  
  /**
   * Position all elements semantically
   */
  positionElements(conceptGraph, sceneGraph) {
    const scenario = this.detectScenario(conceptGraph);
    console.log(`🎯 [SemanticPositioner] Detected scenario: ${scenario}`);
    
    // Get the layout template
    const layout = SCENARIO_LAYOUTS[scenario] || SCENARIO_LAYOUTS['free_body'];
    
    // First, position the main bodies
    this.positionBodies(conceptGraph, sceneGraph, layout);
    
    // Then, attach forces to their bodies
    this.positionForces(conceptGraph, sceneGraph);
    
    // Finally, position structures (ground, surfaces)
    this.positionStructures(conceptGraph, sceneGraph, layout);
    
    return sceneGraph;
  }
  
  /**
   * Detect what kind of physics scenario this is
   */
  detectScenario(conceptGraph) {
    const entities = Array.from(conceptGraph.entities.values());
    const topic = conceptGraph.metadata.topic?.toLowerCase() || '';
    
    // Check for specific scenarios
    if (topic.includes('incline') || topic.includes('ramp')) {
      return 'inclined_plane';
    }
    
    if (topic.includes('pulley')) {
      return 'pulley';
    }
    
    if (topic.includes('projectile') || topic.includes('trajectory')) {
      return 'projectile';
    }
    
    if (topic.includes('collision') || topic.includes('newton') || 
        entities.filter(e => e.type === 'body').length >= 2) {
      return 'two_body_interaction';
    }
    
    // Check if there's a surface/ground
    const hasSurface = entities.some(e => 
      e.type === 'structure' || 
      e.properties?.variant === 'ground_plane'
    );
    
    if (hasSurface) {
      return 'body_on_surface';
    }
    
    return 'free_body';
  }
  
  /**
   * Position main bodies based on scenario layout
   */
  positionBodies(conceptGraph, sceneGraph, layout) {
    const { width, height, margin, bodySize } = this.options;
    const usableWidth = width - 2 * margin;
    const usableHeight = height - 2 * margin;
    
    // Find all body nodes
    for (const [nodeId, node] of sceneGraph.nodes) {
      const entity = conceptGraph.entities.get(nodeId);
      if (!entity) continue;
      
      // Position bodies
      if (entity.type === 'body' || entity.type === 'object') {
        const layoutKey = this.findLayoutKey(nodeId, layout);
        const position = layout[layoutKey] || layout.body || { x: 0.5, y: 0.45 };
        
        node.x = margin + position.x * usableWidth - bodySize / 2;
        node.y = margin + position.y * usableHeight - bodySize / 2;
        node.width = bodySize;
        node.height = bodySize;
        
        // Store center for force attachment
        node.center = {
          x: node.x + bodySize / 2,
          y: node.y + bodySize / 2,
        };
        
        console.log(`🎯 [SemanticPositioner] Body "${nodeId}" at (${node.x.toFixed(0)}, ${node.y.toFixed(0)})`);
      }
    }
  }
  
  /**
   * Position forces emanating from their attached bodies
   */
  positionForces(conceptGraph, sceneGraph) {
    const { forceVectorLength, bodySize } = this.options;
    
    // Find the main body (forces attach to this)
    let mainBody = null;
    for (const [nodeId, node] of sceneGraph.nodes) {
      const entity = conceptGraph.entities.get(nodeId);
      if (entity && (entity.type === 'body' || entity.type === 'object')) {
        mainBody = { id: nodeId, node, entity };
        break;
      }
    }
    
    if (!mainBody) {
      console.warn('🎯 [SemanticPositioner] No main body found for force attachment');
      return;
    }
    
    const bodyCenter = mainBody.node.center || {
      x: mainBody.node.x + mainBody.node.width / 2,
      y: mainBody.node.y + mainBody.node.height / 2,
    };
    
    // Position each force relative to the body
    for (const [nodeId, node] of sceneGraph.nodes) {
      const entity = conceptGraph.entities.get(nodeId);
      if (!entity || entity.type !== 'force') continue;
      
      const variant = entity.properties?.variant || 'generic';
      const direction = entity.properties?.direction || 'right';
      
      // Get attachment rules
      const rules = FORCE_ATTACHMENT_RULES[variant] || FORCE_ATTACHMENT_RULES[direction] || {
        attachPoint: 'center',
        direction: direction,
        offset: { x: 0, y: 0 },
      };
      
      // Calculate attachment point on body
      const attachPoint = this.getAttachPoint(mainBody.node, rules.attachPoint);
      
      // Calculate force vector position
      const forceDir = this.getDirectionVector(direction);
      
      // Position force: start at attach point, extend in direction
      node.x = attachPoint.x + rules.offset.x;
      node.y = attachPoint.y + rules.offset.y;
      node.width = forceVectorLength;
      node.height = 20;
      
      // Store direction for rendering
      node.style = node.style || {};
      node.style.direction = direction;
      node.style.startPoint = { ...attachPoint };
      node.style.endPoint = {
        x: attachPoint.x + forceDir.x * forceVectorLength,
        y: attachPoint.y + forceDir.y * forceVectorLength,
      };
      
      console.log(`🎯 [SemanticPositioner] Force "${nodeId}" attached at (${attachPoint.x.toFixed(0)}, ${attachPoint.y.toFixed(0)}) pointing ${direction}`);
    }
  }
  
  /**
   * Position structures (ground, surfaces, etc.)
   */
  positionStructures(conceptGraph, sceneGraph, layout) {
    const { width, height, margin } = this.options;
    
    for (const [nodeId, node] of sceneGraph.nodes) {
      const entity = conceptGraph.entities.get(nodeId);
      if (!entity || entity.type !== 'structure') continue;
      
      const variant = entity.properties?.variant || 'ground_plane';
      
      if (variant === 'ground_plane' || nodeId.includes('ground') || nodeId.includes('surface')) {
        // Position ground below the body
        const layoutPos = layout.surface || layout.ground || { x: 0.1, y: 0.55 };
        
        node.x = margin + layoutPos.x * (width - 2 * margin);
        node.y = margin + layoutPos.y * (height - 2 * margin);
        node.width = (width - 2 * margin) * 0.5;
        node.height = 8;
        
        console.log(`🎯 [SemanticPositioner] Structure "${nodeId}" at y=${node.y.toFixed(0)}`);
      }
    }
  }
  
  /**
   * Get attachment point on a body
   */
  getAttachPoint(bodyNode, attachType) {
    const { x, y, width, height } = bodyNode;
    
    switch (attachType) {
      case 'center':
        return { x: x + width / 2, y: y + height / 2 };
      case 'top_center':
        return { x: x + width / 2, y: y };
      case 'bottom_center':
        return { x: x + width / 2, y: y + height };
      case 'left_center':
        return { x: x, y: y + height / 2 };
      case 'right_center':
        return { x: x + width, y: y + height / 2 };
      default:
        return { x: x + width / 2, y: y + height / 2 };
    }
  }
  
  /**
   * Convert direction string to unit vector
   */
  getDirectionVector(direction) {
    switch (direction) {
      case 'up': return { x: 0, y: -1 };
      case 'down': return { x: 0, y: 1 };
      case 'left': return { x: -1, y: 0 };
      case 'right': return { x: 1, y: 0 };
      case 'up_right': return { x: 0.707, y: -0.707 };
      case 'up_left': return { x: -0.707, y: -0.707 };
      case 'down_right': return { x: 0.707, y: 0.707 };
      case 'down_left': return { x: -0.707, y: 0.707 };
      default: return { x: 1, y: 0 };
    }
  }
  
  /**
   * Find the best layout key for a node
   */
  findLayoutKey(nodeId, layout) {
    // Direct match
    if (layout[nodeId]) return nodeId;
    
    // Try partial matches
    for (const key of Object.keys(layout)) {
      if (nodeId.includes(key) || key.includes(nodeId)) {
        return key;
      }
    }
    
    // Default
    return 'body';
  }
}

// ============================================
// EXPORTS
// ============================================

export function createSemanticPositioner(options) {
  return new SemanticPositioner(options);
}

export default SemanticPositioner;

