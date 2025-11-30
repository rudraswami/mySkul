/**
 * ➡️ FlowArrow Primitive
 * ======================
 * 
 * Animated flow arrow for process diagrams.
 */

import React from 'react';
import { motion } from 'framer-motion';

const FlowArrow = ({
  x1 = 0,
  y1 = 0,
  x2 = 100,
  y2 = 0,
  color = '#10B981',
  label = '',
  animated = true,
  delay = 0,
  particles = false,
  particleCount = 3,
  style = 'straight', // straight, curved, zigzag
  thickness = 'medium', // thin, medium, thick
}) => {
  const strokeWidths = { thin: 2, medium: 4, thick: 6 };
  const strokeWidth = strokeWidths[thickness] || strokeWidths.medium;
  
  const midX = (x1 + x2) / 2;
  const midY = (y1 + y2) / 2;
  const length = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
  const angle = Math.atan2(y2 - y1, x2 - x1) * (180 / Math.PI);

  // Path based on style
  let path;
  switch (style) {
    case 'curved':
      const curveHeight = length * 0.2;
      path = `M ${x1} ${y1} Q ${midX} ${midY - curveHeight} ${x2} ${y2}`;
      break;
    case 'zigzag':
      const segLen = length / 4;
      const zigHeight = 10;
      path = `M ${x1} ${y1} L ${x1 + segLen} ${y1 - zigHeight} L ${x1 + 2*segLen} ${y1 + zigHeight} L ${x1 + 3*segLen} ${y1 - zigHeight} L ${x2} ${y2}`;
      break;
    default:
      path = `M ${x1} ${y1} L ${x2} ${y2}`;
  }

  return (
    <g>
      {/* Arrow path */}
      <motion.path
        d={path}
        stroke={color}
        strokeWidth={strokeWidth}
        fill="none"
        strokeLinecap="round"
        initial={animated ? { pathLength: 0, opacity: 0 } : undefined}
        animate={animated ? { pathLength: 1, opacity: 1 } : undefined}
        transition={{ delay, duration: 0.6, ease: 'easeOut' }}
      />

      {/* Arrowhead */}
      <motion.polygon
        points={`${x2},${y2} ${x2-12},${y2-5} ${x2-12},${y2+5}`}
        fill={color}
        transform={`rotate(${angle}, ${x2}, ${y2})`}
        initial={animated ? { scale: 0 } : undefined}
        animate={animated ? { scale: 1 } : undefined}
        transition={{ delay: delay + 0.4, duration: 0.2 }}
      />

      {/* Animated particles */}
      {particles && Array.from({ length: particleCount }).map((_, i) => (
        <motion.circle
          key={i}
          r={4}
          fill={color}
          initial={{ x: x1, y: y1, opacity: 0 }}
          animate={{
            x: [x1, x2],
            y: [y1, y2],
            opacity: [0, 1, 1, 0],
          }}
          transition={{
            delay: delay + 0.5 + i * 0.3,
            duration: 1.5,
            repeat: Infinity,
            repeatDelay: 0.5,
            ease: 'easeInOut',
          }}
        />
      ))}

      {/* Label */}
      {label && (
        <motion.text
          x={midX}
          y={midY - 10}
          fontSize={10}
          textAnchor="middle"
          fill={color}
          fontWeight="bold"
          initial={animated ? { opacity: 0 } : undefined}
          animate={animated ? { opacity: 1 } : undefined}
          transition={{ delay: delay + 0.5 }}
        >
          {label}
        </motion.text>
      )}
    </g>
  );
};

export default FlowArrow;

