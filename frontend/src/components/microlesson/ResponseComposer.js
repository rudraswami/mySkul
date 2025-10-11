import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, ChevronDown, ChevronUp, Heart, GraduationCap, Zap } from 'lucide-react';
import ConceptCard from './ConceptCard';
import FormulaCard from './FormulaCard';
import TipCard from './TipCard';
import PracticeActions from './PracticeActions';
import MotivationalFooter from './MotivationalFooter';
import VisualConceptBlock from '../VisualConceptBlock';
import MentorCard from './MentorCard';

/**
 * ResponseComposer - AI Tutor 2.3 Complete UX Redesign
 * Student-first design with collapsible mentor, emotional anchors, and progressive reveal
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

  const { primary, secondary } = dual_response;
  const microLessonSections = primary.micro_lesson_sections || {};
  const sentiment = sentiment_analysis?.primary_sentiment || 'neutral';
  
  // Dynamic emotional anchors based on sentiment and topic
  const getEmotionalAnchor = (position) => {
    const anchors = {
      concept: [
        "💡 Take a deep breath — this part builds your concept foundation.",
        "✨ Focus here — this is the core idea you need to master!",
        "🎯 Starting point locked in — let's build on this!"
      ],
      formula: [
        "🧮 This is the key equation — let's break it down together!",
        "📐 The formula is your toolkit — understand it, own it!",
        "✨ Mathematics made simple — one step at a time!"
      ],
      steps: [
        "🎯 Almost there — let's visualize the next step!",
        "💪 You're doing great — breaking down complex ideas!",
        "🚀 Each step brings clarity — keep the momentum!"
      ],
      practice: [
        "🎉 Great! You've cracked the logic — now let's see it in action.",
        "💫 Knowledge unlocked — time to practice and reinforce!",
        "🌟 You've got this — let's solidify your understanding!"
      ]
    };
    
    const options = anchors[position] || anchors.concept;
    return options[Math.floor(Math.random() * options.length)];
  };
  
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

      {/* Professor's Explanation Card with Academic Vibe */}
      <motion.div variants={itemVariants}>
        <div className="p-8 rounded-2xl bg-gradient-to-br from-blue-50 via-indigo-50 to-cyan-50 border-2 border-blue-300 shadow-xl">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900">Professor's Explanation</h2>
              <p className="text-sm text-blue-700">Clear, structured, and exam-focused</p>
            </div>
            <span className="px-3 py-1 bg-blue-200 text-blue-800 rounded-full text-xs font-semibold">
              {Math.round((primary.weight || 0.7) * 100)}% Focus
            </span>
          </div>

          {/* Concept Overview */}
          {microLessonSections.concept_overview && (
            <div className="mb-6">
              <div className="flex items-center space-x-2 mb-3">
                <span className="text-2xl">📘</span>
                <h3 className="text-lg font-bold text-gray-800">Core Concept</h3>
              </div>
              <p className="text-gray-800 text-base leading-relaxed pl-8">
                {cleanText(microLessonSections.concept_overview)}
              </p>
            </div>
          )}

          {/* Dynamic Emotional Anchor */}
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center justify-center space-x-2 my-5 px-4 py-3 bg-gradient-to-r from-yellow-100 to-orange-100 rounded-xl border border-yellow-300"
          >
            <Zap className="w-5 h-5 text-orange-600" />
            <span className="text-orange-800 font-medium text-sm">{getEmotionalAnchor('concept')}</span>
          </motion.div>

          {/* Visual Separator */}
          <div className="flex items-center my-5">
            <div className="flex-1 border-t-2 border-gradient-to-r from-transparent via-gray-300 to-transparent"></div>
            <span className="px-3 text-gray-400">•••</span>
            <div className="flex-1 border-t-2 border-gradient-to-r from-transparent via-gray-300 to-transparent"></div>
          </div>

          {/* Formula Card with Anchor */}
          {formulaList.length > 0 && (
            <>
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center justify-center space-x-2 my-4 px-4 py-2 bg-gradient-to-r from-purple-100 to-indigo-100 rounded-lg border border-purple-200"
              >
                <span className="text-purple-700 font-medium text-xs">{getEmotionalAnchor('formula')}</span>
              </motion.div>
              
              <div className="mb-6">
                <div className="flex items-center space-x-2 mb-3">
                  <span className="text-2xl">🧮</span>
                  <h3 className="text-lg font-bold text-gray-800">Key Formula</h3>
                </div>
                <FormulaCard formulas={formulaList} title="" />
              </div>
            </>
          )}

          {/* Step-by-Step Explanation */}
          {microLessonSections.step_by_step && (
            <div className="mb-6">
              <div className="flex items-center space-x-2 mb-3">
                <span className="text-2xl">📋</span>
                <h3 className="text-lg font-bold text-gray-800">Detailed Breakdown</h3>
              </div>
              <div className="pl-8 text-gray-800 text-base leading-relaxed whitespace-pre-wrap space-y-2">
                {cleanText(microLessonSections.step_by_step)}
              </div>
            </div>
          )}

          {/* Real-Life Examples */}
          {microLessonSections.real_life_analogy && (
            <div className="mb-6">
              <div className="flex items-center space-x-2 mb-3">
                <span className="text-2xl">🌍</span>
                <h3 className="text-lg font-bold text-gray-800">Real-World Connection</h3>
              </div>
              <p className="pl-8 text-gray-800 text-base leading-relaxed">
                {cleanText(microLessonSections.real_life_analogy)}
              </p>
            </div>
          )}

          {/* Tip Section */}
          {microLessonSections.mentor_tip && (
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r-xl">
              <div className="flex items-center space-x-2 mb-2">
                <span className="text-xl">💡</span>
                <h3 className="font-bold text-yellow-900">Pro Tip</h3>
              </div>
              <p className="text-yellow-900 text-sm leading-relaxed">
                {cleanText(microLessonSections.mentor_tip)}
              </p>
            </div>
          )}
        </div>
      </motion.div>

      {/* Emotional Anchor - Motivation */}
      <motion.div
        variants={itemVariants}
        className="flex items-center justify-center space-x-2 text-sm text-purple-700 font-medium"
      >
        <span>💡</span>
        <span>Let's visualize this concept below</span>
        <span>👇</span>
      </motion.div>

      {/* Collapsible Mentor Section */}
      {secondary && secondary.response && (
        <motion.div variants={itemVariants}>
          <div className="border-2 border-pink-200 rounded-2xl overflow-hidden shadow-lg">
            {/* Mentor Toggle Button */}
            <button
              onClick={() => setMentorExpanded(!mentorExpanded)}
              className="w-full p-6 bg-gradient-to-r from-pink-100 to-purple-100 hover:from-pink-200 hover:to-purple-200 transition-all flex items-center justify-between"
            >
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-pink-400 to-purple-500 flex items-center justify-center shadow-lg">
                  <Heart className="w-6 h-6 text-white" />
                </div>
                <div className="text-left">
                  <h3 className="text-xl font-bold text-pink-900">
                    {mentorExpanded ? "Hide Mentor's Motivation" : "💬 Show Mentor's Motivation"}
                  </h3>
                  <p className="text-sm text-pink-700">
                    {mentorExpanded ? "Collapse supportive guidance" : "Get emotional support and study strategies"}
                  </p>
                </div>
              </div>
              <motion.div
                animate={{ rotate: mentorExpanded ? 180 : 0 }}
                transition={{ duration: 0.3 }}
              >
                <ChevronDown className="w-6 h-6 text-pink-700" />
              </motion.div>
            </button>

            {/* Mentor Content - Collapsible */}
            <AnimatePresence>
              {mentorExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.4, ease: "easeInOut" }}
                  className="overflow-hidden"
                >
                  <div className="p-8 bg-gradient-to-br from-pink-50 to-purple-50">
                    <div className="flex items-start space-x-4">
                      <div className="flex-shrink-0">
                        <div className="w-10 h-10 rounded-lg bg-pink-400 flex items-center justify-center">
                          <span className="text-2xl">💜</span>
                        </div>
                      </div>
                      <div className="flex-1">
                        <p className="text-pink-950 text-base leading-relaxed">
                          {cleanText(secondary.response)}
                        </p>
                        <span className="inline-block mt-4 px-3 py-1 bg-pink-200 text-pink-800 rounded-full text-xs font-semibold">
                          {Math.round((secondary.weight || 0.3) * 100)}% Emotional Support
                        </span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      )}

      {/* Practice Actions */}
      <motion.div variants={itemVariants}>
        <PracticeActions
          onTrySimilar={() => onQuickAction && onQuickAction({ action: 'generate_practice' }, message)}
          onSaveToNotes={() => onQuickAction && onQuickAction({ action: 'save_to_notes' }, message)}
          onExplainDifferently={() => onQuickAction && onQuickAction({ action: 'explain_different' }, message)}
          messageData={message}
        />
      </motion.div>

      {/* Motivational Footer */}
      {motivational_footer && (
        <motion.div variants={itemVariants}>
          <MotivationalFooter motivationalData={motivational_footer} />
        </motion.div>
      )}

      {/* Success Celebration */}
      <motion.div
        variants={itemVariants}
        className="text-center p-6 bg-gradient-to-r from-green-100 to-emerald-100 rounded-2xl border-2 border-green-300 shadow-lg"
      >
        <p className="text-lg font-bold text-green-800">
          🎉 Awesome! You've explored this concept thoroughly!
        </p>
        <p className="text-sm text-green-700 mt-2">
          One step closer to mastery. Keep up the great work! 💪
        </p>
      </motion.div>
    </motion.div>
  );
};

export default ResponseComposer;
