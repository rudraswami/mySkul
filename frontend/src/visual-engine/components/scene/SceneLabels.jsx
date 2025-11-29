/**
 * Scene Labels Component
 * Renders text labels, badges, and annotations
 */

import React from 'react';

const SceneLabels = ({ labels = [], onLabelClick }) => {
  return (
    <g id="labels-layer">
      {labels.filter(l => l.visible !== false && l.opacity > 0).map(label => (
        <LabelRenderer
          key={label.id}
          {...label}
          onClick={() => onLabelClick?.(label.id)}
        />
      ))}
    </g>
  );
};

const LabelRenderer = ({
  id,
  type = 'text',
  text,
  x = 50,
  y = 10,
  opacity = 1,
  style = 'default',
  fontSize = 3,
  onClick,
}) => {
  const transform = `translate(${x}, ${y})`;

  const styles = {
    default: {
      fill: '#333',
      bg: null,
      fontWeight: 'normal',
    },
    badge: {
      fill: '#FFF',
      bg: '#FF9800',
      fontWeight: 'bold',
    },
    badge_green: {
      fill: '#FFF',
      bg: '#4CAF50',
      fontWeight: 'bold',
    },
    badge_blue: {
      fill: '#FFF',
      bg: '#2196F3',
      fontWeight: 'bold',
    },
    formula: {
      fill: '#5D4037',
      bg: '#FFFDE7',
      fontWeight: 'bold',
      border: '#FFC107',
    },
    hinglish: {
      fill: '#E65100',
      bg: '#FFF3E0',
      fontWeight: 'bold',
      border: '#FF9800',
    },
    step: {
      fill: '#FFF',
      bg: '#673AB7',
      fontWeight: 'bold',
    },
  };

  const currentStyle = styles[style] || styles.default;
  const textWidth = text ? text.length * fontSize * 0.5 + 3 : 10;

  return (
    <g
      id={`label-${id}`}
      transform={transform}
      opacity={opacity}
      onClick={onClick}
      style={{ cursor: 'pointer' }}
    >
      {currentStyle.bg && (
        <>
          <rect
            x={-textWidth / 2}
            y={-fontSize}
            width={textWidth}
            height={fontSize * 2.5}
            rx={1}
            fill={currentStyle.bg}
            stroke={currentStyle.border || 'none'}
            strokeWidth={currentStyle.border ? 0.3 : 0}
          />
          {/* Notch/pointer */}
          {style === 'badge' && (
            <polygon
              points={`0,${fontSize * 1.5} -1,${fontSize * 2.5} 1,${fontSize * 2.5}`}
              fill={currentStyle.bg}
            />
          )}
        </>
      )}
      <text
        x="0"
        y={fontSize * 0.4}
        textAnchor="middle"
        fontSize={fontSize}
        fill={currentStyle.fill}
        fontWeight={currentStyle.fontWeight}
        fontFamily="Arial, sans-serif"
      >
        {text}
      </text>
    </g>
  );
};

export default SceneLabels;









