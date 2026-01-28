/**
 * 🔷 ENTITY ATOM
 * ==============
 * 
 * Generic visual entity - the universal building block.
 * Can be any shape, color, with optional label.
 * 
 * 🧬 PROCEDURAL GENERATORS (v2.0)
 * Supports procedural generation for complex organic shapes.
 * Set params.generator to use instead of basic shape.
 */

import { Atom } from './Atom';

// Synchronous import for procedural generators
let proceduralGenerators = null;
let generatorsLoading = false;
let generatorsLoadPromise = null;

const loadGenerators = () => {
  if (proceduralGenerators) return Promise.resolve(proceduralGenerators);
  if (generatorsLoadPromise) return generatorsLoadPromise;
  
  generatorsLoading = true;
  generatorsLoadPromise = import('../procedural/generators/index')
    .then(module => {
      // Module exports default object with functions
      proceduralGenerators = module.default || module;
      generatorsLoading = false;
      
      // Verify the module has required functions
      if (proceduralGenerators.hasGenerator && proceduralGenerators.generateNodes) {
        console.log('🧬 [Entity] Procedural generators loaded successfully');
        console.log('🧬 [Entity] Available generators:', proceduralGenerators.listGenerators?.() || 'unknown');
      } else {
        console.error('🧬 [Entity] Generators module missing required functions!');
        console.log('🧬 [Entity] Module keys:', Object.keys(proceduralGenerators));
      }
      
      return proceduralGenerators;
    })
    .catch(e => {
      console.error('[Entity] Procedural generators failed to load:', e);
      generatorsLoading = false;
      return null;
    });
  
  return generatorsLoadPromise;
};

// Pre-load generators on module load
loadGenerators();

export class Entity extends Atom {
  static get type() {
    return 'Entity';
  }

  getDefaultParams() {
    return {
      shape: 'rect',        // rect, circle, ellipse, polygon, hexagon
      width: 80,
      height: 50,
      fill: '#3498DB',
      stroke: '#2980B9',
      strokeWidth: 2,
      cornerRadius: 6,
      label: null,
      labelColor: '#FFFFFF',
      labelSize: 16,        // Font size for label
      shadow: true,
      glow: false,          // Add glow effect for hero objects
      glowColor: null,      // Defaults to fill color
      glowIntensity: 0.4,   // Glow opacity
      isHero: false,        // Mark as hero object (larger rendering)
      // 🧬 Procedural generator (optional)
      generator: null,      // e.g. 'chloroplast', 'mitochondria', 'molecule', 'wave'
      generatorParams: {},  // Params specific to the generator
    };
  }
  
  // Cache for procedural render nodes
  _proceduralNodes = null;
  _generatorResolved = false;

  getInitialState() {
    return {
      highlighted: false,
      selected: false
    };
  }

  static getParamSchema() {
    return {
      shape: { type: 'string', default: 'rect' },
      width: { type: 'number', min: 10, max: 400, default: 80 },
      height: { type: 'number', min: 10, max: 400, default: 50 },
      fill: { type: 'string', default: '#3498DB' },
      stroke: { type: 'string', default: '#2980B9' },
      strokeWidth: { type: 'number', min: 0, max: 10, default: 2 },
      cornerRadius: { type: 'number', min: 0, max: 50, default: 6 },
      label: { type: 'string' },
      shadow: { type: 'boolean', default: true }
    };
  }

  onMount(scene) {
    super.onMount(scene);
    this.size = {
      width: this.params.width,
      height: this.params.height
    };
    
    // 🧬 Initialize procedural generator if specified
    this._initProcedural();
  }
  
  _initProcedural() {
    // 🧬 CRITICAL: Generator can be at root level OR in params
    const generator = this.generator || this.params.generator;
    const generatorParams = this.generatorParams || this.params.generatorParams || {};
    
    if (!generator || this._generatorResolved) return;
    
    console.log(`🧬 [Entity] _initProcedural called for ${this.id}, generator=${generator}`);
    
    // If generators are already loaded, use them synchronously
    if (proceduralGenerators && proceduralGenerators.hasGenerator(generator)) {
      this._generateNodes(generator, generatorParams);
      return;
    }
    
    // Otherwise, load and generate
    loadGenerators().then(generators => {
      if (generators && generators.hasGenerator(generator) && !this._generatorResolved) {
        this._generateNodes(generator, generatorParams);
      } else if (generator && !this._generatorResolved) {
        console.warn(`🧬 [Entity] Generator "${generator}" not found in registry`);
      }
    });
  }
  
  _generateNodes(generator, generatorParams = {}) {
    if (this._generatorResolved) return;
    
    try {
      console.log(`🧬 [Entity] Generating procedural: ${generator} for ${this.id}`);
      console.log(`🧬 [Entity] Params:`, { width: this.params.width, height: this.params.height, ...generatorParams });
      
      // Merge generator params with entity size
      const mergedParams = {
        width: this.params.width,
        height: this.params.height,
        color: this.params.fill,
        ...generatorParams,
      };
      
      this._proceduralNodes = proceduralGenerators.generateNodes(generator, mergedParams);
      this._generatorResolved = true;
      
      console.log(`🧬 [Entity] Generated ${this._proceduralNodes?.length || 0} procedural nodes for ${this.id}:`, 
        this._proceduralNodes?.map(n => n?.constructor?.name || n?.type || 'unknown'));
    } catch (e) {
      console.error('[Entity] Procedural generation failed:', e);
      console.error('[Entity] Generator:', generator, 'Params:', generatorParams);
      this._generatorResolved = true; // Mark as resolved to prevent retries
    }
  }

  render(renderer) {
    if (!this.visible) return;

    const pos = this.getComputedPosition();
    const { 
      shape, width, height, fill, stroke, strokeWidth, cornerRadius, 
      label, labelColor, labelSize, shadow, glow, glowColor, glowIntensity, isHero,
    } = this.params;
    
    // 🧬 CRITICAL: Generator can be at root level OR in params
    // LLM outputs at root, QualityGate puts in params - support both!
    const generator = this.generator || this.params.generator;
    const generatorParams = this.generatorParams || this.params.generatorParams || {};
    
    const { highlighted, selected } = this.state;

    renderer.push();
    renderer.translate(pos.x, pos.y);

    // Apply emphasis
    let currentFill = fill;
    let currentStroke = stroke;
    let currentStrokeWidth = strokeWidth;
    
    if (this.emphasis === 'high' || highlighted || isHero) {
      currentStroke = '#F39C12';
      currentStrokeWidth = Math.max(strokeWidth, 3);
    }
    if (selected) {
      currentStroke = '#E74C3C';
    }

    // 🧬 PROCEDURAL RENDERING (if generator is specified)
    // Try to generate nodes if not yet done but generators are available
    if (generator && !this._generatorResolved && proceduralGenerators) {
      this._generateNodes(generator, generatorParams);
    }
    
    if (generator && this._proceduralNodes && this._proceduralNodes.length > 0) {
      // Render glow effect for procedural shapes
      if (glow || isHero) {
        const glowCol = glowColor || fill;
        renderer.noStroke();
        for (let i = 3; i >= 1; i--) {
          const glowSize = i * 8;
          const glowOpacity = (glowIntensity || 0.3) * (1 - i * 0.25) * this.opacity;
          renderer.fill(glowCol, glowOpacity);
          renderer.ellipse(0, 0, width + glowSize * 2, height + glowSize * 2);
        }
      }
      
      // Render procedural nodes
      this._renderProceduralNodes(renderer);
      
      // Label (on top of procedural content)
      if (label) {
        this._renderLabel(renderer, label, labelColor, labelSize, width, height);
      }
      
      renderer.pop();
      return;
    }

    // 🔷 STANDARD SHAPE RENDERING (fallback)
    
    // Glow effect (for hero objects)
    if (glow || isHero) {
      const glowCol = glowColor || fill;
      renderer.noStroke();
      
      // Multiple glow layers for soft effect
      for (let i = 3; i >= 1; i--) {
        const glowSize = i * 8;
        const glowOpacity = (glowIntensity || 0.3) * (1 - i * 0.25) * this.opacity;
        renderer.fill(glowCol, glowOpacity);
        this.drawShape(renderer, shape, 0, 0, width + glowSize * 2, height + glowSize * 2, cornerRadius + glowSize);
      }
    }

    // Shadow
    if (shadow) {
      renderer.noStroke();
      renderer.fill(0, 0, 0, 30 * this.opacity);
      this.drawShape(renderer, shape, 4, 4, width, height, cornerRadius);
    }

    // Main shape
    renderer.fill(currentFill, this.opacity);
    renderer.stroke(currentStroke);
    renderer.strokeWeight(currentStrokeWidth);
    this.drawShape(renderer, shape, 0, 0, width, height, cornerRadius);

    // Label
    if (label) {
      this._renderLabel(renderer, label, labelColor, labelSize, width, height);
    }

    renderer.pop();
  }
  
  /**
   * 🧬 Render procedural nodes using canvas adapter
   */
  _renderProceduralNodes(renderer) {
    for (const node of this._proceduralNodes) {
      if (node && typeof node.render === 'function') {
        // Create adapter compatible with RenderGraph nodes
        const adapter = this._createNodeAdapter(renderer);
        node.render(adapter);
      }
    }
  }
  
  /**
   * Create adapter to bridge RenderGraph nodes to our renderer
   */
  _createNodeAdapter(renderer) {
    return {
      push: () => renderer.push(),
      pop: () => renderer.pop(),
      translate: (x, y) => renderer.translate(x, y),
      rotate: (a) => renderer.rotate(a),
      scale: (sx, sy) => renderer.scale(sx, sy ?? sx),
      fill: (c, a) => renderer.fill(c, a * this.opacity),
      noFill: () => renderer.noFill(),
      stroke: (c, a) => renderer.stroke(c, a * this.opacity),
      noStroke: () => renderer.noStroke(),
      strokeWeight: (w) => renderer.strokeWeight(w),
      rect: (x, y, w, h, r) => renderer.rect(x, y, w, h, r),
      ellipse: (x, y, w, h) => renderer.ellipse(x, y, w, h),
      line: (x1, y1, x2, y2) => renderer.line(x1, y1, x2, y2),
      beginShape: () => renderer.beginShape(),
      vertex: (x, y) => renderer.vertex(x, y),
      endShape: (close) => renderer.endShape(close),
      text: (str, x, y) => renderer.text(str, x, y),
      textSize: (s) => renderer.textSize(s),
      textAlign: (h, v) => renderer.textAlign(h, v),
      textStyle: (s) => renderer.textStyle(s),
      drawingContext: renderer.ctx || renderer.drawingContext,
    };
  }
  
  /**
   * Render label text
   */
  _renderLabel(renderer, label, labelColor, labelSize, width, height) {
    renderer.noStroke();
    renderer.fill(labelColor, this.opacity);
    renderer.textAlign('center', 'center');
    
    // Scale label size based on object size, with minimum and maximum
    const autoLabelSize = Math.min(Math.max(Math.min(width, height) * 0.25, 12), labelSize || 18);
    renderer.textSize(autoLabelSize);
    renderer.textStyle('bold');
    renderer.text(label, 0, 0);
  }

  drawShape(renderer, shape, x, y, w, h, r) {
    switch (shape) {
      case 'circle':
        renderer.ellipse(x, y, Math.min(w, h), Math.min(w, h));
        break;
      case 'ellipse':
        renderer.ellipse(x, y, w, h);
        break;
      case 'hexagon':
        this.drawHexagon(renderer, x, y, Math.min(w, h) / 2);
        break;
      case 'triangle':
        renderer.triangle(x, y - h/2, x - w/2, y + h/2, x + w/2, y + h/2);
        break;
      case 'rect':
      default:
        renderer.rect(x - w / 2, y - h / 2, w, h, r);
        break;
    }
  }

  drawHexagon(renderer, cx, cy, radius) {
    renderer.beginShape();
    for (let i = 0; i < 6; i++) {
      const angle = (Math.PI / 3) * i - Math.PI / 6;
      const x = cx + radius * Math.cos(angle);
      const y = cy + radius * Math.sin(angle);
      renderer.vertex(x, y);
    }
    renderer.endShape(true);
  }

  onInteract(type, data) {
    super.onInteract(type, data);
    
    if (type === 'tap' || type === 'click') {
      this.setState({ selected: !this.state.selected });
    }
    if (type === 'hover_enter') {
      this.setState({ highlighted: true });
    }
    if (type === 'hover_leave') {
      this.setState({ highlighted: false });
    }
  }
}

export default Entity;
