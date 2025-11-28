/**
 * 🎉 Micro Reward Component
 * 
 * Shows instant dopamine hits for correct answers, streaks, etc.
 * Animated celebrations that make learning feel rewarding.
 */

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import confetti from 'canvas-confetti';

// Celebration animations
const CELEBRATIONS = {
  confetti: () => {
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    });
  },
  
  glow: null, // CSS animation
  
  shake: null, // CSS animation
  
  bounce: null, // CSS animation
  
  sparkle: () => {
    confetti({
      particleCount: 50,
      spread: 60,
      origin: { y: 0.7 },
      colors: ['#FFD700', '#FFA500', '#FF6347']
    });
  },
  
  flame: () => {
    confetti({
      particleCount: 80,
      spread: 100,
      origin: { y: 0.6 },
      colors: ['#FF4500', '#FF6347', '#FFA500', '#FFD700']
    });
  },
  
  pulse: null, // CSS animation
};

// Animation variants
const containerVariants = {
  hidden: { opacity: 0, scale: 0.8, y: 20 },
  visible: { 
    opacity: 1, 
    scale: 1, 
    y: 0,
    transition: { 
      type: 'spring',
      stiffness: 300,
      damping: 20
    }
  },
  exit: { 
    opacity: 0, 
    scale: 0.8, 
    y: -20,
    transition: { duration: 0.3 }
  }
};

const emojiVariants = {
  hidden: { scale: 0, rotate: -180 },
  visible: { 
    scale: 1, 
    rotate: 0,
    transition: { 
      type: 'spring',
      stiffness: 500,
      damping: 15,
      delay: 0.1
    }
  }
};

const xpVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: { 
    opacity: 1, 
    x: 0,
    transition: { delay: 0.3 }
  }
};

/**
 * Main Micro Reward Component
 */
const MicroReward = ({ 
  reward, 
  onComplete,
  autoHide = true,
  hideAfter = 3000 
}) => {
  const [isVisible, setIsVisible] = useState(true);
  
  useEffect(() => {
    if (!reward) return;
    
    // Trigger celebration effect
    const celebrationFn = CELEBRATIONS[reward.celebration_type];
    if (celebrationFn) {
      celebrationFn();
    }
    
    // Auto-hide after delay
    if (autoHide) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        onComplete?.();
      }, hideAfter);
      
      return () => clearTimeout(timer);
    }
  }, [reward, autoHide, hideAfter, onComplete]);
  
  if (!reward) return null;
  
  const getCelebrationClass = () => {
    switch (reward.celebration_type) {
      case 'glow':
        return 'animate-glow';
      case 'shake':
        return 'animate-shake';
      case 'bounce':
        return 'animate-bounce';
      case 'pulse':
        return 'animate-pulse';
      default:
        return '';
    }
  };
  
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          exit="exit"
          className={`fixed top-20 left-1/2 transform -translate-x-1/2 z-50 ${getCelebrationClass()}`}
        >
          <div className="bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 rounded-2xl p-1 shadow-2xl">
            <div className="bg-white dark:bg-gray-900 rounded-xl px-6 py-4 flex items-center space-x-4">
              {/* Emoji */}
              <motion.span 
                variants={emojiVariants}
                className="text-4xl"
              >
                {reward.emoji}
              </motion.span>
              
              {/* Message */}
              <div className="flex flex-col">
                <span className="text-lg font-bold text-gray-900 dark:text-white">
                  {reward.message}
                </span>
                
                {/* XP Earned */}
                {reward.xp_earned > 0 && (
                  <motion.span 
                    variants={xpVariants}
                    className="text-sm font-medium text-green-600 dark:text-green-400"
                  >
                    +{reward.xp_earned} XP
                  </motion.span>
                )}
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

/**
 * Streak Celebration Component
 */
export const StreakCelebration = ({ streakDays, badgeEarned }) => {
  useEffect(() => {
    if (badgeEarned) {
      // Big celebration for badge
      confetti({
        particleCount: 150,
        spread: 100,
        origin: { y: 0.5 },
        colors: ['#FFD700', '#FFA500', '#FF6347', '#4169E1', '#32CD32']
      });
    }
  }, [badgeEarned]);
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.5 }}
      animate={{ opacity: 1, scale: 1 }}
      className="fixed inset-0 flex items-center justify-center z-50 bg-black/50"
    >
      <motion.div
        initial={{ y: 50 }}
        animate={{ y: 0 }}
        className="bg-gradient-to-br from-orange-500 to-red-600 rounded-3xl p-8 text-center shadow-2xl max-w-sm mx-4"
      >
        <motion.div
          animate={{ 
            scale: [1, 1.2, 1],
            rotate: [0, 10, -10, 0]
          }}
          transition={{ repeat: Infinity, duration: 2 }}
          className="text-7xl mb-4"
        >
          🔥
        </motion.div>
        
        <h2 className="text-3xl font-bold text-white mb-2">
          {streakDays} Day Streak!
        </h2>
        
        {badgeEarned && (
          <div className="mt-4 bg-white/20 rounded-xl p-4">
            <p className="text-yellow-200 font-medium">Badge Unlocked!</p>
            <p className="text-2xl font-bold text-white">{badgeEarned}</p>
          </div>
        )}
        
        <p className="text-white/80 mt-4">
          Keep the fire burning! 🔥
        </p>
      </motion.div>
    </motion.div>
  );
};

/**
 * Level Up Celebration Component
 */
export const LevelUpCelebration = ({ oldLevel, newLevel, onClose }) => {
  useEffect(() => {
    // Epic celebration
    const duration = 3000;
    const end = Date.now() + duration;
    
    const frame = () => {
      confetti({
        particleCount: 7,
        angle: 60,
        spread: 55,
        origin: { x: 0 },
        colors: ['#FFD700', '#FFA500', '#FF6347']
      });
      confetti({
        particleCount: 7,
        angle: 120,
        spread: 55,
        origin: { x: 1 },
        colors: ['#FFD700', '#FFA500', '#FF6347']
      });
      
      if (Date.now() < end) {
        requestAnimationFrame(frame);
      }
    };
    
    frame();
  }, []);
  
  const levelEmojis = {
    'Explorer': '🔭',
    'Analyst': '🔬',
    'Tactician': '🎯',
    'Scientist': '🧪',
    'Master': '👑'
  };
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 flex items-center justify-center z-50 bg-black/70"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0, rotate: -180 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ type: 'spring', stiffness: 200, damping: 15 }}
        className="bg-gradient-to-br from-purple-600 via-pink-600 to-orange-500 rounded-3xl p-10 text-center shadow-2xl max-w-md mx-4"
        onClick={e => e.stopPropagation()}
      >
        <motion.div
          animate={{ 
            y: [0, -20, 0],
            scale: [1, 1.1, 1]
          }}
          transition={{ repeat: Infinity, duration: 1.5 }}
          className="text-8xl mb-6"
        >
          {levelEmojis[newLevel] || '🆙'}
        </motion.div>
        
        <h1 className="text-4xl font-bold text-white mb-2">
          LEVEL UP!
        </h1>
        
        <div className="flex items-center justify-center space-x-4 my-6">
          <span className="text-white/60 text-xl">{oldLevel}</span>
          <span className="text-3xl">→</span>
          <span className="text-yellow-300 text-2xl font-bold">{newLevel}</span>
        </div>
        
        <p className="text-white/80 text-lg">
          You're now a <span className="font-bold text-yellow-300">{newLevel}</span>!
        </p>
        
        <button
          onClick={onClose}
          className="mt-6 px-8 py-3 bg-white text-purple-600 font-bold rounded-full hover:bg-yellow-300 transition-colors"
        >
          Continue Learning! 🚀
        </button>
      </motion.div>
    </motion.div>
  );
};

/**
 * Quick XP Popup (for small rewards)
 */
export const XPPopup = ({ xp, position = { x: 0, y: 0 } }) => {
  return (
    <motion.div
      initial={{ opacity: 1, y: 0, scale: 1 }}
      animate={{ opacity: 0, y: -50, scale: 1.5 }}
      transition={{ duration: 1 }}
      className="fixed pointer-events-none z-50 font-bold text-green-500"
      style={{ left: position.x, top: position.y }}
    >
      +{xp} XP
    </motion.div>
  );
};

export default MicroReward;

// Add these styles to your global CSS or tailwind config:
/*
@keyframes glow {
  0%, 100% { box-shadow: 0 0 20px rgba(255, 215, 0, 0.5); }
  50% { box-shadow: 0 0 40px rgba(255, 215, 0, 0.8); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.animate-glow {
  animation: glow 1s ease-in-out infinite;
}

.animate-shake {
  animation: shake 0.5s ease-in-out;
}
*/



