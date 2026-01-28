/**
 * 🎙️ NARRATION ENGINE
 * ====================
 * 
 * Event-driven narration synchronized with visual state.
 * 
 * Narration cues are triggered by atom events, NOT fixed timestamps.
 * This ensures perfect 1:1 sync between what's shown and what's explained.
 */

// Simple EventEmitter implementation (no external dependency)
class SimpleEventEmitter {
  constructor() {
    this._events = {};
  }
  on(event, listener) {
    if (!this._events[event]) this._events[event] = [];
    this._events[event].push(listener);
    return this;
  }
  off(event, listener) {
    if (!this._events[event]) return this;
    if (listener) {
      this._events[event] = this._events[event].filter(l => l !== listener);
    } else {
      delete this._events[event];
    }
    return this;
  }
  emit(event, ...args) {
    if (!this._events[event]) return false;
    this._events[event].forEach(listener => listener(...args));
    return true;
  }
  removeAllListeners(event) {
    if (event) {
      delete this._events[event];
    } else {
      this._events = {};
    }
    return this;
  }
}

export class NarrationEngine {
  constructor() {
    this.events = new SimpleEventEmitter();
    this.cues = [];
    this.behaviorEngine = null;
    this.firedCues = new Set();
    this.currentCue = null;
    this.cueTimeout = null;
    this.queue = [];
    this.isPlaying = false;
  }

  /**
   * Initialize with composition spec narration
   */
  initialize(narrationCues, behaviorEngine) {
    this.cues = narrationCues || [];
    this.behaviorEngine = behaviorEngine;
    this.firedCues.clear();
    this.queue = [];
    this.currentCue = null;

    // Subscribe to behavior engine events
    if (behaviorEngine) {
      behaviorEngine.on('atom_event', (data) => {
        this.checkCues({ type: 'event', source: data.atomId, event: data.event });
      });

      behaviorEngine.on('action_executed', (data) => {
        // Also check after actions execute
        this.checkCues({ type: 'event', source: 'behavior', event: 'action_executed' });
      });
    }

    console.log(`[NarrationEngine] Initialized with ${this.cues.length} cues`);
  }

  /**
   * Check and queue matching cues
   */
  checkCues(triggerContext) {
    for (const cue of this.cues) {
      if (this.firedCues.has(cue.id)) continue;

      if (this.matchesTrigger(cue.trigger, triggerContext)) {
        this.queueCue(cue);
        this.firedCues.add(cue.id);
      }
    }
  }

  /**
   * Match trigger (reuses logic from BehaviorEngine)
   */
  matchesTrigger(trigger, context) {
    // Special handling for scene_ready
    if (trigger.type === 'scene_ready') {
      return context.type === 'event' && context.source === 'scene' && context.event === 'ready';
    }

    if (trigger.type !== context.type) return false;
    if (trigger.source && trigger.source !== context.source) return false;
    if (trigger.event && trigger.event !== context.event) return false;

    return true;
  }

  /**
   * Queue a cue for display
   */
  queueCue(cue) {
    const delay = cue.trigger.delay || 0;

    if (delay > 0) {
      setTimeout(() => this.addToQueue(cue), delay);
    } else {
      this.addToQueue(cue);
    }
  }

  /**
   * Add to queue and process
   */
  addToQueue(cue) {
    this.queue.push(cue);
    
    if (!this.isPlaying) {
      this.processQueue();
    }
  }

  /**
   * Process cue queue
   */
  processQueue() {
    if (this.queue.length === 0) {
      this.isPlaying = false;
      this.currentCue = null;
      this.events.emit('narration_idle');
      return;
    }

    this.isPlaying = true;
    const cue = this.queue.shift();
    this.showCue(cue);
  }

  /**
   * Show narration cue
   */
  showCue(cue) {
    // Clear existing timeout
    if (this.cueTimeout) {
      clearTimeout(this.cueTimeout);
    }

    this.currentCue = cue;
    const duration = cue.duration || 3000;

    // Emit events
    this.events.emit('narration_start', {
      id: cue.id,
      text: cue.text,
      emphasis: cue.emphasis || 'normal',
      highlightAtoms: cue.highlightAtoms || [],
      duration
    });

    console.log(`[NarrationEngine] "${cue.text.substring(0, 50)}..."`);

    // Schedule end
    this.cueTimeout = setTimeout(() => {
      this.events.emit('narration_end', { id: cue.id });
      this.processQueue();
    }, duration);
  }

  /**
   * Manually trigger scene ready
   */
  triggerSceneReady() {
    this.checkCues({ type: 'event', source: 'scene', event: 'ready' });
  }

  /**
   * Skip current narration
   */
  skip() {
    if (this.cueTimeout) {
      clearTimeout(this.cueTimeout);
    }
    if (this.currentCue) {
      this.events.emit('narration_end', { id: this.currentCue.id });
    }
    this.processQueue();
  }

  /**
   * Get current narration text
   */
  getCurrentText() {
    return this.currentCue?.text || null;
  }

  /**
   * Get current emphasis
   */
  getCurrentEmphasis() {
    return this.currentCue?.emphasis || 'normal';
  }

  /**
   * Subscribe to narration events
   */
  on(event, handler) {
    this.events.on(event, handler);
  }

  off(event, handler) {
    this.events.off(event, handler);
  }

  /**
   * Cleanup
   */
  destroy() {
    if (this.cueTimeout) {
      clearTimeout(this.cueTimeout);
    }
    this.events.removeAllListeners();
    this.cues = [];
    this.queue = [];
    this.firedCues.clear();
  }
}

export function createNarrationEngine() {
  return new NarrationEngine();
}

export default NarrationEngine;
