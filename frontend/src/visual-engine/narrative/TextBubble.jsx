/**
 * 💬 TEXT BUBBLE
 * ==============
 * 
 * Speech bubble with typewriter effect for narrative beats
 * Hand-drawn border with RoughJS
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import rough from 'roughjs';
import { NOTEBOOK_THEME } from '../sketch/SketchPrimitives';

// ============================================
// TEXT BUBBLE COMPONENT
// ============================================

const TextBubble = ({
  // Content
  text = '',
  
  // Position
  x = 200,
  y = 50,
  anchorX, // Point to anchor tail to (hand/element position)
  anchorY,
  
  // Styling
  width = 200,
  padding = 16,
  backgroundColor = '#FEF3C7',
  borderColor = NOTEBOOK_THEME.penBlack,
  
  // Animation
  typewriter = true,
  typewriterSpeed = 0.03, // seconds per character
  delay = 0,
  
  // Visibility
  visible = true,
  
  // Callbacks
  onComplete,
  
  // Class
  className = '',
}) => {
  const bubbleRef = useRef(null);
  const svgRef = useRef(null);
  
  const [bubblePath, setBubblePath] = useState('');
  const [tailPath, setTailPath] = useState('');
  const [visibleText, setVisibleText] = useState(typewriter ? '' : text);
  const [isTyping, setIsTyping] = useState(typewriter);
  
  // Generate RoughJS bubble
  useEffect(() => {
    if (svgRef.current) {
      const rc = rough.svg(svgRef.current);
      
      // Main bubble (rounded rectangle)
      const bubble = rc.rectangle(0, 0, width, 80, {
        fill: backgroundColor,
        fillStyle: 'solid',
        stroke: borderColor,
        strokeWidth: 2,
        roughness: 1.5,
        bowing: 1,
      });
      
      const paths = bubble.querySelectorAll('path');
      if (paths.length > 0) {
        setBubblePath(paths[0].getAttribute('d') || '');
      }
      
      // Tail (if anchor point provided)
      if (anchorX !== undefined && anchorY !== undefined) {
        const relativeAnchorX = anchorX - x;
        const relativeAnchorY = anchorY - y;
        
        // Determine tail position (bottom-left of bubble)
        const tailStartX = 20;
        const tailStartY = 80;
        
        const tailPathStr = `M ${tailStartX} ${tailStartY} Q ${tailStartX - 10} ${tailStartY + 10} ${relativeAnchorX} ${relativeAnchorY}`;
        
        const tail = rc.path(tailPathStr, {
          stroke: borderColor,
          strokeWidth: 2,
          roughness: 1.5,
        });
        
        const tailPaths = tail.querySelectorAll('path');
        if (tailPaths.length > 0) {
          setTailPath(tailPaths[0].getAttribute('d') || '');
        }
      }
    }
  }, [width, backgroundColor, borderColor, x, y, anchorX, anchorY]);
  
  // Typewriter effect
  useEffect(() => {
    if (!typewriter || !text) {
      setVisibleText(text);
      setIsTyping(false);
      return;
    }
    
    setVisibleText('');
    setIsTyping(true);
    
    let currentIndex = 0;
    const startTime = Date.now() + delay * 1000;
    
    const typeInterval = setInterval(() => {
      const elapsed = (Date.now() - startTime) / 1000;
      const targetIndex = Math.floor(elapsed / typewriterSpeed);
      
      if (targetIndex > currentIndex && currentIndex < text.length) {
        currentIndex = targetIndex;
        setVisibleText(text.slice(0, currentIndex + 1));
      }
      
      if (currentIndex >= text.length) {
        setIsTyping(false);
        clearInterval(typeInterval);
        onComplete?.();
      }
    }, typewriterSpeed * 1000);
    
    return () => clearInterval(typeInterval);
  }, [text, typewriter, typewriterSpeed, delay, onComplete]);
  
  if (!visible) return null;
  
  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          ref={bubbleRef}
          className={`text-bubble ${className}`}
          initial={{ opacity: 0, scale: 0.8, y: -10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.8, y: -10 }}
          transition={{
            delay,
            type: 'spring',
            stiffness: 300,
            damping: 25,
          }}
          style={{
            position: 'absolute',
            left: x,
            top: y,
            zIndex: 999,
            pointerEvents: 'none',
          }}
        >
          {/* RoughJS Bubble */}
          <svg
            ref={svgRef}
            width={width}
            height={100}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
            }}
          >
            {/* Tail (speech bubble pointer) */}
            {tailPath && (
              <path
                d={tailPath}
                fill="none"
                stroke={borderColor}
                strokeWidth={2}
              />
            )}
            
            {/* Bubble background */}
            {bubblePath && (
              <path
                d={bubblePath}
                fill={backgroundColor}
                stroke={borderColor}
                strokeWidth={2}
              />
            )}
          </svg>
          
          {/* Text Content */}
          <div
            style={{
              position: 'relative',
              padding: `${padding}px`,
              fontFamily: NOTEBOOK_THEME.handwriting,
              fontSize: '16px',
              lineHeight: '1.5',
              color: NOTEBOOK_THEME.penBlack,
              width: `${width}px`,
              minHeight: '80px',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <span>
              {visibleText}
              {isTyping && typewriter && (
                <motion.span
                  animate={{ opacity: [1, 0, 1] }}
                  transition={{ duration: 0.8, repeat: Infinity }}
                >
                  |
                </motion.span>
              )}
            </span>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

// ============================================
// PRESET BUBBLE TYPES
// ============================================

/**
 * Hint bubble (yellow)
 */
export const HintBubble = (props) => (
  <TextBubble
    {...props}
    backgroundColor="#FEF3C7"
    borderColor={NOTEBOOK_THEME.penBlack}
  />
);

/**
 * Insight bubble (blue)
 */
export const InsightBubble = (props) => (
  <TextBubble
    {...props}
    backgroundColor="#DBEAFE"
    borderColor={NOTEBOOK_THEME.inkBlue}
  />
);

/**
 * Encouragement bubble (green)
 */
export const EncouragementBubble = (props) => (
  <TextBubble
    {...props}
    backgroundColor="#D1FAE5"
    borderColor={NOTEBOOK_THEME.markerGreen}
  />
);

/**
 * Memory hook bubble (pink)
 */
export const MemoryHookBubble = (props) => (
  <TextBubble
    {...props}
    backgroundColor="#FCE7F3"
    borderColor={NOTEBOOK_THEME.highlightPink}
  />
);

// ============================================
// DEFAULT EXPORT
// ============================================

export default TextBubble;

