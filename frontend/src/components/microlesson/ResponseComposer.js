import React from 'react';
import { motion } from 'framer-motion';
import ConceptCard from './ConceptCard';
import FormulaCard from './FormulaCard';
import TipCard from './TipCard';
import PracticeActions from './PracticeActions';
import MotivationalFooter from './MotivationalFooter';
import VisualConceptBlock from '../VisualConceptBlock';

/**
 * ResponseComposer - Main orchestrator for AI Tutor 2.1 micro-lesson rendering
 * Transforms raw AI responses into structured, visually appealing micro-lessons
 */
const ResponseComposer = ({ message, onQuickAction }) => {
  const {
    dual_response,
    visual,
    sentiment_analysis,
    motivational_footer
  } = message;

  if (!dual_response || !dual_response.primary) {
    return null;
  }

  const { primary } = dual_response;
  const microLessonSections = primary.micro_lesson_sections || {};
  const sentiment = sentiment_analysis?.primary_sentiment || 'neutral';

  // Extract formulas
  const formulas = microLessonSections.key_formula || '';
  const formulaList = formulas ? 
    (Array.isArray(formulas) ? formulas : [formulas]) : 
    [];

  return (
    <div className="space-y-0">
      {/* Visual Concept (if available) */}
      {visual && visual.generated && (
        <VisualConceptBlock visualData={visual} />
      )}

      {/* Concept Overview Card */}
      {microLessonSections.concept_overview && (
        <ConceptCard
          content={microLessonSections.concept_overview}
          sentiment={sentiment}
        />
      )}

      {/* Formula Card */}
      {formulaList.length > 0 && (
        <FormulaCard
          formulas={formulaList}
          title="Key Formula"
        />
      )}

      {/* Step-by-Step Explanation */}
      {microLessonSections.step_by_step && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.15 }}
          className="p-6 rounded-xl bg-white border border-gray-200 shadow-sm mb-4"
        >
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 mt-1">
              <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
                <span className="text-2xl">📋</span>
              </div>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-3 font-poppins">
                Step-by-Step Explanation
              </h3>
              <div className="text-gray-700 leading-relaxed font-inter whitespace-pre-wrap">
                {microLessonSections.step_by_step}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Real-Life Analogy */}
      {microLessonSections.real_life_analogy && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
          className="p-6 rounded-xl bg-gradient-to-br from-teal-50 to-cyan-50 border border-teal-100 shadow-sm mb-4"
        >
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 mt-1">
              <div className="w-10 h-10 rounded-lg bg-white flex items-center justify-center shadow-sm">
                <span className="text-2xl">🌍</span>
              </div>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-2 font-poppins">
                Real-Life Application
              </h3>
              <p className="text-gray-700 leading-relaxed font-inter">
                {microLessonSections.real_life_analogy}
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Mentor Tip */}
      {microLessonSections.mentor_tip && (
        <TipCard
          content={microLessonSections.mentor_tip}
          type="mentor"
        />
      )}

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
    </div>
  );
};

export default ResponseComposer;
