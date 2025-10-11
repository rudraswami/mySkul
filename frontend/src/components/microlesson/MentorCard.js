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

  // Enhanced mentor text splitting with better natural language processing
  const splitMentorText = (text) => {
    if (!text) return {};
    
    const cleanedText = sanitizeText(text);
    const sections = {
      motivation_spark: '',
      simplified_recap: '',
      confidence_tips: '',
      encouragement: ''
    };
    
    // Enhanced section markers with more natural language patterns
    const sectionPatterns = [
      {
        key: 'motivation_spark',
        patterns: [
          /(?:motivation|why this matters|importance)[:\s]*([^.]*\.)/i,
          /^([^.]*(?:important|matters|great|awesome|excellent)[^.]*\.)/i,
          /^([^.]*(?:you can|you will|this helps)[^.]*\.)/i
        ]
      },
      {
        key: 'simplified_recap', 
        patterns: [
          /(?:recap|summary|key points?|remember)[:\s]*([^.]*\.(?:[^.]*\.){0,2})/i,
          /(?:main idea|in summary|to sum up)[:\s]*([^.]*\.(?:[^.]*\.){0,2})/i,
          /(?:\d+[\.\)]|\u2022|\-)\s*([^.]*\.(?:[^.]*\.){0,1})/g
        ]
      },
      {
        key: 'confidence_tips',
        patterns: [
          /(?:tip|strategy|approach|try|practice)[:\s]*([^.]*\.(?:[^.]*\.){0,1})/i,
          /(?:you can|start by|focus on)[:\s]*([^.]*\.(?:[^.]*\.){0,1})/i,
          /(?:remember to|make sure to|don't forget)[:\s]*([^.]*\.)/i
        ]
      },
      {
        key: 'encouragement',
        patterns: [
          /(?:you've got this|keep going|great job|well done|good luck)[^.]*\./i,
          /(?:confidence|believe|trust yourself)[^.]*\./i,
          /([^.]*(?:proud|amazing|incredible|fantastic)[^.]*\.)$/i
        ]
      }
    ];
    
    // Try to extract structured sections using patterns
    for (const section of sectionPatterns) {
      for (const pattern of section.patterns) {
        const matches = cleanedText.match(pattern);
        if (matches) {
          if (pattern.global) {
            // Handle multiple matches (like bullet points)
            sections[section.key] = matches.slice(0, 3).join(' ').trim();
          } else {
            sections[section.key] = matches[1] ? matches[1].trim() : matches[0].trim();
          }
          if (sections[section.key]) {
            sections[section.key] = sections[section.key].substring(0, 250);
            break;
          }
        }
      }
    }
    
    // Enhanced fallback: Intelligent text distribution for unstructured content
    const hasContent = Object.values(sections).some(s => s && s.trim().length > 0);
    
    if (!hasContent || (!sections.motivation_spark && !sections.simplified_recap)) {
      // Split by sentences for better readability
      const sentences = cleanedText
        .split(/[.!?]+/)
        .map(s => s.trim())
        .filter(s => s.length > 15); // Filter out short fragments
      
      if (sentences.length === 1) {
        // Single sentence - use as motivation
        sections.motivation_spark = sentences[0] + '.';
      } else if (sentences.length === 2) {
        // Two sentences - split between motivation and recap
        sections.motivation_spark = sentences[0] + '.';
        sections.simplified_recap = sentences[1] + '.';
      } else if (sentences.length >= 3) {
        // Multiple sentences - distribute intelligently
        sections.motivation_spark = sentences[0] + '.';
        
        // Use middle sentences for recap (max 2 sentences)
        const recapCount = Math.min(2, sentences.length - 2);
        sections.simplified_recap = sentences.slice(1, 1 + recapCount)
          .map(s => `• ${s}`)
          .join('\n');
        
        // Use actionable sentences for tips
        const actionSentences = sentences.filter(s => 
          /^(?:try|start|focus|practice|remember|make sure|you can|you should)/i.test(s.trim())
        );
        
        if (actionSentences.length > 0) {
          sections.confidence_tips = actionSentences[0] + '.';
        } else if (sentences.length > 3) {
          sections.confidence_tips = sentences[sentences.length - 2] + '.';
        }
        
        // Last sentence or encouraging phrase for encouragement
        const lastSentence = sentences[sentences.length - 1];
        if (/(?:you|great|good|success|confident|believe|proud)/i.test(lastSentence)) {
          sections.encouragement = lastSentence + '.';
        } else {
          sections.encouragement = 'You\'ve got this! Keep up the great work!';
        }
      }
    }
    
    // Ensure all sections have reasonable length
    Object.keys(sections).forEach(key => {
      if (sections[key] && sections[key].length > 300) {
        sections[key] = sections[key].substring(0, 297) + '...';
      }
    });
    
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
              <span>{expanded ? "Mentor's Guidance" : "💬 Show Mentor's Support"}</span>
              <Sparkles className="w-4 h-4 text-pink-600" />
              {!expanded && (
                <span className="ml-2 px-2 py-1 bg-pink-200 text-pink-800 rounded-full text-xs font-bold">
                  {Object.values(mentorSections).filter(s => s && s.trim()).length} sections
                </span>
              )}
            </h3>
            <p className="text-sm text-pink-700">
              {expanded ? "Warm support and confidence-building tips" : 
               `${Object.values(mentorSections).filter(s => s && s.trim()).length} helpful sections available`}
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
                        <ReactMarkdown 
                          components={{
                            p: ({ children }) => <LatexRenderer text={children} />,
                            li: ({ children }) => <li className="mb-1"><LatexRenderer text={children} /></li>,
                            ul: ({ children }) => <ul className="list-disc list-inside">{children}</ul>
                          }}
                        >
                          {mentorSections.confidence_tips}
                        </ReactMarkdown>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )}

              {/* Encouragement Quote */}
              {mentorSections.encouragement && (
                <div className="bg-gradient-to-r from-pink-100 to-purple-100 border-l-4 border-pink-400 p-4 rounded-r-xl">
                  <div className="flex items-center space-x-2 mb-2">
                    <TrendingUp className="w-5 h-5 text-pink-600" />
                    <span className="font-bold text-pink-900">🧭 Keep Going!</span>
                  </div>
                  <div className="text-pink-950 text-sm italic">
                    "<ReactMarkdown 
                      components={{
                        p: ({ children }) => <LatexRenderer text={children} />
                      }}
                    >
                      {mentorSections.encouragement}
                    </ReactMarkdown>"
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
