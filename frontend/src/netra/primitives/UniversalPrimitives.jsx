/**
 * 🎨 UNIVERSAL PRIMITIVES LIBRARY
 * ================================
 * 
 * Subject-agnostic visual building blocks.
 * 
 * The REASONING layer decides WHAT to show.
 * These primitives decide HOW it looks.
 * 
 * Example:
 * - Reasoning: "Show a CAUSE_EFFECT for friction"
 * - Primitives: Box for object, Arrow for force, Line for ground
 * 
 * ALL subjects use the SAME base primitives, styled differently.
 */

import React from 'react';
import { motion } from 'framer-motion';

// ============================================
// THEME CONFIGURATION
// ============================================

export const PRIMITIVE_THEMES = {
  physics: {
    primary: '#3B82F6',     // Blue
    secondary: '#EF4444',   // Red
    accent: '#10B981',      // Green
    background: '#F8FAFC',
    text: '#1E293B',
  },
  chemistry: {
    primary: '#8B5CF6',     // Purple
    secondary: '#F97316',   // Orange
    accent: '#06B6D4',      // Cyan
    background: '#FEFCE8',
    text: '#1E293B',
  },
  biology: {
    primary: '#22C55E',     // Green
    secondary: '#EC4899',   // Pink
    accent: '#84CC16',      // Lime
    background: '#F0FDF4',
    text: '#1E293B',
  },
  math: {
    primary: '#0EA5E9',     // Sky
    secondary: '#F59E0B',   // Amber
    accent: '#6366F1',      // Indigo
    background: '#F8FAFC',
    text: '#1E293B',
  },
  history: {
    primary: '#B45309',     // Amber dark
    secondary: '#78716C',   // Stone
    accent: '#D97706',      // Amber
    background: '#FFFBEB',
    text: '#292524',
  },
  geography: {
    primary: '#059669',     // Emerald
    secondary: '#2563EB',   // Blue
    accent: '#CA8A04',      // Yellow
    background: '#ECFDF5',
    text: '#1E293B',
  },
  default: {
    primary: '#6366F1',
    secondary: '#EC4899',
    accent: '#10B981',
    background: '#F8FAFC',
    text: '#1E293B',
  },
};

// ============================================
// BASE PRIMITIVES (Used by ALL subjects)
// ============================================

/**
 * Universal Box - Represents any entity/concept
 */
export const UniversalBox = ({
  x = 0,
  y = 0,
  width = 100,
  height = 60,
  label = '',
  color = '#6366F1',
  borderStyle = 'solid', // solid, dashed, dotted
  rounded = true,
  emphasis = false,
  animate = true,
  style = {},
}) => {
  const borderRadius = rounded ? 12 : 4;
  
  return (
    <motion.g
      initial={animate ? { opacity: 0, scale: 0.8 } : false}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
    >
      {/* Shadow for emphasis */}
      {emphasis && (
        <rect
          x={x + 3}
          y={y + 3}
          width={width}
          height={height}
          rx={borderRadius}
          fill="rgba(0,0,0,0.1)"
        />
      )}
      
      {/* Main box */}
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        rx={borderRadius}
        fill={`${color}15`}
        stroke={color}
        strokeWidth={emphasis ? 3 : 2}
        strokeDasharray={borderStyle === 'dashed' ? '8,4' : borderStyle === 'dotted' ? '3,3' : 'none'}
        style={style}
      />
      
      {/* Label */}
      {label && (
        <text
          x={x + width / 2}
          y={y + height / 2}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize={14}
          fontWeight={600}
          fill={color}
          style={{ fontFamily: 'system-ui, sans-serif' }}
        >
          {label}
        </text>
      )}
    </motion.g>
  );
};

/**
 * Universal Arrow - Represents relationships/flows/forces
 */
export const UniversalArrow = ({
  x1 = 0,
  y1 = 0,
  x2 = 100,
  y2 = 0,
  label = '',
  color = '#6366F1',
  thickness = 2,
  dashed = false,
  curved = false,
  bidirectional = false,
  animate = true,
}) => {
  // Calculate arrow head
  const angle = Math.atan2(y2 - y1, x2 - x1);
  const headLength = 12;
  
  // Arrow head points
  const headX1 = x2 - headLength * Math.cos(angle - Math.PI / 6);
  const headY1 = y2 - headLength * Math.sin(angle - Math.PI / 6);
  const headX2 = x2 - headLength * Math.cos(angle + Math.PI / 6);
  const headY2 = y2 - headLength * Math.sin(angle + Math.PI / 6);
  
  // Curved path
  const midX = (x1 + x2) / 2;
  const midY = (y1 + y2) / 2 - (curved ? 30 : 0);
  const path = curved
    ? `M ${x1} ${y1} Q ${midX} ${midY} ${x2} ${y2}`
    : `M ${x1} ${y1} L ${x2} ${y2}`;
  
  return (
    <motion.g
      initial={animate ? { opacity: 0, pathLength: 0 } : false}
      animate={{ opacity: 1, pathLength: 1 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
    >
      {/* Main line */}
      <motion.path
        d={path}
        fill="none"
        stroke={color}
        strokeWidth={thickness}
        strokeDasharray={dashed ? '8,4' : 'none'}
        initial={animate ? { pathLength: 0 } : false}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.6 }}
      />
      
      {/* Arrow head */}
      <polygon
        points={`${x2},${y2} ${headX1},${headY1} ${headX2},${headY2}`}
        fill={color}
      />
      
      {/* Bidirectional arrow head */}
      {bidirectional && (
        <polygon
          points={`${x1},${y1} ${x1 + headLength * Math.cos(angle - Math.PI / 6)},${y1 + headLength * Math.sin(angle - Math.PI / 6)} ${x1 + headLength * Math.cos(angle + Math.PI / 6)},${y1 + headLength * Math.sin(angle + Math.PI / 6)}`}
          fill={color}
        />
      )}
      
      {/* Label */}
      {label && (
        <text
          x={midX}
          y={midY - 10}
          textAnchor="middle"
          fontSize={12}
          fill={color}
          style={{ fontFamily: 'system-ui, sans-serif' }}
        >
          {label}
        </text>
      )}
    </motion.g>
  );
};

/**
 * Universal Circle - Represents points, atoms, nodes
 */
export const UniversalCircle = ({
  cx = 50,
  cy = 50,
  r = 30,
  label = '',
  color = '#6366F1',
  filled = true,
  innerLabel = '',
  animate = true,
}) => (
  <motion.g
    initial={animate ? { opacity: 0, scale: 0 } : false}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ duration: 0.4, type: 'spring' }}
  >
    <circle
      cx={cx}
      cy={cy}
      r={r}
      fill={filled ? `${color}30` : 'none'}
      stroke={color}
      strokeWidth={2}
    />
    {innerLabel && (
      <text
        x={cx}
        y={cy}
        textAnchor="middle"
        dominantBaseline="middle"
        fontSize={r > 20 ? 14 : 10}
        fontWeight={600}
        fill={color}
      >
        {innerLabel}
      </text>
    )}
    {label && (
      <text
        x={cx}
        y={cy + r + 16}
        textAnchor="middle"
        fontSize={12}
        fill={color}
      >
        {label}
      </text>
    )}
  </motion.g>
);

/**
 * Universal Line - Represents connections, boundaries, axes
 */
export const UniversalLine = ({
  x1 = 0,
  y1 = 0,
  x2 = 100,
  y2 = 0,
  color = '#64748B',
  thickness = 2,
  dashed = false,
  label = '',
  animate = true,
}) => (
  <motion.g
    initial={animate ? { opacity: 0 } : false}
    animate={{ opacity: 1 }}
    transition={{ duration: 0.3 }}
  >
    <line
      x1={x1}
      y1={y1}
      x2={x2}
      y2={y2}
      stroke={color}
      strokeWidth={thickness}
      strokeDasharray={dashed ? '6,3' : 'none'}
    />
    {label && (
      <text
        x={(x1 + x2) / 2}
        y={(y1 + y2) / 2 - 8}
        textAnchor="middle"
        fontSize={11}
        fill={color}
      >
        {label}
      </text>
    )}
  </motion.g>
);

/**
 * Universal Label - Floating text annotations
 */
export const UniversalLabel = ({
  x = 0,
  y = 0,
  text = '',
  size = 'medium', // small, medium, large
  color = '#1E293B',
  background = false,
  animate = true,
}) => {
  const fontSize = size === 'small' ? 11 : size === 'large' ? 18 : 14;
  
  return (
    <motion.g
      initial={animate ? { opacity: 0, y: y + 10 } : false}
      animate={{ opacity: 1, y }}
      transition={{ duration: 0.3 }}
    >
      {background && (
        <rect
          x={x - 4}
          y={y - fontSize}
          width={text.length * fontSize * 0.6 + 8}
          height={fontSize + 8}
          rx={4}
          fill="white"
          opacity={0.9}
        />
      )}
      <text
        x={x}
        y={y}
        fontSize={fontSize}
        fontWeight={size === 'large' ? 700 : 500}
        fill={color}
        style={{ fontFamily: 'system-ui, sans-serif' }}
      >
        {text}
      </text>
    </motion.g>
  );
};

/**
 * Universal Container - Groups elements with a boundary
 */
export const UniversalContainer = ({
  x = 0,
  y = 0,
  width = 200,
  height = 150,
  title = '',
  color = '#6366F1',
  children,
  animate = true,
}) => (
  <motion.g
    initial={animate ? { opacity: 0 } : false}
    animate={{ opacity: 1 }}
    transition={{ duration: 0.4 }}
  >
    <rect
      x={x}
      y={y}
      width={width}
      height={height}
      rx={8}
      fill={`${color}08`}
      stroke={color}
      strokeWidth={1}
      strokeDasharray="4,4"
    />
    {title && (
      <text
        x={x + 8}
        y={y + 18}
        fontSize={12}
        fontWeight={600}
        fill={color}
      >
        {title}
      </text>
    )}
    {children}
  </motion.g>
);

/**
 * VS Divider - For comparison forms
 */
export const VSDivider = ({
  x = 0,
  y1 = 0,
  y2 = 200,
  color = '#94A3B8',
  animate = true,
}) => (
  <motion.g
    initial={animate ? { opacity: 0 } : false}
    animate={{ opacity: 1 }}
    transition={{ duration: 0.3 }}
  >
    <line
      x1={x}
      y1={y1}
      x2={x}
      y2={y2}
      stroke={color}
      strokeWidth={2}
      strokeDasharray="8,4"
    />
    <circle cx={x} cy={(y1 + y2) / 2} r={20} fill="white" stroke={color} strokeWidth={2} />
    <text
      x={x}
      y={(y1 + y2) / 2 + 5}
      textAnchor="middle"
      fontSize={14}
      fontWeight={700}
      fill={color}
    >
      VS
    </text>
  </motion.g>
);

/**
 * Timeline Marker - For temporal forms
 */
export const TimelineMarker = ({
  x = 0,
  y = 0,
  label = '',
  sublabel = '',
  color = '#6366F1',
  isStart = false,
  isEnd = false,
  animate = true,
}) => (
  <motion.g
    initial={animate ? { opacity: 0, scale: 0 } : false}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ duration: 0.3, type: 'spring' }}
  >
    <circle
      cx={x}
      cy={y}
      r={isStart || isEnd ? 12 : 8}
      fill={isStart || isEnd ? color : 'white'}
      stroke={color}
      strokeWidth={3}
    />
    <text
      x={x}
      y={y - 20}
      textAnchor="middle"
      fontSize={12}
      fontWeight={600}
      fill={color}
    >
      {label}
    </text>
    {sublabel && (
      <text
        x={x}
        y={y + 28}
        textAnchor="middle"
        fontSize={10}
        fill="#64748B"
      >
        {sublabel}
      </text>
    )}
  </motion.g>
);

/**
 * Hierarchy Node - For tree/classification forms
 */
export const HierarchyNode = ({
  x = 0,
  y = 0,
  label = '',
  level = 0, // 0 = root, 1 = child, 2 = grandchild
  color = '#6366F1',
  animate = true,
}) => {
  const sizes = [
    { width: 140, height: 50, fontSize: 16 },
    { width: 110, height: 40, fontSize: 13 },
    { width: 90, height: 32, fontSize: 11 },
  ];
  const { width, height, fontSize } = sizes[Math.min(level, 2)];
  
  return (
    <motion.g
      initial={animate ? { opacity: 0, y: y - 20 } : false}
      animate={{ opacity: 1, y }}
      transition={{ duration: 0.4, delay: level * 0.1 }}
    >
      <rect
        x={x - width / 2}
        y={y - height / 2}
        width={width}
        height={height}
        rx={height / 2}
        fill={level === 0 ? color : `${color}20`}
        stroke={color}
        strokeWidth={level === 0 ? 0 : 2}
      />
      <text
        x={x}
        y={y + 4}
        textAnchor="middle"
        fontSize={fontSize}
        fontWeight={level === 0 ? 700 : 500}
        fill={level === 0 ? 'white' : color}
      >
        {label}
      </text>
    </motion.g>
  );
};

// ============================================
// PRIMITIVE REGISTRY
// ============================================

export const PRIMITIVE_REGISTRY = {
  // Base primitives (work for ALL subjects)
  box: UniversalBox,
  arrow: UniversalArrow,
  circle: UniversalCircle,
  line: UniversalLine,
  label: UniversalLabel,
  container: UniversalContainer,
  vs_divider: VSDivider,
  timeline_marker: TimelineMarker,
  hierarchy_node: HierarchyNode,
  
  // Aliases for semantic mapping
  entity: UniversalBox,
  concept: UniversalBox,
  object: UniversalBox,
  relationship: UniversalArrow,
  flow: UniversalArrow,
  connection: UniversalLine,
  point: UniversalCircle,
  node: UniversalCircle,
  annotation: UniversalLabel,
  group: UniversalContainer,
};

/**
 * Get primitive component by type
 */
export const getPrimitive = (type) => {
  return PRIMITIVE_REGISTRY[type] || UniversalBox;
};

export default PRIMITIVE_REGISTRY;

