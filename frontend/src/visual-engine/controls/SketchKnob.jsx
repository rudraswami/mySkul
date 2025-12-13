/**
 * 🎚️ SKETCH KNOB
 * ===============
 * 
 * Rotary control with RoughJS aesthetics
 * 
 * Features:
 * - Circular knob with indicator
 * - Drag to rotate
 * - Value display
 */

import React, { useState, useRef, useEffect } from 'react';
import { motion, useMotionValue } from 'framer-motion';
import rough from 'roughjs';
import { NOTEBOOK_THEME } from '../sketch/SketchPrimitives';

// ============================================
// SKETCH KNOB COMPONENT
// ============================================

const SketchKnob = ({
  // Value
  value = 50,
  min = 0,
  max = 100,
  onChange,
  
  // Display
  label = '',
  showValue = true,
  unit = '',
  
  // Styling
  color = NOTEBOOK_THEME.markerBlue,
  size = 80,
  
  // Animation
  delay = 0,
  
  // Accessibility
  ariaLabel,
  
  // Class
  className = '',
}) => {
  const knobRef = useRef(null);
  const indicatorRef = useRef(null);
  const containerRef = useRef(null);
  
  const [knobPath, setKnobPath] = useState('');
  const [indicatorPath, setIndicatorPath] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  
  const rotation = useMotionValue(0);
  
  // Calculate rotation from value (-135° to +135°, 270° total range)
  const valueToRotation = (val) => {
    const percentage = (val - min) / (max - min);
    return -135 + percentage * 270;
  };
  
  // Calculate value from rotation
  const rotationToValue = (rot) => {
    // Normalize rotation to 0-270 range
    const normalized = ((rot + 135) % 360 + 360) % 360;
    const clamped = Math.max(0, Math.min(270, normalized));
    const percentage = clamped / 270;
    return min + percentage * (max - min);
  };
  
  // Initialize rotation
  useEffect(() => {
    rotation.set(valueToRotation(value));
  }, [value, rotation]);
  
  // Generate RoughJS knob body
  useEffect(() => {
    if (knobRef.current) {
      const rc = rough.svg(knobRef.current);
      const knob = rc.circle(size / 2, size / 2, size - 10, {
        fill: NOTEBOOK_THEME.paperBg,
        fillStyle: 'solid',
        stroke: NOTEBOOK_THEME.penBlack,
        strokeWidth: 3,
        roughness: 1.5,
      });
      
      const paths = knob.querySelectorAll('path');
      if (paths.length > 0) {
        setKnobPath(paths[0].getAttribute('d') || '');
      }
    }
  }, [size]);
  
  // Generate RoughJS indicator line
  useEffect(() => {
    if (indicatorRef.current) {
      const rc = rough.svg(indicatorRef.current);
      const indicatorLength = size / 3;
      const indicator = rc.line(
        size / 2,
        size / 2 - indicatorLength,
        size / 2,
        size / 2 - 5,
        {
          stroke: color,
          strokeWidth: 4,
          roughness: 1,
        }
      );
      
      const paths = indicator.querySelectorAll('path');
      if (paths.length > 0) {
        setIndicatorPath(paths[0].getAttribute('d') || '');
      }
    }
  }, [size, color]);
  
  // Handle drag
  const handleDrag = (event) => {
    if (!containerRef.current) return;
    
    const rect = containerRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    const deltaX = event.clientX - centerX;
    const deltaY = event.clientY - centerY;
    
    let angle = Math.atan2(deltaY, deltaX) * (180 / Math.PI) + 90;
    
    // Clamp to -135 to +135 range
    if (angle > 180) angle -= 360;
    angle = Math.max(-135, Math.min(135, angle));
    
    rotation.set(angle);
    
    const newValue = Math.round(rotationToValue(angle));
    if (newValue !== value) {
      onChange?.(newValue);
    }
  };
  
  const handlePointerDown = () => {
    setIsDragging(true);
  };
  
  const handlePointerUp = () => {
    setIsDragging(false);
  };
  
  useEffect(() => {
    if (isDragging) {
      const handleMove = (e) => handleDrag(e);
      const handleUp = () => setIsDragging(false);
      
      window.addEventListener('pointermove', handleMove);
      window.addEventListener('pointerup', handleUp);
      
      return () => {
        window.removeEventListener('pointermove', handleMove);
        window.removeEventListener('pointerup', handleUp);
      };
    }
  }, [isDragging]);
  
  return (
    <motion.div
      className={`sketch-knob ${className}`}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay, duration: 0.4 }}
      style={{
        display: 'inline-flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '12px',
        userSelect: 'none',
      }}
    >
      {/* Label */}
      {label && (
        <div
          style={{
            fontFamily: NOTEBOOK_THEME.handwriting,
            fontSize: '16px',
            color: NOTEBOOK_THEME.penBlack,
            textAlign: 'center',
          }}
        >
          {label}
        </div>
      )}
      
      {/* Knob */}
      <div
        ref={containerRef}
        onPointerDown={handlePointerDown}
        style={{
          position: 'relative',
          width: `${size}px`,
          height: `${size}px`,
          cursor: isDragging ? 'grabbing' : 'grab',
        }}
      >
        {/* Knob Body */}
        <svg
          ref={knobRef}
          width={size}
          height={size}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
          }}
        >
          {knobPath && (
            <path
              d={knobPath}
              fill={NOTEBOOK_THEME.paperBg}
              stroke={NOTEBOOK_THEME.penBlack}
              strokeWidth={3}
            />
          )}
        </svg>
        
        {/* Rotating Indicator */}
        <motion.svg
          ref={indicatorRef}
          width={size}
          height={size}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            pointerEvents: 'none',
          }}
          animate={{ rotate: valueToRotation(value) }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        >
          {indicatorPath && (
            <path
              d={indicatorPath}
              fill="none"
              stroke={color}
              strokeWidth={4}
              strokeLinecap="round"
            />
          )}
        </motion.svg>
      </div>
      
      {/* Value Display */}
      {showValue && (
        <motion.div
          style={{
            fontFamily: NOTEBOOK_THEME.handwriting,
            fontSize: '20px',
            fontWeight: 'bold',
            color,
            textAlign: 'center',
          }}
          key={value}
          initial={{ scale: 1.2 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.2 }}
        >
          {value}{unit}
        </motion.div>
      )}
      
      {/* Hidden input for accessibility */}
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange?.(Number(e.target.value))}
        aria-label={ariaLabel || label}
        style={{
          position: 'absolute',
          opacity: 0,
          pointerEvents: 'none',
          width: 1,
          height: 1,
        }}
      />
    </motion.div>
  );
};

export default SketchKnob;

