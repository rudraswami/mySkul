/**
 * ✋ DRAWING HAND
 * ==============
 * 
 * Animated hand that follows strokes as they're drawn
 * The SIGNATURE feature of Magic Notebook!
 * 
 * Features:
 * - 3 poses: idle, drawing, pointing
 * - Follows stroke paths
 * - Rotates to face drawing direction
 * - Smooth Framer Motion animations
 * - Synchronizes with stroke drawing
 */

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';

// ============================================
// HAND SVG GRAPHICS (Inline)
// ============================================

/**
 * Hand in IDLE pose (relaxed, fingers together)
 */
const HandIdle = ({ color = '#FFD7BA', size = 60 }) => (
  <svg width={size} height={size} viewBox="0 0 60 60" fill="none">
    {/* Palm */}
    <path
      d="M 20 25 Q 18 30 18 35 Q 18 42 23 47 Q 28 52 35 52 Q 42 52 47 47 Q 52 42 52 35 L 52 20 Q 52 15 48 15 L 45 15 L 45 10 Q 45 5 40 5 L 37 5 L 37 8 Q 37 5 33 5 L 30 5 L 30 10 Q 30 5 25 5 Q 20 5 20 10 Z"
      fill={color}
      stroke="#000"
      strokeWidth="1.5"
      strokeLinejoin="round"
    />
    {/* Thumb */}
    <path
      d="M 20 25 Q 15 25 12 28 Q 10 32 12 36 Q 14 40 18 40 Q 20 40 20 35"
      fill={color}
      stroke="#000"
      strokeWidth="1.5"
      strokeLinejoin="round"
    />
    {/* Finger lines */}
    <line x1="30" y1="12" x2="30" y2="20" stroke="#000" strokeWidth="1" opacity="0.3" />
    <line x1="37" y1="10" x2="37" y2="20" stroke="#000" strokeWidth="1" opacity="0.3" />
    <line x1="45" y1="15" x2="45" y2="25" stroke="#000" strokeWidth="1" opacity="0.3" />
  </svg>
);

/**
 * Hand in DRAWING pose (holding pen, index finger extended)
 */
const HandDrawing = ({ color = '#FFD7BA', penColor = '#2563EB', size = 60 }) => (
  <svg width={size} height={size} viewBox="0 0 60 60" fill="none">
    {/* Palm (slightly angled) */}
    <path
      d="M 22 28 Q 20 32 20 37 Q 20 43 24 48 Q 28 52 34 52 Q 40 52 45 48 Q 50 44 50 38 L 50 25 Q 50 20 46 20 L 44 20 L 44 18 Q 44 14 40 14 L 38 14 L 38 16 Q 38 14 34 14 L 32 14"
      fill={color}
      stroke="#000"
      strokeWidth="1.5"
      strokeLinejoin="round"
    />
    {/* Pen (between thumb and index) */}
    <line x1="32" y1="14" x2="28" y2="4" stroke={penColor} strokeWidth="3" strokeLinecap="round" />
    <circle cx="28" cy="2" r="2" fill={penColor} />
    {/* Thumb (gripping pen) */}
    <path
      d="M 22 28 Q 18 28 15 30 Q 13 33 14 36 Q 16 39 20 39 Q 22 38 22 35"
      fill={color}
      stroke="#000"
      strokeWidth="1.5"
      strokeLinejoin="round"
    />
    {/* Index finger extended */}
    <path
      d="M 32 14 Q 30 10 30 6 Q 30 3 32 2 Q 34 2 34 6 L 34 14"
      fill={color}
      stroke="#000"
      strokeWidth="1.5"
      strokeLinejoin="round"
    />
    {/* Finger lines */}
    <line x1="38" y1="16" x2="38" y2="22" stroke="#000" strokeWidth="1" opacity="0.3" />
    <line x1="44" y1="20" x2="44" y2="28" stroke="#000" strokeWidth="1" opacity="0.3" />
  </svg>
);

/**
 * Hand in POINTING pose (index finger extended, others curled)
 */
const HandPointing = ({ color = '#FFD7BA', size = 60 }) => (
  <svg width={size} height={size} viewBox="0 0 60 60" fill="none">
    {/* Palm (closed fist) */}
    <path
      d="M 25 30 Q 23 34 23 38 Q 23 44 27 48 Q 31 52 37 52 Q 43 52 47 48 Q 51 44 51 38 L 51 30 Q 51 26 48 26 L 46 26 Q 46 24 44 24 L 42 24 Q 42 22 40 22 L 38 22"
      fill={color}
      stroke="#000"
      strokeWidth="1.5"
      strokeLinejoin="round"
    />
    {/* Thumb (visible) */}
    <path
      d="M 25 30 Q 21 30 18 32 Q 16 35 17 38 Q 19 41 23 41 Q 25 40 25 37"
      fill={color}
      stroke="#000"
      strokeWidth="1.5"
      strokeLinejoin="round"
    />
    {/* Index finger POINTING */}
    <path
      d="M 38 22 Q 36 18 36 12 Q 36 8 36 4 Q 36 2 38 2 Q 40 2 40 4 L 40 12 Q 40 18 38 22"
      fill={color}
      stroke="#000"
      strokeWidth="1.5"
      strokeLinejoin="round"
    />
    {/* Fingernail */}
    <ellipse cx="38" cy="3" rx="2" ry="3" fill="#FFF" opacity="0.5" />
  </svg>
);

// ============================================
// MAIN COMPONENT: DRAWING HAND
// ============================================

const DrawingHand = ({
  // Position
  x = 0,
  y = 0,
  
  // Rotation (in degrees)
  rotation = 0,
  
  // Pose
  pose = 'idle', // 'idle' | 'drawing' | 'pointing'
  
  // Styling
  color = '#FFD7BA',
  penColor = '#2563EB',
  size = 60,
  
  // Animation
  animate = true,
  transition,
  
  // Visibility
  visible = true,
  
  // Callbacks
  onPoseChange,
  
  // Class
  className = '',
}) => {
  // Select hand graphic based on pose
  const HandComponent = useMemo(() => {
    switch (pose) {
      case 'drawing':
        return HandDrawing;
      case 'pointing':
        return HandPointing;
      case 'idle':
      default:
        return HandIdle;
    }
  }, [pose]);
  
  // Default transition with spring physics
  const defaultTransition = useMemo(() => ({
    type: 'spring',
    stiffness: 150,
    damping: 20,
    mass: 0.5,
  }), []);
  
  if (!visible) return null;
  
  return (
    <motion.div
      className={`drawing-hand ${className}`}
      initial={animate ? { opacity: 0, scale: 0.5 } : false}
      animate={{
        x,
        y,
        rotate: rotation,
        opacity: 1,
        scale: 1,
      }}
      transition={transition || defaultTransition}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        pointerEvents: 'none',
        transformOrigin: 'center center',
        zIndex: 1000,
        filter: 'drop-shadow(2px 4px 8px rgba(0,0,0,0.2))',
      }}
      onAnimationComplete={() => {
        if (onPoseChange) {
          onPoseChange(pose);
        }
      }}
    >
      <HandComponent color={color} penColor={penColor} size={size} />
    </motion.div>
  );
};

// ============================================
// PRESET ANIMATIONS
// ============================================

/**
 * Hand floating animation (gentle bobbing)
 */
export const FloatingHandVariants = {
  idle: {
    y: [0, -5, 0],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

/**
 * Hand drawing motion (quick movements)
 */
export const DrawingHandVariants = {
  drawing: {
    scale: [1, 0.95, 1],
    transition: {
      duration: 0.3,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

/**
 * Hand pointing pulse (emphasis)
 */
export const PointingHandVariants = {
  pointing: {
    scale: [1, 1.1, 1],
    transition: {
      duration: 0.5,
      times: [0, 0.5, 1],
    },
  },
};

// ============================================
// EXPORTS
// ============================================

export { HandIdle, HandDrawing, HandPointing };
export default DrawingHand;

