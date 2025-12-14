/**
 * 🧠 CONCEPT GRAPH
 * ================
 * 
 * Semantic representation of educational concepts.
 * NOT a simple list of entities — a rich graph with:
 * - Entities (objects, agents, quantities)
 * - Relationships (causal, spatial, temporal, comparative)
 * - Constraints (physical laws, logical rules)
 * - Processes (transformations, flows, cycles)
 * 
 * This is the foundation of intelligent visual reasoning.
 */

// ============================================
// RELATIONSHIP TYPES
// ============================================

export const RELATIONSHIP_TYPES = {
  // Causal
  CAUSES: 'causes',                    // A causes B
  ENABLES: 'enables',                  // A enables B to happen
  PREVENTS: 'prevents',                // A prevents B
  REQUIRES: 'requires',                // A requires B

  // Spatial
  CONTAINS: 'contains',                // A contains B
  INSIDE: 'inside',                    // A is inside B
  ADJACENT: 'adjacent',                // A is next to B
  ABOVE: 'above',                      // A is above B
  BELOW: 'below',                      // A is below B
  LEFT_OF: 'left_of',                  // A is left of B
  RIGHT_OF: 'right_of',                // A is right of B
  SURROUNDS: 'surrounds',              // A surrounds B
  ATTACHED_TO: 'attached_to',          // A is attached to B

  // Temporal
  BEFORE: 'before',                    // A happens before B
  AFTER: 'after',                      // A happens after B
  DURING: 'during',                    // A happens during B
  SIMULTANEOUS: 'simultaneous',        // A and B happen together

  // Comparative
  GREATER_THAN: 'greater_than',        // A > B
  LESS_THAN: 'less_than',              // A < B
  EQUAL_TO: 'equal_to',                // A = B
  OPPOSITE_TO: 'opposite_to',          // A is opposite to B
  PROPORTIONAL_TO: 'proportional_to',  // A ∝ B
  INVERSELY_PROPORTIONAL: 'inversely_proportional', // A ∝ 1/B

  // Transformational
  BECOMES: 'becomes',                  // A becomes B
  PRODUCES: 'produces',                // A produces B
  CONSUMES: 'consumes',                // A consumes B
  TRANSFORMS_INTO: 'transforms_into',  // A transforms into B

  // Structural
  PART_OF: 'part_of',                  // A is part of B
  COMPOSED_OF: 'composed_of',          // A is composed of B
  CONNECTS: 'connects',                // A connects B and C
  SEPARATES: 'separates',              // A separates B and C

  // Force/Interaction
  ACTS_ON: 'acts_on',                  // Force A acts on B
  REACTS_TO: 'reacts_to',              // A reacts to B
  ATTRACTS: 'attracts',                // A attracts B
  REPELS: 'repels',                    // A repels B
  BALANCES: 'balances',                // A balances B
};

// ============================================
// ENTITY TYPES
// ============================================

export const ENTITY_TYPES = {
  // Physical objects
  OBJECT: 'object',                    // Generic physical object
  BODY: 'body',                        // Rigid body (physics)
  PARTICLE: 'particle',                // Point mass
  FLUID: 'fluid',                      // Liquid or gas
  WAVE: 'wave',                        // Wave phenomenon
  FIELD: 'field',                      // Force field

  // Agents
  AGENT: 'agent',                      // Something that acts
  PERSON: 'person',                    // Human actor
  FORCE: 'force',                      // Physical force
  ENERGY: 'energy',                    // Energy form

  // Quantities
  QUANTITY: 'quantity',                // Measurable value
  VECTOR: 'vector',                    // Has magnitude + direction
  SCALAR: 'scalar',                    // Just magnitude

  // Structures
  STRUCTURE: 'structure',              // Organized arrangement
  SYSTEM: 'system',                    // Collection of interacting parts
  PROCESS: 'process',                  // Sequence of steps
  CYCLE: 'cycle',                      // Repeating process

  // Biological
  CELL: 'cell',                        // Biological cell
  ORGANISM: 'organism',                // Living thing
  ORGAN: 'organ',                      // Body organ
  MOLECULE: 'molecule',                // Chemical molecule

  // Chemical
  ATOM: 'atom',                        // Single atom
  COMPOUND: 'compound',                // Chemical compound
  REACTION: 'reaction',                // Chemical reaction
  SOLUTION: 'solution',                // Mixture

  // Mathematical
  FUNCTION: 'function',                // Mathematical function
  EQUATION: 'equation',                // Mathematical equation
  SHAPE: 'shape',                      // Geometric shape
  SET: 'set',                          // Mathematical set
  GRAPH: 'graph',                      // Graph structure
};

// ============================================
// CONSTRAINT TYPES
// ============================================

export const CONSTRAINT_TYPES = {
  // Conservation laws
  CONSERVATION_ENERGY: 'conservation_energy',
  CONSERVATION_MOMENTUM: 'conservation_momentum',
  CONSERVATION_MASS: 'conservation_mass',
  CONSERVATION_CHARGE: 'conservation_charge',

  // Physical constraints
  NEWTON_THIRD_LAW: 'newton_third_law',
  SPEED_LIMIT: 'speed_limit',          // c = 3×10⁸ m/s
  NON_NEGATIVE_MASS: 'non_negative_mass',
  NON_NEGATIVE_ENERGY: 'non_negative_energy',

  // Chemical constraints
  CHARGE_BALANCE: 'charge_balance',
  OCTET_RULE: 'octet_rule',
  VALENCE_LIMIT: 'valence_limit',

  // Biological constraints
  CELL_MEMBRANE_INTEGRITY: 'cell_membrane_integrity',
  BLOOD_FLOW_DIRECTION: 'blood_flow_direction',
  DNA_BASE_PAIRING: 'dna_base_pairing',

  // Mathematical constraints
  DOMAIN_RESTRICTION: 'domain_restriction',
  CONTINUITY: 'continuity',
  GEOMETRIC_CONSTRAINT: 'geometric_constraint',
};

// ============================================
// CONCEPT GRAPH CLASS
// ============================================

export class ConceptGraph {
  constructor() {
    this.entities = new Map();         // id → Entity
    this.relationships = [];           // Array of Relationship
    this.constraints = [];             // Array of Constraint
    this.processes = [];               // Array of Process
    this.metadata = {
      domain: null,                    // physics, chemistry, biology, math
      topic: null,                     // specific topic
      complexity: 'medium',            // simple, medium, complex
      visualType: null,                // inferred visual type
    };
  }

  /**
   * Add an entity to the graph
   */
  addEntity(id, type, properties = {}) {
    const entity = {
      id,
      type,
      label: properties.label || id,
      properties: {
        ...properties,
        visualHint: properties.visualHint || null, // What it should look like
        importance: properties.importance || 'normal', // visual emphasis
        dynamic: properties.dynamic || false, // changes over time
      },
    };
    this.entities.set(id, entity);
    return entity;
  }

  /**
   * Add a relationship between entities
   */
  addRelationship(fromId, toId, type, properties = {}) {
    const relationship = {
      from: fromId,
      to: toId,
      type,
      label: properties.label || null,
      properties: {
        ...properties,
        visualHint: properties.visualHint || null, // How to show it
        bidirectional: properties.bidirectional || false,
        strength: properties.strength || 'normal', // visual weight
      },
    };
    this.relationships.push(relationship);
    return relationship;
  }

  /**
   * Add a constraint to the graph
   */
  addConstraint(type, affectedEntities = [], properties = {}) {
    const constraint = {
      type,
      affectedEntities,
      properties,
      validate: properties.validate || null, // validation function
      errorMessage: properties.errorMessage || null,
    };
    this.constraints.push(constraint);
    return constraint;
  }

  /**
   * Add a process (sequence of steps)
   */
  addProcess(id, steps = [], properties = {}) {
    const process = {
      id,
      steps: steps.map((step, index) => ({
        order: index + 1,
        entityId: step.entityId || null,
        action: step.action,
        description: step.description,
        duration: step.duration || null,
      })),
      properties: {
        cyclic: properties.cyclic || false,
        reversible: properties.reversible || false,
        parallel: properties.parallel || false,
      },
    };
    this.processes.push(process);
    return process;
  }

  /**
   * Get entity by ID
   */
  getEntity(id) {
    return this.entities.get(id);
  }

  /**
   * Get all entities of a type
   */
  getEntitiesByType(type) {
    return Array.from(this.entities.values()).filter(e => e.type === type);
  }

  /**
   * Get relationships from an entity
   */
  getRelationshipsFrom(entityId) {
    return this.relationships.filter(r => r.from === entityId);
  }

  /**
   * Get relationships to an entity
   */
  getRelationshipsTo(entityId) {
    return this.relationships.filter(r => r.to === entityId);
  }

  /**
   * Get all relationships of a type
   */
  getRelationshipsByType(type) {
    return this.relationships.filter(r => r.type === type);
  }

  /**
   * Find causal chains (A causes B causes C)
   */
  findCausalChains(startId = null) {
    const chains = [];
    const causalRels = this.relationships.filter(r => 
      r.type === RELATIONSHIP_TYPES.CAUSES ||
      r.type === RELATIONSHIP_TYPES.PRODUCES ||
      r.type === RELATIONSHIP_TYPES.ENABLES
    );

    const visited = new Set();
    
    const buildChain = (entityId, currentChain) => {
      if (visited.has(entityId)) return;
      visited.add(entityId);
      
      const nextRels = causalRels.filter(r => r.from === entityId);
      
      if (nextRels.length === 0) {
        if (currentChain.length > 1) {
          chains.push([...currentChain]);
        }
        return;
      }
      
      for (const rel of nextRels) {
        buildChain(rel.to, [...currentChain, rel.to]);
      }
    };

    const startEntities = startId 
      ? [startId]
      : Array.from(this.entities.keys()).filter(id => 
          !causalRels.some(r => r.to === id)
        );

    for (const entityId of startEntities) {
      visited.clear();
      buildChain(entityId, [entityId]);
    }

    return chains;
  }

  /**
   * Find containment hierarchy (A contains B contains C)
   */
  findContainmentHierarchy() {
    const hierarchy = { root: [], children: {} };
    
    const containmentRels = this.relationships.filter(r => 
      r.type === RELATIONSHIP_TYPES.CONTAINS ||
      r.type === RELATIONSHIP_TYPES.COMPOSED_OF
    );

    // Find root containers (not contained by anything)
    const containedIds = new Set(containmentRels.map(r => r.to));
    const rootIds = Array.from(this.entities.keys()).filter(id => 
      !containedIds.has(id)
    );

    hierarchy.root = rootIds;

    // Build children map
    for (const rel of containmentRels) {
      if (!hierarchy.children[rel.from]) {
        hierarchy.children[rel.from] = [];
      }
      hierarchy.children[rel.from].push(rel.to);
    }

    return hierarchy;
  }

  /**
   * Infer visual type from graph structure
   */
  inferVisualType() {
    // Check for cycles
    const hasCycle = this.processes.some(p => p.properties.cyclic);
    if (hasCycle) return 'cycle';

    // Check for containment hierarchy
    const containments = this.getRelationshipsByType(RELATIONSHIP_TYPES.CONTAINS);
    if (containments.length > 2) return 'structure';

    // Check for causal chains
    const causalChains = this.findCausalChains();
    if (causalChains.some(chain => chain.length >= 3)) return 'process_flow';

    // Check for comparisons
    const comparisons = this.relationships.filter(r => 
      r.type === RELATIONSHIP_TYPES.OPPOSITE_TO ||
      r.type === RELATIONSHIP_TYPES.GREATER_THAN ||
      r.type === RELATIONSHIP_TYPES.LESS_THAN
    );
    if (comparisons.length > 0) return 'comparison';

    // Check for forces/interactions (physics)
    const forces = this.getEntitiesByType(ENTITY_TYPES.FORCE);
    if (forces.length > 0) return 'force_diagram';

    // Check for functions (math)
    const functions = this.getEntitiesByType(ENTITY_TYPES.FUNCTION);
    if (functions.length > 0) return 'graph';

    // Check for temporal sequences
    const temporalRels = this.relationships.filter(r =>
      r.type === RELATIONSHIP_TYPES.BEFORE ||
      r.type === RELATIONSHIP_TYPES.AFTER
    );
    if (temporalRels.length > 1) return 'timeline';

    // Default to scene
    return 'scene';
  }

  /**
   * Set metadata
   */
  setMetadata(key, value) {
    this.metadata[key] = value;
  }

  /**
   * Serialize to JSON
   */
  toJSON() {
    return {
      entities: Array.from(this.entities.entries()),
      relationships: this.relationships,
      constraints: this.constraints,
      processes: this.processes,
      metadata: this.metadata,
    };
  }

  /**
   * Create from JSON
   */
  static fromJSON(json) {
    const graph = new ConceptGraph();
    
    for (const [id, entity] of json.entities) {
      graph.entities.set(id, entity);
    }
    
    graph.relationships = json.relationships || [];
    graph.constraints = json.constraints || [];
    graph.processes = json.processes || [];
    graph.metadata = json.metadata || {};
    
    return graph;
  }

  /**
   * Get summary for debugging
   */
  getSummary() {
    return {
      entityCount: this.entities.size,
      relationshipCount: this.relationships.length,
      constraintCount: this.constraints.length,
      processCount: this.processes.length,
      domain: this.metadata.domain,
      inferredVisualType: this.inferVisualType(),
    };
  }
}

// ============================================
// FACTORY FUNCTIONS
// ============================================

/**
 * Create a simple force diagram graph
 */
export function createForceGraph(forces) {
  const graph = new ConceptGraph();
  graph.setMetadata('domain', 'physics');
  graph.setMetadata('topic', 'forces');

  for (const force of forces) {
    graph.addEntity(force.id, ENTITY_TYPES.FORCE, {
      label: force.label,
      magnitude: force.magnitude,
      direction: force.direction,
      origin: force.origin,
      visualHint: 'force_vector',
    });

    if (force.actingOn) {
      graph.addRelationship(force.id, force.actingOn, RELATIONSHIP_TYPES.ACTS_ON);
    }
  }

  return graph;
}

/**
 * Create a process flow graph
 */
export function createProcessGraph(steps) {
  const graph = new ConceptGraph();
  graph.setMetadata('visualType', 'process_flow');

  for (let i = 0; i < steps.length; i++) {
    const step = steps[i];
    graph.addEntity(step.id || `step_${i}`, ENTITY_TYPES.PROCESS, {
      label: step.label,
      order: i + 1,
      description: step.description,
    });

    if (i > 0) {
      const prevId = steps[i - 1].id || `step_${i - 1}`;
      const currId = step.id || `step_${i}`;
      graph.addRelationship(prevId, currId, RELATIONSHIP_TYPES.CAUSES);
    }
  }

  return graph;
}

/**
 * Create a structure/anatomy graph
 */
export function createStructureGraph(structure, parts) {
  const graph = new ConceptGraph();
  graph.setMetadata('visualType', 'structure');

  graph.addEntity(structure.id, ENTITY_TYPES.STRUCTURE, {
    label: structure.label,
    visualHint: structure.visualHint,
  });

  for (const part of parts) {
    graph.addEntity(part.id, part.type || ENTITY_TYPES.OBJECT, {
      label: part.label,
      visualHint: part.visualHint,
    });
    graph.addRelationship(structure.id, part.id, RELATIONSHIP_TYPES.CONTAINS);
  }

  return graph;
}

export default ConceptGraph;



