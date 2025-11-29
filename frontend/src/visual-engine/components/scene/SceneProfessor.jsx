/**
 * Scene Professor Component
 * Animated Indian professor avatar with gestures
 */

import React from 'react';

const SceneProfessor = ({ 
  id,
  x = 10, 
  y = 50, 
  scale = 1, 
  gesture = 'standing',
  gestureProgress = 0,
  armAngle = 0,
  speech,
  onClick,
}) => {
  const transform = `translate(${x}, ${y}) scale(${scale * 0.15})`;

  // Gesture-based arm angles
  const gestures = {
    standing: { leftArm: 10, rightArm: -10, head: 0 },
    pointing: { leftArm: -60, rightArm: -10, head: 5 },
    explaining: { leftArm: -40, rightArm: 20, head: 0 },
    thinking: { leftArm: 20, rightArm: -30, head: -10 },
    celebrating: { leftArm: -70, rightArm: -70, head: 0 },
  };

  const currentGesture = gestures[gesture] || gestures.standing;
  const leftArmAngle = armAngle || currentGesture.leftArm;
  const rightArmAngle = currentGesture.rightArm;
  const headTilt = currentGesture.head;

  return (
    <g id={`professor-${id}`} transform={transform} onClick={onClick} style={{ cursor: 'pointer' }}>
      {/* Shadow */}
      <ellipse cx="0" cy="75" rx="25" ry="8" fill="rgba(0,0,0,0.15)" />

      {/* Body - Kurta */}
      <path
        d="M -20 20 L -25 70 L 25 70 L 20 20 Q 0 25 -20 20"
        fill="#1565C0"
        stroke="#0D47A1"
        strokeWidth="2"
      />

      {/* Kurta collar */}
      <path d="M -10 20 L 0 30 L 10 20" fill="#1976D2" stroke="#0D47A1" strokeWidth="1" />

      {/* Legs */}
      <rect x="-12" y="70" width="10" height="30" fill="#37474F" />
      <rect x="2" y="70" width="10" height="30" fill="#37474F" />

      {/* Shoes */}
      <ellipse cx="-7" cy="102" rx="8" ry="5" fill="#4E342E" />
      <ellipse cx="7" cy="102" rx="8" ry="5" fill="#4E342E" />

      {/* Left Arm (gesturing) */}
      <g transform={`rotate(${leftArmAngle} -15 25)`}>
        <path
          d="M -20 25 L -45 45 L -50 40"
          fill="none"
          stroke="#FFE0B2"
          strokeWidth="8"
          strokeLinecap="round"
        />
        {/* Hand */}
        <circle cx="-50" cy="40" r="6" fill="#FFE0B2" />
        
        {/* Pointing finger for pointing gesture */}
        {gesture === 'pointing' && (
          <path d="M -50 40 L -65 30" stroke="#FFE0B2" strokeWidth="4" strokeLinecap="round" />
        )}
      </g>

      {/* Right Arm */}
      <g transform={`rotate(${rightArmAngle} 15 25)`}>
        <path
          d="M 20 25 L 40 50 L 45 48"
          fill="none"
          stroke="#FFE0B2"
          strokeWidth="8"
          strokeLinecap="round"
        />
        <circle cx="45" cy="48" r="6" fill="#FFE0B2" />
        
        {/* Chalk/Pointer */}
        <rect x="42" y="45" width="20" height="4" fill="#FFF" rx="1" transform="rotate(20 42 47)" />
      </g>

      {/* Head */}
      <g transform={`rotate(${headTilt} 0 0)`}>
        {/* Face */}
        <circle cx="0" cy="0" r="22" fill="#FFE0B2" stroke="#FFCC80" strokeWidth="2" />
        
        {/* Hair */}
        <path
          d="M -20 -8 Q -22 -25 -10 -28 Q 0 -32 10 -28 Q 22 -25 20 -8"
          fill="#212121"
        />
        
        {/* Eyes */}
        <g>
          <ellipse cx="-8" cy="-2" rx="3" ry="4" fill="#212121" />
          <ellipse cx="8" cy="-2" rx="3" ry="4" fill="#212121" />
          {/* Eye shine */}
          <circle cx="-7" cy="-3" r="1" fill="white" />
          <circle cx="9" cy="-3" r="1" fill="white" />
        </g>
        
        {/* Eyebrows */}
        <path d="M -12 -8 Q -8 -12 -4 -8" fill="none" stroke="#424242" strokeWidth="2" />
        <path d="M 4 -8 Q 8 -12 12 -8" fill="none" stroke="#424242" strokeWidth="2" />
        
        {/* Nose */}
        <path d="M 0 0 L 2 6 L -2 6" fill="#FFCC80" />
        
        {/* Mouth */}
        <path
          d={gesture === 'celebrating' ? "M -8 10 Q 0 18 8 10" : "M -6 10 Q 0 14 6 10"}
          fill="none"
          stroke="#5D4037"
          strokeWidth="2"
        />
        
        {/* Glasses */}
        <circle cx="-8" cy="-2" r="8" fill="none" stroke="#424242" strokeWidth="2" />
        <circle cx="8" cy="-2" r="8" fill="none" stroke="#424242" strokeWidth="2" />
        <line x1="0" y1="-2" x2="-8" y2="-2" stroke="#424242" strokeWidth="2" />
        <line x1="16" y1="-2" x2="22" y2="-5" stroke="#424242" strokeWidth="2" />
        <line x1="-16" y1="-2" x2="-22" y2="-5" stroke="#424242" strokeWidth="2" />
        
        {/* Mustache */}
        <path d="M -8 6 Q -4 8 0 6 Q 4 8 8 6" fill="#424242" />
      </g>

      {/* Speech Bubble */}
      {speech && (
        <g>
          <path
            d="M 40 -40 L 55 -55 L 130 -55 L 130 -25 L 55 -25 L 40 -40 L 48 -32"
            fill="white"
            stroke="#E0E0E0"
            strokeWidth="1"
          />
          <text x="92" y="-38" textAnchor="middle" fontSize="9" fill="#333">
            {speech}
          </text>
        </g>
      )}

      {/* Celebration particles */}
      {gesture === 'celebrating' && (
        <g>
          {[...Array(6)].map((_, i) => (
            <circle
              key={i}
              cx={-30 + i * 12}
              cy={-50}
              r="4"
              fill={['#FF5722', '#FFC107', '#4CAF50', '#2196F3', '#9C27B0', '#E91E63'][i]}
            >
              <animate
                attributeName="cy"
                values="-40;-60;-40"
                dur="1s"
                repeatCount="indefinite"
                begin={`${i * 0.1}s`}
              />
              <animate
                attributeName="opacity"
                values="1;0.5;1"
                dur="1s"
                repeatCount="indefinite"
                begin={`${i * 0.1}s`}
              />
            </circle>
          ))}
        </g>
      )}
    </g>
  );
};

export default SceneProfessor;







