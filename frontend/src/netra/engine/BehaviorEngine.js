/**
 * 🎮 BEHAVIOR ENGINE
 * ==================
 * 
 * Event-driven behavior system for NETRA compositions.
 * 
 * Wires triggers to actions based on CompositionSpec behaviors.
 * Listens to atom events, state changes, and user interactions.
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

export class BehaviorEngine {
  constructor() {
    this.events = new SimpleEventEmitter();
    this.rules = [];
    this.atoms = new Map();
    this.scene = null;
    this.firedOnce = new Set();
    this.timeouts = [];
    this.startTime = 0;
  }

  /**
   * Initialize with composition spec behaviors
   */
  initialize(behaviors, scene) {
    this.scene = scene;
    this.rules = behaviors || [];
    this.firedOnce.clear();
    this.startTime = Date.now();

    // Clear existing timeouts
    this.timeouts.forEach(t => clearTimeout(t));
    this.timeouts = [];

    console.log(`[BehaviorEngine] Initialized with ${this.rules.length} rules`);
  }

  /**
   * Register an atom for event listening
   */
  registerAtom(atom) {
    this.atoms.set(atom.id, atom);

    // Listen to all atom events
    atom.events.on('*', (eventName, data) => {
      this.handleAtomEvent(atom.id, eventName, data);
    });

    // Forward specific events
    const forwardEvents = [
      'mounted', 'shown', 'hidden', 'started_moving', 'stopped',
      'state_changed', 'position_changed', 'interact', 'animation_complete'
    ];

    forwardEvents.forEach(eventName => {
      atom.on(eventName, (data) => {
        this.handleAtomEvent(atom.id, eventName, data);
      });
    });
  }

  /**
   * Unregister an atom
   */
  unregisterAtom(atomId) {
    const atom = this.atoms.get(atomId);
    if (atom) {
      atom.events.removeAllListeners();
    }
    this.atoms.delete(atomId);
  }

  /**
   * Handle atom event
   */
  handleAtomEvent(atomId, eventName, data) {
    // Emit global event
    this.events.emit(`${atomId}.${eventName}`, data);
    this.events.emit('atom_event', { atomId, event: eventName, data });

    // Check rules
    this.checkRules({ type: 'event', source: atomId, event: eventName }, data);
  }

  /**
   * Handle scene event
   */
  handleSceneEvent(eventName, data) {
    this.events.emit(`scene.${eventName}`, data);
    this.checkRules({ type: 'event', source: 'scene', event: eventName }, data);
  }

  /**
   * Handle user interaction
   */
  handleInteraction(atomId, interactionType, data) {
    this.events.emit(`user.${interactionType}`, { atomId, ...data });
    this.checkRules({ type: 'interaction', source: 'user', event: interactionType, atomId }, data);
  }

  /**
   * Check and fire matching rules
   */
  checkRules(triggerContext, eventData) {
    for (const rule of this.rules) {
      if (this.matchesTrigger(rule.trigger, triggerContext)) {
        // Check once constraint
        if (rule.once && this.firedOnce.has(rule.id)) {
          continue;
        }

        // Check enabled
        if (rule.enabled === false) {
          continue;
        }

        // Apply delay if specified
        const delay = rule.trigger.delay || 0;
        
        if (delay > 0) {
          const timeout = setTimeout(() => {
            this.executeAction(rule, eventData);
          }, delay);
          this.timeouts.push(timeout);
        } else {
          this.executeAction(rule, eventData);
        }

        // Mark as fired if once
        if (rule.once) {
          this.firedOnce.add(rule.id);
        }
      }
    }
  }

  /**
   * Check if trigger matches context
   */
  matchesTrigger(trigger, context) {
    // Type match
    if (trigger.type !== context.type) {
      // Special case: scene_ready is an event type
      if (trigger.type === 'scene_ready' && context.type === 'event' && context.event === 'ready') {
        return context.source === 'scene';
      }
      return false;
    }

    // Source match (if specified)
    if (trigger.source && trigger.source !== context.source) {
      return false;
    }

    // Event match (if specified)
    if (trigger.event && trigger.event !== context.event) {
      return false;
    }

    // Time trigger
    if (trigger.type === 'time') {
      const elapsed = Date.now() - this.startTime;
      return elapsed >= trigger.time;
    }

    // State condition
    if (trigger.type === 'state' && trigger.condition) {
      return this.evaluateCondition(trigger.condition, trigger.source);
    }

    return true;
  }

  /**
   * Evaluate state condition
   */
  evaluateCondition(condition, sourceId) {
    const atom = this.atoms.get(sourceId);
    if (!atom) return false;

    const state = atom.getState();

    // Simple condition parsing: "velocity > 0", "isMoving == true"
    const match = condition.match(/(\w+)\s*(>|<|>=|<=|==|!=)\s*(.+)/);
    if (!match) return false;

    const [, prop, operator, valueStr] = match;
    const actualValue = state[prop];
    let expectedValue = valueStr.trim();

    // Parse expected value
    if (expectedValue === 'true') expectedValue = true;
    else if (expectedValue === 'false') expectedValue = false;
    else if (!isNaN(expectedValue)) expectedValue = parseFloat(expectedValue);

    switch (operator) {
      case '>': return actualValue > expectedValue;
      case '<': return actualValue < expectedValue;
      case '>=': return actualValue >= expectedValue;
      case '<=': return actualValue <= expectedValue;
      case '==': return actualValue == expectedValue;
      case '!=': return actualValue != expectedValue;
      default: return false;
    }
  }

  /**
   * Execute action
   */
  executeAction(rule, eventData) {
    const { action } = rule;
    
    // Handle multiple targets (action.targets array)
    if (action.targets && Array.isArray(action.targets)) {
      action.targets.forEach(targetId => {
        const singleAction = { ...action, target: targetId };
        this.executeSingleAction(rule, singleAction, eventData);
      });
      return;
    }
    
    this.executeSingleAction(rule, action, eventData);
  }
  
  /**
   * Execute action on a single target
   */
  executeSingleAction(rule, action, eventData) {
    // ============================================
    // VALIDATION: Block invalid/undefined actions
    // ============================================
    if (!action || !action.type) {
      console.warn(`[BehaviorEngine] ⚠️ BLOCKED: Rule ${rule?.id} has undefined action type`);
      return; // Silent skip - don't crash
    }
    
    const targetAtom = this.atoms.get(action.target);
    
    // Skip if no target atom found (except for scene-level actions)
    if (!targetAtom && action.target !== 'scene' && !action.targets) {
      console.warn(`[BehaviorEngine] ⚠️ Target atom not found: ${action.target}`);
      return;
    }

    console.log(`[BehaviorEngine] Executing: ${rule.id} → ${action.type} on ${action.target}`);

    switch (action.type) {
      case 'show':
        targetAtom?.show();
        break;

      case 'hide':
        targetAtom?.hide();
        break;

      case 'animate':
        if (targetAtom && action.params) {
          const { property, target, duration, easing } = action.params;
          targetAtom.animate(property, target, duration || 500, easing);
        }
        break;

      case 'setState':
        targetAtom?.setState(action.params || {});
        break;

      // ============================================
      // ANIMATION ACTIONS (fadeIn, scaleIn, pulse, etc.)
      // ============================================
      case 'fadeIn':
        if (targetAtom) {
          const duration = action.duration || action.params?.duration || 500;
          targetAtom.setState({ opacity: 0 });
          targetAtom.show();
          targetAtom.animate('opacity', 1, duration, 'easeOut');
        }
        break;

      case 'fadeOut':
        if (targetAtom) {
          const duration = action.duration || action.params?.duration || 500;
          targetAtom.animate('opacity', 0, duration, 'easeIn');
          setTimeout(() => targetAtom.hide(), duration);
        }
        break;

      case 'scaleIn':
        if (targetAtom) {
          const duration = action.duration || action.params?.duration || 500;
          targetAtom.setState({ scale: 0.01 });
          targetAtom.show();
          targetAtom.animate('scale', 1, duration, 'easeOutBack');
        }
        break;

      case 'scaleOut':
        if (targetAtom) {
          const duration = action.duration || action.params?.duration || 300;
          targetAtom.animate('scale', 0, duration, 'easeIn');
        }
        break;

      case 'pulse':
        if (targetAtom) {
          const duration = action.duration || action.params?.duration || 1000;
          const loop = action.loop || action.params?.loop || false;
          const pulseAnimation = () => {
            targetAtom.animate('scale', 1.15, duration / 2, 'easeInOut');
            setTimeout(() => {
              targetAtom.animate('scale', 1, duration / 2, 'easeInOut');
              if (loop) setTimeout(pulseAnimation, duration / 2);
            }, duration / 2);
          };
          pulseAnimation();
        }
        break;

      case 'drawLine':
        // For connectors - animate drawing from start to end
        if (targetAtom) {
          const duration = action.duration || action.params?.duration || 500;
          targetAtom.setState({ drawProgress: 0 });
          targetAtom.show();
          targetAtom.animate('drawProgress', 1, duration, 'easeOut');
        }
        break;

      case 'highlight':
        if (targetAtom) {
          const duration = action.duration || action.params?.duration || 300;
          targetAtom.setState({ highlighted: true });
          targetAtom.animate('glowIntensity', 1, duration, 'easeOut');
        }
        break;

      case 'unhighlight':
        if (targetAtom) {
          const duration = action.duration || action.params?.duration || 300;
          targetAtom.animate('glowIntensity', 0, duration, 'easeIn');
          setTimeout(() => targetAtom.setState({ highlighted: false }), duration);
        }
        break;

      case 'moveTo':
        if (targetAtom && action.params) {
          const { x, y, duration = 500 } = action.params;
          if (x !== undefined) targetAtom.animate('x', x, duration, 'easeInOut');
          if (y !== undefined) targetAtom.animate('y', y, duration, 'easeInOut');
        }
        break;

      case 'bounce':
        if (targetAtom) {
          const duration = action.duration || 400;
          const originalY = targetAtom.state.y || 0;
          targetAtom.animate('y', originalY - 20, duration / 2, 'easeOut');
          setTimeout(() => {
            targetAtom.animate('y', originalY, duration / 2, 'easeIn');
          }, duration / 2);
        }
        break;

      case 'shake':
        if (targetAtom) {
          const duration = action.duration || 500;
          const originalX = targetAtom.state.x || 0;
          const shakeSequence = [5, -5, 4, -4, 2, -2, 0];
          shakeSequence.forEach((offset, i) => {
            setTimeout(() => {
              targetAtom.setState({ x: originalX + offset });
            }, (duration / shakeSequence.length) * i);
          });
        }
        break;

      case 'emit':
        if (action.params?.event) {
          if (action.target === 'scene') {
            this.handleSceneEvent(action.params.event, action.params.data);
          } else {
            targetAtom?.emit(action.params.event, action.params.data);
          }
        }
        break;

      case 'applyForce':
        if (targetAtom?.applyForce && action.params) {
          targetAtom.applyForce(action.params);
        } else if (targetAtom) {
          // Simulate force with velocity animation
          const { direction = 0, magnitude = 100 } = action.params || {};
          const radians = direction * Math.PI / 180;
          const vx = Math.cos(radians) * magnitude;
          const vy = Math.sin(radians) * magnitude;
          const duration = action.params?.duration || 1000;
          targetAtom.animate('x', (targetAtom.state.x || 0) + vx, duration, 'easeOut');
          targetAtom.animate('y', (targetAtom.state.y || 0) + vy, duration, 'easeOut');
        }
        break;

      // ============================================
      // ONTOLOGY-SPECIFIC BEHAVIORS
      // ============================================
      
      // SYSTEMIC_CAUSAL: Flow particles between atoms
      case 'flowParticles':
        if (action.params) {
          const { from, to, count = 5, speed = 1000 } = action.params;
          const fromAtom = this.atoms.get(from);
          const toAtom = this.atoms.get(to);
          if (fromAtom && toAtom) {
            // Emit flow event - renderer should create particles
            this.events.emit('flow_particles', {
              from: { x: fromAtom.state.x, y: fromAtom.state.y },
              to: { x: toAtom.state.x, y: toAtom.state.y },
              count, speed
            });
            // Highlight the flow path
            fromAtom.setState({ flowing: true });
            setTimeout(() => fromAtom.setState({ flowing: false }), speed);
          }
        }
        break;

      // SYSTEMIC_CAUSAL: Chain reaction sequence
      case 'chainReaction':
        if (action.params) {
          const { atoms: atomIds = [], delays = [] } = action.params;
          atomIds.forEach((atomId, i) => {
            const atom = this.atoms.get(atomId);
            const delay = delays[i] || i * 300;
            setTimeout(() => {
              atom?.setState({ activated: true, highlighted: true });
              atom?.animate('scale', 1.2, 200, 'easeOut');
              setTimeout(() => atom?.animate('scale', 1, 200, 'easeIn'), 200);
            }, delay);
          });
        }
        break;

      // SYSTEMIC_CAUSAL: Cycle loop animation
      case 'cycleLoop':
        if (action.params) {
          const { atoms: atomIds = [], duration = 2000 } = action.params;
          const cycleStep = duration / atomIds.length;
          const runCycle = () => {
            atomIds.forEach((atomId, i) => {
              const atom = this.atoms.get(atomId);
              setTimeout(() => {
                atom?.setState({ active: true });
                atom?.animate('glowIntensity', 1, cycleStep / 2);
                setTimeout(() => {
                  atom?.setState({ active: false });
                  atom?.animate('glowIntensity', 0, cycleStep / 2);
                }, cycleStep / 2);
              }, i * cycleStep);
            });
          };
          runCycle();
          if (action.params.loop) {
            this.intervals = this.intervals || [];
            this.intervals.push(setInterval(runCycle, duration));
          }
        }
        break;

      // PHYSICAL_MECHANICAL: Collision reaction
      case 'collisionReaction':
        if (action.params) {
          const { atom1, atom2, effect = 'bounce' } = action.params;
          const a1 = this.atoms.get(atom1);
          const a2 = this.atoms.get(atom2);
          if (a1 && a2) {
            // Trigger collision effect on both
            a1?.animate('scale', 0.9, 100);
            a2?.animate('scale', 0.9, 100);
            setTimeout(() => {
              a1?.animate('scale', 1, 200, 'easeOutBack');
              a2?.animate('scale', 1, 200, 'easeOutBack');
            }, 100);
            this.events.emit('collision', { atom1, atom2, effect });
          }
        }
        break;

      // PHYSICAL_MECHANICAL: Friction drag effect
      case 'frictionDrag':
        if (targetAtom) {
          const coefficient = action.params?.coefficient || 0.3;
          const duration = action.params?.duration || 1000;
          // Simulate friction by gradually slowing/dimming the target
          targetAtom.animate('opacity', 0.7, duration, 'easeOut');
          setTimeout(() => {
            targetAtom.animate('opacity', 1, duration / 2, 'easeIn');
          }, duration);
          this.events.emit('friction_applied', { target: action.target, coefficient });
        }
        break;

      // ABSTRACT_RELATIONAL: Connect flow animation
      case 'connectFlow':
        if (action.params) {
          const { from, to, style = 'solid' } = action.params;
          // Create connector animation
          this.events.emit('connect_flow', { from, to, style });
        }
        break;

      // ABSTRACT_RELATIONAL: Compare highlight
      case 'compareHighlight':
        if (action.params) {
          const { atom1, atom2 } = action.params;
          const a1 = this.atoms.get(atom1);
          const a2 = this.atoms.get(atom2);
          // Highlight both with contrasting colors
          a1?.setState({ highlighted: true, compareMode: 'left' });
          a2?.setState({ highlighted: true, compareMode: 'right' });
        }
        break;

      // ABSTRACT_RELATIONAL: Group pulse
      case 'groupPulse':
        if (action.params?.atoms) {
          const duration = action.params.duration || 1000;
          action.params.atoms.forEach(atomId => {
            const atom = this.atoms.get(atomId);
            if (atom) {
              atom.animate('scale', 1.1, duration / 2, 'easeInOut');
              setTimeout(() => atom.animate('scale', 1, duration / 2, 'easeInOut'), duration / 2);
            }
          });
        }
        break;

      // CHRONOLOGICAL: Timeline reveal
      case 'timelineReveal':
        if (action.params) {
          const { atoms: atomIds = [], interval = 500 } = action.params;
          atomIds.forEach((atomId, i) => {
            const atom = this.atoms.get(atomId);
            setTimeout(() => {
              atom?.setState({ opacity: 0 });
              atom?.show();
              atom?.animate('opacity', 1, 300, 'easeOut');
              atom?.animate('scale', 1, 300, 'easeOutBack');
            }, i * interval);
          });
        }
        break;

      // CHRONOLOGICAL: Stage transition
      case 'stageTransition':
        if (action.params) {
          const { from, to, duration = 500 } = action.params;
          const fromAtom = this.atoms.get(from);
          const toAtom = this.atoms.get(to);
          if (fromAtom && toAtom) {
            // Fade out from, fade in to
            fromAtom.animate('opacity', 0, duration, 'easeIn');
            setTimeout(() => fromAtom.hide(), duration);
            toAtom.setState({ opacity: 0 });
            toAtom.show();
            setTimeout(() => toAtom.animate('opacity', 1, duration, 'easeOut'), duration / 2);
          }
        }
        break;

      // CHRONOLOGICAL: Evolution path animation
      case 'evolutionPath':
        if (action.params) {
          const { atom: atomId, path = [] } = action.params;
          const atom = this.atoms.get(atomId);
          if (atom && path.length > 0) {
            const stepDuration = (action.params.duration || 2000) / path.length;
            path.forEach((point, i) => {
              setTimeout(() => {
                atom.animate('x', point.x, stepDuration, 'easeInOut');
                atom.animate('y', point.y, stepDuration, 'easeInOut');
              }, i * stepDuration);
            });
          }
        }
        break;

      // Fallback for unrecognized actions - execute as generic animate if possible
      default:
        // Try to handle as a generic animation if params exist
        if (targetAtom && action.params) {
          console.log(`[BehaviorEngine] Treating unknown action "${action.type}" as generic animation`);
          const { duration = 500, ...props } = action.params;
          Object.entries(props).forEach(([prop, value]) => {
            if (typeof value === 'number') {
              targetAtom.animate(prop, value, duration);
            } else {
              targetAtom.setState({ [prop]: value });
            }
          });
        } else {
          console.warn(`[BehaviorEngine] Unknown action type: ${action.type}`);
        }
    }

    // Emit action executed event
    this.events.emit('action_executed', { rule, action, eventData });
  }

  /**
   * Start time-based triggers
   */
  startTimeTriggers() {
    this.startTime = Date.now();

    for (const rule of this.rules) {
      if (rule.trigger.type === 'time') {
        const timeout = setTimeout(() => {
          if (!rule.once || !this.firedOnce.has(rule.id)) {
            this.executeAction(rule, {});
            if (rule.once) this.firedOnce.add(rule.id);
          }
        }, rule.trigger.time + (rule.trigger.delay || 0));
        this.timeouts.push(timeout);
      }
    }
  }

  /**
   * Subscribe to behavior events
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
    this.timeouts.forEach(t => clearTimeout(t));
    this.timeouts = [];
    this.atoms.forEach(atom => atom.events.removeAllListeners());
    this.atoms.clear();
    this.events.removeAllListeners();
    this.rules = [];
  }
}

export function createBehaviorEngine() {
  return new BehaviorEngine();
}

export default BehaviorEngine;
