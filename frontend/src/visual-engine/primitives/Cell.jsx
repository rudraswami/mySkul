/**
 * 🧬 Cell Primitive
 * =================
 * 
 * Animated cell for biology visualizations.
 * Supports plant cell, animal cell, bacteria.
 */

import React from 'react';
import { motion } from 'framer-motion';

const Cell = ({
  x = 0,
  y = 0,
  type = 'animal', // animal, plant, bacteria
  size = 150,
  animated = true,
  showLabels = true,
  highlightOrganelle = null, // nucleus, mitochondria, chloroplast, etc.
}) => {
  const organelles = {
    animal: [
      { name: 'Nucleus', x: 0, y: 0, r: size * 0.2, color: '#8B5CF6', emoji: '🟣' },
      { name: 'Mitochondria', x: -size * 0.25, y: -size * 0.15, r: size * 0.08, color: '#EF4444', emoji: '🔴' },
      { name: 'Mitochondria', x: size * 0.2, y: size * 0.2, r: size * 0.08, color: '#EF4444', emoji: '🔴' },
      { name: 'ER', x: size * 0.15, y: -size * 0.2, r: size * 0.1, color: '#3B82F6', emoji: '🔵' },
      { name: 'Golgi', x: -size * 0.2, y: size * 0.15, r: size * 0.07, color: '#F59E0B', emoji: '🟡' },
    ],
    plant: [
      { name: 'Nucleus', x: 0, y: 0, r: size * 0.15, color: '#8B5CF6', emoji: '🟣' },
      { name: 'Chloroplast', x: -size * 0.25, y: -size * 0.15, r: size * 0.1, color: '#22C55E', emoji: '🟢' },
      { name: 'Chloroplast', x: size * 0.2, y: size * 0.2, r: size * 0.1, color: '#22C55E', emoji: '🟢' },
      { name: 'Chloroplast', x: -size * 0.15, y: size * 0.25, r: size * 0.1, color: '#22C55E', emoji: '🟢' },
      { name: 'Vacuole', x: size * 0.1, y: -size * 0.1, r: size * 0.18, color: '#06B6D4', emoji: '💧' },
    ],
    bacteria: [
      { name: 'Nucleoid', x: 0, y: 0, r: size * 0.25, color: '#8B5CF6', emoji: '🟣' },
      { name: 'Ribosome', x: -size * 0.2, y: -size * 0.1, r: size * 0.05, color: '#374151', emoji: '⚫' },
      { name: 'Ribosome', x: size * 0.15, y: size * 0.15, r: size * 0.05, color: '#374151', emoji: '⚫' },
    ],
  };

  const cellOrganelles = organelles[type] || organelles.animal;
  
  const cellShape = type === 'plant' 
    ? `M ${-size * 0.45} ${-size * 0.35} L ${size * 0.45} ${-size * 0.35} L ${size * 0.45} ${size * 0.35} L ${-size * 0.45} ${size * 0.35} Z`
    : type === 'bacteria'
    ? `M ${-size * 0.35} 0 Q ${-size * 0.35} ${-size * 0.2} ${-size * 0.15} ${-size * 0.25} L ${size * 0.15} ${-size * 0.25} Q ${size * 0.35} ${-size * 0.2} ${size * 0.35} 0 Q ${size * 0.35} ${size * 0.2} ${size * 0.15} ${size * 0.25} L ${-size * 0.15} ${size * 0.25} Q ${-size * 0.35} ${size * 0.2} ${-size * 0.35} 0`
    : null; // Animal cell uses ellipse

  return (
    <g transform={`translate(${x}, ${y})`}>
      {/* Cell wall (plant only) */}
      {type === 'plant' && (
        <motion.rect
          x={-size * 0.48}
          y={-size * 0.38}
          width={size * 0.96}
          height={size * 0.76}
          rx={5}
          fill="none"
          stroke="#22C55E"
          strokeWidth={4}
          initial={animated ? { pathLength: 0 } : undefined}
          animate={animated ? { pathLength: 1 } : undefined}
          transition={{ duration: 1 }}
        />
      )}

      {/* Cell membrane */}
      {cellShape ? (
        <motion.path
          d={cellShape}
          fill="#FEF3C7"
          stroke="#F59E0B"
          strokeWidth={3}
          initial={animated ? { scale: 0, opacity: 0 } : undefined}
          animate={animated ? { scale: 1, opacity: 1 } : undefined}
          transition={{ duration: 0.5 }}
        />
      ) : (
        <motion.ellipse
          cx={0}
          cy={0}
          rx={size * 0.45}
          ry={size * 0.35}
          fill="#FEF3C7"
          stroke="#F59E0B"
          strokeWidth={3}
          initial={animated ? { scale: 0, opacity: 0 } : undefined}
          animate={animated ? { scale: 1, opacity: 1 } : undefined}
          transition={{ duration: 0.5 }}
        />
      )}

      {/* Organelles */}
      {cellOrganelles.map((org, i) => {
        const isHighlighted = highlightOrganelle === org.name.toLowerCase();
        return (
          <motion.g
            key={i}
            initial={animated ? { scale: 0, opacity: 0 } : undefined}
            animate={animated ? { scale: 1, opacity: 1 } : undefined}
            transition={{ delay: 0.3 + i * 0.1 }}
          >
            <motion.circle
              cx={org.x}
              cy={org.y}
              r={org.r}
              fill={org.color}
              opacity={isHighlighted ? 1 : 0.8}
              animate={isHighlighted ? { scale: [1, 1.2, 1] } : undefined}
              transition={isHighlighted ? { repeat: Infinity, duration: 1 } : undefined}
            />
            
            {/* Highlight ring */}
            {isHighlighted && (
              <motion.circle
                cx={org.x}
                cy={org.y}
                r={org.r + 5}
                fill="none"
                stroke={org.color}
                strokeWidth={2}
                animate={{ opacity: [1, 0.3, 1] }}
                transition={{ repeat: Infinity, duration: 1 }}
              />
            )}
          </motion.g>
        );
      })}

      {/* Labels */}
      {showLabels && (
        <g transform={`translate(${size * 0.55}, ${-size * 0.3})`}>
          {[...new Set(cellOrganelles.map(o => o.name))].map((name, i) => {
            const org = cellOrganelles.find(o => o.name === name);
            return (
              <g key={name} transform={`translate(0, ${i * 18})`}>
                <circle cx={0} cy={0} r={6} fill={org.color} />
                <text x={12} y={4} fontSize={10} fill="#374151">
                  {name}
                </text>
              </g>
            );
          })}
        </g>
      )}

      {/* Cell type label */}
      <text
        x={0}
        y={size * 0.5}
        fontSize={14}
        fontWeight="bold"
        textAnchor="middle"
        fill="#374151"
        textTransform="capitalize"
      >
        {type.charAt(0).toUpperCase() + type.slice(1)} Cell
      </text>
    </g>
  );
};

export default Cell;

