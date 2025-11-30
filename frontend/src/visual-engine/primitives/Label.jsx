/**
 * 🏷️ Label Primitive
 * ===================
 * 
 * Configurable label/badge for annotations.
 */

import React from 'react';
import { motion } from 'framer-motion';

const Label = ({
  x = 0,
  y = 0,
  text = 'Label',
  color = '#FF9933',
  textColor = 'white',
  size = 'medium', // small, medium, large
  shape = 'rounded', // rounded, pill, badge, tag
  animated = true,
  delay = 0,
  icon = null,
  pulse = false,
}) => {
  const sizes = {
    small: { fontSize: 10, paddingX: 8, paddingY: 4, rx: 4 },
    medium: { fontSize: 12, paddingX: 12, paddingY: 6, rx: 6 },
    large: { fontSize: 14, paddingX: 16, paddingY: 8, rx: 8 },
  };

  const sizeConfig = sizes[size] || sizes.medium;
  const textWidth = text.length * (sizeConfig.fontSize * 0.6);
  const width = textWidth + sizeConfig.paddingX * 2 + (icon ? 20 : 0);
  const height = sizeConfig.fontSize + sizeConfig.paddingY * 2;

  const rx = shape === 'pill' ? height / 2 : shape === 'badge' ? 4 : sizeConfig.rx;

  return (
    <motion.g
      initial={animated ? { scale: 0, opacity: 0 } : undefined}
      animate={animated ? { scale: 1, opacity: 1 } : undefined}
      transition={{ delay, type: 'spring', stiffness: 300 }}
    >
      {/* Background */}
      <motion.rect
        x={x - width / 2}
        y={y - height / 2}
        width={width}
        height={height}
        rx={rx}
        fill={color}
        animate={pulse ? { scale: [1, 1.05, 1] } : undefined}
        transition={pulse ? { repeat: Infinity, duration: 1.5 } : undefined}
      />

      {/* Icon */}
      {icon && (
        <text
          x={x - width / 2 + sizeConfig.paddingX}
          y={y + sizeConfig.fontSize / 3}
          fontSize={sizeConfig.fontSize}
        >
          {icon}
        </text>
      )}

      {/* Text */}
      <text
        x={x + (icon ? 8 : 0)}
        y={y + sizeConfig.fontSize / 3}
        fontSize={sizeConfig.fontSize}
        fontWeight="bold"
        textAnchor="middle"
        fill={textColor}
        fontFamily="sans-serif"
      >
        {text}
      </text>
    </motion.g>
  );
};

export default Label;

