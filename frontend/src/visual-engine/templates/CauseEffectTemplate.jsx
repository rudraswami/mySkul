/**
 * ⚡ Cause-Effect Template
 * ========================
 * 
 * Before/after comparison visualization.
 * Great for reactions, changes, transformations.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { COLORS, SUBJECT_THEMES } from '../primitives';

const CauseEffectTemplate = ({
  config = {},
  step = 0,
  subject = 'physics',
}) => {
  const {
    cause = { title: 'Before', items: [{ emoji: '⚪', label: 'State A' }], color: '#3B82F6' },
    effect = { title: 'After', items: [{ emoji: '⚫', label: 'State B' }], color: '#10B981' },
    action = { emoji: '⚡', label: 'Change', color: '#F59E0B' },
    title = 'Cause & Effect',
    subtitle = 'See what changed!',
    comparison = '', // "2x faster", "50% less", etc.
    memory_hook = 'Action creates reaction! ⚡',
  } = config;

  const theme = SUBJECT_THEMES[subject] || SUBJECT_THEMES.physics;
  const BEFORE_X = 100;
  const AFTER_X = 400;
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
        ⚡ {title}
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

      {/* BEFORE Section */}
      <motion.g
        initial={{ x: -30, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <rect x={BEFORE_X - 70} y={CENTER_Y - 100} width={140} height={200} rx={15} fill="#FEF2F2" stroke={cause.color} strokeWidth={3} />
        
        {/* Header */}
        <rect x={BEFORE_X - 70} y={CENTER_Y - 100} width={140} height={35} rx={15} fill={cause.color} />
        <text x={BEFORE_X} y={CENTER_Y - 76} fontSize={14} fontWeight="bold" textAnchor="middle" fill="white">
          {cause.title}
        </text>

        {/* Items */}
        {cause.items.map((item, i) => (
          <motion.g
            key={i}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.4 + i * 0.1, type: 'spring' }}
          >
            <circle cx={BEFORE_X} cy={CENTER_Y - 30 + i * 60} r={30} fill="white" stroke={cause.color} strokeWidth={2} />
            <text x={BEFORE_X} y={CENTER_Y - 25 + i * 60} fontSize={24} textAnchor="middle">{item.emoji}</text>
            <text x={BEFORE_X} y={CENTER_Y + 5 + i * 60} fontSize={11} textAnchor="middle" fill={cause.color} fontWeight="bold">
              {item.label}
            </text>
          </motion.g>
        ))}
      </motion.g>

      {/* ACTION Arrow (Center) */}
      {step >= 2 && (
        <motion.g
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.6, type: 'spring' }}
        >
          {/* Arrow line */}
          <motion.line
            x1={BEFORE_X + 80}
            y1={CENTER_Y}
            x2={AFTER_X - 80}
            y2={CENTER_Y}
            stroke={action.color}
            strokeWidth={6}
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.5 }}
          />
          <polygon
            points={`${AFTER_X - 75},${CENTER_Y} ${AFTER_X - 95},${CENTER_Y - 12} ${AFTER_X - 95},${CENTER_Y + 12}`}
            fill={action.color}
          />

          {/* Action label */}
          <circle cx={250} cy={CENTER_Y - 50} r={35} fill={action.color} stroke="white" strokeWidth={3} />
          <text x={250} y={CENTER_Y - 45} fontSize={28} textAnchor="middle">{action.emoji}</text>
          <text x={250} y={CENTER_Y - 15} fontSize={12} textAnchor="middle" fill="white" fontWeight="bold">
            {action.label}
          </text>

          {/* Comparison badge */}
          {comparison && (
            <motion.g
              initial={{ y: -10, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.8 }}
            >
              <rect x={200} y={CENTER_Y + 25} width={100} height={25} rx={12} fill="#FEF3C7" stroke={action.color} strokeWidth={2} />
              <text x={250} y={CENTER_Y + 42} fontSize={11} textAnchor="middle" fill={action.color} fontWeight="bold">
                {comparison}
              </text>
            </motion.g>
          )}
        </motion.g>
      )}

      {/* AFTER Section */}
      <motion.g
        initial={{ x: 30, opacity: 0 }}
        animate={{ x: 0, opacity: step >= 3 ? 1 : 0.3 }}
        transition={{ delay: 0.4 }}
      >
        <rect x={AFTER_X - 70} y={CENTER_Y - 100} width={140} height={200} rx={15} fill="#ECFDF5" stroke={effect.color} strokeWidth={3} />
        
        {/* Header */}
        <rect x={AFTER_X - 70} y={CENTER_Y - 100} width={140} height={35} rx={15} fill={effect.color} />
        <text x={AFTER_X} y={CENTER_Y - 76} fontSize={14} fontWeight="bold" textAnchor="middle" fill="white">
          {effect.title}
        </text>

        {/* Items */}
        {effect.items.map((item, i) => (
          <motion.g
            key={i}
            initial={{ scale: 0 }}
            animate={{ scale: step >= 3 ? 1 : 0.5 }}
            transition={{ delay: 0.9 + i * 0.1, type: 'spring' }}
          >
            <motion.circle
              cx={AFTER_X}
              cy={CENTER_Y - 30 + i * 60}
              r={30}
              fill="white"
              stroke={effect.color}
              strokeWidth={2}
              animate={step >= 3 ? { scale: [1, 1.1, 1] } : {}}
              transition={{ delay: 1, duration: 0.5 }}
            />
            <text x={AFTER_X} y={CENTER_Y - 25 + i * 60} fontSize={24} textAnchor="middle">{item.emoji}</text>
            <text x={AFTER_X} y={CENTER_Y + 5 + i * 60} fontSize={11} textAnchor="middle" fill={effect.color} fontWeight="bold">
              {item.label}
            </text>
          </motion.g>
        ))}
      </motion.g>

      {/* Memory Hook */}
      {step >= 4 && (
        <motion.g initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ type: 'spring' }}>
          <rect x={100} y={345} width={300} height={38} rx={19} fill="#ECFDF5" stroke={COLORS.green} strokeWidth={2} />
          <text x={250} y={370} fontSize={14} textAnchor="middle" fill={COLORS.green} fontWeight="bold">
            💡 {memory_hook}
          </text>
        </motion.g>
      )}
    </g>
  );
};

export default CauseEffectTemplate;

