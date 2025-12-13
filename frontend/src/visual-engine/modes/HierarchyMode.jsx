/**
 * 🌳 HIERARCHY MODE
 * ==================
 * 
 * Tree structures and hierarchical relationships
 * Best for: Taxonomies, org charts, classification
 * 
 * Examples:
 * - Biological classification
 * - Number system hierarchy
 * - Organization chart
 * - File system tree
 */

import React from 'react';
import {
  SketchCircle,
  SketchRect,
  SketchLine,
  SketchLabel,
} from '../sketch/SketchPrimitives';

export const HierarchyMode = ({ blueprint, animationState = {} }) => {
  const { items = [], connections = [], labels = [], root } = blueprint;
  
  return (
    <g id="hierarchy-mode">
      {/* Connections (draw first, before nodes) */}
      {connections.map((conn, i) => {
        const fromItem = items.find(it => it.id === conn.from);
        const toItem = items.find(it => it.id === conn.to);
        
        if (!fromItem || !toItem) return null;
        
        return (
          <SketchLine
            key={`conn-${i}`}
            x1={fromItem.position.x}
            y1={fromItem.position.y + (fromItem.radius || 20)}
            x2={toItem.position.x}
            y2={toItem.position.y - (toItem.radius || 20)}
            strokeWidth={2}
            delay={i * 0.1}
          />
        );
      })}
      
      {/* Nodes */}
      {items.map((item, i) => (
        <HierarchyNode
          key={item.id}
          item={item}
          isRoot={item.id === root}
          delay={0.5 + i * 0.2}
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

// Hierarchy node
const HierarchyNode = ({ item, isRoot, delay }) => {
  const { position, label, level = 0, color, emoji } = item;
  
  // Size based on level (root is larger)
  const radius = isRoot ? 35 : (level === 1 ? 28 : 22);
  const fontSize = isRoot ? 14 : (level === 1 ? 12 : 10);
  
  // Color based on level
  const nodeColor = color || (
    isRoot ? '#3B82F6' : 
    level === 1 ? '#10B981' : 
    level === 2 ? '#F59E0B' : 
    '#6B7280'
  );
  
  return (
    <g>
      {/* Node circle */}
      <SketchCircle
        cx={position.x}
        cy={position.y}
        radius={radius}
        fill={nodeColor}
        opacity={0.2}
        strokeWidth={isRoot ? 3 : 2}
        delay={delay}
      />
      
      {/* Emoji (if provided) */}
      {emoji && (
        <text
          x={position.x}
          y={position.y - 5}
          textAnchor="middle"
          fontSize={fontSize + 4}
        >
          {emoji}
        </text>
      )}
      
      {/* Label */}
      <text
        x={position.x}
        y={position.y + (emoji ? radius + 15 : 5)}
        textAnchor="middle"
        fontSize={fontSize}
        fontWeight={isRoot ? 'bold' : 'normal'}
        fill="#333"
      >
        {label}
      </text>
      
      {/* Level indicator (optional) */}
      {!isRoot && (
        <circle
          cx={position.x + radius - 5}
          cy={position.y - radius + 5}
          r="8"
          fill="#FFF"
          stroke={nodeColor}
          strokeWidth="1.5"
        />
      )}
      {!isRoot && (
        <text
          x={position.x + radius - 5}
          y={position.y - radius + 9}
          textAnchor="middle"
          fontSize="9"
          fontWeight="bold"
          fill={nodeColor}
        >
          {level}
        </text>
      )}
    </g>
  );
};

export default HierarchyMode;

