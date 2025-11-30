/**
 * 🔄 Cycle Template
 * =================
 * 
 * Circular process visualization for biology/chemistry cycles.
 * Krebs cycle, water cycle, nitrogen cycle, etc.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { COLORS, SUBJECT_THEMES } from '../primitives';

const CycleTemplate = ({
  config = {},
  step = 0,
  subject = 'biology',
}) => {
  const {
    steps = [
      { name: 'Step 1', emoji: '1️⃣', color: '#3B82F6', description: '' },
      { name: 'Step 2', emoji: '2️⃣', color: '#10B981', description: '' },
      { name: 'Step 3', emoji: '3️⃣', color: '#F59E0B', description: '' },
      { name: 'Step 4', emoji: '4️⃣', color: '#EF4444', description: '' },
    ],
    title = 'Cycle Process',
    subtitle = 'A continuous loop!',
    center_label = 'CYCLE',
    memory_hook = 'It goes round and round! 🔄',
  } = config;

  const theme = SUBJECT_THEMES[subject] || SUBJECT_THEMES.biology;
  const numSteps = steps.length;
  const RADIUS = 110;
  const CENTER_X = 250;
  const CENTER_Y = 200;
  const angleStep = (2 * Math.PI) / numSteps;
  const startAngle = -Math.PI / 2;

  const getPosition = (index) => {
    const angle = startAngle + index * angleStep;
    return {
      x: CENTER_X + Math.cos(angle) * RADIUS,
      y: CENTER_Y + Math.sin(angle) * RADIUS,
    };
  };

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
        🔄 {title}
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

      {/* Center circle */}
      <motion.circle
        cx={CENTER_X}
        cy={CENTER_Y}
        r={RADIUS * 0.35}
        fill="#F3F4F6"
        stroke={theme.primary}
        strokeWidth={3}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.5 }}
      />
      <text
        x={CENTER_X}
        y={CENTER_Y + 5}
        fontSize={14}
        fontWeight="bold"
        textAnchor="middle"
        fill={theme.primary}
      >
        {center_label}
      </text>

      {/* Connecting arrows */}
      {steps.map((_, i) => {
        const pos1 = getPosition(i);
        const pos2 = getPosition((i + 1) % numSteps);
        const midAngle = startAngle + (i + 0.5) * angleStep;
        const ctrl = {
          x: CENTER_X + Math.cos(midAngle) * RADIUS * 1.1,
          y: CENTER_Y + Math.sin(midAngle) * RADIUS * 1.1,
        };

        return (
          <motion.path
            key={`arrow-${i}`}
            d={`M ${pos1.x * 0.65 + CENTER_X * 0.35} ${pos1.y * 0.65 + CENTER_Y * 0.35} 
                Q ${ctrl.x * 0.6 + CENTER_X * 0.4} ${ctrl.y * 0.6 + CENTER_Y * 0.4} 
                ${pos2.x * 0.65 + CENTER_X * 0.35} ${pos2.y * 0.65 + CENTER_Y * 0.35}`}
            stroke="#9CA3AF"
            strokeWidth={3}
            fill="none"
            strokeLinecap="round"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={step >= 1 ? { pathLength: 1, opacity: 1 } : {}}
            transition={{ delay: 0.5 + i * 0.15, duration: 0.5 }}
          />
        );
      })}

      {/* Step nodes */}
      {steps.map((stepData, i) => {
        const pos = getPosition(i);
        const isActive = step >= 1;
        const isHighlighted = step === i + 1;
        const nodeSize = 35;

        return (
          <motion.g
            key={i}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: isActive ? 1 : 0.4 }}
            transition={{ delay: i * 0.1, type: 'spring' }}
          >
            {/* Node circle */}
            <motion.circle
              cx={pos.x}
              cy={pos.y}
              r={nodeSize}
              fill={stepData.color}
              stroke={isHighlighted ? '#1F2937' : 'white'}
              strokeWidth={isHighlighted ? 4 : 2}
              animate={isHighlighted ? { scale: [1, 1.1, 1] } : {}}
              transition={isHighlighted ? { repeat: Infinity, duration: 1 } : {}}
            />

            {/* Emoji */}
            <text x={pos.x} y={pos.y - 8} fontSize={20} textAnchor="middle">
              {stepData.emoji}
            </text>

            {/* Step name */}
            <text
              x={pos.x}
              y={pos.y + 14}
              fontSize={10}
              fontWeight="bold"
              textAnchor="middle"
              fill="white"
            >
              {stepData.name.length > 8 ? stepData.name.slice(0, 8) + '...' : stepData.name}
            </text>

            {/* External label */}
            {stepData.description && (
              <text
                x={pos.x + (pos.x > CENTER_X ? 50 : -50)}
                y={pos.y}
                fontSize={10}
                textAnchor={pos.x > CENTER_X ? 'start' : 'end'}
                fill="#636E72"
              >
                {stepData.description}
              </text>
            )}
          </motion.g>
        );
      })}

      {/* Animated rotation indicator */}
      {step >= 2 && (
        <motion.g
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 8, ease: 'linear' }}
          style={{ transformOrigin: `${CENTER_X}px ${CENTER_Y}px` }}
        >
          <circle cx={CENTER_X} cy={CENTER_Y - RADIUS - 15} r={6} fill={theme.primary} />
        </motion.g>
      )}

      {/* Memory Hook */}
      {step >= 4 && (
        <motion.g initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ type: 'spring' }}>
          <rect x={100} y={365} width={300} height={38} rx={19} fill="#ECFDF5" stroke={COLORS.green} strokeWidth={2} />
          <text x={250} y={390} fontSize={14} textAnchor="middle" fill={COLORS.green} fontWeight="bold">
            💡 {memory_hook}
          </text>
        </motion.g>
      )}
    </g>
  );
};

export default CycleTemplate;

