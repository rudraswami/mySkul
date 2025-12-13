/**
 * 🎬 NARRATIVE ENGINE
 * ===================
 * 
 * 5-Beat Teaching System - The Conductor
 * 
 * Orchestrates the complete teaching experience:
 * - Coordinates hand movement
 * - Triggers text bubbles
 * - Controls drawing sequences
 * - Manages beat transitions
 * - Synchronizes all animations
 * 
 * This is the HEART of the Magic Notebook teaching flow.
 */

import { generateHandTimeline, getHandStateAtTime } from './HandMotionPath';
import { TIMING } from '../sketch/RevealSequenceEngine';

// ============================================
// 5-BEAT STRUCTURE
// ============================================

/**
 * The 5 teaching beats (from PRD)
 */
export const BEATS = {
  SETUP: 1,           // "Let me show you..."
  CONCEPT: 2,         // Draw main idea
  CONNECTION: 3,      // "See how this relates..."
  INSIGHT: 4,         // "The key insight is..."
  MEMORY_HOOK: 5,     // "Now you'll never forget!"
};

/**
 * Default beat timings (in seconds)
 */
export const BEAT_TIMINGS = {
  [BEATS.SETUP]: 2,           // 0-2s
  [BEATS.CONCEPT]: 2,         // 2-4s
  [BEATS.CONNECTION]: 2,      // 4-6s
  [BEATS.INSIGHT]: 2,         // 6-8s
  [BEATS.MEMORY_HOOK]: 2,     // 8-10s
};

/**
 * Beat phases
 */
export const BEAT_PHASES = {
  INTRO: 'intro',             // Beat text appears
  DRAWING: 'drawing',         // Elements draw
  HIGHLIGHT: 'highlight',     // Key elements emphasized
  PAUSE: 'pause',            // Moment to absorb
  TRANSITION: 'transition',   // Move to next beat
};

// ============================================
// NARRATIVE ENGINE CLASS
// ============================================

export class NarrativeEngine {
  constructor(blueprint, options = {}) {
    this.blueprint = blueprint;
    this.options = {
      speed: 1.0,                    // Playback speed multiplier
      enableHand: true,              // Show drawing hand
      enableBubbles: true,           // Show text bubbles
      autoAdvance: true,             // Auto-advance beats
      pauseDuration: 0.5,            // Pause between beats
      ...options,
    };
    
    this.currentBeat = 0;
    this.currentTime = 0;
    this.isPlaying = false;
    this.isPaused = false;
    
    // Callbacks
    this.onBeatChange = options.onBeatChange || null;
    this.onPhaseChange = options.onPhaseChange || null;
    this.onComplete = options.onComplete || null;
    
    // Generate timelines
    this.generateTimelines();
  }
  
  /**
   * Generate animation timelines from blueprint
   */
  generateTimelines() {
    const beats = this.blueprint.beats || this.generateDefaultBeats();
    
    this.beatTimeline = [];
    let cumulativeTime = 0;
    
    beats.forEach((beat, index) => {
      const beatNumber = beat.beat || (index + 1);
      const duration = (beat.duration || BEAT_TIMINGS[beatNumber]) / this.options.speed;
      
      this.beatTimeline.push({
        beat: beatNumber,
        startTime: cumulativeTime,
        endTime: cumulativeTime + duration,
        duration,
        text: beat.text,
        drawItems: beat.drawItems || [],
        highlightItems: beat.highlightItems || [],
        pause: beat.pause || false,
      });
      
      cumulativeTime += duration;
      
      // Add pause if specified
      if (beat.pause) {
        cumulativeTime += this.options.pauseDuration / this.options.speed;
      }
    });
    
    this.totalDuration = cumulativeTime;
    
    // Generate hand timeline if enabled
    if (this.options.enableHand) {
      const waypoints = this.extractWaypoints();
      this.handTimeline = generateHandTimeline(waypoints, 1.5 / this.options.speed);
    }
  }
  
  /**
   * Generate default beats if none provided
   */
  generateDefaultBeats() {
    const concept = this.blueprint.concept || 'Concept';
    
    return [
      {
        beat: BEATS.SETUP,
        text: `Let me show you ${concept}...`,
        drawItems: [],
        duration: 2,
      },
      {
        beat: BEATS.CONCEPT,
        text: 'Here\'s the main idea:',
        drawItems: this.blueprint.items?.slice(0, 1).map(i => i.id) || [],
        duration: 2,
      },
      {
        beat: BEATS.CONNECTION,
        text: 'See how this connects...',
        drawItems: this.blueprint.items?.slice(1).map(i => i.id) || [],
        duration: 2,
      },
      {
        beat: BEATS.INSIGHT,
        text: 'The key insight is:',
        highlightItems: this.blueprint.highlights || [],
        pause: true,
        duration: 2,
      },
      {
        beat: BEATS.MEMORY_HOOK,
        text: 'Now you\'ll never forget! 💪',
        duration: 2,
      },
    ];
  }
  
  /**
   * Extract waypoints for hand movement from blueprint
   */
  extractWaypoints() {
    if (!this.blueprint.items) return [];
    
    return this.blueprint.items
      .filter(item => item.position)
      .map((item, index) => ({
        x: item.position.x,
        y: item.position.y,
        delay: index * 0.5,
        itemId: item.id,
      }));
  }
  
  /**
   * Get current beat data
   */
  getCurrentBeat() {
    return this.beatTimeline.find(
      beat => this.currentTime >= beat.startTime && this.currentTime < beat.endTime
    ) || null;
  }
  
  /**
   * Get current beat phase
   */
  getCurrentPhase() {
    const beat = this.getCurrentBeat();
    if (!beat) return null;
    
    const beatProgress = (this.currentTime - beat.startTime) / beat.duration;
    
    if (beatProgress < 0.1) return BEAT_PHASES.INTRO;
    if (beatProgress < 0.6) return BEAT_PHASES.DRAWING;
    if (beatProgress < 0.8) return BEAT_PHASES.HIGHLIGHT;
    if (beatProgress < 0.95) return BEAT_PHASES.PAUSE;
    return BEAT_PHASES.TRANSITION;
  }
  
  /**
   * Get hand state at current time
   */
  getHandState() {
    if (!this.options.enableHand || !this.handTimeline) {
      return { x: 0, y: 0, angle: 0, pose: 'idle', visible: false };
    }
    
    return {
      ...getHandStateAtTime(this.handTimeline, this.currentTime),
      visible: true,
    };
  }
  
  /**
   * Get text bubble state at current time
   */
  getBubbleState() {
    if (!this.options.enableBubbles) {
      return { text: '', visible: false };
    }
    
    const beat = this.getCurrentBeat();
    if (!beat) {
      return { text: '', visible: false };
    }
    
    const phase = this.getCurrentPhase();
    
    return {
      text: beat.text,
      visible: phase === BEAT_PHASES.INTRO || phase === BEAT_PHASES.DRAWING,
      type: this.getBubbleType(beat.beat),
    };
  }
  
  /**
   * Get bubble type based on beat
   */
  getBubbleType(beatNumber) {
    switch (beatNumber) {
      case BEATS.SETUP:
        return 'hint';
      case BEATS.CONCEPT:
      case BEATS.CONNECTION:
        return 'insight';
      case BEATS.INSIGHT:
        return 'highlight';
      case BEATS.MEMORY_HOOK:
        return 'memory';
      default:
        return 'hint';
    }
  }
  
  /**
   * Get items to draw at current time
   */
  getDrawItems() {
    const beat = this.getCurrentBeat();
    if (!beat) return [];
    
    return beat.drawItems || [];
  }
  
  /**
   * Get items to highlight at current time
   */
  getHighlightItems() {
    const beat = this.getCurrentBeat();
    if (!beat) return [];
    
    const phase = this.getCurrentPhase();
    
    if (phase === BEAT_PHASES.HIGHLIGHT || phase === BEAT_PHASES.PAUSE) {
      return beat.highlightItems || [];
    }
    
    return [];
  }
  
  /**
   * Play narrative
   */
  play() {
    this.isPlaying = true;
    this.isPaused = false;
  }
  
  /**
   * Pause narrative
   */
  pause() {
    this.isPlaying = false;
    this.isPaused = true;
  }
  
  /**
   * Stop and reset narrative
   */
  stop() {
    this.isPlaying = false;
    this.isPaused = false;
    this.currentTime = 0;
    this.currentBeat = 0;
  }
  
  /**
   * Seek to specific time
   */
  seekTo(time) {
    this.currentTime = Math.max(0, Math.min(time, this.totalDuration));
    
    const beat = this.getCurrentBeat();
    if (beat && beat.beat !== this.currentBeat) {
      this.currentBeat = beat.beat;
      this.onBeatChange?.(this.currentBeat, beat);
    }
  }
  
  /**
   * Skip to next beat
   */
  nextBeat() {
    const currentBeat = this.getCurrentBeat();
    if (!currentBeat) return;
    
    const nextBeatData = this.beatTimeline.find(b => b.beat > currentBeat.beat);
    if (nextBeatData) {
      this.seekTo(nextBeatData.startTime);
    }
  }
  
  /**
   * Skip to previous beat
   */
  previousBeat() {
    const currentBeat = this.getCurrentBeat();
    if (!currentBeat) return;
    
    // Go to start of current beat if we're past the intro
    if (this.currentTime - currentBeat.startTime > 0.5) {
      this.seekTo(currentBeat.startTime);
      return;
    }
    
    // Otherwise go to previous beat
    const prevBeatData = [...this.beatTimeline]
      .reverse()
      .find(b => b.beat < currentBeat.beat);
    
    if (prevBeatData) {
      this.seekTo(prevBeatData.startTime);
    }
  }
  
  /**
   * Update (call this in animation loop)
   * @param {number} deltaTime - Time elapsed since last update (in seconds)
   * @returns {Object} Current state
   */
  update(deltaTime) {
    if (!this.isPlaying) {
      return this.getState();
    }
    
    // Update time
    const prevTime = this.currentTime;
    this.currentTime += deltaTime;
    
    // Check if beat changed
    const prevBeat = this.getCurrentBeat();
    const newBeat = this.beatTimeline.find(
      beat => this.currentTime >= beat.startTime && this.currentTime < beat.endTime
    );
    
    if (newBeat && (!prevBeat || newBeat.beat !== prevBeat.beat)) {
      this.currentBeat = newBeat.beat;
      this.onBeatChange?.(this.currentBeat, newBeat);
    }
    
    // Check if phase changed
    const phase = this.getCurrentPhase();
    this.onPhaseChange?.(phase);
    
    // Check if complete
    if (this.currentTime >= this.totalDuration) {
      this.isPlaying = false;
      this.onComplete?.();
    }
    
    return this.getState();
  }
  
  /**
   * Get complete current state
   */
  getState() {
    return {
      currentTime: this.currentTime,
      totalDuration: this.totalDuration,
      progress: this.currentTime / this.totalDuration,
      currentBeat: this.currentBeat,
      beatData: this.getCurrentBeat(),
      phase: this.getCurrentPhase(),
      hand: this.getHandState(),
      bubble: this.getBubbleState(),
      drawItems: this.getDrawItems(),
      highlightItems: this.getHighlightItems(),
      isPlaying: this.isPlaying,
      isPaused: this.isPaused,
      isComplete: this.currentTime >= this.totalDuration,
    };
  }
  
  /**
   * Set playback speed
   */
  setSpeed(speed) {
    this.options.speed = Math.max(0.25, Math.min(2, speed));
    this.generateTimelines(); // Regenerate with new speed
  }
  
  /**
   * Get total beats
   */
  getTotalBeats() {
    return this.beatTimeline.length;
  }
}

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Create a narrative engine from blueprint
 */
export function createNarrativeEngine(blueprint, options) {
  return new NarrativeEngine(blueprint, options);
}

/**
 * Validate beat structure
 */
export function validateBeats(beats) {
  const errors = [];
  
  if (!Array.isArray(beats)) {
    errors.push('Beats must be an array');
    return { valid: false, errors };
  }
  
  beats.forEach((beat, i) => {
    if (typeof beat.beat !== 'number') {
      errors.push(`Beat ${i}: 'beat' must be a number`);
    }
    if (!beat.text) {
      errors.push(`Beat ${i}: 'text' is required`);
    }
  });
  
  return {
    valid: errors.length === 0,
    errors,
  };
}

// ============================================
// EXPORTS
// ============================================

export default NarrativeEngine;

