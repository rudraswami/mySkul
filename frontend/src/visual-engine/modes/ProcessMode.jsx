/**
 * 🔄 PROCESS MODE
 * ================
 * 
 * Step-by-step sequential flow
 * Best for: Processes, algorithms, procedures
 * 
 * Examples:
 * - Photosynthesis steps
 * - Algorithm execution
 * - Chemical reaction mechanism
 */

import React from 'react';
import {
  SketchCircle,
  SketchRect,
  SketchArrow,
  SketchLabel,
} from '../sketch/SketchPrimitives';

export const ProcessMode = ({ blueprint, animationState = {} }) => {
  const { items = [], arrows = [], labels = [], steps = [] } = blueprint;
  
  return (
    <g id="process-mode">
      {/* Steps */}
      {items.map((item, i) => (
        <ProcessStep
          key={item.id}
          item={item}
          stepNumber={i + 1}
          delay={i * 0.6}
        />
      ))}
      
      {/* Flow arrows */}
      {arrows.map((arrow, i) => {
        const fromItem = items.find(it => it.id === arrow.from);
        const toItem = items.find(it => it.id === arrow.to);
        
        if (!fromItem || !toItem) return null;
        
        return (
          <SketchArrow
            key={`arrow-${i}`}
            x1={fromItem.position.x + (fromItem.radius || 30)}
            y1={fromItem.position.y}
            x2={toItem.position.x - (toItem.radius || 30)}
            y2={toItem.position.y}
            label={arrow.label}
            style="flow"
            delay={i * 0.6 + 0.4}
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
    </g>
  );
};

// Helper: Process step
const ProcessStep = ({ item, stepNumber, delay }) => {
  return (
    <g>
      {/* Step number badge */}
      <SketchCircle
        cx={item.position.x - 40}
        cy={item.position.y - 30}
        radius={12}
        fill="#3B82F6"
        delay={delay}
      />
      <text
        x={item.position.x - 40}
        y={item.position.y - 26}
        textAnchor="middle"
        fill="#fff"
        fontSize="12"
        fontWeight="bold"
      >
        {stepNumber}
      </text>
      
      {/* Main item */}
      {item.type === 'circle' ? (
        <SketchCircle
          cx={item.position.x}
          cy={item.position.y}
          radius={item.radius || 30}
          label={item.label}
          emoji={item.emoji}
          delay={delay + 0.1}
        />
      ) : (
        <SketchRect
          x={item.position.x - (item.width || 50) / 2}
          y={item.position.y - (item.height || 40) / 2}
          width={item.width || 50}
          height={item.height || 40}
          label={item.label}
          delay={delay + 0.1}
        />
      )}
    </g>
  );
};

export default ProcessMode;

