/**
 * 🎛️ SKETCH SLIDER WITH VALIDATION
 * ==================================
 * 
 * Enhanced SketchSlider with validator integration
 * Provides real-time feedback for invalid values
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, useMotionValue, useTransform, useAnimation } from 'framer-motion';
import rough from 'roughjs';
import { NOTEBOOK_THEME } from '../sketch/SketchPrimitives';
import { useValidationFeedback } from '../feedback/useValidationFeedback';
import { ValidationFeedback } from '../feedback/ValidationFeedback';

// ============================================
// SKETCH SLIDER WITH VALIDATION
// ============================================

export const SketchSliderWithValidation = ({
  // Value props
  value = 50,
  min = 0,
  max = 100,
  step = 1,
  onChange,
  
  // Display props
  label = '',
  showValue = true,
  unit = '',
  
  // Validation props
  subject = 'general',
  property = null,
  validationContext = {},
  enableValidation = true,
  onValidationError,
  
  // Styling
  color = NOTEBOOK_THEME.markerBlue,
  width = 200,
  thumbSize = 20,
  
  // Animation
  delay = 0,
  
  // Class
  className = '',
}) => {
  const [currentValue, setCurrentValue] = useState(value);
  const [isDragging, setIsDragging] = useState(false);
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const thumbX = useMotionValue(0);
  const controls = useAnimation();
  
  // Validator
  const { validate, validation, isValid, errors } = useValidationFeedback(subject);
  const [showValidationFeedback, setShowValidationFeedback] = useState(false);
  
  // Calculate thumb position
  const railWidth = width - thumbSize;
  const percentage = ((currentValue - min) / (max - min)) * 100;
  const thumbPosition = (currentValue - min) / (max - min) * railWidth;
  
  // Update thumb position when value changes
  useEffect(() => {
    thumbX.set(thumbPosition);
  }, [thumbPosition, thumbX]);
  
  // Draw RoughJS elements
  useEffect(() => {
    if (!canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const rc = rough.canvas(canvas);
    
    // Clear canvas
    ctx.clearRect(0, 0, width, 100);
    
    // Draw rail (sketchy line)
    rc.line(thumbSize/2, 40, width - thumbSize/2, 40, {
      stroke: isValid ? '#94A3B8' : '#EF4444',
      strokeWidth: 3,
      roughness: 1.5,
      bowing: 1,
    });
    
    // Draw value markers (at min and max)
    rc.circle(thumbSize/2, 40, 4, {
      fill: '#CBD5E1',
      fillStyle: 'solid',
    });
    
    rc.circle(width - thumbSize/2, 40, 4, {
      fill: '#CBD5E1',
      fillStyle: 'solid',
    });
  }, [width, thumbSize, isValid]);
  
  // Handle drag
  const handlePointerDown = useCallback((e) => {
    setIsDragging(true);
    e.currentTarget.setPointerCapture(e.pointerId);
  }, []);
  
  const handlePointerMove = useCallback((e) => {
    if (!isDragging || !containerRef.current) return;
    
    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const railWidth = width - thumbSize;
    
    // Calculate new value
    const percentage = Math.max(0, Math.min(1, (x - thumbSize/2) / railWidth));
    const newValue = min + percentage * (max - min);
    const steppedValue = Math.round(newValue / step) * step;
    
    if (steppedValue !== currentValue) {
      handleValueChange(steppedValue);
    }
  }, [isDragging, width, thumbSize, min, max, step, currentValue]);
  
  const handlePointerUp = useCallback((e) => {
    setIsDragging(false);
    e.currentTarget.releasePointerCapture(e.pointerId);
  }, []);
  
  // Handle value change with validation
  const handleValueChange = (newValue) => {
    const clampedValue = Math.max(min, Math.min(max, newValue));
    setCurrentValue(clampedValue);
    
    // Validate
    if (enableValidation && property) {
      const validationResult = validate(clampedValue, property, {
        ...validationContext,
        min,
        max,
      });
      
      // Show feedback if invalid
      if (!validationResult.valid) {
        setShowValidationFeedback(true);
        onValidationError?.(validationResult);
        
        // Trigger shake animation
        controls.start({
          x: [0, -5, 5, -5, 5, 0],
          transition: { duration: 0.4 }
        });
        
        // Log error
        console.log('⚠️ Validation Error:', validationResult.results[0]?.message);
        
        // Hide feedback after 3 seconds
        setTimeout(() => setShowValidationFeedback(false), 3000);
      } else {
        setShowValidationFeedback(false);
      }
      
      // Call onChange only if valid
      if (validationResult.valid) {
        onChange?.(clampedValue);
      }
    } else {
      // No validation, always call onChange
      onChange?.(clampedValue);
    }
  };
  
  // Calculate thumb position for display
  const displayThumbX = useTransform(
    thumbX,
    [0, railWidth],
    [thumbSize/2, width - thumbSize/2]
  );
  
  return (
    <ValidationFeedback
      validation={showValidationFeedback ? validation : null}
      targetX={width / 2}
      targetY={40}
      onComplete={() => setShowValidationFeedback(false)}
    >
      <motion.div
        ref={containerRef}
        className={className}
        style={{
          width,
          height: 80,
          position: 'relative',
          userSelect: 'none',
        }}
        animate={controls}
      >
        {/* Label */}
        <div
          style={{
            fontFamily: NOTEBOOK_THEME.handwriting,
            fontSize: '14px',
            color: isValid ? '#333' : '#EF4444',
            marginBottom: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <span>{label}</span>
          {showValue && (
            <span style={{ fontWeight: 'bold' }}>
              {currentValue}{unit}
            </span>
          )}
          {!isValid && <span>⚠️</span>}
        </div>
        
        {/* Canvas for RoughJS rail */}
        <canvas
          ref={canvasRef}
          width={width}
          height={100}
          style={{
            position: 'absolute',
            top: '20px',
            left: 0,
            pointerEvents: 'none',
          }}
        />
        
        {/* Thumb (draggable) */}
        <motion.div
          style={{
            position: 'absolute',
            top: '30px',
            x: displayThumbX,
            width: thumbSize,
            height: thumbSize,
            cursor: isDragging ? 'grabbing' : 'grab',
            touchAction: 'none',
          }}
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        >
          <svg width={thumbSize} height={thumbSize}>
            <circle
              cx={thumbSize / 2}
              cy={thumbSize / 2}
              r={thumbSize / 2 - 2}
              fill={isValid ? color : '#EF4444'}
              stroke="#fff"
              strokeWidth="2"
              filter="url(#hand-drawn)"
            />
          </svg>
        </motion.div>
        
        {/* Min/Max labels */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginTop: '50px',
            fontFamily: NOTEBOOK_THEME.handwriting,
            fontSize: '11px',
            color: '#999',
          }}
        >
          <span>{min}{unit}</span>
          <span>{max}{unit}</span>
        </div>
        
        {/* Validation error message (inline) */}
        {!isValid && errors.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            style={{
              marginTop: '4px',
              padding: '6px 10px',
              background: '#FEE2E2',
              border: '1px solid #EF4444',
              borderRadius: '6px',
              fontSize: '11px',
              fontFamily: NOTEBOOK_THEME.handwriting,
              color: '#DC2626',
            }}
          >
            {errors[0].message}
          </motion.div>
        )}
      </motion.div>
    </ValidationFeedback>
  );
};

export default SketchSliderWithValidation;








