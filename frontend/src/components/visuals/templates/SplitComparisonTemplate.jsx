/**
 * SplitComparisonTemplate - Side-by-Side Comparison Layout
 * ========================================================
 * 
 * A template for comparing two scenarios in a "split-panel" layout.
 * Each panel looks like a distinct sheet of paper with sketchy aesthetics.
 * 
 * Features:
 * - Two side-by-side "sketch pads"
 * - Central connector (VS badge or arrow)
 * - Synchronized controls
 * - Draw-in animations
 * - Mobile-responsive stacking
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { SketchyFilterDefs, getSketchyFilter } from './SketchyFilters';
import '../styles/SketchTheme.css';

// ============================================
// SKETCH PAD COMPONENT
// ============================================
const SketchPad = ({ 
  title, 
  subtitle,
  children, 
  rotation = 0,
  color = 'blue',
  delay = 0 
}) => {
  const colorMap = {
    blue: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700' },
    orange: { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-700' },
    green: { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700' },
    purple: { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-700' },
  };
  
  const colors = colorMap[color] || colorMap.blue;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20, rotate: 0 }}
      animate={{ opacity: 1, y: 0, rotate: rotation }}
      transition={{ 
        duration: 0.6, 
        delay,
        ease: [0.22, 1, 0.36, 1] // Custom easing for organic feel
      }}
      className="flex-1 min-w-0"
    >
      <div 
        className={`sketch-pad ${colors.bg} border-2 ${colors.border} rounded-xl overflow-hidden h-full`}
        style={{ transform: `rotate(${rotation}deg)` }}
      >
        {/* Pad Header */}
        <div className={`px-4 py-3 border-b-2 ${colors.border} ${colors.bg}`}>
          <h3 
            className={`text-lg font-bold ${colors.text} font-sketch-title`}
            style={{ fontFamily: "'Caveat', cursive" }}
          >
            {title}
          </h3>
          {subtitle && (
            <p 
              className="text-sm text-gray-500 font-sketch"
              style={{ fontFamily: "'Patrick Hand', cursive" }}
            >
              {subtitle}
            </p>
          )}
        </div>
        
        {/* Pad Content */}
        <div className="p-4 flex-1">
          {children}
        </div>
      </div>
    </motion.div>
  );
};

// ============================================
// VS CONNECTOR COMPONENT
// ============================================
const VSConnector = ({ type = 'vs', delay = 0.3 }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ 
        duration: 0.4, 
        delay,
        type: 'spring',
        stiffness: 200
      }}
      className="flex items-center justify-center px-2 md:px-4"
    >
      {type === 'vs' ? (
        <div 
          className="vs-badge flex items-center justify-center w-12 h-12 md:w-14 md:h-14"
          style={{
            background: 'linear-gradient(135deg, #8b5cf6, #3b82f6)',
            borderRadius: '50%',
            boxShadow: '0 4px 12px rgba(139, 92, 246, 0.3)',
          }}
        >
          <span 
            className="text-white text-lg md:text-xl font-bold"
            style={{ fontFamily: "'Caveat', cursive" }}
          >
            VS
          </span>
        </div>
      ) : type === 'arrow' ? (
        <svg width="40" height="40" viewBox="0 0 40 40">
          <motion.path
            d="M 5 20 L 30 20 M 22 12 L 30 20 L 22 28"
            stroke="#8b5cf6"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="none"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.8, delay: delay + 0.2 }}
          />
        </svg>
      ) : (
        <div className="w-1 h-20 bg-gradient-to-b from-purple-300 via-purple-500 to-purple-300 rounded-full" />
      )}
    </motion.div>
  );
};

// ============================================
// CONTROL SLIDER COMPONENT
// ============================================
const SketchSlider = ({ 
  label, 
  value, 
  onChange, 
  min = 0, 
  max = 100, 
  unit = '' 
}) => {
  return (
    <div className="flex flex-col items-center gap-2">
      <label 
        className="text-sm font-medium text-gray-600 font-sketch"
        style={{ fontFamily: "'Patrick Hand', cursive" }}
      >
        {label}
      </label>
      <div className="flex items-center gap-3">
        <input
          type="range"
          min={min}
          max={max}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="sketch-slider w-48"
        />
        <span 
          className="text-lg font-bold text-purple-600 min-w-[60px] text-center font-sketch"
          style={{ fontFamily: "'Patrick Hand', cursive" }}
        >
          {value}{unit}
        </span>
      </div>
    </div>
  );
};

// ============================================
// MAIN SPLIT COMPARISON TEMPLATE
// ============================================
const SplitComparisonTemplate = ({
  leftTitle = "Scenario A",
  leftSubtitle = "",
  leftContent,
  leftColor = "blue",
  rightTitle = "Scenario B",
  rightSubtitle = "",
  rightContent,
  rightColor = "orange",
  connectorType = "vs", // 'vs' | 'arrow' | 'divider'
  controls = null,
  className = "",
}) => {
  return (
    <div className={`w-full h-full flex flex-col bg-sketch-paper ${className}`}>
      {/* Include SVG Filter Definitions */}
      <SketchyFilterDefs />
      
      {/* Main Comparison Area */}
      <div className="flex-1 flex flex-col md:flex-row items-stretch gap-4 md:gap-0 p-4 md:p-6">
        {/* Left Panel */}
        <SketchPad
          title={leftTitle}
          subtitle={leftSubtitle}
          color={leftColor}
          rotation={-0.5}
          delay={0}
        >
          {leftContent}
        </SketchPad>
        
        {/* Connector */}
        <VSConnector type={connectorType} delay={0.3} />
        
        {/* Right Panel */}
        <SketchPad
          title={rightTitle}
          subtitle={rightSubtitle}
          color={rightColor}
          rotation={0.5}
          delay={0.15}
        >
          {rightContent}
        </SketchPad>
      </div>
      
      {/* Control Deck */}
      {controls && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.4 }}
          className="sketch-control-deck"
        >
          {controls}
        </motion.div>
      )}
    </div>
  );
};

// ============================================
// DRAW-IN SVG WRAPPER
// ============================================
export const DrawInSVG = ({ 
  children, 
  width = 300, 
  height = 200, 
  delay = 0,
  className = "" 
}) => {
  return (
    <motion.svg
      width="100%"
      height="100%"
      viewBox={`0 0 ${width} ${height}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay }}
      className={className}
      style={{ filter: getSketchyFilter('light') }}
    >
      {children}
    </motion.svg>
  );
};

// ============================================
// ANIMATED PATH COMPONENT
// ============================================
export const AnimatedPath = ({
  d,
  stroke = "#1e293b",
  strokeWidth = 3,
  fill = "none",
  delay = 0,
  duration = 1.5,
  className = ""
}) => {
  return (
    <motion.path
      d={d}
      stroke={stroke}
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      fill={fill}
      initial={{ pathLength: 0, opacity: 0 }}
      animate={{ pathLength: 1, opacity: 1 }}
      transition={{ 
        pathLength: { duration, delay, ease: "easeInOut" },
        opacity: { duration: 0.3, delay }
      }}
      className={className}
    />
  );
};

// ============================================
// ANIMATED TEXT LABEL
// ============================================
export const AnimatedLabel = ({
  x,
  y,
  children,
  delay = 0,
  color = "#1e293b",
  fontSize = 14,
  className = ""
}) => {
  return (
    <motion.text
      x={x}
      y={y}
      fill={color}
      fontSize={fontSize}
      textAnchor="middle"
      dominantBaseline="middle"
      initial={{ opacity: 0, y: y - 10 }}
      animate={{ opacity: 1, y }}
      transition={{ delay: delay + 1.2, duration: 0.4 }}
      style={{ fontFamily: "'Patrick Hand', cursive" }}
      className={className}
    >
      {children}
    </motion.text>
  );
};

// Export components
export { SketchPad, VSConnector, SketchSlider };
export default SplitComparisonTemplate;


