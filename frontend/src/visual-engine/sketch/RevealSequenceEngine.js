/**
 * 🎬 REVEAL SEQUENCE ENGINE (SketchSense V6)
 * ==========================================
 * 
 * Controls the cinematic flow of sketch animations.
 * Everything draws in sequence like a tutor sketching live.
 * 
 * Timeline:
 * 0.0s - Background loads (paper texture)
 * 0.3s - Main shapes draw
 * 1.0s - Arrows animate
 * 1.4s - Highlights appear
 * 1.8s - Labels write in
 * 2.0s - Doodles pop
 * 2.2s - Interactive elements activate
 * 
 * The magic is in the TIMING! ✨
 */

// ============================================
// TIMING CONSTANTS
// ============================================
export const TIMING = {
  // Phase delays (in seconds)
  BACKGROUND: 0.0,
  SHAPES: 0.3,
  CONNECTIONS: 1.0,
  HIGHLIGHTS: 1.4,
  LABELS: 1.8,
  DOODLES: 2.0,
  INTERACTIVE: 2.2,
  
  // Durations
  DRAW_DURATION: 1.5,
  FADE_DURATION: 0.5,
  POP_DURATION: 0.4,
  
  // Stagger between items in same phase
  STAGGER: 0.1,
};

// ============================================
// ELEMENT TYPES
// ============================================
export const ELEMENT_TYPES = {
  BACKGROUND: 'background',
  SHAPE: 'shape',         // circles, rectangles
  CONNECTION: 'connection', // arrows, lines
  HIGHLIGHT: 'highlight',  // marker highlights
  LABEL: 'label',         // text labels
  DOODLE: 'doodle',       // decorations
  INTERACTIVE: 'interactive', // sliders, buttons
  FIGURE: 'figure',       // stick figures
};

// ============================================
// REVEAL SEQUENCE ENGINE CLASS
// ============================================
export class RevealSequenceEngine {
  constructor(options = {}) {
    this.elements = [];
    this.currentPhase = 0;
    this.isPlaying = false;
    this.isPaused = false;
    this.speed = options.speed || 1.0;
    this.onPhaseComplete = options.onPhaseComplete || null;
    this.onComplete = options.onComplete || null;
    
    // Timing overrides
    this.timing = { ...TIMING, ...options.timing };
  }
  
  /**
   * Add element to the sequence
   */
  addElement(element) {
    const elementWithTiming = {
      ...element,
      delay: this.calculateDelay(element),
    };
    this.elements.push(elementWithTiming);
    return this;
  }
  
  /**
   * Add multiple elements
   */
  addElements(elements) {
    elements.forEach(el => this.addElement(el));
    return this;
  }
  
  /**
   * Calculate delay based on element type and index
   */
  calculateDelay(element) {
    const typeOrder = [
      ELEMENT_TYPES.BACKGROUND,
      ELEMENT_TYPES.SHAPE,
      ELEMENT_TYPES.FIGURE,
      ELEMENT_TYPES.CONNECTION,
      ELEMENT_TYPES.HIGHLIGHT,
      ELEMENT_TYPES.LABEL,
      ELEMENT_TYPES.DOODLE,
      ELEMENT_TYPES.INTERACTIVE,
    ];
    
    const phaseDelays = {
      [ELEMENT_TYPES.BACKGROUND]: this.timing.BACKGROUND,
      [ELEMENT_TYPES.SHAPE]: this.timing.SHAPES,
      [ELEMENT_TYPES.FIGURE]: this.timing.SHAPES + 0.2,
      [ELEMENT_TYPES.CONNECTION]: this.timing.CONNECTIONS,
      [ELEMENT_TYPES.HIGHLIGHT]: this.timing.HIGHLIGHTS,
      [ELEMENT_TYPES.LABEL]: this.timing.LABELS,
      [ELEMENT_TYPES.DOODLE]: this.timing.DOODLES,
      [ELEMENT_TYPES.INTERACTIVE]: this.timing.INTERACTIVE,
    };
    
    // Count existing elements of same type for stagger
    const sameTypeElements = this.elements.filter(el => el.type === element.type);
    const staggerOffset = sameTypeElements.length * this.timing.STAGGER;
    
    const baseDelay = phaseDelays[element.type] || this.timing.SHAPES;
    return (baseDelay + staggerOffset) / this.speed;
  }
  
  /**
   * Get all elements with their calculated delays
   */
  getSequence() {
    return this.elements.sort((a, b) => a.delay - b.delay);
  }
  
  /**
   * Get total animation duration
   */
  getTotalDuration() {
    if (this.elements.length === 0) return 0;
    const lastElement = this.elements.reduce((max, el) => 
      el.delay > max.delay ? el : max
    );
    return lastElement.delay + this.timing.DRAW_DURATION / this.speed;
  }
  
  /**
   * Generate Framer Motion variants for an element
   */
  getVariants(elementType) {
    const drawVariants = {
      hidden: { pathLength: 0, opacity: 0 },
      visible: {
        pathLength: 1,
        opacity: 1,
        transition: {
          pathLength: { type: 'spring', duration: this.timing.DRAW_DURATION / this.speed, bounce: 0 },
          opacity: { duration: 0.3 }
        }
      }
    };
    
    const fadeVariants = {
      hidden: { opacity: 0, scale: 0.8 },
      visible: {
        opacity: 1,
        scale: 1,
        transition: { duration: this.timing.FADE_DURATION / this.speed }
      }
    };
    
    const popVariants = {
      hidden: { opacity: 0, scale: 0 },
      visible: {
        opacity: 1,
        scale: [0, 1.2, 1],
        transition: { duration: this.timing.POP_DURATION / this.speed, times: [0, 0.6, 1] }
      }
    };
    
    const slideVariants = {
      hidden: { opacity: 0, y: 20 },
      visible: {
        opacity: 1,
        y: 0,
        transition: { duration: this.timing.FADE_DURATION / this.speed }
      }
    };
    
    switch (elementType) {
      case ELEMENT_TYPES.SHAPE:
      case ELEMENT_TYPES.CONNECTION:
        return drawVariants;
      case ELEMENT_TYPES.HIGHLIGHT:
      case ELEMENT_TYPES.BACKGROUND:
        return fadeVariants;
      case ELEMENT_TYPES.DOODLE:
        return popVariants;
      case ELEMENT_TYPES.LABEL:
      case ELEMENT_TYPES.INTERACTIVE:
      default:
        return slideVariants;
    }
  }
  
  /**
   * Reset the sequence
   */
  reset() {
    this.elements = [];
    this.currentPhase = 0;
    this.isPlaying = false;
    this.isPaused = false;
    return this;
  }
  
  /**
   * Set playback speed (1.0 = normal, 2.0 = 2x fast, 0.5 = half speed)
   */
  setSpeed(speed) {
    this.speed = Math.max(0.1, Math.min(5, speed));
    // Recalculate all delays
    this.elements = this.elements.map(el => ({
      ...el,
      delay: this.calculateDelay(el),
    }));
    return this;
  }
}

// ============================================
// SEQUENCE BUILDER (Fluent API)
// ============================================
export class SequenceBuilder {
  constructor() {
    this.engine = new RevealSequenceEngine();
    this.customDelays = {};
  }
  
  /**
   * Add background element
   */
  background(props = {}) {
    this.engine.addElement({
      type: ELEMENT_TYPES.BACKGROUND,
      ...props,
    });
    return this;
  }
  
  /**
   * Add shape (circle, rect, etc.)
   */
  shape(shapeType, props = {}) {
    this.engine.addElement({
      type: ELEMENT_TYPES.SHAPE,
      shapeType,
      ...props,
    });
    return this;
  }
  
  /**
   * Add stick figure
   */
  figure(pose, props = {}) {
    this.engine.addElement({
      type: ELEMENT_TYPES.FIGURE,
      pose,
      ...props,
    });
    return this;
  }
  
  /**
   * Add arrow/line connection
   */
  connect(from, to, props = {}) {
    this.engine.addElement({
      type: ELEMENT_TYPES.CONNECTION,
      from,
      to,
      ...props,
    });
    return this;
  }
  
  /**
   * Add highlight
   */
  highlight(target, props = {}) {
    this.engine.addElement({
      type: ELEMENT_TYPES.HIGHLIGHT,
      target,
      ...props,
    });
    return this;
  }
  
  /**
   * Add label
   */
  label(text, position, props = {}) {
    this.engine.addElement({
      type: ELEMENT_TYPES.LABEL,
      text,
      position,
      ...props,
    });
    return this;
  }
  
  /**
   * Add doodle decoration
   */
  doodle(doodleType, position, props = {}) {
    this.engine.addElement({
      type: ELEMENT_TYPES.DOODLE,
      doodleType,
      position,
      ...props,
    });
    return this;
  }
  
  /**
   * Add interactive element
   */
  interactive(interactiveType, props = {}) {
    this.engine.addElement({
      type: ELEMENT_TYPES.INTERACTIVE,
      interactiveType,
      ...props,
    });
    return this;
  }
  
  /**
   * Build and return the sequence
   */
  build() {
    return this.engine;
  }
}

// ============================================
// PRESET SEQUENCES
// ============================================
export const PRESET_SEQUENCES = {
  /**
   * Simple concept explanation
   */
  simpleConcept: () => {
    return new SequenceBuilder()
      .background()
      .shape('circle', { id: 'main', label: 'Concept' })
      .label('Main Idea', { x: 200, y: 50 })
      .doodle('sparkle', { x: 250, y: 80 })
      .build();
  },
  
  /**
   * Cause and Effect
   */
  causeEffect: () => {
    return new SequenceBuilder()
      .background()
      .shape('rect', { id: 'cause', x: 50, y: 100 })
      .shape('rect', { id: 'effect', x: 250, y: 100 })
      .connect('cause', 'effect', { label: 'leads to' })
      .label('Cause', { x: 100, y: 90 })
      .label('Effect', { x: 300, y: 90 })
      .highlight('effect')
      .doodle('star', { x: 350, y: 80 })
      .build();
  },
  
  /**
   * Process Flow
   */
  processFlow: (steps = 3) => {
    const builder = new SequenceBuilder().background();
    
    for (let i = 0; i < steps; i++) {
      builder.shape('rect', { id: `step${i}`, x: 50 + i * 150, y: 100 });
      builder.label(`Step ${i + 1}`, { x: 100 + i * 150, y: 90 });
      if (i < steps - 1) {
        builder.connect(`step${i}`, `step${i + 1}`);
      }
    }
    
    builder.doodle('sparkle', { x: 50 + (steps - 1) * 150 + 80, y: 80 });
    return builder.build();
  },
  
  /**
   * Comparison (Side by Side)
   */
  comparison: () => {
    return new SequenceBuilder()
      .background()
      .shape('rect', { id: 'left', x: 50, y: 80, width: 150, height: 200 })
      .shape('rect', { id: 'right', x: 250, y: 80, width: 150, height: 200 })
      .label('Option A', { x: 125, y: 60 })
      .label('Option B', { x: 325, y: 60 })
      .label('VS', { x: 225, y: 180, fontSize: 24 })
      .highlight('left', { color: '#93C5FD' })
      .highlight('right', { color: '#FDBA74' })
      .build();
  },
  
  /**
   * Physics Force Diagram
   */
  forceDiagram: () => {
    return new SequenceBuilder()
      .background()
      .figure('pushing', { x: 100, y: 200 })
      .shape('rect', { id: 'block', x: 180, y: 180, width: 60, height: 50 })
      .connect('figure', 'block', { label: 'F = ma' })
      .highlight('block')
      .label('Force', { x: 150, y: 150 })
      .doodle('burst', { x: 250, y: 170 })
      .build();
  },
};

// ============================================
// HELPER FUNCTIONS
// ============================================
export function createSequence(options = {}) {
  return new RevealSequenceEngine(options);
}

export function buildSequence() {
  return new SequenceBuilder();
}

// ============================================
// EXPORTS
// ============================================
export default RevealSequenceEngine;


