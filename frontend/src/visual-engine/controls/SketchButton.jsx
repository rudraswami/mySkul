/**
 * 🔘 SKETCH BUTTON
 * =================
 * 
 * Hand-drawn button with RoughJS aesthetics
 * 
 * Features:
 * - RoughJS rectangle border
 * - Hover/press animations
 * - Handwriting font
 * - Icon support
 */

import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import rough from 'roughjs';
import { NOTEBOOK_THEME } from '../sketch/SketchPrimitives';

// ============================================
// SKETCH BUTTON COMPONENT
// ============================================

const SketchButton = ({
  // Content
  children,
  icon,
  
  // Behavior
  onClick,
  disabled = false,
  
  // Styling
  variant = 'primary', // 'primary' | 'secondary' | 'outline'
  color,
  width = 'auto',
  height = 40,
  
  // Animation
  delay = 0,
  
  // Accessibility
  ariaLabel,
  type = 'button',
  
  // Class
  className = '',
}) => {
  const buttonRef = useRef(null);
  const svgRef = useRef(null);
  
  const [buttonPath, setButtonPath] = useState('');
  const [dimensions, setDimensions] = useState({ width: 120, height: 40 });
  const [isPressed, setIsPressed] = useState(false);
  
  // Get colors based on variant
  const getColors = () => {
    const baseColor = color || NOTEBOOK_THEME.markerBlue;
    
    switch (variant) {
      case 'primary':
        return {
          fill: baseColor,
          stroke: NOTEBOOK_THEME.penBlack,
          textColor: '#FFFFFF',
        };
      case 'secondary':
        return {
          fill: NOTEBOOK_THEME.highlightYellow,
          stroke: NOTEBOOK_THEME.penBlack,
          textColor: NOTEBOOK_THEME.penBlack,
        };
      case 'outline':
        return {
          fill: 'transparent',
          stroke: baseColor,
          textColor: baseColor,
        };
      default:
        return {
          fill: baseColor,
          stroke: NOTEBOOK_THEME.penBlack,
          textColor: '#FFFFFF',
        };
    }
  };
  
  const colors = getColors();
  
  // Measure button content
  useEffect(() => {
    if (buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      setDimensions({
        width: width === 'auto' ? Math.max(rect.width, 80) : width,
        height,
      });
    }
  }, [children, icon, width, height]);
  
  // Generate RoughJS button
  useEffect(() => {
    if (svgRef.current) {
      const rc = rough.svg(svgRef.current);
      const button = rc.rectangle(0, 0, dimensions.width, dimensions.height, {
        fill: colors.fill,
        fillStyle: colors.fill === 'transparent' ? undefined : 'solid',
        stroke: colors.stroke,
        strokeWidth: 2,
        roughness: 1.5,
        bowing: 0.5,
      });
      
      const paths = button.querySelectorAll('path');
      if (paths.length > 0) {
        setButtonPath(paths[0].getAttribute('d') || '');
      }
    }
  }, [dimensions, colors]);
  
  const handleClick = (e) => {
    if (!disabled) {
      onClick?.(e);
    }
  };
  
  return (
    <motion.button
      ref={buttonRef}
      type={type}
      className={`sketch-button ${className}`}
      onClick={handleClick}
      disabled={disabled}
      aria-label={ariaLabel}
      onPointerDown={() => setIsPressed(true)}
      onPointerUp={() => setIsPressed(false)}
      onPointerLeave={() => setIsPressed(false)}
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: disabled ? 0.5 : 1, y: 0 }}
      transition={{ delay, duration: 0.3 }}
      whileHover={disabled ? {} : { scale: 1.02, y: -2 }}
      whileTap={disabled ? {} : { scale: 0.98, y: 0 }}
      style={{
        position: 'relative',
        border: 'none',
        background: 'transparent',
        padding: 0,
        cursor: disabled ? 'not-allowed' : 'pointer',
        userSelect: 'none',
        outline: 'none',
      }}
    >
      {/* RoughJS Background */}
      <svg
        ref={svgRef}
        width={dimensions.width}
        height={dimensions.height}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          pointerEvents: 'none',
          filter: isPressed ? 'brightness(0.9)' : 'none',
          transition: 'filter 0.1s',
        }}
      >
        {buttonPath && (
          <path
            d={buttonPath}
            fill={colors.fill}
            stroke={colors.stroke}
            strokeWidth={2}
          />
        )}
      </svg>
      
      {/* Content */}
      <div
        style={{
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
          width: dimensions.width,
          height: dimensions.height,
          padding: '0 16px',
          fontFamily: NOTEBOOK_THEME.handwriting,
          fontSize: '16px',
          fontWeight: 'bold',
          color: colors.textColor,
          pointerEvents: 'none',
        }}
      >
        {icon && <span>{icon}</span>}
        {children}
      </div>
    </motion.button>
  );
};

export default SketchButton;

