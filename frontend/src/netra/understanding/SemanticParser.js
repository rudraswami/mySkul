/**
 * 🧠 SEMANTIC PARSER
 * ==================
 * 
 * The brain that understands educational questions and builds
 * rich ConceptGraphs for visual reasoning.
 * 
 * This is NOT keyword matching. It's semantic understanding:
 * - Identifies entities and their types
 * - Extracts relationships between entities
 * - Infers physical/logical constraints
 * - Detects processes and sequences
 * - Recognizes visual requirements
 * 
 * Uses LLM (GPT-4) for deep understanding with intelligent fallbacks.
 */

import { 
  ConceptGraph, 
  ENTITY_TYPES, 
  RELATIONSHIP_TYPES, 
  CONSTRAINT_TYPES 
} from '../core/ConceptGraph';

// ============================================
// DOMAIN PATTERNS
// ============================================

const DOMAIN_INDICATORS = {
  physics: {
    keywords: [
      'force', 'velocity', 'acceleration', 'momentum', 'energy', 'work', 'power',
      'gravity', 'friction', 'tension', 'normal', 'weight', 'mass', 'speed',
      'projectile', 'motion', 'newton', 'wave', 'light', 'optics', 'reflection',
      'refraction', 'electric', 'magnetic', 'current', 'voltage', 'resistance',
      'circuit', 'pendulum', 'oscillation', 'spring', 'pulley', 'incline',
      'collision', 'elastic', 'inelastic', 'kinetic', 'potential', 'thermal',
      'pressure', 'density', 'buoyancy', 'archimedes', 'fluid',
    ],
    weight: 1.5,
  },
  chemistry: {
    keywords: [
      'atom', 'molecule', 'bond', 'electron', 'proton', 'neutron', 'ion',
      'covalent', 'ionic', 'metallic', 'reaction', 'equation', 'balance',
      'acid', 'base', 'pH', 'salt', 'solution', 'concentration', 'molar',
      'oxidation', 'reduction', 'redox', 'catalyst', 'enzyme', 'organic',
      'carbon', 'hydrogen', 'oxygen', 'nitrogen', 'periodic', 'element',
      'compound', 'mixture', 'solute', 'solvent', 'precipitate', 'gas',
      'valence', 'orbital', 'shell', 'electronegativity',
    ],
    weight: 1.5,
  },
  biology: {
    keywords: [
      'cell', 'nucleus', 'membrane', 'mitochondria', 'chloroplast', 'ribosome',
      'DNA', 'RNA', 'gene', 'chromosome', 'protein', 'amino acid', 'enzyme',
      'photosynthesis', 'respiration', 'metabolism', 'ATP', 'glucose',
      'heart', 'lung', 'blood', 'artery', 'vein', 'capillary', 'organ',
      'tissue', 'neuron', 'synapse', 'brain', 'nerve', 'muscle', 'bone',
      'digestion', 'absorption', 'excretion', 'hormone', 'gland',
      'mitosis', 'meiosis', 'reproduction', 'evolution', 'species',
      'ecosystem', 'food chain', 'photosynthesis', 'krebs', 'calvin',
    ],
    weight: 1.5,
  },
  math: {
    keywords: [
      'function', 'graph', 'equation', 'formula', 'variable', 'constant',
      'linear', 'quadratic', 'polynomial', 'exponential', 'logarithm',
      'derivative', 'integral', 'calculus', 'limit', 'slope', 'tangent',
      'triangle', 'circle', 'square', 'rectangle', 'polygon', 'angle',
      'area', 'perimeter', 'volume', 'surface', 'geometry', 'algebra',
      'trigonometry', 'sine', 'cosine', 'tangent', 'vector', 'matrix',
      'probability', 'statistics', 'mean', 'median', 'mode', 'variance',
      'set', 'union', 'intersection', 'subset', 'venn', 'fraction',
      'decimal', 'percentage', 'ratio', 'proportion', 'inequality',
    ],
    weight: 1.5,
  },
};

// ============================================
// ENTITY EXTRACTION PATTERNS
// ============================================

const ENTITY_PATTERNS = {
  physics: {
    // Objects
    bodies: [
      { pattern: /\b(ball|sphere|object|body|block|box|car|truck|rocket|projectile)\b/gi, type: ENTITY_TYPES.BODY },
      { pattern: /\b(person|man|woman|boy|girl|student)\b/gi, type: ENTITY_TYPES.PERSON },
      { pattern: /\b(planet|earth|moon|sun|star)\b/gi, type: ENTITY_TYPES.BODY, variant: 'celestial' },
    ],
    // Forces
    forces: [
      { pattern: /\b(force|thrust|push|pull)\b/gi, type: ENTITY_TYPES.FORCE },
      { pattern: /\b(gravity|gravitational force|weight)\b/gi, type: ENTITY_TYPES.FORCE, variant: 'gravitational' },
      { pattern: /\b(friction|frictional force)\b/gi, type: ENTITY_TYPES.FORCE, variant: 'friction' },
      { pattern: /\b(normal force)\b/gi, type: ENTITY_TYPES.FORCE, variant: 'normal' },
      { pattern: /\b(tension)\b/gi, type: ENTITY_TYPES.FORCE, variant: 'tension' },
      { pattern: /\b(spring force)\b/gi, type: ENTITY_TYPES.FORCE, variant: 'spring' },
    ],
    // Motion
    motion: [
      { pattern: /\b(velocity|speed)\b/gi, type: ENTITY_TYPES.VECTOR, variant: 'velocity' },
      { pattern: /\b(acceleration)\b/gi, type: ENTITY_TYPES.VECTOR, variant: 'acceleration' },
      { pattern: /\b(momentum)\b/gi, type: ENTITY_TYPES.VECTOR, variant: 'momentum' },
      { pattern: /\b(displacement|distance)\b/gi, type: ENTITY_TYPES.SCALAR },
    ],
    // Structures
    structures: [
      { pattern: /\b(incline|ramp|slope)\b/gi, type: ENTITY_TYPES.STRUCTURE, variant: 'incline' },
      { pattern: /\b(pulley)\b/gi, type: ENTITY_TYPES.STRUCTURE, variant: 'pulley' },
      { pattern: /\b(spring)\b/gi, type: ENTITY_TYPES.STRUCTURE, variant: 'spring' },
      { pattern: /\b(pendulum)\b/gi, type: ENTITY_TYPES.STRUCTURE, variant: 'pendulum' },
      { pattern: /\b(circuit)\b/gi, type: ENTITY_TYPES.STRUCTURE, variant: 'circuit' },
    ],
    // Waves and fields
    phenomena: [
      { pattern: /\b(wave|light|ray)\b/gi, type: ENTITY_TYPES.WAVE },
      { pattern: /\b(electric field|magnetic field)\b/gi, type: ENTITY_TYPES.FIELD },
    ],
  },

  chemistry: {
    particles: [
      { pattern: /\b(atom|electron|proton|neutron|ion)\b/gi, type: ENTITY_TYPES.ATOM },
      { pattern: /\b(molecule|compound)\b/gi, type: ENTITY_TYPES.MOLECULE },
    ],
    reactions: [
      { pattern: /\b(reaction|process)\b/gi, type: ENTITY_TYPES.REACTION },
    ],
    elements: [
      { pattern: /\b(hydrogen|oxygen|carbon|nitrogen|sodium|chlorine|iron|copper|gold|silver)\b/gi, type: ENTITY_TYPES.ATOM, isElement: true },
    ],
  },

  biology: {
    cells: [
      { pattern: /\b(cell|cells)\b/gi, type: ENTITY_TYPES.CELL },
      { pattern: /\b(nucleus|mitochondria|chloroplast|ribosome|membrane)\b/gi, type: ENTITY_TYPES.STRUCTURE, variant: 'organelle' },
    ],
    organisms: [
      { pattern: /\b(plant|animal|bacteria|virus|organism)\b/gi, type: ENTITY_TYPES.ORGANISM },
    ],
    organs: [
      { pattern: /\b(heart|lung|kidney|liver|brain|stomach|intestine)\b/gi, type: ENTITY_TYPES.ORGAN },
    ],
    molecules: [
      { pattern: /\b(DNA|RNA|protein|enzyme|ATP|glucose)\b/gi, type: ENTITY_TYPES.MOLECULE },
    ],
    processes: [
      { pattern: /\b(photosynthesis|respiration|digestion|mitosis|meiosis)\b/gi, type: ENTITY_TYPES.PROCESS },
    ],
  },

  math: {
    functions: [
      { pattern: /\b(function|f\(x\)|y\s*=)\b/gi, type: ENTITY_TYPES.FUNCTION },
    ],
    shapes: [
      { pattern: /\b(triangle|circle|square|rectangle|polygon|line|point)\b/gi, type: ENTITY_TYPES.SHAPE },
    ],
    equations: [
      { pattern: /\b(equation|formula|expression)\b/gi, type: ENTITY_TYPES.EQUATION },
    ],
    sets: [
      { pattern: /\b(set|group|collection)\b/gi, type: ENTITY_TYPES.SET },
    ],
  },
};

// ============================================
// RELATIONSHIP EXTRACTION PATTERNS
// ============================================

const RELATIONSHIP_PATTERNS = [
  // Causal
  { pattern: /(\w+)\s+(causes?|leads?\s+to|results?\s+in|produces?)\s+(\w+)/gi, type: RELATIONSHIP_TYPES.CAUSES },
  { pattern: /(\w+)\s+(enables?|allows?)\s+(\w+)/gi, type: RELATIONSHIP_TYPES.ENABLES },
  { pattern: /(\w+)\s+(prevents?|stops?|blocks?)\s+(\w+)/gi, type: RELATIONSHIP_TYPES.PREVENTS },

  // Spatial
  { pattern: /(\w+)\s+(contains?|includes?|has)\s+(\w+)/gi, type: RELATIONSHIP_TYPES.CONTAINS },
  { pattern: /(\w+)\s+(is\s+inside|within)\s+(\w+)/gi, type: RELATIONSHIP_TYPES.INSIDE },
  { pattern: /(\w+)\s+(is\s+above|over)\s+(\w+)/gi, type: RELATIONSHIP_TYPES.ABOVE },
  { pattern: /(\w+)\s+(is\s+below|under|beneath)\s+(\w+)/gi, type: RELATIONSHIP_TYPES.BELOW },
  { pattern: /(\w+)\s+(connects?\s+to|attached\s+to)\s+(\w+)/gi, type: RELATIONSHIP_TYPES.ATTACHED_TO },

  // Comparative
  { pattern: /(\w+)\s+(is\s+greater\s+than|exceeds?|>)\s+(\w+)/gi, type: RELATIONSHIP_TYPES.GREATER_THAN },
  { pattern: /(\w+)\s+(is\s+less\s+than|<)\s+(\w+)/gi, type: RELATIONSHIP_TYPES.LESS_THAN },
  { pattern: /(\w+)\s+(equals?|is\s+equal\s+to|=)\s+(\w+)/gi, type: RELATIONSHIP_TYPES.EQUAL_TO },
  { pattern: /(\w+)\s+(is\s+opposite\s+to|opposes?)\s+(\w+)/gi, type: RELATIONSHIP_TYPES.OPPOSITE_TO },

  // Transformational
  { pattern: /(\w+)\s+(becomes?|turns?\s+into|transforms?\s+into)\s+(\w+)/gi, type: RELATIONSHIP_TYPES.BECOMES },

  // Force/Interaction
  { pattern: /(\w+)\s+(acts?\s+on|exerts?\s+on|applies?\s+to)\s+(\w+)/gi, type: RELATIONSHIP_TYPES.ACTS_ON },
  { pattern: /(\w+)\s+(reacts?\s+to|responds?\s+to)\s+(\w+)/gi, type: RELATIONSHIP_TYPES.REACTS_TO },
  { pattern: /(\w+)\s+(attracts?)\s+(\w+)/gi, type: RELATIONSHIP_TYPES.ATTRACTS },
  { pattern: /(\w+)\s+(repels?)\s+(\w+)/gi, type: RELATIONSHIP_TYPES.REPELS },
];

// ============================================
// SEMANTIC PARSER CLASS
// ============================================

export class SemanticParser {
  constructor(options = {}) {
    this.options = {
      useLLM: true,                    // Use LLM for deep understanding
      fallbackToRules: true,           // Fall back to rule-based parsing
      enrichWithContext: true,         // Add domain context
      ...options,
    };
    
    this.apiClient = options.apiClient || null;
  }

  /**
   * Parse a question into a ConceptGraph
   * @param {string} question - Natural language question
   * @param {Object} context - Additional context (subject, level, etc.)
   * @returns {Promise<ConceptGraph>} Parsed concept graph
   */
  async parse(question, context = {}) {
    console.log('═══════════════════════════════════════════════════');
    console.log('🧠 [SemanticParser] PARSE CALLED');
    console.log('🧠 [SemanticParser] Question:', JSON.stringify(question));
    console.log('🧠 [SemanticParser] Question type:', typeof question);
    console.log('🧠 [SemanticParser] Context:', JSON.stringify(context));
    console.log('═══════════════════════════════════════════════════');
    
    // CRITICAL: Validate question
    if (!question || typeof question !== 'string' || question.trim() === '') {
      console.error('❌ [SemanticParser] INVALID QUESTION - returning fallback graph');
      console.error('❌ [SemanticParser] Received:', question, 'Type:', typeof question);
      
      // Create a fallback graph with generic content
      const fallbackGraph = new ConceptGraph();
      fallbackGraph.setMetadata('domain', context.subject || 'physics');
      fallbackGraph.setMetadata('topic', 'Concept');
      fallbackGraph.setMetadata('error', 'No valid question provided');
      
      // Add a single placeholder entity
      fallbackGraph.addEntity('placeholder', ENTITY_TYPES.OBJECT, {
        label: 'Ask a question to see visual',
        visualHint: 'generic',
        importance: 'normal',
      });
      
      return fallbackGraph;
    }
    
    // STEP 1: Try LLM parsing first (intelligent path)
    // This is the preferred path - uses GPT-4 for deep understanding
    if (this.options.useLLM) {
      try {
        console.log('🧠 [SemanticParser] Trying LLM-based parsing...');
        const llmGraph = await this.parseWithLLM(question, context);
        if (llmGraph && llmGraph.entities.size > 0) {
          console.log('✅ [SemanticParser] LLM parsing successful!', llmGraph.getSummary());
          return llmGraph;
        }
        console.log('⚠️ [SemanticParser] LLM returned empty graph, falling back to rules');
      } catch (error) {
        console.warn('⚠️ [SemanticParser] LLM parsing failed, falling back to rules:', error.message);
      }
    }
    
    // STEP 2: Fall back to rule-based parsing
    console.log('🧠 [SemanticParser] Using rule-based parsing...');
    const graph = new ConceptGraph();

    // Detect domain
    const domain = context.subject || this.detectDomain(question);
    graph.setMetadata('domain', domain);

    // Extract topic
    const topic = this.extractTopic(question);
    graph.setMetadata('topic', topic);

    // Rule-based parsing
    if (this.options.fallbackToRules) {
      this.extractEntitiesWithRules(question, domain, graph);
      this.extractRelationshipsWithRules(question, graph);
      this.inferConstraints(domain, graph);
      this.detectProcesses(question, graph);
    }

    // Enrich with domain context (concept templates)
    if (this.options.enrichWithContext) {
      this.enrichWithDomainContext(domain, graph);
    }

    // Infer visual type
    graph.setMetadata('visualType', graph.inferVisualType());
    
    console.log('🧠 [SemanticParser] Rule-based parsing complete:', graph.getSummary());

    return graph;
  }

  /**
   * Detect domain from question keywords
   */
  detectDomain(question) {
    const questionLower = question.toLowerCase();
    const scores = {};

    for (const [domain, config] of Object.entries(DOMAIN_INDICATORS)) {
      scores[domain] = 0;
      for (const keyword of config.keywords) {
        if (questionLower.includes(keyword.toLowerCase())) {
          scores[domain] += config.weight;
        }
      }
    }

    // Find highest score
    let maxScore = 0;
    let detectedDomain = 'physics'; // Default

    for (const [domain, score] of Object.entries(scores)) {
      if (score > maxScore) {
        maxScore = score;
        detectedDomain = domain;
      }
    }

    return detectedDomain;
  }

  /**
   * Extract topic from question
   */
  extractTopic(question) {
    // NULL CHECK - Critical fix!
    if (!question || typeof question !== 'string' || question.trim() === '') {
      console.error('❌ [SemanticParser] extractTopic received empty/null question:', question);
      return 'Concept'; // Fallback
    }
    
    // Remove common question starters
    const starters = [
      'explain', 'what is', 'how does', 'why does', 'describe',
      'show me', 'illustrate', 'demonstrate', 'what happens when',
    ];

    let topic = question.toLowerCase().trim();
    for (const starter of starters) {
      if (topic.startsWith(starter)) {
        topic = topic.substring(starter.length).trim();
        break;
      }
    }

    // Remove trailing punctuation
    topic = topic.replace(/[?.!]+$/, '').trim();
    
    // If topic is empty after processing, use original question
    if (!topic) {
      topic = question.trim();
    }

    // Capitalize first letter
    const result = topic.charAt(0).toUpperCase() + topic.slice(1);
    console.log(`🧠 [SemanticParser] extractTopic: "${question}" → "${result}"`);
    return result;
  }

  /**
   * Extract entities using rule-based patterns
   */
  extractEntitiesWithRules(question, domain, graph) {
    const patterns = ENTITY_PATTERNS[domain];
    if (!patterns) return;

    const questionLower = question.toLowerCase();
    let entityCounter = 0;

    const extractFromCategory = (category) => {
      for (const item of category) {
        const matches = question.match(item.pattern);
        if (matches) {
          for (const match of [...new Set(matches)]) { // Deduplicate
            const entityId = `${item.type}_${entityCounter++}`;
            graph.addEntity(entityId, item.type, {
              label: match.trim(),
              variant: item.variant || null,
              visualHint: this.inferVisualHint(item.type, item.variant),
              importance: this.inferImportance(match, question),
            });
          }
        }
      }
    };

    // Extract from all categories in domain
    for (const category of Object.values(patterns)) {
      if (Array.isArray(category)) {
        extractFromCategory(category);
      }
    }

    // If no entities found, create placeholder
    if (graph.entities.size === 0) {
      graph.addEntity('main_concept', ENTITY_TYPES.OBJECT, {
        label: this.extractTopic(question),
        visualHint: 'central_concept',
        importance: 'high',
      });
    }
  }

  /**
   * Extract relationships using patterns
   */
  extractRelationshipsWithRules(question, graph) {
    const entities = Array.from(graph.entities.values());
    if (entities.length < 2) return;

    // Apply relationship patterns
    for (const pattern of RELATIONSHIP_PATTERNS) {
      const regex = new RegExp(pattern.pattern);
      const match = regex.exec(question);
      if (match) {
        // Try to match to existing entities
        const fromEntity = this.findMatchingEntity(match[1], entities);
        const toEntity = this.findMatchingEntity(match[3], entities);

        if (fromEntity && toEntity && fromEntity.id !== toEntity.id) {
          graph.addRelationship(fromEntity.id, toEntity.id, pattern.type);
        }
      }
    }

    // Infer physics-specific relationships
    this.inferPhysicsRelationships(question, graph);
  }

  /**
   * Find entity that matches a word
   */
  findMatchingEntity(word, entities) {
    const wordLower = word.toLowerCase();
    return entities.find(e => 
      e.label.toLowerCase().includes(wordLower) ||
      wordLower.includes(e.label.toLowerCase())
    );
  }

  /**
   * Infer physics-specific relationships
   */
  inferPhysicsRelationships(question, graph) {
    const questionLower = question.toLowerCase();
    const forces = graph.getEntitiesByType(ENTITY_TYPES.FORCE);
    const bodies = graph.getEntitiesByType(ENTITY_TYPES.BODY);

    // Newton's Third Law
    if (questionLower.includes('action') && questionLower.includes('reaction')) {
      graph.addConstraint(CONSTRAINT_TYPES.NEWTON_THIRD_LAW, [], {
        description: 'Every action has equal and opposite reaction',
      });

      // If we have forces, mark them as paired
      if (forces.length >= 2) {
        graph.addRelationship(forces[0].id, forces[1].id, RELATIONSHIP_TYPES.OPPOSITE_TO, {
          label: 'equal & opposite',
        });
      }
    }

    // Force acting on body
    for (const force of forces) {
      for (const body of bodies) {
        graph.addRelationship(force.id, body.id, RELATIONSHIP_TYPES.ACTS_ON);
      }
    }

    // Projectile motion
    if (questionLower.includes('projectile') || questionLower.includes('trajectory')) {
      const projectile = bodies[0] || graph.addEntity('projectile', ENTITY_TYPES.BODY, {
        label: 'Projectile',
        visualHint: 'ball',
      });

      graph.addEntity('gravity_force', ENTITY_TYPES.FORCE, {
        label: 'Weight (mg)',
        variant: 'gravitational',
        visualHint: 'force_vector',
        direction: 'down',
      });
    }
  }

  /**
   * Infer constraints from domain
   */
  inferConstraints(domain, graph) {
    if (domain === 'physics') {
      // Energy conservation for motion problems
      const hasMotion = graph.getEntitiesByType(ENTITY_TYPES.VECTOR).length > 0;
      if (hasMotion) {
        graph.addConstraint(CONSTRAINT_TYPES.CONSERVATION_ENERGY);
        graph.addConstraint(CONSTRAINT_TYPES.CONSERVATION_MOMENTUM);
      }
    }

    if (domain === 'chemistry') {
      // Charge balance for reactions
      const hasReaction = graph.getEntitiesByType(ENTITY_TYPES.REACTION).length > 0;
      if (hasReaction) {
        graph.addConstraint(CONSTRAINT_TYPES.CHARGE_BALANCE);
        graph.addConstraint(CONSTRAINT_TYPES.CONSERVATION_MASS);
      }
    }
  }

  /**
   * Detect processes (step sequences)
   */
  detectProcesses(question, graph) {
    const questionLower = question.toLowerCase();

    // Detect step indicators
    const stepIndicators = ['first', 'then', 'next', 'finally', 'step'];
    const hasSteps = stepIndicators.some(s => questionLower.includes(s));

    // Detect cycle indicators
    const cycleIndicators = ['cycle', 'loop', 'repeats', 'continuous'];
    const isCycle = cycleIndicators.some(c => questionLower.includes(c));

    if (hasSteps || isCycle) {
      graph.addProcess('main_process', [], {
        cyclic: isCycle,
      });
    }
  }

  /**
   * Enrich with domain-specific context
   */
  enrichWithDomainContext(domain, graph) {
    const topic = graph.metadata.topic?.toLowerCase() || '';
    
    // CONCEPT-SPECIFIC ENRICHMENT
    // When a user asks "explain X", we add the canonical diagram entities for X
    this.addConceptSpecificEntities(topic, domain, graph);
    
    // Add ground/reference for physics if we have bodies
    if (domain === 'physics') {
      const bodies = graph.getEntitiesByType(ENTITY_TYPES.BODY);
      if (bodies.length > 0 && !graph.entities.has('ground')) {
        graph.addEntity('ground', ENTITY_TYPES.STRUCTURE, {
          label: 'Surface',
          visualHint: 'ground_plane',
          importance: 'low',
        });
      }
    }
  }
  
  /**
   * Add concept-specific entities for well-known topics
   * This is the "intelligent" part - knowing what to show for each concept
   */
  addConceptSpecificEntities(topic, domain, graph) {
    // PHYSICS CONCEPTS
    const physicsConceptTemplates = {
      // FRICTION
      friction: () => {
        graph.addEntity('block', ENTITY_TYPES.BODY, {
          label: 'Block',
          variant: 'box',
          visualHint: 'rigid_body',
          importance: 'high',
          mass: 'm',
        });
        graph.addEntity('surface', ENTITY_TYPES.STRUCTURE, {
          label: 'Rough Surface',
          visualHint: 'ground_plane',
          importance: 'normal',
        });
        graph.addEntity('weight', ENTITY_TYPES.FORCE, {
          label: 'Weight (W = mg)',
          variant: 'gravitational',
          visualHint: 'force_vector',
          direction: 'down',
          importance: 'normal',
        });
        graph.addEntity('normal', ENTITY_TYPES.FORCE, {
          label: 'Normal (N)',
          variant: 'normal',
          visualHint: 'force_vector',
          direction: 'up',
          importance: 'normal',
        });
        graph.addEntity('friction_force', ENTITY_TYPES.FORCE, {
          label: 'Friction (f = μN)',
          variant: 'friction',
          visualHint: 'force_vector',
          direction: 'left',
          importance: 'high',
          color: '#E67E22',
        });
        graph.addEntity('applied_force', ENTITY_TYPES.FORCE, {
          label: 'Applied Force (F)',
          variant: 'applied',
          visualHint: 'force_vector',
          direction: 'right',
          importance: 'normal',
        });
        // Add relationships
        graph.addRelationship('weight', 'block', RELATIONSHIP_TYPES.ACTS_ON);
        graph.addRelationship('normal', 'block', RELATIONSHIP_TYPES.ACTS_ON);
        graph.addRelationship('friction_force', 'block', RELATIONSHIP_TYPES.ACTS_ON);
        graph.addRelationship('applied_force', 'block', RELATIONSHIP_TYPES.ACTS_ON);
        graph.addRelationship('friction_force', 'applied_force', RELATIONSHIP_TYPES.OPPOSITE_TO);
        graph.addRelationship('normal', 'weight', RELATIONSHIP_TYPES.OPPOSITE_TO);
      },
      
      // NEWTON'S LAWS
      'newton': () => {
        graph.addEntity('object', ENTITY_TYPES.BODY, {
          label: 'Object',
          variant: 'box',
          visualHint: 'rigid_body',
          importance: 'high',
        });
        graph.addEntity('force_a', ENTITY_TYPES.FORCE, {
          label: 'Action Force',
          variant: 'applied',
          visualHint: 'force_vector',
          direction: 'right',
          importance: 'high',
          color: '#E74C3C',
        });
        graph.addEntity('force_b', ENTITY_TYPES.FORCE, {
          label: 'Reaction Force',
          variant: 'applied',
          visualHint: 'force_vector',
          direction: 'left',
          importance: 'high',
          color: '#3498DB',
        });
        graph.addRelationship('force_a', 'force_b', RELATIONSHIP_TYPES.OPPOSITE_TO, {
          label: 'Equal & Opposite',
        });
      },
      
      // PROJECTILE MOTION
      'projectile': () => {
        graph.addEntity('ball', ENTITY_TYPES.BODY, {
          label: 'Projectile',
          variant: 'ball',
          visualHint: 'rigid_body',
          importance: 'high',
        });
        graph.addEntity('trajectory', ENTITY_TYPES.PATH, {
          label: 'Trajectory',
          visualHint: 'parabola',
          importance: 'high',
        });
        graph.addEntity('gravity', ENTITY_TYPES.FORCE, {
          label: 'Gravity (g)',
          variant: 'gravitational',
          visualHint: 'force_vector',
          direction: 'down',
          importance: 'normal',
        });
        graph.addEntity('velocity', ENTITY_TYPES.VECTOR, {
          label: 'Velocity (v)',
          variant: 'velocity',
          visualHint: 'velocity_arrow',
          importance: 'normal',
        });
      },
      
      // FREE BODY DIAGRAM
      'free body': () => {
        graph.addEntity('body', ENTITY_TYPES.BODY, {
          label: 'Body',
          variant: 'box',
          visualHint: 'rigid_body',
          importance: 'high',
        });
        graph.addEntity('weight', ENTITY_TYPES.FORCE, {
          label: 'Weight (W)',
          variant: 'gravitational',
          direction: 'down',
        });
        graph.addEntity('normal', ENTITY_TYPES.FORCE, {
          label: 'Normal (N)',
          variant: 'normal',
          direction: 'up',
        });
      },
      
      // GRAVITY
      'gravity': () => {
        graph.addEntity('earth', ENTITY_TYPES.BODY, {
          label: 'Earth',
          variant: 'sphere',
          visualHint: 'planet',
          importance: 'normal',
        });
        graph.addEntity('object', ENTITY_TYPES.BODY, {
          label: 'Object',
          variant: 'ball',
          visualHint: 'rigid_body',
          importance: 'high',
        });
        graph.addEntity('gravity_force', ENTITY_TYPES.FORCE, {
          label: 'Gravitational Force (F = GMm/r²)',
          variant: 'gravitational',
          direction: 'down',
          importance: 'high',
        });
        graph.addRelationship('gravity_force', 'object', RELATIONSHIP_TYPES.ACTS_ON);
      },
    };
    
    // Check if topic matches any template (with fuzzy matching for typos)
    console.log(`🧠 [SemanticParser] Checking concept templates for topic: "${topic}"`);
    
    for (const [conceptKey, generateEntities] of Object.entries(physicsConceptTemplates)) {
      // Fuzzy match: check if topic contains concept OR concept is similar (handles typos)
      const topicLower = topic.toLowerCase();
      const keyLower = conceptKey.toLowerCase();
      
      // Check exact match first
      if (topicLower.includes(keyLower)) {
        this.applyConceptTemplate(graph, conceptKey, generateEntities);
        return;
      }
      
      // Check fuzzy match for common typos (e.g., "fritction" vs "friction")
      if (this.isSimilar(topicLower, keyLower, 0.7)) {
        console.log(`🧠 [SemanticParser] Fuzzy matched "${topicLower}" → "${keyLower}"`);
        this.applyConceptTemplate(graph, conceptKey, generateEntities);
        return;
      }
    }
    
    // If no template matched, create a generic concept visualization
    console.log(`🧠 [SemanticParser] No concept template matched for topic: "${topic}"`);
    console.log(`🧠 [SemanticParser] Creating generic concept visualization...`);
    
    // Create a default concept map for unknown topics
    // This ensures SOMETHING is always rendered
    if (graph.entities.size === 0) {
      // Add a central concept node
      graph.addEntity('central_concept', ENTITY_TYPES.OBJECT, {
        label: topic || 'Concept',
        visualHint: 'concept',
        importance: 'high',
        variant: 'circle',
      });
      
      // If we have any words in the topic, add them as related concepts
      const words = topic.split(/\s+/).filter(w => w.length > 3);
      if (words.length > 1) {
        words.slice(0, 4).forEach((word, i) => {
          const id = `related_${i}`;
          graph.addEntity(id, ENTITY_TYPES.OBJECT, {
            label: word.charAt(0).toUpperCase() + word.slice(1),
            visualHint: 'concept',
            importance: 'normal',
            variant: 'rounded',
          });
          graph.addRelationship('central_concept', id, RELATIONSHIP_TYPES.RELATED_TO);
        });
      }
      
      console.log(`🧠 [SemanticParser] Created generic concept map with ${graph.entities.size} entities`);
    }
  }
  
  /**
   * Apply a concept template to the graph
   */
  applyConceptTemplate(graph, conceptKey, generateEntities) {
    // Remove placeholder entity if it exists
    if (graph.entities.has('main_concept')) {
      graph.entities.delete('main_concept');
    }
    generateEntities();
    console.log(`🧠 [SemanticParser] Added concept-specific entities for: ${conceptKey}`);
    console.log(`🧠 [SemanticParser] Entities created:`, Array.from(graph.entities.keys()));
    console.log(`🧠 [SemanticParser] Relationships created:`, graph.relationships.length);
  }
  
  /**
   * Simple similarity check for typo tolerance
   * Uses character overlap ratio
   */
  isSimilar(str1, str2, threshold = 0.7) {
    // Remove spaces and normalize
    const s1 = str1.replace(/\s+/g, '');
    const s2 = str2.replace(/\s+/g, '');
    
    if (s1.length < 3 || s2.length < 3) return false;
    
    // Check if one contains the other (partial match)
    if (s1.includes(s2) || s2.includes(s1)) return true;
    
    // Calculate character overlap
    const chars1 = new Set(s1.split(''));
    const chars2 = new Set(s2.split(''));
    const intersection = new Set([...chars1].filter(c => chars2.has(c)));
    const union = new Set([...chars1, ...chars2]);
    
    const similarity = intersection.size / union.size;
    
    // Also check if starting characters match
    const startMatch = s1.substring(0, 3) === s2.substring(0, 3);
    
    return similarity >= threshold || (similarity >= 0.5 && startMatch);
  }

  /**
   * Infer visual hint for entity
   */
  inferVisualHint(type, variant) {
    const hints = {
      [ENTITY_TYPES.FORCE]: 'force_vector',
      [ENTITY_TYPES.BODY]: variant || 'body',
      [ENTITY_TYPES.VECTOR]: variant === 'velocity' ? 'velocity_arrow' : 'vector',
      [ENTITY_TYPES.CELL]: 'cell_diagram',
      [ENTITY_TYPES.ATOM]: 'atom_orbital',
      [ENTITY_TYPES.MOLECULE]: 'molecule_structure',
      [ENTITY_TYPES.FUNCTION]: 'function_curve',
      [ENTITY_TYPES.SHAPE]: variant || 'geometric_shape',
    };

    return hints[type] || 'generic';
  }

  /**
   * Infer importance based on position in question
   */
  inferImportance(word, question) {
    const position = question.toLowerCase().indexOf(word.toLowerCase());
    const normalizedPosition = position / question.length;

    if (normalizedPosition < 0.3) return 'high';
    if (normalizedPosition < 0.6) return 'normal';
    return 'low';
  }

  /**
   * Parse with LLM (API call to NETRA backend)
   * This is the intelligent path - uses GPT-4 to understand the concept
   */
  async parseWithLLM(question, context) {
    console.log('═══════════════════════════════════════════════════');
    console.log('🧠 [SemanticParser] CALLING LLM BACKEND');
    console.log('🧠 [SemanticParser] Question:', question);
    console.log('🧠 [SemanticParser] Context:', context);
    console.log('═══════════════════════════════════════════════════');
    
    try {
      const requestBody = {
        question,
        subject: context.subject || null,
        level: context.level || 'high_school',
        language: context.language || 'en',
      };
      
      console.log('🧠 [SemanticParser] Request body:', JSON.stringify(requestBody));
      
      // Get backend URL - same as shared apiClient uses
      const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      const endpoint = `${BACKEND_URL}/api/netra/parse-concept`;
      
      console.log('🧠 [SemanticParser] Calling endpoint:', endpoint);
      
      // Call the NETRA backend endpoint
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('dhruv_ai_token') || ''}`,
        },
        credentials: 'include', // Include cookies for auth
        body: JSON.stringify(requestBody),
      });
      
      console.log('🧠 [SemanticParser] Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ [SemanticParser] LLM backend error:', response.status, errorText);
        return null;
      }
      
      const data = await response.json();
      console.log('🧠 [SemanticParser] LLM Response:', data);
      
      if (!data.success) {
        console.warn('⚠️ [SemanticParser] LLM returned unsuccessful response:', data);
        return null;
      }
      
      console.log('✅ [SemanticParser] LLM parsed:', data.topic, `(${data.entities?.length || 0} entities)`);
      
      // Convert LLM response to ConceptGraph
      const graph = this.convertLLMResponseToGraph(data);
      console.log('✅ [SemanticParser] Converted to graph:', graph.getSummary());
      
      return graph;
      
    } catch (error) {
      console.error('❌ [SemanticParser] LLM call FAILED:', error);
      console.error('❌ [SemanticParser] Error details:', error.message, error.stack);
      return null;
    }
  }
  
  /**
   * Convert LLM API response to ConceptGraph
   */
  convertLLMResponseToGraph(data) {
    const graph = new ConceptGraph();
    
    // Set metadata
    graph.setMetadata('domain', data.domain || 'physics');
    graph.setMetadata('topic', data.topic || 'Concept');
    graph.setMetadata('title', data.title || data.topic);
    graph.setMetadata('summary', data.summary || '');
    graph.setMetadata('visualType', this.mapLayoutToVisualType(data.visual_hints?.layout_strategy));
    
    // Add entities
    for (const entity of (data.entities || [])) {
      const entityType = this.mapLLMTypeToEntityType(entity.type);
      graph.addEntity(entity.id, entityType, {
        label: entity.label,
        variant: entity.variant,
        visualHint: this.mapEntityToVisualHint(entity.type, entity.variant),
        direction: entity.properties?.direction,
        color: entity.properties?.color,
        importance: entity.properties?.importance || 'normal',
        formula: entity.properties?.formula,
        mass: entity.properties?.mass,
      });
    }
    
    // Add relationships
    for (const rel of (data.relationships || [])) {
      const relType = this.mapLLMRelationToType(rel.type);
      graph.addRelationship(rel.from || rel.from_entity, rel.to || rel.to_entity, relType, {
        label: rel.label,
      });
    }
    
    // Add constraints
    for (const constraint of (data.constraints || [])) {
      graph.addConstraint(CONSTRAINT_TYPES.PHYSICS_LAW, [], {
        description: constraint,
      });
    }
    
    // Store visual hints in metadata
    if (data.visual_hints) {
      graph.setMetadata('layoutStrategy', data.visual_hints.layout_strategy);
      graph.setMetadata('emphasis', data.visual_hints.emphasis);
      graph.setMetadata('style', data.visual_hints.style);
      graph.setMetadata('annotations', data.visual_hints.annotations);
    }
    
    console.log('🧠 [SemanticParser] Converted to ConceptGraph:', graph.getSummary());
    
    return graph;
  }
  
  /**
   * Map LLM entity type to ENTITY_TYPES
   */
  mapLLMTypeToEntityType(llmType) {
    const typeMap = {
      'body': ENTITY_TYPES.BODY,
      'force': ENTITY_TYPES.FORCE,
      'vector': ENTITY_TYPES.VECTOR,
      'structure': ENTITY_TYPES.STRUCTURE,
      'process': ENTITY_TYPES.PROCESS,
      'concept': ENTITY_TYPES.OBJECT,
      'label': ENTITY_TYPES.OBJECT,
      'cell': ENTITY_TYPES.CELL,
      'atom': ENTITY_TYPES.ATOM,
      'molecule': ENTITY_TYPES.MOLECULE,
      'function': ENTITY_TYPES.FUNCTION,
      'organ': ENTITY_TYPES.ORGAN,
      'path': ENTITY_TYPES.PATH,
    };
    return typeMap[llmType?.toLowerCase()] || ENTITY_TYPES.OBJECT;
  }
  
  /**
   * Map LLM relationship type to RELATIONSHIP_TYPES
   */
  mapLLMRelationToType(llmRelation) {
    const relMap = {
      'acts_on': RELATIONSHIP_TYPES.ACTS_ON,
      'causes': RELATIONSHIP_TYPES.CAUSES,
      'contains': RELATIONSHIP_TYPES.CONTAINS,
      'opposite_to': RELATIONSHIP_TYPES.OPPOSITE_TO,
      'becomes': RELATIONSHIP_TYPES.BECOMES,
      'connects': RELATIONSHIP_TYPES.ATTACHED_TO,
      'produces': RELATIONSHIP_TYPES.PRODUCES,
      'enables': RELATIONSHIP_TYPES.ENABLES,
      'prevents': RELATIONSHIP_TYPES.PREVENTS,
    };
    return relMap[llmRelation?.toLowerCase()] || RELATIONSHIP_TYPES.ACTS_ON;
  }
  
  /**
   * Map entity type/variant to visual hint
   */
  mapEntityToVisualHint(type, variant) {
    if (type === 'force') return 'force_vector';
    if (type === 'body') return 'rigid_body';
    if (type === 'structure' && variant === 'ground') return 'ground_plane';
    if (type === 'cell') return 'cell_diagram';
    if (type === 'atom') return 'atom_orbital';
    if (type === 'process') return 'process_box';
    return type;
  }
  
  /**
   * Map layout strategy to visual type
   */
  mapLayoutToVisualType(layoutStrategy) {
    const layoutMap = {
      'force_diagram': 'force_diagram',
      'causal_flow': 'process_flow',
      'cycle': 'cycle',
      'structure': 'structure',
      'comparison': 'comparison',
      'timeline': 'timeline',
      'graph': 'graph',
    };
    return layoutMap[layoutStrategy] || 'scene';
  }
}

// ============================================
// FACTORY FUNCTION
// ============================================

/**
 * Create a semantic parser
 */
export function createSemanticParser(options) {
  return new SemanticParser(options);
}

/**
 * Quick parse helper
 */
export async function parseQuestion(question, context = {}, options = {}) {
  const parser = new SemanticParser(options);
  return await parser.parse(question, context);
}

export default SemanticParser;



