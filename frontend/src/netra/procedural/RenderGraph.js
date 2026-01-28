/**
 * 🎬 RENDER GRAPH
 * ===============
 * 
 * Tree structure of renderable nodes.
 * Converts ProceduralScenePlan into executable render operations.
 * 
 * Each node type knows how to render itself using the Canvas adapter.
 */

// ============================================
// BASE NODE CLASS
// ============================================

export class RenderNode {
  constructor(spec = {}) {
    this.id = spec.id || `node_${Date.now()}`;
    this.type = 'base';
    this.position = spec.position || { x: 0, y: 0 };
    this.transform = spec.transform || {};
    this.opacity = spec.opacity ?? 1;
    this.visible = spec.visible ?? true;
    this.zIndex = spec.zIndex ?? 0;
    this.role = spec.role || 'effect';
    this.effects = spec.effects || [];
    this.children = [];
    this.parent = null;
  }

  addChild(node) {
    node.parent = this;
    this.children.push(node);
    return this;
  }

  removeChild(node) {
    const idx = this.children.indexOf(node);
    if (idx >= 0) {
      this.children.splice(idx, 1);
      node.parent = null;
    }
    return this;
  }

  // Get world position (accounting for parent transforms)
  getWorldPosition() {
    let x = this.position.x;
    let y = this.position.y;
    let parent = this.parent;
    
    while (parent) {
      x += parent.position.x;
      y += parent.position.y;
      parent = parent.parent;
    }
    
    return { x, y };
  }

  // Apply transform to renderer context
  applyTransform(renderer) {
    const pos = this.getWorldPosition();
    renderer.translate(pos.x, pos.y);
    
    if (this.transform.rotation) {
      renderer.rotate(this.transform.rotation * Math.PI / 180);
    }
    
    if (this.transform.scale) {
      const sx = typeof this.transform.scale === 'number' 
        ? this.transform.scale 
        : this.transform.scale.x;
      const sy = typeof this.transform.scale === 'number' 
        ? this.transform.scale 
        : this.transform.scale.y;
      renderer.scale(sx, sy);
    }
  }

  // Render effects before main content
  renderEffectsBefore(renderer) {
    // Glow effect (rendered as larger blurred shape behind)
    const glowEffect = this.effects.find(e => e.type === 'glow');
    if (glowEffect) {
      this.renderGlow(renderer, glowEffect.params);
    }
    
    // Shadow effect
    const shadowEffect = this.effects.find(e => e.type === 'shadow');
    if (shadowEffect) {
      this.renderShadow(renderer, shadowEffect.params);
    }
  }

  renderGlow(renderer, params = {}) {
    const { color = '#FFD700', intensity = 0.5, radius = 15 } = params;
    // Override in subclasses
  }

  renderShadow(renderer, params = {}) {
    const { color = '#000000', offsetX = 4, offsetY = 4, radius = 8 } = params;
    // Override in subclasses
  }

  // Main render method - override in subclasses
  render(renderer) {
    if (!this.visible) return;
    
    renderer.push();
    this.applyTransform(renderer);
    this.renderEffectsBefore(renderer);
    this.renderContent(renderer);
    this.renderChildren(renderer);
    renderer.pop();
  }

  renderContent(renderer) {
    // Override in subclasses
  }

  renderChildren(renderer) {
    // Sort by zIndex and render
    const sorted = [...this.children].sort((a, b) => a.zIndex - b.zIndex);
    for (const child of sorted) {
      child.render(renderer);
    }
  }

  // Update for animations
  update(dt, time) {
    for (const child of this.children) {
      child.update(dt, time);
    }
  }
}

// ============================================
// LAYER NODE
// ============================================

export class LayerNode extends RenderNode {
  constructor(spec = {}) {
    super(spec);
    this.type = 'layer';
    this.mask = spec.mask || null;
    this.blendMode = spec.blendMode || 'normal';
  }

  render(renderer) {
    if (!this.visible) return;
    
    renderer.push();
    
    // Apply blend mode if supported
    if (renderer.drawingContext && this.blendMode !== 'normal') {
      renderer.drawingContext.globalCompositeOperation = this.blendMode;
    }
    
    // Apply layer opacity
    if (renderer.drawingContext && this.opacity < 1) {
      renderer.drawingContext.globalAlpha = this.opacity;
    }
    
    this.renderChildren(renderer);
    
    renderer.pop();
  }
}

// ============================================
// SHAPE NODES
// ============================================

export class ShapeNode extends RenderNode {
  constructor(spec = {}) {
    super(spec);
    this.type = 'shape';
    this.fill = spec.fill || { type: 'solid', color: '#3B82F6' };
    this.stroke = spec.stroke || null;
    this.width = spec.width || 100;
    this.height = spec.height || 100;
  }

  applyFill(renderer) {
    if (!this.fill) {
      renderer.noFill();
      return;
    }
    
    if (this.fill.type === 'solid') {
      renderer.fill(this.fill.color, this.opacity);
    } else if (this.fill.type === 'gradient' && this.fill.gradient) {
      // For gradient, we'll handle it in subclass or use solid fallback
      const colors = this.fill.gradient.colors;
      renderer.fill(colors[0], this.opacity);
    }
  }

  applyStroke(renderer) {
    if (!this.stroke) {
      renderer.noStroke();
      return;
    }
    
    renderer.stroke(this.stroke.color, this.opacity);
    renderer.strokeWeight(this.stroke.width || 2);
  }

  renderGlow(renderer, params = {}) {
    const { color = '#FFD700', intensity = 0.5, radius = 15 } = params;
    renderer.noStroke();
    
    // Multiple glow layers
    for (let i = 3; i >= 1; i--) {
      const glowSize = i * radius / 3;
      const alpha = intensity * (1 - i * 0.25);
      renderer.fill(color, alpha);
      this.renderShape(renderer, this.width + glowSize * 2, this.height + glowSize * 2);
    }
  }

  renderShadow(renderer, params = {}) {
    const { offsetX = 4, offsetY = 4 } = params;
    renderer.push();
    renderer.translate(offsetX, offsetY);
    renderer.noStroke();
    renderer.fill(0, 0, 0, 0.2);
    this.renderShape(renderer, this.width, this.height);
    renderer.pop();
  }

  renderShape(renderer, w, h) {
    // Override in subclasses
  }

  renderContent(renderer) {
    this.applyFill(renderer);
    this.applyStroke(renderer);
    this.renderShape(renderer, this.width, this.height);
  }
}

export class RectNode extends ShapeNode {
  constructor(spec = {}) {
    super(spec);
    this.shapeType = 'rect';
    this.cornerRadius = spec.cornerRadius || 0;
  }

  renderShape(renderer, w, h) {
    renderer.rect(-w / 2, -h / 2, w, h, this.cornerRadius);
  }
}

export class EllipseNode extends ShapeNode {
  constructor(spec = {}) {
    super(spec);
    this.shapeType = 'ellipse';
  }

  renderShape(renderer, w, h) {
    renderer.ellipse(0, 0, w, h);
  }
}

export class CircleNode extends EllipseNode {
  constructor(spec = {}) {
    super(spec);
    this.shapeType = 'circle';
    this.height = this.width; // Ensure circle
  }
}

export class PolygonNode extends ShapeNode {
  constructor(spec = {}) {
    super(spec);
    this.shapeType = 'polygon';
    this.sides = spec.sides || 6;
  }

  renderShape(renderer, w, h) {
    const radius = Math.min(w, h) / 2;
    renderer.beginShape();
    for (let i = 0; i < this.sides; i++) {
      const angle = (Math.PI * 2 * i) / this.sides - Math.PI / 2;
      const x = Math.cos(angle) * radius;
      const y = Math.sin(angle) * radius;
      renderer.vertex(x, y);
    }
    renderer.endShape(true);
  }
}

// ============================================
// PATH NODE (For organic shapes)
// ============================================

export class PathNode extends RenderNode {
  constructor(spec = {}) {
    super(spec);
    this.type = 'path';
    this.d = spec.d || ''; // SVG path data
    this.fill = spec.fill || { type: 'solid', color: '#3B82F6' };
    this.stroke = spec.stroke || null;
    this.closed = spec.closed ?? true;
  }

  renderContent(renderer) {
    if (!this.d) return;
    
    const ctx = renderer.drawingContext;
    if (!ctx) return;
    
    const path = new Path2D(this.d);
    
    // Apply fill
    if (this.fill && this.fill.type === 'solid') {
      ctx.fillStyle = this.fill.color;
      ctx.globalAlpha = this.opacity;
      ctx.fill(path);
    }
    
    // Apply stroke
    if (this.stroke) {
      ctx.strokeStyle = this.stroke.color;
      ctx.lineWidth = this.stroke.width || 2;
      ctx.globalAlpha = this.opacity;
      ctx.stroke(path);
    }
    
    ctx.globalAlpha = 1;
  }
}

// ============================================
// GROUP NODE
// ============================================

export class GroupNode extends RenderNode {
  constructor(spec = {}) {
    super(spec);
    this.type = 'group';
  }
}

// ============================================
// TEXT NODE
// ============================================

export class TextNode extends RenderNode {
  constructor(spec = {}) {
    super(spec);
    this.type = 'text';
    this.text = spec.text || '';
    this.fontSize = spec.fontSize || 16;
    this.fontWeight = spec.fontWeight || 'normal';
    this.fontFamily = spec.fontFamily || 'system-ui, sans-serif';
    this.fill = spec.fill || { type: 'solid', color: '#1F2937' };
    this.align = spec.align || 'center';
    this.baseline = spec.baseline || 'middle';
  }

  renderContent(renderer) {
    if (!this.text) return;
    
    renderer.noStroke();
    
    if (this.fill && this.fill.color) {
      renderer.fill(this.fill.color, this.opacity);
    }
    
    renderer.textAlign(this.align, this.baseline);
    renderer.textSize(this.fontSize);
    renderer.textStyle(this.fontWeight);
    renderer.text(this.text, 0, 0);
  }
}

// ============================================
// PROCEDURAL NODE (Base for generators)
// ============================================

export class ProceduralNode extends RenderNode {
  constructor(spec = {}) {
    super(spec);
    this.type = 'procedural';
    this.generatorType = spec.generatorType || 'unknown';
    this.params = spec.params || {};
    this.generated = null; // Will hold generated child nodes
  }

  // Generate child nodes based on params
  generate() {
    // Override in specific generator subclasses
    return [];
  }

  render(renderer) {
    if (!this.visible) return;
    
    // Generate if not yet done
    if (!this.generated) {
      this.generated = this.generate();
      this.generated.forEach(node => this.addChild(node));
    }
    
    renderer.push();
    this.applyTransform(renderer);
    this.renderEffectsBefore(renderer);
    this.renderChildren(renderer);
    renderer.pop();
  }
}

// ============================================
// PARTICLE SYSTEM NODE
// ============================================

export class ParticleSystemNode extends RenderNode {
  constructor(spec = {}) {
    super(spec);
    this.type = 'particleSystem';
    this.particleSpec = spec.particle || {};
    this.emitter = spec.emitter || { type: 'point', position: { x: 0, y: 0 } };
    this.physics = spec.physics || {};
    this.rate = spec.rate || 10;
    this.lifetime = spec.lifetime || 2000;
    
    this.particles = [];
    this.lastEmit = 0;
    this.active = spec.active ?? true;
  }

  update(dt, time) {
    if (!this.active) return;
    
    // Emit new particles
    const emitInterval = 1000 / this.rate;
    if (time - this.lastEmit > emitInterval) {
      this.emitParticle();
      this.lastEmit = time;
    }
    
    // Update existing particles
    this.particles = this.particles.filter(p => {
      p.age += dt;
      
      // Apply physics
      if (this.physics.gravity) {
        p.vy += this.physics.gravity.y * dt / 1000;
      }
      if (this.physics.wind) {
        p.vx += this.physics.wind.x * dt / 1000;
      }
      
      p.x += p.vx * dt / 1000;
      p.y += p.vy * dt / 1000;
      
      // Calculate opacity based on lifetime
      p.opacity = 1 - (p.age / p.lifetime);
      
      return p.age < p.lifetime;
    });
  }

  emitParticle() {
    const spec = this.particleSpec;
    const size = spec.size || [5, 10];
    const color = Array.isArray(spec.color) 
      ? spec.color[Math.floor(Math.random() * spec.color.length)]
      : spec.color || '#FFFFFF';
    
    // Get emit position
    let x = 0, y = 0;
    if (this.emitter.type === 'point') {
      x = this.emitter.position?.x || 0;
      y = this.emitter.position?.y || 0;
    } else if (this.emitter.type === 'area') {
      x = (this.emitter.position?.x || 0) + (Math.random() - 0.5) * (this.emitter.size?.width || 100);
      y = (this.emitter.position?.y || 0) + (Math.random() - 0.5) * (this.emitter.size?.height || 100);
    }
    
    // Calculate initial velocity
    const speed = 20 + Math.random() * 30;
    const direction = (this.emitter.direction || -90) * Math.PI / 180;
    const spread = (this.emitter.spread || 30) * Math.PI / 180;
    const angle = direction + (Math.random() - 0.5) * spread;
    
    this.particles.push({
      x,
      y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      size: size[0] + Math.random() * (size[1] - size[0]),
      color,
      opacity: 1,
      age: 0,
      lifetime: this.lifetime * (0.8 + Math.random() * 0.4),
    });
  }

  renderContent(renderer) {
    for (const p of this.particles) {
      renderer.noStroke();
      renderer.fill(p.color, p.opacity * this.opacity);
      renderer.ellipse(p.x, p.y, p.size, p.size);
    }
  }
}

// ============================================
// RENDER GRAPH BUILDER
// ============================================

export class RenderGraphBuilder {
  constructor() {
    this.root = new LayerNode({ id: 'root', zIndex: 0 });
  }

  /**
   * Build RenderGraph from ProceduralScenePlan
   */
  build(plan) {
    this.root = new LayerNode({ id: 'root', zIndex: 0 });
    
    // Create layers
    for (const layerSpec of plan.layers || []) {
      const layer = this.buildLayer(layerSpec);
      this.root.addChild(layer);
    }
    
    // Add global effects as top layer
    if (plan.effects && plan.effects.length > 0) {
      const effectsLayer = new LayerNode({ id: 'effects', zIndex: 1000 });
      // Process global effects
      this.root.addChild(effectsLayer);
    }
    
    // Add particle systems
    if (plan.particles && plan.particles.length > 0) {
      const particlesLayer = new LayerNode({ id: 'particles', zIndex: 500 });
      for (const psSpec of plan.particles) {
        const ps = new ParticleSystemNode(psSpec);
        particlesLayer.addChild(ps);
      }
      this.root.addChild(particlesLayer);
    }
    
    return this.root;
  }

  buildLayer(spec) {
    const layer = new LayerNode({
      id: spec.id,
      zIndex: spec.zIndex || 0,
      opacity: spec.opacity,
      blendMode: spec.blendMode,
      mask: spec.mask,
    });
    
    for (const elemSpec of spec.elements || []) {
      const element = this.buildElement(elemSpec);
      if (element) {
        layer.addChild(element);
      }
    }
    
    return layer;
  }

  buildElement(spec) {
    const { type } = spec;
    
    switch (type) {
      case 'shape':
        return this.buildShape(spec);
      case 'path':
        return new PathNode(spec);
      case 'group':
        return this.buildGroup(spec);
      case 'procedural':
        return this.buildProcedural(spec);
      case 'text':
        return new TextNode(spec);
      default:
        console.warn(`Unknown element type: ${type}`);
        return null;
    }
  }

  buildShape(spec) {
    const shape = spec.shape || 'rect';
    
    switch (shape) {
      case 'rect':
        return new RectNode(spec);
      case 'ellipse':
        return new EllipseNode(spec);
      case 'circle':
        return new CircleNode(spec);
      case 'polygon':
      case 'hexagon':
        return new PolygonNode({ ...spec, sides: shape === 'hexagon' ? 6 : spec.sides });
      default:
        return new RectNode(spec);
    }
  }

  buildGroup(spec) {
    const group = new GroupNode(spec);
    
    for (const childSpec of spec.children || []) {
      const child = this.buildElement(childSpec);
      if (child) {
        group.addChild(child);
      }
    }
    
    return group;
  }

  buildProcedural(spec) {
    // Will be extended by generator registry
    const { generator } = spec;
    if (!generator) {
      console.warn('Procedural element missing generator spec');
      return null;
    }
    
    // Return a ProceduralNode that will be resolved by generators
    return new ProceduralNode({
      ...spec,
      generatorType: generator.type,
      params: generator.params,
    });
  }
}

// ============================================
// EXPORTS
// ============================================

export default {
  RenderNode,
  LayerNode,
  ShapeNode,
  RectNode,
  EllipseNode,
  CircleNode,
  PolygonNode,
  PathNode,
  GroupNode,
  TextNode,
  ProceduralNode,
  ParticleSystemNode,
  RenderGraphBuilder,
};
