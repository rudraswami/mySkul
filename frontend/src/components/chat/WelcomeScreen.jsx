/**
 * Enhanced Welcome Screen - Premium First Impression
 * Features: Unique branding, engaging prompts, no generic icons
 */
import React from 'react';
import { motion } from 'framer-motion';
import { 
  Sparkles, 
  Zap, 
  Target, 
  BookOpen,
  ArrowRight,
  Rocket,
  Brain,
  Trophy
} from 'lucide-react';

// Animated mascot/logo
const SathiLogo = () => (
  <motion.div
    initial={{ scale: 0, rotate: -180 }}
    animate={{ scale: 1, rotate: 0 }}
    transition={{ type: 'spring', duration: 0.8 }}
    className="relative"
  >
    {/* Outer glow */}
    <div className="absolute inset-0 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full blur-2xl opacity-30 scale-150" />
    
    {/* Main logo container */}
    <div className="relative w-24 h-24 bg-gradient-to-br from-purple-500 via-pink-500 to-orange-400 rounded-3xl flex items-center justify-center shadow-2xl shadow-purple-500/30">
      {/* Animated sparkle effect */}
      <motion.div
        animate={{ 
          scale: [1, 1.2, 1],
          rotate: [0, 180, 360]
        }}
        transition={{ 
          duration: 3, 
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute inset-0 flex items-center justify-center"
      >
        <Sparkles className="w-6 h-6 text-white/30 absolute top-2 right-2" />
        <Sparkles className="w-4 h-4 text-white/20 absolute bottom-3 left-3" />
      </motion.div>
      
      {/* Main emoji/icon */}
      <span className="text-5xl">🤝</span>
    </div>
    
    {/* Status indicator */}
    <motion.div
      animate={{ scale: [1, 1.2, 1] }}
      transition={{ duration: 2, repeat: Infinity }}
      className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 rounded-full border-4 border-white dark:border-gray-900 flex items-center justify-center"
    >
      <div className="w-2 h-2 bg-white rounded-full" />
    </motion.div>
  </motion.div>
);

// Quick prompt card
const PromptCard = ({ text, icon: Icon, gradient, onClick, delay }) => (
  <motion.button
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.3 }}
    whileHover={{ scale: 1.02, y: -2 }}
    whileTap={{ scale: 0.98 }}
    onClick={() => onClick?.(text)}
    className="group relative flex items-start gap-3 p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-700 hover:shadow-lg hover:shadow-purple-500/10 transition-all duration-200 text-left"
  >
    {/* Icon */}
    <div className={`flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br ${gradient} flex items-center justify-center shadow-sm`}>
      <Icon className="w-5 h-5 text-white" />
    </div>
    
    {/* Text */}
    <div className="flex-1 min-w-0">
      <p className="text-sm text-gray-700 dark:text-gray-200 font-medium line-clamp-2 group-hover:text-purple-700 dark:group-hover:text-purple-300 transition-colors">
        {text}
      </p>
    </div>
    
    {/* Arrow */}
    <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-purple-500 group-hover:translate-x-1 transition-all flex-shrink-0 mt-1" />
  </motion.button>
);

export default function WelcomeScreen({ 
  onPromptClick, 
  prompts = [],
  userName = null 
}) {
  // Default prompts if none provided
  const defaultPrompts = prompts.length > 0 ? prompts : [
    {
      text: "Explain the fundamental theorem of calculus",
      icon: BookOpen,
      gradient: "from-blue-500 to-cyan-500"
    },
    {
      text: "What is the difference between permutations and combinations?",
      icon: Brain,
      gradient: "from-purple-500 to-pink-500"
    },
    {
      text: "How do I solve quadratic equations in real-world problems?",
      icon: Target,
      gradient: "from-orange-500 to-red-500"
    },
    {
      text: "Give me a JEE-level problem on integration by parts",
      icon: Trophy,
      gradient: "from-green-500 to-emerald-500"
    }
  ];

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-4 py-8">
      {/* Logo */}
      <SathiLogo />
      
      {/* Main Heading */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mt-8 text-center"
      >
        <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-orange-500 bg-clip-text text-transparent mb-3">
          {userName ? `Hey ${userName}!` : 'Hey!'} Ready to Learn?
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300 max-w-md mx-auto">
          Your AI friend who explains things in the coolest way!
        </p>
      </motion.div>

      {/* Features tagline */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="flex flex-wrap items-center justify-center gap-2 mt-4 text-sm text-gray-500 dark:text-gray-400"
      >
        <span className="flex items-center gap-1">
          <span>🏏</span> Cricket analogies
        </span>
        <span className="text-gray-300 dark:text-gray-600">•</span>
        <span className="flex items-center gap-1">
          <span>🎯</span> Real examples
        </span>
        <span className="text-gray-300 dark:text-gray-600">•</span>
        <span className="flex items-center gap-1">
          <span>📝</span> Exam tips
        </span>
        <span className="text-gray-300 dark:text-gray-600">•</span>
        <span className="flex items-center gap-1">
          <span>🗣️</span> Hinglish!
        </span>
      </motion.div>

      {/* Quick Prompts */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="w-full max-w-2xl mt-10"
      >
        <p className="text-center text-sm font-medium text-gray-500 dark:text-gray-400 mb-4">
          Try asking something like...
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {defaultPrompts.map((prompt, index) => (
            <PromptCard
              key={index}
              text={typeof prompt === 'string' ? prompt : prompt.text}
              icon={typeof prompt === 'object' ? prompt.icon : BookOpen}
              gradient={typeof prompt === 'object' ? prompt.gradient : 'from-purple-500 to-pink-500'}
              onClick={onPromptClick}
              delay={0.6 + index * 0.1}
            />
          ))}
        </div>
      </motion.div>

      {/* Bottom hint */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="mt-8 text-center text-sm text-gray-400 dark:text-gray-500"
      >
        Ask anything - I'll explain it like a friend! 💪
      </motion.p>
    </div>
  );
}


