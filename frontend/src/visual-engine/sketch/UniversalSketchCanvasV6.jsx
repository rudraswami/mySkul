/**
 * 🎨 UNIVERSAL SKETCH CANVAS V6 (Magic Notebook Engine)
 * =====================================================
 * 
 * "A personal AI tutor sketching explanations for you in a magical notebook."
 * 
 * This is the heart of SketchSense V6.
 * It transforms any blueprint into a LIVE, hand-drawn, animated visual.
 * 
 * Features:
 * ✅ RoughJS hand-drawn aesthetics
 * ✅ Framer Motion pathLength animations
 * ✅ Cinematic reveal sequences
 * ✅ Notebook paper background
 * ✅ Handwriting labels
 * ✅ Highlighter marks
 * ✅ Stick figures & doodles
 * ✅ Interactive controls
 * ✅ Validation + Ghost Mentor
 * ✅ Cultural asset swapping
 * 
 * NO boxes. NO corporate UI. Just magic! ✨
 */

import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Sketch Primitives
import {
  SketchCircle,
  SketchRect,
  SketchArrow,
  SketchLabel,
  SketchHighlight,
  SketchStickFigure,
  SketchDoodle,
  SketchLine,
  SketchFilters,
  NOTEBOOK_THEME,
  drawVariants,
  fadeInVariants,
  popVariants,
} from './SketchPrimitives';

// Reveal Sequence Engine
import RevealSequenceEngine, { 
  TIMING, 
  ELEMENT_TYPES,
  PRESET_SEQUENCES,
  buildSequence,
} from './RevealSequenceEngine';

// Validators
import { getValidatorForSubject } from '../validators/ValidatorEngine';

// Feedback
import { getFeedbackController, FEEDBACK_TYPES } from '../feedback/FeedbackController';

// ============================================
// PAPER BACKGROUND COMPONENT
// ============================================
const NotebookPaper = ({ children, className = '' }) => (
  <div
    className={`notebook-paper ${className}`}
    style={{
      background: NOTEBOOK_THEME.paperBg,
      backgroundImage: `
        radial-gradient(${NOTEBOOK_THEME.dotColor} 1px, transparent 1px)
      `,
      backgroundSize: '20px 20px',
      position: 'relative',
      overflow: 'hidden',
      borderRadius: '12px',
      fontFamily: NOTEBOOK_THEME.handwriting,
    }}
  >
    {/* Paper texture overlay */}
    <div 
      style={{
        position: 'absolute',
        inset: 0,
        background: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%' height='100%' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E")`,
        pointerEvents: 'none',
      }}
    />
    {children}
  </div>
);

// ============================================
// GHOST MENTOR COMPONENT
// ============================================
const GhostMentor = ({ message, type = 'hint', visible = false }) => {
  if (!visible || !message) return null;
  
  const bgColors = {
    hint: '#FEF3C7',
    warning: '#FEE2E2',
    success: '#D1FAE5',
    info: '#DBEAFE',
  };
  
  const icons = {
    hint: '💡',
    warning: '⚠️',
    success: '✨',
    info: 'ℹ️',
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, y: -20, scale: 0.9, rotate: -2 }}
      animate={{ opacity: 1, y: 0, scale: 1, rotate: 0 }}
      exit={{ opacity: 0, y: -10, scale: 0.9 }}
      transition={{ type: 'spring', damping: 15 }}
      style={{
        position: 'absolute',
        top: '16px',
        right: '16px',
        padding: '12px 16px',
        background: bgColors[type],
        borderRadius: '8px',
        boxShadow: '2px 4px 12px rgba(0,0,0,0.1)',
        fontFamily: NOTEBOOK_THEME.handwriting,
        fontSize: '14px',
        maxWidth: '250px',
        transform: 'rotate(-1deg)',
        border: '2px solid rgba(0,0,0,0.1)',
        zIndex: 100,
      }}
    >
      <span style={{ marginRight: '8px' }}>{icons[type]}</span>
      {message}
    </motion.div>
  );
};

// ============================================
// SKETCH SLIDER (Interactive Control)
// ============================================
const SketchSlider = ({ 
  label, 
  value, 
  min = 0, 
  max = 100, 
  onChange,
  color = NOTEBOOK_THEME.markerBlue,
  delay = 0,
}) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay }}
    style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
      padding: '8px 0',
    }}
  >
    <label 
      style={{ 
        fontFamily: NOTEBOOK_THEME.handwriting, 
        fontSize: '16px',
        color: NOTEBOOK_THEME.penBlack,
      }}
    >
      {label}: <strong>{value}</strong>
    </label>
    <input
      type="range"
      min={min}
      max={max}
      value={value}
      onChange={(e) => onChange(Number(e.target.value))}
      style={{
        width: '100%',
        height: '8px',
        borderRadius: '4px',
        background: `linear-gradient(to right, ${color} ${(value - min) / (max - min) * 100}%, #E5E7EB ${(value - min) / (max - min) * 100}%)`,
        cursor: 'pointer',
        WebkitAppearance: 'none',
      }}
    />
  </motion.div>
);

// ============================================
// BLUEPRINT RENDERER
// ============================================
const BlueprintRenderer = ({ 
  blueprint, 
  sequence, 
  interactiveState,
  onStateChange,
}) => {
  if (!blueprint) return null;
  
  const items = blueprint.items || [];
  const arrows = blueprint.arrows || [];
  const highlights = blueprint.highlights || [];
  const labels = blueprint.labels || [];
  const doodles = blueprint.doodles || [];
  const figures = blueprint.figures || [];
  
  // Calculate positions (simple auto-layout)
  const getPosition = (index, total) => {
    const width = 400;
    const height = 300;
    const padding = 60;
    
    if (total === 1) {
      return { x: width / 2, y: height / 2 };
    }
    
    // Spread items horizontally
    const spacing = (width - padding * 2) / (total - 1);
    return { 
      x: padding + index * spacing, 
      y: height / 2 
    };
  };
  
  // Find item by ID
  const findItem = (id) => items.find(item => item.id === id || item.label === id);
  
  return (
    <g className="blueprint-content">
      {/* Render highlights first (background) */}
      {highlights.map((hl, i) => {
        const target = findItem(hl);
        if (!target) return null;
        const pos = getPosition(items.indexOf(target), items.length);
        return (
          <SketchHighlight
            key={`hl-${i}`}
            x={pos.x - 50}
            y={pos.y - 25}
            width={100}
            height={50}
            delay={TIMING.HIGHLIGHTS + i * 0.1}
          />
        );
      })}
      
      {/* Render shapes */}
      {items.map((item, i) => {
        const pos = item.position || getPosition(i, items.length);
        const delay = TIMING.SHAPES + i * 0.15;
        
        if (item.type === 'circle') {
          return (
            <g key={`item-${i}`} transform={`translate(${pos.x}, ${pos.y})`}>
              <SketchCircle
                cx={0}
                cy={0}
                radius={item.radius || 40}
                fill={item.fill}
                stroke={item.stroke || NOTEBOOK_THEME.pencilGray}
                delay={delay}
              />
              {item.label && (
                <SketchLabel
                  x={0}
                  y={5}
                  text={item.label}
                  delay={TIMING.LABELS + i * 0.1}
                />
              )}
            </g>
          );
        }
        
        if (item.type === 'rect' || item.type === 'node') {
          return (
            <g key={`item-${i}`} transform={`translate(${pos.x - 40}, ${pos.y - 25})`}>
              <SketchRect
                x={0}
                y={0}
                width={item.width || 80}
                height={item.height || 50}
                fill={item.fill}
                stroke={item.stroke || NOTEBOOK_THEME.pencilGray}
                delay={delay}
              />
              {item.label && (
                <SketchLabel
                  x={40}
                  y={30}
                  text={item.label}
                  delay={TIMING.LABELS + i * 0.1}
                />
              )}
            </g>
          );
        }
        
        return null;
      })}
      
      {/* Render arrows/connections */}
      {arrows.map((arrow, i) => {
        const fromItem = findItem(arrow.from);
        const toItem = findItem(arrow.to);
        if (!fromItem || !toItem) return null;
        
        const fromPos = fromItem.position || getPosition(items.indexOf(fromItem), items.length);
        const toPos = toItem.position || getPosition(items.indexOf(toItem), items.length);
        
        return (
          <SketchArrow
            key={`arrow-${i}`}
            x1={fromPos.x + 45}
            y1={fromPos.y}
            x2={toPos.x - 45}
            y2={toPos.y}
            stroke={arrow.style === 'energy' ? NOTEBOOK_THEME.highlightOrange : NOTEBOOK_THEME.markerBlue}
            label={arrow.label}
            curved={arrow.curved}
            delay={TIMING.CONNECTIONS + i * 0.15}
          />
        );
      })}
      
      {/* Render stick figures */}
      {figures.map((fig, i) => (
        <SketchStickFigure
          key={`fig-${i}`}
          x={fig.x || 100}
          y={fig.y || 150}
          size={fig.size || 60}
          pose={fig.pose || 'standing'}
          expression={fig.expression || 'neutral'}
          delay={TIMING.SHAPES + 0.2 + i * 0.15}
        />
      ))}
      
      {/* Render additional labels */}
      {labels.map((lbl, i) => (
        <SketchLabel
          key={`lbl-${i}`}
          x={lbl.x || 200}
          y={lbl.y || 50}
          text={lbl.text}
          fontSize={lbl.fontSize || 18}
          color={lbl.color || NOTEBOOK_THEME.penBlack}
          underline={lbl.underline}
          delay={TIMING.LABELS + i * 0.1}
        />
      ))}
      
      {/* Render doodles */}
      {doodles.map((doodle, i) => (
        <SketchDoodle
          key={`doodle-${i}`}
          x={doodle.x || 350}
          y={doodle.y || 50}
          type={doodle.type || 'sparkle'}
          size={doodle.size || 25}
          color={doodle.color || NOTEBOOK_THEME.highlightYellow}
          delay={TIMING.DOODLES + i * 0.1}
        />
      ))}
    </g>
  );
};

// ============================================
// MAIN COMPONENT: UniversalSketchCanvasV6
// ============================================
const UniversalSketchCanvasV6 = ({
  // Core Props
  blueprint = null,
  question = '',
  
  // Context
  subject = 'physics',
  concept = '',
  culturalContext = null,
  
  // Bloom's Taxonomy
  difficultyLevel = 'apply', // 'recall', 'understand', 'apply'
  
  // Interaction
  mode = 'learn', // 'learn', 'quiz'
  enableValidation = true,
  enableFeedback = true,
  
  // Callbacks
  onStateChange = null,
  onValidationFeedback = null,
  onComplete = null,
  
  // Styling
  width = '100%',
  height = 400,
  className = '',
  style = {},
}) => {
  // ============ STATE ============
  const svgRef = useRef(null);
  const [interactiveState, setInteractiveState] = useState({
    force: 10,
    velocity: 5,
    mass: 1,
    angle: 45,
  });
  const [mentorMessage, setMentorMessage] = useState(null);
  const [mentorType, setMentorType] = useState('hint');
  const [isAnimating, setIsAnimating] = useState(true);
  const [sequenceComplete, setSequenceComplete] = useState(false);
  
  // Feedback controller
  const feedbackController = useMemo(() => getFeedbackController(), []);
  
  // ============ GENERATE DEFAULT BLUEPRINT IF NONE PROVIDED ============
  const effectiveBlueprint = useMemo(() => {
    if (blueprint && Object.keys(blueprint).length > 0) {
      return blueprint;
    }
    
    // Generate a simple concept blueprint from the question
    const lowerQ = (question || concept || '').toLowerCase();
    
    // Physics concepts
    if (lowerQ.includes('force')) {
      return {
        items: [
          { type: 'rect', label: 'Object', id: 'block' },
        ],
        figures: [
          { x: 80, y: 180, pose: 'pushing', expression: 'happy' },
        ],
        arrows: [
          { from: 'figure', to: 'block', label: 'F = ma', style: 'energy' },
        ],
        highlights: ['block'],
        doodles: [
          { type: 'burst', x: 280, y: 140 },
        ],
        labels: [
          { text: 'Force & Motion', x: 200, y: 40, fontSize: 22, underline: true },
        ],
      };
    }
    
    if (lowerQ.includes('velocity') || lowerQ.includes('speed') || lowerQ.includes('motion')) {
      return {
        items: [
          { type: 'circle', label: 'Start', id: 'start', position: { x: 80, y: 180 } },
          { type: 'circle', label: 'End', id: 'end', position: { x: 320, y: 180 } },
        ],
        arrows: [
          { from: 'start', to: 'end', label: 'v = d/t' },
        ],
        doodles: [
          { type: 'sparkle', x: 360, y: 160 },
        ],
        labels: [
          { text: 'Velocity', x: 200, y: 40, fontSize: 22, underline: true },
          { text: 'distance', x: 200, y: 220, fontSize: 14 },
        ],
      };
    }
    
    if (lowerQ.includes('gravity') || lowerQ.includes('fall')) {
      return {
        items: [
          { type: 'circle', label: '🍎', id: 'apple', position: { x: 200, y: 80 } },
        ],
        figures: [
          { x: 200, y: 280, pose: 'standing', expression: 'surprised' },
        ],
        arrows: [
          { from: 'apple', to: 'figure', label: 'g = 9.8 m/s²' },
        ],
        doodles: [
          { type: 'star', x: 240, y: 60 },
        ],
        labels: [
          { text: 'Gravity', x: 200, y: 30, fontSize: 22, underline: true },
        ],
      };
    }
    
    // Default: simple concept display
    return {
      items: [
        { type: 'circle', label: concept || 'Concept', id: 'main' },
      ],
      doodles: [
        { type: 'sparkle', x: 280, y: 120 },
      ],
      labels: [
        { text: concept || question?.slice(0, 30) || 'Visual Explanation', x: 200, y: 40, fontSize: 20 },
      ],
    };
  }, [blueprint, question, concept]);
  
  // ============ VALIDATION ============
  const handleStateChange = useCallback((key, value) => {
    const newState = { ...interactiveState, [key]: value };
    setInteractiveState(newState);
    
    if (enableValidation) {
      const validator = getValidatorForSubject(subject);
      if (validator) {
        const result = validator.validate(newState, effectiveBlueprint);
        if (!result.isValid) {
          setMentorMessage(result.mentorMessage);
          setMentorType('warning');
          onValidationFeedback?.(result);
          
          // Auto-hide after 4 seconds
          setTimeout(() => setMentorMessage(null), 4000);
        }
      }
    }
    
    onStateChange?.(newState);
  }, [interactiveState, subject, effectiveBlueprint, enableValidation, onStateChange, onValidationFeedback]);
  
  // ============ ANIMATION COMPLETE ============
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsAnimating(false);
      setSequenceComplete(true);
      onComplete?.();
    }, TIMING.INTERACTIVE * 1000 + 500);
    
    return () => clearTimeout(timer);
  }, [onComplete]);
  
  // ============ RENDER ============
  return (
    <NotebookPaper 
      className={`universal-sketch-canvas-v6 ${className}`}
      style={{ width, minHeight: height, ...style }}
    >
      {/* Ghost Mentor */}
      <AnimatePresence>
        <GhostMentor
          message={mentorMessage}
          type={mentorType}
          visible={!!mentorMessage}
        />
      </AnimatePresence>
      
      {/* Main SVG Canvas */}
      <svg
        ref={svgRef}
        width="100%"
        height={height}
        viewBox="0 0 400 300"
        preserveAspectRatio="xMidYMid meet"
        style={{ display: 'block' }}
      >
        {/* Filter Definitions */}
        <SketchFilters />
        
        {/* Blueprint Content */}
        <BlueprintRenderer
          blueprint={effectiveBlueprint}
          interactiveState={interactiveState}
          onStateChange={handleStateChange}
        />
      </svg>
      
      {/* Interactive Controls (after animation completes) */}
      <AnimatePresence>
        {sequenceComplete && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            style={{
              padding: '16px 24px',
              borderTop: `2px dashed ${NOTEBOOK_THEME.lineColor}`,
              background: 'rgba(255,255,255,0.5)',
            }}
          >
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
              gap: '16px',
            }}>
              <SketchSlider
                label="Force"
                value={interactiveState.force}
                min={0}
                max={100}
                onChange={(v) => handleStateChange('force', v)}
                color={NOTEBOOK_THEME.markerBlue}
                delay={0.1}
              />
              <SketchSlider
                label="Mass"
                value={interactiveState.mass}
                min={1}
                max={20}
                onChange={(v) => handleStateChange('mass', v)}
                color={NOTEBOOK_THEME.markerGreen}
                delay={0.2}
              />
            </div>
            
            {/* Formula Display */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              style={{
                marginTop: '12px',
                padding: '8px 16px',
                background: NOTEBOOK_THEME.highlightYellow,
                borderRadius: '8px',
                fontFamily: NOTEBOOK_THEME.handwriting,
                fontSize: '16px',
                display: 'inline-block',
                transform: 'rotate(-1deg)',
              }}
            >
              ✏️ a = F/m = {interactiveState.force}/{interactiveState.mass} = <strong>{(interactiveState.force / interactiveState.mass).toFixed(1)} m/s²</strong>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Subject Badge */}
      <div
        style={{
          position: 'absolute',
          bottom: '8px',
          right: '8px',
          padding: '4px 12px',
          background: NOTEBOOK_THEME.highlightBlue,
          borderRadius: '12px',
          fontFamily: NOTEBOOK_THEME.handwriting,
          fontSize: '12px',
          opacity: 0.8,
        }}
      >
        📚 {subject}
      </div>
    </NotebookPaper>
  );
};

// ============================================
// EXPORTS
// ============================================
export { 
  NotebookPaper, 
  GhostMentor, 
  SketchSlider,
  BlueprintRenderer,
  NOTEBOOK_THEME,
};

export default UniversalSketchCanvasV6;


