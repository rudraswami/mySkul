/**
 * 🔢 Counter Primitive
 * ====================
 * 
 * Live updating counter with animations.
 * Perfect for showing changing values (speed, distance, time).
 */

import React from 'react';
import { motion } from 'framer-motion';

const Counter = ({
  x = 0,
  y = 0,
  value = 0,
  label = 'Value',
  unit = '',
  color = '#FF9933',
  backgroundColor = 'white',
  size = 'medium', // small, medium, large
  decimals = 1,
  animated = true,
  showLabel = true,
  style = 'box', // box, digital, minimal
  icon = null,
}) => {
  const sizes = {
    small: { width: 60, height: 35, fontSize: 14, labelSize: 9 },
    medium: { width: 80, height: 45, fontSize: 18, labelSize: 10 },
    large: { width: 100, height: 55, fontSize: 24, labelSize: 12 },
  };

  const sizeConfig = sizes[size] || sizes.medium;
  const displayValue = typeof value === 'number' ? value.toFixed(decimals) : value;

  if (style === 'digital') {
    return (
      <motion.g
        initial={animated ? { opacity: 0, scale: 0.8 } : undefined}
        animate={animated ? { opacity: 1, scale: 1 } : undefined}
      >
        <rect
          x={x - sizeConfig.width / 2}
          y={y - sizeConfig.height / 2}
          width={sizeConfig.width}
          height={sizeConfig.height}
          rx={6}
          fill="#1F2937"
          stroke={color}
          strokeWidth={2}
        />
        
        {showLabel && (
          <text
            x={x}
            y={y - sizeConfig.height / 4}
            fontSize={sizeConfig.labelSize}
            textAnchor="middle"
            fill={color}
            fontFamily="sans-serif"
          >
            {label}
          </text>
        )}
        
        <motion.text
          x={x}
          y={y + sizeConfig.fontSize / 3}
          fontSize={sizeConfig.fontSize}
          fontWeight="bold"
          textAnchor="middle"
          fill="#10B981"
          fontFamily="monospace"
          key={displayValue}
          initial={{ scale: 1.2 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.2 }}
        >
          {displayValue}{unit}
        </motion.text>
      </motion.g>
    );
  }

  if (style === 'minimal') {
    return (
      <motion.g
        initial={animated ? { opacity: 0 } : undefined}
        animate={animated ? { opacity: 1 } : undefined}
      >
        <motion.text
          x={x}
          y={y}
          fontSize={sizeConfig.fontSize * 1.2}
          fontWeight="bold"
          textAnchor="middle"
          fill={color}
          fontFamily="'Caveat', cursive"
          key={displayValue}
          initial={{ scale: 1.3 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 500 }}
        >
          {icon && icon} {displayValue}{unit}
        </motion.text>
        {showLabel && (
          <text
            x={x}
            y={y + 16}
            fontSize={sizeConfig.labelSize}
            textAnchor="middle"
            fill="#636E72"
          >
            {label}
          </text>
        )}
      </motion.g>
    );
  }

  // Default box style
  return (
    <motion.g
      initial={animated ? { opacity: 0, scale: 0.8 } : undefined}
      animate={animated ? { opacity: 1, scale: 1 } : undefined}
      transition={{ type: 'spring', stiffness: 200 }}
    >
      <rect
        x={x - sizeConfig.width / 2}
        y={y - sizeConfig.height / 2}
        width={sizeConfig.width}
        height={sizeConfig.height}
        rx={8}
        fill={backgroundColor}
        stroke={color}
        strokeWidth={2}
      />

      {showLabel && (
        <text
          x={x}
          y={y - sizeConfig.height / 4 + 3}
          fontSize={sizeConfig.labelSize}
          textAnchor="middle"
          fill="#636E72"
          fontFamily="sans-serif"
        >
          {label}
        </text>
      )}

      <motion.text
        x={x}
        y={y + sizeConfig.fontSize / 3 + 2}
        fontSize={sizeConfig.fontSize}
        fontWeight="bold"
        textAnchor="middle"
        fill={color}
        fontFamily="'Caveat', cursive"
        key={displayValue}
        initial={{ scale: 1.3 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', stiffness: 500 }}
      >
        {displayValue}{unit}
      </motion.text>
    </motion.g>
  );
};

export default Counter;

