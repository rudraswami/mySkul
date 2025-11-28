/**
 * ConceptNavigator.jsx
 * Phase 5: Cross-concept linking and navigation
 * 
 * Features:
 * - Visual concept map
 * - Prerequisites display
 * - Related concepts
 * - Learning path suggestions
 * - Smooth transitions between concepts
 */

import React, { useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ChevronRight, ChevronLeft, ArrowRight, 
  BookOpen, Target, Lightbulb, Link2, 
  CheckCircle, Lock, Sparkles, TrendingUp
} from 'lucide-react';
import { 
  getConceptDetails, 
  getRelatedConcepts, 
  getNextConcepts,
  getLearningPath 
} from '../../config/conceptGraph';

// Difficulty badge colors
const DIFFICULTY_COLORS = {
  easy: { bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-700 dark:text-green-300', border: 'border-green-300' },
  medium: { bg: 'bg-yellow-100 dark:bg-yellow-900/30', text: 'text-yellow-700 dark:text-yellow-300', border: 'border-yellow-300' },
  hard: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-700 dark:text-red-300', border: 'border-red-300' },
};

const ConceptNavigator = ({
  currentConcept,
  subject = 'physics',
  masteredConcepts = [],
  onConceptSelect,
  onClose,
  showMiniMap = true,
  showSuggestions = true,
}) => {
  const [activeTab, setActiveTab] = useState('related');
  const [hoveredConcept, setHoveredConcept] = useState(null);
  const [showPath, setShowPath] = useState(null);

  // Get concept data
  const conceptDetails = useMemo(() => 
    getConceptDetails(subject, currentConcept),
    [subject, currentConcept]
  );

  const relatedConcepts = useMemo(() => 
    getRelatedConcepts(subject, currentConcept),
    [subject, currentConcept]
  );

  const nextSuggestions = useMemo(() => 
    getNextConcepts(subject, masteredConcepts).slice(0, 5),
    [subject, masteredConcepts]
  );

  // Check if concept is mastered
  const isMastered = useCallback((concept) => 
    masteredConcepts.includes(concept),
    [masteredConcepts]
  );

  // Handle concept click
  const handleConceptClick = useCallback((concept) => {
    onConceptSelect?.(concept);
  }, [onConceptSelect]);

  // Format concept name
  const formatName = (name) => 
    name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

  // Render concept chip
  const ConceptChip = ({ concept, type, showArrow = false }) => {
    const mastered = isMastered(concept);
    const isHovered = hoveredConcept === concept;
    
    const typeColors = {
      prerequisite: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300',
      leads_to: 'bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800 text-purple-700 dark:text-purple-300',
      related: 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300',
      suggestion: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-700 dark:text-green-300',
    };

    return (
      <motion.button
        onClick={() => handleConceptClick(concept)}
        onMouseEnter={() => setHoveredConcept(concept)}
        onMouseLeave={() => setHoveredConcept(null)}
        className={`
          relative flex items-center gap-2 px-3 py-2 rounded-lg border transition-all
          ${typeColors[type] || typeColors.related}
          ${isHovered ? 'shadow-md scale-105' : ''}
          hover:shadow-md
        `}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        {mastered && (
          <CheckCircle className="w-4 h-4 text-green-500" />
        )}
        <span className="text-sm font-medium">{formatName(concept)}</span>
        {showArrow && <ArrowRight className="w-4 h-4 opacity-50" />}
        
        {/* Hover tooltip */}
        <AnimatePresence>
          {isHovered && (
            <motion.div
              className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded whitespace-nowrap z-10"
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 5 }}
            >
              Click to explore
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>
    );
  };

  if (!conceptDetails) {
    return (
      <div className="p-4 text-center text-gray-500">
        Concept not found in knowledge graph
      </div>
    );
  }

  return (
    <motion.div
      className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {/* Header */}
      <div className="px-4 py-3 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Link2 className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            <h3 className="font-semibold text-gray-800 dark:text-gray-200">
              Concept Navigator
            </h3>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              ✕
            </button>
          )}
        </div>
        
        {/* Current concept */}
        <div className="mt-2 flex items-center gap-2">
          <span className="text-lg font-bold text-gray-900 dark:text-white">
            {conceptDetails.name}
          </span>
          <span className={`px-2 py-0.5 text-xs rounded-full ${DIFFICULTY_COLORS[conceptDetails.difficulty]?.bg} ${DIFFICULTY_COLORS[conceptDetails.difficulty]?.text}`}>
            {conceptDetails.difficulty}
          </span>
          {isMastered(currentConcept) && (
            <span className="flex items-center gap-1 px-2 py-0.5 text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full">
              <CheckCircle className="w-3 h-3" /> Mastered
            </span>
          )}
        </div>
        
        {/* Chapter info */}
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {conceptDetails.chapter} • Class {conceptDetails.class?.join(', ')}
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-700">
        {[
          { id: 'related', label: 'Related', icon: Link2 },
          { id: 'path', label: 'Learn Path', icon: TrendingUp },
          { id: 'suggestions', label: 'Next Up', icon: Sparkles },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2.5 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-500 bg-indigo-50/50 dark:bg-indigo-900/20'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="p-4">
        <AnimatePresence mode="wait">
          {/* Related Concepts Tab */}
          {activeTab === 'related' && (
            <motion.div
              key="related"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              className="space-y-4"
            >
              {/* Prerequisites */}
              {relatedConcepts.prerequisites?.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <BookOpen className="w-4 h-4 text-blue-500" />
                    <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Prerequisites (Learn First)
                    </h4>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {relatedConcepts.prerequisites.map((concept) => (
                      <ConceptChip key={concept} concept={concept} type="prerequisite" />
                    ))}
                  </div>
                </div>
              )}

              {/* Leads To */}
              {relatedConcepts.leads_to?.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Target className="w-4 h-4 text-purple-500" />
                    <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Leads To (Learn Next)
                    </h4>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {relatedConcepts.leads_to.map((concept) => (
                      <ConceptChip key={concept} concept={concept} type="leads_to" showArrow />
                    ))}
                  </div>
                </div>
              )}

              {/* Related */}
              {relatedConcepts.related?.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Lightbulb className="w-4 h-4 text-yellow-500" />
                    <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Related Concepts
                    </h4>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {relatedConcepts.related.map((concept) => (
                      <ConceptChip key={concept} concept={concept} type="related" />
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {/* Learning Path Tab */}
          {activeTab === 'path' && (
            <motion.div
              key="path"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              className="space-y-4"
            >
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                Your learning journey for {conceptDetails.name}:
              </p>
              
              {/* Prerequisites chain */}
              <div className="relative">
                {conceptDetails.allPrerequisites?.length > 0 ? (
                  <div className="space-y-2">
                    {conceptDetails.allPrerequisites.map((prereq, idx) => (
                      <motion.div
                        key={prereq}
                        className="flex items-center gap-3"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.1 }}
                      >
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          isMastered(prereq) 
                            ? 'bg-green-100 dark:bg-green-900/30' 
                            : 'bg-gray-100 dark:bg-gray-700'
                        }`}>
                          {isMastered(prereq) ? (
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          ) : (
                            <span className="text-xs font-bold text-gray-500">{idx + 1}</span>
                          )}
                        </div>
                        <button
                          onClick={() => handleConceptClick(prereq)}
                          className={`text-sm font-medium ${
                            isMastered(prereq)
                              ? 'text-green-600 dark:text-green-400 line-through opacity-70'
                              : 'text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400'
                          }`}
                        >
                          {formatName(prereq)}
                        </button>
                        {idx < conceptDetails.allPrerequisites.length - 1 && (
                          <ChevronRight className="w-4 h-4 text-gray-400" />
                        )}
                      </motion.div>
                    ))}
                    
                    {/* Current concept */}
                    <motion.div
                      className="flex items-center gap-3 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: conceptDetails.allPrerequisites.length * 0.1 }}
                    >
                      <div className="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
                        <Target className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                      </div>
                      <span className="text-sm font-bold text-indigo-600 dark:text-indigo-400">
                        {conceptDetails.name} (Current)
                      </span>
                    </motion.div>
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <CheckCircle className="w-8 h-8 text-green-500 mx-auto mb-2" />
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      No prerequisites! You can start learning this directly.
                    </p>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* Suggestions Tab */}
          {activeTab === 'suggestions' && showSuggestions && (
            <motion.div
              key="suggestions"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              className="space-y-3"
            >
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                Based on your progress, we recommend:
              </p>
              
              {nextSuggestions.length > 0 ? (
                nextSuggestions.map((suggestion, idx) => (
                  <motion.button
                    key={suggestion.concept}
                    onClick={() => handleConceptClick(suggestion.concept)}
                    className="w-full flex items-center gap-3 p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-green-300 dark:hover:border-green-700 hover:bg-green-50 dark:hover:bg-green-900/20 transition-all text-left"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    whileHover={{ scale: 1.01 }}
                  >
                    <div className="w-8 h-8 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                      <Sparkles className="w-4 h-4 text-green-600 dark:text-green-400" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-800 dark:text-gray-200">
                        {formatName(suggestion.concept)}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {suggestion.chapter} • {suggestion.difficulty}
                      </p>
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-400" />
                  </motion.button>
                ))
              ) : (
                <div className="text-center py-4">
                  <Lock className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Complete more concepts to unlock suggestions!
                  </p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Mini Map (Visual representation) */}
      {showMiniMap && (
        <div className="px-4 pb-4">
          <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
            <h4 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
              Concept Map
            </h4>
            <div className="flex items-center justify-center gap-2 flex-wrap">
              {relatedConcepts.prerequisites?.slice(0, 2).map((c) => (
                <span key={c} className="px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded">
                  {formatName(c)}
                </span>
              ))}
              <ChevronRight className="w-4 h-4 text-gray-400" />
              <span className="px-3 py-1 text-xs bg-indigo-500 text-white rounded-full font-medium">
                {conceptDetails.name}
              </span>
              <ChevronRight className="w-4 h-4 text-gray-400" />
              {relatedConcepts.leads_to?.slice(0, 2).map((c) => (
                <span key={c} className="px-2 py-1 text-xs bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded">
                  {formatName(c)}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default ConceptNavigator;



