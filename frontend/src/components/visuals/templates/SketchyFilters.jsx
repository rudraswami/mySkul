/**
 * SketchyFilters - SVG Filter Definitions for Hand-Drawn Effect
 * ==============================================================
 * 
 * These SVG filters create the "living ink" aesthetic by adding:
 * - Subtle wobble/displacement to lines
 * - Organic imperfections
 * - Hand-drawn feel
 * 
 * Include this component once in your app to make filters available globally.
 */

import React from 'react';

/**
 * Global SVG Filters Definition
 * Add this component to your app's root to make filters available everywhere
 */
export const SketchyFilterDefs = () => (
  <svg 
    style={{ position: 'absolute', width: 0, height: 0 }} 
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <defs>
      {/* Main Sketchy Filter - Adds hand-drawn wobble effect */}
      <filter id="sketchy" x="-5%" y="-5%" width="110%" height="110%">
        {/* Create organic noise pattern */}
        <feTurbulence 
          type="turbulence" 
          baseFrequency="0.02" 
          numOctaves="3" 
          result="turbulence"
          seed="2"
        />
        {/* Apply displacement for wobble effect */}
        <feDisplacementMap 
          in="SourceGraphic" 
          in2="turbulence" 
          scale="2" 
          xChannelSelector="R" 
          yChannelSelector="G"
        />
      </filter>

      {/* Light Sketchy - More subtle wobble for small elements */}
      <filter id="sketchy-light" x="-2%" y="-2%" width="104%" height="104%">
        <feTurbulence 
          type="turbulence" 
          baseFrequency="0.03" 
          numOctaves="2" 
          result="turbulence"
          seed="5"
        />
        <feDisplacementMap 
          in="SourceGraphic" 
          in2="turbulence" 
          scale="1" 
          xChannelSelector="R" 
          yChannelSelector="G"
        />
      </filter>

      {/* Heavy Sketchy - More dramatic wobble for emphasis */}
      <filter id="sketchy-heavy" x="-10%" y="-10%" width="120%" height="120%">
        <feTurbulence 
          type="turbulence" 
          baseFrequency="0.015" 
          numOctaves="4" 
          result="turbulence"
          seed="7"
        />
        <feDisplacementMap 
          in="SourceGraphic" 
          in2="turbulence" 
          scale="4" 
          xChannelSelector="R" 
          yChannelSelector="G"
        />
      </filter>

      {/* Pencil Effect - Grainy texture like graphite */}
      <filter id="pencil" x="0%" y="0%" width="100%" height="100%">
        <feTurbulence 
          type="fractalNoise" 
          baseFrequency="0.5" 
          numOctaves="5" 
          result="noise"
        />
        <feDisplacementMap 
          in="SourceGraphic" 
          in2="noise" 
          scale="1" 
          xChannelSelector="R" 
          yChannelSelector="G"
          result="displaced"
        />
        <feComposite 
          in="displaced" 
          in2="SourceGraphic" 
          operator="in"
        />
      </filter>

      {/* Paper Texture Filter */}
      <filter id="paper-texture" x="0%" y="0%" width="100%" height="100%">
        <feTurbulence 
          type="fractalNoise" 
          baseFrequency="0.9" 
          numOctaves="4" 
          stitchTiles="stitch" 
          result="noise"
        />
        <feColorMatrix 
          in="noise" 
          type="saturate" 
          values="0" 
          result="mono"
        />
        <feBlend 
          in="SourceGraphic" 
          in2="mono" 
          mode="multiply" 
          result="blended"
        />
      </filter>

      {/* Glow Effect for emphasis */}
      <filter id="sketch-glow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur in="SourceGraphic" stdDeviation="3" result="blur"/>
        <feMerge>
          <feMergeNode in="blur"/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>

      {/* Drop Shadow for depth */}
      <filter id="sketch-shadow" x="-10%" y="-10%" width="130%" height="130%">
        <feDropShadow dx="2" dy="2" stdDeviation="2" floodColor="#1e293b" floodOpacity="0.15"/>
      </filter>

      {/* Arrow Marker Definitions */}
      <marker 
        id="arrow-head" 
        markerWidth="10" 
        markerHeight="10" 
        refX="9" 
        refY="3" 
        orient="auto" 
        markerUnits="strokeWidth"
      >
        <path d="M0,0 L0,6 L9,3 z" fill="currentColor"/>
      </marker>

      <marker 
        id="arrow-head-blue" 
        markerWidth="10" 
        markerHeight="10" 
        refX="9" 
        refY="3" 
        orient="auto" 
        markerUnits="strokeWidth"
      >
        <path d="M0,0 L0,6 L9,3 z" fill="#3b82f6"/>
      </marker>

      <marker 
        id="arrow-head-orange" 
        markerWidth="10" 
        markerHeight="10" 
        refX="9" 
        refY="3" 
        orient="auto" 
        markerUnits="strokeWidth"
      >
        <path d="M0,0 L0,6 L9,3 z" fill="#f97316"/>
      </marker>

      <marker 
        id="arrow-head-green" 
        markerWidth="10" 
        markerHeight="10" 
        refX="9" 
        refY="3" 
        orient="auto" 
        markerUnits="strokeWidth"
      >
        <path d="M0,0 L0,6 L9,3 z" fill="#22c55e"/>
      </marker>
    </defs>
  </svg>
);

/**
 * Apply sketchy filter to an SVG element
 * @param {string} intensity - 'light' | 'normal' | 'heavy'
 * @returns {string} Filter URL reference
 */
export const getSketchyFilter = (intensity = 'normal') => {
  switch (intensity) {
    case 'light':
      return 'url(#sketchy-light)';
    case 'heavy':
      return 'url(#sketchy-heavy)';
    case 'pencil':
      return 'url(#pencil)';
    default:
      return 'url(#sketchy)';
  }
};

export default SketchyFilterDefs;


