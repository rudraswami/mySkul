/**
 * 🛡️ VALIDATION FEEDBACK
 * =======================
 * 
 * Visual feedback components for validation errors
 * Integrates with validators (Phase 7)
 */

import React, { useEffect, useState } from 'react';
import { motion, useAnimation } from 'framer-motion';
import { FEEDBACK_TYPE, VALIDATION_STATUS } from '../validators/BaseValidator';
import { TextBubble } from '../narrative';
import rough from 'roughjs/bundled/rough.esm';

// ============================================
// VALIDATION FEEDBACK COMPONENT
// ============================================

export const ValidationFeedback = ({
  validation,
  targetX,
  targetY,
  onComplete,
  children,
}) => {
  const [feedback, setFeedback] = useState(null);
  const controls = useAnimation();
  
  useEffect(() => {
    if (!validation || validation.valid) {
      setFeedback(null);
      return;
    }
    
    // Get primary feedback
    const primaryResult = validation.results[0];
    if (primaryResult) {
      setFeedback({
        type: primaryResult.feedback,
        message: primaryResult.message,
        status: primaryResult.status,
      });
      
      // Trigger animation
      triggerFeedbackAnimation(primaryResult.feedback);
    }
  }, [validation]);
  
  const triggerFeedbackAnimation = async (feedbackType) => {
    switch (feedbackType) {
      case FEEDBACK_TYPE.SHAKE:
        await controls.start({
          x: [0, -10, 10, -10, 10, 0],
          transition: { duration: 0.5 },
        });
        break;
      
      case FEEDBACK_TYPE.DIM:
        await controls.start({
          opacity: [1, 0.3, 1],
          transition: { duration: 0.8 },
        });
        break;
      
      case FEEDBACK_TYPE.GLOW:
        await controls.start({
          filter: [
            'drop-shadow(0 0 0px #4ade80)',
            'drop-shadow(0 0 20px #4ade80)',
            'drop-shadow(0 0 0px #4ade80)',
          ],
          transition: { duration: 1 },
        });
        break;
      
      default:
        break;
    }
    
    onComplete?.();
  };
  
  if (!feedback) {
    return <div>{children}</div>;
  }
  
  return (
    <div style={{ position: 'relative' }}>
      <motion.div animate={controls}>
        {children}
      </motion.div>
      
      {/* Scribble overlay */}
      {feedback.type === FEEDBACK_TYPE.SCRIBBLE && (
        <ScribbleOverlay x={targetX} y={targetY} />
      )}
      
      {/* Ghost Mentor bubble */}
      {feedback.type === FEEDBACK_TYPE.GHOST_MENTOR && (
        <TextBubble
          text={feedback.message}
          x={targetX - 100}
          y={targetY - 120}
          anchorX={targetX}
          anchorY={targetY}
          visible={true}
          typewriter={true}
          style={{ background: '#fee', borderColor: '#f44' }}
        />
      )}
      
      {/* Highlight */}
      {feedback.type === FEEDBACK_TYPE.HIGHLIGHT && (
        <HighlightEffect x={targetX} y={targetY} />
      )}
    </div>
  );
};

// ============================================
// SCRIBBLE OVERLAY
// ============================================

const ScribbleOverlay = ({ x, y, width = 100, height = 100 }) => {
  const canvasRef = React.useRef(null);
  
  useEffect(() => {
    if (!canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const rc = rough.canvas(canvas);
    
    // Draw red scribble
    rc.line(x - 50, y - 50, x + 50, y + 50, {
      stroke: '#ef4444',
      strokeWidth: 3,
      roughness: 2,
    });
    
    rc.line(x + 50, y - 50, x - 50, y + 50, {
      stroke: '#ef4444',
      strokeWidth: 3,
      roughness: 2,
    });
  }, [x, y]);
  
  return (
    <motion.canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{
        position: 'absolute',
        left: x - width / 2,
        top: y - height / 2,
        pointerEvents: 'none',
      }}
      initial={{ opacity: 0, scale: 0.5 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
    />
  );
};

// ============================================
// HIGHLIGHT EFFECT
// ============================================

const HighlightEffect = ({ x, y, size = 120 }) => {
  return (
    <motion.div
      style={{
        position: 'absolute',
        left: x - size / 2,
        top: y - size / 2,
        width: size,
        height: size,
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(250,204,21,0.3), transparent)',
        pointerEvents: 'none',
      }}
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: [0, 1.2, 1], opacity: [0, 0.8, 0.5] }}
      transition={{ duration: 0.8 }}
    />
  );
};

// ============================================
// STATUS INDICATOR
// ============================================

export const ValidationStatusIndicator = ({ status }) => {
  const colors = {
    [VALIDATION_STATUS.VALID]: '#4ade80',
    [VALIDATION_STATUS.WARNING]: '#facc15',
    [VALIDATION_STATUS.ERROR]: '#ef4444',
    [VALIDATION_STATUS.INFO]: '#3b82f6',
  };
  
  const icons = {
    [VALIDATION_STATUS.VALID]: '✓',
    [VALIDATION_STATUS.WARNING]: '⚠',
    [VALIDATION_STATUS.ERROR]: '✗',
    [VALIDATION_STATUS.INFO]: 'ℹ',
  };
  
  return (
    <motion.div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        padding: '4px 8px',
        borderRadius: '12px',
        background: colors[status] + '20',
        color: colors[status],
        fontSize: '14px',
        fontWeight: 600,
      }}
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ type: 'spring', stiffness: 300 }}
    >
      <span>{icons[status]}</span>
      <span style={{ textTransform: 'capitalize' }}>{status}</span>
    </motion.div>
  );
};

export default ValidationFeedback;

