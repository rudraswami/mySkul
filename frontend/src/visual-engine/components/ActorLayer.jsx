/**
 * ActorLayer - Professor Avatar and Character Rendering
 * Animated stick figure with Indian professor styling
 */

import React from 'react';
import { motion } from 'framer-motion';

const ActorLayer = ({ actors, animState, width, height }) => {
  return (
    <g id="actors-layer">
      {actors.map(actor => (
        <Actor
          key={actor.id}
          {...actor}
          animState={animState}
          width={width}
          height={height}
        />
      ))}
    </g>
  );
};

const Actor = ({ 
  id, 
  type, 
  position, 
  scale = 1, 
  initialState,
  actions,
  speech,
  animState,
  width, 
  height 
}) => {
  const x = (position?.x || 0.15) * width;
  const y = (position?.y || 0.6) * height;

  // Check if this actor has active animation
  const activeAnim = animState?.activeAnimations?.find(a => a.target === id);
  const gesture = activeAnim?.gesture || initialState || 'standing';

  if (type === 'professor') {
    return (
      <ProfessorAvatar
        x={x}
        y={y}
        scale={scale}
        gesture={gesture}
        speech={speech}
        animProgress={activeAnim?.progress || 0}
      />
    );
  }

  // Default stick figure
  return (
    <StickFigure
      x={x}
      y={y}
      scale={scale}
      gesture={gesture}
    />
  );
};

/**
 * Indian Professor Avatar
 * - Professional attire (kurta or shirt)
 * - Expressive gestures
 * - Speech bubble support
 */
const ProfessorAvatar = ({ x, y, scale, gesture, speech, animProgress }) => {
  const gestures = {
    standing: { armAngle: 0, pointing: false },
    pointing: { armAngle: -45, pointing: true },
    explaining: { armAngle: -30, pointing: false },
    thinking: { armAngle: 15, headTilt: -10 },
    celebrating: { armAngle: -60, celebration: true },
  };

  const currentGesture = gestures[gesture] || gestures['standing'];

  return (
    <motion.g
      id="professor"
      transform={`translate(${x}, ${y}) scale(${scale})`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Shadow */}
      <ellipse cx="0" cy="75" rx="25" ry="8" fill="rgba(0,0,0,0.2)" />

      {/* Body - Kurta style */}
      <motion.path
        d="M -20 20 L -25 70 L 25 70 L 20 20 Q 0 25 -20 20"
        fill="#1565C0"
        stroke="#0D47A1"
        strokeWidth="2"
        animate={{ 
          d: gesture === 'explaining' 
            ? "M -20 20 L -27 70 L 27 70 L 20 20 Q 0 25 -20 20"
            : "M -20 20 L -25 70 L 25 70 L 20 20 Q 0 25 -20 20"
        }}
        transition={{ duration: 0.3 }}
      />

      {/* Kurta collar */}
      <path
        d="M -10 20 L 0 30 L 10 20"
        fill="#1976D2"
        stroke="#0D47A1"
        strokeWidth="1"
      />

      {/* Legs */}
      <rect x="-12" y="70" width="10" height="30" fill="#37474F" />
      <rect x="2" y="70" width="10" height="30" fill="#37474F" />

      {/* Shoes */}
      <ellipse cx="-7" cy="102" rx="8" ry="5" fill="#4E342E" />
      <ellipse cx="7" cy="102" rx="8" ry="5" fill="#4E342E" />

      {/* Left Arm (gesturing) */}
      <motion.g
        animate={{ rotate: currentGesture.armAngle }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        style={{ transformOrigin: '-15px 25px' }}
      >
        <path
          d="M -20 25 L -45 45 L -50 40"
          fill="none"
          stroke="#FFE0B2"
          strokeWidth="8"
          strokeLinecap="round"
        />
        {/* Hand */}
        <circle cx="-50" cy="40" r="6" fill="#FFE0B2" />
        
        {/* Pointing finger */}
        {currentGesture.pointing && (
          <motion.path
            d="M -50 40 L -65 30"
            stroke="#FFE0B2"
            strokeWidth="4"
            strokeLinecap="round"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.3 }}
          />
        )}
      </motion.g>

      {/* Right Arm (holding chalk/pointer) */}
      <g>
        <path
          d="M 20 25 L 40 50 L 45 48"
          fill="none"
          stroke="#FFE0B2"
          strokeWidth="8"
          strokeLinecap="round"
        />
        <circle cx="45" cy="48" r="6" fill="#FFE0B2" />
        
        {/* Chalk/Pointer */}
        <rect x="42" y="45" width="20" height="4" fill="#FFF" rx="1" transform="rotate(20 42 47)" />
      </g>

      {/* Head */}
      <motion.g
        animate={{ rotate: currentGesture.headTilt || 0 }}
        transition={{ duration: 0.3 }}
      >
        {/* Face */}
        <circle cx="0" cy="0" r="22" fill="#FFE0B2" stroke="#FFCC80" strokeWidth="2" />
        
        {/* Hair */}
        <path
          d="M -20 -8 Q -22 -25 -10 -28 Q 0 -32 10 -28 Q 22 -25 20 -8"
          fill="#212121"
        />
        
        {/* Eyes */}
        <motion.g
          animate={{ scaleY: gesture === 'thinking' ? 0.1 : 1 }}
          transition={{ duration: 0.2 }}
        >
          <ellipse cx="-8" cy="-2" rx="3" ry="4" fill="#212121" />
          <ellipse cx="8" cy="-2" rx="3" ry="4" fill="#212121" />
          {/* Eye shine */}
          <circle cx="-7" cy="-3" r="1" fill="white" />
          <circle cx="9" cy="-3" r="1" fill="white" />
        </motion.g>
        
        {/* Eyebrows */}
        <motion.path
          d="M -12 -8 Q -8 -12 -4 -8"
          fill="none"
          stroke="#424242"
          strokeWidth="2"
          animate={{ 
            d: gesture === 'explaining' 
              ? "M -12 -10 Q -8 -14 -4 -10" 
              : "M -12 -8 Q -8 -12 -4 -8" 
          }}
        />
        <motion.path
          d="M 4 -8 Q 8 -12 12 -8"
          fill="none"
          stroke="#424242"
          strokeWidth="2"
          animate={{ 
            d: gesture === 'explaining' 
              ? "M 4 -10 Q 8 -14 12 -10" 
              : "M 4 -8 Q 8 -12 12 -8" 
          }}
        />
        
        {/* Nose */}
        <path d="M 0 0 L 2 6 L -2 6" fill="#FFCC80" />
        
        {/* Mouth */}
        <motion.path
          d="M -6 10 Q 0 14 6 10"
          fill="none"
          stroke="#5D4037"
          strokeWidth="2"
          animate={{
            d: gesture === 'celebrating' 
              ? "M -8 10 Q 0 18 8 10" 
              : "M -6 10 Q 0 14 6 10"
          }}
        />
        
        {/* Glasses */}
        <circle cx="-8" cy="-2" r="8" fill="none" stroke="#424242" strokeWidth="2" />
        <circle cx="8" cy="-2" r="8" fill="none" stroke="#424242" strokeWidth="2" />
        <line x1="0" y1="-2" x2="-8" y2="-2" stroke="#424242" strokeWidth="2" />
        <line x1="16" y1="-2" x2="22" y2="-5" stroke="#424242" strokeWidth="2" />
        <line x1="-16" y1="-2" x2="-22" y2="-5" stroke="#424242" strokeWidth="2" />
        
        {/* Mustache */}
        <path
          d="M -8 6 Q -4 8 0 6 Q 4 8 8 6"
          fill="#424242"
        />
      </motion.g>

      {/* Speech Bubble */}
      {speech && (
        <motion.g
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5 }}
        >
          <path
            d="M 40 -40 L 60 -60 L 150 -60 L 150 -20 L 60 -20 L 40 -40 L 50 -30"
            fill="white"
            stroke="#E0E0E0"
            strokeWidth="2"
          />
          <text x="100" y="-35" textAnchor="middle" fontSize="11" fill="#333">
            {speech}
          </text>
        </motion.g>
      )}

      {/* Celebration particles */}
      {gesture === 'celebrating' && (
        <g>
          {[...Array(6)].map((_, i) => (
            <motion.circle
              key={i}
              cx={-30 + i * 12}
              cy={-50}
              r="4"
              fill={['#FF5722', '#FFC107', '#4CAF50', '#2196F3', '#9C27B0', '#E91E63'][i]}
              initial={{ y: 0, opacity: 1 }}
              animate={{ y: [-10, -40], opacity: [1, 0] }}
              transition={{ 
                repeat: Infinity, 
                duration: 1, 
                delay: i * 0.1,
                ease: 'easeOut'
              }}
            />
          ))}
        </g>
      )}
    </motion.g>
  );
};

/**
 * Simple Stick Figure (for secondary characters)
 */
const StickFigure = ({ x, y, scale, gesture }) => {
  return (
    <g transform={`translate(${x}, ${y}) scale(${scale})`}>
      {/* Head */}
      <circle cx="0" cy="-40" r="15" fill="#FFE0B2" stroke="#FFCC80" strokeWidth="2" />
      
      {/* Body */}
      <line x1="0" y1="-25" x2="0" y2="20" stroke="#333" strokeWidth="4" />
      
      {/* Arms */}
      <line x1="0" y1="-15" x2="-25" y2="5" stroke="#333" strokeWidth="4" />
      <line x1="0" y1="-15" x2="25" y2="5" stroke="#333" strokeWidth="4" />
      
      {/* Legs */}
      <line x1="0" y1="20" x2="-15" y2="50" stroke="#333" strokeWidth="4" />
      <line x1="0" y1="20" x2="15" y2="50" stroke="#333" strokeWidth="4" />
      
      {/* Eyes */}
      <circle cx="-5" cy="-42" r="2" fill="#333" />
      <circle cx="5" cy="-42" r="2" fill="#333" />
    </g>
  );
};

export default ActorLayer;






