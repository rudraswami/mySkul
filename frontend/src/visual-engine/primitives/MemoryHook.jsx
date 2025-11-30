/**
 * 💡 MemoryHook Primitive
 * =======================
 * 
 * Memorable takeaway banner for concept retention.
 */

import React from 'react';
import { motion } from 'framer-motion';

const MemoryHook = ({
  x = 0,
  y = 0,
  text = 'Remember this!',
  color = '#10B981',
  backgroundColor = '#ECFDF5',
  width = 300,
  animated = true,
  delay = 0,
  icon = '💡',
  style = 'pill', // pill, banner, sticky, speech
}) => {
  const height = 40;

  if (style === 'sticky') {
    return (
      <motion.g
        initial={animated ? { y: y + 20, opacity: 0, rotate: -5 } : undefined}
        animate={animated ? { y, opacity: 1, rotate: 2 } : undefined}
        transition={{ delay, type: 'spring', stiffness: 200 }}
      >
        {/* Shadow */}
        <rect
          x={x - width / 2 + 5}
          y={y - height / 2 + 5}
          width={width}
          height={height + 10}
          rx={3}
          fill="rgba(0,0,0,0.1)"
        />
        {/* Sticky note */}
        <rect
          x={x - width / 2}
          y={y - height / 2}
          width={width}
          height={height + 10}
          rx={3}
          fill="#FEF08A"
          stroke="#FCD34D"
          strokeWidth={1}
        />
        {/* Tape */}
        <rect
          x={x - 20}
          y={y - height / 2 - 8}
          width={40}
          height={15}
          fill="rgba(255,255,255,0.7)"
          stroke="#D1D5DB"
          strokeWidth={1}
        />
        {/* Text */}
        <text
          x={x}
          y={y + 5}
          fontSize={13}
          fontWeight="bold"
          textAnchor="middle"
          fill="#92400E"
          fontFamily="'Caveat', cursive"
        >
          {icon} {text}
        </text>
      </motion.g>
    );
  }

  if (style === 'speech') {
    return (
      <motion.g
        initial={animated ? { scale: 0, opacity: 0 } : undefined}
        animate={animated ? { scale: 1, opacity: 1 } : undefined}
        transition={{ delay, type: 'spring', stiffness: 200 }}
      >
        {/* Speech bubble */}
        <path
          d={`M ${x - width / 2} ${y - height / 2}
              L ${x + width / 2} ${y - height / 2}
              Q ${x + width / 2 + 10} ${y - height / 2} ${x + width / 2 + 10} ${y - height / 2 + 10}
              L ${x + width / 2 + 10} ${y + height / 2 - 10}
              Q ${x + width / 2 + 10} ${y + height / 2} ${x + width / 2} ${y + height / 2}
              L ${x - 20} ${y + height / 2}
              L ${x - 30} ${y + height / 2 + 15}
              L ${x - 10} ${y + height / 2}
              L ${x - width / 2} ${y + height / 2}
              Q ${x - width / 2 - 10} ${y + height / 2} ${x - width / 2 - 10} ${y + height / 2 - 10}
              L ${x - width / 2 - 10} ${y - height / 2 + 10}
              Q ${x - width / 2 - 10} ${y - height / 2} ${x - width / 2} ${y - height / 2}
              Z`}
          fill="white"
          stroke={color}
          strokeWidth={2}
        />
        <text
          x={x}
          y={y + 5}
          fontSize={13}
          fontWeight="bold"
          textAnchor="middle"
          fill={color}
        >
          {icon} {text}
        </text>
      </motion.g>
    );
  }

  if (style === 'banner') {
    return (
      <motion.g
        initial={animated ? { scaleX: 0, opacity: 0 } : undefined}
        animate={animated ? { scaleX: 1, opacity: 1 } : undefined}
        transition={{ delay, duration: 0.5 }}
        style={{ originX: 0.5 }}
      >
        {/* Banner */}
        <rect
          x={x - width / 2}
          y={y - height / 2}
          width={width}
          height={height}
          fill={backgroundColor}
          stroke={color}
          strokeWidth={3}
        />
        {/* Ribbon ends */}
        <polygon
          points={`${x - width / 2} ${y - height / 2} ${x - width / 2 - 15} ${y} ${x - width / 2} ${y + height / 2}`}
          fill={color}
        />
        <polygon
          points={`${x + width / 2} ${y - height / 2} ${x + width / 2 + 15} ${y} ${x + width / 2} ${y + height / 2}`}
          fill={color}
        />
        <text
          x={x}
          y={y + 5}
          fontSize={14}
          fontWeight="bold"
          textAnchor="middle"
          fill={color}
        >
          {icon} {text}
        </text>
      </motion.g>
    );
  }

  // Default pill style
  return (
    <motion.g
      initial={animated ? { y: y + 20, opacity: 0 } : undefined}
      animate={animated ? { y, opacity: 1 } : undefined}
      transition={{ delay, type: 'spring', stiffness: 200 }}
    >
      <rect
        x={x - width / 2}
        y={y - height / 2}
        width={width}
        height={height}
        rx={height / 2}
        fill={backgroundColor}
        stroke={color}
        strokeWidth={2}
      />
      <text
        x={x}
        y={y + 5}
        fontSize={14}
        fontWeight="bold"
        textAnchor="middle"
        fill={color}
      >
        {icon} {text}
      </text>
    </motion.g>
  );
};

export default MemoryHook;

