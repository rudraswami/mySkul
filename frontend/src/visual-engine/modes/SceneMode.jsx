/**
 * 🎬 SCENE MODE
 * ==============
 * 
 * Physical scenarios, forces, motion
 * Best for: Physics concepts, cause-effect relationships
 * 
 * Examples:
 * - Ball rolling down ramp
 * - Force diagrams
 * - Cricket ball trajectory
 */

import React from 'react';
import {
  SketchCircle,
  SketchRect,
  SketchArrow,
  SketchLabel,
  SketchStickFigure,
} from '../sketch/SketchPrimitives';

export const SceneMode = ({ blueprint, animationState = {} }) => {
  const { items = [], arrows = [], figures = [], labels = [] } = blueprint;
  
  return (
    <g id="scene-mode">
      {/* Background elements */}
      {blueprint.background?.elements?.map((elem, i) => (
        <BackgroundElement key={i} element={elem} />
      ))}
      
      {/* Figures (stick people) */}
      {figures.map((figure, i) => (
        <SketchStickFigure
          key={`figure-${i}`}
          x={figure.x}
          y={figure.y}
          pose={figure.pose || 'idle'}
          expression={figure.expression || 'neutral'}
          delay={i * 0.3}
        />
      ))}
      
      {/* Main items (circles, rects) */}
      {items.map((item, i) => {
        const itemState = animationState.items?.[item.id] || {};
        const shouldDraw = itemState.visible !== false;
        
        if (!shouldDraw) return null;
        
        if (item.type === 'circle') {
          return (
            <SketchCircle
              key={item.id}
              cx={item.position.x}
              cy={item.position.y}
              radius={item.radius || 30}
              label={item.metaphorLabel || item.label}
              emoji={item.metaphorEmoji}
              delay={i * 0.4}
            />
          );
        }
        
        if (item.type === 'rect') {
          return (
            <SketchRect
              key={item.id}
              x={item.position.x - (item.width || 40) / 2}
              y={item.position.y - (item.height || 40) / 2}
              width={item.width || 40}
              height={item.height || 40}
              label={item.metaphorLabel || item.label}
              delay={i * 0.4}
            />
          );
        }
        
        return null;
      })}
      
      {/* Arrows (connections, forces) */}
      {arrows.map((arrow, i) => {
        const fromItem = items.find(it => it.id === arrow.from);
        const toItem = items.find(it => it.id === arrow.to);
        
        if (!fromItem || !toItem) return null;
        
        return (
          <SketchArrow
            key={`arrow-${i}`}
            x1={fromItem.position.x}
            y1={fromItem.position.y}
            x2={toItem.position.x}
            y2={toItem.position.y}
            label={arrow.label}
            style={arrow.style || 'default'}
            curved={arrow.curved}
            delay={items.length * 0.4 + i * 0.3}
          />
        );
      })}
      
      {/* Labels */}
      {labels.map((label, i) => (
        <SketchLabel
          key={`label-${i}`}
          x={label.x}
          y={label.y}
          text={label.text}
          fontSize={label.fontSize}
          underline={label.underline}
          delay={i * 0.2}
        />
      ))}
    </g>
  );
};

// Helper: Background elements
const BackgroundElement = ({ element }) => {
  if (element === 'grass_field') {
    return (
      <rect
        x="0"
        y="250"
        width="400"
        height="50"
        fill="#90EE90"
        opacity="0.3"
      />
    );
  }
  
  if (element === 'road') {
    return (
      <g>
        <rect x="0" y="200" width="400" height="100" fill="#666" opacity="0.2" />
        <line x1="0" y1="250" x2="400" y2="250" stroke="#fff" strokeWidth="2" strokeDasharray="10,5" opacity="0.5" />
      </g>
    );
  }
  
  return null;
};

export default SceneMode;

