import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, Lightbulb, BookOpen, Target, Star } from 'lucide-react';

/**
 * ProgressiveExplanation - Collapsible sections for progressive disclosure
 * Foundation → Step-by-step → Real-life → Key Points
 */
const ProgressiveExplanation = ({ sections, sentiment }) => {
  const [expandedSections, setExpandedSections] = useState({
    foundation: true,
    step_by_step: false,
    real_life: false,
    key_points: false
  });

  const toggleSection = (sectionKey) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionKey]: !prev[sectionKey]
    }));
  };

  const sectionConfig = {
    foundation: {
      title: 'Foundation',
      icon: Lightbulb,
      color: 'blue',
      description: 'Core concept in simple terms'
    },
    step_by_step: {
      title: 'Step-by-Step',
      icon: BookOpen,
      color: 'purple',
      description: 'Detailed explanation with examples'
    },
    real_life: {
      title: 'Real-Life Application',
      icon: Target,
      color: 'green',
      description: 'Practical use and analogies'
    },
    key_points: {
      title: 'Key Points',
      icon: Star,
      color: 'orange',
      description: 'Essential takeaways'
    }
  };

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-50 border-blue-200 text-blue-700 hover:bg-blue-100',
      purple: 'bg-purple-50 border-purple-200 text-purple-700 hover:bg-purple-100',
      green: 'bg-green-50 border-green-200 text-green-700 hover:bg-green-100',
      orange: 'bg-orange-50 border-orange-200 text-orange-700 hover:bg-orange-100'
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="space-y-3 my-4">
      {Object.keys(sectionConfig).map((sectionKey) => {
        const section = sectionConfig[sectionKey];
        const content = sections[sectionKey];
        const isExpanded = expandedSections[sectionKey];
        const Icon = section.icon;

        // Skip if no content
        if (!content || content.trim() === '') return null;

        return (
          <motion.div
            key={sectionKey}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className={`border rounded-lg overflow-hidden ${getColorClasses(section.color)}`}
          >
            {/* Section Header */}
            <button
              onClick={() => toggleSection(sectionKey)}
              className="w-full flex items-center justify-between p-3 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <Icon className="w-5 h-5" />
                <div className="text-left">
                  <div className="font-medium">{section.title}</div>
                  {!isExpanded && (
                    <div className="text-xs opacity-75">{section.description}</div>
                  )}
                </div>
              </div>
              <motion.div
                animate={{ rotate: isExpanded ? 180 : 0 }}
                transition={{ duration: 0.2 }}
              >
                <ChevronDown className="w-5 h-5" />
              </motion.div>
            </button>

            {/* Section Content */}
            <AnimatePresence>
              {isExpanded && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                  className="px-3 pb-3"
                >
                  <div className="bg-white p-3 rounded text-gray-700 text-sm leading-relaxed">
                    {content}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        );
      })}
    </div>
  );
};

export default ProgressiveExplanation;