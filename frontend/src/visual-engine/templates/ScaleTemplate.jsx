/**
 * 📏 Scale Template
 * =================
 * 
 * Spectrum/range visualization.
 * pH scale, EM spectrum, temperature scale, etc.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { COLORS, SUBJECT_THEMES } from '../primitives';

const ScaleTemplate = ({
  config = {},
  step = 0,
  subject = 'chemistry',
}) => {
  const {
    min = 0,
    max = 14,
    current_value = 7,
    markers = [
      { value: 0, label: 'Acidic', emoji: '🍋', color: '#EF4444' },
      { value: 7, label: 'Neutral', emoji: '💧', color: '#10B981' },
      { value: 14, label: 'Basic', emoji: '🧼', color: '#3B82F6' },
    ],
    unit = '',
    title = 'pH Scale',
    subtitle = 'Where does it fall?',
    gradient_colors = ['#EF4444', '#F59E0B', '#FCD34D', '#10B981', '#3B82F6', '#8B5CF6'],
    memory_hook = 'Lower = Acidic, Higher = Basic! 📏',
  } = config;

  const theme = SUBJECT_THEMES[subject] || SUBJECT_THEMES.chemistry;
  
  const SCALE_X = 60;
  const SCALE_WIDTH = 380;
  const SCALE_Y = 200;
  const SCALE_HEIGHT = 50;

  const valueToX = (val) => SCALE_X + ((val - min) / (max - min)) * SCALE_WIDTH;
  const currentX = valueToX(current_value);

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
        📏 {title}
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

      {/* Gradient scale bar */}
      <defs>
        <linearGradient id="scaleGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          {gradient_colors.map((color, i) => (
            <stop
              key={i}
              offset={`${(i / (gradient_colors.length - 1)) * 100}%`}
              stopColor={color}
            />
          ))}
        </linearGradient>
      </defs>

      <motion.rect
        x={SCALE_X}
        y={SCALE_Y}
        width={SCALE_WIDTH}
        height={SCALE_HEIGHT}
        rx={10}
        fill="url(#scaleGradient)"
        stroke="#374151"
        strokeWidth={2}
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        style={{ originX: 0 }}
        transition={{ duration: 0.8 }}
      />

      {/* Scale numbers */}
      <motion.g
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        {Array.from({ length: max - min + 1 }).map((_, i) => {
          const val = min + i;
          const x = valueToX(val);
          const isMain = val % Math.ceil((max - min) / 7) === 0 || val === min || val === max;
          
          return (
            <g key={val}>
              <line
                x1={x}
                y1={SCALE_Y + SCALE_HEIGHT}
                x2={x}
                y2={SCALE_Y + SCALE_HEIGHT + (isMain ? 15 : 8)}
                stroke="#374151"
                strokeWidth={isMain ? 2 : 1}
              />
              {isMain && (
                <text
                  x={x}
                  y={SCALE_Y + SCALE_HEIGHT + 28}
                  fontSize={12}
                  textAnchor="middle"
                  fill="#374151"
                  fontWeight="bold"
                >
                  {val}{unit}
                </text>
              )}
            </g>
          );
        })}
      </motion.g>

      {/* Marker labels */}
      {step >= 1 && markers.map((marker, i) => {
        const x = valueToX(marker.value);
        
        return (
          <motion.g
            key={i}
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.6 + i * 0.2, type: 'spring' }}
          >
            <rect
              x={x - 40}
              y={SCALE_Y - 60}
              width={80}
              height={45}
              rx={10}
              fill="white"
              stroke={marker.color}
              strokeWidth={2}
            />
            <text x={x} y={SCALE_Y - 40} fontSize={18} textAnchor="middle">{marker.emoji}</text>
            <text x={x} y={SCALE_Y - 22} fontSize={11} textAnchor="middle" fill={marker.color} fontWeight="bold">
              {marker.label}
            </text>
            
            {/* Connector line */}
            <line
              x1={x}
              y1={SCALE_Y - 15}
              x2={x}
              y2={SCALE_Y}
              stroke={marker.color}
              strokeWidth={2}
              strokeDasharray="4 2"
            />
          </motion.g>
        );
      })}

      {/* Current value indicator */}
      {step >= 2 && (
        <motion.g
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1, type: 'spring' }}
        >
          {/* Pointer */}
          <polygon
            points={`${currentX},${SCALE_Y + SCALE_HEIGHT + 50} ${currentX - 12},${SCALE_Y + SCALE_HEIGHT + 70} ${currentX + 12},${SCALE_Y + SCALE_HEIGHT + 70}`}
            fill={theme.primary}
          />
          
          {/* Value box */}
          <rect
            x={currentX - 45}
            y={SCALE_Y + SCALE_HEIGHT + 70}
            width={90}
            height={40}
            rx={10}
            fill={theme.primary}
          />
          <text
            x={currentX}
            y={SCALE_Y + SCALE_HEIGHT + 88}
            fontSize={10}
            textAnchor="middle"
            fill="white"
          >
            Current Value
          </text>
          <text
            x={currentX}
            y={SCALE_Y + SCALE_HEIGHT + 105}
            fontSize={16}
            fontWeight="bold"
            textAnchor="middle"
            fill="white"
          >
            {current_value}{unit}
          </text>
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

export default ScaleTemplate;

