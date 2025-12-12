/**
 * ForceComparisonTemplate - Split-Panel Force Visualization
 * =========================================================
 * 
 * Demonstrates Newton's Second Law (F = ma) through side-by-side comparison.
 * Left panel shows small force, right panel shows large force.
 * A single slider controls both simultaneously to show the contrast.
 * 
 * Features:
 * - Sketchy stick figures pushing blocks
 * - Hand-drawn arrows (size proportional to force)
 * - Real-time synchronized animation
 * - Draw-in animation effect
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion, useAnimationControls } from 'framer-motion';
import SplitComparisonTemplate, { 
  DrawInSVG, 
  AnimatedPath, 
  AnimatedLabel,
  SketchSlider 
} from './SplitComparisonTemplate';
import { getSketchyFilter } from './SketchyFilters';

// ============================================
// STICK FIGURE COMPONENT (Hand-drawn style)
// ============================================
const StickFigure = ({ 
  x, 
  y, 
  size = 'small', // 'small' | 'large'
  pushing = false,
  delay = 0 
}) => {
  const scale = size === 'large' ? 1.3 : 1;
  const headRadius = size === 'large' ? 12 : 10;
  const color = size === 'large' ? '#f97316' : '#3b82f6'; // Orange for big, blue for small
  
  // Pushing animation - lean forward
  const bodyAngle = pushing ? -15 : 0;
  
  return (
    <motion.g
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay, duration: 0.5 }}
      style={{ filter: getSketchyFilter('light') }}
    >
      {/* Head */}
      <motion.circle
        cx={x}
        cy={y - 40 * scale}
        r={headRadius}
        stroke={color}
        strokeWidth="2.5"
        fill="none"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ delay, duration: 0.6 }}
      />
      
      {/* Body */}
      <motion.line
        x1={x}
        y1={y - 28 * scale}
        x2={x + (pushing ? 8 : 0)}
        y2={y + 10 * scale}
        stroke={color}
        strokeWidth="2.5"
        strokeLinecap="round"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ delay: delay + 0.2, duration: 0.5 }}
      />
      
      {/* Arms - extended when pushing */}
      <motion.path
        d={pushing 
          ? `M ${x - 5} ${y - 15 * scale} L ${x + 25} ${y - 10 * scale}` // Extended arms
          : `M ${x - 10} ${y - 20 * scale} L ${x} ${y - 15 * scale} L ${x + 10} ${y - 20 * scale}` // Arms down
        }
        stroke={color}
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ delay: delay + 0.3, duration: 0.5 }}
      />
      
      {/* Legs */}
      <motion.path
        d={`M ${x} ${y + 10 * scale} L ${x - 12} ${y + 40 * scale} M ${x} ${y + 10 * scale} L ${x + 12} ${y + 40 * scale}`}
        stroke={color}
        strokeWidth="2.5"
        strokeLinecap="round"
        fill="none"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ delay: delay + 0.4, duration: 0.5 }}
      />
      
      {/* Muscles for large figure */}
      {size === 'large' && (
        <>
          {/* Bicep bump */}
          <motion.ellipse
            cx={x + 15}
            cy={y - 12 * scale}
            rx="5"
            ry="3"
            stroke={color}
            strokeWidth="1.5"
            fill="none"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: delay + 0.6, duration: 0.3 }}
          />
        </>
      )}
    </motion.g>
  );
};

// ============================================
// BLOCK COMPONENT
// ============================================
const Block = ({ 
  x, 
  y, 
  width = 50, 
  height = 40, 
  color = '#94a3b8',
  label = '',
  delay = 0,
  animate = false,
  velocity = 0 // pixels per second
}) => {
  const controls = useAnimationControls();
  
  useEffect(() => {
    if (animate && velocity > 0) {
      controls.start({
        x: x + velocity * 0.5,
        transition: {
          duration: 2,
          repeat: Infinity,
          repeatType: 'reverse',
          ease: 'linear'
        }
      });
    } else {
      controls.set({ x });
    }
  }, [animate, velocity, x, controls]);
  
  return (
    <motion.g
      initial={{ x }}
      animate={controls}
    >
      {/* Main block */}
      <motion.rect
        x={0}
        y={y}
        width={width}
        height={height}
        rx="4"
        stroke="#475569"
        strokeWidth="2.5"
        fill={color}
        style={{ filter: getSketchyFilter('light') }}
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ delay, duration: 0.6 }}
      />
      
      {/* Block label */}
      {label && (
        <motion.text
          x={width / 2}
          y={y + height / 2 + 4}
          textAnchor="middle"
          fill="#1e293b"
          fontSize="12"
          fontWeight="600"
          style={{ fontFamily: "'Patrick Hand', cursive" }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: delay + 0.4, duration: 0.3 }}
        >
          {label}
        </motion.text>
      )}
    </motion.g>
  );
};

// ============================================
// FORCE ARROW COMPONENT
// ============================================
const ForceArrow = ({
  x,
  y,
  length,
  thickness = 3,
  color = '#ef4444',
  label = '',
  delay = 0,
  pulse = false
}) => {
  const arrowHeadSize = Math.max(8, thickness * 2);
  
  return (
    <motion.g
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay, duration: 0.3 }}
    >
      {/* Arrow shaft */}
      <motion.line
        x1={x}
        y1={y}
        x2={x + length - arrowHeadSize}
        y2={y}
        stroke={color}
        strokeWidth={thickness}
        strokeLinecap="round"
        style={{ filter: getSketchyFilter('light') }}
        initial={{ pathLength: 0 }}
        animate={{ 
          pathLength: 1,
          strokeWidth: pulse ? [thickness, thickness * 1.3, thickness] : thickness
        }}
        transition={{ 
          pathLength: { delay, duration: 0.8 },
          strokeWidth: pulse ? { duration: 1, repeat: Infinity } : {}
        }}
      />
      
      {/* Arrow head */}
      <motion.polygon
        points={`
          ${x + length},${y}
          ${x + length - arrowHeadSize},${y - arrowHeadSize / 2}
          ${x + length - arrowHeadSize},${y + arrowHeadSize / 2}
        `}
        fill={color}
        initial={{ opacity: 0, scale: 0 }}
        animate={{ 
          opacity: 1, 
          scale: pulse ? [1, 1.1, 1] : 1 
        }}
        transition={{ 
          opacity: { delay: delay + 0.6, duration: 0.3 },
          scale: pulse ? { duration: 1, repeat: Infinity } : {}
        }}
      />
      
      {/* Arrow label */}
      {label && (
        <motion.text
          x={x + length / 2}
          y={y - 15}
          textAnchor="middle"
          fill={color}
          fontSize="14"
          fontWeight="600"
          style={{ fontFamily: "'Patrick Hand', cursive" }}
          initial={{ opacity: 0, y: y - 5 }}
          animate={{ opacity: 1, y: y - 15 }}
          transition={{ delay: delay + 0.8, duration: 0.3 }}
        >
          {label}
        </motion.text>
      )}
    </motion.g>
  );
};

// ============================================
// GROUND/SURFACE COMPONENT
// ============================================
const Ground = ({ y, width, delay = 0 }) => (
  <motion.g
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    transition={{ delay, duration: 0.3 }}
  >
    {/* Main ground line */}
    <motion.line
      x1={0}
      y1={y}
      x2={width}
      y2={y}
      stroke="#64748b"
      strokeWidth="2"
      strokeLinecap="round"
      initial={{ pathLength: 0 }}
      animate={{ pathLength: 1 }}
      transition={{ delay, duration: 0.8 }}
    />
    
    {/* Hatching lines for ground texture */}
    {[...Array(Math.floor(width / 15))].map((_, i) => (
      <motion.line
        key={i}
        x1={10 + i * 15}
        y1={y}
        x2={5 + i * 15}
        y2={y + 8}
        stroke="#94a3b8"
        strokeWidth="1.5"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ delay: delay + 0.5 + i * 0.03, duration: 0.2 }}
      />
    ))}
  </motion.g>
);

// ============================================
// SMALL FORCE PANEL CONTENT
// ============================================
const SmallForcePanel = ({ force, animate }) => {
  const arrowLength = 30 + force * 0.5; // Small, proportional arrow
  const velocity = force * 0.3; // Slow movement
  
  return (
    <DrawInSVG width={280} height={180}>
      {/* Ground */}
      <Ground y={150} width={280} delay={0} />
      
      {/* Stick figure - small */}
      <StickFigure 
        x={60} 
        y={110} 
        size="small" 
        pushing={true} 
        delay={0.2}
      />
      
      {/* Block */}
      <Block
        x={100}
        y={110}
        width={50}
        height={40}
        color="#dbeafe"
        label="1 kg"
        delay={0.4}
        animate={animate}
        velocity={velocity}
      />
      
      {/* Force arrow - thin and short */}
      <ForceArrow
        x={155}
        y={130}
        length={arrowLength}
        thickness={2}
        color="#3b82f6"
        label={`F = ${force}N`}
        delay={0.6}
        pulse={false}
      />
      
      {/* Acceleration label */}
      <AnimatedLabel x={140} y={170} delay={0.8} color="#64748b" fontSize={12}>
        a = {(force / 1).toFixed(1)} m/s²
      </AnimatedLabel>
    </DrawInSVG>
  );
};

// ============================================
// BIG FORCE PANEL CONTENT
// ============================================
const BigForcePanel = ({ force, animate }) => {
  const arrowLength = 30 + force * 2; // Much longer arrow
  const velocity = force * 1.5; // Fast movement
  
  return (
    <DrawInSVG width={280} height={180}>
      {/* Ground */}
      <Ground y={150} width={280} delay={0} />
      
      {/* Stick figure - large with muscles */}
      <StickFigure 
        x={50} 
        y={110} 
        size="large" 
        pushing={true} 
        delay={0.2}
      />
      
      {/* Block */}
      <Block
        x={100}
        y={110}
        width={50}
        height={40}
        color="#fed7aa"
        label="1 kg"
        delay={0.4}
        animate={animate}
        velocity={velocity}
      />
      
      {/* Force arrow - thick and long, pulsing */}
      <ForceArrow
        x={155}
        y={130}
        length={arrowLength}
        thickness={5}
        color="#f97316"
        label={`F = ${force * 5}N`}
        delay={0.6}
        pulse={true}
      />
      
      {/* Acceleration label */}
      <AnimatedLabel x={140} y={170} delay={0.8} color="#64748b" fontSize={12}>
        a = {((force * 5) / 1).toFixed(1)} m/s²
      </AnimatedLabel>
    </DrawInSVG>
  );
};

// ============================================
// MAIN FORCE COMPARISON TEMPLATE
// ============================================
const ForceComparisonTemplate = ({
  initialForce = 10,
  showControls = true,
  animate = true,
  className = ""
}) => {
  const [force, setForce] = useState(initialForce);
  const [isAnimating, setIsAnimating] = useState(animate);
  
  // Control slider
  const controls = showControls ? (
    <div className="flex flex-col md:flex-row items-center gap-4 md:gap-8">
      <SketchSlider
        label="🎚️ Force Level"
        value={force}
        onChange={setForce}
        min={5}
        max={50}
        unit=" N"
      />
      
      <button
        onClick={() => setIsAnimating(!isAnimating)}
        className={`
          px-6 py-2 rounded-xl font-medium transition-all
          ${isAnimating 
            ? 'bg-orange-500 text-white shadow-lg shadow-orange-500/30' 
            : 'bg-gray-200 text-gray-700'}
        `}
        style={{ fontFamily: "'Patrick Hand', cursive" }}
      >
        {isAnimating ? '⏸️ Pause' : '▶️ Play'}
      </button>
      
      {/* Formula reminder */}
      <div 
        className="hidden md:block px-4 py-2 bg-yellow-100 border border-yellow-300 rounded-lg"
        style={{ fontFamily: "'Patrick Hand', cursive" }}
      >
        <span className="text-yellow-800 font-medium">📐 F = m × a</span>
      </div>
    </div>
  ) : null;

  return (
    <SplitComparisonTemplate
      leftTitle="🐢 Small Push"
      leftSubtitle="Low Force"
      leftContent={<SmallForcePanel force={force} animate={isAnimating} />}
      leftColor="blue"
      rightTitle="💪 Big Push!"
      rightSubtitle="High Force"
      rightContent={<BigForcePanel force={force} animate={isAnimating} />}
      rightColor="orange"
      connectorType="vs"
      controls={controls}
      className={className}
    />
  );
};

export default ForceComparisonTemplate;


