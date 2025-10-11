/**
 * VisualConceptBlock Component
 * Displays concept visualizations with fade-in animations
 */
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Lightbulb, AlertCircle } from 'lucide-react';
import { useVisualGenerator } from '../hooks/useVisualGenerator';

const VisualConceptBlock = ({ 
  topic, 
  subject = 'general',
  className = '',
  showTitle = true,
  animate = true 
}) => {
  const { generateVisual, isLoading, error } = useVisualGenerator();
  const [visual, setVisual] = useState(null);

  useEffect(() => {
    if (topic) {
      generateVisual(topic, subject, false).then(result => {
        setVisual(result);
      });
    }
  }, [topic, subject, generateVisual]);

  const containerVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: { 
      opacity: 1, 
      scale: 1,
      transition: { 
        duration: 0.6,
        ease: "easeOut"
      }
    }
  };

  const svgVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { 
        delay: 0.2,
        duration: 0.5
      }
    }
  };

  if (isLoading) {
    return (
      <div className={`flex items-center justify-center p-6 ${className}`}>
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  if (error && !visual) {
    return (
      <div className={`flex items-center justify-center p-4 text-gray-500 ${className}`}>
        <AlertCircle className="w-5 h-5 mr-2" />
        <span className="text-sm">Visual not available</span>
      </div>
    );
  }

  if (!visual?.content) {
    return null;
  }

  const MotionWrapper = animate ? motion.div : 'div';
  const motionProps = animate ? {
    variants: containerVariants,
    initial: "hidden",
    animate: "visible"
  } : {};

  return (
    <MotionWrapper
      {...motionProps}
      className={`bg-gradient-to-br from-gray-50 to-white rounded-xl p-6 shadow-sm border border-gray-100 ${className}`}
    >
      {/* Title */}
      {showTitle && topic && (
        <div className="flex items-center mb-4">
          <Lightbulb className="w-4 h-4 text-amber-500 mr-2" />
          <h3 className="text-sm font-medium text-gray-700 capitalize">
            {topic.replace(/_/g, ' ')}
          </h3>
        </div>
      )}

      {/* Visual Content */}
      <div className="flex justify-center">
        <motion.div
          variants={animate ? svgVariants : {}}
          className="relative"
        >
          {visual.type === 'svg' ? (
            <div 
              dangerouslySetInnerHTML={{ __html: visual.content }}
              className="concept-visual"
            />
          ) : (
            <img 
              src={visual.content} 
              alt={`Visual representation of ${topic}`}
              className="max-w-[120px] max-h-[100px] object-contain"
              loading="lazy"
            />
          )}
          
          {/* Success Indicator */}
          {visual.success && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.8 }}
              className="absolute -top-2 -right-2 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center"
            >
              <span className="text-white text-xs">✓</span>
            </motion.div>
          )}
        </motion.div>
      </div>

      {/* Metadata */}
      {visual.fallback && (
        <div className="mt-3 text-center">
          <span className="text-xs text-gray-400">Concept visualization</span>
        </div>
      )}
      
      {/* CSS for concept visuals */}
      <style jsx>{`
        .concept-visual svg {
          filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.1));
          transition: transform 0.2s ease;
        }
        .concept-visual:hover svg {
          transform: scale(1.05);
        }
      `}</style>
    </MotionWrapper>
  );
};

export default VisualConceptBlock;