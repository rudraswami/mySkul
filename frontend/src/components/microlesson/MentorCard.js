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
  
  // Enhanced text sanitization and section parsing
  const sanitizeText = (text) => {
    if (!text) return '';
    
    let cleaned = text
      .replace(/\\"/g, '"')
      .replace(/\\'/g, "'")
      .replace(/\\\\/g, '')
      .replace(/\\n/g, '\n')
      .replace(/\\r/g, '\r')
      .replace(/\\t/g, '\t')
      // Remove emojis but preserve text
      .replace(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu, '')
      // Remove specific symbols  
      .replace(/[✅❌☑💡🔎📔💙👇📚🧮🧠🎯⚡💪🌟]/g, '')
      // Remove numbered emojis
      .replace(/[1-9]️⃣|🔟/g, '')
      .replace(/\u00a0/g, ' ')
      .trim();
    
    return DOMPurify.sanitize(cleaned, {
      ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'code'],
      ALLOWED_ATTR: []
    });
  };

  // Split mentor text by sections using ### markers or regex
  const splitMentorText = (text) => {
    if (!text) return {};
    
    const cleanedText = sanitizeText(text);
    const sections = {
      motivation_spark: '',
      simplified_recap: '',
      confidence_tips: '',
      encouragement: ''
    };
    
    // Split by ### markers or numbered sections
    const sectionMarkers = [
      { key: 'motivation_spark', patterns: ['### Motivation', '1.', 'Motivation', 'Why this matters'] },
      { key: 'simplified_recap', patterns: ['### Quick Recap', '2.', 'Recap', 'Summary', 'Key Points'] },
      { key: 'confidence_tips', patterns: ['### Confidence Tips', '3.', 'Tips', 'Strategy', 'How to'] },
      { key: 'encouragement', patterns: ['### Encouragement', '4.', 'Keep Going', 'You got this'] }
    ];
    
    // Try to parse structured sections
    let remainingText = cleanedText;
    
    for (const section of sectionMarkers) {
      for (const pattern of section.patterns) {
        const regex = new RegExp(`${pattern}[:\\s]*([^#]*?)(?=###|$)`, 'i');
        const match = remainingText.match(regex);
        if (match && match[1]) {
          sections[section.key] = match[1].trim().substring(0, 300);
          remainingText = remainingText.replace(match[0], '');
          break;
        }
      }
    }
    
    // If no structured sections found, distribute text intelligently
    if (!sections.motivation_spark && !sections.simplified_recap) {
      const sentences = cleanedText.split(/[.!?]+/).filter(s => s.trim().length > 10);
      
      if (sentences.length > 0) {
        sections.motivation_spark = sentences[0]?.trim() + '.';
      }
      if (sentences.length > 2) {
        sections.simplified_recap = sentences.slice(1, 3).join('. ').trim() + '.';
      }
      if (sentences.length > 3) {
        sections.confidence_tips = sentences.slice(3, 5).join('. ').trim() + '.';
      }
      if (sentences.length > 5) {
        sections.encouragement = sentences[sentences.length - 1]?.trim() + '.';
      }
    }
    
    return sections;
  };

  // Use existing sections or split the raw text
  const mentorSections = sections.motivation_spark 
    ? sections 
    : splitMentorText(mentorData.response || mentorData.raw_text || '');

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
                    <ReactMarkdown 
                      components={{
                        p: ({ children }) => <LatexRenderer text={children} />
                      }}
                    >
                      {mentorSections.motivation_spark || sanitizeText(mentorData.response?.substring(0, 150)) + '...'}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>

              {/* Horizontal Separator */}
              <div className="border-t-2 border-pink-200 my-4"></div>

              {/* Simplified Recap - Collapsible */}
              {mentorSections.simplified_recap && (
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
                        <ReactMarkdown 
                          components={{
                            p: ({ children }) => <LatexRenderer text={children} />,
                            li: ({ children }) => <li className="mb-1"><LatexRenderer text={children} /></li>,
                            ul: ({ children }) => <ul className="list-disc list-inside">{children}</ul>
                          }}
                        >
                          {mentorSections.simplified_recap}
                        </ReactMarkdown>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )}

              {/* Confidence Tips - Collapsible */}
              {mentorSections.confidence_tips && (
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
