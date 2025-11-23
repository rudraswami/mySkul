/**
 * Premium Streaming Response - Student-Centric Design
 * Large text, short chunks, animated sections, visual hierarchy
 * Feels like a real-time teacher, not a static textbook
 */
import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, BookOpen, Lightbulb, AlertTriangle, Clock, 
  CheckCircle, TrendingUp, Zap, Target, Brain, Award
} from 'lucide-react';

export default function PremiumStreamingResponse({ 
  message, 
  sessionId, 
  subject = "General",
  onComplete 
}) {
  const [sections, setSections] = useState({});
  const [currentSection, setCurrentSection] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingStyle, setStreamingStyle] = useState(null);
  
  // Section types with their visual configs
  const sectionConfigs = {
    greeting: {
      icon: Sparkles,
      color: 'purple',
      bgGradient: 'from-purple-50 to-pink-50',
      borderColor: 'border-purple-300',
      textColor: 'text-purple-900',
      iconColor: 'text-purple-600'
    },
    summary: {
      icon: Target,
      color: 'blue',
      bgGradient: 'from-blue-50 to-cyan-50',
      borderColor: 'border-blue-300',
      textColor: 'text-blue-900',
      iconColor: 'text-blue-600',
      title: '🎯 Quick Summary'
    },
    formula: {
      icon: Brain,
      color: 'indigo',
      bgGradient: 'from-indigo-50 to-purple-50',
      borderColor: 'border-indigo-300',
      textColor: 'text-indigo-900',
      iconColor: 'text-indigo-600',
      title: '📐 Key Formula'
    },
    example: {
      icon: BookOpen,
      color: 'green',
      bgGradient: 'from-green-50 to-emerald-50',
      borderColor: 'border-green-300',
      textColor: 'text-green-900',
      iconColor: 'text-green-600',
      title: '💡 Example'
    },
    mistakes: {
      icon: AlertTriangle,
      color: 'orange',
      bgGradient: 'from-orange-50 to-yellow-50',
      borderColor: 'border-orange-300',
      textColor: 'text-orange-900',
      iconColor: 'text-orange-600',
      title: '⚠️ Common Mistakes'
    },
    exam_tip: {
      icon: Award,
      color: 'red',
      bgGradient: 'from-red-50 to-pink-50',
      borderColor: 'border-red-300',
      textColor: 'text-red-900',
      iconColor: 'text-red-600',
      title: '🎯 Exam Tip'
    },
    quick_revision: {
      icon: Clock,
      color: 'yellow',
      bgGradient: 'from-yellow-50 to-amber-50',
      borderColor: 'border-yellow-300',
      textColor: 'text-yellow-900',
      iconColor: 'text-yellow-600',
      title: '⚡ Quick Revision'
    },
    main: {
      icon: BookOpen,
      color: 'gray',
      bgGradient: 'from-gray-50 to-slate-50',
      borderColor: 'border-gray-300',
      textColor: 'text-gray-900',
      iconColor: 'text-gray-600'
    }
  };

  useEffect(() => {
    startStreaming();
    
    return () => {
      // Cleanup
    };
  }, [message]);

  const startStreaming = async () => {
    setIsStreaming(true);
    
    // Simulate streaming (replace with actual API call)
    await simulateStream();
    
    setIsStreaming(false);
    if (onComplete) onComplete();
  };

  const simulateStream = async () => {
    // Greeting
    await streamSection('greeting', 'Alright! Let me break this down for you... 🔥', 100);
    
    // Summary
    await streamSection('summary', 
      'Force is the push or pull that makes things move or stop. Think of it like pushing a cart in a market - the harder you push, the faster it goes!',
      200
    );
    
    // Formula
    await streamSection('formula',
      '**Force = Mass × Acceleration**\n\nOr simply: **F = ma**\n\nWhere:\n• F = Force (in Newtons)\n• m = Mass (in kg)\n• a = Acceleration (in m/s²)',
      300
    );
    
    // Example
    await streamSection('example',
      '**Indian Street Market Scene:**\n\nRaju is pushing his vegetable cart (mass = 50 kg).\n\nTo accelerate it from rest to 2 m/s²:\n\n**F = 50 kg × 2 m/s² = 100 N**\n\nSo Raju needs to apply 100 Newtons of force!',
      400
    );
    
    // Mistakes
    await streamSection('mistakes',
      '❌ **Don\'t forget units!** Always write Newtons (N)\n\n❌ **Mass ≠ Weight** Mass is in kg, weight is force\n\n❌ **Direction matters** Force is a vector (has direction)',
      500
    );
    
    // Exam Tip
    await streamSection('exam_tip',
      '🎯 **JEE/NEET Pattern:** They often give mass in grams - convert to kg first!\n\n⚡ **Quick Check:** If acceleration doubles, force doubles (direct proportion)',
      600
    );
    
    // Quick Revision
    await streamSection('quick_revision',
      '• Force = Push or Pull\n• Formula: F = ma\n• Unit: Newton (N)\n• Direction matters (vector)\n• More mass = More force needed',
      700
    );
  };

  const streamSection = async (sectionType, content, delay) => {
    await new Promise(resolve => setTimeout(resolve, delay));
    
    setCurrentSection({ type: sectionType, content: '' });
    
    // Stream text character by character
    const words = content.split(' ');
    for (let i = 0; i < words.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 30));
      setSections(prev => ({
        ...prev,
        [sectionType]: {
          ...prev[sectionType],
          content: words.slice(0, i + 1).join(' ')
        }
      }));
    }
    
    // Mark as complete
    setSections(prev => ({
      ...prev,
      [sectionType]: {
        ...prev[sectionType],
        content: content,
        complete: true
      }
    }));
  };

  const renderSection = (sectionType, data) => {
    const config = sectionConfigs[sectionType];
    const IconComponent = config.icon;
    const isComplete = data.complete;
    const isCurrentlyStreaming = currentSection?.type === sectionType && !isComplete;

    if (sectionType === 'greeting') {
      return (
        <motion.div
          key={sectionType}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`bg-gradient-to-r ${config.bgGradient} rounded-2xl p-6 border-2 ${config.borderColor} shadow-sm mb-4`}
        >
          <div className="flex items-start gap-4">
            <motion.div
              animate={{ rotate: [0, 15, -15, 0] }}
              transition={{ duration: 0.6 }}
            >
              <IconComponent className={`w-8 h-8 ${config.iconColor}`} />
            </motion.div>
            <div className="flex-1">
              <p className={`${config.textColor} font-bold text-xl leading-relaxed`} style={{ fontSize: '20px', lineHeight: '1.7' }}>
                {data.content}
                {isCurrentlyStreaming && <TypeCursor color={config.color} />}
              </p>
            </div>
          </div>
        </motion.div>
      );
    }

    return (
      <motion.div
        key={sectionType}
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4 }}
        className={`bg-gradient-to-br ${config.bgGradient} rounded-xl p-5 border-l-4 ${config.borderColor} shadow-sm mb-4`}
      >
        {/* Animated Section Header */}
        <motion.div
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          className="flex items-center gap-3 mb-4"
        >
          <motion.div
            animate={{ rotate: isCurrentlyStreaming ? 360 : 0 }}
            transition={{ duration: 2, repeat: isCurrentlyStreaming ? Infinity : 0, ease: "linear" }}
            className={`p-2 bg-white rounded-lg shadow-sm`}
          >
            <IconComponent className={`w-6 h-6 ${config.iconColor}`} />
          </motion.div>
          <h3 className={`${config.textColor} font-bold text-lg`} style={{ fontSize: '18px' }}>
            {config.title}
          </h3>
        </motion.div>

        {/* Content with formatting */}
        <div className={`${config.textColor} space-y-3`} style={{ fontSize: '17px', lineHeight: '1.8' }}>
          {data.content.split('\n').map((line, idx) => {
            if (line.trim().startsWith('•')) {
              // Bullet point
              return (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="flex items-start gap-3 pl-2"
                >
                  <span className={`${config.iconColor} font-bold mt-1`}>•</span>
                  <span>{line.replace('•', '').trim()}</span>
                </motion.div>
              );
            } else if (line.includes('**')) {
              // Bold text
              const parts = line.split('**');
              return (
                <p key={idx} className="font-medium">
                  {parts.map((part, i) => 
                    i % 2 === 1 ? <strong key={i} className="font-bold">{part}</strong> : part
                  )}
                </p>
              );
            } else if (line.trim().startsWith('❌') || line.trim().startsWith('✅') || line.trim().startsWith('⚡') || line.trim().startsWith('🎯')) {
              // Special formatted line
              return (
                <motion.p
                  key={idx}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: idx * 0.05 }}
                  className="font-medium py-1"
                >
                  {line}
                </motion.p>
              );
            } else if (line.trim()) {
              return <p key={idx} className="leading-relaxed">{line}</p>;
            }
            return null;
          })}
          {isCurrentlyStreaming && <TypeCursor color={config.color} />}
        </div>

        {/* Completion checkmark */}
        {isComplete && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 500, damping: 30 }}
            className="mt-4 flex items-center gap-2"
          >
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="text-green-700 text-sm font-medium">Completed</span>
          </motion.div>
        )}
      </motion.div>
    );
  };

  return (
    <div className="space-y-4 max-w-4xl mx-auto">
      {/* Render all sections */}
      {Object.entries(sections).map(([sectionType, data]) => 
        renderSection(sectionType, data)
      )}

      {/* Streaming indicator */}
      {isStreaming && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center gap-3 text-gray-500 text-base px-4"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="w-5 h-5 border-3 border-purple-300 border-t-purple-600 rounded-full"
          />
          <span style={{ fontSize: '16px' }}>AI is explaining...</span>
        </motion.div>
      )}
    </div>
  );
}

// Typing cursor component
function TypeCursor({ color = 'purple' }) {
  return (
    <motion.span
      animate={{ opacity: [0, 1, 0] }}
      transition={{ duration: 0.8, repeat: Infinity }}
      className={`inline-block ml-1 w-0.5 h-5 bg-${color}-600`}
      style={{ width: '3px', height: '20px', backgroundColor: color === 'purple' ? '#9333ea' : '#3b82f6' }}
    />
  );
}

// Export section types for backend
export const SectionTypes = {
  GREETING: 'greeting',
  SUMMARY: 'summary',
  FORMULA: 'formula',
  EXAMPLE: 'example',
  MISTAKES: 'mistakes',
  EXAM_TIP: 'exam_tip',
  QUICK_REVISION: 'quick_revision',
  MAIN: 'main'
};



