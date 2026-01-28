/**
 * SmartBoard - Interactive Visual Learning Panel ("Magic Notebook")
 * ==================================================================
 * 
 * The right-side panel in the Digital Classroom layout.
 * Renders visual artifacts from the AI tutor with a SKETCH aesthetic.
 * 
 * Features:
 * - 🎨 Magic Notebook theme (hand-drawn, sketchy, warm)
 * - 📐 Dot-grid paper background
 * - ✏️ Handwriting font (Patrick Hand)
 * - 📝 Live Formula Sticky Notes
 * - Animated visual transitions (Spring physics)
 * - Beautiful empty state with guidance
 * 
 * SketchSense V5.0 Compatible
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
  Eye,
  PenTool
} from 'lucide-react';

// ============================================
// SKETCHSENSE THEME CONSTANTS
// ============================================
const SKETCH_THEME = {
  // Notebook paper background
  notebookBg: '#fdfcf8',
  gridColor: '#cbd5e1',
  gridSize: '20px',
  
  // Highlighter colors (warm, playful)
  highlightYellow: '#fde047',
  highlightBlue: '#3b82f6',
  highlightRed: '#ef4444',
  highlightGreen: '#22c55e',
  highlightOrange: '#f97316',
  
  // Sticky note colors
  stickyYellow: '#fef3c7',
  stickyBorder: '#fcd34d',
};

// Inline style for handwriting font (Patrick Hand)
const fontSketchStyle = {
  fontFamily: "'Patrick Hand', 'Comic Sans MS', 'Segoe Print', cursive",
  letterSpacing: '0.02em',
};

// ============================================
// 🎬 DEMO VISUAL SYSTEM (VC Demo)
// ============================================
// Hardcoded premium visuals for demo questions - 100% reliable
let DemoVisualRenderer = null;
let isDemoQuestion = null;
let getDemoConfig = null;
let DEMO_SYSTEM_AVAILABLE = false;
try {
  const demoModule = require('../../netra/demo');
  DemoVisualRenderer = demoModule.DemoVisualRenderer;
  isDemoQuestion = demoModule.isDemoQuestion;
  getDemoConfig = demoModule.getDemoConfig;
  DEMO_SYSTEM_AVAILABLE = !!(DemoVisualRenderer && isDemoQuestion);
  console.log('🎬 DEMO Visual System loaded successfully');
} catch (err) {
  console.warn('⚠️ Demo Visual System not available:', err.message);
}

// ============================================
// NETRA v4.0 - VISUAL INTELLIGENCE ENGINE
// ============================================
// Import NETRA v4 - AI-powered image generation
let NetraEngineV4 = null;
let NETRA_V4_AVAILABLE = false;
try {
  const netraV4Module = require('../../netra/v4');
  NetraEngineV4 = netraV4Module.NetraEngineV4;
  NETRA_V4_AVAILABLE = !!NetraEngineV4;
  console.log('🔮 NETRA v4.0 Engine loaded successfully');
} catch (err) {
  console.warn('⚠️ NETRA v4.0 failed to load:', err.message);
}

// ============================================
// NETRA - VISUAL REASONING ENGINE (v7.0) - Legacy
// ============================================
// Import NETRA - The new semantic visual reasoning engine
// Wrapped in try-catch to prevent breaking if NETRA fails to load
let NetraEngine = null;
let NETRA_AVAILABLE = false;
try {
  const netraModule = require('../../netra');
  NetraEngine = netraModule.NetraEngine;
  NETRA_AVAILABLE = !!NetraEngine;
  console.log('🔮 NETRA Engine (legacy) loaded successfully');
} catch (err) {
  console.warn('⚠️ NETRA Engine failed to load, falling back to V6:', err.message);
}

// Legacy fallback - MagicNotebookEngine V6
import MagicNotebookEngine from '../../visual-engine/MagicNotebookEngine';

// Legacy V5 fallback
import UniversalSketchCanvas, { 
  NOTEBOOK_THEME,
  GhostMentor,
} from '../../visual-engine/sketch/UniversalSketchCanvasV6';

// NETRA is DEFAULT (if available) - Semantic visual reasoning
// Automatically falls back to V6 if NETRA fails to load
const USE_NETRA_ENGINE = NETRA_AVAILABLE;
const USE_MAGIC_NOTEBOOK_V6 = !USE_NETRA_ENGINE;

// ============================================
// NETRA v5.0 - DYNAMIC VISUAL RENDERER
// ============================================
// New composition-based renderer with atoms, behaviors, narration
let DynamicVisualRenderer = null;
let COMPOSITION_MODE_AVAILABLE = false;
try {
  const rendererModule = require('../../netra/renderer/DynamicVisualRenderer');
  DynamicVisualRenderer = rendererModule.default || rendererModule.DynamicVisualRenderer;
  COMPOSITION_MODE_AVAILABLE = !!DynamicVisualRenderer;
  console.log('🎨 NETRA DynamicVisualRenderer loaded successfully');
} catch (err) {
  console.warn('⚠️ DynamicVisualRenderer not available:', err.message);
}

// Import Sketch Primitives for direct use
import {
  SketchFilters,
} from '../../visual-engine/sketch/SketchPrimitives';

// Import SketchyFilterDefs for SVG filter definitions
import { SketchyFilterDefs } from './templates/SketchyFilters';

// Legacy fallback - only used if V6 fails
let ConfigDrivenSketch = null;
try {
  ConfigDrivenSketch = require('../../visual-engine').ConfigDrivenSketch;
} catch (e) {
  console.warn('ConfigDrivenSketch fallback not available');
}

// Import VisualSketchViewer for legacy SVG-only visuals
import VisualSketchViewer from '../visual/VisualSketchViewer';

// Import SketchSense Theme
import './styles/SketchTheme.css';

// ============================================
// NETRA v4 IMAGE RENDERER
// ============================================
const NetraV4ImageRenderer = ({ visual, teaching, onTeachingStart }) => {
  const [showTeaching, setShowTeaching] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  
  if (!visual?.image_base64) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        <p>Visual loading...</p>
      </div>
    );
  }
  
  const imageUrl = `data:image/${visual.image_format || 'png'};base64,${visual.image_base64}`;
  const steps = teaching?.steps || [];
  const hotspots = teaching?.hotspots || [];
  
  return (
    <div className="relative w-full h-full">
      {/* Generated Image */}
      <motion.img
        src={imageUrl}
        alt={teaching?.title || "Educational visual"}
        className="w-full h-full object-contain"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      />
      
      {/* Teaching Overlay */}
      {showTeaching && steps.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="absolute inset-0 bg-black/40"
        >
          {/* Hotspots */}
          {hotspots.map((hotspot, idx) => (
            <div
              key={hotspot.id || idx}
              className="absolute border-2 border-blue-400 bg-blue-500/20 rounded-lg cursor-pointer hover:bg-blue-500/40 transition-colors"
              style={{
                left: `${hotspot.x_percent}%`,
                top: `${hotspot.y_percent}%`,
                width: `${hotspot.width_percent || 10}%`,
                height: `${hotspot.height_percent || 10}%`,
                transform: 'translate(-50%, -50%)',
              }}
              title={hotspot.description}
            >
              <span className="absolute -top-6 left-1/2 -translate-x-1/2 px-2 py-0.5 bg-gray-800 text-white text-xs rounded-full whitespace-nowrap">
                {hotspot.label}
              </span>
            </div>
          ))}
          
          {/* Narration Bar */}
          {steps[currentStep] && (
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              className="absolute bottom-0 left-0 right-0 bg-gray-900/90 backdrop-blur-sm text-white p-4"
            >
              <div className="flex items-center gap-2 mb-2">
                {steps.map((_, i) => (
                  <div
                    key={i}
                    className={`h-1 flex-1 rounded-full ${i <= currentStep ? 'bg-blue-500' : 'bg-gray-600'}`}
                  />
                ))}
              </div>
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center font-bold text-sm">
                  {currentStep + 1}
                </div>
                <div className="flex-1">
                  <p className="text-sm text-gray-300 mb-1">Step {currentStep + 1} of {steps.length}</p>
                  <p className="text-base">{steps[currentStep].narration}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
                    disabled={currentStep === 0}
                    className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 disabled:opacity-50"
                  >
                    ←
                  </button>
                  <button
                    onClick={() => setCurrentStep(Math.min(steps.length - 1, currentStep + 1))}
                    disabled={currentStep === steps.length - 1}
                    className="p-2 rounded-lg bg-blue-500 hover:bg-blue-400 disabled:opacity-50"
                  >
                    →
                  </button>
                  <button
                    onClick={() => setShowTeaching(false)}
                    className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 ml-2"
                  >
                    ✕
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </motion.div>
      )}
      
      {/* Title & Teaching Button */}
      <div className="absolute top-3 left-3 right-3 flex items-start justify-between">
        {teaching?.title && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="px-3 py-1.5 bg-white/90 backdrop-blur-sm rounded-lg shadow-sm"
          >
            <h3 className="text-sm font-semibold text-gray-800">{teaching.title}</h3>
          </motion.div>
        )}
        
        {steps.length > 0 && !showTeaching && (
          <motion.button
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5 }}
            onClick={() => setShowTeaching(true)}
            className="px-3 py-1.5 bg-blue-500 text-white rounded-lg shadow-lg hover:bg-blue-600 transition-colors text-sm font-medium flex items-center gap-2"
          >
            <Play size={14} />
            Learn Step-by-Step
          </motion.button>
        )}
      </div>
      
      {/* Key Takeaways */}
      {teaching?.key_takeaways?.length > 0 && !showTeaching && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="absolute bottom-3 left-3 right-3 px-3 py-2 bg-white/90 backdrop-blur-sm rounded-lg shadow-sm"
        >
          <p className="text-xs text-gray-500 mb-1">💡 Key Takeaways</p>
          <ul className="text-xs text-gray-700 space-y-0.5">
            {teaching.key_takeaways.slice(0, 2).map((takeaway, i) => (
              <li key={i}>• {takeaway}</li>
            ))}
          </ul>
        </motion.div>
      )}
    </div>
  );
};

// ============================================
// LIVE FORMULA STICKY NOTE (Magic Notebook Feature)
// ============================================
const FormulaStickyNote = ({ formula, concept }) => {
  if (!formula) return null;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: -10, rotate: 0 }}
      animate={{ opacity: 1, y: 0, rotate: -1 }}
      exit={{ opacity: 0, y: -10 }}
      className="absolute top-4 left-4 z-20"
      style={{
        transform: 'rotate(-1deg)',
      }}
    >
      <div 
        className="px-4 py-3 rounded-lg shadow-md border"
        style={{
          backgroundColor: SKETCH_THEME.stickyYellow,
          borderColor: SKETCH_THEME.stickyBorder,
          maxWidth: '220px',
        }}
      >
        {/* Sticky note "pin" */}
        <div 
          className="absolute -top-2 left-1/2 -translate-x-1/2 w-4 h-4 rounded-full shadow-sm"
          style={{ backgroundColor: SKETCH_THEME.highlightRed }}
        />
        
        {/* Label */}
        <p 
          className="text-xs text-amber-700 uppercase tracking-wide mb-1"
          style={fontSketchStyle}
        >
          📐 Key Formula
        </p>
        
        {/* Formula */}
        <p 
          className="text-lg text-gray-800 font-medium"
          style={{
            ...fontSketchStyle,
            fontSize: '1.1rem',
          }}
        >
          {formula}
        </p>
        
        {/* Concept label if available */}
        {concept && (
          <p 
            className="text-xs text-amber-600 mt-1 italic"
            style={fontSketchStyle}
          >
            — {concept}
          </p>
        )}
      </div>
    </motion.div>
  );
};

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

      {/* Title - Sketch Style */}
      <h3 
        className="text-2xl font-bold text-gray-800 mb-3"
        style={fontSketchStyle}
      >
        📓 Your Magic Notebook
      </h3>
      
      {/* Subtitle */}
      <p 
        className="text-gray-500 text-sm max-w-sm mb-8 leading-relaxed"
        style={fontSketchStyle}
      >
        Ask me anything! I'll sketch concepts, diagrams, and visualizations right here to help you understand better.
      </p>

      {/* Animated Tips Carousel */}
      <div className="w-full max-w-md px-4">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4 text-center">
          Try asking...
        </p>
        <div className="relative min-h-[72px]">
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
                  className={`flex items-center gap-4 p-4 bg-white/90 backdrop-blur-sm rounded-2xl border ${colors.border} shadow-lg`}
                >
                  <div className={`w-12 h-12 ${colors.bg} rounded-xl flex items-center justify-center flex-shrink-0`}>
                    <tip.icon className={`w-6 h-6 ${colors.text}`} />
                  </div>
                  <p className="text-base text-gray-700 text-left font-medium flex-1">
                    "{tip.text}"
                  </p>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
        
        {/* Tip Indicators */}
        <div className="flex justify-center items-center gap-3 mt-6">
          {tips.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentTipIndex(index)}
              className={`h-2 rounded-full transition-all duration-300 ${
                index === currentTipIndex 
                  ? 'bg-purple-500 w-8' 
                  : 'bg-gray-300 hover:bg-gray-400 w-2'
              }`}
            />
          ))}
        </div>
      </div>
    </motion.div>
  );
};

// ============================================
// LOADING SKELETON - "Sathi is Sketching..." Animation
// ============================================
const SketchingLoadingState = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex flex-col items-center justify-center h-full text-center px-8 py-12"
    >
      {/* Pulsing Grid Animation */}
      <div className="relative w-64 h-48 mb-8">
        {/* Animated grid dots */}
        <div 
          className="absolute inset-0 rounded-2xl overflow-hidden"
          style={{
            backgroundColor: 'rgba(255,255,255,0.8)',
            border: `2px solid ${SKETCH_THEME.gridColor}`,
          }}
        >
          {/* Animated pulsing grid pattern */}
          <motion.div
            className="absolute inset-0"
            style={{
              backgroundImage: `radial-gradient(${SKETCH_THEME.highlightBlue}40 2px, transparent 2px)`,
              backgroundSize: '16px 16px',
            }}
            animate={{
              opacity: [0.3, 0.7, 0.3],
              scale: [1, 1.02, 1],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
          
          {/* Animated "sketch" lines being drawn */}
          <svg className="absolute inset-0 w-full h-full" viewBox="0 0 256 192">
            {/* Animated line 1 */}
            <motion.path
              d="M 30 50 Q 80 30 130 60 T 220 50"
              fill="none"
              stroke={SKETCH_THEME.highlightBlue}
              strokeWidth="3"
              strokeLinecap="round"
              strokeDasharray="200"
              initial={{ strokeDashoffset: 200 }}
              animate={{ strokeDashoffset: [200, 0, 200] }}
              transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
            />
            {/* Animated line 2 */}
            <motion.path
              d="M 40 100 L 100 100 L 100 150 L 160 150"
              fill="none"
              stroke={SKETCH_THEME.highlightOrange}
              strokeWidth="3"
              strokeLinecap="round"
              strokeDasharray="180"
              initial={{ strokeDashoffset: 180 }}
              animate={{ strokeDashoffset: [180, 0, 180] }}
              transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
            />
            {/* Animated circle */}
            <motion.circle
              cx="200"
              cy="120"
              r="25"
              fill="none"
              stroke={SKETCH_THEME.highlightGreen}
              strokeWidth="3"
              strokeDasharray="160"
              initial={{ strokeDashoffset: 160 }}
              animate={{ strokeDashoffset: [160, 0, 160] }}
              transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
            />
          </svg>
        </div>
        
        {/* Floating pencil animation */}
        <motion.div
          className="absolute -top-4 -right-4 w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg"
          animate={{
            y: [0, -8, 0],
            rotate: [0, 10, 0, -10, 0],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          <PenTool className="w-6 h-6 text-white" />
        </motion.div>
        
        {/* Floating sparkle */}
        <motion.div
          className="absolute -bottom-2 -left-2"
          animate={{
            scale: [0.8, 1.2, 0.8],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
          }}
        >
          <Sparkles className="w-8 h-8 text-orange-400" />
        </motion.div>
      </div>
      
      {/* Text */}
      <h3 
        className="text-xl font-bold text-gray-800 mb-2"
        style={fontSketchStyle}
      >
        ✏️ Sathi is sketching...
      </h3>
      <p 
        className="text-gray-500 text-sm max-w-xs"
        style={fontSketchStyle}
      >
        Creating a visual explanation just for you!
      </p>
      
      {/* Progress dots */}
      <div className="flex gap-2 mt-6">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="w-2.5 h-2.5 rounded-full bg-purple-400"
            animate={{
              scale: [1, 1.4, 1],
              opacity: [0.4, 1, 0.4],
            }}
            transition={{
              duration: 1,
              repeat: Infinity,
              delay: i * 0.2,
            }}
          />
        ))}
      </div>
    </motion.div>
  );
};

// ============================================
// FALLBACK CONCEPT CARD - Generated locally when no visual arrives
// ============================================
const FallbackConceptCard = ({ topic, subject }) => {
  // Generate a local fallback when timeout occurs
  const getSubjectEmoji = () => {
    const lower = (subject || '').toLowerCase();
    if (lower.includes('physics')) return '⚛️';
    if (lower.includes('chemistry')) return '🧪';
    if (lower.includes('biology')) return '🧬';
    if (lower.includes('math')) return '📐';
    return '📚';
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="w-full max-w-md mx-auto"
    >
      <div 
        className="rounded-2xl shadow-lg overflow-hidden"
        style={{
          backgroundColor: 'white',
          border: `2px solid ${SKETCH_THEME.gridColor}`,
          transform: 'rotate(-1deg)',
        }}
      >
        {/* Header */}
        <div 
          className="px-6 py-5"
          style={{
            background: `linear-gradient(135deg, ${SKETCH_THEME.highlightBlue}20 0%, ${SKETCH_THEME.highlightBlue}10 100%)`,
            borderBottom: `2px dashed ${SKETCH_THEME.gridColor}`,
          }}
        >
          <div className="flex items-center gap-3">
            <div 
              className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl"
              style={{ backgroundColor: `${SKETCH_THEME.highlightBlue}20` }}
            >
              {getSubjectEmoji()}
            </div>
            <div>
              <h3 
                className="text-lg font-bold text-gray-800"
                style={fontSketchStyle}
              >
                {topic || 'Concept Overview'}
              </h3>
              {subject && (
                <span 
                  className="text-sm text-gray-500"
                  style={fontSketchStyle}
                >
                  {subject}
                </span>
              )}
            </div>
          </div>
        </div>
        
        {/* Content */}
        <div className="p-6 text-center">
          <motion.div
            animate={{ rotate: [0, 5, -5, 0] }}
            transition={{ duration: 3, repeat: Infinity }}
            className="text-5xl mb-4"
          >
            💡
          </motion.div>
          <p 
            className="text-gray-600 mb-4"
            style={fontSketchStyle}
          >
            I'm thinking about the best way to visualize this concept...
          </p>
          <p 
            className="text-sm text-gray-400"
            style={fontSketchStyle}
          >
            Check the explanation on the left for detailed information!
          </p>
        </div>
        
        {/* Footer */}
        <div 
          className="px-6 py-3"
          style={{
            backgroundColor: SKETCH_THEME.notebookBg,
            borderTop: `1px dashed ${SKETCH_THEME.gridColor}`,
          }}
        >
          <p 
            className="text-xs text-center text-gray-400"
            style={fontSketchStyle}
          >
            ✨ Complex visuals coming soon...
          </p>
        </div>
      </div>
    </motion.div>
  );
};

// Live Concept Card - Shows when chatting but no visual (Sketch Style)
const ConceptCard = ({ topic, formula, subject }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, rotate: 0 }}
      animate={{ opacity: 1, scale: 1, rotate: -0.5 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="w-full max-w-lg mx-auto"
    >
      <div 
        className="rounded-2xl shadow-lg overflow-hidden"
        style={{
          backgroundColor: 'white',
          border: `2px solid ${SKETCH_THEME.gridColor}`,
        }}
      >
        {/* Header - Sketch Style */}
        <div 
          className="px-6 py-4"
          style={{
            background: `linear-gradient(135deg, ${SKETCH_THEME.highlightYellow} 0%, ${SKETCH_THEME.stickyYellow} 100%)`,
            borderBottom: `2px dashed ${SKETCH_THEME.stickyBorder}`,
          }}
        >
          <div 
            className="flex items-center gap-2 text-amber-700 text-sm mb-1"
            style={fontSketchStyle}
          >
            <PenTool className="w-4 h-4" />
            <span>Live Notes</span>
          </div>
          <h3 
            className="text-xl font-bold text-gray-800"
            style={fontSketchStyle}
          >
            📝 {topic || 'Current Topic'}
          </h3>
          {subject && (
            <span 
              className="inline-block mt-2 px-2 py-0.5 rounded-full text-xs"
              style={{
                backgroundColor: 'rgba(255,255,255,0.7)',
                color: '#92400e',
                ...fontSketchStyle,
              }}
            >
              📚 {subject}
            </span>
          )}
        </div>
        
        {/* Content */}
        <div className="p-6">
          {formula ? (
            <div className="space-y-4">
              <div 
                className="text-sm font-medium uppercase tracking-wider"
                style={{
                  ...fontSketchStyle,
                  color: SKETCH_THEME.highlightBlue,
                }}
              >
                📐 Key Formula
              </div>
              <div 
                className="p-4 rounded-xl"
                style={{
                  backgroundColor: SKETCH_THEME.stickyYellow,
                  border: `2px solid ${SKETCH_THEME.stickyBorder}`,
                  transform: 'rotate(-0.5deg)',
                }}
              >
                <p 
                  className="text-xl text-gray-800 text-center"
                  style={{
                    ...fontSketchStyle,
                    fontWeight: '600',
                  }}
                >
                  {formula}
                </p>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <motion.div
                animate={{ rotate: [0, 10, -10, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="text-4xl mb-4"
              >
                ✏️
              </motion.div>
              <p 
                className="text-gray-500 text-sm"
                style={fontSketchStyle}
              >
                Ask about a specific concept to see formulas and key points here!
              </p>
            </div>
          )}
        </div>
        
        {/* Footer - Sketch Style */}
        <div 
          className="px-6 py-3"
          style={{
            backgroundColor: SKETCH_THEME.notebookBg,
            borderTop: `1px dashed ${SKETCH_THEME.gridColor}`,
          }}
        >
          <p 
            className="text-xs text-center text-gray-400"
            style={fontSketchStyle}
          >
            ✨ Notes update as we discuss concepts...
          </p>
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
  isFullscreen = false,
  currentTopic = null,
  keyFormula = null,
  subject = null,
  isConversationActive = false,
  isActive = true, // SmartBoard panel is visible/open
  isLoading = false, // NEW: Loading state from parent
  userQuestion = null, // NEW: Current question for fallback
}) {
  // Timeout state for fallback
  const [showFallback, setShowFallback] = useState(false);
  const timeoutRef = React.useRef(null);
  
  // Determine what type of visual to render
  const hasVisual = artifact && (
    artifact.svg || 
    artifact.visual_sketch?.svg || 
    artifact.blueprint ||
    artifact.template ||
    artifact.mode ||
    artifact.concept ||           // Whiteboard engine returns concept
    artifact.originalQuestion     // Or has original question
  );
  
  // NETRA can generate visuals from just a question - no artifact needed!
  // If conversation is active and we have a question, let NETRA render
  const canNetraGenerate = USE_NETRA_ENGINE && (
    userQuestion || 
    artifact?.originalQuestion || 
    artifact?.concept ||
    currentTopic
  );
  
  // ================================================================
  // 🎯 ENTERPRISE-GRADE VISUAL GATING (Cognito OS v1.0)
  // ================================================================
  // CRITICAL: Only generate visuals when backend EXPLICITLY says visual_needed=true
  // This prevents unnecessary visual generation for greetings, simple facts, etc.
  //
  // Defense in Depth:
  // 1. Backend sets visual_needed based on semantic intent
  // 2. Frontend checks visual_needed === true (NOT !== false)
  // 3. Intent-based fallback gating for edge cases
  // ================================================================
  
  // PRIMARY GATE: Backend must explicitly say visual is needed
  // 🎨 NETRA v5.0: Also allow visuals when use_composition is true (frontend composition mode)
  const backendSaysVisualNeeded = artifact?.visual_needed === true || artifact?.use_composition === true;
  const visualSkipReason = artifact?.visual_skip_reason;
  
  // SECONDARY GATE: Intent-based fallback (defense in depth)
  // These intents should NEVER trigger visual generation
  const NO_VISUAL_INTENTS = [
    'greeting', 'acknowledgment', 'chitchat', 'conversational',
    'clarification_or_followup', 'simple_fact', 'meta_question',
    'off_topic', 'feedback'
  ];
  const artifactIntent = artifact?.intent || '';
  const intentBlocksVisual = NO_VISUAL_INTENTS.includes(artifactIntent);
  
  // Combined decision: visual needed AND intent allows it
  const backendSaysNoVisual = !backendSaysVisualNeeded || intentBlocksVisual;
  
  // Log visual gating decision
  if (backendSaysNoVisual && (artifact?.originalQuestion || userQuestion)) {
    console.log(`🚫 [SmartBoard] Visual BLOCKED: visual_needed=${artifact?.visual_needed}, intent=${artifactIntent}, reason=${visualSkipReason || 'not_needed'}`);
  }
  
  // Show NETRA if:
  // 1. We have an explicit visual artifact (svg, blueprint, etc.) OR
  // 2. NETRA can generate AND backend says visual IS needed AND conversation active
  // 🎨 NETRA v5.0: Start visual IMMEDIATELY if use_composition is true (PARALLEL mode)
  const canStartImmediately = artifact?.use_composition === true && canNetraGenerate && !intentBlocksVisual;
  
  const shouldShowNetra = hasVisual || canStartImmediately || (
    isConversationActive && 
    canNetraGenerate && 
    !isLoading && 
    backendSaysVisualNeeded &&  // MUST be explicitly true
    !intentBlocksVisual         // Intent must allow visuals
  );
  
  // Debug logging for visual flow (production-grade observability)
  React.useEffect(() => {
    // Calculate the actual question that will be passed to NETRA
    const netraQuestion = 
      (artifact?.originalQuestion && artifact.originalQuestion.trim()) ||
      (artifact?.concept && artifact.concept.trim()) ||
      (userQuestion && userQuestion.trim()) ||
      currentTopic ||
      'explain the concept';
      
    console.log('═══════════════════════════════════════════════════');
    console.log('🎨 [SmartBoard] VISUAL GATING DEBUG (Cognito OS v1.0)');
    console.log('═══════════════════════════════════════════════════');
    console.log('🎨 hasVisual:', hasVisual);
    console.log('🎨 shouldShowNetra:', shouldShowNetra);
    console.log('🎨 canNetraGenerate:', canNetraGenerate);
    console.log('🎨 isConversationActive:', isConversationActive);
    console.log('🎨 isLoading:', isLoading);
    console.log('🎨 userQuestion:', userQuestion);
    console.log('🎨 currentTopic:', currentTopic);
    console.log('🎨 artifact?.originalQuestion:', artifact?.originalQuestion);
    console.log('🎨 artifact?.concept:', artifact?.concept);
    console.log('🎯 GATING: visual_needed:', artifact?.visual_needed);
    console.log('🎯 GATING: use_composition:', artifact?.use_composition);  // 🎨 NEW
    console.log('🎯 GATING: visual_skip_reason:', artifact?.visual_skip_reason);
    console.log('🎯 GATING: intent:', artifactIntent);
    console.log('🎯 GATING: backendSaysVisualNeeded:', backendSaysVisualNeeded);
    console.log('🎯 GATING: intentBlocksVisual:', intentBlocksVisual);
    console.log('🎯 GATING: canStartImmediately:', canStartImmediately);  // 🎨 NEW: Parallel mode check
    console.log('🎯 DECISION: backendSaysNoVisual:', backendSaysNoVisual);
    console.log('🎨 → NETRA will render:', shouldShowNetra ? netraQuestion : 'BLOCKED');
    console.log('═══════════════════════════════════════════════════');
  }, [hasVisual, shouldShowNetra, canNetraGenerate, isConversationActive, isLoading, userQuestion, currentTopic, artifact, backendSaysNoVisual, backendSaysVisualNeeded, intentBlocksVisual, artifactIntent, canStartImmediately]);
  
  // Handle loading timeout - show fallback after 5 seconds
  useEffect(() => {
    if (isLoading && !hasVisual) {
      // Start timeout when loading begins
      setShowFallback(false);
      timeoutRef.current = setTimeout(() => {
        setShowFallback(true);
      }, 5000); // 5 second timeout
    } else {
      // Clear timeout when visual arrives or loading stops
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      if (hasVisual) {
        setShowFallback(false);
      }
    }
    
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [isLoading, hasVisual]);
  
  // Show concept card if conversation is active but no visual
  const showConceptCard = isConversationActive && !hasVisual && !isLoading && (currentTopic || keyFormula);
  
  // Show loading skeleton
  const showLoadingSkeleton = isLoading && !hasVisual && !showFallback;
  
  // Show fallback when timeout occurs
  const showFallbackCard = isLoading && !hasVisual && showFallback;
  
  // Status indicator - green when active OR has visual OR loading
  const isStatusActive = isActive || hasVisual || isLoading;

  return (
    <div 
      className={`flex flex-col h-full relative overflow-hidden ${className}`}
      style={{
        // Magic Notebook paper background
        backgroundColor: SKETCH_THEME.notebookBg,
        // Dot grid pattern (sketchy notebook feel)
        backgroundImage: `radial-gradient(${SKETCH_THEME.gridColor} 1px, transparent 1px)`,
        backgroundSize: `${SKETCH_THEME.gridSize} ${SKETCH_THEME.gridSize}`,
      }}
    >
      {/* Subtle warm gradient overlay for depth */}
      <div className="absolute inset-0 bg-gradient-to-br from-amber-50/20 via-transparent to-purple-50/15 pointer-events-none" />
      
      {/* SVG Filter Definitions for Sketchy Effects */}
      <SketchyFilterDefs />
      
      {/* Live Formula Sticky Note */}
      <AnimatePresence>
        {keyFormula && (
          <FormulaStickyNote formula={keyFormula} concept={currentTopic} />
        )}
      </AnimatePresence>
      
      {/* Header Bar - Magic Notebook Style */}
      <div 
        className="relative z-10 flex-shrink-0 px-4 py-3 border-b-2 flex items-center justify-between"
        style={{
          backgroundColor: 'rgba(255, 255, 255, 0.85)',
          backdropFilter: 'blur(8px)',
          borderColor: SKETCH_THEME.gridColor,
        }}
      >
        <div className="flex items-center gap-3">
          {/* Live indicator */}
          <div className="relative">
            <div 
              className="w-2.5 h-2.5 rounded-full"
              style={{ backgroundColor: isStatusActive ? SKETCH_THEME.highlightGreen : '#9CA3AF' }}
            />
            {isStatusActive && (
              <div 
                className="absolute inset-0 w-2.5 h-2.5 rounded-full animate-ping opacity-50"
                style={{ backgroundColor: SKETCH_THEME.highlightGreen }}
              />
            )}
          </div>
          
          {/* Title with sketch font */}
          <span 
            className="text-base font-semibold text-gray-700"
            style={fontSketchStyle}
          >
            {isLoading && !hasVisual 
              ? '✏️ Sketching...' 
              : hasVisual 
                ? '✏️ Visual Ready' 
                : '📓 Magic Notebook'}
          </span>
          
          {/* Sketch indicator */}
          {hasVisual && (
            <PenTool className="w-4 h-4 text-purple-500" />
          )}
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
          {/* Priority 1: Loading Skeleton */}
          {showLoadingSkeleton ? (
            <SketchingLoadingState key="loading" />
          ) : /* Priority 2: Fallback Card (after timeout) */
          showFallbackCard ? (
            <FallbackConceptCard 
              key="fallback"
              topic={currentTopic || userQuestion?.split(' ').slice(0, 4).join(' ')}
              subject={subject}
            />
          ) : /* Priority 3: NETRA Visual (can generate from question alone!) */
          shouldShowNetra ? (
            <motion.div
              key="visual"
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.98, opacity: 0 }}
              transition={{ 
                type: 'spring', 
                stiffness: 400, 
                damping: 30,
              }}
              className="w-full h-full flex items-center justify-center"
            >
              {/* Visual Container - FULL BLEED - No Card - Immersive Simulation */}
              <div 
                className="w-full h-full overflow-visible flex items-center justify-center"
                style={{
                  // TRANSPARENT - Visual renders directly on MagicBook dotted canvas
                  backgroundColor: 'transparent',
                  // No border, no shadow, no card - visual IS the content
                }}
              >
                {/* 
                  REMOVED: Visual Title Bar 
                  V6 Magic Notebook renders concept title directly in SVG canvas
                  with hand-drawn aesthetic. No HTML title bar needed.
                */}
                
                {/* Visual Content - NETRA Visual Engines - FULL BLEED */}
                <div className="w-full h-full flex items-center justify-center" style={{ background: 'transparent' }}>
                  {(() => {
                    // Calculate question for debugging (matches NetraEngine priority)
                    const netraQuestion = 
                      (artifact?.originalQuestion && artifact.originalQuestion.trim()) ||
                      (userQuestion && userQuestion.trim()) ||
                      currentTopic ||
                      (artifact?.concept && artifact.concept.trim() && artifact.concept !== 'Concept' ? artifact.concept.trim() : null) ||
                      'explain the concept';
                    console.log('🎯 [SmartBoard] === VISUAL ENGINE ROUTING ===');
                    console.log('🎯 [SmartBoard] NETRA Question:', netraQuestion);
                    console.log('🎯 [SmartBoard] Artifact keys:', Object.keys(artifact || {}));
                    console.log('🎯 [SmartBoard] Has scene_data:', !!artifact?.scene_data);
                    console.log('🎯 [SmartBoard] Has composition:', !!artifact?.composition);
                    console.log('🎯 [SmartBoard] use_composition flag:', artifact?.use_composition);  // 🎨 NEW
                    console.log('🎯 [SmartBoard] COMPOSITION_MODE_AVAILABLE:', COMPOSITION_MODE_AVAILABLE);
                    console.log('🎯 [SmartBoard] USE_NETRA_ENGINE:', USE_NETRA_ENGINE);
                    console.log('🎯 [SmartBoard] DynamicVisualRenderer loaded:', !!DynamicVisualRenderer);
                    return null;
                  })()}
                  {/* ════════════════════════════════════════════════════════════
                      🎬 DEMO VISUAL SYSTEM (VC Demo) - PRIORITY #1
                      ════════════════════════════════════════════════════════════
                      Hardcoded premium visuals for demo questions.
                      100% reliable, no LLM calls, instant render.
                      ════════════════════════════════════════════════════════════ */}
                  {(() => {
                    const currentQuestion = 
                      (artifact?.originalQuestion && artifact.originalQuestion.trim()) ||
                      (userQuestion && userQuestion.trim()) ||
                      currentTopic ||
                      '';
                    
                    // Check if this is a demo question
                    if (DEMO_SYSTEM_AVAILABLE && isDemoQuestion && isDemoQuestion(currentQuestion)) {
                      const demoConfig = getDemoConfig(currentQuestion);
                      console.log('════════════════════════════════════════════════');
                      console.log('🎬 [SmartBoard] DEMO VISUAL SYSTEM (VC Demo)');
                      console.log('🎬 Question:', currentQuestion.substring(0, 50));
                      console.log('🎬 Visual Type:', demoConfig?.visualType);
                      console.log('🎬 100% Reliable - No LLM calls');
                      console.log('════════════════════════════════════════════════');
                      
                      return (
                        <DemoVisualRenderer
                          demoConfig={demoConfig}
                          width={620}
                          height={420}
                          onReady={() => {
                            console.log('✅ [SmartBoard] DEMO visual ready');
                          }}
                          onPhaseChange={(phase) => {
                            console.log('🎬 [SmartBoard] DEMO phase:', phase);
                          }}
                        />
                      );
                    }
                    return null;
                  })()}

                  {/* ════════════════════════════════════════════════════════════
                      🎨 NETRA v5.0 - COMPOSITION ENGINE (ONLY RENDERER)
                      ════════════════════════════════════════════════════════════
                      ALL legacy renderers removed:
                      - ❌ Scene-based rendering (use_scene_renderer + scene_data)
                      - ❌ NetraV4 image renderer (image_base64)
                      - ❌ MagicNotebookEngine
                      - ❌ UniversalSketchCanvas
                      
                      ONLY ONE RENDERER: NetraEngine with Composition Mode
                      ════════════════════════════════════════════════════════════ */}
                  {!DEMO_SYSTEM_AVAILABLE || !isDemoQuestion || !isDemoQuestion(
                    (artifact?.originalQuestion && artifact.originalQuestion.trim()) ||
                    (userQuestion && userQuestion.trim()) ||
                    currentTopic ||
                    ''
                  ) ? (
                    USE_NETRA_ENGINE && NetraEngine ? (
                    (() => {
                      // 🎨 NETRA v5.0: ALWAYS use composition mode
                      // This is the ONLY visual engine - no fallbacks to legacy renderers
                      console.log('════════════════════════════════════════════════');
                      console.log('🎨 [SmartBoard] NETRA COMPOSITION ENGINE (ONLY RENDERER)');
                      console.log('🎨 Question:', (artifact?.originalQuestion || userQuestion || currentTopic || '').substring(0, 50));
                      console.log('🎨 Subject:', artifact?.subject || subject || 'physics');
                      console.log('════════════════════════════════════════════════');
                      return (
                        <NetraEngine
                          question={
                            // Priority: originalQuestion > userQuestion > currentTopic > concept
                            (artifact?.originalQuestion && artifact.originalQuestion.trim()) ||
                            (userQuestion && userQuestion.trim()) ||
                            currentTopic ||
                            (artifact?.concept && artifact.concept.trim() && artifact.concept !== 'Concept' ? artifact.concept.trim() : null) ||
                            'explain the concept'
                          }
                          context={{
                            subject: artifact?.subject || subject || 'physics',
                            level: 'high_school',
                            visual_needed: true,  // Always needed - this is visual engine
                            intent: artifact?.intent,
                          }}
                          useCompositionMode={true}  // 🎨 ALWAYS ON - composition is THE ONLY engine
                          width={720}   // 🎬 LARGER: 90% of MagicBook width
                          height={520}  // 🎬 LARGER: Better proportions for simulation
                          showGrid={false}
                          showMetadata={process.env.NODE_ENV === 'development'}
                          useLLM={true}
                          className="mx-auto"  // Center the visual
                          onGenerated={(result) => {
                            console.log('✅ [SmartBoard] NETRA composition generated');
                            console.log('✅ Atoms:', result.composition?.atoms?.length || 0);
                            console.log('✅ Mode:', result.metadata?.renderMode);
                          }}
                          onError={(error) => {
                            console.error('❌ [SmartBoard] NETRA error:', error);
                          }}
                          onRenderComplete={() => {
                            console.log('✨ [SmartBoard] NETRA render complete');
                          }}
                        />
                      );
                    })()
                  ) : (
                    /* 🚫 NO LEGACY FALLBACK - Show error if NetraEngine unavailable */
                    <div style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      height: '100%',
                      padding: 40,
                      background: 'linear-gradient(135deg, #fef3f2 0%, #fee2e2 100%)',
                      borderRadius: 16,
                    }}>
                      <div style={{ fontSize: 48, marginBottom: 16 }}>⚠️</div>
                      <div style={{
                        fontFamily: "'Inter', sans-serif",
                        fontSize: 16,
                        fontWeight: 500,
                        color: '#991b1b',
                        textAlign: 'center',
                      }}>
                        Visual Engine Unavailable
                      </div>
                      <div style={{
                        fontFamily: "'Inter', sans-serif",
                        fontSize: 13,
                        color: '#b91c1c',
                        marginTop: 8,
                        textAlign: 'center',
                      }}>
                        NetraEngine failed to load. Please refresh the page.
                      </div>
                    </div>
                  )
                  ) : null}
                </div>
              </div>

              {/* Visual Caption - Sketch Style */}
              {artifact?.caption && (
                <motion.p
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="text-center text-sm mt-4"
                  style={{
                    ...fontSketchStyle,
                    color: '#6B7280',
                    fontStyle: 'italic',
                  }}
                >
                  💡 {artifact.caption}
                </motion.p>
              )}
            </motion.div>
          ) : /* Priority 4: Concept Card (when no visual but have topic) */
          showConceptCard ? (
            <ConceptCard 
              key="concept"
              topic={currentTopic}
              formula={keyFormula}
              subject={subject}
            />
          ) : /* Priority 5: Empty State */
          (
            <EmptyBoardState key="empty" />
          )}
        </AnimatePresence>
      </div>

      {/* Footer Hint - Sketch Notebook Style */}
      {!shouldShowNetra && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="relative z-10 flex-shrink-0 px-4 py-3"
          style={{
            background: 'linear-gradient(to top, rgba(255,255,255,0.9), transparent)',
            borderTop: `1px dashed ${SKETCH_THEME.gridColor}`,
          }}
        >
          <p 
            className="text-xs text-center text-gray-500"
            style={fontSketchStyle}
          >
            ✏️ Sketches appear here when I explain concepts...
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
