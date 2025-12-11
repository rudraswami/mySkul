/**
 * SmartBoard - Interactive Visual Learning Panel
 * ==============================================
 * 
 * The right-side panel in the Digital Classroom layout.
 * Renders visual artifacts from the AI tutor.
 * 
 * Features:
 * - Animated visual transitions (Spring physics)
 * - Beautiful empty state with guidance
 * - Non-scrollable fixed panel
 * - Dot pattern background ("The Druv Vibe")
 * - Academic serif typography for titles
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Sparkles,
  Lightbulb,
  Palette,
  Zap,
  BookOpen,
  Play,
  Maximize2,
  Minimize2,
  Eye
} from 'lucide-react';

// Import the Visual Engine - with safe fallback
let ConfigDrivenSketch;
try {
  ConfigDrivenSketch = require('../../visual-engine').ConfigDrivenSketch;
} catch (e) {
  ConfigDrivenSketch = null;
}

// Import VisualSketchViewer
import VisualSketchViewer from '../visual/VisualSketchViewer';

// Empty State Component - Premium Design
const EmptyBoardState = () => {
  const [currentTipIndex, setCurrentTipIndex] = useState(0);
  
  const tips = [
    { icon: Lightbulb, color: 'purple', text: 'Explain Newton\'s laws with visuals', emoji: '💡' },
    { icon: Zap, color: 'orange', text: 'Show me how photosynthesis works', emoji: '⚡' },
    { icon: BookOpen, color: 'green', text: 'Draw the cell structure', emoji: '📖' },
    { icon: Eye, color: 'blue', text: 'Visualize projectile motion', emoji: '👁️' },
  ];
  
  // Rotate tips every 4 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTipIndex((prev) => (prev + 1) % tips.length);
    }, 4000);
    return () => clearInterval(interval);
  }, [tips.length]);

  const colorClasses = {
    purple: { bg: 'bg-purple-100', text: 'text-purple-600', border: 'border-purple-200' },
    orange: { bg: 'bg-orange-100', text: 'text-orange-600', border: 'border-orange-200' },
    green: { bg: 'bg-green-100', text: 'text-green-600', border: 'border-green-200' },
    blue: { bg: 'bg-blue-100', text: 'text-blue-600', border: 'border-blue-200' },
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="flex flex-col items-center justify-center h-full text-center px-8 py-12"
    >
      {/* Animated Icon Container */}
      <motion.div
        className="relative mb-8"
        animate={{ 
          y: [0, -8, 0],
        }}
        transition={{ 
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        {/* Main Icon */}
        <div className="w-28 h-28 bg-gradient-to-br from-purple-100 via-white to-orange-100 rounded-3xl flex items-center justify-center shadow-xl border border-purple-100/50">
          <motion.div
            animate={{ 
              scale: [1, 1.1, 1],
              rotate: [0, 5, -5, 0]
            }}
            transition={{ 
              duration: 4,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          >
            <Palette className="w-14 h-14 text-purple-500" />
          </motion.div>
        </div>
        
        {/* Floating Sparkle */}
        <motion.div
          animate={{ 
            scale: [0.8, 1.2, 0.8],
            rotate: [0, 180, 360]
          }}
          transition={{ duration: 3, repeat: Infinity }}
          className="absolute -top-3 -right-3 w-10 h-10 bg-gradient-to-br from-orange-400 to-orange-500 rounded-xl flex items-center justify-center shadow-lg"
        >
          <Sparkles className="w-5 h-5 text-white" />
        </motion.div>
        
        {/* Secondary decorative dot */}
        <motion.div
          animate={{ scale: [1, 1.3, 1] }}
          transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
          className="absolute -bottom-2 -left-2 w-6 h-6 bg-purple-400 rounded-full opacity-60"
        />
      </motion.div>

      {/* Title - Academic Serif */}
      <h3 
        className="text-2xl font-bold text-gray-800 mb-3"
        style={{ fontFamily: "'Merriweather', 'Georgia', serif" }}
      >
        Your Visual SmartBoard
      </h3>
      
      {/* Subtitle */}
      <p className="text-gray-500 text-sm max-w-sm mb-8 leading-relaxed">
        Ask me anything! I'll draw concepts, diagrams, and visualizations right here to help you understand better.
      </p>

      {/* Animated Tips Carousel */}
      <div className="w-full max-w-sm">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
          Try asking...
        </p>
        <div className="relative h-16 overflow-hidden">
          <AnimatePresence mode="wait">
            {tips.map((tip, index) => {
              if (index !== currentTipIndex) return null;
              const colors = colorClasses[tip.color];
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                  className={`absolute inset-x-0 flex items-center gap-4 p-4 bg-white/80 backdrop-blur-sm rounded-2xl border ${colors.border} shadow-sm`}
                >
                  <div className={`w-10 h-10 ${colors.bg} rounded-xl flex items-center justify-center flex-shrink-0`}>
                    <tip.icon className={`w-5 h-5 ${colors.text}`} />
                  </div>
                  <p className="text-sm text-gray-700 text-left font-medium">
                    "{tip.text}"
                  </p>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
        
        {/* Tip Indicators */}
        <div className="flex justify-center gap-2 mt-4">
          {tips.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentTipIndex(index)}
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                index === currentTipIndex 
                  ? 'bg-purple-500 w-6' 
                  : 'bg-gray-300 hover:bg-gray-400'
              }`}
            />
          ))}
        </div>
      </div>
    </motion.div>
  );
};

// Main SmartBoard Component
export default function SmartBoard({ 
  artifact = null,
  onFullscreen,
  className = '',
  isFullscreen = false
}) {
  // Determine what type of visual to render
  const hasVisual = artifact && (
    artifact.svg || 
    artifact.visual_sketch?.svg || 
    artifact.blueprint ||
    artifact.template ||
    artifact.mode
  );

  return (
    <div 
      className={`flex flex-col h-full bg-slate-50 relative overflow-hidden ${className}`}
      style={{
        backgroundImage: 'radial-gradient(circle at 1px 1px, #e5e7eb 1px, transparent 0)',
        backgroundSize: '24px 24px'
      }}
    >
      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-50/30 via-transparent to-orange-50/20 pointer-events-none" />
      
      {/* Header Bar - Glassmorphic */}
      <div className="relative z-10 flex-shrink-0 px-4 py-3 bg-white/70 backdrop-blur-md border-b border-gray-200/50 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className={`w-2.5 h-2.5 rounded-full ${hasVisual ? 'bg-green-500' : 'bg-gray-400'}`} />
            {hasVisual && (
              <div className="absolute inset-0 w-2.5 h-2.5 rounded-full bg-green-500 animate-ping opacity-50" />
            )}
          </div>
          <span 
            className="text-sm font-semibold text-gray-700"
            style={{ fontFamily: "'Merriweather', 'Georgia', serif" }}
          >
            {hasVisual ? '🎨 Visual Ready' : '📺 SmartBoard'}
          </span>
        </div>
        
        {hasVisual && onFullscreen && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onFullscreen}
            className="flex items-center gap-1.5 px-3 py-1.5 text-gray-500 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-all text-sm font-medium"
            title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          >
            {isFullscreen ? (
              <Minimize2 className="w-4 h-4" />
            ) : (
              <Maximize2 className="w-4 h-4" />
            )}
            <span className="hidden sm:inline">{isFullscreen ? 'Exit' : 'Expand'}</span>
          </motion.button>
        )}
      </div>

      {/* Main Content Area */}
      <div className="relative z-0 flex-1 flex items-center justify-center p-4 overflow-auto">
        <AnimatePresence mode="wait">
          {!hasVisual ? (
            <EmptyBoardState key="empty" />
          ) : (
            <motion.div
              key="visual"
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: -10 }}
              transition={{ 
                type: 'spring', 
                stiffness: 300, 
                damping: 25,
                mass: 0.8
              }}
              className="w-full max-w-2xl"
            >
              {/* Visual Card Container - Premium Design */}
              <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden ring-1 ring-black/5">
                {/* Visual Title Bar */}
                {artifact.concept && (
                  <div className="px-4 py-3 bg-gradient-to-r from-purple-50 to-orange-50 border-b border-gray-100">
                    <h4 
                      className="text-base font-semibold text-gray-800"
                      style={{ fontFamily: "'Merriweather', 'Georgia', serif" }}
                    >
                      {artifact.concept}
                    </h4>
                    {artifact.subject && (
                      <span className="inline-flex items-center gap-1 mt-1 px-2 py-0.5 bg-white/80 rounded-full text-xs font-medium text-purple-600">
                        {artifact.subject}
                      </span>
                    )}
                  </div>
                )}
                
                {/* Visual Content */}
                <div className="p-2">
                  {ConfigDrivenSketch && (artifact.blueprint || artifact.template || artifact.mode) ? (
                    // Use ConfigDrivenSketch for blueprint-based visuals
                    <ConfigDrivenSketch
                      blueprint={artifact.blueprint || artifact}
                      concept={artifact.concept}
                      subject={artifact.subject}
                      professorOutput={artifact.professorOutput}
                      renderDirectives={artifact.render_directives}
                    />
                  ) : artifact.svg || artifact.visual_sketch?.svg ? (
                    // Use VisualSketchViewer for SVG-based visuals
                    <VisualSketchViewer
                      visualData={artifact.visual_sketch || artifact}
                      concept={artifact.concept}
                      subject={artifact.subject}
                    />
                  ) : (
                    // Fallback empty state
                    <div className="p-8 text-center text-gray-400">
                      <Palette className="w-12 h-12 mx-auto mb-3 opacity-50" />
                      <p>Visual data format not recognized</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Visual Caption */}
              {artifact.caption && (
                <motion.p
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="text-center text-sm text-gray-500 mt-4 italic"
                >
                  {artifact.caption}
                </motion.p>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer Hint - Only when empty */}
      {!hasVisual && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="relative z-10 flex-shrink-0 px-4 py-3 bg-gradient-to-t from-white/80 to-transparent border-t border-gray-100/50"
        >
          <p className="text-xs text-center text-gray-400 font-medium">
            ✨ Visuals appear here automatically when I explain concepts
          </p>
        </motion.div>
      )}
    </div>
  );
}

// Toast notification for new visual - Premium Design
export const VisualToast = ({ show, onClose }) => {
  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ opacity: 0, y: 30, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -20, scale: 0.95 }}
          transition={{ type: 'spring', stiffness: 400, damping: 25 }}
          className="fixed bottom-24 left-1/2 -translate-x-1/2 z-50 md:hidden"
        >
          <button
            onClick={onClose}
            className="flex items-center gap-3 px-5 py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-2xl shadow-xl shadow-purple-500/30 hover:shadow-purple-500/40 transition-shadow"
          >
            <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
              <Sparkles className="w-4 h-4" />
            </div>
            <div className="text-left">
              <p className="text-sm font-semibold">I've drawn this on the Board!</p>
              <p className="text-xs text-purple-200">Tap to view →</p>
            </div>
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
