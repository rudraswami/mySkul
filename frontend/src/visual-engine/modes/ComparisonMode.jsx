/**
 * ⚖️ COMPARISON MODE
 * ===================
 * 
 * Side-by-side comparison (X vs Y)
 * Best for: Comparing two concepts, pros/cons
 * 
 * Examples:
 * - AC vs DC current
 * - Plant cell vs Animal cell
 * - Covalent vs Ionic bonds
 */

import React from 'react';
import {
  SketchCircle,
  SketchRect,
  SketchLabel,
  SketchLine,
} from '../sketch/SketchPrimitives';

export const ComparisonMode = ({ blueprint, animationState = {} }) => {
  const { items = [], labels = [], comparisons = [] } = blueprint;
  
  // Split items into left and right
  const midpoint = 200;
  const leftItems = items.filter(item => item.position.x < midpoint);
  const rightItems = items.filter(item => item.position.x >= midpoint);
  
  return (
    <g id="comparison-mode">
      {/* Center divider line */}
      <SketchLine
        x1={midpoint}
        y1={30}
        x2={midpoint}
        y2={270}
        strokeWidth={2}
        delay={0}
      />
      
      {/* "VS" label */}
      <SketchLabel
        x={midpoint}
        y={15}
        text="VS"
        fontSize={20}
        bold={true}
        delay={0.2}
      />
      
      {/* Left side */}
      <g id="left-side">
        {leftItems.map((item, i) => (
          <ComparisonItem
            key={`left-${item.id}`}
            item={item}
            delay={0.5 + i * 0.3}
            side="left"
          />
        ))}
      </g>
      
      {/* Right side */}
      <g id="right-side">
        {rightItems.map((item, i) => (
          <ComparisonItem
            key={`right-${item.id}`}
            item={item}
            delay={0.5 + i * 0.3}
            side="right"
          />
        ))}
      </g>
      
      {/* Comparison labels */}
      {comparisons.map((comp, i) => (
        <ComparisonLabel
          key={`comp-${i}`}
          comparison={comp}
          delay={1.5 + i * 0.2}
        />
      ))}
      
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

// Helper: Comparison item
const ComparisonItem = ({ item, delay, side }) => {
  if (item.type === 'circle') {
    return (
      <SketchCircle
        cx={item.position.x}
        cy={item.position.y}
        radius={item.radius || 30}
        label={item.label}
        emoji={item.emoji}
        delay={delay}
      />
    );
  }
  
  if (item.type === 'rect') {
    return (
      <SketchRect
        x={item.position.x - (item.width || 40) / 2}
        y={item.position.y - (item.height || 40) / 2}
        width={item.width || 40}
        height={item.height || 40}
        label={item.label}
        delay={delay}
      />
    );
  }
  
  return null;
};

// Helper: Comparison label
const ComparisonLabel = ({ comparison, delay }) => {
  return (
    <g>
      <SketchLabel
        x={comparison.x || 200}
        y={comparison.y || 280}
        text={comparison.text}
        fontSize={14}
        color="#666"
        delay={delay}
      />
    </g>
  );
};

export default ComparisonMode;

