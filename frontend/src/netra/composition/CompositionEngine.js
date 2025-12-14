/**
 * 🎨 COMPOSITION ENGINE
 * =====================
 * 
 * Intelligent visual composition based on semantic understanding.
 * 
 * This is NOT position math. It's semantic layout:
 * - "A causes B" → A positioned before B in flow
 * - "A contains B" → B nested inside A
 * - "Forces are opposite" → Arrows point away from each other
 * - "Timeline" → Elements arranged chronologically
 * 
 * The engine reasons about MEANING, not coordinates.
 */

import { RELATIONSHIP_TYPES, ENTITY_TYPES } from '../core/ConceptGraph';
import { getVisualSpec, VISUAL_FORMS } from '../semantics/VisualOntology';

// ============================================
// COMPOSITION STRATEGIES
// ============================================

export const COMPOSITION_STRATEGIES = {
  CAUSAL_FLOW: 'causal_flow',           // Left-to-right cause-effect
  HIERARCHICAL: 'hierarchical',          // Top-down containment
  RADIAL: 'radial',                      // Center-out structure
  TEMPORAL: 'temporal',                  // Timeline left-to-right
  COMPARATIVE: 'comparative',            // Side-by-side
  FORCE_DIAGRAM: 'force_diagram',        // Physics force layout
  CYCLIC: 'cyclic',                      // Circular process
  STRUCTURAL: 'structural',              // Anatomy/component layout
  GRAPH: 'graph',                        // Mathematical graph layout
};

// ============================================
// VISUAL CONSTRAINTS
// ============================================

const CONSTRAINTS = {
  MIN_MARGIN: 40,                        // Minimum edge margin
  MIN_SPACING: 60,                       // Minimum between elements
  ARROW_CLEARANCE: 20,                   // Space for arrows
  LABEL_OFFSET: 25,                      // Label distance from shape
  FORCE_VECTOR_LENGTH: 80,               // Standard force arrow length
  EMPHASIS_SCALE: 1.3,                   // Scale for important elements
};

// ============================================
// SCENE GRAPH NODE
// ============================================

class SceneNode {
  constructor(entityId, entityData) {
    this.id = entityId;
    this.entity = entityData;
    
    // Computed layout
    this.x = 0;
    this.y = 0;
    this.width = 0;
    this.height = 0;
    this.rotation = 0;
    
    // Visual specification
    this.visualSpec = null;
    this.primitive = null;
    this.style = {};
    
    // Hierarchy
    this.parent = null;
    this.children = [];
    
    // Connections
    this.incomingArrows = [];
    this.outgoingArrows = [];
    
    // Animation
    this.drawOrder = 0;
    this.animationDelay = 0;
  }

  /**
   * Set position
   */
  setPosition(x, y) {
    this.x = x;
    this.y = y;
  }

  /**
   * Set size
   */
  setSize(width, height) {
    this.width = width;
    this.height = height;
  }

  /**
   * Get center position
   */
  getCenter() {
    return {
      x: this.x + this.width / 2,
      y: this.y + this.height / 2,
    };
  }

  /**
   * Get bounds
   */
  getBounds() {
    return {
      left: this.x,
      top: this.y,
      right: this.x + this.width,
      bottom: this.y + this.height,
      width: this.width,
      height: this.height,
    };
  }
}

// ============================================
// SCENE GRAPH
// ============================================

class SceneGraph {
  constructor() {
    this.nodes = new Map();              // entityId → SceneNode
    this.arrows = [];                    // Connection arrows
    this.annotations = [];               // Labels, callouts
    this.decorations = [];               // Background elements
    
    this.bounds = {
      width: 800,
      height: 600,
    };
    
    this.metadata = {};
  }

  /**
   * Add a node
   */
  addNode(entityId, entityData) {
    const node = new SceneNode(entityId, entityData);
    this.nodes.set(entityId, node);
    return node;
  }

  /**
   * Get node by ID
   */
  getNode(entityId) {
    return this.nodes.get(entityId);
  }

  /**
   * Add an arrow connection
   */
  addArrow(fromId, toId, relationship) {
    const arrow = {
      from: fromId,
      to: toId,
      relationship,
      style: this.inferArrowStyle(relationship),
      label: relationship.label || null,
      curved: false,
      bidirectional: relationship.properties?.bidirectional || false,
    };
    
    this.arrows.push(arrow);
    
    // Register with nodes
    const fromNode = this.nodes.get(fromId);
    const toNode = this.nodes.get(toId);
    if (fromNode) fromNode.outgoingArrows.push(arrow);
    if (toNode) toNode.incomingArrows.push(arrow);
    
    return arrow;
  }

  /**
   * Add annotation
   */
  addAnnotation(text, position, style = {}) {
    this.annotations.push({
      text,
      x: position.x,
      y: position.y,
      ...style,
    });
  }

  /**
   * Infer arrow style from relationship type
   */
  inferArrowStyle(relationship) {
    const styleMap = {
      [RELATIONSHIP_TYPES.CAUSES]: { color: '#2C3E50', width: 2, head: 'arrow' },
      [RELATIONSHIP_TYPES.ENABLES]: { color: '#27AE60', width: 2, head: 'arrow', dashed: true },
      [RELATIONSHIP_TYPES.PREVENTS]: { color: '#E74C3C', width: 2, head: 'blocked' },
      [RELATIONSHIP_TYPES.ACTS_ON]: { color: '#E74C3C', width: 3, head: 'arrow' },
      [RELATIONSHIP_TYPES.ATTRACTS]: { color: '#3498DB', width: 2, head: 'arrow' },
      [RELATIONSHIP_TYPES.REPELS]: { color: '#E74C3C', width: 2, head: 'double_arrow' },
      [RELATIONSHIP_TYPES.BECOMES]: { color: '#9B59B6', width: 2, head: 'arrow' },
    };

    return styleMap[relationship.type] || { color: '#7F8C8D', width: 1.5, head: 'arrow' };
  }

  /**
   * Set bounds
   */
  setBounds(width, height) {
    this.bounds = { width, height };
  }

  /**
   * Get all nodes as array
   */
  getNodes() {
    return Array.from(this.nodes.values());
  }

  /**
   * Export to renderable format
   */
  toRenderSpec() {
    return {
      nodes: Array.from(this.nodes.values()).map(node => ({
        id: node.id,
        x: node.x,
        y: node.y,
        width: node.width,
        height: node.height,
        rotation: node.rotation,
        entity: node.entity,
        visualSpec: node.visualSpec,
        primitive: node.primitive,
        style: node.style,
        drawOrder: node.drawOrder,
        animationDelay: node.animationDelay,
      })),
      arrows: this.arrows.map(arrow => ({
        ...arrow,
        fromNode: this.nodes.get(arrow.from),
        toNode: this.nodes.get(arrow.to),
      })),
      annotations: this.annotations,
      decorations: this.decorations,
      bounds: this.bounds,
      metadata: this.metadata,
    };
  }
}

// ============================================
// COMPOSITION ENGINE CLASS
// ============================================

export class CompositionEngine {
  constructor(options = {}) {
    this.options = {
      width: 800,
      height: 600,
      margin: CONSTRAINTS.MIN_MARGIN,
      style: 'sketch',                   // sketch, technical, minimal
      animationEnabled: true,
      ...options,
    };
  }

  /**
   * Compose a scene from ConceptGraph
   * @param {ConceptGraph} conceptGraph - The semantic concept graph
   * @param {string} domain - The subject domain
   * @returns {SceneGraph} The composed scene graph
   */
  compose(conceptGraph, domain = 'physics') {
    const scene = new SceneGraph();
    scene.setBounds(this.options.width, this.options.height);
    scene.metadata = { ...conceptGraph.metadata, domain };

    // Step 1: Determine composition strategy
    const strategy = this.selectStrategy(conceptGraph);
    scene.metadata.strategy = strategy;

    // Step 2: Create scene nodes from entities
    this.createSceneNodes(conceptGraph, scene, domain);

    // Step 3: Apply composition strategy
    this.applyStrategy(strategy, conceptGraph, scene);

    // Step 4: Create arrows from relationships
    this.createArrows(conceptGraph, scene);

    // Step 5: Add annotations
    this.addAnnotations(conceptGraph, scene);

    // Step 6: Compute draw order for animation
    this.computeDrawOrder(scene);

    return scene;
  }

  /**
   * Select composition strategy based on graph structure
   */
  selectStrategy(conceptGraph) {
    const visualType = conceptGraph.inferVisualType();

    const strategyMap = {
      'force_diagram': COMPOSITION_STRATEGIES.FORCE_DIAGRAM,
      'process_flow': COMPOSITION_STRATEGIES.CAUSAL_FLOW,
      'cycle': COMPOSITION_STRATEGIES.CYCLIC,
      'structure': COMPOSITION_STRATEGIES.STRUCTURAL,
      'comparison': COMPOSITION_STRATEGIES.COMPARATIVE,
      'timeline': COMPOSITION_STRATEGIES.TEMPORAL,
      'graph': COMPOSITION_STRATEGIES.GRAPH,
      'scene': COMPOSITION_STRATEGIES.CAUSAL_FLOW, // Default
    };

    return strategyMap[visualType] || COMPOSITION_STRATEGIES.CAUSAL_FLOW;
  }

  /**
   * Create scene nodes from entities
   */
  createSceneNodes(conceptGraph, scene, domain) {
    console.log(`🎨 [CompositionEngine] Creating nodes from ${conceptGraph.entities.size} entities`);
    
    for (const [entityId, entity] of conceptGraph.entities) {
      console.log(`🎨 [CompositionEngine] Creating node: ${entityId}`, entity);
      const node = scene.addNode(entityId, entity);
      
      // Get visual specification from ontology
      const visualHint = entity.properties?.visualHint;
      const visualSpec = getVisualSpec(domain, visualHint || entity.type);
      node.visualSpec = visualSpec;

      // Determine primitive and size
      this.configurePrimitive(node, entity, visualSpec);

      // Apply importance scaling
      if (entity.properties?.importance === 'high') {
        node.width *= CONSTRAINTS.EMPHASIS_SCALE;
        node.height *= CONSTRAINTS.EMPHASIS_SCALE;
      }
    }
  }

  /**
   * Configure primitive type and size for a node
   */
  configurePrimitive(node, entity, visualSpec) {
    const type = entity.type;
    const variant = entity.properties?.variant;

    // Primitive sizing based on type
    const sizingRules = {
      [ENTITY_TYPES.BODY]: { width: 60, height: 60, primitive: 'body' },
      [ENTITY_TYPES.FORCE]: { width: CONSTRAINTS.FORCE_VECTOR_LENGTH, height: 20, primitive: 'force_vector' },
      [ENTITY_TYPES.VECTOR]: { width: 60, height: 20, primitive: 'vector' },
      [ENTITY_TYPES.STRUCTURE]: { width: 100, height: 80, primitive: 'structure' },
      [ENTITY_TYPES.CELL]: { width: 120, height: 100, primitive: 'cell' },
      [ENTITY_TYPES.ATOM]: { width: 80, height: 80, primitive: 'atom' },
      [ENTITY_TYPES.MOLECULE]: { width: 100, height: 80, primitive: 'molecule' },
      [ENTITY_TYPES.FUNCTION]: { width: 200, height: 150, primitive: 'graph' },
      [ENTITY_TYPES.SHAPE]: { width: 80, height: 80, primitive: 'shape' },
      [ENTITY_TYPES.PROCESS]: { width: 100, height: 60, primitive: 'process_box' },
      [ENTITY_TYPES.ORGAN]: { width: 120, height: 100, primitive: 'organ' },
      [ENTITY_TYPES.OBJECT]: { width: 80, height: 50, primitive: 'generic' }, // Generic concept nodes
    };

    const sizing = sizingRules[type] || { width: 60, height: 60, primitive: 'generic' };
    
    node.setSize(sizing.width, sizing.height);
    node.primitive = sizing.primitive;

    // Override from visual spec if available
    if (visualSpec?.properties) {
      node.style = { ...node.style, ...visualSpec.properties };
    }

    // Handle force vectors specially
    if (type === ENTITY_TYPES.FORCE) {
      node.primitive = 'force_vector';
      const direction = entity.properties?.direction || 'right';
      node.style.direction = direction;
      node.style.variant = variant;
    }
  }

  /**
   * Apply composition strategy to position nodes
   */
  applyStrategy(strategy, conceptGraph, scene) {
    switch (strategy) {
      case COMPOSITION_STRATEGIES.FORCE_DIAGRAM:
        this.layoutForceDiagram(conceptGraph, scene);
        break;
      case COMPOSITION_STRATEGIES.CAUSAL_FLOW:
        this.layoutCausalFlow(conceptGraph, scene);
        break;
      case COMPOSITION_STRATEGIES.CYCLIC:
        this.layoutCyclic(conceptGraph, scene);
        break;
      case COMPOSITION_STRATEGIES.HIERARCHICAL:
        this.layoutHierarchical(conceptGraph, scene);
        break;
      case COMPOSITION_STRATEGIES.COMPARATIVE:
        this.layoutComparative(conceptGraph, scene);
        break;
      case COMPOSITION_STRATEGIES.TEMPORAL:
        this.layoutTemporal(conceptGraph, scene);
        break;
      case COMPOSITION_STRATEGIES.STRUCTURAL:
        this.layoutStructural(conceptGraph, scene);
        break;
      case COMPOSITION_STRATEGIES.GRAPH:
        this.layoutGraph(conceptGraph, scene);
        break;
      default:
        this.layoutCausalFlow(conceptGraph, scene);
    }
  }

  /**
   * FORCE DIAGRAM LAYOUT
   * Physics-specific: body in center, forces as vectors attached to it
   */
  layoutForceDiagram(conceptGraph, scene) {
    const { width, height } = this.options;
    const centerX = width / 2;
    const centerY = height / 2;

    const nodes = scene.getNodes();
    const bodies = nodes.filter(n => n.entity.type === ENTITY_TYPES.BODY);
    const forces = nodes.filter(n => n.entity.type === ENTITY_TYPES.FORCE);
    const others = nodes.filter(n => 
      n.entity.type !== ENTITY_TYPES.BODY && 
      n.entity.type !== ENTITY_TYPES.FORCE
    );

    // Position main body at center
    if (bodies.length > 0) {
      const mainBody = bodies[0];
      mainBody.setPosition(centerX - mainBody.width / 2, centerY - mainBody.height / 2);
      mainBody.drawOrder = 1;

      // Position forces around the body
      forces.forEach((force, index) => {
        const direction = force.entity.properties?.direction || 
                          this.inferForceDirection(force, index, forces.length);
        
        const { x, y, rotation } = this.positionForceVector(
          mainBody, 
          force, 
          direction
        );
        
        force.setPosition(x, y);
        force.rotation = rotation;
        force.drawOrder = 2 + index;
      });
    } else {
      // No body, just layout forces in a pattern
      this.layoutRadially(forces, centerX, centerY, 100);
    }

    // Position other elements (ground, etc.)
    others.forEach((node, index) => {
      if (node.entity.properties?.visualHint === 'ground_plane') {
        // Ground at bottom
        node.setPosition(0, height - 60);
        node.setSize(width, 40);
      } else {
        // Other elements at edges
        node.setPosition(
          this.options.margin + index * 80,
          height - 100
        );
      }
      node.drawOrder = 10 + index;
    });
  }

  /**
   * Position a force vector relative to a body
   */
  positionForceVector(body, force, direction) {
    const bodyCenter = body.getCenter();
    const forceLength = force.width;
    
    const directionAngles = {
      'up': -90,
      'down': 90,
      'left': 180,
      'right': 0,
      'up-left': -135,
      'up-right': -45,
      'down-left': 135,
      'down-right': 45,
    };

    const angle = directionAngles[direction] || 0;
    const radians = (angle * Math.PI) / 180;
    
    // Position force starting from body surface
    const offset = body.width / 2 + 10;
    const startX = bodyCenter.x + Math.cos(radians) * offset;
    const startY = bodyCenter.y + Math.sin(radians) * offset;

    return {
      x: startX,
      y: startY,
      rotation: angle,
    };
  }

  /**
   * Infer force direction based on variant and index
   */
  inferForceDirection(force, index, total) {
    const variant = force.entity.properties?.variant;
    
    const variantDirections = {
      'gravitational': 'down',
      'normal': 'up',
      'friction': index % 2 === 0 ? 'left' : 'right',
      'tension': 'up-right',
      'applied': 'right',
    };

    if (variantDirections[variant]) {
      return variantDirections[variant];
    }

    // Default: distribute around
    const directions = ['up', 'right', 'down', 'left'];
    return directions[index % directions.length];
  }

  /**
   * CAUSAL FLOW LAYOUT
   * Left-to-right flow for cause-effect sequences
   */
  layoutCausalFlow(conceptGraph, scene) {
    const { width, height } = this.options;
    const nodes = scene.getNodes();
    
    // Find causal chains
    const causalChains = conceptGraph.findCausalChains();
    
    if (causalChains.length > 0) {
      // Layout along the longest chain
      const longestChain = causalChains.reduce((a, b) => 
        a.length > b.length ? a : b
      );
      
      const spacing = (width - 2 * this.options.margin) / (longestChain.length + 1);
      const y = height / 2;
      
      longestChain.forEach((entityId, index) => {
        const node = scene.getNode(entityId);
        if (node) {
          node.setPosition(
            this.options.margin + (index + 1) * spacing - node.width / 2,
            y - node.height / 2
          );
          node.drawOrder = index + 1;
        }
      });

      // Position remaining nodes
      const positioned = new Set(longestChain);
      const remaining = nodes.filter(n => !positioned.has(n.id));
      remaining.forEach((node, index) => {
        node.setPosition(
          this.options.margin + index * 80,
          height - 100
        );
        node.drawOrder = longestChain.length + index + 1;
      });
    } else {
      // No chains, use simple horizontal layout
      this.layoutHorizontally(nodes, width, height);
    }
  }

  /**
   * CYCLIC LAYOUT
   * Circular arrangement for processes
   */
  layoutCyclic(conceptGraph, scene) {
    const { width, height } = this.options;
    const centerX = width / 2;
    const centerY = height / 2;
    const nodes = scene.getNodes();
    
    this.layoutRadially(nodes, centerX, centerY, Math.min(width, height) / 3);
  }

  /**
   * HIERARCHICAL LAYOUT
   * Top-down tree for containment
   */
  layoutHierarchical(conceptGraph, scene) {
    const { width, height } = this.options;
    const hierarchy = conceptGraph.findContainmentHierarchy();
    const nodes = scene.getNodes();
    
    // Layout root nodes at top
    const levelHeight = (height - 2 * this.options.margin) / 3;
    let currentY = this.options.margin;
    
    const layoutLevel = (nodeIds, level) => {
      const levelNodes = nodeIds.map(id => scene.getNode(id)).filter(Boolean);
      const spacing = (width - 2 * this.options.margin) / (levelNodes.length + 1);
      
      levelNodes.forEach((node, index) => {
        node.setPosition(
          this.options.margin + (index + 1) * spacing - node.width / 2,
          currentY
        );
        node.drawOrder = level * 10 + index;
        
        // Layout children
        const children = hierarchy.children[node.id] || [];
        if (children.length > 0) {
          currentY += levelHeight;
          layoutLevel(children, level + 1);
          currentY -= levelHeight;
        }
      });
    };

    if (hierarchy.root.length > 0) {
      layoutLevel(hierarchy.root, 1);
    } else {
      this.layoutHorizontally(nodes, width, height);
    }
  }

  /**
   * COMPARATIVE LAYOUT
   * Side-by-side for comparisons
   */
  layoutComparative(conceptGraph, scene) {
    const { width, height } = this.options;
    const nodes = scene.getNodes();
    
    // Split into two groups
    const halfWidth = width / 2;
    const leftNodes = nodes.slice(0, Math.ceil(nodes.length / 2));
    const rightNodes = nodes.slice(Math.ceil(nodes.length / 2));

    // Left side
    leftNodes.forEach((node, index) => {
      node.setPosition(
        halfWidth / 2 - node.width / 2,
        this.options.margin + index * 80
      );
      node.drawOrder = index + 1;
    });

    // Right side
    rightNodes.forEach((node, index) => {
      node.setPosition(
        halfWidth + halfWidth / 2 - node.width / 2,
        this.options.margin + index * 80
      );
      node.drawOrder = leftNodes.length + index + 1;
    });

    // Add VS divider
    scene.addAnnotation('VS', { x: halfWidth, y: height / 2 }, {
      fontSize: 24,
      fontWeight: 'bold',
      color: '#7F8C8D',
    });
  }

  /**
   * TEMPORAL LAYOUT
   * Timeline left-to-right
   */
  layoutTemporal(conceptGraph, scene) {
    const { width, height } = this.options;
    const nodes = scene.getNodes();
    
    // Sort by temporal relationships
    // ... complex sorting logic
    
    // For now, use simple horizontal layout
    this.layoutHorizontally(nodes, width, height);
    
    // Add timeline line
    scene.decorations.push({
      type: 'line',
      x1: this.options.margin,
      y1: height / 2,
      x2: width - this.options.margin,
      y2: height / 2,
      style: { color: '#BDC3C7', width: 2, dashed: true },
    });
  }

  /**
   * STRUCTURAL LAYOUT
   * Anatomy/component layout with containment
   */
  layoutStructural(conceptGraph, scene) {
    const { width, height } = this.options;
    const nodes = scene.getNodes();
    
    // Find main structure
    const structures = nodes.filter(n => 
      n.entity.type === ENTITY_TYPES.STRUCTURE ||
      n.entity.type === ENTITY_TYPES.CELL ||
      n.entity.type === ENTITY_TYPES.ORGAN
    );

    if (structures.length > 0) {
      // Main structure at center
      const mainStructure = structures[0];
      mainStructure.setPosition(
        (width - mainStructure.width) / 2,
        (height - mainStructure.height) / 2
      );
      mainStructure.setSize(
        Math.min(width * 0.6, mainStructure.width * 2),
        Math.min(height * 0.6, mainStructure.height * 2)
      );
      mainStructure.drawOrder = 1;

      // Position parts inside or around
      const parts = nodes.filter(n => n.id !== mainStructure.id);
      this.layoutInsideContainer(parts, mainStructure);
    } else {
      this.layoutHorizontally(nodes, width, height);
    }
  }

  /**
   * GRAPH LAYOUT
   * Mathematical plot layout
   */
  layoutGraph(conceptGraph, scene) {
    const { width, height } = this.options;
    const nodes = scene.getNodes();
    
    // Find function or graph entities
    const graphs = nodes.filter(n => 
      n.entity.type === ENTITY_TYPES.FUNCTION ||
      n.entity.type === ENTITY_TYPES.GRAPH
    );

    if (graphs.length > 0) {
      // Graph takes most of the space
      const mainGraph = graphs[0];
      mainGraph.setPosition(this.options.margin, this.options.margin);
      mainGraph.setSize(
        width - 2 * this.options.margin,
        height - 2 * this.options.margin - 60
      );
      mainGraph.drawOrder = 1;

      // Other elements at bottom
      const others = nodes.filter(n => n.id !== mainGraph.id);
      others.forEach((node, index) => {
        node.setPosition(
          this.options.margin + index * 100,
          height - 50
        );
        node.drawOrder = 2 + index;
      });
    } else {
      this.layoutHorizontally(nodes, width, height);
    }
  }

  // ============================================
  // HELPER LAYOUT METHODS
  // ============================================

  layoutHorizontally(nodes, width, height) {
    const spacing = (width - 2 * this.options.margin) / (nodes.length + 1);
    const y = height / 2;

    nodes.forEach((node, index) => {
      node.setPosition(
        this.options.margin + (index + 1) * spacing - node.width / 2,
        y - node.height / 2
      );
      node.drawOrder = index + 1;
    });
  }

  layoutRadially(nodes, centerX, centerY, radius) {
    const angleStep = (2 * Math.PI) / nodes.length;

    nodes.forEach((node, index) => {
      const angle = index * angleStep - Math.PI / 2; // Start from top
      node.setPosition(
        centerX + Math.cos(angle) * radius - node.width / 2,
        centerY + Math.sin(angle) * radius - node.height / 2
      );
      node.drawOrder = index + 1;
    });
  }

  layoutInsideContainer(nodes, container) {
    const bounds = container.getBounds();
    const padding = 20;
    const innerWidth = bounds.width - 2 * padding;
    const innerHeight = bounds.height - 2 * padding;

    // Simple grid layout inside
    const cols = Math.ceil(Math.sqrt(nodes.length));
    const rows = Math.ceil(nodes.length / cols);
    const cellWidth = innerWidth / cols;
    const cellHeight = innerHeight / rows;

    nodes.forEach((node, index) => {
      const col = index % cols;
      const row = Math.floor(index / cols);
      
      node.setPosition(
        bounds.left + padding + col * cellWidth + (cellWidth - node.width) / 2,
        bounds.top + padding + row * cellHeight + (cellHeight - node.height) / 2
      );
      node.drawOrder = 10 + index;
    });
  }

  /**
   * Create arrows from relationships
   */
  createArrows(conceptGraph, scene) {
    for (const relationship of conceptGraph.relationships) {
      // Skip containment relationships (shown via nesting)
      if (relationship.type === RELATIONSHIP_TYPES.CONTAINS ||
          relationship.type === RELATIONSHIP_TYPES.INSIDE) {
        continue;
      }

      scene.addArrow(relationship.from, relationship.to, relationship);
    }
  }

  /**
   * Add annotations from concept graph
   */
  addAnnotations(conceptGraph, scene) {
    // Title annotation
    if (conceptGraph.metadata.topic) {
      scene.addAnnotation(conceptGraph.metadata.topic, {
        x: this.options.width / 2,
        y: 25,
      }, {
        fontSize: 20,
        fontWeight: 'bold',
        textAnchor: 'middle',
      });
    }
  }

  /**
   * Compute draw order for animation sequencing
   */
  computeDrawOrder(scene) {
    // Already set by layout strategies
    // Add animation delays
    let maxOrder = 0;
    for (const node of scene.getNodes()) {
      maxOrder = Math.max(maxOrder, node.drawOrder);
      node.animationDelay = node.drawOrder * 0.2; // 200ms between elements
    }

    // Arrows come after nodes
    for (let i = 0; i < scene.arrows.length; i++) {
      scene.arrows[i].drawOrder = maxOrder + i + 1;
      scene.arrows[i].animationDelay = (maxOrder + i + 1) * 0.2;
    }
  }
}

// ============================================
// FACTORY FUNCTIONS
// ============================================

/**
 * Create a composition engine
 */
export function createCompositionEngine(options) {
  return new CompositionEngine(options);
}

/**
 * Quick compose helper
 */
export function composeScene(conceptGraph, domain, options = {}) {
  const engine = new CompositionEngine(options);
  return engine.compose(conceptGraph, domain);
}

export { SceneGraph, SceneNode };
export default CompositionEngine;



