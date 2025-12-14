/**
 * ⚡ FORCE VECTOR PRIMITIVE
 * =========================
 * 
 * A physics-accurate force vector with:
 * - Directional arrow with proper head
 * - Magnitude representation (length or label)
 * - Origin point indicator
 * - Hand-drawn aesthetic
 * - Animation support
 * 
 * This is NOT a simple arrow. It's a physics-aware component.
 */

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';

// ============================================
// FORCE TYPES & STYLES
// ============================================

const FORCE_STYLES = {
  gravitational: {
    color: '#2C3E50',
    label: 'W = mg',
    defaultDirection: 'down',
    strokeWidth: 3,
  },
  normal: {
    color: '#3498DB',
    label: 'N',
    defaultDirection: 'up',
    strokeWidth: 3,
  },
  friction: {
    color: '#E67E22',
    label: 'f',
    defaultDirection: 'opposite',
    strokeWidth: 2.5,
  },
  tension: {
    color: '#9B59B6',
    label: 'T',
    defaultDirection: 'along_rope',
    strokeWidth: 3,
  },
  applied: {
    color: '#E74C3C',
    label: 'F',
    defaultDirection: 'specified',
    strokeWidth: 3,
  },
  spring: {
    color: '#27AE60',
    label: 'F = -kx',
    defaultDirection: 'toward_equilibrium',
    strokeWidth: 2.5,
  },
  centripetal: {
    color: '#1ABC9C',
    label: 'Fc',
    defaultDirection: 'toward_center',
    strokeWidth: 3,
  },
  buoyancy: {
    color: '#3498DB',
    label: 'Fb',
    defaultDirection: 'up',
    strokeWidth: 3,
  },
  default: {
    color: '#E74C3C',
    label: 'F',
    defaultDirection: 'right',
    strokeWidth: 3,
  },
};

// ============================================
// ARROW HEAD SHAPES
// ============================================

const ArrowHead = ({ x, y, angle, size = 12, color }) => {
  // Create arrow head path
  const rad = (angle * Math.PI) / 180;
  const tipX = x;
  const tipY = y;
  
  // Two points for the arrow wings
  const wing1X = tipX - size * Math.cos(rad - Math.PI / 6);
  const wing1Y = tipY - size * Math.sin(rad - Math.PI / 6);
  const wing2X = tipX - size * Math.cos(rad + Math.PI / 6);
  const wing2Y = tipY - size * Math.sin(rad + Math.PI / 6);
  
  return (
    <polygon
      points={`${tipX},${tipY} ${wing1X},${wing1Y} ${wing2X},${wing2Y}`}
      fill={color}
    />
  );
};

// ============================================
// FORCE VECTOR COMPONENT
// ============================================

const ForceVector = ({
  // Position
  x = 0,
  y = 0,
  
  // Vector properties
  angle = 0,              // Degrees, 0 = right, 90 = down
  magnitude = 80,         // Length in pixels (or calculated from value)
  
  // Force type
  variant = 'default',    // gravitational, normal, friction, etc.
  
  // Display
  label = null,           // Custom label (overrides variant default)
  showLabel = true,
  showMagnitudeValue = false,
  magnitudeValue = null,  // e.g., "10 N"
  
  // Style
  color = null,           // Override color
  strokeWidth = null,     // Override stroke width
  dashed = false,
  
  // Animation
  animated = true,
  delay = 0,
  
  // Hand-drawn style
  sketchy = true,
  
  // Interactivity
  onClick = null,
  onHover = null,
  
  ...props
}) => {
  // Get style from variant
  const style = FORCE_STYLES[variant] || FORCE_STYLES.default;
  const finalColor = color || style.color;
  const finalStrokeWidth = strokeWidth || style.strokeWidth;
  const displayLabel = label || style.label;

  // Calculate end point
  const endPoint = useMemo(() => {
    const rad = (angle * Math.PI) / 180;
    return {
      x: x + Math.cos(rad) * magnitude,
      y: y + Math.sin(rad) * magnitude,
    };
  }, [x, y, angle, magnitude]);

  // Generate slightly wobbly path for hand-drawn effect
  const pathData = useMemo(() => {
    if (!sketchy) {
      return `M ${x} ${y} L ${endPoint.x} ${endPoint.y}`;
    }
    
    // Add slight wobble for hand-drawn feel
    const midX = (x + endPoint.x) / 2;
    const midY = (y + endPoint.y) / 2;
    const wobble = 1.5;
    const offsetX = (Math.random() - 0.5) * wobble;
    const offsetY = (Math.random() - 0.5) * wobble;
    
    return `M ${x} ${y} Q ${midX + offsetX} ${midY + offsetY} ${endPoint.x} ${endPoint.y}`;
  }, [x, y, endPoint, sketchy]);

  // Label position (offset from midpoint, perpendicular to arrow)
  const labelPosition = useMemo(() => {
    const midX = (x + endPoint.x) / 2;
    const midY = (y + endPoint.y) / 2;
    const perpAngle = angle + 90;
    const rad = (perpAngle * Math.PI) / 180;
    const offset = 20;
    
    return {
      x: midX + Math.cos(rad) * offset,
      y: midY + Math.sin(rad) * offset,
    };
  }, [x, y, endPoint, angle]);

  // Animation variants
  const drawVariants = {
    hidden: {
      pathLength: 0,
      opacity: 0,
    },
    visible: {
      pathLength: 1,
      opacity: 1,
      transition: {
        pathLength: { duration: 0.6, ease: 'easeInOut', delay },
        opacity: { duration: 0.2, delay },
      },
    },
  };

  const fadeInVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: { duration: 0.3, delay: delay + 0.4 },
    },
  };

  return (
    <g
      className="force-vector"
      data-variant={variant}
      onClick={onClick}
      onMouseEnter={onHover}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
      {...props}
    >
      {/* Origin point indicator */}
      <circle
        cx={x}
        cy={y}
        r={4}
        fill={finalColor}
        opacity={0.6}
      />

      {/* Arrow shaft */}
      <motion.path
        d={pathData}
        fill="none"
        stroke={finalColor}
        strokeWidth={finalStrokeWidth}
        strokeLinecap="round"
        strokeDasharray={dashed ? '8 4' : 'none'}
        initial={animated ? 'hidden' : 'visible'}
        animate="visible"
        variants={drawVariants}
        filter="url(#pencil-texture)"
      />

      {/* Arrow head */}
      <motion.g
        initial={animated ? { opacity: 0, scale: 0 } : { opacity: 1, scale: 1 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.2, delay: delay + 0.5 }}
      >
        <ArrowHead
          x={endPoint.x}
          y={endPoint.y}
          angle={angle}
          size={finalStrokeWidth * 4}
          color={finalColor}
        />
      </motion.g>

      {/* Force label */}
      {showLabel && displayLabel && (
        <motion.text
          x={labelPosition.x}
          y={labelPosition.y}
          textAnchor="middle"
          dominantBaseline="middle"
          fill={finalColor}
          fontSize={14}
          fontWeight="600"
          fontFamily="'Kalam', 'Comic Sans MS', cursive"
          initial={animated ? 'hidden' : 'visible'}
          animate="visible"
          variants={fadeInVariants}
        >
          {displayLabel}
        </motion.text>
      )}

      {/* Magnitude value (optional) */}
      {showMagnitudeValue && magnitudeValue && (
        <motion.text
          x={labelPosition.x}
          y={labelPosition.y + 16}
          textAnchor="middle"
          dominantBaseline="middle"
          fill="#7F8C8D"
          fontSize={11}
          fontFamily="'Kalam', 'Comic Sans MS', cursive"
          initial={animated ? 'hidden' : 'visible'}
          animate="visible"
          variants={fadeInVariants}
        >
          {magnitudeValue}
        </motion.text>
      )}
    </g>
  );
};

// ============================================
// PAIRED FORCE VECTORS (Newton's 3rd Law)
// ============================================

export const ActionReactionPair = ({
  x,
  y,
  magnitude = 80,
  actionAngle = 0,
  actionLabel = 'F₁',
  reactionLabel = 'F₂',
  color = '#E74C3C',
  animated = true,
  delay = 0,
}) => {
  const reactionAngle = actionAngle + 180;

  return (
    <g className="action-reaction-pair">
      {/* Action force */}
      <ForceVector
        x={x}
        y={y}
        angle={actionAngle}
        magnitude={magnitude}
        label={actionLabel}
        color={color}
        animated={animated}
        delay={delay}
      />
      
      {/* Reaction force (equal and opposite) */}
      <ForceVector
        x={x}
        y={y}
        angle={reactionAngle}
        magnitude={magnitude}
        label={reactionLabel}
        color={color}
        animated={animated}
        delay={delay + 0.3}
      />
      
      {/* Equal sign indicator */}
      <motion.text
        x={x}
        y={y - magnitude / 2 - 10}
        textAnchor="middle"
        fill="#7F8C8D"
        fontSize={12}
        fontFamily="'Kalam', cursive"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: delay + 0.8 }}
      >
        |F₁| = |F₂|
      </motion.text>
    </g>
  );
};

// ============================================
// FORCE SYSTEM (Multiple forces on one body)
// ============================================

export const ForceSystem = ({
  x,
  y,
  forces = [],     // Array of { angle, magnitude, variant, label }
  showResultant = false,
  animated = true,
  delay = 0,
}) => {
  // Calculate resultant force
  const resultant = useMemo(() => {
    let sumX = 0;
    let sumY = 0;
    
    forces.forEach(f => {
      const rad = (f.angle * Math.PI) / 180;
      sumX += Math.cos(rad) * f.magnitude;
      sumY += Math.sin(rad) * f.magnitude;
    });
    
    const magnitude = Math.sqrt(sumX * sumX + sumY * sumY);
    const angle = (Math.atan2(sumY, sumX) * 180) / Math.PI;
    
    return { magnitude, angle };
  }, [forces]);

  return (
    <g className="force-system">
      {/* Individual forces */}
      {forces.map((force, index) => (
        <ForceVector
          key={`force-${index}`}
          x={x}
          y={y}
          angle={force.angle}
          magnitude={force.magnitude}
          variant={force.variant}
          label={force.label}
          animated={animated}
          delay={delay + index * 0.2}
        />
      ))}
      
      {/* Resultant force */}
      {showResultant && resultant.magnitude > 0.1 && (
        <ForceVector
          x={x}
          y={y}
          angle={resultant.angle}
          magnitude={resultant.magnitude}
          label="ΣF"
          color="#1ABC9C"
          strokeWidth={4}
          dashed={true}
          animated={animated}
          delay={delay + forces.length * 0.2 + 0.3}
        />
      )}
    </g>
  );
};

export default ForceVector;



