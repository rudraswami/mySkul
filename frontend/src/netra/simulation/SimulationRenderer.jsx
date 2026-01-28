/**
 * 🎬 SIMULATION RENDERER
 * ======================
 * 
 * React component that renders a SimulationRuntime.
 * Handles:
 * - Canvas rendering
 * - Entity drawing with templates
 * - Idle animations
 * - Interaction controls
 * - Narration display synced to events
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { createSimulationRuntime } from './SimulationRuntime';
import { compileScript, createPlaceholderScene } from './ScriptCompiler';
import { ENTITY_TEMPLATES } from './EntityTemplates';

// ============================================
// ENTITY RENDERER
// ============================================

function renderEntity(ctx, entity, palette) {
  const { position, style, size, shape, label, state: entityState } = entity;
  
  if (!entityState.visible || entityState.opacity <= 0) return;
  
  ctx.save();
  
  // Apply transforms
  ctx.translate(position.x, position.y);
  
  // Apply scale (from state or idle animation)
  const scale = (entityState.scale || 1) * (entity.breatheScale || 1) * (entity.pulseScale || 1);
  ctx.scale(scale, scale);
  
  // Apply rotation
  if (entityState.rotation) {
    ctx.rotate(entityState.rotation);
  }
  
  // Apply opacity
  ctx.globalAlpha = entityState.opacity || 1;
  
  // Apply idle float offset
  const yOffset = entity.idleOffset || 0;
  ctx.translate(0, yOffset);
  
  // Draw highlight glow if highlighted
  if (entityState.highlighted || entity.glowIntensity > 0) {
    const glowIntensity = entity.glowIntensity || 0.5;
    ctx.shadowColor = style.fill || palette.primary;
    ctx.shadowBlur = 20 * glowIntensity;
  }
  
  // Draw based on shape
  const halfWidth = (size?.width || 60) / 2;
  const halfHeight = (size?.height || 60) / 2;
  
  switch (shape) {
    case 'circle':
    case 'ellipse':
      drawEllipse(ctx, 0, 0, halfWidth * 2, halfHeight * 2, style);
      break;
      
    case 'rect':
    case 'rounded_rect':
      drawRect(ctx, -halfWidth, -halfHeight, halfWidth * 2, halfHeight * 2, style);
      break;
      
    case 'arrow':
      drawArrow(ctx, 0, 0, halfWidth * 2, style);
      break;
      
    case 'line':
      drawLine(ctx, -halfWidth, 0, halfWidth, 0, style);
      break;
      
    case 'text':
      drawText(ctx, label || '', 0, 0, style);
      break;
      
    case 'pill':
      drawPill(ctx, 0, 0, halfWidth * 2, halfHeight * 2, style, label);
      break;
      
    case 'progress':
      drawProgressBar(ctx, -halfWidth, -halfHeight / 2, halfWidth * 2, halfHeight, style, entity.properties?.value || 0.5);
      break;
      
    default:
      // Default: draw ellipse
      drawEllipse(ctx, 0, 0, halfWidth * 2, halfHeight * 2, style);
  }
  
  // Draw label if present and not text shape
  if (label && shape !== 'text' && shape !== 'pill') {
    ctx.shadowBlur = 0;
    ctx.fillStyle = style.labelColor || '#FFFFFF';
    ctx.font = `${style.fontSize || 14}px Inter, system-ui, sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, 0, 0);
  }
  
  ctx.restore();
}

function drawEllipse(ctx, x, y, w, h, style) {
  ctx.beginPath();
  ctx.ellipse(x, y, w / 2, h / 2, 0, 0, Math.PI * 2);
  
  if (style.fill) {
    if (style.gradient === 'radial') {
      const gradient = ctx.createRadialGradient(x - w/4, y - h/4, 0, x, y, w/2);
      gradient.addColorStop(0, lightenColor(style.fill, 30));
      gradient.addColorStop(1, style.fill);
      ctx.fillStyle = gradient;
    } else {
      ctx.fillStyle = style.fill;
    }
    ctx.fill();
  }
  
  if (style.stroke) {
    ctx.strokeStyle = style.stroke;
    ctx.lineWidth = style.strokeWidth || 2;
    ctx.stroke();
  }
}

function drawRect(ctx, x, y, w, h, style) {
  const radius = style.rounded || 0;
  
  ctx.beginPath();
  if (radius > 0) {
    ctx.roundRect(x, y, w, h, radius);
  } else {
    ctx.rect(x, y, w, h);
  }
  
  if (style.fill) {
    ctx.fillStyle = applyOpacity(style.fill, style.fillOpacity || 1);
    ctx.fill();
  }
  
  if (style.stroke) {
    ctx.strokeStyle = style.stroke;
    ctx.lineWidth = style.strokeWidth || 2;
    if (style.dash) {
      ctx.setLineDash(style.dash);
    }
    ctx.stroke();
    ctx.setLineDash([]);
  }
}

function drawArrow(ctx, x, y, length, style) {
  const headLength = 12;
  
  ctx.beginPath();
  ctx.moveTo(x - length/2, y);
  ctx.lineTo(x + length/2 - headLength, y);
  
  ctx.strokeStyle = style.stroke || style.fill;
  ctx.lineWidth = style.strokeWidth || 3;
  ctx.stroke();
  
  // Arrow head
  ctx.beginPath();
  ctx.moveTo(x + length/2, y);
  ctx.lineTo(x + length/2 - headLength, y - 6);
  ctx.lineTo(x + length/2 - headLength, y + 6);
  ctx.closePath();
  ctx.fillStyle = style.fill || style.stroke;
  ctx.fill();
}

function drawLine(ctx, x1, y1, x2, y2, style) {
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.strokeStyle = style.stroke || '#666';
  ctx.lineWidth = style.strokeWidth || 2;
  if (style.dash) {
    ctx.setLineDash(style.dash);
  }
  ctx.stroke();
  ctx.setLineDash([]);
}

function drawText(ctx, text, x, y, style) {
  ctx.font = `${style.fontWeight || 'normal'} ${style.fontSize || 14}px ${style.fontFamily || 'Inter, system-ui, sans-serif'}`;
  ctx.fillStyle = style.color || '#1E293B';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, x, y);
}

function drawPill(ctx, x, y, w, h, style, label) {
  const radius = h / 2;
  
  ctx.beginPath();
  ctx.roundRect(x - w/2, y - h/2, w, h, radius);
  
  ctx.fillStyle = applyOpacity(style.fill, style.fillOpacity || 0.2);
  ctx.fill();
  
  ctx.strokeStyle = style.stroke || style.fill;
  ctx.lineWidth = style.strokeWidth || 1;
  ctx.stroke();
  
  if (label) {
    ctx.fillStyle = style.color || style.fill;
    ctx.font = `${style.fontWeight || 'medium'} ${style.fontSize || 12}px Inter, system-ui, sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, x, y);
  }
}

function drawProgressBar(ctx, x, y, w, h, style, value) {
  const radius = style.rounded || h / 2;
  
  // Track
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, radius);
  ctx.fillStyle = style.trackFill || '#E2E8F0';
  ctx.fill();
  
  // Fill
  const fillWidth = w * Math.max(0, Math.min(1, value));
  if (fillWidth > 0) {
    ctx.beginPath();
    ctx.roundRect(x, y, fillWidth, h, radius);
    ctx.fillStyle = style.fill || '#3B82F6';
    ctx.fill();
  }
}

function lightenColor(hex, percent) {
  const num = parseInt(hex.replace('#', ''), 16);
  const amt = Math.round(2.55 * percent);
  const R = Math.min(255, (num >> 16) + amt);
  const G = Math.min(255, ((num >> 8) & 0x00FF) + amt);
  const B = Math.min(255, (num & 0x0000FF) + amt);
  return `#${(1 << 24 | R << 16 | G << 8 | B).toString(16).slice(1)}`;
}

function applyOpacity(color, opacity) {
  if (opacity >= 1) return color;
  const hex = color.replace('#', '');
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

// ============================================
// NARRATION DISPLAY
// ============================================

const NarrationDisplay = ({ text, visible }) => {
  if (!visible || !text) return null;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="absolute bottom-4 left-4 right-4 p-4 rounded-xl bg-white/95 shadow-lg border border-gray-200 backdrop-blur-sm"
    >
      <p className="text-sm md:text-base text-gray-800 leading-relaxed font-medium">
        {text}
      </p>
    </motion.div>
  );
};

// ============================================
// INTERACTION CONTROLS
// ============================================

const InteractionControls = ({ interactions, constants, onConstantChange }) => {
  if (!interactions || interactions.length === 0) return null;
  
  return (
    <div className="absolute top-4 right-4 flex flex-col gap-3 bg-white/95 backdrop-blur-sm rounded-xl p-4 shadow-lg border border-gray-200 min-w-[180px]">
      <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Controls</div>
      {interactions.map(interaction => {
        const constDef = constants[interaction.target];
        if (!constDef) return null;
        
        if (interaction.type === 'slider') {
          return (
            <div key={interaction.id} className="flex flex-col gap-1.5">
              <div className="flex justify-between items-center">
                <label className="text-sm font-medium text-gray-700">
                  {interaction.label || interaction.target}
                </label>
                <span className="text-sm text-gray-500 font-mono">
                  {constDef.value?.toFixed?.(2) || constDef.value}
                  {constDef.unit && ` ${constDef.unit}`}
                </span>
              </div>
              <input
                type="range"
                min={constDef.min || 0}
                max={constDef.max || 100}
                step={constDef.step || 0.1}
                defaultValue={constDef.value}
                onChange={(e) => onConstantChange(interaction.target, parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
            </div>
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

const SimulationRenderer = ({
  script,
  width = 800,
  height = 600,
  className = '',
  style = {},
  onReady,
  onNarration,
  onStateChange,
  autoStart = true
}) => {
  const canvasRef = useRef(null);
  const runtimeRef = useRef(null);
  const animationRef = useRef(null);
  
  const [isReady, setIsReady] = useState(false);
  const [narration, setNarration] = useState({ text: null, visible: false });
  const [currentState, setCurrentState] = useState('idle');
  const [constants, setConstants] = useState({});
  const [error, setError] = useState(null);
  
  // Initialize runtime
  useEffect(() => {
    if (!script || !canvasRef.current) return;
    
    console.log('[SimulationRenderer] Initializing with script:', script.ontology, script.world);
    
    try {
      // Compile script if needed
      const compiledScene = script._compiled ? script : compileScript(script, { width, height });
      
      // Create runtime
      const runtime = createSimulationRuntime(compiledScene, { width, height });
      runtimeRef.current = runtime;
      
      // Store constants for controls
      setConstants(script.constants || {});
      
      // Subscribe to events
      runtime.events.on('tick', () => {
        // Trigger re-render
        renderFrame();
      });
      
      runtime.events.on('state_change', ({ from, to }) => {
        setCurrentState(to);
        onStateChange?.({ from, to });
      });
      
      // Subscribe to narration events
      (script.narration || []).forEach(narr => {
        if (narr.event === 'start') {
          // Show intro narration immediately
          setTimeout(() => {
            setNarration({ text: narr.text, visible: true });
            onNarration?.(narr);
          }, 500);
          setTimeout(() => setNarration(prev => ({ ...prev, visible: false })), 5000);
        } else {
          // Subscribe to specific events
          runtime.events.on(narr.event, () => {
            setNarration({ text: narr.text, visible: true });
            onNarration?.(narr);
            setTimeout(() => setNarration(prev => ({ ...prev, visible: false })), 5000);
          });
        }
      });
      
      // Start if autoStart
      if (autoStart) {
        runtime.start();
      }
      
      setIsReady(true);
      onReady?.();
      
      // Initial render
      renderFrame();
      
    } catch (err) {
      console.error('[SimulationRenderer] Initialization error:', err);
      setError(err.message);
    }
    
    // Cleanup
    return () => {
      if (runtimeRef.current) {
        runtimeRef.current.destroy();
      }
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [script, width, height, autoStart]);
  
  // Render frame
  const renderFrame = useCallback(() => {
    if (!canvasRef.current || !runtimeRef.current) return;
    
    const ctx = canvasRef.current.getContext('2d');
    const { entities, palette, backgroundGradient } = runtimeRef.current.getRenderState();
    
    // Clear and draw background
    ctx.clearRect(0, 0, width, height);
    
    // Draw gradient background
    if (backgroundGradient && backgroundGradient.length >= 2) {
      const gradient = ctx.createLinearGradient(0, 0, 0, height);
      gradient.addColorStop(0, backgroundGradient[0]);
      gradient.addColorStop(1, backgroundGradient[1]);
      ctx.fillStyle = gradient;
    } else {
      ctx.fillStyle = '#F8FAFC';
    }
    ctx.fillRect(0, 0, width, height);
    
    // Sort by z-index (if present)
    const sortedEntities = [...entities].sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0));
    
    // Render entities
    sortedEntities.forEach(entity => {
      renderEntity(ctx, entity, palette);
    });
  }, [width, height]);
  
  // Handle constant changes from controls
  const handleConstantChange = useCallback((name, value) => {
    if (runtimeRef.current) {
      runtimeRef.current.setConstant(name, value);
      setConstants(prev => ({
        ...prev,
        [name]: { ...prev[name], value }
      }));
    }
  }, []);
  
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
      className={`relative overflow-hidden rounded-xl ${className}`}
      style={{ width, height, ...style }}
    >
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="cursor-pointer"
        style={{ display: 'block' }}
      />
      
      {/* Interaction Controls */}
      <InteractionControls
        interactions={script?.interactions}
        constants={constants}
        onConstantChange={handleConstantChange}
      />
      
      {/* Narration Display */}
      <AnimatePresence>
        {narration.visible && (
          <NarrationDisplay
            text={narration.text}
            visible={narration.visible}
          />
        )}
      </AnimatePresence>
      
      {/* State indicator (dev) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="absolute top-4 left-4 bg-black/60 text-white text-xs px-2 py-1 rounded font-mono">
          State: {currentState}
        </div>
      )}
      
      {/* Loading indicator */}
      {!isReady && (
        <div className="absolute inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm">
          <div className="flex flex-col items-center gap-3">
            <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-gray-600 font-medium">Preparing simulation...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default SimulationRenderer;
export { SimulationRenderer };
