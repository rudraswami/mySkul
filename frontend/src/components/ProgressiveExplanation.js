/**
 * ProgressiveExplanation Component
 * Collapsible sections with smooth animations and staggered reveals
 */
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BookOpen, 
  Target, 
  Lightbulb, 
  Heart, 
  ChevronDown, 
  ChevronUp,
  Clock,
  CheckCircle
} from 'lucide-react';

const ProgressiveExplanation = ({ 
  sections = [],
  defaultExpanded = ['foundation'],
  className = '' 
}) => {
  const [expandedSections, setExpandedSections] = useState(new Set(defaultExpanded));

  const toggleSection = (sectionId) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId);
      } else {
        newSet.add(sectionId);
      }
      return newSet;
    });
  };

  // Section icon mapping
  const getSectionIcon = (type) => {
    switch (type) {
      case 'foundation':
        return BookOpen;
      case 'steps':
        return Target;
      case 'reallife':
        return Lightbulb;
      case 'mentor':
        return Heart;
      case 'practice':
        return CheckCircle;
      default:
        return BookOpen;
    }
  };

  // Section color mapping
  const getSectionColors = (type, isExpanded) => {
    const colors = {
      foundation: {
        bg: isExpanded ? 'bg-blue-50' : 'bg-gray-50',
        border: isExpanded ? 'border-blue-200' : 'border-gray-200',
        icon: 'text-blue-600',
        title: isExpanded ? 'text-blue-800' : 'text-gray-700'
      },
      steps: {
        bg: isExpanded ? 'bg-green-50' : 'bg-gray-50',
        border: isExpanded ? 'border-green-200' : 'border-gray-200',
        icon: 'text-green-600',
        title: isExpanded ? 'text-green-800' : 'text-gray-700'
      },
      reallife: {
        bg: isExpanded ? 'bg-amber-50' : 'bg-gray-50',
        border: isExpanded ? 'border-amber-200' : 'border-gray-200',
        icon: 'text-amber-600',
        title: isExpanded ? 'text-amber-800' : 'text-gray-700'
      },
      mentor: {
        bg: isExpanded ? 'bg-purple-50' : 'bg-gray-50',
        border: isExpanded ? 'border-purple-200' : 'border-gray-200',
        icon: 'text-purple-600',
        title: isExpanded ? 'text-purple-800' : 'text-gray-700'
      },
      practice: {
        bg: isExpanded ? 'bg-emerald-50' : 'bg-gray-50',
        border: isExpanded ? 'border-emerald-200' : 'border-gray-200',
        icon: 'text-emerald-600',
        title: isExpanded ? 'text-emerald-800' : 'text-gray-700'
      }
    };
    return colors[type] || colors.foundation;
  };

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const sectionVariants = {
    hidden: { 
      opacity: 0, 
      y: 20,
      scale: 0.98
    },
    visible: { 
      opacity: 1, 
      y: 0,
      scale: 1,
      transition: {
        duration: 0.4,
        ease: "easeOut"
      }
    }
  };

  const contentVariants = {
    hidden: { 
      opacity: 0,
      height: 0,
      transition: {
        duration: 0.3
      }
    },
    visible: { 
      opacity: 1,
      height: "auto",
      transition: {
        duration: 0.4,
        ease: "easeOut"
      }
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className={`space-y-3 ${className}`}
    >
      {sections.map((section, index) => {
        const { id, type, title, content, readTime } = section;
        const isExpanded = expandedSections.has(id);
        const SectionIcon = getSectionIcon(type);
        const colors = getSectionColors(type, isExpanded);
        const isAlwaysVisible = defaultExpanded.includes(id) && type === 'foundation';

        return (
          <motion.div
            key={id}
            variants={sectionVariants}
            className={`rounded-xl border ${colors.border} ${colors.bg} overflow-hidden transition-all duration-200`}
          >
            {/* Section Header */}
            <button
              onClick={() => !isAlwaysVisible && toggleSection(id)}
              className={`w-full p-4 text-left transition-all duration-200 ${
                isAlwaysVisible ? 'cursor-default' : 'cursor-pointer hover:bg-opacity-80'
              }`}
              disabled={isAlwaysVisible}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg bg-white shadow-sm ${colors.icon}`}>
                    <SectionIcon className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className={`font-semibold ${colors.title}`}>
                      {title}
                    </h3>
                    {readTime && (
                      <div className="flex items-center mt-1 text-xs text-gray-500">
                        <Clock className="w-3 h-3 mr-1" />
                        <span>{readTime}</span>
                      </div>
                    )}
                  </div>
                </div>
                
                {!isAlwaysVisible && (
                  <motion.div
                    animate={{ rotate: isExpanded ? 180 : 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <ChevronDown className={`w-5 h-5 ${colors.icon}`} />
                  </motion.div>
                )}
              </div>
            </button>

            {/* Section Content */}
            <AnimatePresence initial={false}>
              {(isExpanded || isAlwaysVisible) && (
                <motion.div
                  variants={contentVariants}
                  initial={isAlwaysVisible ? "visible" : "hidden"}
                  animate="visible"
                  exit="hidden"
                  className="overflow-hidden"
                >
                  <div className="px-4 pb-4">
                    <div className="pl-12">
                      {typeof content === 'string' ? (
                        <div className="prose prose-sm max-w-none text-gray-700">
                          <div dangerouslySetInnerHTML={{ __html: content }} />
                        </div>
                      ) : (
                        content
                      )}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        );
      })}
    </motion.div>
  );
};

// Helper function to create sections from AI response
export const createSectionsFromResponse = (aiResponse) => {
  if (!aiResponse) return [];

  const sections = [];

  // Foundation (always visible)
  if (aiResponse.foundation || aiResponse.concept) {
    sections.push({
      id: 'foundation',
      type: 'foundation',
      title: 'Concept Foundation',
      content: aiResponse.foundation || aiResponse.concept,
      readTime: '2 min read'
    });
  }

  // Step-by-step explanation
  if (aiResponse.steps || aiResponse.explanation) {
    sections.push({
      id: 'steps',
      type: 'steps',
      title: 'Step-by-Step Explanation',
      content: aiResponse.steps || aiResponse.explanation,
      readTime: '3 min read'
    });
  }

  // Real-life applications
  if (aiResponse.reallife || aiResponse.applications) {
    sections.push({
      id: 'reallife',
      type: 'reallife',
      title: 'Real-Life Applications',
      content: aiResponse.reallife || aiResponse.applications,
      readTime: '2 min read'
    });
  }

  // Mentor tip
  if (aiResponse.mentor_tip || aiResponse.tip) {
    sections.push({
      id: 'mentor',
      type: 'mentor',
      title: 'Mentor Tip',
      content: aiResponse.mentor_tip || aiResponse.tip,
      readTime: '1 min read'
    });
  }

  // Practice section
  if (aiResponse.practice || aiResponse.examples) {
    sections.push({
      id: 'practice',
      type: 'practice',
      title: 'Quick Practice',
      content: aiResponse.practice || aiResponse.examples,
      readTime: '5 min practice'
    });
  }

  return sections;
};

export default ProgressiveExplanation;