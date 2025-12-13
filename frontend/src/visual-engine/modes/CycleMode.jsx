/**
 * ♻️ CYCLE MODE
 * ==============
 * 
 * Circular loops and repeating processes
 * Best for: Cycles, feedback loops, circular processes
 * 
 * Examples:
 * - Water cycle
 * - Krebs cycle
 * - Carbon cycle
 * - Feedback loops
 */

import React from 'react';
import {
  SketchCircle,
  SketchArrow,
  SketchLabel,
  SketchPath,
} from '../sketch/SketchPrimitives';

export const CycleMode = ({ blueprint, animationState = {} }) => {
  const { items = [], arrows = [], labels = [], centerLabel } = blueprint;
  
  // Calculate center
  const centerX = blueprint.centerX || 200;
  const centerY = blueprint.centerY || 150;
  
  return (
    <g id="cycle-mode">
      {/* Center label (optional) */}
      {centerLabel && (
        <SketchLabel
          x={centerX}
          y={centerY}
          text={centerLabel}
          fontSize={18}
          bold={true}
          delay={0}
        />
      )}
      
      {/* Circular items */}
      {items.map((item, i) => (
        <SketchCircle
          key={item.id}
          cx={item.position.x}
          cy={item.position.y}
          radius={item.radius || 25}
          label={item.label}
          emoji={item.emoji}
          delay={i * 0.4}
        />
      ))}
      
      {/* Curved arrows forming cycle */}
      {arrows.map((arrow, i) => {
        const fromItem = items.find(it => it.id === arrow.from);
        const toItem = items.find(it => it.id === arrow.to);
        
        if (!fromItem || !toItem) return null;
        
        return (
          <CurvedArrow
            key={`arrow-${i}`}
            from={fromItem.position}
            to={toItem.position}
            centerX={centerX}
            centerY={centerY}
            label={arrow.label}
            delay={items.length * 0.4 + i * 0.3}
          />
        );
      })}
      
      {/* Additional labels */}
      {labels.map((label, i) => (
        <SketchLabel
          key={`label-${i}`}
          x={label.x}
          y={label.y}
          text={label.text}
          fontSize={label.fontSize}
          delay={i * 0.2}
        />
      ))}
      
      {/* Cycle direction indicator */}
      <CycleDirectionIndicator
        centerX={centerX}
        centerY={centerY}
        delay={2}
      />
    </g>
  );
};

// Helper: Curved arrow
const CurvedArrow = ({ from, to, centerX, centerY, label, delay }) => {
  // Create curved path going around center
  const midX = (from.x + to.x) / 2;
  const midY = (from.y + to.y) / 2;
  
  // Control point pushed toward/away from center
  const dx = midX - centerX;
  const dy = midY - centerY;
  const dist = Math.sqrt(dx * dx + dy * dy);
  
  // Push control point outward
  const controlX = midX + (dx / dist) * 20;
  const controlY = midY + (dy / dist) * 20;
  
  const path = `M ${from.x} ${from.y} Q ${controlX} ${controlY} ${to.x} ${to.y}`;
  
  return (
    <g>
      <SketchPath
        d={path}
        stroke="#3B82F6"
        strokeWidth={2}
        fill="none"
        arrowEnd={true}
        delay={delay}
      />
      {label && (
        <text
          x={controlX}
          y={controlY - 5}
          textAnchor="middle"
          fill="#666"
          fontSize="12"
        >
          {label}
        </text>
      )}
    </g>
  );
};

// Helper: Cycle direction indicator
const CycleDirectionIndicator = ({ centerX, centerY, delay }) => {
  return (
    <g opacity="0.4">
      <circle
        cx={centerX}
        cy={centerY}
        r="80"
        fill="none"
        stroke="#999"
        strokeWidth="1"
        strokeDasharray="5,5"
      />
      <text
        x={centerX + 60}
        y={centerY - 60}
        fill="#999"
        fontSize="20"
      >
        ↻
      </text>
    </g>
  );
};

export default CycleMode;

