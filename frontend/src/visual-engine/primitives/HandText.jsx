/**
 * ✍️ HandText Primitive
 * =====================
 * 
 * Hand-written style text for sketch aesthetics.
 */

import React from 'react';
import { motion } from 'framer-motion';

const HandText = ({
  x = 0,
  y = 0,
  children,
  size = 16,
  color = '#2D3436',
  weight = 'normal', // normal, bold, light
  anchor = 'middle', // start, middle, end
  animated = true,
  delay = 0,
  underline = false,
  highlight = false,
  highlightColor = '#FEF08A',
  rotation = 0,
  opacity = 1,
}) => {
  const fontWeight = weight === 'bold' ? '700' : weight === 'light' ? '300' : '400';
  
  // Calculate text width approximation for underline/highlight
  const textWidth = String(children).length * size * 0.5;

  return (
    <motion.g
      initial={animated ? { opacity: 0, y: y + 10 } : undefined}
      animate={animated ? { opacity, y } : undefined}
      transition={{ delay, duration: 0.4 }}
      transform={rotation ? `rotate(${rotation}, ${x}, ${y})` : undefined}
    >
      {/* Highlight background */}
      {highlight && (
        <rect
          x={anchor === 'middle' ? x - textWidth / 2 - 5 : anchor === 'end' ? x - textWidth - 5 : x - 5}
          y={y - size * 0.7}
          width={textWidth + 10}
          height={size * 1.2}
          rx={4}
          fill={highlightColor}
        />
      )}

      {/* Main text */}
      <text
        x={x}
        y={y}
        fontSize={size}
        fontWeight={fontWeight}
        textAnchor={anchor}
        fill={color}
        fontFamily="'Caveat', 'Patrick Hand', 'Comic Sans MS', cursive"
        style={{ letterSpacing: '0.02em' }}
      >
        {children}
      </text>

      {/* Underline */}
      {underline && (
        <motion.line
          x1={anchor === 'middle' ? x - textWidth / 2 : anchor === 'end' ? x - textWidth : x}
          y1={y + 5}
          x2={anchor === 'middle' ? x + textWidth / 2 : anchor === 'end' ? x : x + textWidth}
          y2={y + 5}
          stroke={color}
          strokeWidth={2}
          initial={animated ? { pathLength: 0 } : undefined}
          animate={animated ? { pathLength: 1 } : undefined}
          transition={{ delay: delay + 0.3, duration: 0.4 }}
        />
      )}
    </motion.g>
  );
};

export default HandText;

