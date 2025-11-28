/**
 * Timeline Engine
 * Step-based animation sequencing with proper state management
 * Runs animations step-wise without losing object state
 */

import { sceneRegistry } from './SceneObjectRegistry';

class TimelineEngine {
  constructor() {
    this.steps = [];
    this.currentStepIndex = 0;
    this.isPlaying = false;
    this.isPaused = false;
    this.animationQueue = [];
    this.listeners = {};
    this.stepCallbacks = new Map();
  }

  /**
   * Initialize timeline with steps
   */
  init(steps) {
    this.steps = steps.map((step, index) => ({
      id: step.id || `step_${index}`,
      index,
      title: step.title || `Step ${index + 1}`,
      description: step.description || '',
      animations: step.animations || [],
      labels: step.labels || [],
      duration: step.duration || 2000,
      autoAdvance: step.autoAdvance ?? true,
      completed: false,
    }));
    
    this.currentStepIndex = 0;
    this.emit('init', { steps: this.steps, currentStep: 0 });
    
    return this;
  }

  /**
   * Get current step
   */
  getCurrentStep() {
    return this.steps[this.currentStepIndex] || null;
  }

  /**
   * Get step by index
   */
  getStep(index) {
    return this.steps[index] || null;
  }

  /**
   * Play from current step
   */
  async play() {
    if (this.isPlaying) return;
    
    this.isPlaying = true;
    this.isPaused = false;
    this.emit('play', { step: this.currentStepIndex });
    
    await this.runCurrentStep();
  }

  /**
   * Pause playback
   */
  pause() {
    this.isPaused = true;
    this.isPlaying = false;
    this.emit('pause', { step: this.currentStepIndex });
  }

  /**
   * Stop and reset
   */
  stop() {
    this.isPlaying = false;
    this.isPaused = false;
    this.currentStepIndex = 0;
    this.animationQueue = [];
    
    // Reset all step states
    this.steps.forEach(step => {
      step.completed = false;
    });
    
    this.emit('stop', { step: 0 });
  }

  /**
   * Go to next step
   */
  async nextStep() {
    if (this.currentStepIndex < this.steps.length - 1) {
      // Mark current as completed
      if (this.steps[this.currentStepIndex]) {
        this.steps[this.currentStepIndex].completed = true;
      }
      
      this.currentStepIndex++;
      this.emit('stepChange', { 
        step: this.currentStepIndex, 
        direction: 'next',
        stepData: this.getCurrentStep()
      });
      
      if (this.isPlaying) {
        await this.runCurrentStep();
      }
      
      return true;
    }
    
    // Reached end
    this.emit('complete', { totalSteps: this.steps.length });
    return false;
  }

  /**
   * Go to previous step
   */
  async prevStep() {
    if (this.currentStepIndex > 0) {
      this.currentStepIndex--;
      
      // Mark as not completed
      if (this.steps[this.currentStepIndex]) {
        this.steps[this.currentStepIndex].completed = false;
      }
      
      this.emit('stepChange', { 
        step: this.currentStepIndex, 
        direction: 'prev',
        stepData: this.getCurrentStep()
      });
      
      if (this.isPlaying) {
        await this.runCurrentStep();
      }
      
      return true;
    }
    return false;
  }

  /**
   * Go to specific step
   */
  async goToStep(index) {
    if (index >= 0 && index < this.steps.length) {
      const prevIndex = this.currentStepIndex;
      this.currentStepIndex = index;
      
      // Update completed states
      this.steps.forEach((step, i) => {
        step.completed = i < index;
      });
      
      this.emit('stepChange', { 
        step: index, 
        prevStep: prevIndex,
        stepData: this.getCurrentStep()
      });
      
      if (this.isPlaying) {
        await this.runCurrentStep();
      }
    }
  }

  /**
   * Run current step's animations
   */
  async runCurrentStep() {
    const step = this.getCurrentStep();
    if (!step) return;

    this.emit('stepStart', { step: this.currentStepIndex, stepData: step });

    // Run all animations in this step
    const animationPromises = step.animations.map(animId => {
      return this.runAnimation(animId);
    });

    // Show labels for this step
    step.labels.forEach(labelId => {
      sceneRegistry.show(labelId);
    });

    // Wait for all animations
    await Promise.all(animationPromises);

    this.emit('stepEnd', { step: this.currentStepIndex, stepData: step });

    // Auto-advance if enabled
    if (step.autoAdvance && this.isPlaying && !this.isPaused) {
      setTimeout(() => {
        if (this.isPlaying && !this.isPaused) {
          this.nextStep();
        }
      }, step.duration);
    }
  }

  /**
   * Run a specific animation
   */
  async runAnimation(animationId) {
    return new Promise((resolve) => {
      // Emit animation start
      this.emit('animationStart', { id: animationId });
      
      // Animation will be handled by the component
      // This just tracks the state
      const callback = this.stepCallbacks.get(animationId);
      if (callback) {
        callback();
      }
      
      // Resolve after a short delay (actual animation handled by components)
      setTimeout(resolve, 100);
    });
  }

  /**
   * Register animation callback
   */
  onAnimation(animationId, callback) {
    this.stepCallbacks.set(animationId, callback);
    return () => this.stepCallbacks.delete(animationId);
  }

  /**
   * Replay from beginning
   */
  async replay() {
    this.stop();
    sceneRegistry.reset();
    
    // Small delay before replay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    this.emit('replay', {});
    await this.play();
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
   * Get progress info
   */
  getProgress() {
    return {
      currentStep: this.currentStepIndex,
      totalSteps: this.steps.length,
      progress: this.steps.length > 0 
        ? (this.currentStepIndex / (this.steps.length - 1)) * 100 
        : 0,
      isPlaying: this.isPlaying,
      isPaused: this.isPaused,
    };
  }
}

// Singleton
export const timelineEngine = new TimelineEngine();
export default TimelineEngine;






