/**
 * VectorArrow - Animated Force/Motion Vector
 * Shows magnitude and direction with smooth animation
 */

import React from 'react';
import { motion } from 'framer-motion';

const VectorArrow = ({
  id,
  target,
  direction = 'right',
  length = 100,
  opacity = 1,
  color = 'force',
  label,
  labelHi,
  width,
  height,
  startX,
  startY,
  style = {},
}) => {
  // Default positions based on direction
  const positions = {
    right: { x: startX || width * 0.3, y: startY || height * 0.5, angle: 0 },
    left: { x: startX || width * 0.7, y: startY || height * 0.5, angle: 180 },
    up: { x: startX || width * 0.5, y: startY || height * 0.7, angle: -90 },
    down: { x: startX || width * 0.5, y: startY || height * 0.3, angle: 90 },
    diagonal_up: { x: startX || width * 0.3, y: startY || height * 0.6, angle: -30 },
    diagonal_down: { x: startX || width * 0.3, y: startY || height * 0.4, angle: 30 },
  };

  const pos = positions[direction] || positions['right'];

  const colors = {
    force: { fill: '#FF9800', stroke: '#E65100', gradient: ['#FFB74D', '#FF9800'] },
    motion: { fill: '#4CAF50', stroke: '#2E7D32', gradient: ['#81C784', '#4CAF50'] },
    gravity: { fill: '#9C27B0', stroke: '#6A1B9A', gradient: ['#BA68C8', '#9C27B0'] },
    friction: { fill: '#F44336', stroke: '#C62828', gradient: ['#EF5350', '#F44336'] },
    tension: { fill: '#2196F3', stroke: '#1565C0', gradient: ['#64B5F6', '#2196F3'] },
    normal: { fill: '#00BCD4', stroke: '#00838F', gradient: ['#4DD0E1', '#00BCD4'] },
  };

  const colorSet = colors[color] || colors['force'];

  return (
    <motion.g
      id={`vector-${id}`}
      transform={`translate(${pos.x}, ${pos.y}) rotate(${pos.angle})`}
      initial={{ opacity: 0 }}
      animate={{ opacity }}
      transition={{ duration: 0.3 }}
    >
      {/* Gradient definition */}
      <defs>
        <linearGradient id={`vector-gradient-${id}`} x1="0%" y1="50%" x2="100%" y2="50%">
          <stop offset="0%" stopColor={colorSet.gradient[0]} />
          <stop offset="100%" stopColor={colorSet.gradient[1]} />
        </linearGradient>
        
        {/* Glow filter */}
        <filter id={`vector-glow-${id}`} x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="4" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {/* Arrow body */}
      <motion.rect
        x="0"
        y="-8"
        width={length * 0.7}
        height="16"
        rx="4"
        fill={`url(#vector-gradient-${id})`}
        filter={`url(#vector-glow-${id})`}
        initial={{ width: 0 }}
        animate={{ width: length * 0.7 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
      />

      {/* Arrow head */}
      <motion.polygon
        points={`${length * 0.65},-15 ${length},0 ${length * 0.65},15`}
        fill={colorSet.fill}
        stroke={colorSet.stroke}
        strokeWidth="2"
        filter={`url(#vector-glow-${id})`}
        initial={{ x: -length }}
        animate={{ x: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
      />

      {/* Magnitude indicator (dashed lines) */}
      {length > 80 && (
        <g opacity="0.5">
          <line x1="0" y1="25" x2={length} y2="25" stroke={colorSet.stroke} strokeWidth="1" strokeDasharray="4 4" />
          <line x1="0" y1="20" x2="0" y2="30" stroke={colorSet.stroke} strokeWidth="2" />
          <line x1={length} y1="20" x2={length} y2="30" stroke={colorSet.stroke} strokeWidth="2" />
        </g>
      )}

      {/* Label */}
      {label && (
        <motion.g
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.3 }}
        >
          {/* Label background */}
          <rect
            x={length / 2 - 50}
            y="-40"
            width="100"
            height="28"
            rx="6"
            fill={colorSet.fill}
            opacity="0.9"
          />
          
          {/* Label text */}
          <text
            x={length / 2}
            y="-22"
            textAnchor="middle"
            fontSize="14"
            fontWeight="bold"
            fill="white"
          >
            {label}
          </text>
          
          {/* Hindi label */}
          {labelHi && (
            <text
              x={length / 2}
              y={length > 80 ? 45 : -55}
              textAnchor="middle"
              fontSize="12"
              fill={colorSet.stroke}
            >
              {labelHi}
            </text>
          )}
        </motion.g>
      )}

      {/* Animation particles along the arrow */}
      <g>
        {[...Array(3)].map((_, i) => (
          <motion.circle
            key={i}
            cx="0"
            cy="0"
            r="3"
            fill="white"
            opacity="0.8"
            animate={{
              cx: [0, length * 0.8],
              opacity: [0, 1, 0],
            }}
            transition={{
              repeat: Infinity,
              duration: 1.5,
              delay: i * 0.3,
              ease: 'easeInOut',
            }}
          />
        ))}
      </g>
    </motion.g>
  );
};

/**
 * Multi-directional force arrows for free body diagrams
 */
export const ForceArrows = ({
  forces = [],
  centerX,
  centerY,
  width,
  height,
}) => {
  return (
    <g id="force-arrows">
      {forces.map((force, i) => (
        <VectorArrow
          key={force.id || i}
          {...force}
          startX={centerX}
          startY={centerY}
          width={width}
          height={height}
        />
      ))}
    </g>
  );
};

export default VectorArrow;


