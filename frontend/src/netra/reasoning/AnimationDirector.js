/**
 * 🎬 ANIMATION DIRECTOR
 * =====================
 * 
 * Decides HOW to reveal the visual over time based on intent.
 * 
 * Different intents need different reveal strategies:
 * - COUNTERFACTUAL: Flash between reality and alternate
 * - CAUSAL_INQUIRY: Show cause, pause, then effect
 * - TEMPORAL: Sequential timeline reveal
 * - INTUITIVE: Story-like beats with narration
 * 
 * The director creates an animation plan, not specific keyframes.
 * The renderer interprets the plan.
 */

import { INTENT_TYPES } from './IntentClassifier';
import { VISUAL_FORMS } from './FormSelector';

// ============================================
// ANIMATION STRATEGIES
// ============================================

export const ANIMATION_STRATEGIES = {
  // Sequential strategies
  SEQUENTIAL_BUILD: 'sequential_build',     // A, then B, then C
  PROGRESSIVE_REVEAL: 'progressive_reveal', // Gradually more detail
  
  // Parallel strategies
  PARALLEL_EMERGE: 'parallel_emerge',       // A and B appear together
  SIMULTANEOUS: 'simultaneous',             // Everything at once
  
  // Comparative strategies
  CONTRAST_FLASH: 'contrast_flash',         // Flash between A and B
  SIDE_BY_SIDE_GROW: 'side_by_side_grow',   // Both grow simultaneously
  ALTERNATE_FOCUS: 'alternate_focus',       // Focus A, then focus B
  
  // Causal strategies
  CAUSE_THEN_EFFECT: 'cause_then_effect',   // Cause → pause → effect
  CHAIN_REACTION: 'chain_reaction',         // Domino effect
  TRIGGER_RESPONSE: 'trigger_response',     // Action → reaction
  
  // Story strategies
  STORY_BEATS: 'story_beats',               // Narrative with pauses
  TEACHER_DRAWING: 'teacher_drawing',       // Like hand-drawing
  CINEMATIC: 'cinematic',                   // Zoom, pan, reveal
  
  // Temporal strategies
  TIMELINE_MARCH: 'timeline_march',         // Left to right time
  BEFORE_AFTER: 'before_after',             // State transition
  
  // Emphasis strategies
  HIGHLIGHT_KEY: 'highlight_key',           // Pop the important part
  ZOOM_FOCUS: 'zoom_focus',                 // Zoom into detail
};

// ============================================
// INTENT TO ANIMATION MAPPING
// ============================================

const INTENT_ANIMATION_MAPPING = {
  [INTENT_TYPES.CONCEPTUAL]: {
    primary: ANIMATION_STRATEGIES.TEACHER_DRAWING,
    alternatives: [ANIMATION_STRATEGIES.SEQUENTIAL_BUILD, ANIMATION_STRATEGIES.PROGRESSIVE_REVEAL],
  },
  
  [INTENT_TYPES.CAUSAL_INQUIRY]: {
    primary: ANIMATION_STRATEGIES.CAUSE_THEN_EFFECT,
    alternatives: [ANIMATION_STRATEGIES.CHAIN_REACTION],
  },
  
  [INTENT_TYPES.MECHANISTIC]: {
    primary: ANIMATION_STRATEGIES.CHAIN_REACTION,
    alternatives: [ANIMATION_STRATEGIES.SEQUENTIAL_BUILD],
  },
  
  [INTENT_TYPES.COUNTERFACTUAL]: {
    primary: ANIMATION_STRATEGIES.CONTRAST_FLASH,
    alternatives: [ANIMATION_STRATEGIES.SIDE_BY_SIDE_GROW, ANIMATION_STRATEGIES.ALTERNATE_FOCUS],
  },
  
  [INTENT_TYPES.COMPARATIVE]: {
    primary: ANIMATION_STRATEGIES.SIDE_BY_SIDE_GROW,
    alternatives: [ANIMATION_STRATEGIES.ALTERNATE_FOCUS],
  },
  
  [INTENT_TYPES.CLASSIFICATORY]: {
    primary: ANIMATION_STRATEGIES.PROGRESSIVE_REVEAL,
    alternatives: [ANIMATION_STRATEGIES.SEQUENTIAL_BUILD],
  },
  
  [INTENT_TYPES.TEMPORAL]: {
    primary: ANIMATION_STRATEGIES.TIMELINE_MARCH,
    alternatives: [ANIMATION_STRATEGIES.BEFORE_AFTER],
  },
  
  [INTENT_TYPES.SEQUENTIAL]: {
    primary: ANIMATION_STRATEGIES.SEQUENTIAL_BUILD,
    alternatives: [ANIMATION_STRATEGIES.CHAIN_REACTION],
  },
  
  [INTENT_TYPES.INTUITIVE]: {
    primary: ANIMATION_STRATEGIES.STORY_BEATS,
    alternatives: [ANIMATION_STRATEGIES.TEACHER_DRAWING, ANIMATION_STRATEGIES.CINEMATIC],
  },
  
  [INTENT_TYPES.ANALOGICAL]: {
    primary: ANIMATION_STRATEGIES.STORY_BEATS,
    alternatives: [ANIMATION_STRATEGIES.PARALLEL_EMERGE],
  },
  
  [INTENT_TYPES.QUANTITATIVE]: {
    primary: ANIMATION_STRATEGIES.SEQUENTIAL_BUILD,
    alternatives: [ANIMATION_STRATEGIES.HIGHLIGHT_KEY],
  },
  
  [INTENT_TYPES.RELATIONAL]: {
    primary: ANIMATION_STRATEGIES.PROGRESSIVE_REVEAL,
    alternatives: [ANIMATION_STRATEGIES.TRIGGER_RESPONSE],
  },
  
  [INTENT_TYPES.EDGE_CASE]: {
    primary: ANIMATION_STRATEGIES.BEFORE_AFTER,
    alternatives: [ANIMATION_STRATEGIES.HIGHLIGHT_KEY],
  },
  
  [INTENT_TYPES.BOUNDARY]: {
    primary: ANIMATION_STRATEGIES.PROGRESSIVE_REVEAL,
    alternatives: [ANIMATION_STRATEGIES.ZOOM_FOCUS],
  },
};

// ============================================
// ANIMATION STRATEGY SPECIFICATIONS
// ============================================

const STRATEGY_SPECS = {
  [ANIMATION_STRATEGIES.SEQUENTIAL_BUILD]: {
    name: 'Sequential Build',
    description: 'Elements appear one after another',
    timing: {
      stagger: 400,        // Delay between elements
      duration: 500,       // Each element animation
      easing: 'easeOut',
    },
    order: 'importance',   // Order by importance or position
    effects: ['fade_in', 'scale_up'],
  },
  
  [ANIMATION_STRATEGIES.PROGRESSIVE_REVEAL]: {
    name: 'Progressive Reveal',
    description: 'Gradually reveal more detail',
    timing: {
      stagger: 300,
      duration: 600,
      easing: 'easeInOut',
    },
    order: 'hierarchy',    // Core first, details later
    effects: ['fade_in', 'blur_in'],
  },
  
  [ANIMATION_STRATEGIES.PARALLEL_EMERGE]: {
    name: 'Parallel Emerge',
    description: 'Elements grow together',
    timing: {
      stagger: 0,          // No stagger
      duration: 800,
      easing: 'spring',
    },
    order: 'simultaneous',
    effects: ['scale_up', 'fade_in'],
  },
  
  [ANIMATION_STRATEGIES.CONTRAST_FLASH]: {
    name: 'Contrast Flash',
    description: 'Alternate between two states',
    timing: {
      flashDuration: 1000,
      flashCount: 2,
      finalHold: 2000,
      easing: 'linear',
    },
    order: 'alternating',
    effects: ['flash', 'crossfade'],
    special: 'toggle_visibility',
  },
  
  [ANIMATION_STRATEGIES.SIDE_BY_SIDE_GROW]: {
    name: 'Side by Side Grow',
    description: 'Both sides grow simultaneously',
    timing: {
      stagger: 100,
      duration: 700,
      easing: 'spring',
    },
    order: 'parallel_groups',
    effects: ['scale_up', 'slide_in'],
  },
  
  [ANIMATION_STRATEGIES.ALTERNATE_FOCUS]: {
    name: 'Alternate Focus',
    description: 'Spotlight shifts between elements',
    timing: {
      focusDuration: 1500,
      transitionDuration: 300,
      easing: 'easeInOut',
    },
    order: 'group_alternate',
    effects: ['spotlight', 'dim_others'],
  },
  
  [ANIMATION_STRATEGIES.CAUSE_THEN_EFFECT]: {
    name: 'Cause Then Effect',
    description: 'Show cause, pause, show effect',
    timing: {
      causeDuration: 800,
      pauseDuration: 600,
      effectDuration: 800,
      easing: 'easeOut',
    },
    order: 'causal',
    effects: ['draw', 'pulse', 'grow'],
  },
  
  [ANIMATION_STRATEGIES.CHAIN_REACTION]: {
    name: 'Chain Reaction',
    description: 'Domino effect through elements',
    timing: {
      stagger: 250,
      duration: 400,
      overlap: 0.3,        // 30% overlap
      easing: 'easeIn',
    },
    order: 'causal_chain',
    effects: ['trigger', 'ripple'],
  },
  
  [ANIMATION_STRATEGIES.TRIGGER_RESPONSE]: {
    name: 'Trigger Response',
    description: 'Action causes reaction',
    timing: {
      triggerDuration: 500,
      responseDuration: 600,
      responseDelay: 200,
      easing: 'spring',
    },
    order: 'action_reaction',
    effects: ['push', 'bounce'],
  },
  
  [ANIMATION_STRATEGIES.STORY_BEATS]: {
    name: 'Story Beats',
    description: 'Narrative with pauses',
    timing: {
      beatDuration: 1200,
      pauseBetween: 500,
      easing: 'easeInOut',
    },
    order: 'narrative',
    effects: ['draw', 'fade_in', 'thought_bubble'],
    narration: true,
  },
  
  [ANIMATION_STRATEGIES.TEACHER_DRAWING]: {
    name: 'Teacher Drawing',
    description: 'Like watching someone draw',
    timing: {
      strokeDuration: 600,
      pauseBetween: 200,
      easing: 'linear',
    },
    order: 'drawing_order',
    effects: ['pencil_draw', 'sketch_in'],
  },
  
  [ANIMATION_STRATEGIES.CINEMATIC]: {
    name: 'Cinematic',
    description: 'Camera movements and reveals',
    timing: {
      panDuration: 1000,
      zoomDuration: 800,
      holdDuration: 500,
      easing: 'easeInOut',
    },
    order: 'scene',
    effects: ['pan', 'zoom', 'fade'],
  },
  
  [ANIMATION_STRATEGIES.TIMELINE_MARCH]: {
    name: 'Timeline March',
    description: 'Progress along timeline',
    timing: {
      stagger: 500,
      duration: 400,
      easing: 'linear',
    },
    order: 'temporal',
    effects: ['slide_in', 'marker_appear'],
  },
  
  [ANIMATION_STRATEGIES.BEFORE_AFTER]: {
    name: 'Before After',
    description: 'State transition',
    timing: {
      beforeDuration: 1000,
      transitionDuration: 600,
      afterDuration: 1000,
      easing: 'easeInOut',
    },
    order: 'state_change',
    effects: ['morph', 'crossfade'],
  },
  
  [ANIMATION_STRATEGIES.HIGHLIGHT_KEY]: {
    name: 'Highlight Key',
    description: 'Emphasize important element',
    timing: {
      setupDuration: 500,
      highlightDuration: 1500,
      pulseDuration: 300,
      easing: 'spring',
    },
    order: 'emphasis_last',
    effects: ['glow', 'pulse', 'scale_up'],
  },
  
  [ANIMATION_STRATEGIES.ZOOM_FOCUS]: {
    name: 'Zoom Focus',
    description: 'Zoom into detail',
    timing: {
      zoomDuration: 800,
      holdDuration: 1500,
      zoomOutDuration: 600,
      easing: 'easeInOut',
    },
    order: 'zoom_target',
    effects: ['zoom', 'blur_background'],
  },
  
  [ANIMATION_STRATEGIES.SIMULTANEOUS]: {
    name: 'Simultaneous',
    description: 'Everything appears at once',
    timing: {
      duration: 500,
      easing: 'spring',
    },
    order: 'all',
    effects: ['fade_in'],
  },
};

// ============================================
// ANIMATION DIRECTOR CLASS
// ============================================

export class AnimationDirector {
  constructor(options = {}) {
    this.options = {
      preferVariation: true,
      includeNarration: true,
      ...options,
    };
    
    this.lastStrategy = null;
  }
  
  /**
   * Direct the animation for the visual
   * @param {Object} intentResult - Result from IntentClassifier
   * @param {Object} formResult - Result from FormSelector
   * @param {Object} layoutResult - Result from LayoutVariator
   * @returns {Object} Animation direction plan
   */
  direct(intentResult, formResult, layoutResult) {
    const intent = intentResult.primary;
    const mapping = INTENT_ANIMATION_MAPPING[intent];
    
    if (!mapping) {
      console.warn(`⚠️ [AnimationDirector] No mapping for intent: ${intent}`);
      return this.createResult(ANIMATION_STRATEGIES.SEQUENTIAL_BUILD, intentResult);
    }
    
    // Select strategy
    let strategy = mapping.primary;
    
    // Use alternative for variation
    if (this.options.preferVariation && mapping.alternatives.length > 0) {
      if (strategy === this.lastStrategy || Math.random() < 0.3) {
        const alternatives = mapping.alternatives.filter(s => s !== this.lastStrategy);
        if (alternatives.length > 0) {
          strategy = alternatives[Math.floor(Math.random() * alternatives.length)];
        }
      }
    }
    
    this.lastStrategy = strategy;
    
    const spec = STRATEGY_SPECS[strategy];
    const result = this.createResult(strategy, intentResult, spec, layoutResult);
    
    console.log(`🎬 [AnimationDirector] Strategy: ${spec.name}`);
    
    return result;
  }
  
  /**
   * Create animation direction result
   */
  createResult(strategy, intentResult, spec = null, layoutResult = null) {
    spec = spec || STRATEGY_SPECS[strategy] || STRATEGY_SPECS[ANIMATION_STRATEGIES.SEQUENTIAL_BUILD];
    
    return {
      strategy,
      name: spec.name,
      description: spec.description,
      timing: { ...spec.timing },
      order: spec.order,
      effects: [...spec.effects],
      narration: spec.narration || false,
      
      // Context
      intent: intentResult.primary,
      layout: layoutResult?.layout || 'default',
      
      // Helper methods
      getTiming: () => spec.timing,
      getEffects: () => spec.effects,
      isSequential: () => spec.order === 'importance' || spec.order === 'drawing_order',
      isParallel: () => spec.order === 'simultaneous' || spec.order === 'parallel_groups',
      hasNarration: () => spec.narration === true,
      
      // Generate beat sequence for this strategy
      generateBeats: (filledForm) => this.generateBeats(strategy, spec, filledForm),
    };
  }
  
  /**
   * Generate animation beats from strategy and content
   */
  generateBeats(strategy, spec, filledForm) {
    const beats = [];
    const slots = filledForm?.slots || {};
    const slotNames = Object.keys(slots);
    
    switch (spec.order) {
      case 'importance':
        // Sort by importance, animate in order
        const sortedByImportance = slotNames.sort((a, b) => {
          const impA = slots[a].content?.properties?.importance === 'high' ? 0 : 1;
          const impB = slots[b].content?.properties?.importance === 'high' ? 0 : 1;
          return impA - impB;
        });
        
        sortedByImportance.forEach((slotName, i) => {
          beats.push({
            id: `beat_${i}`,
            slotName,
            delay: i * (spec.timing.stagger || 400),
            duration: spec.timing.duration || 500,
            effect: spec.effects[0] || 'fade_in',
          });
        });
        break;
      
      case 'parallel_groups':
        // Group left/right, animate together
        beats.push({
          id: 'beat_parallel',
          slots: slotNames,
          delay: 0,
          duration: spec.timing.duration || 700,
          effect: 'parallel',
        });
        break;
      
      case 'causal':
        // Cause first, then effect
        const causeSlots = slotNames.filter(n => n.includes('cause') || n.includes('left'));
        const effectSlots = slotNames.filter(n => n.includes('effect') || n.includes('right'));
        
        beats.push({
          id: 'beat_cause',
          slots: causeSlots.length > 0 ? causeSlots : [slotNames[0]],
          delay: 0,
          duration: spec.timing.causeDuration || 800,
          effect: 'draw',
        });
        
        beats.push({
          id: 'beat_pause',
          type: 'pause',
          delay: spec.timing.causeDuration || 800,
          duration: spec.timing.pauseDuration || 600,
        });
        
        beats.push({
          id: 'beat_effect',
          slots: effectSlots.length > 0 ? effectSlots : [slotNames[slotNames.length - 1]],
          delay: (spec.timing.causeDuration || 800) + (spec.timing.pauseDuration || 600),
          duration: spec.timing.effectDuration || 800,
          effect: 'grow',
        });
        break;
      
      case 'narrative':
        // Story beats with pauses
        slotNames.forEach((slotName, i) => {
          beats.push({
            id: `beat_${i}`,
            slotName,
            delay: i * ((spec.timing.beatDuration || 1200) + (spec.timing.pauseBetween || 500)),
            duration: spec.timing.beatDuration || 1200,
            effect: spec.effects[i % spec.effects.length] || 'fade_in',
            narration: slots[slotName].content?.properties?.label || slotName,
          });
        });
        break;
      
      case 'alternating':
        // Flash between groups
        beats.push({
          id: 'beat_flash',
          type: 'flash',
          groups: ['left', 'right'],
          flashCount: spec.timing.flashCount || 2,
          flashDuration: spec.timing.flashDuration || 1000,
          finalHold: spec.timing.finalHold || 2000,
        });
        break;
      
      default:
        // Default: sequential
        slotNames.forEach((slotName, i) => {
          beats.push({
            id: `beat_${i}`,
            slotName,
            delay: i * 400,
            duration: 500,
            effect: 'fade_in',
          });
        });
    }
    
    return beats;
  }
}

// ============================================
// EXPORTS
// ============================================

export function createAnimationDirector(options) {
  return new AnimationDirector(options);
}

export default AnimationDirector;

