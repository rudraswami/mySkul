/**
 * 📦 Container Primitive
 * ======================
 * 
 * Configurable container/panel for grouping elements.
 */

import React from 'react';
import { motion } from 'framer-motion';

const Container = ({
  x = 0,
  y = 0,
  width = 150,
  height = 100,
  title = '',
  titlePosition = 'top', // top, inside
  color = '#3B82F6',
  backgroundColor = 'white',
  borderStyle = 'solid', // solid, dashed, double
  borderRadius = 12,
  animated = true,
  delay = 0,
  icon = null,
  badge = null,
  glow = false,
  children,
}) => {
  const strokeDasharray = borderStyle === 'dashed' ? '8 4' : 'none';

  return (
    <motion.g
      initial={animated ? { opacity: 0, scale: 0.9 } : undefined}
      animate={animated ? { opacity: 1, scale: 1 } : undefined}
      transition={{ delay, duration: 0.4 }}
    >
      {/* Glow effect */}
      {glow && (
        <motion.rect
          x={x - 5}
          y={y - 5}
          width={width + 10}
          height={height + 10}
          rx={borderRadius + 5}
          fill="none"
          stroke={color}
          strokeWidth={3}
          opacity={0.3}
          animate={{ opacity: [0.3, 0.6, 0.3] }}
          transition={{ repeat: Infinity, duration: 2 }}
        />
      )}

      {/* Main container */}
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        rx={borderRadius}
        fill={backgroundColor}
        stroke={color}
        strokeWidth={2}
        strokeDasharray={strokeDasharray}
      />

      {/* Title bar */}
      {title && titlePosition === 'top' && (
        <>
          <rect
            x={x}
            y={y}
            width={width}
            height={28}
            rx={borderRadius}
            fill={color}
          />
          {/* Bottom corners fix */}
          <rect
            x={x}
            y={y + 15}
            width={width}
            height={13}
            fill={color}
          />
          {/* Icon */}
          {icon && (
            <text x={x + 12} y={y + 19} fontSize={14}>
              {icon}
            </text>
          )}
          {/* Title text */}
          <text
            x={x + (icon ? 30 : 12)}
            y={y + 19}
            fontSize={12}
            fontWeight="bold"
            fill="white"
          >
            {title}
          </text>
        </>
      )}

      {/* Inside title */}
      {title && titlePosition === 'inside' && (
        <text
          x={x + width / 2}
          y={y + 20}
          fontSize={12}
          fontWeight="bold"
          textAnchor="middle"
          fill={color}
        >
          {icon && icon} {title}
        </text>
      )}

      {/* Badge */}
      {badge && (
        <g transform={`translate(${x + width - 25}, ${y - 10})`}>
          <rect
            x={0}
            y={0}
            width={35}
            height={20}
            rx={10}
            fill={color}
          />
          <text
            x={17}
            y={14}
            fontSize={10}
            fontWeight="bold"
            textAnchor="middle"
            fill="white"
          >
            {badge}
          </text>
        </g>
      )}
    </motion.g>
  );
};

export default Container;

