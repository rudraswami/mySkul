/**
 * 🔘 SKETCH TOGGLE
 * =================
 * 
 * Hand-drawn toggle switch with RoughJS aesthetics
 * NO HTML checkbox - Pure SVG!
 * 
 * Features:
 * - RoughJS track (wobbly pill shape)
 * - RoughJS knob (circle with wobble)
 * - Click to toggle
 * - Smooth animation
 * - Accessible
 */

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import rough from 'roughjs';
import { NOTEBOOK_THEME } from '../sketch/SketchPrimitives';

// ============================================
// SKETCH TOGGLE COMPONENT
// ============================================

const SketchToggle = ({
  // Value
  checked = false,
  onChange,
  
  // Display
  label = '',
  
  // Styling
  colorOn = NOTEBOOK_THEME.markerGreen,
  colorOff = NOTEBOOK_THEME.lineColor,
  width = 60,
  height = 30,
  
  // Animation
  delay = 0,
  
  // Accessibility
  ariaLabel,
  
  // Class
  className = '',
}) => {
  const trackRef = useRef(null);
  const knobRef = useRef(null);
  
  const [trackPathOn, setTrackPathOn] = useState('');
  const [trackPathOff, setTrackPathOff] = useState('');
  const [knobPath, setKnobPath] = useState('');
  
  const knobSize = height - 8;
  const knobX = checked ? width - knobSize - 4 : 4;
  
  // Generate RoughJS track (ON state)
  useEffect(() => {
    if (trackRef.current) {
      const rc = rough.svg(trackRef.current);
      const track = rc.rectangle(0, 0, width, height, {
        fill: colorOn,
        fillStyle: 'solid',
        stroke: NOTEBOOK_THEME.penBlack,
        strokeWidth: 2,
        roughness: 1.5,
        bowing: 1,
      });
      
      const paths = track.querySelectorAll('path');
      if (paths.length > 0) {
        setTrackPathOn(paths[0].getAttribute('d') || '');
      }
    }
  }, [width, height, colorOn]);
  
  // Generate RoughJS track (OFF state)
  useEffect(() => {
    if (trackRef.current) {
      const rc = rough.svg(trackRef.current);
      const track = rc.rectangle(0, 0, width, height, {
        fill: colorOff,
        fillStyle: 'solid',
        stroke: NOTEBOOK_THEME.penBlack,
        strokeWidth: 2,
        roughness: 1.5,
        bowing: 1,
      });
      
      const paths = track.querySelectorAll('path');
      if (paths.length > 0) {
        setTrackPathOff(paths[0].getAttribute('d') || '');
      }
    }
  }, [width, height, colorOff]);
  
  // Generate RoughJS knob
  useEffect(() => {
    if (knobRef.current) {
      const rc = rough.svg(knobRef.current);
      const knob = rc.circle(knobSize / 2, knobSize / 2, knobSize, {
        fill: '#FFFFFF',
        fillStyle: 'solid',
        stroke: NOTEBOOK_THEME.penBlack,
        strokeWidth: 2,
        roughness: 1.5,
      });
      
      const paths = knob.querySelectorAll('path');
      if (paths.length > 0) {
        setKnobPath(paths[0].getAttribute('d') || '');
      }
    }
  }, [knobSize]);
  
  const handleClick = () => {
    onChange?.(!checked);
  };
  
  return (
    <motion.div
      className={`sketch-toggle ${className}`}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay, duration: 0.3 }}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '12px',
        cursor: 'pointer',
        userSelect: 'none',
      }}
      onClick={handleClick}
    >
      {/* Toggle Switch */}
      <div
        style={{
          position: 'relative',
          width: `${width}px`,
          height: `${height}px`,
        }}
      >
        {/* Track */}
        <svg
          ref={trackRef}
          width={width}
          height={height}
          style={{ position: 'absolute', top: 0, left: 0 }}
        >
          <AnimatePresence mode="wait">
            {checked ? (
              trackPathOn && (
                <motion.path
                  key="on"
                  d={trackPathOn}
                  fill={colorOn}
                  stroke={NOTEBOOK_THEME.penBlack}
                  strokeWidth={2}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                />
              )
            ) : (
              trackPathOff && (
                <motion.path
                  key="off"
                  d={trackPathOff}
                  fill={colorOff}
                  stroke={NOTEBOOK_THEME.penBlack}
                  strokeWidth={2}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                />
              )
            )}
          </AnimatePresence>
        </svg>
        
        {/* Knob */}
        <motion.div
          style={{
            position: 'absolute',
            top: '4px',
            left: '4px',
          }}
          animate={{ x: knobX }}
          transition={{ type: 'spring', stiffness: 500, damping: 30 }}
        >
          <svg
            ref={knobRef}
            width={knobSize}
            height={knobSize}
            style={{
              filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))',
            }}
          >
            {knobPath && (
              <path
                d={knobPath}
                fill="#FFFFFF"
                stroke={NOTEBOOK_THEME.penBlack}
                strokeWidth={2}
              />
            )}
          </svg>
        </motion.div>
      </div>
      
      {/* Label */}
      {label && (
        <span
          style={{
            fontFamily: NOTEBOOK_THEME.handwriting,
            fontSize: '16px',
            color: NOTEBOOK_THEME.penBlack,
          }}
        >
          {label}
        </span>
      )}
      
      {/* Hidden checkbox for accessibility */}
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange?.(e.target.checked)}
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

export default SketchToggle;

