/**
 * 🏗️ STRUCTURE MODE
 * ==================
 * 
 * Labeled diagrams and anatomical structures
 * Best for: Anatomy, molecular structure, system components
 * 
 * Examples:
 * - Heart structure
 * - Atom structure
 * - Cell organelles
 * - Plant anatomy
 */

import React from 'react';
import {
  SketchCircle,
  SketchRect,
  SketchLabel,
  SketchLine,
  SketchPath,
} from '../sketch/SketchPrimitives';

export const StructureMode = ({ blueprint, animationState = {} }) => {
  const { items = [], labels = [], callouts = [], structures = [] } = blueprint;
  
  return (
    <g id="structure-mode">
      {/* Main structure items */}
      {items.map((item, i) => (
        <StructureItem
          key={item.id}
          item={item}
          delay={i * 0.3}
        />
      ))}
      
      {/* Callout labels with leader lines */}
      {callouts.map((callout, i) => (
        <Callout
          key={`callout-${i}`}
          callout={callout}
          delay={items.length * 0.3 + i * 0.2}
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
          bold={label.bold}
          underline={label.underline}
          delay={i * 0.2}
        />
      ))}
    </g>
  );
};

// Helper: Structure item
const StructureItem = ({ item, delay }) => {
  const { position, type, radius, width, height, label, color, pattern } = item;
  
  if (type === 'circle') {
    return (
      <SketchCircle
        cx={position.x}
        cy={position.y}
        radius={radius || 30}
        fill={color || '#E3F2FD'}
        label={label}
        delay={delay}
      />
    );
  }
  
  if (type === 'rect') {
    return (
      <SketchRect
        x={position.x - (width || 40) / 2}
        y={position.y - (height || 40) / 2}
        width={width || 40}
        height={height || 40}
        fill={color || '#FFF9C4'}
        label={label}
        delay={delay}
      />
    );
  }
  
  if (type === 'ellipse') {
    return (
      <g>
        <ellipse
          cx={position.x}
          cy={position.y}
          rx={width || 40}
          ry={height || 25}
          fill={color || '#F3E5F5'}
          stroke="#333"
          strokeWidth="2"
          opacity="0.8"
        />
        {label && (
          <text
            x={position.x}
            y={position.y + 5}
            textAnchor="middle"
            fontSize="12"
            fill="#333"
          >
            {label}
          </text>
        )}
      </g>
    );
  }
  
  return null;
};

// Helper: Callout with leader line
const Callout = ({ callout, delay }) => {
  const { from, to, text, side = 'right' } = callout;
  
  return (
    <g>
      {/* Leader line */}
      <SketchLine
        x1={from.x}
        y1={from.y}
        x2={to.x}
        y2={to.y}
        strokeWidth={1.5}
        strokeDasharray="3,2"
        delay={delay}
      />
      
      {/* Label box */}
      <g>
        <rect
          x={to.x - (side === 'right' ? 0 : 80)}
          y={to.y - 15}
          width="80"
          height="25"
          fill="#FFF"
          stroke="#666"
          strokeWidth="1"
          rx="3"
        />
        <text
          x={to.x + (side === 'right' ? 40 : -40)}
          y={to.y + 2}
          textAnchor="middle"
          fontSize="11"
          fill="#333"
        >
          {text}
        </text>
      </g>
    </g>
  );
};

export default StructureMode;

