/**
 * Visual Sketch Viewer Component (V5.0)
 * Displays interactive animated visual explanations using SketchSense V5.0
 */
import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Maximize2, Sparkles, BookOpen, Trophy, Share2 } from 'lucide-react';

// Import SketchSense V6 Magic Notebook Engine
import UniversalSketchCanvas from '../../visual-engine/sketch/UniversalSketchCanvasV6';

// Check if concept has interactive template
const hasInteractiveTemplate = (question) => {
  if (!question) return false;
  const concepts = [
    'force', 'motion', 'velocity', 'acceleration', 'gravity', 'friction', 
    'momentum', 'newton', 'energy', 'wave', 'photosynthesis', 'cell',
    'atom', 'acid', 'base', 'dna', 'respiration', 'quadratic', 'pythagoras'
  ];
  const lowerQ = question.toLowerCase();
  return concepts.some(c => lowerQ.includes(c));
};

// Extract concept from question
const extractConcept = (question) => {
  if (!question) return 'force';
  const lowerQ = question.toLowerCase();
  
  const conceptMap = {
    'velocity': 'velocity',
    'speed': 'velocity',
    'motion': 'velocity',
    'force': 'force',
    'push': 'force',
    'pull': 'force',
    'gravity': 'gravity',
    'fall': 'gravity',
    'photosynthesis': 'photosynthesis',
    'plant': 'photosynthesis',
    'cell': 'cell',
    'atom': 'atom',
  };
  
  for (const [keyword, concept] of Object.entries(conceptMap)) {
    if (lowerQ.includes(keyword)) {
      return concept;
    }
  }
  
  return 'force'; // default
};

const VisualSketchViewer = ({ 
  svg, 
  metaphors = [], 
  estimatedMarks, 
  onClose, 
  onShare, 
  embedded = false,
  question = '',
  studentProfile = null,
  whiteboardVisual = null, // New prop for whiteboard visual data
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [currentLayer, setCurrentLayer] = useState(0);

  // Check if we should use the new Interactive Visual Engine
  const shouldUseInteractive = useMemo(() => {
    return hasInteractiveTemplate(question) || whiteboardVisual;
  }, [question, whiteboardVisual]);

  const concept = useMemo(() => {
    if (whiteboardVisual?.concept) return whiteboardVisual.concept;
    return extractConcept(question);
  }, [question, whiteboardVisual]);

  const subject = useMemo(() => {
    if (whiteboardVisual?.subject) return whiteboardVisual.subject;
    if (studentProfile?.subject) return studentProfile.subject;
    return 'physics';
  }, [whiteboardVisual, studentProfile]);

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 300);
    return () => clearTimeout(timer);
  }, [svg]);

  // Handle click-to-advance layers (for static SVG)
  const handleSvgClick = () => {
    if (embedded && !isExpanded) {
      setIsExpanded(true);
    } else {
      setCurrentLayer(prev => prev + 1);
    }
  };

  // If we have an interactive template - use UniversalSketchCanvas (SketchSense V5.0)!
  if (shouldUseInteractive) {
    return (
      <div className="my-4">
        <UniversalSketchCanvas
          blueprint={{ concept, subject }}
          question={question}
          subject={subject}
          enableValidation={true}
          enableFeedback={true}
          style={{ minHeight: '400px', borderRadius: '12px' }}
        />
      </div>
    );
  }

  // Fallback: Show static SVG if no interactive template
  if (!svg) return null;

  // Embedded compact view
  if (embedded && !isExpanded) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="my-6 rounded-xl overflow-hidden border-2 border-purple-200 dark:border-purple-700 bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-900 dark:to-indigo-900 shadow-lg cursor-pointer hover:shadow-xl transition-all"
        onClick={handleSvgClick}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-100 to-indigo-100 dark:from-purple-800 dark:to-indigo-800 p-3 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Sparkles className="h-4 w-4 text-purple-600 dark:text-purple-300" />
            <span className="text-sm font-semibold text-gray-900 dark:text-white">Visual Explanation</span>
            {estimatedMarks && (
              <span className="text-xs px-2 py-0.5 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded-full">
                {estimatedMarks} marks
              </span>
            )}
          </div>
          <Maximize2 className="h-4 w-4 text-gray-600 dark:text-gray-400" />
        </div>
        
        {/* SVG Preview */}
        <div className="bg-white dark:bg-gray-800 p-4 max-h-64 overflow-hidden">
          <div 
            className="w-full flex justify-center items-center"
            dangerouslySetInnerHTML={{ __html: svg }}
            style={{ minHeight: '200px' }}
          />
        </div>
        
        {/* Hint */}
        <div className="bg-purple-50 dark:bg-purple-900 p-2 text-center">
          <p className="text-xs text-gray-600 dark:text-gray-400">
            💡 Click to expand • Tap to reveal layers
          </p>
        </div>
      </motion.div>
    );
  }

  // Fullscreen/Expanded mode
  return (
    <AnimatePresence>
      {isExpanded && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 bg-black bg-opacity-75 flex items-center justify-center p-4"
          onClick={() => setIsExpanded(false)}
        >
          <motion.div
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.9, y: 20 }}
            className="relative bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-4xl w-full h-full max-h-[90vh] overflow-hidden flex flex-col"
            onClick={e => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-purple-100 to-indigo-100 dark:from-purple-800 dark:to-indigo-800">
              <div className="flex items-center space-x-2">
                <Sparkles className="h-5 w-5 text-purple-600 dark:text-purple-300" />
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">Visual Explanation</h3>
                {estimatedMarks && (
                  <span className="px-3 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded-full text-sm font-medium">
                    {estimatedMarks} marks
                  </span>
                )}
              </div>
              <div className="flex items-center space-x-2">
                {onShare && (
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={onShare}
                    className="p-2 rounded-full bg-purple-200 dark:bg-purple-700 text-purple-800 dark:text-purple-200 hover:bg-purple-300 dark:hover:bg-purple-600 transition-colors"
                    title="Share Visual"
                  >
                    <Share2 className="h-5 w-5" />
                  </motion.button>
                )}
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setIsExpanded(false)}
                  className="p-2 rounded-full bg-red-100 dark:bg-red-700 text-red-800 dark:text-red-200 hover:bg-red-200 dark:hover:bg-red-600 transition-colors"
                  title="Close"
                >
                  <X className="h-5 w-5" />
                </motion.button>
              </div>
            </div>

            {/* SVG Content */}
            <div className="flex-grow flex items-center justify-center p-4 overflow-auto bg-gray-50 dark:bg-gray-900">
              {isLoading ? (
                <div className="text-gray-500 dark:text-gray-400 flex flex-col items-center">
                  <Sparkles className="h-10 w-10 animate-pulse mb-2" />
                  Loading visual...
                </div>
              ) : (
                <div 
                  className="max-w-full max-h-full cursor-pointer"
                  dangerouslySetInnerHTML={{ __html: svg }}
                  onClick={handleSvgClick}
                />
              )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-700 flex flex-wrap items-center justify-between gap-3">
              {metaphors && metaphors.length > 0 && (
                <div className="flex items-center space-x-2 text-sm text-gray-700 dark:text-gray-300">
                  <BookOpen className="h-4 w-4" />
                  <span>Metaphors: {metaphors.join(', ')}</span>
                </div>
              )}
              {estimatedMarks && (
                <div className="flex items-center space-x-2 text-sm text-gray-700 dark:text-gray-300">
                  <Trophy className="h-4 w-4" />
                  <span>Estimated Marks: {estimatedMarks}</span>
                </div>
              )}
              {currentLayer > 0 && (
                <div className="flex items-center space-x-2 text-sm text-purple-700 dark:text-purple-300">
                  <Sparkles className="h-4 w-4" />
                  <span>Layer {currentLayer}</span>
                </div>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default VisualSketchViewer;
