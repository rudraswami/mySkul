/**
 * PremiumWelcome - Emotionally Intelligent AI Mentor Interface
 * DRON AI's signature welcome experience - warm, supportive, student-first
 * 
 * Design Philosophy: "Someone smart, calm, and supportive is sitting next to the student"
 */
import React, { useState, useMemo, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  Brain, 
  BookOpen, 
  Calculator, 
  FlaskConical,
  Globe,
  Code,
  Lightbulb,
  Rocket,
  Target,
  Clock,
  TrendingUp,
  Zap,
  MessageCircle,
  HelpCircle,
  FileText,
  Mic,
  Camera,
  Eye,
  Send,
  Image,
  CheckCircle2,
  Heart,
  Shield,
  Info,
  RotateCw,
  Trophy,
  ArrowRight,
  Sparkle
} from 'lucide-react';

// Mode-specific mood colors for background
const MOOD_COLORS = {
  conceptual: { primary: 'rgba(99, 102, 241, 0.15)', warm: 'rgba(251, 191, 36, 0.08)' }, // Calm
  practice: { primary: 'rgba(99, 102, 241, 0.12)', warm: 'rgba(251, 191, 36, 0.05)' }, // Neutral
  exam: { primary: 'rgba(139, 92, 246, 0.18)', warm: 'rgba(245, 158, 11, 0.1)' }, // Focused
  doubt: { primary: 'rgba(245, 158, 11, 0.12)', warm: 'rgba(251, 191, 36, 0.15)' } // Warm & reassuring
};

// Neural Background with mood-aware warmth and mentor zone
const NeuralBackground = ({ mood = 'conceptual' }) => {
  const moodStyle = MOOD_COLORS[mood] || MOOD_COLORS.conceptual;
  
  return (
    <div className="sathi-neural-container">
      <motion.div 
        className="sathi-neural-mesh"
        animate={{ 
          background: `radial-gradient(ellipse at 50% 30%, ${moodStyle.primary} 0%, transparent 60%)`
        }}
        transition={{ duration: 1.5, ease: "easeInOut" }}
      />
      <motion.div 
        className="sathi-warm-glow"
        animate={{ 
          background: `radial-gradient(ellipse at 50% 40%, ${moodStyle.warm} 0%, transparent 50%)`
        }}
        transition={{ duration: 1.5, ease: "easeInOut" }}
      />
      {/* Warm Mentor Zone - focused glow around AI presence, headline, input */}
      <div className="sathi-mentor-zone" />
      <div className="sathi-grid-overlay" />
      {/* Subtle ambient noise texture */}
      <div className="sathi-ambient-noise" />
    </div>
  );
};

// Floating Particles - softer, mood-responsive
const FloatingParticles = ({ mood = 'conceptual' }) => {
  const particleCount = mood === 'doubt' ? 10 : 7; // More particles in doubt mode for warmth
  
  return (
    <div className="sathi-particles">
      {[...Array(particleCount)].map((_, i) => (
        <div 
          key={i} 
          className={`sathi-particle ${mood === 'doubt' ? 'sathi-particle-warm' : (i % 3 === 0 ? 'sathi-particle-warm' : 'sathi-particle-cool')}`} 
        />
      ))}
    </div>
  );
};

// AI Mentor Presence - State-aware animations
// States: idle (soft glow), listening (pulse), thinking (rotation), explaining (ripple)
const MentorPresence = ({ aiState = 'idle' }) => {
  // State-specific animation configurations
  const stateAnimations = {
    idle: {
      glow: { scale: [1, 1.1, 1], opacity: [0.3, 0.5, 0.3] },
      glowTransition: { duration: 4, repeat: Infinity, ease: "easeInOut" },
      orbit: { rotate: 360 },
      orbitTransition: { duration: 30, repeat: Infinity, ease: "linear" }
    },
    listening: {
      glow: { scale: [1, 1.2, 1], opacity: [0.4, 0.7, 0.4] },
      glowTransition: { duration: 1.5, repeat: Infinity, ease: "easeInOut" },
      orbit: { rotate: 360 },
      orbitTransition: { duration: 8, repeat: Infinity, ease: "linear" }
    },
    thinking: {
      glow: { scale: [1, 1.15, 1], opacity: [0.5, 0.7, 0.5] },
      glowTransition: { duration: 2, repeat: Infinity, ease: "easeInOut" },
      orbit: { rotate: 360 },
      orbitTransition: { duration: 3, repeat: Infinity, ease: "linear" }
    },
    explaining: {
      glow: { scale: [1, 1.25, 1.1, 1.2, 1], opacity: [0.4, 0.6, 0.5, 0.6, 0.4] },
      glowTransition: { duration: 2.5, repeat: Infinity, ease: "easeOut" },
      orbit: { rotate: 360 },
      orbitTransition: { duration: 15, repeat: Infinity, ease: "linear" }
    }
  };
  
  const anim = stateAnimations[aiState] || stateAnimations.idle;
  
  // Status text based on state
  const statusText = {
    idle: 'Ready to help',
    listening: 'Listening...',
    thinking: 'Thinking...',
    explaining: 'Explaining'
  };

  return (
    <motion.div 
      className="sathi-mentor-presence"
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
    >
      {/* Outer breathing glow - state responsive */}
      <motion.div 
        className={`sathi-mentor-glow sathi-mentor-glow-${aiState}`}
        animate={anim.glow}
        transition={anim.glowTransition}
      />
      
      {/* Ripple effect for explaining state */}
      {aiState === 'explaining' && (
        <>
          <motion.div 
            className="sathi-mentor-ripple"
            animate={{ scale: [1, 2], opacity: [0.3, 0] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "easeOut" }}
          />
          <motion.div 
            className="sathi-mentor-ripple"
            animate={{ scale: [1, 2], opacity: [0.3, 0] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "easeOut", delay: 0.5 }}
          />
        </>
      )}
      
      {/* Inner warm core */}
      <div className="sathi-mentor-core">
        <motion.div
          animate={anim.orbit}
          transition={anim.orbitTransition}
          className="sathi-mentor-orbit"
        >
          <div className="sathi-orbit-dot" />
        </motion.div>
        
        {/* Mentor icon - friendly, not robotic */}
        <div className="sathi-mentor-face">
          <motion.span 
            className="sathi-mentor-emoji"
            animate={aiState === 'thinking' ? { rotate: [0, 5, -5, 0] } : {}}
            transition={{ duration: 0.5, repeat: aiState === 'thinking' ? Infinity : 0 }}
          >
            🤝
          </motion.span>
        </div>
      </div>
      
      {/* Active indicator with state text */}
      <motion.div 
        className={`sathi-mentor-active sathi-mentor-active-${aiState}`}
        animate={{ scale: aiState === 'listening' ? [1, 1.3, 1] : [1, 1.2, 1] }}
        transition={{ duration: aiState === 'listening' ? 1 : 2, repeat: Infinity }}
      />
      
      {/* Status text */}
      <motion.div 
        className="sathi-mentor-status"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        {statusText[aiState]}
      </motion.div>
    </motion.div>
  );
};

// Capability Indicators - Clean single-row, no dots, border glow for active
const CapabilityIndicators = ({ capabilities, onToggle }) => {
  const [hoveredCap, setHoveredCap] = useState(null);
  
  const capabilityConfig = [
    { 
      id: 'exam', 
      icon: '🎯', 
      label: 'Exam-focused', 
      tooltip: 'Answers optimized for exam patterns and scoring',
      defaultOn: true 
    },
    { 
      id: 'visual', 
      icon: '🖼️', 
      label: 'Visual explanations', 
      tooltip: 'Include diagrams and visual aids when helpful',
      defaultOn: true 
    },
    { 
      id: 'hinglish', 
      icon: '🗣️', 
      label: 'Hinglish support', 
      tooltip: 'Mix Hindi and English for easier understanding',
      defaultOn: false 
    },
    { 
      id: 'adaptive', 
      icon: '🧠', 
      label: 'Adapts to you', 
      tooltip: 'Learns your pace and adjusts explanations',
      defaultOn: true 
    },
    { 
      id: 'cognitive', 
      icon: '🪞', 
      label: 'Cognitive Mirror', 
      tooltip: 'I adapt based on your confusion or confidence',
      defaultOn: true,
      special: true 
    }
  ];
  
  const [activeCapabilities, setActiveCapabilities] = useState(() => {
    const initial = {};
    capabilityConfig.forEach(cap => {
      initial[cap.id] = capabilities?.[cap.id] ?? cap.defaultOn;
    });
    return initial;
  });
  
  const handleToggle = (capId) => {
    setActiveCapabilities(prev => {
      const newState = { ...prev, [capId]: !prev[capId] };
      onToggle?.(newState);
      return newState;
    });
  };
  
  return (
    <motion.div 
      className="sathi-capabilities-container"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.6 }}
    >
      <div className="sathi-capabilities-row">
        {capabilityConfig.map((cap, i) => (
          <motion.button 
            key={cap.id}
            className={`sathi-capability-tag-clean ${activeCapabilities[cap.id] ? 'active' : ''} ${cap.special ? 'special' : ''}`}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.65 + i * 0.05 }}
            onClick={() => handleToggle(cap.id)}
            onMouseEnter={() => setHoveredCap(cap.id)}
            onMouseLeave={() => setHoveredCap(null)}
          >
            <span className="sathi-cap-icon">{cap.icon}</span>
            <span className="sathi-cap-label">{cap.label}</span>
            
            {/* Tooltip */}
            <AnimatePresence>
              {hoveredCap === cap.id && (
                <motion.div 
                  className="sathi-cap-tooltip"
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 5 }}
                >
                  {cap.tooltip}
                </motion.div>
              )}
            </AnimatePresence>
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
};

// Learning Mode Selector - Primary control with micro-descriptions
const LearningModeSelector = ({ activeMode, onModeChange }) => {
  const modes = [
    { 
      id: 'conceptual', 
      label: 'Concepts', 
      icon: Brain,
      microDesc: 'Slow & clear explanations',
      color: 'indigo'
    },
    { 
      id: 'practice', 
      label: 'Practice', 
      icon: Target,
      microDesc: 'Step-by-step problem solving',
      color: 'emerald'
    },
    { 
      id: 'exam', 
      label: 'Exam Prep', 
      icon: FileText,
      microDesc: 'Time-optimized answers',
      color: 'amber'
    },
    { 
      id: 'doubt', 
      label: 'Doubts', 
      icon: HelpCircle,
      microDesc: 'Patient, detailed clarity',
      color: 'rose'
    },
  ];

  const selectedMode = modes.find(m => m.id === activeMode);

  return (
    <div className="sathi-mode-selector-wrapper">
      <div className="sathi-mode-selector">
        {modes.map((mode) => (
          <motion.button
            key={mode.id}
            className={`sathi-mode-chip sathi-mode-${mode.color} ${activeMode === mode.id ? 'active' : ''}`}
            onClick={() => onModeChange(mode.id)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <mode.icon size={16} />
            <span>{mode.label}</span>
          </motion.button>
        ))}
      </div>
      
      {/* Micro-description for selected mode */}
      <AnimatePresence mode="wait">
        <motion.div 
          key={activeMode}
          className="sathi-mode-description"
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 5 }}
          transition={{ duration: 0.2 }}
        >
          <span className="sathi-mode-desc-icon">→</span>
          <span>{selectedMode?.microDesc}</span>
        </motion.div>
      </AnimatePresence>
      
      {/* Exam prep session hint */}
      {activeMode === 'exam' && (
        <motion.div 
          className="sathi-session-hint"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <span className="sathi-hint-flow">Concept → Practice → Recap</span>
        </motion.div>
      )}
    </div>
  );
};

// Topic Card Component - Enhanced with variants
const TopicCard = ({ icon: Icon, title, description, onClick, variant = 'default', badge }) => (
  <motion.button
    className={`sathi-topic-card sathi-card-${variant}`}
    onClick={onClick}
    whileHover={{ scale: 1.02, y: -2 }}
    whileTap={{ scale: 0.98 }}
  >
    {badge && <span className="sathi-card-badge">{badge}</span>}
    <div className={`sathi-topic-icon sathi-icon-${variant}`}>
      <Icon size={20} />
    </div>
    <div className="sathi-topic-content">
      <div className="sathi-topic-title">{title}</div>
      <div className="sathi-topic-desc">{description}</div>
    </div>
    {variant === 'continue' && (
      <div className="sathi-card-arrow">
        <ArrowRight size={16} />
      </div>
    )}
  </motion.button>
);

// Smart Cards - Continue & Quick Win
const SmartCards = ({ onSendMessage }) => (
  <div className="sathi-smart-cards">
    <TopicCard
      icon={RotateCw}
      title="Continue where you left off"
      description="Pick up from your last session"
      onClick={() => onSendMessage?.('Continue from where we left off')}
      variant="continue"
    />
    <TopicCard
      icon={Trophy}
      title="Quick confidence booster"
      description="A small win to build momentum"
      onClick={() => onSendMessage?.('Give me a quick confidence booster - something I can solve easily')}
      variant="quickwin"
      badge="⚡ Quick Win"
    />
  </div>
);

// Mentor Reassurance - Emotional micro-copy
const MentorReassurance = () => {
  const reassurances = [
    { icon: Heart, text: "No question is too simple. I'm here to help you understand." },
    { icon: Shield, text: "This is a safe space. Take your time, ask anything." },
    { icon: CheckCircle2, text: "I explain until it clicks. No judgment, just learning." }
  ];
  
  const [current, setCurrent] = useState(0);
  
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrent(prev => (prev + 1) % reassurances.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);
  
  return (
    <motion.div className="sathi-reassurance">
      <AnimatePresence mode="wait">
        <motion.div
          key={current}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="sathi-reassurance-content"
        >
          {React.createElement(reassurances[current].icon, { size: 14, className: "sathi-reassurance-icon" })}
          <span>{reassurances[current].text}</span>
        </motion.div>
      </AnimatePresence>
    </motion.div>
  );
};

// Intelligent Input Bar with rotating placeholders
const IntelligentInput = ({ onSend, inputValue, setInputValue }) => {
  const placeholders = [
    "What's confusing you today?",
    "Ask me anything — I'll explain like a friend",
    "Stuck on a problem? Let's solve it together",
    "Need a concept explained? I'm all ears",
    "Type your doubt... no question is silly"
  ];
  
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  
  useEffect(() => {
    const timer = setInterval(() => {
      setPlaceholderIndex(prev => (prev + 1) % placeholders.length);
    }, 4000);
    return () => clearInterval(timer);
  }, []);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && onSend) {
      onSend(inputValue);
      setInputValue('');
    }
  };
  
  return (
    <motion.div 
      className="sathi-input-wrapper"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
    >
      <div className="sathi-input-glow" />
      <form onSubmit={handleSubmit} className="sathi-input-container">
        <input
          type="text"
          className="sathi-input-field"
          placeholder={placeholders[placeholderIndex]}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
        />
        <div className="sathi-input-actions">
          <button type="button" className="sathi-input-btn sathi-input-hint" title="Visual explanation">
            <Eye size={18} />
          </button>
          <button 
            type="submit" 
            className="sathi-input-btn sathi-send-btn"
            disabled={!inputValue.trim()}
          >
            <Send size={18} />
          </button>
        </div>
      </form>
    </motion.div>
  );
};

// Quick Action Button - Enhanced
const QuickAction = ({ icon: Icon, label, onClick, subtle }) => (
  <button className={`sathi-quick-action ${subtle ? 'sathi-quick-subtle' : ''}`} onClick={onClick}>
    <Icon size={14} />
    {label}
  </button>
);

// Main Premium Welcome Component - Emotionally Intelligent
const PremiumWelcome = ({ onSendMessage, userProfile }) => {
  const [activeMode, setActiveMode] = useState('conceptual');
  const [inputValue, setInputValue] = useState('');
  
  // Emotionally intelligent, context-aware greeting
  const greetingData = useMemo(() => {
    const hour = new Date().getHours();
    const day = new Date().getDay();
    const isWeekend = day === 0 || day === 6;
    
    // Time-based greeting with emotional context
    let greeting, subtext;
    
    if (hour >= 5 && hour < 12) {
      greeting = 'Good morning';
      subtext = isWeekend 
        ? "Weekend study session? That's dedication 💪" 
        : "Fresh mind, ready to learn something new?";
    } else if (hour >= 12 && hour < 17) {
      greeting = 'Good afternoon';
      subtext = "Let's make this session productive";
    } else if (hour >= 17 && hour < 21) {
      greeting = 'Good evening';
      subtext = "Perfect time for some revision";
    } else {
      greeting = 'Hey';
      subtext = "Late night study? I'm here with you";
    }
    
    return { greeting, subtext };
  }, []);

  // Get user's first name with fallback
  const firstName = useMemo(() => {
    if (userProfile?.name) {
      return userProfile.name.split(' ')[0];
    }
    return null;
  }, [userProfile]);
  
  // Personalized title based on context
  const titleMessage = useMemo(() => {
    const messages = [
      "What's on your mind?",
      "What would you like to explore?",
      "Ready to learn something new?",
      "What can I help you understand?"
    ];
    return messages[Math.floor(Math.random() * messages.length)];
  }, []);

  // Smart suggestions based on time and mode
  const suggestions = useMemo(() => {
    const baseSuggestions = {
      conceptual: [
        {
          icon: Calculator,
          title: 'Explain calculus intuitively',
          description: 'Derivatives, integrals with real examples'
        },
        {
          icon: FlaskConical,
          title: 'Chemistry made simple',
          description: 'Organic reactions step by step'
        },
        {
          icon: Globe,
          title: 'Physics fundamentals',
          description: 'Mechanics, waves, thermodynamics'
        },
        {
          icon: Code,
          title: 'Programming concepts',
          description: 'Data structures and algorithms'
        }
      ],
      practice: [
        {
          icon: Target,
          title: 'JEE level problems',
          description: 'Challenging practice questions'
        },
        {
          icon: Calculator,
          title: 'Numerical practice',
          description: 'Step-by-step problem solving'
        },
        {
          icon: BookOpen,
          title: 'Previous year questions',
          description: 'CBSE, JEE, NEET papers'
        },
        {
          icon: Lightbulb,
          title: 'Quick quiz mode',
          description: 'Test your understanding'
        }
      ],
      exam: [
        {
          icon: Clock,
          title: 'Time management tips',
          description: 'Maximize your exam performance'
        },
        {
          icon: FileText,
          title: 'Important formulas',
          description: 'Quick revision sheets'
        },
        {
          icon: TrendingUp,
          title: 'High-yield topics',
          description: 'Focus areas for scoring'
        },
        {
          icon: Rocket,
          title: 'Last minute revision',
          description: 'Key points to remember'
        }
      ],
      doubt: [
        {
          icon: HelpCircle,
          title: 'Clear any concept',
          description: 'Ask anything, get clarity'
        },
        {
          icon: MessageCircle,
          title: 'Step-by-step solutions',
          description: 'Detailed explanations'
        },
        {
          icon: Brain,
          title: 'Why does this work?',
          description: 'Deep understanding'
        },
        {
          icon: Lightbulb,
          title: 'Alternative methods',
          description: 'Different approaches to solve'
        }
      ]
    };
    
    return baseSuggestions[activeMode] || baseSuggestions.conceptual;
  }, [activeMode]);

  const handleTopicClick = useCallback((title) => {
    if (onSendMessage) {
      onSendMessage(title);
    }
  }, [onSendMessage]);

  const handleQuickAction = useCallback((action) => {
    const quickMessages = {
      'continue': 'Continue from where we left off',
      'revision': 'Help me revise what I learned today',
      'test': 'Give me a quick test on recent topics'
    };
    if (onSendMessage && quickMessages[action]) {
      onSendMessage(quickMessages[action]);
    }
  }, [onSendMessage]);

  // Gen Z friendly reassurance messages - dynamic based on time
  const reassuranceMessages = useMemo(() => {
    const hour = new Date().getHours();
    const isLateNight = hour >= 22 || hour < 6;
    
    const baseMessages = [
      "Stuck? That's literally how learning works.",
      "No dumb questions. Only dumb textbooks.",
      "Your teacher explains it once. I'll explain it 100 ways.",
      "Confusion is temporary. Understanding is forever."
    ];
    
    if (isLateNight) {
      return [
        "Late night grind? I respect the hustle. 💪",
        "Sleep is important, but so is clearing doubts.",
        "Quick question before bed? Let's do it.",
        ...baseMessages
      ];
    }
    
    return [
      ...baseMessages,
      "Take your time. I'm not going anywhere.",
      "Every expert was once a confused student."
    ];
  }, []);
  
  const [reassuranceIndex, setReassuranceIndex] = useState(0);
  
  useEffect(() => {
    const timer = setInterval(() => {
      setReassuranceIndex(prev => (prev + 1) % reassuranceMessages.length);
    }, 5000);
    return () => clearInterval(timer);
  }, [reassuranceMessages.length]);
  
  // Dynamic placeholder that cycles - context-aware
  const placeholders = useMemo(() => {
    const hour = new Date().getHours();
    const isLateNight = hour >= 22 || hour < 6;
    const isMorning = hour >= 6 && hour < 12;
    
    const basePlaceholders = [
      "Why does this formula even exist?",
      "Explain like I'm 5...",
      "Solve this step by step...",
      "What's the trick to remember this?"
    ];
    
    if (isLateNight) {
      return [
        "One quick doubt before I sleep...",
        "Just need to understand this part...",
        ...basePlaceholders
      ];
    } else if (isMorning) {
      return [
        "Let's start fresh! What should I focus on?",
        "Help me understand yesterday's topic better",
        ...basePlaceholders
      ];
    }
    
    return [
      ...basePlaceholders,
      "Quick revision for tomorrow's test",
      "I keep forgetting this concept..."
    ];
  }, []);
  
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  
  useEffect(() => {
    const timer = setInterval(() => {
      setPlaceholderIndex(prev => (prev + 1) % placeholders.length);
    }, 3000);
    return () => clearInterval(timer);
  }, [placeholders.length]);
  
  // Smart greeting based on time and context
  const getSmartGreeting = () => {
    const hour = new Date().getHours();
    const name = firstName ? `, ${firstName}` : '';
    
    if (hour >= 22 || hour < 5) {
      return { line1: `Late night grind${name}?`, line2: "Let's make it count." };
    } else if (hour >= 5 && hour < 12) {
      return { line1: `Morning${name}!`, line2: "Fresh mind = faster learning." };
    } else if (hour >= 12 && hour < 17) {
      return { line1: `Hey${name}!`, line2: "Ready when you are." };
    } else {
      return { line1: `Evening${name}!`, line2: "Let's clear some doubts." };
    }
  };
  
  const smartGreeting = getSmartGreeting();
  
  // Quick action buttons - what students actually need (dynamic based on context)
  const quickActions = useMemo(() => {
    const hour = new Date().getHours();
    const isLateNight = hour >= 22 || hour < 6;
    const isMorning = hour >= 6 && hour < 12;
    
    // Context-aware actions
    const baseActions = [
      { icon: Zap, label: "Quiz me", action: "Give me a quick quiz on my last topic" },
      { icon: Camera, label: "Solve from photo", action: "I'll describe a problem from my textbook" },
    ];
    
    if (isLateNight) {
      // Late night = quick revision, not long sessions
      return [
        ...baseActions,
        { icon: Target, label: "Quick revision", action: "Help me revise one topic quickly before sleep" },
        { icon: Sparkles, label: "Key points only", action: "Give me just the key points, I'm tired" }
      ];
    } else if (isMorning) {
      // Morning = fresh start
      return [
        ...baseActions,
        { icon: Target, label: "Fresh start", action: "What should I study today?" },
        { icon: Sparkles, label: "Explain simply", action: "Explain the concept I'm stuck on in simple terms" }
      ];
    } else {
      // Default
      return [
        ...baseActions,
        { icon: Target, label: "Last-minute tips", action: "Quick revision tips for exam tomorrow" },
        { icon: Sparkles, label: "Explain simply", action: "Explain the concept I'm stuck on in simple terms" }
      ];
    }
  }, []);
  
  // Trust badges - what makes Sathi special (dynamic tooltips)
  const trustBadges = useMemo(() => [
    { 
      id: 'exam', 
      icon: BookOpen, 
      label: 'Exam-focused', 
      tooltip: 'Every answer is optimized for how exams ask questions',
      special: false 
    },
    { 
      id: 'visual', 
      icon: Eye, 
      label: 'Visual explanations', 
      tooltip: 'Diagrams and step-by-step visuals when you need them',
      special: false 
    },
    { 
      id: 'adaptive', 
      icon: Brain, 
      label: 'Adapts to you', 
      tooltip: 'I learn how you learn and adjust my explanations',
      special: false 
    },
    { 
      id: 'safe', 
      icon: Sparkles, 
      label: 'No judgment zone', 
      tooltip: 'Ask anything - there are no stupid questions here',
      special: true 
    }
  ], []);

  return (
    <>
      <NeuralBackground mood={activeMode} />
      <FloatingParticles mood={activeMode} />
      
      <div className="sathi-welcome-wrapper sathi-clean-welcome">
        <motion.div 
          className="sathi-welcome-content sathi-hero-layout"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          
          {/* ===== HERO ZONE: Mentor + Greeting + Input ===== */}
          <div className="sathi-hero-zone">
            
            {/* Animated AI Avatar - Not boring emoji */}
            <motion.div 
              className="sathi-ai-avatar"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.6, ease: "easeOut" }}
            >
              <div className="sathi-avatar-core">
                <motion.div 
                  className="sathi-avatar-ring sathi-ring-1"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                />
                <motion.div 
                  className="sathi-avatar-ring sathi-ring-2"
                  animate={{ rotate: -360 }}
                  transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
                />
                <div className="sathi-avatar-face">
                  <motion.div
                    className="sathi-avatar-emoji"
                    animate={{ scale: [1, 1.05, 1] }}
                    transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                  >
                    🧠
                  </motion.div>
                </div>
              </div>
              <motion.div 
                className="sathi-avatar-glow"
                animate={{ opacity: [0.3, 0.6, 0.3], scale: [1, 1.1, 1] }}
                transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
              />
            </motion.div>
            
            {/* Smart Greeting */}
            <motion.div 
              className="sathi-smart-greeting"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <div className="sathi-greeting-line1">{smartGreeting.line1}</div>
              <div className="sathi-greeting-line2">{smartGreeting.line2}</div>
            </motion.div>
            
            {/* THE Hero Input - Center Stage */}
            <motion.div 
              className="sathi-hero-input-wrapper"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <div className="sathi-hero-input-glow" />
              <form 
                onSubmit={(e) => {
                  e.preventDefault();
                  if (inputValue.trim() && onSendMessage) {
                    onSendMessage(inputValue);
                    setInputValue('');
                  }
                }} 
                className="sathi-hero-input-container"
              >
                <input
                  type="text"
                  className="sathi-hero-input"
                  placeholder={placeholders[placeholderIndex]}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  autoFocus
                />
                <div className="sathi-input-actions">
                  <button 
                    type="button" 
                    className="sathi-voice-btn"
                    title="Voice input coming soon"
                  >
                    <Mic size={18} />
                  </button>
                  <button 
                    type="submit" 
                    className="sathi-hero-send"
                    disabled={!inputValue.trim()}
                  >
                    <Send size={18} />
                  </button>
                </div>
              </form>
            </motion.div>
            
            {/* Rotating Reassurance - Gen Z tone */}
            <motion.div 
              className="sathi-hero-reassurance"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7 }}
            >
              <AnimatePresence mode="wait">
                <motion.span
                  key={reassuranceIndex}
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -5 }}
                  transition={{ duration: 0.3 }}
                >
                  {reassuranceMessages[reassuranceIndex]}
                </motion.span>
              </AnimatePresence>
            </motion.div>
          </div>
          
          {/* ===== QUICK ACTIONS: What students actually need ===== */}
          <motion.div 
            className="sathi-quick-actions"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.9 }}
          >
            {quickActions.map((action, index) => (
              <motion.button
                key={index}
                className="sathi-quick-action-btn"
                onClick={() => {
                  setInputValue(action.action);
                  if (onSendMessage) onSendMessage(action.action);
                }}
                whileHover={{ scale: 1.05, y: -3 }}
                whileTap={{ scale: 0.95 }}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.9 + index * 0.1 }}
              >
                <action.icon size={18} />
                <span>{action.label}</span>
              </motion.button>
            ))}
          </motion.div>
          
          {/* ===== SMART SUGGESTIONS: Based on learning mode ===== */}
          <motion.div 
            className="sathi-suggestion-zone"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.1 }}
          >
            <div className="sathi-suggestion-label">or try these...</div>
            <div className="sathi-suggestion-chips">
              {suggestions.slice(0, 4).map((topic, index) => (
                <motion.button
                  key={`${activeMode}-${index}`}
                  className="sathi-suggestion-chip"
                  onClick={() => handleTopicClick(topic.title)}
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.2 + index * 0.1 }}
                >
                  <topic.icon size={16} />
                  <span>{topic.title}</span>
                </motion.button>
              ))}
            </div>
          </motion.div>
          
          {/* ===== TRUST BADGES: Why Sathi is different - Dynamic ===== */}
          <motion.div 
            className="sathi-trust-badges"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.4 }}
          >
            {trustBadges.map((badge, index) => (
              <motion.div 
                key={badge.id}
                className={`sathi-badge ${badge.special ? 'sathi-badge-special' : ''}`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.4 + index * 0.1 }}
                title={badge.tooltip}
              >
                <badge.icon size={16} />
                <span>{badge.label}</span>
              </motion.div>
            ))}
          </motion.div>
          
        </motion.div>
      </div>
    </>
  );
};

export default PremiumWelcome;

