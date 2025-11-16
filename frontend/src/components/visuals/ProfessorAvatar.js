/**
 * Professor Avatar Component
 * Animated SVG professor character that:
 * - Points to elements
 * - Writes equations on board
 * - Demonstrates concepts
 * - Shows explaining gestures
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function ProfessorAvatar({
  action = 'explaining',
  targetPosition = null,
  visible = true,
  speechBubble = null,
  currentTime = 0,
  professorActions = []
}) {
  const [currentAction, setCurrentAction] = useState(action);
  const [showSpeech, setShowSpeech] = useState(false);
  const [speechText, setSpeechText] = useState('');

  // Update action based on timeline
  useEffect(() => {
    if (professorActions && professorActions.length > 0) {
      const activeAction = professorActions.find(
        pa => currentTime >= pa.time && currentTime <= (pa.time + (pa.duration_ms || 2000))
      );
      
      if (activeAction) {
        setCurrentAction(activeAction.action);
        if (activeAction.speech_bubble) {
          setSpeechText(activeAction.speech_bubble);
          setShowSpeech(true);
        } else {
          setShowSpeech(false);
        }
      }
    }
  }, [currentTime, professorActions]);

  // Animation variants for different actions
  const avatarVariants = {
    explaining: {
      scale: [1, 1.02, 1],
      y: [0, -2, 0],
      transition: { duration: 2, repeat: Infinity, ease: "easeInOut" }
    },
    pointing: {
      rotate: [0, -5, 0, 5, 0],
      transition: { duration: 1.5, repeat: 2 }
    },
    writing: {
      x: [0, 3, 0, -3, 0],
      transition: { duration: 0.8, repeat: 3 }
    },
    demonstrating: {
      scale: [1, 1.05, 1],
      rotate: [0, 10, 0, -10, 0],
      transition: { duration: 2, repeat: 2 }
    },
    concluding: {
      scale: [1, 1.1, 1],
      y: [0, -5, 0],
      transition: { duration: 0.8 }
    }
  };

  const armVariants = {
    explaining: {
      rotate: [-10, 10, -10],
      transition: { duration: 2, repeat: Infinity }
    },
    pointing: {
      rotate: targetPosition ? calculatePointingAngle(targetPosition) : -30,
      transition: { duration: 0.5 }
    },
    writing: {
      rotate: [-15, -5, -15],
      x: [0, 5, 0],
      transition: { duration: 0.4, repeat: 5 }
    },
    demonstrating: {
      rotate: [-20, 20, -20],
      transition: { duration: 1.5, repeat: 2 }
    }
  };

  // Calculate pointing angle to target
  function calculatePointingAngle(target) {
    const avatarPos = { x: 750, y: 500 }; // Bottom right position
    const dx = target.x - avatarPos.x;
    const dy = target.y - avatarPos.y;
    return Math.atan2(dy, dx) * (180 / Math.PI);
  }

  if (!visible) return null;

  return (
    <motion.div
      className="absolute bottom-4 right-4 z-50"
      initial={{ opacity: 0, scale: 0.8, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.8, y: 20 }}
      transition={{ duration: 0.5 }}
    >
      {/* Professor SVG Character */}
      <motion.svg
        width="120"
        height="140"
        viewBox="0 0 120 140"
        variants={avatarVariants}
        animate={currentAction}
      >
        {/* Head */}
        <circle cx="60" cy="35" r="22" fill="#F3E5D8" stroke="#D4A574" strokeWidth="2"/>
        
        {/* Face features */}
        <circle cx="52" cy="32" r="3" fill="#1E293B"/> {/* Left eye */}
        <circle cx="68" cy="32" r="3" fill="#1E293B"/> {/* Right eye */}
        <path d="M 52 42 Q 60 46 68 42" stroke="#1E293B" strokeWidth="2" fill="none" strokeLinecap="round"/> {/* Smile */}
        
        {/* Hair */}
        <path d="M 40 25 Q 45 18 50 20 Q 55 15 60 18 Q 65 15 70 20 Q 75 18 80 25" fill="#1E293B" />
        
        {/* Neck */}
        <rect x="54" y="55" width="12" height="8" fill="#F3E5D8"/>
        
        {/* Lab coat/Shirt */}
        <rect x="40" y="63" width="40" height="50" rx="6" fill="white" stroke="#E5E7EB" strokeWidth="2"/>
        <rect x="45" y="68" width="30" height="40" rx="4" fill="#4A5568"/> {/* Inner shirt */}
        
        {/* Collar */}
        <path d="M 50 63 L 55 68" stroke="#E5E7EB" strokeWidth="2" fill="none"/>
        <path d="M 70 63 L 65 68" stroke="#E5E7EB" strokeWidth="2" fill="none"/>
        
        {/* Arm (pointing/writing) */}
        <motion.g
          variants={armVariants}
          animate={currentAction}
          style={{ transformOrigin: '75px 70px' }}
        >
          <line x1="75" y1="70" x2="105" y2="55" stroke="#F3E5D8" strokeWidth="6" strokeLinecap="round"/>
          <circle cx="105" cy="55" r="6" fill="#F3E5D8" stroke="#D4A574" strokeWidth="2"/>
          
          {/* Pointer finger when pointing */}
          {currentAction === 'pointing' && (
            <line x1="105" y1="55" x2="115" y2="45" stroke="#F3E5D8" strokeWidth="3" strokeLinecap="round"/>
          )}
          
          {/* Chalk when writing */}
          {currentAction === 'writing' && (
            <rect x="103" y="50" width="8" height="15" rx="2" fill="#FCD34D" stroke="#F59E0B" strokeWidth="1"/>
          )}
        </motion.g>
        
        {/* Badge/Icon */}
        <circle cx="60" cy="85" r="8" fill="#7C3AED" stroke="#6D28D9" strokeWidth="2"/>
        <text x="60" y="89" textAnchor="middle" fill="white" fontSize="12">👨‍🏫</text>
      </motion.svg>

      {/* Speech Bubble */}
      <AnimatePresence>
        {showSpeech && speechText && (
          <motion.div
            className="absolute top-0 right-full mr-4 bg-white rounded-xl shadow-lg p-3 max-w-xs"
            style={{ minWidth: '200px' }}
            initial={{ opacity: 0, x: 20, scale: 0.8 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 10, scale: 0.9 }}
            transition={{ duration: 0.3 }}
          >
            {/* Speech bubble tail */}
            <div className="absolute top-8 right-0 w-0 h-0 border-t-8 border-t-transparent border-b-8 border-b-transparent border-l-8 border-l-white" style={{ right: '-8px' }}/>
            
            <p className="text-sm text-gray-700 leading-relaxed">{speechText}</p>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Professor name badge */}
      <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-3 py-1 rounded-full text-xs font-semibold shadow-md">
        Professor
      </div>
    </motion.div>
  );
}

