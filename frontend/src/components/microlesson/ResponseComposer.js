import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, ChevronDown, ChevronUp, Heart, GraduationCap } from 'lucide-react';
import ConceptCard from './ConceptCard';
import FormulaCard from './FormulaCard';
import TipCard from './TipCard';
import PracticeActions from './PracticeActions';
import MotivationalFooter from './MotivationalFooter';
import VisualConceptBlock from '../VisualConceptBlock';

/**
 * ResponseComposer - AI Tutor 2.3 Complete UX Redesign
 * Student-first design with collapsible mentor, emotional anchors, and progressive reveal
 */
const ResponseComposer = ({ message, onQuickAction }) => {
  const [mentorExpanded, setMentorExpanded] = useState(false);
  
  const {
    dual_response,
    visual,
    sentiment_analysis,
    motivational_footer
  } = message;

  if (!dual_response || !dual_response.primary) {
    return null;
  }

  const { primary, secondary } = dual_response;
  const microLessonSections = primary.micro_lesson_sections || {};
  const sentiment = sentiment_analysis?.primary_sentiment || 'neutral';
  
  // Clean special characters from text
  const cleanText = (text) => {
    if (!text) return '';
    return text
      .replace(/\\n/g, '\n')
      .replace(/\\"/g, '"')
      .replace(/\\'/g, "'")
      .replace(/\\\\/g, '\\')
      .replace(/\u00a0/g, ' ')
      .trim();
  };

  // Extract formulas
  const formulas = microLessonSections.key_formula || '';
  const formulaList = formulas ? 
    (Array.isArray(formulas) ? formulas.map(f => cleanText(f)) : [cleanText(formulas)]) : 
    [];
  
  // Animation variants for progressive reveal
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.4, ease: "easeOut" }
    }
  };

  return (
    <motion.div 
      className="space-y-5"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Friendly Welcome Banner */}
      <motion.div
        variants={itemVariants}
        className="flex items-center justify-center space-x-3 p-4 bg-gradient-to-r from-purple-100 via-blue-100 to-indigo-100 rounded-2xl border-2 border-purple-200"
      >
        <Sparkles className="w-6 h-6 text-purple-600" />
        <span className="text-lg font-bold text-gray-800">Let's explore this together! 🎓</span>
        <Sparkles className="w-6 h-6 text-purple-600" />
      </motion.div>

      {/* Visual Concept (if available) */}
      {visual && visual.generated && (
        <motion.div variants={itemVariants}>
          <VisualConceptBlock visualData={visual} />
        </motion.div>
      )}

      {/* Concept Overview Card */}
      {microLessonSections.concept_overview && (
        <ConceptCard
          content={microLessonSections.concept_overview}
          sentiment={sentiment}
        />
      )}

      {/* Transition: Formula Section */}
      {formulaList.length > 0 && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="text-center text-sm text-gray-600 font-medium"
          >
            {transitionPhrases.formula}
          </motion.div>
          <FormulaCard
            formulas={formulaList}
            title="Key Formula"
          />
        </>
      )}

      {/* Transition: Step-by-Step */}
      {microLessonSections.step_by_step && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.15 }}
            className="text-center text-sm text-gray-600 font-medium"
          >
            {transitionPhrases.stepByStep}
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.2 }}
            className="p-8 rounded-xl bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-100 shadow-sm"
          >
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 mt-1">
                <div className="w-12 h-12 rounded-xl bg-white flex items-center justify-center shadow-md">
                  <span className="text-3xl">📋</span>
                </div>
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-bold text-gray-900 mb-4 font-poppins flex items-center">
                  Detailed Explanation
                  <span className="ml-2 text-2xl">✨</span>
                </h3>
                <div className="text-gray-800 leading-relaxed font-inter text-base whitespace-pre-wrap space-y-3">
                  {microLessonSections.step_by_step}
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}

      {/* Transition: Real-Life */}
      {microLessonSections.real_life_analogy && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.25 }}
            className="text-center text-sm text-gray-600 font-medium"
          >
            {transitionPhrases.realLife}
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.3 }}
            className="p-8 rounded-xl bg-gradient-to-br from-teal-50 via-cyan-50 to-blue-50 border border-teal-100 shadow-sm"
          >
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 mt-1">
                <div className="w-12 h-12 rounded-xl bg-white flex items-center justify-center shadow-md">
                  <span className="text-3xl">🌍</span>
                </div>
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-bold text-gray-900 mb-4 font-poppins flex items-center">
                  Real-World Connection
                  <span className="ml-2 text-2xl">💡</span>
                </h3>
                <p className="text-gray-800 leading-relaxed font-inter text-base">
                  {microLessonSections.real_life_analogy}
                </p>
              </div>
            </div>
          </motion.div>
        </>
      )}

      {/* Mentor Tip with transition */}
      {microLessonSections.mentor_tip && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.35 }}
            className="text-center text-sm text-gray-600 font-medium"
          >
            {transitionPhrases.tip}
          </motion.div>
          <TipCard
            content={microLessonSections.mentor_tip}
            type="mentor"
          />
        </>
      )}

      {/* Mentor Response (if available) */}
      {secondary && secondary.response && (
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          className="p-8 rounded-xl bg-gradient-to-br from-pink-50 via-purple-50 to-pink-50 border-2 border-pink-200 shadow-lg"
        >
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-pink-400 to-purple-400 flex items-center justify-center shadow-lg">
                <span className="text-3xl">💜</span>
              </div>
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-pink-900 mb-3 font-poppins flex items-center">
                Your Mentor's Guidance
                <span className="ml-2 text-sm px-3 py-1 bg-pink-200 text-pink-800 rounded-full">
                  {Math.round((secondary.weight || 0.5) * 100)}% Support
                </span>
              </h3>
              <p className="text-pink-950 leading-relaxed font-inter text-base">
                {secondary.response}
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Practice Section with transition */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.45 }}
        className="text-center text-sm text-gray-600 font-medium"
      >
        {transitionPhrases.practice}
      </motion.div>

      {/* Practice Actions */}
      <PracticeActions
        onTrySimilar={() => onQuickAction && onQuickAction({ action: 'generate_practice' }, message)}
        onSaveToNotes={() => onQuickAction && onQuickAction({ action: 'save_to_notes' }, message)}
        onExplainDifferently={() => onQuickAction && onQuickAction({ action: 'explain_different' }, message)}
        messageData={message}
      />

      {/* Motivational Footer */}
      {motivational_footer && (
        <MotivationalFooter motivationalData={motivational_footer} />
      )}

      {/* Success Moment */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="text-center p-6 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-200"
      >
        <p className="text-green-800 font-medium">
          🎉 Great job exploring this concept! You're one step closer to mastery. 
        </p>
      </motion.div>
    </div>
  );
};

export default ResponseComposer;
