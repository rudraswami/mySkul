/**
 * Premium Welcome Screen - Sathi AI Tutor
 * A unique, student-attractive first impression
 * Features: Glassmorphism, animated gradients, engaging prompts
 */
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  Zap, 
  Target, 
  BookOpen,
  ArrowRight,
  Rocket,
  Brain,
  Trophy,
  MessageCircle,
  Lightbulb,
  GraduationCap,
  Star
} from 'lucide-react';

// Animated floating particles
const FloatingParticle = ({ delay, size, color, duration }) => (
  <motion.div
    className={`absolute rounded-full ${color} opacity-60`}
    style={{ width: size, height: size }}
    initial={{ 
      x: Math.random() * 100 - 50,
      y: Math.random() * 100,
      scale: 0 
    }}
    animate={{ 
      y: [0, -20, 0],
      x: [0, Math.random() * 20 - 10, 0],
      scale: [1, 1.2, 1],
      opacity: [0.3, 0.6, 0.3]
    }}
    transition={{ 
      duration: duration || 3,
      delay,
      repeat: Infinity,
      ease: "easeInOut"
    }}
  />
);

// Animated mascot with personality
const SathiMascot = () => {
  const [isHovered, setIsHovered] = useState(false);
  
  return (
    <motion.div
      initial={{ scale: 0, rotate: -180 }}
      animate={{ scale: 1, rotate: 0 }}
      transition={{ type: 'spring', duration: 0.8, bounce: 0.4 }}
      className="relative cursor-pointer"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Outer animated ring */}
      <motion.div
        className="absolute inset-0 rounded-3xl"
        style={{
          background: 'linear-gradient(135deg, #8B5CF6 0%, #EC4899 50%, #F97316 100%)',
          filter: 'blur(20px)',
          opacity: 0.4
        }}
        animate={{ 
          scale: [1, 1.15, 1],
          rotate: [0, 180, 360]
        }}
        transition={{ 
          duration: 8, 
          repeat: Infinity,
          ease: "linear"
        }}
      />
      
      {/* Secondary glow */}
      <motion.div
        className="absolute -inset-4 rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(139, 92, 246, 0.3) 0%, transparent 70%)'
        }}
        animate={{ scale: [1, 1.2, 1] }}
        transition={{ duration: 2, repeat: Infinity }}
      />
      
      {/* Main logo container */}
      <div className="relative w-20 h-20 sm:w-24 sm:h-24 md:w-28 md:h-28 rounded-2xl sm:rounded-3xl overflow-hidden shadow-2xl">
        {/* Animated gradient background */}
        <motion.div
          className="absolute inset-0"
          style={{
            background: 'linear-gradient(135deg, #8B5CF6 0%, #EC4899 50%, #F97316 100%)',
            backgroundSize: '200% 200%'
          }}
          animate={{
            backgroundPosition: ['0% 0%', '100% 100%', '0% 0%']
          }}
          transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
        />
        
        {/* Glass overlay */}
        <div className="absolute inset-0 bg-white/10 backdrop-blur-sm" />
        
        {/* Sparkles */}
        <motion.div
          animate={{ 
            rotate: [0, 360],
            scale: [1, 1.1, 1]
          }}
          transition={{ 
            duration: 20, 
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute inset-0 flex items-center justify-center"
        >
          <Sparkles className="w-6 h-6 text-white/40 absolute top-3 right-3" />
          <Sparkles className="w-4 h-4 text-white/30 absolute bottom-4 left-3" />
          <Star className="w-3 h-3 text-yellow-300/50 absolute top-5 left-5" />
        </motion.div>
        
        {/* Main emoji */}
        <div className="relative w-full h-full flex items-center justify-center">
          <motion.span 
            className="text-4xl sm:text-5xl md:text-6xl"
            animate={isHovered ? { scale: [1, 1.2, 1], rotate: [0, 10, -10, 0] } : {}}
            transition={{ duration: 0.5 }}
          >
            🤝
          </motion.span>
        </div>
      </div>
      
      {/* Online status */}
      <motion.div
        animate={{ scale: [1, 1.3, 1] }}
        transition={{ duration: 2, repeat: Infinity }}
        className="absolute -bottom-1 -right-1 w-7 h-7 bg-emerald-500 rounded-full border-4 border-white dark:border-gray-900 shadow-lg flex items-center justify-center"
      >
        <motion.div 
          className="w-2.5 h-2.5 bg-white rounded-full"
          animate={{ opacity: [1, 0.5, 1] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        />
      </motion.div>
    </motion.div>
  );
};

// Typing indicator for welcome text
const TypewriterText = ({ text, className, delay = 0 }) => {
  const [displayText, setDisplayText] = useState('');
  
  useEffect(() => {
    let i = 0;
    const timer = setTimeout(() => {
      const interval = setInterval(() => {
        if (i < text.length) {
          setDisplayText(text.slice(0, i + 1));
          i++;
        } else {
          clearInterval(interval);
        }
      }, 50);
      return () => clearInterval(interval);
    }, delay);
    return () => clearTimeout(timer);
  }, [text, delay]);
  
  return <span className={className}>{displayText}</span>;
};

// Quick prompt card with unique design
const PromptCard = ({ text, icon: Icon, gradient, accent, onClick, delay, index }) => (
  <motion.button
    initial={{ opacity: 0, y: 30, scale: 0.9 }}
    animate={{ opacity: 1, y: 0, scale: 1 }}
    transition={{ 
      delay, 
      duration: 0.4,
      type: "spring",
      stiffness: 100
    }}
    whileHover={{ 
      scale: 1.03, 
      y: -4,
      transition: { duration: 0.2 }
    }}
    whileTap={{ scale: 0.97 }}
    onClick={() => onClick?.(text)}
    className="group relative flex items-start gap-4 p-5 rounded-2xl text-left overflow-hidden transition-all duration-300"
    style={{
      background: 'rgba(255, 255, 255, 0.7)',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(255, 255, 255, 0.8)',
      boxShadow: '0 4px 24px -1px rgba(0, 0, 0, 0.05)'
    }}
  >
    {/* Hover gradient overlay */}
    <motion.div
      className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-300`}
    />
    
    {/* Accent line */}
    <motion.div
      className={`absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b ${gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-300`}
    />
    
    {/* Icon container */}
    <div className={`flex-shrink-0 w-12 h-12 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow duration-300`}>
      <Icon className="w-6 h-6 text-white" />
    </div>
    
    {/* Text content */}
    <div className="flex-1 min-w-0 pt-1">
      <p className="text-sm font-medium text-gray-700 dark:text-gray-200 leading-relaxed group-hover:text-gray-900 dark:group-hover:text-white transition-colors">
        {text}
      </p>
    </div>
    
    {/* Arrow indicator */}
    <motion.div
      className="flex-shrink-0 pt-1"
      initial={{ x: 0, opacity: 0.4 }}
      whileHover={{ x: 4, opacity: 1 }}
    >
      <ArrowRight className={`w-5 h-5 ${accent} group-hover:translate-x-1 transition-transform`} />
    </motion.div>
  </motion.button>
);

// Feature badge
const FeatureBadge = ({ icon, text, delay }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.8 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ delay, type: "spring" }}
    className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 shadow-sm"
  >
    <span className="text-sm">{icon}</span>
    <span className="text-xs font-medium text-gray-600 dark:text-gray-300">{text}</span>
  </motion.div>
);

export default function WelcomeScreen({ 
  onPromptClick, 
  prompts = [],
  userName = null 
}) {
  const [showSubtitle, setShowSubtitle] = useState(false);
  
  useEffect(() => {
    const timer = setTimeout(() => setShowSubtitle(true), 800);
    return () => clearTimeout(timer);
  }, []);

  // Unique prompts with personality
  const defaultPrompts = prompts.length > 0 ? prompts : [
    {
      text: "Explain the fundamental theorem of calculus",
      icon: BookOpen,
      gradient: "from-blue-500 to-cyan-500",
      accent: "text-blue-500"
    },
    {
      text: "What is the difference between permutations and combinations?",
      icon: Brain,
      gradient: "from-purple-500 to-pink-500",
      accent: "text-purple-500"
    },
    {
      text: "How do I solve quadratic equations in real-world problems?",
      icon: Target,
      gradient: "from-orange-500 to-red-500",
      accent: "text-orange-500"
    },
    {
      text: "Give me a JEE-level problem on integration by parts",
      icon: Trophy,
      gradient: "from-emerald-500 to-teal-500",
      accent: "text-emerald-500"
    }
  ];

  return (
    <div className="relative flex flex-col items-center justify-center min-h-[50vh] sm:min-h-[60vh] md:min-h-[70vh] px-4 py-6 sm:py-8 md:py-12 overflow-hidden">
      {/* Background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Gradient mesh background */}
        <div 
          className="absolute inset-0 opacity-30"
          style={{
            background: `
              radial-gradient(at 20% 20%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
              radial-gradient(at 80% 20%, rgba(236, 72, 153, 0.12) 0%, transparent 50%),
              radial-gradient(at 50% 80%, rgba(59, 130, 246, 0.1) 0%, transparent 50%)
            `
          }}
        />
        
        {/* Floating particles */}
        <div className="absolute top-20 left-[15%]">
          <FloatingParticle delay={0} size={8} color="bg-purple-400" duration={4} />
        </div>
        <div className="absolute top-32 right-[20%]">
          <FloatingParticle delay={1} size={6} color="bg-pink-400" duration={3.5} />
        </div>
        <div className="absolute top-48 left-[25%]">
          <FloatingParticle delay={0.5} size={10} color="bg-blue-400" duration={4.5} />
        </div>
        <div className="absolute bottom-32 right-[30%]">
          <FloatingParticle delay={1.5} size={7} color="bg-orange-400" duration={3} />
        </div>
        <div className="absolute bottom-48 left-[10%]">
          <FloatingParticle delay={2} size={5} color="bg-emerald-400" duration={5} />
        </div>
      </div>
      
      {/* Content */}
      <div className="relative z-10 flex flex-col items-center">
        {/* Mascot */}
        <SathiMascot />
        
        {/* Main heading */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="mt-6 sm:mt-8 md:mt-10 text-center"
        >
          <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl font-bold tracking-tight">
            <span className="bg-gradient-to-r from-purple-600 via-pink-500 to-orange-500 bg-clip-text text-transparent">
              {userName ? `Hey ${userName}!` : 'Hey!'} Ready to Learn?
            </span>
            <motion.span 
              className="inline-block ml-2"
              animate={{ rotate: [0, 14, -8, 14, 0] }}
              transition={{ duration: 1.5, repeat: Infinity, repeatDelay: 3 }}
            >
              💪
            </motion.span>
          </h1>
          
          <AnimatePresence>
            {showSubtitle && (
              <motion.p
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4 }}
                className="mt-3 sm:mt-4 text-sm sm:text-base md:text-lg lg:text-xl text-gray-600 dark:text-gray-300 max-w-lg mx-auto font-medium px-2"
              >
                Your AI friend who explains things in the coolest way!
              </motion.p>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Feature badges */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="flex flex-wrap items-center justify-center gap-1.5 sm:gap-2 mt-4 sm:mt-6 px-2"
        >
          <FeatureBadge icon="🏏" text="Cricket analogies" delay={0.7} />
          <FeatureBadge icon="🎯" text="Real examples" delay={0.8} />
          <FeatureBadge icon="📝" text="Exam tips" delay={0.9} />
          <FeatureBadge icon="🗣️" text="Hinglish!" delay={1.0} />
        </motion.div>

        {/* Quick prompts */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="w-full max-w-2xl mt-6 sm:mt-8 md:mt-12 px-2"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {defaultPrompts.map((prompt, index) => (
              <PromptCard
                key={index}
                text={typeof prompt === 'string' ? prompt : prompt.text}
                icon={typeof prompt === 'object' ? prompt.icon : BookOpen}
                gradient={typeof prompt === 'object' ? prompt.gradient : 'from-purple-500 to-pink-500'}
                accent={typeof prompt === 'object' ? prompt.accent : 'text-purple-500'}
                onClick={onPromptClick}
                delay={0.9 + index * 0.1}
                index={index}
              />
            ))}
          </div>
        </motion.div>

        {/* Bottom hint with personality */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.3 }}
          className="mt-6 sm:mt-8 md:mt-10 text-center"
        >
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Ask anything - I'll explain it like a friend! 
            <motion.span 
              className="inline-block ml-1"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 2 }}
            >
              💪
            </motion.span>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
