/**
 * 🎬 SCENE OBJECT RESOLVER
 * =========================
 * 
 * THE CRITICAL MISSING LAYER.
 * 
 * Converts abstract entities into RICH VISUAL SCENE OBJECTS.
 * This is NOT node → box conversion. This is semantic visual intelligence.
 * 
 * A SceneObject has:
 * - objectType: ACTOR | SURFACE | ENVIRONMENT | EFFECT | FORCE | LABEL
 * - visualForm: The concrete visual representation (sliding_block, rough_surface, etc.)
 * - spatialRules: How it positions relative to others (ON_TOP_OF, ATTACHED_TO, etc.)
 * - renderHints: Visual styling and animation hints
 * 
 * The same "friction" entity becomes:
 * - Ice scene: smooth_ice_surface + sliding_person
 * - Carpet scene: rough_carpet_texture + stopping_object
 * - Microscopic: surface_bumps + interlocking_molecules
 */

import { ENTITY_TYPES, RELATIONSHIP_TYPES } from '../core/ConceptGraph';
import { INTENT_TYPES } from './IntentClassifier';
import { STRUCTURAL_FORMS } from './FormSelector';

// ============================================
// SCENE OBJECT TYPES
// ============================================

export const OBJECT_TYPES = {
  // Primary elements - things that DO something
  ACTOR: 'actor',                    // Moving objects, agents (block, person, car)
  SURFACE: 'surface',                // Things actors interact with (ground, ice, carpet)
  ENVIRONMENT: 'environment',        // Background context (sky, lab, cell interior)
  
  // Physics/forces
  FORCE: 'force',                    // Force vectors, interactions
  MOTION: 'motion',                  // Motion indicators, trajectories
  EFFECT: 'effect',                  // Visual effects (glow, particles, trails)
  
  // Structural
  CONTAINER: 'container',            // Contains other objects (cell membrane, beaker)
  REGION: 'region',                  // Bounded areas (reaction zone, field region)
  
  // Annotations
  LABEL: 'label',                    // Text annotations
  INDICATOR: 'indicator',            // Arrows, pointers, highlights
  MEASUREMENT: 'measurement',        // Rulers, scales, graphs
};

// ============================================
// VISUAL FORMS - Concrete visual representations
// ============================================

export const VISUAL_FORMS = {
  // Actor forms
  SLIDING_BLOCK: 'sliding_block',
  ROLLING_BALL: 'rolling_ball',
  PERSON_WALKING: 'person_walking',
  PERSON_SLIDING: 'person_sliding',
  CAR_MOVING: 'car_moving',
  PARTICLE: 'particle',
  PLANET_BODY: 'planet_body',
  
  // Surface forms
  FLAT_GROUND: 'flat_ground',
  ROUGH_SURFACE: 'rough_surface',
  SMOOTH_ICE: 'smooth_ice',
  INCLINED_PLANE: 'inclined_plane',
  CARPET_TEXTURE: 'carpet_texture',
  MICROSCOPIC_BUMPS: 'microscopic_bumps',
  WATER_SURFACE: 'water_surface',
  
  // Environment forms
  OUTDOOR_SCENE: 'outdoor_scene',
  LAB_BACKGROUND: 'lab_background',
  CELL_INTERIOR: 'cell_interior',
  SPACE_BACKGROUND: 'space_background',
  ROAD_SCENE: 'road_scene',
  ROOM_INTERIOR: 'room_interior',
  
  // Force forms
  FORCE_ARROW: 'force_arrow',
  GRAVITATIONAL_PULL: 'gravitational_pull',
  FRICTION_RESISTANCE: 'friction_resistance',
  SPRING_FORCE: 'spring_force',
  TENSION_LINE: 'tension_line',
  
  // Motion forms
  VELOCITY_VECTOR: 'velocity_vector',
  MOTION_TRAIL: 'motion_trail',
  TRAJECTORY_ARC: 'trajectory_arc',
  OSCILLATION_PATH: 'oscillation_path',
  
  // Effect forms
  IMPACT_BURST: 'impact_burst',
  HEAT_GLOW: 'heat_glow',
  LIGHT_RAYS: 'light_rays',
  PARTICLE_EMISSION: 'particle_emission',
  ENERGY_FLOW: 'energy_flow',
  CHAOS_SCATTER: 'chaos_scatter',
  
  // Biology forms
  CELL_MEMBRANE: 'cell_membrane',
  CHLOROPLAST: 'chloroplast',
  MITOCHONDRIA: 'mitochondria',
  DNA_HELIX: 'dna_helix',
  LEAF_CROSS_SECTION: 'leaf_cross_section',
  
  // Chemistry forms
  ATOM_BOHR: 'atom_bohr',
  MOLECULE_STRUCTURE: 'molecule_structure',
  BEAKER_CONTAINER: 'beaker_container',
  REACTION_ARROW: 'reaction_arrow',
  
  // Measurement forms
  RULER_SCALE: 'ruler_scale',
  GRAPH_AXES: 'graph_axes',
  FORMULA_DISPLAY: 'formula_display',
};

// ============================================
// SPATIAL RULES - How objects relate spatially
// ============================================

export const SPATIAL_RULES = {
  // Relative positioning
  ON_TOP_OF: 'on_top_of',             // Object sits on another
  BELOW: 'below',                      // Object is below another
  LEFT_OF: 'left_of',                  // Spatial ordering
  RIGHT_OF: 'right_of',
  INSIDE: 'inside',                    // Contained within
  SURROUNDING: 'surrounding',          // Wraps around
  
  // Attachment
  ATTACHED_TO: 'attached_to',          // Physically connected
  ORIGINATES_FROM: 'originates_from',  // Starts from (forces, arrows)
  POINTS_TOWARD: 'points_toward',      // Direction indicator
  
  // Flow
  FLOWS_THROUGH: 'flows_through',      // Movement path
  EMANATES_FROM: 'emanates_from',      // Radiation, emission
  CONNECTS: 'connects',                // Links two objects
  
  // Background
  FILLS_BACKGROUND: 'fills_background', // Environment
  SPANS_WIDTH: 'spans_width',           // Full width element
  CENTERED: 'centered',                 // Center of scene
  
  // Comparison
  SIDE_BY_SIDE: 'side_by_side',        // Parallel comparison
  OPPOSITE: 'opposite',                 // Opposing positions
};

// ============================================
// SCENE OBJECT CLASS
// ============================================

export class SceneObject {
  constructor(id, objectType, visualForm, options = {}) {
    this.id = id;
    this.objectType = objectType;
    this.visualForm = visualForm;
    
    // Spatial relationships
    this.spatialRules = options.spatialRules || [];
    this.relatedTo = options.relatedTo || null;  // ID of related object
    
    // Visual properties
    this.renderHints = {
      color: options.color || null,
      size: options.size || 'medium',  // small, medium, large
      emphasis: options.emphasis || 'normal',  // normal, high, low
      variant: options.variant || null,
      opacity: options.opacity || 1,
      animated: options.animated !== false,
      ...options.renderHints,
    };
    
    // Content
    this.label = options.label || null;
    this.properties = options.properties || {};
    
    // Source entity reference
    this.sourceEntity = options.sourceEntity || null;
    
    // Animation
    this.drawOrder = options.drawOrder || 0;
    this.animationDelay = options.animationDelay || 0;
  }
  
  /**
   * Add a spatial relationship
   */
  addSpatialRule(rule, relatedToId = null) {
    this.spatialRules.push({ rule, relatedTo: relatedToId });
    return this;
  }
  
  /**
   * Set visual emphasis
   */
  setEmphasis(level) {
    this.renderHints.emphasis = level;
    return this;
  }
  
  /**
   * Convert to serializable format
   */
  toJSON() {
    return {
      id: this.id,
      objectType: this.objectType,
      visualForm: this.visualForm,
      spatialRules: this.spatialRules,
      renderHints: this.renderHints,
      label: this.label,
      properties: this.properties,
      drawOrder: this.drawOrder,
      animationDelay: this.animationDelay,
    };
  }
}

// ============================================
// INTENT-BASED VISUAL STRATEGY MAP
// ============================================

/**
 * Maps intent types to visual strategies for scene construction.
 * Different intents produce DIFFERENT scene objects for the SAME topic.
 */
const INTENT_VISUAL_STRATEGIES = {
  [INTENT_TYPES.CONCEPTUAL]: {
    name: 'explanation_scene',
    environment: VISUAL_FORMS.OUTDOOR_SCENE,
    actorStyle: 'realistic',
    showLabels: true,
    showForces: true,
    showCausation: true,
    description: 'Rich scene showing concept in action',
  },
  
  [INTENT_TYPES.CAUSAL_INQUIRY]: {
    name: 'microscopic_zoom',
    environment: VISUAL_FORMS.LAB_BACKGROUND,
    actorStyle: 'detailed',
    showLabels: true,
    showCausation: true,
    zoomLevel: 'microscopic',
    description: 'Zoom into the WHY - show underlying mechanism',
  },
  
  [INTENT_TYPES.COUNTERFACTUAL]: {
    name: 'split_reality',
    environment: VISUAL_FORMS.OUTDOOR_SCENE,
    splitView: true,
    showContrast: true,
    realityLabel: 'With {concept}',
    alternateLabel: 'Without {concept}',
    description: 'Side-by-side reality vs alternate world',
  },
  
  [INTENT_TYPES.COMPARATIVE]: {
    name: 'side_by_side',
    environment: VISUAL_FORMS.LAB_BACKGROUND,
    splitView: true,
    showDifferences: true,
    highlightContrasts: true,
    description: 'Direct comparison of two scenarios',
  },
  
  [INTENT_TYPES.INTUITIVE]: {
    name: 'relatable_metaphor',
    environment: VISUAL_FORMS.ROOM_INTERIOR,
    actorStyle: 'everyday',
    useMetaphors: true,
    indianContext: true,  // Indian student context
    description: 'Everyday scenario student can relate to',
  },
  
  [INTENT_TYPES.MECHANISTIC]: {
    name: 'step_by_step',
    environment: VISUAL_FORMS.LAB_BACKGROUND,
    showSequence: true,
    numberSteps: true,
    description: 'Step-by-step breakdown of mechanism',
  },
  
  [INTENT_TYPES.TEMPORAL]: {
    name: 'timeline_flow',
    environment: VISUAL_FORMS.OUTDOOR_SCENE,
    showTimeline: true,
    showProgression: true,
    description: 'Changes over time',
  },
  
  [INTENT_TYPES.QUANTITATIVE]: {
    name: 'formula_focus',
    environment: VISUAL_FORMS.LAB_BACKGROUND,
    showFormula: true,
    showMeasurements: true,
    showGraph: true,
    description: 'Emphasize mathematical relationships',
  },
};

// ============================================
// DOMAIN-SPECIFIC SCENE TEMPLATES
// ============================================

/**
 * Physics scene templates for common concepts
 */
const PHYSICS_SCENE_TEMPLATES = {
  friction: {
    actors: [
      { type: 'sliding_object', forms: ['SLIDING_BLOCK', 'PERSON_SLIDING', 'CAR_MOVING'] },
    ],
    surfaces: [
      { type: 'contact_surface', forms: ['ROUGH_SURFACE', 'SMOOTH_ICE', 'CARPET_TEXTURE'] },
    ],
    forces: ['friction_force', 'normal_force', 'applied_force', 'gravity'],
    environments: ['OUTDOOR_SCENE', 'ROOM_INTERIOR', 'ROAD_SCENE'],
    effects: ['motion_trail', 'heat_glow'],
    intuitiveMetaphors: {
      ice_skating: { actor: 'PERSON_SLIDING', surface: 'SMOOTH_ICE', environment: 'OUTDOOR_SCENE' },
      carpet_walk: { actor: 'PERSON_WALKING', surface: 'CARPET_TEXTURE', environment: 'ROOM_INTERIOR' },
      car_braking: { actor: 'CAR_MOVING', surface: 'ROUGH_SURFACE', environment: 'ROAD_SCENE' },
    },
    counterfactual: {
      withFriction: { surface: 'ROUGH_SURFACE', effect: null, motionState: 'controlled' },
      withoutFriction: { surface: 'SMOOTH_ICE', effect: 'CHAOS_SCATTER', motionState: 'uncontrolled' },
    },
    microscopic: {
      surface: 'MICROSCOPIC_BUMPS',
      showInterlocking: true,
      zoom: 100,
    },
  },
  
  gravity: {
    actors: [
      { type: 'falling_object', forms: ['ROLLING_BALL', 'PARTICLE', 'PERSON_WALKING'] },
    ],
    forces: ['gravitational_force', 'normal_force'],
    environments: ['OUTDOOR_SCENE', 'SPACE_BACKGROUND'],
    counterfactual: {
      withGravity: { showGrounding: true, showWeight: true },
      withoutGravity: { showFloating: true, showWeightlessness: true },
    },
  },
  
  projectile_motion: {
    actors: [{ type: 'projectile', forms: ['ROLLING_BALL', 'PARTICLE'] }],
    motions: ['TRAJECTORY_ARC', 'VELOCITY_VECTOR'],
    forces: ['gravity'],
    environments: ['OUTDOOR_SCENE'],
    showDecomposition: true,
  },
  
  newtons_laws: {
    actors: [{ type: 'body', forms: ['SLIDING_BLOCK', 'CAR_MOVING'] }],
    forces: ['applied_force', 'friction_force', 'normal_force', 'gravity'],
    showActionReaction: true,
    environments: ['LAB_BACKGROUND', 'OUTDOOR_SCENE'],
  },
};

/**
 * Biology scene templates
 */
const BIOLOGY_SCENE_TEMPLATES = {
  photosynthesis: {
    containers: ['LEAF_CROSS_SECTION', 'CHLOROPLAST'],
    flows: ['light_rays_in', 'co2_in', 'glucose_out', 'oxygen_out'],
    environments: ['OUTDOOR_SCENE'],
    effects: ['LIGHT_RAYS', 'ENERGY_FLOW'],
    microscopic: {
      container: 'CHLOROPLAST',
      showThylakoids: true,
      showChlorophyll: true,
    },
  },
  
  cell_structure: {
    containers: ['CELL_MEMBRANE'],
    parts: ['MITOCHONDRIA', 'CHLOROPLAST', 'nucleus'],
    environments: ['CELL_INTERIOR'],
  },
  
  dna_replication: {
    actors: ['DNA_HELIX'],
    showUnwinding: true,
    showReplication: true,
    environments: ['CELL_INTERIOR'],
  },
};

/**
 * Chemistry scene templates
 */
const CHEMISTRY_SCENE_TEMPLATES = {
  atomic_structure: {
    actors: ['ATOM_BOHR'],
    showElectronShells: true,
    environments: ['LAB_BACKGROUND'],
  },
  
  chemical_reaction: {
    actors: ['MOLECULE_STRUCTURE'],
    containers: ['BEAKER_CONTAINER'],
    flows: ['REACTION_ARROW'],
    showBondBreaking: true,
    showBondForming: true,
    environments: ['LAB_BACKGROUND'],
  },
  
  chemical_bonding: {
    actors: ['ATOM_BOHR', 'MOLECULE_STRUCTURE'],
    showElectronTransfer: true,
    showElectronSharing: true,
    environments: ['LAB_BACKGROUND'],
  },
};

// ============================================
// SCENE OBJECT RESOLVER CLASS
// ============================================

export class SceneObjectResolver {
  constructor(options = {}) {
    this.options = {
      preferMetaphors: true,         // Use real-world metaphors
      indianContext: true,            // Indian student context
      showEnvironments: true,         // Include background environments
      ...options,
    };
    
    // Scene templates by domain
    this.sceneTemplates = {
      physics: PHYSICS_SCENE_TEMPLATES,
      biology: BIOLOGY_SCENE_TEMPLATES,
      chemistry: CHEMISTRY_SCENE_TEMPLATES,
    };
  }
  
  /**
   * Main resolution method: Convert ConceptGraph entities to SceneObjects
   * 
   * @param {ConceptGraph} conceptGraph - The parsed concept graph
   * @param {Object} intentResult - Result from IntentClassifier
   * @param {Object} formResult - Result from FormSelector
   * @param {Object} context - Additional context (domain, topic, etc.)
   * @returns {Array<SceneObject>} Array of scene objects
   */
  resolve(conceptGraph, intentResult, formResult, context = {}) {
    const domain = conceptGraph.metadata.domain || context.domain || 'physics';
    const topic = conceptGraph.metadata.topic || context.topic || 'unknown';
    const intent = intentResult.primary;
    
    console.log('🎬 [SceneObjectResolver] Resolving scene objects');
    console.log('🎬 Domain:', domain, '| Topic:', topic, '| Intent:', intent);
    
    // Get visual strategy based on intent
    const strategy = INTENT_VISUAL_STRATEGIES[intent] || INTENT_VISUAL_STRATEGIES[INTENT_TYPES.CONCEPTUAL];
    
    // Get scene template if available
    const templates = this.sceneTemplates[domain] || {};
    const topicTemplate = this.findTopicTemplate(topic, templates);
    
    // Build scene objects
    const sceneObjects = [];
    let drawOrder = 0;
    
    // 1. Add environment (background)
    if (this.options.showEnvironments) {
      const envObject = this.createEnvironment(strategy, topicTemplate, domain);
      if (envObject) {
        envObject.drawOrder = drawOrder++;
        sceneObjects.push(envObject);
      }
    }
    
    // 2. Add surfaces if relevant
    const surfaceObjects = this.createSurfaces(conceptGraph, strategy, topicTemplate, intent);
    surfaceObjects.forEach(obj => {
      obj.drawOrder = drawOrder++;
      sceneObjects.push(obj);
    });
    
    // 3. Convert entities to actors/objects
    let hasActors = false;
    for (const [entityId, entity] of conceptGraph.entities) {
      const sceneObject = this.resolveEntity(entity, entityId, strategy, topicTemplate, intent, domain);
      if (sceneObject) {
        sceneObject.drawOrder = drawOrder++;
        sceneObjects.push(sceneObject);
        if (sceneObject.objectType === OBJECT_TYPES.ACTOR) {
          hasActors = true;
        }
      }
    }
    
    // ============================================
    // CRITICAL FIX: Create default actors if none exist!
    // For physics topics like friction, we MUST have an object
    // ============================================
    if (domain === 'physics' && !hasActors) {
      console.log('🎬 [SceneObjectResolver] No actors found - creating default actor for', topic);
      const defaultActor = this.createDefaultActor(topic, strategy, topicTemplate, intent);
      if (defaultActor) {
        defaultActor.drawOrder = drawOrder++;
        sceneObjects.push(defaultActor);
        hasActors = true;
      }
    }
    
    // 4. Add forces if physics domain
    if (domain === 'physics') {
      const forceObjects = this.createForces(conceptGraph, strategy, topicTemplate);
      // If we created default actor, create default forces too
      if (forceObjects.length === 0 && hasActors) {
        const defaultForces = this.createDefaultForces(topic, topicTemplate);
        defaultForces.forEach(obj => {
          obj.drawOrder = drawOrder++;
          sceneObjects.push(obj);
        });
      } else {
        forceObjects.forEach(obj => {
          obj.drawOrder = drawOrder++;
          sceneObjects.push(obj);
        });
      }
    }
    
    // 5. Add effects based on intent
    const effectObjects = this.createEffects(strategy, topicTemplate, intent);
    effectObjects.forEach(obj => {
      obj.drawOrder = drawOrder++;
      sceneObjects.push(obj);
    });
    
    // 6. Add title label
    const titleLabel = this.createTitleLabel(topic);
    titleLabel.drawOrder = drawOrder++;
    sceneObjects.push(titleLabel);
    
    // 7. Handle special cases based on form
    if (formResult.form === STRUCTURAL_FORMS.COUNTERFACTUAL || 
        formResult.form === STRUCTURAL_FORMS.COMPARISON) {
      this.addComparisonObjects(sceneObjects, conceptGraph, strategy, topicTemplate);
    }
    
    // 8. Compute animation delays
    this.computeAnimationDelays(sceneObjects);
    
    console.log('🎬 [SceneObjectResolver] Created', sceneObjects.length, 'scene objects');
    sceneObjects.forEach(obj => console.log('  -', obj.objectType, ':', obj.visualForm, '| id:', obj.id));
    
    return sceneObjects;
  }
  
  /**
   * Create a default actor when none exists in the concept graph
   * This is CRITICAL for questions like "Explain friction" where no object is mentioned
   */
  createDefaultActor(topic, strategy, topicTemplate, intent) {
    const topicLower = topic.toLowerCase();
    
    // Determine actor type based on topic
    let visualForm = VISUAL_FORMS.SLIDING_BLOCK;  // Default for most physics
    let label = 'Object';
    
    // Topic-specific actors
    if (topicLower.includes('friction')) {
      // For intuitive understanding, use relatable actor
      if (intent === INTENT_TYPES.INTUITIVE) {
        visualForm = VISUAL_FORMS.PERSON_SLIDING;
        label = 'Person';
      } else {
        visualForm = VISUAL_FORMS.SLIDING_BLOCK;
        label = 'Block';
      }
    } else if (topicLower.includes('projectile') || topicLower.includes('throw')) {
      visualForm = VISUAL_FORMS.ROLLING_BALL;
      label = 'Ball';
    } else if (topicLower.includes('car') || topicLower.includes('vehicle')) {
      visualForm = VISUAL_FORMS.CAR_MOVING;
      label = 'Car';
    } else if (topicLower.includes('gravity') || topicLower.includes('falling')) {
      visualForm = VISUAL_FORMS.ROLLING_BALL;
      label = 'Ball';
    } else if (topicLower.includes('momentum') || topicLower.includes('collision')) {
      visualForm = VISUAL_FORMS.ROLLING_BALL;
      label = 'Ball';
    }
    
    // Use template if available
    if (topicTemplate?.actors?.[0]?.forms) {
      visualForm = VISUAL_FORMS[topicTemplate.actors[0].forms[0]] || visualForm;
    }
    
    return new SceneObject(
      'actor_default',
      OBJECT_TYPES.ACTOR,
      visualForm,
      {
        label,
        spatialRules: [{ rule: SPATIAL_RULES.ON_TOP_OF, relatedTo: 'surface_main' }],
        renderHints: {
          emphasis: 'high',
          size: 'large',
          animated: true,
        },
        properties: {
          isDefaultActor: true,
        },
      }
    );
  }
  
  /**
   * Create default forces when topic requires them
   */
  createDefaultForces(topic, topicTemplate) {
    const topicLower = topic.toLowerCase();
    const forces = [];
    
    // Common physics scenarios
    if (topicLower.includes('friction')) {
      // Friction scenario: show all relevant forces
      forces.push(new SceneObject('force_applied', OBJECT_TYPES.FORCE, VISUAL_FORMS.FORCE_ARROW, {
        label: 'Applied Force (F)',
        properties: { variant: 'applied', direction: 'right', magnitude: 80 },
        spatialRules: [{ rule: SPATIAL_RULES.ORIGINATES_FROM, relatedTo: 'actor_default' }],
        renderHints: { color: '#3498DB' },
      }));
      
      forces.push(new SceneObject('force_friction', OBJECT_TYPES.FORCE, VISUAL_FORMS.FRICTION_RESISTANCE, {
        label: 'Friction Force (f = μN)',
        properties: { variant: 'friction', direction: 'left', magnitude: 60 },
        spatialRules: [{ rule: SPATIAL_RULES.ORIGINATES_FROM, relatedTo: 'actor_default' }],
        renderHints: { color: '#E67E22' },
      }));
      
      forces.push(new SceneObject('force_normal', OBJECT_TYPES.FORCE, VISUAL_FORMS.FORCE_ARROW, {
        label: 'Normal Force (N)',
        properties: { variant: 'normal', direction: 'up', magnitude: 70 },
        spatialRules: [{ rule: SPATIAL_RULES.ORIGINATES_FROM, relatedTo: 'actor_default' }],
        renderHints: { color: '#3498DB' },
      }));
      
      forces.push(new SceneObject('force_weight', OBJECT_TYPES.FORCE, VISUAL_FORMS.GRAVITATIONAL_PULL, {
        label: 'Weight (W = mg)',
        properties: { variant: 'gravitational', direction: 'down', magnitude: 70 },
        spatialRules: [{ rule: SPATIAL_RULES.ORIGINATES_FROM, relatedTo: 'actor_default' }],
        renderHints: { color: '#E74C3C' },
      }));
    } else if (topicLower.includes('gravity') || topicLower.includes('weight')) {
      forces.push(new SceneObject('force_weight', OBJECT_TYPES.FORCE, VISUAL_FORMS.GRAVITATIONAL_PULL, {
        label: 'Weight (W = mg)',
        properties: { variant: 'gravitational', direction: 'down', magnitude: 80 },
        spatialRules: [{ rule: SPATIAL_RULES.ORIGINATES_FROM, relatedTo: 'actor_default' }],
        renderHints: { color: '#E74C3C' },
      }));
    } else if (topicLower.includes('newton') || topicLower.includes('force')) {
      forces.push(new SceneObject('force_applied', OBJECT_TYPES.FORCE, VISUAL_FORMS.FORCE_ARROW, {
        label: 'Applied Force (F)',
        properties: { variant: 'applied', direction: 'right', magnitude: 80 },
        spatialRules: [{ rule: SPATIAL_RULES.ORIGINATES_FROM, relatedTo: 'actor_default' }],
        renderHints: { color: '#3498DB' },
      }));
    }
    
    return forces;
  }
  
  /**
   * Create title label for the scene
   */
  createTitleLabel(topic) {
    // Clean up topic for display
    let displayTopic = topic;
    if (topic.toLowerCase().startsWith('explain ')) {
      displayTopic = topic.substring(8);
    }
    displayTopic = displayTopic.charAt(0).toUpperCase() + displayTopic.slice(1);
    
    return new SceneObject(
      'label_title',
      OBJECT_TYPES.LABEL,
      'TITLE_LABEL',
      {
        label: displayTopic,
        spatialRules: [{ rule: SPATIAL_RULES.FILLS_BACKGROUND }],
        renderHints: {
          position: 'top-right',
          size: 'medium',
          emphasis: 'normal',
        },
      }
    );
  }
  
  /**
   * Find matching topic template
   */
  findTopicTemplate(topic, templates) {
    const topicLower = topic.toLowerCase();
    
    // Direct match
    if (templates[topicLower]) {
      return templates[topicLower];
    }
    
    // Partial match
    for (const [key, template] of Object.entries(templates)) {
      if (topicLower.includes(key) || key.includes(topicLower)) {
        return template;
      }
    }
    
    return null;
  }
  
  /**
   * Create environment background
   */
  createEnvironment(strategy, topicTemplate, domain) {
    let visualForm = strategy.environment;
    
    // Override from template if available
    if (topicTemplate?.environments) {
      visualForm = topicTemplate.environments[0];
    }
    
    // Map string to VISUAL_FORMS constant if needed
    const formKey = typeof visualForm === 'string' ? visualForm : VISUAL_FORMS.OUTDOOR_SCENE;
    
    return new SceneObject(
      'env_background',
      OBJECT_TYPES.ENVIRONMENT,
      formKey,
      {
        spatialRules: [{ rule: SPATIAL_RULES.FILLS_BACKGROUND }],
        renderHints: {
          opacity: 0.8,
          size: 'full',
        },
        drawOrder: 0,
      }
    );
  }
  
  /**
   * Create surface objects
   */
  createSurfaces(conceptGraph, strategy, topicTemplate, intent) {
    const surfaces = [];
    
    // Check if we need surfaces from template
    if (!topicTemplate?.surfaces) {
      // Default ground for physics
      surfaces.push(new SceneObject(
        'surface_ground',
        OBJECT_TYPES.SURFACE,
        VISUAL_FORMS.FLAT_GROUND,
        {
          spatialRules: [{ rule: SPATIAL_RULES.SPANS_WIDTH }],
          renderHints: { size: 'large' },
        }
      ));
      return surfaces;
    }
    
    // Use template surfaces based on intent
    if (intent === INTENT_TYPES.CAUSAL_INQUIRY && topicTemplate.microscopic) {
      // Microscopic view - show surface details
      surfaces.push(new SceneObject(
        'surface_microscopic',
        OBJECT_TYPES.SURFACE,
        VISUAL_FORMS.MICROSCOPIC_BUMPS,
        {
          spatialRules: [{ rule: SPATIAL_RULES.SPANS_WIDTH }],
          renderHints: { 
            size: 'large',
            variant: 'zoomed',
            emphasis: 'high',
          },
          properties: {
            zoom: topicTemplate.microscopic.zoom || 100,
            showInterlocking: topicTemplate.microscopic.showInterlocking,
          },
        }
      ));
    } else if (intent === INTENT_TYPES.INTUITIVE && topicTemplate.intuitiveMetaphors) {
      // Use intuitive metaphor surface
      const metaphor = this.selectMetaphor(topicTemplate.intuitiveMetaphors);
      surfaces.push(new SceneObject(
        'surface_metaphor',
        OBJECT_TYPES.SURFACE,
        VISUAL_FORMS[metaphor.surface] || VISUAL_FORMS.ROUGH_SURFACE,
        {
          spatialRules: [{ rule: SPATIAL_RULES.SPANS_WIDTH }],
          renderHints: { size: 'large' },
        }
      ));
    } else if (intent === INTENT_TYPES.COUNTERFACTUAL && topicTemplate.counterfactual) {
      // Split view - two different surfaces
      const cf = topicTemplate.counterfactual;
      
      surfaces.push(new SceneObject(
        'surface_reality',
        OBJECT_TYPES.SURFACE,
        VISUAL_FORMS[cf.withFriction?.surface] || VISUAL_FORMS.ROUGH_SURFACE,
        {
          spatialRules: [{ rule: SPATIAL_RULES.LEFT_OF }],
          label: 'With Friction',
          renderHints: { size: 'medium' },
        }
      ));
      
      surfaces.push(new SceneObject(
        'surface_alternate',
        OBJECT_TYPES.SURFACE,
        VISUAL_FORMS[cf.withoutFriction?.surface] || VISUAL_FORMS.SMOOTH_ICE,
        {
          spatialRules: [{ rule: SPATIAL_RULES.RIGHT_OF }],
          label: 'Without Friction',
          renderHints: { size: 'medium' },
        }
      ));
    } else {
      // Default surface from template
      const surfaceDef = topicTemplate.surfaces[0];
      surfaces.push(new SceneObject(
        'surface_main',
        OBJECT_TYPES.SURFACE,
        VISUAL_FORMS[surfaceDef.forms[0]] || VISUAL_FORMS.ROUGH_SURFACE,
        {
          spatialRules: [{ rule: SPATIAL_RULES.SPANS_WIDTH }],
          renderHints: { size: 'large' },
        }
      ));
    }
    
    return surfaces;
  }
  
  /**
   * Resolve a single entity to a SceneObject
   */
  resolveEntity(entity, entityId, strategy, topicTemplate, intent, domain) {
    const entityType = entity.type;
    
    // Skip if already handled as surface/force
    if (entity.properties?.visualHint === 'ground_plane') {
      return null;
    }
    
    // Determine object type and visual form based on entity type
    let objectType = OBJECT_TYPES.ACTOR;
    let visualForm = VISUAL_FORMS.SLIDING_BLOCK;  // Default
    let spatialRules = [];
    
    // Map entity types to scene object types
    switch (entityType) {
      case ENTITY_TYPES.BODY:
      case ENTITY_TYPES.OBJECT:
        objectType = OBJECT_TYPES.ACTOR;
        visualForm = this.selectActorForm(entity, strategy, topicTemplate, intent);
        spatialRules.push({ rule: SPATIAL_RULES.ON_TOP_OF, relatedTo: 'surface_main' });
        break;
        
      case ENTITY_TYPES.FORCE:
        objectType = OBJECT_TYPES.FORCE;
        visualForm = this.selectForceForm(entity);
        spatialRules.push({ rule: SPATIAL_RULES.ATTACHED_TO, relatedTo: entity.properties?.actingOn });
        break;
        
      case ENTITY_TYPES.CELL:
        objectType = OBJECT_TYPES.CONTAINER;
        visualForm = VISUAL_FORMS.CELL_MEMBRANE;
        spatialRules.push({ rule: SPATIAL_RULES.CENTERED });
        break;
        
      case ENTITY_TYPES.ATOM:
        objectType = OBJECT_TYPES.ACTOR;
        visualForm = VISUAL_FORMS.ATOM_BOHR;
        break;
        
      case ENTITY_TYPES.MOLECULE:
        objectType = OBJECT_TYPES.ACTOR;
        visualForm = VISUAL_FORMS.MOLECULE_STRUCTURE;
        break;
        
      case ENTITY_TYPES.STRUCTURE:
        objectType = OBJECT_TYPES.CONTAINER;
        visualForm = this.selectStructureForm(entity, domain);
        break;
        
      case ENTITY_TYPES.PROCESS:
        objectType = OBJECT_TYPES.REGION;
        visualForm = VISUAL_FORMS.ENERGY_FLOW;
        break;
        
      default:
        objectType = OBJECT_TYPES.ACTOR;
        visualForm = VISUAL_FORMS.SLIDING_BLOCK;
    }
    
    return new SceneObject(
      entityId,
      objectType,
      visualForm,
      {
        spatialRules,
        label: entity.label,
        properties: entity.properties || {},
        sourceEntity: entity,
        renderHints: {
          emphasis: entity.properties?.importance === 'high' ? 'high' : 'normal',
          variant: entity.properties?.variant,
        },
      }
    );
  }
  
  /**
   * Select appropriate actor form based on context
   */
  selectActorForm(entity, strategy, topicTemplate, intent) {
    // Intuitive intent - use metaphors
    if (intent === INTENT_TYPES.INTUITIVE && topicTemplate?.intuitiveMetaphors) {
      const metaphor = this.selectMetaphor(topicTemplate.intuitiveMetaphors);
      return VISUAL_FORMS[metaphor.actor] || VISUAL_FORMS.PERSON_WALKING;
    }
    
    // From template
    if (topicTemplate?.actors?.[0]?.forms) {
      const forms = topicTemplate.actors[0].forms;
      const formKey = forms[0];
      return VISUAL_FORMS[formKey] || VISUAL_FORMS.SLIDING_BLOCK;
    }
    
    // Default based on variant
    const variant = entity.properties?.variant;
    if (variant === 'ball') return VISUAL_FORMS.ROLLING_BALL;
    if (variant === 'car') return VISUAL_FORMS.CAR_MOVING;
    if (variant === 'person') return VISUAL_FORMS.PERSON_WALKING;
    
    return VISUAL_FORMS.SLIDING_BLOCK;
  }
  
  /**
   * Select appropriate force form
   */
  selectForceForm(entity) {
    const variant = entity.properties?.variant;
    
    switch (variant) {
      case 'gravitational':
        return VISUAL_FORMS.GRAVITATIONAL_PULL;
      case 'friction':
        return VISUAL_FORMS.FRICTION_RESISTANCE;
      case 'spring':
        return VISUAL_FORMS.SPRING_FORCE;
      case 'tension':
        return VISUAL_FORMS.TENSION_LINE;
      default:
        return VISUAL_FORMS.FORCE_ARROW;
    }
  }
  
  /**
   * Select structure form based on domain
   */
  selectStructureForm(entity, domain) {
    const hint = entity.properties?.visualHint;
    
    if (domain === 'biology') {
      if (hint === 'leaf') return VISUAL_FORMS.LEAF_CROSS_SECTION;
      if (hint === 'chloroplast') return VISUAL_FORMS.CHLOROPLAST;
      return VISUAL_FORMS.CELL_MEMBRANE;
    }
    
    if (domain === 'chemistry') {
      return VISUAL_FORMS.BEAKER_CONTAINER;
    }
    
    return VISUAL_FORMS.SLIDING_BLOCK;
  }
  
  /**
   * Select metaphor for intuitive intent
   */
  selectMetaphor(metaphors) {
    const keys = Object.keys(metaphors);
    
    // Prefer Indian context metaphors
    if (this.options.indianContext) {
      // carpet_walk is common in Indian homes
      if (metaphors.carpet_walk) return metaphors.carpet_walk;
    }
    
    // Random selection for variety
    const randomKey = keys[Math.floor(Math.random() * keys.length)];
    return metaphors[randomKey];
  }
  
  /**
   * Create force objects from concept graph
   */
  createForces(conceptGraph, strategy, topicTemplate) {
    const forces = [];
    
    // Get force entities
    const forceEntities = Array.from(conceptGraph.entities.values())
      .filter(e => e.type === ENTITY_TYPES.FORCE);
    
    for (const entity of forceEntities) {
      const force = new SceneObject(
        entity.id || `force_${forces.length}`,
        OBJECT_TYPES.FORCE,
        this.selectForceForm(entity),
        {
          label: entity.label,
          properties: entity.properties,
          spatialRules: [
            { rule: SPATIAL_RULES.ORIGINATES_FROM, relatedTo: entity.properties?.actingOn }
          ],
          renderHints: {
            color: this.getForceColor(entity.properties?.variant),
            emphasis: entity.properties?.importance === 'high' ? 'high' : 'normal',
          },
        }
      );
      forces.push(force);
    }
    
    return forces;
  }
  
  /**
   * Get color for force type
   */
  getForceColor(variant) {
    const colors = {
      gravitational: '#2C3E50',
      normal: '#3498DB',
      friction: '#E67E22',
      tension: '#9B59B6',
      applied: '#E74C3C',
      spring: '#27AE60',
    };
    return colors[variant] || '#E74C3C';
  }
  
  /**
   * Create effect objects based on intent
   */
  createEffects(strategy, topicTemplate, intent) {
    const effects = [];
    
    // Counterfactual shows chaos in alternate world
    if (intent === INTENT_TYPES.COUNTERFACTUAL && topicTemplate?.counterfactual?.withoutFriction?.effect) {
      effects.push(new SceneObject(
        'effect_chaos',
        OBJECT_TYPES.EFFECT,
        VISUAL_FORMS.CHAOS_SCATTER,
        {
          spatialRules: [{ rule: SPATIAL_RULES.RIGHT_OF }],
          renderHints: { animated: true },
        }
      ));
    }
    
    // Causal inquiry may show heat/energy effects
    if (intent === INTENT_TYPES.CAUSAL_INQUIRY && topicTemplate?.effects) {
      for (const effect of topicTemplate.effects) {
        effects.push(new SceneObject(
          `effect_${effect}`,
          OBJECT_TYPES.EFFECT,
          VISUAL_FORMS[effect.toUpperCase()] || VISUAL_FORMS.HEAT_GLOW,
          {
            renderHints: { animated: true, opacity: 0.6 },
          }
        ));
      }
    }
    
    return effects;
  }
  
  /**
   * Add objects for comparison forms
   */
  addComparisonObjects(sceneObjects, conceptGraph, strategy, topicTemplate) {
    // Add VS divider for comparisons
    sceneObjects.push(new SceneObject(
      'divider_vs',
      OBJECT_TYPES.INDICATOR,
      'VS_DIVIDER',
      {
        spatialRules: [{ rule: SPATIAL_RULES.CENTERED }],
        renderHints: { emphasis: 'high' },
      }
    ));
  }
  
  /**
   * Compute animation delays for scene objects
   */
  computeAnimationDelays(sceneObjects) {
    // Sort by draw order
    sceneObjects.sort((a, b) => a.drawOrder - b.drawOrder);
    
    // Assign staggered delays
    sceneObjects.forEach((obj, index) => {
      obj.animationDelay = index * 0.15;  // 150ms between elements
    });
  }
}

// ============================================
// EXPORTS
// ============================================

export function createSceneObjectResolver(options) {
  return new SceneObjectResolver(options);
}

export default SceneObjectResolver;
