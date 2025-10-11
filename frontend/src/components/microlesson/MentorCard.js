import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Heart, ChevronDown, Sparkles, MessageCircle, Target, TrendingUp } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import DOMPurify from 'dompurify';
import LatexRenderer from './LatexRenderer';

/**
 * MentorCard - Structured emotional guidance with collapsible sections
 * AI Tutor 2.4 - Student-friendly mentor experience
 */
const MentorCard = ({ mentorData, weight }) => {
  const [expanded, setExpanded] = useState(false);
  const [showRecap, setShowRecap] = useState(false);
  const [showTips, setShowTips] = useState(false);

  if (!mentorData) return null;

  const sections = mentorData.mentor_sections || {};
  
  // Clean text helper (preserving LaTeX for LatexRenderer)
  const cleanText = (text) => {
    if (!text) return '';
    return text
      .replace(/\*\*(.+?)\*\*/g, '$1')  // Remove bold markers
      .replace(/\*(.+?)\*/g, '$1')      // Remove italic markers
      .replace(/✅/g, '')                // Remove checkmarks
      .replace(/❌/g, '')
      .replace(/\\"/g, '"')
      .replace(/\\'/g, "'")
      .replace(/\\\\/g, '')
      .trim();
  };

  return (
    <div className="border-2 border-pink-200 rounded-2xl overflow-hidden shadow-lg">
      {/* Mentor Toggle Button */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-6 bg-gradient-to-r from-pink-100 via-purple-100 to-pink-100 hover:from-pink-200 hover:to-purple-200 transition-all flex items-center justify-between group"
      >
        <div className="flex items-center space-x-4">
          <motion.div 
            className="w-14 h-14 rounded-full bg-gradient-to-br from-pink-400 to-purple-500 flex items-center justify-center shadow-lg"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            <Heart className="w-7 h-7 text-white" />
          </motion.div>
          <div className="text-left">
            <h3 className="text-xl font-bold text-pink-900 flex items-center space-x-2">
              <span>{expanded ? "Mentor's Guidance" : "💬 Show Mentor's Motivation"}</span>
              <Sparkles className="w-4 h-4 text-pink-600" />
            </h3>
            <p className="text-sm text-pink-700">
              {expanded ? "Warm support and confidence-building tips" : "Get emotional support and study strategies"}
            </p>
          </div>
        </div>
        <motion.div
          animate={{ rotate: expanded ? 180 : 0 }}
          transition={{ duration: 0.3 }}
          className="text-pink-700 group-hover:text-pink-900"
        >
          <ChevronDown className="w-6 h-6" />
        </motion.div>
      </button>

      {/* Mentor Content - Expandable */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.4, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="p-6 bg-gradient-to-br from-pink-50 via-purple-50 to-pink-50 space-y-4">
              
              {/* Motivation Spark - Always visible */}
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-1">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-pink-400 to-pink-500 flex items-center justify-center shadow-md">
                    <span className="text-2xl">💙</span>
                  </div>
                </div>
                <div className="flex-1">
                  <h4 className="font-bold text-pink-900 mb-2 flex items-center space-x-2">
                    <span>Motivation Spark</span>
                    <Sparkles className="w-4 h-4 text-pink-600" />
                  </h4>
                  <div className="text-pink-950 text-base leading-relaxed">
                    <LatexRenderer text={sections.motivation_spark || mentorData.response?.substring(0, 150) + '...'} />
                  </div>
                </div>
              </div>

              {/* Horizontal Separator */}
              <div className="border-t-2 border-pink-200 my-4"></div>

              {/* Simplified Recap - Collapsible */}
              {sections.simplified_recap && (
                <div>
                  <button
                    onClick={() => setShowRecap(!showRecap)}
                    className="flex items-center space-x-2 text-pink-900 font-semibold hover:text-pink-700 transition-colors mb-2"
                  >
                    <MessageCircle className="w-5 h-5" />
                    <span>💬 Quick Recap</span>
                    <motion.div animate={{ rotate: showRecap ? 180 : 0 }}>
                      <ChevronDown className="w-4 h-4" />
                    </motion.div>
                  </button>
                  
                  <AnimatePresence>
                    {showRecap && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="pl-7 text-pink-900 text-sm leading-relaxed"
                      >
                        <LatexRenderer text={sections.simplified_recap} />
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )}

              {/* Confidence Tips - Collapsible */}
              {sections.confidence_tips && (
                <div>
                  <button
                    onClick={() => setShowTips(!showTips)}
                    className="flex items-center space-x-2 text-pink-900 font-semibold hover:text-pink-700 transition-colors mb-2"
                  >
                    <Target className="w-5 h-5" />
                    <span>🌟 Confidence Boost</span>
                    <motion.div animate={{ rotate: showTips ? 180 : 0 }}>
                      <ChevronDown className="w-4 h-4" />
                    </motion.div>
                  </button>
                  
                  <AnimatePresence>
                    {showTips && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="pl-7 text-pink-900 text-sm leading-relaxed"
                      >
                        <LatexRenderer text={sections.confidence_tips} />
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )}

              {/* Encouragement Quote */}
              {sections.encouragement && (
                <div className="bg-gradient-to-r from-pink-100 to-purple-100 border-l-4 border-pink-400 p-4 rounded-r-xl">
                  <div className="flex items-center space-x-2 mb-2">
                    <TrendingUp className="w-5 h-5 text-pink-600" />
                    <span className="font-bold text-pink-900">🧭 Keep Going!</span>
                  </div>
                  <div className="text-pink-950 text-sm italic">
                    "<LatexRenderer text={sections.encouragement} />"
                  </div>
                </div>
              )}

              {/* Support Badge */}
              <div className="flex justify-end">
                <span className="px-4 py-2 bg-pink-200 text-pink-800 rounded-full text-xs font-bold shadow-sm">
                  {Math.round((weight || 0.3) * 100)}% Emotional Support
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default MentorCard;
