/**
 * 🎨 UNIVERSAL SKETCH RENDERER
 * =============================
 * 
 * The core SVG renderer for Magic Notebook Engine V6
 * 
 * Features:
 * - Consumes JSON blueprints
 * - RoughJS hand-drawn aesthetics
 * - Framer Motion pathLength animations
 * - Layered rendering (background → shapes → connections → labels → doodles)
 * - Automatic layout fallback
 * - Performance optimized with memoization
 * 
 * This is the FOUNDATION. Everything else builds on top of this.
 */

import React, { useMemo, useCallback, useRef, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Sketch Primitives
import {
  SketchCircle,
  SketchRect,
  SketchArrow,
  SketchLabel,
  SketchHighlight,
  SketchStickFigure,
  SketchDoodle,
  SketchLine,
  SketchPath,
  TypewriterLabel,
  PulseHighlight,
  GlowEffect,
  SketchFilters,
  NOTEBOOK_THEME,
} from '../sketch/SketchPrimitives';

// Reveal Timing
import { TIMING } from '../sketch/RevealSequenceEngine';

// Blueprint Schema
import { validateBlueprint } from './BlueprintSchema';

// Engine Context
import { useEngine } from './EngineContext';

// ============================================
// CONSTANTS
// ============================================

const DEFAULT_VIEWBOX = { width: 400, height: 300 };
const DEFAULT_PADDING = 20;

// ============================================
// AUTO-LAYOUT HELPER
// ============================================

/**
 * Calculate positions for items that don't have explicit positions
 * Simple horizontal flow layout
 */
function autoLayoutItems(items, viewBox = DEFAULT_VIEWBOX) {
  if (!items || items.length === 0) return [];
  
  const { width, height } = viewBox;
  const padding = DEFAULT_PADDING;
  const availableWidth = width - padding * 2;
  const spacing = items.length > 1 ? availableWidth / (items.length - 1) : 0;
  
  return items.map((item, index) => {
    // If item already has position, keep it
    if (item.position) {
      return item;
    }
    
    // Auto-calculate position
    const x = items.length === 1 
      ? width / 2 
      : padding + index * spacing;
    const y = height / 2;
    
    return {
      ...item,
      position: { x, y },
    };
  });
}

// ============================================
// LAYER RENDERER COMPONENTS
// ============================================

/**
 * Background Layer - Highlights
 */
const BackgroundLayer = React.memo(({ highlights, items, useTypewriter }) => {
  if (!highlights || highlights.length === 0) return null;
  
  return (
    <g className="layer-background">
      {highlights.map((hlId, i) => {
        const item = items.find(it => it.id === hlId || it.label === hlId);
        if (!item || !item.position) return null;
        
        const { x, y } = item.position;
        const width = item.width || 100;
        const height = item.height || 50;
        
        return (
          <SketchHighlight
            key={`hl-${i}`}
            x={x - width / 2}
            y={y - height / 2}
            width={width}
            height={height}
            delay={TIMING.HIGHLIGHTS + i * 0.1}
          />
        );
      })}
    </g>
  );
});

BackgroundLayer.displayName = 'BackgroundLayer';

/**
 * Shapes Layer - Circles, Rectangles, Paths
 */
const ShapesLayer = React.memo(({ items }) => {
  if (!items || items.length === 0) return null;
  
  return (
    <g className="layer-shapes">
      {items.map((item, i) => {
        if (!item.position) return null;
        
        const { x, y } = item.position;
        const delay = TIMING.SHAPES + i * 0.15;
        
        // Circle
        if (item.type === 'circle') {
          return (
            <g key={`item-${i}`} transform={`translate(${x}, ${y})`}>
              <SketchCircle
                cx={0}
                cy={0}
                radius={item.radius || 40}
                fill={item.fill || 'transparent'}
                stroke={item.stroke || NOTEBOOK_THEME.pencilGray}
                delay={delay}
              />
            </g>
          );
        }
        
        // Rectangle / Node
        if (item.type === 'rect' || item.type === 'node') {
          const width = item.width || 80;
          const height = item.height || 50;
          
          return (
            <g key={`item-${i}`} transform={`translate(${x - width/2}, ${y - height/2})`}>
              <SketchRect
                x={0}
                y={0}
                width={width}
                height={height}
                fill={item.fill || 'transparent'}
                stroke={item.stroke || NOTEBOOK_THEME.pencilGray}
                delay={delay}
              />
            </g>
          );
        }
        
        // Custom Path
        if (item.type === 'path' && item.d) {
          return (
            <SketchPath
              key={`item-${i}`}
              d={item.d}
              fill={item.fill || 'none'}
              stroke={item.stroke || NOTEBOOK_THEME.pencilGray}
              delay={delay}
            />
          );
        }
        
        return null;
      })}
    </g>
  );
});

ShapesLayer.displayName = 'ShapesLayer';

/**
 * Connections Layer - Arrows
 */
const ConnectionsLayer = React.memo(({ arrows, items }) => {
  if (!arrows || arrows.length === 0) return null;
  
  const findItem = (id) => items.find(item => item.id === id || item.label === id);
  
  return (
    <g className="layer-connections">
      {arrows.map((arrow, i) => {
        const fromItem = findItem(arrow.from);
        const toItem = findItem(arrow.to);
        
        if (!fromItem || !toItem || !fromItem.position || !toItem.position) {
          return null;
        }
        
        const { x: x1, y: y1 } = fromItem.position;
        const { x: x2, y: y2 } = toItem.position;
        
        // Offset arrows to not overlap with shapes
        const offsetX = 45;
        const adjustedX1 = x1 + (x2 > x1 ? offsetX : -offsetX);
        const adjustedX2 = x2 + (x2 > x1 ? -offsetX : offsetX);
        
        const strokeColor = arrow.style === 'energy' 
          ? NOTEBOOK_THEME.highlightOrange 
          : NOTEBOOK_THEME.markerBlue;
        
        return (
          <SketchArrow
            key={`arrow-${i}`}
            x1={adjustedX1}
            y1={y1}
            x2={adjustedX2}
            y2={y2}
            stroke={strokeColor}
            label={arrow.label}
            curved={arrow.curved}
            delay={TIMING.CONNECTIONS + i * 0.15}
          />
        );
      })}
    </g>
  );
});

ConnectionsLayer.displayName = 'ConnectionsLayer';

/**
 * Labels Layer - Text
 */
const LabelsLayer = React.memo(({ labels, items, useTypewriter }) => {
  if (!labels || labels.length === 0) return null;
  
  return (
    <g className="layer-labels">
      {/* Item labels */}
      {items.map((item, i) => {
        if (!item.label || !item.position) return null;
        
        const { x, y } = item.position;
        const LabelComponent = (useTypewriter && item.typewriter !== false) 
          ? TypewriterLabel 
          : SketchLabel;
        
        return (
          <LabelComponent
            key={`item-label-${i}`}
            x={x}
            y={y + 5}
            text={item.label}
            delay={TIMING.LABELS + i * 0.1}
          />
        );
      })}
      
      {/* Additional labels */}
      {labels.map((lbl, i) => {
        const LabelComponent = (useTypewriter && lbl.typewriter !== false) 
          ? TypewriterLabel 
          : SketchLabel;
        
        return (
          <LabelComponent
            key={`lbl-${i}`}
            x={lbl.x || 200}
            y={lbl.y || 50}
            text={lbl.text}
            fontSize={lbl.fontSize || 18}
            color={lbl.color || NOTEBOOK_THEME.penBlack}
            underline={lbl.underline}
            delay={TIMING.LABELS + items.length * 0.1 + i * 0.1}
          />
        );
      })}
    </g>
  );
});

LabelsLayer.displayName = 'LabelsLayer';

/**
 * Figures Layer - Stick Figures
 */
const FiguresLayer = React.memo(({ figures }) => {
  if (!figures || figures.length === 0) return null;
  
  return (
    <g className="layer-figures">
      {figures.map((fig, i) => (
        <SketchStickFigure
          key={`fig-${i}`}
          x={fig.x || 100}
          y={fig.y || 150}
          size={fig.size || 60}
          pose={fig.pose || 'standing'}
          expression={fig.expression || 'neutral'}
          delay={TIMING.SHAPES + 0.2 + i * 0.15}
        />
      ))}
    </g>
  );
});

FiguresLayer.displayName = 'FiguresLayer';

/**
 * Doodles Layer - Decorative Elements
 */
const DoodlesLayer = React.memo(({ doodles }) => {
  if (!doodles || doodles.length === 0) return null;
  
  return (
    <g className="layer-doodles">
      {doodles.map((doodle, i) => (
        <SketchDoodle
          key={`doodle-${i}`}
          x={doodle.x || 350}
          y={doodle.y || 50}
          type={doodle.type || 'sparkle'}
          size={doodle.size || 25}
          color={doodle.color || NOTEBOOK_THEME.highlightYellow}
          delay={TIMING.DOODLES + i * 0.1}
        />
      ))}
    </g>
  );
});

DoodlesLayer.displayName = 'DoodlesLayer';

// ============================================
// MAIN RENDERER COMPONENT
// ============================================

const UniversalSketchRenderer = ({
  // Core Props
  blueprint = null,
  
  // Display Options
  width = '100%',
  height = 400,
  viewBox = DEFAULT_VIEWBOX,
  preserveAspectRatio = 'xMidYMid meet',
  
  // Animation Options
  useTypewriter = true,
  autoPlay = true,
  
  // Callbacks
  onRenderComplete = null,
  onLayerComplete = null,
  
  // Styling
  className = '',
  style = {},
}) => {
  const svgRef = useRef(null);
  const [renderStartTime] = useState(Date.now());
  const [isRendered, setIsRendered] = useState(false);
  
  // Try to use engine context if available (optional)
  let engineContext = null;
  try {
    engineContext = useEngine();
  } catch (e) {
    // Not in EngineProvider, that's okay
  }
  
  // ============================================
  // BLUEPRINT VALIDATION & PROCESSING
  // ============================================
  
  const validatedBlueprint = useMemo(() => {
    if (!blueprint) return null;
    
    const validation = validateBlueprint(blueprint);
    if (!validation.valid) {
      console.warn('Blueprint validation errors:', validation.errors);
    }
    
    return blueprint;
  }, [blueprint]);
  
  // Auto-layout items without positions
  const processedItems = useMemo(() => {
    if (!validatedBlueprint?.items) return [];
    return autoLayoutItems(validatedBlueprint.items, viewBox);
  }, [validatedBlueprint, viewBox]);
  
  // ============================================
  // LAYER DATA
  // ============================================
  
  const layers = useMemo(() => ({
    highlights: validatedBlueprint?.highlights || [],
    items: processedItems,
    arrows: validatedBlueprint?.arrows || [],
    labels: validatedBlueprint?.labels || [],
    figures: validatedBlueprint?.figures || [],
    doodles: validatedBlueprint?.doodles || [],
  }), [validatedBlueprint, processedItems]);
  
  // ============================================
  // RENDER COMPLETE CALLBACK
  // ============================================
  
  useEffect(() => {
    if (!isRendered && validatedBlueprint) {
      // Calculate total animation time
      const totalTime = TIMING.INTERACTIVE * 1000 + 500;
      
      const timer = setTimeout(() => {
        setIsRendered(true);
        
        const renderTime = Date.now() - renderStartTime;
        
        // Update engine context if available
        if (engineContext) {
          engineContext.setRenderTime(renderTime);
          engineContext.enableInteraction();
        }
        
        // Call callback
        onRenderComplete?.({ renderTime, blueprint: validatedBlueprint });
      }, totalTime);
      
      return () => clearTimeout(timer);
    }
  }, [isRendered, validatedBlueprint, renderStartTime, engineContext, onRenderComplete]);
  
  // ============================================
  // RENDER
  // ============================================
  
  if (!validatedBlueprint) {
    return (
      <div 
        className={`universal-sketch-renderer empty ${className}`}
        style={{ width, height, ...style }}
      >
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          fontFamily: NOTEBOOK_THEME.handwriting,
          color: NOTEBOOK_THEME.pencilGray,
          fontSize: '18px',
        }}>
          No blueprint provided
        </div>
      </div>
    );
  }
  
  return (
    <div 
      className={`universal-sketch-renderer ${className}`}
      style={{ width, height, position: 'relative', ...style }}
    >
      <svg
        ref={svgRef}
        width="100%"
        height="100%"
        viewBox={`0 0 ${viewBox.width} ${viewBox.height}`}
        preserveAspectRatio={preserveAspectRatio}
        style={{ display: 'block' }}
      >
        {/* Filter Definitions */}
        <SketchFilters />
        
        {/* Layered Rendering (Order Matters!) */}
        <BackgroundLayer 
          highlights={layers.highlights} 
          items={layers.items}
        />
        
        <ShapesLayer 
          items={layers.items}
        />
        
        <FiguresLayer 
          figures={layers.figures}
        />
        
        <ConnectionsLayer 
          arrows={layers.arrows} 
          items={layers.items}
        />
        
        <LabelsLayer 
          labels={layers.labels} 
          items={layers.items}
          useTypewriter={useTypewriter}
        />
        
        <DoodlesLayer 
          doodles={layers.doodles}
        />
      </svg>
      
      {/* Mode Badge */}
      {validatedBlueprint.mode && (
        <div
          style={{
            position: 'absolute',
            bottom: '8px',
            right: '8px',
            padding: '4px 12px',
            background: NOTEBOOK_THEME.highlightBlue,
            borderRadius: '12px',
            fontFamily: NOTEBOOK_THEME.handwriting,
            fontSize: '12px',
            opacity: 0.8,
            pointerEvents: 'none',
          }}
        >
          {validatedBlueprint.mode}
        </div>
      )}
    </div>
  );
};

// ============================================
// EXPORTS
// ============================================

export default UniversalSketchRenderer;

