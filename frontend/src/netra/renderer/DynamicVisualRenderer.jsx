/**
 * 🎬 DYNAMIC VISUAL RENDERER
 * ===========================
 * 
 * Main renderer for NETRA compositions.
 * 
 * Uses pluggable RendererAdapter pattern:
 * - CanvasAdapter (p5.js) - default
 * - Future: PixiAdapter, ThreeAdapter
 * 
 * Integrates:
 * - AtomRegistry for atom instantiation
 * - BehaviorEngine for event-driven rules
 * - NarrationEngine for synced text
 * - Physics (Matter.js) when enabled
 */

import React, { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { createAtom } from '../atoms/AtomRegistry';
import { createBehaviorEngine } from '../engine/BehaviorEngine';
import { createNarrationEngine } from '../engine/NarrationEngine';

// ============================================
// CANVAS RENDERER ADAPTER (p5.js style)
// ============================================

class CanvasRendererAdapter {
  constructor(canvas, width, height) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.width = width;
    this.height = height;
  }

  // Drawing state
  push() {
    this.ctx.save();
  }

  pop() {
    this.ctx.restore();
  }

  // Transforms
  translate(x, y) {
    this.ctx.translate(x, y);
  }

  rotate(angle) {
    this.ctx.rotate(angle);
  }

  scale(sx, sy) {
    this.ctx.scale(sx, sy ?? sx);
  }

  // Colors
  fill(color, opacity = 1) {
    if (typeof color === 'number') {
      // Grayscale
      this.ctx.fillStyle = `rgba(${color}, ${color}, ${color}, ${opacity})`;
    } else if (color) {
      this.ctx.fillStyle = this.applyOpacity(color, opacity);
    }
  }

  stroke(color, opacity = 1) {
    if (typeof color === 'number') {
      this.ctx.strokeStyle = `rgba(${color}, ${color}, ${color}, ${opacity})`;
    } else if (color) {
      this.ctx.strokeStyle = this.applyOpacity(color, opacity);
    }
  }

  strokeWeight(weight) {
    this.ctx.lineWidth = weight;
  }

  noFill() {
    this.ctx.fillStyle = 'transparent';
  }

  noStroke() {
    this.ctx.strokeStyle = 'transparent';
  }

  applyOpacity(color, opacity) {
    if (opacity >= 1) return color;
    if (color.startsWith('#')) {
      const r = parseInt(color.slice(1, 3), 16);
      const g = parseInt(color.slice(3, 5), 16);
      const b = parseInt(color.slice(5, 7), 16);
      return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    }
    if (color.startsWith('rgb(')) {
      return color.replace('rgb(', 'rgba(').replace(')', `, ${opacity})`);
    }
    return color;
  }

  // Shapes
  rect(x, y, w, h, r = 0) {
    this.ctx.beginPath();
    if (r > 0) {
      this.ctx.roundRect(x, y, w, h, r);
    } else {
      this.ctx.rect(x, y, w, h);
    }
    this.ctx.fill();
    this.ctx.stroke();
  }

  ellipse(x, y, w, h) {
    this.ctx.beginPath();
    this.ctx.ellipse(x, y, w / 2, h / 2, 0, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.stroke();
  }

  line(x1, y1, x2, y2) {
    this.ctx.beginPath();
    this.ctx.moveTo(x1, y1);
    this.ctx.lineTo(x2, y2);
    this.ctx.stroke();
  }

  triangle(x1, y1, x2, y2, x3, y3) {
    this.ctx.beginPath();
    this.ctx.moveTo(x1, y1);
    this.ctx.lineTo(x2, y2);
    this.ctx.lineTo(x3, y3);
    this.ctx.closePath();
    this.ctx.fill();
    this.ctx.stroke();
  }

  beginShape() {
    this.ctx.beginPath();
    this._shapeStarted = true;
  }

  vertex(x, y) {
    if (!this._firstVertex) {
      this.ctx.moveTo(x, y);
      this._firstVertex = true;
    } else {
      this.ctx.lineTo(x, y);
    }
  }

  quadraticVertex(cpx, cpy, x, y) {
    this.ctx.quadraticCurveTo(cpx, cpy, x, y);
  }

  endShape(close) {
    if (close) this.ctx.closePath();
    this.ctx.fill();
    this.ctx.stroke();
    this._shapeStarted = false;
    this._firstVertex = false;
  }

  // Text
  text(str, x, y) {
    this.ctx.fillText(str, x, y);
  }

  textSize(size) {
    const font = this.ctx.font;
    this.ctx.font = font.replace(/\d+px/, `${size}px`);
  }

  textFont(family) {
    const size = this.ctx.font.match(/\d+px/)?.[0] || '14px';
    this.ctx.font = `${size} ${family}`;
  }

  textAlign(hAlign, vAlign) {
    this.ctx.textAlign = hAlign === 'center' ? 'center' : hAlign === 'right' ? 'right' : 'left';
    this.ctx.textBaseline = vAlign === 'center' ? 'middle' : vAlign === 'bottom' ? 'bottom' : 'top';
  }

  textStyle(style) {
    const font = this.ctx.font;
    if (style === 'bold') {
      this.ctx.font = 'bold ' + font.replace('bold ', '');
    } else {
      this.ctx.font = font.replace('bold ', '');
    }
  }

  // Access to raw context
  get drawingContext() {
    return this.ctx;
  }

  // Clear
  clear() {
    this.ctx.clearRect(0, 0, this.width, this.height);
  }

  // Background
  background(color) {
    this.ctx.fillStyle = color;
    this.ctx.fillRect(0, 0, this.width, this.height);
  }

  // Gradient background
  gradientBackground(colors, direction = 'vertical') {
    const gradient = direction === 'vertical'
      ? this.ctx.createLinearGradient(0, 0, 0, this.height)
      : this.ctx.createLinearGradient(0, 0, this.width, 0);
    
    colors.forEach((color, i) => {
      gradient.addColorStop(i / (colors.length - 1), color);
    });
    
    this.ctx.fillStyle = gradient;
    this.ctx.fillRect(0, 0, this.width, this.height);
  }
}

// ============================================
// SCENE MANAGER
// ============================================

class Scene {
  constructor(composition, options = {}) {
    this.composition = composition;
    this.atoms = new Map();
    this.physicsWorld = null;
    this.behaviorEngine = createBehaviorEngine();
    this.narrationEngine = createNarrationEngine();
    this.running = false;
    this.lastTime = 0;
    this.options = options;
  }

  async initialize() {
    const { atoms, behaviors, narration, stage } = this.composition;

    // Initialize physics if enabled
    if (stage.physics?.enabled && typeof window !== 'undefined') {
      await this.initializePhysics(stage.physics);
    }

    // NOTE: Scene enhancement (scaling, positioning) is now handled by SceneEnhancer
    // in VisualComposer BEFORE the composition reaches this renderer.
    // This ensures atoms are already properly sized and positioned.

    // Create atoms
    for (const atomDef of atoms) {
      // 🧬 CRITICAL: Merge generator fields into params if they're at root level
      // LLM often outputs generator at root, but Entity expects it in params
      const generatorField = atomDef.params?.generator || atomDef.generator;
      const generatorParamsField = atomDef.params?.generatorParams || atomDef.generatorParams;
      
      if (generatorField) {
        console.log(`🧬 [Scene] Atom ${atomDef.id} has generator: ${generatorField}`);
      }
      
      const mergedParams = {
        ...atomDef.params,
        // Preserve any generator in params, but also check root level
        generator: generatorField,
        generatorParams: generatorParamsField,
      };
      
      const atom = createAtom(atomDef.type, atomDef.id, mergedParams);
      
      // Also set at instance level for backwards compatibility
      if (atomDef.generator && !atom.generator) {
        atom.generator = atomDef.generator;
        atom.generatorParams = atomDef.generatorParams || {};
      }
      
      if (atomDef.position) {
        atom.setPosition(atomDef.position.x, atomDef.position.y);
      }
      
      if (atomDef.attachedTo) {
        atom.attachedTo = atomDef.attachedTo;
        atom.attachAnchor = atomDef.attachAnchor || 'center';
      }
      
      if (atomDef.emphasis) {
        atom.emphasis = atomDef.emphasis;
      }
      
      if (atomDef.zIndex !== undefined) {
        atom.zIndex = atomDef.zIndex;
      }

      if (atomDef.initialState) {
        atom.setState(atomDef.initialState);
      }

      atom.onMount(this);
      this.atoms.set(atomDef.id, atom);
      this.behaviorEngine.registerAtom(atom);
    }

    // Initialize behavior engine
    this.behaviorEngine.initialize(behaviors, this);

    // Initialize narration engine
    this.narrationEngine.initialize(narration, this.behaviorEngine);

    console.log(`[Scene] ✅ Initialized with ${this.atoms.size} atoms`);
  }

  async initializePhysics(physicsConfig) {
    try {
      // Dynamically import Matter.js
      const Matter = await import('matter-js');
      window.Matter = Matter;

      const engine = Matter.Engine.create();
      
      if (physicsConfig.gravity) {
        engine.gravity.x = physicsConfig.gravity.x || 0;
        engine.gravity.y = physicsConfig.gravity.y || 1;
      }

      this.physicsWorld = engine.world;
      this.physicsEngine = engine;

      console.log('[Scene] Physics initialized');
    } catch (error) {
      console.warn('[Scene] Matter.js not available:', error.message);
    }
  }

  getAtom(id) {
    return this.atoms.get(id);
  }

  update(dt) {
    // Update physics
    if (this.physicsEngine && typeof window !== 'undefined' && window.Matter) {
      window.Matter.Engine.update(this.physicsEngine, dt);
    }

    // Update all atoms
    for (const atom of this.atoms.values()) {
      atom.update(dt);
    }
  }

  render(renderer) {
    // Sort atoms by zIndex
    const sortedAtoms = Array.from(this.atoms.values())
      .sort((a, b) => a.zIndex - b.zIndex);

    // Render each atom
    for (const atom of sortedAtoms) {
      atom.render(renderer);
    }
  }

  start() {
    this.running = true;
    this.lastTime = performance.now();
    
    // Trigger scene ready
    setTimeout(() => {
      this.behaviorEngine.handleSceneEvent('ready', {});
      this.behaviorEngine.startTimeTriggers();
      this.narrationEngine.triggerSceneReady();
    }, 100);
  }

  stop() {
    this.running = false;
  }

  handleInteraction(atomId, type, data) {
    const atom = this.atoms.get(atomId);
    if (atom) {
      atom.onInteract(type, data);
    }
    this.behaviorEngine.handleInteraction(atomId, type, data);
  }

  destroy() {
    this.stop();
    
    for (const atom of this.atoms.values()) {
      atom.onUnmount();
    }
    
    this.atoms.clear();
    this.behaviorEngine.destroy();
    this.narrationEngine.destroy();
    
    if (this.physicsEngine) {
      window.Matter?.Engine.clear(this.physicsEngine);
    }
  }
}

// ============================================
// NARRATION DISPLAY COMPONENT
// ============================================

const NarrationDisplay = ({ text, emphasis, visible }) => {
  if (!visible || !text) return null;

  const emphasisStyles = {
    normal: 'bg-white/95 text-gray-800',
    key_point: 'bg-amber-50 text-amber-900 border-amber-200',
    question: 'bg-blue-50 text-blue-900 border-blue-200'
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className={`absolute bottom-4 left-4 right-4 p-4 rounded-xl shadow-lg border backdrop-blur-sm ${emphasisStyles[emphasis] || emphasisStyles.normal}`}
    >
      <p className="text-sm md:text-base leading-relaxed font-medium">
        {emphasis === 'key_point' && <span className="mr-2">💡</span>}
        {emphasis === 'question' && <span className="mr-2">🤔</span>}
        {text}
      </p>
    </motion.div>
  );
};

// ============================================
// INTERACTION CONTROLS COMPONENT
// ============================================

const InteractionControls = ({ interactions, scene, onInteraction }) => {
  if (!interactions || interactions.length === 0) return null;

  return (
    <div className="absolute top-4 right-4 flex flex-col gap-2 bg-white/90 backdrop-blur-sm rounded-lg p-3 shadow-md">
      {interactions.map(interaction => {
        if (interaction.type === 'slider' && interaction.config) {
          const { param, min, max, step, defaultValue, unit } = interaction.config;
          return (
            <div key={interaction.id} className="flex flex-col gap-1">
              <label className="text-xs font-medium text-gray-700">
                {interaction.label || param}
              </label>
              <input
                type="range"
                min={min}
                max={max}
                step={step || 0.01}
                defaultValue={defaultValue ?? (min + max) / 2}
                onChange={(e) => {
                  onInteraction?.(interaction.target, 'slider', {
                    param,
                    value: parseFloat(e.target.value)
                  });
                }}
                className="w-32"
              />
              <span className="text-xs text-gray-500">
                {unit ? `${defaultValue ?? (min + max) / 2} ${unit}` : ''}
              </span>
            </div>
          );
        }

        if (interaction.type === 'toggle' && interaction.config) {
          return (
            <label key={interaction.id} className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                defaultChecked={false}
                onChange={(e) => {
                  onInteraction?.(interaction.target, 'toggle', {
                    param: interaction.config.param,
                    value: e.target.checked
                  });
                }}
                className="w-4 h-4"
              />
              <span className="text-xs font-medium text-gray-700">
                {interaction.label}
              </span>
            </label>
          );
        }

        return null;
      })}
    </div>
  );
};

// ============================================
// MAIN COMPONENT
// ============================================

const DynamicVisualRenderer = ({
  composition,
  width = 800,
  height = 600,
  className = '',
  style = {},
  onReady,
  onNarration,
  onInteraction,
}) => {
  const canvasRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const animationRef = useRef(null);
  
  // 🔧 FIX: Use refs for callbacks to prevent re-initialization
  const onReadyRef = useRef(onReady);
  const onNarrationRef = useRef(onNarration);
  const onInteractionRef = useRef(onInteraction);
  
  // Update refs when callbacks change (but don't trigger re-init)
  useEffect(() => {
    onReadyRef.current = onReady;
    onNarrationRef.current = onNarration;
    onInteractionRef.current = onInteraction;
  }, [onReady, onNarration, onInteraction]);
  
  // 🔧 FIX: Track initialization state to prevent duplicate inits
  const initializingRef = useRef(false);
  const initializedIdRef = useRef(null);

  const [isReady, setIsReady] = useState(false);
  const [narration, setNarration] = useState({ text: null, emphasis: 'normal', visible: false });
  const [error, setError] = useState(null);

  // Generate stable composition ID for change detection
  const compositionId = useMemo(() => {
    if (!composition) return null;
    return composition.id || composition.metadata?.questionHash || 
           `${composition.atoms?.length || 0}-${composition.behaviors?.length || 0}-${Date.now()}`;
  }, [composition]);

  // Initialize scene - ONLY when composition actually changes
  useEffect(() => {
    if (!composition || !canvasRef.current) return;
    
    // 🔧 FIX: Prevent duplicate initialization
    if (initializingRef.current) {
      console.log('[DynamicVisualRenderer] ⚠️ Already initializing, skipping...');
      return;
    }
    if (initializedIdRef.current === compositionId) {
      console.log('[DynamicVisualRenderer] ⚠️ Already initialized this composition, skipping...');
      return;
    }
    
    console.log('[DynamicVisualRenderer] 🎬 Initializing scene for:', compositionId);
    initializingRef.current = true;

    const canvas = canvasRef.current;
    const scene = new Scene(composition, { width, height });
    const renderer = new CanvasRendererAdapter(canvas, width, height);

    sceneRef.current = scene;
    rendererRef.current = renderer;

    // Initialize async
    scene.initialize().then(() => {
      initializedIdRef.current = compositionId;
      initializingRef.current = false;
      
      // Subscribe to narration events - use refs for callbacks
      scene.narrationEngine.on('narration_start', (data) => {
        setNarration({ text: data.text, emphasis: data.emphasis, visible: true });
        onNarrationRef.current?.(data);
      });

      scene.narrationEngine.on('narration_end', () => {
        setNarration(prev => ({ ...prev, visible: false }));
      });

      // Start scene
      scene.start();
      setIsReady(true);
      onReadyRef.current?.();
      console.log('[DynamicVisualRenderer] ✅ Scene ready and rendering');

      // Start render loop
      const renderLoop = (time) => {
        if (!scene.running) return;

        const dt = time - (scene.lastTime || time);
        scene.lastTime = time;

        // Clear canvas - NO BACKGROUND (transparent to show dotted grid)
        // Visual renders directly on MagicBook canvas
        const { stage } = composition;
        renderer.clear();
        
        // REMOVED: Background rendering - visuals are now transparent/full-bleed
        // If you need a background, the composition must explicitly request it
        // with stage.background.forceBackground = true
        if (stage.background?.forceBackground) {
          if (stage.background.type === 'gradient' && Array.isArray(stage.background.value)) {
            renderer.gradientBackground(stage.background.value, stage.background.direction);
          } else {
            renderer.background(stage.background.value || 'transparent');
          }
        }
        // Default: transparent - let MagicBook dotted grid show through

        // Update and render scene
        scene.update(dt);
        scene.render(renderer);

        animationRef.current = requestAnimationFrame(renderLoop);
      };

      animationRef.current = requestAnimationFrame(renderLoop);
    }).catch(err => {
      console.error('[DynamicVisualRenderer] Initialization error:', err);
      setError(err.message);
    });

    // Cleanup
    return () => {
      console.log('[DynamicVisualRenderer] 🧹 Cleaning up scene...');
      initializingRef.current = false;
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }
      scene.destroy();
    };
  // 🔧 FIX: Only depend on compositionId, width, height - NOT callback functions
  }, [compositionId, width, height]);

  // Handle canvas interactions
  const handleCanvasClick = useCallback((e) => {
    if (!sceneRef.current) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Find clicked atom
    for (const [id, atom] of sceneRef.current.atoms) {
      if (atom.containsPoint(x, y)) {
        sceneRef.current.handleInteraction(id, 'tap', { x, y });
        break;
      }
    }
  }, []);

  // Handle drag
  const handleDrag = useCallback((atomId, position) => {
    if (!sceneRef.current) return;
    sceneRef.current.handleInteraction(atomId, 'drag', { position });
    onInteraction?.(atomId, 'drag', { position });
  }, [onInteraction]);

  // Handle control interaction
  const handleControlInteraction = useCallback((atomId, type, data) => {
    if (!sceneRef.current) return;
    
    const atom = sceneRef.current.getAtom(atomId);
    if (atom) {
      if (type === 'slider' && atom.params) {
        // Update atom param
        atom.params[data.param] = data.value;
        
        // Special handling for known params
        if (data.param === 'friction' && atom.setFriction) {
          atom.setFriction(data.value);
        }
        if (data.param === 'magnitude' && atom.setMagnitude) {
          atom.setMagnitude(data.value);
        }
      }
    }
    
    onInteraction?.(atomId, type, data);
  }, [onInteraction]);

  if (error) {
    return (
      <div 
        className={`flex items-center justify-center bg-red-50 rounded-xl ${className}`}
        style={{ width, height, ...style }}
      >
        <p className="text-red-600 text-sm">Error: {error}</p>
      </div>
    );
  }

  return (
    <div 
      className={`relative overflow-visible ${className}`}
      style={{ width, height, ...style }}
    >
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        onClick={handleCanvasClick}
        className="cursor-pointer"
        style={{ display: 'block', background: 'transparent' }}
      />

      {/* Interaction Controls */}
      <InteractionControls
        interactions={composition?.interactions}
        scene={sceneRef.current}
        onInteraction={handleControlInteraction}
      />

      {/* Narration Display */}
      <AnimatePresence>
        {narration.visible && (
          <NarrationDisplay
            text={narration.text}
            emphasis={narration.emphasis}
            visible={narration.visible}
          />
        )}
      </AnimatePresence>

      {/* Loading indicator */}
      {!isReady && (
        <div className="absolute inset-0 flex items-center justify-center bg-white/80">
          <div className="flex flex-col items-center gap-2">
            <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-gray-600">Preparing visual...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default DynamicVisualRenderer;
export { DynamicVisualRenderer, Scene, CanvasRendererAdapter };
