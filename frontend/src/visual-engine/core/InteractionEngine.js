/**
 * Interaction Engine
 * Handles tap, long-press, swipe, and drag interactions
 * Maps user gestures to scene actions
 */

import { sceneRegistry } from './SceneObjectRegistry';
import { timelineEngine } from './TimelineEngine';

class InteractionEngine {
  constructor() {
    this.interactions = new Map(); // objectId -> interaction config
    this.globalInteractions = []; // Scene-wide interactions
    this.listeners = {};
    this.touchState = {
      startX: 0,
      startY: 0,
      startTime: 0,
      currentTarget: null,
      isLongPress: false,
      longPressTimer: null,
    };
    
    // Configuration
    this.config = {
      longPressDelay: 500, // ms
      swipeThreshold: 50, // px
      tapMaxDuration: 300, // ms
    };
  }

  /**
   * Register interaction for an object
   */
  register(objectId, interactionConfig) {
    this.interactions.set(objectId, {
      objectId,
      ...interactionConfig,
    });
  }

  /**
   * Register global interaction (e.g., swipe anywhere)
   */
  registerGlobal(interactionConfig) {
    this.globalInteractions.push(interactionConfig);
  }

  /**
   * Handle touch/pointer start
   */
  handleStart(event, objectId = null) {
    const point = this.getPoint(event);
    
    this.touchState = {
      startX: point.x,
      startY: point.y,
      startTime: Date.now(),
      currentTarget: objectId,
      isLongPress: false,
      longPressTimer: null,
    };

    // Start long press timer
    if (objectId) {
      this.touchState.longPressTimer = setTimeout(() => {
        this.touchState.isLongPress = true;
        this.handleLongPress(objectId);
      }, this.config.longPressDelay);
    }

    this.emit('touchStart', { objectId, point });
  }

  /**
   * Handle touch/pointer move
   */
  handleMove(event) {
    const point = this.getPoint(event);
    const deltaX = point.x - this.touchState.startX;
    const deltaY = point.y - this.touchState.startY;

    // Cancel long press if moved too much
    if (Math.abs(deltaX) > 10 || Math.abs(deltaY) > 10) {
      this.cancelLongPress();
    }

    this.emit('touchMove', { point, deltaX, deltaY });
  }

  /**
   * Handle touch/pointer end
   */
  handleEnd(event) {
    this.cancelLongPress();

    const point = this.getPoint(event);
    const deltaX = point.x - this.touchState.startX;
    const deltaY = point.y - this.touchState.startY;
    const duration = Date.now() - this.touchState.startTime;

    // Detect gesture type
    if (this.touchState.isLongPress) {
      // Already handled
      return;
    }

    if (Math.abs(deltaX) > this.config.swipeThreshold) {
      // Swipe
      const direction = deltaX > 0 ? 'right' : 'left';
      this.handleSwipe(direction);
    } else if (Math.abs(deltaY) > this.config.swipeThreshold) {
      // Vertical swipe
      const direction = deltaY > 0 ? 'down' : 'up';
      this.handleSwipe(direction);
    } else if (duration < this.config.tapMaxDuration) {
      // Tap
      this.handleTap(this.touchState.currentTarget);
    }

    // Reset state
    this.touchState.currentTarget = null;
    this.emit('touchEnd', { point });
  }

  /**
   * Handle tap interaction
   */
  handleTap(objectId) {
    this.emit('tap', { objectId });

    if (objectId) {
      // Get object's interaction config
      const config = this.interactions.get(objectId);
      
      if (config?.onTap) {
        this.executeAction(config.onTap, objectId);
      } else {
        // Default: highlight the object
        sceneRegistry.highlight(objectId, 1000);
      }
    }

    // Check global interactions
    this.globalInteractions.forEach(interaction => {
      if (interaction.onTap) {
        this.executeAction(interaction.onTap, objectId);
      }
    });
  }

  /**
   * Handle long press interaction
   */
  handleLongPress(objectId) {
    this.emit('longPress', { objectId });

    if (objectId) {
      const config = this.interactions.get(objectId);
      
      if (config?.onLongPress) {
        this.executeAction(config.onLongPress, objectId);
      } else {
        // Default: show formula/details
        this.emit('showFormula', { objectId });
      }
    }
  }

  /**
   * Handle swipe interaction
   */
  handleSwipe(direction) {
    this.emit('swipe', { direction });

    // Check global interactions
    this.globalInteractions.forEach(interaction => {
      if (interaction.onSwipe) {
        if (interaction.onSwipe === 'next_step' && direction === 'left') {
          timelineEngine.nextStep();
        } else if (interaction.onSwipe === 'prev_step' && direction === 'right') {
          timelineEngine.prevStep();
        }
      }
    });

    // Default swipe behavior
    if (direction === 'left') {
      timelineEngine.nextStep();
    } else if (direction === 'right') {
      timelineEngine.prevStep();
    }
  }

  /**
   * Execute an action string
   */
  executeAction(action, targetId) {
    if (typeof action === 'function') {
      action(targetId);
      return;
    }

    if (typeof action !== 'string') return;

    // Parse action string: "highlight(force_arrow)", "show(formula)"
    const match = action.match(/^(\w+)\(([^)]*)\)$/);
    
    if (match) {
      const [, actionType, params] = match;
      const paramList = params.split(',').map(p => p.trim());

      switch (actionType) {
        case 'highlight':
          sceneRegistry.highlight(paramList[0] || targetId, 1500);
          break;
        case 'show':
          sceneRegistry.show(paramList[0]);
          break;
        case 'hide':
          sceneRegistry.hide(paramList[0]);
          break;
        case 'animate':
          this.emit('animate', { objectId: paramList[0] || targetId });
          break;
        case 'next_step':
          timelineEngine.nextStep();
          break;
        case 'prev_step':
          timelineEngine.prevStep();
          break;
        case 'showFormula':
          this.emit('showFormula', { objectId: paramList[0] || targetId });
          break;
        default:
          console.warn(`InteractionEngine: Unknown action "${actionType}"`);
      }
    }
  }

  /**
   * Cancel long press timer
   */
  cancelLongPress() {
    if (this.touchState.longPressTimer) {
      clearTimeout(this.touchState.longPressTimer);
      this.touchState.longPressTimer = null;
    }
  }

  /**
   * Get point from event
   */
  getPoint(event) {
    if (event.touches && event.touches.length > 0) {
      return { x: event.touches[0].clientX, y: event.touches[0].clientY };
    }
    if (event.changedTouches && event.changedTouches.length > 0) {
      return { x: event.changedTouches[0].clientX, y: event.changedTouches[0].clientY };
    }
    return { x: event.clientX || 0, y: event.clientY || 0 };
  }

  /**
   * Event handling
   */
  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = new Set();
    }
    this.listeners[event].add(callback);
    return () => this.listeners[event].delete(callback);
  }

  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(cb => cb(data));
    }
  }

  /**
   * Clear all interactions
   */
  clear() {
    this.interactions.clear();
    this.globalInteractions = [];
    this.cancelLongPress();
  }
}

// Singleton
export const interactionEngine = new InteractionEngine();
export default InteractionEngine;









