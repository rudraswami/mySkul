/**
 * 🖊️ AnimatedPath Primitive
 * =========================
 * 
 * Hand-drawn animated SVG path.
 */

import React, { useRef, useState, useEffect } from 'react';
import { motion } from 'framer-motion';

// Add wobble for hand-drawn effect
const wobble = (value, amount = 2) => value + (Math.random() - 0.5) * amount;

// Generate hand-drawn line path
export const handDrawnLine = (x1, y1, x2, y2, segments = 8) => {
  let d = `M ${wobble(x1)} ${wobble(y1)}`;
  for (let i = 1; i <= segments; i++) {
    const t = i / segments;
    const x = x1 + (x2 - x1) * t;
    const y = y1 + (y2 - y1) * t;
    d += ` L ${wobble(x, 1.5)} ${wobble(y, 1.5)}`;
  }
  return d;
};

// Generate hand-drawn rectangle
export const handDrawnRect = (x, y, width, height) => {
  return [
    handDrawnLine(x, y, x + width, y),
    handDrawnLine(x + width, y, x + width, y + height),
    handDrawnLine(x + width, y + height, x, y + height),
    handDrawnLine(x, y + height, x, y),
  ].join(' ');
};

// Generate hand-drawn circle (approximation)
export const handDrawnCircle = (cx, cy, r, segments = 24) => {
  let d = '';
  for (let i = 0; i <= segments; i++) {
    const angle = (i / segments) * 2 * Math.PI;
    const x = cx + Math.cos(angle) * r;
    const y = cy + Math.sin(angle) * r;
    d += `${i === 0 ? 'M' : 'L'} ${wobble(x, 1)} ${wobble(y, 1)} `;
  }
  return d + 'Z';
};

const AnimatedPath = ({
  d,
  stroke = '#2D3436',
  strokeWidth = 3,
  fill = 'none',
  delay = 0,
  duration = 0.8,
  animated = true,
  handDrawn = false,
  onComplete,
}) => {
  const pathRef = useRef(null);
  const [length, setLength] = useState(500);

  useEffect(() => {
    if (pathRef.current) {
      setLength(pathRef.current.getTotalLength() || 500);
    }
  }, [d]);

  return (
    <motion.path
      ref={pathRef}
      d={d}
      stroke={stroke}
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      fill={fill}
      initial={animated ? { strokeDasharray: length, strokeDashoffset: length, opacity: 0 } : undefined}
      animate={animated ? { strokeDashoffset: 0, opacity: 1 } : undefined}
      transition={{ delay, duration, ease: 'easeInOut' }}
      onAnimationComplete={onComplete}
    />
  );
};

export default AnimatedPath;

