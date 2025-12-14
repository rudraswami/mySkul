/**
 * 🎬 ANIMATED RENDERER
 * ====================
 * 
 * A beat-based animated renderer that makes visuals feel like
 * a teacher is drawing and explaining in real-time.
 * 
 * Key Features:
 * - Beat-by-beat revelation (not all at once)
 * - "Drawing" animations (lines grow, shapes form)
 * - Narration bubbles at each beat
 * - Emphasis effects (glow, pulse, circle)
 * - Cause→Effect animations (force applied → motion result)
 * 
 * This transforms static diagrams into engaging visual stories.
 */

import React, { useState, useEffect, useRef, useMemo } from 'react';
import { motion, AnimatePresence, useAnimation } from 'framer-motion';

// ============================================
// ANIMATION VARIANTS
// ============================================

const ANIMATION_VARIANTS = {
  // Drawing animation - like a pencil drawing
  draw: {
    hidden: { pathLength: 0, opacity: 0 },
    visible: {
      pathLength: 1,
      opacity: 1,
      transition: { duration: 0.8, ease: 'easeInOut' },
    },
  },
  
  // Fade in
  fade: {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { duration: 0.5 },
    },
  },
  
  // Grow from center
  grow: {
    hidden: { scale: 0, opacity: 0 },
    visible: {
      scale: 1,
      opacity: 1,
      transition: { type: 'spring', stiffness: 200, damping: 15 },
    },
  },
  
  // Grow in specific direction (for force vectors)
  grow_right: {
    hidden: { scaleX: 0, opacity: 0, originX: 0 },
    visible: {
      scaleX: 1,
      opacity: 1,
      transition: { duration: 0.6, ease: 'easeOut' },
    },
  },
  
  grow_left: {
    hidden: { scaleX: 0, opacity: 0, originX: 1 },
    visible: {
      scaleX: 1,
      opacity: 1,
      transition: { duration: 0.6, ease: 'easeOut' },
    },
  },
  
  grow_up: {
    hidden: { scaleY: 0, opacity: 0, originY: 1 },
    visible: {
      scaleY: 1,
      opacity: 1,
      transition: { duration: 0.6, ease: 'easeOut' },
    },
  },
  
  grow_down: {
    hidden: { scaleY: 0, opacity: 0, originY: 0 },
    visible: {
      scaleY: 1,
      opacity: 1,
      transition: { duration: 0.6, ease: 'easeOut' },
    },
  },
  
  // Pop in (for formulas, results)
  pop: {
    hidden: { scale: 0, opacity: 0, rotate: -10 },
    visible: {
      scale: 1,
      opacity: 1,
      rotate: 0,
      transition: { type: 'spring', stiffness: 300, damping: 10 },
    },
  },
  
  // Slide in
  slide_right: {
    hidden: { x: -50, opacity: 0 },
    visible: {
      x: 0,
      opacity: 1,
      transition: { type: 'spring', stiffness: 100 },
    },
  },
};

// ============================================
// EMPHASIS EFFECTS
// ============================================

const EmphasisGlow = ({ children, color = '#3498DB', active }) => (
  <motion.g
    animate={active ? {
      filter: [`drop-shadow(0 0 0px ${color})`, `drop-shadow(0 0 15px ${color})`, `drop-shadow(0 0 0px ${color})`],
    } : {}}
    transition={{ duration: 1.5, repeat: Infinity }}
  >
    {children}
  </motion.g>
);

const EmphasisPulse = ({ children, active }) => (
  <motion.g
    animate={active ? { scale: [1, 1.1, 1] } : {}}
    transition={{ duration: 0.8, repeat: 3 }}
  >
    {children}
  </motion.g>
);

const TeacherPointer = ({ x, y, visible }) => (
  <AnimatePresence>
    {visible && (
      <motion.g
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0 }}
      >
        {/* Pointer finger */}
        <motion.text
          x={x - 20}
          y={y - 20}
          fontSize={24}
          animate={{ y: [y - 20, y - 15, y - 20] }}
          transition={{ duration: 0.5, repeat: Infinity }}
        >
          👆
        </motion.text>
      </motion.g>
    )}
  </AnimatePresence>
);

// ============================================
// NARRATION BUBBLE
// ============================================

const NarrationBubble = ({ text, x, y, visible }) => (
  <AnimatePresence>
    {visible && text && (
      <motion.g
        initial={{ opacity: 0, y: y + 20 }}
        animate={{ opacity: 1, y: y }}
        exit={{ opacity: 0, y: y - 20 }}
        transition={{ duration: 0.3 }}
      >
        <rect
          x={x - 100}
          y={y - 30}
          width={200}
          height={40}
          rx={20}
          fill="rgba(52, 73, 94, 0.95)"
        />
        <text
          x={x}
          y={y - 5}
          textAnchor="middle"
          fill="white"
          fontSize={12}
          fontFamily="'Kalam', cursive"
        >
          {text}
        </text>
        {/* Bubble tail */}
        <polygon
          points={`${x - 10},${y + 10} ${x + 10},${y + 10} ${x},${y + 25}`}
          fill="rgba(52, 73, 94, 0.95)"
        />
      </motion.g>
    )}
  </AnimatePresence>
);

// ============================================
// ANIMATED FORCE VECTOR
// ============================================

const AnimatedForceVector = ({ 
  startX, startY, 
  endX, endY, 
  label, 
  color = '#E74C3C',
  animationType = 'grow',
  delay = 0,
  visible = true,
  emphasis = false,
}) => {
  const length = Math.sqrt((endX - startX) ** 2 + (endY - startY) ** 2);
  const angle = Math.atan2(endY - startY, endX - startX) * (180 / Math.PI);
  
  const arrowSize = 12;
  
  return (
    <AnimatePresence>
      {visible && (
        <motion.g
          initial="hidden"
          animate="visible"
          variants={ANIMATION_VARIANTS[animationType] || ANIMATION_VARIANTS.grow}
          style={{ 
            transformOrigin: `${startX}px ${startY}px`,
          }}
          transition={{ delay }}
        >
          <EmphasisPulse active={emphasis}>
            {/* Arrow line */}
            <motion.line
              x1={startX}
              y1={startY}
              x2={endX - arrowSize * Math.cos(angle * Math.PI / 180)}
              y2={endY - arrowSize * Math.sin(angle * Math.PI / 180)}
              stroke={color}
              strokeWidth={3}
              strokeLinecap="round"
            />
            
            {/* Arrow head */}
            <motion.polygon
              points={`
                ${endX},${endY}
                ${endX - arrowSize * Math.cos((angle - 25) * Math.PI / 180)},${endY - arrowSize * Math.sin((angle - 25) * Math.PI / 180)}
                ${endX - arrowSize * Math.cos((angle + 25) * Math.PI / 180)},${endY - arrowSize * Math.sin((angle + 25) * Math.PI / 180)}
              `}
              fill={color}
            />
            
            {/* Label */}
            {label && (
              <motion.text
                x={(startX + endX) / 2 + (angle > 90 || angle < -90 ? -15 : 15)}
                y={(startY + endY) / 2 - 10}
                fill={color}
                fontSize={11}
                fontFamily="'Kalam', cursive"
                fontWeight="bold"
              >
                {label}
              </motion.text>
            )}
          </EmphasisPulse>
        </motion.g>
      )}
    </AnimatePresence>
  );
};

// ============================================
// ANIMATED BODY (BOX/BALL)
// ============================================

const AnimatedBody = ({
  x, y, width, height,
  variant = 'box',
  label,
  animationType = 'draw',
  delay = 0,
  visible = true,
  emphasis = false,
}) => {
  const renderBody = () => {
    switch (variant) {
      case 'ball':
      case 'circle':
        return (
          <circle
            cx={x + width / 2}
            cy={y + height / 2}
            r={Math.min(width, height) / 2}
            fill="#F39C12"
            stroke="#E67E22"
            strokeWidth={3}
          />
        );
      
      case 'box':
      default:
        return (
          <g>
            {/* 3D box effect */}
            <rect
              x={x + 5}
              y={y + 5}
              width={width}
              height={height}
              fill="#E67E22"
              rx={3}
            />
            <rect
              x={x}
              y={y}
              width={width}
              height={height}
              fill="#F39C12"
              stroke="#E67E22"
              strokeWidth={2}
              rx={3}
            />
            {/* Highlight */}
            <rect
              x={x + 5}
              y={y + 5}
              width={width - 10}
              height={10}
              fill="rgba(255,255,255,0.3)"
              rx={2}
            />
          </g>
        );
    }
  };
  
  return (
    <AnimatePresence>
      {visible && (
        <motion.g
          initial="hidden"
          animate="visible"
          variants={ANIMATION_VARIANTS[animationType] || ANIMATION_VARIANTS.draw}
          transition={{ delay }}
        >
          <EmphasisGlow active={emphasis} color="#F39C12">
            {renderBody()}
            
            {/* Label */}
            {label && (
              <text
                x={x + width / 2}
                y={y + height + 20}
                textAnchor="middle"
                fill="#2C3E50"
                fontSize={14}
                fontFamily="'Kalam', cursive"
                fontWeight="bold"
              >
                {label}
              </text>
            )}
          </EmphasisGlow>
        </motion.g>
      )}
    </AnimatePresence>
  );
};

// ============================================
// ANIMATED GROUND/SURFACE
// ============================================

const AnimatedGround = ({
  x, y, width,
  animationType = 'draw',
  delay = 0,
  visible = true,
}) => {
  const hatchCount = Math.floor(width / 15);
  
  return (
    <AnimatePresence>
      {visible && (
        <motion.g
          initial="hidden"
          animate="visible"
          variants={ANIMATION_VARIANTS[animationType]}
          transition={{ delay }}
        >
          {/* Main line */}
          <motion.line
            x1={x}
            y1={y}
            x2={x + width}
            y2={y}
            stroke="#2C3E50"
            strokeWidth={3}
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.8, delay }}
          />
          
          {/* Hatch marks */}
          {Array.from({ length: hatchCount }).map((_, i) => (
            <motion.line
              key={i}
              x1={x + i * 15 + 10}
              y1={y}
              x2={x + i * 15}
              y2={y + 12}
              stroke="#2C3E50"
              strokeWidth={2}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: delay + 0.5 + i * 0.05 }}
            />
          ))}
        </motion.g>
      )}
    </AnimatePresence>
  );
};

// ============================================
// FORMULA BOX
// ============================================

const FormulaBox = ({
  x, y,
  formula,
  animationType = 'pop',
  delay = 0,
  visible = true,
}) => (
  <AnimatePresence>
    {visible && formula && (
      <motion.g
        initial="hidden"
        animate="visible"
        variants={ANIMATION_VARIANTS[animationType]}
        transition={{ delay }}
      >
        <rect
          x={x - 80}
          y={y - 20}
          width={160}
          height={40}
          rx={8}
          fill="#ECF0F1"
          stroke="#3498DB"
          strokeWidth={2}
        />
        <text
          x={x}
          y={y + 5}
          textAnchor="middle"
          fill="#2980B9"
          fontSize={16}
          fontFamily="'Kalam', cursive"
          fontWeight="bold"
        >
          {formula}
        </text>
      </motion.g>
    )}
  </AnimatePresence>
);

// ============================================
// MAIN ANIMATED RENDERER COMPONENT
// ============================================

const AnimatedRenderer = ({
  sceneGraph,
  teachingSequence = null,
  animationBeats = null,         // NEW: Dynamic beats from AnimationDirector
  animationResult = null,        // NEW: Full animation result with strategy
  reasoning = null,              // NEW: Complete reasoning context
  width = 600,
  height = 500,
  autoPlay = true,
  onBeatChange = null,
  onComplete = null,
}) => {
  const [currentBeat, setCurrentBeat] = useState(0);
  const [visibleElements, setVisibleElements] = useState(new Set());
  const [activeNarration, setActiveNarration] = useState(null);
  const [emphasis, setEmphasis] = useState(new Set());
  const timerRef = useRef(null);
  
  // Convert scene graph to render-ready format
  const renderSpec = useMemo(() => {
    if (!sceneGraph) return { nodes: [], arrows: [] };
    
    const nodes = Array.from(sceneGraph.nodes?.values() || []);
    const arrows = sceneGraph.arrows || [];
    
    return { nodes, arrows };
  }, [sceneGraph]);
  
  // Determine which beats to use (v3.0 animationBeats take priority)
  const effectiveBeats = useMemo(() => {
    // Priority: animationBeats (v3.0) > teachingSequence.beats (v2.0)
    if (animationBeats && animationBeats.length > 0) {
      console.log('🎬 [AnimatedRenderer] Using v3.0 animationBeats:', animationBeats.length);
      return animationBeats;
    }
    if (teachingSequence?.beats?.length > 0) {
      console.log('🎬 [AnimatedRenderer] Using v2.0 teachingSequence:', teachingSequence.beats.length);
      return teachingSequence.beats;
    }
    return [];
  }, [animationBeats, teachingSequence]);

  // Log animation strategy for debugging
  useEffect(() => {
    if (animationResult) {
      console.log('🎬 [AnimatedRenderer] Animation Strategy:', animationResult.strategy);
    }
    if (reasoning?.intent) {
      console.log('🎬 [AnimatedRenderer] Intent:', reasoning.intent.primary);
    }
  }, [animationResult, reasoning]);

  // Play teaching sequence
  useEffect(() => {
    if (effectiveBeats.length === 0 || !autoPlay) {
      // If no sequence, show everything immediately
      const allIds = new Set(renderSpec.nodes.map(n => n.id));
      setVisibleElements(allIds);
      return;
    }
    
    const beats = effectiveBeats;
    if (beats.length === 0) return;
    
    let beatIndex = 0;
    
    const playBeat = () => {
      if (beatIndex >= beats.length) {
        onComplete?.();
        return;
      }
      
      const beat = beats[beatIndex];
      console.log(`🎬 [AnimatedRenderer] Playing beat ${beatIndex + 1}/${beats.length}:`, beat.type);
      
      // Update visible elements - handle multiple beat formats
      setVisibleElements(prev => {
        const next = new Set(prev);
        
        // v3.0 format: slots/slotName (from AnimationDirector)
        if (beat.slots && Array.isArray(beat.slots)) {
          beat.slots.forEach(slotName => next.add(slotName));
        } else if (beat.slotName) {
          next.add(beat.slotName);
        }
        
        // v2.0 format: entities (from TeachingBeatEngine)
        if (beat.entities && Array.isArray(beat.entities)) {
          beat.entities.forEach(id => next.add(id));
        }
        
        // If beat has type 'pause', don't add any elements (just a delay)
        // No need for explicit handling - just skip
        
        return next;
      });
      
      // Update narration
      if (beat.narration) {
        setActiveNarration(beat.narration);
      }
      
      // Update emphasis
      if (beat.emphasis && Array.isArray(beat.emphasis)) {
        setEmphasis(new Set(beat.emphasis));
        // Clear emphasis after duration
        const duration = beat.duration || 1000;
        setTimeout(() => setEmphasis(new Set()), duration);
      }
      
      onBeatChange?.(beatIndex, beat);
      setCurrentBeat(beatIndex);
      
      // Schedule next beat with safe defaults
      beatIndex++;
      const beatDuration = beat.duration || 1000;
      const beatDelay = beat.delay || 200;
      timerRef.current = setTimeout(playBeat, beatDuration + beatDelay);
    };
    
    // Start playing after initial delay
    timerRef.current = setTimeout(playBeat, 500);
    
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [teachingSequence, autoPlay, renderSpec, onBeatChange, onComplete]);
  
  // Render a node based on its type
  const renderNode = (node, delay = 0) => {
    const isVisible = visibleElements.has(node.id) || !teachingSequence;
    const isEmphasized = emphasis.has(node.id);
    const primitive = node.primitive || 'generic';
    
    // Get animation type based on direction for forces
    let animationType = 'draw';
    if (primitive === 'force_vector') {
      const dir = node.style?.direction || 'right';
      animationType = `grow_${dir}`;
    }
    
    switch (primitive) {
      case 'body':
        return (
          <AnimatedBody
            key={node.id}
            x={node.x}
            y={node.y}
            width={node.width}
            height={node.height}
            variant={node.entity?.properties?.variant || 'box'}
            label={node.entity?.properties?.label}
            animationType={animationType}
            delay={delay}
            visible={isVisible}
            emphasis={isEmphasized}
          />
        );
      
      case 'force_vector':
        const startPoint = node.style?.startPoint || { x: node.x, y: node.y };
        const endPoint = node.style?.endPoint || { 
          x: node.x + node.width, 
          y: node.y 
        };
        return (
          <AnimatedForceVector
            key={node.id}
            startX={startPoint.x}
            startY={startPoint.y}
            endX={endPoint.x}
            endY={endPoint.y}
            label={node.entity?.properties?.label}
            color={node.entity?.properties?.color || '#E74C3C'}
            animationType={animationType}
            delay={delay}
            visible={isVisible}
            emphasis={isEmphasized}
          />
        );
      
      case 'structure':
        return (
          <AnimatedGround
            key={node.id}
            x={node.x}
            y={node.y}
            width={node.width}
            animationType="draw"
            delay={delay}
            visible={isVisible}
          />
        );
      
      default:
        // Generic shape
        return (
          <motion.g
            key={node.id}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={isVisible ? { opacity: 1, scale: 1 } : {}}
            transition={{ delay, duration: 0.5 }}
          >
            <rect
              x={node.x}
              y={node.y}
              width={node.width}
              height={node.height}
              rx={5}
              fill="#ECF0F1"
              stroke="#2C3E50"
              strokeWidth={2}
            />
            {node.entity?.properties?.label && (
              <text
                x={node.x + node.width / 2}
                y={node.y + node.height / 2 + 4}
                textAnchor="middle"
                fill="#2C3E50"
                fontSize={12}
              >
                {node.entity.properties.label}
              </text>
            )}
          </motion.g>
        );
    }
  };
  
  return (
    <svg
      width={width}
      height={height}
      style={{ background: 'transparent' }}
    >
      {/* Definitions */}
      <defs>
        <filter id="glow">
          <feGaussianBlur stdDeviation="3" result="coloredBlur" />
          <feMerge>
            <feMergeNode in="coloredBlur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      
      {/* Render all nodes */}
      <g>
        {renderSpec.nodes.map((node, i) => renderNode(node, i * 0.1))}
      </g>
      
      {/* Narration bubble */}
      <NarrationBubble
        text={activeNarration}
        x={width / 2}
        y={height - 60}
        visible={!!activeNarration}
      />
      
      {/* Beat indicator */}
      {teachingSequence && (
        <g transform={`translate(${width - 100}, 20)`}>
          <text fill="#999" fontSize={10}>
            Beat {currentBeat + 1} / {teachingSequence.beats?.length || 0}
          </text>
        </g>
      )}
    </svg>
  );
};

export default AnimatedRenderer;

