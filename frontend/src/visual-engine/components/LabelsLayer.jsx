/**
 * LabelsLayer - Text, Formulas, and Annotations
 * Supports Hinglish (Hindi + English) labels
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const LabelsLayer = ({
  labels,
  props,
  actors,
  language = 'hinglish',
  activeLabel,
  width,
  height,
}) => {
  // Get position for a label based on its target
  const getLabelPosition = (label) => {
    if (label.position?.x && label.position?.y) {
      return {
        x: label.position.x * width,
        y: label.position.y * height,
      };
    }

    // Find target position
    const target = [...props, ...actors].find(
      item => item.id === label.target
    );

    if (!target) {
      return { x: width / 2, y: height / 2 };
    }

    const targetX = (target.animatedPosition?.x || target.position?.x || 0.5) * width;
    const targetY = (target.animatedPosition?.y || target.position?.y || 0.5) * height;

    // Offset based on position preference
    const offsets = {
      above: { x: 0, y: -50 },
      below: { x: 0, y: 50 },
      left: { x: -80, y: 0 },
      right: { x: 80, y: 0 },
    };

    const offset = offsets[label.position] || offsets['above'];

    return {
      x: targetX + offset.x,
      y: targetY + offset.y,
    };
  };

  return (
    <g id="labels-layer">
      <AnimatePresence>
        {labels.map((label, index) => {
          const pos = getLabelPosition(label);
          const isActive = activeLabel === label.target || label.showOn === 'always';
          const text = language === 'hinglish' && label.textHi ? label.textHi : label.text;

          // Skip if not visible
          if (label.showOn?.startsWith('step:') && !isActive) {
            return null;
          }

          return (
            <Label
              key={label.id || index}
              {...label}
              x={pos.x}
              y={pos.y}
              text={text}
              secondaryText={language === 'hinglish' ? label.text : label.textHi}
              isActive={isActive}
            />
          );
        })}
      </AnimatePresence>
    </g>
  );
};

const Label = ({
  id,
  x,
  y,
  text,
  secondaryText,
  style = 'default',
  isActive,
  animation = 'fadeIn',
}) => {
  const styles = {
    default: {
      bg: '#FFFFFF',
      border: '#E0E0E0',
      text: '#333333',
      fontSize: 12,
    },
    highlight: {
      bg: '#FF9800',
      border: '#E65100',
      text: '#FFFFFF',
      fontSize: 14,
      fontWeight: 'bold',
    },
    formula: {
      bg: '#FFF8E1',
      border: '#FFC107',
      text: '#5D4037',
      fontSize: 16,
      fontWeight: 'bold',
      fontFamily: 'monospace',
    },
    velocity: {
      bg: '#E8F5E9',
      border: '#4CAF50',
      text: '#2E7D32',
      fontSize: 13,
    },
    insight: {
      bg: '#E3F2FD',
      border: '#2196F3',
      text: '#1565C0',
      fontSize: 12,
    },
    speech: {
      bg: '#FFFFFF',
      border: '#9E9E9E',
      text: '#333333',
      fontSize: 11,
      isSpeech: true,
    },
  };

  const currentStyle = styles[style] || styles['default'];

  const animations = {
    fadeIn: {
      initial: { opacity: 0, y: 10 },
      animate: { opacity: 1, y: 0 },
      exit: { opacity: 0, y: -10 },
    },
    scaleIn: {
      initial: { opacity: 0, scale: 0.8 },
      animate: { opacity: 1, scale: 1 },
      exit: { opacity: 0, scale: 0.8 },
    },
    slideIn: {
      initial: { opacity: 0, x: -20 },
      animate: { opacity: 1, x: 0 },
      exit: { opacity: 0, x: 20 },
    },
  };

  const currentAnimation = animations[animation] || animations['fadeIn'];

  // Estimate text width
  const textWidth = Math.max(text.length * 7, secondaryText ? secondaryText.length * 6 : 0, 60);
  const padding = 12;
  const boxWidth = textWidth + padding * 2;
  const boxHeight = secondaryText ? 45 : 30;

  return (
    <motion.g
      id={`label-${id}`}
      {...currentAnimation}
      transition={{ duration: 0.3 }}
    >
      {/* Speech bubble pointer */}
      {currentStyle.isSpeech && (
        <polygon
          points={`${x - 8},${y + boxHeight / 2} ${x - 20},${y + boxHeight / 2 + 15} ${x + 8},${y + boxHeight / 2}`}
          fill={currentStyle.bg}
          stroke={currentStyle.border}
          strokeWidth="1.5"
        />
      )}

      {/* Background */}
      <rect
        x={x - boxWidth / 2}
        y={y - boxHeight / 2}
        width={boxWidth}
        height={boxHeight}
        rx="6"
        fill={currentStyle.bg}
        stroke={currentStyle.border}
        strokeWidth="2"
        filter="url(#shadow)"
      />

      {/* Main text */}
      <text
        x={x}
        y={secondaryText ? y - 5 : y + 4}
        textAnchor="middle"
        fontSize={currentStyle.fontSize}
        fontWeight={currentStyle.fontWeight || 'normal'}
        fontFamily={currentStyle.fontFamily || 'system-ui, sans-serif'}
        fill={currentStyle.text}
      >
        {text}
      </text>

      {/* Secondary text (Hindi/English) */}
      {secondaryText && (
        <text
          x={x}
          y={y + 12}
          textAnchor="middle"
          fontSize={currentStyle.fontSize - 2}
          fill={currentStyle.text}
          opacity="0.7"
        >
          {secondaryText}
        </text>
      )}

      {/* Pulsing indicator for active labels */}
      {isActive && style === 'highlight' && (
        <motion.circle
          cx={x + boxWidth / 2 - 5}
          cy={y - boxHeight / 2 + 5}
          r="4"
          fill="#FF5722"
          animate={{ scale: [1, 1.5, 1], opacity: [1, 0.5, 1] }}
          transition={{ repeat: Infinity, duration: 1 }}
        />
      )}
    </motion.g>
  );
};

/**
 * Formula Display Component
 * Special rendering for mathematical formulas
 */
export const FormulaDisplay = ({ formula, x, y }) => {
  return (
    <g transform={`translate(${x}, ${y})`}>
      <rect
        x="-80"
        y="-30"
        width="160"
        height="60"
        rx="8"
        fill="#FFFDE7"
        stroke="#FFC107"
        strokeWidth="2"
        filter="url(#shadow)"
      />
      
      <text
        x="0"
        y="0"
        textAnchor="middle"
        fontSize="24"
        fontWeight="bold"
        fontFamily="'Times New Roman', serif"
        fill="#5D4037"
      >
        {formula.main}
      </text>
      
      <text
        x="0"
        y="20"
        textAnchor="middle"
        fontSize="10"
        fill="#8D6E63"
      >
        {formula.meaning}
      </text>
    </g>
  );
};

export default LabelsLayer;


