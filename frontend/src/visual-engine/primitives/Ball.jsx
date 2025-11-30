/**
 * ⚽ Ball Primitive
 * =================
 * 
 * Configurable ball/sphere for physics visualizations.
 * Supports: cricket, tennis, football, medicine, bowling, atom
 */

import React from 'react';
import { motion } from 'framer-motion';

const BALL_TYPES = {
  cricket: {
    color: '#DC2626',
    strokeColor: '#991B1B',
    pattern: (cx, cy, r) => (
      <>
        {/* Seam */}
        <path
          d={`M ${cx - r * 0.7} ${cy - r * 0.3} Q ${cx} ${cy - r * 0.8} ${cx + r * 0.7} ${cy - r * 0.3}`}
          stroke="white"
          strokeWidth={2}
          fill="none"
        />
        <path
          d={`M ${cx - r * 0.7} ${cy + r * 0.3} Q ${cx} ${cy + r * 0.8} ${cx + r * 0.7} ${cy + r * 0.3}`}
          stroke="white"
          strokeWidth={2}
          fill="none"
        />
      </>
    ),
  },
  tennis: {
    color: '#BEF264',
    strokeColor: '#84CC16',
    pattern: (cx, cy, r) => (
      <>
        <path
          d={`M ${cx} ${cy - r} Q ${cx + r * 0.5} ${cy} ${cx} ${cy + r}`}
          stroke="white"
          strokeWidth={2}
          fill="none"
        />
        <path
          d={`M ${cx} ${cy - r} Q ${cx - r * 0.5} ${cy} ${cx} ${cy + r}`}
          stroke="white"
          strokeWidth={2}
          fill="none"
        />
      </>
    ),
  },
  football: {
    color: '#1F2937',
    strokeColor: '#111827',
    pattern: (cx, cy, r) => (
      <>
        {/* Pentagon pattern */}
        <polygon
          points={`${cx},${cy - r * 0.4} ${cx + r * 0.4},${cy - r * 0.1} ${cx + r * 0.25},${cy + r * 0.35} ${cx - r * 0.25},${cy + r * 0.35} ${cx - r * 0.4},${cy - r * 0.1}`}
          fill="white"
          stroke="#374151"
          strokeWidth={1}
        />
      </>
    ),
  },
  medicine: {
    color: '#7C3AED',
    strokeColor: '#5B21B6',
    pattern: () => null,
  },
  bowling: {
    color: '#1F2937',
    strokeColor: '#111827',
    pattern: (cx, cy, r) => (
      <>
        {/* Finger holes */}
        <circle cx={cx - r * 0.25} cy={cy - r * 0.2} r={r * 0.12} fill="#374151" />
        <circle cx={cx + r * 0.1} cy={cy - r * 0.25} r={r * 0.12} fill="#374151" />
        <circle cx={cx + r * 0.25} cy={cy + r * 0.1} r={r * 0.12} fill="#374151" />
      </>
    ),
  },
  generic: {
    color: '#3B82F6',
    strokeColor: '#1D4ED8',
    pattern: () => null,
  },
};

const Ball = ({
  type = 'generic',
  x = 0,
  y = 0,
  radius = 20,
  color,
  label = '',
  mass = '',
  animate = false,
  animateX = 0,
  animateY = 0,
  showForce = false,
  forceDirection = 'right',
  forceMagnitude = 0,
  glow = false,
  pulse = false,
}) => {
  const ballConfig = BALL_TYPES[type] || BALL_TYPES.generic;
  const fillColor = color || ballConfig.color;
  const strokeColor = ballConfig.strokeColor;
  const PatternComponent = ballConfig.pattern;

  return (
    <motion.g
      initial={animate ? { x: 0, y: 0 } : undefined}
      animate={animate ? { x: animateX, y: animateY } : undefined}
      transition={{ duration: 2, ease: 'easeOut' }}
    >
      <g transform={`translate(${x}, ${y})`}>
        {/* Glow effect */}
        {glow && (
          <motion.circle
            cx={0}
            cy={0}
            r={radius + 5}
            fill="none"
            stroke={fillColor}
            strokeWidth={3}
            opacity={0.5}
            animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.2, 0.5] }}
            transition={{ repeat: Infinity, duration: 1.5 }}
          />
        )}

        {/* Main ball */}
        <motion.circle
          cx={0}
          cy={0}
          r={radius}
          fill={fillColor}
          stroke={strokeColor}
          strokeWidth={2}
          animate={pulse ? { scale: [1, 1.1, 1] } : undefined}
          transition={pulse ? { repeat: Infinity, duration: 0.5 } : undefined}
        />

        {/* Pattern */}
        {PatternComponent && PatternComponent(0, 0, radius)}

        {/* Shine */}
        <ellipse cx={-radius * 0.3} cy={-radius * 0.3} rx={radius * 0.2} ry={radius * 0.15} fill="white" opacity={0.4} />

        {/* Mass label */}
        {mass && (
          <text x={0} y={radius * 0.15} fontSize={radius * 0.6} textAnchor="middle" fill="white" fontWeight="bold">
            {mass}
          </text>
        )}

        {/* Label below */}
        {label && (
          <text x={0} y={radius + 18} fontSize={12} textAnchor="middle" fill="#374151" fontWeight="bold">
            {label}
          </text>
        )}

        {/* Force arrow */}
        {showForce && (
          <g transform={`rotate(${forceDirection === 'left' ? 180 : forceDirection === 'up' ? -90 : forceDirection === 'down' ? 90 : 0})`}>
            <motion.line
              x1={radius + 5}
              y1={0}
              x2={radius + 30 + forceMagnitude}
              y2={0}
              stroke="#10B981"
              strokeWidth={4}
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 0.5 }}
            />
            <polygon
              points={`${radius + 30 + forceMagnitude},0 ${radius + 20 + forceMagnitude},-6 ${radius + 20 + forceMagnitude},6`}
              fill="#10B981"
            />
            <text x={radius + 15 + forceMagnitude / 2} y={-10} fontSize={10} fill="#10B981" fontWeight="bold">
              F
            </text>
          </g>
        )}
      </g>
    </motion.g>
  );
};

export default Ball;

