/**
 * Animation Timeline Controller
 * Manages sequencing, timing, and coordination of all scene animations
 */

export class AnimationTimeline {
  constructor() {
    this.animations = [];
    this.currentTime = 0;
    this.isPlaying = false;
    this.speed = 1;
    this.listeners = {}; // Changed from Set to Object for event-based listeners
    this.stepIndex = 0;
    this.lastTick = 0;
  }

  /**
   * Initialize timeline with animations from scene config
   */
  init(sceneConfig) {
    this.animations = [];
    this.currentTime = 0;
    this.stepIndex = 0;

    // Add step-based animations
    if (sceneConfig.steps?.length > 0) {
      this.initStepMode(sceneConfig);
    } else {
      this.initAutoMode(sceneConfig);
    }

    return this;
  }

  initStepMode(config) {
    let timeOffset = 0;
    
    config.steps.forEach((step, stepIdx) => {
      step.animations.forEach(animId => {
        const anim = config.animations.find(a => a.id === animId);
        if (anim) {
          this.animations.push({
            ...anim,
            startTime: timeOffset + anim.delay,
            endTime: timeOffset + anim.delay + anim.duration,
            step: stepIdx,
          });
        }
      });
      
      timeOffset += step.duration;
    });
  }

  initAutoMode(config) {
    let timeOffset = 500; // Initial delay
    
    config.animations
      .filter(a => a.trigger === 'auto')
      .forEach(anim => {
        this.animations.push({
          ...anim,
          startTime: timeOffset + anim.delay,
          endTime: timeOffset + anim.delay + anim.duration,
          step: 0,
        });
        
        if (!anim.loop) {
          timeOffset += anim.duration / 2; // Stagger animations
        }
      });
  }

  /**
   * Get animation state at current time
   */
  getState() {
    const state = {
      time: this.currentTime,
      step: this.stepIndex,
      activeAnimations: [],
      completedAnimations: [],
      pendingAnimations: [],
    };

    this.animations.forEach(anim => {
      if (this.currentTime >= anim.endTime) {
        state.completedAnimations.push(anim.id);
      } else if (this.currentTime >= anim.startTime) {
        const progress = (this.currentTime - anim.startTime) / (anim.endTime - anim.startTime);
        state.activeAnimations.push({
          ...anim,
          progress: Math.min(1, Math.max(0, progress)),
        });
      } else {
        state.pendingAnimations.push(anim.id);
      }
    });

    return state;
  }

  /**
   * Calculate animation values at current progress
   */
  calculateValues(anim) {
    const state = this.getState();
    const activeAnim = state.activeAnimations.find(a => a.id === anim.id);
    
    if (!activeAnim) {
      return anim.type === 'vector_grow' ? { length: 0, opacity: 0 } : null;
    }

    const progress = this.ease(activeAnim.progress, anim.easing);
    
    return this.interpolate(anim, progress);
  }

  /**
   * Interpolate animation values based on type
   */
  interpolate(anim, progress) {
    switch (anim.type) {
      case 'throw':
        return this.interpolateThrow(anim, progress);
      case 'push':
      case 'pull':
        return this.interpolateForce(anim, progress);
      case 'fall':
        return this.interpolateFall(anim, progress);
      case 'move':
        return this.interpolateMove(anim, progress);
      case 'vector_grow':
        return this.interpolateVector(anim, progress);
      case 'rotate':
        return { rotation: anim.params.angle * progress };
      case 'scale':
        return { 
          scale: anim.params.from + (anim.params.to - anim.params.from) * progress 
        };
      case 'gesture':
        return { gestureProgress: progress, gesture: anim.params.gesture };
      default:
        return { progress };
    }
  }

  interpolateThrow(anim, progress) {
    const force = { low: 150, medium: 250, high: 350 }[anim.params.force] || 250;
    const angle = (anim.params.angle * Math.PI) / 180;
    
    // Projectile motion
    const t = progress * 2; // Time factor
    const vx = force * Math.cos(angle);
    const vy = force * Math.sin(angle);
    const g = 400; // Gravity
    
    return {
      x: vx * t,
      y: vy * t + 0.5 * g * t * t,
      rotation: progress * 720, // Ball spin
    };
  }

  interpolateForce(anim, progress) {
    const force = { low: 50, medium: 100, high: 200 }[anim.params.force] || 100;
    const direction = anim.params.direction === 'left' ? -1 : 1;
    
    return {
      x: direction * force * progress,
      y: 0,
    };
  }

  interpolateFall(anim, progress) {
    const g = anim.params.acceleration || 9.8;
    const height = 200;
    
    // y = 0.5 * g * t^2 (scaled)
    const y = 0.5 * g * progress * progress * height;
    
    return {
      x: 0,
      y: Math.min(y, height),
    };
  }

  interpolateMove(anim, progress) {
    const to = anim.params.to || { x: 0, y: 0 };
    
    if (anim.params.path === 'curve') {
      // Bezier curve movement
      const cp = { x: to.x * 0.5, y: to.y - 50 }; // Control point
      const t = progress;
      return {
        x: (1-t)*(1-t)*0 + 2*(1-t)*t*cp.x + t*t*to.x,
        y: (1-t)*(1-t)*0 + 2*(1-t)*t*cp.y + t*t*to.y,
      };
    }
    
    return {
      x: to.x * progress,
      y: to.y * progress,
    };
  }

  interpolateVector(anim, progress) {
    const magnitude = anim.params.magnitude || 100;
    
    return {
      length: magnitude * progress,
      opacity: Math.min(1, progress * 2),
      direction: anim.params.direction,
    };
  }

  /**
   * Easing functions
   */
  ease(t, type) {
    switch (type) {
      case 'linear':
        return t;
      case 'easeIn':
        return t * t;
      case 'easeOut':
        return 1 - (1 - t) * (1 - t);
      case 'easeInOut':
        return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
      case 'bounce':
        return this.bounceEase(t);
      case 'elastic':
        return this.elasticEase(t);
      default:
        return t;
    }
  }

  bounceEase(t) {
    const n1 = 7.5625;
    const d1 = 2.75;
    if (t < 1 / d1) return n1 * t * t;
    if (t < 2 / d1) return n1 * (t -= 1.5 / d1) * t + 0.75;
    if (t < 2.5 / d1) return n1 * (t -= 2.25 / d1) * t + 0.9375;
    return n1 * (t -= 2.625 / d1) * t + 0.984375;
  }

  elasticEase(t) {
    const c4 = (2 * Math.PI) / 3;
    return t === 0 ? 0 : t === 1 ? 1 :
      Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
  }

  /**
   * Timeline controls
   */
  play() {
    this.isPlaying = true;
    this.lastTick = performance.now();
    this.tick();
    this.emit('play');
  }

  pause() {
    this.isPlaying = false;
    this.emit('pause');
  }

  stop() {
    this.isPlaying = false;
    this.currentTime = 0;
    this.stepIndex = 0;
    this.emit('stop');
  }

  nextStep() {
    const maxStep = Math.max(...this.animations.map(a => a.step || 0));
    if (this.stepIndex < maxStep) {
      this.stepIndex++;
      // Jump to step start time
      const stepAnim = this.animations.find(a => a.step === this.stepIndex);
      if (stepAnim) {
        this.currentTime = stepAnim.startTime;
      }
      this.emit('step', this.stepIndex);
    }
  }

  prevStep() {
    if (this.stepIndex > 0) {
      this.stepIndex--;
      const stepAnim = this.animations.find(a => a.step === this.stepIndex);
      if (stepAnim) {
        this.currentTime = stepAnim.startTime;
      }
      this.emit('step', this.stepIndex);
    }
  }

  tick() {
    if (!this.isPlaying) return;

    const now = performance.now();
    const delta = (now - this.lastTick) * this.speed;
    this.lastTick = now;
    
    this.currentTime += delta;
    this.emit('tick', this.getState());

    requestAnimationFrame(() => this.tick());
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
   * Get total duration
   */
  getTotalDuration() {
    if (this.animations.length === 0) return 0;
    return Math.max(...this.animations.map(a => a.endTime));
  }
}

export default new AnimationTimeline();

