/**
 * 🎨 UNIVERSAL SKETCH CANVAS (SketchSense V5.0)
 * =============================================
 * 
 * THE MODE ROUTER - Central coordinator for all visual rendering.
 * 
 * "If you can ask it, Druv can draw it."
 * 
 * This component implements the Gemini PRD's Universal Renderer:
 * - Reads JSON Blueprint from backend
 * - Routes to appropriate Rendering Strategy (8 Master Modes)
 * - Applies "SketchSense" aesthetics universally
 * - Integrates Intelligence Layer (Validators, Bloom's, Cultural Context)
 * 
 * 8 MASTER RENDERING MODES:
 * 1. SCENE      - Interactive physics simulations
 * 2. COMPARISON - Split-panel side-by-side views
 * 3. PROCESS    - Linear flow diagrams
 * 4. CYCLE      - Circular looping processes
 * 5. STRUCTURE  - Anatomy/labeling diagrams
 * 6. GRAPH      - Mathematical function plots
 * 7. TIMELINE   - Chronological sequences
 * 8. HIERARCHY  - Tree/taxonomy diagrams
 * 
 * @version 5.0
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// ============================================
// V6 MAGIC NOTEBOOK ENGINE - THE NEW DEFAULT
// ============================================
// Import V6 as the primary renderer - hand-drawn, animated, ALIVE!
import UniversalSketchCanvasV6, {
  NotebookPaper,
  GhostMentor,
  SketchSlider,
  BlueprintRenderer,
  NOTEBOOK_THEME,
} from './sketch/UniversalSketchCanvasV6';

// Legacy Mode Renderers (deprecated - only used for backwards compatibility)
import ConfigDrivenSketch, { INTERACTION_MODES, DIFFICULTY_LEVELS } from './components/ConfigDrivenSketch';

// Import SketchSense Templates
import SplitComparisonTemplate from '../components/visuals/templates/SplitComparisonTemplate';
import ForceComparisonTemplate from '../components/visuals/templates/ForceComparisonTemplate';
import { SketchyFilterDefs } from '../components/visuals/templates/SketchyFilters';

// Import Validators
import { ValidatorEngine, getValidatorForSubject } from './validators/ValidatorEngine';

// Import Feedback System
import { FeedbackController } from './feedback/FeedbackController';

// Import Asset Factory
import assetFactory, { detectCulturalContext, transformToThemedConfig } from '../utils/AssetFactory';

// ============================================
// MASTER RENDERING MODES (8 Core Modes)
// ============================================
export const MASTER_MODES = {
  SCENE: 'scene',           // Physics simulations, real-world examples
  COMPARISON: 'comparison', // Split-panel side-by-side
  PROCESS: 'process',       // Linear flow (reactions, algorithms)
  CYCLE: 'cycle',          // Circular looping (Krebs, Water cycle)
  STRUCTURE: 'structure',   // Anatomy/labeling
  GRAPH: 'graph',          // Mathematical plots
  TIMELINE: 'timeline',     // Chronological events
  HIERARCHY: 'hierarchy',   // Tree diagrams
};

// ============================================
// SKETCHSENSE THEME (Uses V6 NOTEBOOK_THEME)
// ============================================
// Re-export NOTEBOOK_THEME as SKETCH_THEME for backwards compatibility
const SKETCH_THEME = {
  ...NOTEBOOK_THEME,
  // Additional legacy aliases
  paperBg: NOTEBOOK_THEME.paperBg,
  dotGridColor: NOTEBOOK_THEME.dotColor,
  dotGridSize: '20px',
  fontHandwriting: NOTEBOOK_THEME.handwriting,
  fontTitle: "'Caveat', cursive",
  strokeDashDuration: '1.5s',
  wobbleFilter: 'url(#sketchy)',
};

// ============================================
// MODE DETECTOR
// ============================================
function detectModeFromBlueprint(blueprint) {
  if (!blueprint) return MASTER_MODES.SCENE;
  
  // Explicit mode in blueprint
  if (blueprint.mode && MASTER_MODES[blueprint.mode.toUpperCase()]) {
    return blueprint.mode.toLowerCase();
  }
  
  // Auto-detect from structure
  const config = blueprint.config || blueprint;
  
  // COMPARISON: Has left/right panels or "vs" content
  if (config.left_panel && config.right_panel) return MASTER_MODES.COMPARISON;
  if (config.compare || config.versus || blueprint.template === 'comparison') return MASTER_MODES.COMPARISON;
  
  // CYCLE: Has circular arrangement or cycle keyword
  if (config.cycle || config.circular || blueprint.template?.includes('cycle')) return MASTER_MODES.CYCLE;
  
  // PROCESS: Has steps array with sequential structure
  if (config.steps && Array.isArray(config.steps)) return MASTER_MODES.PROCESS;
  if (config.flow || config.sequence) return MASTER_MODES.PROCESS;
  
  // STRUCTURE: Has components with positions or anatomy
  if (config.components || config.parts || config.anatomy) return MASTER_MODES.STRUCTURE;
  
  // GRAPH: Has mathematical expressions or axes
  if (config.expression || config.function || config.axes) return MASTER_MODES.GRAPH;
  if (config.x_axis || config.y_axis || blueprint.plot) return MASTER_MODES.GRAPH;
  
  // TIMELINE: Has events with dates/times
  if (config.events || config.milestones || blueprint.chronological) return MASTER_MODES.TIMELINE;
  
  // HIERARCHY: Has tree structure or taxonomy
  if (config.root || config.branches || config.taxonomy) return MASTER_MODES.HIERARCHY;
  if (config.parent || config.children) return MASTER_MODES.HIERARCHY;
  
  // SCENE: Default for physics, simulations
  if (config.entities || config.physics || config.simulation) return MASTER_MODES.SCENE;
  
  // Default fallback
  return MASTER_MODES.SCENE;
}

// ============================================
// SUBJECT DETECTOR
// ============================================
function detectSubject(blueprint, question) {
  const text = `${question || ''} ${blueprint?.concept || ''} ${blueprint?.subject || ''}`.toLowerCase();
  
  if (/physics|motion|force|velocity|acceleration|newton|gravity|projectile|wave|light|electric/i.test(text)) {
    return 'physics';
  }
  if (/chemistry|reaction|element|compound|acid|base|organic|inorganic|bond|atom/i.test(text)) {
    return 'chemistry';
  }
  if (/biology|cell|dna|protein|organ|plant|animal|human|body|disease|evolution/i.test(text)) {
    return 'biology';
  }
  if (/math|calculus|algebra|geometry|trigonometry|equation|function|graph|derivative|integral/i.test(text)) {
    return 'mathematics';
  }
  
  return blueprint?.subject || 'general';
}

// ============================================
// MAIN COMPONENT: UniversalSketchCanvas
// ============================================
const UniversalSketchCanvas = ({
  // Core Props
  blueprint = null,
  question = '',
  
  // Mode Overrides
  mode = null, // Force specific mode
  subject = null, // Force specific subject
  
  // Intelligence Layer
  difficultyLevel = DIFFICULTY_LEVELS.APPLY,
  interactionMode = INTERACTION_MODES.LEARN,
  enableValidation = true,
  enableFeedback = true,
  
  // Cultural Context
  culturalContext = null, // 'cricket', 'train', 'diwali', etc.
  
  // Callbacks
  onStateChange = null,
  onValidationFeedback = null,
  onQuizAnswer = null,
  onAnimationComplete = null,
  
  // Styling
  className = '',
  style = {},
}) => {
  // ============ STATE ============
  const [currentMode, setCurrentMode] = useState(mode || MASTER_MODES.SCENE);
  const [currentSubject, setCurrentSubject] = useState(subject || 'physics');
  const [interactiveState, setInteractiveState] = useState({});
  const [validationFeedback, setValidationFeedback] = useState(null);
  const [themedBlueprint, setThemedBlueprint] = useState(blueprint);
  const [isDrawing, setIsDrawing] = useState(true);
  
  // ============ MODE DETECTION ============
  useEffect(() => {
    if (mode) {
      setCurrentMode(mode);
    } else if (blueprint) {
      const detectedMode = detectModeFromBlueprint(blueprint);
      setCurrentMode(detectedMode);
    }
  }, [blueprint, mode]);
  
  // ============ SUBJECT DETECTION ============
  useEffect(() => {
    if (subject) {
      setCurrentSubject(subject);
    } else {
      const detectedSubject = detectSubject(blueprint, question);
      setCurrentSubject(detectedSubject);
    }
  }, [blueprint, question, subject]);
  
  // ============ CULTURAL CONTEXT & THEMING ============
  useEffect(() => {
    if (blueprint) {
      const context = culturalContext || detectCulturalContext(question);
      if (context && transformToThemedConfig) {
        try {
          const themed = transformToThemedConfig(blueprint, question);
          setThemedBlueprint(themed);
        } catch (e) {
          console.warn('Asset theming failed:', e);
          setThemedBlueprint(blueprint);
        }
      } else {
        setThemedBlueprint(blueprint);
      }
    }
  }, [blueprint, culturalContext, question]);
  
  // ============ VALIDATION ============
  const handleStateChange = useCallback((newState) => {
    setInteractiveState(newState);
    
    if (enableValidation) {
      try {
        const validator = getValidatorForSubject(currentSubject);
        if (validator) {
          const result = validator.validate(newState, themedBlueprint);
          if (!result.isValid) {
            setValidationFeedback({
              type: result.violationType,
              message: result.mentorMessage,
              visualEffect: result.visualEffect,
            });
            onValidationFeedback?.(result);
          } else {
            setValidationFeedback(null);
          }
        }
      } catch (e) {
        console.warn('Validation error:', e);
      }
    }
    
    onStateChange?.(newState);
  }, [currentSubject, themedBlueprint, enableValidation, onStateChange, onValidationFeedback]);
  
  // ============ RENDER MODE COMPONENT ============
  // 🎨 V6 MAGIC NOTEBOOK ENGINE - Hand-drawn, animated, ALIVE!
  // ALL modes now use the V6 engine by default. No more corporate boxes!
  const renderModeContent = useMemo(() => {
    const commonProps = {
      blueprint: themedBlueprint,
      question: question,
      concept: themedBlueprint?.concept || question?.slice(0, 50),
      subject: currentSubject,
      difficultyLevel,
      mode: interactionMode,
      enableValidation: enableValidation,
      enableFeedback: enableFeedback,
      onStateChange: handleStateChange,
      onValidationFeedback,
      onComplete: onAnimationComplete,
    };
    
    // 🎨 V6: USE THE MAGIC NOTEBOOK ENGINE FOR EVERYTHING!
    // No more boring templates. Just hand-drawn sketchy visuals.
    return (
      <UniversalSketchCanvasV6
        {...commonProps}
        style={{ minHeight: '380px' }}
      />
    );
  }, [currentMode, themedBlueprint, currentSubject, difficultyLevel, interactionMode, enableValidation, enableFeedback, handleStateChange, onValidationFeedback, onAnimationComplete, question]);
  
  // ============ DRAW-IN ANIMATION ============
  useEffect(() => {
    setIsDrawing(true);
    const timer = setTimeout(() => setIsDrawing(false), 1500);
    return () => clearTimeout(timer);
  }, [blueprint]);
  
  // ============ RENDER ============
  // 🎨 V6: Use NotebookPaper wrapper for consistent Magic Notebook aesthetic
  return (
    <NotebookPaper 
      className={`universal-sketch-canvas ${className}`}
      style={{ minHeight: '400px', ...style }}
    >
      {/* SVG Filter Definitions */}
      <SketchyFilterDefs />
      
      {/* Mode Badge - Sketchy Style */}
      <motion.div 
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="absolute top-3 right-3 z-20 px-3 py-1 rounded-lg text-xs font-medium"
        style={{
          backgroundColor: NOTEBOOK_THEME.highlightYellow,
          color: '#92400e',
          fontFamily: NOTEBOOK_THEME.handwriting,
          transform: 'rotate(-2deg)',
          boxShadow: '2px 2px 4px rgba(0,0,0,0.1)',
        }}
      >
        {getModeEmoji(currentMode)} {currentMode.toUpperCase()}
      </motion.div>
      
      {/* Draw-in Animation Overlay */}
      <AnimatePresence>
        {isDrawing && (
          <motion.div
            className="absolute inset-0 z-30 pointer-events-none"
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            style={{
              background: `linear-gradient(90deg, ${NOTEBOOK_THEME.paperBg} 0%, transparent 100%)`,
            }}
          />
        )}
      </AnimatePresence>
      
      {/* Ghost Mentor - Validation Feedback */}
      <AnimatePresence>
        {validationFeedback && (
          <GhostMentor
            message={validationFeedback.message}
            type={validationFeedback.type === 'warning' ? 'warning' : 'hint'}
            visible={true}
          />
        )}
      </AnimatePresence>
      
      {/* Main Content - V6 Magic Notebook Engine */}
      <div className="w-full h-full min-h-[380px]">
        {renderModeContent}
      </div>
      
      {/* Difficulty Level Badge - Sketchy Style */}
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="absolute bottom-3 left-3 z-20 px-3 py-1 rounded-lg text-xs"
        style={{
          backgroundColor: getDifficultyColor(difficultyLevel),
          color: 'white',
          fontFamily: NOTEBOOK_THEME.handwriting,
          transform: 'rotate(1deg)',
          boxShadow: '2px 2px 4px rgba(0,0,0,0.1)',
        }}
      >
        {getDifficultyEmoji(difficultyLevel)} {difficultyLevel}
      </motion.div>
    </NotebookPaper>
  );
};

// ============================================
// HELPER FUNCTIONS
// ============================================
function getModeEmoji(mode) {
  const emojis = {
    [MASTER_MODES.SCENE]: '🎬',
    [MASTER_MODES.COMPARISON]: '⚖️',
    [MASTER_MODES.PROCESS]: '➡️',
    [MASTER_MODES.CYCLE]: '🔄',
    [MASTER_MODES.STRUCTURE]: '🔬',
    [MASTER_MODES.GRAPH]: '📈',
    [MASTER_MODES.TIMELINE]: '📅',
    [MASTER_MODES.HIERARCHY]: '🌳',
  };
  return emojis[mode] || '✨';
}

function getDifficultyColor(level) {
  const colors = {
    [DIFFICULTY_LEVELS.RECALL]: '#f59e0b',
    [DIFFICULTY_LEVELS.UNDERSTAND]: '#3b82f6',
    [DIFFICULTY_LEVELS.APPLY]: '#10b981',
  };
  return colors[level] || '#6b7280';
}

function getDifficultyEmoji(level) {
  const emojis = {
    [DIFFICULTY_LEVELS.RECALL]: '🧠',
    [DIFFICULTY_LEVELS.UNDERSTAND]: '💡',
    [DIFFICULTY_LEVELS.APPLY]: '🔬',
  };
  return emojis[level] || '📚';
}

// Empty state component
const EmptyState = () => (
  <div className="flex flex-col items-center justify-center h-full text-center p-8">
    <motion.div
      animate={{ y: [0, -10, 0] }}
      transition={{ duration: 2, repeat: Infinity }}
      className="text-6xl mb-4"
    >
      📓
    </motion.div>
    <h3 
      className="text-xl font-bold text-gray-700 mb-2"
      style={{ fontFamily: "'Patrick Hand', cursive" }}
    >
      Magic Notebook Ready
    </h3>
    <p 
      className="text-gray-500"
      style={{ fontFamily: "'Patrick Hand', cursive" }}
    >
      Ask me anything and I'll sketch it for you!
    </p>
  </div>
);

// ============================================
// EXPORTS
// ============================================
export { 
  SKETCH_THEME, 
  detectModeFromBlueprint, 
  detectSubject,
  // Re-export from ConfigDrivenSketch for convenience
  DIFFICULTY_LEVELS,
  INTERACTION_MODES,
};
export default UniversalSketchCanvas;

