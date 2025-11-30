/**
 * ➡️ Arrow Primitive
 * ==================
 * 
 * Configurable arrow for forces, vectors, flow directions.
 * Supports: force, velocity, acceleration, flow, pointer
 */

import React from 'react';
import { motion } from 'framer-motion';

const Arrow = ({
  x1 = 0,
  y1 = 0,
  x2 = 50,
  y2 = 0,
  color = '#10B981',
  strokeWidth = 4,
  label = '',
  labelPosition = 'above', // above, below, middle
  arrowSize = 10,
  dashed = false,
  animated = true,
  delay = 0,
  curved = false,
  curveHeight = 20,
  bidirectional = false,
  style = 'solid', // solid, dashed, dotted
}) => {
  const angle = Math.atan2(y2 - y1, x2 - x1);
  const length = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
  const midX = (x1 + x2) / 2;
  const midY = (y1 + y2) / 2;

  // Calculate arrowhead points
  const arrowPoint1X = x2 - arrowSize * Math.cos(angle - Math.PI / 6);
  const arrowPoint1Y = y2 - arrowSize * Math.sin(angle - Math.PI / 6);
  const arrowPoint2X = x2 - arrowSize * Math.cos(angle + Math.PI / 6);
  const arrowPoint2Y = y2 - arrowSize * Math.sin(angle + Math.PI / 6);

  // Back arrowhead for bidirectional
  const backArrow1X = x1 + arrowSize * Math.cos(angle - Math.PI / 6);
  const backArrow1Y = y1 + arrowSize * Math.sin(angle - Math.PI / 6);
  const backArrow2X = x1 + arrowSize * Math.cos(angle + Math.PI / 6);
  const backArrow2Y = y1 + arrowSize * Math.sin(angle + Math.PI / 6);

  // Curved path
  const curvedPath = curved
    ? `M ${x1} ${y1} Q ${midX} ${midY - curveHeight} ${x2} ${y2}`
    : null;

  const strokeDasharray = style === 'dashed' ? '8 4' : style === 'dotted' ? '2 4' : 'none';

  // Label position calculation
  const labelOffset = labelPosition === 'above' ? -12 : labelPosition === 'below' ? 18 : 0;
  const labelRotation = Math.abs(angle) > Math.PI / 2 ? angle + Math.PI : angle;

  return (
    <motion.g
      initial={animated ? { opacity: 0 } : undefined}
      animate={animated ? { opacity: 1 } : undefined}
      transition={{ delay, duration: 0.3 }}
    >
      {/* Arrow line */}
      {curved ? (
        <motion.path
          d={curvedPath}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={strokeDasharray}
          initial={animated ? { pathLength: 0 } : undefined}
          animate={animated ? { pathLength: 1 } : undefined}
          transition={{ delay, duration: 0.6, ease: 'easeOut' }}
        />
      ) : (
        <motion.line
          x1={x1}
          y1={y1}
          x2={x2}
          y2={y2}
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={strokeDasharray}
          initial={animated ? { pathLength: 0 } : undefined}
          animate={animated ? { pathLength: 1 } : undefined}
          transition={{ delay, duration: 0.6, ease: 'easeOut' }}
        />
      )}

      {/* Forward arrowhead */}
      <motion.polygon
        points={`${x2},${y2} ${arrowPoint1X},${arrowPoint1Y} ${arrowPoint2X},${arrowPoint2Y}`}
        fill={color}
        initial={animated ? { scale: 0, opacity: 0 } : undefined}
        animate={animated ? { scale: 1, opacity: 1 } : undefined}
        transition={{ delay: delay + 0.4, duration: 0.2 }}
      />

      {/* Back arrowhead for bidirectional */}
      {bidirectional && (
        <motion.polygon
          points={`${x1},${y1} ${backArrow1X},${backArrow1Y} ${backArrow2X},${backArrow2Y}`}
          fill={color}
          initial={animated ? { scale: 0, opacity: 0 } : undefined}
          animate={animated ? { scale: 1, opacity: 1 } : undefined}
          transition={{ delay: delay + 0.4, duration: 0.2 }}
        />
      )}

      {/* Label */}
      {label && (
        <motion.text
          x={midX}
          y={midY + labelOffset}
          fontSize={12}
          textAnchor="middle"
          fill={color}
          fontWeight="bold"
          fontFamily="sans-serif"
          initial={animated ? { opacity: 0 } : undefined}
          animate={animated ? { opacity: 1 } : undefined}
          transition={{ delay: delay + 0.5, duration: 0.3 }}
        >
          {label}
        </motion.text>
      )}
    </motion.g>
  );
};

export default Arrow;

