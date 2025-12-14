/**
 * 🎨 SVG RENDERER
 * ===============
 * 
 * The main rendering engine that transforms SceneGraph into SVG.
 * 
 * Features:
 * - Domain-specific primitive rendering
 * - Hand-drawn aesthetic (pencil textures, wobble)
 * - Animation orchestration
 * - Interactive elements
 * - Layered rendering (background → shapes → arrows → labels)
 */

import React, { useMemo, useRef, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Import physics primitives
import ForceVector, { ForceSystem, ActionReactionPair } from '../primitives/physics/ForceVector';
import RigidBody from '../primitives/physics/RigidBody';

// ============================================
// THEME
// ============================================

const NETRA_THEME = {
  // Colors
  background: '#FFFEF7',              // Warm off-white
  gridColor: 'rgba(200, 200, 200, 0.3)',
  pencilGray: '#4A4A4A',
  penBlack: '#1A1A1A',
  highlightYellow: 'rgba(255, 235, 59, 0.4)',
  highlightBlue: 'rgba(33, 150, 243, 0.2)',
  
  // Typography
  handwriting: "'Kalam', 'Caveat', 'Comic Sans MS', cursive",
  technical: "'IBM Plex Mono', 'Fira Code', monospace",
  
  // Stroke
  defaultStrokeWidth: 2,
  sketchyStrokeWidth: 2.5,
};

// ============================================
// SVG FILTERS (Hand-drawn effects)
// ============================================

const SketchFilters = () => (
  <defs>
    {/* Pencil texture filter */}
    <filter id="pencil-texture" x="-5%" y="-5%" width="110%" height="110%">
      <feTurbulence
        type="fractalNoise"
        baseFrequency="0.03"
        numOctaves="3"
        result="noise"
      />
      <feDisplacementMap
        in="SourceGraphic"
        in2="noise"
        scale="1"
        xChannelSelector="R"
        yChannelSelector="G"
      />
    </filter>
    
    {/* Shadow filter */}
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="2" dy="2" stdDeviation="2" floodOpacity="0.15" />
    </filter>
    
    {/* Glow filter */}
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    {/* Arrow markers */}
    <marker
      id="arrow-head"
      markerWidth="10"
      markerHeight="7"
      refX="9"
      refY="3.5"
      orient="auto"
    >
      <polygon points="0 0, 10 3.5, 0 7" fill="#2C3E50" />
    </marker>
    
    <marker
      id="arrow-head-red"
      markerWidth="10"
      markerHeight="7"
      refX="9"
      refY="3.5"
      orient="auto"
    >
      <polygon points="0 0, 10 3.5, 0 7" fill="#E74C3C" />
    </marker>
    
    <marker
      id="arrow-head-blue"
      markerWidth="10"
      markerHeight="7"
      refX="9"
      refY="3.5"
      orient="auto"
    >
      <polygon points="0 0, 10 3.5, 0 7" fill="#3498DB" />
    </marker>
  </defs>
);

// ============================================
// BACKGROUND LAYER
// ============================================

const BackgroundLayer = ({ width, height, showGrid = true, transparent = true }) => (
  <g className="layer-background">
    {/* Main background - TRANSPARENT by default to let SmartBoard notebook show through */}
    {!transparent && (
      <rect
        x={0}
        y={0}
        width={width}
        height={height}
        fill={NETRA_THEME.background}
      />
    )}
    
    {/* Grid pattern */}
    {showGrid && (
      <g className="grid">
        {/* Vertical lines */}
        {Array.from({ length: Math.floor(width / 40) }).map((_, i) => (
          <line
            key={`v-${i}`}
            x1={(i + 1) * 40}
            y1={0}
            x2={(i + 1) * 40}
            y2={height}
            stroke={NETRA_THEME.gridColor}
            strokeWidth={0.5}
          />
        ))}
        {/* Horizontal lines */}
        {Array.from({ length: Math.floor(height / 40) }).map((_, i) => (
          <line
            key={`h-${i}`}
            x1={0}
            y1={(i + 1) * 40}
            x2={width}
            y2={(i + 1) * 40}
            stroke={NETRA_THEME.gridColor}
            strokeWidth={0.5}
          />
        ))}
      </g>
    )}
  </g>
);

// ============================================
// NODE RENDERER
// ============================================

const NodeRenderer = ({ node, domain }) => {
  const { id, x, y, width, height, entity, primitive, style, animationDelay } = node;
  
  // Render based on primitive type
  switch (primitive) {
    case 'force_vector':
      return (
        <ForceVector
          x={x}
          y={y}
          angle={style?.direction ? getAngleFromDirection(style.direction) : 0}
          magnitude={width}
          variant={style?.variant || entity.properties?.variant || 'default'}
          label={entity.label}
          animated={true}
          delay={animationDelay}
        />
      );
    
    case 'body':
      return (
        <RigidBody
          x={x}
          y={y}
          width={width}
          height={height}
          variant={entity.properties?.variant || 'block'}
          label={entity.label}
          showLabel={true}
          animated={true}
          delay={animationDelay}
        />
      );
    
    case 'ground_plane':
    case 'structure':  // Also handle 'structure' primitive for ground/surface
      // Check if it's a ground plane based on visualHint
      if (entity.properties?.visualHint === 'ground_plane') {
        return (
          <GroundPlane
            y={y}
            width={width}
            delay={animationDelay}
          />
        );
      }
      // Otherwise render as a generic structure box
      return (
        <StructureBox
          x={x}
          y={y}
          width={width}
          height={height}
          label={entity.label}
          delay={animationDelay}
        />
      );
    
    case 'cell':
      return (
        <CellDiagram
          x={x}
          y={y}
          width={width}
          height={height}
          variant={entity.properties?.variant || 'animal'}
          label={entity.label}
          delay={animationDelay}
        />
      );
    
    case 'atom':
      return (
        <AtomDiagram
          x={x}
          y={y}
          size={width}
          element={entity.label}
          delay={animationDelay}
        />
      );
    
    case 'graph':
      return (
        <GraphPlot
          x={x}
          y={y}
          width={width}
          height={height}
          delay={animationDelay}
        />
      );
    
    case 'process_box':
      return (
        <ProcessBox
          x={x}
          y={y}
          width={width}
          height={height}
          label={entity.label}
          delay={animationDelay}
        />
      );
    
    // Default: generic shape
    default:
      return (
        <GenericShape
          x={x}
          y={y}
          width={width}
          height={height}
          label={entity.label}
          delay={animationDelay}
        />
      );
  }
};

// Helper: Get angle from direction string
const getAngleFromDirection = (direction) => {
  const directionAngles = {
    'up': -90,
    'down': 90,
    'left': 180,
    'right': 0,
    'up-left': -135,
    'up-right': -45,
    'down-left': 135,
    'down-right': 45,
  };
  return directionAngles[direction] || 0;
};

// ============================================
// SIMPLIFIED PRIMITIVES (Placeholders)
// ============================================

const GroundPlane = ({ y, width, delay = 0 }) => (
  <motion.g
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    transition={{ delay }}
  >
    <line
      x1={0}
      y1={y}
      x2={width}
      y2={y}
      stroke="#2C3E50"
      strokeWidth={3}
    />
    {/* Hatching */}
    {Array.from({ length: Math.floor(width / 15) }).map((_, i) => (
      <line
        key={i}
        x1={i * 15}
        y1={y}
        x2={i * 15 - 10}
        y2={y + 15}
        stroke="#7F8C8D"
        strokeWidth={1.5}
      />
    ))}
  </motion.g>
);

// Structure Box - Generic container/structure component
const StructureBox = ({ x, y, width, height, label, delay = 0 }) => (
  <motion.g
    transform={`translate(${x}, ${y})`}
    initial={{ opacity: 0, scale: 0.9 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ delay, duration: 0.3 }}
  >
    <rect
      x={0}
      y={0}
      width={width}
      height={height}
      fill="rgba(236, 240, 241, 0.8)"
      stroke="#2C3E50"
      strokeWidth={2}
      rx={4}
    />
    {label && (
      <text
        x={width / 2}
        y={height / 2}
        textAnchor="middle"
        dominantBaseline="middle"
        fill="#2C3E50"
        fontSize={12}
        fontFamily={NETRA_THEME.handwriting}
      >
        {label}
      </text>
    )}
  </motion.g>
);

const CellDiagram = ({ x, y, width, height, variant, label, delay = 0 }) => (
  <motion.g
    transform={`translate(${x}, ${y})`}
    initial={{ opacity: 0, scale: 0.8 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ delay, duration: 0.4 }}
  >
    {/* Cell membrane */}
    <ellipse
      cx={width / 2}
      cy={height / 2}
      rx={width / 2 - 5}
      ry={height / 2 - 5}
      fill="rgba(200, 230, 255, 0.4)"
      stroke="#3498DB"
      strokeWidth={3}
      strokeDasharray="15 5"
    />
    {/* Nucleus */}
    <ellipse
      cx={width / 2}
      cy={height / 2}
      rx={width * 0.2}
      ry={height * 0.2}
      fill="#9B59B6"
      stroke="#7D3C98"
      strokeWidth={2}
    />
    {/* Label */}
    <text
      x={width / 2}
      y={height + 15}
      textAnchor="middle"
      fill="#2C3E50"
      fontSize={12}
      fontFamily={NETRA_THEME.handwriting}
    >
      {label}
    </text>
  </motion.g>
);

const AtomDiagram = ({ x, y, size, element, delay = 0 }) => (
  <motion.g
    transform={`translate(${x}, ${y})`}
    initial={{ opacity: 0, scale: 0.5 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ delay, duration: 0.5 }}
  >
    {/* Nucleus */}
    <circle
      cx={size / 2}
      cy={size / 2}
      r={size * 0.15}
      fill="#E74C3C"
      stroke="#922B21"
      strokeWidth={2}
    />
    {/* Electron orbits */}
    <ellipse
      cx={size / 2}
      cy={size / 2}
      rx={size * 0.4}
      ry={size * 0.2}
      fill="none"
      stroke="#3498DB"
      strokeWidth={1.5}
      strokeDasharray="5 3"
    />
    <ellipse
      cx={size / 2}
      cy={size / 2}
      rx={size * 0.2}
      ry={size * 0.4}
      fill="none"
      stroke="#3498DB"
      strokeWidth={1.5}
      strokeDasharray="5 3"
    />
    {/* Element symbol */}
    <text
      x={size / 2}
      y={size / 2 + 4}
      textAnchor="middle"
      fill="white"
      fontSize={12}
      fontWeight="bold"
    >
      {element?.charAt(0) || 'X'}
    </text>
  </motion.g>
);

const GraphPlot = ({ x, y, width, height, delay = 0 }) => {
  const axisMargin = 30;
  
  return (
    <motion.g
      transform={`translate(${x}, ${y})`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay, duration: 0.4 }}
    >
      {/* Axes */}
      <line
        x1={axisMargin}
        y1={height - axisMargin}
        x2={width - 10}
        y2={height - axisMargin}
        stroke="#2C3E50"
        strokeWidth={2}
        markerEnd="url(#arrow-head)"
      />
      <line
        x1={axisMargin}
        y1={height - axisMargin}
        x2={axisMargin}
        y2={10}
        stroke="#2C3E50"
        strokeWidth={2}
        markerEnd="url(#arrow-head)"
      />
      {/* Axis labels */}
      <text
        x={width - 15}
        y={height - 10}
        fill="#2C3E50"
        fontSize={14}
        fontFamily={NETRA_THEME.handwriting}
      >
        x
      </text>
      <text
        x={15}
        y={20}
        fill="#2C3E50"
        fontSize={14}
        fontFamily={NETRA_THEME.handwriting}
      >
        y
      </text>
    </motion.g>
  );
};

const ProcessBox = ({ x, y, width, height, label, delay = 0 }) => (
  <motion.g
    transform={`translate(${x}, ${y})`}
    initial={{ opacity: 0, y: -20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.3 }}
  >
    <rect
      x={0}
      y={0}
      width={width}
      height={height}
      rx={8}
      fill="#ECF0F1"
      stroke="#2C3E50"
      strokeWidth={2}
    />
    <text
      x={width / 2}
      y={height / 2 + 4}
      textAnchor="middle"
      fill="#2C3E50"
      fontSize={13}
      fontFamily={NETRA_THEME.handwriting}
    >
      {label}
    </text>
  </motion.g>
);

const GenericShape = ({ x, y, width, height, label, delay = 0 }) => (
  <motion.g
    transform={`translate(${x}, ${y})`}
    initial={{ opacity: 0, scale: 0.8 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ delay, duration: 0.4 }}
  >
    <rect
      x={0}
      y={0}
      width={width}
      height={height}
      rx={5}
      fill="#ECF0F1"
      stroke="#2C3E50"
      strokeWidth={2}
      filter="url(#pencil-texture)"
    />
    {label && (
      <text
        x={width / 2}
        y={height / 2 + 4}
        textAnchor="middle"
        fill="#2C3E50"
        fontSize={12}
        fontFamily={NETRA_THEME.handwriting}
      >
        {label}
      </text>
    )}
  </motion.g>
);

// ============================================
// ARROW RENDERER
// ============================================

const ArrowRenderer = ({ arrow }) => {
  const { fromNode, toNode, style, label, curved, drawOrder } = arrow;
  
  if (!fromNode || !toNode) return null;
  
  // Calculate start and end points
  const fromCenter = {
    x: fromNode.x + fromNode.width / 2,
    y: fromNode.y + fromNode.height / 2,
  };
  const toCenter = {
    x: toNode.x + toNode.width / 2,
    y: toNode.y + toNode.height / 2,
  };
  
  // Adjust for shape edges
  const dx = toCenter.x - fromCenter.x;
  const dy = toCenter.y - fromCenter.y;
  const angle = Math.atan2(dy, dx);
  
  const startX = fromCenter.x + Math.cos(angle) * (fromNode.width / 2 + 5);
  const startY = fromCenter.y + Math.sin(angle) * (fromNode.height / 2 + 5);
  const endX = toCenter.x - Math.cos(angle) * (toNode.width / 2 + 15);
  const endY = toCenter.y - Math.sin(angle) * (toNode.height / 2 + 15);
  
  // Path
  const pathData = curved
    ? `M ${startX} ${startY} Q ${(startX + endX) / 2} ${Math.min(startY, endY) - 30} ${endX} ${endY}`
    : `M ${startX} ${startY} L ${endX} ${endY}`;
  
  return (
    <motion.g
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: arrow.animationDelay || 0.5, duration: 0.3 }}
    >
      <motion.path
        d={pathData}
        fill="none"
        stroke={style?.color || '#2C3E50'}
        strokeWidth={style?.width || 2}
        strokeDasharray={style?.dashed ? '8 4' : 'none'}
        markerEnd="url(#arrow-head)"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ delay: arrow.animationDelay || 0.5, duration: 0.5 }}
      />
      {label && (
        <text
          x={(startX + endX) / 2}
          y={(startY + endY) / 2 - 10}
          textAnchor="middle"
          fill="#7F8C8D"
          fontSize={11}
          fontFamily={NETRA_THEME.handwriting}
        >
          {label}
        </text>
      )}
    </motion.g>
  );
};

// ============================================
// ANNOTATION RENDERER
// ============================================

const AnnotationRenderer = ({ annotations }) => (
  <g className="layer-annotations">
    {annotations.map((annotation, i) => (
      <motion.text
        key={i}
        x={annotation.x}
        y={annotation.y}
        textAnchor={annotation.textAnchor || 'start'}
        fill={annotation.color || '#2C3E50'}
        fontSize={annotation.fontSize || 14}
        fontWeight={annotation.fontWeight || 'normal'}
        fontFamily={NETRA_THEME.handwriting}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 + i * 0.1 }}
      >
        {annotation.text}
      </motion.text>
    ))}
  </g>
);

// ============================================
// MAIN SVG RENDERER
// ============================================

const SVGRenderer = ({
  sceneGraph,
  width = 800,
  height = 600,
  showGrid = true,
  style = {},
  className = '',
  onRenderComplete = null,
}) => {
  const svgRef = useRef(null);
  const [isRendered, setIsRendered] = useState(false);
  
  // Extract render data from scene graph
  const renderSpec = useMemo(() => {
    if (!sceneGraph) {
      console.log('🎨 [SVGRenderer] No sceneGraph provided');
      return null;
    }
    const spec = sceneGraph.toRenderSpec ? sceneGraph.toRenderSpec() : sceneGraph;
    console.log('🎨 [SVGRenderer] RenderSpec:', {
      nodeCount: spec.nodes?.length || 0,
      arrowCount: spec.arrows?.length || 0,
      nodes: spec.nodes?.map(n => ({ id: n.id, primitive: n.primitive, x: n.x, y: n.y })),
    });
    return spec;
  }, [sceneGraph]);

  // Trigger render complete callback
  useEffect(() => {
    if (renderSpec && !isRendered) {
      const maxDelay = Math.max(
        ...renderSpec.nodes.map(n => n.animationDelay || 0),
        ...renderSpec.arrows.map(a => a.animationDelay || 0)
      );
      
      const timer = setTimeout(() => {
        setIsRendered(true);
        onRenderComplete?.();
      }, (maxDelay + 1) * 1000);
      
      return () => clearTimeout(timer);
    }
  }, [renderSpec, isRendered, onRenderComplete]);

  if (!renderSpec) {
    return (
      <div
        className={`netra-renderer empty ${className}`}
        style={{ width, height, ...style }}
      >
        <svg width="100%" height="100%" viewBox={`0 0 ${width} ${height}`}>
          <BackgroundLayer width={width} height={height} showGrid={showGrid} />
          <text
            x={width / 2}
            y={height / 2}
            textAnchor="middle"
            fill="#BDC3C7"
            fontSize={16}
            fontFamily={NETRA_THEME.handwriting}
          >
            No scene to render
          </text>
        </svg>
      </div>
    );
  }

  const domain = renderSpec.metadata?.domain || 'physics';

  return (
    <div
      className={`netra-renderer ${className}`}
      style={{ width, height, position: 'relative', ...style }}
    >
      <svg
        ref={svgRef}
        width="100%"
        height="100%"
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Filters and markers */}
        <SketchFilters />
        
        {/* Background layer - transparent by default, SmartBoard provides notebook background */}
        <BackgroundLayer width={width} height={height} showGrid={false} transparent={true} />
        
        {/* Decorations layer */}
        <g className="layer-decorations">
          {renderSpec.decorations?.map((dec, i) => {
            if (dec.type === 'line') {
              return (
                <line
                  key={i}
                  x1={dec.x1}
                  y1={dec.y1}
                  x2={dec.x2}
                  y2={dec.y2}
                  stroke={dec.style?.color}
                  strokeWidth={dec.style?.width}
                  strokeDasharray={dec.style?.dashed ? '8 4' : 'none'}
                />
              );
            }
            return null;
          })}
        </g>
        
        {/* Nodes layer */}
        <g className="layer-nodes">
          {renderSpec.nodes
            .sort((a, b) => (a.drawOrder || 0) - (b.drawOrder || 0))
            .map(node => (
              <NodeRenderer
                key={node.id}
                node={node}
                domain={domain}
              />
            ))}
        </g>
        
        {/* Arrows layer */}
        <g className="layer-arrows">
          {renderSpec.arrows.map((arrow, i) => (
            <ArrowRenderer key={i} arrow={arrow} />
          ))}
        </g>
        
        {/* Annotations layer */}
        <AnnotationRenderer annotations={renderSpec.annotations || []} />
      </svg>
      
      {/* Strategy badge (dev mode) */}
      {process.env.NODE_ENV === 'development' && renderSpec.metadata?.strategy && (
        <div
          style={{
            position: 'absolute',
            bottom: 8,
            right: 8,
            background: 'rgba(0,0,0,0.6)',
            color: 'white',
            padding: '4px 8px',
            borderRadius: 4,
            fontSize: 10,
            fontFamily: 'monospace',
          }}
        >
          {renderSpec.metadata.strategy}
        </div>
      )}
    </div>
  );
};

export default SVGRenderer;
export { NETRA_THEME, SketchFilters };



