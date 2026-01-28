/**
 * 🎨 PROCEDURAL RENDERER
 * ======================
 * 
 * Renders the RenderGraph to a Canvas context.
 * Supports:
 * - Shape primitives (rect, ellipse, polygon)
 * - SVG paths
 * - Procedural generators (organic shapes, molecules, etc.)
 * - Effects (glow, shadow, blur)
 * - Particle systems
 * 
 * This is the execution engine that brings ProceduralScenePlan to life.
 */

import { RenderGraphBuilder, ProceduralNode, ParticleSystemNode } from './RenderGraph';
import { generateNodes, hasGenerator } from './generators/index';

// ============================================
// PROCEDURAL RENDERER CLASS
// ============================================

export class ProceduralRenderer {
  constructor(canvas, width = 720, height = 520) {
    this.canvas = canvas;
    this.width = width;
    this.height = height;
    this.ctx = canvas?.getContext('2d');
    
    this.graph = null;
    this.graphBuilder = new RenderGraphBuilder();
    
    // Animation state
    this.running = false;
    this.lastTime = 0;
    this.animationFrameId = null;
    
    // Time tracking for choreography
    this.sceneTime = 0;
    this.activeChoreography = [];
    this.completedChoreography = new Set();
    
    // Callbacks
    this.onNarration = null;
    this.onReady = null;
    
    console.log('🎨 [ProceduralRenderer] Initialized:', { width, height });
  }

  // ============================================
  // SCENE LOADING
  // ============================================

  /**
   * Load a ProceduralScenePlan and build the render graph
   */
  loadScene(plan) {
    console.log('🎨 [ProceduralRenderer] Loading scene...');
    
    // Build render graph from plan
    this.graph = this.graphBuilder.build(plan);
    
    // Resolve procedural nodes
    this.resolveProcedurals(this.graph);
    
    // Extract choreography
    this.activeChoreography = plan.choreography || [];
    this.completedChoreography.clear();
    
    // Reset scene time
    this.sceneTime = 0;
    
    console.log('🎨 [ProceduralRenderer] Scene loaded:', {
      layerCount: this.graph.children.length,
      choreographyCount: this.activeChoreography.length,
    });
    
    // Notify ready
    if (this.onReady) {
      this.onReady();
    }
    
    return this;
  }

  /**
   * Recursively resolve procedural nodes using generators
   */
  resolveProcedurals(node) {
    if (!node) return;
    
    // If this is a procedural node, generate its children
    if (node instanceof ProceduralNode && !node.generated) {
      const { generatorType, params } = node;
      
      if (hasGenerator(generatorType)) {
        console.log(`🧬 [Generator] Resolving: ${generatorType}`);
        const children = generateNodes(generatorType, params);
        node.generated = children;
        children.forEach(child => node.addChild(child));
      }
    }
    
    // Recurse to children
    for (const child of node.children || []) {
      this.resolveProcedurals(child);
    }
  }

  // ============================================
  // ANIMATION LOOP
  // ============================================

  start() {
    if (this.running) return;
    
    this.running = true;
    this.lastTime = performance.now();
    
    console.log('🎬 [ProceduralRenderer] Animation started');
    this.animate(this.lastTime);
  }

  stop() {
    this.running = false;
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
    console.log('🎬 [ProceduralRenderer] Animation stopped');
  }

  animate(time) {
    if (!this.running) return;
    
    const dt = time - this.lastTime;
    this.lastTime = time;
    this.sceneTime += dt;
    
    // Process choreography
    this.processChoreography(this.sceneTime);
    
    // Update scene (particles, animations)
    this.update(dt, time);
    
    // Render
    this.render();
    
    // Next frame
    this.animationFrameId = requestAnimationFrame((t) => this.animate(t));
  }

  // ============================================
  // CHOREOGRAPHY PROCESSOR
  // ============================================

  processChoreography(sceneTime) {
    for (const beat of this.activeChoreography) {
      if (this.completedChoreography.has(beat.id)) continue;
      
      // Check if it's time to execute this beat
      if (sceneTime >= beat.delay) {
        this.executeBeat(beat);
        this.completedChoreography.add(beat.id);
      }
    }
  }

  executeBeat(beat) {
    console.log(`🎼 [Choreography] Executing: ${beat.id} @ ${beat.delay}ms`);
    
    const { target, action, narration } = beat;
    
    // Find target node(s)
    const targets = this.findTargets(target);
    
    // Apply action
    for (const node of targets) {
      this.applyAction(node, action);
    }
    
    // Trigger narration
    if (narration && this.onNarration) {
      this.onNarration({
        text: narration.text,
        emphasis: narration.emphasis || 'normal',
        position: narration.position || 'bottom',
      });
    }
  }

  findTargets(targetSpec) {
    if (targetSpec === '*') {
      return this.getAllNodes(this.graph);
    }
    
    if (Array.isArray(targetSpec)) {
      return targetSpec.flatMap(id => this.findNodeById(this.graph, id) || []);
    }
    
    const node = this.findNodeById(this.graph, targetSpec);
    return node ? [node] : [];
  }

  findNodeById(node, id) {
    if (!node) return null;
    if (node.id === id) return node;
    
    for (const child of node.children || []) {
      const found = this.findNodeById(child, id);
      if (found) return found;
    }
    
    return null;
  }

  getAllNodes(node, result = []) {
    if (node) {
      result.push(node);
      for (const child of node.children || []) {
        this.getAllNodes(child, result);
      }
    }
    return result;
  }

  applyAction(node, action) {
    if (!node || !action) return;
    
    const { type, params = {} } = action;
    
    switch (type) {
      case 'fadeIn':
        node.visible = true;
        this.animateProperty(node, 'opacity', 0, 1, params.duration || 500);
        break;
        
      case 'fadeOut':
        this.animateProperty(node, 'opacity', node.opacity, 0, params.duration || 500);
        break;
        
      case 'scaleIn':
        node.visible = true;
        const fromScale = params.fromScale || 0;
        node.transform = node.transform || {};
        this.animateProperty(node.transform, 'scale', fromScale, 1, params.duration || 500);
        break;
        
      case 'moveTo':
        this.animateProperty(node.position, 'x', node.position.x, params.x, params.duration || 1000);
        this.animateProperty(node.position, 'y', node.position.y, params.y, params.duration || 1000);
        break;
        
      case 'pulse':
        this.pulseAnimation(node, params.duration || 800, params.scale || 1.1, params.loop);
        break;
        
      case 'glow':
        node.effects = node.effects || [];
        node.effects.push({ type: 'glow', params: { color: params.color, intensity: params.intensity } });
        break;
        
      case 'show':
        node.visible = true;
        node.opacity = 1;
        break;
        
      case 'hide':
        node.visible = false;
        break;
        
      case 'highlight':
        node.emphasis = 'high';
        setTimeout(() => { node.emphasis = 'normal'; }, params.duration || 2000);
        break;
        
      default:
        console.warn(`Unknown action type: ${type}`);
    }
  }

  // ============================================
  // ANIMATION HELPERS
  // ============================================

  animateProperty(obj, prop, from, to, duration, easing = 'easeInOut') {
    const startTime = this.sceneTime;
    const animate = () => {
      const elapsed = this.sceneTime - startTime;
      const t = Math.min(elapsed / duration, 1);
      const easedT = this.ease(t, easing);
      
      obj[prop] = from + (to - from) * easedT;
      
      if (t < 1 && this.running) {
        // Animation continues in next frame automatically
      }
    };
    
    // Store animation to be processed in update loop
    if (!this._animations) this._animations = [];
    this._animations.push({ obj, prop, from, to, duration, startTime, easing });
  }

  pulseAnimation(node, duration, scale, loop) {
    const startTime = this.sceneTime;
    node._pulseAnim = { startTime, duration, scale, loop };
  }

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
        if (t < 1 / 2.75) return 7.5625 * t * t;
        if (t < 2 / 2.75) return 7.5625 * (t -= 1.5 / 2.75) * t + 0.75;
        if (t < 2.5 / 2.75) return 7.5625 * (t -= 2.25 / 2.75) * t + 0.9375;
        return 7.5625 * (t -= 2.625 / 2.75) * t + 0.984375;
      default:
        return t;
    }
  }

  // ============================================
  // UPDATE
  // ============================================

  update(dt, time) {
    if (!this.graph) return;
    
    // Process ongoing animations
    if (this._animations) {
      this._animations = this._animations.filter(anim => {
        const elapsed = this.sceneTime - anim.startTime;
        const t = Math.min(elapsed / anim.duration, 1);
        const easedT = this.ease(t, anim.easing);
        
        anim.obj[anim.prop] = anim.from + (anim.to - anim.from) * easedT;
        
        return t < 1; // Keep animation if not complete
      });
    }
    
    // Update pulse animations
    this.updatePulseAnimations(this.graph);
    
    // Update particles
    this.graph.update(dt, time);
  }

  updatePulseAnimations(node) {
    if (!node) return;
    
    if (node._pulseAnim) {
      const { startTime, duration, scale, loop } = node._pulseAnim;
      const elapsed = this.sceneTime - startTime;
      
      if (loop || elapsed < duration) {
        const t = (elapsed % duration) / duration;
        const pulseT = Math.sin(t * Math.PI) * (scale - 1) + 1;
        node.transform = node.transform || {};
        node.transform.scale = pulseT;
      } else {
        node.transform = node.transform || {};
        node.transform.scale = 1;
        delete node._pulseAnim;
      }
    }
    
    for (const child of node.children || []) {
      this.updatePulseAnimations(child);
    }
  }

  // ============================================
  // RENDER
  // ============================================

  render() {
    if (!this.ctx || !this.graph) return;
    
    // Clear canvas
    this.ctx.clearRect(0, 0, this.width, this.height);
    
    // Draw background
    this.drawBackground();
    
    // Render graph
    this.renderNode(this.graph);
  }

  drawBackground() {
    const gradient = this.ctx.createLinearGradient(0, 0, 0, this.height);
    gradient.addColorStop(0, '#F8FAFC');
    gradient.addColorStop(1, '#E2E8F0');
    this.ctx.fillStyle = gradient;
    this.ctx.fillRect(0, 0, this.width, this.height);
  }

  renderNode(node) {
    if (!node || !node.visible) return;
    
    // Use node's own render method with our canvas adapter
    node.render(this.createCanvasAdapter());
  }

  // ============================================
  // CANVAS ADAPTER
  // Create an adapter that matches our RenderNode expectations
  // ============================================

  createCanvasAdapter() {
    const ctx = this.ctx;
    const stack = [];
    
    return {
      // State management
      push: () => { ctx.save(); stack.push({}); },
      pop: () => { ctx.restore(); stack.pop(); },
      
      // Transform
      translate: (x, y) => ctx.translate(x, y),
      rotate: (angle) => ctx.rotate(angle),
      scale: (sx, sy) => ctx.scale(sx, sy ?? sx),
      
      // Style
      fill: (color, alpha = 1) => {
        if (typeof color === 'number') {
          ctx.fillStyle = `rgba(${color}, ${color}, ${color}, ${alpha})`;
        } else {
          ctx.globalAlpha = alpha;
          ctx.fillStyle = color;
        }
      },
      noFill: () => { ctx.fillStyle = 'transparent'; },
      
      stroke: (color, alpha = 1) => {
        if (typeof color === 'number') {
          ctx.strokeStyle = `rgba(${color}, ${color}, ${color}, ${alpha})`;
        } else {
          ctx.globalAlpha = alpha;
          ctx.strokeStyle = color;
        }
      },
      noStroke: () => { ctx.strokeStyle = 'transparent'; },
      strokeWeight: (w) => { ctx.lineWidth = w; },
      
      // Shapes
      rect: (x, y, w, h, r = 0) => {
        ctx.beginPath();
        if (r > 0) {
          ctx.roundRect(x, y, w, h, r);
        } else {
          ctx.rect(x, y, w, h);
        }
        if (ctx.fillStyle !== 'transparent') ctx.fill();
        if (ctx.strokeStyle !== 'transparent') ctx.stroke();
      },
      
      ellipse: (x, y, w, h) => {
        ctx.beginPath();
        ctx.ellipse(x, y, w / 2, h / 2, 0, 0, Math.PI * 2);
        if (ctx.fillStyle !== 'transparent') ctx.fill();
        if (ctx.strokeStyle !== 'transparent') ctx.stroke();
      },
      
      line: (x1, y1, x2, y2) => {
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
      },
      
      // Shapes - path
      beginShape: () => ctx.beginPath(),
      vertex: (x, y) => {
        if (ctx._shapeStarted) {
          ctx.lineTo(x, y);
        } else {
          ctx.moveTo(x, y);
          ctx._shapeStarted = true;
        }
      },
      endShape: (close = false) => {
        if (close) ctx.closePath();
        if (ctx.fillStyle !== 'transparent') ctx.fill();
        if (ctx.strokeStyle !== 'transparent') ctx.stroke();
        ctx._shapeStarted = false;
      },
      
      // Text
      text: (str, x, y) => {
        if (ctx.fillStyle !== 'transparent') {
          ctx.fillText(str, x, y);
        }
        if (ctx.strokeStyle !== 'transparent') {
          ctx.strokeText(str, x, y);
        }
      },
      textSize: (size) => {
        ctx.font = `${size}px system-ui, sans-serif`;
      },
      textStyle: (style) => {
        const size = parseInt(ctx.font) || 16;
        ctx.font = `${style === 'bold' ? 'bold ' : ''}${size}px system-ui, sans-serif`;
      },
      textAlign: (h, v) => {
        ctx.textAlign = h || 'center';
        ctx.textBaseline = v || 'middle';
      },
      
      // Effects
      applyGlow: (color, intensity) => {
        ctx.shadowColor = color;
        ctx.shadowBlur = intensity * 30;
      },
      removeGlow: () => {
        ctx.shadowColor = 'transparent';
        ctx.shadowBlur = 0;
      },
      
      // Raw context access
      drawingContext: ctx,
    };
  }

  // ============================================
  // CLEANUP
  // ============================================

  destroy() {
    this.stop();
    this.graph = null;
    this._animations = null;
    console.log('🎨 [ProceduralRenderer] Destroyed');
  }
}

// ============================================
// EXPORTS
// ============================================

export default ProceduralRenderer;
