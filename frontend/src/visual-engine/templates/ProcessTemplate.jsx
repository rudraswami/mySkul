/**
 * 🔄 Process Template
 * ===================
 * 
 * Flow-based visualization for transformations, reactions, digestion.
 * Shows input → process → output with animated flow.
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { COLORS, SUBJECT_THEMES } from '../primitives';

const ProcessTemplate = ({
  config = {},
  step = 0,
  subject = 'biology',
}) => {
  const {
    inputs = [{ name: 'Input A', emoji: '📥', color: '#3B82F6' }],
    process = { name: 'Process', emoji: '⚡', color: '#8B5CF6' },
    outputs = [{ name: 'Output', emoji: '📤', color: '#10B981' }],
    title = 'Process Flow',
    subtitle = 'Watch the transformation!',
    formula = '',
    memory_hook = 'Input transforms to output!',
  } = config;

  const theme = SUBJECT_THEMES[subject] || SUBJECT_THEMES.biology;
  const [flowActive, setFlowActive] = useState(false);
  const [processActive, setProcessActive] = useState(false);
  const [outputActive, setOutputActive] = useState(false);

  useEffect(() => {
    if (step >= 1) setFlowActive(true);
    if (step >= 2) setProcessActive(true);
    if (step >= 3) setOutputActive(true);
  }, [step]);

  const INPUT_X = 80;
  const PROCESS_X = 250;
  const OUTPUT_X = 420;
  const CENTER_Y = 180;

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

      {/* INPUT SECTION */}
      <motion.g
        initial={{ x: -30, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <rect x={INPUT_X - 55} y={CENTER_Y - 80} width={110} height={160} rx={12} fill="#E0F2FE" stroke={COLORS.blue} strokeWidth={2} />
        <rect x={INPUT_X - 55} y={CENTER_Y - 80} width={110} height={30} rx={12} fill={COLORS.blue} />
        <text x={INPUT_X} y={CENTER_Y - 58} fontSize={12} textAnchor="middle" fill="white" fontWeight="bold">📥 INPUTS</text>
        
        {inputs.map((input, i) => (
          <motion.g
            key={i}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.3 + i * 0.1, type: 'spring' }}
          >
            <rect
              x={INPUT_X - 45}
              y={CENTER_Y - 35 + i * 50}
              width={90}
              height={40}
              rx={8}
              fill="white"
              stroke={input.color}
              strokeWidth={2}
            />
            <text x={INPUT_X} y={CENTER_Y - 15 + i * 50} fontSize={18} textAnchor="middle">{input.emoji}</text>
            <text x={INPUT_X} y={CENTER_Y + 5 + i * 50} fontSize={10} textAnchor="middle" fill={input.color} fontWeight="bold">
              {input.name}
            </text>
          </motion.g>
        ))}
      </motion.g>

      {/* Input → Process Arrow */}
      {flowActive && (
        <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <motion.line
            x1={INPUT_X + 60} y1={CENTER_Y}
            x2={PROCESS_X - 60} y2={CENTER_Y}
            stroke={theme.primary}
            strokeWidth={4}
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.5 }}
          />
          <polygon points={`${PROCESS_X - 55},${CENTER_Y} ${PROCESS_X - 70},${CENTER_Y - 8} ${PROCESS_X - 70},${CENTER_Y + 8}`} fill={theme.primary} />
          
          {/* Animated particles */}
          {[0, 1, 2].map((i) => (
            <motion.circle
              key={i}
              r={5}
              fill={theme.primary}
              initial={{ x: INPUT_X + 60, y: CENTER_Y, opacity: 0 }}
              animate={{
                x: [INPUT_X + 60, PROCESS_X - 60],
                y: [CENTER_Y, CENTER_Y],
                opacity: [0, 1, 1, 0],
              }}
              transition={{
                delay: 0.5 + i * 0.4,
                duration: 1,
                repeat: Infinity,
                repeatDelay: 0.6,
              }}
            />
          ))}
        </motion.g>
      )}

      {/* PROCESS SECTION */}
      <motion.g
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: processActive ? 1 : 0.8, opacity: processActive ? 1 : 0.5 }}
        transition={{ delay: 0.4, type: 'spring' }}
      >
        <rect x={PROCESS_X - 55} y={CENTER_Y - 55} width={110} height={110} rx={55} fill={process.color} stroke="#1F2937" strokeWidth={3} />
        <motion.g
          animate={processActive ? { rotate: 360 } : {}}
          transition={{ repeat: Infinity, duration: 3, ease: 'linear' }}
        >
          <text x={PROCESS_X} y={CENTER_Y - 10} fontSize={32} textAnchor="middle">{process.emoji}</text>
        </motion.g>
        <text x={PROCESS_X} y={CENTER_Y + 25} fontSize={12} textAnchor="middle" fill="white" fontWeight="bold">
          {process.name}
        </text>
      </motion.g>

      {/* Process → Output Arrow */}
      {processActive && (
        <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <motion.line
            x1={PROCESS_X + 60} y1={CENTER_Y}
            x2={OUTPUT_X - 60} y2={CENTER_Y}
            stroke={COLORS.green}
            strokeWidth={4}
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.5 }}
          />
          <polygon points={`${OUTPUT_X - 55},${CENTER_Y} ${OUTPUT_X - 70},${CENTER_Y - 8} ${OUTPUT_X - 70},${CENTER_Y + 8}`} fill={COLORS.green} />
          
          {[0, 1, 2].map((i) => (
            <motion.circle
              key={i}
              r={5}
              fill={COLORS.green}
              initial={{ x: PROCESS_X + 60, y: CENTER_Y, opacity: 0 }}
              animate={{
                x: [PROCESS_X + 60, OUTPUT_X - 60],
                y: [CENTER_Y, CENTER_Y],
                opacity: [0, 1, 1, 0],
              }}
              transition={{
                delay: 0.8 + i * 0.4,
                duration: 1,
                repeat: Infinity,
                repeatDelay: 0.6,
              }}
            />
          ))}
        </motion.g>
      )}

      {/* OUTPUT SECTION */}
      <motion.g
        initial={{ x: 30, opacity: 0 }}
        animate={{ x: 0, opacity: outputActive ? 1 : 0.3 }}
        transition={{ delay: 0.6 }}
      >
        <rect x={OUTPUT_X - 55} y={CENTER_Y - 80} width={110} height={160} rx={12} fill="#ECFDF5" stroke={COLORS.green} strokeWidth={2} />
        <rect x={OUTPUT_X - 55} y={CENTER_Y - 80} width={110} height={30} rx={12} fill={COLORS.green} />
        <text x={OUTPUT_X} y={CENTER_Y - 58} fontSize={12} textAnchor="middle" fill="white" fontWeight="bold">📤 OUTPUTS</text>
        
        {outputs.map((output, i) => (
          <motion.g
            key={i}
            initial={{ scale: 0 }}
            animate={{ scale: outputActive ? 1 : 0 }}
            transition={{ delay: 0.8 + i * 0.1, type: 'spring' }}
          >
            <rect
              x={OUTPUT_X - 45}
              y={CENTER_Y - 35 + i * 50}
              width={90}
              height={40}
              rx={8}
              fill="white"
              stroke={output.color}
              strokeWidth={2}
            />
            <text x={OUTPUT_X} y={CENTER_Y - 15 + i * 50} fontSize={18} textAnchor="middle">{output.emoji}</text>
            <text x={OUTPUT_X} y={CENTER_Y + 5 + i * 50} fontSize={10} textAnchor="middle" fill={output.color} fontWeight="bold">
              {output.name}
            </text>
          </motion.g>
        ))}
      </motion.g>

      {/* Formula */}
      {step >= 3 && formula && (
        <motion.g initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}>
          <rect x={100} y={290} width={300} height={40} rx={10} fill="#FEF3C7" stroke={theme.primary} strokeWidth={2} />
          <text x={250} y={316} fontSize={14} fontWeight="bold" textAnchor="middle" fill={theme.primary} fontFamily="'Caveat', cursive">
            {formula}
          </text>
        </motion.g>
      )}

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

export default ProcessTemplate;

