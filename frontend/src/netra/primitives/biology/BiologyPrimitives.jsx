/**
 * 🧬 BIOLOGY PRIMITIVES
 * =====================
 * 
 * Visual components for biology concepts.
 * Organic, flowing shapes for life sciences.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { PRIMITIVE_THEMES } from '../UniversalPrimitives';

const theme = PRIMITIVE_THEMES.biology;

/**
 * Cell - Basic cell structure
 */
export const Cell = ({
  cx = 100,
  cy = 100,
  size = 80,
  type = 'animal', // animal, plant, bacteria
  showNucleus = true,
  showOrganelles = true,
  color = theme.primary,
  animate = true,
}) => {
  const isPlant = type === 'plant';
  
  return (
    <motion.g
      initial={animate ? { opacity: 0, scale: 0.8 } : false}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Cell wall (plant only) */}
      {isPlant && (
        <rect
          x={cx - size - 5}
          y={cy - size * 0.7 - 5}
          width={size * 2 + 10}
          height={size * 1.4 + 10}
          rx={8}
          fill="none"
          stroke="#84CC16"
          strokeWidth={4}
        />
      )}
      
      {/* Cell membrane */}
      <ellipse
        cx={cx}
        cy={cy}
        rx={size}
        ry={size * 0.7}
        fill={`${color}20`}
        stroke={color}
        strokeWidth={2}
      />
      
      {/* Nucleus */}
      {showNucleus && (
        <motion.g
          initial={animate ? { scale: 0 } : false}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2 }}
        >
          <circle
            cx={cx - size * 0.2}
            cy={cy}
            r={size * 0.3}
            fill={`${theme.secondary}30`}
            stroke={theme.secondary}
            strokeWidth={2}
          />
          <text
            x={cx - size * 0.2}
            y={cy + 4}
            textAnchor="middle"
            fontSize={10}
            fill={theme.secondary}
          >
            Nucleus
          </text>
        </motion.g>
      )}
      
      {/* Organelles */}
      {showOrganelles && (
        <>
          {/* Mitochondria */}
          <ellipse
            cx={cx + size * 0.4}
            cy={cy - size * 0.2}
            rx={12}
            ry={6}
            fill={`${theme.accent}50`}
            stroke={theme.accent}
            strokeWidth={1}
          />
          {/* ER */}
          <path
            d={`M ${cx + size * 0.5} ${cy + size * 0.2} Q ${cx + size * 0.6} ${cy + size * 0.3} ${cx + size * 0.5} ${cy + size * 0.4}`}
            fill="none"
            stroke={theme.primary}
            strokeWidth={2}
          />
          {/* Vacuole (large in plant) */}
          {isPlant && (
            <ellipse
              cx={cx + size * 0.2}
              cy={cy}
              rx={size * 0.4}
              ry={size * 0.3}
              fill="#06B6D420"
              stroke="#06B6D4"
              strokeWidth={1}
              strokeDasharray="4,2"
            />
          )}
        </>
      )}
    </motion.g>
  );
};

/**
 * DNA Helix - Double helix representation
 */
export const DNAHelix = ({
  x = 0,
  y = 0,
  width = 60,
  height = 120,
  basePairs = 6,
  color = theme.primary,
  animate = true,
}) => {
  const pairHeight = height / basePairs;
  
  return (
    <motion.g
      initial={animate ? { opacity: 0 } : false}
      animate={{ opacity: 1 }}
    >
      {Array.from({ length: basePairs }).map((_, i) => {
        const yPos = y + i * pairHeight + pairHeight / 2;
        const offset = Math.sin(i * 0.8) * 10;
        
        return (
          <motion.g
            key={i}
            initial={animate ? { opacity: 0, x: -10 } : false}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            {/* Left strand */}
            <circle cx={x + offset} cy={yPos} r={6} fill={theme.primary} />
            {/* Right strand */}
            <circle cx={x + width - offset} cy={yPos} r={6} fill={theme.secondary} />
            {/* Base pair connection */}
            <line
              x1={x + offset + 6}
              y1={yPos}
              x2={x + width - offset - 6}
              y2={yPos}
              stroke={i % 2 === 0 ? '#22C55E' : '#EAB308'}
              strokeWidth={3}
            />
            {/* Backbone connections */}
            {i < basePairs - 1 && (
              <>
                <line
                  x1={x + offset}
                  y1={yPos + 6}
                  x2={x + Math.sin((i + 1) * 0.8) * 10}
                  y2={yPos + pairHeight - 6}
                  stroke={theme.primary}
                  strokeWidth={2}
                />
                <line
                  x1={x + width - offset}
                  y1={yPos + 6}
                  x2={x + width - Math.sin((i + 1) * 0.8) * 10}
                  y2={yPos + pairHeight - 6}
                  stroke={theme.secondary}
                  strokeWidth={2}
                />
              </>
            )}
          </motion.g>
        );
      })}
    </motion.g>
  );
};

/**
 * Organ - Simplified organ shape
 */
export const Organ = ({
  cx = 50,
  cy = 50,
  type = 'heart', // heart, lung, kidney, brain, liver
  size = 60,
  color = theme.secondary,
  label = '',
  animate = true,
}) => {
  const renderOrgan = () => {
    switch (type) {
      case 'heart':
        return (
          <path
            d={`M ${cx} ${cy + size * 0.35} 
               C ${cx - size * 0.5} ${cy - size * 0.1} 
                 ${cx - size * 0.5} ${cy - size * 0.4} 
                 ${cx} ${cy - size * 0.2}
               C ${cx + size * 0.5} ${cy - size * 0.4} 
                 ${cx + size * 0.5} ${cy - size * 0.1} 
                 ${cx} ${cy + size * 0.35}`}
            fill={`${color}40`}
            stroke={color}
            strokeWidth={2}
          />
        );
      case 'brain':
        return (
          <g>
            <ellipse cx={cx} cy={cy} rx={size * 0.5} ry={size * 0.4} fill={`${color}40`} stroke={color} strokeWidth={2} />
            {/* Gyri pattern */}
            <path d={`M ${cx - size * 0.3} ${cy} Q ${cx} ${cy - size * 0.2} ${cx + size * 0.3} ${cy}`} fill="none" stroke={color} strokeWidth={1} />
            <path d={`M ${cx - size * 0.2} ${cy + size * 0.15} Q ${cx} ${cy} ${cx + size * 0.2} ${cy + size * 0.15}`} fill="none" stroke={color} strokeWidth={1} />
          </g>
        );
      case 'lung':
        return (
          <ellipse cx={cx} cy={cy} rx={size * 0.35} ry={size * 0.5} fill={`${color}40`} stroke={color} strokeWidth={2} />
        );
      default:
        return <ellipse cx={cx} cy={cy} rx={size * 0.4} ry={size * 0.3} fill={`${color}40`} stroke={color} strokeWidth={2} />;
    }
  };
  
  return (
    <motion.g
      initial={animate ? { opacity: 0, scale: 0.8 } : false}
      animate={{ opacity: 1, scale: 1 }}
    >
      {renderOrgan()}
      {label && (
        <text x={cx} y={cy + size * 0.6} textAnchor="middle" fontSize={12} fill={color}>
          {label}
        </text>
      )}
    </motion.g>
  );
};

/**
 * Membrane - Cell membrane / barrier
 */
export const Membrane = ({
  x = 0,
  y = 0,
  width = 200,
  thickness = 20,
  showPhospholipids = true,
  color = theme.primary,
  animate = true,
}) => (
  <motion.g
    initial={animate ? { opacity: 0 } : false}
    animate={{ opacity: 1 }}
  >
    {/* Membrane bilayer */}
    <rect x={x} y={y} width={width} height={thickness} fill={`${color}30`} rx={4} />
    
    {/* Phospholipid heads */}
    {showPhospholipids && Array.from({ length: Math.floor(width / 15) }).map((_, i) => (
      <g key={i}>
        <circle cx={x + 10 + i * 15} cy={y + 5} r={4} fill={theme.secondary} />
        <circle cx={x + 10 + i * 15} cy={y + thickness - 5} r={4} fill={theme.secondary} />
        <line x1={x + 10 + i * 15} y1={y + 5} x2={x + 10 + i * 15} y2={y + thickness / 2} stroke={color} strokeWidth={1} />
        <line x1={x + 10 + i * 15} y1={y + thickness - 5} x2={x + 10 + i * 15} y2={y + thickness / 2} stroke={color} strokeWidth={1} />
      </g>
    ))}
  </motion.g>
);

/**
 * Ecosystem Flow - Food chain / energy flow
 */
export const EcosystemLevel = ({
  x = 0,
  y = 0,
  width = 150,
  height = 40,
  label = '',
  level = 0, // 0 = producer, 1 = primary consumer, etc.
  color = theme.primary,
  animate = true,
}) => {
  const colors = ['#22C55E', '#84CC16', '#EAB308', '#F97316', '#EF4444'];
  const levelColor = colors[level % colors.length];
  
  return (
    <motion.g
      initial={animate ? { opacity: 0, x: -20 } : false}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: level * 0.15 }}
    >
      <rect
        x={x}
        y={y}
        width={width - level * 20}
        height={height}
        rx={6}
        fill={`${levelColor}30`}
        stroke={levelColor}
        strokeWidth={2}
      />
      <text
        x={x + (width - level * 20) / 2}
        y={y + height / 2 + 4}
        textAnchor="middle"
        fontSize={12}
        fontWeight={600}
        fill={levelColor}
      >
        {label}
      </text>
    </motion.g>
  );
};

// Registry
export const BIOLOGY_PRIMITIVES = {
  cell: Cell,
  dna: DNAHelix,
  organ: Organ,
  membrane: Membrane,
  ecosystem_level: EcosystemLevel,
};

export default BIOLOGY_PRIMITIVES;

