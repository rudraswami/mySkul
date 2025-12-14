/**
 * 📐 MATH PRIMITIVES
 * ==================
 * 
 * Visual components for mathematics concepts.
 * Precise, clean geometric representations.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { PRIMITIVE_THEMES } from '../UniversalPrimitives';

const theme = PRIMITIVE_THEMES.math;

/**
 * Coordinate Axes - X-Y axes with labels
 */
export const CoordinateAxes = ({
  x = 50,
  y = 50,
  width = 200,
  height = 150,
  showGrid = true,
  xLabel = 'x',
  yLabel = 'y',
  color = theme.primary,
  animate = true,
}) => {
  const originX = x;
  const originY = y + height;
  
  return (
    <motion.g
      initial={animate ? { opacity: 0 } : false}
      animate={{ opacity: 1 }}
    >
      {/* Grid */}
      {showGrid && (
        <g opacity={0.3}>
          {Array.from({ length: 10 }).map((_, i) => (
            <g key={i}>
              <line x1={originX + i * 20} y1={originY} x2={originX + i * 20} y2={y} stroke={color} strokeWidth={0.5} />
              <line x1={originX} y1={originY - i * 15} x2={x + width} y2={originY - i * 15} stroke={color} strokeWidth={0.5} />
            </g>
          ))}
        </g>
      )}
      
      {/* X-axis */}
      <motion.line
        x1={originX}
        y1={originY}
        x2={x + width}
        y2={originY}
        stroke={color}
        strokeWidth={2}
        initial={animate ? { pathLength: 0 } : false}
        animate={{ pathLength: 1 }}
      />
      <polygon points={`${x + width},${originY} ${x + width - 8},${originY - 4} ${x + width - 8},${originY + 4}`} fill={color} />
      <text x={x + width - 5} y={originY + 18} fontSize={14} fontWeight={600} fill={color}>{xLabel}</text>
      
      {/* Y-axis */}
      <motion.line
        x1={originX}
        y1={originY}
        x2={originX}
        y2={y}
        stroke={color}
        strokeWidth={2}
        initial={animate ? { pathLength: 0 } : false}
        animate={{ pathLength: 1 }}
      />
      <polygon points={`${originX},${y} ${originX - 4},${y + 8} ${originX + 4},${y + 8}`} fill={color} />
      <text x={originX - 15} y={y + 10} fontSize={14} fontWeight={600} fill={color}>{yLabel}</text>
      
      {/* Origin label */}
      <text x={originX - 12} y={originY + 15} fontSize={12} fill="#64748B">O</text>
    </motion.g>
  );
};

/**
 * Graph Curve - Plotted function
 */
export const GraphCurve = ({
  points = [], // [{x, y}, ...]
  originX = 50,
  originY = 200,
  scaleX = 20,
  scaleY = 15,
  color = theme.secondary,
  label = '',
  dashed = false,
  animate = true,
}) => {
  if (points.length < 2) return null;
  
  const pathData = points.map((p, i) => 
    `${i === 0 ? 'M' : 'L'} ${originX + p.x * scaleX} ${originY - p.y * scaleY}`
  ).join(' ');
  
  return (
    <motion.g>
      <motion.path
        d={pathData}
        fill="none"
        stroke={color}
        strokeWidth={3}
        strokeDasharray={dashed ? '8,4' : 'none'}
        initial={animate ? { pathLength: 0 } : false}
        animate={{ pathLength: 1 }}
        transition={{ duration: 1, ease: 'easeInOut' }}
      />
      {label && (
        <text
          x={originX + points[points.length - 1].x * scaleX + 10}
          y={originY - points[points.length - 1].y * scaleY}
          fontSize={12}
          fontWeight={600}
          fill={color}
        >
          {label}
        </text>
      )}
    </motion.g>
  );
};

/**
 * Equation Box - Formatted equation display
 */
export const EquationBox = ({
  x = 0,
  y = 0,
  equation = 'y = mx + b',
  color = theme.primary,
  size = 'medium', // small, medium, large
  boxed = true,
  animate = true,
}) => {
  const fontSize = size === 'small' ? 14 : size === 'large' ? 24 : 18;
  const padding = size === 'small' ? 8 : size === 'large' ? 16 : 12;
  
  return (
    <motion.g
      initial={animate ? { opacity: 0, scale: 0.9 } : false}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      {boxed && (
        <rect
          x={x}
          y={y}
          width={equation.length * fontSize * 0.6 + padding * 2}
          height={fontSize + padding * 2}
          rx={6}
          fill={`${color}10`}
          stroke={color}
          strokeWidth={1}
        />
      )}
      <text
        x={x + padding}
        y={y + fontSize + padding - 4}
        fontSize={fontSize}
        fontFamily="'Cambria Math', 'Times New Roman', serif"
        fontStyle="italic"
        fill={color}
      >
        {equation}
      </text>
    </motion.g>
  );
};

/**
 * Geometric Shape - Triangle, Square, Circle with labels
 */
export const GeometricShape = ({
  cx = 100,
  cy = 100,
  type = 'triangle', // triangle, square, circle, rectangle
  size = 60,
  labels = {}, // { a: 'a', b: 'b', c: 'c' } for sides
  color = theme.primary,
  showAngles = false,
  animate = true,
}) => {
  const renderShape = () => {
    switch (type) {
      case 'triangle':
        const h = size * 0.866; // height for equilateral
        return (
          <g>
            <polygon
              points={`${cx},${cy - h * 0.6} ${cx - size / 2},${cy + h * 0.4} ${cx + size / 2},${cy + h * 0.4}`}
              fill={`${color}15`}
              stroke={color}
              strokeWidth={2}
            />
            {/* Side labels */}
            {labels.a && <text x={cx - size * 0.4} y={cy} fontSize={12} fill={color}>{labels.a}</text>}
            {labels.b && <text x={cx + size * 0.3} y={cy} fontSize={12} fill={color}>{labels.b}</text>}
            {labels.c && <text x={cx} y={cy + h * 0.4 + 15} fontSize={12} fill={color} textAnchor="middle">{labels.c}</text>}
          </g>
        );
      case 'square':
        return (
          <g>
            <rect
              x={cx - size / 2}
              y={cy - size / 2}
              width={size}
              height={size}
              fill={`${color}15`}
              stroke={color}
              strokeWidth={2}
            />
            {/* Right angle marker */}
            <path
              d={`M ${cx - size / 2 + 10} ${cy + size / 2} L ${cx - size / 2 + 10} ${cy + size / 2 - 10} L ${cx - size / 2} ${cy + size / 2 - 10}`}
              fill="none"
              stroke={color}
              strokeWidth={1}
            />
          </g>
        );
      case 'circle':
        return (
          <g>
            <circle cx={cx} cy={cy} r={size / 2} fill={`${color}15`} stroke={color} strokeWidth={2} />
            {/* Radius line */}
            <line x1={cx} y1={cy} x2={cx + size / 2} y2={cy} stroke={color} strokeWidth={1} strokeDasharray="4,2" />
            {labels.r && <text x={cx + size / 4} y={cy - 5} fontSize={11} fill={color}>{labels.r}</text>}
          </g>
        );
      default:
        return <rect x={cx - size / 2} y={cy - size / 3} width={size} height={size * 0.66} fill={`${color}15`} stroke={color} strokeWidth={2} />;
    }
  };
  
  return (
    <motion.g
      initial={animate ? { opacity: 0, scale: 0.8 } : false}
      animate={{ opacity: 1, scale: 1 }}
    >
      {renderShape()}
    </motion.g>
  );
};

/**
 * Number Line - For integers, fractions, real numbers
 */
export const NumberLine = ({
  x = 50,
  y = 100,
  length = 300,
  min = -5,
  max = 5,
  highlights = [], // [{value, label, color}]
  color = theme.primary,
  animate = true,
}) => {
  const range = max - min;
  const getX = (value) => x + ((value - min) / range) * length;
  
  return (
    <motion.g
      initial={animate ? { opacity: 0 } : false}
      animate={{ opacity: 1 }}
    >
      {/* Main line */}
      <line x1={x} y1={y} x2={x + length} y2={y} stroke={color} strokeWidth={2} />
      <polygon points={`${x + length + 8},${y} ${x + length},${y - 4} ${x + length},${y + 4}`} fill={color} />
      
      {/* Tick marks */}
      {Array.from({ length: range + 1 }).map((_, i) => {
        const value = min + i;
        const xPos = getX(value);
        return (
          <g key={i}>
            <line x1={xPos} y1={y - 6} x2={xPos} y2={y + 6} stroke={color} strokeWidth={1} />
            <text x={xPos} y={y + 20} textAnchor="middle" fontSize={11} fill="#64748B">{value}</text>
          </g>
        );
      })}
      
      {/* Highlights */}
      {highlights.map((h, i) => (
        <motion.g
          key={i}
          initial={animate ? { scale: 0 } : false}
          animate={{ scale: 1 }}
          transition={{ delay: 0.3 + i * 0.1 }}
        >
          <circle cx={getX(h.value)} cy={y} r={8} fill={h.color || theme.secondary} />
          {h.label && (
            <text x={getX(h.value)} y={y - 15} textAnchor="middle" fontSize={10} fill={h.color || theme.secondary}>
              {h.label}
            </text>
          )}
        </motion.g>
      ))}
    </motion.g>
  );
};

/**
 * Set Diagram - Venn diagram
 */
export const SetDiagram = ({
  x = 100,
  y = 100,
  sets = [{ label: 'A', color: theme.primary }, { label: 'B', color: theme.secondary }],
  overlap = true,
  size = 60,
  animate = true,
}) => (
  <motion.g
    initial={animate ? { opacity: 0 } : false}
    animate={{ opacity: 1 }}
  >
    {sets.map((set, i) => {
      const offset = overlap ? (i - (sets.length - 1) / 2) * size * 0.7 : (i - (sets.length - 1) / 2) * size * 1.5;
      return (
        <motion.g
          key={i}
          initial={animate ? { scale: 0 } : false}
          animate={{ scale: 1 }}
          transition={{ delay: i * 0.2 }}
        >
          <circle
            cx={x + offset}
            cy={y}
            r={size}
            fill={`${set.color}20`}
            stroke={set.color}
            strokeWidth={2}
          />
          <text
            x={x + offset + (i === 0 ? -size * 0.5 : i === sets.length - 1 ? size * 0.5 : 0)}
            y={y}
            textAnchor="middle"
            fontSize={16}
            fontWeight={600}
            fill={set.color}
          >
            {set.label}
          </text>
        </motion.g>
      );
    })}
  </motion.g>
);

// Registry
export const MATH_PRIMITIVES = {
  axes: CoordinateAxes,
  coordinate_axes: CoordinateAxes,
  graph_curve: GraphCurve,
  curve: GraphCurve,
  equation: EquationBox,
  equation_box: EquationBox,
  shape: GeometricShape,
  geometric_shape: GeometricShape,
  number_line: NumberLine,
  set_diagram: SetDiagram,
  venn: SetDiagram,
};

export default MATH_PRIMITIVES;

