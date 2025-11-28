/**
 * Compact Physics Scene
 * 
 * - Takes less vertical space (fits with text)
 * - More polished, attractive graphics
 * - Clean, professional look
 * - Sliders in a compact bottom bar
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import { RotateCcw, Maximize2, Play, ChevronDown, ChevronUp } from 'lucide-react';

const CompactPhysicsScene = ({ 
  embedded = true,
}) => {
  // Physics values
  const [force, setForce] = useState(15);
  const [mass, setMass] = useState(0.15);
  const acceleration = force / mass;
  
  // Animation state
  const [isPlaying, setIsPlaying] = useState(false);
  const [ballPosition, setBallPosition] = useState({ x: 140, y: 95 });
  const [ballTrail, setBallTrail] = useState([]);
  const [showControls, setShowControls] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false);
  
  const animationRef = useRef(null);
  const forceArrowLength = (force / 30) * 80;
  const ballSpeed = Math.min(acceleration / 60, 4);

  const playSimulation = useCallback(() => {
    setIsPlaying(true);
    
    let time = 0;
    let startX = 140;
    let startY = 95;
    const trail = [];
    
    const animate = () => {
      time += 0.035 * ballSpeed;
      
      if (time > 1.2) {
        setIsPlaying(false);
        return;
      }
      
      const x = startX + (acceleration * 1.5) * time * time;
      const y = startY - 50 * time + 35 * time * time;
      
      trail.push({ x, y, opacity: 1 - time * 0.7 });
      if (trail.length > 8) trail.shift();
      setBallTrail([...trail]);
      
      setBallPosition({ x: Math.min(x, 360), y });
      
      animationRef.current = requestAnimationFrame(animate);
    };
    
    animate();
  }, [acceleration, ballSpeed]);

  const resetSimulation = () => {
    if (animationRef.current) cancelAnimationFrame(animationRef.current);
    setIsPlaying(false);
    setBallPosition({ x: 140, y: 95 });
    setBallTrail([]);
  };

  useEffect(() => {
    resetSimulation();
  }, [force, mass]);

  return (
    <motion.div
      className={`rounded-xl overflow-hidden shadow-lg border border-gray-200 bg-white ${isExpanded ? 'fixed inset-8 z-50' : ''}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {isExpanded && <div className="fixed inset-0 bg-black/80 -z-10" onClick={() => setIsExpanded(false)} />}

      {/* COMPACT SCENE - Only 220px height! */}
      <div className="relative" style={{ height: isExpanded ? '60vh' : '220px' }}>
        <svg viewBox="0 0 420 180" className="w-full h-full" preserveAspectRatio="xMidYMid slice">
          <defs>
            <linearGradient id="skyC" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#4FC3F7" />
              <stop offset="100%" stopColor="#E1F5FE" />
            </linearGradient>
            <linearGradient id="grassC" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#66BB6A" />
              <stop offset="100%" stopColor="#2E7D32" />
            </linearGradient>
            <linearGradient id="forceC" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#FF5722" />
              <stop offset="100%" stopColor="#FF9800" />
            </linearGradient>
            <filter id="shadowC">
              <feDropShadow dx="1" dy="2" stdDeviation="2" floodOpacity="0.2"/>
            </filter>
          </defs>

          {/* Sky */}
          <rect x="0" y="0" width="420" height="120" fill="url(#skyC)" />
          
          {/* Sun */}
          <circle cx="380" cy="30" r="22" fill="#FFD54F" />
          <circle cx="380" cy="30" r="17" fill="#FFEB3B" />
          
          {/* Cloud */}
          <g opacity="0.9">
            <ellipse cx="80" cy="35" rx="28" ry="14" fill="white" />
            <ellipse cx="105" cy="32" rx="22" ry="11" fill="white" />
            <ellipse cx="58" cy="32" rx="18" ry="10" fill="white" />
          </g>

          {/* Ground */}
          <rect x="0" y="120" width="420" height="60" fill="url(#grassC)" />
          
          {/* Cricket Pitch */}
          <rect x="50" y="128" width="320" height="45" rx="4" fill="#E8E0DB" />
          <line x1="90" y1="128" x2="90" y2="173" stroke="white" strokeWidth="1.5" opacity="0.4" />
          <line x1="330" y1="128" x2="330" y2="173" stroke="white" strokeWidth="1.5" opacity="0.4" />

          {/* === PROFESSOR (Compact, Polished) === */}
          <g transform="translate(60, 75)" filter="url(#shadowC)">
            {/* Shadow */}
            <ellipse cx="0" cy="52" rx="18" ry="5" fill="rgba(0,0,0,0.15)" />
            
            {/* Body */}
            <path d="M -14 15 L -17 48 L 17 48 L 14 15 Q 0 20 -14 15" fill="#1565C0" />
            <path d="M -8 15 L 0 24 L 8 15" fill="#1976D2" />
            
            {/* Legs */}
            <rect x="-10" y="48" width="8" height="22" fill="#37474F" rx="1" />
            <rect x="2" y="48" width="8" height="22" fill="#37474F" rx="1" />
            
            {/* Shoes */}
            <ellipse cx="-6" cy="71" rx="7" ry="3" fill="#3E2723" />
            <ellipse cx="6" cy="71" rx="7" ry="3" fill="#3E2723" />
            
            {/* Throwing arm */}
            <g transform={`rotate(${isPlaying ? -70 : -50} -10 18)`}>
              <path d="M -14 18 L -35 30" stroke="#FFCCBC" strokeWidth="7" strokeLinecap="round" />
              <circle cx="-37" cy="31" r="5" fill="#FFCCBC" />
            </g>
            
            {/* Other arm */}
            <path d="M 14 20 L 28 35" stroke="#FFCCBC" strokeWidth="7" strokeLinecap="round" />
            <circle cx="29" cy="36" r="5" fill="#FFCCBC" />
            
            {/* Head */}
            <circle cx="0" cy="0" r="17" fill="#FFCCBC" />
            
            {/* Hair */}
            <path d="M -15 -6 Q -17 -22 -9 -24 Q 0 -28 9 -24 Q 17 -22 15 -6" fill="#1a1a1a" />
            
            {/* Eyes */}
            <ellipse cx="-6" cy="-1" rx="3" ry="3.5" fill="#212121" />
            <ellipse cx="6" cy="-1" rx="3" ry="3.5" fill="#212121" />
            <circle cx="-5" cy="-2" r="1" fill="white" />
            <circle cx="7" cy="-2" r="1" fill="white" />
            
            {/* Glasses */}
            <circle cx="-6" cy="-1" r="7" fill="none" stroke="#333" strokeWidth="1.5" />
            <circle cx="6" cy="-1" r="7" fill="none" stroke="#333" strokeWidth="1.5" />
            <line x1="1" y1="-1" x2="-1" y2="-1" stroke="#333" strokeWidth="1.5" />
            
            {/* Mustache */}
            <path d="M -6 7 Q 0 10 6 7" fill="#333" />
            
            {/* Smile */}
            <path d="M -5 11 Q 0 16 5 11" fill="none" stroke="#5D4037" strokeWidth="1.5" />
          </g>

          {/* === BALL TRAIL === */}
          {ballTrail.map((p, i) => (
            <circle key={i} cx={p.x} cy={p.y} r={6 - i * 0.5} fill="#D32F2F" opacity={p.opacity * 0.4} />
          ))}

          {/* === BALL === */}
          <g transform={`translate(${ballPosition.x}, ${ballPosition.y})`}>
            <ellipse cx="3" cy="12" rx="10" ry="3" fill="rgba(0,0,0,0.15)" />
            
            {isPlaying && <circle cx="0" cy="0" r="16" fill="#FF5722" opacity="0.2" />}
            
            <circle cx="0" cy="0" r="12" fill="#C62828" stroke="#8B0000" strokeWidth="1.5" />
            <path d="M -8 -8 Q 0 0 8 8" stroke="white" strokeWidth="1.5" fill="none" />
            <circle cx="-4" cy="-5" r="3" fill="white" opacity="0.4" />
            
            {isPlaying && (
              <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="0.2s" repeatCount="indefinite" additive="sum" />
            )}
          </g>

          {/* === FORCE ARROW === */}
          {!isPlaying && (
            <g transform={`translate(${ballPosition.x + 18}, ${ballPosition.y})`}>
              <line x1="0" y1="0" x2={forceArrowLength} y2="0" stroke="url(#forceC)" strokeWidth="6" strokeLinecap="round" />
              <polygon points={`${forceArrowLength + 3},0 ${forceArrowLength - 8},-7 ${forceArrowLength - 8},7`} fill="#FF5722" />
              
              {/* Force label */}
              <g transform={`translate(${forceArrowLength / 2}, -18)`}>
                <rect x="-20" y="-10" width="40" height="20" rx="4" fill="#FF5722" />
                <text x="0" y="5" textAnchor="middle" fontSize="11" fill="white" fontWeight="bold">{force}N</text>
              </g>
            </g>
          )}

          {/* === MASS LABEL === */}
          <g transform={`translate(${ballPosition.x}, ${ballPosition.y + 22})`}>
            <rect x="-28" y="0" width="56" height="18" rx="4" fill="white" stroke="#4CAF50" strokeWidth="1.5" />
            <text x="0" y="13" textAnchor="middle" fontSize="10" fill="#2E7D32" fontWeight="bold">{mass.toFixed(2)} kg</text>
          </g>

          {/* === STUMPS === */}
          <g transform="translate(365, 130)">
            <rect x="-10" y="0" width="4" height="38" fill="#6D4C41" rx="1" />
            <rect x="-2" y="0" width="4" height="38" fill="#6D4C41" rx="1" />
            <rect x="6" y="0" width="4" height="38" fill="#6D4C41" rx="1" />
            <rect x="-9" y="-3" width="9" height="3" fill="#FFC107" rx="1" />
            <rect x="0" y="-3" width="9" height="3" fill="#FFC107" rx="1" />
          </g>

          {/* === BAT === */}
          <g transform="translate(310, 145) rotate(-20)">
            <rect x="-3" y="-28" width="6" height="14" fill="#5D4037" rx="1" />
            <rect x="-7" y="-14" width="14" height="35" fill="#EFEBE9" rx="2" stroke="#A1887F" strokeWidth="0.5" />
          </g>

        </svg>

        {/* === MINIMAL TOP UI === */}
        <div className="absolute top-2 left-2 bg-white/95 backdrop-blur-sm rounded-lg px-3 py-1.5 shadow-sm border border-gray-100">
          <div className="text-lg font-bold text-gray-800">F = m × a</div>
        </div>

        <div className="absolute top-2 right-2 flex space-x-1.5">
          <button onClick={resetSimulation} className="p-1.5 bg-white/90 rounded-lg shadow-sm hover:bg-white">
            <RotateCcw className="w-4 h-4 text-gray-600" />
          </button>
          <button onClick={() => setIsExpanded(!isExpanded)} className="p-1.5 bg-white/90 rounded-lg shadow-sm hover:bg-white">
            <Maximize2 className="w-4 h-4 text-gray-600" />
          </button>
        </div>

        {/* === PLAY BUTTON === */}
        {!isPlaying && (
          <motion.button
            onClick={playSimulation}
            className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-14 h-14 bg-orange-500 hover:bg-orange-600 rounded-full shadow-lg flex items-center justify-center"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            <Play className="w-7 h-7 text-white ml-0.5" fill="white" />
          </motion.button>
        )}
      </div>

      {/* === COMPACT CONTROLS === */}
      <div className="bg-gray-50 border-t border-gray-100">
        {/* Toggle */}
        <button 
          onClick={() => setShowControls(!showControls)}
          className="w-full py-1.5 flex items-center justify-center text-gray-500 hover:bg-gray-100 text-sm"
        >
          {showControls ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          <span className="ml-1">{showControls ? 'Hide' : 'Show'} Controls</span>
        </button>

        {showControls && (
          <div className="px-4 pb-3 space-y-2">
            {/* Live Formula */}
            <div className="flex items-center justify-center py-2 bg-white rounded-lg border border-gray-100">
              <span className="text-orange-500 font-bold">{force}N</span>
              <span className="text-gray-400 mx-2">=</span>
              <span className="text-green-600 font-bold">{mass.toFixed(2)}kg</span>
              <span className="text-gray-400 mx-2">×</span>
              <span className="text-blue-600 font-bold text-lg">{acceleration.toFixed(1)} m/s²</span>
            </div>

            {/* Compact Sliders */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Force</span>
                  <span className="font-medium text-orange-500">{force}N</span>
                </div>
                <input
                  type="range"
                  min="5" max="30"
                  value={force}
                  onChange={(e) => setForce(Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-orange-500"
                />
              </div>
              <div>
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Mass</span>
                  <span className="font-medium text-green-600">{mass.toFixed(2)}kg</span>
                </div>
                <input
                  type="range"
                  min="10" max="50"
                  value={mass * 100}
                  onChange={(e) => setMass(Number(e.target.value) / 100)}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-green-500"
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default CompactPhysicsScene;






