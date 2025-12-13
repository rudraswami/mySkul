/**
 * 🎛️ SKETCH SLIDER
 * ================
 * 
 * Hand-drawn slider with RoughJS aesthetics
 * NO HTML <input type="range"> - Pure SVG!
 * 
 * Features:
 * - RoughJS rail (wobbly line)
 * - RoughJS thumb (circle with wobble)
 * - Drag interaction (pointer events - mouse + touch unified)
 * - Smooth Framer Motion animation
 * - Value labels in handwriting font
 * - Accessible (hidden HTML input for screen readers)
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, useMotionValue, useTransform } from 'framer-motion';
import rough from 'roughjs';
import { NOTEBOOK_THEME } from '../sketch/SketchPrimitives';

// ============================================
// SKETCH SLIDER COMPONENT
// ============================================

const SketchSlider = ({
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
  
  // Styling
  color = NOTEBOOK_THEME.markerBlue,
  width = 200,
  thumbSize = 20,
  
  // Animation
  delay = 0,
  
  // Accessibility
  ariaLabel,
  
  // Class
  className = '',
}) => {
  const railRef = useRef(null);
  const thumbRef = useRef(null);
  const containerRef = useRef(null);
  
  const [railPath, setRailPath] = useState('');
  const [thumbPath, setThumbPath] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  
  // Motion value for smooth dragging
  const x = useMotionValue(0);
  
  // Calculate position from value
  const valueToPosition = useCallback((val) => {
    const percentage = (val - min) / (max - min);
    return percentage * width;
  }, [min, max, width]);
  
  // Calculate value from position
  const positionToValue = useCallback((pos) => {
    const percentage = Math.max(0, Math.min(1, pos / width));
    const rawValue = min + percentage * (max - min);
    const steppedValue = Math.round(rawValue / step) * step;
    return Math.max(min, Math.min(max, steppedValue));
  }, [min, max, width, step]);
  
  // Initialize position
  useEffect(() => {
    x.set(valueToPosition(value));
  }, [value, x, valueToPosition]);
  
  // Generate RoughJS rail
  useEffect(() => {
    if (railRef.current) {
      const rc = rough.svg(railRef.current);
      const rail = rc.line(0, 0, width, 0, {
        stroke: NOTEBOOK_THEME.lineColor,
        strokeWidth: 3,
        roughness: 1.5,
        bowing: 0.5,
      });
      
      const paths = rail.querySelectorAll('path');
      if (paths.length > 0) {
        setRailPath(paths[0].getAttribute('d') || '');
      }
    }
  }, [width]);
  
  // Generate RoughJS thumb
  useEffect(() => {
    if (thumbRef.current) {
      const rc = rough.svg(thumbRef.current);
      const thumb = rc.circle(0, 0, thumbSize, {
        fill: color,
        fillStyle: 'solid',
        stroke: NOTEBOOK_THEME.penBlack,
        strokeWidth: 2,
        roughness: 1.5,
      });
      
      const paths = thumb.querySelectorAll('path');
      if (paths.length > 0) {
        setThumbPath(paths[0].getAttribute('d') || '');
      }
    }
  }, [thumbSize, color]);
  
  // Handle drag
  const handleDrag = useCallback((event, info) => {
    const newPosition = Math.max(0, Math.min(width, info.point.x));
    x.set(newPosition);
    
    const newValue = positionToValue(newPosition);
    if (newValue !== value) {
      onChange?.(newValue);
    }
  }, [width, x, positionToValue, value, onChange]);
  
  // Handle pointer down (start drag)
  const handlePointerDown = useCallback((event) => {
    setIsDragging(true);
    
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const clickX = event.clientX - rect.left;
      const newValue = positionToValue(clickX);
      
      x.set(valueToPosition(newValue));
      onChange?.(newValue);
    }
  }, [x, positionToValue, valueToPosition, onChange]);
  
  // Handle pointer up (end drag)
  const handlePointerUp = useCallback(() => {
    setIsDragging(false);
  }, []);
  
  return (
    <motion.div
      className={`sketch-slider ${className}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      style={{
        display: 'flex',
        flexDirection: 'column',
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
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span>{label}</span>
          {showValue && (
            <span style={{ fontWeight: 'bold', color }}>
              {value}{unit}
            </span>
          )}
        </div>
      )}
      
      {/* Slider Container */}
      <div
        ref={containerRef}
        onPointerDown={handlePointerDown}
        onPointerUp={handlePointerUp}
        style={{
          position: 'relative',
          width: `${width}px`,
          height: `${thumbSize + 20}px`,
          cursor: isDragging ? 'grabbing' : 'pointer',
        }}
      >
        {/* Rail (RoughJS) */}
        <svg
          ref={railRef}
          width={width}
          height={thumbSize + 20}
          style={{
            position: 'absolute',
            top: '50%',
            left: 0,
            transform: 'translateY(-50%)',
            pointerEvents: 'none',
          }}
        >
          {railPath && (
            <path
              d={railPath}
              fill="none"
              stroke={NOTEBOOK_THEME.lineColor}
              strokeWidth={3}
              strokeLinecap="round"
            />
          )}
          
          {/* Active portion (colored) */}
          {railPath && (
            <motion.path
              d={railPath}
              fill="none"
              stroke={color}
              strokeWidth={3}
              strokeLinecap="round"
              style={{
                pathLength: useTransform(x, [0, width], [0, 1]),
              }}
            />
          )}
        </svg>
        
        {/* Thumb (RoughJS) - Draggable */}
        <motion.div
          drag="x"
          dragConstraints={{ left: 0, right: width }}
          dragElastic={0}
          dragMomentum={false}
          onDrag={handleDrag}
          style={{
            position: 'absolute',
            top: '50%',
            left: 0,
            x,
            y: '-50%',
            cursor: isDragging ? 'grabbing' : 'grab',
            touchAction: 'none',
          }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        >
          <svg
            ref={thumbRef}
            width={thumbSize * 2}
            height={thumbSize * 2}
            style={{
              overflow: 'visible',
              filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))',
            }}
          >
            <g transform={`translate(${thumbSize}, ${thumbSize})`}>
              {thumbPath && (
                <path
                  d={thumbPath}
                  fill={color}
                  stroke={NOTEBOOK_THEME.penBlack}
                  strokeWidth={2}
                />
              )}
            </g>
          </svg>
        </motion.div>
      </div>
      
      {/* Hidden HTML input for accessibility */}
      <input
        type="range"
        min={min}
        max={max}
        step={step}
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

export default SketchSlider;

