/**
 * AnimationLibrary.js
 * Phase 1.3: Enhanced animation system
 * 
 * Features:
 * - Speed blur effects
 * - Pulse animations
 * - Micro-transitions
 * - Particle effects
 * - Smooth value changes
 */

// Animation presets for Framer Motion
export const ANIMATION_PRESETS = {
  // === ENTRANCE ANIMATIONS ===
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.3 }
  },
  
  slideUp: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
    transition: { duration: 0.4, ease: 'easeOut' }
  },
  
  slideDown: {
    initial: { opacity: 0, y: -20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: 20 },
    transition: { duration: 0.4, ease: 'easeOut' }
  },
  
  slideLeft: {
    initial: { opacity: 0, x: 30 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -30 },
    transition: { duration: 0.4, ease: 'easeOut' }
  },
  
  slideRight: {
    initial: { opacity: 0, x: -30 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 30 },
    transition: { duration: 0.4, ease: 'easeOut' }
  },
  
  scaleIn: {
    initial: { opacity: 0, scale: 0.8 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.8 },
    transition: { duration: 0.3, ease: 'easeOut' }
  },
  
  bounceIn: {
    initial: { opacity: 0, scale: 0.3 },
    animate: { opacity: 1, scale: 1 },
    transition: { 
      type: 'spring', 
      stiffness: 500, 
      damping: 25 
    }
  },

  // === CONTINUOUS ANIMATIONS ===
  pulse: {
    animate: {
      scale: [1, 1.05, 1],
      opacity: [1, 0.8, 1],
    },
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: 'easeInOut'
    }
  },
  
  pulseFast: {
    animate: {
      scale: [1, 1.1, 1],
    },
    transition: {
      duration: 0.8,
      repeat: Infinity,
      ease: 'easeInOut'
    }
  },
  
  glow: {
    animate: {
      boxShadow: [
        '0 0 5px rgba(255, 165, 0, 0.5)',
        '0 0 20px rgba(255, 165, 0, 0.8)',
        '0 0 5px rgba(255, 165, 0, 0.5)',
      ],
    },
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut'
    }
  },
  
  float: {
    animate: {
      y: [0, -10, 0],
    },
    transition: {
      duration: 3,
      repeat: Infinity,
      ease: 'easeInOut'
    }
  },
  
  spin: {
    animate: {
      rotate: 360,
    },
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'linear'
    }
  },
  
  shake: {
    animate: {
      x: [0, -5, 5, -5, 5, 0],
    },
    transition: {
      duration: 0.5,
      ease: 'easeInOut'
    }
  },
  
  wobble: {
    animate: {
      rotate: [0, -3, 3, -3, 3, 0],
    },
    transition: {
      duration: 0.8,
      ease: 'easeInOut'
    }
  },

  // === PHYSICS ANIMATIONS ===
  forceArrowPulse: {
    animate: {
      scaleX: [1, 1.15, 1],
      opacity: [1, 0.9, 1],
    },
    transition: {
      duration: 0.8,
      repeat: Infinity,
      ease: 'easeInOut'
    }
  },
  
  vectorGrow: {
    initial: { scaleX: 0, originX: 0 },
    animate: { scaleX: 1 },
    transition: { duration: 0.5, ease: 'easeOut' }
  },
  
  ballMotion: {
    animate: (custom) => ({
      x: custom.endX,
      y: custom.trajectory ? 
        [custom.startY, custom.peakY, custom.endY] : 
        custom.endY,
    }),
    transition: (custom) => ({
      duration: custom.duration || 1,
      ease: custom.ease || 'easeOut'
    })
  },
  
  gravity: {
    animate: (custom) => ({
      y: custom.groundY,
    }),
    transition: {
      type: 'spring',
      stiffness: 100,
      damping: 10,
    }
  },
  
  bounce: {
    animate: {
      y: [0, -20, 0, -10, 0, -5, 0],
    },
    transition: {
      duration: 1,
      times: [0, 0.2, 0.4, 0.55, 0.7, 0.85, 1],
      ease: 'easeOut'
    }
  },

  // === VALUE CHANGE ANIMATIONS ===
  valueIncrease: {
    animate: {
      scale: [1, 1.2, 1],
      color: ['inherit', '#22c55e', 'inherit'],
    },
    transition: {
      duration: 0.4,
      ease: 'easeOut'
    }
  },
  
  valueDecrease: {
    animate: {
      scale: [1, 0.9, 1],
      color: ['inherit', '#ef4444', 'inherit'],
    },
    transition: {
      duration: 0.4,
      ease: 'easeOut'
    }
  },
  
  highlightChange: {
    animate: {
      backgroundColor: ['transparent', 'rgba(255, 215, 0, 0.3)', 'transparent'],
    },
    transition: {
      duration: 0.6,
      ease: 'easeInOut'
    }
  },
};

// === SPEED BLUR EFFECT ===
export const createSpeedBlur = (velocity, direction = 'horizontal') => {
  const blurAmount = Math.min(velocity / 10, 10);
  const stretchAmount = 1 + (velocity / 100);
  
  return {
    filter: `blur(${blurAmount}px)`,
    transform: direction === 'horizontal' 
      ? `scaleX(${stretchAmount})`
      : `scaleY(${stretchAmount})`,
  };
};

// === SVG FILTER DEFINITIONS ===
export const SVG_FILTERS = {
  speedBlur: `
    <filter id="speedBlur" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="3 0" />
    </filter>
  `,
  
  glow: `
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  `,
  
  shadow: `
    <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
      <feDropShadow dx="2" dy="3" stdDeviation="2" flood-opacity="0.3" />
    </filter>
  `,
  
  motionTrail: `
    <filter id="motionTrail" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="2" result="blur1" />
      <feOffset in="blur1" dx="-5" dy="0" result="offset1" />
      <feGaussianBlur in="offset1" stdDeviation="3" result="blur2" />
      <feOffset in="blur2" dx="-10" dy="0" result="offset2" />
      <feMerge>
        <feMergeNode in="offset2" />
        <feMergeNode in="offset1" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  `,
};

// === PARTICLE SYSTEM ===
export class ParticleSystem {
  constructor(config = {}) {
    this.particles = [];
    this.config = {
      maxParticles: config.maxParticles || 50,
      particleLife: config.particleLife || 1000,
      emitRate: config.emitRate || 10,
      gravity: config.gravity || 0.1,
      ...config
    };
  }

  emit(x, y, count = 1, options = {}) {
    for (let i = 0; i < count; i++) {
      if (this.particles.length >= this.config.maxParticles) break;
      
      this.particles.push({
        id: Date.now() + Math.random(),
        x,
        y,
        vx: (Math.random() - 0.5) * (options.spread || 5),
        vy: (Math.random() - 0.5) * (options.spread || 5) - (options.upward ? 3 : 0),
        life: this.config.particleLife,
        maxLife: this.config.particleLife,
        size: options.size || 4,
        color: options.color || '#FFD700',
        type: options.type || 'circle',
      });
    }
  }

  update(deltaTime) {
    this.particles = this.particles.filter(p => {
      p.x += p.vx;
      p.y += p.vy;
      p.vy += this.config.gravity;
      p.life -= deltaTime;
      return p.life > 0;
    });
  }

  render() {
    return this.particles.map(p => ({
      ...p,
      opacity: p.life / p.maxLife,
      scale: (p.life / p.maxLife) * p.size,
    }));
  }

  clear() {
    this.particles = [];
  }
}

// === SPRING PHYSICS ===
export const springPhysics = {
  // Soft spring (gentle bounce)
  soft: {
    type: 'spring',
    stiffness: 100,
    damping: 15,
    mass: 1,
  },
  
  // Medium spring (balanced)
  medium: {
    type: 'spring',
    stiffness: 300,
    damping: 25,
    mass: 1,
  },
  
  // Stiff spring (snappy)
  stiff: {
    type: 'spring',
    stiffness: 500,
    damping: 30,
    mass: 1,
  },
  
  // Bouncy spring
  bouncy: {
    type: 'spring',
    stiffness: 400,
    damping: 10,
    mass: 1,
  },
  
  // Wobbly spring
  wobbly: {
    type: 'spring',
    stiffness: 180,
    damping: 12,
    mass: 1,
  },
};

// === EASING FUNCTIONS ===
export const easings = {
  // Standard easings
  linear: [0, 0, 1, 1],
  easeIn: [0.4, 0, 1, 1],
  easeOut: [0, 0, 0.2, 1],
  easeInOut: [0.4, 0, 0.2, 1],
  
  // Physics-based
  accelerate: [0.4, 0, 0.8, 0.4],
  decelerate: [0.2, 0.6, 0.4, 1],
  
  // Dramatic
  anticipate: [0.36, 0, 0.66, -0.56],
  overshoot: [0.34, 1.56, 0.64, 1],
  
  // Bounce
  bounceOut: (t) => {
    const n1 = 7.5625;
    const d1 = 2.75;
    if (t < 1 / d1) return n1 * t * t;
    if (t < 2 / d1) return n1 * (t -= 1.5 / d1) * t + 0.75;
    if (t < 2.5 / d1) return n1 * (t -= 2.25 / d1) * t + 0.9375;
    return n1 * (t -= 2.625 / d1) * t + 0.984375;
  },
};

// === ANIMATION SEQUENCES ===
export const createSequence = (steps) => {
  return {
    animate: async (controls) => {
      for (const step of steps) {
        await controls.start(step.animation);
        if (step.delay) {
          await new Promise(resolve => setTimeout(resolve, step.delay));
        }
      }
    }
  };
};

// === STAGGER ANIMATIONS ===
export const staggerConfig = {
  fast: {
    staggerChildren: 0.05,
    delayChildren: 0,
  },
  medium: {
    staggerChildren: 0.1,
    delayChildren: 0.1,
  },
  slow: {
    staggerChildren: 0.2,
    delayChildren: 0.2,
  },
};

// === MICRO-TRANSITION HELPERS ===
export const microTransitions = {
  // Smooth value interpolation
  smoothValue: (from, to, progress) => {
    return from + (to - from) * progress;
  },
  
  // Color interpolation
  interpolateColor: (color1, color2, progress) => {
    const r1 = parseInt(color1.slice(1, 3), 16);
    const g1 = parseInt(color1.slice(3, 5), 16);
    const b1 = parseInt(color1.slice(5, 7), 16);
    
    const r2 = parseInt(color2.slice(1, 3), 16);
    const g2 = parseInt(color2.slice(3, 5), 16);
    const b2 = parseInt(color2.slice(5, 7), 16);
    
    const r = Math.round(r1 + (r2 - r1) * progress);
    const g = Math.round(g1 + (g2 - g1) * progress);
    const b = Math.round(b1 + (b2 - b1) * progress);
    
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
  },
  
  // Size based on value
  sizeFromValue: (value, minValue, maxValue, minSize, maxSize) => {
    const normalized = (value - minValue) / (maxValue - minValue);
    return minSize + (maxSize - minSize) * normalized;
  },
  
  // Arrow thickness based on force
  arrowThickness: (force, minForce = 0, maxForce = 50) => {
    const normalized = Math.min(Math.max((force - minForce) / (maxForce - minForce), 0), 1);
    return 2 + normalized * 8; // 2px to 10px
  },
  
  // Opacity based on distance
  distanceOpacity: (distance, maxDistance) => {
    return Math.max(0, 1 - (distance / maxDistance));
  },
};

// === TRAIL EFFECT ===
export const createTrail = (positions, maxLength = 10) => {
  const trail = positions.slice(-maxLength);
  return trail.map((pos, idx) => ({
    ...pos,
    opacity: (idx + 1) / trail.length,
    scale: 0.5 + (idx / trail.length) * 0.5,
  }));
};

// === GESTURE ANIMATIONS ===
export const gestureAnimations = {
  tap: {
    scale: 0.95,
    transition: { duration: 0.1 }
  },
  
  hover: {
    scale: 1.05,
    transition: { duration: 0.2 }
  },
  
  drag: {
    scale: 1.1,
    boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
    transition: { duration: 0.2 }
  },
  
  focus: {
    boxShadow: '0 0 0 3px rgba(66, 153, 225, 0.5)',
    transition: { duration: 0.2 }
  },
};

// === CELEBRATION ANIMATIONS ===
export const celebrationAnimations = {
  confetti: {
    particles: 50,
    spread: 360,
    colors: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8'],
    gravity: 0.3,
  },
  
  sparkle: {
    particles: 20,
    spread: 180,
    colors: ['#FFD700', '#FFF'],
    gravity: 0.05,
    upward: true,
  },
  
  burst: {
    particles: 30,
    spread: 360,
    colors: ['#FF5722', '#FF9800', '#FFC107'],
    gravity: 0.2,
  },
};

export default {
  ANIMATION_PRESETS,
  SVG_FILTERS,
  ParticleSystem,
  springPhysics,
  easings,
  createSequence,
  staggerConfig,
  microTransitions,
  createTrail,
  gestureAnimations,
  celebrationAnimations,
  createSpeedBlur,
};
