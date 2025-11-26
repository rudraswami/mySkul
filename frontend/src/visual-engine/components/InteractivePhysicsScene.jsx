/**
 * Interactive Physics Scene
 * 
 * NEXT LEVEL: Students don't just watch - they EXPLORE!
 * - Drag sliders to change Force & Mass
 * - See Acceleration change in real-time
 * - Ball speed reflects the physics
 * - Truly understand F = m × a
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RotateCcw, Maximize2, X, Play, Pause } from 'lucide-react';

const InteractivePhysicsScene = ({ 
  onClose, 
  embedded = true,
}) => {
  // Physics values (interactive!)
  const [force, setForce] = useState(15); // 5-30 N
  const [mass, setMass] = useState(0.15); // 0.1-0.5 kg
  const acceleration = force / mass; // Calculated!
  
  // Animation state
  const [isPlaying, setIsPlaying] = useState(false);
  const [ballPosition, setBallPosition] = useState({ x: 180, y: 200 });
  const [ballVelocity, setBallVelocity] = useState(0);
  const [ballTrail, setBallTrail] = useState([]);
  const [showForceArrow, setShowForceArrow] = useState(true);
  const [professorGesture, setProfessorGesture] = useState('explaining');
  const [isExpanded, setIsExpanded] = useState(false);
  const [hasPlayed, setHasPlayed] = useState(false);
  
  const animationRef = useRef(null);

  // Calculate arrow length based on force
  const forceArrowLength = (force / 30) * 120;
  
  // Calculate ball speed based on acceleration
  const ballSpeed = Math.min(acceleration / 50, 5); // Cap speed for visibility

  // Play the physics simulation
  const playSimulation = useCallback(() => {
    setIsPlaying(true);
    setHasPlayed(true);
    setProfessorGesture('throwing');
    
    let time = 0;
    let startX = 180;
    let startY = 200;
    const trail = [];
    
    const animate = () => {
      time += 0.03 * ballSpeed;
      
      if (time > 1.5) {
        setIsPlaying(false);
        setProfessorGesture('celebrating');
        return;
      }
      
      // Physics-based motion!
      const x = startX + (acceleration * 2) * time * time; // s = 0.5 * a * t^2
      const y = startY - 80 * time + 50 * time * time;
      
      // Trail effect
      trail.push({ x, y, opacity: 1 - time * 0.6 });
      if (trail.length > 12) trail.shift();
      setBallTrail([...trail]);
      
      setBallPosition({ x: Math.min(x, 540), y });
      setBallVelocity(acceleration * time * 10);
      
      animationRef.current = requestAnimationFrame(animate);
    };
    
    animate();
  }, [acceleration, ballSpeed]);

  // Reset simulation
  const resetSimulation = () => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    setIsPlaying(false);
    setBallPosition({ x: 180, y: 200 });
    setBallVelocity(0);
    setBallTrail([]);
    setProfessorGesture('explaining');
    setHasPlayed(false);
  };

  // Auto-update when force/mass changes
  useEffect(() => {
    if (hasPlayed && !isPlaying) {
      // Reset when values change
      resetSimulation();
    }
  }, [force, mass]);

  return (
    <motion.div
      className={`relative rounded-2xl overflow-hidden shadow-2xl bg-white ${isExpanded ? 'fixed inset-4 z-50' : ''}`}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
    >
      {isExpanded && (
        <div className="fixed inset-0 bg-black/90 -z-10" onClick={() => setIsExpanded(false)} />
      )}

      {/* === MAIN SCENE === */}
      <div className="relative" style={{ minHeight: embedded ? '380px' : '480px' }}>
        <svg viewBox="0 0 640 380" className="w-full h-full">
          <defs>
            <linearGradient id="sky" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#4FC3F7" />
              <stop offset="60%" stopColor="#B3E5FC" />
              <stop offset="100%" stopColor="#E1F5FE" />
            </linearGradient>
            <linearGradient id="grass" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#66BB6A" />
              <stop offset="100%" stopColor="#388E3C" />
            </linearGradient>
            <linearGradient id="forceGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#FF5722" />
              <stop offset="100%" stopColor="#FF9800" />
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="blur"/>
              <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>

          {/* Sky */}
          <rect x="0" y="0" width="640" height="240" fill="url(#sky)" />
          
          {/* Sun */}
          <g transform="translate(560, 55)">
            {[...Array(8)].map((_, i) => (
              <line 
                key={i}
                x1="0" y1="0" 
                x2={Math.cos(i * 45 * Math.PI / 180) * 50} 
                y2={Math.sin(i * 45 * Math.PI / 180) * 50}
                stroke="#FFD54F" strokeWidth="3" opacity="0.4"
              />
            ))}
            <circle cx="0" cy="0" r="35" fill="#FFD54F" />
            <circle cx="0" cy="0" r="28" fill="#FFEB3B" />
          </g>
          
          {/* Clouds */}
          <g opacity="0.9">
            <ellipse cx="100" cy="60" rx="45" ry="22" fill="white" />
            <ellipse cx="140" cy="55" rx="35" ry="18" fill="white" />
            <ellipse cx="70" cy="55" rx="28" ry="15" fill="white" />
          </g>
          <g opacity="0.7">
            <ellipse cx="350" cy="45" rx="55" ry="25" fill="white" />
            <ellipse cx="395" cy="40" rx="40" ry="20" fill="white" />
          </g>

          {/* Ground */}
          <rect x="0" y="240" width="640" height="140" fill="url(#grass)" />
          
          {/* Grass blades */}
          {[...Array(20)].map((_, i) => (
            <path 
              key={i}
              d={`M ${i * 32 + 10} 380 Q ${i * 32 + 15} 365 ${i * 32 + 20} 380`}
              stroke="#81C784" strokeWidth="2" fill="none"
            />
          ))}
          
          {/* Cricket Pitch */}
          <rect x="80" y="260" width="480" height="95" rx="6" fill="#E8E0DB" />
          <line x1="140" y1="260" x2="140" y2="355" stroke="white" strokeWidth="2" opacity="0.5" />
          <line x1="500" y1="260" x2="500" y2="355" stroke="white" strokeWidth="2" opacity="0.5" />
          
          {/* Boundary */}
          <ellipse cx="320" cy="310" rx="290" ry="50" fill="none" stroke="white" strokeWidth="2" strokeDasharray="12 8" opacity="0.25" />

          {/* === PROFESSOR === */}
          <g transform="translate(90, 175)">
            <ellipse cx="0" cy="115" rx="32" ry="10" fill="rgba(0,0,0,0.15)" />
            
            {/* Body */}
            <path d="M -26 30 L -32 100 L 32 100 L 26 30 Q 0 40 -26 30" fill="#1565C0" stroke="#0D47A1" strokeWidth="2" />
            <path d="M -14 30 L 0 45 L 14 30" fill="#1976D2" />
            
            {/* Legs */}
            <rect x="-18" y="100" width="14" height="42" fill="#37474F" rx="2" />
            <rect x="4" y="100" width="14" height="42" fill="#37474F" rx="2" />
            <ellipse cx="-11" cy="145" rx="13" ry="6" fill="#4E342E" />
            <ellipse cx="11" cy="145" rx="13" ry="6" fill="#4E342E" />
            
            {/* Arms */}
            <g transform={`rotate(${professorGesture === 'throwing' ? -75 : professorGesture === 'celebrating' ? -60 : -45} -18 32)`}>
              <path d="M -26 32 L -58 52" stroke="#FFCCBC" strokeWidth="11" strokeLinecap="round" />
              <circle cx="-61" cy="54" r="9" fill="#FFCCBC" />
            </g>
            <g transform={`rotate(${professorGesture === 'celebrating' ? -50 : 12} 18 32)`}>
              <path d="M 26 35 L 52 60" stroke="#FFCCBC" strokeWidth="11" strokeLinecap="round" />
              <circle cx="54" cy="62" r="9" fill="#FFCCBC" />
            </g>
            
            {/* Head */}
            <circle cx="0" cy="0" r="30" fill="#FFCCBC" stroke="#FFAB91" strokeWidth="2" />
            <path d="M -28 -10 Q -30 -36 -16 -40 Q 0 -46 16 -40 Q 30 -36 28 -10" fill="#1a1a1a" />
            
            {/* Eyes */}
            <ellipse cx="-11" cy="-2" rx="5" ry="6" fill="#212121" />
            <ellipse cx="11" cy="-2" rx="5" ry="6" fill="#212121" />
            <circle cx="-9" cy="-4" r="2" fill="white" />
            <circle cx="13" cy="-4" r="2" fill="white" />
            
            {/* Glasses */}
            <circle cx="-11" cy="-2" r="11" fill="none" stroke="#333" strokeWidth="2" />
            <circle cx="11" cy="-2" r="11" fill="none" stroke="#333" strokeWidth="2" />
            <line x1="0" y1="-2" x2="0" y2="-2" stroke="#333" strokeWidth="2" />
            <line x1="22" y1="-4" x2="30" y2="-8" stroke="#333" strokeWidth="2" />
            <line x1="-22" y1="-4" x2="-30" y2="-8" stroke="#333" strokeWidth="2" />
            
            {/* Mustache & Smile */}
            <path d="M -11 12 Q -5 16 0 12 Q 5 16 11 12" fill="#333" />
            <path d={professorGesture === 'celebrating' ? "M -10 22 Q 0 35 10 22" : "M -8 20 Q 0 28 8 20"} fill="none" stroke="#5D4037" strokeWidth="2.5" />
          </g>

          {/* === BALL TRAIL === */}
          {ballTrail.map((point, i) => (
            <circle 
              key={i}
              cx={point.x} cy={point.y} 
              r={10 - i * 0.6}
              fill="#D32F2F"
              opacity={point.opacity * 0.5}
            />
          ))}

          {/* === BALL === */}
          <g transform={`translate(${ballPosition.x}, ${ballPosition.y})`}>
            <ellipse cx="6" cy="22" rx="16" ry="5" fill="rgba(0,0,0,0.2)" />
            
            {/* Glow when moving */}
            {isPlaying && (
              <circle cx="0" cy="0" r="30" fill="#FF5722" opacity="0.25" filter="url(#glow)" />
            )}
            
            <circle cx="0" cy="0" r="20" fill="#D32F2F" stroke="#8B0000" strokeWidth="2" />
            <path d="M -13 -13 Q 0 0 13 13" stroke="white" strokeWidth="2.5" fill="none" />
            <circle cx="-6" cy="-9" r="5" fill="white" opacity="0.4" />
            
            {isPlaying && (
              <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="0.25s" repeatCount="indefinite" additive="sum" />
            )}
          </g>

          {/* === FORCE ARROW (Dynamic size based on force!) === */}
          {showForceArrow && !isPlaying && (
            <g transform={`translate(${ballPosition.x + 28}, ${ballPosition.y})`}>
              {/* Glow */}
              <line x1="0" y1="0" x2={forceArrowLength} y2="0" stroke="#FF9800" strokeWidth="16" strokeLinecap="round" opacity="0.3" filter="url(#glow)" />
              
              {/* Arrow */}
              <line x1="0" y1="0" x2={forceArrowLength} y2="0" stroke="url(#forceGrad)" strokeWidth="10" strokeLinecap="round" />
              <polygon points={`${forceArrowLength + 5},0 ${forceArrowLength - 12},-12 ${forceArrowLength - 12},12`} fill="#FF5722" />
              
              {/* Force label */}
              <g transform={`translate(${forceArrowLength / 2}, -30)`}>
                <rect x="-30" y="-16" width="60" height="32" rx="6" fill="#FF5722" />
                <text x="0" y="6" textAnchor="middle" fontSize="16" fill="white" fontWeight="bold">F = {force}N</text>
              </g>
            </g>
          )}

          {/* === VELOCITY INDICATOR (when moving) === */}
          {isPlaying && ballVelocity > 0 && (
            <g transform={`translate(${ballPosition.x}, ${ballPosition.y - 45})`}>
              <rect x="-45" y="-14" width="90" height="28" rx="6" fill="#2196F3" />
              <text x="0" y="6" textAnchor="middle" fontSize="13" fill="white" fontWeight="bold">
                v = {ballVelocity.toFixed(1)} m/s
              </text>
            </g>
          )}

          {/* === STUMPS === */}
          <g transform="translate(545, 268)">
            <rect x="-18" y="0" width="7" height="65" fill="#8D6E63" rx="1" />
            <rect x="-4" y="0" width="7" height="65" fill="#8D6E63" rx="1" />
            <rect x="10" y="0" width="7" height="65" fill="#8D6E63" rx="1" />
            <rect x="-16" y="-5" width="14" height="4" fill="#FFC107" rx="1" />
            <rect x="0" y="-5" width="14" height="4" fill="#FFC107" rx="1" />
          </g>

          {/* === BAT === */}
          <g transform="translate(465, 290) rotate(-22)">
            <rect x="-5" y="-52" width="10" height="26" fill="#5D4037" rx="2" />
            <rect x="-13" y="-26" width="26" height="65" fill="#EFEBE9" rx="3" stroke="#A1887F" strokeWidth="1" />
          </g>

          {/* === MASS LABEL === */}
          <g transform={`translate(${ballPosition.x}, ${ballPosition.y + 38})`}>
            <rect x="-45" y="0" width="90" height="26" rx="6" fill="white" stroke="#4CAF50" strokeWidth="2" />
            <text x="0" y="18" textAnchor="middle" fontSize="13" fill="#2E7D32" fontWeight="bold">m = {mass.toFixed(2)} kg</text>
          </g>

        </svg>

        {/* === TOP UI === */}
        <div className="absolute top-4 left-4 bg-white/95 backdrop-blur-sm rounded-xl px-5 py-3 shadow-lg">
          <div className="text-2xl font-bold text-gray-800 font-serif">F = m × a</div>
          <div className="text-xs text-gray-500">Newton's Second Law</div>
        </div>

        <div className="absolute top-4 right-4 flex space-x-2">
          <motion.button 
            onClick={resetSimulation}
            className="p-2.5 bg-white/90 rounded-full shadow-lg hover:bg-white"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            <RotateCcw className="w-5 h-5 text-gray-700" />
          </motion.button>
          <motion.button 
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-2.5 bg-white/90 rounded-full shadow-lg hover:bg-white"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            {isExpanded ? <X className="w-5 h-5" /> : <Maximize2 className="w-5 h-5" />}
          </motion.button>
        </div>

        {/* === PLAY BUTTON (Center) === */}
        {!isPlaying && (
          <motion.button
            onClick={playSimulation}
            className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-20 h-20 bg-orange-500 hover:bg-orange-600 rounded-full shadow-2xl flex items-center justify-center"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
          >
            <Play className="w-10 h-10 text-white ml-1" fill="white" />
          </motion.button>
        )}
      </div>

      {/* === INTERACTIVE CONTROLS === */}
      <div className="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 p-5">
        
        {/* Formula Display - Live! */}
        <div className="flex items-center justify-center mb-5">
          <div className="bg-gray-700/50 rounded-xl px-6 py-3 flex items-center space-x-3">
            <span className="text-orange-400 font-bold text-xl">{force}N</span>
            <span className="text-gray-400">=</span>
            <span className="text-green-400 font-bold text-xl">{mass.toFixed(2)}kg</span>
            <span className="text-gray-400">×</span>
            <span className="text-blue-400 font-bold text-2xl">{acceleration.toFixed(1)} m/s²</span>
          </div>
        </div>

        {/* Sliders */}
        <div className="max-w-lg mx-auto space-y-4">
          
          {/* Force Slider */}
          <div className="flex items-center space-x-4">
            <div className="w-20 text-right">
              <span className="text-orange-400 font-bold">Force</span>
            </div>
            <div className="flex-1 relative">
              <input
                type="range"
                min="5"
                max="30"
                value={force}
                onChange={(e) => setForce(Number(e.target.value))}
                className="w-full h-3 bg-gray-700 rounded-lg appearance-none cursor-pointer slider-orange"
                style={{
                  background: `linear-gradient(to right, #FF5722 0%, #FF5722 ${((force - 5) / 25) * 100}%, #374151 ${((force - 5) / 25) * 100}%, #374151 100%)`
                }}
              />
            </div>
            <div className="w-16 bg-orange-500/20 rounded-lg px-3 py-1 text-center">
              <span className="text-orange-400 font-bold">{force}N</span>
            </div>
          </div>

          {/* Mass Slider */}
          <div className="flex items-center space-x-4">
            <div className="w-20 text-right">
              <span className="text-green-400 font-bold">Mass</span>
            </div>
            <div className="flex-1">
              <input
                type="range"
                min="10"
                max="50"
                value={mass * 100}
                onChange={(e) => setMass(Number(e.target.value) / 100)}
                className="w-full h-3 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                style={{
                  background: `linear-gradient(to right, #4CAF50 0%, #4CAF50 ${((mass * 100 - 10) / 40) * 100}%, #374151 ${((mass * 100 - 10) / 40) * 100}%, #374151 100%)`
                }}
              />
            </div>
            <div className="w-16 bg-green-500/20 rounded-lg px-3 py-1 text-center">
              <span className="text-green-400 font-bold">{mass.toFixed(2)}kg</span>
            </div>
          </div>

          {/* Acceleration Result */}
          <div className="flex items-center justify-center pt-2">
            <div className="bg-blue-500/20 rounded-xl px-6 py-3 flex items-center space-x-3">
              <span className="text-gray-400">Acceleration =</span>
              <motion.span 
                className="text-blue-400 font-bold text-2xl"
                key={acceleration.toFixed(1)}
                initial={{ scale: 1.3, color: '#60A5FA' }}
                animate={{ scale: 1, color: '#60A5FA' }}
              >
                {acceleration.toFixed(1)} m/s²
              </motion.span>
            </div>
          </div>
        </div>

        {/* Hint */}
        <p className="text-center text-gray-500 text-sm mt-4">
          Drag sliders to change Force and Mass, then press Play!
        </p>
      </div>

      {/* Custom slider styles */}
      <style jsx>{`
        input[type="range"]::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 24px;
          height: 24px;
          border-radius: 50%;
          background: white;
          cursor: pointer;
          box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        }
        input[type="range"]::-moz-range-thumb {
          width: 24px;
          height: 24px;
          border-radius: 50%;
          background: white;
          cursor: pointer;
          box-shadow: 0 2px 6px rgba(0,0,0,0.3);
          border: none;
        }
      `}</style>
    </motion.div>
  );
};

export default InteractivePhysicsScene;


