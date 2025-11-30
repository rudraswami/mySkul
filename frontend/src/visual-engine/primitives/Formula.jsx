/**
 * 📐 Formula Primitive
 * ====================
 * 
 * Beautiful formula display with optional value substitution.
 * Supports highlighting, step-by-step reveal, and live values.
 */

import React from 'react';
import { motion } from 'framer-motion';

const Formula = ({
  x = 0,
  y = 0,
  formula = 'E = mc²',
  values = {}, // { m: '10', c: '3×10⁸', E: '?' }
  showSubstitution = false,
  color = '#000080',
  backgroundColor = '#FEF3C7',
  borderColor = '#FF9933',
  fontSize = 20,
  animated = true,
  delay = 0,
  width = 200,
  height = 60,
  title = '',
  highlight = false,
}) => {
  // Parse formula and substitute values
  const substituteFormula = () => {
    if (!showSubstitution || !values) return formula;
    let result = formula;
    Object.entries(values).forEach(([key, val]) => {
      result = result.replace(new RegExp(key, 'g'), val);
    });
    return result;
  };

  return (
    <motion.g
      initial={animated ? { opacity: 0, y: y + 20 } : undefined}
      animate={animated ? { opacity: 1, y } : undefined}
      transition={{ delay, duration: 0.5 }}
    >
      {/* Highlight glow */}
      {highlight && (
        <motion.rect
          x={x - width / 2 - 5}
          y={y - height / 2 - 5}
          width={width + 10}
          height={height + 10}
          rx={15}
          fill="none"
          stroke={borderColor}
          strokeWidth={3}
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
        />
      )}

      {/* Background box */}
      <rect
        x={x - width / 2}
        y={y - height / 2}
        width={width}
        height={height}
        rx={12}
        fill={backgroundColor}
        stroke={borderColor}
        strokeWidth={3}
      />

      {/* Title (if provided) */}
      {title && (
        <text
          x={x}
          y={y - height / 2 + 16}
          fontSize={12}
          textAnchor="middle"
          fill="#636E72"
          fontFamily="sans-serif"
        >
          {title}
        </text>
      )}

      {/* Main formula */}
      <text
        x={x}
        y={y + (title ? 8 : 5)}
        fontSize={fontSize}
        fontWeight="bold"
        textAnchor="middle"
        fill={color}
        fontFamily="'Caveat', 'Patrick Hand', cursive"
      >
        {formula}
      </text>

      {/* Substituted values (if enabled) */}
      {showSubstitution && (
        <motion.text
          x={x}
          y={y + height / 2 - 8}
          fontSize={fontSize * 0.7}
          textAnchor="middle"
          fill="#10B981"
          fontWeight="bold"
          fontFamily="'Caveat', cursive"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: delay + 0.5, duration: 0.3 }}
        >
          {substituteFormula()}
        </motion.text>
      )}
    </motion.g>
  );
};

export default Formula;

