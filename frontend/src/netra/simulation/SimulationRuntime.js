/**
 * 🎬 SIMULATION RUNTIME
 * =====================
 * 
 * Continuous tick loop that runs the simulation.
 * - Executes rules each frame
 * - Updates entity states
 * - Emits events for narration sync
 * - Maintains 60fps target
 */

import { RuleEngine } from './RuleInterpreter';
import { createEntityFromTemplate } from './EntityTemplates';
import { computeLayout, applyLayout } from './OntologyLayoutEngine';
import { getPalette, getBackgroundGradient } from './DomainPalettes';

// Event emitter for simulation events
class EventEmitter {
  constructor() {
    this.listeners = new Map();
  }
  
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }
  
  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) callbacks.splice(index, 1);
    }
  }
  
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(cb => cb(data));
    }
  }
  
  removeAllListeners() {
    this.listeners.clear();
  }
}

/**
 * Main simulation runtime
 */
export class SimulationRuntime {
  constructor(script, options = {}) {
    this.script = script;
    this.options = {
      stageWidth: options.width || 800,
      stageHeight: options.height || 600,
      targetFPS: options.targetFPS || 60,
      ...options
    };
    
    // State
    this.entities = new Map();
    this.state = {
      current: script.state?.initial || 'idle',
      variables: { ...script.state?.variables } || {},
      dt: 0
    };
    this.constants = this.resolveConstants(script.constants || {});
    
    // Engines
    this.ruleEngine = new RuleEngine();
    this.events = new EventEmitter();
    
    // Runtime state
    this.running = false;
    this.lastFrameTime = 0;
    this.frameCount = 0;
    this.animationFrameId = null;
    
    // Domain
    this.domain = script._meta?.domain || 'general';
    this.palette = getPalette(this.domain);
    this.backgroundGradient = getBackgroundGradient(this.domain);
  }
  
  /**
   * Resolve constants from script (handles {value, unit, editable} format)
   */
  resolveConstants(constantsDef) {
    const resolved = {};
    for (const [key, def] of Object.entries(constantsDef)) {
      if (typeof def === 'object' && def.value !== undefined) {
        resolved[key] = def.value;
      } else {
        resolved[key] = def;
      }
    }
    return resolved;
  }
  
  /**
   * Initialize the simulation
   */
  initialize() {
    console.log('[SimulationRuntime] Initializing...');
    
    // Create entities from templates
    const scriptEntities = this.script.entities || [];
    scriptEntities.forEach(entityDef => {
      const entity = createEntityFromTemplate(entityDef, this.domain);
      this.entities.set(entity.id, entity);
    });
    
    // Compute layout
    const layout = computeLayout(this.script, {
      width: this.options.stageWidth,
      height: this.options.stageHeight
    });
    
    // Apply layout to entities
    for (const [id, position] of Object.entries(layout)) {
      const entity = this.entities.get(id);
      if (entity) {
        entity.position = position;
      }
    }
    
    // Load rules
    this.ruleEngine.loadRules(this.script.rules || []);
    
    console.log(`[SimulationRuntime] Initialized with ${this.entities.size} entities, ${this.script.rules?.length || 0} rules`);
    
    // Emit start event
    this.events.emit('initialized', {
      entityCount: this.entities.size,
      ruleCount: this.script.rules?.length || 0,
      state: this.state.current
    });
    
    return this;
  }
  
  /**
   * Start the simulation tick loop
   */
  start() {
    if (this.running) return;
    
    this.running = true;
    this.lastFrameTime = performance.now();
    this.frameCount = 0;
    
    console.log('[SimulationRuntime] Started');
    
    // Emit start event
    this.events.emit('start', { state: this.state.current });
    
    // Start render loop
    this.tick();
  }
  
  /**
   * Main tick function (called each frame)
   */
  tick = () => {
    if (!this.running) return;
    
    const now = performance.now();
    const dt = (now - this.lastFrameTime) / 1000;  // Convert to seconds
    this.lastFrameTime = now;
    this.frameCount++;
    
    // Update state delta time
    this.state.dt = dt;
    
    // Execute rules
    const ruleResults = this.ruleEngine.tick(this.state, this.constants, this);
    
    // Emit tick event with results
    this.events.emit('tick', {
      frameCount: this.frameCount,
      dt,
      state: this.state.current,
      variables: { ...this.state.variables },
      ruleResults
    });
    
    // Update entity animations
    this.updateEntities(dt);
    
    // Schedule next frame
    this.animationFrameId = requestAnimationFrame(this.tick);
  }
  
  /**
   * Update entity animations and physics
   */
  updateEntities(dt) {
    for (const entity of this.entities.values()) {
      // Update animations
      if (entity.animation) {
        this.updateEntityAnimation(entity, dt);
      }
      
      // Update idle animations
      if (entity.idleAnimation) {
        this.updateIdleAnimation(entity, dt);
      }
    }
  }
  
  /**
   * Update entity active animation
   */
  updateEntityAnimation(entity, dt) {
    const anim = entity.animation;
    anim.elapsed += dt * 1000;  // Convert to ms
    
    const progress = Math.min(anim.elapsed / anim.duration, 1);
    const eased = this.easeOutCubic(progress);
    
    // Interpolate value
    const current = anim.from + (anim.to - anim.from) * eased;
    
    // Apply to state
    entity.state[anim.property] = current;
    
    // Check if complete
    if (progress >= 1) {
      entity.animation = null;
      this.events.emit('animation_complete', { entityId: entity.id, property: anim.property });
    }
  }
  
  /**
   * Update entity idle animation
   */
  updateIdleAnimation(entity, dt) {
    // Idle animations are continuous
    entity.idlePhase = (entity.idlePhase || 0) + dt;
    
    switch (entity.idleAnimation) {
      case 'subtle_float':
        entity.idleOffset = Math.sin(entity.idlePhase * 2) * 3;
        break;
      case 'glow_pulse':
        entity.glowIntensity = 0.5 + Math.sin(entity.idlePhase * 3) * 0.3;
        break;
      case 'breathe':
        entity.breatheScale = 1 + Math.sin(entity.idlePhase * 1.5) * 0.02;
        break;
      case 'pulse_subtle':
        entity.pulseScale = 1 + Math.sin(entity.idlePhase * 4) * 0.1;
        break;
    }
  }
  
  /**
   * Easing function (ease out cubic)
   */
  easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }
  
  /**
   * Stop the simulation
   */
  stop() {
    this.running = false;
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
    
    console.log('[SimulationRuntime] Stopped');
    this.events.emit('stop', { frameCount: this.frameCount });
  }
  
  /**
   * Pause the simulation (can be resumed)
   */
  pause() {
    this.running = false;
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
    this.events.emit('pause', {});
  }
  
  /**
   * Resume a paused simulation
   */
  resume() {
    if (!this.running) {
      this.running = true;
      this.lastFrameTime = performance.now();
      this.tick();
      this.events.emit('resume', {});
    }
  }
  
  /**
   * Reset simulation to initial state
   */
  reset() {
    this.stop();
    
    // Reset state
    this.state = {
      current: this.script.state?.initial || 'idle',
      variables: { ...this.script.state?.variables } || {},
      dt: 0
    };
    
    // Reset entities
    for (const entity of this.entities.values()) {
      entity.state = {
        visible: true,
        opacity: 1,
        scale: 1,
        rotation: 0,
        highlighted: false
      };
      entity.animation = null;
    }
    
    // Reset rules
    this.ruleEngine.reset();
    
    this.events.emit('reset', {});
  }
  
  // ============================================
  // RUNTIME COMMANDS (called by rules)
  // ============================================
  
  emit(event, data) {
    this.events.emit(event, data);
  }
  
  showEntity(entityId) {
    const entity = this.entities.get(entityId);
    if (entity) {
      entity.state.visible = true;
      entity.animation = { property: 'opacity', from: 0, to: 1, duration: 300, elapsed: 0 };
    }
  }
  
  hideEntity(entityId) {
    const entity = this.entities.get(entityId);
    if (entity) {
      entity.animation = { property: 'opacity', from: 1, to: 0, duration: 300, elapsed: 0 };
      setTimeout(() => {
        entity.state.visible = false;
      }, 300);
    }
  }
  
  highlightEntity(entityId) {
    const entity = this.entities.get(entityId);
    if (entity) {
      entity.state.highlighted = true;
      entity.glowIntensity = 1;
    }
  }
  
  unhighlightEntity(entityId) {
    const entity = this.entities.get(entityId);
    if (entity) {
      entity.state.highlighted = false;
      entity.glowIntensity = 0;
    }
  }
  
  moveEntity(entityId, dx, dy) {
    const entity = this.entities.get(entityId);
    if (entity) {
      entity.position.x += dx;
      entity.position.y += dy;
    }
  }
  
  animateEntity(entityId, property, to, duration = 500) {
    const entity = this.entities.get(entityId);
    if (entity) {
      const from = entity.state[property] || 0;
      entity.animation = { property, from, to, duration, elapsed: 0 };
    }
  }
  
  /**
   * Update a constant (from user interaction)
   */
  setConstant(name, value) {
    this.constants[name] = value;
    this.events.emit('constant_changed', { name, value });
  }
  
  /**
   * Get current state for rendering
   */
  getRenderState() {
    return {
      entities: Array.from(this.entities.values()),
      state: this.state,
      constants: this.constants,
      palette: this.palette,
      backgroundGradient: this.backgroundGradient,
      running: this.running
    };
  }
  
  /**
   * Cleanup
   */
  destroy() {
    this.stop();
    this.events.removeAllListeners();
    this.entities.clear();
  }
}

/**
 * Create a simulation runtime from a SimulationScript
 */
export function createSimulationRuntime(script, options = {}) {
  const runtime = new SimulationRuntime(script, options);
  return runtime.initialize();
}

export default SimulationRuntime;
