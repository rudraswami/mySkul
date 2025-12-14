/**
 * 🏀 RIGID BODY PRIMITIVE
 * =======================
 * 
 * A physics body with:
 * - Multiple shape variants (ball, block, car, rocket, etc.)
 * - Mass indication
 * - Velocity/motion indicators
 * - Hand-drawn aesthetic
 * - Animation support
 * 
 * This is NOT a circle. It's a physics-aware object.
 */

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';

// ============================================
// BODY SHAPES
// ============================================

const BODY_VARIANTS = {
  ball: {
    shape: 'circle',
    defaultSize: 50,
    fill: '#ECF0F1',
    stroke: '#2C3E50',
    aspectRatio: 1,
  },
  block: {
    shape: 'rectangle',
    defaultSize: 60,
    fill: '#D5DBDB',
    stroke: '#2C3E50',
    aspectRatio: 1.2,
  },
  box: {
    shape: 'rectangle_3d',
    defaultSize: 60,
    fill: '#F5B041',
    stroke: '#D68910',
    aspectRatio: 1,
  },
  car: {
    shape: 'car',
    defaultSize: 80,
    fill: '#3498DB',
    stroke: '#2C3E50',
    aspectRatio: 2,
  },
  truck: {
    shape: 'truck',
    defaultSize: 100,
    fill: '#E74C3C',
    stroke: '#922B21',
    aspectRatio: 2.5,
  },
  rocket: {
    shape: 'rocket',
    defaultSize: 80,
    fill: '#7F8C8D',
    stroke: '#2C3E50',
    aspectRatio: 0.3,
  },
  pendulum_bob: {
    shape: 'circle',
    defaultSize: 40,
    fill: '#8E44AD',
    stroke: '#6C3483',
    aspectRatio: 1,
  },
  planet: {
    shape: 'circle',
    defaultSize: 80,
    fill: '#5DADE2',
    stroke: '#2874A6',
    aspectRatio: 1,
  },
  person: {
    shape: 'stick_figure',
    defaultSize: 70,
    fill: '#2C3E50',
    stroke: '#2C3E50',
    aspectRatio: 0.4,
  },
  projectile: {
    shape: 'circle',
    defaultSize: 25,
    fill: '#E74C3C',
    stroke: '#922B21',
    aspectRatio: 1,
  },
  default: {
    shape: 'rectangle',
    defaultSize: 50,
    fill: '#ECF0F1',
    stroke: '#2C3E50',
    aspectRatio: 1,
  },
};

// ============================================
// SHAPE RENDERERS
// ============================================

const CircleShape = ({ size, fill, stroke, strokeWidth, sketchy }) => {
  const radius = size / 2;
  
  // Generate slightly imperfect circle for hand-drawn feel
  const wobblePoints = useMemo(() => {
    if (!sketchy) return null;
    
    const points = [];
    const segments = 24;
    for (let i = 0; i <= segments; i++) {
      const angle = (i / segments) * 2 * Math.PI;
      const wobble = 1 + (Math.random() - 0.5) * 0.03;
      points.push({
        x: radius + Math.cos(angle) * radius * wobble,
        y: radius + Math.sin(angle) * radius * wobble,
      });
    }
    return points;
  }, [radius, sketchy]);

  if (sketchy && wobblePoints) {
    const pathData = wobblePoints.reduce((acc, point, i) => {
      return acc + (i === 0 ? `M ${point.x} ${point.y}` : ` L ${point.x} ${point.y}`);
    }, '') + ' Z';
    
    return (
      <path
        d={pathData}
        fill={fill}
        stroke={stroke}
        strokeWidth={strokeWidth}
        filter="url(#pencil-texture)"
      />
    );
  }

  return (
    <circle
      cx={radius}
      cy={radius}
      r={radius}
      fill={fill}
      stroke={stroke}
      strokeWidth={strokeWidth}
    />
  );
};

const RectangleShape = ({ width, height, fill, stroke, strokeWidth, sketchy }) => {
  if (sketchy) {
    // Hand-drawn rectangle with slight wobble
    const w = 1 + (Math.random() - 0.5) * 0.02;
    const pathData = `
      M 2 2
      L ${width - 2 + w} 2
      L ${width - 2} ${height - 2 + w}
      L 2 ${height - 2}
      Z
    `;
    
    return (
      <path
        d={pathData}
        fill={fill}
        stroke={stroke}
        strokeWidth={strokeWidth}
        strokeLinejoin="round"
        filter="url(#pencil-texture)"
      />
    );
  }

  return (
    <rect
      x={2}
      y={2}
      width={width - 4}
      height={height - 4}
      rx={3}
      fill={fill}
      stroke={stroke}
      strokeWidth={strokeWidth}
    />
  );
};

const Rectangle3DShape = ({ width, height, fill, stroke, strokeWidth }) => {
  const depth = 15;
  
  return (
    <g>
      {/* Top face */}
      <polygon
        points={`
          ${depth},0
          ${width},0
          ${width - depth},${depth}
          0,${depth}
        `}
        fill={fill}
        stroke={stroke}
        strokeWidth={strokeWidth}
        opacity={0.8}
      />
      {/* Front face */}
      <rect
        x={0}
        y={depth}
        width={width - depth}
        height={height - depth}
        fill={fill}
        stroke={stroke}
        strokeWidth={strokeWidth}
      />
      {/* Right face */}
      <polygon
        points={`
          ${width - depth},${depth}
          ${width},0
          ${width},${height - depth}
          ${width - depth},${height}
        `}
        fill={fill}
        stroke={stroke}
        strokeWidth={strokeWidth}
        opacity={0.9}
      />
    </g>
  );
};

const CarShape = ({ width, height, fill, stroke, strokeWidth }) => {
  const wheelRadius = height * 0.25;
  const bodyHeight = height * 0.5;
  
  return (
    <g>
      {/* Car body */}
      <path
        d={`
          M ${wheelRadius * 1.5} ${height - wheelRadius}
          L ${wheelRadius} ${height - wheelRadius}
          L ${wheelRadius * 0.5} ${height - wheelRadius - bodyHeight * 0.3}
          L ${width * 0.2} ${height - wheelRadius - bodyHeight}
          L ${width * 0.35} ${height - wheelRadius - bodyHeight * 1.3}
          L ${width * 0.7} ${height - wheelRadius - bodyHeight * 1.3}
          L ${width * 0.85} ${height - wheelRadius - bodyHeight}
          L ${width - wheelRadius * 0.5} ${height - wheelRadius - bodyHeight * 0.3}
          L ${width - wheelRadius} ${height - wheelRadius}
          L ${width - wheelRadius * 1.5} ${height - wheelRadius}
        `}
        fill={fill}
        stroke={stroke}
        strokeWidth={strokeWidth}
        strokeLinejoin="round"
      />
      {/* Windows */}
      <path
        d={`
          M ${width * 0.25} ${height - wheelRadius - bodyHeight * 0.9}
          L ${width * 0.35} ${height - wheelRadius - bodyHeight * 1.15}
          L ${width * 0.5} ${height - wheelRadius - bodyHeight * 1.15}
          L ${width * 0.5} ${height - wheelRadius - bodyHeight * 0.9}
          Z
        `}
        fill="#AED6F1"
        stroke={stroke}
        strokeWidth={1}
      />
      <path
        d={`
          M ${width * 0.52} ${height - wheelRadius - bodyHeight * 0.9}
          L ${width * 0.52} ${height - wheelRadius - bodyHeight * 1.15}
          L ${width * 0.68} ${height - wheelRadius - bodyHeight * 1.15}
          L ${width * 0.75} ${height - wheelRadius - bodyHeight * 0.9}
          Z
        `}
        fill="#AED6F1"
        stroke={stroke}
        strokeWidth={1}
      />
      {/* Wheels */}
      <circle
        cx={wheelRadius * 2}
        cy={height - wheelRadius}
        r={wheelRadius}
        fill="#2C3E50"
        stroke={stroke}
        strokeWidth={2}
      />
      <circle
        cx={wheelRadius * 2}
        cy={height - wheelRadius}
        r={wheelRadius * 0.5}
        fill="#7F8C8D"
      />
      <circle
        cx={width - wheelRadius * 2}
        cy={height - wheelRadius}
        r={wheelRadius}
        fill="#2C3E50"
        stroke={stroke}
        strokeWidth={2}
      />
      <circle
        cx={width - wheelRadius * 2}
        cy={height - wheelRadius}
        r={wheelRadius * 0.5}
        fill="#7F8C8D"
      />
    </g>
  );
};

const RocketShape = ({ width, height, fill, stroke, strokeWidth }) => {
  const noseHeight = height * 0.2;
  const bodyHeight = height * 0.55;
  const finHeight = height * 0.25;
  
  return (
    <g transform={`translate(${width / 2}, 0)`}>
      {/* Nose cone */}
      <path
        d={`
          M 0 0
          L ${width * 0.3} ${noseHeight}
          L ${-width * 0.3} ${noseHeight}
          Z
        `}
        fill="#E74C3C"
        stroke={stroke}
        strokeWidth={strokeWidth}
      />
      {/* Body */}
      <rect
        x={-width * 0.3}
        y={noseHeight}
        width={width * 0.6}
        height={bodyHeight}
        fill={fill}
        stroke={stroke}
        strokeWidth={strokeWidth}
      />
      {/* Window */}
      <circle
        cx={0}
        cy={noseHeight + bodyHeight * 0.35}
        r={width * 0.12}
        fill="#AED6F1"
        stroke={stroke}
        strokeWidth={1}
      />
      {/* Fins */}
      <path
        d={`
          M ${-width * 0.3} ${noseHeight + bodyHeight}
          L ${-width * 0.5} ${height}
          L ${-width * 0.3} ${height - finHeight * 0.3}
          Z
        `}
        fill="#E74C3C"
        stroke={stroke}
        strokeWidth={strokeWidth}
      />
      <path
        d={`
          M ${width * 0.3} ${noseHeight + bodyHeight}
          L ${width * 0.5} ${height}
          L ${width * 0.3} ${height - finHeight * 0.3}
          Z
        `}
        fill="#E74C3C"
        stroke={stroke}
        strokeWidth={strokeWidth}
      />
      {/* Engine */}
      <rect
        x={-width * 0.15}
        y={noseHeight + bodyHeight}
        width={width * 0.3}
        height={finHeight * 0.5}
        fill="#5D6D7E"
        stroke={stroke}
        strokeWidth={1}
      />
    </g>
  );
};

const StickFigure = ({ size, stroke }) => {
  const headRadius = size * 0.12;
  const bodyLength = size * 0.35;
  const armLength = size * 0.25;
  const legLength = size * 0.35;
  const centerX = size * 0.5;
  
  return (
    <g>
      {/* Head */}
      <circle
        cx={centerX}
        cy={headRadius}
        r={headRadius}
        fill="none"
        stroke={stroke}
        strokeWidth={2}
      />
      {/* Body */}
      <line
        x1={centerX}
        y1={headRadius * 2}
        x2={centerX}
        y2={headRadius * 2 + bodyLength}
        stroke={stroke}
        strokeWidth={2}
        strokeLinecap="round"
      />
      {/* Arms */}
      <line
        x1={centerX - armLength}
        y1={headRadius * 2 + bodyLength * 0.3}
        x2={centerX + armLength}
        y2={headRadius * 2 + bodyLength * 0.3}
        stroke={stroke}
        strokeWidth={2}
        strokeLinecap="round"
      />
      {/* Legs */}
      <line
        x1={centerX}
        y1={headRadius * 2 + bodyLength}
        x2={centerX - armLength * 0.8}
        y2={headRadius * 2 + bodyLength + legLength}
        stroke={stroke}
        strokeWidth={2}
        strokeLinecap="round"
      />
      <line
        x1={centerX}
        y1={headRadius * 2 + bodyLength}
        x2={centerX + armLength * 0.8}
        y2={headRadius * 2 + bodyLength + legLength}
        stroke={stroke}
        strokeWidth={2}
        strokeLinecap="round"
      />
    </g>
  );
};

// ============================================
// RIGID BODY COMPONENT
// ============================================

const RigidBody = ({
  // Position
  x = 0,
  y = 0,
  
  // Size
  size = null,
  width = null,
  height = null,
  
  // Variant
  variant = 'default',
  
  // Physics properties
  mass = null,
  showMass = false,
  
  // Motion indicator
  showVelocity = false,
  velocityAngle = 0,
  velocityMagnitude = 40,
  
  // Style
  fill = null,
  stroke = null,
  strokeWidth = 2.5,
  
  // Label
  label = null,
  showLabel = true,
  
  // Animation
  animated = true,
  delay = 0,
  
  // Hand-drawn style
  sketchy = true,
  
  // Interactivity
  draggable = false,
  onDrag = null,
  onClick = null,
  
  ...props
}) => {
  // Get variant configuration
  const config = BODY_VARIANTS[variant] || BODY_VARIANTS.default;
  
  // Calculate dimensions
  const bodySize = size || config.defaultSize;
  const bodyWidth = width || bodySize * config.aspectRatio;
  const bodyHeight = height || bodySize;
  
  // Final styles
  const finalFill = fill || config.fill;
  const finalStroke = stroke || config.stroke;

  // Render the appropriate shape
  const renderShape = () => {
    switch (config.shape) {
      case 'circle':
        return (
          <CircleShape
            size={bodyWidth}
            fill={finalFill}
            stroke={finalStroke}
            strokeWidth={strokeWidth}
            sketchy={sketchy}
          />
        );
      case 'rectangle':
        return (
          <RectangleShape
            width={bodyWidth}
            height={bodyHeight}
            fill={finalFill}
            stroke={finalStroke}
            strokeWidth={strokeWidth}
            sketchy={sketchy}
          />
        );
      case 'rectangle_3d':
        return (
          <Rectangle3DShape
            width={bodyWidth}
            height={bodyHeight}
            fill={finalFill}
            stroke={finalStroke}
            strokeWidth={strokeWidth}
          />
        );
      case 'car':
        return (
          <CarShape
            width={bodyWidth}
            height={bodyHeight}
            fill={finalFill}
            stroke={finalStroke}
            strokeWidth={strokeWidth}
          />
        );
      case 'rocket':
        return (
          <RocketShape
            width={bodyWidth}
            height={bodyHeight}
            fill={finalFill}
            stroke={finalStroke}
            strokeWidth={strokeWidth}
          />
        );
      case 'stick_figure':
        return (
          <StickFigure
            size={bodyHeight}
            stroke={finalStroke}
          />
        );
      default:
        return (
          <RectangleShape
            width={bodyWidth}
            height={bodyHeight}
            fill={finalFill}
            stroke={finalStroke}
            strokeWidth={strokeWidth}
            sketchy={sketchy}
          />
        );
    }
  };

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.4,
        delay,
        ease: 'easeOut',
      },
    },
  };

  return (
    <motion.g
      className="rigid-body"
      data-variant={variant}
      transform={`translate(${x}, ${y})`}
      initial={animated ? 'hidden' : 'visible'}
      animate="visible"
      variants={containerVariants}
      onClick={onClick}
      style={{ cursor: onClick || draggable ? 'pointer' : 'default' }}
      {...props}
    >
      {/* Main shape */}
      {renderShape()}
      
      {/* Mass label */}
      {showMass && mass && (
        <text
          x={bodyWidth / 2}
          y={bodyHeight / 2}
          textAnchor="middle"
          dominantBaseline="middle"
          fill={finalStroke}
          fontSize={14}
          fontWeight="600"
          fontFamily="'Kalam', cursive"
        >
          m = {mass}
        </text>
      )}
      
      {/* Label below object */}
      {showLabel && label && (
        <text
          x={bodyWidth / 2}
          y={bodyHeight + 18}
          textAnchor="middle"
          fill="#2C3E50"
          fontSize={13}
          fontFamily="'Kalam', cursive"
        >
          {label}
        </text>
      )}
      
      {/* Velocity indicator */}
      {showVelocity && (
        <g transform={`translate(${bodyWidth / 2}, ${bodyHeight / 2})`}>
          <line
            x1={0}
            y1={0}
            x2={Math.cos((velocityAngle * Math.PI) / 180) * velocityMagnitude}
            y2={Math.sin((velocityAngle * Math.PI) / 180) * velocityMagnitude}
            stroke="#3498DB"
            strokeWidth={2}
            markerEnd="url(#velocity-arrow)"
          />
        </g>
      )}
    </motion.g>
  );
};

export default RigidBody;



