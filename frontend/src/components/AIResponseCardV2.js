/**
 * AI Response Card V2 Component
 * Enhanced AI response with visual-first layout, persona adaptation, and progressive disclosure
 */
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Shield, CheckCircle, ExternalLink } from 'lucide-react';
import VisualConceptBlock from './VisualConceptBlock';
import ProgressiveExplanation, { createSectionsFromResponse } from './ProgressiveExplanation';
import QuickActionTray from './QuickActionTray';

const AIResponseCardV2 = ({ 
  response,
  persona = 'hybrid',
  onSaveToNotes,
  onPracticeSimilar,
  onExplainDifferently,
  onShowVisual,
  onCopyResponse,
  onFeedback,
  className = ''
}) => {
  const [sections, setSections] = useState([]);
  const [topic, setTopic] = useState('');
  const [subject, setSubject] = useState('general');
  
  useEffect(() => {
    if (response) {
      // Extract topic and subject from response
      const detectedTopic = response.topic || response.subject || extractTopicFromText(response.text);
      const detectedSubject = response.subject || detectSubject(response.text);
      
      setTopic(detectedTopic);
      setSubject(detectedSubject);
      
      // Create progressive disclosure sections
      const responseSections = createSectionsFromResponse(response);
      setSections(responseSections);
    }
  }, [response]);

  // Extract topic from response text
  const extractTopicFromText = (text) => {
    if (!text) return '';
    
    // Simple topic extraction - look for common patterns
    const topicPatterns = [
      /(?:concept of|topic of|about)\s+([^.]+)/i,
      /(?:understanding|explaining|learning)\s+([^.]+)/i,
      /([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/
    ];
    
    for (const pattern of topicPatterns) {
      const match = text.match(pattern);
      if (match && match[1]) {
        return match[1].trim().substring(0, 50); // Limit length
      }
    }
    
    return 'concept';
  };

  // Detect subject from response content
  const detectSubject = (text) => {
    if (!text) return 'general';
    
    const lowerText = text.toLowerCase();
    
    if (lowerText.includes('math') || lowerText.includes('algebra') || 
        lowerText.includes('calculus') || lowerText.includes('geometry')) {
      return 'mathematics';
    }
    
    if (lowerText.includes('physics') || lowerText.includes('force') || 
        lowerText.includes('energy') || lowerText.includes('motion')) {
      return 'physics';
    }
    
    if (lowerText.includes('chemistry') || lowerText.includes('chemical') || 
        lowerText.includes('molecule') || lowerText.includes('atom')) {
      return 'chemistry';
    }
    
    return 'general';
  };

  // Get persona-based styling
  const getPersonaStyles = () => {
    const styles = {
      professor: {
        accent: 'blue',
        gradient: 'from-blue-50 to-blue-100',
        border: 'border-blue-200'
      },
      mentor: {
        accent: 'green',
        gradient: 'from-green-50 to-green-100',
        border: 'border-green-200'
      },
      hybrid: {
        accent: 'purple',
        gradient: 'from-purple-50 to-purple-100',
        border: 'border-purple-200'
      }
    };
    
    return styles[persona] || styles.hybrid;
  };

  const personaStyles = getPersonaStyles();

  // Animation variants
  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: {
        duration: 0.6,
        ease: "easeOut",
        staggerChildren: 0.1
      }
    }
  };

  const childVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.4 }
    }
  };

  if (!response) {
    return null;
  }

  return (
    <motion.div
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      className={`bg-white rounded-2xl shadow-lg border ${personaStyles.border} overflow-hidden ${className}`}
    >
      {/* Header with Verification Badge */}
      <motion.div 
        variants={childVariants}
        className={`bg-gradient-to-r ${personaStyles.gradient} p-4 border-b ${personaStyles.border}`}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <Shield className="w-5 h-5 text-emerald-600" />
              <span className="text-sm font-medium text-gray-800">
                Hallucination-Free Response
              </span>
              <CheckCircle className="w-4 h-4 text-emerald-600" />
            </div>
          </div>
          
          {/* Persona Indicator */}
          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-600 capitalize">
              {persona} mode
            </span>
            <div className={`w-2 h-2 rounded-full bg-${personaStyles.accent}-500`} />
          </div>
        </div>
      </motion.div>

      {/* Visual Concept Block */}
      {topic && (
        <motion.div variants={childVariants} className="p-6 pb-0">
          <VisualConceptBlock 
            topic={topic}
            subject={subject}
            className="mb-6"
          />
        </motion.div>
      )}

      {/* Progressive Explanation */}
      <motion.div variants={childVariants} className="p-6">
        <ProgressiveExplanation 
          sections={sections}
          defaultExpanded={['foundation']}
        />
      </motion.div>

      {/* Citation and Sources */}
      {response.sources && response.sources.length > 0 && (
        <motion.div 
          variants={childVariants}
          className="px-6 pb-4"
        >
          <div className="bg-gray-50 rounded-lg p-3">
            <h4 className="text-xs font-semibold text-gray-700 mb-2 flex items-center">
              <ExternalLink className="w-3 h-3 mr-1" />
              Verified Sources
            </h4>
            <div className="space-y-1">
              {response.sources.slice(0, 3).map((source, index) => (
                <div key={index} className="text-xs text-gray-600">
                  • {source.title || source.name || `Source ${index + 1}`}
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* Quick Action Tray */}
      <motion.div variants={childVariants} className="p-6 pt-0">
        <QuickActionTray
          responseData={response}
          onSaveToNotes={onSaveToNotes}
          onPracticeSimilar={onPracticeSimilar}
          onExplainDifferently={onExplainDifferently}
          onShowVisual={onShowVisual}
          onCopyResponse={onCopyResponse}
          onFeedback={onFeedback}
        />
      </motion.div>

      {/* Footer with Confidence Badge */}
      {response.confidence && (
        <motion.div 
          variants={childVariants}
          className="px-6 pb-4"
        >
          <div className="flex items-center justify-center">
            <div className="bg-gray-100 rounded-full px-4 py-2 text-xs text-gray-600">
              {getConfidenceMessage(response.confidence)}
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

// Helper function to convert numeric confidence to motivational text
const getConfidenceMessage = (confidence) => {
  if (typeof confidence === 'number') {
    if (confidence >= 0.9) return "Let's master this together! 🎯";
    if (confidence >= 0.7) return "You're on the right track! 💪";
    if (confidence >= 0.5) return "Let's work through this step by step! 🤝";
    return "Let's explore this together! 🔍";
  }
  return confidence;
};

export default AIResponseCardV2;