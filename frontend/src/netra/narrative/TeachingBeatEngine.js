/**
 * 🎬 TEACHING BEAT ENGINE
 * ========================
 * 
 * Transforms a ConceptGraph into a sequence of "teaching beats" -
 * the order in which a great teacher would explain the concept.
 * 
 * This is NOT about layout - it's about STORYTELLING.
 * 
 * A beat is: "What do I show the student NOW, and WHY?"
 * 
 * Example for "explain friction":
 *   Beat 1: Show the block on surface (setup)
 *   Beat 2: Show weight pulling down (gravity exists)
 *   Beat 3: Show normal force pushing up (surface reacts)
 *   Beat 4: Show applied force (you push)
 *   Beat 5: Show friction opposing (surface resists)
 *   Beat 6: Show net effect (motion or no motion)
 */

// ============================================
// TEACHING BEAT TYPES
// ============================================

export const BEAT_TYPES = {
  // Setup beats
  SETUP_SCENE: 'setup_scene',           // Establish the scenario
  INTRODUCE_OBJECT: 'introduce_object', // Show main object
  
  // Explanation beats
  SHOW_CAUSE: 'show_cause',             // Show what causes something
  SHOW_EFFECT: 'show_effect',           // Show the result
  SHOW_RELATIONSHIP: 'show_relationship', // Show how things connect
  
  // Teaching beats
  HIGHLIGHT_KEY: 'highlight_key',       // Emphasize important element
  COMPARE: 'compare',                   // Show comparison
  FORMULA_REVEAL: 'formula_reveal',     // Show mathematical relationship
  
  // Conclusion beats
  SHOW_RESULT: 'show_result',           // Final state
  ASK_QUESTION: 'ask_question',         // Prompt student thinking
};

// ============================================
// TEACHING BEAT CLASS
// ============================================

export class TeachingBeat {
  constructor(type, config = {}) {
    this.id = config.id || `beat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.type = type;
    
    // What to show in this beat
    this.entities = config.entities || [];      // Entity IDs to show
    this.relationships = config.relationships || []; // Relationship IDs to show
    this.annotations = config.annotations || []; // Text annotations
    
    // How to show it
    this.animation = config.animation || 'draw';  // draw, fade, grow, slide
    this.duration = config.duration || 1000;      // ms
    this.delay = config.delay || 0;               // ms before this beat starts
    
    // Teaching context
    this.narration = config.narration || '';      // What to say/think bubble
    this.emphasis = config.emphasis || [];        // Elements to highlight
    this.teacherAction = config.teacherAction || null; // pointer, circle, underline
    
    // Cause-effect
    this.triggerEffect = config.triggerEffect || null; // Animation to trigger
    this.waitForPrevious = config.waitForPrevious !== false; // Sequential by default
  }
  
  toJSON() {
    return {
      id: this.id,
      type: this.type,
      entities: this.entities,
      relationships: this.relationships,
      annotations: this.annotations,
      animation: this.animation,
      duration: this.duration,
      delay: this.delay,
      narration: this.narration,
      emphasis: this.emphasis,
      teacherAction: this.teacherAction,
      triggerEffect: this.triggerEffect,
      waitForPrevious: this.waitForPrevious,
    };
  }
}

// ============================================
// TEACHING SEQUENCE CLASS
// ============================================

export class TeachingSequence {
  constructor() {
    this.beats = [];
    this.metadata = {
      totalDuration: 0,
      beatCount: 0,
    };
  }
  
  addBeat(beat) {
    this.beats.push(beat);
    this.metadata.beatCount = this.beats.length;
    this.metadata.totalDuration += beat.duration + beat.delay;
    return this;
  }
  
  getBeat(index) {
    return this.beats[index] || null;
  }
  
  toJSON() {
    return {
      beats: this.beats.map(b => b.toJSON()),
      metadata: this.metadata,
    };
  }
}

// ============================================
// CONCEPT TEACHING TEMPLATES
// ============================================

/**
 * These templates define HOW to teach specific physics concepts.
 * Each template is a function that takes a ConceptGraph and returns a TeachingSequence.
 */
const PHYSICS_TEACHING_TEMPLATES = {
  // FRICTION - The classic force diagram
  friction: (graph) => {
    const sequence = new TeachingSequence();
    const entities = Array.from(graph.entities.keys());
    
    // Beat 1: Setup - Show the block and surface
    sequence.addBeat(new TeachingBeat(BEAT_TYPES.SETUP_SCENE, {
      id: 'setup',
      entities: entities.filter(e => ['block', 'ground', 'surface'].includes(e)),
      animation: 'draw',
      duration: 800,
      narration: "Let's look at a block resting on a surface...",
      teacherAction: 'draw',
    }));
    
    // Beat 2: Gravity - Show weight
    sequence.addBeat(new TeachingBeat(BEAT_TYPES.SHOW_CAUSE, {
      id: 'gravity',
      entities: entities.filter(e => e.includes('weight') || e.includes('gravity')),
      animation: 'grow_down',
      duration: 600,
      delay: 200,
      narration: "Gravity pulls it down with force W = mg",
      emphasis: ['weight'],
      teacherAction: 'pointer',
    }));
    
    // Beat 3: Normal force - Surface reaction
    sequence.addBeat(new TeachingBeat(BEAT_TYPES.SHOW_EFFECT, {
      id: 'normal',
      entities: entities.filter(e => e.includes('normal')),
      animation: 'grow_up',
      duration: 600,
      delay: 200,
      narration: "The surface pushes back with normal force N",
      relationships: graph.relationships.filter(r => 
        r.type === 'opposite_to' && 
        (r.from.includes('normal') || r.to.includes('normal'))
      ).map(r => r.id),
    }));
    
    // Beat 4: Applied force - The push
    sequence.addBeat(new TeachingBeat(BEAT_TYPES.SHOW_CAUSE, {
      id: 'applied',
      entities: entities.filter(e => e.includes('applied') || e.includes('push')),
      animation: 'grow_right',
      duration: 600,
      delay: 300,
      narration: "When you push with force F...",
      emphasis: ['applied_force'],
      teacherAction: 'circle',
    }));
    
    // Beat 5: Friction - The opposition
    sequence.addBeat(new TeachingBeat(BEAT_TYPES.SHOW_EFFECT, {
      id: 'friction',
      entities: entities.filter(e => e.includes('friction')),
      animation: 'grow_left',
      duration: 800,
      delay: 200,
      narration: "Friction opposes! f = μN",
      emphasis: ['friction_force'],
      teacherAction: 'underline',
      triggerEffect: 'friction_resistance',
    }));
    
    // Beat 6: Result - Net force
    sequence.addBeat(new TeachingBeat(BEAT_TYPES.SHOW_RESULT, {
      id: 'result',
      annotations: [{
        type: 'formula',
        text: 'If F > f → Motion!',
        position: 'bottom',
      }],
      animation: 'fade',
      duration: 1000,
      delay: 400,
      narration: "If your push beats friction, the block moves!",
      teacherAction: 'pointer',
    }));
    
    return sequence;
  },
  
  // NEWTON'S LAWS
  newton: (graph) => {
    const sequence = new TeachingSequence();
    const entities = Array.from(graph.entities.keys());
    
    // Beat 1: Show two objects
    sequence.addBeat(new TeachingBeat(BEAT_TYPES.SETUP_SCENE, {
      entities: entities.filter(e => e.includes('object') || e.includes('body')),
      animation: 'draw',
      duration: 800,
      narration: "When two objects interact...",
    }));
    
    // Beat 2: Show action force
    sequence.addBeat(new TeachingBeat(BEAT_TYPES.SHOW_CAUSE, {
      entities: entities.filter(e => e.includes('action')),
      animation: 'grow',
      duration: 600,
      narration: "One pushes on the other (Action)",
      emphasis: ['action_force'],
    }));
    
    // Beat 3: Show reaction force
    sequence.addBeat(new TeachingBeat(BEAT_TYPES.SHOW_EFFECT, {
      entities: entities.filter(e => e.includes('reaction')),
      animation: 'grow',
      duration: 600,
      delay: 300,
      narration: "It pushes back equally! (Reaction)",
      emphasis: ['reaction_force'],
      triggerEffect: 'equal_opposite',
    }));
    
    // Beat 4: Show equality
    sequence.addBeat(new TeachingBeat(BEAT_TYPES.FORMULA_REVEAL, {
      annotations: [{
        type: 'formula',
        text: 'F₁₂ = -F₂₁',
        position: 'center',
      }],
      animation: 'pop',
      duration: 800,
      narration: "Always equal, always opposite!",
    }));
    
    return sequence;
  },
  
  // PROJECTILE MOTION
  projectile: (graph) => {
    const sequence = new TeachingSequence();
    
    // Beat 1: Show projectile
    sequence.addBeat(new TeachingBeat(BEAT_TYPES.INTRODUCE_OBJECT, {
      entities: ['projectile', 'ball'],
      animation: 'draw',
      duration: 500,
      narration: "A ball is thrown...",
    }));
    
    // Beat 2: Show initial velocity
    sequence.addBeat(new TeachingBeat(BEAT_TYPES.SHOW_CAUSE, {
      entities: ['initial_velocity'],
      animation: 'grow',
      duration: 600,
      narration: "With initial velocity v₀",
    }));
    
    // Beat 3: Show trajectory
    sequence.addBeat(new TeachingBeat(BEAT_TYPES.SHOW_EFFECT, {
      entities: ['trajectory'],
      animation: 'trace_path',
      duration: 1500,
      narration: "It follows a parabolic path...",
      triggerEffect: 'parabola_trace',
    }));
    
    // Beat 4: Show gravity effect
    sequence.addBeat(new TeachingBeat(BEAT_TYPES.SHOW_CAUSE, {
      entities: ['gravity'],
      animation: 'grow_down',
      duration: 600,
      narration: "Gravity pulls it down continuously",
    }));
    
    return sequence;
  },
  
  // FREE BODY DIAGRAM
  'free body': (graph) => {
    const sequence = new TeachingSequence();
    const entities = Array.from(graph.entities.keys());
    
    // Beat 1: Isolate the body
    sequence.addBeat(new TeachingBeat(BEAT_TYPES.INTRODUCE_OBJECT, {
      entities: entities.filter(e => e.includes('body') || e.includes('object') || e.includes('block')),
      animation: 'draw',
      duration: 800,
      narration: "First, isolate the object...",
      teacherAction: 'circle',
    }));
    
    // Beat 2: Add all forces one by one
    const forces = entities.filter(e => 
      e.includes('force') || e.includes('weight') || e.includes('normal') || e.includes('friction')
    );
    
    forces.forEach((force, index) => {
      sequence.addBeat(new TeachingBeat(BEAT_TYPES.SHOW_CAUSE, {
        entities: [force],
        animation: 'grow',
        duration: 500,
        delay: 200,
        narration: `Force ${index + 1}: ${force.replace(/_/g, ' ')}`,
      }));
    });
    
    // Final beat: Show sum
    sequence.addBeat(new TeachingBeat(BEAT_TYPES.FORMULA_REVEAL, {
      annotations: [{
        type: 'formula',
        text: 'ΣF = ma',
        position: 'bottom',
      }],
      animation: 'pop',
      duration: 800,
      narration: "Sum of all forces = mass × acceleration",
    }));
    
    return sequence;
  },
};

// ============================================
// TEACHING BEAT ENGINE CLASS
// ============================================

export class TeachingBeatEngine {
  constructor(options = {}) {
    this.options = {
      defaultBeatDuration: 800,
      pauseBetweenBeats: 200,
      enableNarration: true,
      ...options,
    };
  }
  
  /**
   * Generate teaching sequence from ConceptGraph
   */
  generateSequence(conceptGraph, context = {}) {
    const topic = conceptGraph.metadata.topic?.toLowerCase() || '';
    const domain = conceptGraph.metadata.domain || 'physics';
    
    console.log(`🎬 [TeachingBeatEngine] Generating sequence for: "${topic}" (${domain})`);
    
    // Try to find a specific teaching template
    for (const [key, template] of Object.entries(PHYSICS_TEACHING_TEMPLATES)) {
      if (topic.includes(key)) {
        console.log(`🎬 [TeachingBeatEngine] Using template: ${key}`);
        return template(conceptGraph);
      }
    }
    
    // Fallback: Generate generic sequence
    console.log(`🎬 [TeachingBeatEngine] Using generic sequence generator`);
    return this.generateGenericSequence(conceptGraph);
  }
  
  /**
   * Generate a generic teaching sequence when no template matches
   */
  generateGenericSequence(conceptGraph) {
    const sequence = new TeachingSequence();
    const entities = Array.from(conceptGraph.entities.entries());
    
    // Sort by importance
    entities.sort((a, b) => {
      const impA = a[1].properties?.importance === 'high' ? 0 : 1;
      const impB = b[1].properties?.importance === 'high' ? 0 : 1;
      return impA - impB;
    });
    
    // Group entities by type
    const bodies = entities.filter(([_, e]) => e.type === 'body' || e.type === 'object');
    const forces = entities.filter(([_, e]) => e.type === 'force');
    const structures = entities.filter(([_, e]) => e.type === 'structure');
    const others = entities.filter(([_, e]) => 
      !['body', 'object', 'force', 'structure'].includes(e.type)
    );
    
    // Beat 1: Setup - structures first
    if (structures.length > 0) {
      sequence.addBeat(new TeachingBeat(BEAT_TYPES.SETUP_SCENE, {
        entities: structures.map(([id]) => id),
        animation: 'draw',
        duration: 600,
        narration: "Setting up the scene...",
      }));
    }
    
    // Beat 2: Main objects
    if (bodies.length > 0) {
      sequence.addBeat(new TeachingBeat(BEAT_TYPES.INTRODUCE_OBJECT, {
        entities: bodies.map(([id]) => id),
        animation: 'draw',
        duration: 800,
        narration: "Here's our main object...",
      }));
    }
    
    // Beat 3+: Forces one at a time
    forces.forEach(([id, entity], index) => {
      const direction = entity.properties?.direction || 'right';
      const animation = direction === 'down' ? 'grow_down' : 
                        direction === 'up' ? 'grow_up' :
                        direction === 'left' ? 'grow_left' : 'grow_right';
      
      sequence.addBeat(new TeachingBeat(BEAT_TYPES.SHOW_CAUSE, {
        entities: [id],
        animation,
        duration: 600,
        delay: 200,
        narration: entity.properties?.label || id.replace(/_/g, ' '),
        emphasis: [id],
      }));
    });
    
    // Final beat: Other entities
    if (others.length > 0) {
      sequence.addBeat(new TeachingBeat(BEAT_TYPES.SHOW_RELATIONSHIP, {
        entities: others.map(([id]) => id),
        animation: 'fade',
        duration: 600,
        narration: "Additional elements...",
      }));
    }
    
    return sequence;
  }
}

// ============================================
// EXPORTS
// ============================================

export function createTeachingBeatEngine(options) {
  return new TeachingBeatEngine(options);
}

export default TeachingBeatEngine;

