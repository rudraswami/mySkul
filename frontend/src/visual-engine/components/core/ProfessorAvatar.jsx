/**
 * ProfessorAvatar.jsx
 * Phase 2.1: Interactive professor with gestures & reactions
 * 
 * Features:
 * - Multiple gesture states (point, explain, celebrate, think, wave)
 * - Reactions to value changes
 * - Speech bubbles with Hinglish tips
 * - Eye tracking (follows objects)
 * - Emotional expressions
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Professor gesture states
const GESTURES = {
  idle: 'idle',
  point: 'point',
  explain: 'explain',
  celebrate: 'celebrate',
  think: 'think',
  wave: 'wave',
  surprise: 'surprise',
  encourage: 'encourage',
};

// Professor expressions
const EXPRESSIONS = {
  neutral: 'neutral',
  happy: 'happy',
  excited: 'excited',
  thinking: 'thinking',
  surprised: 'surprised',
  proud: 'proud',
};

const ProfessorAvatar = ({
  gesture = GESTURES.idle,
  expression = EXPRESSIONS.neutral,
  speech = null,
  speechType = 'tip', // 'tip' | 'reaction' | 'explanation' | 'encouragement'
  lookAt = null, // { x, y } coordinates to look at
  size = 'medium', // 'small' | 'medium' | 'large'
  position = { x: 60, y: 75 },
  onSpeechComplete,
  showSpeech = true,
  animated = true,
}) => {
  const [currentGesture, setCurrentGesture] = useState(gesture);
  const [currentExpression, setCurrentExpression] = useState(expression);
  const [eyeOffset, setEyeOffset] = useState({ x: 0, y: 0 });
  const [isBlinking, setIsBlinking] = useState(false);
  const [showSpeechBubble, setShowSpeechBubble] = useState(false);

  // Size configurations
  const sizeConfig = useMemo(() => ({
    small: { scale: 0.6, speechOffset: { x: 40, y: -60 } },
    medium: { scale: 1, speechOffset: { x: 60, y: -80 } },
    large: { scale: 1.4, speechOffset: { x: 80, y: -100 } },
  }), []);

  const config = sizeConfig[size] || sizeConfig.medium;

  // Eye tracking
  useEffect(() => {
    if (lookAt) {
      const dx = lookAt.x - position.x;
      const dy = lookAt.y - position.y;
      const maxOffset = 3;
      
      setEyeOffset({
        x: Math.max(-maxOffset, Math.min(maxOffset, dx / 50)),
        y: Math.max(-maxOffset, Math.min(maxOffset, dy / 50)),
      });
    } else {
      setEyeOffset({ x: 0, y: 0 });
    }
  }, [lookAt, position]);

  // Blinking animation
  useEffect(() => {
    if (!animated) return;
    
    const blinkInterval = setInterval(() => {
      setIsBlinking(true);
      setTimeout(() => setIsBlinking(false), 150);
    }, 3000 + Math.random() * 2000);
    
    return () => clearInterval(blinkInterval);
  }, [animated]);

  // Update gesture and expression
  useEffect(() => {
    setCurrentGesture(gesture);
  }, [gesture]);

  useEffect(() => {
    setCurrentExpression(expression);
  }, [expression]);

  // Speech bubble handling
  useEffect(() => {
    if (speech) {
      setShowSpeechBubble(true);
      const timer = setTimeout(() => {
        setShowSpeechBubble(false);
        onSpeechComplete?.();
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [speech, onSpeechComplete]);

  // Get arm position based on gesture
  const getArmAnimation = useCallback(() => {
    switch (currentGesture) {
      case GESTURES.point:
        return { leftArm: -70, rightArm: 30 };
      case GESTURES.explain:
        return { leftArm: -45, rightArm: 45 };
      case GESTURES.celebrate:
        return { leftArm: -120, rightArm: -120 };
      case GESTURES.think:
        return { leftArm: -30, rightArm: 60 };
      case GESTURES.wave:
        return { leftArm: -50, rightArm: -100 };
      case GESTURES.surprise:
        return { leftArm: -90, rightArm: -90 };
      case GESTURES.encourage:
        return { leftArm: -60, rightArm: -60 };
      default:
        return { leftArm: -50, rightArm: 30 };
    }
  }, [currentGesture]);

  // Get expression elements
  const getExpressionElements = useCallback(() => {
    const baseEyes = { eyeScale: 1, eyebrowY: 0, mouthPath: 'M -5 11 Q 0 16 5 11' };
    
    switch (currentExpression) {
      case EXPRESSIONS.happy:
        return { ...baseEyes, mouthPath: 'M -6 10 Q 0 18 6 10', eyeScale: 0.9 };
      case EXPRESSIONS.excited:
        return { ...baseEyes, mouthPath: 'M -7 9 Q 0 20 7 9', eyeScale: 1.2, eyebrowY: -3 };
      case EXPRESSIONS.thinking:
        return { ...baseEyes, mouthPath: 'M -3 12 Q 0 12 3 14', eyebrowY: 2 };
      case EXPRESSIONS.surprised:
        return { ...baseEyes, mouthPath: 'M -4 12 Q 0 18 4 12', eyeScale: 1.3, eyebrowY: -4 };
      case EXPRESSIONS.proud:
        return { ...baseEyes, mouthPath: 'M -6 10 Q 0 17 6 10', eyebrowY: -2 };
      default:
        return baseEyes;
    }
  }, [currentExpression]);

  const armAnim = getArmAnimation();
  const expressionElements = getExpressionElements();

  // Speech bubble styles
  const getSpeechBubbleStyle = () => {
    const styles = {
      tip: { bg: '#FEF3C7', border: '#F59E0B', text: '#92400E', icon: '💡' },
      reaction: { bg: '#DBEAFE', border: '#3B82F6', text: '#1E40AF', icon: '😮' },
      explanation: { bg: '#F3E8FF', border: '#8B5CF6', text: '#5B21B6', icon: '📚' },
      encouragement: { bg: '#D1FAE5', border: '#10B981', text: '#065F46', icon: '💪' },
    };
    return styles[speechType] || styles.tip;
  };

  const speechStyle = getSpeechBubbleStyle();

  return (
    <g transform={`translate(${position.x}, ${position.y}) scale(${config.scale})`}>
      {/* Shadow */}
      <ellipse cx="0" cy="52" rx="18" ry="5" fill="rgba(0,0,0,0.15)" />
      
      {/* Body */}
      <motion.g
        animate={currentGesture === GESTURES.celebrate ? { y: [0, -5, 0] } : {}}
        transition={{ duration: 0.3, repeat: currentGesture === GESTURES.celebrate ? Infinity : 0 }}
      >
        <path d="M -14 15 L -17 48 L 17 48 L 14 15 Q 0 20 -14 15" fill="#1565C0" />
        <path d="M -8 15 L 0 24 L 8 15" fill="#1976D2" />
      </motion.g>
      
      {/* Legs */}
      <rect x="-10" y="48" width="8" height="22" fill="#37474F" rx="1" />
      <rect x="2" y="48" width="8" height="22" fill="#37474F" rx="1" />
      
      {/* Shoes */}
      <ellipse cx="-6" cy="71" rx="7" ry="3" fill="#3E2723" />
      <ellipse cx="6" cy="71" rx="7" ry="3" fill="#3E2723" />
      
      {/* Left Arm (throwing/pointing arm) */}
      <motion.g
        animate={{ rotate: armAnim.leftArm }}
        transition={{ type: 'spring', stiffness: 200, damping: 20 }}
        style={{ originX: '-10px', originY: '18px' }}
      >
        <g transform="translate(-10, 18)">
          <path d="M 0 0 L -25 12" stroke="#FFCCBC" strokeWidth="7" strokeLinecap="round" />
          <circle cx="-27" cy="13" r="5" fill="#FFCCBC" />
          
          {/* Pointing finger for point gesture */}
          {currentGesture === GESTURES.point && (
            <motion.line
              x1="-27" y1="13" x2="-37" y2="8"
              stroke="#FFCCBC" strokeWidth="3" strokeLinecap="round"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            />
          )}
        </g>
      </motion.g>
      
      {/* Right Arm */}
      <motion.g
        animate={{ 
          rotate: armAnim.rightArm,
          ...(currentGesture === GESTURES.wave ? { rotate: [30, -30, 30] } : {})
        }}
        transition={currentGesture === GESTURES.wave 
          ? { duration: 0.5, repeat: Infinity }
          : { type: 'spring', stiffness: 200, damping: 20 }
        }
        style={{ originX: '14px', originY: '20px' }}
      >
        <g transform="translate(14, 20)">
          <path d="M 0 0 L 14 15" stroke="#FFCCBC" strokeWidth="7" strokeLinecap="round" />
          <circle cx="15" cy="16" r="5" fill="#FFCCBC" />
        </g>
      </motion.g>
      
      {/* Head */}
      <motion.g
        animate={currentGesture === GESTURES.think ? { rotate: [0, 5, 0] } : {}}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <circle cx="0" cy="0" r="17" fill="#FFCCBC" />
        
        {/* Hair */}
        <path d="M -15 -6 Q -17 -22 -9 -24 Q 0 -28 9 -24 Q 17 -22 15 -6" fill="#1a1a1a" />
        
        {/* Eyebrows */}
        <motion.g animate={{ y: expressionElements.eyebrowY }}>
          <line x1="-10" y1="-7" x2="-3" y2="-8" stroke="#333" strokeWidth="1.5" />
          <line x1="3" y1="-8" x2="10" y2="-7" stroke="#333" strokeWidth="1.5" />
        </motion.g>
        
        {/* Eyes */}
        <motion.g animate={{ scaleY: isBlinking ? 0.1 : 1 }} transition={{ duration: 0.1 }}>
          <motion.g animate={{ x: eyeOffset.x, y: eyeOffset.y }}>
            <motion.ellipse 
              cx="-6" cy="-1" 
              rx={3 * expressionElements.eyeScale} 
              ry={3.5 * expressionElements.eyeScale} 
              fill="#212121" 
            />
            <motion.ellipse 
              cx="6" cy="-1" 
              rx={3 * expressionElements.eyeScale} 
              ry={3.5 * expressionElements.eyeScale} 
              fill="#212121" 
            />
            <circle cx={-5 + eyeOffset.x * 0.5} cy={-2 + eyeOffset.y * 0.5} r="1" fill="white" />
            <circle cx={7 + eyeOffset.x * 0.5} cy={-2 + eyeOffset.y * 0.5} r="1" fill="white" />
          </motion.g>
        </motion.g>
        
        {/* Glasses */}
        <circle cx="-6" cy="-1" r="7" fill="none" stroke="#333" strokeWidth="1.5" />
        <circle cx="6" cy="-1" r="7" fill="none" stroke="#333" strokeWidth="1.5" />
        <line x1="1" y1="-1" x2="-1" y2="-1" stroke="#333" strokeWidth="1.5" />
        
        {/* Mustache */}
        <path d="M -6 7 Q 0 10 6 7" fill="#333" />
        
        {/* Mouth */}
        <motion.path 
          d={expressionElements.mouthPath} 
          fill="none" 
          stroke="#5D4037" 
          strokeWidth="1.5"
          animate={currentGesture === GESTURES.celebrate ? { d: 'M -7 9 Q 0 20 7 9' } : {}}
        />
        
        {/* Sweat drop for thinking */}
        {currentGesture === GESTURES.think && (
          <motion.ellipse
            cx="12" cy="-5"
            rx="2" ry="3"
            fill="#90CAF9"
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: [0, 1, 0], y: [-5, 5, 15] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        )}
        
        {/* Stars for celebrate */}
        {currentGesture === GESTURES.celebrate && (
          <>
            <motion.text
              x="-20" y="-25"
              fontSize="10"
              animate={{ opacity: [0, 1, 0], y: [-25, -35] }}
              transition={{ duration: 1, repeat: Infinity }}
            >
              ⭐
            </motion.text>
            <motion.text
              x="15" y="-20"
              fontSize="8"
              animate={{ opacity: [0, 1, 0], y: [-20, -30] }}
              transition={{ duration: 1, repeat: Infinity, delay: 0.3 }}
            >
              ✨
            </motion.text>
          </>
        )}
      </motion.g>
      
      {/* Speech Bubble */}
      <AnimatePresence>
        {showSpeech && showSpeechBubble && speech && (
          <motion.g
            initial={{ opacity: 0, scale: 0.8, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: -10 }}
            transition={{ type: 'spring', stiffness: 300, damping: 25 }}
          >
            <foreignObject
              x={config.speechOffset.x}
              y={config.speechOffset.y}
              width="180"
              height="80"
            >
              <div
                style={{
                  background: speechStyle.bg,
                  border: `2px solid ${speechStyle.border}`,
                  borderRadius: '12px',
                  padding: '8px 12px',
                  fontSize: '11px',
                  color: speechStyle.text,
                  fontWeight: 500,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  position: 'relative',
                }}
              >
                <span style={{ marginRight: '4px' }}>{speechStyle.icon}</span>
                {speech}
                {/* Speech bubble tail */}
                <div
                  style={{
                    position: 'absolute',
                    bottom: '-8px',
                    left: '20px',
                    width: 0,
                    height: 0,
                    borderLeft: '8px solid transparent',
                    borderRight: '8px solid transparent',
                    borderTop: `8px solid ${speechStyle.border}`,
                  }}
                />
              </div>
            </foreignObject>
          </motion.g>
        )}
      </AnimatePresence>
    </g>
  );
};

// Export gesture and expression constants
export { GESTURES, EXPRESSIONS };
export default ProfessorAvatar;



