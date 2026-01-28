/**
 * 🧬 ATOM BASE CLASS
 * ==================
 * 
 * Base class for all Visual Atoms in NETRA.
 * 
 * Atoms are NOT templates - they are behavioral, interactive,
 * physics-aware visual elements that can:
 * - Render themselves (via RendererAdapter)
 * - Update state (physics tick)
 * - Handle interactions (drag, click)
 * - Emit events (for behaviors/narration)
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
  once(event, listener) {
    const onceWrapper = (...args) => {
      listener(...args);
      this.off(event, onceWrapper);
    };
    return this.on(event, onceWrapper);
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

export class Atom {
  /**
   * @param {string} id - Unique atom ID
   * @param {Object} params - Type-specific parameters
   */
  constructor(id, params = {}) {
    this.id = id;
    this.params = { ...this.getDefaultParams(), ...params };
    this.state = this.getInitialState();
    this.events = new SimpleEventEmitter();
    
    // Position & size
    this.position = { x: 0, y: 0 };
    this.size = { width: 100, height: 100 };
    this.anchor = 'center';
    this.zIndex = 0;
    
    // Visibility & emphasis
    this.visible = true;
    this.emphasis = 'normal';
    this.opacity = 1;
    
    // Parent attachment
    this.attachedTo = null;
    this.attachAnchor = 'center';
    
    // Physics body reference (if applicable)
    this.body = null;
    
    // Animation state
    this.animating = false;
    this.animations = [];
  }

  // ============================================
  // OVERRIDE IN SUBCLASSES
  // ============================================

  /** Get default parameters for this atom type */
  getDefaultParams() {
    return {};
  }

  /** Get initial state */
  getInitialState() {
    return {};
  }

  /** Get atom type name */
  static get type() {
    return 'Atom';
  }

  /** Get parameter schema for validation */
  static getParamSchema() {
    return {};
  }

  // ============================================
  // LIFECYCLE METHODS
  // ============================================

  /**
   * Called when atom is added to scene
   * @param {Object} scene - Scene reference
   */
  onMount(scene) {
    this.scene = scene;
    this.emit('mounted');
  }

  /**
   * Called when atom is removed from scene
   */
  onUnmount() {
    this.emit('unmounted');
    this.events.removeAllListeners();
    this.scene = null;
  }

  /**
   * Update tick (called every frame)
   * @param {number} dt - Delta time in ms
   */
  update(dt) {
    // Process animations
    this.processAnimations(dt);
    
    // Sync with physics body if exists
    if (this.body) {
      this.syncFromPhysicsBody();
    }
  }

  /**
   * Render the atom
   * @param {Object} renderer - RendererAdapter instance
   */
  render(renderer) {
    if (!this.visible) return;
    // Override in subclasses
  }

  // ============================================
  // POSITION & ATTACHMENT
  // ============================================

  /**
   * Set position
   */
  setPosition(x, y) {
    const oldPos = { ...this.position };
    this.position = { x, y };
    
    if (this.body) {
      this.syncToPhysicsBody();
    }
    
    this.emit('position_changed', { old: oldPos, new: this.position });
  }

  /**
   * Get computed position (accounting for attachment)
   */
  getComputedPosition() {
    if (this.attachedTo && this.scene) {
      const parent = this.scene.getAtom(this.attachedTo);
      if (parent) {
        const parentPos = parent.getComputedPosition();
        const anchorOffset = this.getAnchorOffset(parent, this.attachAnchor);
        return {
          x: parentPos.x + anchorOffset.x + this.position.x,
          y: parentPos.y + anchorOffset.y + this.position.y
        };
      }
    }
    return { ...this.position };
  }

  /**
   * Get anchor offset for attachment point
   */
  getAnchorOffset(parent, anchor) {
    const w = parent.size.width / 2;
    const h = parent.size.height / 2;
    
    const offsets = {
      'center': { x: 0, y: 0 },
      'top-left': { x: -w, y: -h },
      'top-center': { x: 0, y: -h },
      'top-right': { x: w, y: -h },
      'left-center': { x: -w, y: 0 },
      'right-center': { x: w, y: 0 },
      'bottom-left': { x: -w, y: h },
      'bottom-center': { x: 0, y: h },
      'bottom-right': { x: w, y: h }
    };
    
    return offsets[anchor] || offsets['center'];
  }

  // ============================================
  // STATE MANAGEMENT
  // ============================================

  /**
   * Update state
   */
  setState(updates) {
    const oldState = { ...this.state };
    this.state = { ...this.state, ...updates };
    this.emit('state_changed', { old: oldState, new: this.state, changes: updates });
  }

  /**
   * Get current state
   */
  getState() {
    return { ...this.state };
  }

  // ============================================
  // VISIBILITY & EMPHASIS
  // ============================================

  show() {
    if (!this.visible) {
      this.visible = true;
      this.emit('shown');
    }
  }

  hide() {
    if (this.visible) {
      this.visible = false;
      this.emit('hidden');
    }
  }

  setEmphasis(level) {
    this.emphasis = level;
    this.emit('emphasis_changed', level);
  }

  highlight(duration = 1000) {
    this.emit('highlight_start');
    setTimeout(() => this.emit('highlight_end'), duration);
  }

  // ============================================
  // ANIMATION
  // ============================================

  /**
   * Add animation
   */
  animate(property, target, duration, easing = 'easeOutQuad') {
    const startValue = this.getAnimatableValue(property);
    
    this.animations.push({
      property,
      startValue,
      targetValue: target,
      duration,
      elapsed: 0,
      easing
    });
    
    this.animating = true;
    this.emit('animation_start', { property, target });
  }

  /**
   * Process active animations
   */
  processAnimations(dt) {
    if (this.animations.length === 0) {
      this.animating = false;
      return;
    }

    const completed = [];

    for (const anim of this.animations) {
      anim.elapsed += dt;
      const progress = Math.min(anim.elapsed / anim.duration, 1);
      const easedProgress = this.ease(progress, anim.easing);
      
      const currentValue = this.interpolate(
        anim.startValue,
        anim.targetValue,
        easedProgress
      );
      
      this.setAnimatableValue(anim.property, currentValue);
      
      if (progress >= 1) {
        completed.push(anim);
        this.emit('animation_complete', { property: anim.property });
      }
    }

    this.animations = this.animations.filter(a => !completed.includes(a));
  }

  getAnimatableValue(property) {
    if (property === 'x') return this.position.x;
    if (property === 'y') return this.position.y;
    if (property === 'opacity') return this.opacity;
    return this.state[property] ?? 0;
  }

  setAnimatableValue(property, value) {
    if (property === 'x') this.position.x = value;
    else if (property === 'y') this.position.y = value;
    else if (property === 'opacity') this.opacity = value;
    else this.state[property] = value;
  }

  interpolate(start, end, t) {
    if (typeof start === 'number') {
      return start + (end - start) * t;
    }
    return t >= 1 ? end : start;
  }

  ease(t, type) {
    switch (type) {
      case 'linear': return t;
      case 'easeInQuad': return t * t;
      case 'easeOutQuad': return t * (2 - t);
      case 'easeInOutQuad': return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
      case 'easeOutElastic': {
        const p = 0.3;
        return Math.pow(2, -10 * t) * Math.sin((t - p / 4) * (2 * Math.PI) / p) + 1;
      }
      default: return t * (2 - t);
    }
  }

  // ============================================
  // PHYSICS SYNC
  // ============================================

  syncFromPhysicsBody() {
    if (this.body) {
      this.position.x = this.body.position.x;
      this.position.y = this.body.position.y;
    }
  }

  syncToPhysicsBody() {
    // Override in physics-enabled atoms
  }

  // ============================================
  // INTERACTION
  // ============================================

  /**
   * Handle interaction event
   */
  onInteract(type, data) {
    this.emit(`interact_${type}`, data);
    this.emit('interact', { type, data });
  }

  /**
   * Check if point is inside atom bounds
   */
  containsPoint(x, y) {
    const pos = this.getComputedPosition();
    const hw = this.size.width / 2;
    const hh = this.size.height / 2;
    
    return x >= pos.x - hw && x <= pos.x + hw &&
           y >= pos.y - hh && y <= pos.y + hh;
  }

  // ============================================
  // EVENTS
  // ============================================

  emit(event, data) {
    this.events.emit(event, { atomId: this.id, ...data });
  }

  on(event, handler) {
    this.events.on(event, handler);
  }

  off(event, handler) {
    this.events.off(event, handler);
  }

  once(event, handler) {
    this.events.once(event, handler);
  }
}

export default Atom;
