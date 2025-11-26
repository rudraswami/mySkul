/**
 * Animation Library
 * Pre-built animations for physics concepts and interactions
 * All animations are non-destructive and work with the SceneObjectRegistry
 */

import { sceneRegistry } from './SceneObjectRegistry';

// Easing functions
export const easings = {
  linear: t => t,
  easeIn: t => t * t,
  easeOut: t => 1 - (1 - t) * (1 - t),
  easeInOut: t => t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2,
  bounce: t => {
    const n1 = 7.5625;
    const d1 = 2.75;
    if (t < 1 / d1) return n1 * t * t;
    if (t < 2 / d1) return n1 * (t -= 1.5 / d1) * t + 0.75;
    if (t < 2.5 / d1) return n1 * (t -= 2.25 / d1) * t + 0.9375;
    return n1 * (t -= 2.625 / d1) * t + 0.984375;
  },
  elastic: t => {
    const c4 = (2 * Math.PI) / 3;
    return t === 0 ? 0 : t === 1 ? 1 :
      Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
  },
  spring: t => 1 - Math.cos(t * Math.PI * 2) * Math.exp(-t * 5),
};

/**
 * Base animation runner
 */
export function animate(options) {
  const {
    duration = 1000,
    easing = 'easeOut',
    onUpdate,
    onComplete,
  } = options;

  const startTime = performance.now();
  const easingFn = typeof easing === 'function' ? easing : easings[easing] || easings.linear;

  return new Promise((resolve) => {
    function tick(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easedProgress = easingFn(progress);

      onUpdate?.(easedProgress, progress);

      if (progress < 1) {
        requestAnimationFrame(tick);
      } else {
        onComplete?.();
        resolve();
      }
    }

    requestAnimationFrame(tick);
  });
}

/**
 * Animation Presets for Visual Engine
 */
export const animations = {
  /**
   * Move object from current position to target
   */
  moveTo: (objectId, targetX, targetY, options = {}) => {
    const obj = sceneRegistry.get(objectId);
    if (!obj) return Promise.resolve();

    const startX = obj.x;
    const startY = obj.y;

    sceneRegistry.setAnimationState(objectId, 'moving');

    return animate({
      duration: options.duration || 800,
      easing: options.easing || 'easeOut',
      onUpdate: (progress) => {
        const x = startX + (targetX - startX) * progress;
        const y = startY + (targetY - startY) * progress;
        sceneRegistry.update(objectId, { x, y });
      },
      onComplete: () => {
        sceneRegistry.setAnimationState(objectId, 'idle');
        sceneRegistry.update(objectId, { x: targetX, y: targetY });
      },
    });
  },

  /**
   * Projectile motion (ball throw)
   */
  projectile: (objectId, options = {}) => {
    const obj = sceneRegistry.get(objectId);
    if (!obj) return Promise.resolve();

    const {
      force = 'medium',
      angle = -30,
      duration = 1500,
    } = options;

    const forceMultiplier = { low: 100, medium: 180, high: 280 }[force] || 180;
    const angleRad = (angle * Math.PI) / 180;
    const startX = obj.x;
    const startY = obj.y;
    const vx = forceMultiplier * Math.cos(angleRad);
    const vy = forceMultiplier * Math.sin(angleRad);
    const gravity = 200;

    sceneRegistry.setAnimationState(objectId, 'projectile');

    return animate({
      duration,
      easing: 'linear',
      onUpdate: (progress) => {
        const t = progress * 2;
        const x = startX + vx * t;
        const y = startY + vy * t + 0.5 * gravity * t * t;
        const rotation = (obj.rotation || 0) + progress * 720; // Spin
        sceneRegistry.update(objectId, { x, y, rotation });
      },
      onComplete: () => {
        sceneRegistry.setAnimationState(objectId, 'idle');
      },
    });
  },

  /**
   * Force arrow grow animation
   */
  forceArrowGrow: (objectId, options = {}) => {
    const {
      direction = 'right',
      magnitude = 100,
      duration = 600,
    } = options;

    sceneRegistry.update(objectId, { 
      visible: true, 
      magnitude: 0, 
      direction,
      animationState: 'growing' 
    });

    return animate({
      duration,
      easing: 'easeOut',
      onUpdate: (progress) => {
        sceneRegistry.update(objectId, { 
          magnitude: magnitude * progress,
          opacity: Math.min(1, progress * 2),
        });
      },
      onComplete: () => {
        sceneRegistry.setAnimationState(objectId, 'idle');
      },
    });
  },

  /**
   * Pulse/highlight effect
   */
  pulse: (objectId, options = {}) => {
    const {
      scale = 1.2,
      duration = 600,
      repeat = 2,
    } = options;

    const obj = sceneRegistry.get(objectId);
    if (!obj) return Promise.resolve();

    const originalScale = obj.scale || 1;
    let currentRepeat = 0;

    const runPulse = () => {
      return animate({
        duration: duration / 2,
        easing: 'easeInOut',
        onUpdate: (progress) => {
          const currentScale = originalScale + (scale - originalScale) * Math.sin(progress * Math.PI);
          sceneRegistry.update(objectId, { scale: currentScale, highlighted: true });
        },
      });
    };

    const loop = async () => {
      while (currentRepeat < repeat) {
        await runPulse();
        currentRepeat++;
      }
      sceneRegistry.update(objectId, { scale: originalScale, highlighted: false });
    };

    return loop();
  },

  /**
   * Fade in
   */
  fadeIn: (objectId, options = {}) => {
    sceneRegistry.update(objectId, { visible: true, opacity: 0 });

    return animate({
      duration: options.duration || 400,
      easing: 'easeOut',
      onUpdate: (progress) => {
        sceneRegistry.update(objectId, { opacity: progress });
      },
    });
  },

  /**
   * Fade out
   */
  fadeOut: (objectId, options = {}) => {
    return animate({
      duration: options.duration || 400,
      easing: 'easeIn',
      onUpdate: (progress) => {
        sceneRegistry.update(objectId, { opacity: 1 - progress });
      },
      onComplete: () => {
        sceneRegistry.update(objectId, { visible: false });
      },
    });
  },

  /**
   * Shake effect (for emphasis or error)
   */
  shake: (objectId, options = {}) => {
    const obj = sceneRegistry.get(objectId);
    if (!obj) return Promise.resolve();

    const originalX = obj.x;
    const intensity = options.intensity || 5;

    return animate({
      duration: options.duration || 500,
      easing: 'linear',
      onUpdate: (progress) => {
        const offset = Math.sin(progress * Math.PI * 8) * intensity * (1 - progress);
        sceneRegistry.update(objectId, { x: originalX + offset });
      },
      onComplete: () => {
        sceneRegistry.update(objectId, { x: originalX });
      },
    });
  },

  /**
   * Rotate animation
   */
  rotate: (objectId, options = {}) => {
    const obj = sceneRegistry.get(objectId);
    if (!obj) return Promise.resolve();

    const startRotation = obj.rotation || 0;
    const targetRotation = options.angle || 360;

    return animate({
      duration: options.duration || 800,
      easing: options.easing || 'easeInOut',
      onUpdate: (progress) => {
        sceneRegistry.update(objectId, { 
          rotation: startRotation + targetRotation * progress 
        });
      },
    });
  },

  /**
   * Scale animation
   */
  scale: (objectId, targetScale, options = {}) => {
    const obj = sceneRegistry.get(objectId);
    if (!obj) return Promise.resolve();

    const startScale = obj.scale || 1;

    return animate({
      duration: options.duration || 400,
      easing: options.easing || 'easeOut',
      onUpdate: (progress) => {
        sceneRegistry.update(objectId, { 
          scale: startScale + (targetScale - startScale) * progress 
        });
      },
    });
  },

  /**
   * Spring bounce (for landing/impact)
   */
  springBounce: (objectId, options = {}) => {
    const obj = sceneRegistry.get(objectId);
    if (!obj) return Promise.resolve();

    const originalY = obj.y;
    const bounceHeight = options.height || 20;

    return animate({
      duration: options.duration || 600,
      easing: 'spring',
      onUpdate: (progress) => {
        const bounce = Math.sin(progress * Math.PI * 2) * bounceHeight * (1 - progress);
        sceneRegistry.update(objectId, { y: originalY - bounce });
      },
      onComplete: () => {
        sceneRegistry.update(objectId, { y: originalY });
      },
    });
  },

  /**
   * Professor gesture animation
   */
  professorGesture: (objectId, gesture = 'point', options = {}) => {
    const gestures = {
      point: { armAngle: -45, duration: 400 },
      explain: { armAngle: -30, duration: 300 },
      think: { headTilt: -10, duration: 500 },
      celebrate: { armAngle: -60, scale: 1.05, duration: 600 },
    };

    const config = gestures[gesture] || gestures.point;
    
    return animate({
      duration: config.duration,
      easing: 'easeOut',
      onUpdate: (progress) => {
        sceneRegistry.update(objectId, {
          gesture,
          gestureProgress: progress,
          armAngle: config.armAngle * progress,
          headTilt: (config.headTilt || 0) * progress,
        });
      },
    });
  },

  /**
   * Sequence multiple animations
   */
  sequence: async (animationList) => {
    for (const anim of animationList) {
      if (typeof anim === 'function') {
        await anim();
      } else if (anim.parallel) {
        await Promise.all(anim.parallel.map(a => a()));
      }
    }
  },

  /**
   * Run animations in parallel
   */
  parallel: (animationList) => {
    return Promise.all(animationList.map(anim => 
      typeof anim === 'function' ? anim() : Promise.resolve()
    ));
  },
};

export default animations;


