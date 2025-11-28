/**
 * RefractionScene.jsx
 * Phase 8: Light refraction through lens/prism
 * 
 * Features:
 * - Draggable light beam
 * - Lens/prism selection
 * - Real-time angle calculation
 * - Snell's Law visualization
 */

import React, { useState, useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import { RotateCcw, Maximize2, ChevronDown, ChevronUp, Lightbulb } from 'lucide-react';

const RefractionScene = ({ embedded = true }) => {
  // State
  const [incidentAngle, setIncidentAngle] = useState(30);
  const [medium, setMedium] = useState('glass'); // glass, water, diamond
  const [showControls, setShowControls] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false);
  const [opticalElement, setOpticalElement] = useState('lens'); // lens, prism

  // Refractive indices
  const refractiveIndices = {
    air: 1.0,
    water: 1.33,
    glass: 1.5,
    diamond: 2.42,
  };

  // Calculate refracted angle using Snell's Law
  const refractedAngle = useMemo(() => {
    const n1 = refractiveIndices.air;
    const n2 = refractiveIndices[medium];
    const sinTheta2 = (n1 * Math.sin(incidentAngle * Math.PI / 180)) / n2;
    
    // Check for total internal reflection
    if (Math.abs(sinTheta2) > 1) return null;
    
    return Math.asin(sinTheta2) * 180 / Math.PI;
  }, [incidentAngle, medium]);

  // Calculate ray positions
  const calculateRays = useCallback(() => {
    const centerX = 200;
    const centerY = 100;
    const rayLength = 80;
    
    // Incident ray
    const incidentRad = (90 - incidentAngle) * Math.PI / 180;
    const incidentStartX = centerX - rayLength * Math.cos(incidentRad);
    const incidentStartY = centerY - rayLength * Math.sin(incidentRad);
    
    // Refracted ray
    let refractedEndX, refractedEndY;
    if (refractedAngle !== null) {
      const refractedRad = (90 - refractedAngle) * Math.PI / 180;
      refractedEndX = centerX + rayLength * Math.cos(refractedRad);
      refractedEndY = centerY + rayLength * Math.sin(refractedRad);
    } else {
      // Total internal reflection
      refractedEndX = centerX + rayLength * Math.cos(incidentRad);
      refractedEndY = centerY - rayLength * Math.sin(incidentRad);
    }
    
    return {
      incident: { startX: incidentStartX, startY: incidentStartY, endX: centerX, endY: centerY },
      refracted: { startX: centerX, startY: centerY, endX: refractedEndX, endY: refractedEndY },
    };
  }, [incidentAngle, refractedAngle]);

  const rays = calculateRays();

  return (
    <motion.div
      className={`rounded-xl overflow-hidden shadow-lg border border-gray-200 bg-white ${isExpanded ? 'fixed inset-8 z-50' : ''}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {isExpanded && <div className="fixed inset-0 bg-black/80 -z-10" onClick={() => setIsExpanded(false)} />}

      {/* Scene */}
      <div className="relative bg-gradient-to-b from-gray-900 to-gray-800" style={{ height: isExpanded ? '60vh' : '280px' }}>
        <svg viewBox="0 0 400 200" className="w-full h-full">
          <defs>
            {/* Light beam gradient */}
            <linearGradient id="lightBeam" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#FFD700" />
              <stop offset="100%" stopColor="#FFA500" />
            </linearGradient>
            
            {/* Refracted beam gradient */}
            <linearGradient id="refractedBeam" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#FFA500" />
              <stop offset="100%" stopColor="#FF6B6B" />
            </linearGradient>
            
            {/* Glass gradient */}
            <linearGradient id="glassGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="rgba(135, 206, 235, 0.3)" />
              <stop offset="100%" stopColor="rgba(135, 206, 235, 0.5)" />
            </linearGradient>
            
            {/* Glow filter */}
            <filter id="lightGlow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Background grid */}
          <g opacity="0.1">
            {[...Array(20)].map((_, i) => (
              <line key={`v${i}`} x1={i * 20} y1="0" x2={i * 20} y2="200" stroke="white" strokeWidth="0.5" />
            ))}
            {[...Array(10)].map((_, i) => (
              <line key={`h${i}`} x1="0" y1={i * 20} x2="400" y2={i * 20} stroke="white" strokeWidth="0.5" />
            ))}
          </g>

          {/* Normal line */}
          <line 
            x1="200" y1="20" x2="200" y2="180" 
            stroke="white" strokeWidth="1" strokeDasharray="5 3" opacity="0.5" 
          />
          <text x="205" y="30" fontSize="10" fill="white" opacity="0.7">Normal</text>

          {/* Optical element */}
          {opticalElement === 'lens' ? (
            <g>
              {/* Convex lens */}
              <ellipse 
                cx="200" cy="100" rx="15" ry="60" 
                fill="url(#glassGradient)" 
                stroke="#4FC3F7" strokeWidth="2" 
              />
              <text x="200" y="175" fontSize="10" fill="white" textAnchor="middle" opacity="0.7">
                {medium.charAt(0).toUpperCase() + medium.slice(1)} (n = {refractiveIndices[medium]})
              </text>
            </g>
          ) : (
            <g>
              {/* Prism */}
              <polygon 
                points="200,40 160,160 240,160" 
                fill="url(#glassGradient)" 
                stroke="#4FC3F7" strokeWidth="2" 
              />
              <text x="200" y="180" fontSize="10" fill="white" textAnchor="middle" opacity="0.7">
                {medium.charAt(0).toUpperCase() + medium.slice(1)} Prism
              </text>
            </g>
          )}

          {/* Incident ray */}
          <motion.line
            x1={rays.incident.startX}
            y1={rays.incident.startY}
            x2={rays.incident.endX}
            y2={rays.incident.endY}
            stroke="url(#lightBeam)"
            strokeWidth="4"
            strokeLinecap="round"
            filter="url(#lightGlow)"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.5 }}
          />
          
          {/* Arrow head for incident */}
          <polygon
            points={`${rays.incident.endX},${rays.incident.endY} ${rays.incident.endX - 8},${rays.incident.endY - 12} ${rays.incident.endX + 4},${rays.incident.endY - 8}`}
            fill="#FFD700"
          />

          {/* Refracted ray */}
          <motion.line
            x1={rays.refracted.startX}
            y1={rays.refracted.startY}
            x2={rays.refracted.endX}
            y2={rays.refracted.endY}
            stroke={refractedAngle !== null ? "url(#refractedBeam)" : "#FF6B6B"}
            strokeWidth="4"
            strokeLinecap="round"
            filter="url(#lightGlow)"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          />

          {/* Angle arcs */}
          <g opacity="0.8">
            {/* Incident angle arc */}
            <path
              d={`M 200 70 A 30 30 0 0 1 ${200 - 30 * Math.sin(incidentAngle * Math.PI / 180)} ${70 + 30 * Math.cos(incidentAngle * Math.PI / 180)}`}
              fill="none"
              stroke="#FFD700"
              strokeWidth="2"
            />
            <text 
              x={200 - 40 * Math.sin((incidentAngle / 2) * Math.PI / 180)} 
              y={75 + 40 * Math.cos((incidentAngle / 2) * Math.PI / 180)}
              fontSize="11" fill="#FFD700" fontWeight="bold"
            >
              θ₁ = {incidentAngle}°
            </text>

            {/* Refracted angle arc */}
            {refractedAngle !== null && (
              <>
                <path
                  d={`M 200 130 A 30 30 0 0 0 ${200 + 30 * Math.sin(refractedAngle * Math.PI / 180)} ${130 + 30 * Math.cos(refractedAngle * Math.PI / 180)}`}
                  fill="none"
                  stroke="#FF6B6B"
                  strokeWidth="2"
                />
                <text 
                  x={200 + 45 * Math.sin((refractedAngle / 2) * Math.PI / 180)} 
                  y={135 + 45 * Math.cos((refractedAngle / 2) * Math.PI / 180)}
                  fontSize="11" fill="#FF6B6B" fontWeight="bold"
                >
                  θ₂ = {refractedAngle.toFixed(1)}°
                </text>
              </>
            )}
          </g>

          {/* Light source */}
          <g transform={`translate(${rays.incident.startX - 15}, ${rays.incident.startY - 15})`}>
            <circle cx="15" cy="15" r="12" fill="#FFD700" filter="url(#lightGlow)" />
            <text x="15" y="40" fontSize="9" fill="white" textAnchor="middle">Light</text>
          </g>

          {/* Total Internal Reflection warning */}
          {refractedAngle === null && (
            <text x="200" y="190" fontSize="11" fill="#FF6B6B" textAnchor="middle" fontWeight="bold">
              ⚠️ Total Internal Reflection!
            </text>
          )}
        </svg>

        {/* Formula overlay */}
        <div className="absolute top-2 left-2 bg-black/70 backdrop-blur-sm rounded-lg px-3 py-2">
          <p className="text-sm text-white font-mono">
            n₁ sin θ₁ = n₂ sin θ₂
          </p>
          <p className="text-xs text-gray-300 mt-1">
            Snell's Law
          </p>
        </div>

        {/* Controls */}
        <div className="absolute top-2 right-2 flex gap-2">
          <button 
            onClick={() => { setIncidentAngle(30); setMedium('glass'); }}
            className="p-1.5 bg-white/20 rounded-lg hover:bg-white/30"
          >
            <RotateCcw className="w-4 h-4 text-white" />
          </button>
          <button 
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1.5 bg-white/20 rounded-lg hover:bg-white/30"
          >
            <Maximize2 className="w-4 h-4 text-white" />
          </button>
        </div>
      </div>

      {/* Controls Panel */}
      <div className="bg-gray-50 border-t border-gray-200">
        <button 
          onClick={() => setShowControls(!showControls)}
          className="w-full py-1.5 flex items-center justify-center text-gray-500 hover:bg-gray-100 text-sm"
        >
          {showControls ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          <span className="ml-1">{showControls ? 'Hide' : 'Show'} Controls</span>
        </button>

        {showControls && (
          <div className="px-4 pb-4 space-y-4">
            {/* Optical element selector */}
            <div className="flex gap-2">
              <button
                onClick={() => setOpticalElement('lens')}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                  opticalElement === 'lens' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                🔍 Lens
              </button>
              <button
                onClick={() => setOpticalElement('prism')}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                  opticalElement === 'prism' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                🔺 Prism
              </button>
            </div>

            {/* Incident angle slider */}
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Incident Angle</span>
                <span className="font-bold text-yellow-600">{incidentAngle}°</span>
              </div>
              <input
                type="range"
                min="5" max="85" value={incidentAngle}
                onChange={(e) => setIncidentAngle(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-yellow-500"
              />
            </div>

            {/* Medium selector */}
            <div>
              <p className="text-sm text-gray-600 mb-2">Medium</p>
              <div className="grid grid-cols-3 gap-2">
                {Object.entries(refractiveIndices).filter(([k]) => k !== 'air').map(([key, n]) => (
                  <button
                    key={key}
                    onClick={() => setMedium(key)}
                    className={`py-2 rounded-lg text-xs font-medium transition-colors ${
                      medium === key 
                        ? 'bg-cyan-500 text-white' 
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    {key.charAt(0).toUpperCase() + key.slice(1)}
                    <br />
                    <span className="opacity-70">n={n}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Live calculation */}
            <div className="p-3 bg-white rounded-lg border border-gray-200">
              <div className="flex items-center gap-2 mb-2">
                <Lightbulb className="w-4 h-4 text-yellow-500" />
                <span className="text-sm font-medium text-gray-700">Live Calculation</span>
              </div>
              <p className="text-sm text-gray-600 font-mono">
                {refractiveIndices.air} × sin({incidentAngle}°) = {refractiveIndices[medium]} × sin(θ₂)
              </p>
              <p className="text-sm text-gray-600 font-mono mt-1">
                θ₂ = {refractedAngle !== null ? `${refractedAngle.toFixed(2)}°` : 'TIR!'}
              </p>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default RefractionScene;



