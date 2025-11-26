/**
 * Scene Object Registry
 * Maintains persistent object definitions with stable IDs
 * Objects are NEVER deleted - only their properties are updated
 */

class SceneObjectRegistry {
  constructor() {
    this.objects = new Map();
    this.listeners = new Set();
    this.history = []; // For undo/replay
  }

  /**
   * Register a new object or update existing
   */
  register(id, properties) {
    const existing = this.objects.get(id);
    
    if (existing) {
      // MERGE properties - never overwrite completely
      const updated = {
        ...existing,
        ...properties,
        // Preserve critical properties
        id: existing.id,
        created: existing.created,
        updated: Date.now(),
      };
      this.objects.set(id, updated);
      this.history.push({ type: 'update', id, prev: existing, next: updated });
    } else {
      // New object
      const newObj = {
        id,
        ...properties,
        // Default properties
        x: properties.x ?? 0,
        y: properties.y ?? 0,
        scale: properties.scale ?? 1,
        rotation: properties.rotation ?? 0,
        opacity: properties.opacity ?? 1,
        visible: properties.visible ?? true,
        interactive: properties.interactive ?? true,
        animationState: 'idle',
        created: Date.now(),
        updated: Date.now(),
      };
      this.objects.set(id, newObj);
      this.history.push({ type: 'create', id, obj: newObj });
    }

    this.notifyListeners();
    return this.objects.get(id);
  }

  /**
   * Get object by ID
   */
  get(id) {
    return this.objects.get(id);
  }

  /**
   * Get all objects
   */
  getAll() {
    return Array.from(this.objects.values());
  }

  /**
   * Get objects by type
   */
  getByType(type) {
    return this.getAll().filter(obj => obj.type === type);
  }

  /**
   * Update object property (non-destructive)
   */
  update(id, propertyUpdates) {
    const obj = this.objects.get(id);
    if (!obj) {
      console.warn(`SceneObjectRegistry: Object ${id} not found`);
      return null;
    }

    const updated = {
      ...obj,
      ...propertyUpdates,
      id: obj.id, // Preserve ID
      updated: Date.now(),
    };

    this.objects.set(id, updated);
    this.history.push({ type: 'update', id, prev: obj, next: updated });
    this.notifyListeners();
    
    return updated;
  }

  /**
   * Update animation state
   */
  setAnimationState(id, state) {
    return this.update(id, { animationState: state });
  }

  /**
   * Hide object (don't delete!)
   */
  hide(id) {
    return this.update(id, { visible: false, opacity: 0 });
  }

  /**
   * Show object
   */
  show(id) {
    return this.update(id, { visible: true, opacity: 1 });
  }

  /**
   * Highlight object
   */
  highlight(id, duration = 1000) {
    this.update(id, { highlighted: true, highlightStart: Date.now() });
    
    // Auto-remove highlight
    setTimeout(() => {
      this.update(id, { highlighted: false });
    }, duration);
  }

  /**
   * Move object to position
   */
  moveTo(id, x, y) {
    return this.update(id, { x, y });
  }

  /**
   * Reset all objects to initial state
   */
  reset() {
    this.objects.forEach((obj, id) => {
      if (obj.initialState) {
        this.objects.set(id, { ...obj, ...obj.initialState, updated: Date.now() });
      }
    });
    this.notifyListeners();
  }

  /**
   * Clear registry (for scene change)
   */
  clear() {
    this.objects.clear();
    this.history = [];
    this.notifyListeners();
  }

  /**
   * Subscribe to changes
   */
  subscribe(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  /**
   * Notify all listeners
   */
  notifyListeners() {
    const objects = this.getAll();
    this.listeners.forEach(cb => cb(objects));
  }

  /**
   * Export state for debugging
   */
  exportState() {
    return {
      objects: Object.fromEntries(this.objects),
      historyLength: this.history.length,
    };
  }
}

// Singleton instance
export const sceneRegistry = new SceneObjectRegistry();
export default SceneObjectRegistry;


