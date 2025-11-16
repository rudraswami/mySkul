import React from 'react';

/**
 * Atom SVG Component - for Chemistry concepts
 */
export const Atom = ({ x = 0, y = 0, size = 50, color = '#8B5CF6', protons = 6 }) => {
  const radius = size / 2;
  
  return (
    <g transform={`translate(${x}, ${y})`}>
      {/* Electron orbits */}
      <circle
        cx="0"
        cy="0"
        r={radius * 0.6}
        fill="none"
        stroke="#A78BFA"
        strokeWidth="1"
        strokeDasharray="2,2"
        opacity="0.6"
      />
      <circle
        cx="0"
        cy="0"
        r={radius * 0.9}
        fill="none"
        stroke="#A78BFA"
        strokeWidth="1"
        strokeDasharray="2,2"
        opacity="0.4"
      />

      {/* Nucleus (protons + neutrons) */}
      <circle
        cx="0"
        cy="0"
        r={radius * 0.25}
        fill={color}
        stroke="#6D28D9"
        strokeWidth="2"
      />

      {/* Electrons on orbits */}
      <circle cx={radius * 0.6} cy="0" r="4" fill="#00D9FF" />
      <circle cx={radius * -0.3} cy={radius * 0.5} r="4" fill="#00D9FF" />
      <circle cx={radius * -0.3} cy={radius * -0.5} r="4" fill="#00D9FF" />
      
      {/* Additional electron */}
      <circle cx={radius * 0.9} cy={radius * 0.3} r="3" fill="#00D9FF" opacity="0.7" />
    </g>
  );
};

export default Atom;


