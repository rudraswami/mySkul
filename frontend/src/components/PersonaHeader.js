/**
 * PersonaHeader Component
 * Displays adaptive emotion gradient header with persona indicators
 */
import React from 'react';
import { motion } from 'framer-motion';
import { Brain, Heart, BookOpen, Users } from 'lucide-react';

const PersonaHeader = ({ 
  personaConfig, 
  motivationalMessage, 
  userStats = {}, 
  className = '' 
}) => {
  if (!personaConfig) {
    return null;
  }

  const { colorScheme, gradient, greeting, tone } = personaConfig;
  
  // Persona icons
  const PersonaIcon = () => {
    switch (tone) {
      case 'academic':
        return <BookOpen className="w-5 h-5" />;
      case 'supportive':
        return <Heart className="w-5 h-5" />;
      default:
        return <Brain className="w-5 h-5" />;
    }
  };

  // Animation variants
  const headerVariants = {
    hidden: { opacity: 0, y: -20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.5, ease: "easeOut" }
    }
  };

  const pulseVariants = {
    pulse: {
      scale: [1, 1.05, 1],
      transition: {
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  return (
    <motion.div
      variants={headerVariants}
      initial="hidden"
      animate="visible"
      className={`relative overflow-hidden rounded-lg ${className}`}
    >
      {/* Gradient Background */}
      <div className={`bg-gradient-to-r ${gradient} p-4`}>
        {/* Top Row - Persona and Stats */}
        <div className="flex items-center justify-between mb-2">
          {/* Persona Indicator */}
          <motion.div 
            className="flex items-center space-x-2 text-white"
            variants={tone === 'supportive' ? pulseVariants : {}}
            animate={tone === 'supportive' ? 'pulse' : ''}
          >
            <div className="p-2 bg-white bg-opacity-20 rounded-full">
              <PersonaIcon />
            </div>
            <div>
              <span className="text-sm font-medium opacity-90">
                {tone === 'academic' ? 'Professor Mode' : 
                 tone === 'supportive' ? 'Mentor Mode' : 
                 'Adaptive Mode'}
              </span>
            </div>
          </motion.div>

          {/* User Stats */}
          {userStats && (
            <div className="flex items-center space-x-4 text-white text-sm">
              {userStats.streak && (
                <div className="flex items-center space-x-1">
                  <span className="opacity-75">Streak:</span>
                  <span className="font-bold">{userStats.streak}</span>
                  <span>🔥</span>
                </div>
              )}
              {userStats.focus && (
                <div className="flex items-center space-x-1">
                  <span className="opacity-75">Focus:</span>
                  <span className="font-medium">{userStats.focus}</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Greeting Message */}
        <motion.div 
          className="text-white"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <p className="text-lg font-medium mb-1">{greeting}</p>
          {motivationalMessage && (
            <motion.p 
              className="text-sm opacity-90"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
            >
              {motivationalMessage}
            </motion.p>
          )}
        </motion.div>

        {/* Decorative Elements */}
        <div className="absolute top-0 right-0 w-20 h-20 opacity-10">
          <div className="w-full h-full rounded-full bg-white transform rotate-12 -translate-x-4 -translate-y-4"></div>
        </div>
        <div className="absolute bottom-0 left-0 w-16 h-16 opacity-10">
          <div className="w-full h-full rounded-full bg-white transform -rotate-12 translate-x-2 translate-y-2"></div>
        </div>
      </div>

      {/* Bottom Accent Line */}
      <motion.div 
        className={`h-1 bg-gradient-to-r ${gradient} opacity-60`}
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ delay: 0.7, duration: 0.8 }}
      />
    </motion.div>
  );
};

export default PersonaHeader;