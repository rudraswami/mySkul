import React from 'react';
import { motion } from 'framer-motion';
import { GraduationCap, Heart, Sparkles } from 'lucide-react';
import PersonaHeader from './PersonaHeader';
import ResponseComposer from './microlesson/ResponseComposer';

/**
 * AIResponseCardV2 - Enhanced AI Tutor 2.0 response card
 * Features: Adaptive personas, visual concepts, progressive disclosure, quick actions
 */
const AIResponseCardV2 = ({ message, onQuickAction }) => {
  const {
    dual_response,
    visual,
    sentiment_analysis,
    quick_actions,
    persona_blend
  } = message;

  if (!dual_response) {
    return null;
  }

  const { primary, secondary } = dual_response;
  const progressiveSections = primary.progressive_sections || {};

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-4"
    >
      {/* Persona Blend Header */}
      {persona_blend && (
        <PersonaHeader
          personaBlend={persona_blend}
          sentimentAnalysis={sentiment_analysis}
        />
      )}

      {/* Professor Response with Progressive Disclosure */}
      <div className="bg-white rounded-lg border border-blue-100 shadow-sm overflow-hidden">
        {/* Professor Header */}
        <div className="flex items-center space-x-2 px-4 py-3 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-blue-100">
          <GraduationCap className="w-5 h-5 text-blue-600" />
          <span className="font-semibold text-blue-900">Professor AI</span>
          <span className="text-xs text-blue-600 ml-auto">
            {Math.round((primary.weight || 0.5) * 100)}% Focus
          </span>
        </div>

        <div className="p-4">
          {/* Visual Concept */}
          {visual && visual.generated && (
            <VisualConceptBlock visualData={visual} />
          )}

          {/* Progressive Sections */}
          {Object.keys(progressiveSections).length > 0 ? (
            <ProgressiveExplanation
              sections={progressiveSections}
              sentiment={sentiment_analysis?.primary_sentiment}
            />
          ) : (
            <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
              {primary.response}
            </div>
          )}
        </div>
      </div>

      {/* Mentor Response */}
      {secondary && secondary.response && (
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-r from-pink-50 to-purple-50 rounded-lg border border-pink-100 p-4"
        >
          <div className="flex items-center space-x-2 mb-2">
            <Heart className="w-4 h-4 text-pink-500" />
            <span className="font-medium text-pink-900">Mentor AI</span>
            <span className="text-xs text-pink-600">
              {Math.round((secondary.weight || 0.5) * 100)}% Support
            </span>
          </div>
          <p className="text-pink-900 text-sm leading-relaxed">
            {secondary.response}
          </p>
        </motion.div>
      )}

      {/* Quick Actions */}
      {quick_actions && quick_actions.length > 0 && (
        <QuickActionTray
          actions={quick_actions}
          onAction={onQuickAction}
          messageData={message}
        />
      )}

      {/* Confidence Indicator */}
      {sentiment_analysis && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="flex items-center justify-between text-xs text-gray-500 px-2"
        >
          <div className="flex items-center space-x-2">
            <Sparkles className="w-3 h-3" />
            <span>AI Confidence: {Math.round((primary.confidence || 0.9) * 100)}%</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className={`w-2 h-2 rounded-full ${
              sentiment_analysis.needs_encouragement ? 'bg-orange-400' : 'bg-green-400'
            }`} />
            <span className="capitalize">{sentiment_analysis.primary_sentiment || 'neutral'}</span>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default AIResponseCardV2;