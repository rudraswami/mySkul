/**
 * 🧬 Structure Template
 * =====================
 * 
 * Anatomy/component visualization for cells, atoms, organs.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { COLORS, SUBJECT_THEMES } from '../primitives';

const StructureTemplate = ({
  config = {},
  step = 0,
  subject = 'biology',
}) => {
  const {
    type = 'cell', // cell, atom, organ, molecule
    components = [
      { name: 'Nucleus', x: 0, y: 0, size: 40, color: '#8B5CF6', emoji: '🟣', description: 'Control center' },
      { name: 'Mitochondria', x: -60, y: -40, size: 25, color: '#EF4444', emoji: '🔴', description: 'Powerhouse' },
      { name: 'Ribosome', x: 50, y: 50, size: 15, color: '#3B82F6', emoji: '🔵', description: 'Protein factory' },
    ],
    title = 'Cell Structure',
    subtitle = 'Know your parts!',
    highlight = null, // component name to highlight
    memory_hook = 'Each part has a job! 🏭',
  } = config;

  const theme = SUBJECT_THEMES[subject] || SUBJECT_THEMES.biology;
  const CENTER_X = 200;
  const CENTER_Y = 200;

  return (
    <g>
      {/* Title */}
      <motion.text
        x={250} y={30}
        fontSize={22}
        fontWeight="bold"
        textAnchor="middle"
        fill={COLORS.navy}
        fontFamily="'Caveat', cursive"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        🧬 {title}
      </motion.text>
      <motion.text
        x={250} y={52}
        fontSize={14}
        textAnchor="middle"
        fill={COLORS.chalkLight}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        {subtitle}
      </motion.text>

      {/* Main structure outline */}
      <motion.ellipse
        cx={CENTER_X}
        cy={CENTER_Y}
        rx={130}
        ry={100}
        fill="#FEF3C7"
        stroke={theme.primary}
        strokeWidth={4}
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
      />

      {/* Membrane label */}
      <text
        x={CENTER_X + 100}
        y={CENTER_Y - 85}
        fontSize={11}
        fill={theme.primary}
        fontWeight="bold"
      >
        Membrane →
      </text>

      {/* Components */}
      {components.map((comp, i) => {
        const isHighlighted = highlight === comp.name.toLowerCase() || (step === i + 1);
        const cx = CENTER_X + comp.x;
        const cy = CENTER_Y + comp.y;

        return (
          <motion.g
            key={i}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: step >= 1 ? 1 : 0.3 }}
            transition={{ delay: 0.3 + i * 0.15, type: 'spring' }}
          >
            {/* Highlight ring */}
            {isHighlighted && (
              <motion.circle
                cx={cx}
                cy={cy}
                r={comp.size + 8}
                fill="none"
                stroke={comp.color}
                strokeWidth={3}
                animate={{ opacity: [1, 0.3, 1], scale: [1, 1.1, 1] }}
                transition={{ repeat: Infinity, duration: 1 }}
              />
            )}

            {/* Component circle */}
            <circle
              cx={cx}
              cy={cy}
              r={comp.size}
              fill={comp.color}
              stroke={isHighlighted ? '#1F2937' : 'white'}
              strokeWidth={isHighlighted ? 3 : 2}
            />

            {/* Emoji */}
            <text
              x={cx}
              y={cy + 5}
              fontSize={comp.size * 0.6}
              textAnchor="middle"
            >
              {comp.emoji}
            </text>
          </motion.g>
        );
      })}

      {/* Legend */}
      <motion.g
        initial={{ x: 30, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <rect x={360} y={80} width={130} height={components.length * 45 + 30} rx={10} fill="white" stroke="#E5E7EB" strokeWidth={2} />
        <text x={425} y={105} fontSize={12} fontWeight="bold" textAnchor="middle" fill={COLORS.navy}>PARTS</text>
        
        {components.map((comp, i) => {
          const isActive = step === i + 1 || highlight === comp.name.toLowerCase();
          return (
            <g key={i} transform={`translate(370, ${120 + i * 45})`}>
              <circle cx={12} cy={12} r={10} fill={comp.color} />
              <text x={30} y={8} fontSize={11} fontWeight={isActive ? 'bold' : 'normal'} fill={isActive ? comp.color : '#374151'}>
                {comp.name}
              </text>
              <text x={30} y={22} fontSize={9} fill="#636E72">
                {comp.description}
              </text>
            </g>
          );
        })}
      </motion.g>

      {/* Memory Hook */}
      {step >= 4 && (
        <motion.g initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ type: 'spring' }}>
          <rect x={50} y={345} width={300} height={38} rx={19} fill="#ECFDF5" stroke={COLORS.green} strokeWidth={2} />
          <text x={200} y={370} fontSize={14} textAnchor="middle" fill={COLORS.green} fontWeight="bold">
            💡 {memory_hook}
          </text>
        </motion.g>
      )}
    </g>
  );
};

export default StructureTemplate;

