/**
 * Scene Props Component
 * Renders interactive objects with persistent state
 */

import React from 'react';

const SceneProps = ({ props = [], highlightedId, onPropClick }) => {
  return (
    <g id="props-layer">
      {props.filter(p => p.visible !== false).map(prop => (
        <PropRenderer
          key={prop.id}
          {...prop}
          isHighlighted={highlightedId === prop.id}
          onClick={() => onPropClick?.(prop.id)}
        />
      ))}
    </g>
  );
};

const PropRenderer = ({ 
  id, 
  propType, 
  x = 50, 
  y = 50, 
  scale = 1, 
  rotation = 0, 
  opacity = 1,
  isHighlighted,
  onClick,
  ...rest 
}) => {
  const transform = `translate(${x}, ${y}) rotate(${rotation}) scale(${scale})`;
  
  const PropComponent = propComponents[propType] || propComponents.box;

  return (
    <g
      id={`prop-${id}`}
      transform={transform}
      opacity={opacity}
      onClick={onClick}
      style={{ cursor: 'pointer' }}
    >
      {/* Highlight glow */}
      {isHighlighted && (
        <circle cx="0" cy="0" r="8" fill="none" stroke="#FF9800" strokeWidth="0.5" opacity="0.8">
          <animate attributeName="r" values="6;10;6" dur="1s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.8;0.3;0.8" dur="1s" repeatCount="indefinite" />
        </circle>
      )}
      <PropComponent {...rest} />
    </g>
  );
};

/**
 * Prop Components Library
 */
const propComponents = {
  // Cricket ball
  cricket_ball: () => (
    <g>
      <circle cx="0" cy="0" r="2.5" fill="#D32F2F" stroke="#8B0000" strokeWidth="0.3" />
      <path d="M -1.5 -1.5 Q 0 0 1.5 1.5" stroke="#FFF" strokeWidth="0.3" fill="none" />
    </g>
  ),

  // Bat
  bat: () => (
    <g>
      <rect x="-1" y="-12" width="2" height="6" fill="#4E342E" rx="0.5" />
      <rect x="-2.5" y="-6" width="5" height="14" fill="#D7CCC8" rx="0.5" />
    </g>
  ),

  // Stumps
  stumps: () => (
    <g>
      <rect x="-3" y="-10" width="1" height="12" fill="#8D6E63" />
      <rect x="-0.5" y="-10" width="1" height="12" fill="#8D6E63" />
      <rect x="2" y="-10" width="1" height="12" fill="#8D6E63" />
      <rect x="-2.5" y="-11" width="2.5" height="0.8" fill="#FFC107" />
      <rect x="0" y="-11" width="2.5" height="0.8" fill="#FFC107" />
    </g>
  ),

  // Box/Block
  box: ({ text }) => (
    <g>
      <rect x="-5" y="-5" width="10" height="10" fill="#8D6E63" stroke="#5D4037" strokeWidth="0.3" />
      <line x1="-5" y1="0" x2="5" y2="0" stroke="#6D4C41" strokeWidth="0.5" />
      <line x1="0" y1="-5" x2="0" y2="5" stroke="#6D4C41" strokeWidth="0.5" />
      {text && (
        <text x="0" y="2" textAnchor="middle" fontSize="3" fill="#FFF">{text}</text>
      )}
    </g>
  ),

  // Auto-rickshaw
  auto_rickshaw: () => (
    <g>
      <path d="M -6 0 L -6 -6 L -4 -9 L 5 -9 L 7 -6 L 7 0 Z" fill="#81C784" stroke="#2E7D32" strokeWidth="0.3" />
      <path d="M -5 -9 L -4 -12 L 4 -12 L 5 -9" fill="#FDD835" stroke="#F9A825" strokeWidth="0.3" />
      <rect x="-5" y="-8" width="3" height="3" fill="#81D4FA" rx="0.3" />
      <rect x="1" y="-8" width="5" height="3" fill="#81D4FA" rx="0.3" />
      <circle cx="-4" cy="1" r="2" fill="#37474F" stroke="#263238" strokeWidth="0.3" />
      <circle cx="5" cy="1" r="2" fill="#37474F" stroke="#263238" strokeWidth="0.3" />
      <circle cx="-6.5" cy="-3" r="1" fill="#FFF59D" />
    </g>
  ),

  // Scooter
  scooter: () => (
    <g>
      <ellipse cx="0" cy="-3" rx="5" ry="2.5" fill="#42A5F5" />
      <path d="M -1 -6 L -1 -9 L 1 -9 L 1 -6" stroke="#424242" strokeWidth="0.6" fill="none" />
      <rect x="-3" y="-10" width="6" height="1" fill="#424242" rx="0.3" />
      <ellipse cx="2" cy="-5" rx="3" ry="1.2" fill="#263238" />
      <circle cx="-4" cy="1" r="2.5" fill="#424242" stroke="#212121" strokeWidth="0.3" />
      <circle cx="4" cy="1" r="2.5" fill="#424242" stroke="#212121" strokeWidth="0.3" />
    </g>
  ),

  // Mango
  mango: () => (
    <g>
      <ellipse cx="0" cy="0" rx="2.5" ry="3.5" fill="#FF9800" stroke="#E65100" strokeWidth="0.3" />
      <path d="M 0 -3.5 Q 0.5 -4.5 0.3 -5" stroke="#4E342E" strokeWidth="0.4" fill="none" />
      <ellipse cx="1.2" cy="-4.5" rx="1.5" ry="0.8" fill="#66BB6A" transform="rotate(30 1.2 -4.5)" />
    </g>
  ),

  // Tree
  tree: () => (
    <g>
      <rect x="-3" y="0" width="6" height="15" fill="#5D4037" />
      <circle cx="0" cy="-8" r="12" fill="#4CAF50" />
      <circle cx="-6" cy="-4" r="7" fill="#66BB6A" />
      <circle cx="6" cy="-4" r="7" fill="#43A047" />
      <circle cx="0" cy="-14" r="8" fill="#81C784" />
    </g>
  ),

  // Chai cup
  chai_cup: () => (
    <g>
      <path d="M -3 -4 L -2.5 4 L 2.5 4 L 3 -4 Z" fill="#EFEBE9" stroke="#8D6E63" strokeWidth="0.3" />
      <ellipse cx="0" cy="-3" rx="2.5" ry="0.8" fill="#6D4C41" />
      <path d="M 3 -2 Q 5 0 3 2" stroke="#8D6E63" strokeWidth="0.5" fill="none" />
      {/* Steam */}
      <path d="M -1 -5 Q -1.5 -7 -0.5 -8" stroke="#B0BEC5" strokeWidth="0.3" fill="none" opacity="0.6">
        <animate attributeName="opacity" values="0.6;0.2;0.6" dur="2s" repeatCount="indefinite" />
      </path>
      <path d="M 1 -5 Q 1.5 -7 0.5 -8" stroke="#B0BEC5" strokeWidth="0.3" fill="none" opacity="0.6">
        <animate attributeName="opacity" values="0.2;0.6;0.2" dur="2s" repeatCount="indefinite" />
      </path>
    </g>
  ),

  // Gas cylinder
  gas_cylinder: () => (
    <g>
      <rect x="-4" y="-8" width="8" height="14" fill="#D32F2F" rx="2" />
      <ellipse cx="0" cy="-8" rx="4" ry="1.5" fill="#C62828" />
      <rect x="-1" y="-11" width="2" height="3" fill="#424242" rx="0.3" />
      <circle cx="0" cy="-11" r="1.2" fill="#616161" />
      <ellipse cx="0" cy="6" rx="4" ry="1.5" fill="#B71C1C" />
      <ellipse cx="0" cy="0" rx="3" ry="4" fill="none" stroke="#FFCDD2" strokeWidth="0.3" />
    </g>
  ),

  // Tiffin box
  tiffin: () => (
    <g>
      <ellipse cx="0" cy="4" rx="3.5" ry="1" fill="#B0BEC5" />
      <rect x="-3.5" y="-2" width="7" height="6" fill="#CFD8DC" rx="0.3" />
      <ellipse cx="0" cy="-2" rx="3.5" ry="1" fill="#ECEFF1" />
      <rect x="-3.5" y="-7" width="7" height="5" fill="#CFD8DC" rx="0.3" />
      <ellipse cx="0" cy="-7" rx="3.5" ry="1" fill="#ECEFF1" />
      <path d="M -1 -8 Q 0 -11 1 -8" stroke="#78909C" strokeWidth="0.5" fill="none" />
    </g>
  ),

  // Spring
  spring: () => (
    <g>
      <path
        d="M 0 -8 Q 3 -7 0 -6 Q -3 -5 0 -4 Q 3 -3 0 -2 Q -3 -1 0 0 Q 3 1 0 2 Q -3 3 0 4 Q 3 5 0 6 Q -3 7 0 8"
        fill="none"
        stroke="#607D8B"
        strokeWidth="0.8"
      />
      <rect x="-2" y="-10" width="4" height="1.5" fill="#455A64" />
      <rect x="-2" y="8" width="4" height="1.5" fill="#455A64" />
    </g>
  ),

  // Pulley
  pulley: () => (
    <g>
      <rect x="-1" y="-10" width="2" height="4" fill="#424242" />
      <circle cx="0" cy="-5" r="4" fill="#78909C" stroke="#455A64" strokeWidth="0.5" />
      <circle cx="0" cy="-5" r="1" fill="#455A64" />
      <path d="M -3.5 -5 L -3.5 6" stroke="#8D6E63" strokeWidth="0.5" />
      <path d="M 3.5 -5 L 3.5 6" stroke="#8D6E63" strokeWidth="0.5" />
    </g>
  ),

  // Badge/Label
  badge_orange: ({ text }) => (
    <g>
      <rect x="-12" y="-5" width="24" height="10" rx="2" fill="#FF9800" />
      <text x="0" y="1" textAnchor="middle" fontSize="3.5" fill="#FFF" fontWeight="bold">
        {text || 'Label'}
      </text>
    </g>
  ),

  // Formula card
  card: ({ text }) => (
    <g>
      <rect x="-15" y="-8" width="30" height="16" rx="2" fill="#FFFDE7" stroke="#FFC107" strokeWidth="0.5" />
      <text x="0" y="0" textAnchor="middle" fontSize="5" fill="#5D4037" fontWeight="bold">
        {text || 'F = ma'}
      </text>
      <text x="0" y="5" textAnchor="middle" fontSize="2.5" fill="#8D6E63">
        Formula
      </text>
    </g>
  ),
};

export default SceneProps;






